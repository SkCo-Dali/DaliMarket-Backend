# presentation/routers/opportunity_summary_router.py
from fastapi import APIRouter, Depends
from application.services.opportunity_summary_service import OpportunitySummaryService
from domain.models.opportunity_summary import OpportunitySummary
from infrastructure.adapters.cosmos_adapter import get_cosmos_session, CosmosAdapter
from infrastructure.repositories.opportunity_detail_repository import OpportunityDetailRepository
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository

router = APIRouter(prefix="/opportunity-summary", tags=["Opportunity Summary"])


def get_opportunity_simmary_service(session: CosmosAdapter = Depends(get_cosmos_session)):
    opportunity_detail_repo = OpportunityDetailRepository(session)
    opportunity_leads_repo = OpportunityLeadsRepository(session)
    return OpportunitySummaryService(opportunity_detail_repo, opportunity_leads_repo)

@router.get("/{agte_id}", response_model=list[OpportunitySummary])
def list_opportunity_summary_by_agte_id(agte_id: int, service: OpportunitySummaryService = Depends(get_opportunity_simmary_service)):
    return service.list_opportunity_summary_by_agte_id(agte_id)