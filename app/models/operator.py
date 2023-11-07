from datetime import timedelta

import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy_utc import UtcDateTime

from app.database import db
from app.utils import current_datetime


class Operator(db.Model, SerializerMixin):
    __tablename__ = 'operators'

    login = sa.Column(sa.VARCHAR(30), primary_key=True)
    password = sa.Column(sa.VARCHAR(102), nullable=False)
    logged_at = sa.Column(UtcDateTime)
    expires_at = sa.Column(UtcDateTime)

    timedelta_renewal = timedelta(minutes=5)
    timedelta_expiration = timedelta(minutes=20)

    @property
    def is_logged(self):
        """
        Retorna se o operador está logado.
        """
        return (self.logged_at, self.expires_at) != (None, None)

    @property
    def is_expired(self):
        """
        Retorna se o login está com data expirada.
        """
        # Obtendo data e hora atual.
        now = current_datetime()

        # Caso não haja data de login, finaliza função retornando None.
        if not self.is_logged:
            return

        # Retorna True se estiver expirado, False se não.
        return now - self.expires_at > self.timedelta_renewal \
            or now - self.logged_at > self.timedelta_expiration

    def set_logged(self):
        """
        Define o operador como logado, em outras palavras, adiciona data
        de login e expiração.
        """
        # Obtendo data e hora atual.
        now = current_datetime()

        self.logged_at = now
        self.expires_at = now + self.timedelta_renewal
        db.session.commit()

    def set_logout(self):
        """
        Desfaz o login, em outras palavras, redefine todas as datas de login
        para nenhuma.
        """
        self.logged_at = None
        self.expires_at = None
        db.session.commit()

    def renewal(self):
        """
        Faz a renovação da data de expiração do login.
        """
        # Obtendo data e hora atual.
        now = current_datetime()

        expires_at = now + self.timedelta_renewal
        max_expires_at = self.logged_at + self.timedelta_expiration

        # (23:00 - (23:00 - 20:00 = 03:00)) = 20:00
        # (05:00 - (max(05:00 - 20:00, 00:00) = 00:00)) = 05:00
        self.expires_at = (
            expires_at - max(expires_at - max_expires_at, timedelta())
        )
        db.session.commit()

    @classmethod
    def find_by_login(cls, login: str):
        return db.session.execute(
            sa.select(cls).filter_by(login=login).limit(1)
        ).scalar()
