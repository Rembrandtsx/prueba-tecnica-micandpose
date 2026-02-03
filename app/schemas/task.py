"""Pydantic schemas for task requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ──────────────────────────────────────────────────────────────────


class TaskStatusEnum(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ─── Request Schemas ─────────────────────────────────────────────────────────


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Task priority from 1 (low) to 5 (high)",
    )

    model_config = {"extra": "ignore"}


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)

    model_config = {"extra": "ignore"}


class BatchProcessRequest(BaseModel):
    """Schema for batch processing request."""

    task_ids: list[int] = Field(..., min_length=1, description="List of task IDs to process")

    @field_validator("task_ids")
    @classmethod
    def validate_task_ids(cls, v: list[int]) -> list[int]:
        """Validate that task IDs are positive integers."""
        if not v:
            raise ValueError("task_ids cannot be empty")
        if any(task_id <= 0 for task_id in v):
            raise ValueError("All task IDs must be positive integers")
        return v


# ─── Response Schemas ────────────────────────────────────────────────────────


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatusEnum
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    total: int
    skip: int
    limit: int
    tasks: list[TaskResponse]


class BatchProcessResponse(BaseModel):
    """Schema for batch processing response."""

    processed_count: int = Field(..., description="Number of tasks successfully processed")
    total_requested: int = Field(..., description="Total number of tasks requested to process")
