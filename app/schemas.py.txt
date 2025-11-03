from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Employees ---
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    nif: Optional[str] = None
    base_salary: float

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    nif: Optional[str] = None
    base_salary: Optional[float] = None

class EmployeeOut(EmployeeBase):
    id: int
    class Config:
        from_attributes = True

# --- Payroll config / brackets ---
class PayrollConfigOut(BaseModel):
    id: int
    inss_employee_rate: float
    inss_employer_rate: float
    class Config:
        from_attributes = True

class TaxBracketIn(BaseModel):
    min_amount: float
    max_amount: Optional[float] = None
    rate: float
    deduction: float = 0.0

class TaxBracketOut(TaxBracketIn):
    id: int
    class Config:
        from_attributes = True

# --- Payslip ---
class PayslipPreviewIn(BaseModel):
    employee_id: int
    gross: float
    period: str  # "YYYY-MM"

class PayslipOut(BaseModel):
    employee_id: int
    period: str
    gross: float
    inss_emp: float
    irt: float
    net: float
    class Config:
        from_attributes = True

# --- Dashboard ---
class StatsOut(BaseModel):
    total_employees: int
    last_payslips: int

# --- Payroll Preview ---
class PayrollRequest(BaseModel):
    gross_salary: float
    taxable_allowances: float = 0
    non_taxable_allowances: float = 0
    other_deductions: float = 0
    irt_base_mode: str = "gross_minus_inss"  # ou "gross_only"

