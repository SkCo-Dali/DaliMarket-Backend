# infrastructure/adapters/cosmos.py
import logging
from azure.cosmos import CosmosClient, PartitionKey
from core.settings import settings
from core.exceptions import ConnectionErrorException


class CosmosSession:
    def __init__(self):
        try:
            self.client = CosmosClient(settings.COSMOS_URI, credential=settings.COSMOS_KEY)
            self.database = self.client.create_database_if_not_exists(id=settings.COSMOS_DATABASE)
        except Exception as e:
            logging.error(f"Error al conectar con Cosmos DB: {str(e)}")
            raise ConnectionErrorException("No se pudo establecer conexión con Cosmos DB.")

    def get_container(self, container_name: str, partition_key: str):
        try:
            return self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=partition_key),
                offer_throughput=400
            )
        except Exception as e:
            logging.error(f"Error al obtener contenedor {container_name}: {str(e)}")
            raise ConnectionErrorException(f"No se pudo obtener el contenedor {container_name}.")

    def close(self):
        self.client = None


def get_cosmos_session():
    db = CosmosSession()
    try:
        yield db
    finally:
        db.close()
