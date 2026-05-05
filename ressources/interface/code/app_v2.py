"""
Version 2 : UNE FENÊTRE PAR JOUEUR.

Chaque joueur ouvre une URL différente : /jeu/Alice ou /jeu/Bob.
Chaque navigateur ne voit que SA carte.
C'est le modèle CLIENT-SERVEUR :

    [navigateur Alice]  <---|
                            |---> [serveur Python : possède la Partie]
    [navigateur Bob]    <---|

- le serveur (ce script) connaît tout l'état du jeu
- chaque client (navigateur) ne reçoit que ce que le serveur lui envoie
- les boutons cliqués envoient une "demande" au serveur, qui met à
  jour le modèle puis ré-envoie l'état à tous

Différences avec la V1 :
1. URL paramétrée : /jeu/{nom} au lieu de /jeu
2. Chaque page n'affiche QUE le joueur qui correspond à son nom
3. Un timer fait que chaque navigateur se rafraîchit automatiquement,
   sinon Alice ne verrait pas que Bob a fini de choisir

Pour lancer :
    python app_v2.py
Puis ouvrir DEUX onglets :
    http://localhost:8080/jeu/Alice
    http://localhost:8080/jeu/Bob
(Après avoir créé la partie sur http://localhost:8080/)
"""
from nicegui import ui, app
from partie import Partie

# Rendre le dossier img/ accessible depuis le navigateur via /img/...
app.add_static_files('/img', 'img')

partie = None  # vit dans la mémoire du serveur, partagé entre tous les clients


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
                ).props('target=_blank') # target: pour ouvrir dans une nouvelle page

    ui.button('Créer la partie', on_click=commencer)


@ui.page('/jeu/{nom}')
def jeu(nom: str):
    """
    Une page par joueur. Le {nom} dans l'URL identifie qui je suis.
    Chaque navigateur qui ouvre cette URL exécute cette fonction
    SÉPARÉMENT, mais tous lisent et écrivent dans la même variable
    `partie` côté serveur.
    """
    if partie is None:
        ui.label("Aucune partie en cours.")
        return
    moi = partie.joueur(nom)
    if moi is None:
        ui.label(f"Joueur '{nom}' inconnu.")
        return
    
    # ----- CONTRÔLEUR : fonctions appelées par les boutons -----

    def parier():
        partie.faire_choix(moi, True)

    def passer():
        partie.faire_choix(moi, False)

    def manche_suivante():
        partie.commencer_manche()
        afficher.refresh()

    # ----- VUE : ce qui dessine la page -----
    @ui.refreshable
    def afficher():
        ui.label(f"Tu es {moi.nom}").style('font-size: 1.5em')
    
        with ui.row().classes('items-center'):
            ui.icon('paid').style('color: #d4af37; font-size: 1.5em')
            ui.label(f"{moi.pieces}").style('font-size: 1.1em')
        ui.separator()

        if partie.phase == "mise":
            if moi.choix is None:
                # Note : on n'affiche QUE la carte de "moi", pas celle des autres.
                ui.image(f'/img/{moi.carte}.png').style('width: 150px')
                ui.button("Parier (1 pièce)", on_click=parier)
                ui.button("Passe", on_click=passer)
            else:
                ui.label("Tu as choisi. En attente des autres joueurs...")
                ui.spinner()

        elif partie.phase == "resultat":
            ui.label("--- Résultat ---").style('font-weight: bold')
            for j in partie.joueurs:
                # Pour chaque joueur : son nom, sa carte (image), ses pièces
                with ui.row().classes('items-center'):
                    ui.label(f"{j.nom} :").style('min-width: 80px')
                    ui.image(f'/img/{j.carte}.png').style('width: 60px')
                    ui.icon('paid').style('color: #d4af37; font-size: 1.3em')
                    ui.label(f"{j.pieces}")
            ui.label(partie.message).style('color: navy; font-size: 1.2em')
            ui.button("Manche suivante", on_click=manche_suivante)


    afficher()

    # Polling : on regarde l'état toutes les 0.5s,
    # mais on ne redessine la page QUE si quelque chose a changé.
    # Sinon les images flickent inutilement.
    dernier_etat = {"phase": None, "nb_choix_faits": 0}

    def verifier_changements():
        etat_actuel = {
            "phase": partie.phase,
            "nb_choix_faits": sum(1 for j in partie.joueurs if j.choix is not None),
        }
        if etat_actuel != dernier_etat:
            dernier_etat.update(etat_actuel)
            afficher.refresh()

    ui.timer(0.5, verifier_changements)


# host='0.0.0.0' = accessible depuis les autres ordinateurs du même réseau
# (sinon : seul localhost sur la même machine)
ui.run(host='0.0.0.0', port=8080)
