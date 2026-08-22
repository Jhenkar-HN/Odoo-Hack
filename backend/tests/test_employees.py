from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.user import User


def test_create_employee_with_auto_login_id(client: TestClient, admin_token: str):
    res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Robert",
            "last_name": "Miller",
            "email": "robert.miller@hrmscorp.com",
            "phone": "+1-555-9988",
            "department": "Engineering",
            "job_position": "Backend Developer",
            "date_of_joining": "2026-06-01",
            "private_info": {
                "pan": "ABCDE9999Z",
                "bank_name": "Citibank",
                "bank_account_number": "112233445566"
            }
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert "data" in data
    # Login ID format: OI + RO + MI + 2026 + 001 = OIROMI2026001
    assert data["data"]["login_id"] == "OIROMI2026001"
    assert "temporary_password" in data["data"]
    assert data["data"]["employee"]["first_name"] == "Robert"


def test_create_employee_duplicate_email_fails(client: TestClient, admin_token: str):
    # Try to create employee with existing email (john.doe@hrmscorp.com)
    res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Johnny",
            "last_name": "Doe",
            "email": "john.doe@hrmscorp.com",
            "department": "Engineering",
            "job_position": "QA Engineer"
        }
    )
    assert res.status_code == 409
    assert res.json()["success"] is False
    assert res.json()["error_code"] == "DUPLICATE_RESOURCE"


def test_employee_directory_search(client: TestClient, employee_token: str):
    res = client.get(
        "/api/v1/employees?query=Alice",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] >= 1
    assert any(emp["first_name"] == "Alice" for emp in data["items"])


def test_employee_skills_and_certifications(client: TestClient, employee_token: str, db_session: Session):
    # Get John Doe's profile id
    user = db_session.query(User).filter(User.email == "john.doe@hrmscorp.com").first()

    # Add skill
    res_skill = client.post(
        f"/api/v1/employees/{user.employee_id}/skills",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"name": "Kubernetes"}
    )
    assert res_skill.status_code == 200

    # Add certification
    res_cert = client.post(
        f"/api/v1/employees/{user.employee_id}/certifications",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "name": "CKA - Certified Kubernetes Administrator",
            "issuing_organization": "Linux Foundation",
            "issue_date": "2025-01-10"
        }
    )
    assert res_cert.status_code == 200
    assert res_cert.json()["data"]["name"] == "CKA - Certified Kubernetes Administrator"
