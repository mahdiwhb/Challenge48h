"""KPI endpoints: summary and rankings."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db

router = APIRouter()


@router.get("/kpis/summary")
def kpi_summary(db: Session = Depends(get_db)):
    """Get KPI summary with top/bottom arrondissements."""
    rows = db.execute(text("""
        SELECT code_arrondissement, nom, score_parkshare, rang,
               kpi_pression_stationnement, kpi_densite_residentielle
        FROM kpi_scores ORDER BY rang
    """)).fetchall()
    
    data = [dict(r._mapping) for r in rows]
    scores = [d["score_parkshare"] for d in data]
    
    return {
        "total_arrondissements": len(data),
        "score_moyen": round(sum(scores) / len(scores), 1) if scores else 0,
        "score_max": max(scores) if scores else 0,
        "score_min": min(scores) if scores else 0,
        "top_5": data[:5],
        "bottom_5": data[-5:][::-1],
        "all_scores": data,
    }


@router.get("/kpis/rankings")
def kpi_rankings(
    sort_by: str = "score_parkshare",
    order: str = "desc",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get arrondissement rankings with optional sorting."""
    # Whitelist of allowed sort columns
    allowed_sorts = {
        "score_parkshare", "rang", "kpi_pression_stationnement",
        "kpi_densite_residentielle", "nom"
    }
    if sort_by not in allowed_sorts:
        sort_by = "score_parkshare"
    
    direction = "DESC" if order == "desc" else "ASC"
    
    rows = db.execute(text(f"""
        SELECT k.rang, k.code_arrondissement, k.nom, k.score_parkshare,
               k.kpi_pression_stationnement, k.kpi_densite_residentielle
        FROM kpi_scores k
        ORDER BY {sort_by} {direction}
        LIMIT :limit
    """), {"limit": limit}).fetchall()
    
    return [dict(r._mapping) for r in rows]


@router.get("/kpis/config")
def scoring_config(db: Session = Depends(get_db)):
    """Get current scoring configuration."""
    rows = db.execute(text("SELECT key, value, description FROM scoring_config")).fetchall()
    return {r[0]: {"weight": r[1], "description": r[2]} for r in rows}
