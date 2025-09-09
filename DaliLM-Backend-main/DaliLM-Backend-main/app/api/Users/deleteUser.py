from fastapi import APIRouter, HTTPException, Path, Depends
import pyodbc
import os
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


@router.delete("/api/users/{id}")
def delete_user(
    id: UUID = Path(..., description="ID del usuario en formato UUID"),
    current_user: dict = Depends(get_current_user)
):
    try:
        requester_email = current_user["email"]

        # Validar rol en base de datos
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM dalilm.Users WHERE Email = ?", requester_email)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=403, detail="Usuario autenticado no encontrado en la base de datos.")

        requester_role = row[0].lower()
        if requester_role not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios.")

        # Verificar que el usuario a eliminar exista
        cursor.execute("SELECT 1 FROM dalilm.Users WHERE Id = ?", str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Soft delete (IsActive = 0)
        cursor.execute("""
            UPDATE dalilm.Users
            SET IsActive = 0, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, str(id))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Usuario eliminado correctamente (soft delete)."}


    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")
