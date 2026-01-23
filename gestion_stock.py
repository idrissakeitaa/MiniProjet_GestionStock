from database import get_connection, creer_tables
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# ==============================================================
# CLASSES MÉTIER
# ==============================================================

class Produit:
    def __init__(self, code, nom, description, quantite, prix):
        self.code_prod = code
        self.nom_prod = nom
        self.description = description
        self.quantite = quantite
        self.prix_unit = prix

    def retirer_stock(self, qte):
        if qte <= self.quantite:
            self.quantite -= qte
            return True
        return False


class Commande:
    def __init__(self, code_cmd, produit, quantite):
        self.code_cmd = code_cmd
        self.produit = produit
        self.quantite_cmd = quantite

    def calculer_total(self):
        return self.quantite_cmd * self.produit.prix_unit


class Facture:
    def __init__(self, commande):
        self.code_cmd = commande.code_cmd
        self.nom_produit = commande.produit.nom_prod
        self.quantite = commande.quantite_cmd
        self.prix_unitaire = commande.produit.prix_unit
        self.total = commande.calculer_total()


# ==============================================================
# GESTION DU STOCK (SQLITE)
# ==============================================================

class GestionStock:
    def __init__(self):
        creer_tables()

        self.produits = []
        self.commandes = []
        self.historique = []
        self.factures = []

        self.charger_produits()
        self.charger_commandes()
        self.charger_historique()
        self.reconstruire_factures()

    # ---------------- PRODUITS ----------------

    def charger_produits(self):
        self.produits.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM produits")
        for code, nom, desc, qte, prix in cur.fetchall():
            self.produits.append(Produit(code, nom, desc, qte, prix))
        conn.close()

    def ajouter_produit(self, produit):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO produits VALUES (?, ?, ?, ?, ?)",
                (
                    produit.code_prod,
                    produit.nom_prod,
                    produit.description,
                    produit.quantite,
                    produit.prix_unit
                )
            )
            conn.commit()
            self.produits.append(produit)
            return True
        except:
            return False
        finally:
            conn.close()

    def mettre_a_jour_stock(self, produit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE produits SET quantite = ? WHERE code = ?",
            (produit.quantite, produit.code_prod)
        )
        conn.commit()
        conn.close()

    # ---------------- COMMANDES ----------------

    def ajouter_commande(self, commande):
        conn = get_connection()
        cur = conn.cursor()

        # Vérifier si le code commande existe déjà
        cur.execute(
            "SELECT code_cmd FROM commandes WHERE code_cmd = ?",
            (commande.code_cmd,)
        )
        if cur.fetchone():
            conn.close()
            return False

        # Vérifier le stock
        if not commande.produit.retirer_stock(commande.quantite_cmd):
            conn.close()
            return False

        total = commande.calculer_total()

        # Insérer la commande
        cur.execute(
            "INSERT INTO commandes VALUES (?, ?, ?, ?)",
            (
                commande.code_cmd,
                commande.produit.code_prod,
                commande.quantite_cmd,
                total
            )
        )

        conn.commit()
        conn.close()

        # Mise à jour mémoire + base
        self.mettre_a_jour_stock(commande.produit)
        self.commandes.append(commande)
        self.factures.append(Facture(commande))

        return True

    # ---------------- CHARGEMENT ----------------

    def charger_commandes(self):
        self.commandes.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM commandes")
        for code_cmd, code_prod, qte, total in cur.fetchall():
            produit = next(
                (p for p in self.produits if p.code_prod == code_prod),
                None
            )
            if produit:
                self.commandes.append(Commande(code_cmd, produit, qte))
        conn.close()

    def charger_historique(self):
        self.historique.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM historique")
        for code_cmd, code_prod, qte, total in cur.fetchall():
            produit = next(
                (p for p in self.produits if p.code_prod == code_prod),
                None
            )
            if produit:
                self.historique.append(Commande(code_cmd, produit, qte))
        conn.close()

    def reconstruire_factures(self):
        self.factures.clear()
        for cmd in self.commandes:
            self.factures.append(Facture(cmd))

    # ---------------- STATISTIQUES ----------------

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

    path = f"{dossier}/facture_{facture.code_cmd}.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "FACTURE")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, f"Commande : {facture.code_cmd}")
    c.drawString(50, height - 150, f"Produit : {facture.nom_produit}")
    c.drawString(50, height - 180, f"Quantité : {facture.quantite}")
    c.drawString(50, height - 210, f"Prix unitaire : {facture.prix_unitaire} DT")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 260, f"TOTAL : {facture.total} DT")

    c.save()
    return path
