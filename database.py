import sqlite3
from pathlib import Path

def init_db(db_path):
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT,
            category TEXT
        )
    ''')
    
    # Create execution table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            actual_amount REAL NOT NULL,
            budget REAL NOT NULL,
            execution_date TEXT,
            category TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection(db_path):
    """Get database connection."""
    return sqlite3.connect(db_path)

def insert_budget(conn, item, amount, date, category):
    """Insert budget record."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budget (item, amount, date, category)
        VALUES (?, ?, ?, ?)
    ''', (item, amount, date, category))
    conn.commit()

def insert_execution(conn, item, actual_amount, budget, execution_date, category):
    """Insert execution record."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO execution (item, actual_amount, budget, execution_date, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (item, actual_amount, budget, execution_date, category))
    conn.commit()

def calculate_total(conn, column, table, condition=None):
    """Calculate total for a column in a table."""
    cursor = conn.cursor()
    where_clause = "WHERE " + condition if condition else ""
    cursor.execute(f"SELECT SUM({column}) FROM {table} {where_clause}")
    result = cursor.fetchone()[0]
    return result or 0.0

def calculate_average(conn, column, table, condition=None):
    """Calculate average for a column in a table."""
    cursor = conn.cursor()
    where_clause = "WHERE " + condition if condition else ""
    cursor.execute(f"SELECT AVG({column}) FROM {table} {where_clause}")
    result = cursor.fetchone()[0]
    return result or 0.0

def calculate_execution_rate(conn, actual_column, budget_column, table, condition=None):
    """Calculate execution rate."""
    cursor = conn.cursor()
    where_clause = "WHERE " + condition if condition else ""
    cursor.execute(f"SELECT SUM({actual_column}), SUM({budget_column}) FROM {table} {where_clause}")
    total_actual, total_budget = cursor.fetchone()
    return (total_actual / total_budget * 100) if total_budget > 0 else 0.0