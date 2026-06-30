"""
Create test data for BudgetDashboard testing.
生成測試用的Excel檔案（實際為CSV格式，可被Excel開啟）
"""

import pandas as pd
import os
from pathlib import Path

def create_test_data():
    """Create sample expense and budget data for testing."""
    
    # Create data directory if it doesn't exist
    data_dir = Path("data/11506")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample expense data for project 114TSD00-15
    expense_data_1 = {
        '購案編號': ['114TSD00-15-001', '114TSD00-15-002', '114TSD00-15-003', '115TSD00-8-001', '115TSD00-8-002'],
        '金額': [150000, 200000, 75000, 300000, 125000],
        '費用說明': ['辦公用品', '軟體授權', '維修費用', '會議費用', '交通費用'],
        '日期': ['2026/06/01', '2026/06/05', '2026/06/10', '2026/06/12', '2026/06/15']
    }
    
    # Sample expense data for project 115TSD00-8
    expense_data_2 = {
        '購案編號': ['114TSD00-15-004', '114TSD00-15-005', '115TSD00-8-003', '115TSD00-8-004', '115TSD00-8-005'],
        '金額': [100000, 175000, 225000, 180000, 95000],
        '費用說明': ['員工培訓', '設備購買', '場地租金', '宣傳費用', '其他費用'],
        '日期': ['2026/06/03', '2026/06/08', '2026/06/14', '2026/06/18', '2026/06/20']
    }
    
    # Sample approved budget data
    budget_data = {
        '帳號': ['UC45', 'SD00', 'UC11', 'UB00', 'UD01', 'UE15', 'UF02'],
        '各類經費': ['一般行政費', '業務費', '研究發展費', '設備投資', '員工福利', '訓練教育', '其他費用'],
        '核定經費': [2000000, 1800000, 1500000, 3000000, 800000, 1200000, 2500000]
    }
    
    # Create DataFrames
    df_expense_1 = pd.DataFrame(expense_data_1)
    df_expense_2 = pd.DataFrame(expense_data_2)
    df_budget = pd.DataFrame(budget_data)
    
    # Save as CSV (Excel can open CSV files)
    df_expense_1.to_csv(data_dir / "1150615_114TSD00-15收支明細.csv", index=False, encoding='utf-8-sig')
    df_expense_2.to_csv(data_dir / "1150615_115TSD00-8收支明細.csv", index=False, encoding='utf-8-sig')
    df_budget.to_csv(data_dir / "各系核定經費及各類經費明細與系所代碼.csv", index=False, encoding='utf-8-sig')
    
    print("✅ 測試資料已建立在:", data_dir.absolute())
    print("📁 檔案列表:")
    for file in data_dir.iterdir():
        print(f"   - {file.name}")
    
    print("\n📝 註記：")
    print("   - 這些是CSV檔案，Excel可以直接開啟")
    print("   - 如果需要真正的Excel (.xlsx) 檔案，請在Excel中開啟後另存為 .xlsx 格式")
    print("   - 資料包含兩個專案的收支明細和各系所的核定經費")
    print("   - 系所代碼從購案編號中可提取：UC45, SD00, UC11, UB00, UD01, UE15, UF02 等")

if __name__ == "__main__":
    create_test_data()