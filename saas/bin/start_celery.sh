#!/bin/bash
celery -A config worker -l INFO
