from os import environ
from pathlib import Path

from dotenv import dotenv_values
from flask import Flask
from sqlalchemy.engine import URL


def init_app(app: Flask):
    """
    Função que irá carregar a configuração para o app.
    """
    config = environ.copy()

    for envfile in Path('environment').glob('*'):
        config.update(dotenv_values(str(envfile)))

    # Caso o app esteja em ambiente de desenvolvimento.
    if app.debug:
        # Utiliza o banco de testes.
        dbname = 'tests'
    # Caso contrário, esteja produção.
    else:
        # Utiliza o banco de produção informado na variavel de ambiente.
        dbname = config['POSTGRES_DB']

    # Caso haja uma variável de ambiente chamada 'HOSTNAME'
    # (critério usado pra saber se a aplicação está em um container docker)
    if 'HOSTNAME' in environ:
        # Define o hostname do banco com o nome do serviço do banco de dados. 
        dbhost = 'database'
    # Caso contrário, esteja rodando localmente.
    else:
        # Utiliza o hostname localhost (não funcionaria dentro de um container docker).
        dbhost = 'localhost'

    # Setting the database URI.
    config['SQLALCHEMY_DATABASE_URI'] = URL.create(
        drivername='postgresql',
        username=config['POSTGRES_USER'],
        password=config['POSTGRES_PASSWORD'],
        host=dbhost,
        port=5432,
        database=dbname
    )

    # Loading app config.
    app.config.from_mapping(config)
