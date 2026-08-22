from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_list_leave_types(client: TestClient, employee_token: str):
    res = client.get(
        "/api/v1/time-off/leave-types",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 4


def test_time_off_application_and_approval_flow(
    client: TestClient, employee_token: str, hr_token: str
):
    # 1. Check initial balances
    res_bal = client.get(
        "/api/v1/time-off/my-balances",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res_bal.status_code == 200
    pto_bal = next(b for b in res_bal.json()["data"] if "Paid Time Off" in b["leave_type_name"])
    initial_remaining = float(pto_bal["remaining_days"])
    leave_type_id = pto_bal["leave_type_id"]

    # 2. Apply for 3 days of PTO
    start = date.today() + timedelta(days=30)
    end = date.today() + timedelta(days=32)

    res_apply = client.post(
        "/api/v1/time-off/requests",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "leave_type_id": leave_type_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "reason": "Family vacation"
        }
    )
    assert res_apply.status_code == 201
    req_id = res_apply.json()["data"]["id"]
    assert float(res_apply.json()["data"]["number_of_days"]) == 3.0
    assert res_apply.json()["data"]["status"] == "PENDING"

    # 3. HR approves the request
    res_appr = client.put(
        f"/api/v1/time-off/requests/{req_id}/approve",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert res_appr.status_code == 200
    assert res_appr.json()["data"]["status"] == "APPROVED"

    # 4. Verify balance is deducted by 3 days
    res_bal_after = client.get(
        "/api/v1/time-off/my-balances",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    pto_after = next(b for b in res_bal_after.json()["data"] if b["leave_type_id"] == leave_type_id)
    assert float(pto_after["remaining_days"]) == initial_remaining - 3.0
    assert float(pto_after["used_days"]) == 3.0


def test_time_off_invalid_dates_rejected(client: TestClient, employee_token: str):
    # End date before start date
    res = client.post(
        "/api/v1/time-off/requests",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "leave_type_id": 1,
            "start_date": "2026-08-20",
            "end_date": "2026-08-15",
            "reason": "Invalid time travel"
        }
    )
    assert res.status_code == 422
    assert res.json()["success"] is False
