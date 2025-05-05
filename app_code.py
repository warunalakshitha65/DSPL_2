import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from plotly.subplots import make_subplots

# Set page configuration with custom theme
st.set_page_config(
    page_title="Returnees Dashboard - Sri Lanka",
    page_icon="🇱🇰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 0.5rem;
        margin-top: 1rem;
    }
    .kpi-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .insight-card {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #6B7280;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("hdx_hapi_returnees_lka.csv")
        df.columns = df.columns.str.strip().str.lower()
        
        # Convert and clean date columns
        df['reference_period_start'] = pd.to_datetime(df['reference_period_start'], errors='coerce')
        df['reference_period_end'] = pd.to_datetime(df['reference_period_end'], errors='coerce')
        
        # Create additional date fields
        df['year'] = df['reference_period_start'].dt.year
        df['month'] = df['reference_period_start'].dt.month
        df['quarter'] = df['reference_period_start'].dt.quarter
        
        # Calculate return duration (in days)
        df['return_duration'] = (df['reference_period_end'] - df['reference_period_start']).dt.days
        
        # Clean numeric columns
        numeric_cols = ['population', 'min_age', 'max_age']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create age groups
        bins = [0, 5, 18, 30, 50, 65, 100]
        labels = ['Under 5', '5-17', '18-29', '30-49', '50-64', '65+']
        df['age_group'] = pd.cut(df['min_age'], bins=bins, labels=labels, right=False)
        
        # Drop records with missing essential data
        df = df.dropna(subset=['population', 'gender', 'min_age', 'max_age'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
df = load_data()

# Function to check if dataframe is empty
def check_data():
    if df.empty:
        st.error("No data available. Please check your data source.")
        st.stop()

check_data()

# Dashboard Header
st.markdown('<h1 class="main-header">🇱🇰 Returnees Dashboard - Sri Lanka</h1>', unsafe_allow_html=True)
st.markdown("""
This interactive dashboard visualizes patterns and trends of displaced population returnees in Sri Lanka.
Use the filters in the sidebar to explore specific segments of data.
""")

# Sidebar for filters
with st.sidebar:
    st.image("https://www.un.org/sites/un2.un.org/files/2021/03/un-emblem-blue.png", width=100)
    st.markdown("## 🔍 Filter Data")
    
    # Time period filter
    st.markdown("### Time Period")
    date_filter = st.radio("Filter by:", ["Year", "Year Range", "Full Period"])
    
    if date_filter == "Year":
        selected_year = st.selectbox("Select Year", sorted(df['year'].dropna().unique(), reverse=True))
        year_filter = (df['year'] == selected_year)
    elif date_filter == "Year Range":
        year_range = st.slider("Select Year Range", 
                          min_value=int(df['year'].min()), 
                          max_value=int(df['year'].max()),
                          value=(int(df['year'].min()), int(df['year'].max())))
        year_filter = (df['year'].between(year_range[0], year_range[1]))
    else:
        year_filter = (df['year'] >= df['year'].min())
    
    # Location filters
    st.markdown("### Geography")
    location_filter_type = st.radio("Location Filter Type:", ["All Locations", "Specific Location"])
    
    if location_filter_type == "Specific Location":
        selected_location = st.selectbox("Select Asylum Location", 
                                    sorted(df['asylum_location_code'].dropna().unique()))
        location_filter = (df['asylum_location_code'] == selected_location)
    else:
        location_filter = (df['asylum_location_code'].notna())
    
    # Demographic filters
    st.markdown("### Demographics")
    
    # Gender filter
    gender_options = ["All"] + sorted(df['gender'].dropna().unique().tolist())
    selected_gender = st.selectbox("Select Gender", gender_options)
    
    if selected_gender != "All":
        gender_filter = (df['gender'] == selected_gender)
    else:
        gender_filter = (df['gender'].notna())
    
    # Age group filter
    age_options = ["All"] + sorted(df['age_group'].dropna().unique().tolist())
    selected_age_group = st.selectbox("Select Age Group", age_options)
    
    if selected_age_group != "All":
        age_filter = (df['age_group'] == selected_age_group)
    else:
        age_filter = (df['age_group'].notna())
    
    # Population group filter
    pop_group_options = ["All"] + sorted(df['population_group'].dropna().unique().tolist())
    selected_pop_group = st.selectbox("Select Population Group", pop_group_options)
    
    if selected_pop_group != "All":
        pop_group_filter = (df['population_group'] == selected_pop_group)
    else:
        pop_group_filter = (df['population_group'].notna())
    
    # Apply all filters
    filtered_df = df[year_filter & location_filter & gender_filter & age_filter & pop_group_filter]
    
    # Show current filter summary
    st.markdown("### Active Filters")
    if date_filter == "Year":
        st.markdown(f"- **Year**: {selected_year}")
    elif date_filter == "Year Range":
        st.markdown(f"- **Years**: {year_range[0]} to {year_range[1]}")
    else:
        st.markdown(f"- **Years**: All ({df['year'].min()} to {df['year'].max()})")
    
    if location_filter_type == "Specific Location":
        st.markdown(f"- **Location**: {selected_location}")
    else:
        st.markdown("- **Location**: All Locations")
        
    st.markdown(f"- **Gender**: {selected_gender}")
    st.markdown(f"- **Age Group**: {selected_age_group}")
    st.markdown(f"- **Population Group**: {selected_pop_group}")
    
    # Reset filters button
    if st.button("Reset All Filters"):
        st.rerun()

# Check if filtered data is empty
if filtered_df.empty:
    st.warning("No data matches your filter criteria. Please adjust your filters.")
    st.stop()

# KPI Cards in the top row
st.markdown('<h2 class="sub-header">📊 Key Metrics</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Format large numbers with commas
total_returnees = f"{int(filtered_df['population'].sum()):,}"
avg_age = f"{filtered_df['min_age'].mean():.1f}"
unique_locations = len(filtered_df['asylum_location_code'].unique())
gender_ratio = f"{filtered_df[filtered_df['gender']=='Male']['population'].sum() / filtered_df['population'].sum():.1%}"

with col1:
    st.markdown("""
    <div class="kpi-card">
        <h3>Total Returnees</h3>
        <h2 style="color:#2563EB; margin:0;">{}</h2>
    </div>
    """.format(total_returnees), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <h3>Average Age</h3>
        <h2 style="color:#2563EB; margin:0;">{}</h2>
    </div>
    """.format(avg_age), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card">
        <h3>Unique Locations</h3>
        <h2 style="color:#2563EB; margin:0;">{}</h2>
    </div>
    """.format(unique_locations), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="kpi-card">
        <h3>Male Ratio</h3>
        <h2 style="color:#2563EB; margin:0;">{}</h2>
    </div>
    """.format(gender_ratio), unsafe_allow_html=True)

# Create tabs for different view sections
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "👥 Demographics", "🌍 Geographic", "📋 Data"])

# Tab 1: Trends Over Time
with tab1:
    st.markdown('<h2 class="sub-header">Returnee Trends Over Time</h2>', unsafe_allow_html=True)
    
    # Time aggregation options
    time_agg = st.radio("Time Aggregation:", ["Yearly", "Quarterly", "Monthly"], horizontal=True)
    
    if time_agg == "Yearly":
        time_col = 'year'
        time_format = '%Y'
    elif time_agg == "Quarterly":
        time_col = ['year', 'quarter']
        time_format = 'Q%q %Y'
    else:
        time_col = ['year', 'month']
        time_format = '%b %Y'
    
    # Create time series data
    if isinstance(time_col, list):
        # For quarterly/monthly data
        time_series = filtered_df.groupby(time_col)['population'].sum().reset_index()
        if time_agg == "Quarterly":
            time_series['period'] = time_series.apply(lambda x: f"Q{x['quarter']} {x['year']}", axis=1)
        else:
            time_series['period'] = time_series.apply(lambda x: datetime(int(x['year']), int(x['month']), 1).strftime('%b %Y'), axis=1)
        x_col = 'period'
    else:
        # For yearly data
        time_series = filtered_df.groupby(time_col)['population'].sum().reset_index()
        x_col = time_col
    
    # Time series chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_time = px.line(
            time_series, 
            x=x_col, 
            y='population',
            markers=True,
            title=f"Returnee Population Over Time ({time_agg})",
            labels={'population': 'Number of Returnees'},
            template="plotly_white"
        )
        fig_time.update_layout(
            xaxis_title="Time Period",
            yaxis_title="Population Count",
            height=400,
            hovermode="x unified"
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        # Summary stats for trend
        if len(time_series) > 1:
            max_period = time_series.loc[time_series['population'].idxmax()]
            min_period = time_series.loc[time_series['population'].idxmin()]
            
            # Calculate trend
            if len(time_series) >= 2:
                latest = time_series.iloc[-1]['population']
                previous = time_series.iloc[-2]['population']
                pct_change = (latest - previous) / previous if previous != 0 else 0
                
                st.markdown("""
                <div class="insight-card">
                    <h3>Trend Analysis</h3>
                    <p>Peak returnees: <b>{:,}</b> in {}</p>
                    <p>Lowest returnees: <b>{:,}</b> in {}</p>
                    <p>Latest period trend: <b>{:+.1%}</b></p>
                </div>
                """.format(
                    int(max_period['population']),
                    max_period[x_col],
                    int(min_period['population']),
                    min_period[x_col],
                    pct_change
                ), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-card">
                    <h3>Trend Analysis</h3>
                    <p>Only one time period available in selected data.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Not enough time periods to show trend analysis.")
    
    # Cumulative trend
    st.markdown("#### Cumulative Returnees Over Time")
    time_series['cumulative'] = time_series['population'].cumsum()
    
    fig_cumulative = px.area(
        time_series,
        x=x_col,
        y='cumulative',
        title="Cumulative Returnee Count",
        labels={'cumulative': 'Cumulative Returnees'},
        template="plotly_white"
    )
    fig_cumulative.update_layout(height=300)
    st.plotly_chart(fig_cumulative, use_container_width=True)

# Tab 2: Demographics
with tab2:
    st.markdown('<h2 class="sub-header">Demographic Analysis</h2>', unsafe_allow_html=True)
    
    # Row 1: Gender and Age distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender breakdown pie chart
        gender_data = filtered_df.groupby('gender')['population'].sum().reset_index()
        
        fig_gender = px.pie(
            gender_data, 
            values='population', 
            names='gender',
            title="Gender Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_gender.update_layout(height=350)
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with col2:
        # Age group breakdown
        age_data = filtered_df.groupby('age_group')['population'].sum().reset_index()
        age_data = age_data.sort_values('age_group')
        
        fig_age = px.bar(
            age_data,
            x='age_group',
            y='population',
            title="Age Group Distribution",
            color='age_group',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_age.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Population Count",
            height=350,
            xaxis={'categoryorder':'array', 'categoryarray':labels}
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Row 2: Population Pyramid and Group Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Population pyramid
        st.markdown("#### Population Pyramid (by Gender & Age)")
        
        # Create pyramid data
        pyramid_df = filtered_df.groupby(['gender', 'age_group'])['population'].sum().reset_index()
        
        # Sort age groups in correct order
        pyramid_df['age_sort'] = pyramid_df['age_group'].map({labels[i]: i for i in range(len(labels))})
        pyramid_df = pyramid_df.sort_values('age_sort')
        
        males = pyramid_df[pyramid_df['gender'] == 'Male']
        females = pyramid_df[pyramid_df['gender'] == 'Female']
        
        # Create pyramid chart
        fig_pyramid = go.Figure()
        
        fig_pyramid.add_trace(go.Bar(
            y=males['age_group'],
            x=-males['population'],
            name='Male',
            orientation='h',
            marker=dict(color='lightblue')
        ))
        
        fig_pyramid.add_trace(go.Bar(
            y=females['age_group'],
            x=females['population'],
            name='Female',
            orientation='h',
            marker=dict(color='pink')
        ))
        
        fig_pyramid.update_layout(
            title="Population Pyramid by Age Group",
            barmode='overlay',
            bargap=0.1,
            xaxis=dict(
                title="Population",
                tickvals=[-30000, -20000, -10000, 0, 10000, 20000, 30000],
                ticktext=['30K', '20K', '10K', '0', '10K', '20K', '30K']
            ),
            yaxis=dict(
                title="Age Group",
                categoryorder='array',
                categoryarray=labels
            ),
            height=400
        )
        
        st.plotly_chart(fig_pyramid, use_container_width=True)
    
    with col2:
        # Top population groups
        st.markdown("#### Population Groups")
        
        pop_groups = filtered_df.groupby('population_group')['population'].sum().reset_index()
        pop_groups = pop_groups.sort_values('population', ascending=False).head(10)
        
        fig_groups = px.bar(
            pop_groups,
            x='population',
            y='population_group',
            title="Top Population Groups",
            orientation='h',
            color='population',
            color_continuous_scale='Blues'
        )
        
        fig_groups.update_layout(
            xaxis_title="Population Count",
            yaxis_title="Population Group",
            height=400,
            yaxis={'categoryorder':'total ascending'}
        )
        
        st.plotly_chart(fig_groups, use_container_width=True)
    
    # Heatmap: Gender vs Age
    st.markdown("#### Demographics Heatmap")
    
    pivot_data = filtered_df.pivot_table(
        values='population', 
        index='gender', 
        columns='age_group', 
        aggfunc='sum'
    ).fillna(0)
    
    # Ensure columns are in correct age order
    if len(pivot_data.columns) > 0:
        ordered_cols = [col for col in labels if col in pivot_data.columns]
        pivot_data = pivot_data[ordered_cols]
    
    fig_heat = px.imshow(
        pivot_data,
        labels=dict(x="Age Group", y="Gender", color="Population"),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale="Viridis",
        title="Gender & Age Group Heatmap"
    )
    
    fig_heat.update_layout(height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

# Tab 3: Geographic Analysis
with tab3:
    st.markdown('<h2 class="sub-header">Geographic Analysis</h2>', unsafe_allow_html=True)
    
    # Get top locations
    location_data = filtered_df.groupby('asylum_location_code')['population'].sum().reset_index()
    location_data = location_data.sort_values('population', ascending=False)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Top locations bar chart
        fig_locations = px.bar(
            location_data.head(10),
            x='asylum_location_code',
            y='population',
            title="Top 10 Asylum Locations",
            color='population',
            color_continuous_scale='Greens'
        )
        
        fig_locations.update_layout(
            xaxis_title="Location Code",
            yaxis_title="Population Count",
            height=400
        )
        
        st.plotly_chart(fig_locations, use_container_width=True)
    
    with col2:
        # Location stats
        st.markdown("""
        <div class="insight-card">
            <h3>Location Insights</h3>
            <p>Total locations: <b>{}</b></p>
            <p>Top location: <b>{}</b> with <b>{:,}</b> returnees</p>
            <p>Location concentration: <b>{:.1%}</b> in top 3 locations</p>
        </div>
        """.format(
            len(location_data),
            location_data.iloc[0]['asylum_location_code'] if len(location_data) > 0 else "N/A",
            int(location_data.iloc[0]['population']) if len(location_data) > 0 else 0,
            location_data.head(3)['population'].sum() / location_data['population'].sum() if len(location_data) > 0 else 0
        ), unsafe_allow_html=True)
        
        # Top destination - origin pairs
        if 'origin_location_code' in filtered_df.columns:
            st.markdown("#### Top Origin-Destination Pairs")
            
            flow_data = filtered_df.groupby(['origin_location_code', 'asylum_location_code'])['population'].sum().reset_index()
            flow_data = flow_data.sort_values('population', ascending=False).head(5)
            
            st.dataframe(
                flow_data.rename(columns={
                    'origin_location_code': 'Origin',
                    'asylum_location_code': 'Destination',
                    'population': 'Population'
                }),
                hide_index=True
            )
    
    # Location time analysis
    st.markdown("#### Location Trends Over Time")
    
    # Get top 5 locations for time analysis
    top_locations = location_data.head(5)['asylum_location_code'].tolist()
    
    # Create location time series
    loc_time_df = filtered_df[filtered_df['asylum_location_code'].isin(top_locations)]
    
    if not loc_time_df.empty:
        loc_time_series = loc_time_df.groupby(['year', 'asylum_location_code'])['population'].sum().reset_index()
        
        fig_loc_time = px.line(
            loc_time_series,
            x='year',
            y='population',
            color='asylum_location_code',
            title="Returnee Trends by Top Locations",
            markers=True,
            line_shape='spline'
        )
        
        fig_loc_time.update_layout(
            xaxis_title="Year",
            yaxis_title="Population Count",
            height=400,
            legend_title="Location Code"
        )
        
        st.plotly_chart(fig_loc_time, use_container_width=True)
    else:
        st.info("No location trend data available for the selected filters.")

# Tab 4: Data Table
with tab4:
    st.markdown('<h2 class="sub-header">Raw Data & Download</h2>', unsafe_allow_html=True)
    
    # Column selection
    all_columns = filtered_df.columns.tolist()
    default_columns = ['asylum_location_code', 'gender', 'age_group', 'population_group', 'year', 'population']
    
    selected_columns = st.multiselect(
        "Select Columns to Display", 
        options=all_columns,
        default=default_columns
    )
    
    if not selected_columns:
        selected_columns = default_columns
    
    # Show data table
    st.dataframe(
        filtered_df[selected_columns].sort_values('population', ascending=False),
        height=400,
        use_container_width=True
    )
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        # Download options
        st.markdown("#### Download Data")
        
        file_format = st.radio("Select Format:", ["CSV", "Excel", "JSON"], horizontal=True)
        
        if file_format == "CSV":
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name="sri_lanka_returnees.csv",
                mime="text/csv"
            )
        elif file_format == "Excel":
            # Using a buffer for Excel
            st.download_button(
                "⬇️ Download Excel",
                data=filtered_df.to_excel(index=False).getvalue() if hasattr(filtered_df.to_excel(index=False), 'getvalue') else filtered_df.to_csv(index=False),
                file_name="sri_lanka_returnees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            json_data = filtered_df.to_json(orient="records")
            st.download_button(
                "⬇️ Download JSON",
                data=json_data,
                file_name="sri_lanka_returnees.json",
                mime="application/json"
            )
    
    with col2:
        # Data summary
        st.markdown("#### Data Summary")
        
        # Show summary stats
        numeric_df = filtered_df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            summary_df = numeric_df.describe().T
            st.dataframe(summary_df.style.format("{:.2f}"), height=300)

# Footer with smart insights
st.markdown('<h2 class="sub-header">💡 Smart Insights</h2>', unsafe_allow_html=True)

# Generate insights based on data
insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    # Time-based insights
    time_data = filtered_df.groupby('year')['population'].sum().reset_index()
    
    if len(time_data) > 1:
        peak_year = time_data.loc[time_data['population'].idxmax(), 'year']
        trend_direction = "increasing" if time_data.iloc[-1]['population'] > time_data.iloc[-2]['population'] else "decreasing"
        
        st.markdown("""
        <div class="insight-card">
            <h3>📈 Temporal Patterns</h3>
            <p>• Peak returnee year was <b>{}</b> with <b>{:,}</b> returnees</p>
            <p>• Recent trend shows <b>{}</b> returnee numbers</p>
            <p>• Variance between years: <b>{:.1%}</b> (max vs min)</p>
        </div>
        """.format(
            peak_year,
            int(time_data.loc[time_data['population'].idxmax(), 'population']),
            trend_direction,
            (time_data['population'].max() - time_data['population'].min()) / time_data['population'].min() if time_data['population'].min() > 0 else 0
        ), unsafe_allow_html=True)
    
    # Demographic insights
    gender_ratio = filtered_df[filtered_df['gender']=='Male']['population'].sum() / filtered_df['population'].sum()
    children_pct = filtered_df[filtered_df['min_age'] < 18]['population'].sum() / filtered_df['population'].sum()
    
    st.markdown("""
    <div class="insight-card">
        <h3>👨‍👩‍👧‍👦 Demographic Patterns</h3>
        <p>• Gender ratio: <b>{:.1%}</b> male, <b>{:.1%}</b> female</p>
        <p>• Children (<18): <b>{:.1%}</b> of total returnees</p>
        <p>• Most common age group: <b>{}</b></p>
    </div>
    """.format(
        gender_ratio,
        1 - gender_ratio,
        children_pct,
        filtered_df.groupby('age_group')['population'].sum().idxmax() if 'age_group' in filtered_df.columns else "N/A"
    ), unsafe_allow_html=True)

with insights_col2:
    # Geographic insights
    if 'asylum_location_code' in filtered_df.columns:
        top_location = filtered_df.groupby('asylum_location_code')['population'].sum().idxmax()
        location_count = len(filtered_df['asylum_location_code'].unique())
        
        st.markdown("""
        <div class="insight-card">
            <h3>🌏 Geographic Patterns</h3>
            <p>• Most common destination: <b>{}</b></p>
            <p>• Total unique locations: <b>{}</b></p>
            <p>• Top 3 locations account for <b>{:.1%}</b> of all returnees</p>
        </div>
        """.format(
            top_location,
            location_count,
            filtered_df[filtered_df['asylum_location_code'].isin(filtered_df.groupby('asylum_location_code')['population'].sum().nlargest(3).index)]['population'].sum() / filtered_df['population'].sum()
        ), unsafe_allow_html=True)
    
    # Population group insights
    if 'population_group' in filtered_df.columns:
        top_group = filtered_df.groupby('population_group')['population'].sum().idxmax()
        group_count = len(filtered_df['population_group'].unique())
        
        st.markdown("""
        <div class="insight-card">
            <h3>👥 Population Group Insights</h3>
            <p>• Most common group: <b>{}</b></p>
            <p>• Total unique groups: <b>{}</b></p>
            <p>• Top group accounts for <b>{:.1%}</b> of all returnees</p>
        </div>
        """.format(
            top_group,
            group_count,
            filtered_df[filtered_df['population_group'] == top_group]['population'].sum() / filtered_df['population'].sum()
        ), unsafe_allow_html=True)

# Add recommendation section
st.markdown('<h2 class="sub-header">🎯 Recommendations</h2>', unsafe_allow_html=True)

# Generate recommendations based on data
recs_col1, recs_col2 = st.columns(2)

with recs_col1:
    st.markdown("""
    <div class="insight-card">
        <h3>Program Recommendations</h3>
        <p>• <b>Focus on top destinations:</b> Concentrate resources on {}, which accounts for the highest returnee population.</p>
        <p>• <b>Age-specific programs:</b> Develop targeted support for {} age group, which represents the largest demographic segment.</p>
        <p>• <b>Family support:</b> Create programs addressing family reunification and stability needs.</p>
    </div>
    """.format(
        filtered_df.groupby('asylum_location_code')['population'].sum().idxmax() if 'asylum_location_code' in filtered_df.columns else "main destinations",
        filtered_df.groupby('age_group')['population'].sum().idxmax() if 'age_group' in filtered_df.columns else "key age groups"
    ), unsafe_allow_html=True)

with recs_col2:
    st.markdown("""
    <div class="insight-card">
        <h3>Monitoring Recommendations</h3>
        <p>• <b>Track seasonal trends:</b> Monitor quarterly patterns to better predict and prepare for returnee flows.</p>
        <p>• <b>Demographic shifts:</b> Watch for changes in gender and age composition that may indicate evolving needs.</p>
        <p>• <b>Geographic focus:</b> Maintain special attention on emerging destination patterns to allocate resources effectively.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer with credits and metadata
st.markdown("""
<div class="footer">
    <p>Sri Lanka Returnees Dashboard | Data Source: HDX HAPI Returnees Dataset | Last updated: {}</p>
    <p>Dashboard Version 2.0 | Created with Streamlit, Pandas, and Plotly</p>
</div>
""".format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)


