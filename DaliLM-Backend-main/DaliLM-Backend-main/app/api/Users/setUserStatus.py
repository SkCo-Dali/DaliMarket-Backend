from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Path, Depends
import pyodbc
import os
from pydantic import BaseModel, EmailStr, field_validator
from dotenv import load_dotenv
import json
from uuid import UUID
from auth_azure import get_current_user

from uuid import uuid4

# Carga del .env solo para desarrollo local
load_dotenv()

# Configuración de la base de datos
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# Crear router de FastAPI
router = APIRouter()


# Modelo para recibir el estado
class ActivateUserInput(BaseModel):
    isActive: bool


@router.put("/api/users/{id}/activate")
def activate_user(
    id: UUID = Path(..., description="ID del usuario en formato UUID"),
    data: dict = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        # 1. Validar rol del usuario autenticado
        requester_email = current_user["email"]

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM dalilm.Users WHERE Email = ?", requester_email)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")

        requester_role = row[0].lower()
        if requester_role not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para activar o desactivar usuarios.")

        # 2. Validación del payload
        input_data = ActivateUserInput(**data)

        # 3. Verificar que el usuario objetivo exista
        cursor.execute("SELECT 1 FROM dalilm.Users WHERE Id = ?", str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # 4. Actualizar el estado (soft toggle)
        cursor.execute("""
            UPDATE dalilm.Users
            SET IsActive = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, int(input_data.isActive), str(id))

        conn.commit()
        cursor.close()
        conn.close()

        action = "activado" if input_data.isActive else "desactivado"
        return {"message": f"Usuario {action} correctamente."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado del usuario: {str(e)}")
