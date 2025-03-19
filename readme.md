# Приложение ToDo

Это простое приложение для управления задачами, созданное с использованием FastAPI и SQLAlchemy.

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/ваш-репозиторий/ToDoApp.git
    ```

2. Перейдите в директорию проекта:
    ```sh
    cd ToDoApp
    ```

3. Создайте и активируйте виртуальное окружение:
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

4. Установите зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Запуск приложения

1. Создайте файл `.env` на основе `.env.example` и укажите необходимые переменные окружения.

2. Запустите приложение:
    ```sh
    uvicorn app.main:app --host 0.0.0.0 --port 80
    ```

## Использование Docker

1. Постройте и запустите контейнеры с помощью Docker Compose:
    ```sh
    docker-compose up --build
    ```

## Конечные точки API

- `GET /` - Главная страница
- `POST /items/` - Создать новую задачу
- `GET /items/` - Получить список всех задач
- `GET /items/{item_id}` - Получить задачу по ID
- `PUT /items/{item_id}` - Обновить задачу по ID
- `DELETE /items/{item_id}` - Удалить задачу по ID
