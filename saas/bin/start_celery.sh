#!/bin/bash
python manage.py celery worker -l info
