:PHONY run
run:
	docker-compose -f compose/compose.yaml --env-file .env up

:PHONY run_d
run_d:
	docker-compose -f compose/compose.yaml --env-file .env up --detach

:PHONY run_build
run_build:
	docker-compose -f compose/compose.yaml --env-file .env up --build

:PHONY down
down:
	docker-compose -f compose/compose.yaml --env-file .env down

:PHONY req
req:
	poetry export --without-hashes -o requirements/requirements.txt
	poetry export --without-hashes --dev -o requirements/requirements.dev.txt
