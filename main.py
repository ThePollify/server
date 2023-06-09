import logging
import os

import uvicorn
from fastapi import FastAPI

# isort: off

import settings
import models
import database
import endpoints

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(endpoints.router)


@app.on_event("startup")
async def init() -> None:
    logging.info("Creating tables in database")
    async with database.engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.create_all)


uvicorn.run(
    app,
    host="0.0.0.0",
    port=settings.settings.port,
    root_path=settings.settings.root_path,
)
