"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.routers import tasks

# ─── Logging Configuration ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# ─── Lifespan Context Manager ─────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


# ─── FastAPI Application ──────────────────────────────────────────────────────

app = FastAPI(
    title="Task Management API",
    description="REST API for managing tasks with MySQL and FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(tasks.router)
