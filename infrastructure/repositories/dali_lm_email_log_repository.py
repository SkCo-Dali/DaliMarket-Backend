from typing import List, Optional
from uuid import UUID
from application.ports.dali_lm_email_log_repository_port import DaliLMEmailLogRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter

class DaliLMEmailLogRepository(DaliLMEmailLogRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def log_email(
        self,
        email_id: UUID,
        user_id: UUID,
        lead_id: UUID,
        campaign: Optional[str],
        from_email: str,
        to_email: str,
        subject: str,
        html_content: Optional[str],
        plain_content: Optional[str],
        status: str,
        error_message: Optional[str],
    ) -> None:
        query = """
            INSERT INTO dalilm.EmailLogs (
                Id, UserId, LeadId, Campaign, FromEmail, ToEmail, Subject, HtmlContent, PlainContent,
                Status, ErrorMessage, CreatedAt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE())
        """
        self.db_adapter.execute_query(
            query,
            (
                str(email_id), str(user_id), str(lead_id), campaign, from_email, to_email,
                subject, html_content, plain_content, status, error_message
            ),
        )
