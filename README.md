# README.md
# Projet : Traitement de documents financiers

## Objectif
Ingestion, OCR, classification et extraction d'informations depuis des documents financiers (PDF, JPG).

## Fonctionnalités
- OCR avec Tesseract
- Classification automatique
- Extraction via regex
- Génération JSON/CSV
- Interface web avec Streamlit
- Déploiement Azure via GitHub Actions

## Exécution locale
```bash
docker build -t document-app .
docker run -p 8501:8501 document-app
```

## CI/CD
- Fichier deploy.yml déclenche le pipeline Azure sur chaque push `main`

## Configuration Azure
- Définir la variable d’environnement `AZURE_STORAGE_CONNECTION_STRING`
- Nommer l’app dans `deploy.yml`

## Auteur
SUP DE VINCI - Groupe Mastère
