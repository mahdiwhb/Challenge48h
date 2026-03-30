# Data Pipeline — Parkshare Market Study

## Structure

```
data/
├── raw/               # Raw source data (seed or ingested)
├── processed/         # Cleaned and transformed data
├── scripts/           # Python pipeline scripts
│   ├── seed_database.py
│   ├── run_pipeline.py
│   ├── ingest.py
│   ├── transform.py
│   ├── compute_kpis.py
│   └── compute_correlations.py
└── scoring_config.json
```

## Pipeline Steps

1. **Ingest** — Load raw data from CSV/JSON seed files or external APIs
2. **Transform** — Clean, normalize, and structure data per arrondissement
3. **Compute KPIs** — Calculate scoring, rankings, and derived metrics
4. **Compute Correlations** — Generate correlation matrix between variables

## Scoring Methodology

### Variables Used

| Variable | Description | Weight |
|----------|-------------|--------|
| `densite_population` | Population density (hab/km²) | 0.25 |
| `part_logements_collectifs` | Share of collective housing (%) | 0.25 |
| `pression_stationnement` | Parking pressure index (0-100) | 0.30 |
| `taux_motorisation` | Motorization rate (vehicles/1000 hab) | 0.20 |

### Calculation

1. Each variable is normalized to [0, 100] using min-max scaling
2. Weighted sum produces raw score
3. Final score is re-normalized to [0, 100]

### KPIs Produced

1. **Score de potentiel Parkshare** — Composite score combining all variables
2. **Classement des arrondissements** — Rank from highest to lowest potential
3. **Indice de pression de stationnement** — Ratio of vehicles to available parking
4. **Densité résidentielle** — Population density focused on residential areas

### Hypotheses & Limitations

- Seed data is based on realistic estimates from INSEE, Paris Open Data, and urban studies
- Parking pressure is estimated from motorization vs. available street/garage spots
- Weights are configurable in `scoring_config.json`
- Real data integration would improve accuracy significantly

## Adding New Data Sources

1. Add ingestion logic in `data/scripts/ingest.py`
2. Add a new raw table in the database schema
3. Add transformation in `data/scripts/transform.py`
4. Update scoring variables if needed in `scoring_config.json`
5. Re-run the pipeline: `make pipeline`
