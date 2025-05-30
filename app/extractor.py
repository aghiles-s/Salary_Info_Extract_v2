import requests
import json

OLLAMA_URL = "http://48.220.32.10:11434/api/generate"
MODEL_NAME = "mistral"

PROMPT_TEMPLATE = """
Tu es un assistant qui lit un texte issu d'une fiche de paie, d'un relevé bancaire ou d'un certificat de salaire.
Extrait les informations suivantes si elles sont présentes :
- nom
- employeur
- date ou mois
- salaire brut
- salaire net
Retourne le résultat en JSON avec des clés claires.

Texte :
\"\"\"
{doc}
\"\"\"
"""

def extract_entities(text):
    prompt = PROMPT_TEMPLATE.format(doc=text)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    try:
        output_text = response.json()["response"]
        result = json.loads(output_text)
    except Exception as e:
        print("Erreur de parsing:", e)
        result = {"raw_output": output_text}

    return result
