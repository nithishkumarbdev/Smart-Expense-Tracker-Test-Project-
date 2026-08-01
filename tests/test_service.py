"""Tests for ExpenseService: business rules independent of HTTP."""

from datetime import date

import pytest

from src.models.expense import ExpenseCreate
from src.services.expense_service import ExpenseService
from src.utils.exceptions import ExpenseNotFoundError


def make_expense(
    title: str = "Coffee",
    amount: float = 4.5,
    category: str = "Food",
    expense_date: date = date(2026, 1, 15),
) -> ExpenseCreate:
    return ExpenseCreate(title=title, amount=amount, category=category, date=expense_date)


def test_create_expense_assigns_id(service: ExpenseService) -> None:
    created = service.create_expense(make_expense())
    assert created.id == 1
    assert created.title == "Coffee"


def test_list_expenses_returns_all_by_default(service: ExpenseService) -> None:
    service.create_expense(make_expense(title="Coffee"))
    service.create_expense(make_expense(title="Bus ticket", category="Travel"))
    result = service.list_expenses()
    assert len(result) == 2


def test_list_expenses_filters_by_category(service: ExpenseService) -> None:
    service.create_expense(make_expense(category="Food"))
    service.create_expense(make_expense(category="Travel"))
    result = service.list_expenses(category="Food")
    assert len(result) == 1
    assert result[0].category == "Food"


def test_category_filter_is_case_insensitive(service: ExpenseService) -> None:
    service.create_expense(make_expense(category="Food"))
    result = service.list_expenses(category="food")
    assert len(result) == 1


def test_delete_expense_removes_it(service: ExpenseService) -> None:
    created = service.create_expense(make_expense())
    service.delete_expense(created.id)
    assert service.list_expenses() == []


def test_delete_nonexistent_expense_raises(service: ExpenseService) -> None:
    with pytest.raises(ExpenseNotFoundError):
        service.delete_expense(999)


def test_calculate_total_overall(service: ExpenseService) -> None:
    service.create_expense(make_expense(amount=10.0, category="Food"))
    service.create_expense(make_expense(amount=5.5, category="Travel"))
    assert service.calculate_total() == 15.5


def test_calculate_total_by_category(service: ExpenseService) -> None:
    service.create_expense(make_expense(amount=10.0, category="Food"))
    service.create_expense(make_expense(amount=5.5, category="Travel"))
    assert service.calculate_total(category="Food") == 10.0


def test_calculate_total_with_no_expenses_is_zero(service: ExpenseService) -> None:
    assert service.calculate_total() == 0.0


def test_calculate_total_rounds_to_two_decimals(service: ExpenseService) -> None:
    service.create_expense(make_expense(amount=0.1))
    service.create_expense(make_expense(amount=0.2))
    # 0.1 + 0.2 == 0.30000000000000004 in raw floating point.
    assert service.calculate_total() == 0.3
