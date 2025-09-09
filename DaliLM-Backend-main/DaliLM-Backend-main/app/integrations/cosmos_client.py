from azure.cosmos import CosmosClient, PartitionKey, exceptions
from app.config import Config
from datetime import datetime
from typing import Optional

class CosmosAnalyticsClient:
    def __init__(self):
        self.client = CosmosClient(Config.COSMOS_ENDPOINT, Config.COSMOS_KEY)
        self.database = self.client.get_database_client(Config.COSMOS_DB)
        self.analytics_container = self.database.get_container_client("whatsapp-analytics")
        self.campaign_container = self.database.get_container_client("whatsapp-campaign-metrics")


    # ---------- Analytics per message ----------

    def upsert_analytics(self, doc: dict):
        """
        doc debe contener:
          - id (uuid del log SQL idealmente)
          - userId (partition key)
        """
        self.analytics.upsert_item(doc)

    def merge_analytics_fields(self, doc_id: str, user_id: str, **fields):
        """
        Lee el doc y hace merge (simple) de los campos entregados.
        """
        try:
            doc = self.analytics.read_item(doc_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            # Si no existe, lo creamos con los campos que tengamos
            doc = {"id": doc_id, "userId": user_id}
        doc.update(fields)
        self.analytics.upsert_item(doc)

    # ---------- Campaign metrics (per batch) ----------

    def _get_campaign_doc(self, batch_id: str) -> Optional[dict]:
        try:
            return self.campaign.read_item(batch_id, partition_key=batch_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def increment_campaign_counter(self, *,
                                   batch_id: str,
                                   user_id: str,
                                   template_id: str,
                                   field: str):
        """
        Incrementa contadores: totalSent, totalDelivered, totalRead, totalClicked.
        Crea el doc si no existe.
        """
        doc = self._get_campaign_doc(batch_id)
        if not doc:
            doc = {
                "id": batch_id,
                "userId": user_id,
                "batchId": batch_id,
                "templateId": template_id,
                "campaignName": f"Batch {batch_id}",
                "createdAt": datetime.utcnow().isoformat(),
                "totalSent": 0,
                "totalDelivered": 0,
                "totalRead": 0,
                "totalClicked": 0,
            }
        if field not in doc:
            doc[field] = 0
        doc[field] += 1
        self.campaign.upsert_item(doc)

    def upsert_campaign_metrics(self, data: dict):
        self.campaign_container.upsert_item(data)
