"""Domain-level exceptions.

These are raised by the storage and service layers and translated into
HTTP responses by handlers registered in ``main.py``. Keeping them
separate from ``fastapi.HTTPException`` means the service layer has no
dependency on FastAPI at all -- it could be reused behind a CLI or a
different web framework without modification.
"""


class ExpenseTrackerError(Exception):
    """Base class for all domain-level errors in this application."""


class ExpenseNotFoundError(ExpenseTrackerError):
    """Raised when an operation references an expense id that doesn't exist."""

    def __init__(self, expense_id: int) -> None:
        self.expense_id = expense_id
        super().__init__(f"Expense with id {expense_id} was not found")


class StorageError(ExpenseTrackerError):
    """Raised when the underlying JSON storage file is unreadable or corrupted."""
