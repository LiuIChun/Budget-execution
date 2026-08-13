"""
Exporter module for BudgetDashboard.
Responsible for exporting data to Excel or other formats.
"""

import pandas as pd
from . import config

def export_to_excel(df, file_name):
    """
    Export DataFrame to Excel file in the output directory.
    """
    output_path = config.OUTPUT_DIR / file_name
    df.to_excel(output_path, index=False)
    return output_path


def export_execution_report(summary_df, detail_df, file_name):
    """Export execution report with summary and detail sheets."""
    output_path = config.OUTPUT_DIR / file_name

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="執行率總表", index=False)
        detail_df.to_excel(writer, sheet_name="明細資料", index=False)

    return output_path
