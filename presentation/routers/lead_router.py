# presentation/routers/lead_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from application.services.lead_service import LeadService
from domain.models.lead import Lead
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.adapters.cosmos_adapter import CosmosAdapter, get_cosmos_session
from infrastructure.repositories.opportunity_leads_repository import OpportunityLeadsRepository
from infrastructure.repositories.lead_repository import LeadRepository


router = APIRouter(prefix="/leads", tags=["Leads"])


def get_lead_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
    cosmos: CosmosAdapter = Depends(get_cosmos_session)
) -> LeadService:
    # Repositorio para leer OpportunityLeads desde Cosmos
    opportunity_leads_repo = OpportunityLeadsRepository(cosmos)

    # Repositorio para guardar Leads en SQL Server
    lead_repo = LeadRepository(sql)

    return LeadService(lead_repo, opportunity_leads_repo)


@router.post("/from-opportunity", response_model=List[Lead])
def create_leads_from_opportunity(
    opportunity_id: int,
    id_agte: int,
    created_by: str,
    service: LeadService = Depends(get_lead_service),
):
    """
    Crea leads en SQL Server a partir de los OpportunityLeads almacenados en Cosmos.
    """
    leads = service.create_leads_from_opportunity(opportunity_id, id_agte, created_by)
    return leads


