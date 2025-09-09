# application/services/opportunity_summary_service.py
from typing import Dict, List, Optional
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail
from domain.models.opportunity_summary import OpportunitySummary

class OpportunitySummaryService:
    """Servicio para generar resúmenes de oportunidades.

    Este servicio combina datos de los repositorios de detalles y leads de
    oportunidades para crear una vista resumida.
    """
    def __init__(self, opportunity_detail_repository: OpportunityDetailRepositoryPort, opportunity_leads_repository: OpportunityLeadsRepositoryPort):
        """Inicializa el servicio de resumen de oportunidades.

        Args:
            opportunity_detail_repository (OpportunityDetailRepositoryPort): El repositorio
                para acceder a los detalles de las oportunidades.
            opportunity_leads_repository (OpportunityLeadsRepositoryPort): El repositorio
                para acceder a los leads de las oportunidades.
        """
        self.opportunity_detail_repository = opportunity_detail_repository
        self.opportunity_leads_repository = opportunity_leads_repository

    def list_details(self) -> List[OpportunityDetail]:
        """Obtiene una lista de todos los detalles de oportunidades.

        Returns:
            List[OpportunityDetail]: Una lista de detalles de oportunidades.
        """
        return self.opportunity_detail_repository.get_all()
    
    def get_detail_by_opportunity_id(self, opportunity_id: str) -> Optional[OpportunityDetail]:
        """Obtiene el detalle de una oportunidad por su ID.

        Args:
            opportunity_id (str): El ID de la oportunidad a buscar.

        Returns:
            Optional[OpportunityDetail]: El detalle de la oportunidad si se encuentra,
                                         de lo contrario None.
        """
        return self.opportunity_detail_repository.get_by_opportunity_id(opportunity_id)
    
    def list_opportunity_summary_by_agte_id(self, agte_id: str) -> List[OpportunitySummary]:
        """Genera una lista de resúmenes de oportunidades para un agente específico.

        Combina la información de leads y detalles para crear un resumen
        de cada oportunidad asignada a un agente.

        Args:
            agte_id (str): El ID del agente.

        Returns:
            List[OpportunitySummary]: Una lista de resúmenes de oportunidades.
        """
        opportunities_leads = self.opportunity_leads_repository.get_by_agte_id(agte_id)
        summaries = []
        for opportunity_lead in opportunities_leads:
            opportunity_id = opportunity_lead.OpportunityId
            detail = self.opportunity_detail_repository.get_by_opportunity_id(opportunity_id)
            if detail:
                summary = OpportunitySummary(
                    OpportunityId=detail.OpportunityId,
                    Priority=opportunity_lead.Priority,
                    lead_count=len(opportunity_lead.leads),
                    Title=detail.Title,
                    Subtitle=detail.Subtitle,
                    Description=detail.Description,
                    Categories=detail.Categories
                )
                summaries.append(summary)
        return summaries