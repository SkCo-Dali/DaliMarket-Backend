# presentation/routers/lead_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from application.services.lead_service import LeadService
from domain.models.lead_ import Lead
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.adapters.cosmos_adapter import CosmosAdapter, get_cosmos_session
from infrastructure.adapters.azure_auth_adapter import AzureAuthAdapter
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository
from infrastructure.repositories.lead_repository import LeadRepository
from infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/leads", tags=["Leads"])
security = HTTPBearer()


def get_lead_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
    cosmos: CosmosAdapter = Depends(get_cosmos_session),
) -> LeadService:
    # Repositorio para leer OpportunityLeads desde Cosmos
    opportunity_leads_repo = OpportunityLeadsRepository(cosmos)

    # Repositorio para guardar Leads en SQL Server
    lead_repo = LeadRepository(sql)

    # Repositorio de Users
    user_repo = UserRepository(sql)

    # Adaptador de autenticación (AuthPort implementation)
    auth_adapter = AzureAuthAdapter()

    return LeadService(lead_repo, opportunity_leads_repo, user_repo, auth_adapter)


@router.post("/from-opportunity", response_model=List[Lead])
def create_leads_from_opportunity(
    opportunity_id: int,
    id_agte: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: LeadService = Depends(get_lead_service),
):
    """
    Crea leads en SQL Server a partir de los OpportunityLeads almacenados en Cosmos.
    El usuario autenticado se obtiene del token JWT de Azure.
    """
    try:
        token = credentials.credentials
        leads = service.create_leads_from_opportunity(opportunity_id, id_agte, token)
        return leads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
