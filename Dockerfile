FROM node:14.17.6 AS builder

COPY frontend /
WORKDIR /
RUN npm install . && npm run build:ee

FROM mirrors.tencent.com/blueking/python:3.11.13-ts3
USER root

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf
RUN dnf install -y gcc gcc-c++ openssl-devel mysql-devel

RUN pip install --upgrade pip setuptools

WORKDIR /app
COPY saas/requirements.txt /app
RUN pip install -r requirements.txt

COPY saas/backend /app/backend
COPY saas/bin /app/bin
COPY saas/config /app/config
COPY saas/resources /app/resources
COPY saas/manage.py /app
COPY saas/settings.py /app
COPY saas/urls.py /app
COPY saas/wsgi.py /app
COPY --from=builder /dist/static /app/staticfiles
COPY --from=builder /dist/index.html /app/resources/templates/
COPY --from=builder /dist/login_success.html /app/resources/templates/

CMD ["bash", "/app/bin/start.sh"]
