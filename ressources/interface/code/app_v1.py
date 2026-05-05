"""
Version 1 : UNE SEULE FENÊTRE pour les deux joueurs.

Tout le monde voit tout (les deux cartes sont visibles à l'écran).
C'est volontairement "incorrect" du point de vue du jeu :
on triche pour simplifier la mise en place. La V2 corrigera ça.

Cette version sert à montrer comment la VUE (NiceGUI) se branche
sur le MODÈLE (la classe Partie) avec un CONTRÔLEUR (les fonctions
appelées au clic des boutons).

Pour lancer :
    pip install nicegui
    python app_v1.py
Puis ouvrir http://localhost:8080 dans le navigateur.
"""
from nicegui import ui, app
from partie import Partie

# Rendre le dossier img/ accessible depuis le navigateur via /img/...
# Sans ça, le navigateur ne pourrait pas charger nos fichiers locaux.
app.add_static_files('/img', 'img')

# Le modèle vit ici, dans la mémoire du serveur.
# Une seule partie à la fois pour ce tutoriel.
partie = None


@ui.page('/')
def accueil():
    """Page d'accueil : on saisit les noms des joueurs."""
    ui.label("Configuration de la partie").style('font-size: 1.5em')
    nom1 = ui.input('Nom joueur 1', value='Alice')
    nom2 = ui.input('Nom joueur 2', value='Bob')

    def commencer():
        global partie # on se refère à la variable partie déclarée à la ligne 26
        partie = Partie([nom1.value, nom2.value])
        partie.commencer_manche()
        ui.navigate.to('/jeu')

    ui.button('Commencer la partie', on_click=commencer)


@ui.page('/jeu')
def jeu():
    """Page de jeu : tout le monde voit tout."""
    if partie is None:
        ui.label("Aucune partie en cours. Retourne sur /")
        return
 
    def manche_suivante():
        partie.commencer_manche()
        afficher.refresh()

    # @ui.refreshable : on déclare que cette fonction peut être
    # redessinée. Plus tard, afficher.refresh() la rejoue.
    @ui.refreshable
    def afficher():
        with ui.row():
            for j in partie.joueurs:
                afficher_panneau(j)
        if partie.phase == "resultat":
            ui.label(partie.message).style('font-size: 1.3em; margin-top: 1em')
            ui.button("Manche suivante", on_click=manche_suivante)

    def afficher_panneau(j):
        """Dessine la carte d'un joueur (identique pour Alice et Bob ici)."""
        with ui.card().style('min-width: 220px'):
            ui.label(j.nom).style('font-weight: bold; font-size: 1.2em')
            # Ligne avec l'icône de pièce et le nombre de pièces
            with ui.row().classes('items-center'):
                ui.icon('paid').style('color: #d4af37; font-size: 1.5em')
                ui.label(f"{j.pieces}").style('font-size: 1.1em')
            # Image de la carte 
            ui.image(f'/img/{j.carte}.png').style('width: 120px')
            if partie.phase == "mise":
                if j.choix is None:
                    ui.button("Parier", on_click=lambda: action(j, True))
                    ui.button("Passe", on_click=lambda: action(j, False))
                else:
                    ui.label("✓ choix fait")

    def action(j, parier):
        """Le 'contrôleur' : on traduit un clic en appel au modèle."""
        partie.faire_choix(j, parier)
        afficher.refresh()  # on redessine la vue après changement

    afficher()


ui.run()
