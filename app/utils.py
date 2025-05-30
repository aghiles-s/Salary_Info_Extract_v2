def validate_data_for_comparison(data: dict) -> bool:
    # On accepte soit 'mois' soit 'période'
    periode = data.get("mois") or data.get("période")
    salaire = data.get("salaire_net") or data.get("salaireNet") or data.get("montant_recu")

    return True
