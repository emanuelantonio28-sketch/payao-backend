from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..auth_utils import hash_password, verify_password, create_token, get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=schemas.Token)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db), admin=Depends(require_role("admin"))):
    # apenas admin cria utilizadores
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email já existe")
    user = models.User(email=user_in.email, hashed_password=hash_password(user_in.password), role=user_in.role)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user.email)}

@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    return {"access_token": create_token(user.email)}
