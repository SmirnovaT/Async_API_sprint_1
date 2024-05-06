FROM python:3.12-slim

WORKDIR /opt/app

COPY . .

RUN apt update
RUN pip install poetry
RUN poetry install

RUN groupadd -r web && useradd -d /opt/app-r -g web web \
     && chown web:web -R /opt/app
USER web

CMD ["python", "./src/main.py"]