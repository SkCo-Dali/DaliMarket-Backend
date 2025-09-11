# application/ports/user_repository_port.py
from abc import ABC, abstractmethod
from domain.models.user import User

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        """Obtiene un usuario por su correo electrónico"""
        pass

