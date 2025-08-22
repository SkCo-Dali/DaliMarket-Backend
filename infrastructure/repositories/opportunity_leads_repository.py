import uuid
import logging
from typing import Dict, List
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos import CosmosSession
from application.ports.opportunity_leads_repository import OpportunityLeadsRepositoryPort


class OpportunityLeadsRepository(OpportunityLeadsRepositoryPort):
    def __init__(self, session: CosmosSession):
        self.container = session.get_container(
            settings.COSMOS_OPPORTUNITY_LEADS_CONTAINER,
            settings.COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY
        )

    def insert(self, lead: Dict) -> Dict:
        try:
            if "id" not in lead:
                lead["id"] = str(uuid.uuid4())
            return self.container.upsert_item(lead)
        except Exception as e:
            logging.error(f"Error al insertar Lead: {str(e)}")
            raise ConnectionErrorException("No se pudo insertar el Lead en Cosmos.")

    def get_all(self) -> List[Dict]:
        try:
            query = "SELECT * FROM c"
            return list(self.container.query_items(query=query, enable_cross_partition_query=True))
        except Exception as e:
            logging.error(f"Error al consultar Leads: {str(e)}")
            raise ConnectionErrorException("No se pudieron consultar los Leads.")
