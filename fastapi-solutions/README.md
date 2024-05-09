### ASYNC API

____________________________________________________________________________
Как запустить проект и проверить его работу:
____________________________________________________________________________
Запуск приложения с docker compose:
```
docker-compose up --build
or
docker-compose up --build -d
```

Запуск приложения для локальной разработки
```
1. docker run -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" krissmelikova/awesome_repository:v1

2. docker run -p 6379:6379 redis:7.2.4-alpine
 
3.uvicorn src.main:app --host 0.0.0.0 --port 8000
```