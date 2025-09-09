from typing import List, Optional
from pydantic import BaseModel

from domain.models.Lead import Lead


class OpportunityLeads(BaseModel):
    """Representa los leads asociados a una oportunidad de venta específica.

    Atributos:
        OpportunityId (int): Identificador único de la oportunidad.
        Beggining (str): Fecha de inicio.
        End (str): Fecha de fin.
        IdAgte (int): Identificador del agente.
        IdSociedad (int): Identificador de la sociedad.
        WSaler (str): Vendedor asignado.
        Status (int): Estado de la oportunidad.
        Priority (int): Prioridad de la oportunidad.
        leads (List[Lead]): Lista de leads asociados a la oportunidad.
    """
    OpportunityId: int
    Beggining: str 
    End: str
    IdAgte: int
    IdSociedad: int
    WSaler: str
    Status: int
    Priority: int
    leads: List[Lead]