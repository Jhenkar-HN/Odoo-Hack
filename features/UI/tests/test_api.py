"""
Automated Integration and Functional Tests for HRMS Application (with Auth & Leaves)
"""
import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db_connection
from app.models import EmployeeCreate, EmployeeUpdate, SkillItem, CertificationItem
from app import crud
from app.auth import hash_password, verify_password
from app.utils import validate_email_format, validate_phone_format, generate_login_id, calculate_salary_breakdown


class TestHRMSBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize DB
        init_db()

    def test_auth_password_hashing(self):
        """Test PBKDF2 password hashing and verification."""
        pwd = "SecretPassword123!"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_auth_user_logins(self):
        """Test HR and Employee logins against database."""
        # 1. HR Admin login
        hr_user = crud.authenticate_user("admin@hrms.com", "admin123")
        self.assertIsNotNone(hr_user)
        self.assertEqual(hr_user["role"], "hr")

        # 2. Employee login with work email
        emp_user = crud.authenticate_user("aarav.sharma@odooindia.com", "employee123")
        self.assertIsNotNone(emp_user)
        self.assertEqual(emp_user["role"], "employee")
        self.assertIsNotNone(emp_user["employee_id"])

        # 3. Invalid credentials
        invalid_user = crud.authenticate_user("admin@hrms.com", "wrong_password")
        self.assertIsNone(invalid_user)

    def test_utils_login_id_generation(self):
        """Test Login ID generation format: OI[First2][Last2][Year][0001]"""
        login_id = generate_login_id("Kushal", "Sharma", "2025-08-22", 1)
        self.assertEqual(login_id, "OIKUSH20250001")

        login_id_2 = generate_login_id("Dev", "Patel", "2024-01-15", 42)
        self.assertEqual(login_id_2, "OIDEPA20240042")

    def test_utils_salary_breakdown(self):
        """Test salary calculations according to HRMS specifications."""
        wage = 50000.0
        breakdown = calculate_salary_breakdown(wage)
        self.assertEqual(breakdown["monthly_wage"], 50000.0)
        self.assertEqual(breakdown["yearly_wage"], 600000.0)
        self.assertEqual(breakdown["basic_salary"], 25000.0)
        self.assertEqual(breakdown["hra"], 12500.0)
        self.assertEqual(breakdown["pf_deduction"], 3000.0)
        self.assertEqual(breakdown["professional_tax"], 200.0)
        self.assertGreater(breakdown["net_monthly"], 0)

        total_components = (
            breakdown["basic_salary"] +
            breakdown["hra"] +
            breakdown["standard_allowance"] +
            breakdown["performance_bonus"] +
            breakdown["lta"] +
            breakdown["fixed_allowance"]
        )
        self.assertAlmostEqual(total_components, wage, places=2)

    def test_employee_crud_and_user_provisioning(self):
        """Test employee creation automatically provisions user credentials."""
        unique_email = f"lead.eng.{os.urandom(4).hex()}@testcorp.com"

        new_emp_in = EmployeeCreate(
            first_name="Neha",
            last_name="Kapoor",
            work_email=unique_email,
            personal_email="neha.kapoor@gmail.com",
            phone="+91 91234 55667",
            department="Engineering",
            job_position="Engineering Manager",
            date_of_joining="2026-02-01",
            monthly_wage=110000.0,
            skills=[SkillItem(name="Team Leadership", level="Expert")]
        )

        emp = crud.create_employee(new_emp_in)
        self.assertIsNotNone(emp["id"])
        emp_id = emp["id"]

        # Check that user account was automatically created
        user_account = crud.authenticate_user(unique_email, "Welcome@123")
        self.assertIsNotNone(user_account)
        self.assertEqual(user_account["employee_id"], emp_id)
        self.assertEqual(user_account["role"], "employee")

        # Cleanup
        crud.delete_employee(emp_id, hard_delete=True)

    def test_leave_application_lifecycle(self):
        """Test employee applying for leave and HR reviewing it."""
        # 1. Get an existing employee
        employees, _ = crud.get_employees(limit=1)
        self.assertGreater(len(employees), 0)
        emp_id = employees[0]["id"]

        # 2. Employee applies for leave
        leave = crud.apply_leave_request(
            emp_id=emp_id,
            leave_type="Sick Leave",
            start_date="2026-09-01",
            end_date="2026-09-02",
            days_count=2.0,
            reason="Medical recovery"
        )
        self.assertIsNotNone(leave["id"])
        self.assertEqual(leave["status"], "pending")

        leave_id = leave["id"]

        # 3. Fetch employee's leaves
        my_leaves = crud.get_employee_leaves(emp_id)
        self.assertTrue(any(l["id"] == leave_id for l in my_leaves))

        # 4. HR approves the leave
        updated_leave = crud.update_leave_status(leave_id, "approved", "HR Admin")
        self.assertEqual(updated_leave["status"], "approved")

        # 5. Verify employee attendance status is set to on_leave
        emp = crud.get_employee_by_id(emp_id)
        self.assertEqual(emp["attendance_status"], "on_leave")


if __name__ == "__main__":
    unittest.main()
