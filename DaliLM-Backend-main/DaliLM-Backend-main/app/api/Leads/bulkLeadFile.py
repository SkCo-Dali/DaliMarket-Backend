
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from fastapi.encoders import jsonable_encoder
from typing import Optional, Any, List, Tuple
import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv
from uuid import uuid4
import json
from datetime import datetime
from auth_azure import get_current_user

# ======================================================
# Bulk Leads Upload API (finalized with rollback-before-fallback)
# - Normaliza vacíos/"null"/pd.NA -> None
# - DocumentNumber -> BIGINT seguro (int o None), NUNCA tupla/lista
# - Evita "TVP rows must be Sequence objects" con guard para secuencias
# - Priority como NVARCHAR (mantiene "Baja/Media/Alta")
# - Respuestas JSON-safe con jsonable_encoder (datetimes -> ISO-8601)
# - Inserción por lotes con fast_executemany y commit por batch
# - CSV en chunks para empezar a insertar antes
# - IMPORTANTE: si falla executemany, hace ROLLBACK del lote antes del fallback fila a fila
# ======================================================

load_dotenv()
router = APIRouter()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# -------- Helpers --------
NULL_WORDS = {"", "null", "none", "nan", "na", "<na>", "nat"}

def _is_nullish(v: Any) -> bool:
    if v is None:
        return True
    try:
        if pd.isna(v):  # cubre pd.NA, NaN, NaT
            return True
    except Exception:
        pass
    s = str(v).strip()
    return s == "" or s.lower() in NULL_WORDS or s in ("<NA>", "NaT")

def s(v: Any) -> Optional[str]:
    """String seguro: None si vacío/nullish; str limpio en otro caso."""
    if _is_nullish(v):
        return None
    return str(v).strip()

def fnum(v: Any) -> Optional[float]:
    """Float seguro: acepta coma decimal; None si vacío/invalid."""
    if _is_nullish(v):
        return None
    sv = str(v).strip()
    if sv.count(",") == 1 and sv.count(".") == 0:
        sv = sv.replace(",", ".")
    try:
        return float(sv)
    except Exception:
        return None

def iint(v: Any) -> Optional[int]:
    """Int seguro: '10.0'->10; None si vacío/invalid."""
    if _is_nullish(v):
        return None
    sv = str(v).strip().replace(",", ".")
    try:
        return int(float(sv))
    except Exception:
        return None

def _parse_jsonish(value: Any) -> Optional[str]:
    """Intenta parsear JSON-ish; devuelve JSON string o None."""
    if _is_nullish(value):
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    svalue = str(value).strip()
    try:
        return json.dumps(json.loads(svalue), ensure_ascii=False)
    except Exception:
        try:
            s2 = svalue.replace("'", '\"')
            return json.dumps(json.loads(s2), ensure_ascii=False)
        except Exception:
            return None

def _to_datetime_or_none(v: Any) -> Optional[datetime]:
    if _is_nullish(v):
        return None
    try:
        return pd.to_datetime(v).to_pydatetime()
    except Exception:
        return None

def doc_bigint(v: Any) -> Optional[int]:
    """
    DocumentNumber → BIGINT (int o None). NUNCA devuelve tuplas/listas.
    Maneja vacíos/<NA>, notación científica, y separadores de miles.
    """
    # Desanidar si viene como [None] o (None,) o {None}
    if isinstance(v, (list, tuple, set)):
        v = next((x for x in v if x is not None), None)
    if _is_nullish(v):
        return None
    sv = str(v).strip()
    # 1) Intento robusto via float (cubre '1.23E+10', '12345.0')
    try:
        n = int(float(sv))
        if 0 <= n <= 9223372036854775807:
            return n
    except Exception:
        pass
    # 2) Limpieza de separadores comunes
    sv2 = sv.replace(" ", "").replace(",", "").replace(".", "")
    if sv2.isdigit():
        try:
            n2 = int(sv2)
            return n2 if 0 <= n2 <= 9223372036854775807 else None
        except Exception:
            return None
    return None

def _open_conn() -> pyodbc.Connection:
    try:
        return pyodbc.connect(CONN_STR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar a SQL Server: {e}")

def _get_user_uuid(conn: pyodbc.Connection, email: str) -> str:
    """Obtiene el Id (UUID) del usuario en dalilm.Users a partir del email."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT TOP 1 Id FROM dalilm.Users WHERE Email = ? AND IsActive = 1", (email,))
            row = cur.fetchone()
            if not row or not row[0]:
                raise HTTPException(status_code=404, detail=f"Usuario no encontrado o inactivo: {email}")
            return str(row[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando usuario por email ({email}): {e}")

SQL_INSERT = """
INSERT INTO dalilm.Leads (
    CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
    Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
    NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios,
    CampaignOwnerName, Age, Gender, PreferredContactChannel
)
VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(),
    ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""

def _row_to_params(row: pd.Series, user_uuid: str) -> Tuple[Any, ...]:
    product_json = _parse_jsonish(row.get("Product"))
    tags_json = _parse_jsonish(row.get("Tags"))
    selected_portfolios_json = _parse_jsonish(row.get("SelectedPortfolios"))
    next_follow_up = _to_datetime_or_none(row.get("NextFollowUp"))
    value_num = fnum(row.get("Value"))
    if value_num is None:
        value_num = 0.0
    priority_val = s(row.get("Priority"))  # Priority como NVARCHAR
    age_int = iint(row.get("Age"))

    params = (
        user_uuid,                      # CreatedBy
        str(uuid4()),                   # Id
        (s(row.get("Name")) or "Sin Nombre"),  # Name (default "Sin Nombre" if empty)
        s(row.get("Email")),            # Email
        s(row.get("Phone")),            # Phone
        doc_bigint(row.get("DocumentNumber")),  # DocumentNumber -> BIGINT
        s(row.get("Company")),          # Company
        s(row.get("Source")),           # Source
        s(row.get("Campaign")),         # Campaign
        product_json,                   # Product
        s(row.get("Stage")),            # Stage
        priority_val,                   # Priority (NVARCHAR)
        value_num,                      # Value (FLOAT)
        user_uuid,                      # AssignedTo
        next_follow_up,                 # NextFollowUp (datetime o None)
        s(row.get("Notes")),            # Notes
        tags_json,                      # Tags
        s(row.get("DocumentType")),     # DocumentType
        selected_portfolios_json,       # SelectedPortfolios
        s(row.get("CampaignOwnerName")),# CampaignOwnerName
        age_int,                        # Age (INT) o None
        s(row.get("Gender")),           # Gender
        s(row.get("PreferredContactChannel")), # PreferredContactChannel
    )

    # Guard: NO se permiten secuencias/dicts (evita TVP o binding incorrecto)
    if any(isinstance(x, (list, tuple, set, dict)) for x in params):
        bad = [(i, type(x).__name__) for i, x in enumerate(params) if isinstance(x, (list, tuple, set, dict))]
        raise HTTPException(status_code=400, detail=jsonable_encoder({
            "message": "Un parámetro no es escalar (lista/tupla/dict) y no puede enviarse como valor simple.",
            "where": bad
        }))

    return params

def _executemany_with_fallback(conn: pyodbc.Connection, cur, params_batch: List[Tuple[Any, ...]]) -> Tuple[int, List[dict]]:
    """
    Intenta executemany (fast_executemany) para todo el batch.
    Si falla, hace ROLLBACK del lote y luego fallback fila por fila (sin commit).
    """
    inserted = 0
    errors: List[dict] = []
    if not params_batch:
        return inserted, errors
    try:
        cur.fast_executemany = True
        cur.executemany(SQL_INSERT, params_batch)
        inserted = len(params_batch)
    except Exception as batch_ex:
        # Deshacer cualquier inserción parcial del batch
        try:
            conn.rollback()
        except Exception:
            pass
        # Fila por fila, el commit lo hará el caller
        for i, p in enumerate(params_batch):
            try:
                cur.execute(SQL_INSERT, p)
                inserted += 1
            except Exception as ex:
                errors.append({
                    "row_index": i,  # índice relativo al batch; el caller lo ajusta
                    "error": str(ex),
                    "param_types": [type(x).__name__ for x in p]
                })
    return inserted, errors

@router.post("/api/leads/bulk")
def bulk_upload_leads(
    file: UploadFile = File(...),
    ipAddress: Optional[str] = Query(None, description="IP del cliente"),
    userAgent: Optional[str] = Query(None, description="UA del cliente"),
    batch_size: int = Query(500, ge=50, le=5000, description="Filas por lote antes de commit"),
    csv_chunksize: int = Query(10000, ge=1000, le=200000, description="Filas por chunk al leer CSV"),
    current_user: dict = Depends(get_current_user)
):
    """
    Carga masiva de Leads desde CSV/Excel con saneo de datos y commits por lote.
    """
    conn = None
    try:
        # Usuario autenticado
        requester_email = current_user.get("email") or current_user.get("preferred_username") or current_user.get("upn")
        if not requester_email:
            raise HTTPException(status_code=401, detail="No se encontró el email en el token.")

        # Tipo de archivo
        filename = (file.filename or "").lower()
        is_csv = filename.endswith(".csv")
        is_xlsx = filename.endswith((".xls", ".xlsx"))
        if not (is_csv or is_xlsx):
            raise HTTPException(status_code=400, detail="Formato no soportado. Use .csv, .xls o .xlsx")

        # Conexión y usuario
        conn = _open_conn()
        conn.autocommit = False  # transacción explícita
        cur = conn.cursor()
        user_uuid = _get_user_uuid(conn, requester_email)

        expected_cols = [
            "Name", "Email", "Phone", "DocumentNumber", "Company", "Source", "Campaign",
            "Product", "Stage", "Priority", "Value", "NextFollowUp", "Notes",
            "Tags", "DocumentType", "SelectedPortfolios", "CampaignOwnerName",
            "Age", "Gender", "PreferredContactChannel"
        ]

        total_inserted = 0
        total_failed = 0
        all_errors: List[dict] = []
        base_index = 0  # índice absoluto a lo largo de todo el archivo

        if is_csv:
            try:
                file.file.seek(0)
            except Exception:
                pass

            reader = pd.read_csv(
                file.file,
                dtype={"DocumentNumber": "string", "Phone": "string", "Company": "string"},
                na_values=["null", "NULL", "Null"],
                chunksize=csv_chunksize
            )

            for chunk_df in reader:
                # Asegura columnas esperadas
                for col in expected_cols:
                    if col not in chunk_df.columns:
                        chunk_df[col] = pd.NA

                params_buffer: List[Tuple[Any, ...]] = []
                for _, row in chunk_df.iterrows():
                    params_buffer.append(_row_to_params(row, user_uuid))
                    if len(params_buffer) >= batch_size:
                        try:
                            inserted, errs = _executemany_with_fallback(conn, cur, params_buffer)
                            conn.commit()
                            total_inserted += inserted
                            for e in errs:
                                e["row_index"] = base_index + e["row_index"]
                            total_failed += len(params_buffer) - inserted
                            all_errors.extend(errs)
                        except Exception as ex:
                            conn.rollback()
                            # Fallback extremo: fila por fila con commit por fila
                            for i, p in enumerate(params_buffer):
                                try:
                                    cur.execute(SQL_INSERT, p)
                                    conn.commit()
                                    total_inserted += 1
                                except Exception as ex2:
                                    conn.rollback()
                                    all_errors.append({
                                        "row_index": base_index + i,
                                        "error": str(ex2),
                                        "param_types": [type(x).__name__ for x in p]
                                    })
                                    total_failed += 1
                        base_index += len(params_buffer)
                        params_buffer.clear()

                # Flush del último batch del chunk
                if params_buffer:
                    try:
                        inserted, errs = _executemany_with_fallback(conn, cur, params_buffer)
                        conn.commit()
                        total_inserted += inserted
                        for e in errs:
                            e["row_index"] = base_index + e["row_index"]
                        total_failed += len(params_buffer) - inserted
                        all_errors.extend(errs)
                    except Exception as ex:
                        conn.rollback()
                        for i, p in enumerate(params_buffer):
                            try:
                                cur.execute(SQL_INSERT, p)
                                conn.commit()
                                total_inserted += 1
                            except Exception as ex2:
                                conn.rollback()
                                all_errors.append({
                                    "row_index": base_index + i,
                                    "error": str(ex2),
                                    "param_types": [type(x).__name__ for x in p]
                                })
                                total_failed += 1
                    base_index += len(params_buffer)
                    params_buffer.clear()

        else:
            # Excel: lectura completa
            df = pd.read_excel(file.file)
            if df.empty:
                conn.close()
                raise HTTPException(status_code=400, detail="El archivo está vacío.")
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = pd.NA

            params_buffer: List[Tuple[Any, ...]] = []
            for _, row in df.iterrows():
                params_buffer.append(_row_to_params(row, user_uuid))
                if len(params_buffer) >= batch_size:
                    try:
                        inserted, errs = _executemany_with_fallback(conn, cur, params_buffer)
                        conn.commit()
                        total_inserted += inserted
                        for e in errs:
                            e["row_index"] = base_index + e["row_index"]
                        total_failed += len(params_buffer) - inserted
                        all_errors.extend(errs)
                    except Exception as ex:
                        conn.rollback()
                        for i, p in enumerate(params_buffer):
                            try:
                                cur.execute(SQL_INSERT, p)
                                conn.commit()
                                total_inserted += 1
                            except Exception as ex2:
                                conn.rollback()
                                all_errors.append({
                                    "row_index": base_index + i,
                                    "error": str(ex2),
                                    "param_types": [type(x).__name__ for x in p]
                                })
                                total_failed += 1
                    base_index += len(params_buffer)
                    params_buffer.clear()

            # Flush final
            if params_buffer:
                try:
                    inserted, errs = _executemany_with_fallback(conn, cur, params_buffer)
                    conn.commit()
                    total_inserted += inserted
                    for e in errs:
                        e["row_index"] = base_index + e["row_index"]
                    total_failed += len(params_buffer) - inserted
                    all_errors.extend(errs)
                except Exception as ex:
                    conn.rollback()
                    for i, p in enumerate(params_buffer):
                        try:
                            cur.execute(SQL_INSERT, p)
                            conn.commit()
                            total_inserted += 1
                        except Exception as ex2:
                            conn.rollback()
                            all_errors.append({
                                "row_index": base_index + i,
                                "error": str(ex2),
                                "param_types": [type(x).__name__ for x in p]
                            })
                            total_failed += 1
                base_index += len(params_buffer)
                params_buffer.clear()

        conn.close()

        if all_errors:
            # Limitar el payload de errores para no saturar la respuesta
            raise HTTPException(
                status_code=400,
                detail=jsonable_encoder({
                    "message": "Algunas filas fallaron. Revisa 'errors' para detalles.",
                    "inserted": int(total_inserted),
                    "failed": int(total_failed),
                    "errors": all_errors[:50]
                })
            )

        return {
            "inserted": int(total_inserted),
            "failed": int(total_failed),
            "message": f"{total_inserted} leads cargados exitosamente."
        }

    except HTTPException as e:
        # Asegura rollback y cierre
        if conn is not None:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
        raise e
    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Error en la carga masiva: {str(e)}")
