run:
	python3 manage.py runserver 0.0.0.0:8000

run_noreload:
	python3 manage.py runserver 0.0.0.0:8000 --noreload

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

test:
	python3 manage.py test

shell:
	python3 manage.py shell

cshell:
	python3 manage.py shell < shellTest.py

fake:
	python3 manage.py migrate --fake backend

flush:
	python3 manage.py flush --no-input

purge: flush
	rm db.sqlite3 || true
	rm -r packages || true
	rm -r media || true
	make migrate

admin:
	python3 manage.py createsuperuser

dep:
	pip3 install -r requirements.txt 

startdocker:
	sudo dockerd

rmdocker:
	rm -rf  ~/.docker

rmdockerconfig:
	rm ~/.docker/config.json

docker_image:
	docker build -t deaddrop/backend:1.0 .

docker_run-%:
	docker run -p 8000:8000 $*

docker_compose_up:
	docker-compose up -d --build

docker_compose_down:
	docker-compose down

docker_compose_down_all:
	docker-compose down --rmi all --volumes

docker_compose_stop:
	docker-compose stop

all:
	make migrate run