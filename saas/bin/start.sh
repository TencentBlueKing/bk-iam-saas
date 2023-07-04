#!/bin/bash
gunicorn wsgi -w 10 -k gevent -b [::]:5000 --max-requests 1024 --max-requests-jitter 50 --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"' --env prometheus_multiproc_dir=/tmp/
