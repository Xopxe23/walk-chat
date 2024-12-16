# Микросервис Chat для WALK


## В приложении реализованы следующие функции для начала работы:

- Функция main[FastAPI] для запуска приложения.
- Подход Чистой Архитектуры в построении структуры приложения. Техника внедрения зависимости.
- Работа с БД Postgres. Генерация файлов миграций alembic.
- Запуск приложения через Docker

## Для запуска локально:

```
python3 -m venv .venv
```
```
pip install -r requirements.txt
```
```
python app/main.py
```

### Для запуска тестов:

```
pytest
```


## Для запуска docker контейнера:
В `.env` MODE=PROD!

```
docker-compose up --build
```

## Для запуска тестов внутри docker контейнера:

```
docker exec -it walk-profile-app pytest
```
