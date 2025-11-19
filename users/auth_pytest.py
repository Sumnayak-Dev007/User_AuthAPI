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
        "password2": "StrongPassw0rd!",
        "phone_number": "9876543210",
        "date_of_birth": "2004-05-20",
    }

    print("\nTesting user registration...")

    r = client.post(register_url, user_data, format="json")
    assert r.status_code == 201, f"Register failed: {r.data}"
    assert "access" in r.data, "JWT access token missing in register response"

    access = r.data["access"]
    refresh = r.data["refresh"]

    print("✔ Registration success")
    print("✔ JWT token received")

    # Login
    print("\nTesting login...")
    login_data = {
        "username": "testuser",
        "password": "StrongPassw0rd!"
    }

    l = client.post(login_url, login_data, format="json", REMOTE_ADDR="1.2.3.4")
    assert l.status_code == 200, f"Login failed: {l.data}"

    print("Login success")

    # Profile access
    print("\nValidating profile data...")

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    pr = client.get(profile_url)

    assert pr.status_code == 200, f"❌ Profile fetch failed: {pr.data}"
    assert pr.data["username"] == "testuser", "❌ Username mismatch"
    assert pr.data["phone_number"] == "9876543210", "❌ Phone number mismatch"
    assert pr.data["date_of_birth"] == "2004-05-20", "❌ Date of birth mismatch"

    print("✔ Profile data verified successfully")

    # Check last_login_ip updated from login
    user = CustomUser.objects.get(username="testuser")
    assert user.last_login_ip == "1.2.3.4", (
        f"❌ last_login_ip not updated correctly (got {user.last_login_ip})"
    )

    print("last_login_ip correctly stored")
    print("\nUser authentication flow successful — user is valid")


@pytest.mark.django_db
def test_invalid_phone_registration():
    client = APIClient()
    register_url = "/api/register/"

    user_data = {
        "username": "badphone",
        "email": "bad@example.com",
        "password": "StrongPassw0rd!",
        "password2": "StrongPassw0rd!",
        "phone_number": "12345",
        "date_of_birth": "2000-02-02",
    }

    print("\nTesting invalid phone number validation...")

    r = client.post(register_url, user_data, format="json")

    assert r.status_code == 400, f"Expected validation error, got {r.status_code}"
    assert "phone_number" in r.data or "non_field_errors" in r.data, (
        f"No phone number error message received. Response: {r.data}"
    )

    print("✔ Invalid phone_number correctly rejected")
    print(f" Error detail: {r.data}")


# NEW: Dedicated Profile Test
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

    # Try profile without auth
    response = client.get("/api/profile/")
    assert response.status_code == 401, "Profile should require authentication"

    # Login to get token
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

    # Validate fields
    assert profile.data["username"] == "profileuser"
    assert profile.data["email"] == "p@example.com"
    assert profile.data["phone_number"] == "9998887776"
    assert profile.data["date_of_birth"] == "2001-01-01"

    # last_login_ip should be saved from login
    user.refresh_from_db()
    assert user.last_login_ip == "9.8.7.6"

    print("\nProfile endpoint validated in isolation")
