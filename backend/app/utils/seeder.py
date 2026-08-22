from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models import (
    User,
    UserRole,
    Employee,
    EmployeePrivateInfo,
    Skill,
    EmployeeSkill,
    Certification,
    Salary,
    Attendance,
    AttendanceStatus,
    LeaveType,
    LeaveBalance,
    TimeOffRequest,
    LeaveRequestStatus,
    Company,
    CompanySettings,
)
from backend.app.repositories.leave_repo import leave_repo


def seed_database(db: Session) -> None:
    """Seed initial data for demonstration and testing."""
    print("[*] Starting database seeding...")

    # 0. Companies
    default_companies = [
        ("HRMS Corp", "CE"),
        ("Apex Global Technologies", "AG"),
    ]
    for c_name, c_code in default_companies:
        existing_comp = db.query(Company).filter(Company.code == c_code).first()
        if not existing_comp:
            comp = Company(name=c_name, code=c_code)
            db.add(comp)
    db.flush()

    # 1. Company Settings
    settings = db.query(CompanySettings).first()
    if not settings:
        settings = CompanySettings(
            company_name="Apex Global Technologies",
            contact_email="hr@apextechnologies.com",
            contact_phone="+1 (555) 019-2834",
            address="450 Innovation Parkway, Suite 1000, Silicon Valley, CA",
        )
        db.add(settings)
        print("  [+] Created Company Settings")

    # 2. Leave Types
    default_leave_types = [
        ("Paid Time Off (PTO)", 18),
        ("Sick Leave", 10),
        ("Casual Leave", 8),
        ("Unpaid Leave", 30),
    ]
    created_lts = {}
    for name, alloc in default_leave_types:
        lt = db.query(LeaveType).filter(LeaveType.name == name).first()
        if not lt:
            lt = LeaveType(name=name, default_allocation=alloc)
            db.add(lt)
            db.flush()
        created_lts[name] = lt
    print(f"  [+] Created {len(created_lts)} Leave Types")

    # 3. Standard Skills
    skills_list = ["Python", "FastAPI", "React", "TypeScript", "SQLAlchemy", "PostgreSQL", "Docker", "HR Management"]
    created_skills = {}
    for s_name in skills_list:
        sk = db.query(Skill).filter(Skill.name == s_name).first()
        if not sk:
            sk = Skill(name=s_name)
            db.add(sk)
            db.flush()
        created_skills[s_name] = sk
    print(f"  [+] Created {len(created_skills)} Skills")

    # 4. Admin User (Standalone System Administrator)
    admin_user = db.query(User).filter(User.email == "admin@hrmscorp.com").first()
    if not admin_user:
        admin_user = User(
            login_id="OIAD2025001",
            email="admin@hrmscorp.com",
            password_hash=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
            must_change_password=False,
        )
        db.add(admin_user)
        print("  [+] Created Admin User (admin@hrmscorp.com / OIAD2025001 | Pass: Admin@123)")

    # 5. HR Officer Employee & User
    hr_emp = db.query(Employee).filter(Employee.email == "hr@hrmscorp.com").first()
    if not hr_emp:
        hr_emp = Employee(
            employee_code="EMP20250001",
            first_name="Sarah",
            last_name="Jenkins",
            email="hr@hrmscorp.com",
            phone="+1-555-0101",
            department="Human Resources",
            job_position="HR Manager",
            company="Apex Global Technologies",
            location="Headquarters",
            date_of_joining=date(2025, 1, 15),
            date_of_birth=date(1988, 5, 20),
            gender="Female",
            nationality="American",
            marital_status="Married",
            residing_address="120 Maple Street, San Jose, CA",
            personal_email="sarah.jenkins.personal@example.com",
            about="Experienced HR professional with 10+ years in talent acquisition and people operations.",
        )
        db.add(hr_emp)
        db.flush()

        hr_user = User(
            employee_id=hr_emp.id,
            login_id="OISJ2025001",
            email=hr_emp.email,
            password_hash=get_password_hash("Hr@123"),
            role=UserRole.HR_OFFICER,
            is_active=True,
            must_change_password=False,
        )
        db.add(hr_user)

        leave_repo.initialize_balances_for_employee(db, hr_emp.id, 2025)
        print("  [+] Created HR Officer (hr@hrmscorp.com / OISJ2025001 | Pass: Hr@123)")

    # 6. Standard Employee 1 (John Doe - Senior Software Engineer)
    emp1 = db.query(Employee).filter(Employee.email == "john.doe@hrmscorp.com").first()
    if not emp1:
        emp1 = Employee(
            employee_code="EMP20250002",
            first_name="John",
            last_name="Doe",
            email="john.doe@hrmscorp.com",
            phone="+1-555-0102",
            department="Engineering",
            job_position="Senior Software Engineer",
            company="Apex Global Technologies",
            location="Headquarters",
            date_of_joining=date(2025, 3, 1),
            date_of_birth=date(1993, 8, 14),
            gender="Male",
            nationality="American",
            marital_status="Single",
            residing_address="742 Evergreen Terrace, Springfield",
            personal_email="john.doe.personal@example.com",
            about="Full-stack engineer passionate about distributed systems and cloud architecture.",
        )
        db.add(emp1)
        db.flush()

        user1 = User(
            employee_id=emp1.id,
            login_id="OIJD2025001",
            email=emp1.email,
            password_hash=get_password_hash("Emp@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
            must_change_password=False,
        )
        db.add(user1)

        # Private info
        pinfo1 = EmployeePrivateInfo(
            employee_id=emp1.id,
            pan="ABCDE1234F",
            uan="100234567890",
            bank_account_number="987654321098",
            bank_name="Chase Manhattan Bank",
            ifsc="CHAS0001234",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+1-555-0199",
        )
        db.add(pinfo1)

        # Skills
        for sk_name in ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]:
            if sk_name in created_skills:
                db.add(EmployeeSkill(employee_id=emp1.id, skill_id=created_skills[sk_name].id))

        # Certifications
        cert1 = Certification(
            employee_id=emp1.id,
            name="AWS Certified Solutions Architect - Associate",
            issuing_organization="Amazon Web Services",
            issue_date=date(2024, 6, 15),
            expiry_date=date(2027, 6, 15),
        )
        db.add(cert1)

        # Salary Structure
        sal1 = Salary(
            employee_id=emp1.id,
            monthly_wage=Decimal("8500.00"),
            yearly_wage=Decimal("102000.00"),
            basic_salary=Decimal("4250.00"),
            hra=Decimal("2125.00"),
            standard_allowance=Decimal("850.00"),
            performance_bonus=Decimal("500.00"),
            leave_travel_allowance=Decimal("350.00"),
            fixed_allowance=Decimal("425.00"),
            professional_tax=Decimal("200.00"),
            employee_pf=Decimal("510.00"),
            employer_pf=Decimal("510.00"),
            effective_from=date(2025, 3, 1),
        )
        db.add(sal1)

        # Leave balances
        leave_repo.initialize_balances_for_employee(db, emp1.id, 2025)

        # Attendance sample records
        today = date.today()
        for i in range(1, 6):
            past_date = today - timedelta(days=i)
            if past_date.weekday() < 5:
                db.add(
                    Attendance(
                        employee_id=emp1.id,
                        attendance_date=past_date,
                        check_in=datetime.combine(past_date, datetime.min.time()).replace(hour=9, minute=0, tzinfo=timezone.utc),
                        check_out=datetime.combine(past_date, datetime.min.time()).replace(hour=17, minute=30, tzinfo=timezone.utc),
                        work_hours=Decimal("8.50"),
                        extra_hours=Decimal("0.50"),
                        status=AttendanceStatus.PRESENT,
                    )
                )

        print("  [+] Created Employee 1 (john.doe@hrmscorp.com / OIJD2025001 | Pass: Emp@123)")

    # 7. Standard Employee 2 (Alice Smith - Product Designer)
    emp2 = db.query(Employee).filter(Employee.email == "alice.smith@hrmscorp.com").first()
    if not emp2:
        emp2 = Employee(
            employee_code="EMP20250003",
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@hrmscorp.com",
            phone="+1-555-0103",
            department="Design",
            job_position="Senior Product Designer",
            company="Apex Global Technologies",
            location="Headquarters",
            date_of_joining=date(2025, 4, 1),
            date_of_birth=date(1995, 11, 3),
            gender="Female",
            nationality="American",
            marital_status="Single",
            residing_address="304 Pine Street, San Francisco, CA",
            personal_email="alice.smith.design@example.com",
            about="UI/UX designer crafting intuitive digital experiences and design systems.",
        )
        db.add(emp2)
        db.flush()

        user2 = User(
            employee_id=emp2.id,
            login_id="OIAS2025001",
            email=emp2.email,
            password_hash=get_password_hash("Emp@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
            must_change_password=False,
        )
        db.add(user2)

        pinfo2 = EmployeePrivateInfo(
            employee_id=emp2.id,
            pan="FGHIJ5678K",
            uan="100987654321",
            bank_account_number="123456789012",
            bank_name="Wells Fargo",
            ifsc="WFBI0004567",
            emergency_contact_name="Bob Smith",
            emergency_contact_phone="+1-555-0188",
        )
        db.add(pinfo2)

        # Salary
        sal2 = Salary(
            employee_id=emp2.id,
            monthly_wage=Decimal("7800.00"),
            yearly_wage=Decimal("93600.00"),
            basic_salary=Decimal("3900.00"),
            hra=Decimal("1950.00"),
            standard_allowance=Decimal("780.00"),
            performance_bonus=Decimal("400.00"),
            leave_travel_allowance=Decimal("370.00"),
            fixed_allowance=Decimal("400.00"),
            professional_tax=Decimal("200.00"),
            employee_pf=Decimal("468.00"),
            employer_pf=Decimal("468.00"),
            effective_from=date(2025, 4, 1),
        )
        db.add(sal2)

        leave_repo.initialize_balances_for_employee(db, emp2.id, 2025)
        print("  [+] Created Employee 2 (alice.smith@hrmscorp.com / OIAS2025001 | Pass: Emp@123)")

    db.commit()
    print("[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()
