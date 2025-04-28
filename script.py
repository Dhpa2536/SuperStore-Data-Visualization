import pandas as pd
import altair as alt
from pathlib import Path
import webbrowser

# Configuration
alt.data_transformers.disable_max_rows()

# Data Loading
try:
    df = pd.read_csv(
        Path("C:/Users/dhrum/PROJECTS/Superstore Analysis/Sample - Superstore.csv"),
        encoding='ISO-8859-1'
    )
except FileNotFoundError:
    df = pd.read_csv("Sample - Superstore.csv")

# Data Prep
df['Order Date'] = pd.to_datetime(df['Order Date'])
df = df[df['Order Date'].dt.year.isin([2014, 2015])]

# Add "All Regions" option
regions = ['All'] + sorted(df['Region'].unique().tolist())

# CORRECTED DROPDOWN - Uses selection_point with proper value format
region_dropdown = alt.selection_point(
    fields=['Region'],
    bind=alt.binding_select(options=regions, name='Select Region:'),
    name='region_filter',
    value=[{'Region': 'All'}]  # <-- Must be a list of objects
)

# Sales Chart
sales = alt.Chart(df).mark_bar().encode(
    x=alt.X('sum(Sales):Q', title='Sales ($)')
        .axis(format='$.1s', labelAngle=0),
    y=alt.Y('Category:N', title='', sort='-x'),
    color=alt.Color('Region:N', legend=alt.Legend(
        title="Region",
        labelLimit=0,
        columns=2,
        orient='top',
        direction='horizontal',
        symbolLimit=0,
    ))
).transform_filter(
    "region_filter.Region == 'All' || datum.Region == region_filter.Region"
).add_params(
    region_dropdown
).properties(
    width=900,
    height=450,
    title='Sales by Category',
)

# Profit Chart
profit = alt.Chart(df).mark_line().encode(
    x=alt.X('yearmonth(Order Date):T', title='Date')
        .axis(labelAngle=45),
    y=alt.Y('sum(Profit):Q', title='Profit ($)')
        .axis(format='$,.0f'),
    color=alt.value('firebrick')
).transform_filter(
    "region_filter.Region == 'All' || datum.Region == region_filter.Region"
).properties(
    width=1000,
    height=400,
    title='Monthly Profit Trend',
)

# Matrix
matrix = alt.Chart(df).mark_circle(size=8).encode(
    alt.X(alt.repeat("column"), type='quantitative')
        .title('Value')
        .axis(labelAngle=0),
    alt.Y(alt.repeat("row"), type='quantitative')
        .title('Value'),
    color='Region:N'
).properties(
    width=300,
    height=300
).repeat(
    row=['Discount', 'Profit', 'Sales'],
    column=['Profit', 'Sales', 'Discount']
).transform_filter(
    "region_filter.Region == 'All' || datum.Region == region_filter.Region"
).properties(
    title='Discount-Profit-Sales Relationships'
)

# Dashboard Configuration
dashboard = alt.vconcat(
    sales,
    profit,
    matrix,
    spacing=30
).configure_legend(
    labelLimit=0,
    columns=2
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=32,
    anchor='middle'
).properties(
    title='Superstore Analysis Dashboard (2014-2015)',
    padding={"left": 80, "right": 80, "top": 50, "bottom": 200}
)

dashboard.save('dashboard_final.html')
webbrowser.open('dashboard_final.html')
