import pytest
from rest_framework.test import APIClient
from users.models import CustomUser


@pytest.mark.django_db
def test_register_login_profile_flow():
    client = APIClient()

    register_url = "/api/register/"
    login_url = "/api/login/"
    profile_url = "/api/profile/"

    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPassw0rd!",
        "password_again": "StrongPassw0rd!",
        "phone_number": "9876543210",
        "date_of_birth": "2004-05-20",
    }

    print("\nTesting user registration...")

    r = client.post(register_url, user_data, format="json")
    assert r.status_code == 201, f"Register failed: {r.data}"

    print("✔ Registration success")

    # Now test login (token returned here)
    print("\nTesting login...")

    login_data = {"username": "testuser", "password": "StrongPassw0rd!"}

    l = client.post(login_url, login_data, format="json", REMOTE_ADDR="1.2.3.4")
    assert l.status_code == 200, f"Login failed: {l.data}"
    assert "access" in l.data, "JWT access token missing in login response"
    assert "refresh" in l.data, "JWT refresh token missing in login response"

    access = l.data["access"]

    print("✔ Login success")
    print("✔ JWT token received")

    # Profile access
    print("\nValidating profile data...")

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    pr = client.get(profile_url)

    assert pr.status_code == 200, f"Profile fetch failed: {pr.data}"
    assert pr.data["username"] == "testuser"
    assert pr.data["phone_number"] == "9876543210"
    assert pr.data["date_of_birth"] == "2004-05-20"

    print("✔ Profile data verified successfully")

    user = CustomUser.objects.get(username="testuser")
    assert user.last_login_ip == "1.2.3.4"

    print("✔ last_login_ip stored correctly")
    print("\nUser authentication flow successful")


@pytest.mark.django_db
def test_invalid_phone_registration():
    client = APIClient()
    register_url = "/api/register/"

    user_data = {
        "username": "badphone",
        "email": "bad@example.com",
        "password": "StrongPassw0rd!",
        "password_again": "StrongPassw0rd!",
        "phone_number": "12345",
        "date_of_birth": "2000-02-02",
    }

    print("\nTesting invalid phone number validation...")

    r = client.post(register_url, user_data, format="json")

    assert r.status_code == 400
    assert "phone_number" in r.data or "non_field_errors" in r.data

    print("✔ Invalid phone_number correctly rejected")


@pytest.mark.django_db
def test_profile_requires_auth_and_returns_correct_fields():
    client = APIClient()

    # Create user manually
    user = CustomUser.objects.create_user(
        username="profileuser",
        email="p@example.com",
        phone_number="9998887776",
        date_of_birth="2001-01-01",
        password="StrongPassw0rd!"
    )

    # Profile without token
    response = client.get("/api/profile/")
    assert response.status_code == 401

    # Login for token
    login_response = client.post(
        "/api/login/",
        {"username": "profileuser", "password": "StrongPassw0rd!"},
        format="json",
        REMOTE_ADDR="9.8.7.6"
    )

    assert login_response.status_code == 200
    access = login_response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    profile = client.get("/api/profile/")

    assert profile.status_code == 200
    assert profile.data["username"] == "profileuser"
    assert profile.data["email"] == "p@example.com"
    assert profile.data["phone_number"] == "9998887776"
    assert profile.data["date_of_birth"] == "2001-01-01"

    user.refresh_from_db()
    assert user.last_login_ip == "9.8.7.6"

    print("\n✔ Profile endpoint validated successfully")
