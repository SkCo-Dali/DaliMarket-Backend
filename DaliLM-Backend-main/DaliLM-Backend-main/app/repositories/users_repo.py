import pyodbc
from uuid import UUID
from typing import Optional, Dict, Any
from app.config import Config

class UsersRepo:
    def __init__(self):
        self.conn_str = Config.SQL_CONN_STR

    def get_daily_whatsapp_limit(self, user_id: UUID) -> Optional[int]:
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DailyWhatsAppLimit
            FROM dalilm.Users
            WHERE Id = ?
        """, str(user_id))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    

    def get_basic_info(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, Name, CountryCodeWhatsApp, WhatsAppNumber, Email
            FROM dalilm.Users
            WHERE Id = ?
        """, str(user_id))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "Id": row[0],
            "Name": row[1],
            "CountryCodeWhatsApp": row[2],
            "WhatsAppNumber": row[3],
            "Email": row[4],
        }
