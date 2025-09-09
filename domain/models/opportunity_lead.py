from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class OpportunityLead(BaseModel):
    tipoDocum: str
    nroDocum: int
    nombres: str
    apellidos: str
    edad: Optional[float] = None
    sexo: Optional[str] = None
    telefonoCliente: Optional[str] = None
    celularCliente: Optional[str] = None
    emailCliente: Optional[str] = None
    empleadorCliente: Optional[str] = None
    extraDetails: Dict[str, Any]