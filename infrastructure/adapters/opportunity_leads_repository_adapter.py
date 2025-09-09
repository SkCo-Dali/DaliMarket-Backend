# infrastructure/adapters/opportunity_leads_repository.py
import logging
from typing import List
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos import CosmosSession
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_leads import OpportunityLeads
from domain.models.Lead import Lead

class OpportunityLeadsRepository(OpportunityLeadsRepositoryPort):
    def __init__(self, session: CosmosSession):
        self.container = session.get_container(
            settings.COSMOS_OPPORTUNITY_LEADS_CONTAINER,
            settings.COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY
        )

    def _map_to_domain(self, doc: dict) -> OpportunityLeads:
        """Convierte un documento de Cosmos en un modelo de dominio."""
        leads = [Lead(**l["lead"]) for l in doc.get("leads", [])]

        return OpportunityLeads(
            OpportunityId=doc["OpportunityId"],
            Beggining=doc["Beggining"],
            End=doc["End"],
            IdAgte=doc["IdAgte"],
            IdSociedad=doc["IdSociedad"],
            WSaler=doc["WSaler"],
            Status=doc["Status"],
            Priority=doc["Priority"],
            leads=leads,
        )

    def get_all(self) -> List[OpportunityLeads]:
        try:
            query = "SELECT * FROM c"
            items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            return [self._map_to_domain(doc) for doc in items]
        except Exception as e:
            logging.error(f"Error al consultar Leads: {str(e)}")
            raise ConnectionErrorException("No se pudieron consultar los Leads.")

    def get_by_agte_id(self, agte_id: int) -> List[OpportunityLeads]:
        try:
            query = "SELECT * FROM c WHERE c.IdAgte=@agte_id"
            parameters = [{"name": "@agte_id", "value": agte_id}]
            items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
            return [self._map_to_domain(doc) for doc in items]
        except Exception as e:
            logging.error(f"Error al consultar Leads por AgteId: {str(e)}")
            raise ConnectionErrorException("No se pudieron consultar los Leads por AgteId.")