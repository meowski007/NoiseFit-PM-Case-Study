"""Tests verifying that Python financial outputs match the Excel workbook formulas,
all dynamic recalculations succeed with zero errors, and charts exist.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import openpyxl
import pytest
from xlcalculator import Evaluator, ModelCompiler

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "model"))

import business_case_model as bcm  # noqa: E402


EXCEL_ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}


def _eval_workbook(xlsx_path: Path) -> Evaluator:
    compiler = ModelCompiler()
    new_model = compiler.read_and_parse_archive(str(xlsx_path))
    return Evaluator(new_model)


def _find_row_by_label(ws, col: int, prefix: str) -> int:
    for r in range(1, ws.max_row + 1):
        v = ws.cell(row=r, column=col).value
        if isinstance(v, str) and v.startswith(prefix):
            return r
    raise AssertionError(f"Could not find label starting with {prefix!r} in sheet {ws.title}")


def test_charts_generated():
    for fname in ("scenario_comparison.png", "cashflow_projection.png", "sensitivity_tornado.png"):
        chart_path = bcm.IMAGES_DIR / fname
        assert chart_path.exists(), f"Missing chart: {chart_path}"
        assert chart_path.stat().st_size > 10_000, f"Chart unexpectedly small: {chart_path}"


def test_workbook_structure_and_real_formulas():
    wb = openpyxl.load_workbook(bcm.WORKBOOK_PATH, data_only=False)
    assert wb.sheetnames == ["Assumptions", "Calculations", "Scenarios", "Summary"]

    # Every key output cell in Summary & Scenarios must be an Excel formula starting with '='
    ws_sum = wb["Summary"]
    for prefix in [
        "Year 0 Upfront Investment",
        "Total 3-Year All-In Cost",
        "Total 3-Year Gross Value Delivered",
        "3-Year Net Benefit",
        "3-Year Lifecycle ROI",
        "Payback Period",
        "3-Year Net Present Value",
    ]:
        r = _find_row_by_label(ws_sum, 1, prefix)
        for col in (3, 4, 5):
            val = ws_sum.cell(row=r, column=col).value
            assert isinstance(val, str) and val.startswith("="), (
                f"Expected formula in Summary!R{r}C{col} ({prefix}), got {val!r}"
            )


def test_python_matches_excel_formulas_and_no_errors():
    py_out = bcm.run_all(write_outputs=False)
    wb = openpyxl.load_workbook(bcm.WORKBOOK_PATH, data_only=False)
    ev = _eval_workbook(bcm.WORKBOOK_PATH)

    # Scan all cells across Calculations, Scenarios, Summary for Excel formula errors
    for sheet_name in ("Calculations", "Scenarios", "Summary"):
        ws = wb[sheet_name]
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                raw = ws.cell(row=r, column=c).value
                if isinstance(raw, str) and raw.startswith("="):
                    coord = f"{sheet_name}!{openpyxl.utils.get_column_letter(c)}{r}"
                    evaluated = ev.evaluate(coord)
                    assert str(evaluated) not in EXCEL_ERRORS, f"Excel error at {coord}: {evaluated}"

    # Verify Summary sheet Low/Base/High outputs match Python computations closely
    ws_sum = wb["Summary"]
    metric_map = {
        "Year 0 Upfront Investment": "y0_investment",
        "Total 3-Year All-In Cost": "total_costs",
        "Total 3-Year Gross Value Delivered": "total_gross",
        "3-Year Net Benefit": "net_benefit_3yr",
        "3-Year Lifecycle ROI": "lifecycle_roi",
        "Payback Period": "payback_months",
        "3-Year Net Present Value": "npv",
    }
    scen_cols = {"low": "C", "base": "D", "high": "E"}

    for prefix, py_key in metric_map.items():
        r = _find_row_by_label(ws_sum, 1, prefix)
        for scen, col_letter in scen_cols.items():
            excel_val = ev.evaluate(f"Summary!{col_letter}{r}")
            py_val = py_out["results"][scen][py_key]
            if py_val is None:
                assert str(excel_val) == "N/A (>36 mo)"
            else:
                assert math.isclose(float(excel_val), float(py_val), rel_tol=1e-6, abs_tol=1e-4), (
                    f"Mismatch for {scen} {py_key}: Excel={excel_val}, Python={py_val}"
                )

    # Verify Scenarios Tornado NPV rows match Python 1-way sensitivity
    ws_scen = wb["Scenarios"]
    for idx, item in enumerate(py_out["sensitivity"], 1):
        r = _find_row_by_label(ws_scen, 1, f"#{idx}: ")
        xl_low = float(ev.evaluate(f"Scenarios!F{r}"))
        xl_high = float(ev.evaluate(f"Scenarios!G{r}"))
        xl_swing = float(ev.evaluate(f"Scenarios!H{r}"))
        assert math.isclose(xl_low, item["npv_at_low"], abs_tol=1e-3)
        assert math.isclose(xl_high, item["npv_at_high"], abs_tol=1e-3)
        assert math.isclose(xl_swing, item["swing"], abs_tol=1e-3)


def test_changing_assumption_updates_excel_outputs(tmp_path: Path):
    """Mutating an editable Assumption input must dynamically update Base NPV."""
    wb = openpyxl.load_workbook(bcm.WORKBOOK_PATH, data_only=False)
    ws_assump = wb["Assumptions"]
    ws_sum = wb["Summary"]

    base_ev = _eval_workbook(bcm.WORKBOOK_PATH)
    npv_row = _find_row_by_label(ws_sum, 1, "3-Year Net Present Value")
    orig_base_npv = float(base_ev.evaluate(f"Summary!D{npv_row}"))

    # Double ticket_deflection_rate Base Case (from 0.25 -> 0.50) in temp copy
    target_row = _find_row_by_label(ws_assump, 1, "ticket_deflection_rate")
    ws_assump.cell(row=target_row, column=6).value = 0.50
    mutated_path = tmp_path / "mutated.xlsx"
    wb.save(mutated_path)

    mut_ev = _eval_workbook(mutated_path)
    new_base_npv = float(mut_ev.evaluate(f"Summary!D{npv_row}"))
    assert new_base_npv > orig_base_npv + 100.0
