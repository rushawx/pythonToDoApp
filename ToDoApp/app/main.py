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
