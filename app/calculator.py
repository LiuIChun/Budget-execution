"""
Calculator module for BudgetDashboard.
Responsible for calculating budget execution rates and other metrics.
"""

import pandas as pd
from . import config
from .department_mapping import get_department_info


# Department codes that must be reported as one department.  The display name
# is the primary department name, without the parenthetical legacy-program tag.
DEPARTMENT_ALIAS_GROUPS = {
    "GB00": ("GB00/US19", "漁業科技與管理系"),
    "US19": ("GB00/US19", "漁業科技與管理系"),
    "UO04": ("UO04/YE00", "海洋休閒管理系"),
    "YE00": ("UO04/YE00", "海洋休閒管理系"),
}


def category_budget_columns():
    """Return category budget column names in display order."""
    return [f"{category}核定" for category in config.EXPENSE_CATEGORIES]


def category_actual_columns():
    """Return category actual column names in display order."""
    return [f"{category}執行金額" for category in config.EXPENSE_CATEGORIES]


def category_summary_columns():
    """Return paired category budget and actual columns."""
    columns = []
    for category in config.EXPENSE_CATEGORIES:
        columns.extend([f"{category}核定", f"{category}執行金額"])
    return columns


def calculate_execution_rate(actual, budget):
    """
    Calculate budget execution rate.
    """
    if budget == 0:
        return 0
    return (actual / budget) * 100


def get_department_chinese_name(dept_code):
    """Return the mapped Chinese department name for a department code."""
    dept_info = get_department_info(dept_code)
    if not dept_info:
        return ""
    return dept_info.get("系所中文名稱") or dept_info.get("college") or ""


def first_non_empty(values):
    """Return the first non-empty value in a grouped column."""
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def join_department_codes(values):
    """Join unique department codes in a stable display order."""
    codes = sorted({str(value).strip() for value in values if str(value).strip()})
    return "/".join(codes)


def get_department_alias(dept_code):
    """Return the reporting group and primary name for a department alias."""
    return DEPARTMENT_ALIAS_GROUPS.get(str(dept_code).strip().upper())


def primary_department_chinese_name(row):
    """Use the configured primary name for a merged department group."""
    alias = get_department_alias(row["系所代碼"])
    if alias:
        return alias[1]
    return row["系所中文名稱"]


def make_department_group_key(row):
    """Group known aliases by Chinese name and unknown departments by code."""
    alias = get_department_alias(row["系所代碼"])
    if alias:
        return f"alias:{alias[0]}"

    dept_name = str(row["系所中文名稱"]).strip()
    if dept_name and dept_name != "未建立對照":
        return f"name:{dept_name}"
    return f"code:{row['系所代碼']}"


def summarize_category_execution(expense_df):
    """Summarize execution amount by department and budget category."""
    if "經費項目" not in expense_df.columns:
        return pd.DataFrame(columns=["系所代碼"] + category_actual_columns())

    category_expense_df = expense_df[
        expense_df["經費項目"].isin(config.EXPENSE_CATEGORIES)
    ].copy()
    if category_expense_df.empty:
        return pd.DataFrame(columns=["系所代碼"] + category_actual_columns())

    category_summary = category_expense_df.pivot_table(
        index="系所代碼",
        columns="經費項目",
        values="執行金額",
        aggfunc="sum",
        fill_value=0.0,
    ).reset_index()
    category_summary.columns.name = None

    rename_columns = {
        category: f"{category}執行金額"
        for category in config.EXPENSE_CATEGORIES
        if category in category_summary.columns
    }
    category_summary = category_summary.rename(columns=rename_columns)
    for col in category_actual_columns():
        if col not in category_summary.columns:
            category_summary[col] = 0.0

    return category_summary[["系所代碼"] + category_actual_columns()]


def summarize_execution(expense_df, budget_df):
    """Summarize execution amount and execution rate by department."""
    if expense_df is None or expense_df.empty:
        raise ValueError("無可用的收支明細資料")
    if budget_df is None or budget_df.empty:
        raise ValueError("無可用的核定經費資料")

    expense_summary = (
        expense_df.groupby("系所代碼", as_index=False)["執行金額"].sum()
        .rename(columns={"執行金額": "執行金額"})
    )
    expense_category_summary = summarize_category_execution(expense_df)
    expense_summary = pd.merge(
        expense_summary, expense_category_summary, on="系所代碼", how="left"
    )

    # Preserve department_name and college columns from budget_df
    summary = pd.merge(budget_df, expense_summary, on="系所代碼", how="outer")
    summary["核定經費"] = summary["核定經費"].fillna(0.0)
    summary["執行金額"] = summary["執行金額"].fillna(0.0)
    for col in category_budget_columns() + category_actual_columns():
        if col not in summary.columns:
            summary[col] = 0.0
        summary[col] = summary[col].fillna(0.0)
    summary["執行率(%)"] = summary.apply(
        lambda row: calculate_execution_rate(row["執行金額"], row["核定經費"]), axis=1
    )

    if "系所中文名稱" not in summary.columns:
        summary["系所中文名稱"] = ""
    summary["系所中文名稱"] = summary["系所中文名稱"].fillna("")
    missing_name_mask = summary["系所中文名稱"] == ""
    summary.loc[missing_name_mask, "系所中文名稱"] = summary.loc[
        missing_name_mask, "系所代碼"
    ].apply(get_department_chinese_name)
    summary["系所中文名稱"] = summary["系所中文名稱"].replace("", "未建立對照")
    summary["系所中文名稱"] = summary.apply(
        primary_department_chinese_name, axis=1
    )

    if 'department_name' in summary.columns:
        summary['department_name'] = summary['department_name'].fillna('未知系統')
    if 'college' in summary.columns:
        summary['college'] = summary['college'].fillna('未知學院')

    summary["_department_group_key"] = summary.apply(make_department_group_key, axis=1)
    agg_rules = {
        "系所代碼": join_department_codes,
        "系所中文名稱": first_non_empty,
        "核定經費": "sum",
        "執行金額": "sum",
    }
    for col in category_budget_columns() + category_actual_columns():
        agg_rules[col] = "sum"
    if "department_name" in summary.columns:
        agg_rules["department_name"] = first_non_empty
    if "college" in summary.columns:
        agg_rules["college"] = first_non_empty
    summary = summary.groupby("_department_group_key", as_index=False).agg(agg_rules)
    summary["執行率(%)"] = summary.apply(
        lambda row: calculate_execution_rate(row["執行金額"], row["核定經費"]), axis=1
    )
    summary = summary.drop(columns=["_department_group_key"])

    summary = summary.sort_values("系所代碼").reset_index(drop=True)

    total_budget = summary["核定經費"].sum()
    total_actual = summary["執行金額"].sum()
    total_rate = calculate_execution_rate(total_actual, total_budget)

    # Create total row with placeholder values for department_name and college
    total_row_data = {
        "系所代碼": "合計",
        "核定經費": total_budget,
        "執行金額": total_actual,
        "執行率(%)": total_rate,
    }
    for col in category_budget_columns() + category_actual_columns():
        total_row_data[col] = summary[col].sum()
    # Add department_name and college to total row if they exist in summary
    if "系所中文名稱" in summary.columns:
        total_row_data["系所中文名稱"] = ""
    if 'department_name' in summary.columns:
        total_row_data["department_name"] = ""
    if 'college' in summary.columns:
        total_row_data["college"] = ""

    total_row = pd.DataFrame([total_row_data])

    result = pd.concat([summary, total_row], ignore_index=True)
    preferred_columns = [
        "系所代碼",
        "系所中文名稱",
        "核定經費",
        "執行金額",
        "執行率(%)",
    ] + category_summary_columns()
    ordered_columns = [col for col in preferred_columns if col in result.columns]
    ordered_columns += [col for col in result.columns if col not in ordered_columns]
    return result[ordered_columns]
