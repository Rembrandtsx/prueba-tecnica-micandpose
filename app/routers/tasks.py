"""Router for task endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    BatchProcessRequest,
    BatchProcessResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskNotFoundException, TaskService

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
logger = logging.getLogger(__name__)


# ─── Dependency: Service instance per request ────────────────────────────────


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """Dependency that provides a TaskService instance."""
    repo = TaskRepository(db)
    return TaskService(repo)


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task with status 'pending' by default.",
)
async def create_task(
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """Create a new task."""
    return await service.create_task(data)


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="List tasks",
    description="List tasks with pagination and optional status filtering.",
)
async def list_tasks(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    service: TaskService = Depends(get_task_service),
):
    """List tasks with pagination and optional status filtering."""
    tasks, total = await service.list_tasks(
        skip=skip,
        limit=limit,
        status=status,
    )
    return TaskListResponse(
        total=total,
        skip=skip,
        limit=limit,
        tasks=tasks,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieve a task by its ID.",
)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Get a task by ID."""
    try:
        return await service.get_task(task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update an existing task. All fields are optional.",
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Update an existing task."""
    try:
        return await service.update_task(task_id, data)
    except TaskNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by its ID.",
)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Delete a task."""
    try:
        await service.delete_task(task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/process-batch",
    response_model=BatchProcessResponse,
    summary="Process tasks in batch",
    description=(
        "Process multiple tasks concurrently. Each task will be processed "
        "asynchronously with a 2-second delay, and its status will be updated to 'completed'."
    ),
)
async def process_batch(
    request: BatchProcessRequest,
    service: TaskService = Depends(get_task_service),
):
    """Process multiple tasks concurrently."""
    processed_count = await service.process_task_batch(request.task_ids)
    return BatchProcessResponse(
        processed_count=processed_count,
        total_requested=len(request.task_ids),
    )
