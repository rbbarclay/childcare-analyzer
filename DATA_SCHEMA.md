# Data Schema & Technical Specifications
## Colorado Early Childhood Capacity Analyzer

**Version**: 1.0  
**Last Updated**: November 6, 2025

---

## 1. OVERVIEW

This document defines the data models, schemas, and technical specifications for the Colorado Early Childhood Capacity Analyzer prototype.

**Key Principles:**
- Keep data models simple and flat for prototype
- Use CSV files for storage (no database needed initially)
- Design for future scalability to database if needed
- Document all assumptions and calculations

---

## 2. DATA SOURCES

### Source 1: Child Care Facilities (Supply Data)

**Provider**: Colorado Department of Early Childhood via data.colorado.gov  
**Dataset**: "Child Care Facility and Licensed Capacity"  
**URL**: https://data.colorado.gov (search: "child care facilities")  
**Format**: CSV download or API  
**Update Frequency**: Quarterly (estimated)

**Key Fields Needed:**
- Facility Name
- License Number (unique ID)
- Address (Street, City, County, Zip)
- Facility Type (Center-Based, Family Child Care Home, etc.)
- Licensed Capacity by Age Group
  - Infants (0-12 months)
  - Toddlers (13-35 months)
  - Preschool (3-5 years)
  - School-Age (optional, not focus)

**Data Quality Notes:**
- May have missing/incomplete capacity data
- Some facilities may list total capacity without age breakdown
- Need to validate county names match our reference list

---

### Source 2: Population Data - Current (Demand Data)

**Provider**: U.S. Census Bureau - American Community Survey (ACS)  
**Dataset**: Table B01001 - Sex by Age  
**URL**: https://data.census.gov or Census API  
**Geographic Level**: County  
**Vintage**: 2019-2023 5-Year Estimates (most recent available)

**Key Fields Needed:**
- County FIPS code
- Age cohorts:
  - Under 1 year
  - 1 year
  - 2 years
  - 3 years
  - 4 years
  - 5 years

**Calculation Notes:**
- Ages 0-2 = sum(under 1, 1 year, 2 years)
- Ages 3-5 = sum(3 years, 4 years, 5 years)
- Ages 0-5 = sum(all above)

---

### Source 3: Population Forecasts (Future Demand)

**Provider**: Colorado State Demography Office  
**URL**: https://demography.dola.colorado.gov  
**Format**: Excel download or interactive tools  
**Forecast Horizon**: 2025-2029

**Key Fields Needed:**
- County name/FIPS
- Year (2025, 2026, 2027, 2028, 2029)
- Age groups (ideally single-year ages 0-5)
- Total population by age

**Fallback**: If detailed forecasts unavailable, use simple growth rate projection:
```
future_population = current_population × (1 + annual_growth_rate) ^ years
```

---

### Source 4: Demographics - Race/Ethnicity (Optional for v0.1)

**Provider**: U.S. Census Bureau - ACS  
**Dataset**: Table B03002 - Hispanic or Latino Origin by Race  
**Geographic Level**: County  

**Key Fields Needed:**
- County FIPS
- Race/Ethnicity categories:
  - Hispanic or Latino (of any race)
  - White alone, not Hispanic or Latino
  - Black or African American alone, not Hispanic or Latino
  - American Indian and Alaska Native alone, not Hispanic or Latino
  - Asian alone, not Hispanic or Latino
  - Native Hawaiian and Other Pacific Islander alone, not Hispanic or Latino
  - Two or More Races, not Hispanic or Latino
- Population by age cohort (0-5) if available, or total

**Note**: Demographic-specific capacity data likely unavailable; can only show need by demographics, not supply

---

### Source 5: Colorado County Reference Data

**Provider**: US Census Bureau or Colorado State GIS  
**Format**: GeoJSON or Shapefile  
**Purpose**: County boundaries for map visualization

**Key Fields Needed:**
- County Name
- County FIPS code (5-digit: state + county)
- Geometry (polygon coordinates)

**URL**: Can use public GeoJSON from:
- https://github.com/plotly/datasets/blob/master/geojson-counties-fips.json (national)
- Filter to Colorado counties (FIPS starting with "08")

---

## 3. DATA MODELS

### 3.1 County Capacity Dataset

**Filename**: `county_capacity.csv`  
**Purpose**: Core dataset with gap calculations for each county, age group, and year

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| county_fips | string | 5-digit FIPS code | "08031" |
| county_name | string | County name | "Denver" |
| year | integer | Year of data/forecast | 2025 |
| age_group | string | Age cohort | "0-2", "3-5", "0-5" |
| population | integer | # children in age group | 20000 |
| licensed_capacity | integer | Total licensed slots | 15000 |
| participation_rate | float | % needing care (assumption) | 0.70 |
| need_estimate | integer | Calculated need | 14000 |
| gap | integer | need - capacity | -1000 |
| gap_pct | float | gap / need | -0.071 |
| severity | string | Gap classification | "Adequate" |
| data_source | string | Where data came from | "ACS 2023, CO ECLDC" |
| last_updated | date | When data refreshed | "2025-11-06" |

**Notes:**
- Each county will have 3 rows per year (ages 0-2, 3-5, 0-5)
- For prototype, may have 2 years (2025, 2029)
- Total rows: 64 counties × 3 age groups × 2 years = 384 rows

---

### 3.2 Provider Dataset

**Filename**: `providers.csv`  
**Purpose**: Facility-level data for county drill-down views

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| provider_id | string | Unique identifier | "FAC12345" |
| facility_name | string | Name of facility | "Bright Beginnings Learning Center" |
| county_fips | string | County FIPS | "08031" |
| county_name | string | County name | "Denver" |
| address_street | string | Street address | "123 Main St" |
| address_city | string | City | "Denver" |
| address_zip | string | ZIP code | "80202" |
| facility_type | string | Type of facility | "Center" or "Home" |
| capacity_0_2 | integer | Licensed slots ages 0-2 | 24 |
| capacity_3_5 | integer | Licensed slots ages 3-5 | 36 |
| capacity_total | integer | Total slots | 60 |
| latitude | float | Latitude (if available) | 39.7392 |
| longitude | float | Longitude (if available) | -104.9903 |
| license_status | string | Active/Inactive/etc | "Active" |
| last_updated | date | Data refresh date | "2025-11-06" |

**Notes:**
- Estimated 3,000-5,000 providers statewide
- For prototype, may use subset or aggregated data if full list too large
- Lat/long optional but useful for future mapping features

---

### 3.3 County Demographics Dataset (Optional)

**Filename**: `county_demographics.csv`  
**Purpose**: Demographic breakdown for equity analysis

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| county_fips | string | County FIPS | "08031" |
| county_name | string | County name | "Denver" |
| year | integer | Year | 2025 |
| age_group | string | Age cohort | "0-5" |
| race_ethnicity | string | Demographic category | "Hispanic or Latino" |
| population | integer | Population count | 8000 |
| pct_of_county | float | % of county population | 0.40 |

**Notes:**
- Each county will have multiple rows (one per demographic category)
- For prototype, may only show aggregated 0-5 data (not broken down by single year)
- Gap by demographic will be calculated as: (population × participation_rate) - (total_capacity × assumed_distribution)
  - Assumption: capacity is distributed proportionally unless better data available

---

### 3.4 County Reference Dataset

**Filename**: `counties_colorado.geojson`  
**Purpose**: Geographic boundaries for map visualization

**GeoJSON Structure:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "GEOID": "08031",
        "NAME": "Denver",
        "STATEFP": "08",
        "COUNTYFP": "031"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-104.9903, 39.7392], ...]]
      }
    },
    // ... 63 more counties
  ]
}
```

**Source**: 
- Can download from US Census TIGER/Line or
- Use plotly's built-in county GeoJSON (filtered to Colorado)

---

## 4. CALCULATIONS & BUSINESS LOGIC

### 4.1 Capacity Need Estimation

**Formula:**
```
need_estimate = population × participation_rate

Where participation_rate =
  - 0.60 (60%) for age group "0-2"
  - 0.70 (70%) for age group "3-5"
  - Weighted average for age group "0-5"
```

**Rationale:**
- Not all families need full-time childcare (stay-at-home parents, informal care, etc.)
- Pre-K has higher participation rate (more universal, often free/subsidized)
- These are industry-standard proxies; validate with state experts

**Example (Ages 3-5):**
```python
population = 20000
participation_rate = 0.70
need_estimate = 20000 * 0.70 = 14000
```

---

### 4.2 Gap Calculation

**Formula:**
```
gap = need_estimate - licensed_capacity
gap_pct = gap / need_estimate
```

**Interpretation:**
- **Positive gap**: Shortage (need exceeds supply)
  - Example: gap = 5000 means 5,000 children lack access
- **Negative gap**: Oversupply (supply exceeds need)
  - Example: gap = -1000 means 1,000 excess slots
- **Zero gap**: Perfect match (rare)

**Example:**
```python
need_estimate = 14000
licensed_capacity = 15000
gap = 14000 - 15000 = -1000
gap_pct = -1000 / 14000 = -0.071 (-7.1%)
```

---

### 4.3 Severity Classification

**Rules:**
```python
if gap_pct > 0.30:
    severity = "Critical"      # Red
    color_code = "#d32f2f"
elif gap_pct > 0.20:
    severity = "Significant"   # Orange
    color_code = "#f57c00"
elif gap_pct > 0.10:
    severity = "Moderate"      # Yellow
    color_code = "#fbc02d"
elif gap_pct > 0.05:
    severity = "Low"           # Light Green
    color_code = "#9ccc65"
else:
    severity = "Adequate"      # Green
    color_code = "#66bb6a"
```

**Thresholds Rationale:**
- 30%+ gap = Critical (roughly 1 in 3 children can't access care)
- 20-30% = Significant (major shortage)
- 10-20% = Moderate (noticeable gap but manageable)
- 5-10% = Low (minor gap, may be frictional)
- <5% = Adequate (reasonable match)

**Note**: Negative gaps (oversupply) map to "Adequate" for visualization purposes

---

### 4.4 Forecast Calculation

**Assumption**: Current capacity remains constant (conservative)

**Formula:**
```
forecast_gap(year) = forecast_need(year) - current_capacity

Where:
  forecast_need(year) = forecast_population(year) × participation_rate
  current_capacity = licensed_capacity as of 2025
```

**Example:**
```python
# Current (2025)
population_2025 = 20000
participation_rate = 0.70
need_2025 = 20000 * 0.70 = 14000
capacity_2025 = 15000
gap_2025 = 14000 - 15000 = -1000 (adequate)

# Forecast (2029)
population_2029 = 23000  # from CO State Demography Office
need_2029 = 23000 * 0.70 = 16100
capacity_2029 = 15000  # ASSUMED constant
gap_2029 = 16100 - 15000 = 1100 (7% gap - "Low" severity)
```

**Interpretation**: Denver's adequate capacity becomes a shortage by 2029 if no new facilities open

---

### 4.5 Aggregation Rules

**County-Level Capacity:**
```sql
SELECT 
  county_fips,
  county_name,
  SUM(capacity_0_2) as total_capacity_0_2,
  SUM(capacity_3_5) as total_capacity_3_5
FROM providers
WHERE license_status = 'Active'
GROUP BY county_fips, county_name
```

**Handling Mixed-Age Facilities:**
- If a facility lists "total capacity" without age breakdown, use typical ratios:
  - 40% for ages 0-2
  - 60% for ages 3-5
- Document this assumption clearly

**Handling Missing Data:**
- If county has no provider data → capacity = 0 (flag as "data quality issue")
- If population data missing → exclude from analysis (should not happen for counties)

---

## 5. DATA PIPELINE ARCHITECTURE

### 5.1 Pipeline Overview

```
[Data Sources] → [Ingestion] → [Processing] → [Output Files] → [Streamlit App]
```

**Stages:**
1. **Ingestion**: Download/fetch raw data from sources
2. **Cleaning**: Standardize formats, handle missing data
3. **Calculation**: Compute gaps, severity, forecasts
4. **Export**: Save processed data to CSV/Parquet
5. **Visualization**: Load into Streamlit for display

---

### 5.2 Data Processing Scripts (Recommended Structure)

**File: `data_pipeline/ingest.py`**
- Download data from Colorado open data portal, Census API
- Save raw files to `data/raw/` directory
- Functions:
  - `fetch_childcare_facilities()`
  - `fetch_census_population()`
  - `fetch_population_forecasts()`

**File: `data_pipeline/clean.py`**
- Standardize county names (handle "Denver" vs "Denver County")
- Handle missing values
- Validate data types
- Functions:
  - `clean_facilities_data(df)`
  - `clean_population_data(df)`
  - `standardize_county_names(df)`

**File: `data_pipeline/calculate.py`**
- Aggregate provider capacity by county
- Calculate need estimates
- Calculate gaps and severity
- Generate forecasts
- Functions:
  - `calculate_county_capacity(facilities_df, population_df)`
  - `calculate_gaps(capacity_df)`
  - `classify_severity(gap_pct)`
  - `generate_forecasts(current_df, forecast_pop_df)`

**File: `data_pipeline/export.py`**
- Save processed datasets to `data/processed/`
- Generate metadata (last updated, source info)
- Functions:
  - `export_county_capacity(df)`
  - `export_providers(df)`

**File: `data_pipeline/run_pipeline.py`**
- Main orchestrator script
- Runs full pipeline end-to-end
- Usage: `python data_pipeline/run_pipeline.py`

---

### 5.3 Directory Structure

```
co-childcare-analyzer/
│
├── data/
│   ├── raw/                    # Raw downloaded data (not in version control)
│   │   ├── facilities_raw.csv
│   │   ├── population_acs.csv
│   │   └── population_forecast.csv
│   │
│   ├── processed/              # Cleaned, calculated data (for app to use)
│   │   ├── county_capacity.csv
│   │   ├── providers.csv
│   │   ├── county_demographics.csv
│   │   └── metadata.json
│   │
│   └── geo/                    # Geographic data
│       └── colorado_counties.geojson
│
├── data_pipeline/
│   ├── __init__.py
│   ├── ingest.py
│   ├── clean.py
│   ├── calculate.py
│   ├── export.py
│   └── run_pipeline.py
│
├── app/
│   ├── app.py                  # Main Streamlit application
│   ├── components/             # Reusable UI components
│   │   ├── map_view.py
│   │   ├── county_list.py
│   │   └── county_detail.py
│   └── utils.py                # Helper functions
│
├── tests/                      # Unit tests (optional for prototype)
│   └── test_calculations.py
│
├── docs/
│   ├── PRD.md
│   ├── LEAN_CANVAS.md
│   ├── DATA_SCHEMA.md          # This file
│   └── USER_GUIDE.md
│
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
└── .gitignore
```

---

## 6. SAMPLE DATA (For Development)

### 6.1 Sample County Capacity Data

For initial development, use realistic sample data:

| county_fips | county_name | year | age_group | population | licensed_capacity | participation_rate | need_estimate | gap | gap_pct | severity |
|-------------|-------------|------|-----------|------------|-------------------|--------------------|--------------|----|---------|----------|
| 08031 | Denver | 2025 | 0-2 | 15000 | 9000 | 0.60 | 9000 | 0 | 0.00 | Adequate |
| 08031 | Denver | 2025 | 3-5 | 20000 | 15000 | 0.70 | 14000 | -1000 | -0.07 | Adequate |
| 08041 | El Paso | 2025 | 0-2 | 18000 | 8000 | 0.60 | 10800 | 2800 | 0.26 | Significant |
| 08041 | El Paso | 2025 | 3-5 | 25000 | 13000 | 0.70 | 17500 | 4500 | 0.26 | Significant |
| 08013 | Boulder | 2025 | 0-2 | 6000 | 4500 | 0.60 | 3600 | -900 | -0.25 | Adequate |
| 08013 | Boulder | 2025 | 3-5 | 8000 | 7000 | 0.70 | 5600 | -1400 | -0.25 | Adequate |

### 6.2 Sample Provider Data

| provider_id | facility_name | county_name | address_city | facility_type | capacity_0_2 | capacity_3_5 |
|-------------|---------------|-------------|--------------|---------------|--------------|--------------|
| FAC001 | Bright Beginnings | Denver | Denver | Center | 24 | 36 |
| FAC002 | Little Steps Home | Denver | Denver | Home | 6 | 0 |
| FAC003 | Rainbow Learning | El Paso | Colorado Springs | Center | 30 | 45 |
| FAC004 | Tiny Tots Academy | Boulder | Boulder | Center | 18 | 27 |

---

## 7. DATA QUALITY & VALIDATION

### 7.1 Validation Checks

**Provider Data:**
- [ ] All providers have valid county assignment
- [ ] Capacity values are positive integers
- [ ] Sum of age-specific capacity ≤ total capacity (if both provided)
- [ ] No duplicate provider IDs
- [ ] License status is valid value

**Population Data:**
- [ ] All 64 Colorado counties present
- [ ] Population values are positive integers
- [ ] Age cohorts sum correctly
- [ ] No missing years in forecast data

**County Reference:**
- [ ] 64 counties in GeoJSON (Colorado has 64 counties)
- [ ] FIPS codes match population and provider data
- [ ] No invalid geometries

### 7.2 Data Quality Flags

Add flags to identify potential issues:

```python
# In county_capacity.csv
data_quality_flag = {
    "ok": No known issues,
    "low_capacity": capacity < 10 (likely data gap),
    "no_providers": capacity = 0,
    "missing_forecast": forecast data unavailable,
    "outlier": gap_pct > 80% or < -50% (extreme value)
}
```

### 7.3 Metadata Tracking

**File: `data/processed/metadata.json`**

```json
{
  "last_updated": "2025-11-06T10:30:00Z",
  "data_sources": {
    "childcare_facilities": {
      "source": "Colorado Open Data Portal",
      "url": "https://data.colorado.gov/...",
      "date_accessed": "2025-11-06",
      "rows": 3542
    },
    "population_current": {
      "source": "US Census ACS 2023",
      "vintage": "2019-2023 5-Year",
      "date_accessed": "2025-11-06"
    },
    "population_forecast": {
      "source": "CO State Demography Office",
      "forecast_year": 2029,
      "date_accessed": "2025-11-06"
    }
  },
  "assumptions": {
    "participation_rate_0_2": 0.60,
    "participation_rate_3_5": 0.70,
    "forecast_assumption": "Capacity constant at 2025 levels"
  },
  "data_quality": {
    "counties_with_data": 64,
    "counties_with_no_providers": ["Hinsdale", "Mineral"],
    "outliers_flagged": 3
  }
}
```

---

## 8. PERFORMANCE CONSIDERATIONS

### 8.1 Data Size Estimates

**County Capacity**: 
- 64 counties × 3 age groups × 5 years = 960 rows
- ~50 KB

**Providers**:
- Estimated 3,000-5,000 facilities statewide
- ~1-2 MB

**GeoJSON**:
- 64 counties with detailed boundaries
- ~500 KB - 1 MB

**Total Data Size**: < 5 MB (very manageable for Streamlit)

### 8.2 Loading Strategy

**On App Startup:**
- Load county_capacity.csv (primary dataset)
- Load colorado_counties.geojson (for map)
- Cache these in Streamlit session state

**On Demand:**
- Load providers.csv only when county detail view opened
- Filter to selected county to reduce memory

**Caching Decorator:**
```python
@st.cache_data
def load_county_capacity():
    return pd.read_csv('data/processed/county_capacity.csv')
```

---

## 9. API ENDPOINTS (Future Consideration)

If the tool evolves beyond prototype, consider REST API:

**GET `/api/counties`**
- Returns list of all counties with summary stats

**GET `/api/counties/{fips}/capacity`**
- Returns capacity data for specific county
- Query params: `year`, `age_group`

**GET `/api/counties/{fips}/providers`**
- Returns list of providers in county

**GET `/api/gaps/ranked`**
- Returns ranked list of counties by gap size
- Query params: `age_group`, `year`, `limit`

---

## 10. ASSUMPTIONS & LIMITATIONS

### Key Assumptions
1. **Participation rates** (60% for 0-2, 70% for 3-5) are proxies; actual need varies by family circumstances
2. **Licensed capacity** ≠ actual enrollment (facilities may not be full)
3. **Capacity remains constant** in forecasts (conservative assumption)
4. **All licensed slots are equally accessible** (ignores affordability, quality, location)
5. **Demographic capacity gaps** assume proportional distribution (may not reflect reality)

### Known Limitations
1. **No affordability analysis**: High-cost slots may not be accessible to low-income families
2. **No quality differentiation**: All licensed capacity treated equally regardless of quality ratings
3. **No geographic access modeling**: County-level analysis doesn't capture drive time or transportation barriers
4. **No waitlist data**: Can't see actual unmet demand
5. **No special needs capacity**: Doesn't identify capacity for children with disabilities

### Document These Prominently
- Include "About the Data" page in app
- Show assumptions in methodology section
- Flag limitations when presenting findings

---

## 11. GLOSSARY OF TERMS

| Term | Definition |
|------|------------|
| **Licensed Capacity** | Maximum number of children a facility is legally permitted to serve based on its license |
| **Need Estimate** | Calculated number of children requiring care (population × participation rate) |
| **Gap** | Difference between need estimate and licensed capacity (positive = shortage) |
| **Gap Percentage** | Gap divided by need estimate, expressed as percentage |
| **Severity** | Classification of gap size (Critical, Significant, Moderate, Low, Adequate) |
| **Participation Rate** | Assumed percentage of population cohort that requires childcare services |
| **Forecast** | Projection of future capacity gaps based on population growth |
| **FIPS Code** | Federal Information Processing Standard code - unique identifier for each county |
| **Age Cohort** | Specific age grouping (0-2, 3-5, 0-5) |
| **Facility Type** | Classification of childcare provider (Center-Based, Family Child Care Home, etc.) |

---

**End of Data Schema & Technical Specifications**
