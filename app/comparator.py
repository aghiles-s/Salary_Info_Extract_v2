import requests

OLLAMA_URL = "http://48.220.32.10:11434/api/generate"
MODEL_NAME = "mistral"

COMPARE_PROMPT_TEMPLATE = """
Tu es un conseiller en crédit qui analyse les revenus d’un individu à partir de deux documents financiers :  
- Une fiche de paie  
- Un relevé bancaire  

🎯 Ton objectif est de :
- Évaluer la **cohérence des revenus déclarés** (salaire net à payer vs montant réellement reçu)
- Vérifier si la personne a des **revenus stables et vérifiables**
- Aider à estimer sa **capacité à obtenir un crédit**

✅ Détail de ce que tu dois faire :
- Compare les **salaires nets** : "salaire_net" (fiche de paie) vs "montant_recu" (relevé bancaire)
- Vérifie que les **périodes/mois** concordent
- Donne un avis sur la **fiabilité des revenus**
- Fournis une **conclusion claire** : 
  - "revenus cohérents et stables"
  - ou "revenus incohérents ou douteux"
  - ou "informations insuffisantes pour conclure"

Voici les données extraites automatiquement :

Document 1 :
{fiche_data}

Document 2 :
{releve_data}

🧠 Fournis une synthèse claire à l’utilisateur (en français), avec des preuves chiffrées, et ta conclusion.
"""


def compare_documents(fiche_data, releve_data):
    prompt = COMPARE_PROMPT_TEMPLATE.format(
        fiche_data=fiche_data,
        releve_data=releve_data
    )
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]
