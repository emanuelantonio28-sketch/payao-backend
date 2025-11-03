# app/calcs.py

from typing import Optional

# Tabela IRT (Angola) em vigor — valores em Kz
# Cada faixa contém: limite inferior (lower), limite superior (upper),
# taxa (rate) e parcela fixa acumulada (fixed).
IRT_BRACKETS = [
    {"lower": 0,         "upper": 100_000,    "rate": 0.00, "fixed": 0},
    {"lower": 100_000,   "upper": 150_000,    "rate": 0.13, "fixed": 0},
    {"lower": 150_000,   "upper": 200_000,    "rate": 0.16, "fixed": 12_500},
    {"lower": 200_000,   "upper": 300_000,    "rate": 0.18, "fixed": 31_250},
    {"lower": 300_000,   "upper": 500_000,    "rate": 0.19, "fixed": 49_250},
    {"lower": 500_000,   "upper": 1_000_000,  "rate": 0.21, "fixed": 187_249},
    {"lower": 1_000_000, "upper": 1_500_000,  "rate": 0.22, "fixed": 292_249},
    {"lower": 1_500_000, "upper": 2_000_000,  "rate": 0.23, "fixed": 402_249},
    {"lower": 2_000_000, "upper": 2_500_000,  "rate": 0.24, "fixed": 517_249},
    {"lower": 2_500_000, "upper": 5_000_000,  "rate": 0.25, "fixed": 1_117_249},
    {"lower": 5_000_000, "upper": 10_000_000, "rate": 0.25, "fixed": 1_942_249},
    {"lower": 10_000_000,"upper": None,       "rate": 0.25, "fixed": 2_342_248},
]

def calc_irt(gross_salary: float) -> int:
    """
    Calcula o IRT com base na tabela em vigor.
    Retorna o imposto arredondado ao Kz mais próximo (int).
    """
    salary = float(gross_salary)
    for b in IRT_BRACKETS:
        upper = b["upper"] if b["upper"] is not None else float("inf")
        if b["lower"] < salary <= upper:
            excess = max(0.0, salary - b["lower"])
            tax = b["fixed"] + b["rate"] * excess
            return int(round(tax))
    return 0
