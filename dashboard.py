"""
BudgetDashboard 首頁 - Streamlit 介面
提供互動式網頁介面來查看預算執行率和歷史趨勢
"""

# Compatibility entrypoint for older Streamlit Cloud deployments.  Keep both
# possible entrypoint files rendering the same maintained application.
from streamlit_app import *  # noqa: F401,F403,E402

import streamlit as st

st.stop()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import sqlite3
from datetime import datetime

# 將 app 目錄加入系統路徑，以便導入自訂模組
sys.path.append(str(Path(__file__).parent / "app"))

# 導入自訂模組
from config import DATA_DIR, OUTPUT_DIR, DATABASE_DIR, DATABASE_PATH
from loader import load_all_monthly_data, find_month_dir
from parser import parse_expense_detail, parse_approved_budget
from calculator import summarize_execution
from exporter import export_execution_report
from history import init_history_db, save_monthly_execution, load_history, get_available_months

# 初始化資料庫
init_history_db()

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
    available_months = get_available_months()
    if available_months:
        selected_month = st.selectbox(
            "選擇月份（有歷史資料的月份）",
            options=available_months,
            index=len(available_months)-1 if available_months else 0
        )
    else:
        selected_month = None
        st.warning("目前尚無歷史資料")
    
    # 手動輸入月份
    manual_month = st.text_input(
        "或手動輸入月份 (例如 11506)",
        value=selected_month if selected_month else ""
    )
    
    # 執行按鈕
    if st.button("🚀 執行預算執行率分析", type="primary"):
        # 使用手動輸入的月份（如果有），否則使用選擇的月份
        month_to_process = manual_month.strip() if manual_month.strip() else selected_month
        
        if month_to_process:
            with st.spinner("正在處理資料中..."):
                try:
                    # 尋找月份資料夾
                    month_dir = find_month_dir(month_to_process if month_to_process else None)
                    
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
                        'budget_file': data["approved_budget_file"]
                    }
                    
                    st.success(f"✅ 分析完成！報表已儲存至: {output_path.name}")
                except Exception as e:
                    st.error(f"❌ 處理失敗: {str(e)}")
        else:
            st.warning("請選擇或輸入月份")

# 主要內容區域
if 'last_result' in st.session_state:
    result = st.session_state['last_result']
    month = result['month']
    summary_df = result['summary_df']
    parsed_expense_df = result['parsed_expense_df']
    
    # 顯示當前處理的月份
    st.subheader(f"📅 {month} 預算執行分析結果")
    
    # KPI 區域
    col1, col2, col3, col4 = st.columns(4)
    
    # 計算 KPI 值
    total_approved = summary_df['budget_amount'].sum()
    total_executed = summary_df['actual_amount'].sum()
    avg_execution_rate = (total_executed / total_approved * 100) if total_approved > 0 else 0
    remaining_budget = total_approved - total_executed
    
    with col1:
        st.metric(
            label="💰 總核定經費",
            value=f"{total_approved:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 總執行金額",
            value=f"{total_executed:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="📊 平均執行率",
            value=f"{avg_execution_rate:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="📉 剩餘經費",
            value=f"{remaining_budget:,.0f}",
            delta=None
        )
    
    st.markdown("---")
    
    # 各系所執行率排行
    st.subheader("📈 各系所執行率排行")
    
    # 計算執行率並排序
    summary_df['execution_rate'] = (summary_df['actual_amount'] / summary_df['budget_amount'] * 100).fillna(0)
    sorted_df = summary_df.sort_values('execution_rate', ascending=False)
    
    # 創建長條圖
    fig = px.bar(
        sorted_df.head(10),  # 顯示前10名
        x='execution_rate',
        y='department_name',
        orientation='h',
        title="前10名系所執行率",
        labels={'execution_rate': '執行率 (%)', 'department_name': '系所名稱'},
        color='execution_rate',
        color_continuous_scale='blues'
    )
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 篩選器
    st.subheader("🔍 篩選條件")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        # 學院篩選
        colleges = ['全部'] + sorted(summary_df['college'].unique().tolist())
        selected_college = st.selectbox("學院篩選", colleges)
    
    with filter_col2:
        # 月份篩選（從歷史資料中取得）
        history_months = get_available_months()
        if history_months:
            selected_history_month = st.selectbox("月份篩選", ['全部'] + history_months)
        else:
            selected_history_month = st.selectbox("月份篩選", ['全部'])
    
    # 根據篩選條件過濾資料
    filtered_df = summary_df.copy()
    if selected_college != '全部':
        filtered_df = filtered_df[filtered_df['college'] == selected_college]
    # 月份篩選在這裡可以根據需求實作
    
    # 顯示過濾後的資料表
    st.subheader("📋 系所執行率詳細資料")
    display_df = filtered_df[['department_name', 'college', 'budget_amount', 'actual_amount', 'execution_rate']].copy()
    display_df.columns = ['系所名稱', '學院', '核定經費', '執行金額', '執行率(%)']
    display_df['執行率(%)'] = display_df['執行率(%)'].round(2)
    st.dataframe(display_df, use_container_width=True)
    
    # 點擊系所展開購案明細
    st.subheader("🔍 購案明細查詢")
    selected_dept = st.selectbox(
        "選擇系所查看購案明細",
        options=['請選擇系所'] + sorted_df['department_name'].tolist()
    )
    
    if selected_dept != '請選擇系所':
        # 過濾選定系別的購案明細
        dept_expenses = parsed_expense_df[
            parsed_expense_df['department_name'] == selected_dept
        ].copy()
        
        if not dept_expenses.empty:
            st.write(f"**{selected_dept}** 的購案明細：")
            
            # 格式化顯示
            display_expenses = dept_expenses[['item_name', 'amount', 'date', 'category']].copy()
            display_expenses.columns = ['購案名稱', '金額', '日期', '類別']
            display_expenses['金額'] = display_expenses['金額'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(display_expenses, use_container_width=True)
            
            # 顯示該系所的總計
            dept_total = dept_expenses['amount'].sum()
            st.info(f"**{selected_dept}** 購案總金額：{dept_total:,.0f}")
        else:
            st.warning(f"未找到 {selected_dept} 的購案明細資料")
else:
    # 顯示歡迎畫面
    st.info("👈 請從側邊欄選擇月份並點擊『執行預算執行率分析』按鈕開始使用")
    
    # 顯示系統說明
    st.markdown("""
    ### 📋 系統功能說明
    
    1. **資料載入**：自動載入指定月份的收支明細和各系核定經費資料
    2. **資料解析**：解析CSV資料並進行資料清洗
    3. **執行率計算**：計算各系所的預算執行率
    4. **結果視覺化**：提供KPI指標、長條圖和詳細資料表
    5. **互動查詢**：點擊系所可查看詳細購案明細
    6. **歷史追蹤**：自動儲存每月分析結果以供趨勢分析
    
    ### 🚀 使用步驟
    1. 在側邊欄選擇有歷史資料的月份或手動輸入月份代號（如 11506）
    2. 點擊『執行預算執行率分析』按鈕
    3. 等待處理完成後，即可在主頁面查看分析結果
    4. 使用篩選器進行多維度分析
    5. 點擊系所名稱查看詳細購案明細
    """)

# 自訂CSS樣式 - Material Design 風格
st.markdown("""
<style>
    /* 主題顏色 - 藍白色系 */
    :root {
        --primary-color: #1976D2;
        --secondary-color: #42A5F5;
        --background-color: #FFFFFF;
        --surface-color: #F5F5F5;
        --text-primary: #212121;
        --text-secondary: #757575;
    }
    
    /* 整體背景 */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-primary);
    }
    
    /* 標題樣式 */
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* 量度卡片樣式 */
    [data-testid="metric-container"] {
        background-color: var(--surface-color);
        border: 1px solid #E0E0E0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 側邊欄樣式 */
    .css-1d391kg {
        background-color: var(--surface-color);
    }
    
    /* 表格樣式 */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .dataframe td {
        border-bottom: 1px solid #EEEEEE !important;
    }
    
    /* 響應式設計 */
    @media (max-width: 768px) {
        .css-18e3th9 {
            padding: 1rem;
        }
        
        .stColumns {
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)
