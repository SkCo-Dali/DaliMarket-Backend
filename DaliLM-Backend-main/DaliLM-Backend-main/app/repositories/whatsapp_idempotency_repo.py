import pyodbc
from uuid import UUID, uuid4
from typing import Optional, Tuple
from datetime import datetime, timedelta
from app.config import Config

class WhatsAppIdempotencyRepo:
    def __init__(self):
        self.conn_str = Config.SQL_CONN_STR

    def get_by_key(self, key: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, UserId, IdempotencyKey, MessagesCount, BatchId, MessageId, Status, CreatedAt, ExpiresAt
            FROM dalilm.WhatsAppIdempotency
            WHERE IdempotencyKey = ?
        """, key)
        row = cursor.fetchone()
        conn.close()
        return row

    def create_pending(self, user_id: str, key: str, messages_count: int,
                       ttl_hours: int = 48):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        expires = datetime.utcnow() + timedelta(hours=ttl_hours)
        new_id = str(uuid4())
        cursor.execute("""
            INSERT INTO dalilm.WhatsAppIdempotency
            (Id, UserId, IdempotencyKey, MessagesCount, Status, ExpiresAt)
            VALUES (?, ?, ?, ?, 'PENDING', ?)
        """, new_id, user_id, key, messages_count, expires)
        conn.commit()
        conn.close()

    def mark_completed_mass(self, key: str, batch_id: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppIdempotency
            SET Status = 'COMPLETED', BatchId = ?
            WHERE IdempotencyKey = ?
        """, batch_id, key)
        conn.commit()
        conn.close()

    def mark_completed_single(self, key: str, message_id: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppIdempotency
            SET Status = 'COMPLETED', MessageId = ?
            WHERE IdempotencyKey = ?
        """, message_id, key)
        conn.commit()
        conn.close()

    def mark_failed(self, key: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppIdempotency
            SET Status = 'FAILED'
            WHERE IdempotencyKey = ?
        """, key)
        conn.commit()
        conn.close()
