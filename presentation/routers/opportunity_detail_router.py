# presentation/routers/opportunity_detail_router.py
from fastapi import APIRouter, Depends
from domain.models.opportunity_detail import OpportunityDetail
from infrastructure.adapters.cosmos_adapter import get_cosmos_session, CosmosAdapter
from infrastructure.repositories.opportunity_detail_repository import OpportunityDetailRepository
from application.services.opportunity_detail_service import OpportunityDetailService

router = APIRouter(prefix="/opportunity-detail", tags=["Opportunity Details"])


def get_opportunity_detail_service(session: CosmosAdapter = Depends(get_cosmos_session)):
    repo = OpportunityDetailRepository(session)
    return OpportunityDetailService(repo)

@router.get("/", response_model=list[OpportunityDetail])
def list_details(service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    return service.list_details()

@router.get("/{opportunity_id}", response_model=OpportunityDetail)
def get_detail_by_opportunity_id(opportunity_id: int, service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    return service.get_detail_by_opportunity_id(opportunity_id)