from fastapi import APIRouter, Depends
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.repositories.opportunity_detail_repository import OpportunityDetailRepository
from application.services.opportunity_detail_service import OpportunityDetailService

router = APIRouter(prefix="/details", tags=["Opportunity Details"])


def get_detail_service(session: CosmosSession = Depends(get_cosmos_session)):
    repo = OpportunityDetailRepository(session)
    return OpportunityDetailService(repo)


@router.post("/")
def create_detail(detail: dict, service: OpportunityDetailService = Depends(get_detail_service)):
    return service.create_detail(detail)


@router.get("/")
def list_details(service: OpportunityDetailService = Depends(get_detail_service)):
    return service.list_details()
