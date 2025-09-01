from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class OpportunityLead(BaseModel):
    tipoDocum: str
    nroDocum: int
    nombres: str
    apellidos: str
    telefonoCliente: Optional[str] = None
    celularCliente: Optional[str] = None
    emailCliente: Optional[str] = None
    extraDetails: Dict[str, Any]