import httpx
from app.config import Config

class BotmakerClient:
    def __init__(self):
        self.base_url = "https://api.botmaker.com/v2.0"
        self.headers = {
            "access-token": Config.BOTMAKER_TOKEN,
            "Content-Type": "application/json"
            }

    async def send_notification(self, campaign: str, channel_id: str, name: str, intentIdOrName: str, contacts: list):
        payload = {
            "campaign": campaign,
            "channelId": channel_id,
            "name": name,
            "intentIdOrName": intentIdOrName,
            "contacts": contacts
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/notifications",
                headers=self.headers,
                json=payload
            )
            print(f"Status Botmaker: {response.status_code}")  # Ej: 201
            response.raise_for_status()  # Lanza excepción si hubo error 4xx o 5xx
            return {"status": response.status_code}

    async def get_message_status(self, message_id: str):
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"{self.base_url}/messages/{message_id}",
                headers=self.headers,
            )
            r.raise_for_status()
            return r.json()
