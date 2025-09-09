# core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuraciones de la aplicación.

    Carga las variables de entorno desde un archivo .env y las expone
    como atributos de esta clase.

    Atributos:
        COSMOS_URI (str): URI de la cuenta de Cosmos DB.
        COSMOS_KEY (str): Clave de acceso principal de Cosmos DB.
        COSMOS_DATABASE (str): Nombre de la base de datos en Cosmos DB.
        COSMOS_OPPORTUNITY_LEADS_CONTAINER (str): Nombre del contenedor para los leads de oportunidades.
        COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY (str): Clave de partición para el contenedor de leads.
        COSMOS_OPPORTUNITY_DETAIL_CONTAINER (str): Nombre del contenedor para los detalles de oportunidades.
        COSMOS_OPPORTUNITY_DETAIL_PARTITION_KEY (str): Clave de partición para el contenedor de detalles.
    """
    COSMOS_URI: str
    COSMOS_KEY: str
    COSMOS_DATABASE: str
    COSMOS_OPPORTUNITY_LEADS_CONTAINER: str
    COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY: str
    COSMOS_OPPORTUNITY_DETAIL_CONTAINER: str
    COSMOS_OPPORTUNITY_DETAIL_PARTITION_KEY: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
