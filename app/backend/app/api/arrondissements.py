"""Arrondissements endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db

router = APIRouter()


@router.get("/arrondissements")
def list_arrondissements(db: Session = Depends(get_db)):
    """List all arrondissements with their scores."""
    rows = db.execute(text("""
        SELECT p.code_arrondissement, p.nom, p.superficie_km2, p.population,
               p.densite_population, p.nb_logements, p.part_logements_collectifs,
               p.nb_voitures, p.taux_motorisation, p.pression_stationnement,
               p.densite_logements_collectifs, p.ratio_vehicules_places,
               k.score_parkshare, k.rang, k.kpi_pression_stationnement, k.kpi_densite_residentielle
        FROM processed_arrondissements p
        JOIN kpi_scores k ON p.code_arrondissement = k.code_arrondissement
        ORDER BY k.rang
    """)).fetchall()
    
    return [dict(row._mapping) for row in rows]


@router.get("/arrondissements/{code}")
def get_arrondissement(code: str, db: Session = Depends(get_db)):
    """Get detailed data for a single arrondissement."""
    row = db.execute(text("""
        SELECT p.*, k.score_parkshare, k.rang,
               k.kpi_pression_stationnement, k.kpi_densite_residentielle
        FROM processed_arrondissements p
        JOIN kpi_scores k ON p.code_arrondissement = k.code_arrondissement
        WHERE p.code_arrondissement = :code
    """), {"code": code}).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Arrondissement {code} not found")
    
    return dict(row._mapping)
