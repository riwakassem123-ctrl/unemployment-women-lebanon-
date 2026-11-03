from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
-----------------------------------------------------------------------------
THE INVISIBLE WORKFORCE | STREAMLIT DATA-STORYTELLING DASHBOARD
Lebanon Labour Force and Household Living Conditions Survey 2022
+ World Bank WDI unemployment series
-----------------------------------------------------------------------------
st.set_page_config(
page_title="The Invisible Workforce | Lebanon",
page_icon="◉",
layout="wide",
initial_sidebar_state="expanded",
)
BASE = Path(__file__).parent
DATA = BASE / "data"
LFS_FILE = DATA / "Labour-force-FULFS-2022.xlsx"
WB_TOTAL_FILE = DATA / "worldbank_total_unemployment.xlsx"
WB_MALE_FILE = DATA / "worldbank_male_unemployment.xlsx"
-----------------------------------------------------------------------------
DESIGN AND STYLING
-----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root {
--ink: #172A3A;
--muted: #657786;
--paper: #F7F8F6;
--teal: #087E8B;
--coral: #D96C5F;
--gold: #D7A84B;
}
html, body, [class="css"] {
font-family: 'DM Sans', sans-serif;
}
.stApp {
background: var(--paper);
}
.block-container {
max-width: 1240px;
padding-top: 2rem;
padding-bottom: 4rem;
}
h1, h2, h3 {
color: var(--ink);
}
.hero {
background: linear-gradient(120deg, #122B3A 0%, #1E5260 100%);
color: white;
padding: 2.4rem 2.6rem;
border-radius: 18px;
margin: 0 0 1.4rem 0;
}
.hero h1 {
font-family: 'Playfair Display', serif;
font-size: clamp(2.4rem, 5vw, 4.2rem);
line-height: 1.05;
color: white;
margin: 0.4rem 0 0.8rem 0;
}
.hero p {
color: #E6F0F0;
font-size: 1.08rem;
max-width: 850px;
}
.eyebrow {
letter-spacing: .16em;
text-transform: uppercase;
font-size: .72rem;
font-weight: 700;
color: #9DD4D3;
}
.section-kicker {
color: var(--teal);
text-transform: uppercase;
letter-spacing: .13em;
font-weight: 700;
font-size: .72rem;
}
.insight {
background: white;
border-left: 4px solid var(--teal);
padding: 1rem 1.2rem;
border-radius: 8px;
margin: .5rem 0 1rem 0;
color: var(--ink);
}
.note {
color: var(--muted);
font-size: .88rem;
}
.metric-card {
background: white;
border: 1px solid #E5EAE8;
border-radius: 13px;
padding: 1rem 1.1rem;
min-height: 115px;
}
.metric-label {
color: var(--muted);
font-size: .82rem;
font-weight: 600;
}
.metric-value {
color: var(--ink);
font-size: 2rem;
font-weight: 700;
line-height: 1.25;
}
.metric-sub {
color: var(--muted);
font-size: .78rem;
}
.story-card {
background: white;
border: 1px solid #E5EAE8;
border-radius: 14px;
padding: 1.2rem;
height: 100%;
}
.story-number {
color: var(--coral);
font-size: .78rem;
letter-spacing: .12em;
font-weight: 700;
}
div[data-testid="stTabs"] button {
font-weight: 600;
}
hr {
border-color: #E2E8E6;
}
footer {
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

COLORS = {
"Women": "#D96C5F",
"Men": "#087E8B",
"Women & Men": "#D7A84B",
"Total": "#172A3A",
}
PLOT = dict(
template="plotly_white",
font=dict(family="DM Sans", color="#172A3A"),
paper_bgcolor="rgba(0,0,0,0)",
plot_bgcolor="rgba(0,0,0,0)",
margin=dict(l=20, r=20, t=65, b=35),
legend_title_text="",
)

-----------------------------------------------------------------------------
DATA FUNCTIONS
-----------------------------------------------------------------------------
def read_table(
sheet,
start,
end,
label_col=0,
women_col=1,
men_col=2,
both_col=3
):
"""Read a section from the supplied labour-force survey workbook."""
raw = pd.read_excel(
LFS_FILE,
sheet_name=sheet,
header=None
)
out = raw.iloc[
start:end,
[label_col, women_col, men_col, both_col]
].copy()
out.columns = [
"Category",
"Women",
"Men",
"Women & Men"
]
out = out.dropna(subset=["Category"])
out["Category"] = (
out["Category"]
.astype(str)
.str.strip()
)
for column in ["Women", "Men", "Women & Men"]:
out[column] = pd.to_numeric(
out[column],
errors="coerce"
)
out = out.dropna(
subset=["Women", "Men"]
)
return out

@st.cache_data(show_spinner=False)
def load_lfs():
# EA.1: National headline indicators
raw1 = pd.read_excel(
LFS_FILE,
sheet_name="EA1",
header=None
)
metrics = {}
for row in range(6, 12):
name = str(raw1.iloc[row, 0]).strip()
metrics[name] = {
"Women": pd.to_numeric(
raw1.iloc[row, 1],
errors="coerce"
),
"Men": pd.to_numeric(
raw1.iloc[row, 2],
errors="coerce"
),
"Women & Men": pd.to_numeric(
raw1.iloc[row, 3],
errors="coerce"
),
"Youth (15–24)": pd.to_numeric(
raw1.iloc[row, 4],
errors="coerce"
),
"Adults (25+)": pd.to_numeric(
raw1.iloc[row, 5],
errors="coerce"
),
}
# EA.40: Labour force participation by age and education
age = read_table("EA40", 6, 17)
education = read_table("EA40", 18, 25)
# EA.39: Unemployment by age and education
unemp_age = read_table("EA39", 6, 17)
unemp_edu = read_table("EA39", 18, 25)
# EA.6A: Education composition among employed people
employed_edu = read_table("EA6", 6, 13)
# EA.8A: Employment status among employed people
status = read_table("EA8", 7, 12)
# EA.37A: Job-search methods
search = read_table("EA37", 7, 12)
# EA.3B: Population status within each sex
raw3 = pd.read_excel(
LFS_FILE,
sheet_name="EA3",
header=None
)
status_by_sex = raw3.iloc[
16:18,
[0, 1, 2, 3]
].copy()
status_by_sex.columns = [
"Gender",
"Employed",
"Unemployed",
"Outside labour force"
]
for column in [
"Employed",
"Unemployed",
"Outside labour force"
]:
status_by_sex[column] = pd.to_numeric(
status_by_sex[column],
errors="coerce"
)
# EA.2B: Population status by age
raw2 = pd.read_excel(
LFS_FILE,
sheet_name="EA2",
header=None
)
age_status = raw2.iloc[
27:39,
[0, 1, 2, 3]
].copy()
age_status.columns = [
"Age group",
"Employed",
"Unemployed",
"Outside labour force"
]
for column in [
"Employed",
"Unemployed",
"Outside labour force"
]:
age_status[column] = pd.to_numeric(
age_status[column],
errors="coerce"
)
return (
metrics,
age,
education,
unemp_age,
unemp_edu,
employed_edu,
status,
search,
status_by_sex,
age_status
)

@st.cache_data(show_spinner=False)
def load_wdi(file, indicator_label):
if not file.exists():
return pd.DataFrame()
raw = pd.read_excel(
file,
sheet_name="Data",
header=3
)
row = raw[
raw["Country Name"]
.astype(str)
.str.strip()
.eq("Lebanon")
]
if row.empty:
return pd.DataFrame()
row = row.iloc[0]
year_columns = [
column
for column in raw.columns
if str(column).isdigit()
]
values = pd.DataFrame({
"Year": [
int(column)
for column in year_columns
],
"Rate": [
pd.to_numeric(
row[column],
errors="coerce"
)
for column in year_columns
]
})
values = values.dropna(
subset=["Rate"]
)
values["Indicator"] = indicator_label
return values

-----------------------------------------------------------------------------
LOAD DATA
-----------------------------------------------------------------------------
try:
(
metrics,
age_lfp,
edu_lfp,
age_unemp,
edu_unemp,
employed_edu,
employment_status,
job_search,
status_by_sex,
age_status
) = load_lfs()
wdi_total = load_wdi(
WB_TOTAL_FILE,
"Total unemployment"
)
wdi_male = load_wdi(
WB_MALE_FILE,
"Male unemployment"
)
except Exception as exc:
st.error(
"The dashboard could not read one of the supplied datasets."
)
st.exception(exc)
st.stop()

-----------------------------------------------------------------------------
SIDEBAR FILTERS
-----------------------------------------------------------------------------
st.sidebar.markdown("## Explore the evidence")
st.sidebar.caption(
"Use these controls to focus the charts below."
)
selected_age = st.sidebar.multiselect(
"Age groups",
options=age_lfp["Category"].tolist(),
default=age_lfp["Category"].tolist(),
key="age_filter"
)
selected_education = st.sidebar.multiselect(
"Education levels",
options=edu_lfp["Category"].tolist(),
default=edu_lfp["Category"].tolist(),
key="edu_filter"
)
st.sidebar.markdown("---")
st.sidebar.markdown("About this dashboard")
st.sidebar.caption(
"Lebanon · Labour Force Survey 2022 and "
"World Bank WDI unemployment estimates. "
"See Methodology for definitions and limitations."
)

-----------------------------------------------------------------------------
HERO SECTION
-----------------------------------------------------------------------------
st.markdown("""
<div class="hero">
<div class="eyebrow">
A data story about work, opportunity & human capital · Lebanon
</div>
<h1>The Invisible Workforce</h1>
<p>
<b>
Why doesn't education always translate into paid employment
for women in Lebanon?
</b>
<br>
Explore how gender, education and age intersect with
labour-market participation — and what the evidence
suggests we should investigate next.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This interactive research blog examines a central tension:
women may attain education and skills, yet their participation
in paid work remains substantially lower than men's.
The dashboard brings together national labour-force survey
indicators and longer-run unemployment estimates to make
the patterns easier to explore.
""")

-----------------------------------------------------------------------------
HEADLINE METRICS
-----------------------------------------------------------------------------
lfp = metrics.get(
"Labour Force Participation Rate",
{}
)
unemp = metrics.get(
"LU1: Unemployment rate",
{}
)
emp_pop = metrics.get(
"Employment-to-Population Ratio",
{}
)
lfp_gap = (
lfp.get("Men", float("nan"))
o	lfp.get("Women", float("nan"))
def metric_card(label, value, sub):
st.markdown(
f"""
<div class="metric-card">
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
<div class="metric-sub">{sub}</div>
</div>
""",
unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)
with m1:
metric_card(
"Women's labour force participation",
f"{lfp.get('Women', float('nan')):.1f}%",
"Lebanon · 2022"
)
with m2:
metric_card(
"Men's labour force participation",
f"{lfp.get('Men', float('nan')):.1f}%",
"Lebanon · 2022"
)
with m3:
metric_card(
"Participation gap",
f"{lfp_gap:.1f} pp",
"Men minus women · 2022"
)
with m4:
metric_card(
"Women's unemployment rate",
f"{unemp.get('Women', float('nan')):.1f}%",
"Among women's labour force · 2022"
)

st.markdown("""
<div class="insight">
<b>The headline:</b>
In the 2022 survey, labour force participation was 22.2%
for women and 66.2% for men — a gap of about 44 percentage
points. Unemployment is only part of the picture: 77.8%
of women aged 15+ were outside the labour force, compared
with 33.8% of men.
</div>
""", unsafe_allow_html=True)

-----------------------------------------------------------------------------
MAIN NAVIGATION
-----------------------------------------------------------------------------
intro_tab, explore_tab, explain_tab, action_tab, method_tab = st.tabs([
"The story",
"Explore the data",
"What the evidence suggests",
"From evidence to action",
"Methodology & sources"
])

=============================================================================
TAB 1: THE STORY
=============================================================================
with intro_tab:
st.markdown("### The question behind the numbers")
st.markdown("""
Educational attainment is often treated as a pathway to
economic opportunity. But education alone does not guarantee
access to paid work.
This project asks how gender, education, age, marital status
and household composition are associated with paid labour
participation in Lebanon — and whether these relationships
differ between women and men.
""")
a, b, c = st.columns(3)
with a:
st.markdown("""
<div class="story-card">
<div class="story-number">01 / PARTICIPATION</div>
<h3>Who is in the labour force?</h3>
<p>
Compare participation, employment-to-population
and inactivity indicators by gender.
</p>
</div>
""", unsafe_allow_html=True)
with b:
st.markdown("""
<div class="story-card">
<div class="story-number">02 / HUMAN CAPITAL</div>
<h3>Does education connect to work?</h3>
<p>
Explore how participation and unemployment
vary across completed education levels.
</p>
</div>
""", unsafe_allow_html=True)
with c:
st.markdown("""
<div class="story-card">
<div class="story-number">03 / LIFE STAGES</div>
<h3>When do gaps appear?</h3>
<p>
Compare participation and unemployment
patterns across age groups.
</p>
</div>
""", unsafe_allow_html=True)
st.markdown("### How to use this blog")
st.markdown("""
Start with Explore the data to inspect the patterns.
Then move to What the evidence suggests for focused
comparisons and interpretations.
The final section translates the observed patterns into
policy ideas that could be tested and evaluated.
""")
st.info(
"The 2022 labour-force survey is a cross-sectional snapshot. "
"It identifies differences and associations, but by itself "
"cannot prove why those differences occur."
)

=============================================================================
TAB 2: EXPLORATORY ANALYSIS
=============================================================================
with explore_tab:
st.markdown(
'<div class="section-kicker">02 · Exploratory analysis</div>',
unsafe_allow_html=True
)
st.header("Explore the labour-market landscape")
st.write("""
Use the filters in the sidebar to focus the age and education
charts. Hover over points and bars for exact values.
""")
# -------------------------------------------------------------------------
# 1. UNEMPLOYMENT OVER TIME
# -------------------------------------------------------------------------
st.subheader("1. Unemployment over time: Lebanon")
if not wdi_total.empty or not wdi_male.empty:
trend = pd.concat(
[wdi_total, wdi_male],
ignore_index=True
)
fig = px.line(
trend,
x="Year",
y="Rate",
color="Indicator",
markers=True,
color_discrete_map={
"Total unemployment": "#D7A84B",
"Male unemployment": "#087E8B"
},
labels={
"Rate": "Unemployment rate (%)",
"Year": "Year"
},
title="World Bank modelled ILO estimates"
)
fig.update_layout(
PLOT,
hovermode="x unified"
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
The uploaded World Bank files contain total and male
unemployment series. A female historical series was
not included, so this chart does not invent or estimate one.
""")
else:
st.warning(
"World Bank trend files were not found. "
"The 2022 national survey comparisons remain available below."
)
# -------------------------------------------------------------------------
# 2. UNEMPLOYMENT BY GENDER
# -------------------------------------------------------------------------
st.subheader("2. Unemployment by gender: 2022")
gender_unemp = pd.DataFrame({
"Gender": ["Women", "Men"],
"Rate": [
unemp.get("Women"),
unemp.get("Men")
]
})
fig = px.bar(
gender_unemp,
x="Gender",
y="Rate",
color="Gender",
text_auto=".1f",
color_discrete_map=COLORS,
title="Unemployment rate among each gender's labour force"
)
fig.update_layout(
PLOT,
showlegend=False,
yaxis_title="Unemployment rate (%)",
xaxis_title=""
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption(
"This is the 2022 Lebanon Labour Force Survey estimate, "
"not the World Bank modelled series above."
)
# -------------------------------------------------------------------------
# 3. FEMALE OVERALL VS FEMALE YOUTH UNEMPLOYMENT
# -------------------------------------------------------------------------
st.subheader(
"3. Female overall and female youth unemployment"
)
youth = age_unemp[
age_unemp["Category"].isin([
"15-19",
"20-24",
"15 - 19",
"20 - 24"
])
].copy()
female_youth = pd.concat([
pd.DataFrame({
"Group": ["Women · all ages 15+"],
"Rate": [unemp.get("Women")]
}),
pd.DataFrame({
"Group": [
f"Women · {x}"
for x in youth["Category"]
],
"Rate": youth["Women"].tolist()
})
], ignore_index=True)
fig = px.bar(
female_youth,
x="Group",
y="Rate",
color="Group",
text_auto=".1f",
color_discrete_sequence=[
"#D96C5F",
"#E9A093",
"#B94E48"
],
title="Female unemployment: overall and selected youth age bands"
)
fig.update_layout(
PLOT,
showlegend=False,
yaxis_title="Unemployment rate (%)",
xaxis_title="",
xaxis_tickangle=-12
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
The survey reports separate 15–19 and 20–24 age bands.
These are shown separately; they are not combined into
a weighted 15–24 estimate.
""")
# -------------------------------------------------------------------------
# 4. PARTICIPATION BY AGE AND GENDER
# -------------------------------------------------------------------------
st.subheader(
"4. Labour force participation by age and gender"
)
age_filtered = age_lfp[
age_lfp["Category"].isin(selected_age)
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
markers=True,
color_discrete_map=COLORS,
title="Participation changes across the life course"
)
fig.update_layout(
PLOT,
yaxis_title="Labour force participation (%)",
xaxis_title="Age group"
)
st.plotly_chart(
fig,
use_container_width=True
)
# -------------------------------------------------------------------------
# 5. PARTICIPATION BY EDUCATION AND GENDER
# -------------------------------------------------------------------------
st.subheader(
"5. Labour force participation by education and gender"
)
edu_filtered = edu_lfp[
edu_lfp["Category"].isin(selected_education)
]
edu_long = edu_filtered.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Participation"
)
fig = px.bar(
edu_long,
x="Category",
y="Participation",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Participation rates by completed education level"
)
fig.update_layout(
PLOT,
yaxis_title="Labour force participation (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
# -------------------------------------------------------------------------
# 6. EDUCATIONAL COMPOSITION OF EMPLOYED PEOPLE
# -------------------------------------------------------------------------
st.subheader(
"6. Who makes up the employed population by education?"
)
emp_long = employed_edu.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Share"
)
fig = px.bar(
emp_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Educational composition within employed women and men"
)
fig.update_layout(
PLOT,
yaxis_title="Share of employed group (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
This chart describes the education composition of employed
people. It is not a participation rate by education; use
the previous chart for that question.
""")
# -------------------------------------------------------------------------
# 7. EMPLOYMENT STATUS
# -------------------------------------------------------------------------
st.subheader(
"7. Employment status among employed women and men"
)
status_long = employment_status.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Share"
)
fig = px.bar(
status_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Employees, employers, own-account and contributing family workers"
)
fig.update_layout(
PLOT,
yaxis_title="Share within employed group (%)",
xaxis_title="",
xaxis_tickangle=-10
)
st.plotly_chart(
fig,
use_container_width=True
)
# -------------------------------------------------------------------------
# 8. JOB SEARCH METHODS
# -------------------------------------------------------------------------
st.subheader(
"8. How do unemployed women and men search for work?"
)
search_long = job_search.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Share"
)
fig = px.bar(
search_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Main job-search method used during the previous four weeks"
)
fig.update_layout(
PLOT,
yaxis_title="Share within unemployed group (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
This table describes the methods reported by unemployed
people; it does not measure the effectiveness of each method.
""")
# -------------------------------------------------------------------------
# SOURCE DATA TABLES AND DOWNLOADS
# -------------------------------------------------------------------------
with st.expander(
"View and download the source data used in these charts"
):
st.markdown(
"Labour force participation by education"
)
st.dataframe(
edu_lfp,
use_container_width=True,
hide_index=True
)
st.download_button(
"Download education participation data (CSV)",
edu_lfp.to_csv(index=False).encode("utf-8-sig"),
"education_participation_2022.csv",
"text/csv"
)
st.markdown(
"Labour force participation by age"
)
st.dataframe(
age_lfp,
use_container_width=True,
hide_index=True
)
st.download_button(
"Download age participation data (CSV)",
age_lfp.to_csv(index=False).encode("utf-8-sig"),
"age_participation_2022.csv",
"text/csv"
)
st.markdown(
"Unemployment by education"
)
st.dataframe(
edu_unemp,
use_container_width=True,
hide_index=True
)
st.download_button(
"Download education unemployment data (CSV)",
edu_unemp.to_csv(index=False).encode("utf-8-sig"),
"education_unemployment_2022.csv",
"text/csv"
)

=============================================================================
TAB 3: EXPLANATORY ANALYSIS
=============================================================================
with explain_tab:
st.markdown(
'<div class="section-kicker">03 · Explanatory analysis</div>',
unsafe_allow_html=True
)
st.header("What does the evidence suggest?")
st.write("""
These views are designed to make the most important
comparisons easier to see. They describe observed gaps;
they do not establish their causes.
""")
# -------------------------------------------------------------------------
# A. EDUCATION AND PARTICIPATION GAP
# -------------------------------------------------------------------------
st.subheader("A. The education–participation gap")
edu_gap = edu_lfp.copy()
edu_gap["Gap (men − women), pp"] = (
edu_gap["Men"] - edu_gap["Women"]
)
edu_gap_long = edu_gap.melt(
id_vars=[
"Category",
"Gap (men − women), pp"
],
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Participation"
)
fig = px.bar(
edu_gap_long,
x="Category",
y="Participation",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Participation rises with higher education for women, but the gender gap remains"
)
fig.update_layout(
PLOT,
yaxis_title="Labour force participation (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
st.markdown("""
<div class="insight">
<b>Key finding:</b>
Among people with university education and above,
participation was 58.9% for women and 78.4% for men —
a gap of about 19.4 percentage points.
Higher education is associated with higher participation
for women in this 2022 snapshot, but the gender difference
does not disappear.
</div>
""", unsafe_allow_html=True)
# -------------------------------------------------------------------------
# B. AGE-RELATED PARTICIPATION GAP
# -------------------------------------------------------------------------
st.subheader(
"B. Where is the age-related participation gap widest?"
)
age_gap = age_lfp.copy()
age_gap["Gap (men − women), pp"] = (
age_gap["Men"] - age_gap["Women"]
)
fig = px.bar(
age_gap,
x="Category",
y="Gap (men − women), pp",
color="Gap (men − women), pp",
color_continuous_scale=[
"#F2C7BF",
"#D96C5F"
],
title="Difference between men's and women's participation by age"
)
fig.update_layout(
PLOT,
coloraxis_showscale=False,
yaxis_title="Percentage-point gap",
xaxis_title="Age group"
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
A larger positive value means the male participation rate
exceeds the female rate by more percentage points.
""")
# -------------------------------------------------------------------------
# C. EMPLOYMENT AND UNEMPLOYMENT STATUS
# -------------------------------------------------------------------------
st.subheader(
"C. Employment is not the same as unemployment"
)
status_long2 = status_by_sex.melt(
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
status_long2,
x="Gender",
y="Share",
color="Status",
barmode="stack",
color_discrete_map={
"Employed": "#087E8B",
"Unemployed": "#D7A84B",
"Outside labour force": "#D96C5F"
},
title="Distribution of residents aged 15+ by primary economic status"
)
fig.update_layout(
PLOT,
yaxis_title="Share of each gender (%)",
xaxis_title=""
)
st.plotly_chart(
fig,
use_container_width=True
)
st.markdown("""
<div class="insight">
<b>Why this matters:</b>
The largest gender difference is not only in unemployment.
The survey shows a much larger share of women outside
the labour force.
Unemployment rates count only people in the labour force
who are without work, available and seeking work.
</div>
""", unsafe_allow_html=True)
# -------------------------------------------------------------------------
# D. EMPLOYMENT STATUS AMONG EMPLOYED PEOPLE
# -------------------------------------------------------------------------
st.subheader(
"D. What happens after women enter employment?"
)
fig = px.bar(
status_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Employment status among employed women and men"
)
fig.update_layout(
PLOT,
yaxis_title="Share within employed group (%)",
xaxis_title="",
xaxis_tickangle=-10
)
st.plotly_chart(
fig,
use_container_width=True
)
st.markdown("""
<div class="insight">
<b>Additional context:</b>
Among employed women, 86.1% were employees, compared
with 70.4% of employed men.
The survey also reports a larger share of women among
contributing family workers than men when looking at
the gender composition of that category. These are
different denominators and should not be confused.
</div>
""", unsafe_allow_html=True)
# -------------------------------------------------------------------------
# E. UNEMPLOYMENT BY EDUCATION
# -------------------------------------------------------------------------
st.subheader("E. Unemployment by education")
ue = edu_unemp.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Unemployment"
)
fig = px.bar(
ue,
x="Category",
y="Unemployment",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Unemployment rates by completed education level"
)
fig.update_layout(
PLOT,
yaxis_title="Unemployment rate (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption("""
Unemployment rates use the labour force as the denominator.
They should not be interpreted as the share of all people
with that education who are unemployed unless the table
definition specifies that denominator.
""")
st.warning("""
Marital status and household composition are part of the
proposed research question, but the uploaded workbook does
not contain the corresponding cross-tabulations.
Those relationships cannot be visualized from the supplied
files. Add the relevant microdata or official tables before
drawing conclusions about them.
""")

=============================================================================
TAB 4: SOLUTIONS AND IMPACT
=============================================================================
with action_tab:
st.markdown(
'<div class="section-kicker">04 · From evidence to action</div>',
unsafe_allow_html=True
)
st.header("Turning evidence into opportunity")
st.write("""
The following are proposed policy directions informed by
the observed participation and education patterns.
They are recommendations to test, not effects proven
by this dashboard.
""")
p1, p2 = st.columns(2)
with p1:
st.markdown("""
<div class="story-card">
<div class="story-number">PILLAR 01</div>
<h3>Education-to-Employment Bridge</h3>
<p>
Connect female graduates and young jobseekers
with paid internships, apprenticeships,
employer partnerships, career guidance
and transparent job-matching.
</p>
<b>What to track</b>
<p>
Internship placements, job offers,
time to first job, and employment
retention after 6 and 12 months.
</p>
</div>
""", unsafe_allow_html=True)
with p2:
st.markdown("""
<div class="story-card">
<div class="story-number">PILLAR 02</div>
<h3>Work and Care Initiative</h3>
<p>
Expand affordable childcare and dependent-care
support, flexible work arrangements,
family-friendly policies and safe transport access.
</p>
<b>What to track</b>
<p>
Return-to-work rates, retention among caregivers,
uptake of flexible work, and access to childcare support.
</p>
</div>
""", unsafe_allow_html=True)
p3, p4 = st.columns(2)
with p3:
st.markdown("""
<div class="story-card">
<div class="story-number">PILLAR 03</div>
<h3>Return-to-Work Programme</h3>
<p>
Offer paid returnships, refresher training,
mentoring and recruitment partnerships
for women returning after career interruptions.
</p>
<b>What to track</b>
<p>
Programme completion, placement rates,
job quality and 6-/12-month retention.
</p>
</div>
""", unsafe_allow_html=True)
with p4:
st.markdown("""
<div class="story-card">
<div class="story-number">PILLAR 04</div>
<h3>Fair Opportunity at Work</h3>
<p>
Encourage transparent recruitment and promotion,
equal-pay reviews, anti-discrimination safeguards
and access to leadership pathways.
</p>
<b>What to track</b>
<p>
Recruitment and promotion by gender,
pay differences for comparable roles,
and leadership representation.
</p>
</div>
""", unsafe_allow_html=True)
st.markdown(
"### Who could help implement the programme?"
)
st.markdown("""
Government institutions can support childcare,
labour protections and transport policy.
Universities can connect graduates to employers.
Private-sector employers can offer paid placements,
flexible arrangements and transparent recruitment.
Civil-society organizations can support outreach,
training and evaluation.
""")
st.markdown(
"### Make the project matter beyond the screen"
)
st.markdown("""
Share the public dashboard with students, faculty,
researchers, employers and relevant organizations.
Ask viewers which barriers they see in practice,
collect their feedback through a short external survey,
and document the number of views, responses and
substantive comments in the technical report.
""")
st.info("""
Impact evidence to collect:
o	Dashboard link and sharing date.
o	Screenshots of posts.
o	Number of views or reactions.
o	Survey responses.
o	Comments from relevant stakeholders.
o	Any concrete follow-up discussion or action.
o	""")
=============================================================================
TAB 5: METHODOLOGY AND SOURCES
=============================================================================
with method_tab:
st.markdown(
'<div class="section-kicker">05 · Methodology & sources</div>',
unsafe_allow_html=True
)
st.header(
"What the data can — and cannot — tell us"
)
st.markdown("### Data used")
st.markdown("""
o	Lebanon Labour Force and Household Living Conditions
o	Survey 2022, supplied workbook
o	
The dashboard uses tables EA.1, EA.2, EA.3, EA.6,
EA.8, EA.37, EA.39 and EA.40.
o	World Bank World Development Indicators, supplied
o	files for total unemployment (`SL.UEM.TOTL.ZS`) and
o	male unemployment (`SL.UEM.TOTL.MA.ZS`).
The series are modelled ILO estimates. The files do not
include a female unemployment series.
""")
st.markdown("### Definitions")
st.markdown("""
o	Labour force participation rate: labour force as a
o	percentage of the relevant population.
o	Employment-to-population ratio: employed people
o	as a percentage of the relevant population.
o	Unemployment rate: unemployed people as a percentage
o	of the labour force. The unemployed are without work,
o	available and seeking work.
o	Outside the labour force: people who are neither
o	employed nor classified as unemployed under the
o	survey definition.
o	""")
st.markdown("### Important limitations")
st.markdown("""
1.	The national labour-force survey workbook provides
2.	2022 cross-sectional tables, not a time series for
3.	every demographic variable.
2.	The uploaded World Bank files include total and male
3.	unemployment, but not female unemployment. The
4.	dashboard therefore does not plot a historical
5.	female unemployment line.
3.	The uploaded workbook does not provide marital-status
4.	or household-composition cross-tabulations. These
5.	dimensions remain part of the research question but
6.	require additional microdata or official tables.
4.	Some tables show the distribution within a gender
5.	or employment category, while others show rates.
6.	Always read the chart caption and denominator
7.	before comparing values.
5.	These descriptive statistics show associations
6.	and differences; they do not establish causality
7.	or directly measure the gender wage gap. Wage data
8.	would be needed to estimate that gap.
9.	""")
st.markdown("### Source notes")
st.markdown("""
The World Bank metadata identifies the unemployment
indicators as ILO modelled estimates from the ILOSTAT
database.
The national survey tables are labelled Lebanon, 2022.
Retain the original workbook and its technical
documentation in your project archive and cite the
full publication details in the final report.
""")

-----------------------------------------------------------------------------
FOOTER
-----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="
text-align:center;
color:#657786;
font-size:.82rem;
">
THE INVISIBLE WORKFORCE · A student data-storytelling project · Lebanon
</div>
""", unsafe_allow_html=True)


