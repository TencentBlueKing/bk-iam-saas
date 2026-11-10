FROM node:14.17.6 AS builder

COPY ./ /app
WORKDIR /app

RUN bash build.sh

FROM mirrors.tencent.com/blueking/python:3.6.8-ts4

RUN dnf makecache && dnf install -y gcc openssl-devel mariadb-devel make

RUN mkdir ~/.pip && printf '[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple/' > ~/.pip/pip.conf

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m pip install --upgrade pip

COPY --from=builder /app/src /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["bash", "/app/bin/start.sh"]
