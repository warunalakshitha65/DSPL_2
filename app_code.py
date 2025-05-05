import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config("Returnees Dashboard - Sri Lanka", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
    df.columns = df.columns.str.strip().str.lower()
    df['reference_period_start'] = pd.to_datetime(df['reference_period_start'], errors='coerce')
    df['year'] = df['reference_period_start'].dt.year
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df['min_age'] = pd.to_numeric(df['min_age'], errors='coerce')
    df['max_age'] = pd.to_numeric(df['max_age'], errors='coerce')
    df = df.dropna(subset=['population', 'gender', 'min_age', 'max_age'])
    return df

df = load_data()

# Header
st.title("📦 Returnees Dashboard - Sri Lanka")
st.caption("Explore trends of displaced population returnees using HDX dataset")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("📊 Total Returnees", int(df['population'].sum()))
col2.metric("📄 Total Records", len(df))
col3.metric("📆 Years", f"{df['year'].min()} - {df['year'].max()}")

st.markdown("---")

# Sidebar Filters
with st.sidebar:
    st.header("🔎 Filter Options")
    selected_location = st.selectbox("Asylum Location", df['asylum_location_code'].dropna().unique())
    selected_gender = st.selectbox("Gender", df['gender'].dropna().unique())
    year_range = st.slider("Year Range", min_value=int(df['year'].min()), max_value=int(df['year'].max()),
                           value=(int(df['year'].min()), int(df['year'].max())))

# Filtered DF
filtered_df = df[
    (df['asylum_location_code'] == selected_location) &
    (df['gender'] == selected_gender) &
    (df['year'].between(year_range[0], year_range[1]))
]

# Line Chart
st.subheader(f"📈 Trend of Returnees - {selected_location} ({selected_gender})")
time_chart = filtered_df.groupby('year')['population'].sum().reset_index()
fig = px.line(time_chart, x='year', y='population', markers=True, title="Population Over Time")
st.plotly_chart(fig, use_container_width=True)

# Bar Chart: Population Group
st.subheader("🧑‍🤝‍🧑 Top Population Groups")
top_groups = filtered_df.groupby('population_group')['population'].sum().nlargest(5).reset_index()
fig_bar = px.bar(top_groups, x='population_group', y='population', title="Top 5 Groups")
st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap: Gender vs Age
st.subheader("🌡️ Gender & Age Heatmap")
age_gender = df.groupby(['gender', 'min_age'])['population'].sum().reset_index()
fig_heat = px.density_heatmap(age_gender, x='min_age', y='gender', z='population', histfunc='sum',
                              color_continuous_scale='Plasma')
st.plotly_chart(fig_heat, use_container_width=True)

# Population Pyramid
st.subheader("🔻 Population Pyramid (by Gender & Age)")
pyramid_df = df[(df['min_age'] <= 100)].groupby(['gender', 'min_age'])['population'].sum().reset_index()
males = pyramid_df[pyramid_df['gender'] == 'Male'].sort_values('min_age')
females = pyramid_df[pyramid_df['gender'] == 'Female'].sort_values('min_age')

fig_pyramid = go.Figure()
fig_pyramid.add_trace(go.Bar(y=males['min_age'], x=-males['population'], name='Male', orientation='h'))
fig_pyramid.add_trace(go.Bar(y=females['min_age'], x=females['population'], name='Female', orientation='h'))
fig_pyramid.update_layout(barmode='overlay', title="Population Pyramid", xaxis_title="Population", yaxis_title="Age")
st.plotly_chart(fig_pyramid, use_container_width=True)

# Smart Insights
st.subheader("💡 Smart Insights")
most_returnees_year = time_chart.loc[time_chart['population'].idxmax(), 'year']
st.markdown(f"- 📌 **Peak Returnee Year**: {most_returnees_year}")
st.markdown(f"- 👥 **Most Common Group**: {top_groups.iloc[0]['population_group']}")
st.markdown(f"- 🚻 **Gender Skew**: {df['gender'].value_counts().idxmax()}")

# Table & Download
st.subheader("📋 Filtered Data Table")
st.dataframe(filtered_df.head(100))
st.download_button("⬇ Download CSV", filtered_df.to_csv(index=False), file_name="filtered_returnees.csv")


