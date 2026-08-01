"""Shared pytest fixtures.

The central idea: every test gets a JSON storage file inside pytest's
``tmp_path`` (a fresh temp directory per test), never the project's real
``expenses.json``. That keeps tests hermetic and repeatable -- running
the suite never mutates data you might actually be tracking, and tests
can't leak state into each other via a shared file.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.routes import get_storage
from src.main import create_app
from src.services.expense_service import ExpenseService
from src.storage.json_storage import JsonStorage


@pytest.fixture
def storage_path(tmp_path: Path) -> Path:
    """A path to a JSON storage file inside a fresh temp directory."""
    return tmp_path / "expenses.json"


@pytest.fixture
def storage(storage_path: Path) -> JsonStorage:
    """A JsonStorage instance for direct storage-layer tests."""
    return JsonStorage(storage_path)


@pytest.fixture
def service(storage: JsonStorage) -> ExpenseService:
    """An ExpenseService backed by the isolated storage fixture."""
    return ExpenseService(storage)


@pytest.fixture
def client(storage_path: Path) -> TestClient:
    """A FastAPI TestClient with storage overridden to the temp file.

    ``app.dependency_overrides`` replaces ``get_storage`` for the
    lifetime of this app instance, so every route -- without any route
    code being aware of it -- reads and writes the temp file instead of
    the real ``expenses.json``.
    """
    app = create_app()
    app.dependency_overrides[get_storage] = lambda: JsonStorage(storage_path)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
