import streamlit as st
from gestion_stock import Produit, Commande, GestionStock, generer_facture_pdf

# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Gestion de Stock",
    page_icon="📦",
    layout="wide"
)

# ============================================================
# DESIGN GLOBAL (CSS UNIQUE)
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc, #eef2ff);
}

/* TITRES */
h1, h2, h3 {
    color: #1e3a8a;
    font-weight: 700;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #eef2ff;
}

/* CARTES */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* PRODUIT */
.product-title {
    font-size: 20px;
    font-weight: bold;
    color: #1e40af;
}
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    color: white;
}
.badge-stock {
    background-color: #16a34a;
}
.badge-low {
    background-color: #dc2626;
}

/* BOUTONS */
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #1e40af);
    color: white;
    border-radius: 10px;
    padding: 10px 26px;
    font-weight: bold;
    border: none;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #1e40af, #1e3a8a);
}

/* TOTAL */
.total {
    font-size: 22px;
    font-weight: bold;
    color: #2563eb;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALISATION
# ============================================================

if "gs" not in st.session_state:
    st.session_state.gs = GestionStock()

gs = st.session_state.gs

# ============================================================
# HEADER
# ============================================================

st.title("📦 Application de Gestion de Stock")
st.markdown("Application web de gestion des **produits, commandes, factures et statistiques**")

col1, col2, col3 = st.columns(3)
col1.metric("📦 Produits", len(gs.produits))
col2.metric("🛒 Commandes", len(gs.commandes))
col3.metric("🧾 Factures", len(gs.factures))

# ============================================================
# MENU
# ============================================================

menu = st.sidebar.radio(
    "Navigation",
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

    col1, col2, col3 = st.columns(3)
    with col1:
        code = st.number_input("Code produit", step=1)
        nom = st.text_input("Nom du produit")
    with col2:
        qte = st.number_input("Quantité", step=1)
        prix = st.number_input("Prix unitaire (DT)", step=0.1)
    with col3:
        desc = st.text_area("Description")

    if st.button("Ajouter le produit"):
        p = Produit(int(code), nom, desc, int(qte), float(prix))
        if gs.ajouter_produit(p):
            st.success("✅ Produit ajouté avec succès")
        else:
            st.error("❌ Code produit déjà existant")

# ============================================================
# AFFICHER PRODUITS (⭐ STAR DU DESIGN ⭐)
# ============================================================

elif menu == "📋 Afficher produits":
    st.subheader("📦 Stock des produits")

    if not gs.produits:
        st.info("Aucun produit en stock")
    else:
        cols = st.columns(3)
        for i, p in enumerate(gs.produits):
            badge = "badge-stock" if p.quantite > 5 else "badge-low"
            stock_txt = "Stock OK" if p.quantite > 5 else "Stock faible"

            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <div class="product-title">📦 {p.nom_prod}</div>
                    <p>{p.description}</p>
                    <span class="badge {badge}">{stock_txt}</span>
                    <hr>
                    <b>Code :</b> {p.code_prod}<br>
                    <b>Quantité :</b> {p.quantite}<br>
                    <b>Prix :</b> {p.prix_unit} DT
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# AJOUT COMMANDE
# ============================================================

elif menu == "🛒 Ajouter commande":
    st.subheader("🛒 Ajouter une commande")

    col1, col2, col3 = st.columns(3)
    with col1:
        code_cmd = st.number_input("Code commande", step=1)
    with col2:
        code_prod = st.number_input("Code produit", step=1)
    with col3:
        qte = st.number_input("Quantité commandée", step=1)

    if st.button("Valider la commande"):
        produit = next((p for p in gs.produits if p.code_prod == code_prod), None)
        if produit:
            cmd = Commande(int(code_cmd), produit, int(qte))
            if gs.ajouter_commande(cmd):
                st.success("✅ Commande validée et facture créée")
            else:
                st.error("❌ Code commande déjà utilisé ou stock insuffisant")
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
        for cmd in gs.commandes:
            st.markdown(f"""
            <div class="card">
                🟢 <b>{cmd.produit.nom_prod}</b><br>
                Quantité : {cmd.quantite_cmd}<br>
                Total : {cmd.calculer_total()} DT
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FACTURES
# ============================================================

elif menu == "🧾 Factures":
    st.subheader("🧾 Factures")

    if not gs.factures:
        st.info("Aucune facture disponible")
    else:
        for f in gs.factures:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h3>🧾 Facture #{f.code_cmd}</h3>
                    Produit : {f.nom_produit}<br>
                    Quantité : {f.quantite}<br>
                    Prix unitaire : {f.prix_unitaire} DT
                    <div class="total">TOTAL : {f.total} DT</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button(f"📄 PDF {f.code_cmd}"):
                    path = generer_facture_pdf(f)
                    with open(path, "rb") as file:
                        st.download_button(
                            "⬇ Télécharger",
                            file,
                            file_name=f"facture_{f.code_cmd}.pdf",
                            mime="application/pdf"
                        )

# ============================================================
# STATISTIQUES
# ============================================================

elif menu == "📊 Statistiques":
    st.subheader("📊 Statistiques des ventes")

    stats = gs.statistiques_produits()
    if stats:
        st.bar_chart(stats)
    else:
        st.info("Aucune donnée disponible")
