# ==============================================================
# Classe Produit
# ==============================================================

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

    def retirer_stock(self, quantite):
        if quantite <= self.quantite:
            self.quantite -= quantite
            return True
        return False


# ==============================================================
# Classe Commande
# ==============================================================

class Commande:
    def __init__(self, code_cmd, produit, quantite_cmd):
        self.code_cmd = code_cmd
        self.produit = produit
        self.quantite_cmd = quantite_cmd
        self.valide = self.produit.retirer_stock(quantite_cmd)

    def afficher(self):
        print(f"Code commande : {self.code_cmd}")
        print(f"Produit : {self.produit.nom_prod}")
        print(f"Quantité commandée : {self.quantite_cmd}")

        if self.valide:
            print("Commande valide")
            print(f"Prix total : {self.calculer_total()} DT")
        else:
            print("Commande refusée : stock insuffisant")

    def calculer_total(self):
        return self.quantite_cmd * self.produit.prix_unit


# ==============================================================
# Classe Facture (NOUVELLE)
# ==============================================================

class Facture:
    def __init__(self, commande):
        self.code_cmd = commande.code_cmd
        self.nom_produit = commande.produit.nom_prod
        self.quantite = commande.quantite_cmd
        self.prix_unitaire = commande.produit.prix_unit
        self.total = commande.calculer_total()

    def afficher(self):
        print("===== FACTURE =====")
        print(f"Commande : {self.code_cmd}")
        print(f"Produit : {self.nom_produit}")
        print(f"Quantité : {self.quantite}")
        print(f"Prix unitaire : {self.prix_unitaire} DT")
        print(f"TOTAL : {self.total} DT")


# ==============================================================
# Classe GestionStock
# ==============================================================

class GestionStock:
    def __init__(self):
        self.produits = []
        self.commandes = []
        self.historique = []
        self.factures = []   # 🔥 liste des factures

    def ajouter_produit(self, produit):
        for p in self.produits:
            if p.code_prod == produit.code_prod:
                print("❌ Produit déjà existant.")
                return False
        self.produits.append(produit)
        print("✅ Produit ajouté.")
        return True

    def afficher_produits(self):
        if not self.produits:
            print("Aucun produit en stock.")
            return

        produits_tries = sorted(self.produits, key=lambda p: p.nom_prod.lower())
        for p in produits_tries:
            print("-----------------")
            p.afficher()

    def ajouter_commande(self, commande):
        if commande.valide:
            self.commandes.append(commande)
            facture = Facture(commande)
            self.factures.append(facture)
            print("✅ Commande enregistrée et facture créée.")
        else:
            print("❌ Commande non enregistrée (stock insuffisant).")

    def supprimer_commande(self, code_cmd):
        for i in range(len(self.commandes)):
            if self.commandes[i].code_cmd == code_cmd:
                cmd = self.commandes.pop(i)
                self.historique.append(cmd)
                print("✅ Commande supprimée et ajoutée à l'historique.")
                return True
        print("❌ Commande introuvable.")
        return False

    def afficher_historique(self):
        if not self.historique:
            print("Historique vide.")
            return

        print("=== HISTORIQUE DES COMMANDES ===")
        for cmd in self.historique:
            print("-----------------")
            cmd.afficher()

    def afficher_factures(self):
        if not self.factures:
            print("Aucune facture disponible.")
            return

        print("=== LISTE DES FACTURES ===")
        for f in self.factures:
            print("-----------------")
            f.afficher()

    def statistiques_produits(self):
        if not self.commandes and not self.historique:
            print("Aucune commande pour les statistiques.")
            return

        stats = {}

        for cmd in self.commandes + self.historique:
            nom = cmd.produit.nom_prod
            stats[nom] = stats.get(nom, 0) + cmd.quantite_cmd

        print("=== STATISTIQUES DES PRODUITS ===")
        for produit, total in stats.items():
            print(f"{produit} : {total} unités commandées")


# ==============================================================
# Menu principal
# ==============================================================

def afficher_menu():
    print("\n===== MENU GESTION DE STOCK =====")
    print("1. Ajouter un produit")
    print("2. Afficher les produits")
    print("3. Ajouter une commande")
    print("4. Supprimer une commande")
    print("5. Afficher historique")
    print("6. Statistiques")
    print("7. Afficher factures")
    print("8. Quitter")


# ==============================================================
# PROGRAMME PRINCIPAL (CONSOLE)
# ==============================================================

if __name__ == "__main__":
    gs = GestionStock()

    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        if choix == "1":
            code = int(input("Code produit : "))
            nom = input("Nom : ")
            desc = input("Description : ")
            qte = int(input("Quantité : "))
            prix = float(input("Prix unitaire : "))
            gs.ajouter_produit(Produit(code, nom, desc, qte, prix))

        elif choix == "2":
            gs.afficher_produits()

        elif choix == "3":
            code_cmd = int(input("Code commande : "))
            code_prod = int(input("Code produit : "))
            qte = int(input("Quantité commandée : "))

            produit = next((p for p in gs.produits if p.code_prod == code_prod), None)
            if produit:
                gs.ajouter_commande(Commande(code_cmd, produit, qte))
            else:
                print("❌ Produit introuvable.")

        elif choix == "4":
            code = int(input("Code commande à supprimer : "))
            gs.supprimer_commande(code)

        elif choix == "5":
            gs.afficher_historique()

        elif choix == "6":
            gs.statistiques_produits()

        elif choix == "7":
            gs.afficher_factures()

        elif choix == "8":
            print("Au revoir 👋")
            break

        else:
            print("Choix invalide.")
