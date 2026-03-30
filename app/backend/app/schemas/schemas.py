"""
Pydantic schemas for API responses.
"""

from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    mode: str


class ArrondissementBase(BaseModel):
    code_arrondissement: str
    nom: str
    superficie_km2: float


class ArrondissementDetail(ArrondissementBase):
    population: int
    densite_population: float
    nb_logements: int
    part_logements_collectifs: float
    nb_voitures: int
    taux_motorisation: float
    pression_stationnement: float
    densite_logements_collectifs: float
    ratio_vehicules_places: float
    score_parkshare: float
    rang: int
    kpi_pression_stationnement: float
    kpi_densite_residentielle: float


class ArrondissementSummary(BaseModel):
    code_arrondissement: str
    nom: str
    score_parkshare: float
    rang: int


class KPISummary(BaseModel):
    total_arrondissements: int
    score_moyen: float
    score_max: float
    score_min: float
    top_5: list[ArrondissementSummary]
    bottom_5: list[ArrondissementSummary]


class RankingItem(BaseModel):
    rang: int
    code_arrondissement: str
    nom: str
    score_parkshare: float
    kpi_pression_stationnement: float
    kpi_densite_residentielle: float


class CorrelationEntry(BaseModel):
    var1: str
    var2: str
    correlation: float


class CorrelationResponse(BaseModel):
    matrix: dict[str, dict[str, float]]
    variables: list[str]
    labels: dict[str, str]


class PipelineStatus(BaseModel):
    id: int
    started_at: str
    finished_at: Optional[str]
    duration_seconds: Optional[float]
    mode: str
    status: str
    num_arrondissements: Optional[int]


class PipelineRunResponse(BaseModel):
    message: str
    status: str


class ChatbotQuery(BaseModel):
    query: str


class ChatbotResponse(BaseModel):
    query: str
    response: str
    source: str


class MapFeatureProperties(BaseModel):
    code: str
    nom: str
    score_parkshare: Optional[float] = None
    rang: Optional[int] = None
    kpi_pression_stationnement: Optional[float] = None
    kpi_densite_residentielle: Optional[float] = None
    population: Optional[int] = None
    taux_motorisation: Optional[float] = None
