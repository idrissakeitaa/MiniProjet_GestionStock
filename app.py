import streamlit as st
from gestion_stock import Produit, Commande, GestionStock

# Configuration page
st.set_page_config(
    page_title="Gestion de Stock",
    page_icon="📦",
    layout="centered"
)

# Initialisation du stock (persistant pendant la session)
if "gs" not in st.session_state:
    st.session_state.gs = GestionStock()

gs = st.session_state.gs

st.title("📦 Application de Gestion de Stock")
st.markdown("Interface web pour la gestion des produits et commandes")

menu = st.sidebar.radio(
    "Menu",
    [
        "➕ Ajouter produit",
        "📋 Afficher produits",
        "🛒 Ajouter commande",
        "📜 Historique",
        "📊 Statistiques"
    ]
)

# =========================
# Ajouter produit
# =========================
if menu == "➕ Ajouter produit":
    st.subheader("Ajouter un produit")

    code = st.number_input("Code produit", step=1)
    nom = st.text_input("Nom du produit")
    desc = st.text_area("Description")
    qte = st.number_input("Quantité", step=1)
    prix = st.number_input("Prix unitaire (DT)", step=0.1)

    if st.button("Ajouter le produit"):
        p = Produit(int(code), nom, desc, int(qte), float(prix))
        gs.ajouter_produit(p)
        st.success("Produit ajouté avec succès")

# =========================
# Afficher produits
# =========================
elif menu == "📋 Afficher produits":
    st.subheader("Liste des produits")

    if not gs.produits:
        st.info("Aucun produit en stock")
    else:
        for p in gs.produits:
            st.write(f"**{p.nom_prod}** | Qté: {p.quantite} | Prix: {p.prix_unit} DT")

# =========================
# Ajouter commande
# =========================
elif menu == "🛒 Ajouter commande":
    st.subheader("Ajouter une commande")

    code_cmd = st.number_input("Code commande", step=1)
    code_prod = st.number_input("Code produit", step=1)
    qte = st.number_input("Quantité commandée", step=1)

    if st.button("Valider la commande"):
        produit = next((p for p in gs.produits if p.code_prod == code_prod), None)
        if produit:
            cmd = Commande(int(code_cmd), produit, int(qte))
            gs.ajouter_commande(cmd)
            st.success("Commande traitée")
        else:
            st.error("Produit introuvable")

# =========================
# Historique
# =========================
elif menu == "📜 Historique":
    st.subheader("Historique des commandes")

    if not gs.historique:
        st.info("Historique vide")
    else:
        for cmd in gs.historique:
            st.write(f"{cmd.produit.nom_prod} - {cmd.quantite_cmd} unités")

# =========================
# Statistiques
# =========================
elif menu == "📊 Statistiques":
    st.subheader("Statistiques des ventes")

    stats = {}
    for cmd in gs.commandes + gs.historique:
        nom = cmd.produit.nom_prod
        stats[nom] = stats.get(nom, 0) + cmd.quantite_cmd

    if stats:
        st.bar_chart(stats)
    else:
        st.info("Aucune donnée disponible")
