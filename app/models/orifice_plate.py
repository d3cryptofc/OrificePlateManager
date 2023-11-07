import sqlalchemy as sa
from sqlalchemy_utc import UtcDateTime
from sqlalchemy_serializer import SerializerMixin

from app.database import db
from app.models.operator import Operator
from app.utils import current_datetime


class OrificePlate(db.Model, SerializerMixin):
    __tablename__ = 'orifice_plates'

    id = sa.Column(sa.Integer, primary_key=True)

    serial_number = sa.Column(sa.VARCHAR(16), nullable=False)
    certificate_number = sa.Column(sa.VARCHAR(20), nullable=False)
    certificate_url = sa.Column(sa.VARCHAR(255), nullable=False, default='')
    calibration_date = sa.Column(sa.Date, nullable=False)
    first_installation_date = sa.Column(sa.Date, nullable=True)
    due_date = sa.Column(sa.Date, nullable=False)
    internal_diameter_reference = sa.Column(sa.Float, nullable=False)
    external_diameter = sa.Column(sa.Float, nullable=False)
    type = sa.Column(sa.VARCHAR(3), nullable=False)
    local = sa.Column(sa.VARCHAR(40), nullable=False)
    point = sa.Column(sa.VARCHAR(20), nullable=False)
    status_text = sa.Column(sa.VARCHAR(20), nullable=False)
    status_date = sa.Column(sa.Date)
    status_local = sa.Column(sa.VARCHAR(40))

    created_by_operator = sa.Column(sa.VARCHAR(30),
                                    sa.ForeignKey(Operator.login),
                                    nullable=False)

    created_at = sa.Column(UtcDateTime,
                           nullable=False,
                           default=current_datetime)

    __table_args__ = (
        sa.CheckConstraint(type.in_(['VPP', 'VEF'])),
        sa.CheckConstraint(status_text.in_([
            'REMOVIDA',
            'AGUARDANDO RETORNO',
            'RESERVADA',
            'INSTALADA/OPERANDO'
        ])),
    )
