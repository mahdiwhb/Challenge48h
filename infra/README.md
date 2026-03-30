# Infrastructure — Parkshare

## Architecture

```
Client (Browser)
     │
     ▼
   Nginx (:80)
     │
     ├── /        → Frontend (React static files)
     └── /api/*   → Backend (FastAPI :8000)
```

## Components

| Service | Port | Description |
|---------|------|-------------|
| nginx | 80 | Reverse proxy + static frontend |
| backend | 8000 | FastAPI application |
| frontend | - | Built at image creation, served by nginx |

## Deployment

### Quick Start
```bash
docker compose up --build -d
```

### With seed data
```bash
docker compose run --rm backend python -m data.scripts.seed_database
docker compose up -d
```

## Variables d'environnement

Voir `.env.example` à la racine du projet.

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_MODE` | demo / production | demo |
| `DATABASE_URL` | SQLite connection string | sqlite:///./data/parkshare.db |
| `WEIGHT_*` | Scoring weights | see .env.example |
| `LLM_API_KEY` | Optional LLM key for chatbot | (empty) |

## Reverse Proxy

Nginx is configured to:
- Serve the React frontend on `/`
- Proxy API requests on `/api/*` to the backend
- Handle CORS and security headers
- WebSocket support for hot reload in dev

## Volumes

- `db-data`: Persists the SQLite database between restarts
