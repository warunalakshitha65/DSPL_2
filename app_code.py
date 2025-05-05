# Returnees Analytics - Streamlit Dashboard (Distinct Version)

import streamlit as st
import pandas as pd
import plotly.express as px

# Initial config
st.set_page_config(page_title="Returnees Analytics - Sri Lanka", layout="centered", page_icon="📦")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("hdx_hapi_returnees_lka.csv")

df = load_data()

# Title & Description
st.title("📦 Returnees Data Explorer - Sri Lanka")
st.caption("Powered by HDX Data | Explore returnee trends across time and categories")

# Quick Overview Section
with st.container():
    st.subheader("🔍 Quick Glance")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Entries", len(df))

    with col2:
        num_cols = df.select_dtypes(include=["number"]).columns
        if len(num_cols) > 0:
            avg_val = df[num_cols[0]].mean()
            st.metric(f"Average of {num_cols[0]}", f"{avg_val:.2f}")

# Filtering Section
st.divider()
st.subheader("📂 Data Filter")

if 'Year' in df.columns:
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

filter_column = st.selectbox("Choose a Category to Filter", df.select_dtypes(include='object').columns)

unique_vals = df[filter_column].dropna().unique()
selected_val = st.selectbox(f"Select a Value from '{filter_column}'", unique_vals)

filtered_df = df[df[filter_column] == selected_val]

# Select numeric field for analysis
numeric_fields = df.select_dtypes(include=["number"]).columns.tolist()
selected_metric = st.selectbox("Select a Numeric Field for Visualization", numeric_fields)

# Charts Section
st.divider()
st.subheader("📊 Visual Exploration")

chart_option = st.radio("Choose Visualization Type", ["Line", "Bar", "Box", "Area", "Histogram"])

if chart_option == "Line":
    if 'Year' in filtered_df.columns:
        fig = px.line(filtered_df, x='Year', y=selected_metric, markers=True, title="Yearly Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Year column is missing or invalid.")

elif chart_option == "Bar":
    top_n = filtered_df.nlargest(10, selected_metric)
    fig = px.bar(top_n, x=filter_column, y=selected_metric, color=selected_metric, title="Top 10 by Value")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Box":
    if 'Year' in filtered_df.columns:
        fig = px.box(filtered_df, x='Year', y=selected_metric, points="outliers", title="Distribution by Year")
        st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Area":
    if 'Year' in filtered_df.columns:
        area_df = filtered_df.groupby("Year")[selected_metric].sum().reset_index()
        fig = px.area(area_df, x='Year', y=selected_metric, title="Cumulative Area Chart")
        st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Histogram":
    fig = px.histogram(filtered_df, x=selected_metric, nbins=30, title="Value Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Stats + Download Section
st.divider()
with st.expander("📈 Statistical Summary"):
    st.dataframe(filtered_df.describe())

st.download_button(
    label="⬇ Download This Filtered Dataset as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_returnees_data.csv",
    mime="text/csv"
)