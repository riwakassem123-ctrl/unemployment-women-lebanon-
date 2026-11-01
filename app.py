import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(
page_title="Unemployment in Lebanon",
page_icon="📊",
layout="wide"
)
st.title("The Invisible Workforce")
st.subheader("Understanding Unemployment in Lebanon")
st.write(
"Explore unemployment trends in Lebanon from 1990 to 2023, "
"comparing total, female, and male unemployment rates."
)
Load Excel data
df = pd.read_excel("lebanon_data.xlsx")
df.columns = df.columns.str.strip()
Convert columns to numbers
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
df["Female"] = pd.to_numeric(df["Female"], errors="coerce")
df["Male"] = pd.to_numeric(df["Male"], errors="coerce")
df = df.dropna(subset=["Year"])
df = df.sort_values("Year")
Dashboard filters
st.sidebar.header("Dashboard Filters")
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
selected_years = st.sidebar.slider(
"Choose year range",
min_year,
max_year,
(min_year, max_year)
)
filtered = df[
(df["Year"] >= selected_years[0]) &
(df["Year"] <= selected_years[1])
]
Unemployment overview
st.header("Unemployment Overview")
if not filtered.empty:
latest = filtered.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric(
"Total unemployment",
f'{latest["Total"]:.1f}%'
)
col2.metric(
"Female unemployment",
f'{latest["Female"]:.1f}%'
)
col3.metric(
"Male unemployment",
f'{latest["Male"]:.1f}%'
)
st.caption(
f'Latest selected year: {int(latest["Year"])}'
)
# Chart 1: Gender comparison
st.header("1. Gender Unemployment Comparison")
gender_data = filtered.melt(
id_vars=["Year"],
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
title="Female vs Male Unemployment in Lebanon"
)
fig1.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment Rate (%)"
)
st.plotly_chart(
fig1,
use_container_width=True
)
# Chart 2: Total unemployment
st.header("2. Total Unemployment Trend")
fig2 = px.line(
filtered,
x="Year",
y="Total",
markers=True,
title="Total Unemployment in Lebanon"
)
fig2.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment Rate (%)"
)
st.plotly_chart(
fig2,
use_container_width=True
)
# Chart 3: All indicators
st.header("3. Overall Comparison")
all_data = filtered.melt(
id_vars=["Year"],
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
title="Total, Female and Male Unemployment"
)
fig3.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment Rate (%)"
)
st.plotly_chart(
fig3,
use_container_width=True
)
# Data table
with st.expander("View the data"):
st.dataframe(
filtered,
use_container_width=True
)
else:
st.warning("No data available for the selected years.")
st.caption(
"Source: World Bank, World Development Indicators. "
"Verify the source against the original dataset."
)


