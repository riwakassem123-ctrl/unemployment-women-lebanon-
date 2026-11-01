#import streamlit as st
import pandas as pd
import plotly.express as px
#Page settings
st.set_page_config(
page_title="Women's Employment in Lebanon",
page_icon="📊",
layout="wide"
)
# Dashboard title
st.title("The Invisible Workforce")
st.subheader("Understanding Unemployment in Lebanon (1990–2023)")
st.markdown("""
This dashboard explores unemployment trends in Lebanon,
with a focus on differences between total, female, and male unemployment.
""")
#Load Excel data
@st.cache_data
def load_data():
  @st.cache_data():
df = pd.read_excel("lebanon_data.xlsx")
df.columns = df.columns.str.strip()
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
for column in ["Total", "Female", "Male"]:
df[column] = pd.to_numeric(df[column], errors="coerce")
return df.dropna(subset=["Year"]).sort_values("Year")
try:
df = load_data()
# Sidebar year filter
st.sidebar.header("Dashboard Filters")
years = st.sidebar.slider(
"Select year range",
int(df["Year"].min()),
int(df["Year"].max()),
(int(df["Year"].min()), int(df["Year"].max()))
)
filtered = df[
(df["Year"] >= years[0]) &
(df["Year"] <= years[1])
]
# Key indicators
st.header("Unemployment Overview")
latest = filtered.dropna(subset=["Total", "Female", "Male"])
if not latest.empty:
latest = latest.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Total unemployment", f'{latest["Total"]:.1f}%')
col2.metric("Female unemployment", f'{latest["Female"]:.1f}%')
col3.metric("Male unemployment", f'{latest["Male"]:.1f}%')
# Chart 1: Gender comparison
st.header("1. The Gender Unemployment Gap")
gender_data = filtered.melt(
id_vars="Year",
value_vars=["Female", "Male"],
var_name="Gender",
value_name="Unemployment Rate"
)
fig1 = px.line(
gender_data,
x="Year",
y="Unemployment Rate",
color="Gender",
markers=True,
title="Female vs. Male Unemployment in Lebanon"
)
fig1.update_layout(
yaxis_title="Unemployment rate (%)",
xaxis_title="Year"
)
st.plotly_chart(fig1, use_container_width=True)
# Chart 2: Total unemployment
st.header("2. Overall Unemployment Trend")
fig2 = px.line(
filtered,
x="Year",
y="Total",
markers=True,
title="Total Unemployment in Lebanon"
)
fig2.update_layout(
yaxis_title="Unemployment rate (%)",
xaxis_title="Year"
)
st.plotly_chart(fig2, use_container_width=True)
# Chart 3: All indicators
st.header("3. Comparing All Three Indicators")
all_data = filtered.melt(
id_vars="Year",
value_vars=["Total", "Female", "Male"],
var_name="Indicator",
value_name="Unemployment Rate"
)
fig3 = px.line(
all_data,
x="Year",
y="Unemployment Rate",
color="Indicator",
markers=True,
title="Unemployment Trends by Indicator"
)
fig3.update_layout(
yaxis_title="Unemployment rate (%)",
xaxis_title="Year"
)
st.plotly_chart(fig3, use_container_width=True)
# Data table
with st.expander("View the underlying data"):
st.dataframe(filtered, use_container_width=True)
st.caption(
"Source: World Bank, World Development Indicators (WDI), "
"based on ILO estimates. Verify the source against your downloaded dataset."
)
except FileNotFoundError:
st.error("Could not find lebanon_data.xlsx. Upload it beside app.py.")
except Exception as e:
st.error(f"Please check your Excel column names and data: {e}")

