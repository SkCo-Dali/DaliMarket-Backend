import pyodbc 
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from app.config import Config

class WhatsAppSendLogsRepo:
    def __init__(self):
        self.conn_str = Config.SQL_CONN_STR

    def create_log(self, *, batch_id: Optional[str], user_id: str, lead_id: str,
                   recipient_number: str, recipient_name: Optional[str],
                   template_id: str, message_content: str,
                   message_id: Optional[str], status: str, failure_reason: Optional[str] = None):
        print(f"Se iniciará el create_log con los datos recipient_number: {recipient_number}, recipient_name: {recipient_name}, message_content: {message_content}, status: {status}, failure_reason: {failure_reason}")
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        log_id = uuid.uuid4()
        cursor.execute("""
            INSERT INTO dalilm.WhatsAppSendLogs
            (Id, BatchId, UserId, LeadId, RecipientNumber, RecipientName, TemplateId,
             MessageContent, WhatsAppMessageId, Status, SentAt, FailureReason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        str(log_id), batch_id, user_id, lead_id, recipient_number, recipient_name,
        template_id, message_content, message_id, status, datetime.utcnow(), failure_reason)
        conn.commit()
        conn.close()
        return log_id

    # (Opcional) si quieres tener una firma más corta para logs del sistema:
    def create_system_log(self, **kwargs):
        return self.create_log(**kwargs)

    def list_by_user(self, user_id: str, limit: int = 50, offset: int = 0):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, BatchId, UserId, LeadId, RecipientNumber, RecipientName, TemplateId,
                   MessageContent, WhatsAppMessageId, Status, SentAt, DeliveredAt, ReadAt, FailureReason
            FROM dalilm.WhatsAppSendLogs
            WHERE UserId = ?
            ORDER BY SentAt DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """, user_id, offset, limit)
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM dalilm.WhatsAppSendLogs WHERE UserId = ?", user_id)
        total = cursor.fetchone()[0]

        conn.close()
        return rows, total
    
    def count_sent_today(self, user_id: str) -> int:
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM dalilm.WhatsAppSendLogs
            WHERE UserId = ?
              AND CAST(SentAt AS DATE) = CAST(SYSUTCDATETIME() AS DATE)
        """, user_id)
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def get_by_message_id(self, message_id: str) -> Optional[dict]:
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, BatchId, UserId, LeadId, RecipientNumber, RecipientName, TemplateId,
                   MessageContent, WhatsAppMessageId, Status, SentAt, DeliveredAt, ReadAt, FailureReason
            FROM dalilm.WhatsAppSendLogs
            WHERE WhatsAppMessageId = ?
        """, message_id)
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "Id": row[0],
            "BatchId": row[1],
            "UserId": row[2],
            "LeadId": row[3],
            "RecipientNumber": row[4],
            "RecipientName": row[5],
            "TemplateId": row[6],
            "MessageContent": row[7],
            "WhatsAppMessageId": row[8],
            "Status": row[9],
            "SentAt": row[10],
            "DeliveredAt": row[11],
            "ReadAt": row[12],
            "FailureReason": row[13],
        }

    def mark_delivered(self, message_id: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppSendLogs
            SET Status = 'DELIVERED', DeliveredAt = ?
            WHERE WhatsAppMessageId = ?
        """, datetime.utcnow(), message_id)
        conn.commit()
        conn.close()

    def mark_failed(self, message_id: str, reason: Optional[str] = None):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppSendLogs
            SET Status = 'FAILED', FailureReason = ?
            WHERE WhatsAppMessageId = ?
        """, reason, message_id)
        conn.commit()
        conn.close()

    def mark_read(self, message_id: str):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dalilm.WhatsAppSendLogs
            SET Status = 'READ', ReadAt = ?
            WHERE WhatsAppMessageId = ?
        """, datetime.utcnow(), message_id)
        conn.commit()
        conn.close()
