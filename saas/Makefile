i18n_all: i18n_po i18n_mo

# make messages of python file and django template file to django.po
i18n_po:
	python manage.py makemessages -d django -l en -e html,part -e py
	python manage.py makemessages -d django -l zh_Hans -e html,part -e py

# compile django.po and djangojs.po to django.mo and djangojs.mo
i18n_mo:
	python manage.py compilemessages

# 虽然使用了poetry，但是由于蓝鲸Smart应用还是依赖requirements，所以需要导出
export_requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export --only=main,dev -f requirements.txt --output requirements_dev.txt --without-hashes

init:
	pip install -U pip setuptools
	pip install poetry
	poetry install
	pip install pre-commit
	pre-commit install

lint:
	pflake8 --config=./pyproject.toml .
	bandit -c ./pyproject.toml -r .
	mypy --config-file=./pyproject.toml .
	lint-imports --config .importlinter

fmt:
	isort --settings-path=./pyproject.toml .
	black --config=./pyproject.toml .

test:
	pytest -c ./pyproject.toml .

cov:
	pytest --cov-report html --cov=backend -c ./pyproject.toml .

serve:
	python manage.py runserver 8000
