# presentation/routers/opportunity_summary_router.py
"""Router para los endpoints de resumen de oportunidades."""
from fastapi import APIRouter, Depends
from application.services.opportunity_summary_service import OpportunitySummaryService
from domain.models.opportunity_detail import OpportunityDetail
from domain.models.opportunity_summary import OpportunitySummary
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.adapters.opportunity_detail_repository_adapter import OpportunityDetailRepository
from application.services.opportunity_detail_service import OpportunityDetailService
from infrastructure.adapters.opportunity_leads_repository_adapter import OpportunityLeadsRepository

router = APIRouter(prefix="/opportunity-summary", tags=["Opportunity Summary"])


def get_opportunity_summary_service(session: CosmosSession = Depends(get_cosmos_session)):
    """Función de dependencia para obtener el servicio de resumen de oportunidades.

    Crea instancias de los repositorios necesarios y los inyecta en
    `OpportunitySummaryService`.

    Args:
        session (CosmosSession): Sesión de Cosmos DB inyectada por FastAPI.

    Returns:
        OpportunitySummaryService: Una instancia del servicio de resumen de oportunidades.
    """
    opportunity_detail_repo = OpportunityDetailRepository(session)
    opportunity_leads_repo = OpportunityLeadsRepository(session)
    return OpportunitySummaryService(opportunity_detail_repo, opportunity_leads_repo)

@router.get("/{agte_id}", response_model=list[OpportunitySummary])
def list_opportunity_summary_by_agte_id(agte_id: int, service: OpportunitySummaryService = Depends(get_opportunity_summary_service)):
    """Endpoint para listar los resúmenes de oportunidades de un agente.

    Args:
        agte_id (int): El ID del agente.
        service (OpportunitySummaryService): Servicio inyectado para manejar la lógica.

    Returns:
        list[OpportunitySummary]: Una lista de resúmenes de oportunidades para el agente.
    """
    return service.list_opportunity_summary_by_agte_id(agte_id)