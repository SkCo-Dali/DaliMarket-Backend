# infrastructure/repositories/log_repository.py
import logging
from core.settings import settings
from core.exceptions import ConnectionErrorException
from infrastructure.adapters.cosmos_adapter import CosmosAdapter
from application.ports.log_repository_port import LogRepositoryPort
from domain.models.log import Log


class LogRepository(LogRepositoryPort):
    def __init__(self, session: CosmosAdapter):
        self.container = session.get_container(
            settings.COSMOS_LOGS_CONTAINER,
            settings.COSMOS_LOGS_PARTITION_KEY
        )

    def save(self, log: Log) -> None:
        """Guarda un log en Cosmos DB."""
        try:
            doc = log.model_dump(mode='json')
            self.container.create_item(body=doc)
        except Exception as e:
            logging.error(f"Error al guardar el log: {str(e)}")
            raise ConnectionErrorException("No se pudo guardar el log.")
