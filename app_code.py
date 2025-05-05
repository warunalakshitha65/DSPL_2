import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# App Config
st.set_page_config(page_title="Returnees Dashboard - Sri Lanka", layout="wide", page_icon="📊")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
    df.columns = df.columns.str.strip()
    df['reference_period_start'] = pd.to_datetime(df['reference_period_start'], errors='coerce')
    df['reference_period_end'] = pd.to_datetime(df['reference_period_end'], errors='coerce')
    df['Year'] = df['reference_period_start'].dt.year
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    return df.dropna(subset=["population"])

df = load_data()

st.title("📊 Returnees Analytics Dashboard - Sri Lanka")
st.caption("Explore returnee data based on origin, asylum, gender, and more — Powered by HDX")

# Sidebar Filters
with st.sidebar:
    st.header("📂 Filters")
    locations = st.multiselect("🌍 Asylum Location Code", options=df['asylum_location_code'].dropna().unique())
    genders = st.multiselect("🚻 Gender", options=df['gender'].dropna().unique())
    pop_groups = st.multiselect("👥 Population Group", options=df['population_group'].dropna().unique())
    year_range = st.slider("📅 Year Range", int(df['Year'].min()), int(df['Year'].max()), (int(df['Year'].min()), int(df['Year'].max())))

# Apply filters
filtered_df = df[
    (df['Year'].between(year_range[0], year_range[1])) &
    (df['asylum_location_code'].isin(locations) if locations else True) &
    (df['gender'].isin(genders) if genders else True) &
    (df['population_group'].isin(pop_groups) if pop_groups else True)
]

# KPI Section
st.markdown("### 📈 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{len(filtered_df):,}")
col2.metric("Total Population", f"{int(filtered_df['population'].sum()):,}")
col3.metric("Years Covered", f"{year_range[0]} - {year_range[1]}")

st.markdown("---")

# Charts Section
st.subheader("📊 Visual Insights")

# 1. Time Series by Year
pop_by_year = filtered_df.groupby("Year")["population"].sum().reset_index()
fig1 = px.line(pop_by_year, x="Year", y="population", markers=True, title="Population Trend Over Time")
st.plotly_chart(fig1, use_container_width=True)

# 2. Population by Group and Gender
fig2 = px.bar(
    filtered_df.groupby(["population_group", "gender"])["population"].sum().reset_index(),
    x="population_group", y="population", color="gender", barmode="group",
    title="Population by Group and Gender"
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Population Pyramid
if 'min_age' in df.columns and 'max_age' in df.columns:
    pyramid_df = filtered_df.copy()
    pyramid_df['age_group'] = pyramid_df['min_age'].astype(str) + "-" + pyramid_df['max_age'].astype(str)
    pyramid_df = pyramid_df.groupby(['age_group', 'gender'])['population'].sum().reset_index()

    male = pyramid_df[pyramid_df['gender'] == 'Male']
    female = pyramid_df[pyramid_df['gender'] == 'Female']
    male['population'] = -male['population']

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(y=male['age_group'], x=male['population'], name='Male', orientation='h'))
    fig3.add_trace(go.Bar(y=female['age_group'], x=female['population'], name='Female', orientation='h'))
    fig3.update_layout(title='Population Pyramid', barmode='relative')
    st.plotly_chart(fig3, use_container_width=True)

# Download Section
st.subheader("📥 Download Filtered Data")
st.download_button("⬇ Download CSV", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="filtered_returnees.csv")

# Raw Data Toggle
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)



