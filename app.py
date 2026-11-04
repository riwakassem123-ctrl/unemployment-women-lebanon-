from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="The Invisible Workforce",
    page_icon="📊",
    layout="wide"
)

# Survey values from EA1
WOMEN_LFP = 22.216
MEN_LFP = 66.213

WOMEN_UNEMPLOYMENT = 32.712
MEN_UNEMPLOYMENT = 28.413

PARTICIPATION_GAP = MEN_LFP - WOMEN_LFP
st.title("The Invisible Workforce")

st.markdown("""
### Understanding Gender, Education and Employment in Lebanon

This interactive dashboard explores gender differences
in labour-force participation and unemployment.
""")
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Women's Labour Force Participation",
    f"{WOMEN_LFP:.1f}%"
)

c2.metric(
    "Men's Labour Force Participation",
    f"{MEN_LFP:.1f}%"
)

c3.metric(
    "Participation Gap",
    f"{PARTICIPATION_GAP:.1f} pp"
)

c4.metric(
    "Women's Unemployment",
    f"{WOMEN_UNEMPLOYMENT:.1f}%"
)
history = pd.DataFrame(
    {
        "Year":[2020,2021,2022,2023],
        "Female":[16.249,15.874,14.593,14.480],
        "Male":[12.045,11.515,9.816,9.705],
        "Total":[13.252,12.715,11.105,10.985]
    }
)

long_df = history.melt(
    id_vars="Year",
    var_name="Indicator",
    value_name="Rate"
)

fig = px.line(
    long_df,
    x="Year",
    y="Rate",
    color="Indicator",
    markers=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.header("Key Findings")

st.write(
    "Women participate in the labour market at much lower rates than men."
)

st.write(
    "The participation gap exceeds 40 percentage points."
)

st.write(
    "Unemployment remains high among women."
)
st.markdown("---")

st.caption(
    "The Invisible Workforce | Lebanon"
)
