import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401
from app.controller.applications import router as applications_router
from app.controller.db_status import router as db_status_router
from app.controller.openrouter import router as openrouter_router
from app.db import Base, engine, test_database_connection

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if test_database_connection() and engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            logging.exception("Database table initialization failed during startup")
    else:
        logging.warning("Database connection unavailable during startup")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(applications_router)
app.include_router(db_status_router)
app.include_router(openrouter_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"message": "App is running"}
