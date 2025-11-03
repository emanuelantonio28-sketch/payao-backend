from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, func, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

# --- Users / Auth ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "admin" | "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Employees ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nif = Column(String(50), unique=True, index=True, nullable=True)
    base_salary = Column(Numeric(12,2), nullable=False, default=0)

# --- Payroll config (parametrizável) ---
class PayrollConfig(Base):
    __tablename__ = "payroll_config"
    id = Column(Integer, primary_key=True)
    inss_employee_rate = Column(Numeric(5,4), nullable=False, default=0.03)  # 3% colaborador
    inss_employer_rate = Column(Numeric(5,4), nullable=False, default=0.08)  # 8% entidade

class TaxBracket(Base):
    __tablename__ = "tax_brackets"
    id = Column(Integer, primary_key=True)
    min_amount = Column(Numeric(12,2), nullable=False)
    max_amount = Column(Numeric(12,2), nullable=True)  # None = sem teto
    rate = Column(Numeric(5,4), nullable=False)        # ex: 0.10 = 10%
    deduction = Column(Numeric(12,2), nullable=False, default=0)  # parcela a deduzir

# --- (opcional) guarda histórico de processamento ---
class Payslip(Base):
    __tablename__ = "payslips"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    period = Column(String(7), nullable=False)  # "2025-11"
    gross = Column(Numeric(12,2), nullable=False)
    inss_emp = Column(Numeric(12,2), nullable=False)
    irt = Column(Numeric(12,2), nullable=False)
    net = Column(Numeric(12,2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
