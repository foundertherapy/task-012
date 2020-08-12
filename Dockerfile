FROM python:3.8.5-alpine3.12
MAINTAINER Mo'ath Zaghdad

ENV PYTHONUNBUFFERD 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN apk --no-cache add gettext

RUN mkdir -p /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
