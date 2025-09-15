# application/ports/log_repository_port.py
from abc import ABC, abstractmethod
from domain.models.log import Log

class LogRepositoryPort(ABC):
    @abstractmethod
    def save(self, log: Log) -> None:
        """Guarda un registro de log en el repositorio."""
        pass