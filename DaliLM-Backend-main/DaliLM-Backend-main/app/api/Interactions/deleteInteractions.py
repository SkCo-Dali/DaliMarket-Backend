from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

# Conexión SQL Server
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

@router.delete("/api/interactions/{id}")
def delete_interaction(id: UUID):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar si la interacción existe
        cursor.execute("SELECT COUNT(*) FROM dalilm.Interactions WHERE Id = ?", str(id))
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="Interacción no encontrada")

        # Eliminar la interacción
        cursor.execute("DELETE FROM dalilm.Interactions WHERE Id = ?", str(id))
        conn.commit()

        return {"message": "Interacción eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar interacción: {str(e)}")
    finally:
        cursor.close()
        conn.close()
