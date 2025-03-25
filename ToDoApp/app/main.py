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
