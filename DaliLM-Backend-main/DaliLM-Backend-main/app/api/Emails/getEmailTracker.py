from fastapi.responses import Response
from fastapi import Request, APIRouter
import pyodbc
import os
from dotenv import load_dotenv


# Cargar .env
load_dotenv()

router = APIRouter()

# Configuración SQL
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

@router.get("/api/emails/open-tracker")
def email_open_tracker(email_id: str, request: Request):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE dalilm.EmailLogs
            SET OpenedAt = GETUTCDATE(), 
                OpenedFromIP = ?,
                OpenedFromUserAgent = ?
            WHERE Id = ?
        """, ip_address, user_agent, email_id)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error registrando apertura: {e}")

    # Devolver una imagen vacía de 1x1 pixel
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21' \
            b'\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02' \
            b'\x44\x01\x00\x3B'
    return Response(content=pixel, media_type="image/gif")
