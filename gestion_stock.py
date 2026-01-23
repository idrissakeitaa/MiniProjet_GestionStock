from database import get_connection, creer_tables
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

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

    def calculer_total(self):
        return self.quantite_cmd * self.produit.prix_unit


# ==============================================================
# Classe Facture
# ==============================================================

class Facture:
    def __init__(self, commande):
        self.code_cmd = commande.code_cmd
        self.nom_produit = commande.produit.nom_prod
        self.quantite = commande.quantite_cmd
        self.prix_unitaire = commande.produit.prix_unit
        self.total = commande.calculer_total()


# ==============================================================
# Classe GestionStock (AVEC SQLITE)
# ==============================================================

class GestionStock:
    def __init__(self):
        creer_tables()
        self.produits = []
        self.commandes = []
        self.historique = []
        self.factures = []
        self.charger_produits()

    # ----------------------------
    # PRODUITS
    # ----------------------------

    def charger_produits(self):
        self.produits.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM produits")
        rows = cur.fetchall()
        conn.close()

        for code, nom, desc, qte, prix in rows:
            self.produits.append(Produit(code, nom, desc, qte, prix))

    def ajouter_produit(self, produit):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT code FROM produits WHERE code = ?", (produit.code_prod,))
        if cur.fetchone():
            conn.close()
            return False

        cur.execute(
            "INSERT INTO produits VALUES (?, ?, ?, ?, ?)",
            (produit.code_prod, produit.nom_prod, produit.description,
             produit.quantite, produit.prix_unit)
        )

        conn.commit()
        conn.close()

        self.produits.append(produit)
        return True

    def mettre_a_jour_stock(self, produit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE produits SET quantite = ? WHERE code = ?",
            (produit.quantite, produit.code_prod)
        )
        conn.commit()
        conn.close()

    # ----------------------------
    # COMMANDES
    # ----------------------------

    def ajouter_commande(self, commande):
        if commande.valide:
            self.commandes.append(commande)
            self.mettre_a_jour_stock(commande.produit)
            facture = Facture(commande)
            self.factures.append(facture)
            return True
        return False

    def supprimer_commande(self, code_cmd):
        for i, cmd in enumerate(self.commandes):
            if cmd.code_cmd == code_cmd:
                self.historique.append(self.commandes.pop(i))
                return True
        return False

    # ----------------------------
    # STATISTIQUES
    # ----------------------------

    def statistiques_produits(self):
        stats = {}
        for cmd in self.commandes + self.historique:
            nom = cmd.produit.nom_prod
            stats[nom] = stats.get(nom, 0) + cmd.quantite_cmd
        return stats


# ==============================================================
# FACTURE PDF
# ==============================================================

def generer_facture_pdf(facture, dossier="factures"):
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    nom_fichier = f"{dossier}/facture_{facture.code_cmd}.pdf"
    c = canvas.Canvas(nom_fichier, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "FACTURE")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 110, f"Commande : {facture.code_cmd}")
    c.drawString(50, height - 140, f"Produit : {facture.nom_produit}")
    c.drawString(50, height - 170, f"Quantité : {facture.quantite}")
    c.drawString(50, height - 200, f"Prix unitaire : {facture.prix_unitaire} DT")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 250, f"TOTAL : {facture.total} DT")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 40, "Application de Gestion de Stock - Python / SQLite")

    c.save()
    return nom_fichier
