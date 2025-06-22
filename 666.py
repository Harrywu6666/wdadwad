import streamlit as st
import pandas as pd
import google.generativeai as genai
import datetime as dt

# ---- 網頁標題 ----
st.set_page_config(page_title="AI Data Viewer", layout="wide")
st.title("📊 AI 資料探索 + Gemini 聊天 + RFM 分析")

# ---- 選單 ----
menu = st.sidebar.selectbox("功能選擇", ["上傳與檢視資料集", "RFM 分析報表", "Gemini 問答"])

# ---- Session 狀態記錄資料集 ----
if "data" not in st.session_state:
    st.session_state.data = None

# ---- 功能一：上傳與顯示 CSV ----
if menu == "上傳與檢視資料集":
    st.header("📂 上傳 CSV 資料集")
    uploaded_file = st.file_uploader("請選擇檔案（CSV）", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.data = df  # 保存資料供 RFM 使用
        st.success("✅ 資料成功上傳！")
        st.dataframe(df)

# ---- 功能二：RFM 分析報表 ----
elif menu == "RFM 分析報表":
    st.header("📊 RFM 顧客價值分析")

    if st.session_state.data is not None:
        df = st.session_state.data.copy()

        # 檢查必要欄位是否存在
        required_cols = {'customer_id', 'date', 'value [USD]'}
        if not required_cols.issubset(df.columns):
            st.error("❌ 資料缺少必要欄位：customer_id、date、value [USD]")
        else:
            reference_date = dt.datetime(2018, 12, 1)

            rfm_table = df.groupby('customer_id').agg({
                'date': lambda x: (reference_date - pd.to_datetime(x).max()).days,
                'customer_id': 'count',
                'value [USD]': 'sum'
            })

            rfm_table.columns = ['recency', 'frequency', 'monetary']

            rfm_table['R_score'] = pd.qcut(rfm_table['recency'], 5, labels=[5, 4, 3, 2, 1])
            rfm_table['F_score'] = pd.qcut(rfm_table['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
            rfm_table['M_score'] = pd.qcut(rfm_table['monetary'], 5, labels=[1, 2, 3, 4, 5])

            rfm_table['RFM_Segment'] = (
                rfm_table['R_score'].astype(str)
                + rfm_table['F_score'].astype(str)
                + rfm_table['M_score'].astype(str)
            )
            rfm_table['RFM_Score'] = rfm_table[['R_score', 'F_score', 'M_score']].astype(int).sum(axis=1)

            st.subheader("📋 RFM 表格前 10 筆")
            st.dataframe(rfm_table.head(10))

            csv = rfm_table.to_csv().encode('utf-8-sig')
            st.download_button("📥 下載 RFM 分析結果", data=csv, file_name='rfm_analysis.csv', mime='text/csv')
    else:
        st.warning("⚠️ 請先上傳資料集！")

# ---- 功能三：Gemini 聊天 ----
elif menu == "Gemini 問答":
    st.header("💬 Gemini AI 聊天室")

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        user_input = st.text_area("請輸入你的問題")
        if st.button("送出"):
            with st.spinner("Gemini 回應中..."):
                response = model.generate_content(user_input)
                st.markdown("### 🤖 Gemini 回應")
                st.write(response.text)
    except Exception as e:
        st.error(f"❌ 發生錯誤：{e}")

