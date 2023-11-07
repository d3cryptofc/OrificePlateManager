import json

from flask import Flask

from app import config, views, resources, models, session


def create_app():
    """
    Função que cria o app e inicializa todas as extensões.
    """
    app = Flask(__name__)

    # Configurando JSON do Flask-Restful.
    json.JSONEncoder.default = str
    app.config['RESTFUL_JSON'] = dict(
        cls=json.JSONEncoder,
        ensure_ascii=False
    )

    # Definindo uma chave secreta para a aplicação.
    app.secret_key = bytes.fromhex(
        'ba6dcb5cc7aa7c7bc427930965e203152ad6bfd2580c31dbc9'
        'dfd5cf66a8807262318472932d92dbd93685f22c7045eed2dc'
        '1e9e52c0d185da6879079f8c726c178c209baa704a4071965d'
        '3329008f6fee0d2e57d3a0cdd2201797ac5ca844dce02461b0'
    )

    # Iterando extensões e inicializando-as.
    for extension in (config, models, session, resources, views):
        extension.init_app(app)

    return app
