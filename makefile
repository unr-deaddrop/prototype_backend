run:
	python3 manage.py runserver

migrate:
	python3 manage.py migrate

shell:
	python3 manage.py shell

all:
	make migrate run