from collections import defaultdict
from flask import request
from flask_pydantic import validate
from flask_restful import Api, Resource
import sqlalchemy as sa
from werkzeug.exceptions import NotFound, Conflict

from app.database import db
from app.models import OrificePlate, Operator, PlateReplacement
from app.schemes.orifice_plate import (
    OrificePlatePostSchema,
    OrificePlatePutSchema,
    OrificePlatePatchSchema,
    OrificePlateDeleteSchema
)
from app.session import login_required
from app.utils import current_datetime


class Plate(Resource):
    @login_required(only_admin=False)
    def get(sel, operator):
        # Obtendo parâmetros de consulta da requisição GET.
        args = request.args

        # Caso o parâmetro `onlylocations` seja positivo.
        if args.get('onlylocations', '').lower() in ('1', 'yes', 'true'):
            # Retornando todos os locais de placas já cadastrados no
            # banco de dados.
            return list(
                db.session.execute(
                    sa.select(OrificePlate.local)
                    .select_from(OrificePlate)
                    .distinct()
                ).scalars()
            )

        # Obtendo número de série fornecido pelo usuário.
        serial_number = args.get('serial_number')

        # Obtendo número de certificado fornecido pelo usuário.
        certificate_number = args.get('certificate_number')

        # Obtendo todos os locais fornecidos pelo usuário.
        locations = args.getlist('location')

        # Obtendo todos os tipos de placas fornecidos pelo usuário.
        types = args.getlist('type')

        # Obtendo todas as situações de placas fornecidas pelo usuário.
        statuses = args.getlist('status')

        # Iniciando instrução de consulta para a tabela de placas de orifício.
        stmt = sa.select(OrificePlate).order_by(OrificePlate.created_at)

        # Caso o número de série tenha sido preenchido.
        if serial_number:
            # Filtra pelo número de série fornecido.
            stmt = stmt.filter_by(serial_number=serial_number)

        # Caso o número de certificado tenha sido preenchido.
        if certificate_number:
            # Filtra pelo número de certificado fornecido.
            stmt = stmt.filter_by(certificate_number=certificate_number)

        # Caso o alguma localização tenha sido selecionada.
        if locations:
            # Filtra pelas localizações fornecidas.
            stmt = stmt.where(OrificePlate.local.in_(locations))

        # Caso o algum tipo de placa tenha sido selecionado.
        if types:
            # Filtra pelos tipos de placas fornecidos.
            stmt = stmt.where(OrificePlate.type.in_(types))

        # Caso o alguma situação de placa tenha sido selecionada.
        if statuses:
            # Filtra pelas situações de placas fornecidas.
            stmt = stmt.where(OrificePlate.status_text.in_(statuses))

        # Realizando a consulta e obtendo as linhas.
        rows = db.session.execute(stmt).scalars()

        # Criando um default dict onde o valor padrão é uma lista vazia.
        results = defaultdict(list)

        # Iterando as linhas da consulta realizada.
        for row in rows:
            # Agrupando a linha no default dict pelo número de série.
            results[row.serial_number].append(row.to_dict())

        # Retornando os grupos de placas.
        return list(results.values())

    @login_required()
    @validate()
    def post(self, body: OrificePlatePostSchema, operator):
        """
        Recurso de adição de placas de orifício.
        """
        # HACK: O decorador `flask_pydantic.validate` espera que os tipos
        # nas anotações de tipos sejam modelos pydantic, portanto não posso
        # colocar anotações de tipos que não sejam modelos pydantic, e,
        # como alternativa, a anotação dentro da função terá o mesmo efeito.
        operator: Operator

        # Obtendo possível placa existente com o mesmo número de série.
        already_exists = db.session.execute(
            sa.select(OrificePlate)
            .filter_by(serial_number=body.serial_number)
        ).scalar()

        # Caso uma placa com o mesmo número de série já exista.
        if already_exists:
            raise Conflict(
                'Já existe uma placa registrada com este número de série, '
                'faça uma substituição de placa ao invés disso.'
            )

        # Criando umma placa de orifício com os dados recebidos na requisição.
        plate = OrificePlate(**(
            body.dict() | dict(created_by_operator=operator.login)
        ))

        # Adicionando a placa na tabela.
        db.session.add(plate)

        # Confirmando a adição.
        db.session.commit()

        # Retornando mensagem de sucesso.
        return dict(
            message='Nova placa adicionada com êxito!',
            plate=plate.to_dict()
        )

    @login_required()
    @validate()
    def put(self, body: OrificePlatePutSchema, operator):
        """
        Recurso de substituição de placas de orifício.
        """
        # HACK: O decorador `flask_pydantic.validate` espera que os tipos
        # nas anotações de tipos sejam modelos pydantic, portanto não posso
        # colocar anotações de tipos que não sejam modelos pydantic, e,
        # como alternativa, a anotação dentro da função terá o mesmo efeito.
        operator: Operator

        # Obtendo a última placa associada ao número de série fornecido.
        last_plate: OrificePlate = db.session.execute(
            sa.select(OrificePlate)
            .filter_by(serial_number=body.serial_number)
            .order_by(OrificePlate.id.desc())
        ).scalar()

        # Caso não haja placa nenhuma com o número de série fornecido.
        if not last_plate:
            raise NotFound(
                'A solicitação de substituição falhou, não há nenhuma placa '
                'para o número de série fornecido.'
            )

        # Atualizando a situação das placas para removidas.
        db.session.execute(
            sa.update(OrificePlate)
            .values(
                status_text='REMOVIDA',
                status_date=current_datetime(),
                status_local=None
            )
            .where(
                (OrificePlate.serial_number == body.serial_number)
                & (OrificePlate.status_text != 'REMOVIDA')
            )
        )

        # Criando uma nova placa de substituição.
        plate = OrificePlate(**(
            last_plate.to_dict()
            | dict(
                id=None,
                certificate_number=body.certificate_number,
                certificate_url=body.certificate_url,
                internal_diameter_reference=body.internal_diameter_reference,
                status_text='INSTALADA/OPERANDO',
                status_date=current_datetime(),
                created_at=None,
                created_by_operator=operator.login
            )
        ))

        # Adicionando a nova placa de substituição.
        db.session.add(plate)

        # Registrando a substituição na tabela de histórico.
        db.session.add(PlateReplacement(
            before_certificate_number=last_plate.certificate_number,
            after_certificate_number=body.certificate_number,
            reason=body.reason
        ))

        # Confirmando as alterações.
        db.session.commit()

        # Retornando mensagem de sucesso.
        return dict(
            message='A placa foi substituída com êxito!',
            plate=plate.to_dict()
        )

    @login_required()
    @validate()
    def patch(self, body: OrificePlatePatchSchema, operator):
        """
        Recurso de edição de placas de orifício.
        """
        # HACK: O decorador `flask_pydantic.validate` espera que os tipos
        # nas anotações de tipos sejam modelos pydantic, portanto não posso
        # colocar anotações de tipos que não sejam modelos pydantic, e,
        # como alternativa, a anotação dentro da função terá o mesmo efeito.
        operator: Operator

        # Fazendo a edição da placa e obtendo quantidade de linhas afetadas.
        rowcount = db.session.execute(
            sa.update(OrificePlate)
            .values(**body.dict())
            .filter_by(id=body.id)
        ).rowcount

        # Caso nenhuma linha tenha sido afetada pela instrução de atualização.
        if not rowcount:
            raise NotFound(
                'A solicitação de edição falhou, não há nenhuma placa para o '
                'ID fornecido.'
            )

        # Confirmando as alterações.
        db.session.commit()

        # Mensagem de sucesso.
        return dict(message='A placa foi editada com êxito!')

    @login_required()
    @validate()
    def delete(self, body: OrificePlateDeleteSchema, operator):
        """
        Recurso de remoção de placas de orifício.
        """
        # Fazendo remoção da placa pelo ID e obtendo quantidade de
        # linhas afetadas.
        rowcount = db.session.execute(
            sa.delete(OrificePlate).filter_by(id=body.plate_id)
        ).rowcount

        # Caso nenhuma linha tenha sido afetada pela instrução de remoção.
        if not rowcount:
            raise NotFound(
                'A solicitação de remoção falhou, não há nenhuma placa a '
                'identificação fornecida.'
            )

        # Confirmando a remoção.
        db.session.commit()

        # Retornando mensagem de sucesso.
        return dict(
            message='A placa foi removida com êxito!'
        )


def init(api: Api):
    api.add_resource(Plate, '/plate')
