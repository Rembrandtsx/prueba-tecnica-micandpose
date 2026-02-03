"""Service layer for task business logic."""

import asyncio
import logging
from typing import Optional

from app.core.database import async_session_factory
from app.models.task import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


# ─── Exceptions ──────────────────────────────────────────────────────────────


class TaskNotFoundException(Exception):
    """Raised when a task is not found by ID."""
    pass


# ─── Service ────────────────────────────────────────────────────────────────


class TaskService:
    """Service containing business logic for tasks."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

    # ─── Create ──────────────────────────────────────────────────────

    async def create_task(self, data: TaskCreate) -> Task:
        """Create a new task with default status 'pending'."""
        task = Task(
            title=data.title,
            description=data.description,
            status=TaskStatus.PENDING,
            priority=data.priority,
        )
        return await self._repo.create(task)

    # ─── Read ────────────────────────────────────────────────────────

    async def get_task(self, task_id: int) -> Task:
        """Get a task by ID, raising exception if not found."""
        task = await self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(f"Task with id '{task_id}' not found.")
        return task

    async def list_tasks(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[list[Task], int]:
        """List tasks with pagination and optional status filtering."""
        return await self._repo.get_all(
            skip=skip,
            limit=limit,
            status_filter=status,
        )

    # ─── Update ──────────────────────────────────────────────────────

    async def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        """Update an existing task."""
        task = await self.get_task(task_id)

        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status.value
        if data.priority is not None:
            task.priority = data.priority

        return await self._repo.update(task)

    # ─── Delete ────────────────────────────────────────────────────────

    async def delete_task(self, task_id: int) -> None:
        """Delete a task."""
        task = await self.get_task(task_id)
        await self._repo.delete(task)

    # ─── Batch Processing ────────────────────────────────────────────────

    async def process_task_batch(self, task_ids: list[int]) -> int:
        """
        Process multiple tasks concurrently.
        
        For each task:
        - Simulates 2 seconds of processing with asyncio.sleep(2)
        - Updates status to 'completed'
        - Handles errors gracefully
        
        Each task uses its own database session to avoid concurrent operation errors.
        
        Returns:
            Number of successfully processed tasks
        """
        async def process_single_task(task_id: int) -> bool:
            """Process a single task, returning True if successful."""
            # Create a new database session for this task
            async with async_session_factory() as session:
                try:
                    # Simulate processing time
                    await asyncio.sleep(2)
                    
                    # Create a new repository with the new session
                    repo = TaskRepository(session)
                    
                    # Update task status to completed
                    updated = await repo.update_status(
                        task_id,
                        TaskStatus.COMPLETED
                    )
                    
                    # Commit the transaction
                    await session.commit()
                    
                    if updated:
                        logger.info(f"Task {task_id} processed successfully")
                        return True
                    else:
                        logger.warning(f"Task {task_id} not found")
                        return False
                except Exception as e:
                    # Rollback on error
                    await session.rollback()
                    logger.error(f"Error processing task {task_id}: {e}")
                    return False

        # Process all tasks concurrently using asyncio.gather
        results = await asyncio.gather(
            *[process_single_task(task_id) for task_id in task_ids],
            return_exceptions=True
        )

        # Count successful processing (True values, excluding exceptions)
        processed_count = sum(
            1 for result in results
            if result is True
        )

        return processed_count
