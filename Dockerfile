FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt update \
    && apt install python3 python3-pip gunicorn git nginx supervisor -y

ADD . /app
COPY ./assets/proxy.conf /etc/nginx/nginx.conf
COPY ./assets/process.conf /etc/supervisor/conf.d/

WORKDIR /app

RUN mkdir -p /var/log/model_pipeline/ \
    && chmod -R +x assets/scripts/* \
    && ./assets/scripts/setup.sh \
    && pip install -r requirements.txt

CMD ["/app/assets/scripts/init.sh"]

