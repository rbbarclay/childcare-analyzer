# Implementation Guide for Claude Code

This document provides guidance for an AI coding assistant (like Claude Code) to build the Colorado Early Childhood Capacity Analyzer.

---

## Phase 1: Project Setup & Structure

### Step 1.1: Create Directory Structure

Create the following directory structure:

```
co-childcare-analyzer/
├── data/
│   ├── raw/
│   ├── processed/
│   └── geo/
├── data_pipeline/
│   └── __init__.py
├── app/
│   ├── components/
│   └── __init__.py
├── tests/
└── docs/
```

Add `.gitkeep` files to empty directories to preserve them in git.

### Step 1.2: Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Phase 2: Data Pipeline Development

### Step 2.1: Create Sample Data Generator

**File: `data_pipeline/generate_sample_data.py`**

This script should generate realistic sample data for development:

**Colorado Counties to Include:**
- Denver (08031) - large urban
- El Paso (08041) - large urban (Colorado Springs)
- Boulder (08013) - medium urban
- Larimer (08069) - medium urban (Fort Collins)
- Mesa (08077) - medium rural (Grand Junction)
- Pueblo (08101) - medium urban
- Adams (08001) - suburban
- Arapahoe (08005) - suburban
- Jefferson (08059) - suburban
- Weld (08123) - mixed urban/rural
- La Plata (08067) - small rural (Durango)
- Routt (08107) - small rural (Steamboat Springs)
- ... (all 64 counties)

**Sample Data Characteristics:**
- Population ranges: 100 (tiny rural) to 25,000 (large urban) per age group
- Gap severity distribution: mix of adequate, moderate, and critical
- Some counties with oversupply (negative gaps)
- Forecast shows some gaps worsening, some improving

**Key Functions:**
```python
def generate_county_capacity_data(years=[2025, 2029]):
    """Generate county_capacity.csv with realistic data"""
    pass

def generate_provider_data():
    """Generate providers.csv with facility-level data"""
    pass

def generate_demographic_data():
    """Generate county_demographics.csv (optional)"""
    pass

def save_sample_data():
    """Save all sample datasets to data/processed/"""
    pass
```

### Step 2.2: Create Colorado GeoJSON

**File: `data_pipeline/fetch_geojson.py`**

Download Colorado county boundaries:

```python
import requests
import json

def fetch_colorado_counties():
    """
    Fetch US counties GeoJSON and filter to Colorado (FIPS starting with '08')
    Save to data/geo/colorado_counties.geojson
    """
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    response = requests.get(url)
    all_counties = response.json()
    
    # Filter to Colorado counties (FIPS codes starting with "08")
    co_counties = {
        "type": "FeatureCollection",
        "features": [
            f for f in all_counties["features"]
            if f["id"].startswith("08")
        ]
    }
    
    with open('data/geo/colorado_counties.geojson', 'w') as f:
        json.dump(co_counties, f)
```

### Step 2.3: Create Calculation Functions

**File: `data_pipeline/calculate.py`**

Implement core business logic:

```python
import pandas as pd

def calculate_need_estimate(population, age_group):
    """
    Calculate estimated childcare need based on population
    
    Args:
        population: int, number of children in age group
        age_group: str, "0-2", "3-5", or "0-5"
    
    Returns:
        int, estimated number of children needing care
    """
    participation_rates = {
        "0-2": 0.60,
        "3-5": 0.70,
        "0-5": 0.65  # Weighted average
    }
    return int(population * participation_rates[age_group])


def calculate_gap(need_estimate, licensed_capacity):
    """
    Calculate gap between need and supply
    
    Returns:
        tuple: (gap, gap_pct)
    """
    gap = need_estimate - licensed_capacity
    gap_pct = gap / need_estimate if need_estimate > 0 else 0
    return gap, gap_pct


def classify_severity(gap_pct):
    """
    Classify gap severity based on percentage
    
    Returns:
        tuple: (severity, color_code)
    """
    if gap_pct > 0.30:
        return "Critical", "#d32f2f"
    elif gap_pct > 0.20:
        return "Significant", "#f57c00"
    elif gap_pct > 0.10:
        return "Moderate", "#fbc02d"
    elif gap_pct > 0.05:
        return "Low", "#9ccc65"
    else:
        return "Adequate", "#66bb6a"


def process_county_data(population_df, capacity_df):
    """
    Process and merge population and capacity data
    Calculate gaps and severity for all counties
    
    Returns:
        DataFrame with county_capacity schema
    """
    # Implementation here
    pass
```

---

## Phase 3: Streamlit Application Development

### Step 3.1: Main App Structure

**File: `app/app.py`**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Colorado Early Childhood Capacity Analyzer",
    page_icon="🎓",
    layout="wide"
)

# Load data (with caching)
@st.cache_data
def load_data():
    county_capacity = pd.read_csv('data/processed/county_capacity.csv')
    providers = pd.read_csv('data/processed/providers.csv')
    return county_capacity, providers

@st.cache_data
def load_geojson():
    import json
    with open('data/geo/colorado_counties.geojson') as f:
        return json.load(f)

# Main app
def main():
    # Header
    st.title("🎓 Colorado Early Childhood Capacity Analyzer")
    st.markdown("*Identifying childcare capacity gaps across Colorado*")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    age_group = st.sidebar.radio(
        "Age Group",
        ["0-5", "0-2", "3-5"],
        index=0
    )
    
    time_period = st.sidebar.radio(
        "Time Period",
        ["Current (2025)", "Forecast (2029)"],
        index=0
    )
    
    # Load data
    county_capacity, providers = load_data()
    
    # Filter data based on selections
    year = 2025 if "Current" in time_period else 2029
    filtered_data = county_capacity[
        (county_capacity['age_group'] == age_group) &
        (county_capacity['year'] == year)
    ]
    
    # Layout: Two columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Capacity Gap Map")
        # Map will go here
        render_map(filtered_data)
    
    with col2:
        st.subheader("Top Counties by Gap")
        # Table will go here
        render_county_table(filtered_data)

if __name__ == "__main__":
    main()
```

### Step 3.2: Map Component

**File: `app/components/map_view.py`**

```python
import plotly.express as px
import streamlit as st

def render_choropleth_map(data, geojson):
    """
    Render interactive choropleth map of Colorado counties
    
    Args:
        data: DataFrame with county_capacity data
        geojson: GeoJSON with county boundaries
    """
    fig = px.choropleth(
        data,
        geojson=geojson,
        locations='county_fips',
        color='severity',
        color_discrete_map={
            "Critical": "#d32f2f",
            "Significant": "#f57c00",
            "Moderate": "#fbc02d",
            "Low": "#9ccc65",
            "Adequate": "#66bb6a"
        },
        hover_data={
            'county_name': True,
            'population': ':,',
            'gap': ':,',
            'gap_pct': ':.1%'
        },
        labels={
            'county_name': 'County',
            'population': 'Population',
            'gap': 'Gap',
            'gap_pct': 'Gap %'
        }
    )
    
    # Update layout to focus on Colorado
    fig.update_geos(
        center=dict(lon=-105.5, lat=39.0),
        projection_scale=12,
        visible=False
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add legend explanation
    st.markdown("""
    **Gap Severity Scale:**
    - 🔴 **Critical**: >30% gap
    - 🟠 **Significant**: 20-30% gap
    - 🟡 **Moderate**: 10-20% gap
    - 🟢 **Low**: 5-10% gap
    - 🟢 **Adequate**: <5% gap
    """)
```

### Step 3.3: County Table Component

**File: `app/components/county_list.py`**

```python
import streamlit as st
import pandas as pd

def render_county_table(data):
    """
    Render sortable table of counties ranked by gap
    
    Args:
        data: DataFrame with county_capacity data
    """
    # Sort by gap (descending) and take top 20
    top_counties = data.nlargest(20, 'gap')
    
    # Format for display
    display_df = top_counties[[
        'county_name', 'gap', 'gap_pct', 'population', 'licensed_capacity'
    ]].copy()
    
    display_df['gap_pct'] = display_df['gap_pct'].apply(lambda x: f"{x:.1%}")
    display_df['gap'] = display_df['gap'].apply(lambda x: f"{x:,}")
    display_df['population'] = display_df['population'].apply(lambda x: f"{x:,}")
    display_df['licensed_capacity'] = display_df['licensed_capacity'].apply(lambda x: f"{x:,}")
    
    display_df.columns = ['County', 'Gap', 'Gap %', 'Population (0-5)', 'Licensed Capacity']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Export button
    if st.button("📥 Export to CSV"):
        csv = top_counties.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="colorado_childcare_gaps.csv",
            mime="text/csv"
        )
```

### Step 3.4: County Detail View (Advanced)

**File: `app/components/county_detail.py`**

Create a county detail page that shows:
- Summary statistics
- Time series chart (if forecast mode)
- Provider list
- Demographic breakdown (if available)

This should be triggered when user clicks on a county in the map.

---

## Phase 4: Testing & Refinement

### Step 4.1: Test Data Processing

```python
# tests/test_calculations.py
import pytest
from data_pipeline.calculate import (
    calculate_need_estimate,
    calculate_gap,
    classify_severity
)

def test_need_estimate_0_2():
    assert calculate_need_estimate(1000, "0-2") == 600

def test_need_estimate_3_5():
    assert calculate_need_estimate(1000, "3-5") == 700

def test_gap_shortage():
    gap, gap_pct = calculate_gap(1000, 700)
    assert gap == 300
    assert gap_pct == 0.30

def test_gap_oversupply():
    gap, gap_pct = calculate_gap(1000, 1200)
    assert gap == -200
    assert gap_pct == -0.20

def test_severity_critical():
    severity, color = classify_severity(0.35)
    assert severity == "Critical"

def test_severity_adequate():
    severity, color = classify_severity(0.03)
    assert severity == "Adequate"
```

### Step 4.2: Manual Testing Checklist

- [ ] Map loads and displays all counties
- [ ] Counties are color-coded correctly
- [ ] Hover tooltips show correct data
- [ ] Age group filter updates map and table
- [ ] Time period filter updates to forecast data
- [ ] County table sorts correctly
- [ ] CSV export works
- [ ] About page displays methodology
- [ ] App loads in <5 seconds
- [ ] No errors in console

---

## Phase 5: Documentation

### Step 5.1: Create User Guide

**File: `docs/USER_GUIDE.md`**

Include:
- How to navigate the app
- How to interpret the map colors
- What the gap percentage means
- How forecasts are calculated
- How to export data
- FAQ section

### Step 5.2: Add About Page to App

```python
# In app.py, add About page to sidebar
with st.sidebar:
    if st.button("ℹ️ About This Tool"):
        show_about_page()

def show_about_page():
    st.markdown("""
    ## About the Colorado Early Childhood Capacity Analyzer
    
    This tool helps identify gaps in childcare and pre-K capacity across Colorado...
    
    ### How Gaps Are Calculated
    
    ### Data Sources
    
    ### Assumptions & Limitations
    
    ### Contact
    """)
```

---

## Phase 6: Deployment

### Option 1: Streamlit Cloud (Recommended for Prototype)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Deploy (free tier available)

### Option 2: Local Deployment

```bash
streamlit run app/app.py
```

### Option 3: Docker (For Production)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py"]
```

---

## Key Implementation Notes

### 1. State Management
Use Streamlit session state for:
- Selected county (when clicked on map)
- Filter selections
- Cached data

### 2. Performance Optimization
- Use `@st.cache_data` for data loading
- Filter large datasets before rendering
- Lazy load county detail data

### 3. Error Handling
- Handle missing data gracefully
- Validate user inputs
- Display user-friendly error messages

### 4. Code Organization
- Keep components modular and reusable
- Separate data processing from visualization
- Use clear function and variable names
- Add docstrings to all functions

### 5. Data Validation
- Check that all 64 Colorado counties present
- Validate FIPS codes match between datasets
- Ensure no negative populations or capacities
- Flag outliers (gap > 80% or < -50%)

---

## Common Pitfalls to Avoid

❌ **Don't**: Hardcode file paths without checking OS compatibility  
✅ **Do**: Use `os.path.join()` or `pathlib.Path`

❌ **Don't**: Load all provider data on initial page load  
✅ **Do**: Load only when county detail view is opened

❌ **Don't**: Use exact color hex codes without defining them as constants  
✅ **Do**: Define color scale once and reuse

❌ **Don't**: Forget to handle edge cases (divide by zero, missing counties)  
✅ **Do**: Add defensive checks and fallbacks

❌ **Don't**: Commit raw data files to git  
✅ **Do**: Use .gitignore and document data sources

---

## Success Criteria Checklist

Before considering the prototype complete, ensure:

- [ ] All 64 Colorado counties display on map
- [ ] Gap calculations are correct (verified with sample data)
- [ ] Filters work (age group, time period)
- [ ] County detail view shows provider list
- [ ] Forecast data displays for 2029
- [ ] CSV export includes all relevant columns
- [ ] About page documents methodology
- [ ] App runs without errors
- [ ] Load time < 5 seconds
- [ ] Code is well-commented
- [ ] README has clear setup instructions

---

**End of Implementation Guide**
