import streamlit as st
import fitz  # PyMuPDF
import json
import requests
from pathlib import Path
import re

OLLAMA_URL = "http://48.220.32.10:11434/api/generate"
MODEL_NAME = "mistral"

def extract_text_from_pdf_file(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
    return text

def detect_document_type(text):
    prompt = f"""
Tu es un assistant qui détecte le type de document parmi :
- fiche de paie
- contrat de travail
- relevé de compte bancaire

Lis le texte suivant et retourne un seul mot parmi ces choix :
"fiche_de_paie", "contrat_de_travail", "releve_bancaire".

Ne retourne rien d'autre que ce mot.

Texte :
{text}
"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip().replace('"', '').replace("'", "").lower()

def analyze_fiche_de_paie(text):
    prompt = f"""
Lis ce texte issu d'une fiche de paie et retourne un JSON avec :
- nom
- prénom
- poste
- entreprise
- salaire net (ou net à payer)
- période (mois et année)

Si un champ est absent, mets null.

Format :
{{
  "nom": "...",
  "prenom": "...",
  "poste": "...",
  "entreprise": "...",
  "salaire": 2500,
  "periode": "Avril 2025"
}}

Texte :
{text}
"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return json.loads(response.json()["response"])

def analyze_contrat(text):
    prompt = f"""
Lis ce contrat de travail et retourne un JSON avec :
- nom
- prénom
- poste
- entreprise
- salaire brut mensuel

Format :
{{
  "nom": "...",
  "prenom": "...",
  "poste": "...",
  "entreprise": "...",
  "salaire_brut": 3200
}}

Texte :
{text}
"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return json.loads(response.json()["response"])

def analyze_releve_bancaire(text, entreprise):
    prompt = f"""
Lis ce relevé bancaire et identifie les virements reçus de l'entreprise **{entreprise}** (ou avec une référence salaire).

Retourne une liste JSON des montants trouvés (en euros), un pour chaque mois si possible.

Format :
[2500.00, 2550.00, 2600.00]

Texte :
{text}
"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    try:
        return json.loads(response.json()["response"])
    except json.JSONDecodeError:
        return []

def save_to_db(data, db_path="data/json/db.json"):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with open(path, "r") as f:
            db = json.load(f)
    else:
        db = []
    db.append(data)
    with open(path, "w") as f:
        json.dump(db, f, indent=2)

# ---------------- Interface ----------------

st.set_page_config(page_title="📊 Analyse de Documents Financiers", layout="centered")
st.title("📊 Analyse de Fiches de Paie & Justificatifs")

st.markdown("""
Déposez **au moins 3 fiches de paie**, et éventuellement :
- un **contrat de travail**
- un ou plusieurs **relevés bancaires**

L'application :
- Détecte automatiquement le type de chaque document
- Vérifie les salaires bruts/nets
- Calcule la capacité d’emprunt
- Génère un résumé intelligent
""")

uploaded_files = st.file_uploader("📥 Déposez vos fichiers PDF", type=["pdf"], accept_multiple_files=True)
loan_years = st.slider("📆 Durée de l'emprunt (années)", 5, 30, 20)

if uploaded_files and st.button("🔍 Analyser"):
    fiches_de_paie, contrats, releves = [], [], []
    types_detectes = []

    for file in uploaded_files:
        text = extract_text_from_pdf_file(file)
        with st.expander(f"📝 {file.name} - contenu extrait"):
            st.text(text)

        doc_type = detect_document_type(text)
        types_detectes.append(doc_type)
        st.info(f"📄 Type détecté : **{doc_type}**")

        if doc_type == "fiche_de_paie":
            fiches_de_paie.append(text)
        elif doc_type == "contrat_de_travail":
            contrats.append(text)
        elif doc_type == "releve_bancaire":
            releves.append(text)
        else:
            st.warning(f"❌ Type non reconnu : {file.name} (détection = {doc_type})")

    if len(fiches_de_paie) < 3:
        st.error("❌ Il faut au moins 3 fiches de paie pour continuer.")
        st.stop()

    # Analyse fiches de paie
    paie_data, periodes, salaires_nets = [], [], []
    for text in fiches_de_paie:
        data = analyze_fiche_de_paie(text)
        paie_data.append(data)
        if data.get("periode"):
            periodes.append(data["periode"])
        if data.get("salaire"):
            salaires_nets.append(float(data["salaire"]))

    salaire_moyen = round(sum(salaires_nets) / len(salaires_nets), 2)
    mensualite = round(salaire_moyen * 0.33, 2)
    montant_total = round(mensualite * 12 * loan_years, 2)

    verifie = "non"
    raison_non_verifie = "Aucune correspondance trouvée avec les relevés ou contrats."

    identite = paie_data[0]
    nom_complet = f"{identite['prenom']} {identite['nom']}".strip()

    for contrat_text in contrats:
        contrat = analyze_contrat(contrat_text)
        salaire_brut = contrat.get("salaire_brut")
        if salaire_brut:
            for salaire_net in salaires_nets:
                salaire_base_estime = round(salaire_net / 0.77, 2)  # estimation du brut
                ecart = abs(salaire_brut - salaire_base_estime)
                if ecart <= 200:
                    verifie = "oui"
                    raison_non_verifie = ""
                    break
            if verifie == "oui":
                break
            else:
                raison_non_verifie = f"Écart trop grand entre salaire brut du contrat ({salaire_brut}) et base estimée ({salaire_base_estime})."

    if verifie == "non" and releves:
        for rel in releves:
            montants_detectes = analyze_releve_bancaire(rel, identite['entreprise'])
            if montants_detectes:
                fiche_verifiee = False
                for salaire_net in salaires_nets:
                    if any(abs(float(montant) - salaire_net) < 50 for montant in montants_detectes):
                        verifie = "oui"
                        raison_non_verifie = ""
                        fiche_verifiee = True
                        break
                if fiche_verifiee:
                    break
            else:
                raison_non_verifie = "Aucun virement correspondant au salaire net trouvé dans les relevés."

    data_finale = {
        "nom_complet": nom_complet,
        "poste": identite.get("poste"),
        "entreprise": identite.get("entreprise"),
        "salaire": salaire_moyen,
        "mensualite_max": mensualite,
        "montant_max_empruntable": montant_total,
        "duree_emprunt_annees": loan_years,
        "verifie": verifie
    }

    resume = (
        f"Les documents reçus comprennent : {types_detectes.count('fiche_de_paie')} fiches de paie, "
        f"{types_detectes.count('contrat_de_travail')} contrat(s), "
        f"{types_detectes.count('releve_bancaire')} relevé(s) bancaire(s).\n"
        f"Employé : **{nom_complet}**, poste : **{data_finale['poste']}**, entreprise : **{data_finale['entreprise']}**.\n"
        f"Périodes couvertes : **{', '.join(sorted(set(periodes)))}**.\n"
        f"✅ Données vérifiées : **{verifie.upper()}**."
    )
    if verifie == "non":
        resume += f"\n❌ Raison : {raison_non_verifie}"

    st.success("✅ Analyse complète réalisée !")
    st.json(data_finale)
    st.markdown("🧾 **Résumé global :**")
    st.markdown(resume)

    save_to_db(data_finale)

    import pandas as pd


    csv_data = pd.DataFrame([data_finale]).to_csv(index=False).encode("utf-8")
    json_data = json.dumps(data_finale, indent=2).encode("utf-8")

    st.download_button("📄 Télécharger les résultats (CSV)", data=csv_data, file_name="resultats.csv", mime="text/csv")
    st.download_button("🗂 Télécharger les résultats (JSON)", data=json_data, file_name="resultats.json",
                       mime="application/json")

