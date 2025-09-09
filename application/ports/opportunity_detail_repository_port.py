# application/ports/opportunity_detail_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List

from domain.models.opportunity_detail import OpportunityDetail


class OpportunityDetailRepositoryPort(ABC):
    """Define el puerto del repositorio para los detalles de oportunidades.

    Esta clase abstracta define la interfaz que deben implementar los adaptadores
    de repositorio para interactuar con la fuente de datos de detalles de oportunidades.
    """

    @abstractmethod
    def get_all(self) -> List[OpportunityDetail]:
        """Obtiene todos los detalles de oportunidades.

        Returns:
            List[OpportunityDetail]: Una lista de todos los detalles de oportunidades.
        """
        pass

    @abstractmethod
    def get_by_opportunity_id(self, opportunity_id: int) -> OpportunityDetail:
        """Obtiene el detalle de una oportunidad por su ID.

        Args:
            opportunity_id (int): El ID de la oportunidad a buscar.

        Returns:
            OpportunityDetail: El detalle de la oportunidad encontrada.
        """
        pass
