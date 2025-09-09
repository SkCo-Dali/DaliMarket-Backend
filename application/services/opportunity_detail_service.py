# application/services/opportunity_detail_service.py
from typing import Dict, List, Optional
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail


class OpportunityDetailService:
    """Servicio para gestionar la lógica de negocio de los detalles de oportunidades.

    Este servicio utiliza un puerto de repositorio para desacoplar la lógica
    de la implementación concreta de la base de datos.
    """
    def __init__(self, repository: OpportunityDetailRepositoryPort):
        """Inicializa el servicio de detalles de oportunidades.

        Args:
            repository (OpportunityDetailRepositoryPort): El repositorio a utilizar
                                                        para acceder a los datos.
        """
        self.repository = repository

    def list_details(self) -> List[OpportunityDetail]:
        """Obtiene una lista de todos los detalles de oportunidades.

        Returns:
            List[OpportunityDetail]: Una lista de detalles de oportunidades.
        """
        return self.repository.get_all()
    
    def get_detail_by_opportunity_id(self, opportunity_id: str) -> Optional[OpportunityDetail]:
        """Obtiene el detalle de una oportunidad por su ID.

        Args:
            opportunity_id (str): El ID de la oportunidad a buscar.

        Returns:
            Optional[OpportunityDetail]: El detalle de la oportunidad si se encuentra,
                                         de lo contrario None.
        """
        return self.repository.get_by_opportunity_id(opportunity_id)
