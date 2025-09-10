# infrastructure/repositories/opportunity_detail_repository.py
import logging
from typing import List, Optional
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos_adapter import CosmosAdapter
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail


class OpportunityDetailRepository(OpportunityDetailRepositoryPort):
    def __init__(self, session: CosmosAdapter):
        self.container = session.get_container(
            settings.COSMOS_OPPORTUNITY_DETAIL_CONTAINER,
            settings.COSMOS_OPPORTUNITY_DETAIL_PARTITION_KEY
        )

    def _map_to_domain(self, doc: dict) -> OpportunityDetail:
        """Convierte un documento de Cosmos en un modelo de dominio."""
        return OpportunityDetail(
            OpportunityId=doc["OpportunityId"],
            Title=doc["Title"],
            Subtitle=doc.get("Subtitle"),
            Description=doc.get("Description"),
            EmailTemplate=doc.get("EmailTemplate"),
            DaliPrompt=doc.get("DaliPrompt"),
            Categories=doc.get("Categories", []),
        )

    def get_all(self) -> List[OpportunityDetail]:
        try:
            query = "SELECT * FROM c"
            items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            return [self._map_to_domain(doc) for doc in items]
        except Exception as e:
            logging.error(f"Error al consultar Details: {str(e)}")
            raise ConnectionErrorException("No se pudieron consultar los Details.")

    def get_by_opportunity_id(self, opportunity_id: int) -> Optional[OpportunityDetail]:
        try:
            query = "SELECT * FROM c WHERE c.OpportunityId=@id"
            parameters = [{"name": "@id", "value": opportunity_id}]
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            if items:
                return self._map_to_domain(items[0])
            return None
        except Exception as e:
            logging.error(f"Error al consultar Detail por ID: {str(e)}")
            raise ConnectionErrorException("No se pudo consultar el Detail por ID.")
