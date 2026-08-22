from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.employee import Employee


def test_admin_can_access_users_management(client: TestClient, admin_token: str):
    res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_hr_officer_cannot_access_users_management(client: TestClient, hr_token: str):
    res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 403
    assert res.json()["success"] is False
    assert res.json()["error_code"] == "PERMISSION_DENIED"


def test_employee_cannot_access_users_management(client: TestClient, employee_token: str):
    res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 403
    assert res.json()["success"] is False


def test_employee_cannot_access_other_employee_salary(
    client: TestClient, employee_token: str, db_session: Session
):
    # Employee 1 is John Doe. Let's find Alice Smith's employee id (emp 2)
    emp2 = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()
    assert emp2 is not None

    # John Doe attempts to query Alice Smith's salary
    res = client.get(
        f"/api/v1/salaries/employee/{emp2.id}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 403
    assert res.json()["success"] is False
    assert "Access denied" in res.json()["message"]


def test_employee_can_access_own_salary(
    client: TestClient, employee_token: str, db_session: Session
):
    emp1 = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()
    assert emp1 is not None

    res = client.get(
        f"/api/v1/salaries/employee/{emp1.id}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["data"]["employee_id"] == emp1.id


def test_employee_cannot_access_other_private_info(
    client: TestClient, employee_token: str, db_session: Session
):
    emp2 = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    res = client.get(
        f"/api/v1/employees/{emp2.id}/private-info",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 403
    assert res.json()["success"] is False


def test_hr_officer_can_access_employee_private_info(
    client: TestClient, hr_token: str, db_session: Session
):
    emp2 = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    res = client.get(
        f"/api/v1/employees/{emp2.id}/private-info",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["data"]["bank_name"] == "Wells Fargo"
