"""Unit tests for TaskService business logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskNotFoundException, TaskService


# ─── Helper: Create mock task ────────────────────────────────────────────────

def make_task(
    *,
    task_id: int = 1,
    title: str = "Test Task",
    status: str = TaskStatus.PENDING,
    priority: int = 3,
) -> Task:
    """Create a mock Task object for testing."""
    task = MagicMock(spec=Task)
    task.id = task_id
    task.title = title
    task.description = None
    task.status = status
    task.priority = priority
    return task


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repo) -> TaskService:
    """Create a TaskService instance with mocked repository."""
    return TaskService(repository=mock_repo)


# ─── Tests: Create ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestCreateTask:
    """Tests for creating tasks."""

    async def test_create_task_with_default_status(self, service, mock_repo):
        """Test that created tasks have status 'pending' by default."""
        mock_repo.create.return_value = make_task(status=TaskStatus.PENDING)

        data = TaskCreate(
            title="New Task",
            description="Description",
            priority=4,
        )
        result = await service.create_task(data)

        mock_repo.create.assert_awaited_once()
        created_task = mock_repo.create.call_args[0][0]
        assert created_task.status == TaskStatus.PENDING
        assert created_task.title == "New Task"
        assert created_task.priority == 4


# ─── Tests: Get ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestGetTask:
    """Tests for getting tasks."""

    async def test_get_existing_task(self, service, mock_repo):
        """Test getting an existing task."""
        task = make_task(task_id=1)
        mock_repo.get_by_id.return_value = task

        result = await service.get_task(1)
        assert result == task
        mock_repo.get_by_id.assert_awaited_once_with(1)

    async def test_get_nonexistent_task_raises_exception(self, service, mock_repo):
        """Test that getting a non-existent task raises exception."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundException):
            await service.get_task(999)


# ─── Tests: Update ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestUpdateTask:
    """Tests for updating tasks."""

    async def test_update_task_fields(self, service, mock_repo):
        """Test updating task fields."""
        task = make_task(task_id=1, title="Old Title")
        mock_repo.get_by_id.return_value = task
        mock_repo.update.return_value = task

        data = TaskUpdate(
            title="New Title",
            priority=5,
        )
        result = await service.update_task(1, data)

        assert task.title == "New Title"
        assert task.priority == 5
        mock_repo.update.assert_awaited_once()

    async def test_update_nonexistent_task_raises_exception(self, service, mock_repo):
        """Test that updating a non-existent task raises exception."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundException):
            await service.update_task(999, TaskUpdate(title="New Title"))


# ─── Tests: Delete ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestDeleteTask:
    """Tests for deleting tasks."""

    async def test_delete_existing_task(self, service, mock_repo):
        """Test deleting an existing task."""
        task = make_task(task_id=1)
        mock_repo.get_by_id.return_value = task

        await service.delete_task(1)

        mock_repo.delete.assert_awaited_once_with(task)

    async def test_delete_nonexistent_task_raises_exception(self, service, mock_repo):
        """Test that deleting a non-existent task raises exception."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundException):
            await service.delete_task(999)
