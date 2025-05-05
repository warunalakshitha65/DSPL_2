import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="Refugee Population Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #2563EB;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .stat-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        margin-bottom: 20px;
    }
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .stat-label {
        font-size: 14px;
        color: #6B7280;
    }
    .insights-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>Refugee & Population Data Dashboard</div>", unsafe_allow_html=True)

# Allow users to upload a CSV file or use sample data
st.markdown("<div class='section-header'>Data Input</div>", unsafe_allow_html=True)

upload_option = st.radio(
    "Choose data source:",
    ["Upload CSV file", "Use sample data"]
)

@st.cache_data
def load_sample_data():
    # Create sample data similar to what was provided
    data = {
        'origin_location_code': ['AFG', 'AFG', 'AFG', 'SYR', 'SYR', 'SYR', 'SOM', 'SOM'],
        'origin_has_hrp': [True, True, True, True, True, True, False, False],
        'origin_in_gho': [True, True, True, True, True, True, False, False],
        'asylum_location_code': ['LKA', 'PAK', 'IRN', 'TUR', 'LBN', 'JOR', 'KEN', 'ETH'],
        'asylum_has_hrp': [False, True, False, False, True, True, True, True],
        'asylum_in_gho': [False, True, False, False, True, True, True, True],
        'population_group': ['RET', 'REF', 'REF', 'REF', 'REF', 'REF', 'REF', 'REF'],
        'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm'],
        'age_range': ['0-4', '5-11', '12-17', '18-59', '60+', 'all', '0-4', '18-59'],
        'min_age': [0, 5, 12, 18, 60, None, 0, 18],
        'max_age': [4, 11, 17, 59, None, None, 4, 59],
        'population': [10, 50, 35, 100, 40, 500, 25, 75],
        'reference_period_start': ['1/1/2022', '1/1/2022', '1/1/2022', '1/1/2022', '1/1/2022', '1/1/2022', '1/1/2022', '1/1/2022'],
        'reference_period_end': ['12/31/2022', '12/31/2022', '12/31/2022', '12/31/2022', '12/31/2022', '12/31/2022', '12/31/2022', '12/31/2022']
    }
    return pd.DataFrame(data)

if upload_option == "Upload CSV file":
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    if uploaded_file is not None:
        try:
            # Try different encodings if necessary
            df = pd.read_csv(uploaded_file)
            st.success("File successfully loaded!")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
    else:
        st.info("Please upload a CSV file to continue")
        st.stop()
else:
    df = load_sample_data()
    st.info("Using sample data for demonstration")

# Display the raw data with an expander
with st.expander("View Raw Data"):
    st.dataframe(df)

# Data preprocessing
df_processed = df.copy()

# Convert date columns to datetime if they're not already
try:
    df_processed['reference_period_start'] = pd.to_datetime(df_processed['reference_period_start'])
    df_processed['reference_period_end'] = pd.to_datetime(df_processed['reference_period_end'])
except Exception as e:
    st.warning(f"Could not convert date columns to datetime format: {e}")

# Handle None values in age columns
df_processed['min_age'] = pd.to_numeric(df_processed['min_age'], errors='coerce')
df_processed['max_age'] = pd.to_numeric(df_processed['max_age'], errors='coerce')

# Main dashboard layout
st.markdown("<div class='section-header'>Dashboard Overview</div>", unsafe_allow_html=True)

# Create sidebar for filters
st.sidebar.title("Filters")

# Select time period if dates are available
try:
    min_date = df_processed['reference_period_start'].min().date()
    max_date = df_processed['reference_period_end'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df_processed['reference_period_start'].dt.date >= start_date) & (df_processed['reference_period_end'].dt.date <= end_date)
        df_filtered = df_processed[mask]
    else:
        df_filtered = df_processed
except Exception as e:
    st.sidebar.warning("Could not apply date filtering")
    df_filtered = df_processed

# Country filters
origin_countries = st.sidebar.multiselect(
    "Origin Countries",
    options=sorted(df_filtered['origin_location_code'].unique()),
    default=sorted(df_filtered['origin_location_code'].unique())[:3] if len(df_filtered['origin_location_code'].unique()) > 3 else sorted(df_filtered['origin_location_code'].unique())
)

asylum_countries = st.sidebar.multiselect(
    "Asylum Countries",
    options=sorted(df_filtered['asylum_location_code'].unique()),
    default=sorted(df_filtered['asylum_location_code'].unique())[:3] if len(df_filtered['asylum_location_code'].unique()) > 3 else sorted(df_filtered['asylum_location_code'].unique())
)

# Population group filter
population_groups = st.sidebar.multiselect(
    "Population Groups",
    options=sorted(df_filtered['population_group'].unique()),
    default=sorted(df_filtered['population_group'].unique())
)

# Gender filter
genders = st.sidebar.multiselect(
    "Gender",
    options=sorted(df_filtered['gender'].unique()),
    default=sorted(df_filtered['gender'].unique())
)

# Age range filter
age_ranges = st.sidebar.multiselect(
    "Age Ranges",
    options=sorted(df_filtered['age_range'].unique()),
    default=sorted(df_filtered['age_range'].unique())
)

# Apply filters
if origin_countries:
    df_filtered = df_filtered[df_filtered['origin_location_code'].isin(origin_countries)]
if asylum_countries:
    df_filtered = df_filtered[df_filtered['asylum_location_code'].isin(asylum_countries)]
if population_groups:
    df_filtered = df_filtered[df_filtered['population_group'].isin(population_groups)]
if genders:
    df_filtered = df_filtered[df_filtered['gender'].isin(genders)]
if age_ranges:
    df_filtered = df_filtered[df_filtered['age_range'].isin(age_ranges)]

# Check if we have data after filtering
if df_filtered.empty:
    st.warning("No data available with the selected filters. Please adjust your filters.")
    st.stop()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-number'>{df_filtered['population'].sum():,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='stat-label'>Total Population</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-number'>{len(df_filtered['origin_location_code'].unique()):,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='stat-label'>Origin Countries</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-number'>{len(df_filtered['asylum_location_code'].unique()):,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='stat-label'>Asylum Countries</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-number'>{len(df_filtered['population_group'].unique()):,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='stat-label'>Population Groups</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Population Overview", "Demographics", "Geographic Analysis", "Trends"])

with tab1:
    st.markdown("<div class='section-header'>Population Overview</div>", unsafe_allow_html=True)
    
    # Population by population group
    pop_by_group = df_filtered.groupby('population_group')['population'].sum().reset_index()
    
    fig1 = px.bar(
        pop_by_group,
        x='population_group',
        y='population',
        title='Population by Group',
        labels={'population_group': 'Population Group', 'population': 'Population'},
        color='population_group',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Population by gender
    if 'gender' in df_filtered.columns and not df_filtered['gender'].isna().all():
        pop_by_gender = df_filtered.groupby('gender')['population'].sum().reset_index()
        
        fig2 = px.pie(
            pop_by_gender,
            values='population',
            names='gender',
            title='Population by Gender',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("<div class='section-header'>Demographic Analysis</div>", unsafe_allow_html=True)
    
    # Age breakdown
    if 'age_range' in df_filtered.columns and not df_filtered['age_range'].isna().all():
        # Create a custom sort order for age ranges to display them in logical order
        age_order = ['0-4', '5-11', '12-17', '18-59', '60+', 'all']
        
        # Filter out the 'all' category for age-specific analysis
        df_age = df_filtered[df_filtered['age_range'] != 'all']
        
        if not df_age.empty:
            # Create a categorical type with ordered categories
            df_age['age_range'] = pd.Categorical(
                df_age['age_range'],
                categories=[cat for cat in age_order if cat in df_age['age_range'].unique()],
                ordered=True
            )
            
            # Sort by the new categorical column
            pop_by_age = df_age.sort_values('age_range').groupby(['age_range', 'gender'])['population'].sum().reset_index()
            
            # Create age pyramid
            fig3 = px.bar(
                pop_by_age,
                x='population',
                y='age_range',
                color='gender',
                orientation='h',
                title='Population by Age and Gender',
                barmode='group',
                color_discrete_map={'m': '#0068C9', 'f': '#FF5A5F'},
                labels={'population': 'Population', 'age_range': 'Age Range', 'gender': 'Gender'},
                category_orders={'age_range': [cat for cat in age_order if cat in df_age['age_range'].unique()]}
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    # Cross-tabulation of demographic data
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Heatmap of population by age range and population group
        if ('age_range' in df_filtered.columns and not df_filtered['age_range'].isna().all() and
            'population_group' in df_filtered.columns and not df_filtered['population_group'].isna().all()):
            # Filter out 'all' age range for specific analysis
            df_heat = df_filtered[df_filtered['age_range'] != 'all']
            if not df_heat.empty:
                heat_data = df_heat.pivot_table(
                    values='population',
                    index='age_range',
                    columns='population_group',
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Try to order the age ranges if possible
                try:
                    heat_data = heat_data.reindex([cat for cat in age_order if cat in heat_data.index])
                except Exception:
                    pass
                
                fig4 = px.imshow(
                    heat_data,
                    title='Population by Age Range and Group',
                    labels=dict(x='Population Group', y='Age Range', color='Population'),
                    color_continuous_scale='Blues',
                    text_auto=True
                )
                fig4.update_layout(xaxis={'side': 'top'})
                st.plotly_chart(fig4, use_container_width=True)
    
    with col_right:
        # Population composition by gender and population group
        if ('gender' in df_filtered.columns and not df_filtered['gender'].isna().all() and
            'population_group' in df_filtered.columns and not df_filtered['population_group'].isna().all()):
            pop_composition = df_filtered.pivot_table(
                values='population',
                index='gender',
                columns='population_group',
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            # Melt the dataframe for easier plotting
            pop_composition_melted = pd.melt(
                pop_composition,
                id_vars=['gender'],
                value_vars=[col for col in pop_composition.columns if col != 'gender'],
                var_name='Population Group',
                value_name='Population'
            )
            
            fig5 = px.bar(
                pop_composition_melted,
                x='gender',
                y='Population',
                color='Population Group',
                title='Population by Gender and Group',
                labels={'gender': 'Gender', 'Population': 'Population', 'Population Group': 'Population Group'},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.markdown("<div class='section-header'>Geographic Analysis</div>", unsafe_allow_html=True)
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        # Top origin countries
        origin_counts = df_filtered.groupby('origin_location_code')['population'].sum().reset_index()
        origin_counts = origin_counts.sort_values('population', ascending=False).head(10)
        
        fig6 = px.bar(
            origin_counts,
            x='origin_location_code',
            y='population',
            title='Top Origin Countries',
            labels={'origin_location_code': 'Country Code', 'population': 'Population'},
            color='population',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    with col_geo2:
        # Top asylum countries
        asylum_counts = df_filtered.groupby('asylum_location_code')['population'].sum().reset_index()
        asylum_counts = asylum_counts.sort_values('population', ascending=False).head(10)
        
        fig7 = px.bar(
            asylum_counts,
            x='asylum_location_code',
            y='population',
            title='Top Asylum Countries',
            labels={'asylum_location_code': 'Country Code', 'population': 'Population'},
            color='population',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    # Migration flow analysis
    migration_flows = df_filtered.groupby(['origin_location_code', 'asylum_location_code'])['population'].sum().reset_index()
    migration_flows = migration_flows.sort_values('population', ascending=False).head(15)
    
    fig8 = px.bar(
        migration_flows,
        x='origin_location_code',
        y='population',
        color='asylum_location_code',
        title='Top Migration Flows',
        labels={
            'origin_location_code': 'Origin Country',
            'asylum_location_code': 'Asylum Country',
            'population': 'Population'
        },
        barmode='group'
    )
    st.plotly_chart(fig8, use_container_width=True)
    
    # Humanitarian Response Plan (HRP) analysis
    if 'origin_has_hrp' in df_filtered.columns and 'asylum_has_hrp' in df_filtered.columns:
        col_hrp1, col_hrp2 = st.columns(2)
        
        with col_hrp1:
            # Origin countries with HRP
            origin_hrp = df_filtered.groupby('origin_has_hrp')['population'].sum().reset_index()
            
            fig9 = px.pie(
                origin_hrp,
                values='population',
                names='origin_has_hrp',
                title='Population from Countries with HRP vs Non-HRP',
                hole=0.4,
                color_discrete_sequence=['#1E88E5', '#D81B60']
            )
            st.plotly_chart(fig9, use_container_width=True)
        
        with col_hrp2:
            # Asylum countries with HRP
            asylum_hrp = df_filtered.groupby('asylum_has_hrp')['population'].sum().reset_index()
            
            fig10 = px.pie(
                asylum_hrp,
                values='population',
                names='asylum_has_hrp',
                title='Population in Asylum Countries with HRP vs Non-HRP',
                hole=0.4,
                color_discrete_sequence=['#1E88E5', '#D81B60']
            )
            st.plotly_chart(fig10, use_container_width=True)

with tab4:
    st.markdown("<div class='section-header'>Trends & Patterns</div>", unsafe_allow_html=True)
    
    # Try to analyze time-based trends if dates are available and parseable
    try:
        if 'reference_period_start' in df_filtered.columns and pd.api.types.is_datetime64_any_dtype(df_filtered['reference_period_start']):
            # Extract year and month for trend analysis
            df_filtered['year'] = df_filtered['reference_period_start'].dt.year
            df_filtered['month'] = df_filtered['reference_period_start'].dt.month
            
            # Population trend by year (if multiple years are available)
            years = sorted(df_filtered['year'].unique())
            if len(years) > 1:
                pop_by_year = df_filtered.groupby(['year', 'population_group'])['population'].sum().reset_index()
                
                fig11 = px.line(
                    pop_by_year,
                    x='year',
                    y='population',
                    color='population_group',
                    title='Population Trend by Year and Group',
                    labels={'year': 'Year', 'population': 'Population', 'population_group': 'Population Group'},
                    markers=True
                )
                st.plotly_chart(fig11, use_container_width=True)
            else:
                st.info("Multiple years of data not available for trend analysis")
            
            # Distribution analysis
            col_dist1, col_dist2 = st.columns(2)
            
            with col_dist1:
                # Distribution of population by age range
                if 'age_range' in df_filtered.columns and not df_filtered['age_range'].isna().all():
                    df_age_dist = df_filtered[df_filtered['age_range'] != 'all']
                    if not df_age_dist.empty:
                        # Try to create an ordered categorical for age ranges
                        try:
                            df_age_dist['age_range'] = pd.Categorical(
                                df_age_dist['age_range'],
                                categories=[cat for cat in age_order if cat in df_age_dist['age_range'].unique()],
                                ordered=True
                            )
                            age_dist = df_age_dist.sort_values('age_range').groupby('age_range')['population'].sum().reset_index()
                        except Exception:
                            age_dist = df_age_dist.groupby('age_range')['population'].sum().reset_index()
                        
                        fig12 = px.bar(
                            age_dist,
                            x='age_range',
                            y='population',
                            title='Population Distribution by Age Range',
                            labels={'age_range': 'Age Range', 'population': 'Population'},
                            color='population',
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig12, use_container_width=True)
            
            with col_dist2:
                # Gender ratio analysis by population group
                if 'gender' in df_filtered.columns and 'population_group' in df_filtered.columns:
                    gender_ratio = df_filtered.pivot_table(
                        values='population',
                        index='population_group', 
                        columns='gender',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Calculate ratio if both genders are present
                    if 'm' in gender_ratio.columns and 'f' in gender_ratio.columns:
                        gender_ratio['ratio_m_f'] = gender_ratio['m'] / gender_ratio['f']
                        gender_ratio['ratio_m_f'] = gender_ratio['ratio_m_f'].replace([np.inf, -np.inf], np.nan)
                        
                        fig13 = px.bar(
                            gender_ratio,
                            x='population_group',
                            y='ratio_m_f',
                            title='Male to Female Ratio by Population Group',
                            labels={
                                'population_group': 'Population Group',
                                'ratio_m_f': 'Male/Female Ratio'
                            },
                            color='ratio_m_f',
                            color_continuous_scale='RdBu',
                            color_continuous_midpoint=1
                        )
                        fig13.add_hline(y=1, line_dash="dash", line_color="black")
                        st.plotly_chart(fig13, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate time-based trends: {e}")

# Additional insights section
st.markdown("<div class='section-header'>Key Insights</div>", unsafe_allow_html=True)

# Generate some insights based on the data
st.markdown("<div class='insights-box'>", unsafe_allow_html=True)

total_population = df_filtered['population'].sum()

if total_population > 0:
    # Most common population group
    top_group = df_filtered.groupby('population_group')['population'].sum().sort_values(ascending=False).index[0]
    top_group_percentage = (df_filtered[df_filtered['population_group'] == top_group]['population'].sum() / total_population) * 100
    
    st.markdown(f"• The most common population group is **{top_group}**, representing **{top_group_percentage:.1f}%** of the total population.")
    
    # Top origin and asylum countries
    top_origin = df_filtered.groupby('origin_location_code')['population'].sum().sort_values(ascending=False).index[0]
    top_origin_percentage = (df_filtered[df_filtered['origin_location_code'] == top_origin]['population'].sum() / total_population) * 100
    
    top_asylum = df_filtered.groupby('asylum_location_code')['population'].sum().sort_values(ascending=False).index[0]
    top_asylum_percentage = (df_filtered[df_filtered['asylum_location_code'] == top_asylum]['population'].sum() / total_population) * 100
    
    st.markdown(f"• The top origin country is **{top_origin}**, accounting for **{top_origin_percentage:.1f}%** of the population.")
    st.markdown(f"• The top asylum country is **{top_asylum}**, hosting **{top_asylum_percentage:.1f}%** of the population.")
    
    # Gender distribution if available
    if 'gender' in df_filtered.columns and not df_filtered['gender'].isna().all():
        gender_counts = df_filtered.groupby('gender')['population'].sum()
        if 'm' in gender_counts and 'f' in gender_counts:
            male_percentage = (gender_counts['m'] / total_population) * 100
            female_percentage = (gender_counts['f'] / total_population) * 100
            
            st.markdown(f"• Gender distribution: **{male_percentage:.1f}%** male and **{female_percentage:.1f}%** female.")
            
            if male_percentage > female_percentage:
                st.markdown(f"• There are more males than females with a ratio of **{male_percentage/female_percentage:.2f}**.")
            elif female_percentage > male_percentage:
                st.markdown(f"• There are more females than males with a ratio of **{female_percentage/male_percentage:.2f}**.")
    
    # Age distribution insights if available
    if 'age_range' in df_filtered.columns and not df_filtered['age_range'].isna().all():
        df_age_insight = df_filtered[df_filtered['age_range'] != 'all']
        if not df_age_insight.empty:
            age_dist = df_age_insight.groupby('age_range')['population'].sum()
            
            # Check for children (0-17)
            children_ranges = [range_name for range_name in age_dist.index if any(r in range_name for r in ['0-4', '5-11', '12-17'])]
            children_population = sum(age_dist[range_name] for range_name in children_ranges if range_name in age_dist.index)
            children_percentage = (children_population / total_population) * 100
            
            # Check for working age (18-59)
            working_age_ranges = [range_name for range_name in age_dist.index if '18-59' in range_name]
            working_age_population = sum(age_dist[range_name] for range_name in working_age_ranges if range_name in age_dist.index)
            working_age_percentage = (working_age_population / total_population) * 100
            
            # Check for elderly (60+)
            elderly_ranges = [range_name for range_name in age_dist.index if '60+' in range_name]
            elderly_population = sum(age_dist[range_name] for range_name in elderly_ranges if range_name in age_dist.index)
            elderly_percentage = (elderly_population / total_population) * 100
            
            if children_percentage > 0:
                st.markdown(f"• Children (0-17) represent **{children_percentage:.1f}%** of the total population.")
            
            if working_age_percentage > 0:
                st.markdown(f"• Working age population (18-59) represents **{working_age_percentage:.1f}%** of the total population.")
            
            if elderly_percentage > 0:
                st.markdown(f"• Elderly population (60+) represents **{elderly_percentage:.1f}%** of the total population.")
    
    # HRP insights if available
    if 'origin_has_hrp' in df_filtered.columns:
        hrp_origin_population = df_filtered[df_filtered['origin_has_hrp'] == True]['population'].sum()
        hrp_origin_percentage = (hrp_origin_population / total_population) * 100
        
        if hrp_origin_percentage > 0:
            st.markdown(f"• **{hrp_origin_percentage:.1f}%** of the population comes from countries with Humanitarian Response Plans.")
    
    if 'asylum_has_hrp' in df_filtered.columns:
        hrp_asylum_population = df_filtered[df_filtered['asylum_has_hrp'] == True]['population'].sum()
        hrp_asylum_percentage = (hrp_asylum_population / total_population) * 100
        
        if hrp_asylum_percentage > 0:
            st.markdown(f"• **{hrp_asylum_percentage:.1f}%** of the population is hosted in countries with Humanitarian Response Plans.")

st.markdown("</div>", unsafe_allow_html=True)

# Export functionality
st.markdown("<div class='section-header'>Export Data</div>", unsafe_allow_html=True)

export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("Export Filtered Data to CSV"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="refugee_population_filtered_data.csv",
            mime="text/csv"
        )

with export_col2:
    if st.button("Export Summary Statistics"):
        # Create a summary dataframe
        summary_stats = pd.DataFrame()
        
        # Population by group
        pop_by_group = df_filtered.groupby('population_group')['population'].sum().reset_index()
        pop_by_group.columns = ['Population Group', 'Total Population']
        
        # Population by gender
        pop_by_gender = df_filtered.groupby('gender')['population'].sum().reset_index()
        pop_by_gender.columns = ['Gender', 'Total Population']
        
        # Population by origin country
        pop_by_origin = df_filtered.groupby('origin_location_code')['population'].sum().reset_index()
        pop_by_origin.columns = ['Origin Country', 'Total Population']
        pop_by_origin = pop_by_origin.sort_values('Total Population', ascending=False)
        
        # Population by asylum country
        pop_by_asylum = df_filtered.groupby('asylum_location_code')['population'].sum().reset_index()
        pop_by_asylum.columns = ['Asylum Country', 'Total Population']
        pop_by_asylum = pop_by_asylum.sort_values('Total Population', ascending=False)
        
        # Create excel buffer
        buffer = io.BytesIO()
        
        # Create Excel writer object
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pop_by_group.to_excel(writer, sheet_name='Population by Group', index=False)
            pop_by_gender.to_excel(writer, sheet_name='Population by Gender', index=False)
            pop_by_origin.to_excel(writer, sheet_name='Population by Origin', index=False)
            pop_by_asylum.to_excel(writer, sheet_name='Population by Asylum', index=False)
            
            # If age data is available
            if 'age_range' in df_filtered.columns and not df_filtered['age_range'].isna().all():
                df_age_export = df_filtered[df_filtered['age_range'] != 'all']
                if not df_age_export.empty:
                    age_dist = df_age_export.groupby('age_range')['population'].sum().reset_index()
                    age_dist.columns = ['Age Range', 'Total Population']
                    age_dist.to_excel(writer, sheet_name='Population by Age', index=False)
            
            # Origin-Asylum flow
            origin_asylum_flow = df_filtered.groupby(['origin_location_code', 'asylum_location_code'])['population'].sum().reset_index()
            origin_asylum_flow.columns = ['Origin Country', 'Asylum Country', 'Population']
            origin_asylum_flow = origin_asylum_flow.sort_values('Population', ascending=False)
            origin_asylum_flow.to_excel(writer, sheet_name='Origin-Asylum Flow', index=False)

        # Download button for Excel file
        st.download_button(
            label="Download Excel Summary",
            data=buffer.getvalue(),
            file_name="refugee_population_summary.xlsx",
            mime="application/vnd.ms-excel"
        )

# Footer with information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px;">
    Refugee Population Dashboard | Created with Streamlit | Data as of: {}</div>
""".format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

# Help section with tooltips
with st.expander("Help & Information"):
    st.markdown("""
    ### About This Dashboard
    
    This dashboard provides analysis and visualization of refugee and related population data. It allows for filtering and exploration across various dimensions including:
    
    - **Origin Countries**: Countries from which populations originate
    - **Asylum Countries**: Countries hosting populations
    - **Population Groups**: Different categories of populations (e.g., refugees, returnees)
    - **Demographics**: Gender and age distribution
    - **Geographic Analysis**: Analysis of migration flows
    - **HRP Status**: Humanitarian Response Plan status analysis
    
    ### Data Dictionary
    
    - **origin_location_code**: Country code for origin country
    - **origin_has_hrp**: Whether origin country has a Humanitarian Response Plan
    - **origin_in_gho**: Whether origin country is in Global Humanitarian Overview
    - **asylum_location_code**: Country code for asylum country
    - **asylum_has_hrp**: Whether asylum country has a Humanitarian Response Plan
    - **asylum_in_gho**: Whether asylum country is in Global Humanitarian Overview
    - **population_group**: Category of population (e.g., REF for refugee, RET for returnee)
    - **gender**: Gender (m/f)
    - **age_range**: Age range category
    - **min_age**: Minimum age in range
    - **max_age**: Maximum age in range
    - **population**: Population count
    - **reference_period_start**: Start date of reference period
    - **reference_period_end**: End date of reference period
    
    ### Tips for Using the Dashboard
    
    - Use the filters in the sidebar to narrow down your analysis
    - Hover over charts for detailed information
    - Use the tabs to navigate between different analysis views
    - Export data or summary statistics using the buttons provided
    """)

    st.info("For technical support or questions about the data, please contact your data administrator.")