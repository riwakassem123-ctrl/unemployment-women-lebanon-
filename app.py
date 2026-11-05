from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION AND FILE PATHS
# ============================================================

st.set_page_config(
    page_title="The Invisible Workforce | Lebanon",
    page_icon="📊",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def find_input_file(expected_name, keywords):
    """Find an Excel workbook in the project folder or its data subfolder."""
    candidates = []
    for root in (DATA_DIR, BASE_DIR):
        if root.exists():
            candidates.extend(
                p for p in root.rglob("*")
                if p.is_file() and p.suffix.lower() in {".xlsx", ".xls"}
            )
    expected = expected_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    for file in candidates:
        stem = file.stem.lower().replace(" ", "").replace("-", "").replace("_", "")
        if stem == expected:
            return file
    for file in candidates:
        stem = file.stem.lower()
        if all(word.lower() in stem for word in keywords):
            return file
    return None

# Keep these two Excel workbooks beside app.py or inside a folder named data.
LFS_FILE = find_input_file("Labour-force-FULFS-2022", ["labour", "2022"])
HISTORICAL_FILE = find_input_file("unemployment rate women", ["unemployment", "women"])


# ============================================================
# 2. COLORS AND CHART STYLE
# ============================================================

COLORS = {
    "Women": "#D96C5F",
    "Men": "#087E8B",
    "Women & Men": "#D7A84B",
}

STATUS_COLORS = {
    "Employed": "#087E8B",
    "Unemployed": "#D7A84B",
    "Outside labour force": "#D96C5F",
}

PLOT_LAYOUT = {
    "template": "plotly_white",
    "font": {"family": "Arial", "color": "#172A3A"},
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": {"l": 25, "r": 25, "t": 65, "b": 45},
    "legend_title_text": "",
}


# ============================================================
# 3. PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F7F8F6;
    }
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        background: linear-gradient(120deg, #122B3A, #1E5260);
        padding: 2.4rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.4rem;
    }
    .hero h1 {
        color: white;
        font-size: 3rem;
        line-height: 1.1;
        margin-bottom: .6rem;
    }
    .hero p {
        color: #E6F0F0;
        font-size: 1.08rem;
    }
    .insight {
        background: white;
        border-left: 4px solid #087E8B;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin: .7rem 0 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ============================================================

def load_historical_data():
    if HISTORICAL_FILE is None or not HISTORICAL_FILE.exists():
        raise FileNotFoundError(
            "Historical Excel workbook not found. "
            "Check the filename and location."
        )

    excel = pd.ExcelFile(HISTORICAL_FILE)

    for sheet in excel.sheet_names:
        raw = pd.read_excel(
            HISTORICAL_FILE,
            sheet_name=sheet,
            header=None
        )

        # E = Year, F = Total, G = Female, H = Male
        if raw.shape[1] < 8:
            continue

        result = pd.DataFrame({
            "Year": pd.to_numeric(raw.iloc[:, 4], errors="coerce"),

            "Total unemployment": pd.to_numeric(
                raw.iloc[:, 5].astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False),
                errors="coerce"
            ),

            "Female unemployment": pd.to_numeric(
                raw.iloc[:, 6].astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False),
                errors="coerce"
            ),

            "Male unemployment": pd.to_numeric(
                raw.iloc[:, 7].astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False),
                errors="coerce"
            )
        })

        result = result[
            result["Year"].between(1991, 2023)
        ].dropna()

        if not result.empty:
            result["Year"] = result["Year"].astype(int)

            result = (
                result
                .drop_duplicates(subset="Year")
                .sort_values("Year")
                .reset_index(drop=True)
            )

            return result

    raise ValueError(
        "Historical data could not be read from columns E, F, G and H. "
        "Please check the workbook."
    )



# 5. SURVEY DATA HELPERS
# ============================================================

def read_section(sheet_name, start_row, end_row):
    """Read a verified four-column section from the survey workbook."""
    raw = pd.read_excel(
        LFS_FILE,
        sheet_name=sheet_name,
        header=None,
    )

    # EA39 and EA40 place the Men and Women & Men values in
    # columns D and E, with a blank spacer column C.
    if sheet_name in {"EA39", "EA40"}:
        table = raw.iloc[start_row:end_row, [0, 1, 3, 4]].copy()
    else:
        table = raw.iloc[start_row:end_row, 0:4].copy()

    table.columns = ["Category", "Women", "Men", "Women & Men"]

    table["Category"] = table["Category"].astype(str).str.strip()

    for column in ["Women", "Men", "Women & Men"]:
        table[column] = pd.to_numeric(table[column], errors="coerce")

    table = table.dropna(subset=["Women", "Men"])
    table = table[
        ~table["Category"].str.lower().isin(["", "nan", "total"])
    ]

    return table.reset_index(drop=True)


def find_indicator(indicators, keyword):
    """Find an EA1 indicator by a distinctive part of its label."""
    for label, values in indicators.items():
        if keyword.lower() in label.lower():
            return values

    raise KeyError(
        f"Could not find the indicator containing '{keyword}' in EA1."
    )


@st.cache_data(show_spinner=False)
def load_survey():
    if LFS_FILE is None or not LFS_FILE.exists():
        raise FileNotFoundError(
            "2022 labour-force workbook not found. Place "
            "'Labour-force-FULFS-2022.xlsx' in the project folder or data folder."
        )

    available_sheets = pd.ExcelFile(LFS_FILE).sheet_names
    required_sheets = ["EA1", "EA3", "EA6", "EA8", "EA37", "EA39", "EA40"]
    missing_sheets = [
        sheet for sheet in required_sheets
        if sheet not in available_sheets
    ]

    if missing_sheets:
        raise ValueError(
            "The survey workbook is missing sheets: "
            + ", ".join(missing_sheets)
        )

    # EA1: Main labour-force indicators. Rows 6-11, columns A-D.
    headline_raw = pd.read_excel(
        LFS_FILE,
        sheet_name="EA1",
        header=None,
    )

    indicators = {}

    for row_index in range(6, 12):
        label = str(headline_raw.iloc[row_index, 0]).strip()

        if not label or label.lower() == "nan":
            continue

        indicators[label] = {
            "Women": pd.to_numeric(
                headline_raw.iloc[row_index, 1], errors="coerce"
            ),
            "Men": pd.to_numeric(
                headline_raw.iloc[row_index, 2], errors="coerce"
            ),
            "Women & Men": pd.to_numeric(
                headline_raw.iloc[row_index, 3], errors="coerce"
            ),
        }

    # EA40: Age rows 6-16; education rows 18-24.
    age_lfp = read_section("EA40", 6, 17)
    education_lfp = read_section("EA40", 18, 25)

    # EA39: Age rows 6-16; education rows 18-24.
    age_unemployment = read_section("EA39", 6, 17)
    education_unemployment = read_section("EA39", 18, 25)

    # EA6A: Employed population by completed education, rows 6-12.
    employed_education = read_section("EA6", 6, 13)

    # EA8A: Employment status among employed people, rows 7-11.
    employment_status = read_section("EA8", 7, 12)

    # EA37A: Job-search methods, rows 7-11.
    job_search = read_section("EA37", 7, 12)

    # EA3B: Economic status by sex, rows 16-17.
    status_raw = pd.read_excel(
        LFS_FILE,
        sheet_name="EA3",
        header=None,
    )

    status = status_raw.iloc[16:18, 0:4].copy()
    status.columns = [
        "Gender",
        "Employed",
        "Unemployed",
        "Outside labour force",
    ]

    status["Gender"] = status["Gender"].astype(str).str.strip()

    for column in ["Employed", "Unemployed", "Outside labour force"]:
        status[column] = pd.to_numeric(status[column], errors="coerce")

    status = status.dropna(
        subset=["Employed", "Unemployed", "Outside labour force"]
    )

    return {
        "indicators": indicators,
        "age_lfp": age_lfp,
        "education_lfp": education_lfp,
        "age_unemployment": age_unemployment,
        "education_unemployment": education_unemployment,
        "employed_education": employed_education,
        "employment_status": employment_status,
        "job_search": job_search,
        "status": status,
    }


# ============================================================
# 6. GENERAL CHART HELPERS
# ============================================================

def to_long(data, value_name):
    return data.melt(
        id_vars="Category",
        value_vars=["Women", "Men"],
        var_name="Gender",
        value_name=value_name,
    )


def draw_gender_bar(data, value_name, title, y_title):
    if data.empty:
        st.warning("No observations are available for this chart.")
        return

    long_data = to_long(data, value_name)

    fig = px.bar(
        long_data,
        x="Category",
        y=value_name,
        color="Gender",
        barmode="group",
        color_discrete_map=COLORS,
        title=title,
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="",
        yaxis_title=y_title,
        xaxis_tickangle=-12,
    )

    st.plotly_chart(fig, use_container_width=True)
    key="row_gender_bar_chart"

def draw_gender_line(data, value_name, title, y_title):
    if data.empty:
        st.warning("No observations are available for this chart.")
        return

    long_data = to_long(data, value_name)

    fig = px.line(
        long_data,
        x="Category",
        y=value_name,
        color="Gender",
        markers=True,
        color_discrete_map=COLORS,
        title=title,
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="",
        yaxis_title=y_title,
    )

# ============================================================
# 7. LOAD AND VALIDATE DATA
# ============================================================

try:
    historical = load_historical_data()
    survey = load_survey()

    indicators = survey["indicators"]
    age_lfp = survey["age_lfp"]
    education_lfp = survey["education_lfp"]
    age_unemployment = survey["age_unemployment"]
    education_unemployment = survey["education_unemployment"]
    employed_education = survey["employed_education"]
    employment_status = survey["employment_status"]
    job_search = survey["job_search"]
    status_by_gender = survey["status"]

    lfp = find_indicator(indicators, "Labour Force Participation Rate")
    unemployment = find_indicator(indicators, "LU1: Unemployment rate")

except Exception as error:
    st.error(
        "The dashboard could not load the data. "
        "Check the workbook filename and worksheet structure."
    )
    st.exception(error)
    st.stop()


# ============================================================
# 8. HEADLINE CALCULATIONS
# ============================================================

participation_gap = lfp["Men"] - lfp["Women"]
unemployment_gap = unemployment["Women"] - unemployment["Men"]


# ============================================================
# 9. DASHBOARD HEADER AND HEADLINE METRICS
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div style="
            letter-spacing: .14em;
            text-transform: uppercase;
            font-size: .75rem;
            color: #9DD4D3;
            font-weight: 700;
        ">
            Lebanon · Labour market · 2022
        </div>
        <h1>The Invisible Workforce</h1>
        <p>
            <b>Understanding gender, education and paid employment in Lebanon.</b>
            <br>
            Explore how labour-force participation and unemployment
            differ between women and men, and how these patterns
            vary by age and education.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "This interactive research blog examines gender differences "
    "in Lebanon's labour market using the 2022 Labour Force and "
    "Household Living Conditions Survey and the historical "
    "unemployment table supplied with the project."
)

st.subheader("The headline indicators")

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "Women's labour-force participation",
    f"{lfp['Women']:.1f}%",
)
metric2.metric(
    "Men's labour-force participation",
    f"{lfp['Men']:.1f}%",
)
metric3.metric(
    "Participation gap",
    f"{participation_gap:.1f} pp",
)
metric4.metric(
    "Women's unemployment rate",
    f"{unemployment['Women']:.1f}%",
)

st.markdown(
    f"""
    <div class="insight">
        <b>Key observation:</b>
        Labour-force participation was {lfp['Women']:.1f}% among women
        and {lfp['Men']:.1f}% among men in 2022.
        The difference is {participation_gap:.1f} percentage points.
        Unemployment alone does not capture the full picture because
        people outside the labour force are not counted as unemployed.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 10. NAVIGATION TABS
# ============================================================

story_tab, explore_tab, findings_tab, action_tab, methods_tab = st.tabs(
    [
        "The story",
        "Explore the data",
        "Key findings",
        "From evidence to action",
        "Methodology & sources",
    ]
)


# ============================================================
# 11. THE STORY TAB
# ============================================================

with story_tab:
    st.header("The question behind the numbers")

    st.write(
        "How are gender, educational attainment and age associated "
        "with paid labour participation in Lebanon? And do these "
        "relationships differ between women and men?"
    )

    st.write(
        "The analysis focuses on variables available in the supplied "
        "survey tables. Marital status and household composition are "
        "not included in the available cross-tabulations."
    )

    col1, col2, col3 = st.columns(3)

    col1.markdown(
        "### 01 · Participation\n"
        "Who is employed, unemployed or outside the labour force?"
    )
    col2.markdown(
        "### 02 · Education\n"
        "How do participation and unemployment vary by education?"
    )
    col3.markdown(
        "### 03 · Age\n"
        "At which life stages are gender differences most visible?"
    )

    st.info(
        "The 2022 survey is a cross-sectional snapshot. "
        "It identifies associations and differences, not causal effects."
    )


# ============================================================
# 12. EXPLORE THE DATA TAB
# ============================================================

with explore_tab:
    st.header("Explore the labour-market landscape")

    st.caption(
        "Hover over charts for exact values. Use the filters "
        "to explore selected age groups and education levels."
    )

    st.subheader("1. Historical unemployment, 1991–2023")

    historical_long = historical.melt(
        id_vars="Year",
        value_vars=[
            "Total unemployment",
            "Female unemployment",
            "Male unemployment",
        ],
        var_name="Indicator",
        value_name="Rate",
    )

    historical_colors = {
        "Total unemployment": "#D7A84B",
        "Female unemployment": "#D96C5F",
        "Male unemployment": "#087E8B",
    }

    fig = px.line(
        historical_long,
        x="Year",
        y="Rate",
        color="Indicator",
        markers=True,
        color_discrete_map=historical_colors,
        title="Unemployment estimates for Lebanon, 1991–2023",
        labels={
            "Rate": "Unemployment rate (%)",
            "Year": "Year",
        },
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)
    key="historical _unemployment _detail _chart"
    st.caption(
        f"Historical source: {HISTORICAL_FILE.name}. "
        "Values are loaded directly from the supplied Excel workbook."
    )

    st.subheader("2. Unemployment by gender in 2022")

    gender_unemployment = pd.DataFrame(
        {
            "Gender": ["Women", "Men"],
            "Rate": [unemployment["Women"], unemployment["Men"]],
        }
    )

    fig = px.bar(
        gender_unemployment,
        x="Gender",
        y="Rate",
        color="Gender",
        text_auto=".1f",
        color_discrete_map=COLORS,
        title="Unemployment among each gender's labour force",
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Unemployment rate (%)",
    )

    st.plotly_chart(fig, use_container_width=True)
    key="unemployment_age_chart"
    st.subheader("3. Unemployment by age")

    draw_gender_line(
        age_unemployment,
        "Unemployment",
        "Unemployment rates across age groups",
        "Unemployment rate (%)",
    )

    st.subheader("4. Labour-force participation by age")

    age_options = age_lfp["Category"].tolist()

    selected_ages = st.multiselect(
        "Select age groups",
        options=age_options,
        default=age_options,
        key="age_filter",
    )

    filtered_age = age_lfp[
        age_lfp["Category"].isin(selected_ages)
    ]

    draw_gender_line(
        filtered_age,
        "Participation",
        "Labour-force participation across age groups",
        "Participation rate (%)",
    )

    st.subheader("5. Labour-force participation by education")

    education_options = education_lfp["Category"].tolist()

    selected_education = st.multiselect(
        "Select education levels",
        options=education_options,
        default=education_options,
        key="education_filter",
    )

    filtered_education = education_lfp[
        education_lfp["Category"].isin(selected_education)
    ]
st.plotly_chart(fig,use_container_width=True, key="education_filter")
key="education_participation_bar"

draw_gender_bar(
        filtered_education,
        "Participation",
        "Participation by completed education level",
        "Participation rate (%)",
    )

st.subheader("6. Education composition of employed people")
st.plotly_chart(figure,use_container_width=True)
key="education_composition"
draw_gender_bar(
        employed_education,
        "Share",
        "Educational composition within employed women and men",
        "Share of employed group (%)",
    )

st.caption(
        "This chart shows the educational composition of employed people. "
        "It is not a participation rate by education."
    )

st.subheader("7. Employment status among employed people")
st.plotly_chart(figure,use_container_width=True)
key="employment_status"
draw_gender_bar(
        employment_status,
        "Share",
        "Employment status within employed women and men",
        "Share within employed group (%)",
    )
st.subheader("8. Job-search methods")
draw_gender_bar(
        job_search,
        "Share",
        "Main job-search methods among unemployed people",
        "Share within unemployed group (%)",
    )
with st.expander("View the underlying survey tables"):
        st.markdown("**Participation by age**")
        st.dataframe(age_lfp, use_container_width=True, hide_index=True)

        st.markdown("**Participation by education**")
        st.dataframe(
            education_lfp,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("**Unemployment by age**")
        st.dataframe(
            age_unemployment,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("**Unemployment by education**")
        st.dataframe(
            education_unemployment,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download participation by education (CSV)",
            data=education_lfp.to_csv(index=False).encode("utf-8-sig"),
            file_name="participation_by_education_2022.csv",
            mime="text/csv",
        )


# ============================================================
# 13. KEY FINDINGS TAB
# ============================================================

with findings_tab:
    st.header("What does the evidence suggest?")

    st.write(
        "The comparisons highlight observed differences between "
        "women and men. They do not establish the causes of those "
        "differences."
    )

    st.subheader("A. Education and participation")

    draw_gender_bar(
        education_lfp,
        "Participation",
        "Participation by completed education level and gender",
        "Participation rate (%)",
    )

    university_rows = education_lfp[
        education_lfp["Category"].str.lower().str.contains(
            "university",
            na=False,
        )
    ]

    if not university_rows.empty:
        university_women = university_rows.iloc[0]["Women"]
        university_men = university_rows.iloc[0]["Men"]

        st.markdown(
            f"""
            <div class="insight">
                <b>University education:</b>
                participation is {university_women:.1f}% among women
                and {university_men:.1f}% among men.
                The difference is
                {university_men - university_women:.1f} percentage points.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("B. Participation gap by age")

    age_gap = age_lfp.copy()
    age_gap["Gap"] = age_gap["Men"] - age_gap["Women"]

    fig = px.bar(
        age_gap,
        x="Category",
        y="Gap",
        text_auto=".1f",
        title="Participation gap by age group (men minus women)",
        labels={"Gap": "Percentage-point gap", "Category": "Age group"},
        color="Gap",
        color_continuous_scale=["#F2C7BF", "#D96C5F"],
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, use_container_width=True)
    key="economic_status_by_ gender"
    st.subheader("C. Economic status by gender")

    status_long = status_by_gender.melt(
        id_vars="Gender",
        value_vars=[
            "Employed",
            "Unemployed",
            "Outside labour force",
        ],
        var_name="Status",
        value_name="Share",
    )

    fig = px.bar(
        status_long,
        x="Gender",
        y="Share",
        color="Status",
        barmode="group",
        color_discrete_map=STATUS_COLORS,
        title="Economic status within each gender",
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="",
        yaxis_title="Share of each gender (%)",
    )

    st.plotly_chart(fig, use_container_width=True)
    key=f"gender_bar"
    st.subheader("D. Employment status among employed people")

    draw_gender_bar(
        employment_status,
        "Share",
        "Employment status within employed women and men",
        "Share within employed group (%)",
    )

    st.subheader("E. Unemployment by education")

    draw_gender_bar(
        education_unemployment,
        "Unemployment",
        "Unemployment rates by completed education level",
        "Unemployment rate (%)",
    )

    st.warning(
        "The supplied survey tables do not provide the required "
        "cross-tabulations for marital status and household composition. "
        "These parts of the research question cannot be answered "
        "from the supplied tables."
    )


# ============================================================
# 14. FROM EVIDENCE TO ACTION TAB
# ============================================================

with action_tab:
    st.header("From evidence to action")

    st.write(
        "The following are policy proposals suggested by the "
        "descriptive patterns. Their effectiveness would need "
        "to be evaluated separately."
    )

    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            ### 1 · Education-to-employment bridge

            Strengthen career guidance, internships, apprenticeships
            and employer partnerships so educational qualifications
            connect more directly to paid work.
            """
        )

        st.markdown(
            """
            ### 2 · Work and care support

            Assess access to affordable childcare, safe transport
            and flexible work arrangements, and evaluate whether
            these reduce barriers to employment.
            """
        )

    with right:
        st.markdown(
            """
            ### 3 · Return-to-work pathways

            Develop skills-refresh programmes, mentoring and
            structured re-entry opportunities for women returning
            to paid employment.
            """
        )

        st.markdown(
            """
            ### 4 · Measure opportunity

            Track recruitment, pay, promotion and employment
            conditions by gender and education to identify
            where gaps persist.
            """
        )


# ============================================================
# 15. METHODOLOGY AND SOURCES TAB
# ============================================================

with methods_tab:
    st.header("Methodology and sources")

    st.markdown(
        """
        **National source**

        Lebanon Labour Force and Household Living Conditions
        Survey 2022. Tables EA1, EA3, EA6, EA8, EA37, EA39 and EA40.
        """
    )

    st.markdown(
        """
        **Historical source**

        Excel workbook supplied by the user: unemployment rate women.
        The dashboard reads Year, Female/Women and Male/Men columns,
        and reads Total/Overall when that column is available.
        """
    )

    st.markdown(
        """
        **Approach**

        Descriptive analysis of published survey tables and
        historical unemployment values. Participation rates,
        unemployment rates, employment composition and
        employment status are treated as distinct measures
        because they have different denominators.
        """
    )

    st.markdown(
        """
        **Limitations**

        The national survey tables relate to 2022. Cross-sectional
        comparisons do not establish causality.

        Marital status and household composition are not available
        in the supplied cross-tabulations.

        Historical values were transcribed from the supplied
        screenshot and should be checked against the original table.
        """
    )

    st.markdown(
        """
        **Definitions**

        Labour-force participation is the share of the relevant
        population that is employed or unemployed.

        Unemployment is measured among the labour force.

        People outside the labour force are neither employed
        nor unemployed under the survey classification.
        """
    )


# ============================================================
# 16. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "The Invisible Workforce · Lebanon · "
    "Exploratory and explanatory data storytelling"
)

