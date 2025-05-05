# 📦 Returnees Analytics Dashboard - Cleaned Version

import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit page setup
st.set_page_config(page_title="Returnees Analytics - Sri Lanka", layout="centered", page_icon="📦")

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
    df.columns = df.columns.str.strip()
    df['reference_period_start'] = pd.to_datetime(df['reference_period_start'], errors='coerce')
    df['Year'] = df['reference_period_start'].dt.year
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    return df.dropna(subset=['population'])
    
df = load_data()

# Title and description
st.title("📦 Returnees Data Explorer - Sri Lanka")
st.caption("Powered by HDX Data | Explore returnee trends across time and categories")

# Overview
with st.container():
    st.subheader("🔍 Quick Glance")
    col1, col2 = st.columns(2)
    col1.metric("Total Records", len(df))
    col2.metric("Total Returnees", int(df['population'].sum()))

# Filters
st.divider()
st.subheader("📂 Data Filter")

filter_column = st.selectbox("Choose a Category to Filter", df.select_dtypes(include='object').columns)
unique_vals = df[filter_column].dropna().unique()
selected_val = st.selectbox(f"Select a Value from '{filter_column}'", unique_vals)
filtered_df = df[df[filter_column] == selected_val]

numeric_fields = df.select_dtypes(include=["number"]).columns.tolist()
selected_metric = st.selectbox("Select a Numeric Field for Visualization", numeric_fields)

# Charts
st.divider()
st.subheader("📊 Visual Exploration")

chart_option = st.radio("Choose Visualization Type", ["Line", "Bar", "Box", "Area", "Histogram"])

if chart_option == "Line":
    if 'Year' in filtered_df.columns:
        fig = px.line(filtered_df, x='Year', y=selected_metric, markers=True, title=f"Yearly Trend of {selected_metric}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Year column not found.")

elif chart_option == "Bar":
    top_n = filtered_df.nlargest(10, selected_metric)
    fig = px.bar(top_n, x=filter_column, y=selected_metric, color=selected_metric, title=f"Top 10 by {selected_metric}")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Box":
    fig = px.box(filtered_df, x='Year', y=selected_metric, points="outliers", title=f"{selected_metric} Distribution by Year")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Area":
    area_df = filtered_df.groupby("Year")[selected_metric].sum().reset_index()
    fig = px.area(area_df, x='Year', y=selected_metric, title=f"{selected_metric} Area Chart Over Years")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Histogram":
    fig = px.histogram(filtered_df, x=selected_metric, nbins=30, title=f"{selected_metric} Value Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Summary and download
st.divider()
with st.expander("📈 Statistical Summary"):
    st.dataframe(filtered_df.describe())

st.download_button(
    label="⬇ Download Filtered Dataset as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_returnees_data.csv",
    mime="text/csv"
)
