FROM python:3.10.7 as base
MAINTAINER togglecorp dev@togglecorp.com

WORKDIR /code

COPY . /code/

RUN apt update -y \
    && pip install --upgrade --no-cache-dir pip poetry \
    && poetry --version \
    # Configure to use system instead of virtualenvs
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    # Clean-up
    && pip uninstall -y poetry virtualenv-clone virtualenv \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

