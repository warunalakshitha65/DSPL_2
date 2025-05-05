import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the cleaned dataset
df = pd.read_csv('cleaned_returnees_dataset.csv')

# Convert 'reference_period_start' to datetime and extract year
df['reference_period_start'] = pd.to_datetime(df['reference_period_start'])
df['year'] = df['reference_period_start'].dt.year

# Sidebar filters
st.sidebar.title("📊 Filter Options")
origin_codes = st.sidebar.multiselect("Select Origin Location Codes:", df['origin_location_code'].unique(), default=df['origin_location_code'].unique())
asylum_codes = st.sidebar.multiselect("Select Asylum Location Codes:", df['asylum_location_code'].unique(), default=df['asylum_location_code'].unique())
genders = st.sidebar.multiselect("Select Genders:", df['sex'].unique(), default=df['sex'].unique())
age_ranges = st.sidebar.multiselect("Select Age Ranges:", df['age_range'].unique(), default=df['age_range'].unique())
years = st.sidebar.multiselect("Select Years:", sorted(df['year'].unique()), default=sorted(df['year'].unique()))

# Filter the dataset
filtered_df = df[
    (df['origin_location_code'].isin(origin_codes)) &
    (df['asylum_location_code'].isin(asylum_codes)) &
    (df['sex'].isin(genders)) &
    (df['age_range'].isin(age_ranges)) &
    (df['year'].isin(years))
]

# Tabs
tab1, tab2 = st.tabs(["📈 Overview", "👤 Demographics"])

# ============ TAB 1: Overview ============

with tab1:
    st.markdown("### 🌍 Returnees by Origin Location (Choropleth)")

    map_df = filtered_df.groupby('origin_location_code')['population'].sum().reset_index()
    map_df = map_df[map_df['origin_location_code'].str.len() == 3]  # Adjust depending on your code format

    fig_map = px.choropleth(
        map_df,
        locations='origin_location_code',
        locationmode='ISO-3',
        color='population',
        color_continuous_scale='Blues',
        template='plotly_white',
        title="Returnees by Origin Country"
    )

    fig_map.update_layout(margin=dict(l=40, r=40, t=40, b=40), height=450)
    st.plotly_chart(fig_map, use_container_width=True)

    # Animated bar chart over time
    st.markdown("### 📽️ Animated Bar Chart: Top Population Groups Over Time")

    anim_df = filtered_df.groupby(['year', 'population_group'])['population'].sum().reset_index()
    anim_df = anim_df[anim_df['population_group'].notna()]

    fig_anim = px.bar(
        anim_df,
        x='population_group',
        y='population',
        color='population_group',
        animation_frame='year',
        range_y=[0, anim_df['population'].max()],
        title="Population Groups Over Time",
        template="plotly_white"
    )
    fig_anim.update_layout(height=450, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_anim, use_container_width=True)

# ============ TAB 2: Demographics ============

with tab2:
    # Gender distribution
    st.markdown("### 👥 Gender Distribution of Returnees")

    gender_df = filtered_df.groupby('sex')['population'].sum().reset_index()

    fig_gender = px.pie(
        gender_df,
        names='sex',
        values='population',
        title="Gender Distribution",
        template="plotly_white"
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    # Age range box plot by population group
    st.markdown("### 📦 Age Range Distribution by Population Group (Box Plot)")

    box_df = filtered_df.copy()
    box_df['age_range_length'] = box_df['max_age'] - box_df['min_age']

    fig_box = px.box(
        box_df,
        x='population_group',
        y='age_range_length',
        points='all',
        title="Age Range Spread per Population Group",
        template="plotly_white",
        color='population_group'
    )
    fig_box.update_layout(height=400, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_box, use_container_width=True)

# End of app
st.markdown("---")
st.markdown("Built with ❤️ by Waruna for MLDM Coursework Dashboard (2025)")
