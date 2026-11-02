import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Women Unemployment in Lebanon",
    layout="wide"
)

# Title
st.title("Women Unemployment in Lebanon Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel(
        "unemployment rate  women.xlsx",
        engine="openpyxl"
    )
    return df

try:
    df = load_data()

    st.success("Data loaded successfully!")

    st.subheader("Raw Data")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading data: {e}")

