"""
Settings module for BudgetDashboard.
Handles user-configurable settings that persist between runs.
"""

import json
import os
from pathlib import Path

# Settings file path
SETTINGS_FILE = Path(__file__).parent.parent / "user_settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "year": "115",
    "data_dir": str(Path(__file__).parent.parent / "data"),
    "output_dir": str(Path(__file__).parent.parent / "output"),
    "project_codes": ["114TSD00-15", "115TSD00-8"],
    "dept_code_length": 4,
    "dept_code_pattern": r"([A-Za-z]{2}\d{2})"  # e.g., UC45, SD00
}

def load_settings():
    """Load user settings from file, or return defaults if file doesn't exist."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = DEFAULT_SETTINGS.copy()
                merged.update(settings)
                return merged
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, return defaults
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save user settings to file."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def reset_to_defaults():
    """Reset settings to default values."""
    return save_settings(DEFAULT_SETTINGS.copy())

def is_first_run():
    """Check if this is the first run (settings file doesn't exist)."""
    return not SETTINGS_FILE.exists()