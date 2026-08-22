import re
from typing import Dict, Any, Optional
from datetime import datetime


def clean_string(val: Optional[str]) -> str:
    """Trim string or return empty string."""
    return (val or "").strip()


def validate_email_format(email: str) -> bool:
    """Validate RFC-compliant email string format."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_phone_format(phone: str) -> bool:
    """Validate international/standard phone number format (7 to 15 digits)."""
    if not phone:
        return False
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def generate_login_id(first_name: str, last_name: str, joining_date_str: str, sequence_no: int) -> str:
    """
    Generate Login ID in format:
    OI[first 2 chars of first name][first 2 chars of last name][joining year][4-digit sequence]
    Example: Kushal Sharma joining in 2025 sequence 1 -> OIKUSH20250001
    """
    f_clean = re.sub(r"[^A-Za-z]", "", first_name or "EM").upper()
    l_clean = re.sub(r"[^A-Za-z]", "", last_name or "PL").upper()

    f_prefix = (f_clean + "XX")[:2]
    l_prefix = (l_clean + "XX")[:2]

    try:
        if joining_date_str:
            # Handles YYYY-MM-DD or DD/MM/YYYY
            if "-" in joining_date_str:
                year = joining_date_str.split("-")[0]
            elif "/" in joining_date_str:
                year = joining_date_str.split("/")[-1]
            else:
                year = str(datetime.now().year)
        else:
            year = str(datetime.now().year)
    except Exception:
        year = str(datetime.now().year)

    if len(year) != 4 or not year.isdigit():
        year = str(datetime.now().year)

    seq_str = f"{sequence_no:04d}"
    return f"OI{f_prefix}{l_prefix}{year}{seq_str}"


def calculate_salary_breakdown(monthly_wage: float) -> Dict[str, Any]:
    """
    Compute structured salary breakdown according to HRMS specifications:
    - Monthly Wage
    - Yearly Wage (Monthly * 12)
    - Basic Salary (50% of Wage)
    - House Rent Allowance (HRA: 50% of Basic)
    - Standard Allowance (Fixed ₹4,167 or remaining balance)
    - Performance Bonus (8.33% of Basic)
    - Leave Travel Allowance (LTA: 8.333% of Basic)
    - Fixed Allowance (Remaining balance so total sum matches Monthly Wage)
    - Provident Fund / PF (12% of Basic)
    - Professional Tax / PT (Fixed ₹200)
    - Net In-hand Monthly
    """
    wage = max(0.0, float(monthly_wage or 0.0))
    yearly_wage = wage * 12.0

    if wage == 0:
        return {
            "monthly_wage": 0.0,
            "yearly_wage": 0.0,
            "basic_salary": 0.0,
            "hra": 0.0,
            "standard_allowance": 0.0,
            "performance_bonus": 0.0,
            "lta": 0.0,
            "fixed_allowance": 0.0,
            "pf_deduction": 0.0,
            "professional_tax": 0.0,
            "total_deductions": 0.0,
            "net_monthly": 0.0,
            "net_yearly": 0.0,
        }

    # Basic is 50% of monthly wage
    basic = round(wage * 0.50, 2)

    # HRA is 50% of Basic salary
    hra = round(basic * 0.50, 2)

    # Performance bonus is 8.33% of Basic
    performance_bonus = round(basic * 0.0833, 2)

    # Leave travel allowance is 8.333% of Basic
    lta = round(basic * 0.08333, 2)

    # Standard allowance default 4167 (or remaining if wage is lower)
    temp_sum = basic + hra + performance_bonus + lta
    standard_allowance = 4167.0 if wage >= (temp_sum + 4167.0) else max(0.0, round(wage - temp_sum, 2))

    # Fixed allowance is the remaining portion so sum equals monthly wage exactly
    current_components_sum = basic + hra + performance_bonus + lta + standard_allowance
    fixed_allowance = max(0.0, round(wage - current_components_sum, 2))

    # Deductions
    # PF is 12% of Basic
    pf_deduction = round(basic * 0.12, 2)
    # Professional Tax is fixed ₹200
    professional_tax = 200.0 if wage > 15000 else 0.0

    total_deductions = round(pf_deduction + professional_tax, 2)
    net_monthly = max(0.0, round(wage - total_deductions, 2))
    net_yearly = round(net_monthly * 12.0, 2)

    return {
        "monthly_wage": wage,
        "yearly_wage": round(yearly_wage, 2),
        "basic_salary": basic,
        "hra": hra,
        "standard_allowance": standard_allowance,
        "performance_bonus": performance_bonus,
        "lta": lta,
        "fixed_allowance": fixed_allowance,
        "pf_deduction": pf_deduction,
        "professional_tax": professional_tax,
        "total_deductions": total_deductions,
        "net_monthly": net_monthly,
        "net_yearly": net_yearly,
    }
