import streamlit as st
from gestion_stock import Produit, Commande, GestionStock
from gestion_stock import generer_facture_pdf


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Gestion de Stock",
    page_icon="📦",
    layout="centered"
)

# ============================================================
# STYLE (DESIGN)
# ============================================================

st.markdown("""
<style>
body {
    background-color: #f8fafc;
}
.card {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}
.title {
    font-weight: bold;
    font-size: 18px;
}
.total {
    color: #2563EB;
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALISATION DU STOCK (SESSION)
# ============================================================

if "gs" not in st.session_state:
    st.session_state.gs = GestionStock()

gs = st.session_state.gs

# ============================================================
# TITRE
# ============================================================

st.title("📦 Application de Gestion de Stock")
st.markdown("Interface web pour la gestion des produits, commandes, factures et statistiques")

# ============================================================
# MENU
# ============================================================

menu = st.sidebar.radio(
    "Menu",
    [
        "➕ Ajouter produit",
        "📋 Afficher produits",
        "🛒 Ajouter commande",
        "📜 Historique",
        "🧾 Factures",
        "📊 Statistiques"
    ]
)

# ============================================================
# AJOUT PRODUIT
# ============================================================

if menu == "➕ Ajouter produit":
    st.subheader("➕ Ajouter un produit")

    col1, col2 = st.columns(2)
    with col1:
        code = st.number_input("Code produit", step=1)
        nom = st.text_input("Nom du produit")
    with col2:
        qte = st.number_input("Quantité", step=1)
        prix = st.number_input("Prix unitaire (DT)", step=0.1)

    desc = st.text_area("Description")

    if st.button("Ajouter le produit"):
        p = Produit(int(code), nom, desc, int(qte), float(prix))
        gs.ajouter_produit(p)
        st.success("✅ Produit ajouté avec succès")

# ============================================================
# AFFICHER PRODUITS
# ============================================================

elif menu == "📋 Afficher produits":
    st.subheader("📦 Stock des produits")

    if not gs.produits:
        st.info("Aucun produit en stock")
    else:
        for p in gs.produits:
            st.markdown(f"""
            <div class="card">
                <div class="title">{p.nom_prod}</div>
                <p>{p.description}</p>
                <b>Quantité :</b> {p.quantite}<br>
                <b>Prix :</b> {p.prix_unit} DT
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# AJOUT COMMANDE
# ============================================================

elif menu == "🛒 Ajouter commande":
    st.subheader("🛒 Ajouter une commande")

    col1, col2 = st.columns(2)
    with col1:
        code_cmd = st.number_input("Code commande", step=1)
        code_prod = st.number_input("Code produit", step=1)
    with col2:
        qte = st.number_input("Quantité commandée", step=1)

    if st.button("Valider la commande"):
        produit = next((p for p in gs.produits if p.code_prod == code_prod), None)
        if produit:
            cmd = Commande(int(code_cmd), produit, int(qte))
            gs.ajouter_commande(cmd)
            if cmd.valide:
                st.success("✅ Commande validée et facture créée")
            else:
                st.error("❌ Stock insuffisant")
        else:
            st.error("❌ Produit introuvable")

# ============================================================
# HISTORIQUE
# ============================================================

elif menu == "📜 Historique":
    st.subheader("📜 Historique des commandes")

    if not gs.commandes and not gs.historique:
        st.info("Aucune commande enregistrée")
    else:
        st.markdown("### 🟢 Commandes actives")
        for cmd in gs.commandes:
            st.markdown(f"""
            <div class="card">
                <b>Produit :</b> {cmd.produit.nom_prod}<br>
                <b>Quantité :</b> {cmd.quantite_cmd}<br>
                <b>Total :</b> {cmd.calculer_total()} DT
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🔴 Commandes supprimées")
        if not gs.historique:
            st.write("Aucune commande supprimée")
        else:
            for cmd in gs.historique:
                st.markdown(f"""
                <div class="card">
                    <b>Produit :</b> {cmd.produit.nom_prod}<br>
                    <b>Quantité :</b> {cmd.quantite_cmd}<br>
                    <b>Total :</b> {cmd.calculer_total()} DT
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# FACTURES
# ============================================================

elif menu == "🧾 Factures":
    st.subheader("🧾 Factures des commandes")

    if not gs.factures:
        st.info("Aucune facture disponible")
    else:
        for f in gs.factures:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="title">Commande n° {f.code_cmd}</div>
                    <b>Produit :</b> {f.nom_produit}<br>
                    <b>Quantité :</b> {f.quantite}<br>
                    <b>Prix unitaire :</b> {f.prix_unitaire} DT<br>
                    <div class="total">TOTAL : {f.total} DT</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"📄 PDF {f.code_cmd}"):
                    chemin = generer_facture_pdf(f)
                    with open(chemin, "rb") as file:
                        st.download_button(
                            label="⬇ Télécharger",
                            data=file,
                            file_name=f"facture_{f.code_cmd}.pdf",
                            mime="application/pdf"
                        )


# ============================================================
# STATISTIQUES
# ============================================================

elif menu == "📊 Statistiques":
    st.subheader("📊 Statistiques des ventes")

    stats = {}
    for cmd in gs.commandes + gs.historique:
        nom = cmd.produit.nom_prod
        stats[nom] = stats.get(nom, 0) + cmd.quantite_cmd

    if stats:
        st.bar_chart(stats)
        st.success("📈 Statistiques mises à jour")
    else:
        st.info("Aucune donnée disponible")
