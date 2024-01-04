run:
	python3 manage.py runserver 0.0.0.0:8000

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

shell:
	python3 manage.py shell

cshell:
	python3 manage.py shell < shellTest.py

fake:
	python3 manage.py migrate --fake backend

flush:
	python3 manage.py flush

purge:
	make flush
	rm db.sqlite3
	make migrate

admin:
	python3 manage.py createsuperuser

dep:
	pip3 install -r requirements.txt 

startdocker:
	sudo dockerd

docker_image:
	docker build -t deaddrop/backend:1.0 .

docker_run-%:
	docker run -p 8000:8000 $*

all:
	make migrate run