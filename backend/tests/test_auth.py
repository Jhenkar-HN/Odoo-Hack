from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.user import User


def test_login_success_with_email(client: TestClient):
    res = client.post("/api/v1/auth/login", json={
        "login_id": "admin@hrmscorp.com",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "ADMIN"
    assert "password" not in data["data"]


def test_login_success_with_generated_login_id(client: TestClient):
    res = client.post("/api/v1/auth/login", json={
        "login_id": "OIAD2025001",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["login_id"] == "OIAD2025001"


def test_login_failure_invalid_password(client: TestClient):
    res = client.post("/api/v1/auth/login", json={
        "login_id": "admin@hrmscorp.com",
        "password": "WrongPassword!99"
    })
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "UNAUTHORIZED"


def test_login_failure_invalid_user(client: TestClient):
    res = client.post("/api/v1/auth/login", json={
        "login_id": "nonexistent@hrmscorp.com",
        "password": "AnyPassword123"
    })
    assert res.status_code == 401
    assert res.json()["success"] is False


def test_login_failure_inactive_user(client: TestClient, db_session: Session):
    # Deactivate user
    user = db_session.query(User).filter(User.email == "john.doe@hrmscorp.com").first()
    user.is_active = False
    db_session.commit()

    res = client.post("/api/v1/auth/login", json={
        "login_id": "john.doe@hrmscorp.com",
        "password": "Emp@123"
    })
    assert res.status_code == 401
    assert "inactive" in res.json()["message"].lower()


def test_get_me_endpoint(client: TestClient, admin_token: str):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["email"] == "admin@hrmscorp.com"
    assert data["data"]["role"] == "ADMIN"
    assert "password_hash" not in data["data"]


def test_protected_route_rejects_missing_token(client: TestClient):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert res.json()["success"] is False


def test_change_password_flow(client: TestClient, employee_token: str):
    # Change password
    res = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "old_password": "Emp@123",
            "new_password": "NewSecretPassword@456"
        }
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Login with old password fails
    res_old = client.post("/api/v1/auth/login", json={
        "login_id": "john.doe@hrmscorp.com",
        "password": "Emp@123"
    })
    assert res_old.status_code == 401

    # Login with new password succeeds
    res_new = client.post("/api/v1/auth/login", json={
        "login_id": "john.doe@hrmscorp.com",
        "password": "NewSecretPassword@456"
    })
    assert res_new.status_code == 200
    assert res_new.json()["success"] is True


def test_signup_success(client: TestClient):
    res = client.post("/api/v1/auth/signup", json={
        "employee_id": "OINEW2026001",
        "email": "new.hire@hrmscorp.com",
        "full_name": "New Hire",
        "password": "StrongPassword123!",
        "role": "EMPLOYEE"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["email"] == "new.hire@hrmscorp.com"
    assert data["data"]["role"] == "EMPLOYEE"


def test_signup_weak_password_rejected(client: TestClient):
    # Too short (< 8 chars)
    res = client.post("/api/v1/auth/signup", json={
        "employee_id": "OIBAD2026001",
        "email": "bad.pass@hrmscorp.com",
        "password": "short1",
        "role": "EMPLOYEE"
    })
    assert res.status_code == 422


def test_signup_duplicate_email_rejected(client: TestClient):
    res = client.post("/api/v1/auth/signup", json={
        "employee_id": "OIDUP2026001",
        "email": "admin@hrmscorp.com",
        "password": "ValidPassword123!",
        "role": "EMPLOYEE"
    })
    assert res.status_code in [400, 409]
    assert res.json()["success"] is False


def test_verify_email_endpoint(client: TestClient):
    res = client.post("/api/v1/auth/verify-email", json={
        "email": "test.user@hrmscorp.com",
        "code": "123456"
    })
    assert res.status_code == 200
    assert res.json()["data"]["verified"] is True

