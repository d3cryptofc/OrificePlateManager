from flask import request, session
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from werkzeug.security import check_password_hash

from app.models import Operator
from app.session import create_login_session


def validate_login_pattern(login: str,
                           minlength: int = 5,
                           maxlength: int = 30):
    # Caso o login esteja vazio.
    if not login.strip():
        raise BadRequest('O campo de login não deve estar vazio!')

    # Caso o login tenha um tamanho inválido.
    if not (minlength - 1 < len(login) < maxlength + 1):
        raise BadRequest(
            'O campo de login deve ter no mínimo {} '
            'caracteres e no máximo {}.'
            .format(minlength, maxlength)
        )


def validate_password_pattern(password: str,
                              minlength: int = 8,
                              maxlength: int = 30):
    # Caso a senha esteja vazia.
    if not password:
        raise BadRequest('O campo de senha não deve estar vazio!')

    # Caso a senha tenha um tamanho inválido.
    if not (minlength - 1 < len(password) < maxlength + 1):
        raise BadRequest(
            'O campo de senha deve ter no mínimo {} '
            'caracteres e no máximo {}.'
            .format(minlength, maxlength)
        )


class Admin(Resource):
    def post(self):
        data = request.json

        # Obtendo o login enviado pelo usuário.
        login = data.get('login', '')
        # Realizando validação de padrão do login.
        validate_login_pattern(login)

        # Obtendo a senha enviada pelo usuário.
        password = data.get('password', '')
        # Realizando validação de padrão da senha.
        validate_password_pattern(password)

        # Obtendo operador no banco de dados através do login.
        operator = Operator.find_by_login(login)

        # Caso o login não exista ou a senha hash não bata com a
        # senha recebida.
        if not operator or not check_password_hash(operator.password,
                                                   password):
            raise NotFound('Login ou senha incorretos!')

        print(operator.login, operator.logged_at, operator.expires_at)

        # Caso o login esteja expirado.
        if operator.is_expired:
            # Remove as datas de login, desloga.
            operator.set_logout()

        # Caso operador não esteja logado, define datas de expiração.
        if not operator.is_logged:
            # Definindo no banco de dados que há alguem logado.
            operator.set_logged()

            # Abrindo sessão com os dados de login.
            create_login_session(operator)

            # Respondendo mensagem de sucesso.
            return dict(
                message='Login realizado com êxito!'
            )

        # Destruindo sessão que foi criada.
        session.clear()

        # Caso já haja alguém logado na conta.
        raise Forbidden(
            'Alguém já está logado! '
            'Aguarde a expiração ou desconexão do mesmo.'
        )


def init(api: Api):
    api.add_resource(Admin, '/auth')
