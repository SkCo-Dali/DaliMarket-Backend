# infrastructure/repositories/user_repository.py
import logging
from fastapi import HTTPException
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter


class UserRepository:
    def __init__(self, adapter: SqlServerAdapter):
        self.adapter = adapter

    def get_id_by_email(self, email: str) -> str:
        """
        Obtiene el Id de un usuario en SQL Server a partir de su correo electrónico.
        """
        try:
            query = "SELECT Id FROM dalilm.Users WHERE Email = ?"
            result = self.adapter.execute_query(query, (email,), fetchone=True)

            if not result:
                logging.error(f"Usuario no encontrado para email: {email}")
                raise HTTPException(status_code=404, detail=f"Usuario con email {email} no encontrado.")

            return result[0]

        except HTTPException:
            # si ya lanzamos el error, lo dejamos pasar
            raise
        except Exception as e:
            logging.error(f"Error al consultar el usuario por email {email}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al consultar el usuario por email {email}: {str(e)}")
