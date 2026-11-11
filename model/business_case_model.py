"""Financial model, Excel workbook builder, sensitivity engine, and chart generator
for the NoiseFit Sync Center Business Case.

Single source of truth: model/assumptions.yaml
Outputs:
  - model/business_case_model.xlsx (4 sheets: Assumptions, Calculations, Scenarios, Summary)
  - docs/images/scenario_comparison.png
  - docs/images/cashflow_projection.png
  - docs/images/sensitivity_tornado.png
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure matplotlib has a writable config/cache directory in restricted environments
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "mpl_noisefit"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import yaml
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


REPO_ROOT = Path(__file__).resolve().parent.parent
ASSUMPTIONS_PATH = REPO_ROOT / "model" / "assumptions.yaml"
WORKBOOK_PATH = REPO_ROOT / "model" / "business_case_model.xlsx"
IMAGES_DIR = REPO_ROOT / "docs" / "images"

# Color palette (Consulting Navy + Teal + Coral + Slate)
NAVY = "#0F2744"
TEAL = "#0D9488"
SLATE = "#475569"
CORAL = "#DC2626"
AMBER = "#D97706"
EMERALD = "#059669"
LIGHT_BG = "#F8FAFC"


def load_assumptions(path: Path = ASSUMPTIONS_PATH) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Load YAML assumptions and return (metadata, ordered parameter list, id->param map)."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    params = data["parameters"]
    by_id = {p["id"]: p for p in params}
    return data["metadata"], params, by_id


def extract_scenario_inputs(params: List[Dict[str, Any]], scenario: str) -> Dict[str, float]:
    """Extract scalar parameter values for 'low', 'base', or 'high' scenario."""
    if scenario not in ("low", "base", "high"):
        raise ValueError(f"Unknown scenario: {scenario}")
    return {p["id"]: float(p[scenario]) for p in params}


def compute_market_sizing(by_id: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compute top-down and bottom-up TAM / SAM / SOM metrics (all assumptions explicit)."""
    smartphones_m = float(by_id["india_active_smartphones_m"]["base"])
    internet_m = float(by_id["india_active_internet_users_m"]["base"])
    sw_cy24_m = float(by_id["india_smartwatch_shipments_cy24_m"]["base"])
    sw_cy25_m = float(by_id["india_smartwatch_shipments_cy25_m"]["base"])
    noise_share = float(by_id["noise_smartwatch_share_cy25"]["base"])
    rev_cr = float(by_id["noise_fy25_revenue_cr"]["base"])
    som_low = float(by_id["active_noisefit_users_m"]["low"])
    som_base = float(by_id["active_noisefit_users_m"]["base"])
    som_high = float(by_id["active_noisefit_users_m"]["high"])

    # Top-down TAM: 25% of India's 740M active smartphone base interested/adopting wearable/fitness apps [ASSUMPTION]
    tam_users_m = smartphones_m * 0.25
    # SAM: 2-year India smartwatch shipment cohort (CY24 + CY25 = 63.9M) x 0.94 net active/tail adjustment [ASSUMPTION] -> ~60M
    sw_2yr_m = sw_cy24_m + sw_cy25_m
    sam_users_m = 60.0  # Explicitly reconciled from 63.9M 2-yr shipments + residual 2023 cohort net of dormancy [ASSUMPTION]

    # Bottom-up Noise smartwatch shipments
    noise_cy24_units_m = sw_cy24_m * 0.27  # Counterpoint CY24 Noise share = 27%
    noise_cy25_units_m = sw_cy25_m * noise_share  # IDC CY25 Noise share = 26.6% -> 7.6874M
    noise_2yr_units_m = noise_cy24_units_m + noise_cy25_units_m
    implied_rev_per_watch_inr = (rev_cr * 1e7) / (noise_cy25_units_m * 1e6)

    return {
        "india_smartphones_m": smartphones_m,
        "india_internet_m": internet_m,
        "tam_users_m": tam_users_m,
        "sw_2yr_shipments_m": sw_2yr_m,
        "sam_users_m": sam_users_m,
        "som_low_m": som_low,
        "som_base_m": som_base,
        "som_high_m": som_high,
        "noise_cy24_units_m": noise_cy24_units_m,
        "noise_cy25_units_m": noise_cy25_units_m,
        "noise_2yr_units_m": noise_2yr_units_m,
        "implied_rev_per_watch_inr": implied_rev_per_watch_inr,
    }


def compute_scenario(inp: Dict[str, float]) -> Dict[str, Any]:
    """Evaluate complete 3-year cash flow model for a single input dictionary (units: INR Lakhs)."""
    g = inp["annual_base_growth_rate"]
    r = inp["discount_rate"]
    y1_real = inp["rollout_y1_realization"]
    prev = inp["annual_sync_failure_prevalence"]

    # Shipments & active user trajectory (Y1, Y2, Y3)
    ship_y1 = inp["india_smartwatch_shipments_cy25_m"] * 1_000_000.0 * inp["noise_smartwatch_share_cy25"]
    users_y1 = inp["active_noisefit_users_m"] * 1_000_000.0
    eval_y1 = inp["prospective_store_evaluators_m"] * 1_000_000.0

    growth_mults = [1.0, 1.0 + g, (1.0 + g) ** 2]
    real_mults = [y1_real, 1.0, 1.0]

    # Yearly breakdown lists (index 0=Y1, 1=Y2, 2=Y3)
    d1_list, d2_list, d3_list, d4_list = [], [], [], []
    failure_users_list, deflected_tickets_list, prevented_rmas_list, upgrades_list = [], [], [], []

    for yr_idx in range(3):
        gm = growth_mults[yr_idx]
        rm = real_mults[yr_idx]

        users_y = users_y1 * gm
        fail_y = users_y * prev
        ship_y = ship_y1 * gm
        eval_y = eval_y1 * gm

        # Driver 1: Retention -> repeat smartwatch upgrades (realized factor applied to incremental uplift)
        retained_y = fail_y * inp["retention_lift_annual"] * rm
        upgrades_y = retained_y * inp["repeat_upgrade_propensity"]
        d1_y = (upgrades_y * inp["hw_contribution_margin_inr"]) / 100_000.0

        # Driver 2: Rating protection -> organic evaluator CVR lift
        conv_y = eval_y * inp["baseline_evaluator_cvr"] * inp["rating_relative_cvr_lift"] * rm
        d2_y = (conv_y * inp["hw_contribution_margin_inr"]) / 100_000.0

        # Driver 3: Support ticket deflection
        base_tickets_y = fail_y * inp["ticket_escalation_rate"]
        deflected_y = base_tickets_y * inp["ticket_deflection_rate"] * rm
        d3_y = (deflected_y * inp["support_cost_per_ticket_inr"]) / 100_000.0

        # Driver 4: Prevented false hardware returns / RMAs
        raw_rmas_y = ship_y * inp["sync_attributed_rma_rate"]
        prev_rmas_y = raw_rmas_y * inp["rma_prevention_share"] * rm
        d4_y = (prev_rmas_y * inp["avoided_cost_per_rma_inr"]) / 100_000.0

        d1_list.append(d1_y)
        d2_list.append(d2_y)
        d3_list.append(d3_y)
        d4_list.append(d4_y)
        failure_users_list.append(fail_y)
        upgrades_list.append(upgrades_y)
        deflected_tickets_list.append(deflected_y)
        prevented_rmas_list.append(prev_rmas_y)

    # Costs
    build_pw = (
        inp["pw_pm"]
        + inp["pw_android"]
        + inp["pw_ios"]
        + inp["pw_firmware_ble"]
        + inp["pw_ux_design"]
        + inp["pw_qa_oem_lab"]
        + inp["pw_data_analytics"]
        + inp["pw_support_legal"]
    )
    upfront_labour = build_pw * inp["loaded_cost_per_pw_lakhs"]
    non_labour_setup = inp["non_labour_setup_lakhs"]
    y0_investment = upfront_labour + non_labour_setup

    annual_maint_labour = inp["annual_maint_pw"] * inp["loaded_cost_per_pw_lakhs"]
    annual_infra = inp["annual_infra_compliance_lakhs"]
    annual_opex = annual_maint_labour + annual_infra

    gross_by_year = [d1_list[i] + d2_list[i] + d3_list[i] + d4_list[i] for i in range(3)]
    net_by_year = [gross_by_year[i] - annual_opex for i in range(3)]
    cash_flows = [-y0_investment] + net_by_year

    cum_cf = []
    running = 0.0
    for cf in cash_flows:
        running += cf
        cum_cf.append(running)

    total_gross = sum(gross_by_year)
    total_opex = 3.0 * annual_opex
    total_costs = y0_investment + total_opex
    net_benefit_3yr = total_gross - total_costs  # Equals cum_cf[3]

    lifecycle_roi = (total_gross - total_costs) / total_costs
    capex_roi = net_benefit_3yr / y0_investment

    # Standard discounted NPV with time-0 outflow at t=0
    npv = cash_flows[0] + sum(net_by_year[i] / ((1.0 + r) ** (i + 1)) for i in range(3))

    # Payback period in months (linear intra-year interpolation; None if unrecovered in 36 months)
    payback_months: float | None = None
    if cum_cf[1] >= 0 and cash_flows[1] > 0:
        payback_months = (-cash_flows[0] / cash_flows[1]) * 12.0
    elif cum_cf[2] >= 0 and cash_flows[2] > 0:
        payback_months = 12.0 + (-cum_cf[1] / cash_flows[2]) * 12.0
    elif cum_cf[3] >= 0 and cash_flows[3] > 0:
        payback_months = 24.0 + (-cum_cf[2] / cash_flows[3]) * 12.0

    # Present values of each benefit driver & OpEx for transparent sensitivity decomposition
    pv_d1 = sum(d1_list[i] / ((1.0 + r) ** (i + 1)) for i in range(3))
    pv_d2 = sum(d2_list[i] / ((1.0 + r) ** (i + 1)) for i in range(3))
    pv_d3 = sum(d3_list[i] / ((1.0 + r) ** (i + 1)) for i in range(3))
    pv_d4 = sum(d4_list[i] / ((1.0 + r) ** (i + 1)) for i in range(3))
    pv_opex = sum(annual_opex / ((1.0 + r) ** (i + 1)) for i in range(3))

    return {
        "ship_y1": ship_y1,
        "users_y1": users_y1,
        "failure_users": failure_users_list,
        "upgrades": upgrades_list,
        "deflected_tickets": deflected_tickets_list,
        "prevented_rmas": prevented_rmas_list,
        "d1_yearly": d1_list,
        "d2_yearly": d2_list,
        "d3_yearly": d3_list,
        "d4_yearly": d4_list,
        "d1_total": sum(d1_list),
        "d2_total": sum(d2_list),
        "d3_total": sum(d3_list),
        "d4_total": sum(d4_list),
        "pv_d1": pv_d1,
        "pv_d2": pv_d2,
        "pv_d3": pv_d3,
        "pv_d4": pv_d4,
        "pv_opex": pv_opex,
        "build_pw": build_pw,
        "upfront_labour": upfront_labour,
        "non_labour_setup": non_labour_setup,
        "y0_investment": y0_investment,
        "annual_maint_labour": annual_maint_labour,
        "annual_infra": annual_infra,
        "annual_opex": annual_opex,
        "gross_by_year": gross_by_year,
        "net_by_year": net_by_year,
        "cash_flows": cash_flows,
        "cum_cf": cum_cf,
        "total_gross": total_gross,
        "total_opex": total_opex,
        "total_costs": total_costs,
        "net_benefit_3yr": net_benefit_3yr,
        "lifecycle_roi": lifecycle_roi,
        "capex_roi": capex_roi,
        "discount_rate": r,
        "npv": npv,
        "payback_months": payback_months,
    }


SENSITIVITY_SPECS = [
    ("annual_sync_failure_prevalence", "Annual Sync Failure Prevalence"),
    ("ticket_deflection_rate", "Support Ticket Deflection Rate"),
    ("active_noisefit_users_m", "Active NoiseFit User Base (M)"),
    ("ticket_escalation_rate", "Failure-to-Ticket Escalation Rate"),
    ("support_cost_per_ticket_inr", "Support Cost per Ticket (INR)"),
    ("retention_lift_annual", "Annual Retention Lift (Failure Users)"),
    ("hw_contribution_margin_inr", "Hardware Contribution Margin (INR)"),
    ("rma_prevention_share", "Preventable False RMA Share"),
    ("rollout_y1_realization", "Year 1 Rollout Realization Factor"),
    ("loaded_cost_per_pw_lakhs", "Blended Cost per Person-Week"),
    ("discount_rate", "Discount Rate (WACC)"),
]


def compute_sensitivity(params: List[Dict[str, Any]], by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run exact 1-way sensitivity on Base NPV across each parameter's Low-to-High bounds."""
    base_inp = extract_scenario_inputs(params, "base")
    base_res = compute_scenario(base_inp)
    base_npv = base_res["npv"]

    rows = []
    for pid, short_label in SENSITIVITY_SPECS:
        p = by_id[pid]
        low_inp = dict(base_inp)
        high_inp = dict(base_inp)
        low_inp[pid] = float(p["low"])
        high_inp[pid] = float(p["high"])

        npv_at_low = compute_scenario(low_inp)["npv"]
        npv_at_high = compute_scenario(high_inp)["npv"]
        swing = abs(npv_at_high - npv_at_low)

        rows.append(
            {
                "id": pid,
                "label": short_label,
                "unit": p["unit"],
                "low_val": float(p["low"]),
                "base_val": float(p["base"]),
                "high_val": float(p["high"]),
                "npv_at_low": npv_at_low,
                "npv_at_high": npv_at_high,
                "delta_low": npv_at_low - base_npv,
                "delta_high": npv_at_high - base_npv,
                "swing": swing,
            }
        )

    rows.sort(key=lambda x: x["swing"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# OPENPYXL WORKBOOK BUILDER (ALL CALCULATIONS & SUMMARY USE REAL FORMULAS)
# ---------------------------------------------------------------------------

def _thin_border() -> Border:
    side = Side(border_style="thin", color="CBD5E1")
    return Border(left=side, right=side, top=side, bottom=side)


def _total_border() -> Border:
    thin = Side(border_style="thin", color="94A3B8")
    thick = Side(border_style="double", color="0F2744")
    return Border(top=thin, bottom=thick, left=thin, right=thin)


def _style_header(ws, row_idx: int, col_start: int, col_end: int) -> None:
    fill = PatternFill("solid", fgColor="0F2744")
    font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for c in range(col_start, col_end + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row_idx].height = 26


def _style_section(ws, row_idx: int, col_start: int, col_end: int, title: str) -> None:
    fill = PatternFill("solid", fgColor="E2E8F0")
    font = Font(name="Calibri", size=10, bold=True, color="0F2744")
    ws.cell(row=row_idx, column=col_start, value=title)
    for c in range(col_start, col_end + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = fill
        cell.font = font
        cell.border = _thin_border()
    ws.row_dimensions[row_idx].height = 20


def _num_fmt_for_unit(unit: str) -> str:
    if unit == "%":
        return "0.0%"
    if "INR Lakhs" in unit:
        return "₹#,##0.00"
    if unit == "INR":
        return "₹#,##0"
    if "Person-Weeks" in unit or "Stars" in unit or unit.startswith("M "):
        return "#,##0.0"
    return "#,##0.00"


def build_workbook(
    metadata: Dict[str, Any],
    params: List[Dict[str, Any]],
    by_id: Dict[str, Dict[str, Any]],
    output_path: Path = WORKBOOK_PATH,
) -> Path:
    """Create business_case_model.xlsx with dynamic formulas across all 4 required sheets."""
    wb = openpyxl.Workbook()
    # Rename default sheet
    ws_assump = wb.active
    ws_assump.title = "Assumptions"
    ws_calc = wb.create_sheet("Calculations")
    ws_scen = wb.create_sheet("Scenarios")
    ws_sum = wb.create_sheet("Summary")

    font_title = Font(name="Calibri", size=14, bold=True, color="0F2744")
    font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
    font_input = Font(name="Calibri", size=10, bold=False, color="1D4ED8")
    font_const = Font(name="Calibri", size=10, bold=False, color="0F172A")
    font_formula = Font(name="Calibri", size=10, bold=False, color="0F172A")
    font_link = Font(name="Calibri", size=10, bold=False, color="065F46")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F2744")
    fill_alt = PatternFill("solid", fgColor="F8FAFC")
    fill_assump = PatternFill("solid", fgColor="EFF6FF")
    fill_total = PatternFill("solid", fgColor="F1F5F9")
    fill_highlight = PatternFill("solid", fgColor="ECFDF5")

    # =========================================================================
    # SHEET 1: ASSUMPTIONS
    # =========================================================================
    ws_assump.views.sheetView[0].showGridLines = True
    ws_assump["A1"] = "NoiseFit Sync Center — Business Case Model Assumptions"
    ws_assump["A1"].font = font_title
    ws_assump["A2"] = (
        "Blue cells on light-blue shading denote editable ASSUMPTION inputs; dark text denotes VERIFIED_FACT constants. "
        "All outputs cascade via live Excel formulas."
    )
    ws_assump["A2"].font = font_sub

    headers_a = [
        "Param_ID",
        "Category",
        "Parameter Description",
        "Unit",
        "Low Case (Conservative)",
        "Base Case",
        "High Case (Optimistic)",
        "Evidence Status",
        "Source or Assumption",
        "Reasoning & Notes",
    ]
    for col_i, h in enumerate(headers_a, 1):
        ws_assump.cell(row=4, column=col_i, value=h)
    _style_header(ws_assump, 4, 1, len(headers_a))

    a_row_map: Dict[str, int] = {}
    cur_r = 5
    last_cat = None
    for p in params:
        if p["category"] != last_cat:
            _style_section(ws_assump, cur_r, 1, len(headers_a), p["category"])
            cur_r += 1
            last_cat = p["category"]

        a_row_map[p["id"]] = cur_r
        fmt = _num_fmt_for_unit(p["unit"])
        is_assump = p["status"] == "ASSUMPTION"

        vals = [
            p["id"],
            p["category"],
            p["label"],
            p["unit"],
            float(p["low"]),
            float(p["base"]),
            float(p["high"]),
            p["status"],
            p["source"],
            p["notes"],
        ]
        for col_i, v in enumerate(vals, 1):
            cell = ws_assump.cell(row=cur_r, column=col_i, value=v)
            cell.border = _thin_border()
            cell.alignment = Alignment(vertical="center", wrap_text=(col_i in (3, 9, 10)))
            if col_i in (5, 6, 7):
                cell.number_format = fmt
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.font = font_input if is_assump else font_const
                if is_assump:
                    cell.fill = fill_assump
            else:
                cell.font = font_const
        ws_assump.row_dimensions[cur_r].height = 24
        cur_r += 1

    widths_a = [28, 30, 44, 14, 18, 15, 18, 16, 42, 54]
    for idx, w in enumerate(widths_a, 1):
        ws_assump.column_dimensions[get_column_letter(idx)].width = w
    ws_assump.freeze_panes = "D5"

    # Helper to address Assumptions Low (E), Base (F), High (G)
    def a_ref(pid: str, scen_col: str) -> str:
        return f"Assumptions!{scen_col}{a_row_map[pid]}"

    # =========================================================================
    # SHEET 2: CALCULATIONS (Cols C=Low, D=Base, E=High)
    # =========================================================================
    ws_calc.views.sheetView[0].showGridLines = True
    ws_calc["A1"] = "NoiseFit Sync Center — 3-Year Operating & Cash Flow Calculations"
    ws_calc["A1"].font = font_title
    ws_calc["A2"] = "Every cell below uses dynamic Excel formulas tracing back to Assumptions. Monetary values in INR Lakhs."
    ws_calc["A2"].font = font_sub

    headers_c = ["Metric / Line Item", "Unit", "Low Case", "Base Case", "High Case"]
    for col_i, h in enumerate(headers_c, 1):
        ws_calc.cell(row=4, column=col_i, value=h)
    _style_header(ws_calc, 4, 1, 5)

    c_rows: Dict[str, int] = {}
    cr = 5

    def add_calc_row(
        key: str,
        label: str,
        unit: str,
        formula_fn,
        fmt: str = "#,##0.00",
        is_total: bool = False,
        is_highlight: bool = False,
    ) -> int:
        nonlocal cr
        c_rows[key] = cr
        ws_calc.cell(row=cr, column=1, value=label)
        ws_calc.cell(row=cr, column=2, value=unit)
        for s_idx, (a_col, c_col) in enumerate([("E", "C"), ("F", "D"), ("G", "E")]):
            cell = ws_calc.cell(row=cr, column=3 + s_idx, value=formula_fn(a_col, c_col))
            cell.number_format = fmt
            cell.alignment = Alignment(horizontal="right", vertical="center")
        for c_i in range(1, 6):
            cell = ws_calc.cell(row=cr, column=c_i)
            cell.border = _total_border() if is_total else _thin_border()
            cell.font = font_bold if (is_total or is_highlight) else font_formula
            if is_highlight:
                cell.fill = fill_highlight
            elif is_total:
                cell.fill = fill_total
            elif cr % 2 == 1:
                cell.fill = fill_alt
        ws_calc.row_dimensions[cr].height = 21
        row_out = cr
        cr += 1
        return row_out

    # Section A: Addressable Cohorts
    _style_section(ws_calc, cr, 1, 5, "A. Active Base, Failure-Affected Cohorts & Shipments Trajectory")
    cr += 1
    add_calc_row("ship_y1", "Noise Smartwatch Shipments (Year 1 Baseline)", "Devices",
                 lambda a, c: f"={a_ref('india_smartwatch_shipments_cy25_m', a)}*1000000*{a_ref('noise_smartwatch_share_cy25', a)}", "#,##0")
    add_calc_row("ship_y2", "Noise Smartwatch Shipments (Year 2)", "Devices",
                 lambda a, c: f"={c}{c_rows['ship_y1']}*(1+{a_ref('annual_base_growth_rate', a)})", "#,##0")
    add_calc_row("ship_y3", "Noise Smartwatch Shipments (Year 3)", "Devices",
                 lambda a, c: f"={c}{c_rows['ship_y2']}*(1+{a_ref('annual_base_growth_rate', a)})", "#,##0")
    add_calc_row("users_y1", "Active NoiseFit Users (Year 1)", "Users",
                 lambda a, c: f"={a_ref('active_noisefit_users_m', a)}*1000000", "#,##0")
    add_calc_row("users_y2", "Active NoiseFit Users (Year 2)", "Users",
                 lambda a, c: f"={c}{c_rows['users_y1']}*(1+{a_ref('annual_base_growth_rate', a)})", "#,##0")
    add_calc_row("users_y3", "Active NoiseFit Users (Year 3)", "Users",
                 lambda a, c: f"={c}{c_rows['users_y2']}*(1+{a_ref('annual_base_growth_rate', a)})", "#,##0")
    add_calc_row("fail_y1", "Failure-Affected Users (Year 1)", "Users",
                 lambda a, c: f"={c}{c_rows['users_y1']}*{a_ref('annual_sync_failure_prevalence', a)}", "#,##0")
    add_calc_row("fail_y2", "Failure-Affected Users (Year 2)", "Users",
                 lambda a, c: f"={c}{c_rows['users_y2']}*{a_ref('annual_sync_failure_prevalence', a)}", "#,##0")
    add_calc_row("fail_y3", "Failure-Affected Users (Year 3)", "Users",
                 lambda a, c: f"={c}{c_rows['users_y3']}*{a_ref('annual_sync_failure_prevalence', a)}", "#,##0")

    # Section B: Driver 1
    _style_section(ws_calc, cr, 1, 5, "B. Value Driver 1 — Retention & Repeat Hardware Upgrades")
    cr += 1
    add_calc_row("upg_y1", "Incremental Repeat Upgrades Saved (Year 1, Realized)", "Devices",
                 lambda a, c: f"={c}{c_rows['fail_y1']}*{a_ref('retention_lift_annual', a)}*{a_ref('repeat_upgrade_propensity', a)}*{a_ref('rollout_y1_realization', a)}", "#,##0")
    add_calc_row("upg_y2", "Incremental Repeat Upgrades Saved (Year 2)", "Devices",
                 lambda a, c: f"={c}{c_rows['fail_y2']}*{a_ref('retention_lift_annual', a)}*{a_ref('repeat_upgrade_propensity', a)}", "#,##0")
    add_calc_row("upg_y3", "Incremental Repeat Upgrades Saved (Year 3)", "Devices",
                 lambda a, c: f"={c}{c_rows['fail_y3']}*{a_ref('retention_lift_annual', a)}*{a_ref('repeat_upgrade_propensity', a)}", "#,##0")
    add_calc_row("d1_y1", "Driver 1 Benefit — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['upg_y1']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d1_y2", "Driver 1 Benefit — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['upg_y2']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d1_y3", "Driver 1 Benefit — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['upg_y3']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d1_tot", "Driver 1 Total 3-Year Benefit", "INR Lakhs",
                 lambda a, c: f"=SUM({c}{c_rows['d1_y1']}:{c}{c_rows['d1_y3']})", "₹#,##0.00", is_total=True)

    # Section C: Driver 2
    _style_section(ws_calc, cr, 1, 5, "C. Value Driver 2 — App Store Rating Defense & Conversion")
    cr += 1
    add_calc_row("conv_y1", "Incremental Organic Hardware Conversions (Year 1, Realized)", "Devices",
                 lambda a, c: f"={a_ref('prospective_store_evaluators_m', a)}*1000000*{a_ref('baseline_evaluator_cvr', a)}*{a_ref('rating_relative_cvr_lift', a)}*{a_ref('rollout_y1_realization', a)}", "#,##0")
    add_calc_row("conv_y2", "Incremental Organic Hardware Conversions (Year 2)", "Devices",
                 lambda a, c: f"={a_ref('prospective_store_evaluators_m', a)}*1000000*(1+{a_ref('annual_base_growth_rate', a)})*{a_ref('baseline_evaluator_cvr', a)}*{a_ref('rating_relative_cvr_lift', a)}", "#,##0")
    add_calc_row("conv_y3", "Incremental Organic Hardware Conversions (Year 3)", "Devices",
                 lambda a, c: f"={a_ref('prospective_store_evaluators_m', a)}*1000000*((1+{a_ref('annual_base_growth_rate', a)})^2)*{a_ref('baseline_evaluator_cvr', a)}*{a_ref('rating_relative_cvr_lift', a)}", "#,##0")
    add_calc_row("d2_y1", "Driver 2 Benefit — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['conv_y1']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d2_y2", "Driver 2 Benefit — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['conv_y2']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d2_y3", "Driver 2 Benefit — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['conv_y3']}*{a_ref('hw_contribution_margin_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d2_tot", "Driver 2 Total 3-Year Benefit", "INR Lakhs",
                 lambda a, c: f"=SUM({c}{c_rows['d2_y1']}:{c}{c_rows['d2_y3']})", "₹#,##0.00", is_total=True)

    # Section D: Driver 3
    _style_section(ws_calc, cr, 1, 5, "D. Value Driver 3 — Support Ticket Deflection & Ops Cost Saved")
    cr += 1
    add_calc_row("tkt_y1", "Sync & Connectivity Tickets Deflected (Year 1, Realized)", "Tickets",
                 lambda a, c: f"={c}{c_rows['fail_y1']}*{a_ref('ticket_escalation_rate', a)}*{a_ref('ticket_deflection_rate', a)}*{a_ref('rollout_y1_realization', a)}", "#,##0")
    add_calc_row("tkt_y2", "Sync & Connectivity Tickets Deflected (Year 2)", "Tickets",
                 lambda a, c: f"={c}{c_rows['fail_y2']}*{a_ref('ticket_escalation_rate', a)}*{a_ref('ticket_deflection_rate', a)}", "#,##0")
    add_calc_row("tkt_y3", "Sync & Connectivity Tickets Deflected (Year 3)", "Tickets",
                 lambda a, c: f"={c}{c_rows['fail_y3']}*{a_ref('ticket_escalation_rate', a)}*{a_ref('ticket_deflection_rate', a)}", "#,##0")
    add_calc_row("d3_y1", "Driver 3 Benefit — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['tkt_y1']}*{a_ref('support_cost_per_ticket_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d3_y2", "Driver 3 Benefit — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['tkt_y2']}*{a_ref('support_cost_per_ticket_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d3_y3", "Driver 3 Benefit — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['tkt_y3']}*{a_ref('support_cost_per_ticket_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d3_tot", "Driver 3 Total 3-Year Benefit", "INR Lakhs",
                 lambda a, c: f"=SUM({c}{c_rows['d3_y1']}:{c}{c_rows['d3_y3']})", "₹#,##0.00", is_total=True)

    # Section E: Driver 4
    _style_section(ws_calc, cr, 1, 5, "E. Value Driver 4 — Prevented False Hardware Returns / RMAs")
    cr += 1
    add_calc_row("rma_y1", "False Sync RMAs Prevented (Year 1, Realized)", "Devices",
                 lambda a, c: f"={c}{c_rows['ship_y1']}*{a_ref('sync_attributed_rma_rate', a)}*{a_ref('rma_prevention_share', a)}*{a_ref('rollout_y1_realization', a)}", "#,##0")
    add_calc_row("rma_y2", "False Sync RMAs Prevented (Year 2)", "Devices",
                 lambda a, c: f"={c}{c_rows['ship_y2']}*{a_ref('sync_attributed_rma_rate', a)}*{a_ref('rma_prevention_share', a)}", "#,##0")
    add_calc_row("rma_y3", "False Sync RMAs Prevented (Year 3)", "Devices",
                 lambda a, c: f"={c}{c_rows['ship_y3']}*{a_ref('sync_attributed_rma_rate', a)}*{a_ref('rma_prevention_share', a)}", "#,##0")
    add_calc_row("d4_y1", "Driver 4 Benefit — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['rma_y1']}*{a_ref('avoided_cost_per_rma_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d4_y2", "Driver 4 Benefit — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['rma_y2']}*{a_ref('avoided_cost_per_rma_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d4_y3", "Driver 4 Benefit — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['rma_y3']}*{a_ref('avoided_cost_per_rma_inr', a)}/100000", "₹#,##0.00")
    add_calc_row("d4_tot", "Driver 4 Total 3-Year Benefit", "INR Lakhs",
                 lambda a, c: f"=SUM({c}{c_rows['d4_y1']}:{c}{c_rows['d4_y3']})", "₹#,##0.00", is_total=True)

    # Section F: Investment & OpEx
    _style_section(ws_calc, cr, 1, 5, "F. Upfront Build Investment & Ongoing Operating Costs")
    cr += 1
    pw_first = a_row_map["pw_pm"]
    pw_last = a_row_map["pw_support_legal"]
    add_calc_row("build_pw", "Total Upfront Build Effort", "Person-Weeks",
                 lambda a, c: f"=SUM(Assumptions!{a}{pw_first}:{a}{pw_last})", "#,##0.0")
    add_calc_row("upfront_labour", "Upfront Build Labour Cost", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['build_pw']}*{a_ref('loaded_cost_per_pw_lakhs', a)}", "₹#,##0.00")
    add_calc_row("non_labour", "Non-Labour Setup (Device Lab, Usability, Legal)", "INR Lakhs",
                 lambda a, c: f"={a_ref('non_labour_setup_lakhs', a)}", "₹#,##0.00")
    add_calc_row("y0_inv", "Total Year 0 Upfront Investment", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['upfront_labour']}+{c}{c_rows['non_labour']}", "₹#,##0.00", is_total=True)
    add_calc_row("maint_labour", "Annual Maintenance Labour Cost (Y1/Y2/Y3)", "INR Lakhs/yr",
                 lambda a, c: f"={a_ref('annual_maint_pw', a)}*{a_ref('loaded_cost_per_pw_lakhs', a)}", "₹#,##0.00")
    add_calc_row("infra_opex", "Annual Telemetry Infra & Compliance OpEx (Y1/Y2/Y3)", "INR Lakhs/yr",
                 lambda a, c: f"={a_ref('annual_infra_compliance_lakhs', a)}", "₹#,##0.00")
    add_calc_row("annual_opex", "Total Annual Operating Cost (Y1/Y2/Y3)", "INR Lakhs/yr",
                 lambda a, c: f"={c}{c_rows['maint_labour']}+{c}{c_rows['infra_opex']}", "₹#,##0.00", is_total=True)

    # Section G: Cash Flows & Financial KPIs (Note: contiguous rows for y1..y3 net CF allow clean =NPV(r, range))
    _style_section(ws_calc, cr, 1, 5, "G. 3-Year Cash Flow Statement & Financial Metrics")
    cr += 1
    add_calc_row("gross_y1", "Gross Benefits — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['d1_y1']}+{c}{c_rows['d2_y1']}+{c}{c_rows['d3_y1']}+{c}{c_rows['d4_y1']}", "₹#,##0.00")
    add_calc_row("gross_y2", "Gross Benefits — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['d1_y2']}+{c}{c_rows['d2_y2']}+{c}{c_rows['d3_y2']}+{c}{c_rows['d4_y2']}", "₹#,##0.00")
    add_calc_row("gross_y3", "Gross Benefits — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['d1_y3']}+{c}{c_rows['d2_y3']}+{c}{c_rows['d3_y3']}+{c}{c_rows['d4_y3']}", "₹#,##0.00")
    add_calc_row("total_gross", "Total 3-Year Gross Benefits", "INR Lakhs",
                 lambda a, c: f"=SUM({c}{c_rows['gross_y1']}:{c}{c_rows['gross_y3']})", "₹#,##0.00", is_total=True)
    add_calc_row("total_opex", "Total 3-Year Operating Costs (Y1–Y3)", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['annual_opex']}*3", "₹#,##0.00")
    add_calc_row("total_costs", "Total 3-Year All-In Costs (Y0 + Y1–Y3 OpEx)", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['y0_inv']}+{c}{c_rows['total_opex']}", "₹#,##0.00", is_total=True)

    # Net Cash Flows placed in contiguous rows Y0..Y3
    add_calc_row("cf_y0", "Net Cash Flow — Year 0 (Initial Outlay)", "INR Lakhs",
                 lambda a, c: f"=-{c}{c_rows['y0_inv']}", "₹#,##0.00")
    add_calc_row("cf_y1", "Net Cash Flow — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['gross_y1']}-{c}{c_rows['annual_opex']}", "₹#,##0.00")
    add_calc_row("cf_y2", "Net Cash Flow — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['gross_y2']}-{c}{c_rows['annual_opex']}", "₹#,##0.00")
    add_calc_row("cf_y3", "Net Cash Flow — Year 3", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['gross_y3']}-{c}{c_rows['annual_opex']}", "₹#,##0.00")

    add_calc_row("cum_y0", "Cumulative Net Cash Flow — Year 0", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['cf_y0']}", "₹#,##0.00")
    add_calc_row("cum_y1", "Cumulative Net Cash Flow — Year 1", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['cum_y0']}+{c}{c_rows['cf_y1']}", "₹#,##0.00")
    add_calc_row("cum_y2", "Cumulative Net Cash Flow — Year 2", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['cum_y1']}+{c}{c_rows['cf_y2']}", "₹#,##0.00")
    add_calc_row("cum_y3", "Cumulative Net Cash Flow — Year 3 (3-Yr Net Benefit)", "INR Lakhs",
                 lambda a, c: f"={c}{c_rows['cum_y2']}+{c}{c_rows['cf_y3']}", "₹#,##0.00", is_total=True)

    add_calc_row("disc_rate", "Discount Rate (WACC)", "%",
                 lambda a, c: f"={a_ref('discount_rate', a)}", "0.0%")
    add_calc_row("lifecycle_roi", "3-Year Lifecycle ROI ((Gross - All-In Cost) / All-In Cost)", "%",
                 lambda a, c: f"=({c}{c_rows['total_gross']}-{c}{c_rows['total_costs']})/{c}{c_rows['total_costs']}", "0.0%", is_highlight=True)
    add_calc_row("capex_roi", "3-Year Net ROI on Initial CapEx (Net Benefit / Y0 Cost)", "%",
                 lambda a, c: f"={c}{c_rows['cum_y3']}/{c}{c_rows['y0_inv']}", "0.0%")
    add_calc_row("payback_m", "Payback Period (Undiscounted Months)", "Months",
                 lambda a, c: (
                     f"=IF({c}{c_rows['cum_y1']}>=0, (-{c}{c_rows['cf_y0']}/{c}{c_rows['cf_y1']})*12, "
                     f"IF({c}{c_rows['cum_y2']}>=0, 12+(-{c}{c_rows['cum_y1']}/{c}{c_rows['cf_y2']})*12, "
                     f"IF({c}{c_rows['cum_y3']}>=0, 24+(-{c}{c_rows['cum_y2']}/{c}{c_rows['cf_y3']})*12, \"N/A (>36 mo)\")))"
                 ), "0.0", is_highlight=True)
    add_calc_row("npv", "3-Year Net Present Value (NPV @ Scenario Discount Rate)", "INR Lakhs",
                 lambda a, c: f"=NPV({c}{c_rows['disc_rate']}, {c}{c_rows['cf_y1']}:{c}{c_rows['cf_y3']})+{c}{c_rows['cf_y0']}", "₹#,##0.00", is_highlight=True)

    for idx, w in enumerate([54, 16, 18, 18, 18], 1):
        ws_calc.column_dimensions[get_column_letter(idx)].width = w
    ws_calc.freeze_panes = "C5"

    # =========================================================================
    # SHEET 3: SCENARIOS (Scenario Comparison + Driver Mix + Live 1-Way Tornado)
    # =========================================================================
    ws_scen.views.sheetView[0].showGridLines = True
    ws_scen["A1"] = "NoiseFit Sync Center — Scenario Analysis & One-Way Sensitivity (Tornado)"
    ws_scen["A1"].font = font_title
    ws_scen["A2"] = "All scenario metrics and one-way sensitivity swings are live Excel formulas linked to Calculations & Assumptions."
    ws_scen["A2"].font = font_sub

    for col_i, h in enumerate(["Scenario Financial Summary", "Unit", "Low Case", "Base Case", "High Case", "High vs Low Spread"], 1):
        ws_scen.cell(row=4, column=col_i, value=h)
    _style_header(ws_scen, 4, 1, 6)

    scen_rows_spec = [
        ("Active NoiseFit Users (Year 1)", "Users", "users_y1", "#,##0"),
        ("Failure-Affected Users (Year 1)", "Users", "fail_y1", "#,##0"),
        ("Driver 1: Retention & Repeat Upgrades (3-Yr)", "INR Lakhs", "d1_tot", "₹#,##0.00"),
        ("Driver 2: App Rating Defense & Conversion (3-Yr)", "INR Lakhs", "d2_tot", "₹#,##0.00"),
        ("Driver 3: Support Ticket Deflection (3-Yr)", "INR Lakhs", "d3_tot", "₹#,##0.00"),
        ("Driver 4: Prevented False RMAs (3-Yr)", "INR Lakhs", "d4_tot", "₹#,##0.00"),
        ("Total 3-Year Gross Benefits", "INR Lakhs", "total_gross", "₹#,##0.00"),
        ("Year 0 Upfront Build Investment", "INR Lakhs", "y0_inv", "₹#,##0.00"),
        ("Total 3-Year Ongoing Operating Costs", "INR Lakhs", "total_opex", "₹#,##0.00"),
        ("Total 3-Year All-In Cost", "INR Lakhs", "total_costs", "₹#,##0.00"),
        ("3-Year Net Benefit (Undiscounted)", "INR Lakhs", "cum_y3", "₹#,##0.00"),
        ("Discount Rate (WACC)", "%", "disc_rate", "0.0%"),
        ("3-Year Lifecycle ROI", "%", "lifecycle_roi", "0.0%"),
        ("3-Year Net ROI on Initial CapEx", "%", "capex_roi", "0.0%"),
        ("Payback Period", "Months", "payback_m", "0.0"),
        ("3-Year Net Present Value (NPV)", "INR Lakhs", "npv", "₹#,##0.00"),
    ]

    scen_row_map: Dict[str, int] = {}
    sr = 5
    for label, unit, key, fmt in scen_rows_spec:
        scen_row_map[key] = sr
        cr_idx = c_rows[key]
        ws_scen.cell(row=sr, column=1, value=label)
        ws_scen.cell(row=sr, column=2, value=unit)
        ws_scen.cell(row=sr, column=3, value=f"=Calculations!C{cr_idx}")
        ws_scen.cell(row=sr, column=4, value=f"=Calculations!D{cr_idx}")
        ws_scen.cell(row=sr, column=5, value=f"=Calculations!E{cr_idx}")
        if key == "payback_m":
            ws_scen.cell(row=sr, column=6, value="See Scenario Cols")
        else:
            ws_scen.cell(row=sr, column=6, value=f"=E{sr}-C{sr}")

        is_hi = key in ("lifecycle_roi", "payback_m", "npv")
        is_tot = key in ("total_gross", "total_costs", "cum_y3")
        for col_i in range(1, 7):
            c = ws_scen.cell(row=sr, column=col_i)
            c.border = _total_border() if is_tot else _thin_border()
            c.font = font_bold if (is_hi or is_tot) else (font_link if col_i in (3, 4, 5) else font_formula)
            if is_hi:
                c.fill = fill_highlight
            elif is_tot:
                c.fill = fill_total
            elif sr % 2 == 1:
                c.fill = fill_alt
            if col_i in (3, 4, 5, 6):
                c.number_format = fmt
                c.alignment = Alignment(horizontal="right", vertical="center")
        ws_scen.row_dimensions[sr].height = 21
        sr += 1

    # Table 2: Base Case Driver Share
    sr += 1
    _style_section(ws_scen, sr, 1, 6, "Base Case Value Driver Mix (3-Year Gross Benefit Share)")
    sr += 1
    driver_mix_start = sr
    for d_key, d_label in [
        ("d3_tot", "Driver 3: Support Ticket Deflection & Ops Cost Saved"),
        ("d1_tot", "Driver 1: Retention & Repeat Hardware Upgrades"),
        ("d4_tot", "Driver 4: Prevented False Hardware Returns / RMAs"),
        ("d2_tot", "Driver 2: App Store Rating Defense & Conversion"),
    ]:
        ws_scen.cell(row=sr, column=1, value=d_label)
        ws_scen.cell(row=sr, column=2, value="INR Lakhs")
        ws_scen.cell(row=sr, column=3, value=f"=D{scen_row_map[d_key]}")
        ws_scen.cell(row=sr, column=4, value=f"=C{sr}/D{scen_row_map['total_gross']}")
        ws_scen.cell(row=sr, column=3).number_format = "₹#,##0.00"
        ws_scen.cell(row=sr, column=4).number_format = "0.0%"
        for col_i in range(1, 5):
            ws_scen.cell(row=sr, column=col_i).border = _thin_border()
            ws_scen.cell(row=sr, column=col_i).font = font_formula
        ws_scen.row_dimensions[sr].height = 20
        sr += 1

    # Table 3: Helper Present Values (Base Case) + Live One-Way Tornado Sensitivity Table
    sr += 1
    _style_section(ws_scen, sr, 1, 8, "One-Way Sensitivity Analysis on Base 3-Year NPV (Live Excel Decomposition)")
    sr += 1
    pv_hdr_row = sr
    ws_scen.cell(row=sr, column=1, value="Base PV Helper Block (INR Lakhs)")
    ws_scen.cell(row=sr, column=2, value="PV(D1)")
    ws_scen.cell(row=sr, column=3, value="PV(D2)")
    ws_scen.cell(row=sr, column=4, value="PV(D3)")
    ws_scen.cell(row=sr, column=5, value="PV(D4)")
    ws_scen.cell(row=sr, column=6, value="PV(OpEx)")
    ws_scen.cell(row=sr, column=7, value="Base NPV")
    _style_header(ws_scen, sr, 1, 7)
    sr += 1
    pv_val_row = sr
    base_disc_cell = f"Calculations!D{c_rows['disc_rate']}"
    ws_scen.cell(row=sr, column=1, value="Discounted @ Base WACC")
    ws_scen.cell(row=sr, column=2, value=f"=NPV({base_disc_cell}, Calculations!D{c_rows['d1_y1']}:D{c_rows['d1_y3']})")
    ws_scen.cell(row=sr, column=3, value=f"=NPV({base_disc_cell}, Calculations!D{c_rows['d2_y1']}:D{c_rows['d2_y3']})")
    ws_scen.cell(row=sr, column=4, value=f"=NPV({base_disc_cell}, Calculations!D{c_rows['d3_y1']}:D{c_rows['d3_y3']})")
    ws_scen.cell(row=sr, column=5, value=f"=NPV({base_disc_cell}, Calculations!D{c_rows['d4_y1']}:D{c_rows['d4_y3']})")
    ws_scen.cell(row=sr, column=6, value=f"=Calculations!D{c_rows['annual_opex']}*(1/(1+{base_disc_cell})+1/((1+{base_disc_cell})^2)+1/((1+{base_disc_cell})^3))")
    ws_scen.cell(row=sr, column=7, value=f"=D{scen_row_map['npv']}")
    for col_i in range(2, 8):
        c = ws_scen.cell(row=sr, column=col_i)
        c.number_format = "₹#,##0.00"
        c.font = font_formula
        c.border = _thin_border()
    sr += 2

    # Headers for Tornado Table
    t_hdr = ["Parameter Tested (Low -> High)", "Unit", "Low Bound", "Base Value", "High Bound", "NPV @ Low Input", "NPV @ High Input", "Total NPV Swing"]
    for col_i, h in enumerate(t_hdr, 1):
        ws_scen.cell(row=sr, column=col_i, value=h)
    _style_header(ws_scen, sr, 1, 8)
    sr += 1

    pv_d1_c = f"B{pv_val_row}"
    pv_d2_c = f"C{pv_val_row}"
    pv_d3_c = f"D{pv_val_row}"
    pv_d4_c = f"E{pv_val_row}"
    base_npv_c = f"G{pv_val_row}"

    def _tornado_npv_formula(pid: str, bound_col: str) -> str:
        """Exact closed-form Excel formula matching compute_scenario when only pid moves to bound_col."""
        val_ref = f"Assumptions!{bound_col}{a_row_map[pid]}"
        base_ref = f"Assumptions!F{a_row_map[pid]}"
        ratio_m1 = f"({val_ref}/{base_ref}-1)"
        if pid in ("annual_sync_failure_prevalence", "active_noisefit_users_m"):
            return f"={base_npv_c}+({pv_d1_c}+{pv_d3_c})*{ratio_m1}"
        if pid in ("ticket_deflection_rate", "ticket_escalation_rate", "support_cost_per_ticket_inr"):
            return f"={base_npv_c}+{pv_d3_c}*{ratio_m1}"
        if pid == "retention_lift_annual":
            return f"={base_npv_c}+{pv_d1_c}*{ratio_m1}"
        if pid == "hw_contribution_margin_inr":
            return f"={base_npv_c}+({pv_d1_c}+{pv_d2_c})*{ratio_m1}"
        if pid == "rma_prevention_share":
            return f"={base_npv_c}+{pv_d4_c}*{ratio_m1}"
        if pid == "rollout_y1_realization":
            return f"={base_npv_c}+((Calculations!D{c_rows['gross_y1']}*{ratio_m1})/(1+{base_disc_cell}))"
        if pid == "loaded_cost_per_pw_lakhs":
            delta_rate = f"({val_ref}-{base_ref})"
            pv_maint_pw = f"({a_ref('annual_maint_pw', 'F')}*(1/(1+{base_disc_cell})+1/((1+{base_disc_cell})^2)+1/((1+{base_disc_cell})^3)))"
            return f"={base_npv_c}-{delta_rate}*(Calculations!D{c_rows['build_pw']}+{pv_maint_pw})"
        if pid == "discount_rate":
            return f"=NPV({val_ref}, Calculations!D{c_rows['cf_y1']}:D{c_rows['cf_y3']})+Calculations!D{c_rows['cf_y0']}"
        raise ValueError(f"Unsupported tornado pid: {pid}")

    # Pre-sort Tornado rows by magnitude using Python compute_sensitivity so Excel displays Top -> Bottom cleanly!
    sens_sorted = compute_sensitivity(params, by_id)
    tornado_rows_excel: Dict[str, int] = {}
    for rank_i, item in enumerate(sens_sorted, 1):
        pid = item["id"]
        tornado_rows_excel[pid] = sr
        fmt_u = _num_fmt_for_unit(item["unit"])
        ws_scen.cell(row=sr, column=1, value=f"#{rank_i}: {item['label']}")
        ws_scen.cell(row=sr, column=2, value=item["unit"])
        ws_scen.cell(row=sr, column=3, value=f"={a_ref(pid, 'E')}")
        ws_scen.cell(row=sr, column=4, value=f"={a_ref(pid, 'F')}")
        ws_scen.cell(row=sr, column=5, value=f"={a_ref(pid, 'G')}")
        ws_scen.cell(row=sr, column=6, value=_tornado_npv_formula(pid, "E"))
        ws_scen.cell(row=sr, column=7, value=_tornado_npv_formula(pid, "G"))
        ws_scen.cell(row=sr, column=8, value=f"=ABS(G{sr}-F{sr})")

        for col_i in range(1, 9):
            c = ws_scen.cell(row=sr, column=col_i)
            c.border = _thin_border()
            c.font = font_bold if rank_i <= 3 else font_formula
            if rank_i <= 3:
                c.fill = PatternFill("solid", fgColor="FEF3C7")
            if col_i in (3, 4, 5):
                c.number_format = fmt_u
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif col_i in (6, 7, 8):
                c.number_format = "₹#,##0.00"
                c.alignment = Alignment(horizontal="right", vertical="center")
        ws_scen.row_dimensions[sr].height = 21
        sr += 1

    for idx, w in enumerate([48, 13, 15, 15, 15, 18, 18, 18], 1):
        ws_scen.column_dimensions[get_column_letter(idx)].width = w
    ws_scen.freeze_panes = "C5"

    # =========================================================================
    # SHEET 4: SUMMARY (Executive Scorecard Linked Dynamically to Scenarios/Calcs)
    # =========================================================================
    ws_sum.views.sheetView[0].showGridLines = True
    ws_sum["A1"] = "NoiseFit Sync Center — Executive Business Case Summary"
    ws_sum["A1"].font = font_title
    ws_sum["A2"] = (
        "Recommendation: APPROVE & FUND (Base Case 3-Yr ROI: 399.6%, Payback: 6.0 Months, NPV @ 12%: ₹217.54 Lakhs / ₹2.18 Cr). "
        "Offer Sync Center FREE to all NoiseFit users."
    )
    ws_sum["A2"].font = Font(name="Calibri", size=10, bold=True, color="065F46")

    # Section 1: Headline Scenario Scorecard
    for col_i, h in enumerate(["Headline Business Case Metric", "Unit", "Low Case", "Base Case", "High Case"], 1):
        ws_sum.cell(row=4, column=col_i, value=h)
    _style_header(ws_sum, 4, 1, 5)

    sum_metrics = [
        ("Year 0 Upfront Investment", "INR Lakhs", "y0_inv", "₹#,##0.00"),
        ("Total 3-Year All-In Cost (Y0 + Y1–Y3 OpEx)", "INR Lakhs", "total_costs", "₹#,##0.00"),
        ("Total 3-Year Gross Value Delivered", "INR Lakhs", "total_gross", "₹#,##0.00"),
        ("3-Year Net Benefit (Undiscounted)", "INR Lakhs", "cum_y3", "₹#,##0.00"),
        ("3-Year Lifecycle ROI", "%", "lifecycle_roi", "0.0%"),
        ("Payback Period", "Months", "payback_m", "0.0"),
        ("3-Year Net Present Value (NPV)", "INR Lakhs", "npv", "₹#,##0.00"),
    ]
    sum_row_map: Dict[str, int] = {}
    xr = 5
    for label, unit, key, fmt in sum_metrics:
        sum_row_map[key] = xr
        s_row = scen_row_map[key]
        ws_sum.cell(row=xr, column=1, value=label)
        ws_sum.cell(row=xr, column=2, value=unit)
        ws_sum.cell(row=xr, column=3, value=f"=Scenarios!C{s_row}")
        ws_sum.cell(row=xr, column=4, value=f"=Scenarios!D{s_row}")
        ws_sum.cell(row=xr, column=5, value=f"=Scenarios!E{s_row}")
        is_hi = key in ("lifecycle_roi", "payback_m", "npv")
        for col_i in range(1, 6):
            c = ws_sum.cell(row=xr, column=col_i)
            c.border = _thin_border()
            c.font = font_bold if is_hi else (font_link if col_i >= 3 else font_formula)
            if is_hi:
                c.fill = fill_highlight
            if col_i >= 3:
                c.number_format = fmt
                c.alignment = Alignment(horizontal="right", vertical="center")
        ws_sum.row_dimensions[xr].height = 22
        xr += 1

    # Section 2: Market Sizing Snapshot on Summary (Formula-Driven)
    xr += 1
    _style_section(ws_sum, xr, 1, 5, "Market Sizing Snapshot (TAM / SAM / SOM — Top-Down & Bottom-Up)")
    xr += 1
    for col_i, h in enumerate(["Market Tier", "Metric", "Estimate", "Unit", "Methodology / Grounding"], 1):
        ws_sum.cell(row=xr, column=col_i, value=h)
    _style_header(ws_sum, xr, 1, 5)
    xr += 1
    ms_rows = [
        ("India Macro Base", "Active Smartphones / Internet Users", f"={a_ref('india_active_smartphones_m', 'F')}", "M devices", "Counterpoint (Feb 2026); 958M internet users (IAMAI 2026)"),
        ("TAM (Top-Down)", "Wearable-Eligible Smartphone App Pool (25% Assump.)", f"={a_ref('india_active_smartphones_m', 'F')}*0.25", "M users", "740M active smartphones x 25% connected-wearable adoption [ASSUMPTION]"),
        ("SAM (India Smartwatches)", "Active Smartwatch Companion App Users", f"=({a_ref('india_smartwatch_shipments_cy24_m', 'F')}+{a_ref('india_smartwatch_shipments_cy25_m', 'F')})*0.939", "M users", "IDC 63.9M CY24-25 shipments + 2023 tail net of dormancy [ASSUMPTION]"),
        ("SOM (NoiseFit Active Base)", "Active NoiseFit Connected Users (Base Case)", f"={a_ref('active_noisefit_users_m', 'F')}", "M users", "17.1M 2-yr Noise shipments x ~60% survival + tail (~20% of SAM) [ASSUMPTION]"),
        ("Bottom-Up Shipments Check", "Noise Annual Smartwatch Volume (CY25)", f"={a_ref('india_smartwatch_shipments_cy25_m', 'F')}*{a_ref('noise_smartwatch_share_cy25', 'F')}", "M watches", "IDC CY25: 28.9M x 26.6% Noise share = 7.69M watches/yr"),
    ]
    for tier, m_lbl, fml, unit, meth in ms_rows:
        ws_sum.cell(row=xr, column=1, value=tier)
        ws_sum.cell(row=xr, column=2, value=m_lbl)
        c3 = ws_sum.cell(row=xr, column=3, value=fml)
        c3.number_format = "#,##0.0"
        c3.alignment = Alignment(horizontal="right", vertical="center")
        ws_sum.cell(row=xr, column=4, value=unit)
        ws_sum.cell(row=xr, column=5, value=meth)
        for col_i in range(1, 6):
            c = ws_sum.cell(row=xr, column=col_i)
            c.border = _thin_border()
            c.font = font_formula
            c.alignment = Alignment(vertical="center", wrap_text=(col_i == 5))
        ws_sum.row_dimensions[xr].height = 24
        xr += 1

    # Section 3: Top 3 Most Sensitive Assumptions (Formula-Linked to Scenarios Tornado Table)
    xr += 1
    _style_section(ws_sum, xr, 1, 5, "Top 3 Sensitivity Drivers (Largest Base NPV Impact)")
    xr += 1
    for col_i, h in enumerate(["Rank & Assumption", "Low -> High Range", "NPV @ Low (₹L)", "NPV @ High (₹L)", "Total Swing (₹L)"], 1):
        ws_sum.cell(row=xr, column=col_i, value=h)
    _style_header(ws_sum, xr, 1, 5)
    xr += 1
    for item in sens_sorted[:3]:
        tr = tornado_rows_excel[item["id"]]
        ws_sum.cell(row=xr, column=1, value=f"=Scenarios!A{tr}")
        ws_sum.cell(row=xr, column=2, value=f"{item['low_val']:.2g} to {item['high_val']:.2g} ({item['unit']})")
        c3 = ws_sum.cell(row=xr, column=3, value=f"=Scenarios!F{tr}")
        c4 = ws_sum.cell(row=xr, column=4, value=f"=Scenarios!G{tr}")
        c5 = ws_sum.cell(row=xr, column=5, value=f"=Scenarios!H{tr}")
        for cc in (c3, c4, c5):
            cc.number_format = "₹#,##0.00"
            cc.alignment = Alignment(horizontal="right", vertical="center")
        for col_i in range(1, 6):
            c = ws_sum.cell(row=xr, column=col_i)
            c.border = _thin_border()
            c.font = font_bold if col_i == 5 else font_link
        ws_sum.row_dimensions[xr].height = 22
        xr += 1

    # Section 4: Pricing & Compliance Decision Summary
    xr += 1
    _style_section(ws_sum, xr, 1, 5, "Strategic Decisions: Pricing & Compliance Summary")
    xr += 1
    notes_sum = [
        ("Pricing & Packaging", "Free for All Users — Zero Paywall on Sync Center & Diagnostics", "Preserves KPI-05 ticket deflection & avoids Gold-paywall Play Store backlash."),
        ("Privacy & DPDP 2023", "Mandatory Notice, Zero-PII Diagnostic Logs (NFR-04), 90d Erasure", "Subject to pre-launch legal counsel signoff (not legal advice)."),
        ("Launch & Kill Gate", "5-Phase Rollout (EXP-NF-001); Kill/Pivot if MDE < +10pp Recovery", "Pause GA if 7d uninstall delta >0.0% or crash rate >+0.05%."),
    ]
    for k, v, d in notes_sum:
        ws_sum.cell(row=xr, column=1, value=k).font = font_bold
        ws_sum.cell(row=xr, column=2, value=v).font = font_const
        ws_sum.cell(row=xr, column=3, value=d).font = font_sub
        ws_sum.merge_cells(start_row=xr, start_column=3, end_row=xr, end_column=5)
        for col_i in range(1, 6):
            ws_sum.cell(row=xr, column=col_i).border = _thin_border()
        ws_sum.row_dimensions[xr].height = 24
        xr += 1

    for idx, w in enumerate([44, 24, 18, 18, 48], 1):
        ws_sum.column_dimensions[get_column_letter(idx)].width = w
    ws_sum.freeze_panes = "B5"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


# ---------------------------------------------------------------------------
# CHART GENERATION (docs/images/)
# ---------------------------------------------------------------------------

def generate_charts(
    results_by_scen: Dict[str, Dict[str, Any]],
    sensitivity_rows: List[Dict[str, Any]],
    out_dir: Path = IMAGES_DIR,
) -> List[Path]:
    """Generate 3 consulting-grade visual charts into docs/images/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#CBD5E1",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": "#E2E8F0",
            "grid.linestyle": "--",
            "grid.alpha": 0.7,
        }
    )

    # 1. Scenario Comparison Chart
    fig, ax = plt.subplots(figsize=(9.5, 5.4), dpi=300)
    scenarios = ["Low Case\n(Conservative)", "Base Case\n(Expected)", "High Case\n(Optimistic)"]
    keys = ["low", "base", "high"]
    gross = [results_by_scen[k]["total_gross"] for k in keys]
    costs = [results_by_scen[k]["total_costs"] for k in keys]
    npvs = [results_by_scen[k]["npv"] for k in keys]

    x = np.arange(len(scenarios))
    w = 0.25
    b1 = ax.bar(x - w, gross, w, label="3-Yr Gross Benefits (₹L)", color=TEAL, edgecolor="white")
    b2 = ax.bar(x, costs, w, label="3-Yr All-In Costs (₹L)", color=SLATE, edgecolor="white")
    npv_colors = [CORAL if v < 0 else NAVY for v in npvs]
    b3 = ax.bar(x + w, npvs, w, label="3-Yr NPV @ WACC (₹L)", color=npv_colors, edgecolor="white")

    ax.axhline(0, color="#0F172A", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=10, fontweight="bold", color="#0F172A")
    ax.set_ylabel("INR Lakhs (₹L)", fontsize=10, fontweight="bold", color="#0F172A")
    ax.set_title(
        "NoiseFit Sync Center: 3-Year Scenario Comparison (Gross Value, Costs & NPV)",
        fontsize=12.5,
        fontweight="bold",
        color=NAVY,
        pad=14,
    )

    for bars in (b1, b2, b3):
        for rect in bars:
            val = rect.get_height()
            va = "bottom" if val >= 0 else "top"
            lbl_txt = f"₹{val:,.1f}L" if val >= 0 else f"-₹{abs(val):,.1f}L"
            ax.annotate(
                lbl_txt,
                xy=(rect.get_x() + rect.get_width() / 2, val),
                xytext=(0, 4 if val >= 0 else -10),
                textcoords="offset points",
                ha="center",
                va=va,
                fontsize=8.5,
                fontweight="bold",
                color="#0F172A",
            )

    # Annotate ROI & Payback callouts cleanly above each cluster
    max_y = max(max(gross), max(npvs))
    ax.set_ylim(min(min(npvs) - 115, -80), max_y * 1.25)
    for idx_k, k in enumerate(keys):
        res = results_by_scen[k]
        pb_str = f"{res['payback_months']:.1f} mo" if res["payback_months"] is not None else ">36 mo"
        roi_str = f"ROI: {res['lifecycle_roi']*100:,.0f}% | Payback: {pb_str}"
        top_cluster = max(gross[idx_k], costs[idx_k], npvs[idx_k])
        ax.text(
            x[idx_k],
            top_cluster + max_y * 0.095,
            roi_str,
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#F1F5F9", edgecolor="#94A3B8"),
            color=NAVY,
        )

    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=9)
    fig.text(
        0.01,
        0.01,
        "Source: model/business_case_model.py | WACC: 15% Low / 12% Base / 10% High [ASSUMPTION]",
        fontsize=7.5,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    p_scen = out_dir / "scenario_comparison.png"
    fig.savefig(p_scen, dpi=300)
    plt.close(fig)

    # 2. 3-Year Cash Flow Chart (Base Net Annual Bars + Low/Base/High Cumulative Curves)
    fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=300)
    years = ["Year 0\n(Build)", "Year 1\n(70% Ramp)", "Year 2\n(Steady)", "Year 3\n(Steady)"]
    x_yr = np.arange(len(years))
    base = results_by_scen["base"]
    low = results_by_scen["low"]
    high = results_by_scen["high"]

    bar_colors = [CORAL if v < 0 else TEAL for v in base["cash_flows"]]
    bars = ax.bar(x_yr, base["cash_flows"], width=0.44, color=bar_colors, alpha=0.88, zorder=2)
    ax.plot(x_yr, base["cum_cf"], marker="o", linewidth=2.5, markersize=7, color=NAVY, zorder=4, label="Base Cumulative Net CF (₹L)")
    ax.plot(x_yr, low["cum_cf"], marker="s", linestyle="--", linewidth=1.8, color=CORAL, zorder=3, label="Low Cumulative Net CF (₹L)")
    ax.plot(x_yr, high["cum_cf"], marker="^", linestyle="--", linewidth=1.8, color=EMERALD, zorder=3, label="High Cumulative Net CF (₹L)")

    ax.axhline(0, color="#0F172A", linewidth=1.0, zorder=1)
    for bi, rect in enumerate(bars):
        val = rect.get_height()
        if val < 0:
            ax.annotate(
                f"-₹{abs(val):,.1f}L",
                xy=(rect.get_x() + rect.get_width() / 2, val),
                xytext=(0, -14),
                textcoords="offset points",
                ha="center",
                fontsize=8.5,
                fontweight="bold",
                color=CORAL,
            )
        elif bi == 1:
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                val + 10.0,
                f"+₹{val:,.1f}L (Yr 1)",
                ha="center",
                va="bottom",
                fontsize=8.2,
                fontweight="bold",
                color="#0F766E",
                zorder=5,
            )
        else:
            # Place annual bar label neatly near bottom inside Y2/Y3 bar so it never collides with Cum line
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                16.0,
                f"+₹{val:,.1f}L\n(Yr {bi})",
                ha="center",
                va="bottom",
                fontsize=8.0,
                fontweight="bold",
                color="white",
                zorder=5,
            )

    # Label cumulative Base curve for Y1..Y3 cleanly away from bars and High line
    for xi, cv in zip(x_yr[1:], base["cum_cf"][1:]):
        if xi == 1:
            xy_off = (52, 42)
            arrow = dict(arrowstyle="->", color=NAVY, lw=1.0)
        elif xi == 2:
            xy_off = (0, 30)
            arrow = None
        else:
            xy_off = (0, 16)
            arrow = None
        ax.annotate(
            f"Cum: ₹{cv:,.1f}L",
            xy=(xi, cv),
            xytext=xy_off,
            textcoords="offset points",
            ha="center",
            arrowprops=arrow,
            fontsize=8.5,
            fontweight="bold",
            color=NAVY,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#CBD5E1", alpha=0.95),
            zorder=6,
        )

    # Highlight Base Payback Crossover (~Year 0.50 = 6.0 months) cleanly below Low curve
    ax.set_ylim(-155, max(high["cum_cf"]) * 1.12)
    if base["payback_months"] is not None:
        pb_x = base["payback_months"] / 12.0
        ax.scatter([pb_x], [0], s=95, zorder=6, color=AMBER, edgecolor="black")
        ax.annotate(
            f"Base Payback: {base['payback_months']:.1f} months",
            xy=(pb_x, 0),
            xytext=(pb_x + 0.35, -118),
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.6),
            fontsize=8.5,
            fontweight="bold",
            color="#92400E",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFBEB", edgecolor=AMBER),
            zorder=7,
        )

    ax.set_xticks(x_yr)
    ax.set_xticklabels(years, fontsize=10, fontweight="bold", color="#0F172A")
    ax.set_ylabel("INR Lakhs (₹L)", fontsize=10, fontweight="bold", color="#0F172A")
    ax.set_title(
        "NoiseFit Sync Center: 3-Year Cash Flow Trajectory & Payback Profile",
        fontsize=12.5,
        fontweight="bold",
        color=NAVY,
        pad=14,
    )
    handles, leg_labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor=TEAL, alpha=0.88))
    leg_labels.append("Base Annual Net CF (+Y1..Y3)")
    handles.append(Patch(facecolor=CORAL, alpha=0.88))
    leg_labels.append("Base Upfront Outlay (-Y0)")
    ax.legend(handles, leg_labels, loc="upper left", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.3)
    fig.text(
        0.01,
        0.01,
        "Source: model/business_case_model.py | Year 1 realization: 60% Low / 70% Base / 80% High [ASSUMPTION]",
        fontsize=7.5,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    p_cf = out_dir / "cashflow_projection.png"
    fig.savefig(p_cf, dpi=300)
    plt.close(fig)

    # 3. Sensitivity Tornado Chart (Top 10 ranked by absolute Base NPV swing)
    top_rows = list(reversed(sensitivity_rows[:10]))  # Largest at top
    base_npv = results_by_scen["base"]["npv"]

    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=300)
    y_pos = np.arange(len(top_rows))
    labels = [row["label"] for row in top_rows]
    d_low = [row["delta_low"] for row in top_rows]
    d_high = [row["delta_high"] for row in top_rows]

    for idx_y, (dl, dh, row) in enumerate(zip(d_low, d_high, top_rows)):
        neg_val = min(dl, dh)
        pos_val = max(dl, dh)
        ax.barh(idx_y, neg_val, height=0.62, color=CORAL, alpha=0.88,
                label="Downside Impact on Base NPV" if idx_y == len(top_rows) - 1 else "")
        ax.barh(idx_y, pos_val, height=0.62, color=TEAL, alpha=0.88,
                label="Upside Impact on Base NPV" if idx_y == len(top_rows) - 1 else "")
        swing = row["swing"]
        ax.text(
            pos_val + 2.2,
            idx_y,
            f"Swing: ₹{swing:,.1f}L",
            va="center",
            ha="left",
            fontsize=8.3,
            fontweight="bold" if idx_y >= len(top_rows) - 3 else "normal",
            color=NAVY if idx_y >= len(top_rows) - 3 else SLATE,
        )

    ax.axvline(0, color="#0F172A", linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.2, fontweight="bold", color="#0F172A")
    for tick_i, tick in enumerate(ax.get_yticklabels()):
        if tick_i >= len(top_rows) - 3:
            tick.set_color(NAVY)
        else:
            tick.set_color(SLATE)

    max_right = max(max(d_low + d_high), 50)
    min_left = min(min(d_low + d_high), -50)
    ax.set_xlim(min_left * 1.25, max_right * 1.48)
    ax.set_xlabel(f"Delta vs. Base 3-Year NPV of ₹{base_npv:,.1f}L (INR Lakhs)", fontsize=10, fontweight="bold", color="#0F172A")
    fig.suptitle(
        "One-Way Sensitivity Analysis (Tornado): Impact on Base 3-Year NPV",
        fontsize=12.5,
        fontweight="bold",
        color=NAVY,
        y=0.97,
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.09),
        ncol=2,
        frameon=True,
        facecolor="white",
        edgecolor="#CBD5E1",
        fontsize=8.8,
    )
    fig.text(
        0.01,
        0.01,
        "Source: model/business_case_model.py | Top 3 sensitivity drivers highlighted in dark navy labels [ASSUMPTION]",
        fontsize=7.5,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    p_torn = out_dir / "sensitivity_tornado.png"
    fig.savefig(p_torn, dpi=300)
    plt.close(fig)

    return [p_scen, p_cf, p_torn]


def run_all(write_outputs: bool = True) -> Dict[str, Any]:
    """Run entire model pipeline, optionally generating Excel workbook and charts."""
    metadata, params, by_id = load_assumptions()
    market = compute_market_sizing(by_id)
    results = {
        s: compute_scenario(extract_scenario_inputs(params, s))
        for s in ("low", "base", "high")
    }
    sensitivity = compute_sensitivity(params, by_id)

    if write_outputs:
        build_workbook(metadata, params, by_id, WORKBOOK_PATH)
        charts = generate_charts(results, sensitivity, IMAGES_DIR)
    else:
        charts = []

    return {
        "metadata": metadata,
        "market": market,
        "results": results,
        "sensitivity": sensitivity,
        "charts": charts,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    out = run_all(write_outputs=True)
    m = out["market"]
    print("=== NOISEFIT SYNC CENTER: MARKET SIZING SUMMARY ===")
    print(f"TAM (India Wearable-Eligible Smartphones @ 25% [ASSUMPTION]): {m['tam_users_m']:.1f}M users")
    print(f"SAM (India Active Smartwatch Companion Users [ASSUMPTION]):    {m['sam_users_m']:.1f}M users")
    print(f"SOM (Active NoiseFit Users Low / Base / High [ASSUMPTION]):   {m['som_low_m']:.1f}M / {m['som_base_m']:.1f}M / {m['som_high_m']:.1f}M")
    print(f"Bottom-Up CY25 Noise Shipments (28.9M x 26.6%):               {m['noise_cy25_units_m']:.2f}M watches/yr")
    print(f"Implied RoC FY25 Realization / Watch (Rs 1,048 Cr / 7.69M):   INR {m['implied_rev_per_watch_inr']:,.0f}")

    print("\n=== 3-YEAR FINANCIAL SCENARIOS (INR Lakhs) ===")
    for s in ("low", "base", "high"):
        r = out["results"][s]
        pb = f"{r['payback_months']:.1f} mo" if r["payback_months"] is not None else "N/A (>36 mo)"
        print(
            f"[{s.upper():4s}] Y0 CapEx=₹{r['y0_investment']:6.2f}L | 3Yr OpEx=₹{r['total_opex']:5.2f}L | "
            f"3Yr Gross=₹{r['total_gross']:7.2f}L | Net=₹{r['net_benefit_3yr']:7.2f}L | "
            f"Lifecycle ROI={r['lifecycle_roi']*100:6.1f}% | Payback={pb:12s} | "
            f"NPV (@{r['discount_rate']*100:.0f}%)=₹{r['npv']:7.2f}L"
        )

    b = out["results"]["base"]
    print("\n=== BASE CASE 3-YEAR VALUE DRIVER BREAKDOWN ===")
    for lbl, val in [
        ("Driver 3 (Support Deflection)", b["d3_total"]),
        ("Driver 1 (Retention / Upgrades)", b["d1_total"]),
        ("Driver 4 (Prevented RMAs)", b["d4_total"]),
        ("Driver 2 (Rating -> CVR)", b["d2_total"]),
    ]:
        print(f"  {lbl:34s}: ₹{val:6.2f}L ({val / b['total_gross'] * 100:5.1f}%)")

    print("\n=== TOP 5 SENSITIVITY DRIVERS (1-WAY BASE NPV SWING) ===")
    for idx, item in enumerate(out["sensitivity"][:5], 1):
        print(
            f"  #{idx} {item['label']:40s} | NPV Low=₹{item['npv_at_low']:6.2f}L | "
            f"NPV High=₹{item['npv_at_high']:6.2f}L | Swing=₹{item['swing']:6.2f}L"
        )
    print(f"\nGenerated workbook: {WORKBOOK_PATH}")
    print(f"Generated charts:   {[str(p.name) for p in out['charts']]}")


if __name__ == "__main__":
    main()
