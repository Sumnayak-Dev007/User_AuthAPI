## User Authentication API (Django + Docker)
Overview

This project implements a Django REST API for user management, including registration, login, and profile retrieval. It is fully Dockerized with PostgreSQL and includes JWT token authentication.

Features:

Custom user model extending Django’s AbstractUser with additional fields:

phone_number (validated for Indian numbers)

date_of_birth

last_login_ip

REST endpoints:

POST /api/register/ — User registration with JWT tokens

POST /api/login/ — User login and obtain JWT tokens

GET /api/profile/ — Retrieve authenticated user profile 

Dockerized environment for easy setup

Pytest unit tests included

Middleware to capture and store user IP address


## Prerequisites

Docker (>=20.10)

Docker Compose (>=2.0)

Optional: Postman or Insomnia for API testing

Docker handles Python, PostgreSQL, and dependencies automatically — no manual setup required.

## Installation & Running
1. Clone the repository
```
git clone https://github.com/Sumnayak-Dev007/User_AuthAPI.git

```
2. Build and start Docker containers
```
docker-compose up --build

```
This will:

Build the Django image

Start PostgreSQL and Django containers

Run migrations automatically

Create a superuser automatically

Start the Django server at http://localhost:8000

4. Access the API & Admin Panel

Admin Panel: http://localhost:8000/admin/

Username: admin

Password: 

## Testing
Run unit tests with Pytest:
```
docker-compose exec web pytest

```
All tests are in users/auth_pytest.py/

Covers registration, login, and profile endpoints

## Notes
The project is fully Dockerized; just run docker-compose up --build.

entrypoint.sh handles migrations, superuser creation, and static files.

JWT authentication is used for protected endpoints.

Middleware logs the user IP for registrations and logins.
