"""
Configuration module for BudgetDashboard.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_DIR = BASE_DIR / "database"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database file
DATABASE_PATH = DATABASE_DIR / "budget.db"

# File patterns or specific files (if known)
# Example: 
# EXPENSE_DETAIL_PATTERN = "*-收支明細.xlsx"
# APPROVED_BUDGET_FILE = "各系核定經費.xlsx"

# Column name configurations (can be adjusted per year/format)
PURCHASE_NO = "購案編號"
AMOUNT = "金額"
ACCOUNT_CODE = "帳號"

# Expected project codes for validation/filtering
PROJECT_FILES = [
    "114TSD00-15",
    "115TSD00-8"
]

# Department code extraction pattern
DEPT_CODE_PATTERN = r"([A-Za-z]{2}\d{2})"  # e.g., UC45, SD00

# You can add more configuration as needed