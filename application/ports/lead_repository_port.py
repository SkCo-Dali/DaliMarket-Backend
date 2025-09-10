# application/ports/lead_repository_port.py
from abc import ABC, abstractmethod
from domain.models.lead_ import Lead


class LeadRepositoryPort(ABC):
    @abstractmethod
    def create_lead(self, lead: Lead) -> None:
        """Crea un lead en el repositorio (ej. SQL Server)"""
        pass
