"""
Seed the SQLite database with demo data.
Runs the full pipeline and inserts results into all tables.
"""

import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up the database path
DB_PATH = PROJECT_ROOT / "app" / "backend" / "data" / "parkshare.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("DATABASE_URL", f"sqlite:///{DB_PATH}")

from data.scripts.run_pipeline import run_pipeline
from data.scripts.compute_correlations import VARIABLE_LABELS

import sqlite3
import pandas as pd


def create_tables(conn: sqlite3.Connection):
    """Create all required tables."""
    conn.executescript("""
        -- Raw tables
        CREATE TABLE IF NOT EXISTS raw_arrondissements (
            code_arrondissement TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            superficie_km2 REAL,
            code_postal TEXT
        );

        CREATE TABLE IF NOT EXISTS raw_demographics (
            code_arrondissement TEXT PRIMARY KEY,
            population INTEGER,
            densite_population REAL,
            nb_logements INTEGER,
            part_logements_collectifs REAL,
            nb_menages INTEGER,
            taille_moyenne_menage REAL,
            FOREIGN KEY (code_arrondissement) REFERENCES raw_arrondissements(code_arrondissement)
        );

        CREATE TABLE IF NOT EXISTS raw_parking (
            code_arrondissement TEXT PRIMARY KEY,
            nb_voitures INTEGER,
            taux_motorisation REAL,
            places_voirie INTEGER,
            places_parkings_publics INTEGER,
            places_parkings_prives_estim INTEGER,
            pression_stationnement REAL,
            FOREIGN KEY (code_arrondissement) REFERENCES raw_arrondissements(code_arrondissement)
        );

        -- Processed tables
        CREATE TABLE IF NOT EXISTS processed_arrondissements (
            code_arrondissement TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            superficie_km2 REAL,
            population INTEGER,
            densite_population REAL,
            nb_logements INTEGER,
            part_logements_collectifs REAL,
            nb_voitures INTEGER,
            taux_motorisation REAL,
            pression_stationnement REAL,
            densite_logements_collectifs REAL,
            ratio_vehicules_places REAL,
            norm_densite_population REAL,
            norm_part_logements_collectifs REAL,
            norm_pression_stationnement REAL,
            norm_taux_motorisation REAL
        );

        -- KPI tables
        CREATE TABLE IF NOT EXISTS kpi_scores (
            code_arrondissement TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            score_parkshare REAL,
            rang INTEGER,
            kpi_pression_stationnement REAL,
            kpi_densite_residentielle REAL,
            FOREIGN KEY (code_arrondissement) REFERENCES processed_arrondissements(code_arrondissement)
        );

        CREATE TABLE IF NOT EXISTS kpi_rankings (
            rang INTEGER PRIMARY KEY,
            code_arrondissement TEXT NOT NULL,
            nom TEXT NOT NULL,
            score_parkshare REAL,
            FOREIGN KEY (code_arrondissement) REFERENCES kpi_scores(code_arrondissement)
        );

        -- Correlation table
        CREATE TABLE IF NOT EXISTS correlation_matrix (
            var1 TEXT NOT NULL,
            var2 TEXT NOT NULL,
            correlation REAL,
            PRIMARY KEY (var1, var2)
        );

        -- Pipeline tracking
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            duration_seconds REAL,
            mode TEXT,
            status TEXT DEFAULT 'running',
            num_arrondissements INTEGER,
            error_message TEXT
        );

        -- Scoring config
        CREATE TABLE IF NOT EXISTS scoring_config (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL,
            description TEXT
        );

        -- Chatbot logs
        CREATE TABLE IF NOT EXISTS chatbot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- GeoJSON cache
        CREATE TABLE IF NOT EXISTS geojson_cache (
            id INTEGER PRIMARY KEY DEFAULT 1,
            geojson_data TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)


def seed_database():
    """Run pipeline and seed all tables."""
    print(f"🗄️  Database path: {DB_PATH}")
    
    # Run pipeline
    result = run_pipeline(mode="demo")
    df = result["data"]
    corr = result["correlations"]
    geojson = result["geojson"]
    config = result["config"]
    run_info = result["run_info"]
    
    # Connect to SQLite
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        # Create tables
        create_tables(conn)
        print("\n🗄️  Seeding database...")
        
        # Clear existing data
        for table in [
            "raw_arrondissements", "raw_demographics", "raw_parking",
            "processed_arrondissements", "kpi_scores", "kpi_rankings",
            "correlation_matrix", "scoring_config", "geojson_cache"
        ]:
            conn.execute(f"DELETE FROM {table}")
        
        # Raw arrondissements
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO raw_arrondissements VALUES (?, ?, ?, ?)",
                (row["code_arrondissement"], row["nom"], row["superficie_km2"], row["code_postal"])
            )
        
        # Raw demographics
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO raw_demographics VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row["code_arrondissement"], row["population"], row["densite_population"],
                 row["nb_logements"], row["part_logements_collectifs"],
                 row["nb_menages"], row["taille_moyenne_menage"])
            )
        
        # Raw parking
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO raw_parking VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row["code_arrondissement"], row["nb_voitures"], row["taux_motorisation"],
                 row["places_voirie"], row["places_parkings_publics"],
                 row["places_parkings_prives_estim"], row["pression_stationnement"])
            )
        
        # Processed arrondissements
        processed_cols = [
            "code_arrondissement", "nom", "superficie_km2", "population",
            "densite_population", "nb_logements", "part_logements_collectifs",
            "nb_voitures", "taux_motorisation", "pression_stationnement",
            "densite_logements_collectifs", "ratio_vehicules_places",
            "norm_densite_population", "norm_part_logements_collectifs",
            "norm_pression_stationnement", "norm_taux_motorisation"
        ]
        for _, row in df.iterrows():
            vals = [row[c] for c in processed_cols]
            conn.execute(
                f"INSERT INTO processed_arrondissements VALUES ({','.join(['?']*len(processed_cols))})",
                vals
            )
        
        # KPI scores
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO kpi_scores VALUES (?, ?, ?, ?, ?, ?)",
                (row["code_arrondissement"], row["nom"], row["score_parkshare"],
                 row["rang"], row["kpi_pression_stationnement"], row["kpi_densite_residentielle"])
            )
        
        # KPI rankings
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO kpi_rankings VALUES (?, ?, ?, ?)",
                (row["rang"], row["code_arrondissement"], row["nom"], row["score_parkshare"])
            )
        
        # Correlation matrix
        corr_matrix = corr["matrix"]
        for var1 in corr_matrix.index:
            for var2 in corr_matrix.columns:
                conn.execute(
                    "INSERT INTO correlation_matrix VALUES (?, ?, ?)",
                    (var1, var2, float(corr_matrix.loc[var1, var2]))
                )
        
        # Scoring config
        for key, value in config["weights"].items():
            desc = config.get("notes", {}).get(key, "")
            conn.execute(
                "INSERT INTO scoring_config VALUES (?, ?, ?)",
                (key, value, desc)
            )
        
        # GeoJSON cache
        conn.execute(
            "INSERT INTO geojson_cache VALUES (1, ?, ?)",
            (json.dumps(geojson, ensure_ascii=False), datetime.now(timezone.utc).isoformat())
        )
        
        # Pipeline run record
        conn.execute(
            "INSERT INTO pipeline_runs (started_at, finished_at, duration_seconds, mode, status, num_arrondissements) VALUES (?, ?, ?, ?, ?, ?)",
            (run_info["started_at"], run_info["finished_at"], run_info["duration_seconds"],
             run_info["mode"], "completed", run_info["num_arrondissements"])
        )
        
        conn.commit()
        print("✅ Database seeded successfully!")
        print(f"   Tables populated: 10")
        print(f"   Arrondissements: {len(df)}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
