DEV_DB_CONTAINER_NAME = 'opm-dev-database'

routes: databaseup
	@echo -e "\n-> Exibindo as rotas da aplicação"
	FLASK_DEBUG=1 poetry run flask routes

run: databaseup
	@echo -n "-> Rodando aplicação em modo de desenvolvimento | "
	FLASK_DEBUG=1 poetry run flask run

databaseup:
	@echo "-> Criando container de banco de dados postgres com porta exposta (PARA DESENVOLVIMENTO)"
	docker run -d \
		--name $(DEV_DB_CONTAINER_NAME) \
		--publish 5432:5432 \
		--env-file ./environment/database.env \
		--volume ./docker/entrypoint/init.sql:/docker-entrypoint-initdb.d/init.sql:ro \
		--volume ./docker/postgresql-data:/var/lib/postgresql \
		postgres 3>/dev/null 2>&3 1>&3 || :
	@echo

	@echo "-> Aguardando o banco de dados ficar pronto."
	docker exec $(DEV_DB_CONTAINER_NAME) bash -c "until pg_isready > /dev/null; do :; done"
	@echo

databasedown:
	@echo "-> Garantindo que o container do banco de dados com porta exposta tenha sido excluido.."
	docker stop $(DEV_DB_CONTAINER_NAME) 3>/dev/null 2>&3 1>&3 && docker rm $(DEV_DB_CONTAINER_NAME) 3>/dev/null 2>&3 1>&3 || :
	@echo

deploy: down
	@echo "-> Fazendo implantação para produção, criação dos containers necessários."
	docker compose -f docker/docker-compose.yml up -d --build

down:
	@echo "-> Desfazendo possível implantação feita anteriormente."
	docker compose -f docker/docker-compose.yml down
	@echo

logs:
	@echo "-> Exibindo registros de logs dos containers em produção."
	docker compose -f docker/docker-compose.yml logs

prune: databasedown down
	docker system prune