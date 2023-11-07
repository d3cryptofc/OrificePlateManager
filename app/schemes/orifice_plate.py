from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, validator, Field
from pydantic.errors import MissingError


class OrificePlatePostSchema(BaseModel):
    """
    Modelo de validação de entrada de dados do recurso de adição de placas
    de orifício.
    """
    class Config:
        extra = 'forbid'

    serial_number: str = Field(min_length=9, max_length=16)
    certificate_number: str = Field(min_length=9, max_length=20)
    certificate_url: str = Field(max_length=255)
    calibration_date: date
    first_installation_date: Optional[date]
    due_date: date
    internal_diameter_reference: float
    external_diameter: float
    type: Literal['VPP', 'VEF']
    local: str = Field(min_length=5, max_length=40)
    point: str = Field(min_length=5, max_length=20)
    status_text: Literal['REMOVIDA',
                         'AGUARDANDO RETORNO',
                         'RESERVADA',
                         'INSTALADA/OPERANDO']
    status_date: Optional[date] = None
    status_local: Optional[str] = Field(min_length=5,
                                        max_length=40,
                                        default=None)

    @validator('status_date', pre=True)
    @classmethod
    def validate_status_date(cls, value, values):
        status_text = values.get('status_text')
        statuses = ('REMOVIDA', 'INSTALADA/OPERANDO')

        # Caso a situação seja REMOVIDA ou INSTALADA/OPERANDO e `status_text`
        # nào for informado.
        if status_text in statuses and not value:
            # Informa que o campo está faltando.
            raise MissingError

        # Caso a situação não seja REMOVIDA ou INSTALADA/OPERANDO
        # e `status_date` for informado.
        if status_text not in statuses and value:
            raise ValueError(
                'field not supported in current `status_text` value'
            )

        return value

    @validator('status_local', pre=True)
    @classmethod
    def validate_status_local(cls, value, values):
        status_text = values.get('status_text')
        statuses = ('RESERVADA',)

        # Caso a situação seja RESERVADA e `status_local` nào for informado.
        if status_text in statuses and not value:
            # Informa que o campo está faltando.
            raise MissingError

        # Caso a situação não seja RESERVADA e `status_local` for informado.
        if status_text not in statuses and value:
            raise ValueError(
                'field not supported in current `status_text` value'
            )

        return value


class OrificePlatePutSchema(BaseModel):
    """
    Modelo de validação de entrada de dados do recurso de substituição de
    placas de orifício.
    """
    class Config:
        extra = 'forbid'

    serial_number: str = Field(min_length=9, max_length=16)
    certificate_number: str = Field(min_length=9, max_length=20)
    certificate_url: str = Field(max_length=255)
    internal_diameter_reference: float
    reason: str = Field(min_length=10, max_length=100)


class OrificePlatePatchSchema(OrificePlatePostSchema):
    """
    Modelo de validação de entrada de dados do recurso de edição de
    placas de orifício.
    """
    class Config:
        extra = 'forbid'

    id: int


class OrificePlateDeleteSchema(BaseModel):
    """
    Modelo de validação de entrada de dados do recurso de remoção de placas
    de orifício.
    """
    class Config:
        extra = 'forbid'

    plate_id: int
