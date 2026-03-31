from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db

router = APIRouter()

VARIABLE_LABELS = {
    "densite_population": "Densité population",
    "part_logements_collectifs": "% logements collectifs",
    "pression_stationnement": "Pression stationnement",
    "taux_motorisation": "Taux motorisation",
    "densite_logements_collectifs": "Densité log. collectifs",
    "ratio_vehicules_places": "Ratio véhicules/places",
    "score_parkshare": "Score Parkshare",
}


@router.get("/correlations")
def get_correlations(db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT var1, var2, correlation FROM correlation_matrix"
    )).fetchall()
    
    matrix = {}
    variables = set()
    for r in rows:
        var1, var2, corr = r[0], r[1], r[2]
        variables.add(var1)
        variables.add(var2)
        if var1 not in matrix:
            matrix[var1] = {}
        matrix[var1][var2] = corr
    
    variables = sorted(variables)
    
    return {
        "matrix": matrix,
        "variables": variables,
        "labels": VARIABLE_LABELS,
    }


@router.get("/correlations/scatter")
def get_scatter_data(
    var_x: str = "densite_population",
    var_y: str = "score_parkshare",
    db: Session = Depends(get_db),
):
    allowed = {
        "densite_population", "part_logements_collectifs", "pression_stationnement",
        "taux_motorisation", "densite_logements_collectifs", "ratio_vehicules_places",
    }
    
    if var_x not in allowed and var_x != "score_parkshare":
        var_x = "densite_population"
    if var_y not in allowed and var_y != "score_parkshare":
        var_y = "score_parkshare"
    
    rows = db.execute(text(f"""
        SELECT p.code_arrondissement, p.nom, 
               p.{var_x} as x_val, 
               CASE WHEN :var_y = 'score_parkshare' THEN k.score_parkshare ELSE p.{var_y} END as y_val,
               k.score_parkshare, k.rang
        FROM processed_arrondissements p
        JOIN kpi_scores k ON p.code_arrondissement = k.code_arrondissement
    """), {"var_y": var_y}).fetchall()
    
    return {
        "data": [dict(r._mapping) for r in rows],
        "x_label": VARIABLE_LABELS.get(var_x, var_x),
        "y_label": VARIABLE_LABELS.get(var_y, var_y),
    }
