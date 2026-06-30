import csv
from pathlib import Path

def load_csv(file_path):
    """Load CSV file and return list of rows (dict)."""
    rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def load_all_data(base_dir):
    """Load all CSV files from base_dir and return combined list."""
    data = []
    for csv_file in Path(base_dir).glob('*.csv'):
        data.extend(load_csv(str(csv_file)))
    return data