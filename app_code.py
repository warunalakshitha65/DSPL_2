import pandas as pd

# Load dataset
df = pd.read_csv('hdx_hapi_returnees_lka.csv')

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Check for missing values
print(df.isnull().sum())

# Drop rows with any missing values (or you can choose to fill them)
df.dropna(inplace=True)

# Convert date columns to datetime
df['reference_period_start'] = pd.to_datetime(df['reference_period_start'])
df['reference_period_end'] = pd.to_datetime(df['reference_period_end'])

# Ensure numeric columns are correct
df['population'] = pd.to_numeric(df['population'], errors='coerce')
df = df.dropna(subset=['population'])  # Drop rows where population couldn't be converted

# Optional: simplify or map codes to district names if known
import streamlit as st
import pandas as pd
import plotly.express as px

# Load and clean data
df = pd.read_csv('hdx_hapi_returnees_lka.csv')
df.columns = df.columns.str.strip()
df.dropna(inplace=True)
df['reference_period_start'] = pd.to_datetime(df['reference_period_start'])
df['reference_period_end'] = pd.to_datetime(df['reference_period_end'])
df['population'] = pd.to_numeric(df['population'], errors='coerce')
df = df.dropna(subset=['population'])

# Sidebar filters
st.sidebar.title("Filters")
selected_gender = st.sidebar.multiselect("Gender", options=df['gender'].unique(), default=df['gender'].unique())
selected_group = st.sidebar.multiselect("Population Group", options=df['population_group'].unique(), default=df['population_group'].unique())

# Filtered data
filtered_df = df[(df['gender'].isin(selected_gender)) & (df['population_group'].isin(selected_group))]

# Main dashboard
st.title("Returnees Dashboard - Sri Lanka")

# Total returnees
st.metric("Total Returnees", int(filtered_df['population'].sum()))

# Returnees by Asylum Location
asylum_chart = px.bar(filtered_df, x='asylum_location_code', y='population', color='gender', title="Returnees by Asylum Location")
st.plotly_chart(asylum_chart)

# Returnees by Origin Location
origin_chart = px.bar(filtered_df, x='origin_location_code', y='population', color='gender', title="Returnees by Origin Location")
st.plotly_chart(origin_chart)

# Time trend
time_chart = px.line(filtered_df.groupby('reference_period_start')['population'].sum().reset_index(), x='reference_period_start', y='population', title="Population Trend Over Time")
st.plotly_chart(time_chart)

streamlit run dashboard.py



