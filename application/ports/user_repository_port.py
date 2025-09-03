# application/ports/user_repository_port.py
from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_id_by_email(self, email: str) -> str:
        """Obtiene el ID de un usuario por su correo electrónico"""
        pass

