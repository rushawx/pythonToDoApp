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

## Добавление аутентификации BASIC

```python
# ToDoApp/app/db/engine.py

import datetime
import os

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, String, UUID
from sqlalchemy.orm import sessionmaker


load_dotenv()

DB_URL = os.getenv("DB_URL")

engine = sa.create_engine(DB_URL)

session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = sa.orm.declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    todo = Column(DateTime)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
```

```python
# ToDoApp/app/auth/auth.py

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.engine import User
from app.utils.utils import get_db


security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user_from_db(credentials.username)
    if user is None or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return user


def get_user_from_db(username: str, db: Session = next(get_db())):
    return db.query(User).filter(User.username == username).first()
```

```python
# ToDoApp/app/utils/utils.py

import uuid
from app.db.engine import session, User
from sqlalchemy.orm import Session


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_superuser(db: Session = next(get_db())):
    superuser = User(id=uuid.uuid4(), username="admin", password="admin")
    db.add(superuser)
    db.commit()
    db.refresh(superuser)
    return superuser
```

```python
# ToDoApp/app/main.py

import uvicorn
from fastapi import FastAPI, Depends

from app.db.engine import Base, engine, User
from app.handlers.items import router as items_router
from app.auth.auth import authenticate_user
from app.utils.utils import init_superuser


app = FastAPI()

app.include_router(items_router)

Base.metadata.create_all(bind=engine)

init_superuser()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/about_user")
async def about_user(user: User = Depends(authenticate_user)):
    return {"message": f"This is a user: {user.username}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
```

## Добавление аутентификации JWT

```python
# ToDoApp/app/auth/auth.py

import jwt
import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from sqlalchemy.orm import Session

from app.db.engine import User
from app.utils.utils import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def get_user_from_db(username: str, db: Session = next(get_db())):
    return db.query(User).filter(User.username == username).first()
```

```python
# ToDoApp/app/models/users.py

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str

```

```python
# ToDoApp/app/main.py

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.db.engine import Base, engine
from app.models.users import User
from app.handlers.items import router as items_router
from app.auth.auth import create_jwt_token, decode_jwt_token, get_user_from_db
from app.utils.utils import init_superuser


app = FastAPI()

app.include_router(items_router)

Base.metadata.create_all(bind=engine)

init_superuser()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/token")
async def token(user: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user_from_db = get_user_from_db(user.username)
    if not user_from_db or user_from_db.password != user.password:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "access_token": create_jwt_token({"sub": user.username}),
        "token_type": "bearer",
    }


@app.get("/about_user")
async def about_user(user: User = Depends(decode_jwt_token)) -> dict:
    user_from_db = get_user_from_db(user["sub"])
    return {"message": f"This is a user: {user_from_db.username}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)

```