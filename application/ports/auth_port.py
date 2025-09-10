# application/ports/auth_port.py
from abc import ABC, abstractmethod
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

class AuthPort(ABC):
    @abstractmethod
    def get_current_user(self, token: str) -> dict:
        """Valida un token y retorna la identidad del usuario"""
        pass
