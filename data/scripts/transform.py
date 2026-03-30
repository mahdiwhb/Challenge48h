"""
Transform raw data into processed metrics per arrondissement.
Merges, cleans, and normalizes data.
"""

import pandas as pd
import numpy as np


def merge_datasets(arrondissements: pd.DataFrame, demographics: pd.DataFrame, parking: pd.DataFrame) -> pd.DataFrame:
    """Merge all raw datasets on code_arrondissement."""
    df = arrondissements.merge(demographics, on="code_arrondissement", how="left")
    df = df.merge(parking, on="code_arrondissement", how="left")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate merged dataset."""
    # Remove duplicates
    df = df.drop_duplicates(subset=["code_arrondissement"])
    
    # Fill missing values with median for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    
    return df.reset_index(drop=True)


def normalize_column(series: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 100]."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute additional derived metrics."""
    # Density of collective housing per km²
    df["densite_logements_collectifs"] = (
        df["nb_logements"] * df["part_logements_collectifs"] / 100 / df["superficie_km2"]
    )
    
    # Vehicles per available parking spot
    total_places = df["places_voirie"] + df["places_parkings_publics"] + df["places_parkings_prives_estim"]
    df["ratio_vehicules_places"] = df["nb_voitures"] / total_places.replace(0, 1)
    
    # Normalized metrics for scoring
    df["norm_densite_population"] = normalize_column(df["densite_population"])
    df["norm_part_logements_collectifs"] = normalize_column(df["part_logements_collectifs"])
    df["norm_pression_stationnement"] = normalize_column(df["pression_stationnement"])
    df["norm_taux_motorisation"] = normalize_column(df["taux_motorisation"])
    
    return df


def transform_all(raw_data: dict) -> pd.DataFrame:
    """
    Main transformation entry point.
    
    Args:
        raw_data: Dictionary of raw DataFrames from ingestion
    
    Returns:
        Processed DataFrame with all metrics
    """
    print("🔄 Transforming data...")
    
    df = merge_datasets(
        raw_data["arrondissements"],
        raw_data["demographics"],
        raw_data["parking"]
    )
    print(f"   ✓ Merged: {len(df)} arrondissements")
    
    df = clean_data(df)
    print(f"   ✓ Cleaned: {len(df)} rows")
    
    df = compute_derived_metrics(df)
    print(f"   ✓ Derived metrics computed")
    
    return df


if __name__ == "__main__":
    from ingest import ingest_all
    raw = ingest_all()
    processed = transform_all(raw)
    print(f"\n✅ Transformation complete: {processed.columns.tolist()}")
