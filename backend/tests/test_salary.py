from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.employee import Employee


def test_salary_breakdown_computation(client: TestClient, hr_token: str, db_session: Session):
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    res = client.get(
        f"/api/v1/salaries/employee/{emp.id}/breakdown",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert float(data["monthly_wage"]) == 8500.0
    assert float(data["basic_salary"]) == 4250.0
    assert float(data["hra"]) == 2125.0
    assert float(data["net_salary"]) > 0


def test_admin_updates_salary(client: TestClient, admin_token: str, db_session: Session):
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "9000.00",
            "yearly_wage": "108000.00",
            "basic_salary": "4500.00",
            "hra": "2250.00",
            "standard_allowance": "900.00",
            "performance_bonus": "500.00",
            "leave_travel_allowance": "400.00",
            "fixed_allowance": "450.00",
            "professional_tax": "200.00",
            "employee_pf": "540.00",
            "employer_pf": "540.00",
            "effective_from": "2025-05-01"
        }
    )
    assert res.status_code == 201
    assert float(res.json()["data"]["monthly_wage"]) == 9000.0


def test_negative_salary_rejected(client: TestClient, admin_token: str, db_session: Session):
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "-5000.00",
            "basic_salary": "2500.00"
        }
    )
    # Validation error from Pydantic
    assert res.status_code == 422
    assert res.json()["success"] is False


def test_employee_cannot_modify_salary(client: TestClient, employee_token: str, db_session: Session):
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"monthly_wage": "15000.00"}
    )
    assert res.status_code == 403
