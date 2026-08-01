"""Pydantic models describing the Expense resource.

Two shapes are defined deliberately:

- ``ExpenseCreate``: what a client sends on creation. Has no ``id``,
  because the client never gets to choose one.
- ``Expense``: what the API returns. Extends ``ExpenseCreate`` with the
  server-assigned ``id``.

Keeping these separate (rather than one model with an optional ``id``)
means invalid states -- like a client-supplied id -- are unrepresentable
at the type level, not just rejected by convention.
"""

import math
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    """Payload for creating a new expense.

    Validation rules enforced here run before any business logic sees
    the data, so the service layer can trust that a valid ``ExpenseCreate``
    is, by construction, well-formed.
    """

    title: str = Field(
        ...,
        min_length=1,
        description="Short label for the expense.",
        examples=["Lunch with client"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Expense amount. Must be strictly positive.",
        examples=[24.50],
    )
    category: str = Field(
        ...,
        min_length=1,
        description="Category the expense belongs to, e.g. 'Food', 'Travel'.",
        examples=["Food"],
    )
    date: date_type = Field(
        ...,
        description="Date the expense was incurred, in ISO 8601 format (YYYY-MM-DD).",
        examples=["2026-07-15"],
    )

    @field_validator("amount")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        """Reject Infinity/-Infinity/NaN.

        ``gt=0`` alone lets ``Infinity`` through, since ``inf > 0`` is
        True in Python. JSON has no way to represent a non-finite float,
        so without this check the value survives request validation but
        is silently rewritten to ``null`` during JSON serialization --
        the API would report success (201) while quietly storing broken
        data. Caught via manual edge-case testing, not by the initial
        test suite.
        """
        if not math.isfinite(value):
            raise ValueError("must be a finite number")
        return value

    @field_validator("title", "category")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Reject strings that are empty once whitespace is stripped.

        ``min_length=1`` alone still allows a title of ``"   "`` through,
        since that string has length 3. This validator closes that gap
        and normalizes the stored value by stripping surrounding
        whitespace.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace-only")
        return stripped


class Expense(ExpenseCreate):
    """A persisted expense, as returned by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Lunch with client",
                "amount": 24.50,
                "category": "Food",
                "date": "2026-07-15",
            }
        }
    )

    id: int = Field(..., description="Server-assigned unique identifier.")


class TotalResponse(BaseModel):
    """Response payload for total-expense queries."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"total": 152.30, "category": "Food"}
        }
    )

    total: float = Field(..., description="Sum of matching expense amounts, rounded to 2 decimals.")
    category: str | None = Field(
        default=None,
        description="Category the total was filtered by, or null for the overall total.",
    )
