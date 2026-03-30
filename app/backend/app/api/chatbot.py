"""
Rule-based chatbot for Parkshare analytics.
Handles common questions about arrondissements, scores, and KPIs.
Architecture ready for LLM integration.
"""

import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db
from app.backend.app.schemas.schemas import ChatbotQuery, ChatbotResponse
from app.backend.app.core.config import settings

router = APIRouter()


def _get_all_scores(db: Session) -> list[dict]:
    rows = db.execute(text("""
        SELECT k.code_arrondissement, k.nom, k.score_parkshare, k.rang,
               k.kpi_pression_stationnement, k.kpi_densite_residentielle,
               p.population, p.taux_motorisation, p.pression_stationnement,
               p.densite_population, p.part_logements_collectifs
        FROM kpi_scores k
        JOIN processed_arrondissements p ON k.code_arrondissement = p.code_arrondissement
        ORDER BY k.rang
    """)).fetchall()
    return [dict(r._mapping) for r in rows]


def _find_arrondissement(data: list[dict], query: str) -> dict | None:
    """Find arrondissement by number or name in query."""
    # Match patterns like "11e", "11ème", "11", "onzième"
    numbers = re.findall(r'(\d{1,2})(?:e|ème|er|°)?', query)
    for num in numbers:
        code = f"751{int(num):02d}"
        for d in data:
            if d["code_arrondissement"] == code:
                return d
    return None


def _format_arrondissement(d: dict) -> str:
    """Format arrondissement details for response."""
    return (
        f"**{d['nom']}**\n"
        f"- Score Parkshare : **{d['score_parkshare']}/100** (rang {d['rang']})\n"
        f"- Population : {d['population']:,}\n"
        f"- Densité : {d['densite_population']:,.0f} hab/km²\n"
        f"- Pression stationnement : {d['kpi_pression_stationnement']}/100\n"
        f"- Densité résidentielle : {d['kpi_densite_residentielle']}/100\n"
        f"- Taux de motorisation : {d['taux_motorisation']}\n"
        f"- % logements collectifs : {d['part_logements_collectifs']}%"
    )


def rule_based_response(query: str, db: Session) -> str:
    """Process query using rule-based pattern matching."""
    q = query.lower().strip()
    data = _get_all_scores(db)
    
    if not data:
        return "Aucune donnée disponible. Veuillez lancer le pipeline d'abord."
    
    # Best/top arrondissement
    if any(w in q for w in ["meilleur", "top", "premier", "best", "highest"]):
        top = data[0]
        return f"Le meilleur arrondissement pour Parkshare est le **{top['nom']}** avec un score de **{top['score_parkshare']}/100**."
    
    # Worst/bottom
    if any(w in q for w in ["pire", "dernier", "worst", "lowest", "moins"]):
        bottom = data[-1]
        return f"L'arrondissement avec le plus faible potentiel est le **{bottom['nom']}** avec un score de **{bottom['score_parkshare']}/100**."
    
    # Top 5
    if "top 5" in q or "cinq premiers" in q:
        lines = ["**Top 5 des arrondissements Parkshare :**\n"]
        for d in data[:5]:
            lines.append(f"{d['rang']}. {d['nom']} — Score: {d['score_parkshare']}/100")
        return "\n".join(lines)
    
    # Compare two arrondissements
    if "compar" in q:
        numbers = re.findall(r'(\d{1,2})(?:e|ème|er|°)?', q)
        if len(numbers) >= 2:
            a1 = _find_arrondissement(data, numbers[0])
            a2 = _find_arrondissement(data, numbers[1])
            if a1 and a2:
                better = a1 if a1["score_parkshare"] > a2["score_parkshare"] else a2
                return (
                    f"**Comparaison :**\n\n"
                    f"{_format_arrondissement(a1)}\n\n"
                    f"---\n\n"
                    f"{_format_arrondissement(a2)}\n\n"
                    f"➡️ Le **{better['nom']}** a un meilleur potentiel Parkshare."
                )
    
    # Explain score for specific arrondissement
    if any(w in q for w in ["expliq", "pourquoi", "comment", "score", "détail"]):
        arr = _find_arrondissement(data, q)
        if arr:
            factors = []
            if arr["kpi_pression_stationnement"] > 70:
                factors.append("une forte pression de stationnement")
            if arr["kpi_densite_residentielle"] > 70:
                factors.append("une haute densité résidentielle")
            if arr["part_logements_collectifs"] > 92:
                factors.append("un fort taux de logements collectifs")
            if arr["taux_motorisation"] > 300:
                factors.append("un taux de motorisation élevé")
            
            explanation = ", ".join(factors) if factors else "une combinaison équilibrée des indicateurs"
            return (
                f"{_format_arrondissement(arr)}\n\n"
                f"📊 **Explication** : Ce score s'explique par {explanation}."
            )
    
    # Specific arrondissement query
    arr = _find_arrondissement(data, q)
    if arr:
        return _format_arrondissement(arr)
    
    # Summary / overview
    if any(w in q for w in ["résumé", "summary", "vue d'ensemble", "overview", "général"]):
        avg = sum(d["score_parkshare"] for d in data) / len(data)
        return (
            f"**Résumé Parkshare Paris :**\n"
            f"- {len(data)} arrondissements analysés\n"
            f"- Score moyen : {avg:.1f}/100\n"
            f"- Meilleur : {data[0]['nom']} ({data[0]['score_parkshare']})\n"
            f"- Plus faible : {data[-1]['nom']} ({data[-1]['score_parkshare']})\n"
            f"- Les arrondissements de l'est parisien (11e, 18e, 19e, 20e) montrent le plus fort potentiel"
        )
    
    # Default help
    return (
        "Je peux répondre à ces types de questions :\n"
        "- **Quel est le meilleur arrondissement ?**\n"
        "- **Top 5 arrondissements**\n"
        "- **Compare le 11e et le 15e**\n"
        "- **Explique le score du 18e**\n"
        "- **Résumé général**\n"
        "- **Quel est le score du 20e ?**\n\n"
        "Posez votre question sur le potentiel Parkshare à Paris !"
    )


@router.post("/chatbot/query")
def chatbot_query(body: ChatbotQuery, db: Session = Depends(get_db)):
    """Process a chatbot query."""
    
    # Use LLM if configured, otherwise rule-based
    source = "rule-based"
    response = rule_based_response(body.query, db)
    
    # Log the interaction
    db.execute(text(
        "INSERT INTO chatbot_logs (query, response) VALUES (:q, :r)"
    ), {"q": body.query, "r": response})
    db.commit()
    
    return {
        "query": body.query,
        "response": response,
        "source": source,
    }
