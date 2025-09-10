from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_whatsapp_template import DaliLMWhatsAppTemplate
from application.ports.dali_lm_whatsapp_repository_port import DaliLMWhatsAppRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter
import json

class DaliLMWhatsAppRepository(DaliLMWhatsAppRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def get_templates(
        self,
        is_approved: Optional[bool],
        channel_id: Optional[str],
        category: Optional[str],
        language: Optional[str],
    ) -> List[DaliLMWhatsAppTemplate]:
        query = """
            SELECT Id, Name, Content, Variables, IsApproved,
                   WhatsAppTemplateId, Language, Category,
                   CreatedAt, UpdatedAt, ChannelId
            FROM dalilm.WhatsAppTemplates
            WHERE 1=1
        """
        params = []
        if is_approved is not None:
            query += " AND IsApproved = ?"
            params.append(1 if is_approved else 0)
        if channel_id:
            query += " AND ChannelId = ?"
            params.append(channel_id)
        if category:
            query += " AND Category = ?"
            params.append(category)
        if language:
            query += " AND Language = ?"
            params.append(language)

        rows = self.db_adapter.execute_query(query, tuple(params), fetchall=True)
        templates = []
        for row in rows:
            template_dict = {
                "Id": row[0], "Name": row[1], "Content": row[2], "Variables": row[3],
                "IsApproved": row[4], "WhatsAppTemplateId": row[5], "Language": row[6],
                "Category": row[7], "CreatedAt": row[8], "UpdatedAt": row[9], "ChannelId": row[10]
            }
            templates.append(DaliLMWhatsAppTemplate(**template_dict))
        return templates
