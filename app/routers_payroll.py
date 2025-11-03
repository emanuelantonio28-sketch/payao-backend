from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..auth_utils import get_current_user, require_role
from ..services_payroll import preview_payslip
from decimal import Decimal

router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.post("/preview", response_model=schemas.PayslipOut)
def preview(data: schemas.PayslipPreviewIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        res = preview_payslip(db, data.employee_id, data.gross)
        return {
            "employee_id": res["employee_id"],
            "period": data.period,
            "gross": res["gross"],
            "inss_emp": res["inss_emp"],
            "irt": res["irt"],
            "net": res["net"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/config", response_model=schemas.PayrollConfigOut)
def set_config(inss_employee_rate: float, inss_employer_rate: float = 0.08, db: Session = Depends(get_db), admin=Depends(require_role("admin"))):
    cfg = db.query(models.PayrollConfig).first()
    if not cfg:
        cfg = models.PayrollConfig(inss_employee_rate=inss_employee_rate, inss_employer_rate=inss_employer_rate)
        db.add(cfg)
    else:
        cfg.inss_employee_rate = inss_employee_rate
        cfg.inss_employer_rate = inss_employer_rate
    db.commit(); db.refresh(cfg)
    return cfg

@router.post("/brackets", response_model=list[schemas.TaxBracketOut])
def upsert_brackets(items: list[schemas.TaxBracketIn], db: Session = Depends(get_db), admin=Depends(require_role("admin"))):
    # limpa e re-insere (simples)
    db.query(models.TaxBracket).delete()
    db.commit()
    recs = []
    for it in items:
        rec = models.TaxBracket(**it.model_dump())
        db.add(rec); db.flush()
        recs.append(rec)
    db.commit()
    for r in recs: db.refresh(r)
    return recs
