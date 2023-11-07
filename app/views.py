from flask import (
    Flask,
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session
)

from app.models import Operator
from app.session import (
    is_logged_session,
    get_operator_by_session,
    login_required
)
from app.utils import datetime_to_brt

blueprint = Blueprint('views', __name__)


@blueprint.get('/admin')
def admin():
    """
    Rota de login de operador.
    """
    # Obtendo o operador pela sessão atual.
    operator = get_operator_by_session()

    is_logged_session_ = is_logged_session(operator)

    # Caso não haja um operador na sessão ou o operador não está mais logado.
    if not is_logged_session_ \
            or (is_logged_session_ and request.headers.get('Referer')):
        if operator:
            operator.set_logout()
            session.clear()

        # Exibe página de login.
        return render_template('admin.html.j2')

    # Redireciona para a página restrita.
    return redirect(url_for('views.index'))


@blueprint.get('/')
@login_required(rest=False, only_admin=False)
def index(operator: Operator):
    """
    Rota da página restrita onde consulta e gerencia as placas.
    """
    expiration_datetime = (
        datetime_to_brt(operator.expires_at)
        .strftime('%H:%M:%S %d/%m/%Y')
    )

    return render_template(
        'index.html.j2',
        operator=operator,
        expiration_datetime=expiration_datetime,
        is_admin=operator.login == 'admin'
    )


def init_app(app: Flask):
    app.register_blueprint(blueprint)
