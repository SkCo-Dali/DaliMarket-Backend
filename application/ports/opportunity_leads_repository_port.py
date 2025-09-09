# application/ports/opportunity_leads_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List

from domain.models.opportunity_leads import OpportunityLeads


class OpportunityLeadsRepositoryPort(ABC):
    """Define el puerto del repositorio para los leads de oportunidades.

    Esta clase abstracta define la interfaz que deben implementar los adaptadores
    de repositorio para interactuar con la fuente de datos de leads de oportunidades.
    """

    @abstractmethod
    def get_all(self) -> List[OpportunityLeads]:
        """Obtiene todos los leads de todas las oportunidades.

        Returns:
            List[OpportunityLeads]: Una lista de todos los leads de oportunidades.
        """
        pass

    @abstractmethod
    def get_by_agte_id(self, agte_id: int) -> List[OpportunityLeads]:
        """Obtiene los leads de oportunidades para un agente específico.

        Args:
            agte_id (int): El ID del agente.

        Returns:
            List[OpportunityLeads]: Una lista de leads de oportunidades para el agente dado.
        """
        pass