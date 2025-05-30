def classify_text(text):
    if "Salaire" in text:
        return "Bulletin de paie"
    elif "Crédit" in text:
        return "Relevé bancaire"
    elif "Employeur" in text:
        return "Certificat de salaire"
    else:
        return "Inconnu"