import csv
from pathlib import Path

def calculate_total(rows, column_name):
    """Calculate the total of a specific column."""
    total = 0.0
    for row in rows:
        if column_name in row and row[column_name]:
            try:
                total += float(row[column_name])
            except ValueError:
                pass
    return total

def calculate_average(rows, column_name):
    """Calculate the average of a specific column."""
    total = 0.0
    count = 0
    for row in rows:
        if column_name in row and row[column_name]:
            try:
                total += float(row[column_name])
                count += 1
            except ValueError:
                pass
    return total / count if count > 0 else 0.0

def calculate_execution_rate(rows, actual_column, budget_column):
    """Calculate the execution rate (actual / budget * 100)."""
    total_actual = 0.0
    total_budget = 0.0
    for row in rows:
        if actual_column in row and row[actual_column]:
            try:
                total_actual += float(row[actual_column])
            except ValueError:
                pass
        if budget_column in row and row[budget_column]:
            try:
                total_budget += float(row[budget_column])
            except ValueError:
                pass
    return (total_actual / total_budget * 100) if total_budget > 0 else 0.0