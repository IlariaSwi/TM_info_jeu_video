"""
Version 3 : MODÈLE PROPRE pour vos projets.

Cette version résout le problème du flickering en séparant la page
en plusieurs ZONES, chacune indépendamment rafraîchissable. Au lieu
de "tout redessiner toutes les 0.5s", on ne redessine QUE la zone
concernée par un changement.

Concepts illustrés :
1. Plusieurs fonctions @ui.refreshable pour différentes zones.
2. Chaque zone regroupe des éléments qui changent en même temps
   (ou presque, voir note ci-dessous).
3. Polling intelligent : on ne redessine que les zones dont les
   données ont vraiment changé.

Pour vos projets (Codenames, Poker, Loup-garou, Carcassonne) ce
pattern est essentiel : sans lui, des dizaines de cartes ou tuiles
flickeraient en permanence.

Note : on a regroupé pseudo + pièces + carte dans une seule zone
"entête" pour la simplicité, même si techniquement les pièces
changent à la fin de la phase mise (dans resoudre) et la carte
change au début de la phase mise (dans commencer_manche). En
pratique le browser cache l'image et le rendu est stable.

Pour lancer :
    python app_v3.py
Puis ouvrir DEUX onglets :
    http://localhost:8080/jeu/Alice
    http://localhost:8080/jeu/Bob
"""
from nicegui import ui, app
from partie import Partie

app.add_static_files('/img', 'img')

partie = None


@ui.page('/')
def accueil():
    ui.label("Configuration de la partie").style('font-size: 1.5em')
    nom1 = ui.input('Nom joueur 1', value='Alice')
    nom2 = ui.input('Nom joueur 2', value='Bob')
    liens = ui.column()

    def commencer():
        global partie
        partie = Partie([nom1.value, nom2.value])
        partie.commencer_manche()
        liens.clear()
        with liens:
            ui.label("Partie créée. Lien pour chaque joueur :")
            for j in partie.joueurs:
                ui.link(
                    f"➜ entrer comme {j.nom}", f'/jeu/{j.nom}'
                ).props('target=_blank')

    ui.button('Créer la partie', on_click=commencer)


@ui.page('/jeu/{nom}')
def jeu(nom: str):
    if partie is None:
        ui.label("Aucune partie en cours.")
        return
    moi = partie.joueur(nom)
    if moi is None:
        ui.label(f"Joueur '{nom}' inconnu.")
        return

    # ----- CONTRÔLEUR -----

    def parier():
        partie.faire_choix(moi, True)
        zone_jeu.refresh()

    def passer():
        partie.faire_choix(moi, False)
        zone_jeu.refresh()

    def manche_suivante():
        partie.commencer_manche()
        zone_entete.refresh()  # nouvelle carte
        zone_jeu.refresh()     # retour à la phase "mise"

    # ----- VUE : DEUX zones indépendantes -----

    # Zone 1 : entête (pseudo, pièces, ma carte).
    # Change à chaque transition de manche.
    @ui.refreshable
    def zone_entete():
        ui.label(f"Tu es {moi.nom}").style('font-size: 1.5em')
        with ui.row().classes('items-center'):
            ui.icon('paid').style('color: #d4af37; font-size: 1.5em')
            ui.label(f"{moi.pieces}").style('font-size: 1.1em')
        ui.image(f'/img/{moi.carte}.png').style('width: 150px')
        ui.separator()

    # Zone 2 : zone de jeu (boutons, attente, résultat).
    # Change à chaque clic et à chaque changement de phase.
    @ui.refreshable
    def zone_jeu():
        if partie.phase == "mise":
            if moi.choix is None:
                ui.button("Parier (1 pièce)", on_click=parier)
                ui.button("Passe", on_click=passer)
            else:
                ui.label("Tu as choisi. En attente des autres joueurs...")
                ui.spinner()

        elif partie.phase == "resultat":
            ui.label("--- Résultat ---").style('font-weight: bold')
            for j in partie.joueurs:
                if j is moi:
                    continue  # ma carte est déjà affichée plus haut
                with ui.row().classes('items-center'):
                    ui.label(f"{j.nom} :").style('min-width: 80px')
                    ui.image(f'/img/{j.carte}.png').style('width: 60px')
                    ui.icon('paid').style('color: #d4af37; font-size: 1.3em')
                    ui.label(f"{j.pieces}")
            ui.label(partie.message).style('color: navy; font-size: 1.2em')
            ui.button("Manche suivante", on_click=manche_suivante)

    # Affichage initial des deux zones
    zone_entete()
    zone_jeu()

    # ----- POLLING INTELLIGENT -----
    # On surveille les changements et on redessine UNIQUEMENT la zone
    # concernée. Pas de refresh inutile, donc pas de flickering.

    dernier_etat = {
        "phase": None,
        "nb_choix_faits": 0,
        "mes_pieces": moi.pieces,
        "ma_carte": moi.carte,
    }

    def verifier_changements():
        etat_actuel = {
            "phase": partie.phase,
            "nb_choix_faits": sum(1 for j in partie.joueurs if j.choix is not None),
            "mes_pieces": moi.pieces,
            "ma_carte": moi.carte,
        }
        # Si la phase ou les choix ont changé : la zone de jeu doit changer
        if (etat_actuel["phase"] != dernier_etat["phase"]
                or etat_actuel["nb_choix_faits"] != dernier_etat["nb_choix_faits"]):
            zone_jeu.refresh()
        # Si mes pièces ou ma carte ont changé : l'entête doit changer
        if (etat_actuel["mes_pieces"] != dernier_etat["mes_pieces"]
                or etat_actuel["ma_carte"] != dernier_etat["ma_carte"]):
            zone_entete.refresh()
        dernier_etat.update(etat_actuel)

    ui.timer(0.5, verifier_changements)


ui.run(host='0.0.0.0', port=8080)
