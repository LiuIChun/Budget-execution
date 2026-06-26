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

    summary = pd.merge(budget_df, expense_summary, on="系所代碼", how="outer")
    summary["核定經費"] = summary["核定經費"].fillna(0.0)
    summary["執行金額"] = summary["執行金額"].fillna(0.0)
    summary["執行率(%)"] = summary.apply(
        lambda row: calculate_execution_rate(row["執行金額"], row["核定經費"]), axis=1
    )

    summary = summary.sort_values("系所代碼").reset_index(drop=True)

    total_budget = summary["核定經費"].sum()
    total_actual = summary["執行金額"].sum()
    total_rate = calculate_execution_rate(total_actual, total_budget)

    total_row = pd.DataFrame(
        [
            {
                "系所代碼": "合計",
                "核定經費": total_budget,
                "執行金額": total_actual,
                "執行率(%)": total_rate,
            }
        ]
    )

    return pd.concat([summary, total_row], ignore_index=True)