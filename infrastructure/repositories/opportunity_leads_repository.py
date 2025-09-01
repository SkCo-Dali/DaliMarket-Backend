# infrastructure/repositories/opportunity_leads_repository.py
import logging
from typing import List, Optional
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos_adapter import CosmosAdapter
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_leads import OpportunityLeads
from domain.models.opportunity_lead import OpportunityLead

class OpportunityLeadsRepository(OpportunityLeadsRepositoryPort):
    def __init__(self, session: CosmosAdapter):
        self.container = session.get_container(
            settings.COSMOS_OPPORTUNITY_LEADS_CONTAINER,
            settings.COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY
        )

    def _map_to_domain(self, doc: dict) -> OpportunityLeads:
        """Convierte un documento de Cosmos en un modelo de dominio."""
        leads = [OpportunityLead(**l["lead"]) for l in doc.get("leads", [])]

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
        
    def get_by_opportunity_id_and_agte(self, opportunity_id: int, id_agte: int) -> Optional[OpportunityLeads]:
        query = """
        SELECT * FROM c WHERE c.OpportunityId = @opportunity_id AND c.IdAgte = @id_agte
        """
        params = [
            {"name": "@opportunity_id", "value": opportunity_id},
            {"name": "@id_agte", "value": id_agte},
        ]

        items = list(self.container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))

        if not items:
            return None

        return self._map_to_domain(items[0])