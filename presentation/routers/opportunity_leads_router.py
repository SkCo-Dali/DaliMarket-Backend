# presentation/routers/opportunity_leads_router.py
from fastapi import APIRouter, Depends
from domain.models.opportunity_leads import OpportunityLeads
from infrastructure.adapters.cosmos_adapter import get_cosmos_session, CosmosAdapter
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository
from application.services.opportunity_leads_service import OpportunityLeadsService

router = APIRouter(prefix="/opportunity-leads", tags=["Opportunity Leads"])


def get_leads_service(session: CosmosAdapter = Depends(get_cosmos_session)):
    repo = OpportunityLeadsRepository(session)
    return OpportunityLeadsService(repo)

@router.get("/", response_model=list[OpportunityLeads])
def list_leads(service: OpportunityLeadsService = Depends(get_leads_service)):
    return service.list_leads()

@router.get("/{agte_id}", response_model=list[OpportunityLeads])
def get_leads_by_agte_id(agte_id: int, service: OpportunityLeadsService = Depends(get_leads_service)):
    return service.get_leads_by_agte_id(agte_id)
