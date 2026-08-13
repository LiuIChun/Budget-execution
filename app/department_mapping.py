"""
Department mapping data.
Loaded from the department code mapping workbook.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_MAPPING_DIR = DATA_DIR / "11506"
MAPPING_FILE_NAME = "系所經費代碼與中文名稱對照表.xlsx"
MAPPING_FILE_PATTERN = "*系所*代碼*中文名稱*對照表*.xls*"
DEFAULT_MAPPING_FILE_PATH = DEFAULT_MAPPING_DIR / MAPPING_FILE_NAME
_MAPPING_CACHE = {}


def _mapping_candidates(directory):
    """Return possible mapping files under a directory in priority order."""
    directory = Path(directory)
    candidates = [directory / MAPPING_FILE_NAME]
    if directory.exists():
        candidates.extend(sorted(directory.glob(MAPPING_FILE_PATTERN)))

    unique_candidates = []
    seen = set()
    for path in candidates:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique_candidates.append(path)
    return unique_candidates


def find_department_mapping_file(month_dir=None):
    """Find the mapping file, preferring the selected month folder."""
    directories = []
    if month_dir:
        directories.append(Path(month_dir))
    directories.append(DEFAULT_MAPPING_DIR)

    for directory in directories:
        for path in _mapping_candidates(directory):
            if path.exists():
                return path
    return DEFAULT_MAPPING_FILE_PATH


def _load_department_mapping_file(mapping_file_path):
    """Load department mapping from an Excel file."""
    try:
        df = pd.read_excel(mapping_file_path)
    except Exception as e:
        print(f"Warning: Could not load department mapping from {mapping_file_path}: {e}")
        return {}
    
    # Expected columns: 學院, 系所, 帳號. Use the first three columns and ignore the rest.
    df = df.iloc[:, :3]
    df.columns = ["college_name", "department_name", "code"]
    
    # Remove rows where code is NaN
    df = df.dropna(subset=["code"])
    
    # Convert code to string, strip whitespace, and uppercase
    df["code"] = df["code"].astype(str).str.strip().str.upper()
    df["college_name"] = df["college_name"].fillna("").astype(str).str.strip()
    df["department_name"] = df["department_name"].fillna("").astype(str).str.strip()
    
    # Create dictionary mapping code to department info
    mapping = {}
    for _, row in df.iterrows():
        code = row["code"]
        mapping[code] = {
            "department_name": row["college_name"],
            "college": row["department_name"],
            "系所中文名稱": row["department_name"],
            "學院": row["college_name"],
            "code": code,
        }
    return mapping


def load_department_mapping(month_dir=None):
    """Load department mapping, preferring the selected month folder."""
    mapping_file_path = find_department_mapping_file(month_dir)
    try:
        stat = mapping_file_path.stat()
        cache_key = (str(mapping_file_path.resolve()), stat.st_mtime_ns, stat.st_size)
    except OSError:
        cache_key = (str(mapping_file_path), None, None)

    if cache_key not in _MAPPING_CACHE:
        _MAPPING_CACHE[cache_key] = _load_department_mapping_file(mapping_file_path)
    return _MAPPING_CACHE[cache_key]


def set_department_mapping_month(month_dir=None):
    """Set active mapping to the selected month's table, falling back to the default table."""
    global DEPARTMENT_MAPPING, DEPARTMENT_MAPPING_SOURCE
    DEPARTMENT_MAPPING_SOURCE = find_department_mapping_file(month_dir)
    DEPARTMENT_MAPPING = load_department_mapping(month_dir)
    return DEPARTMENT_MAPPING_SOURCE


# Load the default mapping once at module import.
DEPARTMENT_MAPPING_SOURCE = find_department_mapping_file()
DEPARTMENT_MAPPING = load_department_mapping()


def get_department_info(dept_code):
    """Get department information by department code."""
    if not dept_code:
        return None
    return DEPARTMENT_MAPPING.get(str(dept_code).upper())
