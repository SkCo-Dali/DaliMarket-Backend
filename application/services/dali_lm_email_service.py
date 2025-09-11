from fastapi import HTTPException
from typing import List, Optional
from uuid import uuid4
from domain.models.dali_lm_email import DaliLMEmailInput, DaliLMEmailMessage
from application.ports.dali_lm_email_log_repository_port import DaliLMEmailLogRepositoryPort
from application.ports.dali_lm_user_repository_port import DaliLMUserRepositoryPort
from infrastructure.adapters.graph_api_adapter import GraphApiAdapter
from application.ports.auth_port import AuthPort

class DaliLMEmailService:
    def __init__(
        self,
        email_log_repository: DaliLMEmailLogRepositoryPort,
        user_repository: DaliLMUserRepositoryPort,
        graph_api_adapter: GraphApiAdapter,
        auth_adapter: AuthPort,
    ):
        self.email_log_repository = email_log_repository
        self.user_repository = user_repository
        self.graph_api_adapter = graph_api_adapter
        self.auth_adapter = auth_adapter

    def send_emails(self, email_data: DaliLMEmailInput, api_token: str, graph_token: str) -> List[dict]:
        current_user = self.auth_adapter.get_current_user(api_token)
        from_email = current_user.get("email")
        if not from_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el correo del usuario autenticado.")

        user = self.user_repository.get_user_by_email(from_email)
        if not user:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")
        user_id = user.id

        results = []
        for r in email_data.recipients:
            email_id = uuid4()
            status = "Success"
            error = None
            try:
                tracking_pixel = f'<img src="https://skcodalilmprd-temp.azurewebsites.net/api/emails/open-tracker?email_id={email_id}" width="1" height="1" style="display:none;">'
                html_with_tracking = f"{r.html_content}{tracking_pixel}" if (r.html_content and r.html_content.strip()) else None

                self.graph_api_adapter.send_email(
                    access_token=graph_token,
                    to_email=r.to,
                    subject=r.subject,
                    html_body=html_with_tracking,
                    plain_body=r.plain_content,
                )
            except Exception as e:
                status = "Failed"
                error = str(e)

            try:
                self.email_log_repository.log_email(
                    email_id, user_id, r.LeadId, r.Campaign, from_email, r.to, r.subject,
                    r.html_content, r.plain_content, status, error
                )
            except Exception as e_log:
                if status == "Success":
                    status = "LoggedWithError"
                error = (error + f" | LogError: {str(e_log)}") if error else f"LogError: {str(e_log)}"

            results.append({"to": r.to, "status": status, "error": error})

        return results
