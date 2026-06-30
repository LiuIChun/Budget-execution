import csv
from pathlib import Path

def merge_data(source1, source2):
    """Merge two lists of dictionaries into a single list."""
    merged = []
    for row in source1:
        merged.append(row)
    for row in source2:
        merged.append(row)
    return merged

def load_and_merge(base_dir):
    """Load data from two CSV files and merge them."""
    data1 = []
    data2 = []
    
    # Load first source (114TSD00-15)
    csv1_path = Path(base_dir) / '114TSD00-15.csv'
    if csv1_path.exists():
        with open(csv1_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data1 = list(reader)
    
    # Load second source (115TSD00-8)
    csv2_path = Path(base_dir) / '115TSD00-8.csv'
    if csv2_path.exists():
        with open(csv2_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data2 = list(reader)
    
    return merge_data(data1, data2)