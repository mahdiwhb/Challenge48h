import re
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.backend.app.db.database import get_db
from app.backend.app.schemas.schemas import ChatbotQuery, ChatbotResponse
from app.backend.app.core.config import settings

router = APIRouter()

SYSTEM_PROMPT = """Tu es l'assistant analytique Parkshare, expert en étude de marché du stationnement à Paris.
Tu analyses les données des 20 arrondissements parisiens pour identifier le potentiel commercial de Parkshare (partage de places de parking en copropriété).

Données disponibles par arrondissement :
- Score Parkshare (0-100) : score composite de potentiel
- Rang : classement sur les 20 arrondissements
- Population et densité (hab/km²)
- Part de logements collectifs (%)
- Nombre de voitures et taux de motorisation (pour 1000 hab)
- Pression stationnement (indice /100)
- Densité résidentielle (indice /100)

Méthodologie du scoring : normalisation min-max pondérée — densité population (25%), logements collectifs (25%), pression stationnement (30%), taux motorisation (20%).

Réponds en français, de manière concise et structurée avec des chiffres précis tirés des données fournies. Utilise le markdown pour la mise en forme."""


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
    numbers = re.findall(r'(\d{1,2})(?:e|ème|er|°)?', query)
    for num in numbers:
        code = f"751{int(num):02d}"
        for d in data:
            if d["code_arrondissement"] == code:
                return d
    return None


def _format_arrondissement(d: dict) -> str:
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


def _format_data_context(data: list[dict]) -> str:
    lines = ["Voici les données actuelles des 20 arrondissements :\n"]
    for d in data:
        lines.append(
            f"- {d['nom']} : score={d['score_parkshare']}, rang={d['rang']}, "
            f"pop={d['population']}, densité={d['densite_population']:.0f}, "
            f"logements_collectifs={d['part_logements_collectifs']}%, "
            f"motorisation={d['taux_motorisation']}, "
            f"pression={d['kpi_pression_stationnement']}/100, "
            f"densité_rés={d['kpi_densite_residentielle']}/100"
        )
    return "\n".join(lines)


async def _llm_response(query: str, data: list[dict]) -> str | None:
    if not settings.llm_api_key:
        return None

    data_context = _format_data_context(data)
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_context}"},
        {"role": "user", "content": query},
    ]

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.llm_api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1000,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def rule_based_response(query: str, db: Session) -> str:
    q = query.lower().strip()
    data = _get_all_scores(db)

    if not data:
        return "Aucune donnée disponible. Veuillez lancer le pipeline d'abord."

    if any(w in q for w in ["meilleur", "top", "premier", "best", "highest"]):
        top = data[0]
        return f"Le meilleur arrondissement pour Parkshare est le **{top['nom']}** avec un score de **{top['score_parkshare']}/100**."

    if any(w in q for w in ["pire", "dernier", "worst", "lowest", "moins"]):
        bottom = data[-1]
        return f"L'arrondissement avec le plus faible potentiel est le **{bottom['nom']}** avec un score de **{bottom['score_parkshare']}/100**."

    if "top 5" in q or "cinq premiers" in q:
        lines = ["**Top 5 des arrondissements Parkshare :**\n"]
        for d in data[:5]:
            lines.append(f"{d['rang']}. {d['nom']} — Score: {d['score_parkshare']}/100")
        return "\n".join(lines)

    if "compar" in q:
        numbers = re.findall(r'(\d{1,2})(?:e|ème|er|°)?', q)
        if len(numbers) >= 2:
            a1 = _find_arrondissement(data, numbers[0])
            a2 = _find_arrondissement(data, numbers[1])
            if a1 and a2:
                better = a1 if a1["score_parkshare"] > a2["score_parkshare"] else a2
                return (
                    f"**Comparaison :**\n\n"
                    f"{_format_arrondissement(a1)}\n\n---\n\n"
                    f"{_format_arrondissement(a2)}\n\n"
                    f"Le **{better['nom']}** a un meilleur potentiel Parkshare."
                )

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
            return f"{_format_arrondissement(arr)}\n\n**Explication** : Ce score s'explique par {explanation}."

    arr = _find_arrondissement(data, q)
    if arr:
        return _format_arrondissement(arr)

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
async def chatbot_query(body: ChatbotQuery, db: Session = Depends(get_db)):
    data = _get_all_scores(db)
    source = "rule-based"
    response = None

    if settings.llm_api_key:
        response = await _llm_response(body.query, data)
        if response:
            source = "llm"

    if not response:
        response = rule_based_response(body.query, db)

    db.execute(text(
        "INSERT INTO chatbot_logs (query, response) VALUES (:q, :r)"
    ), {"q": body.query, "r": response})
    db.commit()

    return {
        "query": body.query,
        "response": response,
        "source": source,
    }
