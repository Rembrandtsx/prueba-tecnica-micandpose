"""Repository layer for task data access."""

from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskRepository:
    """Repository for task data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ─── Read ──────────────────────────────────────────────────────────

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        result = await self._db.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        status_filter: Optional[str] = None,
    ) -> tuple[list[Task], int]:
        """
        Get all tasks with pagination and optional status filtering.
        
        Returns:
            Tuple of (list of tasks, total count)
        """
        query = select(Task)
        count_query = select(func.count()).select_from(Task)

        if status_filter:
            query = query.where(Task.status == status_filter)
            count_query = count_query.where(Task.status == status_filter)

        # Get total count
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        tasks = list(result.scalars().all())

        return tasks, total

    # ─── Create ────────────────────────────────────────────────────────

    async def create(self, task: Task) -> Task:
        """Create a new task."""
        self._db.add(task)
        await self._db.flush()
        await self._db.refresh(task)
        return task

    # ─── Update ────────────────────────────────────────────────────────

    async def update(self, task: Task) -> Task:
        """Update an existing task."""
        await self._db.flush()
        await self._db.refresh(task)
        return task

    async def update_status(self, task_id: int, status: str) -> bool:
        """
        Update task status by ID.
        
        Returns:
            True if task was updated, False if task not found
        """
        result = await self._db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=status)
        )
        await self._db.flush()
        return result.rowcount > 0

    # ─── Delete ────────────────────────────────────────────────────────

    async def delete(self, task: Task) -> None:
        """Delete a task."""
        await self._db.delete(task)
        await self._db.flush()
