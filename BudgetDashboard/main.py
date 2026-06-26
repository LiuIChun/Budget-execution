"""
Main entry point for the BudgetDashboard application.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent / "app"))

from app.dashboard import run_dashboard

def main():
    """Run the BudgetDashboard application."""
    print("Starting BudgetDashboard...")
    run_dashboard()

if __name__ == "__main__":
    main()