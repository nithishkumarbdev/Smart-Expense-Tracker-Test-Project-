# Smart Expense Tracker API

A REST API for managing personal expenses built with FastAPI.

The API allows users to add expenses, view all expenses, filter expenses by category, calculate total expenses, and delete existing expenses. Expense data is stored in a local JSON file, keeping the project lightweight and easy to run without requiring a database.

---

## Features

- Add a new expense
- View all expenses
- Filter expenses by category
- Calculate total expenses
- Calculate total expenses by category
- Delete an expense
- Automatic request validation using Pydantic
- Consistent JSON error responses
- Local JSON file storage
- Interactive Swagger documentation at `/docs`

---

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- Uvicorn
- Pytest

---

## Architecture

The project follows a simple layered architecture to keep responsibilities separated.

```
Client
   │
   ▼
Routes (HTTP layer)
   │
   ▼
Expense Service (Business Logic)
   │
   ▼
JSON Storage (Persistence)
```

### Why use a service layer?

The route handlers are responsible only for handling HTTP requests and responses.

All business logic such as filtering expenses, calculating totals, and validating operations is kept inside the service layer. This keeps the routes clean, makes the application easier to maintain, and allows the business logic to be tested independently of the API layer.

The storage layer is responsible only for reading and writing data from the JSON file.

---

## Project Structure

```
smart-expense-tracker/
│
├── README.md
├── AI_NOTES.md
├── requirements.txt
├── expenses.json
│
├── src/
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── storage/
│   └── utils/
│
└── tests/
    ├── conftest.py
    ├── test_routes.py
    ├── test_service.py
    └── test_storage.py
```

---

## Requirements

- Python 3.12 or later
- pip

---

## Installation

Clone the repository.

```bash
git clone https://github.com/nithishkumarbdev/Smart-Expense-Tracker-Test-Project-.git
```

Move into the project directory.

```bash
cd smart-expense-tracker
```

Create a virtual environment.

```bash
python3 -m venv venv
```

Activate the virtual environment.

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Server

Start the API using:

```bash
python3 -m uvicorn src.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Running the Tests

Run the complete test suite.

```bash
python3 -m pytest tests/ -v
```

---

# API Examples

The examples below are shown in sequence — run them in order on a fresh
`expenses.json` (`[]`) and the responses will match exactly.

## 1. Add Expense

### Request

```bash
curl -X POST http://127.0.0.1:8000/expenses \
-H "Content-Type: application/json" \
-d '{
"title":"Lunch",
"amount":24.50,
"category":"Food",
"date":"2026-08-01"
}'
```

### Response — `201 Created`

```json
{
  "title": "Lunch",
  "amount": 24.5,
  "category": "Food",
  "date": "2026-08-01",
  "id": 1
}
```

---

## 2. View All Expenses

### Request

```bash
curl http://127.0.0.1:8000/expenses
```

### Response — `200 OK`

```json
[
  {
    "title": "Lunch",
    "amount": 24.5,
    "category": "Food",
    "date": "2026-08-01",
    "id": 1
  }
]
```

---

## 3. Filter Expenses by Category

### Request

```bash
curl "http://127.0.0.1:8000/expenses?category=Food"
```

### Response — `200 OK`

```json
[
  {
    "title": "Lunch",
    "amount": 24.5,
    "category": "Food",
    "date": "2026-08-01",
    "id": 1
  }
]
```

---

## 4. Get Total Expenses

### Request

```bash
curl http://127.0.0.1:8000/expenses/total
```

### Response — `200 OK`

`category` is always present in the response — `null` when no category filter is applied.

```json
{
  "total": 24.5,
  "category": null
}
```

---

## 5. Get Total Expenses by Category

### Request

```bash
curl "http://127.0.0.1:8000/expenses/total?category=Food"
```

### Response — `200 OK`

```json
{
  "total": 24.5,
  "category": "Food"
}
```

---

## 6. Delete an Expense

### Request

```bash
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

### Response

`204 No Content` — empty body.

If the expense does not exist:

```bash
curl -X DELETE http://127.0.0.1:8000/expenses/999
```

```json
{
  "detail": "Expense with id 999 was not found"
}
```

---

## Error Handling

The API returns standard HTTP status codes.

| Status Code | Description |
|-------------|-------------|
| 200 | Request completed successfully |
| 201 | Expense created successfully |
| 204 | Expense deleted successfully |
| 404 | Expense not found |
| 422 | Invalid request or validation error |

Validation errors are returned as JSON responses with descriptive error messages, for example:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "amount"],
      "msg": "Value error, must be a finite number",
      "input": "Infinity"
    }
  ]
}
```

---

## Future Improvements

Possible improvements include:

- Replace JSON storage with a database
- Add update (`PUT`/`PATCH`) endpoints
- Add pagination for large datasets
- Add date range filtering
- Add authentication and user accounts
- Add Docker support for deployment

---

## License

This project was created as part of a Software Engineering Apprenticeship take-home assignment.
