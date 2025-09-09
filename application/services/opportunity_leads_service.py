# application/services/opportunity_leads_service.py
from typing import Dict, List
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_leads import OpportunityLeads


class OpportunityLeadsService:
    """Servicio para gestionar la lógica de negocio de los leads de oportunidades.

    Este servicio utiliza un puerto de repositorio para desacoplar la lógica
    de la implementación concreta de la base de datos.
    """
    def __init__(self, repository: OpportunityLeadsRepositoryPort):
        """Inicializa el servicio de leads de oportunidades.

        Args:
            repository (OpportunityLeadsRepositoryPort): El repositorio a utilizar
                                                       para acceder a los datos.
        """
        self.repository = repository

    def list_leads(self) -> List[OpportunityLeads]:
        """Obtiene una lista de todos los leads de oportunidades.

        Returns:
            List[OpportunityLeads]: Una lista de leads de oportunidades.
        """
        return self.repository.get_all()
    
    def get_leads_by_agte_id(self, agte_id: str) -> List[OpportunityLeads]:
        """Obtiene los leads de oportunidades para un agente específico.

        Args:
            agte_id (str): El ID del agente.

        Returns:
            List[OpportunityLeads]: Una lista de leads de oportunidades para el agente dado.
        """
        return self.repository.get_by_agte_id(agte_id)
