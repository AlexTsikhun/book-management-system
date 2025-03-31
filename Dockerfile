FROM python:3.10.12-slim-bullseye
LABEL maintainer="oleksandr.tsikhun@gmail.com"

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
