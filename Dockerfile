FROM python:3.8.5-alpine3.12
MAINTAINER Moath Zaghdad

ENV PYTHONUNBUFFERD 1


RUN apk --no-cache add gettext
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .temp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip3 install --no-cache-dir pipenv

COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN pipenv install --dev --system

RUN apk del .temp-build-deps


RUN mkdir -p /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
