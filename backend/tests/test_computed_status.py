from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.employee import Employee
from backend.app.models.attendance import Attendance, AttendanceStatus
from backend.app.models.leave import TimeOffRequest, LeaveType, LeaveRequestStatus
from backend.app.services.employee_service import employee_service


def test_computed_status_present_on_checkin(client: TestClient, admin_token: str, db_session: Session):
    """
    Test status is 'present' when employee has an active or completed check-in today.
    """
    # 1. Create an employee
    emp_res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Marcus",
            "last_name": "Aurelius",
            "email": "marcus.status.test@hrmscorp.com",
            "department": "Executive",
            "job_position": "Director",
        },
    )
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["data"]["id"]

    # Initial status should be 'absent'
    status_initial = employee_service.compute_employee_status(db_session, emp_id)
    assert status_initial == "absent"

    # 2. Add an attendance check-in for today
    today = date.today()
    now = datetime.now(timezone.utc)
    att = Attendance(
        employee_id=emp_id,
        attendance_date=today,
        check_in=now,
        check_out=None,  # Active check-in
        work_hours=Decimal("0.00"),
        status=AttendanceStatus.PRESENT,
    )
    db_session.add(att)
    db_session.commit()

    # Verify computed status is now 'present'
    status_after_checkin = employee_service.compute_employee_status(db_session, emp_id)
    assert status_after_checkin == "present"

    # Verify API response includes status == 'present'
    api_res = client.get(
        f"/api/v1/employees/{emp_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert api_res.status_code == 200
    assert api_res.json()["data"]["status"] == "present"
    assert api_res.json()["data"]["attendance_status"] == "present"


def test_computed_status_on_leave_with_approved_request(client: TestClient, admin_token: str, db_session: Session):
    """
    Test status is 'on_leave' when employee has an approved time-off request covering today.
    """
    # 1. Create an employee
    emp_res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Seneca",
            "last_name": "Younger",
            "email": "seneca.leave.test@hrmscorp.com",
            "department": "Philosophy",
            "job_position": "Advisor",
        },
    )
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["data"]["id"]

    # 2. Ensure a leave type exists
    lt = db_session.query(LeaveType).first()
    if not lt:
        lt = LeaveType(name="Vacation Leave", default_allocation=15)
        db_session.add(lt)
        db_session.commit()

    # 3. Add an approved leave request covering today
    today = date.today()
    leave_req = TimeOffRequest(
        employee_id=emp_id,
        leave_type_id=lt.id,
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=2),
        number_of_days=Decimal("4.0"),
        reason="Philosophical retreat",
        status=LeaveRequestStatus.APPROVED,
    )
    db_session.add(leave_req)
    db_session.commit()

    # Verify computed status is 'on_leave'
    status_leave = employee_service.compute_employee_status(db_session, emp_id)
    assert status_leave == "on_leave"

    # Verify API response
    api_res = client.get(
        f"/api/v1/employees/{emp_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert api_res.status_code == 200
    assert api_res.json()["data"]["status"] == "on_leave"


def test_computed_status_absent_by_default(client: TestClient, admin_token: str, db_session: Session):
    """
    Test status is 'absent' when employee has no check-in and no approved leave today.
    """
    emp_res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Epictetus",
            "last_name": "Stoic",
            "email": "epictetus.absent.test@hrmscorp.com",
            "department": "Ethics",
            "job_position": "Lecturer",
        },
    )
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["data"]["id"]

    status = employee_service.compute_employee_status(db_session, emp_id)
    assert status == "absent"

    # Check via list endpoint
    list_res = client.get(
        f"/api/v1/employees?query=epictetus",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_res.status_code == 200
    items = list_res.json()["data"]["items"]
    assert len(items) >= 1
    target = next((item for item in items if item["id"] == emp_id), None)
    assert target is not None
    assert target["status"] == "absent"


def test_batch_computed_statuses_in_employee_list(client: TestClient, admin_token: str, db_session: Session):
    """
    Test batch computation for all employees in GET /api/v1/employees.
    """
    list_res = client.get(
        "/api/v1/employees?size=50",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_res.status_code == 200
    items = list_res.json()["data"]["items"]
    assert len(items) > 0

    valid_statuses = {"present", "on_leave", "absent"}
    for item in items:
        assert "status" in item
        assert item["status"] in valid_statuses
