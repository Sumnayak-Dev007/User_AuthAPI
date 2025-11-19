# User Authentication API (Django + Docker)
### Overview

This project implements a Django REST for user management, including registration, login, and profile retrieval. It is fully Dockerized with PostgreSQL and includes JWT token authentication.

### Features
- Custom user model extending Django’s AbstractUser with additional fields: (phone_number, date_of_birth, last_login_ip)
- User registration, login, and profile retrieval
- JWT authentication
- Middleware for capturing user IP
- Fully Dockerized with PostgreSQL
- Pytest test cases included
- class-based views


### REST endpoints:

#### POST /api/register/ — User registration with JWT tokens

#### POST /api/login/ — User login and obtain JWT tokens

#### GET /api/profile/ — Retrieve authenticated user profile 

# Installation & Running

## Prerequisites

#### Docker (>=20.10)

#### Docker Compose (>=2.0)

#### Optional: Postman or Insomnia for API testing

#### Docker handles Python, PostgreSQL, and dependencies automatically — no manual setup required.

## Installation & Running

### 1. Clone the repository

```
git clone https://github.com/Sumnayak-Dev007/User_AuthAPI.git

```
### 2. Build and start Docker containers

```
docker-compose up --build -d

```

#### Django server will start at :  http://localhost:8000

### 3. Open your browser and visit : http://localhost:8000


### 4. Access the API & Admin Panel

### Admin Panel: http://localhost:8000/admin/

#### Username: admin

#### Password: admin123

## Testing
### Run unit tests with Pytest:
```
docker-compose exec web pytest -vv -s

```
### Test File Location
```
users/tests/auth_pytest.py/

```

### What is covered in the test cases?

### The tests include:

### User Registration Test

- #### Validates successful registration

- #### Confirms returned fields: username, email, phone number, DOB

- #### Ensures JWT access and refresh tokens are generated

- #### Verifies signup_ip is stored through custom middleware

- #### Invalid Phone Number Test

- #### Tests phone number validation for Indian format

- #### Ensures incorrect phone numbers are rejected with 400 Bad Request

### User Login Test

- #### Checks valid username/password authentication

- #### Verified access + refresh tokens are returned

- #### Ensures last_login_ip is saved correctly

### User Profile Test

- #### Confirms /api/profile/ requires JWT authentication

- #### Allows authenticated users to retrieve their own profile information.

- #### Requires access token in the Authorization header.

- #### Validates returned profile data for authenticated user

- #### Confirms last_login_ip updates after login


# API Endpoints
### 1. Register a new user

- ### Endpoint: POST /api/register/

- ### Request JSON:
```
{
  "username": "test1",
  "email": "test@gmail.com",
  "password": "asdf1234",
  "password_again": "asdf1234",
  "phone_number": "+919876543210",
  "date_of_birth": "2004-08-20"
}

```
- ### Response JSON:
```
{
  "username": "test1",
  "email": "test@gmail.com",
  "phone_number": "+919876543210",
  "date_of_birth": "2004-08-20",
  "signup_ip": "172.18.0.1"
}

```
### 2. Login
- ### Endpoint: POST /api/login/
- ### Request JSON:
```
{
  "username": "test1",
  "password": "asdf1234"
}

```
- ### Response JSON:
```
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}

```
## 3. Get User Profile

- ### Endpoint: GET /api/profile/
- ### Authorization: Bearer token in header
```
Authorization: Bearer <access_token>

```

- ### Response JSON:
```
{
  "id": 1,
  "username": "test1",
  "email": "test@gmail.com",
  "phone_number": "+919876543210",
  "date_of_birth": "2004-08-20",
  "last_login_ip": "172.18.0.1"
}


```
### You can use Postman, Insomnia, or curl to test these endpoints.
# Notes

The project is fully Dockerized; 

just run docker-compose up --build.

This will:

- Build the Django image

- Start PostgreSQL and Django containers

- Run migrations automatically

- Create a superuser automatically

- Start the Django server at :  http://localhost:8000

entrypoint.sh handles migrations, superuser creation, and static files.

JWT authentication is used for protected endpoints.

Middleware logs the user IP for registrations and logins.
