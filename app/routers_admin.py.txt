from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..auth_utils import hash_password, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    # admin default (se não existir)
    if not db.query(models.User).filter(models.User.email == "admin@payao.com").first():
        admin = models.User(email="admin@payao.com", hashed_password=hash_password("admin123"), role="admin")
        db.add(admin)

    # config INSS default
    if not db.query(models.PayrollConfig).first():
        cfg = models.PayrollConfig(inss_employee_rate=0.03, inss_employer_rate=0.08)
        db.add(cfg)

    # brackets exemplo (ajusta conforme legislação que definires)
    if db.query(models.TaxBracket).count() == 0:
        # Exemplo fictício: substitui pelos teus escalões oficiais
        brackets = [
            dict(min_amount=0,       max_amount=70000,  rate=0.00, deduction=0),
            dict(min_amount=70000,   max_amount=150000, rate=0.10, deduction=7000),
            dict(min_amount=150000,  max_amount=300000, rate=0.13, deduction=11500),
            dict(min_amount=300000,  max_amount=None,   rate=0.17, deduction=23500),
        ]
        for b in brackets:
            db.add(models.TaxBracket(**b))

    db.commit()
    return {"ok": True}

from ..schemas import StatsOut

@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), admin=Depends(require_role("admin"))):
    total_employees = db.query(models.Employee).count()
    last_payslips = db.query(models.Payslip).count()
    return StatsOut(total_employees=total_employees, last_payslips=last_payslips)

