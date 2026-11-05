from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="The Invisible Workforce | Lebanon",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LFS_FILE = DATA_DIR / "Labour-force-FULFS-2022.xlsx"
HISTORICAL_FILE = DATA_DIR / "unemployment rate women.xlsx"

COLORS = {
    "Women": "#D96C5F",
    "Men": "#087E8B",
    "Women & Men": "#D7A84B"
}

STATUS_COLORS = {
    "Employed": "#087E8B",
    "Unemployed": "#D7A84B",
    "Outside labour force": "#D96C5F"
}

PLOT_LAYOUT = {
    "template": "plotly_white",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "legend_title_text": ""
}

st.markdown("""
<style>
.stApp{
    background:#F7F8F6;
}
.block-container{
    max-width:1250px;
}
.hero{
    background:linear-gradient(120deg,#122B3A,#1E5260);
    padding:2rem;
    border-radius:18px;
    color:white;
    margin-bottom:20px;
}
.insight{
    background:white;
    border-left:4px solid #087E8B;
    padding:1rem;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)
@st.cache_data
def load_historical_data():

    df = pd.read_excel(
        HISTORICAL_FILE,
        engine="openpyxl"
    )

    df = df.iloc[8:].copy()

    df.columns = [
        "Year",
        "Total unemployment",
        "Female unemployment",
        "Male unemployment"
    ]

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    return df.dropna()
    def read_sheet(sheet):

    return pd.read_excel(
        LFS_FILE,
        sheet_name=sheet,
        header=None,
        engine="openpyxl"
    )


def read_section(
    sheet_name,
    start_row,
    end_row
):

    raw = read_sheet(sheet_name)

    table = raw.iloc[
        start_row:end_row,
        0:4
    ].copy()

    table.columns = [
        "Category",
        "Women",
        "Men",
        "Women & Men"
    ]

    for col in [
        "Women",
        "Men",
        "Women & Men"
    ]:
        table[col] = pd.to_numeric(
            table[col],
            errors="coerce"
        )

    table["Category"] = (
        table["Category"]
        .astype(str)
        .str.strip()
    )

    table = table.dropna()

    return table.reset_index(drop=True)
    @st.cache_data
def load_survey():

    if not LFS_FILE.exists():
        st.error(
            f"Missing file: {LFS_FILE}"
        )
        st.stop()

    age_lfp = read_section("EA40", 6, 17)
    education_lfp = read_section("EA40", 18, 25)

    age_unemployment = read_section("EA39", 6, 17)
    education_unemployment = read_section("EA39", 18, 25)

    employed_education = read_section("EA6", 6, 13)

    employment_status = read_section("EA8", 7, 12)

    job_search = read_section("EA37", 7, 12)

    return (
        age_lfp,
        education_lfp,
        age_unemployment,
        education_unemployment,
        employed_education,
        employment_status,
        job_search
    )
historical = load_historical_data()

(
    age_lfp,
    education_lfp,
    age_unemployment,
    education_unemployment,
    employed_education,
    employment_status,
    job_search
) = load_survey()
# =====================================================
# HERO SECTION
# =====================================================

st.markdown(
    """
    <div class="hero">
        <h1>The Invisible Workforce</h1>
        <p>
        Understanding gender, education and paid
        employment in Lebanon.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# TABS
# =====================================================

story_tab, explore_tab, findings_tab, action_tab, methods_tab = st.tabs(
    [
        "The Story",
        "Explore Data",
        "Key Findings",
        "From Evidence To Action",
        "Methodology"
    ]
)
with story_tab:

    st.header(
        "The Question Behind The Numbers"
    )

    st.write(
        """
        How do gender, education and age influence
        labour-force participation in Lebanon?
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### Participation

        Who is employed,
        unemployed,
        or outside the labour force?
        """)

    with col2:
        st.markdown("""
        ### Education

        How do education levels shape opportunities?
        """)

    with col3:
        st.markdown("""
        ### Age

        At what ages do gender gaps become largest?
        """)
        with explore_tab:

    st.header(
        "Explore Data"
    )

    historical_long = historical.melt(
        id_vars="Year",
        var_name="Indicator",
        value_name="Rate"
    )

    fig = px.line(
        historical_long,
        x="Year",
        y="Rate",
        color="Indicator",
        markers=True
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
        st.subheader(
        "Participation by Age"
    )

    age_options = age_lfp["Category"].tolist()

    selected_ages = st.multiselect(
        "Select Age Groups",
        age_options,
        default=age_options
    )

    age_filtered = age_lfp[
        age_lfp["Category"].isin(
            selected_ages
        )
    ]

    age_long = age_filtered.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name="Participation"
    )

    fig = px.line(
        age_long,
        x="Category",
        y="Participation",
        color="Gender",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "Participation by Education"
    )

    education_options = (
        education_lfp["Category"]
        .tolist()
    )

    selected_education = st.multiselect(
        "Select Education Levels",
        education_options,
        default=education_options
    )

    education_filtered = education_lfp[
        education_lfp["Category"].isin(
            selected_education
        )
    ]

    education_long = education_filtered.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name="Participation"
    )

    fig = px.bar(
        education_long,
        x="Category",
        y="Participation",
        color="Gender",
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    with st.expander(
        "View Data Tables"
    ):

        st.dataframe(age_lfp)

        st.dataframe(
            education_lfp
        )

        st.dataframe(
            education_unemployment
        )
            st.download_button(
        label="Download CSV",
        data=education_lfp.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="education_data.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download CSV",
        data=education_lfp.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="education_data.csv",
        mime="text/csv"
    )
with findings_tab:

    st.header(
        "Key Findings"
    )

    st.write(
        """
        Gender differences in labour force
        participation remain substantial.
        """
    )

    st.dataframe(
        education_lfp
    )
with action_tab:

    st.header(
        "From Evidence To Action"
    )

    st.markdown(
        """
        ### Education-to-Employment Bridge

        Strengthen internships,
        apprenticeships,
        and employer partnerships.
        """
    )

    st.markdown(
        """
        ### Work and Care Support

        Expand childcare,
        transport access,
        and workplace flexibility.
        """
    )
with methods_tab:

    st.header(
        "Methodology"
    )

    st.markdown(
        """
        **Data Sources**

        - Labour-force-FULFS-2022.xlsx
        - unemployment rate women.xlsx

        **Analysis**
        - Participation
        - Unemployment
        - Education
        - Employment status
        """
    )
st.markdown("---")

st.caption(
    "The Invisible Workforce • Lebanon • Interactive Dashboard"
)
    st.subheader(
        "Participation Gap by Age"
    )

    age_gap = age_lfp.copy()

    age_gap["Gap"] = (
        age_gap["Men"]
        - age_gap["Women"]
    )

    fig = px.bar(
        age_gap,
        x="Category",
        y="Gap",
        color="Gap",
        color_continuous_scale=[
            "#F2C7BF",
            "#D96C5F"
        ]
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    university = education_lfp[
        education_lfp["Category"]
        .astype(str)
        .str.contains(
            "University",
            case=False,
            na=False
        )
    ]

    if not university.empty:

        female_rate = university.iloc[0]["Women"]
        male_rate = university.iloc[0]["Men"]

        st.info(
            f"""
            University Education Participation

            Women: {female_rate:.1f}%

            Men: {male_rate:.1f}%

            Gap:
            {(male_rate - female_rate):.1f}
            percentage points
            """
        )
    st.subheader(
        "Unemployment by Education"
    )

    unemployment_long = (
        education_unemployment.melt(
            id_vars="Category",
            value_vars=[
                "Women",
                "Men"
            ],
            var_name="Gender",
            value_name="Rate"
        )
    )

    fig = px.bar(
        unemployment_long,
        x="Category",
        y="Rate",
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "Employment Distribution"
    )

    employed_long = (
        employed_education.melt(
            id_vars="Category",
            value_vars=[
                "Women",
                "Men"
            ],
            var_name="Gender",
            value_name="Share"
        )
    )

    fig = px.bar(
        employed_long,
        x="Category",
        y="Share",
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    if "status_by_gender" in locals():

        st.subheader(
            "Economic Status"
        )

        status_long = (
            status_by_gender.melt(
                id_vars="Gender",
                value_vars=[
                    "Employed",
                    "Unemployed",
                    "Outside labour force"
                ],
                var_name="Status",
                value_name="Share"
            )
        )

        fig = px.bar(
            status_long,
            x="Gender",
            y="Share",
            color="Status",
            barmode="stack"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
            if "status_by_gender" in locals():

        st.subheader(
            "Economic Status"
        )

        status_long = (
            status_by_gender.melt(
                id_vars="Gender",
                value_vars=[
                    "Employed",
                    "Unemployed",
                    "Outside labour force"
                ],
                var_name="Status",
                value_name="Share"
            )
        )

        fig = px.bar(
            status_long,
            x="Gender",
            y="Share",
            color="Status",
            barmode="stack"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    st.success(
        """
        Key Insights

        • Women participate less in the labour market.

        • Education improves participation.

        • Youth unemployment remains high.

        • Gender gaps persist across age groups.
        """
    )

        
