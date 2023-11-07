from functools import wraps

from flask import Flask, session, redirect, url_for, render_template
from flask_session import Session
from werkzeug.exceptions import Forbidden

from app.models import Operator


def create_login_session(operator: Operator):
    """
    Armazena os dados do operador na sessão.
    """
    session['login'] = operator.login
    session['password'] = operator.password
    session['logged_at'] = operator.logged_at


def is_empty_session():
    #  Obtendo dados que estão na sessão.
    login = session.get('login')
    password = session.get('password')

    # Caso não haja nenhum login e senha na sessão.
    return not login or not password


def is_logged_session(operator: Operator):
    """
    Retorna True se estiver tudo certo, caso contrário, False.

    CASOS:
    - Não haja login nenhum feito.
    - Login tenha sido expirado.
    - Senhas não batam.
    - Datas de login não batam.
    """
    password = session.get('password')
    logged_at = session.get('logged_at')

    return not (
        not operator
        or not operator.is_logged
        or operator.is_expired
        or operator.password != password
        or operator.logged_at != logged_at
    )


def you_are_not_logged(rest: bool = True, expired: bool = False):
    """
    Gera uma reposta para quem não é operador.
    """
    # Se não for uma API rest, apenas redireciona para o campo de login.
    if not rest:
        if expired:
            return render_template('expired.html.j2')
        else:
            return redirect(url_for('views.admin'))

    if expired:
        raise Forbidden(
            'Sua sessão expirou! Faça login novamente para ter acesso a '
            'este recurso.'
        )
    else:
        raise Forbidden('Faça login para ter acesso a este recurso.')


def get_operator_by_session():
    if is_empty_session():
        return

    return Operator.find_by_login(session.get('login'))


def login_required(rest: bool = True, only_admin=True):
    def inner(function: callable):
        @wraps(function)
        def _inner(*args, **kwargs):
            #  Obtendo dados que estão na sessão.
            login = session.get('login')

            # Caso não haja nenhum login e senha na sessão.
            if is_empty_session():
                # Redireciona ou diz que não é um operador.
                return you_are_not_logged(rest)

            # Obtendo o operador pelo login.
            operator = Operator.find_by_login(login)

            if not is_logged_session(operator):
                # Deletando a sessão existente.
                session.clear()

                # Redireciona ou diz que não é um operador.
                return you_are_not_logged(
                    rest, expired=operator and operator.is_expired
                )

            if only_admin and operator.login.lower() != 'admin':
                raise Forbidden(
                    'Você não possui permissão especial para acessar '
                    'este recurso.'
                )

            # Renovando a expiração de quem está logado.
            operator.renewal()

            return function(*args, **kwargs, operator=operator)
        return _inner
    return inner


def init_app(app: Flask):
    Session(app)
