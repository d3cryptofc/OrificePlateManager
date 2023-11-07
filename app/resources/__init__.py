from flask import Flask, Blueprint
from flask_restful import Api

from app.resources import admin, orifice_plate

blueprint = Blueprint('resources', __name__, url_prefix='/rest')


def init_app(app: Flask):
    api = Api(blueprint, catch_all_404s=True)
    admin.init(api)
    orifice_plate.init(api)
    app.register_blueprint(blueprint)
