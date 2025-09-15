# presentation/routers/opportunity_summary_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from application.services.opportunity_summary_service import OpportunitySummaryService
from domain.models.opportunity_summary import OpportunitySummary
from infrastructure.adapters.azure_auth_adapter import AzureAuthAdapter
from infrastructure.adapters.cosmos_adapter import get_cosmos_session, CosmosAdapter
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.opportunity_detail_repository import OpportunityDetailRepository
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository
from infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/opportunity-summary", tags=["Opportunity Summary"])
security = HTTPBearer()

def get_opportunity_summary_service(
        session: CosmosAdapter = Depends(get_cosmos_session),
        sql: SqlServerAdapter = Depends(get_sql_server_session)
):
    opportunity_detail_repo = OpportunityDetailRepository(session)
    opportunity_leads_repo = OpportunityLeadsRepository(session)
    auth_adapter = AzureAuthAdapter()
    user_repo = UserRepository(sql)  

    return OpportunitySummaryService(opportunity_detail_repo, opportunity_leads_repo, auth_adapter, user_repo)

@router.get("", response_model=list[OpportunitySummary])
def list_opportunity_summary_by_agte_id(
    service: OpportunitySummaryService = Depends(get_opportunity_summary_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
    try:
        token = credentials.credentials
        return service.list_opportunity_summary_by_agte_id(token)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))