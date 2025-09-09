import pyodbc
from app.config import get_connection

class WhatsAppTemplatesRepo:
    def __init__(self):
        self.conn = get_connection()

    def get_templates(self, is_approved: bool = None, channel_id: str = None, category: str = None, language: str = None):
        cursor = self.conn.cursor()

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

        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
