FROM node:14.17.6 AS builder

COPY ./ /app
WORKDIR /app

RUN bash build.sh

FROM python:3.11.10-slim-bullseye

RUN rm /etc/apt/sources.list && \
    echo "deb https://mirrors.cloud.tencent.com/debian bullseye main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.cloud.tencent.com/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.cloud.tencent.com/debian bullseye main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.cloud.tencent.com/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://bkrepo.cwoa.net/pypi/aiops/kingeye-pypi/simple' > ~/.pip/pip.conf

RUN apt-get update && apt-get install -y gcc libssl-dev default-libmysqlclient-dev build-essential



ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --upgrade pip

COPY --from=builder /app/src /app
WORKDIR /app
RUN pip install -r requirements.txt -i https://bkrepo.cwoa.net/pypi/aiops/kingeye-pypi/simple

CMD ["bash", "/app/bin/start.sh"]
