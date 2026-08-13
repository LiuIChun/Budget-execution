"""
History module for BudgetDashboard.
Handles storing and retrieving historical execution data.
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add the app directory to the path so we can import config
sys.path.append(str(Path(__file__).parent))
from . import config

def init_history_db():
    """Initialize the history database table if it doesn't exist."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_execution (
            month TEXT,
            dept_code TEXT,
            budget REAL,
            actual REAL,
            execution_rate REAL,
            PRIMARY KEY (month, dept_code)
        )
    ''')
    conn.commit()
    conn.close()

def save_monthly_execution(month, summary_df):
    """
    Save or update monthly execution data for all departments.
    
    Args:
        month (str): Month identifier (e.g., '11506')
        summary_df (pd.DataFrame): DataFrame with columns ['系所代碼', '核定經費', '執行金額', '執行率(%)']
    """
    init_history_db()
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    for _, row in summary_df.iterrows():
        dept_code = row['系所代碼']
        # Skip the total row if present
        if dept_code == '合計':
            continue
        budget = float(row['核定經費'])
        actual = float(row['執行金額'])
        execution_rate = float(row['執行率(%)'])
        
        cursor.execute('''
            INSERT OR REPLACE INTO monthly_execution 
            (month, dept_code, budget, actual, execution_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (month, dept_code, budget, actual, execution_rate))
    
    conn.commit()
    conn.close()

def load_history(dept_code=None):
    """
    Load historical execution data.
    
    Args:
        dept_code (str, optional): If provided, filter by department code.
        
    Returns:
        pd.DataFrame: Columns [month, dept_code, budget, actual, execution_rate]
    """
    init_history_db()
    conn = sqlite3.connect(config.DATABASE_PATH)
    
    if dept_code:
        query = "SELECT month, dept_code, budget, actual, execution_rate FROM monthly_execution WHERE dept_code = ? ORDER BY month"
        df = pd.read_sql_query(query, conn, params=(dept_code,))
    else:
        query = "SELECT month, dept_code, budget, actual, execution_rate FROM monthly_execution ORDER BY month, dept_code"
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

def get_available_months():
    """Get list of all months with historical data."""
    init_history_db()
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT month FROM monthly_execution ORDER BY month")
    months = [row[0] for row in cursor.fetchall()]
    conn.close()
    return months
