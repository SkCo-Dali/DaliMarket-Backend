import uuid
import logging
from typing import Dict, List
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos import CosmosSession
from application.ports.opportunity_detail_repository import OpportunityDetailRepositoryPort


class OpportunityDetailRepository(OpportunityDetailRepositoryPort):
    def __init__(self, session: CosmosSession):
        self.container = session.get_container(
            settings.COSMOS_OPPORTUNITY_DETAIL_CONTAINER,
            settings.COSMOS_OPPORTUNITY_DETAIL_PARTITION_KEY
        )

    def insert(self, detail: Dict) -> Dict:
        try:
            if "id" not in detail:
                detail["id"] = str(uuid.uuid4())
            return self.container.upsert_item(detail)
        except Exception as e:
            logging.error(f"Error al insertar Detail: {str(e)}")
            raise ConnectionErrorException("No se pudo insertar el Detail en Cosmos.")

    def get_all(self) -> List[Dict]:
        try:
            query = "SELECT * FROM c"
            return list(self.container.query_items(query=query, enable_cross_partition_query=True))
        except Exception as e:
            logging.error(f"Error al consultar Details: {str(e)}")
            raise ConnectionErrorException("No se pudieron consultar los Details.")
        
    def get_by_opportunity_id(self, opportunity_id: str) -> Dict:
        try:
            query = "SELECT * FROM c WHERE c.OpportunityId=@id"
            parameters = [{"name": "@id", "value": opportunity_id}]
            items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
            if items:
                return items[0]
            else:
                return None
        except Exception as e:
            logging.error(f"Error al consultar Detail por ID: {str(e)}")
            raise ConnectionErrorException("No se pudo consultar el Detail por ID.")
