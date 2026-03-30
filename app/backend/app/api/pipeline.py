"""Pipeline management endpoints."""

import subprocess
import sys
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db

router = APIRouter()


def _run_pipeline_task(db_url: str):
    """Background task to run the pipeline."""
    import os
    os.environ["DATABASE_URL"] = db_url
    from data.scripts.seed_database import seed_database
    seed_database()


@router.post("/pipeline/run")
def run_pipeline(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a pipeline re-run."""
    # Record the run as started
    db.execute(text(
        "INSERT INTO pipeline_runs (started_at, mode, status) VALUES (:started, :mode, :status)"
    ), {"started": datetime.now(timezone.utc).isoformat(), "mode": "demo", "status": "running"})
    db.commit()
    
    # Run in background
    from app.backend.app.core.config import settings
    background_tasks.add_task(_run_pipeline_task, settings.database_url)
    
    return {"message": "Pipeline started", "status": "running"}


@router.get("/pipeline/status")
def pipeline_status(db: Session = Depends(get_db)):
    """Get latest pipeline run status."""
    rows = db.execute(text("""
        SELECT id, started_at, finished_at, duration_seconds, mode, status, num_arrondissements
        FROM pipeline_runs ORDER BY id DESC LIMIT 5
    """)).fetchall()
    
    return {
        "runs": [dict(r._mapping) for r in rows],
        "latest": dict(rows[0]._mapping) if rows else None,
    }
