"""
Compute KPIs: scoring, ranking, and derived indicators.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "scoring_config.json"


def load_scoring_config() -> dict:
    """Load scoring weights from config file."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_parkshare_score(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Compute the Parkshare potential score per arrondissement.
    
    Formula:
        score = w1*norm_density + w2*norm_collective + w3*norm_parking_pressure + w4*norm_motorization
    """
    if config is None:
        config = load_scoring_config()
    
    weights = config["weights"]
    
    df["score_parkshare"] = (
        weights["densite_population"] * df["norm_densite_population"]
        + weights["part_logements_collectifs"] * df["norm_part_logements_collectifs"]
        + weights["pression_stationnement"] * df["norm_pression_stationnement"]
        + weights["taux_motorisation"] * df["norm_taux_motorisation"]
    )
    
    # Re-normalize final score to 0-100
    min_s = df["score_parkshare"].min()
    max_s = df["score_parkshare"].max()
    if max_s > min_s:
        df["score_parkshare"] = ((df["score_parkshare"] - min_s) / (max_s - min_s)) * 100
    
    # Round for readability
    df["score_parkshare"] = df["score_parkshare"].round(1)
    
    return df


def compute_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Compute ranking based on Parkshare score."""
    df["rang"] = df["score_parkshare"].rank(ascending=False, method="min").astype(int)
    return df.sort_values("rang")


def compute_parking_pressure_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 3: Indice de pression de stationnement.
    Already in raw data, re-normalized for consistency.
    """
    df["kpi_pression_stationnement"] = df["norm_pression_stationnement"].round(1)
    return df


def compute_residential_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 4: Densité résidentielle (logements collectifs par km²).
    """
    min_val = df["densite_logements_collectifs"].min()
    max_val = df["densite_logements_collectifs"].max()
    if max_val > min_val:
        df["kpi_densite_residentielle"] = (
            (df["densite_logements_collectifs"] - min_val) / (max_val - min_val) * 100
        ).round(1)
    else:
        df["kpi_densite_residentielle"] = 50.0
    return df


def compute_all_kpis(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Main KPI computation entry point.
    
    Returns DataFrame with all KPIs computed.
    """
    print("📊 Computing KPIs...")
    
    df = compute_parkshare_score(df, config)
    print("   ✓ Score Parkshare computed")
    
    df = compute_rankings(df)
    print("   ✓ Rankings computed")
    
    df = compute_parking_pressure_index(df)
    print("   ✓ Indice pression stationnement computed")
    
    df = compute_residential_density(df)
    print("   ✓ Densité résidentielle computed")
    
    return df


if __name__ == "__main__":
    from ingest import ingest_all
    from transform import transform_all
    raw = ingest_all()
    processed = transform_all(raw)
    final = compute_all_kpis(processed)
    print(f"\n✅ KPIs computed for {len(final)} arrondissements")
    print(final[["nom", "score_parkshare", "rang", "kpi_pression_stationnement", "kpi_densite_residentielle"]].to_string())
