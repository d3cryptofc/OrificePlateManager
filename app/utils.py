import json
from pydantic import ValidationError
from pytz import timezone
from datetime import datetime

# Obtendo fuso horário de brasília.
TIMEZONE = timezone('America/Sao_Paulo')


def current_datetime():
    """
    Obtém data e hora atual carimbada com o fuso horário de brasília.
    """
    return datetime.now(TIMEZONE)


def datetime_to_brt(date_time: datetime):
    """
    Converte um objeto datetime para um datetime com fuso horário de brasília.
    """
    return date_time.astimezone(TIMEZONE)


def get_pydantic_validation_errors(exception: ValidationError):
    """
    Obtém os erros de uma validação feita no pydantic, mas o erro vem
    compatível com serialização JSON.
    """
    return json.loads(exception.json(
        include_url=False,
        include_context=False,
        include_input=False
    ))
