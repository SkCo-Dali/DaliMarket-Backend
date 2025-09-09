# app/repositories/whatsapp_batches_repo.py
import pyodbc
import uuid
from datetime import datetime
from app.config import Config

class WhatsAppBatchesRepo:
    def __init__(self):
        self.conn_str = Config.SQL_CONN_STR

    def create_batch(self, user_id: str, template_id: str, total_messages: int) -> uuid.UUID:
        batch_id = uuid.uuid4()
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dalilm.WhatsAppBatches
            (Id, UserId, TemplateId, TotalMessages, Status, CreatedAt)
            VALUES (?, ?, ?, ?, 'PENDING', ?)
        """, str(batch_id), user_id, str(template_id), total_messages, datetime.utcnow())
        conn.commit()
        conn.close()
        return batch_id

    def update_batch_counts(self, batch_id: uuid.UUID, success: int, failed: int, status: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        params = [success, failed, status, datetime.utcnow() if status in ("COMPLETED", "FAILED") else None, str(batch_id)]
        cursor.execute("""
            UPDATE dalilm.WhatsAppBatches
            SET SuccessfulMessages = ?, FailedMessages = ?, Status = ?, CompletedAt = ?
            WHERE Id = ?
        """, *params)
        conn.commit()
        conn.close()

    def get_batch_status(self, batch_id: uuid.UUID):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, Status, TotalMessages, SuccessfulMessages, FailedMessages, CreatedAt, CompletedAt
            FROM dalilm.WhatsAppBatches WHERE Id = ?
        """, str(batch_id))
        row = cursor.fetchone()
        conn.close()
        return row
