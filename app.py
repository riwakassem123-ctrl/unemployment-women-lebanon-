from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
#1. PAGE CONFIGURATION
st.set_page_config(
page_title="The Invisible Workforce | Lebanon",
page_icon="📊",
layout="wide"
)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LFS_FILE = DATA_DIR / "Labour-force-FULFS-2022.xlsx"
#2. COLORS AND CHART SETTING
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
"font": {
"family": "Arial",
"color": "#172A3A"
},
"paper_bgcolor": "rgba(0,0,0,0)",
"plot_bgcolor": "rgba(0,0,0,0)",
"margin": {
"l": 25,
"r": 25,
"t": 65,
"b": 45
},
"legend_title_text": ""
}

#3. PAGE STYLING

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
.small-note {
color: #657786;
font-size: .88rem;
}
</style>
""",
unsafe_allow_html=True
)
#4. HISTORICAL UNEMPLOYMENT DATA
  Values transcribed from "unemployment rate women.xlsx"
@st.cache_data
def load_historical_data():
years = list(range(1991, 2024))
total = [
8.554, 8.225, 8.225, 8.321, 8.421, 8.413,
8.662, 8.571, 8.677, 8.641, 8.459, 8.248,
8.061, 7.850, 8.249, 8.679, 8.980, 7.666,
6.355, 6.768, 7.352, 7.952, 8.477, 8.841,
9.312, 9.794, 10.258, 10.755, 11.301,
13.252, 12.715, 11.105, 10.985
]
female = [
10.553, 8.812, 10.171, 10.256, 10.346,
10.328, 10.524, 10.437, 10.602, 10.462,
10.125, 9.373, 9.755, 9.572, 9.742,
9.999, 10.242, 10.399, 10.345, 10.671,
11.210, 11.753, 12.195, 12.445, 12.812,
13.176, 13.520, 13.898, 14.323, 16.249,
 15.874, 14.593, 14.480
]
male = [
8.080, 7.694, 7.688, 7.778, 7.784,
7.857, 8.066, 8.024, 8.254, 8.116,
7.979, 7.732, 7.755, 7.342, 7.784,
8.258, 8.602, 6.790, 4.999, 5.409,
5.978, 6.568, 7.094, 7.468, 7.941,
8.418, 8.880, 9.376, 9.392, 12.045,
11.515, 9.816, 9.705
]
if not (
len(years) == len(total)
== len(female) == len(male)
):
raise ValueError(
"Historical data arrays have different lengths."
)
historical = pd.DataFrame({
"Year": years,
"Total unemployment": total,
"Female unemployment": female,
"Male unemployment": male
})
return historical

============================================================
5. GENERAL SURVEY HELPER FUNCTION
============================================================
def read_section(sheet_name, start_row, end_row):
raw = pd.read_excel(
LFS_FILE,
sheet_name=sheet_name,
header=None
)
table = raw.iloc[start_row:end_row, 0:4].copy()
table.columns = [
"Category",
"Women",
"Men",
"Women & Men"
]
table["Category"] = (
table["Category"]
.astype(str)
.str.strip()
)
for column in [
"Women",
"Men",
"Women & Men"
]:
table[column] = pd.to_numeric(
table[column],
errors="coerce"
)
table = table.dropna(
subset=["Women", "Men"]
)
table = table[
~table["Category"].str.lower().isin(
["", "nan", "total"]
)
]
return table.reset_index(drop=True)

============================================================
6. LOAD THE 2022 LABOUR FORCE SURVEY
============================================================
@st.cache_data
def load_survey():
if not LFS_FILE.exists():
raise FileNotFoundError(
f"Survey workbook not found: {LFS_FILE}"
)
# --------------------------------------------------------
# EA1: Headline indicators
# --------------------------------------------------------
headline_raw = pd.read_excel(
LFS_FILE,
sheet_name="EA1",
header=None
)
headline = {}
for row_index in range(6, 12):
label = str(
headline_raw.iloc[row_index, 0]
).strip()
if label == "" or label.lower() == "nan":
continue
headline[label] = {
"Women": pd.to_numeric(
headline_raw.iloc[row_index, 1],
errors="coerce"
),
"Men": pd.to_numeric(
headline_raw.iloc[row_index, 2],
errors="coerce"
),
"Women & Men": pd.to_numeric(
headline_raw.iloc[row_index, 3],
errors="coerce"
)
}
# --------------------------------------------------------
# EA40: Labour-force participation
# --------------------------------------------------------
age_lfp = read_section(
"EA40", 6, 17
)
education_lfp = read_section(
"EA40", 18, 25
)
# --------------------------------------------------------
# EA39: Unemployment
# --------------------------------------------------------
age_unemployment = read_section(
"EA39", 6, 17
)
education_unemployment = read_section(
"EA39", 18, 25
)
# --------------------------------------------------------
# EA6: Education composition of employed people
# --------------------------------------------------------
employed_education = read_section(
"EA6", 6, 13
)
# --------------------------------------------------------
# EA8: Employment status
# --------------------------------------------------------
employment_status = read_section(
"EA8", 7, 12
)
# --------------------------------------------------------
# EA37: Job-search methods
# --------------------------------------------------------
job_search = read_section(
"EA37", 7, 12
)
# --------------------------------------------------------
# EA3: Economic status by gender
# --------------------------------------------------------
status_raw = pd.read_excel(
LFS_FILE,
sheet_name="EA3",
header=None
)
status = status_raw.iloc[16:18, 0:4].copy()
status.columns = [
"Gender",
"Employed",
"Unemployed",
"Outside labour force"
]
status["Gender"] = (
status["Gender"]
.astype(str)
.str.strip()
)
for column in [
"Employed",
"Unemployed",
"Outside labour force"
]:
status[column] = pd.to_numeric(
status[column],
errors="coerce"
)
status = status.dropna(
subset=["Employed", "Unemployed"]
)
return (
headline,
age_lfp,
education_lfp,
age_unemployment,
education_unemployment,
employed_education,
employment_status,
job_search,
status
)
#7. FIND HEADLINE INDICATORS
def find_indicator(headline, keyword):
for label, values in headline.items():
if keyword.lower() in label.lower():
return values
return {
"Women": float("nan"),
"Men": float("nan"),
"Women & Men": float("nan")
}
#8. LOAD DATA
try:
historical = load_historical_data()
(
headline,
age_lfp,
education_lfp,
age_unemployment,
education_unemployment,
employed_education,
employment_status,
job_search,
status_by_gender
) = load_survey()
except Exception as error:
st.error(
"The dashboard could not load the data. "
"Please check the Excel filename and sheet structure."
)
st.exception(error)
st.stop()

============================================================
9. PREPARE HEADLINE VALUES
============================================================
lfp = find_indicator(
headline,
"participation"
)
unemployment = find_indicator(
headline,
"unemployment rate"
)
participation_gap = (
lfp["Men"] - lfp["Women"]
)

============================================================
10. DASHBOARD HEADER
============================================================
st.markdown(
"""
<div class="hero">
<div style="
letter-spacing:.14em;
text-transform:uppercase;
font-size:.75rem;
color:#9DD4D3;
font-weight:700;
">
Lebanon · Labour market · 2022
</div>
<h1>The Invisible Workforce</h1>
<p>
<b>
Understanding gender, education and paid employment in Lebanon.
</b>
<br>
Explore how labour-force participation and unemployment
differ between women and men, and how these patterns
vary by age and education.
</p>
</div>
""",
unsafe_allow_html=True
)
st.write(
"This interactive research blog examines gender differences "
"in Lebanon's labour market using the 2022 Labour Force and "
"Household Living Conditions Survey and historical unemployment "
"estimates."
)

============================================================
11. HEADLINE INDICATORS
============================================================
st.subheader("The headline indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric(
"Women's labour-force participation",
f"{lfp['Women']:.1f}%"
)
k2.metric(
"Men's labour-force participation",
f"{lfp['Men']:.1f}%"
)
k3.metric(
"Participation gap",
f"{participation_gap:.1f} pp"
)
k4.metric(
"Women's unemployment rate",
f"{unemployment['Women']:.1f}%"
)
st.markdown(
f"""
<div class="insight">
<b>Key observation:</b>
In the 2022 survey, labour-force participation was
{lfp['Women']:.1f}% for women and
{lfp['Men']:.1f}% for men.
The difference is {participation_gap:.1f}
percentage points.
Unemployment alone does not capture the full picture
because people outside the labour force are not counted
as unemployed.
</div>
""",
unsafe_allow_html=True
)

============================================================
12. DASHBOARD TABS
============================================================
story_tab, explore_tab, findings_tab, action_tab, methods_tab = st.tabs(
[
"The story",
"Explore the data",
"Key findings",
"From evidence to action",
"Methodology & sources"
]
)

============================================================
13. THE STORY TAB
============================================================
with story_tab:
st.header("The question behind the numbers")
st.write(
"How are gender, educational attainment and age associated "
"with paid labour participation in Lebanon, and do these "
"relationships differ between women and men?"
)
st.write(
"The dashboard focuses on the variables supported by "
"the available national survey tables. Marital status "
"and household composition are not included in the "
"available cross-tabulations."
)
col1, col2, col3 = st.columns(3)
with col1:
st.markdown(
"""
### 01 · Participation
Who is employed, unemployed or outside the labour force?
"""
)
with col2:
st.markdown(
"""
### 02 · Education
How do participation and unemployment vary by education?
"""
)
with col3:
st.markdown(
"""
### 03 · Age
At which life stages are gender differences most visible?
"""
)
st.info(
"The 2022 survey is a cross-sectional snapshot. "
"It shows associations and differences, not causal effects."
)

============================================================
14. EXPLORE THE DATA TAB
============================================================
with explore_tab:
st.header("Explore the labour-market landscape")
st.caption(
"Hover over the charts for exact values. "
"Use the filters to explore selected age groups "
"and education levels."
)
# --------------------------------------------------------
# CHART 1: HISTORICAL UNEMPLOYMENT
# --------------------------------------------------------
st.subheader("1. Unemployment over time")
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
historical_colors = {
"Total unemployment": "#D7A84B",
"Female unemployment": "#D96C5F",
"Male unemployment": "#087E8B"
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
"Year": "Year"
}
)
fig.update_layout(
PLOT_LAYOUT,
hovermode="x unified"
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption(
"Historical figures are transcribed from the uploaded "
"historical unemployment table. Values are percentages."
)
# --------------------------------------------------------
# CHART 2: UNEMPLOYMENT BY GENDER
# --------------------------------------------------------
st.subheader("2. Unemployment by gender in 2022")
gender_unemployment = pd.DataFrame({
"Gender": ["Women", "Men"],
"Rate": [
unemployment["Women"],
unemployment["Men"]
]
})
fig = px.bar(
gender_unemployment,
x="Gender",
y="Rate",
color="Gender",
text_auto=".1f",
color_discrete_map=COLORS,
title="Unemployment among each gender's labour force"
)
fig.update_layout(
PLOT_LAYOUT,
showlegend=False,
yaxis_title="Unemployment rate (%)",
xaxis_title=""
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# CHART 3: UNEMPLOYMENT BY AGE
# --------------------------------------------------------
st.subheader("3. Unemployment by age")
age_unemployment_long = age_unemployment.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Unemployment"
)
fig = px.line(
age_unemployment_long,
x="Category",
y="Unemployment",
color="Gender",
markers=True,
color_discrete_map=COLORS,
title="Unemployment rates across age groups"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Unemployment rate (%)",
xaxis_title="Age group"
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# CHART 4: PARTICIPATION BY AGE
# --------------------------------------------------------
st.subheader("4. Labour-force participation by age")
age_options = age_lfp["Category"].tolist()
chosen_ages = st.multiselect(
"Select age groups",
options=age_options,
default=age_options,
key="age_choice"
)
age_view = age_lfp[
age_lfp["Category"].isin(chosen_ages)
]
age_long = age_view.melt(
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
title="Participation rates across age groups"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Labour-force participation (%)",
xaxis_title="Age group"
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# CHART 5: PARTICIPATION BY EDUCATION
# --------------------------------------------------------
st.subheader("5. Labour-force participation by education")
education_options = education_lfp["Category"].tolist()
chosen_education = st.multiselect(
"Select education levels",
options=education_options,
default=education_options,
key="education_choice"
)
education_view = education_lfp[
education_lfp["Category"].isin(chosen_education)
]
education_long = education_view.melt(
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
barmode="group",
color_discrete_map=COLORS,
title="Participation by completed education level"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Labour-force participation (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# CHART 6: EDUCATION COMPOSITION OF EMPLOYED PEOPLE
# --------------------------------------------------------
st.subheader(
"6. Education composition of employed women and men"
)
employed_long = employed_education.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Share"
)
fig = px.bar(
employed_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Educational composition within each employed group"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Share of employed group (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption(
"This chart describes the education composition of "
"employed people. It is not a participation rate by education."
)
# --------------------------------------------------------
# CHART 7: EMPLOYMENT STATUS
# --------------------------------------------------------
st.subheader("7. Employment status among employed people")
employment_long = employment_status.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Share"
)
fig = px.bar(
employment_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Employment status within employed women and men"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Share within employed group (%)",
xaxis_title="",
xaxis_tickangle=-12
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# CHART 8: JOB-SEARCH METHODS
# --------------------------------------------------------
st.subheader("8. How unemployed people search for work")
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
title="Main job-search methods"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Share within unemployed group (%)",
xaxis_title="",
xaxis_tickangle=-12
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# DATA TABLES AND DOWNLOAD
# --------------------------------------------------------
with st.expander("View the tables used in the charts"):
st.markdown("Participation by age")
st.dataframe(
age_lfp,
use_container_width=True,
hide_index=True
)
st.markdown("Participation by education")
st.dataframe(
education_lfp,
use_container_width=True,
hide_index=True
)
st.markdown("Unemployment by education")
st.dataframe(
education_unemployment,
use_container_width=True,
hide_index=True
)
st.download_button(
"Download participation by education (CSV)",
education_lfp.to_csv(
index=False
).encode("utf-8-sig"),
"participation_by_education_2022.csv",
"text/csv"
)

============================================================
15. KEY FINDINGS TAB
============================================================
with findings_tab:
st.header("What does the evidence suggest?")
st.write(
"The comparisons below highlight observed differences. "
"They should not be interpreted as proof of the reasons "
"behind those differences."
)
# --------------------------------------------------------
# FINDING A: EDUCATION AND PARTICIPATION
# --------------------------------------------------------
st.subheader("A. The education–participation relationship")
education_gap = education_lfp.copy()
education_gap["Gender gap"] = (
education_gap["Men"] - education_gap["Women"]
)
education_long = education_gap.melt(
id_vars=["Category", "Gender gap"],
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Participation"
)
fig = px.bar(
education_long,
x="Category",
y="Participation",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Participation by education and gender"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Labour-force participation (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
university = education_lfp[
education_lfp["Category"].str.lower().str.contains(
"university",
na=False
)
]
if not university.empty:
women_rate = university.iloc[0]["Women"]
men_rate = university.iloc[0]["Men"]
st.markdown(
f"""
<div class="insight">
<b>University education:</b>
Participation is {women_rate:.1f}% among women
and {men_rate:.1f}% among men.
The difference is
{men_rate - women_rate:.1f} percentage points.
</div>
""",
unsafe_allow_html=True
)
# --------------------------------------------------------
# FINDING B: GENDER GAP BY AGE
# --------------------------------------------------------
st.subheader("B. How does the gender gap vary by age?")
age_gap = age_lfp.copy()
age_gap["Gap (men minus women)"] = (
age_gap["Men"] - age_gap["Women"]
)
fig = px.bar(
age_gap,
x="Category",
y="Gap (men minus women)",
color="Gap (men minus women)",
color_continuous_scale=[
"#F2C7BF",
"#D96C5F"
],
title="Participation gap by age group"
)
fig.update_layout(
PLOT_LAYOUT,
coloraxis_showscale=False,
yaxis_title="Percentage-point gap",
xaxis_title="Age group"
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# FINDING C: ECONOMIC STATUS
# --------------------------------------------------------
st.subheader(
"C. Employment, unemployment and being outside "
"the labour force"
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
color_discrete_map=STATUS_COLORS,
title="Distribution by economic status"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Share of each gender (%)",
xaxis_title=""
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# FINDING D: EMPLOYMENT STATUS
# --------------------------------------------------------
st.subheader("D. What types of employment do women and men hold?")
fig = px.bar(
employment_long,
x="Category",
y="Share",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Employment status within employed women and men"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Share within employed group (%)",
xaxis_title="",
xaxis_tickangle=-12
)
st.plotly_chart(
fig,
use_container_width=True
)
employees = employment_status[
employment_status["Category"].str.lower().str.contains(
"employee",
na=False
)
]
if not employees.empty:
women_share = employees.iloc[0]["Women"]
men_share = employees.iloc[0]["Men"]
st.caption(
f"Employees account for {women_share:.1f}% "
f"of employed women and {men_share:.1f}% "
"of employed men in the survey table."
)
# --------------------------------------------------------
# FINDING E: UNEMPLOYMENT BY EDUCATION
# --------------------------------------------------------
st.subheader("E. Unemployment by education")
unemployment_long = education_unemployment.melt(
id_vars="Category",
value_vars=["Women", "Men"],
var_name="Gender",
value_name="Unemployment"
)
fig = px.bar(
unemployment_long,
x="Category",
y="Unemployment",
color="Gender",
barmode="group",
color_discrete_map=COLORS,
title="Unemployment rates by completed education level"
)
fig.update_layout(
PLOT_LAYOUT,
yaxis_title="Unemployment rate (%)",
xaxis_title="",
xaxis_tickangle=-15
)
st.plotly_chart(
fig,
use_container_width=True
)
# --------------------------------------------------------
# LIMITATION
# --------------------------------------------------------
st.warning(
"The supplied survey tables do not provide the required "
"cross-tabulations for marital status and household "
"composition. These parts of the research question "
"remain unanswered and would require additional survey "
"microdata or official tables."
)
#16. FROM EVIDENCE TO ACTION TAB
with action_tab:
st.header("From evidence to action")
st.write(
"These are policy ideas suggested by the patterns in "
"the data. They are proposals to evaluate, not impacts "
"established by this descriptive analysis."
)
left, right = st.columns(2)
with left:
st.markdown(
"""
### 1 · Education-to-employment bridge
Strengthen career guidance, internships,
apprenticeships and employer partnerships so
educational qualifications connect more directly
to paid work.
"""
)
st.markdown(
"""
### 2 · Work and care support
Assess access to affordable childcare, safe
transport and flexible work arrangements.
Evaluate whether these reduce barriers to employment.
"""
)
with right:
st.markdown(
"""
### 3 · Return-to-work pathways
Develop skills-refresh programmes, mentoring
and structured re-entry opportunities for women
returning to paid employment.
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
#17. METHODOLOGY AND SOURCES TAB
with methods_tab:
st.header("Methodology and sources")
st.markdown(
"""
National source
Lebanon Labour Force and Household Living Conditions
Survey 2022.
Tables used: EA1, EA3, EA6, EA8, EA37, EA39 and EA40.
"""
)
st.markdown(
"""
Historical source
Historical unemployment table supplied by the user,
containing total, female and male modelled ILO
unemployment estimates for Lebanon from 1991 to 2023.
"""
)
st.markdown(
"""
Approach
Descriptive analysis of published tables and historical
unemployment estimates. Participation rates,
unemployment rates, employment composition and
employment status are kept distinct because they
have different denominators.
"""
)
st.markdown(
"""
Limitations
The national survey tables relate to 2022.
Cross-sectional comparisons do not establish causality.
Marital status and household composition are not
available in the supplied cross-tabulations.
Historical figures are transcribed from the supplied
image of the unemployment table.
"""
)
st.markdown(
"""
Definitions
Labour-force participation is the share of the relevant
population that is employed or unemployed.
Unemployment is measured among the labour force.
People outside the labour force are neither employed
nor unemployed under the survey classification.
"""
)

#18. FOOTER
st.markdown("---")
st.caption(
"The Invisible Workforce · Lebanon · "
"Exploratory and explanatory data storytelling"
)
