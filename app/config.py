from pathlib import Path

# ===== 系統設定 =====
APP_NAME = "BudgetDashboard"
APP_TITLE = "預算執行管理系統"

# ===== 基礎路徑 =====
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== 資料路徑 =====
DATA_FOLDER = "data"
MASTER_FOLDER = "data/master"
OUTPUT_FOLDER = "output"
DATABASE_FILE = "database/budget.db"

# Backward-compatible path objects used by loader/history/exporter.
DATA_DIR = BASE_DIR / DATA_FOLDER
OUTPUT_DIR = BASE_DIR / OUTPUT_FOLDER
DATABASE_PATH = BASE_DIR / DATABASE_FILE
DATABASE_DIR = DATABASE_PATH.parent

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# ===== 收支檔案 =====
PROJECT_FILES = [
    "114TSD00-15",
    "115TSD00-8"
]

# ===== 系所代碼 =====
DEPT_CODE_LENGTH = 4

# ===== Dashboard =====
PAGE_TITLE = "BudgetDashboard"
PAGE_ICON = "📊"

# ===== Excel =====
HEADER_COLOR = "#1F4E78"

# ===== 欄位名稱設定 =====
# These are the standard names we look for in the data
PURCHASE_NO = "購案"          # Purchase order number column name in expense data
AMOUNT = "金額"               # Amount column name in expense data
ACCOUNT_CODE = "帳號"         # Account code column name in budget data
DEPT_NAME_CH = "系所中文名稱" # Department name column name in budget data
BUDGET_AMOUNT = "兩期合計"    # Budget amount column name in budget data

# Budget/expense categories shown in the execution summary.
EXPENSE_CATEGORIES = ["業務費", "國外旅費", "無形資產", "設備費"]

# Regular expression pattern to extract department code from purchase order number
# Expected format: two uppercase letters followed by two digits (e.g., UH53, UE23)
# Capturing group 1 extracts the department code
DEPT_CODE_PATTERN = r'([A-Z]{2}\d{2})'

# File patterns for finding data files (used with glob)
EXPENSE_FILE_PATTERN = "*收支明細*.xls*"  # Matches both .xls and .xlsx files
BUDGET_FILE_PATTERN = "*核定經費*.xls*"   # Matches both .xls and .xlsx files

# Required supplemental snapshot for purchase orders created in ROC year 114.
# This workbook must be present in every published month directory in addition
# to the two regular monthly expense-detail workbooks.
REQUIRED_SUPPLEMENTAL_EXPENSE_FILE = "1150108_114TSD00-15收支明細.xlsx"
REGULAR_EXPENSE_FILE_COUNT = 2

# Default year/month for data processing (can be overridden)
DEFAULT_YEAR = "115"  # Republic of China year
DEFAULT_PERIODS = ["08", "15"]  # Example periods
