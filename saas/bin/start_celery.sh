#!/bin/bash
celery -A config worker -l INFO --max-memory-per-child=500000
