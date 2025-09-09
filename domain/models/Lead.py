from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class Lead(BaseModel):
    """Representa un lead o cliente potencial.

    Atributos:
        tipoDocum (str): Tipo de documento del cliente.
        nroDocum (int): Número de documento del cliente.
        nombres (str): Nombres del cliente.
        apellidos (str): Apellidos del cliente.
        telefonoCliente (Optional[str]): Teléfono fijo del cliente.
        celularCliente (Optional[str]): Teléfono celular del cliente.
        emailCliente (Optional[str]): Correo electrónico del cliente.
        extraDetails (Dict[str, Any]): Detalles adicionales en un diccionario.
    """
    tipoDocum: str
    nroDocum: int
    nombres: str
    apellidos: str
    telefonoCliente: Optional[str] = None
    celularCliente: Optional[str] = None
    emailCliente: Optional[str] = None
    extraDetails: Dict[str, Any]