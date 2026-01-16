#==============================================================
#classe produit
#==============================================================


class Produit:
    def __init__(self, code_prod, nom_prod, description, quantite, prix_unit):
        self.code_prod = code_prod
        self.nom_prod = nom_prod
        self.description = description
        self.quantite = quantite
        self.prix_unit = prix_unit

    def afficher(self):
       print(f"Code : {self.code_prod}")
       print(f"Nom : {self.nom_prod}")
       print(f"Description : {self.description}")
       print(f"Quantité : {self.quantite}")
       print(f"Prix unitaire : {self.prix_unit} DT")

    def modifier(self, nom, description, quantite, prix):
        self.nom_prod = nom
        self.description = description
        self.quantite = quantite
        self.prix_unit = prix




        # =====================================
# Test de la classe Produit
# =====================================

if __name__ == "__main__":
    p1 = Produit(1, "Clavier", "Clavier USB", 15, 45)
    p1.afficher()
