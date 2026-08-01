# AI Notes

## Project Overview

This project is a **Smart Expense Tracker API** built for the Software Engineering Apprenticeship assignment using **FastAPI**. The API allows users to **add, view, filter, calculate totals for, and delete expenses** while storing data in a local JSON file.

The objective was to build a lightweight REST API that follows the assignment requirements while keeping the project well structured, easy to understand, and straightforward to test.

---

## How AI Was Used

AI was used throughout the development process as a coding assistant.

I used it to **discuss different implementation approaches** before starting, understand parts of **FastAPI** and **Pydantic** that I was unfamiliar with, clarify validation behaviour, and troubleshoot issues that came up during development.

AI also helped **generate parts of the initial implementation**, suggested improvements to the project structure, **reviewed sections of the code**, suggested additional test cases, helped identify edge cases, and assisted with improving the project documentation.

Rather than using every suggestion directly, I **reviewed the generated code, modified it where needed, tested the behaviour**, and only kept changes that matched the assignment requirements and the overall structure I wanted for the project.

Throughout development, AI was mainly used as a tool to **speed up implementation, help explain concepts, review work, and improve the overall quality** of the submission.

---

## What Was Verified

Before submitting the project, I reviewed both the implementation and the documentation to make sure everything matched the assignment requirements.

The following areas were verified:

- **Creating** a new expense
- **Retrieving** all expenses
- **Filtering** expenses by category
- **Calculating** total expenses
- **Calculating** totals by category
- **Deleting** expenses
- **Request validation**
- **Error handling**
- **Project structure**
- **Test execution**

I also verified that the commands provided in the **README** worked correctly by running the installation, server startup, and test commands in **GitHub Codespaces**.

After making changes during development, I re-tested the affected functionality to ensure that existing behaviour continued to work correctly and that no regressions had been introduced.

---

## Bugs Found and Fixed

During testing, an edge case was discovered when sending a **non-finite numeric value (`Infinity`)** as the expense amount.

The request initially passed validation because `Infinity` is considered greater than zero, allowing the request to continue. However, when the data was written to the JSON file, the value was **stored incorrectly**.

After adding validation to reject non-finite numeric values, another issue appeared where the **validation error itself failed** because the invalid value could not be represented correctly in a JSON response.

To resolve this, the validation logic was updated to **reject non-finite values before they reached storage**, and the error handling was adjusted so invalid values were returned safely in the response. A **regression test** was also added to ensure the same issue would not occur again in future changes.

---

## My Review

Before submitting the assignment, I personally reviewed the repository to make sure everything was complete and matched the assignment requirements.

During my final review I:

- Verified that each **required API endpoint** behaved as expected
- Confirmed that **request validation** and **error responses** worked correctly
- Ran the **installation, server startup, and test commands** in GitHub Codespaces to confirm the README instructions were accurate
- Reviewed the **project structure** for consistency
- Checked the **documentation** for clarity and corrected small wording issues where necessary
- Confirmed that **all required files** were included in the repository before submission

I also made a few small manual changes after reviewing the project to keep the implementation and documentation consistent.

---

## AI Suggestions Not Used

During development there were opportunities to extend the project beyond the assignment requirements, such as **replacing the local JSON file with a database**, introducing additional infrastructure, or adding extra functionality.

I decided **not to expand** the project in those directions because the assignment specifically requested a **lightweight implementation using local storage**. Instead, I kept the focus on completing the required functionality, improving reliability through testing, and keeping the project simple and maintainable.
