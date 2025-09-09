from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timedelta
import pyodbc, os
from dotenv import load_dotenv
from auth_azure import get_current_user

load_dotenv()
router = APIRouter()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

def get_user_id_by_email(cursor, email: str) -> Optional[str]:
    cursor.execute("SELECT TOP (1) Id FROM dalilm.Users WHERE TRIM(Email)=?", email)
    row = cursor.fetchone()
    return row[0] if row else None

@router.get("/api/emails/logs")
def get_email_logs(
    userId: Optional[str] = Query(None, description="UUID del usuario. Si no se envía, se usan los del token."),
    campaign: Optional[str] = None,
    status: Optional[str] = None,
    fromDate: Optional[str] = None,   # ISO: "2025-08-10" o "2025-08-10T00:00:00"
    toDate: Optional[str] = None,     # ISO: "2025-08-11"
    page: int = 1,
    pageSize: int = 50,
    current_user: dict = Depends(get_current_user)  # Authorization requerido
):
    try:
        requester_email = current_user["email"]

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Resolver userId efectivo
        if userId:
            cursor.execute("SELECT Email FROM dalilm.Users WHERE Id = ?", userId)
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
            if row[0].lower().strip() != requester_email.lower().strip():
                raise HTTPException(status_code=403, detail="No puedes consultar logs de otro usuario.")
            effective_user_id = userId
        else:
            effective_user_id = get_user_id_by_email(cursor, requester_email)
            if not effective_user_id:
                raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")

        # Campos a traer (siempre con cuerpo)
        base_fields = [
            "Id", "UserId", "LeadId", "Campaign", "FromEmail", "ToEmail",
            "Subject", "HtmlContent", "PlainContent",  # <- siempre incluidos
            "Status", "ErrorMessage", "CreatedAt",
            "OpenedAt", "OpenedFromIP", "OpenedFromUserAgent"
        ]

        query = f"""
            SELECT {", ".join(base_fields)}
            FROM dalilm.EmailLogs
            WHERE UserId = ?
        """
        params: List[object] = [effective_user_id]

        if campaign:
            query += " AND Campaign = ?"
            params.append(campaign)
        if status:
            query += " AND Status = ?"
            params.append(status)

        # Fechas (UTC) — toDate inclusivo
        def parse_iso(s: str) -> datetime:
            try:
                return datetime.fromisoformat(s.replace("Z",""))
            except Exception:
                raise HTTPException(status_code=400, detail=f"Fecha inválida: {s}")

        if fromDate:
            dt_from = parse_iso(fromDate)
            query += " AND CreatedAt >= ?"
            params.append(dt_from)
        if toDate:
            dt_to = parse_iso(toDate)
            dt_to_next = dt_to + timedelta(days=1)
            query += " AND CreatedAt < ?"
            params.append(dt_to_next)

        # Orden y paginación
        if page < 1: page = 1
        if pageSize < 1 or pageSize > 500: pageSize = 50
        offset = (page - 1) * pageSize
        query += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, pageSize])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [c[0] for c in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]

        cursor.close(); conn.close()
        return {"page": page, "pageSize": pageSize, "logs": results}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar los logs: {str(e)}")
