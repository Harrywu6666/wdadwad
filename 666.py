import streamlit as st
import google.generativeai as genai
import pandas as pd

# Streamlit 設定
st.set_page_config(page_title="Gemini AI x 資料集探索", layout="wide")
st.title("📊 資料集 + Gemini AI 對話")

tab1, tab2 = st.tabs(["📂 上傳 CSV", "💬 Gemini 聊天"])

# Tab 1: CSV 資料上傳
with tab1:
    st.subheader("上傳你的 CSV 檔案")
    uploaded_file = st.file_uploader("選擇 CSV 檔案", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(uploaded_file, encoding="big5")
            except Exception as e:
                st.error(f"❌ 無法讀取檔案，請確認格式是否正確。錯誤訊息：{e}")
                df = None
        if 'df' in locals() and df is not None:
            st.success("📄 檔案成功上傳！")
            st.dataframe(df)

# Tab 2: Gemini 聊天功能
with tab2:
    st.subheader("與 Gemini 聊天")
    api_key = st.text_input("輸入你的 Gemini API 金鑰", type="password")
    user_input = st.text_area("請輸入問題：", placeholder="你想問 Gemini 什麼？")

    if api_key and user_input:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="models/gemini-pro")  # ✅ 使用正確模型名稱
            chat = model.start_chat()
            response = chat.send_message(user_input)

            st.markdown("### 💡 Gemini 回覆：")
            st.success(response.text)
        except Exception as e:
            st.error(f"⚠️ 發生錯誤：{e}")
    else:
        st.info("請先輸入 API 金鑰與問題內容。")
