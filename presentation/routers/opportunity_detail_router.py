# presentation/routers/opportunity_detail_router.py
"""Router para los endpoints de detalles de oportunidades."""
from fastapi import APIRouter, Depends
from application.services.opportunity_leads_service import OpportunityLeadsService
from domain.models.opportunity_detail import OpportunityDetail
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.adapters.opportunity_detail_repository_adapter import OpportunityDetailRepository
from application.services.opportunity_detail_service import OpportunityDetailService
from infrastructure.adapters.opportunity_leads_repository_adapter import OpportunityLeadsRepository

router = APIRouter(prefix="/opportunity-detail", tags=["Opportunity Details"])


def get_opportunity_detail_service(session: CosmosSession = Depends(get_cosmos_session)):
    """Función de dependencia para obtener el servicio de detalles de oportunidades.

    Crea una instancia de `OpportunityDetailRepository` y la inyecta en
    `OpportunityDetailService`.

    Args:
        session (CosmosSession): Sesión de Cosmos DB inyectada por FastAPI.

    Returns:
        OpportunityDetailService: Una instancia del servicio de detalles de oportunidades.
    """
    repo = OpportunityDetailRepository(session)
    return OpportunityDetailService(repo)

@router.get("/", response_model=list[OpportunityDetail])
def list_details(service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    """Endpoint para listar todos los detalles de oportunidades.

    Args:
        service (OpportunityDetailService): Servicio inyectado para manejar la lógica.

    Returns:
        list[OpportunityDetail]: Una lista de todos los detalles de oportunidades.
    """
    return service.list_details()

@router.get("/{opportunity_id}", response_model=OpportunityDetail)
def get_detail_by_opportunity_id(opportunity_id: int, service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    """Endpoint para obtener el detalle de una oportunidad por su ID.

    Args:
        opportunity_id (int): El ID de la oportunidad a buscar.
        service (OpportunityDetailService): Servicio inyectado para manejar la lógica.

    Returns:
        OpportunityDetail: El detalle de la oportunidad encontrada.
    """
    return service.get_detail_by_opportunity_id(opportunity_id)