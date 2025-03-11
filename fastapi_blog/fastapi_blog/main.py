from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_blog.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}