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

    # Model Configuration
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Model Configuration")

    with st.sidebar.expander("📐 Participation Rates", expanded=False):
        st.markdown("*Adjust the estimated % of children needing formal childcare*")

        participation_0_2 = st.slider(
            "Ages 0-2 Participation Rate",
            min_value=0.30, max_value=0.90, value=0.60, step=0.05,
            help="Default: 60% based on working parent rates"
        )

        participation_3_5 = st.slider(
            "Ages 3-5 Participation Rate",
            min_value=0.30, max_value=0.90, value=0.70, step=0.05,
            help="Default: 70% based on pre-K participation trends"
        )

        st.info(f"📊 **Current Settings:**\n- Ages 0-2: {participation_0_2:.0%}\n- Ages 3-5: {participation_3_5:.0%}\n- Ages 0-5: {(participation_0_2 + participation_3_5)/2:.0%} (avg)")

    with st.sidebar.expander("🎯 Severity Thresholds", expanded=False):
        st.markdown("*Adjust gap % thresholds for severity classification*")

        critical_threshold = st.slider(
            "Critical Threshold",
            min_value=0.15, max_value=0.50, value=0.30, step=0.05,
            help="Gap % above this is 'Critical'"
        ) * 100

        significant_threshold = st.slider(
            "Significant Threshold",
            min_value=0.10, max_value=0.40, value=0.20, step=0.05,
            help="Gap % above this is 'Significant'"
        ) * 100

        moderate_threshold = st.slider(
            "Moderate Threshold",
            min_value=0.05, max_value=0.30, value=0.10, step=0.05,
            help="Gap % above this is 'Moderate'"
        ) * 100

        low_threshold = st.slider(
            "Low Threshold",
            min_value=0.01, max_value=0.20, value=0.05, step=0.01,
            help="Gap % above this is 'Low'"
        ) * 100

        st.info(f"📊 **Thresholds:**\n- Critical: >{critical_threshold:.0f}%\n- Significant: >{significant_threshold:.0f}%\n- Moderate: >{moderate_threshold:.0f}%\n- Low: >{low_threshold:.0f}%")

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

    # Recalculate metrics based on custom participation rates
    participation_rates = {
        '0-2': participation_0_2,
        '3-5': participation_3_5,
        '0-5': (participation_0_2 + participation_3_5) / 2
    }

    severity_thresholds = {
        'critical': critical_threshold / 100,
        'significant': significant_threshold / 100,
        'moderate': moderate_threshold / 100,
        'low': low_threshold / 100
    }

    filtered_data = recalculate_metrics(filtered_data, participation_rates, severity_thresholds)

    # Calculate growth metrics (for trend analysis)
    growth_data = calculate_growth_metrics(county_data, age_group, participation_rates, severity_thresholds)

    # Priority Filtering Options
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Priority Filters")

    show_all = st.sidebar.checkbox("Show all counties", value=True)

    if not show_all:
        growth_filter = st.sidebar.multiselect(
            "Growth Trend",
            options=["Accelerating", "Growing", "Stable", "Improving"],
            default=["Accelerating", "Growing"],
            help="Filter by gap growth rate compared to state average"
        )

        severity_filter = st.sidebar.multiselect(
            "Severity Level",
            options=["Critical", "Significant", "Moderate", "Low", "Adequate"],
            default=["Critical", "Significant"],
            help="Filter by current gap severity"
        )

        # Apply filters to display data
        if year == 2025:
            # For 2025, merge with growth data to enable filtering
            filtered_data = filtered_data.merge(
                growth_data[['county_name', 'growth_category']],
                on='county_name',
                how='left'
            )

            if growth_filter:
                filtered_data = filtered_data[filtered_data['growth_category'].isin(growth_filter)]
            if severity_filter:
                filtered_data = filtered_data[filtered_data['severity'].isin(severity_filter)]
        else:
            # For 2029, apply severity filter only
            if severity_filter:
                filtered_data = filtered_data[filtered_data['severity'].isin(severity_filter)]

    # Display summary statistics
    display_summary_stats(filtered_data, age_group, year)

    # Display growth trend summary
    if year == 2025:
        state_growth = growth_data['state_avg_growth_rate'].iloc[0] if len(growth_data) > 0 else 0
        st.info(f"📊 **Trend Analysis (2025→2029)**: State average gap growth rate: {state_growth:.1%} | Use Priority Filters to focus on accelerating counties")


    # Main content: Map and Table side by side
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Capacity Gap Map")
        render_choropleth_map(filtered_data, geojson, age_group, year)

    with col2:
        st.subheader("Top Counties by Gap")
        # Pass growth data for 2025 view
        if year == 2025:
            render_county_table(filtered_data, age_group, year, growth_data)
        else:
            render_county_table(filtered_data, age_group, year)

    # County Detail View
    if selected_county != "None":
        st.markdown("---")
        # Also recalculate for all years/age groups for the selected county
        county_detail_data = county_data[county_data['county_name'] == selected_county].copy()
        county_detail_data = recalculate_metrics(county_detail_data, participation_rates, severity_thresholds)
        render_county_detail(selected_county, county_detail_data, age_group, year, participation_rates)

    # Methodology Documentation
    st.markdown("---")
    with st.expander("📘 Methodology & Data Sources", expanded=False):
        st.markdown("""
        ## Data Sources

        ### Licensed Childcare Facilities
        - **Source**: Colorado Open Data Portal
        - **Dataset**: Colorado Licensed Child Care Facilities Report
        - **Date**: October 2025
        - **Records**: 4,604 licensed facilities
        - **Link**: [data.colorado.gov](https://data.colorado.gov/Early-childhood/Colorado-Licensed-Child-Care-Facilities-Report/a9rr-k8mu)

        ### Population Data
        - **Source**: U.S. Census Bureau
        - **Dataset**: American Community Survey (ACS) 5-Year Estimates (2022)
        - **Variables**: B01001_003E (Male Under 5), B01001_027E (Female Under 5)
        - **Total**: 380,627 children ages 0-5 in Colorado
        - **Geographic Level**: County

        ### Population Forecasts
        - **Source**: Colorado Department of Local Affairs (DOLA) - State Demography Office
        - **Dataset**: Population Projections in Colorado (q5vp-adf3)
        - **Coverage**: County-level projections from 1990 to 2050
        - **Method**: Official state demographic projections by individual age
        - **2029 Forecast**: 388,869 children ages 0-5 (all 64 counties)
        - **Link**: [data.colorado.gov](https://data.colorado.gov/Demographics/Population-Projections-in-Colorado/q5vp-adf3)
        - **Note**: Capacity is assumed constant at 2025 levels for forecast scenarios

        ### Geographic Boundaries
        - **Source**: Plotly Public Datasets (derived from U.S. Census TIGER/Line)
        - **Coverage**: All 64 Colorado counties
        - **Format**: GeoJSON with FIPS codes

        ---

        ## Calculation Methodology

        ### Capacity by Age Group
        Licensed capacity is aggregated from facility-level data:

        - **Ages 0-2**: Infant (0-12 months) + Toddler (13-35 months) + 40% of home-based capacity
        - **Ages 3-5**: Preschool (3-5 years) + 60% of home-based capacity
        - **Ages 0-5**: Sum of ages 0-2 and 3-5

        **Rationale**: Home-based facilities don't report age-specific capacity, so we apply industry-standard splits based on typical enrollment patterns.

        ### Need Estimation

        **Formula**: `Need = Population × Participation Rate`

        **Default Participation Rates** (configurable in sidebar):
        - **Ages 0-2**: 60%
        - **Ages 3-5**: 70%
        - **Ages 0-5**: 65% (weighted average)

        **Rationale for Defaults**:
        - **Ages 0-2 (60%)**: Based on labor force participation of mothers with young children (~70% nationally, 2024), adjusted downward to account for informal care arrangements
        - **Ages 3-5 (70%)**: Aligns with Colorado Universal Preschool enrollment goals and observed participation (64.5% of 4-year-olds enrolled as of Oct 2024)

        **Important**: These are *estimates* for prototype purposes. Actual participation varies by:
        - Family income and employment status
        - Availability of informal care (relatives, neighbors)
        - Cultural preferences
        - Geographic accessibility

        ### Gap Calculation

        **Formula**: `Gap = Need - Licensed Capacity`

        - **Positive Gap**: Shortage (more children need care than slots available)
        - **Negative Gap**: Oversupply (more slots than estimated need)

        **Gap %**: `Gap ÷ Need × 100`

        This represents the percentage of children who need care but lack access to licensed slots.

        ### Severity Classification

        Counties are classified based on **Gap %** (configurable in sidebar):

        | Severity | Default Threshold | Color | Meaning |
        |----------|-------------------|-------|---------|
        | **Critical** | >30% | Red | Severe shortage - roughly 1 in 3 children lack access |
        | **Significant** | 20-30% | Orange | Major shortage requiring immediate attention |
        | **Moderate** | 10-20% | Yellow | Noticeable gap but manageable |
        | **Low** | 5-10% | Light Green | Minor gap, may be frictional/geographic |
        | **Adequate** | <5% | Green | Reasonable match between need and supply |

        ---

        ## Limitations & Assumptions

        ### Data Limitations
        1. **Snapshot in Time**: October 2025 facility data may not reflect recent openings/closures
        2. **Licensed Capacity Only**: Does not include license-exempt care (relatives, neighbors, nannies)
        3. **Actual Enrollment vs Capacity**: Licensed capacity ≠ current enrollment
        4. **Quality Variations**: All licensed slots treated equally regardless of quality ratings
        5. **Geographic Access**: County-level analysis doesn't capture within-county accessibility issues

        ### Key Assumptions
        1. **Participation Rates**: Default 60%/70% are estimates, not Colorado-specific validated rates
        2. **Constant Capacity**: 2029 forecasts assume no new facility openings/closures
        3. **Uniform Distribution**: Population and capacity assumed evenly distributed within counties
        4. **Age Splits for Home Care**: 40/60 split is industry approximation, not facility-specific
        5. **Need = Demand**: Participation rates proxy for actual demand; doesn't account for affordability barriers

        ### Recommended Validation
        To improve accuracy, we recommend validating with:
        - Colorado Department of Early Childhood (CDEC) enrollment data
        - Colorado Children's Campaign KIDS COUNT reports
        - County-level surveys of working parents
        - Waitlist data from childcare providers
        - Quality ratings (Colorado Shines) to weight capacity

        ---

        ## Model Configuration

        This tool allows you to adjust key assumptions:

        **Participation Rates**: Modify to reflect different scenarios:
        - Conservative: Lower rates (e.g., 50% for 0-2)
        - Progressive: Higher rates matching labor force participation
        - Research-based: Use Colorado-specific survey data if available

        **Severity Thresholds**: Adjust based on policy priorities:
        - Stricter: Lower thresholds to identify more counties as critical
        - Lenient: Higher thresholds for targeted interventions

        ---

        ## For More Information

        - **Colorado Department of Early Childhood**: [cdec.colorado.gov](https://cdec.colorado.gov)
        - **Colorado Children's Campaign**: [coloradokids.org](https://www.coloradokids.org)
        - **Early Milestones Colorado**: [earlymilestones.org](https://www.earlymilestones.org)
        - **Census Data**: [data.census.gov](https://data.census.gov)

        ---

        *Last Updated: 2025-11-07 | Version: 1.1 (Configurable Model)*
        """)

    # Footer with data sources
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Data Sources")
    st.sidebar.markdown("""
    - **Facilities**: Colorado Open Data (Oct 2025)
    - **Population**: US Census ACS 2022
    - **Forecasts**: 0.5% annual growth projection
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ How Gap % Works")
    st.sidebar.markdown(f"""
    **Calculation:**
    - **Need** = Population × Participation Rate
      - Ages 0-2: {participation_0_2:.0%} (configurable)
      - Ages 3-5: {participation_3_5:.0%} (configurable)
    - **Gap** = Need - Licensed Capacity
    - **Gap %** = Gap ÷ Need

    **Example:** Adams County (Ages 0-2)
    - Population: 20,460
    - Need: 20,460 × {participation_0_2:.0%} = {int(20460 * participation_0_2):,}
    - Capacity: 2,792
    - Gap: {int(20460 * participation_0_2):,} - 2,792 = {int(20460 * participation_0_2) - 2792:,}
    - Gap %: {(int(20460 * participation_0_2) - 2792) / int(20460 * participation_0_2):.1%}

    *Adjust participation rates above to see how estimates change.*
    """)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def recalculate_metrics(data, participation_rates, severity_thresholds):
    """
    Recalculate need, gap, gap_pct, and severity based on custom parameters

    Args:
        data: DataFrame with population and licensed_capacity
        participation_rates: dict with keys '0-2', '3-5', '0-5'
        severity_thresholds: dict with keys 'critical', 'significant', 'moderate', 'low'

    Returns:
        DataFrame with recalculated metrics
    """
    df = data.copy()

    # Recalculate need_estimate based on custom participation rates
    df['need_estimate'] = df.apply(
        lambda row: int(row['population'] * participation_rates.get(row['age_group'], 0.65)),
        axis=1
    )

    # Recalculate gap
    df['gap'] = df['need_estimate'] - df['licensed_capacity']

    # Recalculate gap_pct
    df['gap_pct'] = df.apply(
        lambda row: row['gap'] / row['need_estimate'] if row['need_estimate'] > 0 else 0,
        axis=1
    )

    # Reclassify severity based on custom thresholds
    def classify_severity_custom(gap_pct):
        if gap_pct > severity_thresholds['critical']:
            return "Critical", "#d32f2f"
        elif gap_pct > severity_thresholds['significant']:
            return "Significant", "#f57c00"
        elif gap_pct > severity_thresholds['moderate']:
            return "Moderate", "#fbc02d"
        elif gap_pct > severity_thresholds['low']:
            return "Low", "#9ccc65"
        else:
            return "Adequate", "#66bb6a"

    df[['severity', 'color_code']] = df['gap_pct'].apply(
        lambda x: pd.Series(classify_severity_custom(x))
    )

    return df


def calculate_growth_metrics(county_data, age_group, participation_rates, severity_thresholds):
    """
    Calculate growth rates between 2025 and 2029 for trend analysis

    Args:
        county_data: Complete dataset with both years
        age_group: Selected age group
        participation_rates: Custom participation rates
        severity_thresholds: Custom severity thresholds

    Returns:
        DataFrame with growth metrics added
    """
    # Get data for both years
    data_2025 = county_data[
        (county_data['age_group'] == age_group) &
        (county_data['year'] == 2025)
    ].copy()

    data_2029 = county_data[
        (county_data['age_group'] == age_group) &
        (county_data['year'] == 2029)
    ].copy()

    # Recalculate metrics for both years
    data_2025 = recalculate_metrics(data_2025, participation_rates, severity_thresholds)
    data_2029 = recalculate_metrics(data_2029, participation_rates, severity_thresholds)

    # Merge to calculate growth
    merged = data_2025.merge(
        data_2029[['county_name', 'gap', 'gap_pct']],
        on='county_name',
        suffixes=('_2025', '_2029'),
        how='left'
    )

    # Calculate growth metrics
    merged['gap_change'] = merged['gap_2029'] - merged['gap_2025']
    merged['gap_growth_rate'] = merged.apply(
        lambda row: (row['gap_change'] / row['gap_2025']) if row['gap_2025'] > 0 else 0,
        axis=1
    )

    # State average growth rate (for comparison)
    state_avg_growth = merged['gap_change'].sum() / merged['gap_2025'].sum()

    # Classify growth
    def classify_growth(growth_rate):
        if growth_rate < -0.05:  # Improving by >5%
            return "Improving", "↓", "#66bb6a"
        elif growth_rate < state_avg_growth * 0.5:  # Below half state avg
            return "Stable", "→", "#9ccc65"
        elif growth_rate < state_avg_growth * 2.0:  # Within 2x state avg
            return "Growing", "↗", "#fbc02d"
        else:  # More than 2x state average
            return "Accelerating", "⬆", "#d32f2f"

    merged[['growth_category', 'growth_icon', 'growth_color']] = merged['gap_growth_rate'].apply(
        lambda x: pd.Series(classify_growth(x))
    )

    # Add state average for reference
    merged['state_avg_growth_rate'] = state_avg_growth

    return merged


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


def render_county_table(data, age_group, year, growth_data=None):
    """Render sortable table of top counties by gap"""

    # Sort by gap (descending) and take top 20
    top_counties = data.nlargest(20, 'gap').copy()

    # Merge with growth data if available (for 2025 view)
    if growth_data is not None and year == 2025:
        top_counties = top_counties.merge(
            growth_data[['county_name', 'gap_growth_rate', 'growth_category', 'growth_icon']],
            on='county_name',
            how='left'
        )

        # Format for display with growth
        display_df = top_counties[[
            'county_name',
            'gap',
            'gap_pct',
            'gap_growth_rate',
            'growth_icon',
            'need_estimate',
            'licensed_capacity',
            'severity'
        ]].copy()

        display_df['gap'] = display_df['gap'].apply(lambda x: f"{x:,}")
        display_df['gap_pct'] = display_df['gap_pct'].apply(lambda x: f"{x*100:.1f}%")
        display_df['gap_growth_rate'] = display_df['gap_growth_rate'].apply(lambda x: f"{x*100:+.1f}%")
        display_df['need_estimate'] = display_df['need_estimate'].apply(lambda x: f"{x:,}")
        display_df['licensed_capacity'] = display_df['licensed_capacity'].apply(lambda x: f"{x:,}")

        # Create trend column combining icon and growth rate
        display_df['Trend'] = display_df['growth_icon'] + " " + display_df['gap_growth_rate']
        display_df = display_df.drop(columns=['growth_icon', 'gap_growth_rate'])

        display_df.columns = [
            'County',
            'Gap',
            'Gap %',
            'Need',
            'Capacity',
            'Severity',
            'Trend 2025→29'
        ]

        # Reorder columns
        display_df = display_df[[
            'County',
            'Gap',
            'Gap %',
            'Trend 2025→29',
            'Need',
            'Capacity',
            'Severity'
        ]]

    else:
        # Format for display without growth
        display_df = top_counties[[
            'county_name',
            'population',
            'need_estimate',
            'licensed_capacity',
            'gap',
            'gap_pct',
            'severity'
        ]].copy()

        display_df['population'] = display_df['population'].apply(lambda x: f"{x:,}")
        display_df['need_estimate'] = display_df['need_estimate'].apply(lambda x: f"{x:,}")
        display_df['licensed_capacity'] = display_df['licensed_capacity'].apply(lambda x: f"{x:,}")
        display_df['gap'] = display_df['gap'].apply(lambda x: f"{x:,}")
        display_df['gap_pct'] = display_df['gap_pct'].apply(lambda x: f"{x*100:.1f}%")

        display_df.columns = [
            'County',
            'Population',
            'Need',
            'Capacity',
            'Gap',
            'Gap %',
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


def render_county_detail(county_name, county_data, age_group, year, participation_rates):
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
            st.metric(f"Need ({participation_rates['0-2']:.0%} rate)", f"{data_0_2['need_estimate']:,}")
            st.metric("Capacity", f"{data_0_2['licensed_capacity']:,}")
            st.metric("Gap", f"{data_0_2['gap']:,}", delta=f"{data_0_2['gap_pct']*100:.1f}%", delta_color="inverse")
            st.metric("Severity", data_0_2['severity'])

    with col2:
        st.subheader("Ages 3-5")
        if data_3_5 is not None:
            st.metric("Population", f"{data_3_5['population']:,}")
            st.metric(f"Need ({participation_rates['3-5']:.0%} rate)", f"{data_3_5['need_estimate']:,}")
            st.metric("Capacity", f"{data_3_5['licensed_capacity']:,}")
            st.metric("Gap", f"{data_3_5['gap']:,}", delta=f"{data_3_5['gap_pct']*100:.1f}%", delta_color="inverse")
            st.metric("Severity", data_3_5['severity'])

    with col3:
        st.subheader("Ages 0-5 (Total)")
        if data_0_5 is not None:
            st.metric("Population", f"{data_0_5['population']:,}")
            st.metric(f"Need ({participation_rates['0-5']:.0%} rate)", f"{data_0_5['need_estimate']:,}")
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
        'PROVIDER SERVICE TYPE',
        'TOTAL LICENSED CAPACITY',
        'STREET ADDRESS',
        'CITY',
        'ZIP'
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
