import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config("Sri Lanka Returnees Dashboard", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
    df.columns = df.columns.str.strip().str.lower()
    df['reference_period_start'] = pd.to_datetime(df['reference_period_start'], errors='coerce')
    df['year'] = df['reference_period_start'].dt.year
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    return df.dropna(subset=['population'])

df = load_data()

# Header
st.title("📦 Returnees Analytics Dashboard - Sri Lanka")
st.caption("Interactive exploration of returnee trends by location, gender, age and year.")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("Total Returnees", int(df['population'].sum()))
with col3:
    st.metric("Year Range", f"{df['year'].min()} - {df['year'].max()}")

st.markdown("---")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter Options")
    asylum_locations = sorted(df['asylum_location_code'].dropna().unique())
    selected_location = st.selectbox("Asylum Location", options=asylum_locations)

    gender_options = df['gender'].dropna().unique()
    selected_gender = st.selectbox("Gender", options=gender_options)

    years = sorted(df['year'].dropna().unique())
    selected_years = st.slider("Select Year Range", min_value=int(min(years)), max_value=int(max(years)),
                               value=(int(min(years)), int(max(years))))

# Filter Data
filtered_df = df[
    (df['asylum_location_code'] == selected_location) &
    (df['gender'] == selected_gender) &
    (df['year'].between(selected_years[0], selected_years[1]))
]

st.subheader(f"📊 Population Trends for {selected_location} - {selected_gender}")

if filtered_df.empty:
    st.warning("No data available for selected filters.")
else:
    # Charts
    colA, colB = st.columns(2)

    # Line Chart
    time_chart = filtered_df.groupby('year')['population'].sum().reset_index()
    fig_line = px.line(time_chart, x='year', y='population', markers=True, title="Population Over Time")
    colA.plotly_chart(fig_line, use_container_width=True)

    # Bar Chart: Population Groups
    group_chart = filtered_df.groupby('population_group')['population'].sum().reset_index()
    fig_bar = px.bar(group_chart, x='population_group', y='population', title="By Population Group")
    colB.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Top 5 Population Groups Table
    st.subheader("🏆 Top 5 Population Groups by Population")
    top5 = group_chart.sort_values(by='population', ascending=False).head(5)
    st.table(top5)

    # Histogram of Age Ranges
    st.subheader("📊 Age Range Histogram")
    if 'min_age' in filtered_df.columns:
        fig_hist = px.histogram(filtered_df, x='min_age', nbins=20, title="Distribution by Minimum Age")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Growth Rate
    st.subheader("📈 Year-on-Year Growth")
    time_chart['growth_%'] = time_chart['population'].pct_change() * 100
    st.dataframe(time_chart.fillna(0).round(2))

# Data Table and Download
st.markdown("### 📄 Filtered Data Table")
st.dataframe(filtered_df.head(100))

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("⬇ Download Filtered Data", data=csv, file_name="filtered_returnees.csv", mime='text/csv')

