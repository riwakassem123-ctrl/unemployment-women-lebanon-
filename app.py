import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(
page_title="Women's Employment in Lebanon",
page_icon="📊",
layout="wide"
)

@st.cache_data
def load_data():
df = pd.read_excel("lebanon_data.xlsx")
df.columns = df.columns.str.strip()
required_columns = ["Year", "Total", "Female", "Male"]
for column in required_columns:
if column not in df.columns:
raise ValueError(
f"Missing column: {column}. "
f"Available columns: {list(df.columns)}"
)
for column in required_columns:
df[column] = pd.to_numeric(df[column], errors="coerce")
df = df.dropna(subset=["Year"])
df = df.sort_values("Year")
return df


st.title("The Invisible Workforce")
st.subheader("Understanding Unemployment in Lebanon (1990–2023)")
st.write(
"This interactive dashboard explores unemployment trends "
"in Lebanon, comparing total, female, and male unemployment rates."
)
try:
df = load_data()
# SIDEBAR FILTER
st.sidebar.title("Dashboard Filters")
minimum_year = int(df["Year"].min())
maximum_year = int(df["Year"].max())
selected_years = st.sidebar.slider(
"Select year range",
min_value=minimum_year,
max_value=maximum_year,
value=(minimum_year, maximum_year)
)
filtered = df[
(df["Year"] >= selected_years[0]) &
(df["Year"] <= selected_years[1])
].copy()
if filtered.empty:
st.warning("No data available for this year range.")
else:
# LATEST INDICATORS
st.header("Unemployment Overview")
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
f"Figures shown for the latest available year in the "
f"selected range: {int(latest['Year'])}."
)
# CHART 1: GENDER COMPARISON
st.header("1. The Gender Unemployment Gap")
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
title="Female vs. Male Unemployment in Lebanon"
)
fig1.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment rate (% of respective labour force)",
legend_title="Gender"
)
st.plotly_chart(fig1, use_container_width=True)
st.write(
"This chart compares unemployment rates among women "
"and men over time."
)
# CHART 2: TOTAL UNEMPLOYMENT
st.header("2. Overall Unemployment Trend")
fig2 = px.line(
filtered,
x="Year",
y="Total",
markers=True,
title="Total Unemployment in Lebanon"
)
fig2.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment rate (% of total labour force)"
)
st.plotly_chart(fig2, use_container_width=True)
# CHART 3: ALL INDICATORS
st.header("3. Comparing All Three Indicators")
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
title="Unemployment Trends by Indicator"
)
fig3.update_layout(
xaxis_title="Year",
yaxis_title="Unemployment rate (%)",
legend_title="Indicator"
)
st.plotly_chart(fig3, use_container_width=True)
# DATA TABLE
with st.expander("View the underlying data"):
st.dataframe(filtered, use_container_width=True)
st.caption(
"Source: World Bank, World Development Indicators (WDI), "
"based on ILO estimates. Confirm against the original dataset."
)
except FileNotFoundError:
st.error(
"Excel file not found. Make sure lebanon_data.xlsx "
"is uploaded in the same GitHub repository as app.py."
)
except Exception as error:
st.error(f"An error occurred: {error}")


