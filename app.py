from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="The Invisible Workforce | Lebanon",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LFS_FILE = DATA_DIR / "Labour-force-FULFS-2022.xlsx"
HISTORICAL_FILE = DATA_DIR / "unemployment rate women.xlsx"

# =====================================================
# COLORS
# =====================================================

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

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp{
    background:#F7F8F6;
}

.block-container{
    max-width:1250px;
}

.hero{
    background:linear-gradient(
        120deg,
        #122B3A,
        #1E5260
    );
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
    margin-top:10px;
}

</style>
""",
unsafe_allow_html=True)

# =====================================================
# HISTORICAL DATA
# =====================================================

@st.cache_data
def load_historical_data():

    raw = pd.read_excel(
        HISTORICAL_FILE,
        engine="openpyxl"
    )

    raw = raw.iloc[8:].copy()

    raw.columns = [
        "Year",
        "Total unemployment",
        "Female unemployment",
        "Male unemployment"
    ]

    raw["Year"] = pd.to_numeric(
        raw["Year"],
        errors="coerce"
    )

    return raw.dropna()

# =====================================================
# EXCEL HELPERS
# =====================================================

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
 # =====================================================
# LOAD SURVEY
# =====================================================

@st.cache_data
def load_survey():

    if not LFS_FILE.exists():
        st.error(
            f"Missing file: {LFS_FILE}"
        )
        st.stop()

    # EA40
    age_lfp = read_section(
        "EA40",
        6,
        17
    )

    education_lfp = read_section(
        "EA40",
        18,
        25
    )

    # EA39
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

    # EA6
    employed_education = read_section(
        "EA6",
        6,
        13
    )

    # EA8
    employment_status = read_section(
        "EA8",
        7,
        12
    )

    # EA37
    job_search = read_section(
        "EA37",
        7,
        12
    )

    # EA3
    ea3 = read_sheet("EA3")

    status = ea3.iloc[16:19,0:4].copy()

    status.columns = [
        "Gender",
        "Employed",
        "Unemployed",
        "Outside labour force"
    ]

    for col in [
        "Employed",
        "Unemployed",
        "Outside labour force"
    ]:
        status[col] = pd.to_numeric(
            status[col],
            errors="coerce"
        )

    status = status.dropna()

    return (
        age_lfp,
        education_lfp,
        age_unemployment,
        education_unemployment,
        employed_education,
        employment_status,
        job_search,
        status
    )
@st.cache_data
def load_headline_indicators():
    raw = read_sheet("EA1")
    return {
        "women_participation":
            float(raw.iloc[6,3]),

        "men_participation":
            float(raw.iloc[6,4]),

        "overall_participation":
            float(raw.iloc[6,5]),

        "women_unemployment":
            float(raw.iloc[8,3]),

        "men_unemployment":
            float(raw.iloc[8,4]),

        "overall_unemployment":
            float(raw.iloc[8,5])
    }
historical = load_historical_data()

(
    age_lfp,
    education_lfp,
    age_unemployment,
    education_unemployment,
    employed_education,
    employment_status,
    job_search,
    status_by_gender
) = load_survey()

headline = load_headline_indicators()

participation_gap = (
    headline["men_participation"]
    -
    headline["women_participation"]
) 
st.markdown(
f"""
<div class="hero">

<h1>
The Invisible Workforce
</h1>

<p>
Understanding gender,
education and paid employment
in Lebanon.
</p>

</div>
""",
unsafe_allow_html=True
)

st.write(
"""
This dashboard explores labour-force
participation, unemployment,
education and employment patterns
using Lebanon's 2022 Labour Force Survey.
"""
)
st.subheader(
    "Headline Indicators"
)

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Women Participation",
    f"{headline['women_participation']:.1f}%"
)

c2.metric(
    "Men Participation",
    f"{headline['men_participation']:.1f}%"
)

c3.metric(
    "Participation Gap",
    f"{participation_gap:.1f} pp"
)

c4.metric(
    "Women Unemployment",
    f"{headline['women_unemployment']:.1f}%"
)
st.markdown(
f"""
<div class="insight">

<b>Key Observation</b><br>

Women's labour-force participation:

<strong>
{headline['women_participation']:.1f}%
</strong>

<br><br>

Men's labour-force participation:

<strong>
{headline['men_participation']:.1f}%
</strong>

<br><br>

Gap:

<strong>
{participation_gap:.1f}
percentage points
</strong>

</div>
""",
unsafe_allow_html=True
)
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
        How do gender,
        education and age
        influence participation
        in Lebanon's labour market?
        """
    )

    a,b,c = st.columns(3)

    with a:
        st.markdown("""
        ### Participation

        Who is employed,
        unemployed,
        or outside
        the labour force?
        """)

    with b:
        st.markdown("""
        ### Education

        How do education levels
        affect labour outcomes?
        """)

    with c:
        st.markdown("""
        ### Age

        At what ages are
        gender gaps largest?
        """)
with story_tab:
     st.header("Story")
st.caption(
        """
        Use filters and interactive charts
        to examine gender differences
        across age and education.
        """
    )
    st.subheader(
        "1. Historical Unemployment Trends"
    )

    historical_long = historical.melt(
        id_vars="Year",
        value_vars=[
            "Total unemployment",
            "Female unemployment",
            "Male unemployment"
        ],
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
        **PLOT_LAYOUT,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "ILO modelled unemployment estimates."
    )
    st.subheader(
        "2. Unemployment by Gender"
    )

    gender_unemployment = pd.DataFrame({
        "Gender": ["Women", "Men"],
        "Rate": [
            headline["women_unemployment"],
            headline["men_unemployment"]
        ]
    })

    fig = px.bar(
        gender_unemployment,
        x="Gender",
        y="Rate",
        color="Gender",
        text_auto=".1f",
        color_discrete_map=COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "3. Unemployment by Age"
    )

    age_un_long = age_unemployment.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Unemployment"
    )

    fig = px.line(
        age_un_long,
        x="Category",
        y="Unemployment",
        color="Gender",
        markers=True,
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
        "4. Participation by Age"
    )

    age_options = (
        age_lfp["Category"]
        .tolist()
    )

    selected_ages = st.multiselect(
        "Select Age Groups",
        options=age_options,
        default=age_options
    )

    age_view = age_lfp[
        age_lfp["Category"]
        .isin(selected_ages)
    ]

    age_long = age_view.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Participation"
    )

    fig = px.line(
        age_long,
        x="Category",
        y="Participation",
        color="Gender",
        markers=True,
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
        "5. Participation by Education"
    )

    education_options = (
        education_lfp["Category"]
        .tolist()
    )

    selected_education = st.multiselect(
        "Select Education Levels",
        options=education_options,
        default=education_options
    )

    education_view = education_lfp[
        education_lfp["Category"]
        .isin(selected_education)
    ]

    education_long = education_view.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Participation"
    )

    fig = px.bar(
        education_long,
        x="Category",
        y="Participation",
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
        "6. Education Composition of Workers"
    )

    employed_long = employed_education.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Share"
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
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "7. Employment Status"
    )

    employment_long = employment_status.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Share"
    )

    fig = px.bar(
        employment_long,
        x="Category",
        y="Share",
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
        "8. Job Search Methods"
    )

    search_long = job_search.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Share"
    )

    fig = px.bar(
        search_long,
        x="Category",
        y="Share",
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
        label="Download Participation Data",
        data=education_lfp.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="participation.csv",
        mime="text/csv"
    )
with findings_tab:

    st.header(
        "What Does The Evidence Suggest?"
    )

    st.write(
        """
        These findings describe patterns
        observed in the survey.
        They do not establish causality.
        """
    )
    st.subheader(
        "A. Education and Participation"
    )

    education_long = education_lfp.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Participation"
    )

    fig = px.bar(
        education_long,
        x="Category",
        y="Participation",
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
    university = education_lfp[
        education_lfp["Category"]
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
            University education participation:

            Women: {female_rate:.1f}%

            Men: {male_rate:.1f}%

            Gap:
            {(male_rate-female_rate):.1f}
            percentage points
            """
        )
         st.subheader(
        "B. Participation Gap by Age"
    )

    age_gap = age_lfp.copy()

    age_gap["Gap"] = (
        age_gap["Men"]
        -
        age_gap["Women"]
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
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "C. Economic Status"
    )

    status_long = status_by_gender.melt(
        id_vars="Gender",
        value_vars=[
            "Employed",
            "Unemployed",
            "Outside labour force"
        ],
        var_name="Status",
        value_name="Share"
    )

    fig = px.bar(
        status_long,
        x="Gender",
        y="Share",
        color="Status",
        barmode="stack",
        color_discrete_map=STATUS_COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "C. Economic Status"
    )

    status_long = status_by_gender.melt(
        id_vars="Gender",
        value_vars=[
            "Employed",
            "Unemployed",
            "Outside labour force"
        ],
        var_name="Status",
        value_name="Share"
    )

    fig = px.bar(
        status_long,
        x="Gender",
        y="Share",
        color="Status",
        barmode="stack",
        color_discrete_map=STATUS_COLORS
    )

    fig.update_layout(
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader(
        "D. Employment Categories"
    )

    fig = px.bar(
        employment_long,
        x="Category",
        y="Share",
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

    employees = employment_status[
        employment_status["Category"]
        .str.contains(
            "Employee",
            case=False,
            na=False
        )
    ]

    if not employees.empty:

        st.success(
            f"""
            Employees account for
            {employees.iloc[0]['Women']:.1f}% of employed women

            and

            {employees.iloc[0]['Men']:.1f}% of employed men.
            """
        )
    st.subheader(
        "E. Unemployment by Education"
    )

    unemployment_long = education_unemployment.melt(
        id_vars="Category",
        value_vars=[
            "Women",
            "Men"
        ],
        var_name="Gender",
        value_name="Rate"
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
        **PLOT_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.warning(
        """
        The available survey tables do not
        provide marital status or household
        composition cross-tabulations.

        Additional microdata would be needed.
        """
    )
with action_tab:

    st.header(
        "From Evidence To Action"
    )
    st.markdown("""
    ### Education-to-Employment Bridge

    Strengthen internships,
    apprenticeships and
    employer partnerships.
    """)
    st.markdown("""
    ### Work and Care Support

    Improve access to childcare,
    flexible work and
    safe transportation.
    """)
    st.markdown("""
    ### Return-to-Work Pathways

    Support women returning
    to employment through
    retraining and mentoring.
    """)
    st.markdown("""
    ### Opportunity Tracking

    Monitor hiring,
    promotion and pay gaps.
    """)
with methods_tab:

    st.header(
        "Methodology & Sources"
    )

    st.markdown("""
    **National Source**

    Lebanon Labour Force and
    Household Living Conditions Survey 2022.

    Tables:
    EA1, EA3,
    EA6, EA8,
    EA37, EA39,
    EA40.
    """)
    st.markdown("""
    **Historical Source**

    Historical unemployment dataset
    from 1991–2023.

    Total, female and male rates.
    """)
    st.markdown("""
    **Approach**

    Descriptive analysis of:

    - Labour-force participation
    - Unemployment
    - Education
    - Employment status
    - Job-search behaviour
    """)
    st.markdown("""
    **Limitations**

    - Cross-sectional design
    - No causal interpretation
    - Missing household variables
    """)
st.markdown("---")

st.caption(
    """
    The Invisible Workforce
    • Lebanon
    • Interactive Labour Market Dashboard
    """
)

