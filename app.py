import streamlit as st
import google.generativeai as genai

# 使用 secrets 儲存的 API key
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Gemini 聊天室", layout="centered")
st.title("🤖 Gemini AI 聊天室")

user_input = st.text_area("請輸入你的問題")

if st.button("送出"):
    with st.spinner("Gemini 回應中..."):
        try:
            response = model.generate_content(user_input)
            st.markdown("### Gemini 回應")
            st.write(response.text)
        except Exception as e:
            st.error(f"❌ 錯誤：{e}")