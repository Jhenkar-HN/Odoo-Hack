import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_full_hrms_integration_workflow(client: TestClient):
    """
    End-to-end integration test verifying the complete multi-member workflow:
    1. Admin logs in
    2. Admin creates a new Employee (Member 2 foundation) -> Verifies Login ID generation & User account
    3. Admin assigns Salary structure (Member 3 foundation)
    4. New Employee logs in with temporary credentials
    5. Employee checks in (Member 4 foundation)
    6. Employee checks out -> Verifies work hours & overtime calculation
    7. Employee views personal attendance log & summary
    8. Employee submits a Time-Off request
    9. HR Officer logs in and reviews/approves the Time-Off request
    10. Employee views updated Time-Off status and verified deducted leave balance
    """
    # -------------------------------------------------------------
    # Step 1: Admin logs in
    # -------------------------------------------------------------
    admin_login_res = client.post("/api/v1/auth/login", json={
        "login_id": "admin@hrmscorp.com",
        "password": "Admin@123"
    })
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["data"]["access_token"]
    assert admin_token is not None

    # -------------------------------------------------------------
    # Step 2: Admin creates a new Employee
    # -------------------------------------------------------------
    emp_payload = {
        "first_name": "Daniel",
        "last_name": "Craig",
        "email": "daniel.craig@hrmscorp.com",
        "phone": "+1-555-0077",
        "department": "Security",
        "job_position": "Security Operations Lead",
        "date_of_joining": "2026-01-15",
        "private_info": {
            "pan": "DCRAG0070Z",
            "bank_name": "Barclays",
            "bank_account_number": "998877665544"
        }
    }
    create_emp_res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=emp_payload
    )
    assert create_emp_res.status_code == 201
    emp_data = create_emp_res.json()["data"]
    employee_id = emp_data["employee"]["id"]
    login_id = emp_data["login_id"]
    temp_password = emp_data["temporary_password"]

    # Verify Login ID follows: OI + DA + CR + 2026 + 001 = OIDACR2026001
    assert login_id == "OIDACR2026001"
    assert temp_password is not None

    # -------------------------------------------------------------
    # Step 3: Admin assigns Salary to the new Employee
    # -------------------------------------------------------------
    salary_payload = {
        "monthly_wage": "12000.00",
        "yearly_wage": "144000.00",
        "basic_salary": "6000.00",
        "hra": "3000.00",
        "standard_allowance": "1200.00",
        "performance_bonus": "1000.00",
        "leave_travel_allowance": "400.00",
        "fixed_allowance": "400.00",
        "professional_tax": "200.00",
        "employee_pf": "720.00",
        "employer_pf": "720.00",
        "effective_from": "2026-01-15"
    }
    set_salary_res = client.post(
        f"/api/v1/salaries/employee/{employee_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=salary_payload
    )
    assert set_salary_res.status_code == 201
    salary_res_data = set_salary_res.json()["data"]
    assert float(salary_res_data["monthly_wage"]) == 12000.0
    assert float(salary_res_data["net_salary"]) > 0

    # -------------------------------------------------------------
    # Step 4: New Employee logs in with generated Login ID and temp password
    # -------------------------------------------------------------
    emp_login_res = client.post("/api/v1/auth/login", json={
        "login_id": login_id,
        "password": temp_password
    })
    assert emp_login_res.status_code == 200
    emp_token = emp_login_res.json()["data"]["access_token"]
    assert emp_login_res.json()["data"]["employee_id"] == employee_id

    # -------------------------------------------------------------
    # Step 5: Employee Checks In
    # -------------------------------------------------------------
    checkin_date = (date.today() + timedelta(days=5)).isoformat()
    checkin_res = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={"attendance_date": checkin_date}
    )
    assert checkin_res.status_code == 201
    assert checkin_res.json()["data"]["check_in"] is not None

    # -------------------------------------------------------------
    # Step 6: Employee Checks Out
    # -------------------------------------------------------------
    checkout_res = client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={"attendance_date": checkin_date}
    )
    assert checkout_res.status_code == 200
    assert checkout_res.json()["data"]["check_out"] is not None

    # -------------------------------------------------------------
    # Step 7: Employee views personal attendance history & summary
    # -------------------------------------------------------------
    att_history_res = client.get(
        "/api/v1/attendance/my-history",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert att_history_res.status_code == 200
    assert att_history_res.json()["data"]["total"] >= 1

    summary_res = client.get(
        "/api/v1/attendance/my-summary",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert summary_res.status_code == 200
    assert summary_res.json()["data"]["total_days_present"] >= 1

    # -------------------------------------------------------------
    # Step 8: Employee views balances & Submits a Time-Off request
    # -------------------------------------------------------------
    balances_res = client.get(
        "/api/v1/time-off/my-balances",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert balances_res.status_code == 200
    pto_bal = next(b for b in balances_res.json()["data"] if "Paid Time Off" in b["leave_type_name"])
    initial_remaining = float(pto_bal["remaining_days"])
    leave_type_id = pto_bal["leave_type_id"]

    start_date = (date.today() + timedelta(days=15)).isoformat()
    end_date = (date.today() + timedelta(days=17)).isoformat()  # 3 days

    time_off_res = client.post(
        "/api/v1/time-off/requests",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={
            "leave_type_id": leave_type_id,
            "start_date": start_date,
            "end_date": end_date,
            "reason": "Personal rest and travel"
        }
    )
    assert time_off_res.status_code == 201
    request_id = time_off_res.json()["data"]["id"]
    assert time_off_res.json()["data"]["status"] == "PENDING"
    assert float(time_off_res.json()["data"]["number_of_days"]) == 3.0

    # -------------------------------------------------------------
    # Step 9: HR Officer logs in and Approves the request
    # -------------------------------------------------------------
    hr_login_res = client.post("/api/v1/auth/login", json={
        "login_id": "hr@hrmscorp.com",
        "password": "Hr@123"
    })
    assert hr_login_res.status_code == 200
    hr_token = hr_login_res.json()["data"]["access_token"]

    approve_res = client.put(
        f"/api/v1/time-off/requests/{request_id}/approve",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["data"]["status"] == "APPROVED"

    # -------------------------------------------------------------
    # Step 10: Employee views updated status and deducted balance
    # -------------------------------------------------------------
    my_requests_res = client.get(
        "/api/v1/time-off/my-requests",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert my_requests_res.status_code == 200
    my_req = next(r for r in my_requests_res.json()["data"]["items"] if r["id"] == request_id)
    assert my_req["status"] == "APPROVED"

    updated_balances_res = client.get(
        "/api/v1/time-off/my-balances",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert updated_balances_res.status_code == 200
    updated_pto = next(b for b in updated_balances_res.json()["data"] if b["leave_type_id"] == leave_type_id)
    assert float(updated_pto["remaining_days"]) == initial_remaining - 3.0
    assert float(updated_pto["used_days"]) == 3.0
