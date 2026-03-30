"""
Ingest raw data from seed CSV files or external sources.
Supports demo mode (seed files) and real mode (API calls).
"""

import os
import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"


def load_seed_arrondissements() -> pd.DataFrame:
    """Load arrondissement base data from seed CSV."""
    return pd.read_csv(RAW_DIR / "seed_arrondissements.csv")


def load_seed_demographics() -> pd.DataFrame:
    """Load demographic data from seed CSV."""
    return pd.read_csv(RAW_DIR / "seed_demographics.csv")


def load_seed_parking() -> pd.DataFrame:
    """Load parking/transport data from seed CSV."""
    return pd.read_csv(RAW_DIR / "seed_parking.csv")


def load_geojson() -> dict:
    """Load Paris arrondissements GeoJSON."""
    with open(RAW_DIR / "arrondissements.geojson", "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_all(mode: str = "demo") -> dict:
    """
    Main ingestion entry point.
    
    Args:
        mode: "demo" uses seed files, "production" would call external APIs
    
    Returns:
        Dictionary with all raw DataFrames
    """
    if mode == "production":
        # Placeholder for real data ingestion
        # Example: call Paris Open Data API, INSEE API, etc.
        print("⚠️  Production mode not yet configured. Falling back to demo data.")
    
    print("📥 Loading seed data...")
    data = {
        "arrondissements": load_seed_arrondissements(),
        "demographics": load_seed_demographics(),
        "parking": load_seed_parking(),
        "geojson": load_geojson(),
    }
    
    for key, df in data.items():
        if isinstance(df, pd.DataFrame):
            print(f"   ✓ {key}: {len(df)} rows")
    
    return data


if __name__ == "__main__":
    data = ingest_all()
    print("\n✅ Ingestion complete")
