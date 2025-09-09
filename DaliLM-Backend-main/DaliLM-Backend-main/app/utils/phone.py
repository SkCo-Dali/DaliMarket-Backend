import re

def is_valid_co_number(number: str):
    """
    Regla de ejemplo para Colombia:
    - Solo dígitos
    - 10 dígitos
    - Empieza en 3
    """
    original = number
    number = re.sub(r"\D", "", number)
    if len(number) != 12:
        return False, "Debe tener 12 dígitos (se incluye el código del país 57)"
    if not number.startswith("573"):
        return False, "Debe iniciar en 573"
    return True, None
