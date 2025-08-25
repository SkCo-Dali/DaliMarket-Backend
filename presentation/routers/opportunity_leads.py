# presentation/routers/opportunity_leads.py
from fastapi import APIRouter, Depends
from infrastructure.adapters.cosmos import get_cosmos_session, CosmosSession
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository
from application.services.opportunity_leads_service import OpportunityLeadsService

router = APIRouter(prefix="/leads", tags=["Opportunity Leads"])


def get_leads_service(session: CosmosSession = Depends(get_cosmos_session)):
    repo = OpportunityLeadsRepository(session)
    return OpportunityLeadsService(repo)


@router.post("/")
def create_lead(lead: dict, service: OpportunityLeadsService = Depends(get_leads_service)):
    return service.create_lead(lead)


@router.get("/")
def list_leads(service: OpportunityLeadsService = Depends(get_leads_service)):
    return service.list_leads()

@router.get("/{agte_id}")
def get_leads_by_agte_id(agte_id: str, service: OpportunityLeadsService = Depends(get_leads_service)):
    agte_id = int(agte_id) if agte_id.isdigit() else agte_id
    return service.get_leads_by_agte_id(agte_id)
