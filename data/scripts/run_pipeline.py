"""
Full pipeline orchestrator: ingest -> transform -> KPIs -> correlations -> store.
"""

import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.scripts.ingest import ingest_all
from data.scripts.transform import transform_all
from data.scripts.compute_kpis import compute_all_kpis, load_scoring_config
from data.scripts.compute_correlations import compute_correlations, VARIABLE_LABELS


def run_pipeline(mode: str = "demo"):
    """Execute the full data pipeline."""
    start = datetime.now(timezone.utc)
    print("=" * 60)
    print(f"🚀 Parkshare Pipeline — {start.isoformat()}")
    print(f"   Mode: {mode}")
    print("=" * 60)
    
    # Step 1: Ingest
    raw_data = ingest_all(mode=mode)
    
    # Step 2: Transform
    processed = transform_all(raw_data)
    
    # Step 3: KPIs
    config = load_scoring_config()
    final = compute_all_kpis(processed, config)
    
    # Step 4: Correlations
    corr_data = compute_correlations(final)
    
    # Step 5: Save processed data
    processed_dir = Path(__file__).parent.parent / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    final.to_csv(processed_dir / "arrondissements_scored.csv", index=False)
    corr_data["matrix"].to_csv(processed_dir / "correlation_matrix.csv")
    
    with open(processed_dir / "top_correlations.json", "w", encoding="utf-8") as f:
        json.dump(corr_data["top_pairs"], f, indent=2, ensure_ascii=False)
    
    end = datetime.now(timezone.utc)
    duration = (end - start).total_seconds()
    
    print("=" * 60)
    print(f"✅ Pipeline complete in {duration:.1f}s")
    print(f"   Output: {processed_dir}")
    print("=" * 60)
    
    return {
        "data": final,
        "correlations": corr_data,
        "geojson": raw_data["geojson"],
        "config": config,
        "run_info": {
            "started_at": start.isoformat(),
            "finished_at": end.isoformat(),
            "duration_seconds": duration,
            "mode": mode,
            "num_arrondissements": len(final),
        },
    }


if __name__ == "__main__":
    mode = os.environ.get("APP_MODE", "demo")
    run_pipeline(mode=mode)
