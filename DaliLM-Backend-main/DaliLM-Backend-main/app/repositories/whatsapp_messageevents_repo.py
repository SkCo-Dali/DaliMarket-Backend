import pyodbc
import uuid
from app.config import Config
from datetime import datetime

class WhatsAppMessageEventsRepo:
    def __init__(self):
        self.conn_str = Config.SQL_CONN_STR

    def create_event(self, message_log_id, whatsapp_message_id, event_type, event_data):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        event_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO dalilm.WhatsAppMessageEvents
            (Id, MessageLogId, WhatsAppMessageId, EventType, EventData, ReceivedAt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, event_id, message_log_id, whatsapp_message_id, event_type, event_data, datetime.utcnow())
        conn.commit()
        conn.close()
        return event_id
