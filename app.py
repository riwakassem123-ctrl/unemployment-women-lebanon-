from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="The Invisible Workforce | Lebanon",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

LFS_FILE = DATA_DIR / "Labour-force-FULFS-2022.xlsx"
WOMEN_FILE = DATA_DIR / "women unemployment rate.xlsx"

# --------------------------------------------------
# COLORS
# --------------------------------------------------

COLORS = {
    "Women": "#D96C5F",
    "Men": "#087E8B",
    "Women & Men": "#D7A84B"
}

PLOT_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=60, b=40)
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background:#F7F8F6;
}

.hero{
    background:linear-gradient(120deg,#122B3A,#1E5260);
    padding:2rem;
    border-radius:18px;
    color:white;
    margin-bottom:1rem;
}

.hero h1{
    color:white;
}

.insight{
    background:white;
    padding:1rem;
    border-left:4px solid #087E8B;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def read_section(sheet_name, start_row, end_row):

    raw = pd.read_excel(
        LFS_FILE,
        sheet_name=sheet_name,
        header=None
    )

    df = raw.iloc[start_row:end_row, 0:4].copy()

    df.columns = [
        "Category",
        "Women",
        "Men",
        "Women & Men"
    ]

    df["Category"] = df["Category"].astype(str).str.strip()

    for c in ["Women", "Men", "Women & Men"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["Women", "Men"])

    return df


@st.cache_data
def load_survey():

    headline_raw = pd.read_excel(
        LFS_FILE,
        sheet_name="EA1",
        header=None
    )

    headline = {}

    for row in range(6, 12):

        label = str(
            headline_raw.iloc[row, 0]
        ).strip()

        headline[label] = {
            "Women": pd.to_numeric(
                headline_raw.iloc[row, 1],
                errors="coerce"
            ),
            "Men": pd.to_numeric(
                headline_raw.iloc[row, 2],
                errors="coerce"
            ),
            "Women & Men": pd.to_numeric(
                headline_raw.iloc[row, 3],
                errors="coerce"
            )
        }

    age_lfp = read_section("EA40", 6, 17)

    education_lfp = read_section(
        "EA40",
        18,
        25
    )

    age_unemployment = read_section(
        "EA39",
        6,
        17
    )

    education_unemployment = read_section(
        "EA39",
        18,
        25
    )

    employed_education = read_section(
        "EA6",
        6,
        13
    )

    return (
        headline,
        age_lfp,
        education_lfp,
        age_unemployment,
        education_unemployment,
        employed_education
    )


@st.cache_data
def load_women_history():

    df = pd.read_excel(WOMEN_FILE)

    columns = list(df.columns)

    year_col = columns[0]
    value_col = columns[1]

    df = df[[year_col, value_col]]

    df.columns = ["Year", "Rate"]

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    df["Rate"] = pd.to_numeric(
        df["Rate"],
        errors="coerce"
    )

    return df.dropna()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:

    (
        headline,
        age_lfp,
        education_lfp,
        age_unemployment,
        education_unemployment,
        employed_education
    ) = load_survey()

    women_history = load_women_history()

except Exception as e:

    st.error(str(e))
    st.stop()

# --------------------------------------------------
# HEADLINE VALUES
# --------------------------------------------------

lfp = headline.get(
    "Labour Force Participation Rate",
    {}
)

unemployment = headline.get(
    "LU1: Unemployment rate",
    {}
)

participation_gap = (
    lfp.get("Men", 0)
    - lfp.get("Women", 0)
)

# --------------------------------------------------
# HERO
# --------------------------------------------------

st.markdown(
"""
<div class="hero">
<h1>The Invisible Workforce</h1>
<p>
Understanding gender,
education and employment in Lebanon.
</p>
</div>
""",
unsafe_allow_html=True
)

# --------------------------------------------------
# METRICS
# --------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Women LFP",
    f"{lfp.get('Women',0):.1f}%"
)

c2.metric(
    "Men LFP",
    f"{lfp.get('Men',0):.1f}%"
)

c3.metric(
    "Participation Gap",
    f"{participation_gap:.1f} pp"
)

c4.metric(
    "Women Unemployment",
    f"{unemployment.get('Women',0):.1f}%"
)

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Explore Data",
    "Findings"
])

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

with tab1:

    st.markdown(
        f"""
        <div class="insight">
        Labour-force participation was
        {lfp.get('Women',0):.1f}% for women
        compared with
        {lfp.get('Men',0):.1f}% for men.
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# EXPLORE
# --------------------------------------------------

with tab2:

    st.subheader(
        "Female Unemployment Trend"
    )

    fig = px.line(
        women_history,
        x="Year",
        y="Rate",
        markers=True,
        title="Female unemployment rate"
    )

    fig.update_traces(
        line_color="#D96C5F"
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Participation By Age"
    )

    age_long = age_lfp.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name="Rate"
    )

    fig = px.bar(
        age_long,
        x="Category",
        y="Rate",
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Participation By Education"
    )

    edu_long = education_lfp.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name="Rate"
    )

    fig = px.bar(
        edu_long,
        x="Category",
        y="Rate",
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# FINDINGS
# --------------------------------------------------

with tab3:

    st.subheader(
        "Education and Participation"
    )

    edu_gap = education_lfp.copy()

    edu_gap["Gap"] = (
        edu_gap["Men"]
        - edu_gap["Women"]
    )

    st.dataframe(
        edu_gap,
        use_container_width=True
    )

    st.subheader(
        "Unemployment By Education"
    )

    unemp_long = education_unemployment.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name="Rate"
    )

    fig = px.bar(
        unemp_long,
        x="Category",
        y="Rate",
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("---")
st.caption(
    "The Invisible Workforce | Lebanon"
)
