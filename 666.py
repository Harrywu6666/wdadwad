import streamlit as st
import pandas as pd
import google.generativeai as genai
import datetime as dt

# ---- 頁面標題與版面 ----
st.set_page_config(page_title="AI Data Viewer", layout="wide")
st.title("📊 AI 資料探索 + Gemini 聊天 + RFM 分析")

# ---- 選單 ----
menu = st.sidebar.selectbox("功能選擇", ["上傳與檢視資料集", "RFM 分析報表", "Gemini 問答"])

# ---- 記錄資料集 ----
if "data" not in st.session_state:
    st.session_state.data = None
if "rfm_table" not in st.session_state:
    st.session_state.rfm_table = None

# ---- 功能一：上傳 CSV ----
if menu == "上傳與檢視資料集":
    st.header("📂 上傳 CSV 資料集")
    uploaded_file = st.file_uploader("請選擇檔案（CSV）", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.data = df
        st.success("✅ 資料成功上傳！")
        st.dataframe(df)

# ---- 功能二：RFM 分析 + Gemini 說明 ----
elif menu == "RFM 分析報表":
    st.header("📊 RFM 顧客價值分析")

    if st.session_state.data is not None:
        df = st.session_state.data.copy()
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
            rfm_table['RFM_Segment'] = rfm_table['R_score'].astype(str) + rfm_table['F_score'].astype(str) + rfm_table['M_score'].astype(str)
            rfm_table['RFM_Score'] = rfm_table[['R_score', 'F_score', 'M_score']].astype(int).sum(axis=1)

            st.session_state.rfm_table = rfm_table  # 保存供 Gemini 使用

            st.subheader("📋 RFM 表格（前10筆）")
            st.dataframe(rfm_table.head(10))

            csv = rfm_table.to_csv().encode('utf-8-sig')
            st.download_button("📥 下載 RFM 分析結果", data=csv, file_name='rfm_analysis.csv', mime='text/csv')

            # ---- Gemini 分析整張表格摘要 ----
            st.subheader("🧠 Gemini 解說 RFM 分析結果")
            user_prompt = st.text_area("請輸入你的問題（例如：這份客戶有哪些高價值特徵？）")

            if st.button("由 Gemini 分析 RFM 表格"):
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash")

                    rfm = rfm_table.copy()
                    summary_text = f"""
以下是 RFM 分析結果的統計摘要：

📊 平均 Recency：{rfm['recency'].mean():.2f}
📊 平均 Frequency：{rfm['frequency'].mean():.2f}
📊 平均 Monetary：${rfm['monetary'].mean():,.2f}
🎯 RFM Score 平均值：{rfm['RFM_Score'].mean():.2f}
🎯 高 RFM 分數（>12）顧客數：{(rfm['RFM_Score'] > 12).sum()}

🧑‍💼 Top 5 高價值顧客：
{rfm.sort_values('RFM_Score', ascending=False).head(5).reset_index()[['customer_id','recency','frequency','monetary','RFM_Score']].to_string(index=False)}
"""

                    prompt = f"{summary_text}\n\n使用者問題：{user_prompt}\n請根據這些數據提供洞察與建議。"
                    with st.spinner("Gemini 正在分析..."):
                        response = model.generate_content(prompt)
                        st.markdown("### 🤖 Gemini 回應")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
    else:
        st.warning("⚠️ 請先上傳資料集！")

# ---- 功能三：Gemini 自由問答 ----
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
