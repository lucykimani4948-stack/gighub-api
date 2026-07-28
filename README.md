\# HealthTrack API - Patient Records System



\## Student Information

\- \*\*Name:\*\* Lucy Wambui Kimani

\- \*\*Registration:\*\* C027-01-0890/2024

\- \*\*Course:\*\* User Authentication - JWT \& Password Hashing



\---



\## Project Overview



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



\## Setup Instructions



\### 1. Clone Repository

```bash

git clone https://github.com/lucykimani4948-stack/gighub-api.git

cd gighub-api

