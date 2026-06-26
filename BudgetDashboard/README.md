# BudgetDashboard

A tool to track and analyze budget execution by processing monthly Excel files and generating insights.

## Project Structure

```
BudgetDashboard/
│
├── data/                  # 每月放原始Excel
│   ├── 11506/
│   │   ├── 114TSD00-15收支明細.xlsx
│   │   ├── 115TSD00-8收支明細.xlsx
│   │   └── 各系核定經費.xlsx
│   └── 11507/
│
├── output/                # 自動產生的Excel
│
├── database/              # SQLite資料庫
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── loader.py
│   ├── parser.py
│   ├── calculator.py
│   ├── exporter.py
│   └── dashboard.py
│
├── main.py
├── requirements.txt
└── README.md
```

## Description

This project is designed to:
1. Load monthly budget and expense data from Excel files.
2. Parse and structure the data for analysis.
3. Calculate budget execution rates and other financial metrics.
4. Store processed data in a SQLite database for historical tracking.
5. Generate reports and export results to Excel.

## Current Processing Flow

The command-line pipeline now implements the following flow:

1. 讀取三份Excel
2. 合併兩個收支明細
3. 解析購案編號
4. 取得4碼系所代碼
5. 對照核定經費
6. 統計各系所執行金額
7. 計算執行率
8. 輸出Excel

## Input File Rules

- Place files under a month folder, for example `data/11506/`.
- Expense detail files: file name contains `收支明細` (at least two files).
- Approved budget file: file name contains `核定經費` (one file).
- If no month is typed at runtime, the newest month folder under `data/` is used.

## Modules

- **config.py**: Manages directory paths and configuration settings.
- **loader.py**: Loads raw data from Excel files using pandas.
- **parser.py**: Parses loaded data into a structured format suitable for analysis.
- **calculator.py**: Calculates budget execution rates and other metrics.
- **exporter.py**: Exports processed data to Excel or other formats.
- **dashboard.py**: Main dashboard logic that orchestrates the workflow.

## Setup

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your monthly Excel files in the appropriate subdirectories under `data/` (e.g., `data/11506/` for June 2026 data).
4. Run the main script:
   ```bash
   python main.py
   ```

## Dependencies

- pandas>=1.5.0
- openpyxl>=3.0.0

## Future Enhancements

- Implement actual data loading and parsing logic.
- Add SQLite database integration for storing historical data.
- Develop a web-based dashboard for visualization.
- Add more sophisticated financial metrics and reporting.

## License

MIT