import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration with modern styling
st.set_page_config(
    page_title="Returnees Dashboard - Sri Lanka",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {color:#1E88E5; font-size:42px; font-weight:bold; margin-bottom:10px;}
    .sub-header {color:#424242; font-size:22px; margin-bottom:20px;}
    .card {padding:15px; border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom:20px;}
    .metric-value {font-size:28px; font-weight:bold; color:#1E88E5;}
    .metric-label {font-size:14px; color:#616161;}
    .insight-card {background-color:#f5f7ff; padding:15px; border-radius:10px; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

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

# Load data
df = load_data()

# Header section with modern styling
st.markdown('<div class="main-header">Sri Lanka Returnees Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Humanitarian data analysis of displaced population returns</div>', unsafe_allow_html=True)

# Last updated info
today = datetime.now().strftime("%B %d, %Y")
st.markdown(f"<p style='color:#616161; font-size:14px;'>Last updated: {today}</p>", unsafe_allow_html=True)

# KPIs in attractive cards
st.markdown('<div style="display:flex; justify-content:space-between; margin-bottom:30px;">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card" style="background-color:#e3f2fd;">
        <div class="metric-label">TOTAL RETURNEES</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(int(df['population'].sum())), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="background-color:#e8f5e9;">
        <div class="metric-label">DATA RECORDS</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(len(df)), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card" style="background-color:#fffde7;">
        <div class="metric-label">REPORTING PERIOD</div>
        <div class="metric-value">{} - {}</div>
    </div>
    """.format(int(df['year'].min()), int(df['year'].max())), unsafe_allow_html=True)

# Sidebar with improved styling
with st.sidebar:
    st.image("https://via.placeholder.com/150x60?text=HDX+Logo", width=150)
    st.markdown("### 🔍 Filter Dashboard")
    
    selected_location = st.selectbox(
        "📍 Asylum Location", 
        df['asylum_location_code'].dropna().unique()
    )
    
    selected_gender = st.selectbox(
        "👤 Gender", 
        df['gender'].dropna().unique()
    )
    
    year_range = st.slider(
        "📅 Year Range", 
        min_value=int(df['year'].min()), 
        max_value=int(df['year'].max()),
        value=(int(df['year'].min()), int(df['year'].max()))
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This dashboard visualizes data on returnee populations to Sri Lanka, sourced from the Humanitarian Data Exchange (HDX).")

# Filter data based on selections
filtered_df = df[
    (df['asylum_location_code'] == selected_location) &
    (df['gender'] == selected_gender) &
    (df['year'].between(year_range[0], year_range[1]))
]

# Main content in tabs for better organization
tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Demographics", "🔢 Raw Data"])

with tab1:
    # Line Chart with improved styling
    st.markdown("### Population Trend Over Time")
    time_chart = filtered_df.groupby('year')['population'].sum().reset_index()
    
    fig = px.line(
        time_chart, 
        x='year', 
        y='population', 
        markers=True,
        line_shape="spline",
        template="plotly_white"
    )
    
    fig.update_traces(
        line=dict(width=3, color="#1E88E5"),
        marker=dict(size=8, color="#1E88E5")
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="Number of Returnees",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar Chart: Population Group with better styling
    st.markdown("### Top Population Groups")
    top_groups = filtered_df.groupby('population_group')['population'].sum().nlargest(5).reset_index()
    
    fig_bar = px.bar(
        top_groups, 
        x='population_group', 
        y='population',
        color='population',
        color_continuous_scale='Blues',
        template="plotly_white"
    )
    
    fig_bar.update_layout(
        height=400,
        xaxis_title="Population Group",
        yaxis_title="Number of Returnees",
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Heatmap: Gender vs Age
        st.markdown("### Gender & Age Distribution")
        age_gender = filtered_df.groupby(['gender', 'min_age'])['population'].sum().reset_index()
        
        fig_heat = px.density_heatmap(
            age_gender, 
            x='min_age', 
            y='gender', 
            z='population', 
            histfunc='sum',
            color_continuous_scale='Blues',
            template="plotly_white"
        )
        
        fig_heat.update_layout(
            height=350,
            xaxis_title="Age",
            yaxis_title="Gender",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with col2:
        # Population Pyramid
        st.markdown("### Population Pyramid")
        pyramid_df = filtered_df[(filtered_df['min_age'] <= 100)].groupby(['gender', 'min_age'])['population'].sum().reset_index()
        
        males = pyramid_df[pyramid_df['gender'] == 'Male'].sort_values('min_age')
        females = pyramid_df[pyramid_df['gender'] == 'Female'].sort_values('min_age')
        
        fig_pyramid = go.Figure()
        
        fig_pyramid.add_trace(go.Bar(
            y=males['min_age'],
            x=-males['population'],
            name='Male',
            orientation='h',
            marker=dict(color='#1976D2')
        ))
        
        fig_pyramid.add_trace(go.Bar(
            y=females['min_age'],
            x=females['population'],
            name='Female',
            orientation='h',
            marker=dict(color='#EF5350')
        ))
        
        fig_pyramid.update_layout(
            barmode='overlay',
            height=350,
            xaxis_title="Population",
            yaxis_title="Age",
            template="plotly_white",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig_pyramid, use_container_width=True)

    # Smart Insights with better styling
    st.markdown("### 💡 Key Insights")
    
    most_returnees_year = time_chart.loc[time_chart['population'].idxmax(), 'year'] if not time_chart.empty else "N/A"
    most_common_group = top_groups.iloc[0]['population_group'] if not top_groups.empty else "N/A"
    gender_ratio = filtered_df.groupby('gender')['population'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="insight-card">
            <h4>Peak Return Year</h4>
            <p>{}</p>
        </div>
        """.format(most_returnees_year), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card">
            <h4>Primary Group</h4>
            <p>{}</p>
        </div>
        """.format(most_common_group), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="insight-card">
            <h4>Gender Ratio</h4>
            <p>M:F = {:.1f}:{:.1f}</p>
        </div>
        """.format(
            gender_ratio.get('Male', 0) / gender_ratio.sum() * 100 if gender_ratio.sum() > 0 else 0,
            gender_ratio.get('Female', 0) / gender_ratio.sum() * 100 if gender_ratio.sum() > 0 else 0
        ), unsafe_allow_html=True)

with tab3:
    # Data table with download option
    st.markdown("### Filtered Dataset")
    st.markdown(f"Showing data for **{selected_location}** location, **{selected_gender}** gender, years **{year_range[0]}-{year_range[1]}**")
    
    # Display only the most relevant columns
    display_cols = ['year', 'population', 'population_group', 'min_age', 'max_age', 'asylum_location_code']
    st.dataframe(filtered_df[display_cols].head(100), use_container_width=True)
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            filtered_df.to_csv(index=False), 
            file_name="sri_lanka_returnees_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        st.download_button(
            "📥 Download Full Dataset (CSV)",
            df.to_csv(index=False), 
            file_name="sri_lanka_returnees_full.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#9e9e9e; font-size:12px;'>Data source: Humanitarian Data Exchange (HDX) • Developed with Streamlit</p>", unsafe_allow_html=True)
