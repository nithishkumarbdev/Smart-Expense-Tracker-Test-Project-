"""Business logic for expense management.

This layer knows nothing about HTTP or JSON files. It depends only on
``JsonStorage``'s public interface (list_all/add/delete) and the
Pydantic models. That separation is what makes it possible to unit-test
business rules -- e.g. "totals are rounded to 2 decimals" or "category
filtering is case-insensitive" -- without spinning up a FastAPI app.
"""

from src.models.expense import Expense, ExpenseCreate
from src.storage.json_storage import JsonStorage
from src.utils.exceptions import ExpenseNotFoundError


class ExpenseService:
    """Encapsulates all operations on expenses."""

    def __init__(self, storage: JsonStorage) -> None:
        self._storage = storage

    def create_expense(self, payload: ExpenseCreate) -> Expense:
        """Persist a new expense and return it with its assigned id."""
        record = self._storage.add(payload.model_dump(mode="json"))
        return Expense(**record)

    def list_expenses(self, category: str | None = None) -> list[Expense]:
        """Return all expenses, optionally filtered by category.

        The filter is case-insensitive: a client filtering by "food"
        should match a stored category of "Food". Requiring exact case
        matches is a common beginner mistake that makes an API feel
        brittle to actual users.
        """
        expenses = [Expense(**record) for record in self._storage.list_all()]
        if category is not None:
            expenses = [e for e in expenses if e.category.lower() == category.lower()]
        return expenses

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense by id, raising ExpenseNotFoundError if it doesn't exist."""
        deleted = self._storage.delete(expense_id)
        if not deleted:
            raise ExpenseNotFoundError(expense_id)

    def calculate_total(self, category: str | None = None) -> float:
        """Sum expense amounts, optionally scoped to a single category.

        Rounded to 2 decimal places since these are currency amounts and
        floating-point summation can otherwise produce values like
        99.99999999999999.
        """
        matching = self.list_expenses(category=category)
        return round(sum(expense.amount for expense in matching), 2)
