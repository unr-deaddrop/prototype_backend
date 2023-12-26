run:
	python3 manage.py runserver

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

dep:
	pip3 install -r requirements.txt 

all:
	make migrate run