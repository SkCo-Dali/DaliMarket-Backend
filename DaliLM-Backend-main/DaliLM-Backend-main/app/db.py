import aioodbc
from databricks import sql as dbsql
import pandas as pd
from app.config import Config

async def obtener_userId(correo: str):
    try:
        async with aioodbc.connect(dsn=Config.SQL_CONN_STR, autocommit=True) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT top (1) Id as UserId
                    FROM dalilm.Users
                    WHERE trim(Email) = ?
                """, str(correo))
                result = await cursor.fetchone()
                return result if result else None
            if result:
                return result
            else:
                print(f"[ERROR] No se encontró un Id para el correo: {correo}")
                return None
    except Exception as e:
        raise

async def obtener_TemplateInfo(templateId: str):
    try:
        async with aioodbc.connect(dsn=Config.SQL_CONN_STR, autocommit=True) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT top (1) WhatsAppTemplateId, ChannelId
                    FROM dalilm.WhatsAppTemplates
                    WHERE Id = ?
                """, templateId)
                result = await cursor.fetchone()
                return result if result else None
            if result:
                return result
            else:
                print(f"[ERROR] No se encontró un Template para el ID: {templateId}")
                return None
    except Exception as e:
        raise