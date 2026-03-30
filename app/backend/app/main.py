"""
Parkshare Market Study — FastAPI Backend
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
# In Docker: __file__ = /app/app/backend/app/main.py → parent x4 = /app
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.backend.app.db.database import init_db
from app.backend.app.api import arrondissements, kpis, map_data, correlations, pipeline, chatbot, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    init_db()
    yield


app = FastAPI(
    title="Parkshare Market Study API",
    description="API pour l'étude de marché Parkshare — Analyse du potentiel commercial par arrondissement de Paris",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(arrondissements.router, prefix="/api", tags=["Arrondissements"])
app.include_router(kpis.router, prefix="/api", tags=["KPIs"])
app.include_router(map_data.router, prefix="/api", tags=["Map"])
app.include_router(correlations.router, prefix="/api", tags=["Correlations"])
app.include_router(pipeline.router, prefix="/api", tags=["Pipeline"])
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
