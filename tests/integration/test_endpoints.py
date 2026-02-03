"""Integration tests for task endpoints."""

import time

import pytest

from app.models.task import TaskStatus
from tests.conftest import seed_task


# ─── POST /api/tasks ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestCreateEndpoint:
    """Tests for POST /api/tasks endpoint."""

    async def test_create_task_returns_201(self, client):
        """Test creating a task returns 201 with correct data."""
        payload = {
            "title": "New Task",
            "description": "Task description",
            "priority": 4,
        }
        resp = await client.post("/api/tasks", json=payload)
        assert resp.status_code == 201

        body = resp.json()
        assert body["title"] == "New Task"
        assert body["description"] == "Task description"
        assert body["status"] == "pending"
        assert body["priority"] == 4
        assert "id" in body
        assert "created_at" in body

    async def test_create_task_with_minimal_data(self, client):
        """Test creating a task with only required fields."""
        payload = {"title": "Minimal Task"}
        resp = await client.post("/api/tasks", json=payload)
        assert resp.status_code == 201
        assert resp.json()["title"] == "Minimal Task"
        assert resp.json()["status"] == "pending"

    async def test_create_task_invalid_data_returns_422(self, client):
        """Test that invalid data returns 422."""
        # Missing required title
        payload = {"description": "No title"}
        resp = await client.post("/api/tasks", json=payload)
        assert resp.status_code == 422


# ─── GET /api/tasks ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestListEndpoint:
    """Tests for GET /api/tasks endpoint."""

    async def test_list_tasks_empty(self, client):
        """Test listing tasks when database is empty."""
        resp = await client.get("/api/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["tasks"] == []

    async def test_list_tasks_with_data(self, client, db_session):
        """Test listing tasks with existing data."""
        await seed_task(db_session, title="Task 1")
        await seed_task(db_session, title="Task 2")

        resp = await client.get("/api/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert len(body["tasks"]) == 2

    async def test_list_tasks_with_pagination(self, client, db_session):
        """Test pagination parameters."""
        for i in range(5):
            await seed_task(db_session, title=f"Task {i}")

        resp = await client.get("/api/tasks?skip=2&limit=2")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert len(body["tasks"]) == 2
        assert body["skip"] == 2
        assert body["limit"] == 2

    async def test_list_tasks_filter_by_status(self, client, db_session):
        """Test filtering tasks by status."""
        await seed_task(db_session, title="Pending Task", status=TaskStatus.PENDING)
        await seed_task(db_session, title="Completed Task", status=TaskStatus.COMPLETED)

        resp = await client.get("/api/tasks?status=pending")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["tasks"][0]["status"] == "pending"


# ─── GET /api/tasks/{id} ──────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestGetEndpoint:
    """Tests for GET /api/tasks/{id} endpoint."""

    async def test_get_existing_task(self, client, db_session):
        """Test getting an existing task."""
        task = await seed_task(db_session, title="Test Task")

        resp = await client.get(f"/api/tasks/{task.id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == task.id
        assert body["title"] == "Test Task"

    async def test_get_nonexistent_task_returns_404(self, client):
        """Test getting a non-existent task returns 404."""
        resp = await client.get("/api/tasks/99999")
        assert resp.status_code == 404


# ─── PUT /api/tasks/{id} ─────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestUpdateEndpoint:
    """Tests for PUT /api/tasks/{id} endpoint."""

    async def test_update_task(self, client, db_session):
        """Test updating a task."""
        task = await seed_task(db_session, title="Original Title")

        payload = {
            "title": "Updated Title",
            "status": "in_progress",
            "priority": 5,
        }
        resp = await client.put(f"/api/tasks/{task.id}", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "Updated Title"
        assert body["status"] == "in_progress"
        assert body["priority"] == 5

    async def test_update_nonexistent_task_returns_404(self, client):
        """Test updating a non-existent task returns 404."""
        payload = {"title": "Updated Title"}
        resp = await client.put("/api/tasks/99999", json=payload)
        assert resp.status_code == 404


# ─── DELETE /api/tasks/{id} ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestDeleteEndpoint:
    """Tests for DELETE /api/tasks/{id} endpoint."""

    async def test_delete_task(self, client, db_session):
        """Test deleting a task."""
        task = await seed_task(db_session, title="Task to Delete")

        resp = await client.delete(f"/api/tasks/{task.id}")
        assert resp.status_code == 204

        # Verify task is deleted
        resp = await client.get(f"/api/tasks/{task.id}")
        assert resp.status_code == 404

    async def test_delete_nonexistent_task_returns_404(self, client):
        """Test deleting a non-existent task returns 404."""
        resp = await client.delete("/api/tasks/99999")
        assert resp.status_code == 404


# ─── POST /api/tasks/process-batch ───────────────────────────────────────────


@pytest.mark.asyncio
class TestBatchProcessEndpoint:
    """Tests for POST /api/tasks/process-batch endpoint."""

    async def test_batch_process_tasks_concurrent(self, client, db_session):
        """Test that batch processing runs concurrently (not sequentially)."""
        # Create 3 tasks
        task1 = await seed_task(db_session, title="Task 1", status=TaskStatus.PENDING)
        task2 = await seed_task(db_session, title="Task 2", status=TaskStatus.PENDING)
        task3 = await seed_task(db_session, title="Task 3", status=TaskStatus.PENDING)

        payload = {
            "task_ids": [task1.id, task2.id, task3.id]
        }

        # Measure execution time
        start_time = time.time()
        resp = await client.post("/api/tasks/process-batch", json=payload)
        elapsed_time = time.time() - start_time

        assert resp.status_code == 200
        body = resp.json()
        assert body["processed_count"] == 3
        assert body["total_requested"] == 3

        # If sequential, it would take ~6 seconds (2 seconds per task)
        # If concurrent, it should take ~2 seconds (all tasks processed in parallel)
        # Allow some margin for overhead
        assert elapsed_time < 4.0, "Batch processing should be concurrent, not sequential"

        # Verify all tasks are now completed
        for task_id in [task1.id, task2.id, task3.id]:
            task_resp = await client.get(f"/api/tasks/{task_id}")
            assert task_resp.json()["status"] == "completed"

    async def test_batch_process_with_invalid_ids(self, client, db_session):
        """Test batch processing with some invalid task IDs."""
        task = await seed_task(db_session, title="Valid Task", status=TaskStatus.PENDING)

        payload = {
            "task_ids": [task.id, 99999, 99998]  # One valid, two invalid
        }

        resp = await client.post("/api/tasks/process-batch", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        # Only one task should be processed successfully
        assert body["processed_count"] == 1
        assert body["total_requested"] == 3

    async def test_batch_process_empty_list_returns_422(self, client):
        """Test that empty task_ids list returns 422."""
        payload = {"task_ids": []}
        resp = await client.post("/api/tasks/process-batch", json=payload)
        assert resp.status_code == 422
