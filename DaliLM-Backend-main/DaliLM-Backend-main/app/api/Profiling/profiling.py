# profiling.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal, Any, Dict
from uuid import UUID, uuid4
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

# Dependencia de seguridad (asume que ya la tienes en tu proyecto)
try:
    from auth_azure import get_current_user  # Debe retornar dict con 'email' al menos
except Exception:
    # Fallback para desarrollo sin auth
    def get_current_user():
        return {"email": "dev@example.com"}

load_dotenv()
router = APIRouter(prefix="/api/profiling", tags=["profiling"])

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# =====================
# Modelos de entrada
# =====================
class CheckClientRequest(BaseModel):
    email: Optional[EmailStr] = None
    identificationNumber: Optional[str] = None

    @field_validator('identificationNumber')
    @classmethod
    def strip_doc(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator('email')
    @classmethod
    def lower_email(cls, v):
        return v.lower() if isinstance(v, str) else v

class StartProfilingRequest(BaseModel):
    clientEmail: Optional[EmailStr] = None
    clientIdentificationNumber: Optional[str] = None
    clientName: Optional[str] = None

    @field_validator('clientIdentificationNumber')
    @classmethod
    def strip_doc(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator('clientEmail')
    @classmethod
    def lower_email(cls, v):
        return v.lower() if isinstance(v, str) else v

class SaveResponseRequest(BaseModel):
    profileId: UUID
    flowStep: Literal['initial_question', 'nightmare_flow', 'strategic_flow', 'followup', 'custom']
    questionId: str
    selectedAnswer: Optional[str] = None
    additionalNotes: Optional[str] = None

    @field_validator('questionId')
    @classmethod
    def non_empty_q(cls, v):
        v = (v or '').strip()
        if not v:
            raise ValueError('questionId es obligatorio')
        return v

class CompleteProfilingRequest(BaseModel):
    profileId: UUID
    finalData: Dict[str, Any]

# =====================
# Helpers DB
# =====================

def get_conn():
    return pyodbc.connect(CONN_STR, autocommit=False)

# Deriva orden incremental
ORDER_SQL = """
SELECT ISNULL(MAX(ResponseOrder), 0) + 1
FROM dalilm.ProfilingResponses WITH (NOLOCK)
WHERE ProfileId = ?
"""

# =====================
# Endpoints
# =====================

@router.post('/check-client')
def check_client(payload: CheckClientRequest, user=Depends(get_current_user)):
    if not payload.email and not payload.identificationNumber:
        raise HTTPException(status_code=400, detail="Debes enviar email o identificationNumber")

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SET NOCOUNT ON;
            SELECT TOP (1) ProfileId, IsCompleted
            FROM dalilm.ClientProfiles WITH (NOLOCK)
            WHERE (ClientEmail = ? OR ClientIdentificationNumber = ?)
            ORDER BY CreatedAt DESC;
            """,
            payload.email, payload.identificationNumber
        )
        row = cursor.fetchone()
        if row:
            return {"hasProfile": True, "profileId": str(row.ProfileId), "isCompleted": bool(row.IsCompleted)}
        else:
            return {"hasProfile": False, "profileId": None}


@router.post('/start', status_code=status.HTTP_201_CREATED)
def start_profiling(payload: StartProfilingRequest, user=Depends(get_current_user)):
    if not payload.clientEmail and not payload.clientIdentificationNumber:
        raise HTTPException(status_code=400, detail="Debes enviar clientEmail o clientIdentificationNumber")

    # Normaliza
    email = payload.clientEmail
    doc = payload.clientIdentificationNumber
    name = payload.clientName

    # Datos del asesor creador desde el token
    creator_email = (user.get('email') or '').strip().lower()
    created_by_user_id = None

    with get_conn() as conn:
        try:
            cursor = conn.cursor()

            # Resuelve CreatedByUserId desde dalilm.Users
            try:
                cursor.execute(
                    """
                    SELECT TOP (1) Id
                    FROM dalilm.Users WITH (NOLOCK)
                    WHERE TRIM(LOWER(Email)) = ?
                    """,
                    creator_email
                )
                ur = cursor.fetchone()
                if ur:
                    created_by_user_id = ur[0]
            except Exception:
                created_by_user_id = None

            # Verifica si ya existe un perfil para ese email o doc
            cursor.execute(
                """
                SET NOCOUNT ON;
                SELECT TOP (1) ProfileId, IsCompleted
                FROM dalilm.ClientProfiles WITH (UPDLOCK, HOLDLOCK)
                WHERE (ClientEmail = ? OR ClientIdentificationNumber = ?)
                ORDER BY CreatedAt DESC;
                """,
                email, doc
            )
            existing = cursor.fetchone()
            if existing and not bool(existing.IsCompleted):
                # Reusar perfil activo para continuar
                conn.commit()
                return {"profileId": str(existing.ProfileId), "reused": True}

            # Inserta nuevo perfil
            cursor.execute(
                """
                INSERT INTO dalilm.ClientProfiles (ClientEmail, ClientIdentificationNumber, ClientName, ProfileType, CreatedByUserId, CreatedByEmail)
                OUTPUT inserted.ProfileId
                VALUES (?, ?, ?, NULL, ?, ?);
                """,
                email, doc, name, created_by_user_id, creator_email
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return {"profileId": str(new_id), "reused": False}
        except pyodbc.IntegrityError as ie:
            conn.rollback()
            # Maneja violaciones de índices únicos filtrados
            raise HTTPException(status_code=409, detail="Ya existe un perfil para este cliente (email o identificación)")
        except Exception as e:
            conn.rollback()
            raise


@router.post('/save-response', status_code=status.HTTP_201_CREATED)
def save_response(payload: SaveResponseRequest, user=Depends(get_current_user)):
    with get_conn() as conn:
        try:
            cursor = conn.cursor()

            # Valida que el perfil exista
            cursor.execute(
                "SELECT IsCompleted FROM dalilm.ClientProfiles WITH (NOLOCK) WHERE ProfileId = ?;",
                str(payload.profileId)
            )
            pr = cursor.fetchone()
            if not pr:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            if bool(pr.IsCompleted):
                raise HTTPException(status_code=400, detail="El perfil ya está finalizado")

            # Calcula orden
            cursor.execute(ORDER_SQL, str(payload.profileId))
            order = cursor.fetchone()[0]

            # Inserta respuesta
            cursor.execute(
                """
                INSERT INTO dalilm.ProfilingResponses
                (ProfileId, FlowStep, QuestionId, SelectedAnswer, AdditionalNotes, ResponseOrder)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                str(payload.profileId), payload.flowStep, payload.questionId,
                payload.selectedAnswer, payload.additionalNotes, int(order)
            )
            conn.commit()
            return {"saved": True, "order": order}
        except HTTPException:
            raise
        except Exception:
            conn.rollback()
            raise


@router.post('/complete')
def complete_profiling(payload: CompleteProfilingRequest, user=Depends(get_current_user)):
    profile_id = str(payload.profileId)
    with get_conn() as conn:
        try:
            cursor = conn.cursor()

            # 1) Trae respuestas
            cursor.execute(
                """
                SELECT QuestionId, SelectedAnswer
                FROM dalilm.ProfilingResponses WITH (NOLOCK)
                WHERE ProfileId = ?
                ORDER BY ResponseOrder ASC;
                """,
                profile_id
            )
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(status_code=400, detail="No hay respuestas registradas para este perfil")

            # 2) Scoring simple por conteo de categorías
            categories = ['inmediatista', 'planificador', 'familiar', 'maduro']
            counts = {c: 0 for c in categories}
            for r in rows:
                ans = (r.SelectedAnswer or '').strip().lower()
                if ans in counts:
                    counts[ans] += 1

            # Determina perfil final (mayoría). Empate: prioriza la última respuesta categórica.
            final_type = max(counts.items(), key=lambda kv: kv[1])[0]
            if len({v for v in counts.values() if v == counts[final_type]}) > 1:
                # empate, mira última respuesta que pertenezca a categorías
                for r in reversed(rows):
                    ans = (r.SelectedAnswer or '').strip().lower()
                    if ans in categories:
                        final_type = ans
                        break

            # 3) Reglas simples de productos / riesgo / estrategia
            product_map = {
                'inmediatista': 'Fondos de liquidez / money market; seguros de ahorro flexibles a corto plazo',
                'planificador': 'Fondos balanceados moderados; portafolios multiactivo; planes periódicos',
                'familiar': 'Seguros de vida/educación; fondos conservadores para metas familiares',
                'maduro': 'Rentas vitalicias; portafolios conservadores; distribución de ingresos',
            }
            risk_map = {
                'inmediatista': 'Bajo',
                'familiar': 'Bajo a Medio',
                'planificador': 'Medio',
                'maduro': 'Bajo',
            }
            strategy_map = {
                'inmediatista': 'Liquidez y preservación de capital a muy corto plazo',
                'planificador': 'Disciplina de aportes periódicos y diversificación',
                'familiar': 'Protección + ahorro con metas definidas',
                'maduro': 'Ingreso estable y baja volatilidad',
            }

            recommended = product_map.get(final_type, '')
            risk = risk_map.get(final_type, 'Medio')
            strategy = strategy_map.get(final_type, '')

            # 4) Persiste resultado + marca perfil como completado
            result_json = {
                "counts": counts,
                "answers": [{"q": r.QuestionId, "a": r.SelectedAnswer} for r in rows],
                "finalData": payload.finalData,
                "computedAt": datetime.utcnow().isoformat() + 'Z'
            }

            # Inserta o reemplaza resultado (por unicidad por ProfileId debería insertar 1 vez)
            cursor.execute(
                """
                INSERT INTO dalilm.ProfilingResults
                (ProfileId, FinalProfileType, RecommendedProducts, RiskLevel, InvestmentStrategy, ResultData)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                profile_id, final_type, recommended, risk, strategy, str(result_json)
            )

            # Actualiza ClientProfiles
            cursor.execute(
                "UPDATE dalilm.ClientProfiles SET ProfileType = ?, IsCompleted = 1 WHERE ProfileId = ?;",
                final_type, profile_id
            )

            conn.commit()
            return {
                "profileId": profile_id,
                "finalProfileType": final_type,
                "riskLevel": risk,
                "recommendedProducts": recommended,
                "investmentStrategy": strategy
            }
        except HTTPException:
            raise
        except pyodbc.IntegrityError:
            conn.rollback()
            raise HTTPException(status_code=409, detail="Este perfil ya tiene resultados guardados")
        except Exception:
            conn.rollback()
            raise


@router.get('/results/{profileId}')
def get_results(profileId: UUID, user=Depends(get_current_user)):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT FinalProfileType, RecommendedProducts, RiskLevel, InvestmentStrategy, ResultData, CreatedAt
            FROM dalilm.ProfilingResults WITH (NOLOCK)
            WHERE ProfileId = ?;
            """,
            str(profileId)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Resultados no encontrados para este perfil")
        return {
            "profileId": str(profileId),
            "finalProfileType": row.FinalProfileType,
            "riskLevel": row.RiskLevel,
            "recommendedProducts": row.RecommendedProducts,
            "investmentStrategy": row.InvestmentStrategy,
            "resultData": row.ResultData,
            "createdAt": row.CreatedAt.isoformat()
        }