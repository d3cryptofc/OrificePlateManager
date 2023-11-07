from flask import Flask
import sqlalchemy as sa
from werkzeug.security import generate_password_hash

from app.database import db
from app.models.operator import Operator  # noqa
from app.models.orifice_plate import OrificePlate  # noqa
from app.models.replacement_history import PlateReplacement  # noqa


def init_app(app: Flask):
    db.init_app(app)

    with app.app_context():
        # Criando as tabelas a partir dos modelos.
        db.create_all()

        # Tentando procurar pelo operador admin.
        operator_admin = db.session.execute(
            sa.select(Operator).filter_by(login='admin')
        ).scalar()

        # Caso o operador não exista.
        if not operator_admin:
            db.session.add(Operator(
                login='admin',
                password=generate_password_hash(app.config['ADMIN_PASSWORD'])
            ))
            db.session.commit()
