"""
Parser module for BudgetDashboard.
Responsible for parsing loaded data into a structured format.
"""

import re

import pandas as pd
import config


def _find_column(columns, candidates):
    """Find the first matching column by keyword candidates."""
    for candidate in candidates:
        for col in columns:
            if candidate in str(col):
                return col
    return None


def _to_number(value):
    """Convert numeric-like values to float."""
    if pd.isna(value):
        return 0.0
    text = str(value).strip().replace(",", "")
    if text in ("", "-", "--"):
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else 0.0


def _to_text(value):
    """Convert a cell value to stripped text."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _first_non_empty(values):
    """Return the first non-empty value in a group."""
    for value in values:
        text = _to_text(value)
        if text:
            return text
    return ""


def _extract_purchase_id(value):
    """Extract normalized purchase id text."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    # Keep common purchase-id characters only.
    return re.sub(r"[^A-Za-z0-9\-]", "", text)


def _extract_dept_code4(purchase_id):
    """Extract 4-digit department code from purchase id."""
    if not purchase_id:
        return ""
    # Prefer department code pattern from config.
    match = re.search(config.DEPT_CODE_PATTERN, purchase_id)
    if match:
        return match.group(1).upper()

    # Fallback to pure digits when present.
    match = re.search(r"(\d{4})", purchase_id)
    if match:
        return match.group(1)
    return purchase_id[:4].upper() if len(purchase_id) >= 4 else ""

def parse_expense_detail(df):
    """
    Parse expense detail DataFrame.
    """
    if df is None or df.empty:
        raise ValueError("收支明細資料為空")

    columns = df.columns.tolist()
    purchase_col = _find_column(columns, [config.PURCHASE_NO, "購案", "案號", "編號"])
    amount_col = _find_column(columns, [config.AMOUNT, "支出", "執行", "實付", "付款", "請購"])

    if not purchase_col:
        raise ValueError(f"收支明細找不到購案編號欄位，現有欄位: {columns}")
    if not amount_col:
        raise ValueError(f"收支明細找不到金額欄位，現有欄位: {columns}")

    parsed = pd.DataFrame()
    parsed["購案編號原始"] = df[purchase_col]
    parsed["購案編號"] = parsed["購案編號原始"].apply(_extract_purchase_id)
    parsed["系所代碼"] = parsed["購案編號"].apply(_extract_dept_code4)
    parsed["執行金額"] = df[amount_col].apply(_to_number)

    parsed = parsed[parsed["系所代碼"] != ""].copy()
    parsed = parsed[parsed["執行金額"] != 0].copy()
    return parsed

def parse_approved_budget(df):
    """
    Parse approved budget DataFrame.
    """
    if df is None or df.empty:
        raise ValueError("核定經費資料為空")

    columns = df.columns.tolist()
    dept_col = _find_column(columns, ["帳號", "系所代碼", "單位代碼", "部門代碼", "代碼"])
    dept_name_col = _find_column(columns, ["系所中文名稱", "系所名稱", "系所", "單位名稱", "部門名稱"])
    budget_col = _find_column(columns, ["兩期合計", "核定經費", "核定預算", "預算", "核定金額", "經費"])

    if not dept_col:
        raise ValueError(f"核定經費找不到系所欄位，現有欄位: {columns}")
    if not budget_col:
        raise ValueError(f"核定經費找不到金額欄位，現有欄位: {columns}")

    parsed = pd.DataFrame()
    parsed["系所代碼"] = df[dept_col].apply(_to_text).str.upper().str[:4]
    if dept_name_col and dept_name_col != dept_col:
        parsed["系所中文名稱"] = df[dept_name_col].apply(_to_text)
    parsed["核定經費"] = df[budget_col].apply(_to_number)

    parsed = parsed[parsed["系所代碼"] != ""].copy()
    agg_rules = {"核定經費": "sum"}
    if "系所中文名稱" in parsed.columns:
        agg_rules["系所中文名稱"] = _first_non_empty
    parsed = parsed.groupby("系所代碼", as_index=False).agg(agg_rules)

    preferred_columns = ["系所代碼", "系所中文名稱", "核定經費"]
    parsed = parsed[[col for col in preferred_columns if col in parsed.columns]]
    return parsed
