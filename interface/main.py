import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime
from app.ingestion import load_file
from app.ollama_extractor import extract_entities
from app.comparator import compare_documents
from app.utils import validate_data_for_comparison

st.set_page_config(page_title="🧠 Analyse intelligente de documents", layout="centered")
st.title("📁 Analyse automatique de documents financiers")

# Créer les dossiers nécessaires
if not os.path.exists("data/raw"):
    os.makedirs("data/raw")
if not os.path.exists("data/json"):
    os.makedirs("data/json")
if not os.path.exists("data/csv"):
    os.makedirs("data/csv")

st.markdown("""
Déposez jusqu'à **5 fichiers PDF** (fiches de paie, relevés bancaires, etc.).  
Puis cliquez sur **Analyser** pour :
- Détecter les informations clés
- Comparer automatiquement les documents
- Identifier toute incohérence
""")

uploaded_files = st.file_uploader(
    "📥 Déposer vos documents ici (max 5)",
    type=["pdf"],
    accept_multiple_files=True
)

if "docs_data" not in st.session_state:
    st.session_state.docs_data = []

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ Vous ne pouvez charger que 5 documents au maximum.")
    else:
        st.session_state.docs_data = uploaded_files

if st.button("🚀 Analyser les documents") and st.session_state.docs_data:
    st.info("⏳ Traitement en cours... Veuillez patienter.")

    docs_data = []
    for idx, file in enumerate(st.session_state.docs_data):
        try:
            temp_path = f"data/raw/temp_doc_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                st.success(f"✅ Fichier {file.name} chargé avec succès.")
                f.write(file.read())

            text = "\n".join(load_file(temp_path))
            extracted = extract_entities(text)

            docs_data.append({
                "nom": file.name,
                "texte": text,
                "data": extracted
            })

            os.remove(temp_path)
        except Exception as e:
            st.error(f"❌ Erreur avec le fichier {file.name} : {e}")

    # ✅ Affichage du texte extrait + lien de téléchargement
    st.subheader("📄 Textes extraits des documents")
    for doc in docs_data:
        with st.expander(f"Afficher le texte de {doc['nom']}"):
            st.text(doc["texte"])
            file_name_txt = doc["nom"].replace(".pdf", ".txt")
            st.download_button(
                label="📥 Télécharger le texte brut",
                data=doc["texte"],
                file_name=file_name_txt,
                mime="text/plain"
            )

    # Détection des documents valides (au moins salaire + mois/période)
    valid_docs = [
        doc for doc in docs_data
        if validate_data_for_comparison(doc["data"])
    ]

    st.write(f"📊 **Documents valides détectés :** {len(valid_docs)}")

    if len(valid_docs) >= 2:
        doc1 = valid_docs[0]
        doc2 = valid_docs[1]

        st.success("✅ Deux documents comparables détectés. Analyse en cours...")

        result = compare_documents(doc1["data"], doc2["data"])

        st.subheader("🧠 Résultat de la comparaison")
        st.markdown(f"**Analyse :** {result}")

        st.subheader("📌 Preuves détectées :")
        for i, doc in enumerate([doc1, doc2], start=1):
            st.markdown(f"### 📄 Document {i} ({doc['nom']})")
            st.markdown(f"- **Montant détecté :** `{doc['data'].get('salaire_net') or doc['data'].get('montant_recu') or 'N/A'}`")
            st.markdown(f"- **Période :** `{doc['data'].get('mois', 'N/A')}`")
    else:
        st.warning("⚠️ Au moins deux documents valides sont nécessaires pour la comparaison. Veuillez vérifier les données extraites.")