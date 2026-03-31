# 🅿️ Parkshare — Étude de marché Paris

> **Analyse du potentiel commercial de Parkshare par arrondissement de Paris**

Plateforme d'étude de marché pour identifier les zones géographiques à fort potentiel pour Parkshare, une application de partage de places de stationnement entre résidents d'une même copropriété.

![Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Stack](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Stack](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Stack](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Stack](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## 🚀 Lancement rapide

```bash
# 1. Cloner et configurer
cp .env.example .env

# 2. Construire et seeder
docker compose build
docker compose run --rm backend python -m data.scripts.seed_database

# 3. Démarrer
docker compose up -d
```

---

## Commandes utiles : 

```bash
# Seed bdd
python -m data.scripts.seed_database

# launch backend
python -m uvicorn app.backend.app.main:app --host 0.0.0.0 --port 8000

# laucnch fronted
cd app\frontend
npm run dev
```

---

**Accès :**
- 🖥️ Dashboard : [http://localhost](http://localhost)
- 📡 API : [http://localhost/api/docs](http://localhost/api/docs)
- ❤️ Health : [http://localhost/api/health](http://localhost/api/health)

---

## 📋 Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🗺️ **Carte interactive** | Choroplèthe Paris par arrondissement avec hover/clic |
| 📊 **Score de potentiel** | Score composite 0-100 par arrondissement |
| 🏆 **Classement** | Ranking des 20 arrondissements avec tri/filtres |
| 📈 **KPIs** | 4 indicateurs clés : score, pression stationnement, densité, motorisation |
| 🔗 **Corrélations** | Heatmap + scatter plot interactif |
| 💬 **Chatbot** | Assistant analytique rule-based |
| ⚙️ **Pipeline** | Pipeline data automatisable avec monitoring |
| 📥 **Exports** | CSV et JSON téléchargeables |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           Nginx (:80)               │
│   Reverse Proxy + Static Frontend   │
├──────────────┬──────────────────────┤
│   Frontend   │      /api/*          │
│   React/TS   │   FastAPI (:8000)    │
│   Vite       │   SQLAlchemy         │
│   Leaflet    │   Pydantic           │
│   Plotly     │       │              │
│              │   SQLite             │
└──────────────┴──────────────────────┘
        ↑
  Data Pipeline (Python/Pandas)
  Ingest → Transform → KPIs → Store
```

---

## 📁 Structure du projet

```
parkshare/
├── data/
│   ├── raw/                    # Données brutes (seed CSV + GeoJSON)
│   ├── processed/              # Données transformées
│   ├── scripts/                # Pipeline Python
│   │   ├── ingest.py           # Ingestion des sources
│   │   ├── transform.py        # Nettoyage et normalisation
│   │   ├── compute_kpis.py     # Calcul des scores et KPIs
│   │   ├── compute_correlations.py
│   │   ├── run_pipeline.py     # Orchestrateur
│   │   └── seed_database.py    # Script de seed SQLite
│   └── scoring_config.json     # Pondérations paramétrables
│
├── app/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app
│   │   │   ├── api/            # Routes (health, kpis, map, chatbot...)
│   │   │   ├── core/           # Configuration
│   │   │   ├── db/             # Database connection
│   │   │   └── schemas/        # Pydantic models
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx         # Layout principal
│       │   ├── api.ts          # Service API
│       │   ├── pages/          # Overview, Map, Rankings, Correlations, Chatbot
│       │   └── index.css       # Styles
│       ├── package.json
│       └── Dockerfile
│
├── infra/
│   ├── nginx.conf              # Reverse proxy config
│   ├── Dockerfile.nginx        # Frontend build + Nginx
│   └── README.md
│
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

---

## 📊 Méthodologie de scoring

### Variables utilisées

| Variable | Poids | Justification |
|---|---|---|
| Densité de population | 25% | Plus de résidents = plus de demande potentielle |
| Part de logements collectifs | 25% | Copropriétés = cible directe de Parkshare |
| Pression de stationnement | 30% | Fort manque de places = besoin de partage |
| Taux de motorisation | 20% | Plus de véhicules = plus de places nécessaires |

### Formule

```
score = w₁ × norm(densité) + w₂ × norm(% collectif) + w₃ × norm(pression) + w₄ × norm(motorisation)
```

- Chaque variable est normalisée en [0, 100] via min-max scaling
- Le score final est re-normalisé en [0, 100]
- Les poids sont configurables dans `data/scoring_config.json`

### KPIs produits

1. **Score Parkshare** — Score composite de potentiel commercial
2. **Classement** — Rang de chaque arrondissement
3. **Indice de pression de stationnement** — Tension entre demande et offre (normalisé 0-100)
4. **Densité résidentielle** — Densité de logements collectifs par km² (normalisé 0-100)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/arrondissements` | Tous les arrondissements avec scores |
| GET | `/api/arrondissements/{code}` | Détail d'un arrondissement |
| GET | `/api/kpis/summary` | Résumé KPI (top/bottom 5, moyennes) |
| GET | `/api/kpis/rankings` | Classement trié et filtré |
| GET | `/api/kpis/config` | Configuration du scoring |
| GET | `/api/map/geojson` | GeoJSON enrichi avec KPIs |
| GET | `/api/correlations` | Matrice de corrélation |
| GET | `/api/correlations/scatter` | Données scatter plot |
| POST | `/api/pipeline/run` | Relancer le pipeline |
| GET | `/api/pipeline/status` | Statut du dernier pipeline |
| POST | `/api/chatbot/query` | Requête chatbot |

---

## 🗃️ Schéma de base de données

| Table | Description |
|---|---|
| `raw_arrondissements` | Données brutes géographiques |
| `raw_demographics` | Données démographiques brutes |
| `raw_parking` | Données stationnement brutes |
| `processed_arrondissements` | Données transformées et normalisées |
| `kpi_scores` | Scores et KPIs calculés |
| `kpi_rankings` | Classement |
| `correlation_matrix` | Matrice de corrélation |
| `pipeline_runs` | Historique des exécutions pipeline |
| `scoring_config` | Pondérations du scoring |
| `chatbot_logs` | Logs des conversations chatbot |
| `geojson_cache` | Cache GeoJSON |

---

## 🔧 Configuration

### Pondérations du scoring

Modifier `data/scoring_config.json` :

```json
{
  "weights": {
    "densite_population": 0.25,
    "part_logements_collectifs": 0.25,
    "pression_stationnement": 0.30,
    "taux_motorisation": 0.20
  }
}
```

Puis relancer le pipeline :
```bash
docker compose run --rm backend python -m data.scripts.seed_database
```

---

## 🎁 Bonus implémentés

- ✅ **Corrélations** — Heatmap + scatter plot interactif
- ✅ **Automatisation pipeline** — Endpoint API + cron-friendly
- ✅ **Chatbot analytique** — Assistant rule-based, architecture LLM-ready
- ✅ **Export CSV/JSON** — Téléchargement des classements
- ✅ **Sources extensibles** — Architecture prête pour brancher de vraies APIs
- ✅ **Filtres dynamiques** — Tri par KPI, sélection d'indicateur sur la carte

---

## ⚠️ Limites et hypothèses

- Les données seed sont des **estimations réalistes** basées sur des sources publiques (INSEE, Paris Open Data)
- Le GeoJSON est simplifié pour la démo
- Le chatbot fonctionne en mode rule-based (pas de LLM externe requis)
- Le scoring est un modèle simplifié ; en production, on ajouterait des données de terrain

---

## 🚀 Version production

En production, le projet serait amélioré avec :
- Vraies données via API Paris Open Data, INSEE, data.gouv.fr
- GeoJSON officiel haute résolution des arrondissements
- PostgreSQL/PostGIS au lieu de SQLite
- Authentification JWT
- Déploiement cloud (Azure/AWS/GCP)
- CI/CD pipeline
- Monitoring et alerting
- LLM intégré pour le chatbot (GPT-4 / Claude API)

---

## 📝 Choix techniques

| Choix | Justification |
|---|---|
| **SQLite** | Zéro config, fichier unique, idéal pour démo et prototype |
| **FastAPI** | Rapide, moderne, auto-documentation OpenAPI |
| **React + TypeScript** | Standard dashboard, typage fort, écosystème riche |
| **Leaflet** | Carte interactive légère, OpenStreetMap |
| **Plotly** | Graphiques interactifs (heatmap, scatter) |
| **Pandas** | Traitement data standard en Python |
| **Docker Compose** | Déploiement reproductible en une commande |
| **Nginx** | Reverse proxy fiable, sert les fichiers statiques |

---

*Projet réalisé dans le cadre d'un challenge 48h — Mars 2026*