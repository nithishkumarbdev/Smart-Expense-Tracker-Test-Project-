"""HTTP layer: route handlers for the Expenses resource.

Route handlers are intentionally thin. Each one does three things: accept
a validated request, delegate to ``ExpenseService``, and return a response
model. No business logic (filtering, totals, id generation) belongs here --
that lives in ``services/expense_service.py`` so it can be tested and
reasoned about independently of HTTP.

Dependency injection
---------------------
FastAPI's ``Depends()`` lets a route declare "I need an ExpenseService"
without knowing how one is constructed. ``get_expense_service`` builds it
from ``get_storage``, and FastAPI resolves the chain automatically per
request. The payoff shows up in tests: ``app.dependency_overrides`` can
swap ``get_storage`` for a version pointing at a temp file, and every
route picks up the substitution with zero changes to route code.
"""

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, Query, status

from src.models.expense import Expense, ExpenseCreate, TotalResponse
from src.services.expense_service import ExpenseService
from src.storage.json_storage import JsonStorage

DEFAULT_STORAGE_PATH = Path(__file__).resolve().parent.parent.parent / "expenses.json"


@lru_cache
def get_storage() -> JsonStorage:
    """Return a process-wide JsonStorage singleton.

    ``lru_cache`` with no arguments memoizes a single call, giving every
    request the same JsonStorage instance (and therefore the same lock)
    without manually managing global state. Tests override this function
    entirely via ``app.dependency_overrides``, so the cache is never a
    problem across test cases.
    """
    return JsonStorage(DEFAULT_STORAGE_PATH)


def get_expense_service(storage: JsonStorage = Depends(get_storage)) -> ExpenseService:
    """Build an ExpenseService backed by the injected storage."""
    return ExpenseService(storage)


router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post(
    "",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new expense",
    description="Creates an expense record and returns it with a server-assigned id.",
    responses={
        422: {
            "description": (
                "Validation failed (e.g. blank title, non-positive amount, invalid date)."
            )
        },
    },
)
def create_expense(
    payload: ExpenseCreate,
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.create_expense(payload)


@router.get(
    "",
    response_model=list[Expense],
    summary="List expenses",
    description="Returns all expenses, optionally filtered by category (case-insensitive).",
)
def list_expenses(
    category: str | None = Query(
        default=None,
        description="Filter results to a single category, e.g. 'Food'.",
    ),
    service: ExpenseService = Depends(get_expense_service),
) -> list[Expense]:
    return service.list_expenses(category=category)


@router.get(
    "/total",
    response_model=TotalResponse,
    summary="Get total expenses",
    description="Returns the sum of all expense amounts, optionally scoped to one category.",
)
def get_total(
    category: str | None = Query(
        default=None,
        description="Restrict the total to a single category, e.g. 'Food'.",
    ),
    service: ExpenseService = Depends(get_expense_service),
) -> TotalResponse:
    total = service.calculate_total(category=category)
    return TotalResponse(total=total, category=category)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    description="Deletes the expense with the given id.",
    responses={
        404: {"description": "No expense exists with the given id."},
    },
)
def delete_expense(
    expense_id: int,
    service: ExpenseService = Depends(get_expense_service),
) -> None:
    service.delete_expense(expense_id)
