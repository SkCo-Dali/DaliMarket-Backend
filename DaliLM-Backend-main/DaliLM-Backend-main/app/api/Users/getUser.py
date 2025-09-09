from fastapi import APIRouter, HTTPException, Path
import pyodbc
import os
from dotenv import load_dotenv
from uuid import UUID

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


@router.get("/api/users/{id}")
def get_user_by_id(
    id: UUID = Path(..., description="ID del usuario en formato UUID")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
            SELECT *
            FROM dalilm.Users
            WHERE Id = ?
        """
        cursor.execute(query, str(id))
        row = cursor.fetchone()

        # 👇 Esta línea debe ir antes de cerrar el cursor
        columns = [column[0] for column in cursor.description] if row else []

        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user = dict(zip(columns, row))

        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el usuario: {str(e)}")

'''
# --- Ejecución directa para pruebas ---
if __name__ == "__main__":

    respuesta = get_user_by_id('75E5BFC6-FA2B-4E0D-A047-7D4295363591')
    print("Respuesta de la consulta:")
    print(respuesta)
    '''