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
st.caption("Interactive exploration of returnee trends by location, gender, and year.")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("Total Returnees", int(df['population'].sum()))
with col3:
    st.metric("Date Range", f"{df['reference_period_start'].min().date()} to {df['reference_period_start'].max().date()}")

st.markdown("---")

# Filters
with st.sidebar:
    st.header("🔍 Filter Data")
    asylum_locations = sorted(df['asylum_location_code'].dropna().unique())
    selected_location = st.selectbox("Asylum Location", options=asylum_locations)

    gender_options = df['gender'].dropna().unique()
    selected_gender = st.selectbox("Gender", options=gender_options)

    years = sorted(df['year'].dropna().unique())
    selected_years = st.slider("Select Year Range", min_value=int(min(years)), max_value=int(max(years)),
                               value=(int(min(years)), int(max(years))))

# Apply filters
filtered_df = df[
    (df['asylum_location_code'] == selected_location) &
    (df['gender'] == selected_gender) &
    (df['year'].between(selected_years[0], selected_years[1]))
]

# Charts
st.subheader(f"📊 Population Trends for {selected_location} - {selected_gender}")
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    colA, colB = st.columns(2)

    # Line chart: population over time
    time_chart = filtered_df.groupby('year')['population'].sum().reset_index()
    fig_line = px.line(time_chart, x='year', y='population', markers=True, title="Population Over Time")
    colA.plotly_chart(fig_line, use_container_width=True)

    # Bar chart: population by population group
    pop_group = filtered_df.groupby('population_group')['population'].sum().reset_index()
    fig_bar = px.bar(pop_group, x='population_group', y='population', color='population_group',
                     title="Population by Group")
    colB.plotly_chart(fig_bar, use_container_width=True)

# Show Data + Download
st.markdown("### 📄 Filtered Data Preview")
st.dataframe(filtered_df.head(100))

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Filtered Data", data=csv, file_name="filtered_returnees.csv", mime='text/csv')
