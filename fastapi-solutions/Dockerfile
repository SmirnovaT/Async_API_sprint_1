FROM python:3.12-slim-bullseye

WORKDIR /opt/app


COPY poetry.lock pyproject.toml /opt/app/

RUN apt update
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install

COPY . .


RUN groupadd -r web && useradd -d /opt/app-r -g web web \
     && chown web:web -R /opt/app

USER web


CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]