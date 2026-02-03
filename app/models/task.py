"""Task model for the task management system."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text

from app.core.database import Base


class TaskStatus(str):
    """Allowed values for task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Enum for SQLAlchemy
task_status_enum = Enum(
    "pending",
    "in_progress",
    "completed",
    name="task_status",
)


class Task(Base):
    """Task model representing a task in the system."""

    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    title = Column(
        String(200),
        nullable=False,
        index=True,
    )
    description = Column(
        Text,
        nullable=True,
    )
    status = Column(
        task_status_enum,
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
    )
    priority = Column(
        Integer,
        nullable=False,
        default=3,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
