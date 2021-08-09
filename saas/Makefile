i18n_all: i18n_po i18n_mo

# make messages of python file and django template file to django.po
i18n_po:
	python manage.py makemessages -d django -l en -e html,part -e py
	python manage.py makemessages -d django -l zh_Hans -e html,part -e py

# compile django.po and djangojs.po to django.mo and djangojs.mo
i18n_mo:
	python manage.py compilemessages
