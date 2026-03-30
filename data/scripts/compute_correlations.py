"""
Compute correlation matrix between scoring variables.
"""

import pandas as pd
import numpy as np


CORRELATION_VARIABLES = [
    "densite_population",
    "part_logements_collectifs",
    "pression_stationnement",
    "taux_motorisation",
    "densite_logements_collectifs",
    "ratio_vehicules_places",
    "score_parkshare",
]

VARIABLE_LABELS = {
    "densite_population": "Densité population",
    "part_logements_collectifs": "% logements collectifs",
    "pression_stationnement": "Pression stationnement",
    "taux_motorisation": "Taux motorisation",
    "densite_logements_collectifs": "Densité log. collectifs",
    "ratio_vehicules_places": "Ratio véhicules/places",
    "score_parkshare": "Score Parkshare",
}


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation matrix between key variables."""
    available = [v for v in CORRELATION_VARIABLES if v in df.columns]
    corr = df[available].corr().round(3)
    return corr


def get_top_correlations(corr_matrix: pd.DataFrame, n: int = 10) -> list:
    """Get top N strongest correlations (excluding self-correlation)."""
    pairs = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append({
                "var1": cols[i],
                "var2": cols[j],
                "correlation": corr_matrix.iloc[i, j],
                "abs_correlation": abs(corr_matrix.iloc[i, j]),
            })
    
    pairs.sort(key=lambda x: x["abs_correlation"], reverse=True)
    return pairs[:n]


def compute_correlations(df: pd.DataFrame) -> dict:
    """
    Main correlation computation entry point.
    
    Returns dict with matrix and top pairs.
    """
    print("🔗 Computing correlations...")
    
    corr = compute_correlation_matrix(df)
    top = get_top_correlations(corr)
    
    print(f"   ✓ Correlation matrix: {corr.shape[0]}x{corr.shape[1]}")
    print(f"   ✓ Top correlations identified")
    
    return {
        "matrix": corr,
        "top_pairs": top,
        "labels": VARIABLE_LABELS,
    }
