import streamlit as st
import fitz  # PyMuPDF
import os
import json
import requests
from pathlib import Path

OLLAMA_URL = "http://48.220.32.10:11434/api/generate"
MODEL_NAME = "mistral"

def extract_text_from_pdf_file(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
    return text

def analyze_text_with_ollama(text):
    prompt = f"""
    Tu es un assistant expert en lecture de fiches de paie.

    Analyse le texte ci-dessous et retourne un JSON avec les champs suivants **seulement s'ils sont clairement présents** :
    - nom
    - prénom
    - poste
    - entreprise
    - salaire net (ou net à payer)
    

    ⚠️ Très important :
    - N'invente jamais d'information.
    - Si un champ est absent ou ambigu, mets `null` ou ne l'inclus pas dans le JSON.
    - Le champ "salaire" doit être un nombre sans texte (ex: 2450, pas "2450 euros").
    - Identifier le **salaire net** même s’il est appelé autrement : "Net payé en euros", "Net à payer", "Salaire net", "Salaire net à payer", "Rémunération nette", etc.Si plusieurs valeurs similaires existent, prends celle qui est la **plus proche du montant réellement versé au salarié**.

    Retourne uniquement un objet JSON comme ci-dessous :

    {{
      "nom": "...",
      "prenom": "...",
      "poste": "...",
      "entreprise": "...",
      "salaire": 2450
    }}
    - N'invente jamais d'information.
    
    Voici le texte extrait :
    {text}
    """

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    response.raise_for_status()
    generated = response.json()["response"]

    try:
        data = json.loads(generated)
    except json.JSONDecodeError:
        st.error("Erreur de parsing JSON : réponse Mistral invalide.")
        st.code(generated)
        return None

    return data

def save_to_db(data, db_path="data/json/db.json"):
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    if db_file.exists():
        with open(db_file, "r") as f:
            db = json.load(f)
    else:
        db = []

    db.append(data)

    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)

# ---------- Interface Streamlit ----------

st.set_page_config(page_title="📊 Analyse de documents financiers", layout="centered")

st.title("📊 Analyse de Fiches de Paie & Simulation d'Emprunt")

st.markdown("""
Déposez jusqu'à **5 fichiers PDF** (fiches de paie, relevés bancaires, etc.).  
Puis cliquez sur **Analyser** pour :
- Extraire les informations clés
- Calculer votre capacité d'emprunt mensuelle et totale
""")

uploaded_files = st.file_uploader(
    "📥 Déposer vos documents ici (max 5)",
    type=["pdf"],
    accept_multiple_files=True
)

# Slider pour durée d'emprunt
loan_years = st.slider(
    "📆 Choisissez la durée de l'emprunt (en années)",
    min_value=5,
    max_value=30,
    value=20,
    step=1
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ Vous avez déposé plus de 5 fichiers. Seuls les 5 premiers seront analysés.")
        uploaded_files = uploaded_files[:5]

    if st.button("🔍 Analyser"):
        for i, file in enumerate(uploaded_files, 1):
            st.markdown(f"---\n### 📄 Document {i}: `{file.name}`")

            try:
                text = extract_text_from_pdf_file(file)
                with st.expander("📝 Voir le texte brut extrait du PDF"):
                    st.text(text)
                data = analyze_text_with_ollama(text)

                if data:
                    # 🔢 Calcul local : mensualité & montant max
                    try:
                        salaire = float(data.get("salaire", 0))
                        mensualite = round(salaire * 0.33, 2)
                        montant_total = round(mensualite * 12 * loan_years, 2)

                        # Construire nom complet
                        nom = data.get("nom", "")
                        prenom = data.get("prenom", "")
                        nom_complet = f"{prenom} {nom}".strip()

                        # Préparer structure finale pour db.json
                        data_finale = {
                            "nom_complet": nom_complet if nom_complet else None,
                            "poste": data.get("poste"),
                            "entreprise": data.get("entreprise"),
                            "salaire": salaire,
                            "mensualite_max": mensualite,
                            "montant_max_empruntable": montant_total,
                            "duree_emprunt_annees": loan_years
                        }

                        st.success("✅ Données extraites avec succès !")
                        st.json(data_finale)

                        save_to_db(data_finale)

                        st.info(f"📈 Mensualité max : **{mensualite} €**")
                        st.info(f"🏦 Montant max empruntable sur {loan_years} ans : **{montant_total} €**")

                    except (ValueError, TypeError):
                        st.warning("⚠️ Salaire manquant ou invalide, calcul non effectué.")
                else:
                    st.error("❌ Échec de l'extraction pour ce fichier.")

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement : {e}")
