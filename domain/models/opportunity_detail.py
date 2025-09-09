from typing import List, Optional
from pydantic import BaseModel

class OpportunityDetail(BaseModel):
    """Representa el detalle de una oportunidad de venta.

    Atributos:
        OpportunityId (int): Identificador único de la oportunidad.
        Title (str): Título de la oportunidad.
        Subtitle (str): Subtítulo de la oportunidad.
        Description (str): Descripción detallada de la oportunidad.
        EmailTemplate (str): Plantilla de correo electrónico asociada a la oportunidad.
        DaliPrompt (str): Prompt para DALL-E para generar imágenes relacionadas.
        Categories (List[str]): Lista de categorías a las que pertenece la oportunidad.
    """
    OpportunityId: int
    Title: str
    Subtitle: str
    Description: str
    EmailTemplate: str
    DaliPrompt: str
    Categories: List[str]