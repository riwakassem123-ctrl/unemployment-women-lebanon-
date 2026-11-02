import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(
    page_title="Women Unemployment in Lebanon",
    layout="wide"
)

# Dashboard title
st.title("Women Unemployment in Lebanon Dashboard")

@st.cache_data
def load_data():
    df = pd.read_excel("unemployment rate  women.xlsx")
    return df

try:
    df = load_data()

    st.sidebar.header("Dashboard Filters")

    st.write(df.head())

except Exception as e:
    st.error(f"Error loading data: {e}")

