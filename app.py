from pathlib import Path
import re
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
HISTORICAL_FILE = DATA_DIR / "unemployment rate women.xlsx"
LFS_FILE = DATA_DIR / "Labor force 2022.xlsx"

COLORS = {
"Women": "#D96C5F",
"Men": "#087E8B",
"Women & Men": "#D7A84B",
"Total unemployment": "#D7A84B",
"Female unemployment": "#D96C5F",
"Male unemployment": "#087E8B"
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
"l": 20,
"r": 20,
"t": 60,
"b": 35
},
"legend_title_text": ""
}

st.markdown(
"""
<style>
.stApp {
background: #F7F8F6;
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

def normalize_text(value):
  """Normalize text for matching column names and labels."""
value = str(value).strip().lower()
value = re.sub(r"[^a-z0-9]+", " ", value)
return " ".join(value.split())

def find_column(columns, keywords):
 """Find a column using possible words in its name."""
for column in columns:
name = normalize_text(column)
if any(keyword in name for keyword in keywords):
return column
return None

def read_section(sheet_name, start_row, end_row):
 """Read a published survey table from columns A:D."""
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
for col in ["Women", "Men", "Women & Men"]:
table[col] = pd.to_numeric(
table[col],
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

@st.cache_data(show_spinner=False)
def load_historical_data():
"""
Load the cleaned historical unemployment workbook.
Expected information:
Year, Total unemployment, Female unemployment,
Male unemployment.
The function supports:
1.	Years in rows and indicators in columns.
2.	Years in columns and indicators in rows.
3.	"""
if not HISTORICAL_FILE.exists():
raise FileNotFoundError(
f"Missing historical file: {HISTORICAL_FILE}"
)
sheets = pd.read_excel(
HISTORICAL_FILE,
sheet_name=None,
header=None
)
aliases = {
"Year": [
"year",
"date",
"years"
],
"Total unemployment": [
"total unemployment",
"unemployment total",
"total unemployment rate",
"unemployment rate total",
"total"
],
"Female unemployment": [
"female unemployment",
"women unemployment",
"female unemployment rate",
"women unemployment rate",
"female",
"women"
],
"Male unemployment": [
"male unemployment",
"men unemployment",
"male unemployment rate",
"men unemployment rate",
"male",
"men"
]
}
required = list(aliases.keys())
for sheet_name, raw in sheets.items():
if raw.empty:
continue
# Try to identify a header row.
for header_index in range(
min(15, len(raw))
):
headers = [
normalize_text(value)
for value in raw.iloc[header_index].tolist()
]
detected = {}
for field, possible_names in aliases.items():
for index, header in enumerate(headers):
if header in possible_names:
detected[field] = index
break
if all(field in detected for field in required):
data = raw.iloc[
header_index + 1:
].copy()
result = pd.DataFrame({
field: data.iloc[:, column_index].values
for field, column_index in detected.items()
})
break
else:
result = None
if result is not None:
result["Year"] = pd.to_numeric(
result["Year"],
errors="coerce"
)
for column in required[1:]:
result[column] = pd.to_numeric(
result[column],
errors="coerce"
)
result = result.dropna(
subset=["Year"]
)
result["Year"] = result["Year"].astype(int)
result = result[
(result["Year"] >= 1991)
& (result["Year"] <= 2023)
]
result = result.dropna(
subset=required[1:],
how="all"
)
if not result.empty:
return result.sort_values(
"Year"
).reset_index(drop=True)
# Try the alternative layout:
# Indicator names in the first column,
# years across the columns.
for row_index in range(len(raw)):
first_cell = normalize_text(
raw.iloc[row_index, 0]
)
if first_cell not in [
"total unemployment",
"total unemployment rate",
"female unemployment",
"female unemployment rate",
"women unemployment",
"women unemployment rate",
"male unemployment",
"male unemployment rate",
"men unemployment",
"men unemployment rate"
]:
continue
# Identify years in the first row.
year_columns = {}
for column_index in range(raw.shape[1]):
value = pd.to_numeric(
raw.iloc[0, column_index],
errors="coerce"
)
if pd.notna(value) and 1991 <= value <= 2023:
year_columns[column_index] = int(value)
if year_columns:
series_rows = {}
for row_index in range(len(raw)):
label = normalize_text(
raw.iloc[row_index, 0]
)
if "total" in label and "unemployment" in label:
series_rows["Total unemployment"] = row_index
elif (
("female" in label or "women" in label)
and "unemployment" in label
):
series_rows["Female unemployment"] = row_index
elif (
("male" in label or "men" in label)
and "unemployment" in label
):
series_rows["Male unemployment"] = row_index
if all(
field in series_rows
for field in required[1:]
):
records = []
for column_index, year in year_columns.items():
record = {"Year": year}
for field in required[1:]:
row_index = series_rows[field]
record[field] = pd.to_numeric(
raw.iloc[row_index, column_index],
errors="coerce"
)
records.append(record)
result = pd.DataFrame(records)
return result.sort_values(
"Year"
).reset_index(drop=True)
raise ValueError(
"Could not identify the historical data layout. "
"The workbook should contain Year, Total unemployment, "
"Female unemployment, and Male unemployment."
)
@st.cache_data(show_spinner=False)
def load_survey():
if not LFS_FILE.exists():
raise FileNotFoundError(
f"Missing survey file: {LFS_FILE}"
)
# Main indicators
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
# Participation rates
age_lfp = read_section(
"EA40", 6, 17
)
education_lfp = read_section(
"EA40", 18, 25
)
# Unemployment rates
age_unemployment = read_section(
"EA39", 6, 17
)
education_unemployment = read_section(
"EA39", 18, 25
)
# Education composition among employed people
employed_education = read_section(
"EA6", 6, 13
)
# Employment status among employed people
employment_status = read_section(
"EA8", 7, 12
)
# Job-search methods
job_search = read_section(
"EA37", 7, 12
)
# Economic status by gender
status_raw = pd.read_excel(
LFS_FILE,
sheet_name="EA3",
header=None
)
status = status_raw.iloc[
16:19, 0:4
].copy()
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
for col in [
"Employed",
"Unemployed",
"Outside labour force"
]:
status[col] = pd.to_numeric(
status[col],
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
"The dashboard could not load the datasets. "
"Check the two filenames, Excel sheets, and data folder."
)
st.exception(error)
st.stop()

lfp_key = next(
(
key for key in headline
if "participation" in normalize_text(key)
),
None
)
unemployment_key = next(
(
key for key in headline
if "unemployment" in normalize_text(key)
),
None
)
if lfp_key is None or unemployment_key is None:
st.error(
"The labour-force participation or unemployment "
"indicator could not be identified in sheet EA1."
)
st.stop()

lfp = headline[lfp_key]
unemployment = headline[unemployment_key]
participation_gap = (
lfp["Men"] - lfp["Women"]
)
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
"This interactive research blog uses Lebanon's 2022 "
"Labour Force and Household Living Conditions Survey "
"and a cleaned historical unemployment dataset covering "
"1991 to 2023."
)
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
The difference is
{participation_gap:.1f} percentage points.
Unemployment alone does not capture the full picture
because people outside the labour force are not counted
as unemployed.
</div>
""",
unsafe_allow_html=True
)
story_tab, explore_tab, findings_tab, action_tab, methods_tab = st.tabs(
[
"The story",
"Explore the data",
"Key findings",
"From evidence to action",
"Methodology & sources"
]
)
TAB 1: THE STORY
with story_tab:
st.header("The question behind the numbers")
st.write(
"How are gender, educational attainment and age "
"associated with paid labour participation in Lebanon, "
"and do these relationships differ between women and men?"
)
st.write(
"The dashboard focuses on the variables supported "
"by the available national survey tables. Marital status "
"and household composition are not included in the "
"available cross-tabulations, so no conclusions are "
"drawn about them."
)
a, b, c = st.columns(3)
a.markdown(
"""
### 01 · Participation
Who is employed, unemployed or outside the labour force?
"""
)
b.markdown(
"""
### 02 · Education
How do participation and unemployment vary by education?
"""
)
c.markdown(
"""
### 03 · Age
At which life stages are gender differences most visible?
"""
)
st.info(
"The 2022 survey is a cross-sectional snapshot. "
"It shows associations and differences, not causal effects."
)

TAB 2: EXPLORE THE DATA
with explore_tab:
st.header("Explore the labour-market landscape")
st.caption(
"Hover over the charts for exact values. "
"Use the filters to focus on selected age groups "
"and education levels."
)
# 1. HISTORICAL UNEMPLOYMENT
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
historical_long = historical_long.dropna(
subset=["Rate"]
)
fig = px.line(
historical_long,
x="Year",
y="Rate",
color="Indicator",
markers=True,
color_discrete_map=COLORS,
title=(
"Unemployment rates in Lebanon, 1991–2023"
),
labels={
"Rate": "Unemployment rate (%)",
"Year": "Year",
"Indicator": ""
}
)
fig.update_layout(
PLOT_LAYOUT,
hovermode="x unified",
xaxis=dict(
dtick=2,
title="Year"
),
yaxis_title="Unemployment rate (%)"
)
st.plotly_chart(
fig,
use_container_width=True
)
st.caption(
"Source: cleaned historical unemployment workbook. "
"All three series—total, female and male—are taken "
"from the same file."
)
# 2. UNEMPLOYMENT BY GENDER IN 2022
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
# 3. FEMALE UNEMPLOYMENT BY AGE
st.subheader("3. Female unemployment by age")
youth = age_unemployment[
age_unemployment["Category"].isin(
["15-19", "20-24"]
)
].copy()
female_age = pd.concat(
[
pd.DataFrame({
"Age group": ["All ages 15+"],
"Rate": [unemployment["Women"]]
}),
youth[
["Category", "Women"]
].rename(
columns={
"Category": "Age group",
"Women": "Rate"
}
)
],
ignore_index=True
)
fig = px.bar(
female_age,
x="Age group",
y="Rate",
text_auto=".1f",
color_discrete_sequence=["#D96C5F"],
title=(
"Women's unemployment: overall and selected youth groups"
)
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
# 4. PARTICIPATION BY AGE

st.subheader("4. Labour-force participation by age")
age_options = age_lfp["Category"].tolist()
chosen_ages = st.multiselect(
"Select age groups",
age_options,
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
# 5. PARTICIPATION BY EDUCATION
st.subheader(
"5. Labour-force participation by education"
)
education_options = education_lfp[
"Category"
].tolist()
chosen_education = st.multiselect(
"Select education levels",
education_options,
default=education_options,
key="education_choice"
)
education_view = education_lfp[
education_lfp["Category"].isin(
chosen_education
)
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
# 6. EDUCATION COMPOSITION OF EMPLOYED PEOPLE
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
title=(
"Educational composition within each employed group"
)
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
"This chart describes the education composition "
"of employed people. It is not a participation rate "
"by education."
)

# 7. EMPLOYMENT STATUS AMONG EMPLOYED PEOPLE
st.subheader(
"7. Employment status among employed people"
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
title=(
"Employment status within employed women and men"
)
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
# 8. JOB SEARCH METHODS
st.subheader(
"8. How unemployed people search for work"
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
title=(
"Main job-search methods reported in the previous four weeks"
)
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
# TABLES
with st.expander(
"View the tables used in the charts"
):
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
TAB 3: KEY FINDINGS
with findings_tab:
st.header("What does the evidence suggest?")
st.write(
"The comparisons below highlight observed differences. "
"They should not be interpreted as proof of the reasons "
"behind those differences."
)
# A. EDUCATION AND PARTICIPATION
st.subheader(
"A. The education–participation relationship"
)
edu_long = education_lfp.melt(
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
title=(
"Participation by completed education level and gender"
)
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
uw = university.iloc[0]["Women"]
um = university.iloc[0]["Men"]
st.markdown(
f"""
<div class="insight">
<b>University education:</b>
Participation is {uw:.1f}% among women
and {um:.1f}% among men.
The difference is
{um - uw:.1f} percentage points
in the 2022 survey.
</div>
""",
unsafe_allow_html=True
)
# B. AGE GENDER GAP
st.subheader(
"B. How does the gender gap vary by age?"
)
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
# C. ECONOMIC STATUS BY GENDER
st.subheader(
"C. Employment, unemployment and being outside the labour force"
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
color_discrete_map={
"Employed": "#087E8B",
"Unemployed": "#D7A84B",
"Outside labour force": "#D96C5F"
},
title=(
"Distribution of residents aged 15+ by economic status"
)
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
# D. EMPLOYMENT STATUS
st.subheader(
"D. What types of employment do women and men hold?"
)
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
title=(
"Employment status within employed women and men"
)
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
employment_status["Category"].str.lower().eq(
"employees"
)
]
if not employees.empty:
st.caption(
f"Employees account for "
f"{employees.iloc[0]['Women']:.1f}% of employed women "
f"and {employees.iloc[0]['Men']:.1f}% of employed men "
"in the survey table."
)
# E. UNEMPLOYMENT BY EDUCATION
st.subheader(
"E. Unemployment by education"
)
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
title=(
"Unemployment rates by completed education level"
)
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
# LIMITATIONS
The national survey tables are for 2022.
Cross-sectional comparisons do not establish causality.
Marital status and household composition are not
available in the supplied cross-tabulations.
"""
st.warning(
"The supplied survey tables do not provide the required "
"cross-tabulations for marital status and household "
"composition. These parts of the research question "
"remain unanswered and would require additional survey "
"microdata or official tables."
)

TAB 4: FROM EVIDENCE TO ACTION
#with action_tab:
st.header("From evidence to action")
st.write(
"These are policy ideas suggested by the patterns "
"in the data. They are proposals to evaluate, not "
"impacts established by this descriptive analysis."
)
left, right = st.columns(2)
with left:
st.markdown(
"""
### 1 · Education-to-employment bridge
Strengthen career guidance, internships,
apprenticeships and employer partnerships so that
educational qualifications connect more directly
to paid work.
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
TAB 5: METHODOLOGY AND SOURCES
with methods_tab:
st.header("Methodology and sources")
st.markdown(
"""
Historical source:
Cleaned unemployment dataset containing total,
female and male unemployment rates for Lebanon
from 1991 to 2023.
"""
)
st.markdown(
"""
National source:
Lebanon Labour Force and Household Living Conditions
Survey 2022, tables EA1, EA3, EA6, EA8, EA37, EA39
and EA40.
"""
)
st.markdown(
"""
Approach:
Descriptive analysis of historical unemployment
rates and published national survey cross-tabulations.
Participation rates, unemployment rates, employment
composition and employment status are kept distinct
because they use different denominators.
"""
)
st.markdown(
"""
Limitations:
The national survey tables are for 2022.
Cross-sectional comparisons do not establish causality.
Marital status and household composition are not
available in the supplied cross-tabulations.
"""
)
st.markdown("**Definitions:**")
st.markdown ("-Labour-force participation is the share of the relevant population that is employed or unemployed.")
st.markdown ("-Unemployment is measured among the labour force.")
st.markdown ("-People outside the labour force are neither employed nor unemployed under the survey's classification.")

	)
st.markdown(
"""
Historical comparison:
The historical unemployment chart uses the three
series in the cleaned historical workbook. The
national survey provides the separate 2022
cross-sectional analysis.

st.markdown("---")
st.caption(
"The Invisible Workforce · Lebanon · "
"Exploratory and explanatory data storytelling"
)


