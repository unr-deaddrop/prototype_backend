run:
	python3 manage.py runserver

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

shell:
	python3 manage.py shell

cshell:
	python3 manage.py shell < shellTest.py

dep:
	pip3 install django django-rest-framework django-cors-headers 

all:
	make migrate run