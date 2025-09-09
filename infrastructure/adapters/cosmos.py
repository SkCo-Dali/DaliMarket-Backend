# infrastructure/adapters/cosmos.py
import logging
from azure.cosmos import CosmosClient, PartitionKey
from core.settings import settings
from core.exceptions import ConnectionErrorException


class CosmosSession:
    """Gestiona la conexión y sesión con Cosmos DB.

    Esta clase encapsula la inicialización del cliente de Cosmos DB, la
    conexión a la base de datos y la obtención de contenedores.
    """
    def __init__(self):
        """Inicializa la sesión de Cosmos DB.

        Establece una conexión con la cuenta de Cosmos DB y selecciona la
        base de datos. Lanza una ConnectionErrorException si falla la conexión.
        """
        try:
            self.client = CosmosClient(settings.COSMOS_URI, credential=settings.COSMOS_KEY)
            self.database = self.client.create_database_if_not_exists(id=settings.COSMOS_DATABASE)
        except Exception as e:
            logging.error(f"Error al conectar con Cosmos DB: {str(e)}")
            raise ConnectionErrorException("No se pudo establecer conexión con Cosmos DB.")

    def get_container(self, container_name: str, partition_key: str):
        """Obtiene un contenedor de la base de datos.

        Crea el contenedor si no existe.

        Args:
            container_name (str): El nombre del contenedor.
            partition_key (str): La ruta de la clave de partición para el contenedor.

        Returns:
            ContainerProxy: El objeto contenedor para realizar operaciones.

        Raises:
            ConnectionErrorException: Si no se puede obtener el contenedor.
        """
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
        """Cierra la conexión con Cosmos DB."""
        self.client = None


def get_cosmos_session():
    """Generador para la inyección de dependencias de la sesión de Cosmos DB.

    Crea una instancia de CosmosSession y la proporciona a través de un `yield`,
    asegurando que la conexión se cierre después de su uso.

    Yields:
        CosmosSession: Una instancia de la sesión de Cosmos DB.
    """
    db = CosmosSession()
    try:
        yield db
    finally:
        db.close()
