# core/exceptions.py
from fastapi import HTTPException, status


class BusinessException(HTTPException):
    """Excepción para errores de lógica de negocio.

    Se utiliza para encapsular errores que violan las reglas de negocio.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        """Inicializa la excepción de negocio.

        Args:
            detail (str): Mensaje de error detallado.
            status_code (int): Código de estado HTTP. Por defecto es 400.
        """
        super().__init__(status_code=status_code, detail=detail)

class ConnectionErrorException(HTTPException):
    """Excepción para errores de conexión.

    Se utiliza para encapsular errores que ocurren al intentar conectar
    con servicios externos o bases de datos.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        """Inicializa la excepción de error de conexión.

        Args:
            detail (str): Mensaje de error detallado.
            status_code (int): Código de estado HTTP. Por defecto es 500.
        """
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(HTTPException):
    """Excepción para recursos no encontrados.

    Se utiliza cuando una consulta no devuelve ningún resultado o un
    recurso específico no se encuentra.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_404_NOT_FOUND):
        """Inicializa la excepción de recurso no encontrado.

        Args:
            detail (str): Mensaje de error detallado.
            status_code (int): Código de estado HTTP. Por defecto es 404.
        """
        super().__init__(status_code=status_code, detail=detail)

class InvalidInputException(HTTPException):
    """Excepción para datos de entrada inválidos.

    Se utiliza cuando los datos proporcionados en una solicitud no son válidos
    o no cumplen con el formato esperado.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        """Inicializa la excepción de entrada inválida.

        Args:
            detail (str): Mensaje de error detallado.
            status_code (int): Código de estado HTTP. Por defecto es 422.
        """
        super().__init__(status_code=status_code, detail=detail)
