from typing import List, Optional
from pydantic import BaseModel

from domain.models.Lead import Lead


class OpportunitySummary(BaseModel):
    """Representa un resumen de una oportunidad de venta.

    Atributos:
        OpportunityId (int): Identificador único de la oportunidad.
        Priority (int): Prioridad de la oportunidad.
        lead_count (int): Número de leads asociados a la oportunidad.
        Title (str): Título de la oportunidad.
        Subtitle (str): Subtítulo de la oportunidad.
        Description (str): Descripción de la oportunidad.
        Categories (List[str]): Lista de categorías a las que pertenece la oportunidad.
    """
    OpportunityId: int
    Priority: int
    lead_count: int
    Title: str
    Subtitle: str
    Description: str
    Categories: List[str]