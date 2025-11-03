from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..auth_utils import get_current_user, require_role

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("", response_model=schemas.EmployeeOut)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    if db.query(models.Employee).filter(models.Employee.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email já existe")
    emp = models.Employee(**payload.model_dump())
    db.add(emp); db.commit(); db.refresh(emp)
    return emp

@router.get("", response_model=list[schemas.EmployeeOut])
def list_employees(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Employee).order_by(models.Employee.id.desc()).all()

@router.get("/{emp_id}", response_model=schemas.EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Employee).get(emp_id)
    if not emp: raise HTTPException(status_code=404, detail="Não encontrado")
    return emp

@router.put("/{emp_id}", response_model=schemas.EmployeeOut)
def update_employee(emp_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    emp = db.query(models.Employee).get(emp_id)
    if not emp: raise HTTPException(status_code=404, detail="Não encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(emp, k, v)
    db.commit(); db.refresh(emp)
    return emp

@router.delete("/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    emp = db.query(models.Employee).get(emp_id)
    if not emp: raise HTTPException(status_code=404, detail="Não encontrado")
    db.delete(emp); db.commit()
    return {"ok": True}

