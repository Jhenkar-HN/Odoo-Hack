from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.company import Company
from backend.app.models.user import User
from backend.app.repositories.company_repo import company_repo
from backend.app.services.id_generator import IDGeneratorService


def test_generated_login_id_format(client: TestClient, hr_token: str, db_session: Session):
    """
    Test format: [CompanyCode][First 2 letters first name][First 2 letters last name][Year][4-digit serial]
    Example: John Doe at company CE in 2024 -> CEJODO20240001
    """
    # Ensure company CE exists
    comp = db_session.query(Company).filter(Company.code == "CE").first()
    if not comp:
        comp = Company(name="Cloud Engineering Corp", code="CE")
        db_session.add(comp)
        db_session.commit()

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "work_email": "johndoe.format.test@hrmscorp.com",
        "department": "Engineering",
        "job_position": "Software Engineer",
        "company": "CE",
        "date_of_joining": "2024-05-15",
    }

    res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()["data"]

    # Verify ID format starts with CEJODO2024 and ends with 4-digit serial
    login_id = data["login_id"]
    assert login_id.startswith("CEJODO2024")
    assert len(login_id) == len("CEJODO20240001")
    assert login_id[-4:].isdigit()
    assert data["temporary_password"] is not None


def test_serial_number_increments_per_company_per_year(client: TestClient, hr_token: str):
    """
    Test serial number increments sequentially per company per year.
    """
    emp1_payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "work_email": "alice.inc1@hrmscorp.com",
        "department": "Design",
        "job_position": "Product Designer",
        "company": "CE",
        "date_of_joining": "2025-01-10",
    }
    emp2_payload = {
        "first_name": "Bob",
        "last_name": "Taylor",
        "work_email": "bob.inc2@hrmscorp.com",
        "department": "Engineering",
        "job_position": "Backend Developer",
        "company": "CE",
        "date_of_joining": "2025-02-15",
    }

    res1 = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=emp1_payload,
    )
    assert res1.status_code == 201
    login_id_1 = res1.json()["data"]["login_id"]

    res2 = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=emp2_payload,
    )
    assert res2.status_code == 201
    login_id_2 = res2.json()["data"]["login_id"]

    # Check format and sequential increment
    assert login_id_1.startswith("CEALSM2025")
    assert login_id_2.startswith("CEBOTA2025")

    serial_1 = int(login_id_1[-4:])
    serial_2 = int(login_id_2[-4:])
    assert serial_2 == serial_1 + 1


def test_duplicate_initials_handling(client: TestClient, hr_token: str):
    """
    Test that two employees with identical first & last initials (e.g. John Doe & Jonathan Donald)
    receive sequential distinct IDs without collision.
    """
    payload_1 = {
        "first_name": "John",
        "last_name": "Doe",
        "work_email": "johndoe.dup1@hrmscorp.com",
        "department": "QA",
        "job_position": "QA Lead",
        "company": "CE",
        "date_of_joining": "2026-03-01",
    }
    payload_2 = {
        "first_name": "Jonathan",
        "last_name": "Donald",
        "work_email": "jondoe.dup2@hrmscorp.com",
        "department": "QA",
        "job_position": "Automation Engineer",
        "company": "CE",
        "date_of_joining": "2026-04-01",
    }

    res1 = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=payload_1,
    )
    assert res1.status_code == 201
    login_id_1 = res1.json()["data"]["login_id"]

    res2 = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=payload_2,
    )
    assert res2.status_code == 201
    login_id_2 = res2.json()["data"]["login_id"]

    # Both have initials JO + DO
    assert login_id_1.startswith("CEJODO2026")
    assert login_id_2.startswith("CEJODO2026")
    assert login_id_1 != login_id_2

    serial_1 = int(login_id_1[-4:])
    serial_2 = int(login_id_2[-4:])
    assert serial_2 == serial_1 + 1


def test_forced_password_change_flow(client: TestClient, hr_token: str, db_session: Session):
    """
    Test employee creation with random temp password and must_change_password flag,
    and verify that /auth/change-password updates password and clears must_change_password.
    """
    emp_payload = {
        "first_name": "Clark",
        "last_name": "Kent",
        "work_email": "clark.kent@dailyplanet.com",
        "department": "Editorial",
        "job_position": "Journalist",
        "company": "CE",
        "date_of_joining": "2026-06-01",
    }

    # 1. Create employee via HR
    create_res = client.post(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {hr_token}"},
        json=emp_payload,
    )
    assert create_res.status_code == 201
    created_data = create_res.json()["data"]
    login_id = created_data["login_id"]
    temp_password = created_data["temporary_password"]
    assert temp_password is not None

    # Check DB flag
    user = db_session.query(User).filter(User.login_id == login_id).first()
    assert user is not None
    assert user.must_change_password is True

    # 2. Login with temporary password
    login_res = client.post(
        "/api/v1/auth/login",
        json={"login_id": login_id, "password": temp_password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    user_token = token_data["access_token"]
    assert token_data["must_change_password"] is True

    # 3. Change password via /auth/change-password endpoint
    new_password = "MySecureNewPassword@2026"
    change_res = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"old_password": temp_password, "new_password": new_password},
    )
    assert change_res.status_code == 200
    assert change_res.json()["success"] is True

    # 4. Verify DB flag must_change_password is now False
    db_session.refresh(user)
    assert user.must_change_password is False

    # 5. Old password no longer works
    fail_res = client.post(
        "/api/v1/auth/login",
        json={"login_id": login_id, "password": temp_password},
    )
    assert fail_res.status_code == 401

    # 6. New password logs in with must_change_password = False
    new_login_res = client.post(
        "/api/v1/auth/login",
        json={"login_id": login_id, "password": new_password},
    )
    assert new_login_res.status_code == 200
    assert new_login_res.json()["data"]["must_change_password"] is False


def test_transactional_serial_lookup_repository(db_session: Session):
    """
    Test direct repository method get_next_serial_transactional and IDGeneratorService helper.
    """
    company_repo.get_or_create_default(db_session, name="Acme Inc", code="AC")

    s1 = company_repo.get_next_serial_transactional(db_session, "AC", 2026)
    s2 = company_repo.get_next_serial_transactional(db_session, "AC", 2026)
    s3 = company_repo.get_next_serial_transactional(db_session, "AC", 2026)

    assert s1 == 1
    assert s2 == 2
    assert s3 == 3

    # Year 2027 should start at 1
    s_next_year = company_repo.get_next_serial_transactional(db_session, "AC", 2027)
    assert s_next_year == 1

    # Check lookup info schema
    lookup = IDGeneratorService.get_next_serial_info(db_session, "AC", 2026)
    assert lookup.company_code == "AC"
    assert lookup.year == 2026
    assert lookup.next_serial == 4
    assert lookup.formatted_serial == "0004"
