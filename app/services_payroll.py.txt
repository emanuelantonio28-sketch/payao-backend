# app/services_payroll.py
# ------------------------------------------------------------
# Serviço de cálculo de Payroll (Angola)
# - INSS colaborador (default 3%)
# - INSS entidade patronal (default 8%)
# - IRT com base na tabela em vigor (app.calcs.calc_irt)
# - Possibilidade de aplicar IRT sobre o bruto ou sobre o
#   bruto menos INSS do colaborador (mais comum)
# - Estruturas limpas para integrar com FastAPI
# ------------------------------------------------------------

from dataclasses import dataclass, asdict
from typing import Literal, Dict

from app.calcs import calc_irt

# Taxas padrão (ajustáveis se for necessário)
EMPLOYEE_INSS_RATE = 0.03  # 3% colaborador
EMPLOYER_INSS_RATE = 0.08  # 8% entidade

# Caso haja tecto (plafond) de INSS, podes definir aqui (None = sem tecto)
INSS_EMPLOYEE_CAP = None  # ex.: 500_000  -> min(valor calculado, 500_000)
INSS_EMPLOYER_CAP = None


# -----------------------------
# Helpers
# -----------------------------
def _round_kz(value: float) -> int:
    """Arredonda para Kz inteiros (convenção nos recibos)."""
    return int(round(float(value)))


def _calc_inss(base: float, rate: float, cap: float | None = None) -> int:
    """Calcula INSS sobre uma base, respeitando um tecto (cap) se existir."""
    amount = base * rate
    if cap is not None:
        amount = min(amount, cap)
    return _round_kz(amount)


# -----------------------------
# Input / Output
# -----------------------------
@dataclass
class PayrollInput:
    """
    Parâmetros do cálculo.

    gross_salary: salário base/bruto tributável
    taxable_allowances: subsídios/abonos tributáveis (ex.: prémios)
    non_taxable_allowances: abonos não tributáveis (ex.: subsídio de alimentação)
    other_deductions: outras deduções (adiant., faltas, etc.)
    irt_base_mode:
        - "gross_minus_inss": IRT calculado sobre (bruto + subsídios tributáveis - INSS colaborador)
        - "gross": IRT calculado sobre (bruto + subsídios tributáveis)
    """
    gross_salary: float
    taxable_allowances: float = 0.0
    non_taxable_allowances: float = 0.0
    other_deductions: float = 0.0
    irt_base_mode: Literal["gross_minus_inss", "gross"] = "gross_minus_inss"

    # Possibilidade de personalizar taxas por cálculo, se precisares
    employee_inss_rate: float = EMPLOYEE_INSS_RATE
    employer_inss_rate: float = EMPLOYER_INSS_RATE


@dataclass
class PayrollResult:
    # Bases
    gross_salary: int
    taxable_allowances: int
    non_taxable_allowances: int

    # Contribuições
    inss_employee: int
    inss_employer: int

    # Imposto
    irt_base: int
    irt: int

    # Deduções
    other_deductions: int

    # Totais
    total_cost_employer: int  # custo total para a empresa (bruto + inss entidade + NT)
    net_salary: int           # salário líquido a pagar ao colaborador

    # Auxiliar: conversão para dicionário (bom para FastAPI)
    def dict(self) -> Dict:
        return asdict(self)


# -----------------------------
# Serviço principal de Payroll
# -----------------------------
def build_payroll(input_data: PayrollInput) -> PayrollResult:
    """
    Constrói o cálculo completo do payroll.
    Retorna PayrollResult com todos os campos arredondados a Kz inteiros.
    """
    # Bases
    gross = float(input_data.gross_salary)
    tx_allow = float(input_data.taxable_allowances or 0.0)
    nontx_allow = float(input_data.non_taxable_allowances or 0.0)
    others = float(input_data.other_deductions or 0.0)

    # Base tributável “bruta”
    taxable_gross = gross + tx_allow

    # INSS
    inss_employee = _calc_inss(
        base=taxable_gross,
        rate=input_data.employee_inss_rate,
        cap=INSS_EMPLOYEE_CAP,
    )
    inss_employer = _calc_inss(
        base=taxable_gross,
        rate=input_data.employer_inss_rate,
        cap=INSS_EMPLOYER_CAP,
    )

    # Base de IRT
    if input_data.irt_base_mode == "gross_minus_inss":
        irt_base_val = taxable_gross - inss_employee
    else:  # "gross"
        irt_base_val = taxable_gross

    irt_base_val = max(0.0, irt_base_val)
    irt_value = _round_kz(calc_irt(irt_base_val))

    # Líquido (o que entra no bolso)
    net = (
        gross                      # salário base
        + tx_allow                 # + subsídios tributáveis
        + nontx_allow              # + subsídios não tributáveis
        - inss_employee            # - INSS colaborador
        - irt_value                # - IRT
        - others                   # - outras deduções
    )

    # Custo total para a empresa
    total_cost = (
        gross
        + tx_allow
        + nontx_allow
        + inss_employer
    )

    return PayrollResult(
        gross_salary=_round_kz(gross),
        taxable_allowances=_round_kz(tx_allow),
        non_taxable_allowances=_round_kz(nontx_allow),
        inss_employee=_round_kz(inss_employee),
        inss_employer=_round_kz(inss_employer),
        irt_base=_round_kz(irt_base_val),
        irt=_round_kz(irt_value),
        other_deductions=_round_kz(others),
        total_cost_employer=_round_kz(total_cost),
        net_salary=_round_kz(net),
    )


# -----------------------------
# Atalho simples (ex.: para Swagger “preview”)
# -----------------------------
def preview_payroll(
    gross_salary: float,
    taxable_allowances: float = 0.0,
    non_taxable_allowances: float = 0.0,
    other_deductions: float = 0.0,
    irt_base_mode: Literal["gross_minus_inss", "gross"] = "gross_minus_inss",
) -> Dict:
    """
    Função “curta” para chamar directamente num endpoint de preview.
    """
    pr = build_payroll(
        PayrollInput(
            gross_salary=gross_salary,
            taxable_allowances=taxable_allowances,
            non_taxable_allowances=non_taxable_allowances,
            other_deductions=other_deductions,
            irt_base_mode=irt_base_mode,
        )
    )
    return pr.dict()

