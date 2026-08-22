import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.employee import Employee
from backend.app.models.salary import Salary


# ============================================================================
# STEP 7 SPECIFIED TESTS (TEST 1 to TEST 16)
# ============================================================================

def test_1_create_salary_with_valid_data(client: TestClient, admin_token: str, db_session: Session):
    """TEST 1: Create salary with valid data."""
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    payload = {
        "monthly_wage": "10000.00",
        "yearly_wage": "120000.00",
        "basic_salary": "5000.00",
        "hra": "2500.00",
        "standard_allowance": "1000.00",
        "performance_bonus": "500.00",
        "leave_travel_allowance": "500.00",
        "fixed_allowance": "500.00",
        "professional_tax": "200.00",
        "employee_pf": "600.00",
        "employer_pf": "600.00",
        "effective_from": "2025-06-01",
    }
    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    json_data = res.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["employee_id"] == emp.id
    assert float(data["monthly_wage"]) == 10000.00
    assert float(data["yearly_wage"]) == 120000.00
    assert float(data["basic_salary"]) == 5000.00
    assert float(data["total_earnings"]) == 10000.00
    assert float(data["total_deductions"]) == 800.00
    assert float(data["net_salary"]) == 9200.00


def test_2_get_all_salary_records(client: TestClient, admin_token: str, hr_token: str, employee_token: str):
    """TEST 2: Get all salary records."""
    # Admin can list all salaries
    res_admin = client.get("/api/v1/salaries", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert res_admin.json()["success"] is True
    assert isinstance(res_admin.json()["data"], list)
    assert len(res_admin.json()["data"]) > 0

    # HR Officer can list all salaries
    res_hr = client.get("/api/v1/salaries", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_hr.status_code == 200
    assert res_hr.json()["success"] is True
    assert isinstance(res_hr.json()["data"], list)

    # Standard employee cannot list all salaries
    res_emp = client.get("/api/v1/salaries", headers={"Authorization": f"Bearer {employee_token}"})
    assert res_emp.status_code == 403


def test_3_get_salary_for_valid_employee(
    client: TestClient, admin_token: str, hr_token: str, employee_token: str, db_session: Session
):
    """TEST 3: Get salary for a valid employee."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    # Admin access
    res_admin = client.get(f"/api/v1/salaries/employee/{emp.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert res_admin.json()["data"]["employee_id"] == emp.id

    # HR Officer access
    res_hr = client.get(f"/api/v1/salaries/employee/{emp.id}", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_hr.status_code == 200
    assert res_hr.json()["data"]["employee_id"] == emp.id

    # Self Employee access
    res_emp = client.get(f"/api/v1/salaries/employee/{emp.id}", headers={"Authorization": f"Bearer {employee_token}"})
    assert res_emp.status_code == 200
    assert res_emp.json()["data"]["employee_id"] == emp.id


def test_4_get_salary_breakdown(client: TestClient, hr_token: str, employee_token: str, db_session: Session):
    """TEST 4: Get salary breakdown."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    res = client.get(
        f"/api/v1/salaries/employee/{emp.id}/breakdown",
        headers={"Authorization": f"Bearer {hr_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["employee_id"] == emp.id
    assert data["employee_name"] == "John Doe"
    assert float(data["monthly_wage"]) == 8500.00
    assert float(data["basic_salary"]) == 4250.00
    assert float(data["hra"]) == 2125.00
    assert float(data["allowances_total"]) == 2125.00
    assert float(data["gross_earnings"]) == 8500.00
    assert float(data["total_deductions"]) == 710.00  # 200 (tax) + 510 (epf)
    assert float(data["net_salary"]) == 7790.00
    assert float(data["pf_total"]) == 1020.00  # 510 (epf) + 510 (emppf)


def test_5_update_salary_successfully(client: TestClient, admin_token: str, db_session: Session):
    """TEST 5: Update salary successfully (PUT and PATCH)."""
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    # PUT full update
    res_put = client.put(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "12000.00",
            "yearly_wage": "144000.00",
            "basic_salary": "6000.00",
            "hra": "3000.00",
            "standard_allowance": "1000.00",
            "performance_bonus": "1000.00",
            "leave_travel_allowance": "500.00",
            "fixed_allowance": "500.00",
            "professional_tax": "200.00",
            "employee_pf": "720.00",
            "employer_pf": "720.00",
        },
    )
    assert res_put.status_code == 200
    data_put = res_put.json()["data"]
    assert float(data_put["monthly_wage"]) == 12000.00
    assert float(data_put["basic_salary"]) == 6000.00
    assert float(data_put["total_earnings"]) == 12000.00
    assert float(data_put["net_salary"]) == 11080.00

    # PATCH partial update
    res_patch = client.patch(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"performance_bonus": "1500.00"},
    )
    assert res_patch.status_code == 200
    data_patch = res_patch.json()["data"]
    assert float(data_patch["performance_bonus"]) == 1500.00
    assert float(data_patch["total_earnings"]) == 12500.00
    assert float(data_patch["net_salary"]) == 11580.00


def test_6_invalid_employee_id(client: TestClient, admin_token: str):
    """TEST 6: Invalid employee ID."""
    invalid_id = 999999

    # GET salary for invalid employee
    res_get = client.get(f"/api/v1/salaries/employee/{invalid_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_get.status_code == 404

    # GET breakdown for invalid employee
    res_bd = client.get(f"/api/v1/salaries/employee/{invalid_id}/breakdown", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_bd.status_code == 404

    # POST salary for invalid employee
    res_post = client.post(
        f"/api/v1/salaries/employee/{invalid_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"monthly_wage": "5000.00", "basic_salary": "2500.00"},
    )
    assert res_post.status_code == 404

    # PUT salary for invalid employee
    res_put = client.put(
        f"/api/v1/salaries/employee/{invalid_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"monthly_wage": "5000.00", "basic_salary": "2500.00"},
    )
    assert res_put.status_code == 404

    # DELETE salary for invalid employee
    res_del = client.delete(f"/api/v1/salaries/employee/{invalid_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del.status_code == 404


def test_7_negative_basic_salary(client: TestClient, admin_token: str, db_session: Session):
    """TEST 7: Negative basic salary."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "5000.00",
            "basic_salary": "-2500.00",
        },
    )
    assert res.status_code in [400, 422]
    assert res.json()["success"] is False


def test_8_negative_allowance(client: TestClient, admin_token: str, db_session: Session):
    """TEST 8: Negative allowance."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    allowance_fields = ["hra", "standard_allowance", "performance_bonus", "leave_travel_allowance", "fixed_allowance"]
    for field in allowance_fields:
        res = client.post(
            f"/api/v1/salaries/employee/{emp.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "monthly_wage": "5000.00",
                "basic_salary": "2500.00",
                field: "-100.00",
            },
        )
        assert res.status_code in [400, 422], f"Expected rejection for negative {field}"
        assert res.json()["success"] is False


def test_9_negative_pf_or_tax(client: TestClient, admin_token: str, db_session: Session):
    """TEST 9: Negative PF or tax."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    deduction_fields = ["professional_tax", "employee_pf", "employer_pf"]
    for field in deduction_fields:
        res = client.post(
            f"/api/v1/salaries/employee/{emp.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "monthly_wage": "5000.00",
                "basic_salary": "2500.00",
                field: "-50.00",
            },
        )
        assert res.status_code in [400, 422], f"Expected rejection for negative {field}"
        assert res.json()["success"] is False


def test_10_total_deductions_greater_than_gross_earnings(client: TestClient, admin_token: str, db_session: Session):
    """TEST 10: Total deductions greater than Gross Earnings."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    # Create scenario: Gross = 1000, Deductions = 2000 (500 ptax + 1500 epf)
    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "5000.00",
            "basic_salary": "1000.00",
            "hra": "0.00",
            "professional_tax": "500.00",
            "employee_pf": "1500.00",
        },
    )
    assert res.status_code == 400
    assert res.json()["success"] is False
    assert "cannot exceed gross earnings" in res.json()["message"]


def test_11_unauthorized_request(client: TestClient):
    """TEST 11: Unauthorized request."""
    # Missing token on salary endpoints
    res_list = client.get("/api/v1/salaries")
    assert res_list.status_code == 401

    res_get = client.get("/api/v1/salaries/employee/1")
    assert res_get.status_code == 401

    res_post = client.post("/api/v1/salaries/employee/1", json={"basic_salary": "1000.00"})
    assert res_post.status_code == 401

    # Invalid token
    res_inv = client.get("/api/v1/salaries", headers={"Authorization": "Bearer invalid.token.here"})
    assert res_inv.status_code == 401


def test_12_employee_access_other_employee_salary_forbidden(
    client: TestClient, employee_token: str, employee2_token: str, db_session: Session
):
    """TEST 12: Employee attempting to access another employee's salary."""
    emp1 = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()
    emp2 = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    # Emp2 (alice) trying to access Emp1 (john) salary -> 403
    res1 = client.get(f"/api/v1/salaries/employee/{emp1.id}", headers={"Authorization": f"Bearer {employee2_token}"})
    assert res1.status_code == 403

    # Emp2 (alice) trying to access Emp1 (john) salary breakdown -> 403
    res2 = client.get(f"/api/v1/salaries/employee/{emp1.id}/breakdown", headers={"Authorization": f"Bearer {employee2_token}"})
    assert res2.status_code == 403

    # Emp1 (john) trying to access Emp2 (alice) salary -> 403
    res3 = client.get(f"/api/v1/salaries/employee/{emp2.id}", headers={"Authorization": f"Bearer {employee_token}"})
    assert res3.status_code == 403


def test_13_hr_attempting_restricted_modifications(
    client: TestClient, hr_token: str, employee_token: str, db_session: Session
):
    """TEST 13: HR attempting restricted modifications."""
    emp = db_session.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()

    # HR cannot POST
    res_post = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {hr_token}"},
        json={"monthly_wage": "15000.00"},
    )
    assert res_post.status_code == 403

    # HR cannot PUT
    res_put = client.put(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {hr_token}"},
        json={"monthly_wage": "15000.00"},
    )
    assert res_put.status_code == 403

    # HR cannot PATCH
    res_patch = client.patch(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {hr_token}"},
        json={"monthly_wage": "15000.00"},
    )
    assert res_patch.status_code == 403

    # HR cannot DELETE
    res_del = client.delete(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {hr_token}"},
    )
    assert res_del.status_code == 403

    # Employee cannot POST/PUT/PATCH/DELETE
    res_post_emp = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"monthly_wage": "15000.00"},
    )
    assert res_post_emp.status_code == 403


def test_14_correct_gross_earnings_calculation(client: TestClient, admin_token: str, db_session: Session):
    """
    TEST 14: Correct Gross Earnings calculation.
    Gross Earnings = Basic Salary + HRA + Standard Allowance + Performance Bonus + Leave Travel Allowance + Fixed Allowance
    """
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    basic = Decimal("4000.00")
    hra = Decimal("2000.00")
    std_allow = Decimal("800.00")
    perf_bonus = Decimal("500.00")
    lta = Decimal("300.00")
    fixed_allow = Decimal("400.00")
    expected_gross = basic + hra + std_allow + perf_bonus + lta + fixed_allow  # 8000.00

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": str(expected_gross),
            "basic_salary": str(basic),
            "hra": str(hra),
            "standard_allowance": str(std_allow),
            "performance_bonus": str(perf_bonus),
            "leave_travel_allowance": str(lta),
            "fixed_allowance": str(fixed_allow),
            "professional_tax": "200.00",
            "employee_pf": "480.00",
        },
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert Decimal(str(data["total_earnings"])) == expected_gross


def test_15_correct_total_deductions_calculation(client: TestClient, admin_token: str, db_session: Session):
    """
    TEST 15: Correct Total Deductions calculation.
    Total Deductions = Professional Tax + Employee PF
    (Employer PF does NOT reduce employee net salary).
    """
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    ptax = Decimal("200.00")
    epf = Decimal("500.00")
    emppf = Decimal("500.00")
    expected_deductions = ptax + epf  # 700.00

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "6000.00",
            "basic_salary": "3000.00",
            "hra": "1500.00",
            "standard_allowance": "1500.00",
            "professional_tax": str(ptax),
            "employee_pf": str(epf),
            "employer_pf": str(emppf),
        },
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert Decimal(str(data["total_deductions"])) == expected_deductions


def test_16_correct_net_salary_calculation(client: TestClient, admin_token: str, db_session: Session):
    """
    TEST 16: Correct Net Salary calculation.
    Net Salary = Gross Earnings - Total Deductions
    """
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    gross = Decimal("10000.00")
    deductions = Decimal("800.00")
    expected_net = gross - deductions  # 9200.00

    res = client.post(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "monthly_wage": "10000.00",
            "basic_salary": "5000.00",
            "hra": "2500.00",
            "standard_allowance": "1000.00",
            "performance_bonus": "500.00",
            "leave_travel_allowance": "500.00",
            "fixed_allowance": "500.00",
            "professional_tax": "200.00",
            "employee_pf": "600.00",
            "employer_pf": "600.00",
        },
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert Decimal(str(data["net_salary"])) == expected_net
    assert Decimal(str(data["total_earnings"])) - Decimal(str(data["total_deductions"])) == Decimal(str(data["net_salary"]))


def test_admin_deletes_salary(client: TestClient, admin_token: str, db_session: Session):
    """Test salary deletion by Admin."""
    emp = db_session.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()

    # Delete salary
    res_del = client.delete(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # After deletion, getting salary returns 404
    res_get = client.get(
        f"/api/v1/salaries/employee/{emp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_get.status_code == 404
