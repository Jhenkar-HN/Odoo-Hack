from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_attendance_check_in_and_out_flow(client: TestClient, employee2_token: str):
    # Use future date to avoid clash with seed data
    test_date = (date.today() + timedelta(days=10)).isoformat()

    # 1. Check-in
    res_in = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee2_token}"},
        json={"attendance_date": test_date}
    )
    assert res_in.status_code == 201
    assert res_in.json()["success"] is True
    assert res_in.json()["data"]["check_in"] is not None

    # 2. Duplicate check-in fails
    res_dup = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee2_token}"},
        json={"attendance_date": test_date}
    )
    assert res_dup.status_code == 409
    assert res_dup.json()["success"] is False

    # 3. Check-out
    res_out = client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee2_token}"},
        json={"attendance_date": test_date}
    )
    assert res_out.status_code == 200
    assert res_out.json()["success"] is True
    assert res_out.json()["data"]["check_out"] is not None


def test_check_out_without_check_in_fails(client: TestClient, employee2_token: str):
    test_date = (date.today() + timedelta(days=20)).isoformat()

    res = client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee2_token}"},
        json={"attendance_date": test_date}
    )
    assert res.status_code == 400
    assert "Cannot check out without checking in" in res.json()["message"]


def test_attendance_summary(client: TestClient, employee_token: str):
    res = client.get(
        "/api/v1/attendance/my-summary",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_days_present" in data
    assert "total_work_hours" in data
