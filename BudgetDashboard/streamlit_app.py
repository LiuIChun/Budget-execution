"""
Streamlit儀表板 for BudgetDashboard.
提供互動式網頁介面來查看預算執行率和歷史趨勢。
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# 將 app 目錄優先加入系統路徑，以便導入自訂模組
sys.path.insert(0, str(Path(__file__).parent / "app"))

# 導入自訂模組
import config
from config import DATA_DIR, OUTPUT_DIR, DATABASE_DIR, DATABASE_PATH

from loader import load_all_monthly_data, load_approved_budget, find_month_dir
from parser import parse_expense_detail, parse_approved_budget
from calculator import summarize_execution
from exporter import export_execution_report
from history import init_history_db, save_monthly_execution
from department_mapping import set_department_mapping_month

# 初始化資料庫
init_history_db()


def add_department_names(summary_df, budget_file):
    """Add department Chinese names to old summary data when needed."""
    if '系所中文名稱' in summary_df.columns or not budget_file:
        return summary_df

    try:
        budget_df = parse_approved_budget(load_approved_budget(budget_file))
    except Exception:
        return summary_df

    if '系所中文名稱' not in budget_df.columns:
        return summary_df

    name_df = budget_df[['系所代碼', '系所中文名稱']].drop_duplicates('系所代碼')
    enriched_df = summary_df.merge(name_df, on='系所代碼', how='left')
    enriched_df['系所中文名稱'] = enriched_df['系所中文名稱'].fillna('')
    enriched_df.loc[
        (enriched_df['系所代碼'] != '合計') & (enriched_df['系所中文名稱'] == ''),
        '系所中文名稱',
    ] = '未建立對照'
    return enriched_df


def get_available_data_months():
    """Get month folders that contain a complete expense snapshot."""
    if not DATA_DIR.exists():
        return []
    return sorted(
        path.name
        for path in DATA_DIR.iterdir()
        if path.is_dir()
        and len(list(path.glob(config.EXPENSE_FILE_PATTERN))) >= 2
    )


def dataframe_stretch(df):
    """Render a dataframe using the current Streamlit width API with fallback."""
    try:
        st.dataframe(df, width="stretch")
    except (AttributeError, TypeError):
        st.dataframe(df, use_container_width=True)


def execution_rate_text_style(value):
    """Highlight execution rates below 60 percent with red text."""
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return ""
    return "color: #d32f2f; font-weight: 600;" if rate < 60 else ""


def style_execution_rate_table(df):
    """Format and conditionally style the execution-rate column."""
    styler = df.style.format({'執行率(%)': '{:.2f}%'})
    if hasattr(styler, "map"):
        return styler.map(execution_rate_text_style, subset=['執行率(%)'])
    return styler.applymap(execution_rate_text_style, subset=['執行率(%)'])


def plotly_chart_stretch(fig):
    """Render a Plotly chart using the current Streamlit width API with fallback."""
    try:
        st.plotly_chart(fig, width="stretch")
    except (AttributeError, TypeError):
        st.plotly_chart(fig, use_container_width=True)


# 設定頁面配置
st.set_page_config(
    page_title="BudgetDashboard - 預算執行管理系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 應用程式標題
st.title("📊 BudgetDashboard - 預算執行管理系統")
st.markdown("---")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 月份選擇
    available_months = get_available_data_months()
    if available_months:
        selected_month = st.selectbox(
            "選擇月份",
            options=available_months,
            index=len(available_months)-1 if available_months else 0
        )
    else:
        selected_month = None
        st.warning("目前尚無可用月份資料")
    
    # 執行按鈕
    if st.button("🚀 執行預算執行率分析", type="primary"):
        month_to_process = selected_month
        
        if month_to_process:
            with st.spinner("正在處理資料中..."):
                try:
                    # 尋找月份資料夾
                    month_dir = find_month_dir(month_to_process if month_to_process else None)
                    mapping_file = set_department_mapping_month(month_dir)
                    
                    # 載入資料
                    data = load_all_monthly_data(month_dir)
                    
                    # 解析資料
                    parsed_expense_df = parse_expense_detail(data["merged_expense_df"])
                    parsed_budget_df = parse_approved_budget(data["approved_budget_df"])
                    
                    # 計算執行率
                    summary_df = summarize_execution(parsed_expense_df, parsed_budget_df)
                    
                    # 輸出Excel報表
                    output_name = f"budget_execution_{data['month']}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    output_path = export_execution_report(summary_df, parsed_expense_df, output_name)
                    
                    # 儲存至歷史資料庫
                    save_monthly_execution(data['month'], summary_df)
                    
                    # 儲存結果到 session_state 以便在頁面中使用
                    st.session_state['last_result'] = {
                        'month': data['month'],
                        'summary_df': summary_df,
                        'parsed_expense_df': parsed_expense_df,
                        'output_path': output_path,
                        'expense_files': data["expense_files"],
                        'budget_file': data["approved_budget_file"],
                        'mapping_file': mapping_file
                    }
                    
                    st.success(f"✅ 分析完成！報表已儲存至: {output_path.name}")
                except Exception as e:
                    st.error(f"❌ 處理失敗: {str(e)}")
        else:
            st.warning("請輸入月份")

# 主要內容區域
if 'last_result' in st.session_state:
    result = st.session_state['last_result']
    result['summary_df'] = add_department_names(result['summary_df'], result.get('budget_file'))
    
    # 顯示基本資訊
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("來源月份", result['month'])
    with col2:
        st.metric("收支明細檔案數", len(result['expense_files']))
    with col3:
        st.metric("核定經費檔案", result['budget_file'].name)
    
    # 顯示執行率摘要表
    st.subheader("📈 各系所預算執行率摘要")
    
    # 格式化顯示摘要表格
    display_df = result['summary_df'].copy()
    if '系所中文名稱' in display_df.columns:
        category_cols = []
        for category in config.EXPENSE_CATEGORIES:
            category_cols.extend([f'{category}核定', f'{category}執行金額'])
        preferred_cols = [
            '系所代碼',
            '系所中文名稱',
            '核定經費',
            '執行金額',
            '執行率(%)',
        ] + category_cols
        cols = [col for col in preferred_cols if col in display_df.columns]
        cols += [col for col in display_df.columns if col not in cols and col not in ['department_code', 'department_name']]
        display_df = display_df[cols]
    elif 'department_name' in display_df.columns:
        display_df['系所名稱'] = display_df['department_name']
        # 重新排序欄位，讓系所名稱顯示在前面
        cols = ['系所名稱'] + [col for col in display_df.columns if col not in ['系所名稱', 'department_code', 'department_name']]
        display_df = display_df[cols]
    
    # 格式化金額欄位為千分位
    for col in display_df.columns:
        if col == '執行率(%)':
            continue
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
    if '執行率(%)' in display_df.columns:
        dataframe_stretch(style_execution_rate_table(display_df))
    else:
        dataframe_stretch(display_df)
    
    # 執行率條形圖
    st.subheader("📊 各系所執行率比較")
    plot_df = result['summary_df'][result['summary_df']['系所代碼'] != '合計'].copy()
    if not plot_df.empty:
        fig_rate = px.bar(
            plot_df,
            x='系所中文名稱',
            y='執行率(%)',
            title='各系所預算執行率',
            color='執行率(%)',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100],
            hover_data={'系所代碼': True, '系所中文名稱': False},
        )
        fig_rate.update_layout(
            xaxis_title='系所中文名稱',
            yaxis_title='執行率 (%)',
            height=500,
            xaxis_tickangle=-45,
        )
        plotly_chart_stretch(fig_rate)
    else:
        st.info("沒有可顯示的執行率條形圖數據")

else:
    # 沒有執行結果時顯示的內容
    st.info("👈 請在左側選擇月份並點擊『執行預算執行率分析』按鈕來開始分析。")
    
    # 顯示使用說明
    with st.expander("📖 使用說明"):
        st.markdown("""
        ### 使用步驟
        1. 在側邊欄中選擇有歷史資料的月份，或手動輸入月份（例如 11506）
        2. 點擊『執行預算執行率分析』按鈕
        3. 系統將自動：
           - 讀取該月份的兩份收支明細Excel和一份核定經費Excel
           - 解析購案編號中的4碼系所代碼
           - 合併兩份收支資料
           - 對照核定經費
           - 計算各系所執行率
           - 產生Excel報表並儲存至 output/ 資料夾
           - 將結果儲存至 SQLite 資料庫
        4. 分析完成後，儀表板將顯示：
           - 執行率摘要表
           - 執行率比較條形圖
        
        ### 資料夾結構
        - `data/`: 放置每月的資料夾（例如 11506, 11507）
        - 每月資料夾內應包含：
          - 兩份收支明細Excel（格式: *收支明細.xlsx）
          - 一份核定經費Excel（格式: 各系核定經費.xlsx）
        - `output/`: 自動產生的Excel報表將放置在此
        - `database/`: SQLite歷史資料庫
        """)

# 頁尾資訊
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        BudgetDashboard v1.0 | 建立於 2026 | 使用 Streamlit 建立
    </div>
    """,
    unsafe_allow_html=True
)
