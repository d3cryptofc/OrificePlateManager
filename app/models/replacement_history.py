import sqlalchemy as sa
from sqlalchemy_utc import UtcDateTime
from sqlalchemy_serializer import SerializerMixin

from app.database import db
from app.utils import current_datetime


class PlateReplacement(db.Model, SerializerMixin):
    __tablename__ = 'replacement_history'

    id = sa.Column(sa.Integer, primary_key=True)

    before_certificate_number = sa.Column(sa.VARCHAR(20), nullable=False)
    after_certificate_number = sa.Column(sa.VARCHAR(20), nullable=False)
    reason = sa.Column(sa.VARCHAR(100), nullable=False)
    created_at = sa.Column(UtcDateTime,
                           nullable=False,
                           default=current_datetime)
