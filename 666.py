import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

        # 顯示基本統計摘要
        st.subheader("📈 資料摘要")
        st.write(df.describe())

        # 城市平均 AQI 長條圖
        st.subheader("🏙️ 城市平均 AQI")
        avg_aqi = df.groupby("city")["aqi"].mean().sort_values(ascending=False)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(x=avg_aqi.values, y=avg_aqi.index, ax=ax1)
        ax1.set_xlabel("平均 AQI")
        ax1.set_ylabel("城市")
        st.pyplot(fig1)

        # AQI vs 醫院就診 散佈圖
        st.subheader("💥 AQI 與就醫人數關聯")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=df, x="aqi", y="hospital_admissions", hue="city", alpha=0.6, ax=ax2)
        ax2.set_xlabel("AQI")
        ax2.set_ylabel("就醫人數")
        st.pyplot(fig2)

        # 不同人口密度區域的 AQI 箱型圖
        st.subheader("🌍 不同人口密度下的 AQI 分布")
        fig3, ax3 = plt.subplots()
        sns.boxplot(data=df, x="population_density", y="aqi", ax=ax3)
        st.pyplot(fig3)

# ---- 功能二：Gemini API 聊天 ----
elif menu == "Gemini 問答":
    st.header("💬 Gemini AI 聊天室")

    # 從 secrets.toml 讀取 API key
    api_key = st.secrets["GEMINI_API_KEY"]

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    user_input = st.text_area("請輸入你的問題")
    if st.button("送出"):
        with st.spinner("Gemini 回應中..."):
            try:
                response = model.generate_content(user_input)
                st.markdown("### 🤖 Gemini 回應")
                st.write(response.text)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
