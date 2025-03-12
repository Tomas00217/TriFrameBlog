from fastapi import FastAPI
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.blogs.routes import blogs_router

app = FastAPI(title="TriFrameBlog")

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(blogs_router, prefix="", tags=["blogs"])

@app.get("/")
async def root():
    return {"message": "Hello World"}