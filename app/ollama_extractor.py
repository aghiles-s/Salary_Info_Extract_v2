import requests
import json

OLLAMA_URL = "http://48.220.32.10:11434/api/generate"
MODEL_NAME = "mistral"

PROMPT_TEMPLATE = """
Tu es un assistant expert en analyse de documents financiers (comme des fiches de paie, relevés bancaires, certificats de salaire).

Tu reçois le texte brut d’un document PDF. Ton rôle est d’extraire les **informations financières clés** utiles à l’étude de la **capacité de remboursement d’un individu**.

Retourne un objet JSON structuré contenant les champs suivants :

- "nom"
- "employeur"
- "mois" ou "période"
- "salaire_brut"
- "salaire_net" ← correspond à "net à payer"
- "montant_recu" ← montant reçu sur le compte si document bancaire
- "libelle_virement" ← texte associé au salaire sur le relevé
- "iban"

⚠️ Instructions importantes :
- Ne retourne que **le montant net réellement perçu** par la personne.
- Ignore "net imposable", sauf si aucun autre n'est disponible.
- Si plusieurs salaires ou périodes sont présents, extrait **le plus récent**.
- Si une information n’est pas trouvée, indique `null`.

Voici le texte à analyser :
\"\"\"
{doc}
\"\"\"
"""



def extract_entities(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(doc=text)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        raw = response.json().get("response", "")

        # Essayer d'extraire l'objet JSON directement de la réponse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Si le modèle a inclus des commentaires ou du texte autour
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end != -1:
                cleaned = raw[start:end]
                return json.loads(cleaned)
            else:
                return {"error": "JSON introuvable", "raw_output": raw}

    except Exception as e:
        return {"error": str(e)}
