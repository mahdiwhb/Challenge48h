# Parkshare — Application

## Backend (FastAPI)

**Stack :** Python 3.12, FastAPI, SQLAlchemy, Pydantic, Pandas

### Lancement local (hors Docker)

```bash
cd app/backend
pip install -r requirements.txt
python -m data.scripts.seed_database   # depuis la racine
uvicorn app.main:app --reload --port 8000
```

### Endpoints

- `GET /api/health` — Health check
- `GET /api/arrondissements` — Liste des arrondissements avec scores
- `GET /api/arrondissements/{code}` — Détail d'un arrondissement
- `GET /api/kpis/summary` — KPIs globaux (top/bottom 5, moyennes)
- `GET /api/kpis/rankings?sort_by=&order=&limit=` — Classement filtré
- `GET /api/kpis/config` — Pondérations du scoring
- `GET /api/map/geojson?kpi=` — GeoJSON enrichi des KPIs
- `GET /api/correlations` — Matrice de corrélation
- `GET /api/correlations/scatter?x=&y=` — Données scatter plot
- `POST /api/pipeline/run` — Relancer le pipeline
- `GET /api/pipeline/status` — Statut du dernier run
- `POST /api/chatbot/query` — Requête chatbot (`{ "message": "..." }`)

### Documentation auto

FastAPI génère automatiquement :
- Swagger UI : `/api/docs`
- ReDoc : `/api/redoc`

---

## Frontend (React + TypeScript)

**Stack :** React 18, TypeScript, Vite 5, Leaflet, Plotly

### Lancement local (hors Docker)

```bash
cd app/frontend
npm install
npm run dev
```

Le proxy Vite redirige automatiquement `/api` vers `http://localhost:8000`.

### Pages

| Page | Description |
|---|---|
| **Overview** | KPI cards, top/bottom 5, bar chart, export CSV |
| **Carte** | Choroplèthe Leaflet, filtre KPI, détail au clic |
| **Classement** | Tableau trié, score badges, export CSV/JSON |
| **Corrélations** | Heatmap Plotly + scatter plot interactif |
| **Pipeline** | Admin : relancer pipeline, historique, config |
| **Chatbot** | Chat analytique avec suggestions |
