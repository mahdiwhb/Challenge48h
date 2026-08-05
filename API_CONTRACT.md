# Contrat de données Frontend ↔ Backend — Parkshare

Documentation du contrat d'interface entre le frontend React/TypeScript et le backend FastAPI, tel qu'implémenté dans `api.ts`.

| Endpoint | Méthode | Paramètres | Type de retour | Usage |
|---|---|---|---|---|
| `/health` | GET | — | `{status, version, mode}` | Vérification de disponibilité du backend |
| `/arrondissements` | GET | — | `Array<Arrondissement>` | Liste complète des arrondissements |
| `/arrondissements/{code}` | GET | `code: string` | `Arrondissement` | Détail d'un arrondissement |
| `/kpis/summary` | GET | — | `KpiSummary` | Résumé des indicateurs clés |
| `/kpis/rankings` | GET | `sort_by, order` (query) | `Array<Ranking>` | Classement des arrondissements |
| `/map/geojson` | GET | `kpi` (query) | `GeoJSON` | Données cartographiques (format standard) |
| `/correlations` | GET | — | `CorrelationMatrix` | Matrice de corrélation entre variables |
| `/pipeline/run` | POST | — | `PipelineStatus` | Déclenche le pipeline de données (asynchrone) |
| `/pipeline/status` | GET | — | `PipelineStatus` | Interroge l'état du pipeline en cours |
| `/chatbot/query` | POST | `{query: string}` (body) | `{query, response, source}` | Interrogation du chatbot analytique |

## Convention de correspondance
- Tous les codes d'arrondissement suivent le format `750XX` (correspondance directe avec les codes postaux parisiens)
- Les paramètres `sort_by` acceptent les mêmes noms de champs que ceux retournés par `/kpis/summary`, garantissant la cohérence du vocabulaire entre les deux systèmes
