"""Pytest configuration and shared fixtures."""

import os
import tempfile
import atexit

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# ─── Test Database Setup (SQLite file for concurrent access) ────────────────
# Using file instead of :memory: to allow concurrent sessions in batch processing

# Create temporary database file
test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
test_db_file.close()
TEST_DB_URL = f"sqlite+aiosqlite:///{test_db_file.name}"

# Clean up temp file on exit
def cleanup_test_db():
    try:
        os.remove(test_db_file.name)
    except:
        pass

atexit.register(cleanup_test_db)

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionFactory = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Override async_session_factory BEFORE importing app modules
# This ensures batch processing uses test database
from app.core import database
database.async_session_factory = TestSessionFactory

from app.core.database import Base, get_db
from app.main import app
from app.models.task import Task, TaskStatus


# ─── Override get_db dependency ──────────────────────────────────────────────

async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test and drop them after."""
    # Drop all tables first to ensure clean state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up after test - delete all data
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Also clear the file content by recreating tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    """HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True
    ) as c:
        yield c


@pytest_asyncio.fixture
async def db_session():
    """Database session for direct database operations in tests."""
    async with TestSessionFactory() as session:
        yield session


async def seed_task(
    db: AsyncSession,
    *,
    title: str = "Test Task",
    description: str | None = None,
    status: str = TaskStatus.PENDING,
    priority: int = 3,
) -> Task:
    """Helper function to create a test task in the database."""
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
