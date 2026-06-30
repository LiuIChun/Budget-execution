import csv
from datetime import datetime
from pathlib import Path
import pandas as pd
from app.department_mapping import get_department_info

def parse_rows(rows):
    """Parse CSV rows into structured data with proper types."""
    parsed = []
    for row in rows:
        # Convert date string to datetime object
        if 'date' in row and row['date']:
            try:
                # Handle different date formats
                date_str = row['date'].strip()
                if '/' in date_str:
                    row['date'] = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                elif '-' in date_str:
                    row['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    row['date'] = None
            except ValueError:
                row['date'] = None  # Handle invalid dates
        # Convert amount to float
        if 'amount' in row and row['amount']:
            try:
                row['amount'] = float(row['amount'])
            except ValueError:
                row['amount'] = 0.0
        parsed.append(row)
    return parsed

def load_and_parse(file_path):
    """Load CSV file and parse its data."""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return parse_rows(rows)

def parse_expense_detail(expense_df):
    """
    Parse expense detail data from merged expense DataFrame.
    Expected columns: 購案編號, 金額, 費用說明, 日期
    """
    parsed_rows = []
    for _, row in expense_df.iterrows():
        parsed_row = {
            'expense_id': row.get('購案編號', ''),
            'amount': float(row.get('金額', 0)) if pd.notnull(row.get('金額', 0)) else 0.0,
            'description': row.get('費用說明', ''),
            'date': row.get('日期', '')
        }
        # Parse date
        if parsed_row['date']:
            try:
                if '/' in parsed_row['date']:
                    parsed_row['date'] = datetime.datetime.strptime(parsed_row['date'], '%Y/%m/%d')
                elif '-' in parsed_row['date']:
                    parsed_row['date'] = datetime.datetime.strptime(parsed_row['date'], '%Y-%m-%d')
            except ValueError:
                parsed_row['date'] = None
        parsed_rows.append(parsed_row)
    return parsed_rows

def parse_approved_budget(budget_df):
    """
    Parse approved budget data and map department codes to names.
    Expected columns: 帳號, 各類經費, 核定經費
    """
    parsed_rows = []
    for _, row in budget_df.iterrows():
        dept_code = str(row.get('帳號', '')).strip()
        expense_type = row.get('各類經費', '')
        budget_amount = float(row.get('核定經費', 0)) if pd.notnull(row.get('核定經費', 0)) else 0.0
        
        # Get department information from mapping
        dept_info = get_department_info(dept_code)
        if dept_info:
            department_name = dept_info['department_name']
            college = dept_info['college']
        else:
            # Fallback if department code not found
            department_name = f"未知系統({dept_code})"
            college = "未知學院"
        
        parsed_row = {
            'department_code': dept_code,
            'department_name': department_name,
            'college': college,
            'expense_type': expense_type,
            'budget_amount': budget_amount
        }
        parsed_rows.append(parsed_row)
    return parsed_rows
from datetime import datetime
from pathlib import Path
import pandas as pd
from app.department_mapping import get_department_info

def parse_rows(rows):
    """Parse CSV rows into structured data with proper types."""
    parsed = []
    for row in rows:
        # Convert date string to datetime object
        if 'date' in row and row['date']:
            try:
                # Handle different date formats
                date_str = row['date'].strip()
                if '/' in date_str:
                    row['date'] = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                elif '-' in date_str:
                    row['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    row['date'] = None
            except ValueError:
                row['date'] = None  # Handle invalid dates
        # Convert amount to float
        if 'amount' in row and row['amount']:
            try:
                row['amount'] = float(row['amount'])
            except ValueError:
                row['amount'] = 0.0
        parsed.append(row)
    return parsed

def load_and_parse(file_path):
    """Load CSV file and parse its data."""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return parse_rows(rows)

def parse_expense_detail(expense_df):
    """
    Parse expense detail data from merged expense DataFrame.
    Expected columns: 購案編號, 金額, 費用說明, 日期
    """
    parsed_rows = []
    for _, row in expense_df.iterrows():
        parsed_row = {
            'expense_id': row.get('購案編號', ''),
            'amount': float(row.get('金額', 0)) if pd.notnull(row.get('金額', 0)) else 0.0,
            'description': row.get('費用說明', ''),
            'date': row.get('日期', '')
        }
        # Parse date
        if parsed_row['date']:
            try:
                if '/' in parsed_row['date']:
                    parsed_row['date'] = datetime.datetime.strptime(parsed_row['date'], '%Y/%m/%d')
                elif '-' in parsed_row['date']:
                    parsed_row['date'] = datetime.datetime.strptime(parsed_row['date'], '%Y-%m-%d')
            except ValueError:
                parsed_row['date'] = None
        parsed_rows.append(parsed_row)
    return parsed_rows

def parse_approved_budget(budget_df):
    """
    Parse approved budget data and map department codes to names.
    Expected columns: 帳號, 各類經費, 核定經費
    """
    parsed_rows = []
    for _, row in budget_df.iterrows():
        dept_code = str(row.get('帳號', '')).strip()
        expense_type = row.get('各類經費', '')
        budget_amount = float(row.get('核定經費', 0)) if pd.notnull(row.get('核定經費', 0)) else 0.0
        
        # Get department information from mapping
        dept_info = get_department_info(dept_code)
        if dept_info:
            department_name = dept_info['department_name']
            college = dept_info['college']
        else:
            # Fallback if department code not found
            department_name = f"未知系統({dept_code})"
            college = "未知學院"
        
        parsed_row = {
            'department_code': dept_code,
            'department_name': department_name,
            'college': college,
            'expense_type': expense_type,
            'budget_amount': budget_amount
        }
        parsed_rows.append(parsed_row)
    return parsed_rows