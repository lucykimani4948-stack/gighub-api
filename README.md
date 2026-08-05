\# ClinicGuard Patient Management API



\## Student Information

\- \*\*Name\*\*: LUCY WAMBUI KIMANI

\- \*\*Registration\*\*: C027-01-0890/2024

\- \*\*Course\*\*: Programming Assignment

\- \*\*Date\*\*: August 5, 2026



\## Project Overview

ClinicGuard is a secure patient management API built with FastAPI, PostgreSQL, and JWT authentication.



\## Features

\-Role-Based Access Control (Admin, Doctor, Receptionist)

\-  JWT Authentication with bcrypt hashing

\-  Full CRUD operations for patients

\-  Audit logging with middleware

\-  Patient assignment workflow (claim/unassign)

\-  Secure patient search with role-based filtering

\-  Rate limiting to prevent abuse



\## Technology Stack

\- FastAPI

\- PostgreSQL

\- SQLModel (SQLAlchemy)

\- JWT (python-jose)

\- bcrypt for password hashing

\- SlowAPI for rate limiting



\## Setup Instructions



\### Prerequisites

\- Python 3.8+

\- Docker Desktop

\- PostgreSQL



\### Installation

1\. Clone the repository

2\. Create virtual environment: `python -m venv venv`

3\. Activate: `.\\venv\\Scripts\\Activate` (Windows)

4\. Install dependencies: `pip install -r requirements.txt`

5\. Start Docker: `docker compose up -d`

6\. Seed database: `python src/seeds.py`

7\. Run server: `python -m uvicorn src.main:app --reload --port 8000`



\### Login Credentials

| Role | Username | Password |

|------|----------|----------|

| Admin | admin | admin123 |

| Doctor | dr\_james | doctor123 |

| Doctor | dr\_sarah | doctor123 |

| Receptionist | reception | reception123 |



\## API Documentation

After running, visit: http://localhost:8000/docs



\## Endpoints

\- `/register` - User registration

\- `/login` - User login

\- `/patients` - Patient CRUD operations

\- `/patients/search` - Secure patient search

\- `/patients/unassigned` - View unassigned patients

\- `/patients/{id}/claim` - Claim a patient

\- `/patients/{id}/unassign` - Unassign a patient

\- `/users` - User management (admin only)

\- `/audit-logs` - Audit logs (admin only)



\## Exercises Completed

1\. \*\*Exercise 1\*\*: Audit Log - Tracks all patient record accesses

2\. \*\*Exercise 2\*\*: Patient Assignment Workflow - Claim/unassign patients

3\. \*\*Exercise 3\*\*: Secure Patient Search - Role-based search filtering



\## Author

LUCY WAMBUI KIMANI (C027-01-0890/2024)

