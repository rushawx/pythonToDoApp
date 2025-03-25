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
