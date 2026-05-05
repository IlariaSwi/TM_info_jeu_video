"""
Le 'modèle' (le M de MVC) : tout l'état et les règles du jeu, sans interface.
On peut tester ce fichier dans un terminal Python sans aucune UI.

Règles :
- Chaque manche, chaque joueur reçoit une carte cachée (1-13).
- Chaque joueur choisit : PARIER (1 pièce) ou PASSE.
- Quand tous ont choisi :
    * S'il y a au moins 2 miseurs : la plus haute carte gagne 1 pièce de
      chaque autre miseur.
    * Sinon, la manche est annulée.
"""
import random


class Joueur:
    def __init__(self, nom):
        self.nom = nom
        self.pieces = 10
        self.carte = None
        self.choix = None  # None | True (parier) | False (passe)


class Partie:
    def __init__(self, noms_joueurs):
        self.joueurs = [Joueur(nom) for nom in noms_joueurs]
        self.phase = "attente"     # "attente" | "mise" | "resultat"
        self.message = ""

    def commencer_manche(self):
        """Distribue une carte cachée à chaque joueur, passe en phase 'mise'."""
        for j in self.joueurs:
            j.carte = random.randint(1, 13)
            j.choix = None
        self.phase = "mise"
        self.message = ""

    def joueur(self, nom):
        """Retourne le Joueur qui a ce nom (ou None)."""
        for j in self.joueurs:
            if j.nom == nom:
                return j
        return None

    def faire_choix(self, j, parier):
        """Un joueur déclare son choix. Si tout le monde a choisi, on résout."""
        # j = self.joueur(nom)
        if j is None or self.phase != "mise" or j.choix is not None:
            return
        j.choix = parier
        if all(je.choix is not None for je in self.joueurs):
            self.resoudre()

    def resoudre(self):
        miseurs = [j for j in self.joueurs if j.choix]
        if len(miseurs) < 2:
            self.message = "Pas assez de miseurs, manche annulée."
        else:
            # On cherche le joueur avec la carte la plus haute
            gagnant = miseurs[0]
            for j in miseurs[1:]:
                if j.carte > gagnant.carte:
                    gagnant = j
            for j in miseurs:
                if j is gagnant:
                    j.pieces += len(miseurs) - 1
                else:
                    j.pieces -= 1
            self.message = f"{gagnant.nom} gagne avec un {gagnant.carte} !"
        self.phase = "resultat"


# --- petit test rapide quand on lance ce fichier directement ---
if __name__ == "__main__":
    p = Partie(["Alice", "Bob"])
    p.commencer_manche()
    print(f"Phase : {p.phase}")
    for j in p.joueurs:
        print(f"  {j.nom} a la carte {j.carte}, pièces = {j.pieces}")
    print("Alice parie, Bob passe...")
    p.faire_choix(p.joueurs[0], True) # joueur Alice
    p.faire_choix(p.joueurs[1], False) # joueur Bob
    print(f"Phase : {p.phase}")
    print(f"Message : {p.message}")
    for j in p.joueurs:
        print(f"  {j.nom} : pièces = {j.pieces}")
