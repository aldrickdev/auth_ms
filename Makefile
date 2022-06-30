:PHONY run
run:
	docker-compose -f compose/compose.yaml up

:PHONY run_build
run_build:
	docker-compose -f compose/compose.yaml up --build

:PHONY test
test:
	docker-compose -f compose/compose.test.yaml up 

:PHONY test_build
test_build:
	docker-compose -f compose/compose.test.yaml up --build

:PHONY req
req:
	poetry export -o requirements/requirements.txt
	poetry export --dev -o requirements/requirements.dev.txt
