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
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Women Unemployment in Lebanon",
    layout="wide"
)

st.title("Women Unemployment in Lebanon Dashboard")

# Data from your Excel file
years = list(range(1991, 2024))

total = [
8.594,8.225,8.226,8.321,8.421,8.413,8.620,8.571,8.787,8.641,
8.499,8.248,8.061,7.850,8.249,8.679,8.980,7.666,6.355,6.768,
7.352,7.952,8.477,8.840,9.312,9.794,10.258,10.755,11.301,
13.252,12.715,11.105,10.985
]

female = [
10.553,10.181,10.172,10.256,10.346,10.328,10.524,10.437,10.602,
10.426,10.250,9.973,9.755,9.512,9.742,9.999,10.142,10.299,
10.345,10.671,11.210,11.753,12.195,12.445,12.812,13.176,
13.520,13.898,14.323,16.249,15.874,14.593,14.480
]

male = [
8.080,7.694,7.688,7.778,7.874,7.857,8.066,8.024,8.254,
8.116,7.979,7.732,7.550,7.342,7.784,8.258,8.602,6.790,
4.997,5.409,5.978,6.568,7.094,7.468,7.941,8.418,
8.880,9.376,9.922,12.045,11.515,9.816,9.705
]

df = pd.DataFrame({
    "Year": years,
    "Total": total,
    "Female": female,
    "Male": male
})

st.subheader("Unemployment Data")
st.dataframe(df)

# Total unemployment chart
st.subheader("Total Unemployment Rate")

fig_total = px.line(
    df,
    x="Year",
    y="Total",
    markers=True,
    color_discrete_sequence=["#1f77b4"]
)

st.plotly_chart(fig_total, use_container_width=True)

# Gender comparison chart
st.subheader("Male vs Female Unemployment")

df_gender = df.melt(
    id_vars="Year",
    value_vars=["Female", "Male"],
    var_name="Gender",
    value_name="Unemployment Rate"
)

fig_gender = px.line(
    df_gender,
    x="Year",
    y="Unemployment Rate",
    color="Gender",
    markers=True
)

st.plotly_chart(fig_gender, use_container_width=True)

# Combined chart
st.subheader("Total, Female and Male Unemployment")

df_all = df.melt(
    id_vars="Year",
    value_vars=["Total", "Female", "Male"],
    var_name="Series",
    value_name="Rate"
)

fig_all = px.line(
    df_all,
    x="Year",
    y="Rate",
    color="Series",
    markers=True
)

st.plotly_chart(fig_all, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Latest Total (2023)", f"{df['Total'].iloc[-1]:.2f}%")
col2.metric("Latest Female (2023)", f"{df['Female'].iloc[-1]:.2f}%")
col3.metric("Latest Male (2023)", f"{df['Male'].iloc[-1]:.2f}%")
st.set_page_config(
    page_title="Women Unemployment in Lebanon",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# TITLE & INTRODUCTION
# --------------------------------------------------
st.title("📊 Women Unemployment in Lebanon Dashboard")
st.markdown("""
This dashboard explores unemployment trends in Lebanon between 1991 and 2023,
highlighting gender differences and long-term labor market developments.
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel(
        "unemployment rate  women.xlsx",
        engine="openpyxl"
    )

try:
    df = load_data()

    # Rename columns if needed
    df.columns = [str(col).strip() for col in df.columns]

    # Replace these with your actual column names if different
    df = df.rename(columns={
        df.columns"Year",
        df.columns"Total",
        df.columns"Female",
        df.columns"Male"
    })

    # --------------------------------------------------
    # SIDEBAR FILTERS
    # --------------------------------------------------
    st.sidebar.header("🔍 Dashboard Filters")

    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_year,
        max_year,
        (min_year, max_year)
    )

    filtered_df = df[
        (df["Year"] >= selected_years[0]) &
        (df["Year"] <= selected_years[1])
    ]

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------
    st.subheader("📌 Key Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Unemployment",
        f"{filtered_df['Total'].iloc[-1]:.1f}%"
    )

    col2.metric(
        "Female Unemployment",
        f"{filtered_df['Female'].iloc[-1]:.1f}%"
    )

    col3.metric(
        "Male Unemployment",
        f"{filtered_df['Male'].iloc[-1]:.1f}%"
    )

    # --------------------------------------------------
    # KEY FINDINGS
    # --------------------------------------------------
    st.subheader("📈 Main Results")

    gap_latest = (
        filtered_df["Female"].iloc[-1]
        - filtered_df["Male"].iloc[-1]
    )

    highest_female = filtered_df.loc[
        filtered_df["Female"].idxmax()
    ]

    st.info(
        f"""
        • Female unemployment remains consistently higher than male unemployment.

        • Current gender gap: **{gap_latest:.2f} percentage points**

        • Highest female unemployment:
          **{highest_female['Female']:.2f}%**
          in **{int(highest_female['Year'])}**

        • Recent years show elevated unemployment levels linked to economic challenges.
        """
    )

    # --------------------------------------------------
    # TOTAL UNEMPLOYMENT CHART
    # --------------------------------------------------
    st.subheader("📉 Total Unemployment Trend")

    fig_total = px.area(
        filtered_df,
        x="Year",
        y="Total",
        title="Total Unemployment Rate Over Time"
    )

    st.plotly_chart(fig_total, use_container_width=True)

    # --------------------------------------------------
    # GENDER COMPARISON
    # --------------------------------------------------
    st.subheader("👩 Female vs 👨 Male Unemployment")

    gender_df = filtered_df.melt(
        id_vars="Year",
        value_vars=["Female", "Male"],
        var_name="Gender",
        value_name="Rate"
    )

    fig_gender = px.line(
        gender_df,
        x="Year",
        y="Rate",
        color="Gender",
        markers=True,
        title="Gender Comparison"
    )

    st.plotly_chart(fig_gender, use_container_width=True)

    # --------------------------------------------------
    # ALL SERIES
    # --------------------------------------------------
    st.subheader("📊 Total, Female and Male Trends")

    all_df = filtered_df.melt(
        id_vars="Year",
        value_vars=["Total", "Female", "Male"],
        var_name="Series",
        value_name="Rate"
    )

    fig_all = px.line(
        all_df,
        x="Year",
        y="Rate",
        color="Series",
        markers=True,
        title="Unemployment Trends"
    )

    st.plotly_chart(fig_all, use_container_width=True)

    # --------------------------------------------------
    # GENDER GAP
    # --------------------------------------------------
    st.subheader("⚖️ Gender Gap Analysis")

    filtered_df["Gap"] = (
        filtered_df["Female"] -
        filtered_df["Male"]
    )

    fig_gap = px.bar(
        filtered_df,
        x="Year",
        y="Gap",
        color="Gap",
        title="Female-Male Unemployment Gap"
    )

    st.plotly_chart(fig_gap, use_container_width=True)

    # --------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------
    st.subheader("📋 Data Explorer")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # --------------------------------------------------
    # DOWNLOAD BUTTON
    # --------------------------------------------------
    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name="lebanon_unemployment.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
