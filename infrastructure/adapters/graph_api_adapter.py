import requests
from typing import Optional

class GraphApiAdapter:
    def send_email(
        self,
        access_token: str,
        to_email: str,
        subject: str,
        html_body: Optional[str],
        plain_body: Optional[str],
    ) -> None:
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        body_content = html_body if (html_body and html_body.strip()) else (plain_body or "")
        body_type = "HTML" if (html_body and html_body.strip()) else "Text"

        message = {
            "message": {
                "subject": subject,
                "body": {"contentType": body_type, "content": body_content},
                "toRecipients": [{"emailAddress": {"address": to_email}}],
            },
            "saveToSentItems": True
        }

        resp = requests.post(url, headers=headers, json=message, timeout=30)
        if resp.status_code >= 400:
            raise Exception(f"Graph API error: {resp.status_code} - {resp.text}")
