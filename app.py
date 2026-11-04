from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
# ==================================================
# HERO SECTION
# ==================================================
st.set_page_config(
    page_title="The Invisible Workforce | Lebanon",
    page_icon="📊",
    layout="wide"
)
BASE_DIR = Path(__file__).parent

st.markdown("""
<div class="hero">
    <div style="
        letter-spacing:.14em;
        text-transform:uppercase;
        font-size:.75rem;
        color:#9DD4D3;
        font-weight:700;">
        Lebanon · Labour Market · 2022
    </div>

    <h1>The Invisible Workforce</h1>

    <p>
    <b>Understanding Gender, Education and Employment in Lebanon</b><br>
    This interactive research dashboard explores how labour-force participation,
    unemployment, education and employment characteristics differ between
    women and men in Lebanon.
    </p>
</div>
""", unsafe_allow_html=True)
headline = load_survey()[0]

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
st.markdown("""
This dashboard combines Lebanon's 2022 Labour Force and Household Living
Conditions Survey with historical unemployment estimates from 1991–2023.

It is designed as an interactive research blog rather than a simple
collection of charts. The goal is to investigate patterns in labour-force
participation, unemployment, education and employment outcomes and to
identify where women and men experience different labour-market realities.
""")

# ==================================================
# KPI CARDS
# ==================================================

st.subheader("Key Labour Market Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Women's Labour Force Participation",
    f"{lfp.get('Women',0):.1f}%"
)

k2.metric(
    "Men's Labour Force Participation",
    f"{lfp.get('Men',0):.1f}%"
)

k3.metric(
    "Participation Gap",
    f"{participation_gap:.1f} pp"
)

k4.metric(
    "Women's Unemployment",
    f"{unemployment.get('Women',0):.1f}%"
)

st.markdown(
f"""
<div class="insight">

<b>Key Observation</b>

Women's labour-force participation rate was
{lfp.get('Women',0):.1f}% compared with
{lfp.get('Men',0):.1f}% among men.

The participation gap reached approximately
{participation_gap:.1f} percentage points.

Women's unemployment rate reached
{unemployment.get('Women',0):.1f}%.

These figures highlight that labour-market
inequality is not only about unemployment but also
about participation itself.

</div>
""",
unsafe_allow_html=True
)

# ==================================================
# TABS
# ==================================================

story_tab, explore_tab, findings_tab, action_tab, methods_tab = st.tabs([
    "The Story",
    "Explore Data",
    "Key Findings",
    "From Evidence To Action",
    "Methodology"
])

# ==================================================
# TAB 1
# ==================================================

with story_tab:

    st.header("The Research Question")

    st.write("""
    How are gender, age and educational attainment
    associated with labour-market participation
    in Lebanon?
    """)

    st.write("""
    Women and men participate differently in Lebanon's
    labour market.

    Understanding these differences requires looking
    beyond unemployment alone and examining labour-force
    participation, age patterns, educational attainment,
    employment arrangements and job-search strategies.
    """)

    a, b, c = st.columns(3)

    with a:
        st.markdown("""
        ### Participation

        Who participates in the labour market?

        How large is the gender gap?

        Which age groups participate most?
        """)

    with b:
        st.markdown("""
        ### Education

        Does higher education increase labour-force
        participation?

        Does unemployment vary by education?
        """)

    with c:
        st.markdown("""
        ### Employment

        Are women and men concentrated in different
        forms of employment?

        How do unemployed people search for jobs?
        """)

    st.info("""
    This dashboard identifies patterns and associations.

    It does not perform causal or regression analysis and
    therefore cannot establish that age, education or
    gender directly causes particular labour-market outcomes.
    """)

# ==================================================
# TAB 2 INTRODUCTION
# ==================================================

with explore_tab:

    st.header("Explore The Labour Market")

    st.markdown("""
    ### Dashboard Features

    ✅ Historical unemployment trends (1991–2023)

    ✅ Labour-force participation by age

    ✅ Labour-force participation by education

    ✅ Unemployment by age

    ✅ Unemployment by education

    ✅ Education profile of employed workers

    ✅ Employment status comparisons

    ✅ Job-search behaviour

    ✅ Interactive filters

    ✅ Downloadable datasets
    """)

# ==================================================
# TAB 3 INTRODUCTION
# ==================================================

with findings_tab:

    st.header("Key Findings")

    st.markdown("""
    ### Main Findings To Investigate

    1. Women participate in the labour market at much lower rates.

    2. Unemployment alone does not explain the gender gap.

    3. Education is associated with higher participation.

    4. Female and male unemployment trends differ over time.

    5. Employment arrangements vary across genders.

    6. Job-search behaviour also differs.
    """)

# ==================================================
# TAB 4
# ==================================================

with action_tab:

    st.header("From Evidence To Action")

    st.markdown("""
    ### Education-To-Employment Bridge

    Strengthen internships, apprenticeships and
    employer partnerships.
    """)

    st.markdown("""
    ### Work And Care Support

    Expand childcare access, flexible work arrangements
    and transportation support.
    """)

    st.markdown("""
    ### Return-To-Work Programmes

    Support women returning to paid employment through
    skills-refresh and re-entry initiatives.
    """)

    st.markdown("""
    ### Measure Progress

    Monitor participation, hiring and employment outcomes
    using gender-disaggregated indicators.
    """)

# ==================================================
# TAB 5
# ==================================================

with methods_tab:

    st.header("Methodology And Sources")

    st.markdown("""
    ### Source 1

    Lebanon Labour Force and Household Living Conditions
    Survey 2022.
    """)

    st.markdown("""
    ### Source 2

    Historical unemployment dataset 1991–2023.
    """)

    st.markdown("""
    ### Important Definitions

    Participation Rate:
    Share of people who are employed or unemployed and
    actively participating in the labour market.

    Unemployment Rate:
    Share of unemployed people within the labour force.

    Employment Status:
    Form of employment among employed workers.
    """)
headline = load_survey()[0]

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
st.markdown("---")

st.caption(
    "The Invisible Workforce | Lebanon | Interactive Labour Market Dashboard"
)
