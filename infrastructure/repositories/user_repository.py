# infrastructure/repositories/user_repository.py
import logging
from fastapi import HTTPException
from domain.models.user import User
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter


class UserRepository:
    def __init__(self, adapter: SqlServerAdapter):
        self.adapter = adapter

    def get_user_by_email(self, email: str) -> User:
        """
        Obtiene un usuario de SQL Server a partir de su correo electrónico.
        """
        try:
            query = "SELECT Id, idAgte FROM dalilm.Users WHERE Email = ?"
            result = self.adapter.execute_query(query, (email,), fetchone=True)

            if not result:
                logging.error(f"Usuario no encontrado para email: {email}")
                raise HTTPException(
                    status_code=404, detail=f"Usuario con email {email} no encontrado."
                )

            return User(id=result[0], id_agte=result[1])

        except HTTPException:
            # si ya lanzamos el error, lo dejamos pasar
            raise
        except Exception as e:
            logging.error(f"Error al consultar el usuario por email {email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar el usuario por email {email}: {str(e)}",
            )
        
    def get_id_agte_by_email(self, email: str) -> int:
        """
        Obtiene el idAgte de un usuario a partir de su correo electrónico.
        """
        try:
            query = "SELECT idAgte FROM dalilm.Users WHERE Email = ?"
            result = self.adapter.execute_query(query, (email,), fetchone=True)
            if not result:
                logging.error(f"Usuario no encontrado para email: {email}")
                raise HTTPException(
                    status_code=404, detail=f"Usuario con email {email} no encontrado."
                )
            return result[0]
        except HTTPException:
            # si ya lanzamos el error, lo dejamos pasar
            raise
        except Exception as e:
            logging.error(f"Error al consultar el idAgte por email {email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar el idAgte por email {email}: {str(e)}",
            )
