import re

def first_name(full_name: str) -> str:
    if not full_name:
        return ""
    return full_name.strip().split()[0]

def build_wa_me_link(country_code: int | str, number: str) -> str:
    number_digits = re.sub(r"\D", "", number or "")
    cc = str(country_code)
    if number_digits.startswith(cc):
        return f"https://wa.me/{number_digits}"
    return f"https://wa.me/{cc}{number_digits}"
