# presentation/routers/opportunity_detail.py
from fastapi import APIRouter, Depends
from application.services.opportunity_leads_service import OpportunityLeadsService
from domain.models.OpportunityDetail import OpportunityDetail
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.repositories.opportunity_detail_repository import OpportunityDetailRepository
from application.services.opportunity_detail_service import OpportunityDetailService
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository

router = APIRouter(prefix="/opportunity-detail", tags=["Opportunity Details"])


def get_opportunity_detail_service(session: CosmosSession = Depends(get_cosmos_session)):
    repo = OpportunityDetailRepository(session)
    return OpportunityDetailService(repo)

@router.get("/", response_model=list[OpportunityDetail])
def list_details(service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    return service.list_details()

@router.get("/{opportunity_id}", response_model=OpportunityDetail)
def get_detail_by_opportunity_id(opportunity_id: int, service: OpportunityDetailService = Depends(get_opportunity_detail_service)):
    return service.get_detail_by_opportunity_id(opportunity_id)