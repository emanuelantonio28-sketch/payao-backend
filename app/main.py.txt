# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services_payroll import payroll_preview
from app.schemas import PayrollRequest

app = FastAPI(
    title="Sistema Payroll Angola",
    version="1.0.0",
    description="API para processamento salarial (IRT, INSS, etc.)",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "msg": "API Payroll Angola ativa"}

@app.post("/payroll/preview", tags=["Payroll"])
def payroll(data: PayrollRequest):
    return payroll_preview(
        data.gross_salary,
        data.taxable_allowances,
        data.non_taxable_allowances,
        data.other_deductions,
        data.irt_base_mode,
    )

app = FastAPI(
    title="Sistema Payroll Angola",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

