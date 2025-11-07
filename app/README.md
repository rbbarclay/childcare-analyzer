# Colorado Early Childhood Capacity Analyzer - Streamlit Application

Interactive web dashboard for visualizing childcare capacity gaps across Colorado's 64 counties.

## Features

- **Interactive Choropleth Map**: Color-coded map showing capacity gap severity by county
- **Summary Statistics**: Statewide metrics including population, capacity, need, and gap
- **County Rankings**: Sortable table of top 20 counties with largest gaps
- **Filter Controls**:
  - Age Group: 0-2, 3-5, or 0-5 (all ages)
  - Time Period: Current (2025) or Forecast (2029)
- **County Detail View**:
  - Detailed breakdown by age group for any selected county
  - Complete list of licensed childcare facilities
  - Capacity breakdown by type (infant, toddler, preschool, school-age)
  - CSV export for county-specific data
- **Data Export**: Download filtered data as CSV

## Running the Application

### Prerequisites

Ensure all data pipeline scripts have been run successfully:

```bash
cd /home/user/childcare-analyzer/data_pipeline

# 1. Fetch data (if not already done)
python fetch_geojson.py
python fetch_childcare_data.py
python fetch_census_data_fixed.py  # Requires CENSUS_API_KEY environment variable

# 2. Process data
python analyze_capacity.py
python calculate_gaps.py
python generate_final_dataset.py
```

### Start the Application

From the project root directory:

```bash
streamlit run app/app.py
```

The application will open in your default browser at `http://localhost:8501`

### Configuration Options

You can customize Streamlit behavior:

```bash
# Specify a different port
streamlit run app/app.py --server.port 8080

# Run in headless mode (for servers)
streamlit run app/app.py --server.headless true

# Disable CORS for external access
streamlit run app/app.py --server.enableCORS false
```

## Data Sources

The application uses real data from:
- **Facilities**: Colorado Open Data Portal (October 2025)
- **Population**: US Census Bureau ACS 2022 5-Year Estimates
- **Forecasts**: 0.5% annual growth projection through 2029
- **Geography**: Colorado county boundaries GeoJSON

## Application Structure

```
app/
├── app.py          # Main Streamlit application
└── README.md       # This file

Required data files:
├── data/processed/county_capacity.csv        # Main dataset (384 records)
├── data/geo/colorado_counties.geojson        # County boundaries
└── data/raw/childcare_facilities.csv         # Provider details
```

## Key Metrics Explained

### Gap Severity Classification

- **Critical** (>30%): Severe shortage - roughly 1 in 3 children lack access
- **Significant** (20-30%): Major shortage requiring immediate attention
- **Moderate** (10-20%): Noticeable gap but manageable
- **Low** (5-10%): Minor gap, may be frictional/geographic
- **Adequate** (<5%): Reasonable match between need and supply

### Participation Rates

Used to estimate childcare need from population:
- **Ages 0-2**: 60% (based on working parent rates + childcare preferences)
- **Ages 3-5**: 70% (higher due to pre-K participation)
- **Ages 0-5**: 65% (weighted average)

### Gap Calculation

```
Need = Population × Participation Rate
Gap = Need - Licensed Capacity
Gap % = Gap / Need
```

## Performance Optimization

The application uses Streamlit's caching features:
- `@st.cache_data` on data loading functions
- Cached functions: `load_county_capacity()`, `load_geojson()`, `load_providers()`
- Cache persists across user interactions and page refreshes

## Troubleshooting

**Map not displaying:**
- Ensure `colorado_counties.geojson` exists and is valid JSON
- Check that `county_fips` codes match between data and GeoJSON (format: "08XXX")

**No data showing:**
- Verify `county_capacity.csv` exists in `data/processed/`
- Check file contains both 2025 and 2029 data
- Ensure CSV has required columns (county_fips, county_name, year, age_group, etc.)

**County detail view empty:**
- Verify `childcare_facilities.csv` exists in `data/raw/`
- Check that county names match between datasets (title case: "Adams", not "ADAMS")

**Performance issues:**
- Clear Streamlit cache: Press 'C' in the browser
- Reduce data size by filtering to specific counties
- Check system memory usage

## Future Enhancements

Potential improvements for future iterations:
- Click-to-select counties directly on the map
- Trend charts showing gap changes over time
- Provider density heat maps
- Downloadable PDF reports
- Email alerts for critical counties
- Integration with additional data sources (income, transportation access)
