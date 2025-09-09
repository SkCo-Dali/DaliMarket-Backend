from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, field_validator, model_validator
import pyodbc
import os
from dotenv import load_dotenv
from uuid import uuid4
from typing import List, Optional
import requests
import jwt as pyjwt  # para decodificación local sin verificación
from auth_azure import get_current_user

# Cargar .env (solo local)
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

# --------- Modelos ---------
class EmailMessage(BaseModel):
    to: EmailStr
    subject: str
    html_content: str | None = None
    plain_content: str | None = None
    LeadId: str
    Campaign: str | None = None

    @field_validator("subject", mode="after")
    @classmethod
    def subject_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("El asunto no puede estar vacío.")
        return v

    @field_validator("LeadId", mode="after")
    @classmethod
    def lead_id_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("LeadId es obligatorio.")
        return v

    @model_validator(mode="after")
    def check_body(self):
        has_html = bool(self.html_content and self.html_content.strip())
        has_plain = bool(self.plain_content and self.plain_content.strip())
        if not (has_html or has_plain):
            raise ValueError("Debe enviar html_content o plain_content.")
        return self


class EmailInput(BaseModel):
    recipients: List[EmailMessage]

    @field_validator("recipients")
    def validate_recipients(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe especificar al menos un destinatario.")
        return v

# --------- Helpers ---------
def get_user_id_by_email(cursor, email: str) -> Optional[str]:
    cursor.execute("""
        SELECT TOP (1) Id
        FROM dalilm.Users
        WHERE TRIM(Email) = ?
    """, email)
    row = cursor.fetchone()
    return row[0] if row else None

def send_email_graph(access_token: str, to_email: str, subject: str,
                     html_body: Optional[str], plain_body: Optional[str]) -> None:
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",  # <-- token de Graph
        "Content-Type": "application/json"
    }

    body_content = html_body if (html_body and html_body.strip()) else (plain_body or "")
    body_type = "HTML" if (html_body and html_body.strip()) else "Text"

    message = {
        "message": {
            "subject": subject,
            "body": {"contentType": body_type, "content": body_content},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        },
        "saveToSentItems": True
    }

    resp = requests.post(url, headers=headers, json=message, timeout=30)
    if resp.status_code >= 400:
        raise Exception(f"Graph API error: {resp.status_code} - {resp.text}")

# --------- Endpoint ---------
@router.post("/api/emails/send")
def send_emails(
    data: EmailInput,
    request: Request,
    current_user: dict = Depends(get_current_user)  # valida token de TU API
):
    """
    Sin OBO: requiere DOS tokens en headers.
    - Authorization: Bearer <TOKEN_API>   -> valida tu API
    - X-Graph-Token: <TOKEN_GRAPH>        -> usado para llamar a Graph (/me/sendMail)
    """
    try:
        # 1) Correo autenticado (del token de TU API)
        from_email = current_user.get("email")
        if not from_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el correo del usuario autenticado.")

        # 2) Token de Graph enviado por el frontend
        graph_token = request.headers.get("X-Graph-Token")
        if not graph_token:
            raise HTTPException(status_code=400, detail="Falta header X-Graph-Token (token de Microsoft Graph).")

        # 2.1 Validación ligera del token de Graph (sin firma, solo UX)
        try:
            claims = pyjwt.decode(graph_token, options={"verify_signature": False})
            aud = claims.get("aud")
            scp = (claims.get("scp") or "")
            if aud not in ("https://graph.microsoft.com", "00000003-0000-0000-c000-000000000000"):
                raise HTTPException(status_code=403, detail="El token de Graph no tiene audience de Microsoft Graph.")
            if "Mail.Send" not in scp.split():
                raise HTTPException(status_code=403, detail="El token de Graph no incluye el scope Mail.Send.")
        except HTTPException:
            raise
        except Exception:
            # Si falla la decodificación local, seguimos y que Graph responda; o lanza 400 si prefieres.
            pass

        # 3) Conectar a SQL y obtener UserId para logs
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        user_id = get_user_id_by_email(cursor, from_email)
        if not user_id:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")

        results = []

        for r in data.recipients:
            email_id = str(uuid4())
            status = "Success"
            error = None

            try:
                # 4) Tracking pixel (solo si viene HTML)
                tracking_pixel = (
                    f'<img src="https://skcodalilmprd-temp.azurewebsites.net/api/emails/open-tracker?email_id={email_id}" '
                    f'width="1" height="1" style="display:none;">'
                )
                html_with_tracking = f"{r.html_content}{tracking_pixel}" if (r.html_content and r.html_content.strip()) else None

                # 5) Enviar con Graph usando el token de Graph del header
                send_email_graph(
                    access_token=graph_token,
                    to_email=r.to,
                    subject=r.subject,
                    html_body=html_with_tracking,
                    plain_body=r.plain_content
                )

            except Exception as e:
                status = "Failed"
                error = str(e)

            # 6) Registrar en logs
            try:
                cursor.execute("""
                    INSERT INTO dalilm.EmailLogs (
                        Id, UserId, LeadId, Campaign, FromEmail, ToEmail, Subject, HtmlContent, PlainContent,
                        Status, ErrorMessage, CreatedAt
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE())
                """,
                email_id, user_id, r.LeafId if hasattr(r, "LeafId") else r.LeadId, r.Campaign, from_email, r.to, r.subject,
                r.html_content, r.plain_content, status, error)
            except Exception as e_log:
                if status == "Success":
                    status = "LoggedWithError"
                error = (error + f" | LogError: {str(e_log)}") if error else f"LogError: {str(e_log)}"

            results.append({"to": r.to, "status": status, "error": error})

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Proceso completado", "results": results}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar correos: {str(e)}")
