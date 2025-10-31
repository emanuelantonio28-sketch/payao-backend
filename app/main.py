from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .db import SessionLocal

app = FastAPI()

# Dependência (abre e fecha sessão do banco)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota de teste usando banco
@app.get("/")
def root(db: Session = Depends(get_db)):
    return {"msg": "Backend conectado ao Railway!"}
