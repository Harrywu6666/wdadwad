import streamlit as st
import pandas as pd
import google.generativeai as genai

# ---- 網頁標題 ----
st.set_page_config(page_title="AI Data Viewer", layout="wide")
st.title("📊 AI 資料探索 + Gemini 聊天")

# ---- 選單 ----
menu = st.sidebar.selectbox("功能選擇", ["上傳與檢視資料集", "Gemini 問答"])

# ---- 功能一：CSV 上傳與顯示 ----
if menu == "上傳與檢視資料集":
    st.header("📂 上傳 CSV 資料集")
    uploaded_file = st.file_uploader("請選擇檔案（CSV）", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ 資料成功上傳！")
        st.dataframe(df)

# ---- 功能二：Gemini API 聊天 ----
elif menu == "Gemini 問答":
    st.header("💬 Gemini AI 聊天室")

    # API key 輸入（部署時建議用 st.secrets）
    api_key = st.text_input("請輸入你的 Gemini API 金鑰", type="password")

    if api_key:
        try:
            genai.configure(api_key=api_key)

            # 驗證是否支援的模型存在
            support_models = [
                m.name for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]
            if "models/gemini-pro" not in support_models:
                st.error("❌ 模型 'gemini-pro' 不支援 generateContent，請檢查金鑰權限或使用者配額。")
            else:
                model = genai.GenerativeModel("gemini-pro")

                user_input = st.text_area("請輸入你的問題")
                if st.button("送出"):
                    with st.spinner("Gemini 回應中..."):
                        try:
                            response = model.generate_content(user_input)
                            st.markdown("### 🤖 Gemini 回應")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"❌ 發生錯誤：{e}")

        except Exception as e:
            st.error(f"❌ API 設定錯誤或無效金鑰：{e}")
