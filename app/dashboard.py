"""
Dashboard module for BudgetDashboard.
Main dashboard logic that ties together loader, parser, calculator, and exporter.
"""

from datetime import datetime

from .loader import find_month_dir, load_all_monthly_data
from .parser import parse_expense_detail, parse_approved_budget
from .calculator import summarize_execution
from .exporter import export_execution_report
from .settings import load_settings, save_settings, is_first_run
from .history import save_monthly_execution
from .department_mapping import set_department_mapping_month
from . import config

def run_dashboard():
    """
    Run the BudgetDashboard application.
    Execute the monthly budget execution pipeline.
    """
    # Check if this is the first run and show settings if needed
    if is_first_run():
        print("=== 第一次執行 BudgetDashboard ===")
        print("請設定以下參數（設定將會儲存，之後不需要再修改）：")
        
        settings = load_settings()
        
        # Get year setting
        year_input = input(f"年度 [{settings['year']}]: ").strip()
        if year_input:
            settings['year'] = year_input
        
        # Get data directory
        data_dir_input = input(f"每月資料夾位置 [{settings['data_dir']}]: ").strip()
        if data_dir_input:
            settings['data_dir'] = data_dir_input
        
        # Get output directory
        output_dir_input = input(f"匯出位置 [{settings['output_dir']}]: ").strip()
        if output_dir_input:
            settings['output_dir'] = output_dir_input
        
        # Get project codes
        project_codes_input = input(f"計畫代碼 (用逗號分隔) [{','.join(settings['project_codes'])}]: ").strip()
        if project_codes_input:
            settings['project_codes'] = [code.strip() for code in project_codes_input.split(',')]
        
        # Get department code length
        dept_len_input = input(f"系所代碼長度 [{settings['dept_code_length']}]: ").strip()
        if dept_len_input:
            try:
                settings['dept_code_length'] = int(dept_len_input)
                # Update pattern based on length
                if settings['dept_code_length'] == 4:
                    settings['dept_code_pattern'] = r"([A-Za-z]{2}\d{2})"
                else:
                    settings['dept_code_pattern'] = rf"([A-Za-z]{{{settings['dept_code_length']-2}}}\d{{{settings['dept_code_length']-2}}})"
            except ValueError:
                print("無效的長度，使用預設值")
        
        # Save settings
        if save_settings(settings):
            print("\n設定已儲存！")
        else:
            print("\n警告：設定儲存失敗")
    
    # Load settings for use in the dashboard
    settings = load_settings()
    
    print("BudgetDashboard 執行中...")
    print("流程: 讀取Excel -> 合併明細 -> 解析購案編號 -> 取4碼系所代碼 -> 對照核定經費 -> 統計執行金額 -> 計算執行率 -> 輸出Excel")

    try:
        month_input = input("請輸入月份資料夾（例如 11506，直接 Enter 代表抓最新）: ").strip()
        month = month_input if month_input else None

        month_dir = find_month_dir(month)
        mapping_file = set_department_mapping_month(month_dir)
        data = load_all_monthly_data(month_dir)

        merged_expense_df = data["merged_expense_df"]
        approved_budget_df = data["approved_budget_df"]

        parsed_expense_df = parse_expense_detail(merged_expense_df)
        parsed_budget_df = parse_approved_budget(approved_budget_df)

        summary_df = summarize_execution(parsed_expense_df, parsed_budget_df)

        output_name = f"budget_execution_{data['month']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = export_execution_report(summary_df, parsed_expense_df, output_name)

        # Save to history database
        save_monthly_execution(data['month'], summary_df)
        print(f"歷史資料已更新至資料庫: {config.DATABASE_PATH}")

        print(f"\n來源月份: {data['month']}")
        print(f"系所對照表: {mapping_file.name}")
        print("收支明細檔案:")
        for path in data["expense_files"]:
            print(f"- {path.name}")
        print(f"核定經費檔案: {data['approved_budget_file'].name}")
        print(f"\n輸出完成: {output_path}")
    except Exception as exc:
        print(f"\n流程失敗: {exc}")
