from fastapi import APIRouter, HTTPException, Path, Request, Depends
import pyodbc
import os
from pydantic import BaseModel, EmailStr, field_validator
from dotenv import load_dotenv
from uuid import UUID
from auth_azure import get_current_user

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

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

# Modelo de entrada para actualizar
class UserUpdateInput(BaseModel):
    name: str
    email: EmailStr
    role: str
    isActive: bool

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


@router.put("/api/users/{id}")
def update_user(
    id: UUID = Path(..., description="ID del usuario en formato UUID"),
    data: dict = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        user = UserUpdateInput(**data)

        #Solo admins pueden modificar roles
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Role FROM dalilm.Users WHERE Email = ?
        """, current_user["email"])
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")
        
        user_role = row[0]
        if user_role not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para actualizar roles de usuario.")

        # Verificar que el usuario exista
        cursor.execute("""
            SELECT 1 
            FROM dalilm.Users 
            WHERE Id = ?
        """, str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Verificar que no exista otro usuario con el mismo correo
        cursor.execute("""
            SELECT 1 
            FROM dalilm.Users 
            WHERE Email = ? AND Id <> ?
        """, user.email, str(id))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Ya existe otro usuario con este correo.")

        # Actualizar usuario
        cursor.execute("""
            UPDATE dalilm.Users
            SET Name = ?, Email = ?, Role = ?, IsActive = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, user.name, user.email, user.role, int(user.isActive), str(id))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Usuario actualizado exitosamente."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")
