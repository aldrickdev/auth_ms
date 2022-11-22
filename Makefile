src = app
version = 0.0.1
name = greymint-auth
container_name = app

# ========== Main commands ==========
# Runs a formatter, linter then static analyzer
:PHONY check
check: format lint 

# Update requirements files
:PHONY req-up
req-up:
	poetry export --without-hashes -o requirements.txt
	poetry export --without-hashes --dev -o requirements_test.txt

# Run the application on the host manchine
:PHONY run
run:
	python app/main.py

# Builds an image for the application
:PHONY b
b:
	poetry export --without-hashes -o requirements.txt
	docker build -f docker/app.Dockerfile -t $(name):$(version) .

# Runs the application
:PHONY com-up
com-up: 
	docker compose -f docker/compose.yaml --env-file .env up

# Builds an image then runs the application 
:PHONY b-com-up
b-com-up: b com-up

# Runs the application in detached mode
:PHONY com-up-d
com-up-d:
	docker compose -f docker/compose.yaml --env-file .env up --detach

# Builds an image then runs the application 
:PHONY b-com-up-d
b-com-up-d: b com-up-d

# Brings the application down
:PHONY com-down
com-down:
	docker compose -f docker/compose.yaml --env-file .env down
	docker volume prune -f

# Build a image for testing the application
:PHONY tb
tb:
	poetry export --without-hashes --dev -o requirements_test.txt
	docker build -f docker/test_app.Dockerfile -t $(name):$(version)-test .

# Runs the tests in a container
:PHONY test
test: 
	docker compose -f docker/test_compose.yaml --env-file .env up --detach
	docker exec -it ${container_name} pytest -vv
	docker compose -f docker/test_compose.yaml --env-file .env down
	docker volume prune -f


# Builds the images for testing then runs the tests
:PHONY tb-test
tb-test: tb test

# Helpers
:PHONY format
format:
	black $(src)

:PHONY lint
lint:
	flake8 $(src)

:PHONY stana
stana:
	mypy $(src)
