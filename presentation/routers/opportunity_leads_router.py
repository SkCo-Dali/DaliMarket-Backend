# presentation/routers/opportunity_leads_router.py
"""Router para los endpoints de leads de oportunidades."""
from fastapi import APIRouter, Depends
from domain.models.opportunity_leads import OpportunityLeads
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.adapters.opportunity_leads_repository_adapter import OpportunityLeadsRepository
from application.services.opportunity_leads_service import OpportunityLeadsService

router = APIRouter(prefix="/opportunity-leads", tags=["Opportunity Leads"])


def get_leads_service(session: CosmosSession = Depends(get_cosmos_session)):
    """Función de dependencia para obtener el servicio de leads de oportunidades.

    Crea una instancia de `OpportunityLeadsRepository` y la inyecta en
    `OpportunityLeadsService`.

    Args:
        session (CosmosSession): Sesión de Cosmos DB inyectada por FastAPI.

    Returns:
        OpportunityLeadsService: Una instancia del servicio de leads de oportunidades.
    """
    repo = OpportunityLeadsRepository(session)
    return OpportunityLeadsService(repo)

@router.get("/", response_model=list[OpportunityLeads])
def list_leads(service: OpportunityLeadsService = Depends(get_leads_service)):
    """Endpoint para listar todos los leads de oportunidades.

    Args:
        service (OpportunityLeadsService): Servicio inyectado para manejar la lógica.

    Returns:
        list[OpportunityLeads]: Una lista de todos los leads de oportunidades.
    """
    return service.list_leads()

@router.get("/{agte_id}", response_model=list[OpportunityLeads])
def get_leads_by_agte_id(agte_id: int, service: OpportunityLeadsService = Depends(get_leads_service)):
    """Endpoint para obtener los leads de un agente específico por su ID.

    Args:
        agte_id (int): El ID del agente.
        service (OpportunityLeadsService): Servicio inyectado para manejar la lógica.

    Returns:
        list[OpportunityLeads]: Una lista de leads para el agente especificado.
    """
    return service.get_leads_by_agte_id(agte_id)
