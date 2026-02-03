"""Unit tests for Pydantic schemas validation."""

import pytest
from pydantic import ValidationError

from app.schemas.task import (
    BatchProcessRequest,
    TaskCreate,
    TaskStatusEnum,
    TaskUpdate,
)


class TestTaskCreate:
    """Tests for TaskCreate schema."""

    def test_valid_task_create(self):
        """Test creating a task with valid data."""
        data = TaskCreate(
            title="Test Task",
            description="Test description",
            priority=3,
        )
        assert data.title == "Test Task"
        assert data.description == "Test description"
        assert data.priority == 3

    def test_task_create_with_minimal_data(self):
        """Test creating a task with only required fields."""
        data = TaskCreate(title="Minimal Task")
        assert data.title == "Minimal Task"
        assert data.description is None
        assert data.priority == 3  # Default value

    def test_task_create_title_too_long(self):
        """Test that title exceeding 200 characters is rejected."""
        long_title = "a" * 201
        with pytest.raises(ValidationError):
            TaskCreate(title=long_title)

    def test_task_create_priority_out_of_range(self):
        """Test that priority outside 1-5 range is rejected."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", priority=0)
        
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", priority=6)


class TestTaskUpdate:
    """Tests for TaskUpdate schema."""

    def test_valid_task_update(self):
        """Test updating a task with valid data."""
        data = TaskUpdate(
            title="Updated Title",
            status=TaskStatusEnum.COMPLETED,
            priority=5,
        )
        assert data.title == "Updated Title"
        assert data.status == TaskStatusEnum.COMPLETED
        assert data.priority == 5

    def test_task_update_all_fields_optional(self):
        """Test that all fields in TaskUpdate are optional."""
        data = TaskUpdate()
        assert data.title is None
        assert data.description is None
        assert data.status is None
        assert data.priority is None


class TestBatchProcessRequest:
    """Tests for BatchProcessRequest schema."""

    def test_valid_batch_process_request(self):
        """Test valid batch process request."""
        data = BatchProcessRequest(task_ids=[1, 2, 3])
        assert data.task_ids == [1, 2, 3]

    def test_batch_process_request_empty_list(self):
        """Test that empty task_ids list is rejected."""
        with pytest.raises(ValidationError):
            BatchProcessRequest(task_ids=[])

    def test_batch_process_request_invalid_ids(self):
        """Test that negative or zero task IDs are rejected."""
        with pytest.raises(ValidationError):
            BatchProcessRequest(task_ids=[0, 1, 2])
        
        with pytest.raises(ValidationError):
            BatchProcessRequest(task_ids=[-1, 1])
