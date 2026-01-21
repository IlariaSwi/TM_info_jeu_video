class Point:
    '''Un point avec coordonnées x et y'''
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangle:
    '''Un rectangle avec dimensions et liste de sommets'''

    def __init__(self, largeur, hauteur):
        '''Initialise les dimensions du rectangle'''
        self.largeur = largeur
        self.hauteur = hauteur
        self.sommets = []
    
    def set_sommet(self, p):
        '''Ajoute un sommet à la liste de sommets'''
        self.sommets.append(p) # Voyez-vous des problèmes ici ?

    def perimetre(self):
        '''Calcule le périmètre'''
        return self.largeur * 2 + self.hauteur * 2
    
    def surface(self):
        '''Calcule la surface'''
        return self.largeur * self.hauteur
    
    def affiche_sommets(self):
        for s in self.sommets:
            print(f"({s.x}, {s.y})")
    
    def __str__(self):
        '''Représentation de l'objet. C'est le comportement du print()'''
        return f"Rectangle de dimensions {self.largeur} * {self.hauteur}"

def compare(r1, r2):
    if r1.surface() > r2.surface():
        print(f"Le rectangle 1 est plus grand")
    elif r1.surface() < r2.surface():
        print("Le rectangle 2 est plus grand")
    else:
        print("Les rectangles ont la même surface")

rect1 = Rectangle(3, 4)
rect2 = Rectangle(2.5, 7)

print(rect1.largeur)

compare(rect1, rect2)

p1 = Point(0, 0)
p2 = Point(0, 3)

rect1.set_sommet(p1)
rect1.set_sommet(p2)
rect1.set_sommet(Point(5, 0))
rect1.set_sommet(Point(5, 3))

print(rect1.sommets)

rect1.affiche_sommets()
