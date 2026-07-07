"""
Department mapping data.
Loaded from the department code mapping workbook.
"""

import pandas as pd
from pathlib import Path

# Path to the department mapping Excel file
MAPPING_FILE_PATH = Path(__file__).parent.parent / "data" / "11506" / "系所經費代碼與中文名稱對照表.xlsx"

def _load_department_mapping():
    """Load department mapping from Excel file."""
    try:
        df = pd.read_excel(MAPPING_FILE_PATH)
    except Exception as e:
        print(f"Warning: Could not load department mapping from {MAPPING_FILE_PATH}: {e}")
        return {}
    
    # Expected columns: 學院, 系所, 帳號, Unnamed: 3
    # We'll use the first three columns and ignore the rest.
    # Rename columns for clarity
    df = df.iloc[:, :3]  # Take only first three columns
    df.columns = ["college", "department_name", "code"]
    
    # Remove rows where code is NaN
    df = df.dropna(subset=["code"])
    
    # Convert code to string, strip whitespace, and uppercase
    df["code"] = df["code"].astype(str).str.strip().str.upper()
    
    # Create dictionary mapping code to department info
    mapping = {}
    for _, row in df.iterrows():
        code = row["code"]
        mapping[code] = {
            "department_name": row["department_name"],
            "college": row["college"],
            "code": code
        }
    return mapping

# Load the mapping once at module import
DEPARTMENT_MAPPING = _load_department_mapping()


def get_department_info(dept_code):
    """Get department information by department code."""
    if not dept_code:
        return None
    return DEPARTMENT_MAPPING.get(str(dept_code).upper())
