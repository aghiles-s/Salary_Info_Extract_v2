
# 💼 Salary_Info_Extract_v2

**Analyse intelligente de documents financiers**  
Automatise l'extraction de données clés à partir de bulletins de paie, relevés bancaires et certificats de salaire. L'application repose sur un modèle LLM (Mistral via Ollama) déployé en local, et une interface web Streamlit déployée sur Azure.

---

## 🚀 Fonctionnalités

- 📄 Chargement de fichiers PDF
- 🧠 Extraction d'entités avec modèle Mistral local (Ollama)
- 🔍 Comparaison automatique entre documents financiers
- 📊 Visualisation des résultats dans une interface web
- 🌐 Déploiement cloud sécurisé (VM + App Service Azure)

---

## 🧰 Technologies utilisées

| Composant        | Usage                            |
|------------------|----------------------------------|
| Python           | Langage principal                |
| Streamlit        | Interface utilisateur web        |
| Ollama + Mistral | Extraction via LLM local         |
| PyPDF2           | Lecture de contenu PDF           |
| Azure VM         | Hôte du modèle Ollama            |
| Azure App Service| Interface Streamlit              |
| GitHub Actions   | CI/CD automatique                |

---

## 📂 Structure du projet

```plaintext
Salary_Info_Extract_v2/
├── app/
│   ├── ingestion.py         # Lecture PDF
│   ├── classifier.py        # Règles de classification
│   ├── ollama_extractor.py  # Extraction d'entités via LLM
│   ├── comparator.py        # Comparaison des données extraites
│   └── utils.py             # Validation des données
│
├── interface/
│   └── main.py              # Application Streamlit
│
├── .github/workflows/
│   └── deploy.yml           # Déploiement CI/CD
├── data/                    # Dossiers pour fichiers temporaires
├── requirements.txt
└── README.md
```

---

## 📦 Installation

### Prérequis
- Python ≥ 3.10
- Ollama installé (`https://ollama.com`)
- Azure CLI (optionnel)

### Installation
```bash
git clone https://github.com/votre-utilisateur/Salary_Info_Extract_v2.git
cd Salary_Info_Extract_v2
pip install -r requirements.txt
```

---

## ▶️ Utilisation

### Lancer le modèle localement :
```bash
ollama run mistral
```

### Lancer l’interface Streamlit :
```bash
streamlit run interface/main.py
```

---

## 🌐 Déploiement Azure

- Le modèle Mistral est hébergé dans une **VM Azure Linux** (via Ollama)
- L’application Streamlit est déployée via **Azure App Service**
- CI/CD configuré via **GitHub Actions**

---

## 🔒 Sécurité

- Traitement **local et sécurisé dans Azure**
- Aucune dépendance à des APIs cloud externes
- Données personnelles non transférées hors de l’environnement

---

## ✅ Tests

- Tests sur 10 documents : extraction > 90% de précision
- Comparaison automatique validée
- Interface web fonctionnelle

---

## 🛠 À venir

- Dashboard analytique
- Export CSV/JSON automatisé depuis l’interface
- Historique des traitements
- Support multilingue

---

## 📄 Licence

MIT – open source, libre d’utilisation et de modification.

---

## 👥 Auteurs

Projet réalisé dans le cadre du Mastère Sup de Vinci 2025.
