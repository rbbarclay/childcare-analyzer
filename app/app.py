"""
Colorado Early Childhood Capacity Analyzer
Main Streamlit Application

Interactive dashboard for visualizing childcare capacity gaps across Colorado
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Colorado Childcare Capacity Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# DATA LOADING (with caching for performance)
# ============================================================================

@st.cache_data
def load_county_capacity():
    """Load county capacity data with gap calculations"""
    df = pd.read_csv('data/processed/county_capacity.csv')
    # Ensure county_fips is string with leading zeros (5 digits) to match GeoJSON
    df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
    return df


@st.cache_data
def load_geojson():
    """Load Colorado county boundaries GeoJSON"""
    with open('data/geo/colorado_counties.geojson', 'r') as f:
        geojson = json.load(f)
    return geojson


@st.cache_data
def load_providers():
    """Load childcare provider data"""
    df = pd.read_csv('data/raw/childcare_facilities.csv')
    # Standardize county names
    df['COUNTY'] = df['COUNTY'].str.title()
    return df


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Header
    st.title("🎓 Colorado Early Childhood Capacity Analyzer")
    st.markdown("""
    **Identifying childcare and pre-K capacity gaps across Colorado's 64 counties**

    Use the filters below to explore current gaps and future projections.
    """)

    # Load data
    with st.spinner("Loading data..."):
        county_data = load_county_capacity()
        geojson = load_geojson()

    # Sidebar filters
    st.sidebar.header("📊 Filters")

    # Age group filter
    age_group = st.sidebar.radio(
        "Age Group",
        options=["0-5", "0-2", "3-5"],
        index=0,
        help="Select age range to analyze"
    )

    # Time period filter
    time_period = st.sidebar.radio(
        "Time Period",
        options=["Current (2025)", "Forecast (2029)"],
        index=0,
        help="Current year or 4-year forecast"
    )

    # Extract year from selection
    year = 2025 if "Current" in time_period else 2029

    # County selector for detail view
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 County Detail View")

    county_list = sorted(county_data['county_name'].unique().tolist())
    selected_county = st.sidebar.selectbox(
        "Select a county for details",
        options=["None"] + county_list,
        index=0,
        help="View detailed information about a specific county"
    )

    # Filter data based on selections
    filtered_data = county_data[
        (county_data['age_group'] == age_group) &
        (county_data['year'] == year)
    ].copy()

    # Display summary statistics
    display_summary_stats(filtered_data, age_group, year)

    # Main content: Map and Table side by side
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Capacity Gap Map")
        render_choropleth_map(filtered_data, geojson, age_group, year)

    with col2:
        st.subheader("Top Counties by Gap")
        render_county_table(filtered_data, age_group, year)

    # County Detail View
    if selected_county != "None":
        st.markdown("---")
        render_county_detail(selected_county, county_data, age_group, year)

    # Footer with data sources
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Data Sources")
    st.sidebar.markdown("""
    - **Facilities**: Colorado Open Data (Oct 2025)
    - **Population**: US Census ACS 2022
    - **Forecasts**: 0.5% annual growth projection
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.markdown("""
    This tool calculates childcare capacity gaps by comparing:
    - **Need**: Population × participation rate (60% for 0-2, 70% for 3-5)
    - **Supply**: Licensed capacity from facilities
    - **Gap**: Need - Supply
    """)


# ============================================================================
# COMPONENT FUNCTIONS
# ============================================================================

def display_summary_stats(data, age_group, year):
    """Display summary statistics at the top"""

    # Calculate statewide totals
    total_pop = data['population'].sum()
    total_capacity = data['licensed_capacity'].sum()
    total_need = data['need_estimate'].sum()
    total_gap = data['gap'].sum()
    gap_pct = (total_gap / total_need * 100) if total_need > 0 else 0

    # Display in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Population (Ages " + age_group + ")", f"{total_pop:,}")

    with col2:
        st.metric("Licensed Capacity", f"{total_capacity:,}")

    with col3:
        st.metric("Estimated Need", f"{total_need:,}")

    with col4:
        st.metric("Gap (Shortage)", f"{total_gap:,}", delta=f"{gap_pct:.1f}%", delta_color="inverse")

    with col5:
        # Count critical counties
        critical_count = len(data[data['severity'] == 'Critical'])
        st.metric("Critical Counties", f"{critical_count}/64")


def render_choropleth_map(data, geojson, age_group, year):
    """Render interactive choropleth map"""

    # Color scale for severity
    color_discrete_map = {
        "Critical": "#d32f2f",
        "Significant": "#f57c00",
        "Moderate": "#fbc02d",
        "Low": "#9ccc65",
        "Adequate": "#66bb6a"
    }

    # Create choropleth
    fig = px.choropleth(
        data,
        geojson=geojson,
        featureidkey="id",  # Match GeoJSON "id" field with locations column
        locations='county_fips',
        color='severity',
        color_discrete_map=color_discrete_map,
        category_orders={"severity": ["Critical", "Significant", "Moderate", "Low", "Adequate"]},
        hover_data={
            'county_name': True,
            'county_fips': False,
            'population': ':,',
            'licensed_capacity': ':,',
            'gap': ':,',
            'gap_pct': ':.1%',
            'severity': True
        },
        labels={
            'county_name': 'County',
            'population': 'Population',
            'licensed_capacity': 'Capacity',
            'gap': 'Gap',
            'gap_pct': 'Gap %',
            'severity': 'Severity'
        }
    )

    # Update map layout to focus on Colorado
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500,
        legend=dict(
            title="Gap Severity",
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Legend explanation
    with st.expander("📖 Gap Severity Scale"):
        st.markdown("""
        - **Critical** (>30% gap): Severe shortage - roughly 1 in 3 children lack access
        - **Significant** (20-30% gap): Major shortage
        - **Moderate** (10-20% gap): Noticeable gap but manageable
        - **Low** (5-10% gap): Minor gap, may be frictional
        - **Adequate** (<5% gap): Reasonable match between need and supply
        """)


def render_county_table(data, age_group, year):
    """Render sortable table of top counties by gap"""

    # Sort by gap (descending) and take top 20
    top_counties = data.nlargest(20, 'gap').copy()

    # Format for display
    display_df = top_counties[[
        'county_name',
        'gap',
        'gap_pct',
        'population',
        'licensed_capacity',
        'severity'
    ]].copy()

    display_df['gap_pct'] = display_df['gap_pct'].apply(lambda x: f"{x*100:.1f}%")
    display_df['gap'] = display_df['gap'].apply(lambda x: f"{x:,}")
    display_df['population'] = display_df['population'].apply(lambda x: f"{x:,}")
    display_df['licensed_capacity'] = display_df['licensed_capacity'].apply(lambda x: f"{x:,}")

    display_df.columns = [
        'County',
        'Gap',
        'Gap %',
        'Population',
        'Capacity',
        'Severity'
    ]

    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # CSV export button
    csv = top_counties.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name=f"colorado_childcare_gaps_{age_group}_{year}.csv",
        mime="text/csv",
        use_container_width=True
    )


def render_county_detail(county_name, county_data, age_group, year):
    """Render detailed view for a selected county"""

    st.header(f"📍 {county_name} County - Detailed View")

    # Filter data for this county
    county_df = county_data[
        (county_data['county_name'] == county_name) &
        (county_data['year'] == year)
    ].copy()

    if len(county_df) == 0:
        st.warning(f"No data available for {county_name} County")
        return

    # Display metrics for all age groups
    col1, col2, col3 = st.columns(3)

    # Get data for each age group
    data_0_2 = county_df[county_df['age_group'] == '0-2'].iloc[0] if len(county_df[county_df['age_group'] == '0-2']) > 0 else None
    data_3_5 = county_df[county_df['age_group'] == '3-5'].iloc[0] if len(county_df[county_df['age_group'] == '3-5']) > 0 else None
    data_0_5 = county_df[county_df['age_group'] == '0-5'].iloc[0] if len(county_df[county_df['age_group'] == '0-5']) > 0 else None

    with col1:
        st.subheader("Ages 0-2")
        if data_0_2 is not None:
            st.metric("Population", f"{data_0_2['population']:,}")
            st.metric("Capacity", f"{data_0_2['licensed_capacity']:,}")
            st.metric("Gap", f"{data_0_2['gap']:,}", delta=f"{data_0_2['gap_pct']*100:.1f}%", delta_color="inverse")
            st.metric("Severity", data_0_2['severity'])

    with col2:
        st.subheader("Ages 3-5")
        if data_3_5 is not None:
            st.metric("Population", f"{data_3_5['population']:,}")
            st.metric("Capacity", f"{data_3_5['licensed_capacity']:,}")
            st.metric("Gap", f"{data_3_5['gap']:,}", delta=f"{data_3_5['gap_pct']*100:.1f}%", delta_color="inverse")
            st.metric("Severity", data_3_5['severity'])

    with col3:
        st.subheader("Ages 0-5 (Total)")
        if data_0_5 is not None:
            st.metric("Population", f"{data_0_5['population']:,}")
            st.metric("Capacity", f"{data_0_5['licensed_capacity']:,}")
            st.metric("Gap", f"{data_0_5['gap']:,}", delta=f"{data_0_5['gap_pct']*100:.1f}%", delta_color="inverse")
            st.metric("Severity", data_0_5['severity'])

    # Load and display providers
    st.subheader("📋 Licensed Childcare Facilities")

    providers = load_providers()
    county_providers = providers[providers['COUNTY'] == county_name].copy()

    if len(county_providers) == 0:
        st.info(f"No facility data available for {county_name} County")
        return

    st.markdown(f"**Total facilities in {county_name} County: {len(county_providers)}**")

    # Calculate capacity breakdown
    total_capacity = county_providers['TOTAL LICENSED CAPACITY'].fillna(0).sum()
    infant_capacity = county_providers['LICENSED CENTER INFANT CAPACITY'].fillna(0).sum()
    toddler_capacity = county_providers['LICENSED CENTER TODDLER CAPACITY'].fillna(0).sum()
    preschool_capacity = county_providers['LICENSED CENTER PRESCHOOL CAPACITY'].fillna(0).sum()
    school_age_capacity = county_providers['LICENSED SCHOOL AGE CAPACITY'].fillna(0).sum()

    # Display capacity breakdown
    cap_col1, cap_col2, cap_col3, cap_col4, cap_col5 = st.columns(5)
    with cap_col1:
        st.metric("Total Capacity", f"{int(total_capacity):,}")
    with cap_col2:
        st.metric("Infant", f"{int(infant_capacity):,}")
    with cap_col3:
        st.metric("Toddler", f"{int(toddler_capacity):,}")
    with cap_col4:
        st.metric("Preschool", f"{int(preschool_capacity):,}")
    with cap_col5:
        st.metric("School-Age", f"{int(school_age_capacity):,}")

    # Display provider list
    st.markdown("### Facility List")

    # Prepare display columns
    display_providers = county_providers[[
        'PROVIDER NAME',
        'FACILITY TYPE',
        'TOTAL LICENSED CAPACITY',
        'FACILITY ADDRESS 1',
        'CITY',
        'ZIP CODE'
    ]].copy()

    display_providers.columns = [
        'Provider Name',
        'Type',
        'Capacity',
        'Address',
        'City',
        'ZIP'
    ]

    # Sort by capacity (descending)
    display_providers = display_providers.sort_values('Capacity', ascending=False)
    display_providers['Capacity'] = display_providers['Capacity'].fillna(0).astype(int)

    # Display as dataframe
    st.dataframe(
        display_providers,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Download button for this county's providers
    csv = county_providers.to_csv(index=False)
    st.download_button(
        label=f"📥 Download {county_name} County Facilities (CSV)",
        data=csv,
        file_name=f"{county_name.lower()}_childcare_facilities.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
