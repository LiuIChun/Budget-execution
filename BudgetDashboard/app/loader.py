"""
Loader module for BudgetDashboard.
Responsible for loading raw data from Excel files.
"""

import pandas as pd
from pathlib import Path
import config


def _read_excel(file_path):
    """Read an Excel file and return a DataFrame."""
    return pd.read_excel(file_path)


def _find_header_row(raw_df, required_keywords):
    """Find header row index containing all required keywords."""
    for idx in raw_df.index:
        row_values = [str(v).strip() for v in raw_df.loc[idx].tolist()]
        if all(any(keyword in value for value in row_values) for keyword in required_keywords):
            return idx
    return None


def _normalize_columns(columns):
    """Normalize columns to non-empty, unique names."""
    used = {}
    normalized = []
    for i, col in enumerate(columns):
        name = str(col).strip() if str(col).strip() and str(col) != "nan" else f"col_{i}"
        count = used.get(name, 0)
        if count:
            out = f"{name}_{count}"
        else:
            out = name
        used[name] = count + 1
        normalized.append(out)
    return normalized

def load_expense_detail(file_path):
    """
    Load expense detail Excel file.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"找不到收支明細檔案: {file_path}")

    raw_df = pd.read_excel(file_path, header=None)
    header_row = _find_header_row(raw_df, [config.PURCHASE_NO, config.AMOUNT])
    if header_row is None:
        raise ValueError(f"無法在收支明細找到表頭列（{config.PURCHASE_NO}/{config.AMOUNT}）: {file_path.name}")

    data_df = raw_df.iloc[header_row + 1 :].copy()
    data_df.columns = _normalize_columns(raw_df.iloc[header_row].tolist())
    data_df = data_df.dropna(how="all")
    return data_df

def load_approved_budget(file_path):
    """
    Load approved budget Excel file.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"找不到核定經費檔案: {file_path}")

    raw_df = pd.read_excel(file_path, header=None)
    header_row = _find_header_row(raw_df, [config.ACCOUNT_CODE])
    if header_row is None:
        raise ValueError(f"無法在核定經費找到表頭列（{config.ACCOUNT_CODE}）: {file_path.name}")

    data_df = raw_df.iloc[header_row + 1 :].copy()
    data_df.columns = _normalize_columns(raw_df.iloc[header_row].tolist())
    data_df = data_df.dropna(how="all")
    return data_df


def find_month_dir(month=None):
    """Return the target month directory under data/."""
    if month:
        month_path = config.DATA_DIR / str(month)
        if not month_path.exists():
            raise FileNotFoundError(f"找不到月份資料夾: {month_path}")
        return month_path

    month_dirs = sorted([p for p in config.DATA_DIR.iterdir() if p.is_dir()])
    if not month_dirs:
        raise FileNotFoundError("data/ 底下沒有任何月份資料夾")
    return month_dirs[-1]


def find_approved_budget_file(month_dir):
    """Find the budget workbook used to calculate a selected month.

    Prefer a workbook stored with that month's expense files.  Older month
    folders may contain expense snapshots only, so fall back to a shared
    workbook in data/ and then to the newest month folder that has one.
    """
    month_dir = Path(month_dir)

    search_dirs = [month_dir, config.DATA_DIR]
    other_month_dirs = sorted(
        (
            path
            for path in config.DATA_DIR.iterdir()
            if path.is_dir() and path != month_dir
        ),
        reverse=True,
    )
    search_dirs.extend(other_month_dirs)

    for directory in search_dirs:
        approved_files = sorted(directory.glob(config.BUDGET_FILE_PATTERN))
        if approved_files:
            return approved_files[0]

    raise ValueError(
        "找不到核定經費檔案（可放在所選月份資料夾、data/，"
        "或其他月份資料夾；檔名需包含『核定經費』）"
    )

def load_all_monthly_data(month_dir):
    """
    Load all data for a given month directory.
    """
    month_dir = Path(month_dir)
    if not month_dir.exists():
        raise FileNotFoundError(f"找不到月份資料夾: {month_dir}")

    expense_files = sorted(month_dir.glob("*收支明細*.xls*"))
    if len(expense_files) < 2:
        raise ValueError(
            f"{month_dir} 至少需要 2 份收支明細檔，實際找到 {len(expense_files)} 份"
        )

    approved_budget_file = find_approved_budget_file(month_dir)

    expense_dfs = [load_expense_detail(path) for path in expense_files]
    merged_expense_df = pd.concat(expense_dfs, ignore_index=True)
    approved_budget_df = load_approved_budget(approved_budget_file)

    return {
        "month": month_dir.name,
        "month_dir": month_dir,
        "expense_files": expense_files,
        "approved_budget_file": approved_budget_file,
        "merged_expense_df": merged_expense_df,
        "approved_budget_df": approved_budget_df,
    }
