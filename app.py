import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Bookkeeping SaaS", layout="wide")
st.title("📊 AI Bookkeeping SaaS (v1.2 Base)")

st.sidebar.header("Settings")
use_ai = st.sidebar.checkbox("Use AI Classification (OpenAI)", value=False)

st.write("## Upload Bank Statement")
uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.dataframe(df)

st.write("## Sample Data")
st.dataframe(pd.read_csv("sample_data/sample_bank.csv"))
