FROM python:3.12-slim-bullseye

WORKDIR /opt/app

COPY . .

RUN apt update
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install

RUN groupadd -r web && useradd -d /opt/app-r -g web web \
     && chown web:web -R /opt/app
USER web

CMD ["python3.12", "./src/main.py"]