"""
Calculator module for BudgetDashboard.
Responsible for calculating budget execution rates and other metrics.
"""

import pandas as pd

def calculate_execution_rate(actual, budget):
    """
    Calculate budget execution rate.
    """
    if budget == 0:
        return 0
    return (actual / budget) * 100


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

    # Preserve department_name and college columns from budget_df
    summary = pd.merge(budget_df, expense_summary, on="系所代碼", how="outer")
    summary["核定經費"] = summary["核定經費"].fillna(0.0)
    summary["執行金額"] = summary["執行金額"].fillna(0.0)
    summary["執行率(%)"] = summary.apply(
        lambda row: calculate_execution_rate(row["執行金額"], row["核定經費"]), axis=1
    )

    if "系所中文名稱" in summary.columns:
        summary["系所中文名稱"] = (
            summary["系所中文名稱"].fillna("").replace("", "未建立對照")
        )

    # Fill missing department_name and college for departments not in budget
    if 'department_name' in summary.columns:
        summary['department_name'] = summary['department_name'].fillna('未知系統')
    if 'college' in summary.columns:
        summary['college'] = summary['college'].fillna('未知學院')

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
    # Add department_name and college to total row if they exist in summary
    if "系所中文名稱" in summary.columns:
        total_row_data["系所中文名稱"] = ""
    if 'department_name' in summary.columns:
        total_row_data["department_name"] = ""
    if 'college' in summary.columns:
        total_row_data["college"] = ""

    total_row = pd.DataFrame([total_row_data])

    return pd.concat([summary, total_row], ignore_index=True)
