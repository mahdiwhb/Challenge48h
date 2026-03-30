"""Map GeoJSON endpoint with KPI data injected into properties."""

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db

router = APIRouter()


@router.get("/map/geojson")
def get_map_geojson(kpi: str = "score_parkshare", db: Session = Depends(get_db)):
    """
    Get GeoJSON with KPI data in feature properties.
    
    Args:
        kpi: Which KPI to highlight (score_parkshare, kpi_pression_stationnement, kpi_densite_residentielle)
    """
    # Get GeoJSON
    geojson_row = db.execute(text("SELECT geojson_data FROM geojson_cache WHERE id = 1")).fetchone()
    if not geojson_row:
        return {"type": "FeatureCollection", "features": []}
    
    geojson = json.loads(geojson_row[0])
    
    # Get KPI data
    rows = db.execute(text("""
        SELECT k.code_arrondissement, k.score_parkshare, k.rang,
               k.kpi_pression_stationnement, k.kpi_densite_residentielle,
               p.population, p.taux_motorisation, p.densite_population,
               p.part_logements_collectifs, p.pression_stationnement,
               p.nb_voitures, p.nb_logements
        FROM kpi_scores k
        JOIN processed_arrondissements p ON k.code_arrondissement = p.code_arrondissement
    """)).fetchall()
    
    kpi_map = {}
    for r in rows:
        d = dict(r._mapping)
        kpi_map[d["code_arrondissement"]] = d
    
    # Inject KPI data into GeoJSON properties
    for feature in geojson["features"]:
        code = feature["properties"]["code"]
        if code in kpi_map:
            feature["properties"].update(kpi_map[code])
    
    return {
        "geojson": geojson,
        "active_kpi": kpi,
        "kpi_options": [
            {"value": "score_parkshare", "label": "Score Parkshare"},
            {"value": "kpi_pression_stationnement", "label": "Pression stationnement"},
            {"value": "kpi_densite_residentielle", "label": "Densité résidentielle"},
            {"value": "taux_motorisation", "label": "Taux de motorisation"},
            {"value": "densite_population", "label": "Densité de population"},
        ],
    }
