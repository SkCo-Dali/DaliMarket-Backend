# routes_leads.py
from fastapi import APIRouter, Depends, HTTPException
import pyodbc, os
from auth_azure import get_current_user

router = APIRouter()
conn_str = (f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};DATABASE={os.getenv('SQL_DATABASE')};"
            f"UID={os.getenv('SQL_USERNAME')};PWD={os.getenv('SQL_PASSWORD')}")

@router.get("/api/lead-assignments")
def list_visible_leads(current=Depends(get_current_user)):
    email = current["email"]
    with pyodbc.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute("SELECT Id FROM dalilm.Users WHERE Email=? AND IsActive=1", email)
        row = cur.fetchone()
        if not row:
            raise HTTPException(403, "Usuario no válido o inactivo.")
        actor_id = row[0]

        cur.execute("SELECT * FROM dalilm.fn_visible_leads(?)", actor_id)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
