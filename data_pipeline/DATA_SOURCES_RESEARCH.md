# Data Sources Research Guide

This document helps identify and access the real data sources needed for the Colorado Early Childhood Capacity Analyzer.

---

## ✅ COMPLETED: Colorado County Boundaries

**Source**: Plotly Public Datasets (GitHub)
**URL**: https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json
**Status**: ✓ WORKING - Script successfully fetches all 64 Colorado counties
**Script**: `fetch_geojson.py`
**Output**: `data/geo/colorado_counties.geojson`

---

## 🔍 NEEDED: Census Population Data

**Source**: US Census Bureau - American Community Survey (ACS)
**Table**: B01001 - Sex by Age
**Geographic Level**: County (Colorado - FIPS 08)

### Access Method:

**Option 1: Census API (Recommended)**
- API Endpoint: `https://api.census.gov/data/2022/acs/acs5`
- **Requires**: Free API key from https://api.census.gov/data/key_signup.html
- **Status**: Script ready, needs API key
- **Script**: `fetch_census_data.py`

**Option 2: Manual Download**
- Visit: https://data.census.gov
- Navigate to: "Advanced Search" → "Topics" → "Age and Sex"
- Select: Table B01001 (Sex by Age)
- Geography: All Counties in Colorado
- Download as CSV

### Variables Needed:
- B01001_003E through B01001_008E (Male ages 0-5)
- B01001_027E through B01001_032E (Female ages 0-5)

**Action Required**: Get Census API key and set as environment variable

```bash
export CENSUS_API_KEY='your_key_here'
```

---

## 🔍 NEEDED: Colorado Childcare Facilities Data

**Source**: Colorado Department of Early Childhood via data.colorado.gov
**Expected Dataset**: "Child Care Facility and Licensed Capacity" or similar

### Research Steps:

1. **Visit**: https://data.colorado.gov
2. **Search terms to try**:
   - "child care facilities"
   - "licensed childcare"
   - "early childhood"
   - "day care"
   - "preschool"

3. **Look for dataset with**:
   - Facility name and address
   - County location
   - License status (Active/Inactive)
   - Licensed capacity (ideally by age group: 0-2, 3-5)
   - Provider type (Center vs. Home)

4. **Identify access method**:
   - Direct CSV download URL
   - Socrata API endpoint (format: `https://data.colorado.gov/resource/{id}.json`)
   - Excel/XLSX download

### Potential Dataset IDs to Check:

Check these on data.colorado.gov:
- Search "CDHS" (Colorado Department of Human Services - may have legacy data)
- Search "Department of Early Childhood"
- Look in "Health" or "Social Services" categories

### Once Found:

Update `fetch_childcare_data.py` with:
```python
# If Socrata API:
dataset_id = "XXXX-XXXX"  # Replace with actual ID
df = fetch_via_socrata_api(dataset_id)

# If direct CSV:
csv_url = "https://data.colorado.gov/..."
df = fetch_via_csv_url(csv_url)
```

**Action Required**: Manual research on data.colorado.gov to find correct dataset

---

## 🔍 NEEDED: Colorado Population Forecasts

**Source**: Colorado State Demography Office
**Website**: https://demography.dola.colorado.gov

### Research Steps:

1. **Visit**: https://demography.dola.colorado.gov

2. **Navigation paths to try**:
   - "Data" → "Downloads"
   - "Forecasts" or "Projections"
   - "County Profiles"

3. **Look for**:
   - County population forecasts by age
   - Years: 2025-2029 (or closest available)
   - Age groups: 0-5 or single-year ages

4. **Common file locations**:
   - Google Cloud Storage: `https://storage.googleapis.com/co-publicdata/demog/`
   - Download center on main site
   - County lookup tools

### Data Format Needed:

| County | Year | Age_Group | Population |
|--------|------|-----------|------------|
| Adams  | 2025 | 0-2       | 15000      |
| Adams  | 2025 | 3-5       | 18000      |
| ...    | ...  | ...       | ...        |

### Fallback Option:

If official forecasts unavailable, the pipeline can generate simple projections:
```python
from fetch_forecast_data import create_simple_forecast
forecast_df = create_simple_forecast(census_df, growth_rate=0.005)
```

This uses constant 0.5% annual growth (Colorado's approximate growth rate).

**Status**: Has fallback, but official data preferred

---

## Data Quality Checklist

Before proceeding to data processing, verify:

- [ ] **GeoJSON**: All 64 Colorado counties present ✓
- [ ] **Census**: All 64 counties with population ages 0-5
- [ ] **Childcare**: Facilities with county mapping and capacity data
- [ ] **Forecasts**: All 64 counties, years 2025-2029 (or use fallback)

---

## Next Steps After Data Collection

Once all data sources are identified and accessible:

1. Run `python data_pipeline/run_data_pipeline.py`
2. Verify all data downloaded to `data/raw/`
3. Proceed to data cleaning and processing
4. Generate `data/processed/county_capacity.csv`
5. Build Streamlit application

---

## Useful Links

- **Colorado Open Data Portal**: https://data.colorado.gov
- **Census API Docs**: https://www.census.gov/data/developers/data-sets.html
- **Census Data Explorer**: https://data.census.gov
- **CO State Demography**: https://demography.dola.colorado.gov
- **Socrata API Docs**: https://dev.socrata.com/

---

**Status**: 1 of 3 data sources fully automated (GeoJSON ✓)
**Action Needed**: Census API key + Manual research for childcare dataset
