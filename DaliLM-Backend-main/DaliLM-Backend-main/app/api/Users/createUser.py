from fastapi import APIRouter, HTTPException, Depends
import pyodbc
import os
from pydantic import BaseModel, EmailStr, field_validator
from dotenv import load_dotenv
import json
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

# Modelo de entrada
class UserInput(BaseModel):
    name: str
    email: EmailStr
    role: str
    isActive: bool = True

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

    @field_validator("email")
    def email_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("El correo no puede estar vacío")
        return v

    @field_validator("role")
    def role_must_be_valid(cls, v):
        allowed_roles = ['admin', 'seguridad', 'analista', 'supervisor', 'gestor', 'director', 'promotor', 'aliado', 'socio', 'fp']
        if v not in allowed_roles:
            raise ValueError(f"El rol '{v}' no es válido. Roles permitidos: {', '.join(allowed_roles)}")
        return v


# Endpoint POST /api/users
@router.post("/api/users")
def create_user(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        # 1. Obtener el correo autenticado desde el token
        requester_email = current_user["email"]

        # 2. Verificar rol del usuario autenticado en la base de datos
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM dalilm.Users WHERE Email = ?", requester_email)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")

        requester_role = row[0].lower()
        if requester_role not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para crear usuarios.")

        # 3. Validación de los datos del usuario a crear
        user = UserInput(**data)
        user_id = str(uuid4())

        # 4. Verificar si ya existe un usuario con ese correo
        cursor.execute("SELECT 1 FROM dalilm.Users WHERE Email = ?", user.email)
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Ya existe un usuario con este correo.")

        # 5. Crear el usuario
        cursor.execute("""
            INSERT INTO dalilm.Users (Id, Name, Email, Role, IsActive, CreatedAt, UpdatedAt)
            VALUES (?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())
        """, user_id, user.name, user.email, user.role, int(user.isActive))

        # 6. Llamar al SP para actualizar datos relacionados
        cursor.execute("EXEC dalilm.SP_Actualiza_Usuario ?", user.email)

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": "Usuario creado exitosamente.",
            "user": {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "isActive": user.isActive
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")
