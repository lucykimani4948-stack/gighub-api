<<<<<<< HEAD
﻿# SendIt - Document Management & Enrichment API

**Student:** Lucy Wambui Kimani  
**Reg. No:** C027-01-0890/2024  
**Course:** Lab 9: File Uploads & External APIs

## Project Overview
Document management API for SendIt courier company with weather enrichment.

## Features
- User Authentication with JWT
- Role-Based Access Control (Admin, Manager, Staff)
- File Upload with Validation
- Weather Enrichment via Open-Meteo API
- Document Status Tracking
- Search with Filters
- Document Versioning
- Webhook Notifications

## How to Run
1. Create virtual environment: python -m venv venv
2. Activate: .\venv\Scripts\activate
3. Install: pip install -r requirements.txt
4. Start Docker: docker compose up -d
5. Seed database: python seeds.py
6. Run: uvicorn main:app --reload --port 8000
7. Open: http://localhost:8000/docs

## Test Credentials
- Admin: admin / Admin123
- Manager: manager / Manager123
- Staff: staff1 / Staff123

## Screenshots
All endpoint screenshots are in the /screenshots folder.
=======
<<<<<<< HEAD
\# ClinicGuard Patient Management API
=======
\# HealthTrack API - Patient Records System
>>>>>>> 446d107ad0e725a81e4c79e7859dfcb451f18654



\## Student Information

<<<<<<< HEAD
\- \*\*Name\*\*: LUCY WAMBUI KIMANI

\- \*\*Registration\*\*: C027-01-0890/2024

\- \*\*Course\*\*: Programming Assignment

\- \*\*Date\*\*: August 5, 2026
=======
\- \*\*Name:\*\* Lucy Wambui Kimani

\- \*\*Registration:\*\* C027-01-0890/2024

\- \*\*Course:\*\* User Authentication - JWT \& Password Hashing



\---
>>>>>>> 446d107ad0e725a81e4c79e7859dfcb451f18654



\## Project Overview

<<<<<<< HEAD
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
=======


HealthTrack is a secure platform for patients to access their medical records and for doctors to manage patient data. The system implements industry-standard security practices including JWT authentication, password hashing, role-based access control, and two-factor authentication.



\### Features Implemented



\- User Registration \& Login

\- JWT Authentication

\- Password Hashing (bcrypt)

\- Role-Based Access Control (Patient, Doctor, Admin)

\- Password Reset Functionality

\- Token Blacklisting (Logout)

\- Two-Factor Authentication (2FA)

\- Patient Management



\---



\## Technologies Used



\- \*\*Framework:\*\* FastAPI

\- \*\*Database:\*\* SQLite (SQLModel)

\- \*\*Authentication:\*\* JWT (python-jose)

\- \*\*Password Hashing:\*\* bcrypt (passlib)

\- \*\*2FA:\*\* pyotp

\- \*\*Language:\*\* Python 3.13



\---



\## API Endpoints



\### Authentication

| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/register` | Register new user |

| POST | `/login` | Login \& get JWT token |

| POST | `/logout` | Logout \& invalidate token |

| POST | `/forgot-password` | Request password reset |

| POST | `/reset-password` | Reset password with token |

| POST | `/login-2fa` | Login with 2FA verification |



\### User Management

| Method | Endpoint | Description | Access |

|--------|----------|-------------|--------|

| GET | `/users/me` | Get user profile | Authenticated |

| PUT | `/users/me` | Update user profile | Authenticated |

| GET | `/users` | List all users | Admin only |

| POST | `/users/enable-2fa` | Enable 2FA | Authenticated |

| POST | `/users/verify-2fa` | Verify 2FA | Authenticated |

| POST | `/users/disable-2fa` | Disable 2FA | Authenticated |



\### Patient Management

| Method | Endpoint | Description | Access |

|--------|----------|-------------|--------|

| POST | `/patients` | Create patient record | Doctor/Admin |

| GET | `/patients` | List patients | Doctor/Admin |

| GET | `/patients/{id}` | Get patient by ID | Based on role |



\---
>>>>>>> 446d107ad0e725a81e4c79e7859dfcb451f18654



\## Setup Instructions



<<<<<<< HEAD
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
=======
\### 1. Clone Repository

```bash

git clone https://github.com/lucykimani4948-stack/gighub-api.git

cd gighub-api
>>>>>>> 446d107ad0e725a81e4c79e7859dfcb451f18654

>>>>>>> 383572f8d900134b027b956946a9f34aecffa115
