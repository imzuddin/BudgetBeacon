from fastapi import FastAPI

import os
import asyncio

from router import authentication, budget, transactions, reporting

api_path_prefix = os.environ.get("API_PATH_PREFIX", "/api/v1")

app = FastAPI()

origins = []

app.include_router(authentication.router, prefix=api_path_prefix)
app.include_router(budget.router, prefix=api_path_prefix)
app.include_router(transactions.router, prefix=api_path_prefix)
app.include_router(reporting.router, prefix=api_path_prefix)


@app.get("/")
async def root():
    return {"message": "Hello World"}
