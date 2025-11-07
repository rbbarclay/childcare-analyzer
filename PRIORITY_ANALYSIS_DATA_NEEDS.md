# Priority Analysis - Missing Data Sources

## Overview

This document outlines the data sources needed to implement **Phase 2: Equity & Vulnerability Analysis** for the Colorado Early Childhood Capacity Analyzer. These datasets will enable equity-weighted prioritization to ensure resources reach the most vulnerable communities.

---

## ✅ Currently Available Data

We have already integrated:
- ✅ **Population**: US Census ACS 2022 (ages 0-5 by county)
- ✅ **Population Forecasts**: CO DOLA projections through 2050
- ✅ **Licensed Capacity**: CO Open Data childcare facilities (Oct 2025)
- ✅ **Geographic Boundaries**: GeoJSON for all 64 counties
- ✅ **Gap Growth Rates**: Calculated from 2025→2029 projections

---

## 🔍 Missing Data Sources (Priority Order)

### 1. MEDIAN HOUSEHOLD INCOME (Critical - Easy to Obtain)

**Why Needed:**
- Indicates community economic capacity
- Helps identify counties where families can't afford care (even if slots exist)
- Key indicator for subsidy targeting

**Data Source:**
- **Source**: U.S. Census Bureau - American Community Survey (ACS)
- **Table**: B19013 (Median Household Income in the Past 12 Months)
- **API Variable**: `B19013_001E`
- **Geographic Level**: County
- **Latest Available**: ACS 5-Year Estimates 2022 (same as our population data)

**How to Get:**
```python
# Using Census API (we already have the key!)
url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,B19013_001E&for=county:*&in=state:08&key={CENSUS_API_KEY}"
```

**Example Values:**
- Douglas County: ~$132,000 (high-income, can co-invest)
- Alamosa County: ~$39,000 (low-income, needs subsidies)

**Integration Effort**: 30 minutes (similar to existing Census fetch)

---

### 2. CHILD POVERTY RATE (Critical - Easy to Obtain)

**Why Needed:**
- Direct measure of vulnerability for target population (children)
- Federal funding often tied to poverty thresholds
- Helps prioritize areas where families need subsidized care

**Data Source:**
- **Source**: U.S. Census Bureau - American Community Survey (ACS)
- **Table**: B17001 (Poverty Status in the Past 12 Months by Sex by Age)
- **API Variables**:
  - B17001_004E: Male, age 0-5, below poverty level
  - B17001_018E: Female, age 0-5, below poverty level
  - B17001_003E: Male, age 0-5, total (for denominator)
  - B17001_017E: Female, age 0-5, total (for denominator)
- **Geographic Level**: County
- **Latest Available**: ACS 5-Year Estimates 2022

**Calculation:**
```
Child Poverty Rate = (Below Poverty) / (Total Children 0-5) × 100
```

**How to Get:**
```python
url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,B17001_004E,B17001_018E,B17001_003E,B17001_017E&for=county:*&in=state:08&key={CENSUS_API_KEY}"
```

**Federal Thresholds:**
- <10%: Low poverty
- 10-20%: Moderate poverty
- >20%: High poverty (priority for funding)

**Integration Effort**: 45 minutes (need to fetch multiple variables and calculate)

---

### 3. SOCIAL VULNERABILITY INDEX (SVI) (High Priority - Moderate Effort)

**Why Needed:**
- Composite measure of community vulnerability (15 social factors)
- Used by CDC and FEMA for disaster/resource allocation
- Includes factors beyond income: unemployment, disability, language barriers, transportation access

**Data Source:**
- **Source**: CDC/ATSDR Social Vulnerability Index
- **Dataset**: 2022 SVI (latest)
- **URL**: https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html
- **Geographic Level**: County (and census tract for detailed analysis)
- **File Format**: CSV, Geodatabase, or Shapefile

**Key Metrics in SVI:**
- Socioeconomic Status (poverty, unemployment, per capita income, no high school diploma)
- Household Composition & Disability (aged 65+, aged 17 or younger, disability, single-parent households)
- Minority Status & Language (minority, speaks English "less than well")
- Housing Type & Transportation (multi-unit structures, mobile homes, crowding, no vehicle, group quarters)

**Download Options:**
1. **Direct CSV**: https://svi.cdc.gov/data-and-tools-download.html
2. **API**: No official API, but data available via download

**File Structure:**
```csv
STATE,COUNTY,FIPS,E_TOTPOP,E_POV150,E_UNEMP,E_HBURD,E_NOHSDP,...,RPL_THEMES
Colorado,Adams,08001,519572,123456,12345,45678,23456,...,0.8542
```

**Key Field:**
- `RPL_THEMES`: Percentile ranking (0.0-1.0)
  - 0.75-1.0: High vulnerability (top 25%) → Priority!
  - 0.50-0.75: Moderate-high vulnerability
  - 0.25-0.50: Moderate vulnerability
  - 0.0-0.25: Low vulnerability

**Integration Effort**: 1-2 hours (download, filter to Colorado, map FIPS codes)

---

### 4. RACE/ETHNICITY DEMOGRAPHICS (Medium Priority - Easy to Obtain)

**Why Needed:**
- Identify communities of color that may face systemic barriers
- Ensure equitable resource distribution
- Some funding streams prioritize minority-serving areas

**Data Source:**
- **Source**: U.S. Census Bureau - American Community Survey (ACS)
- **Table**: B03002 (Hispanic or Latino Origin by Race)
- **API Variables**:
  - B03002_001E: Total population
  - B03002_003E: White alone, not Hispanic or Latino
  - B03002_012E: Hispanic or Latino (total)
  - B03002_004E: Black or African American alone
  - B03002_006E: Asian alone
  - B03002_005E: American Indian and Alaska Native alone
- **Geographic Level**: County
- **Latest Available**: ACS 5-Year Estimates 2022

**Calculation:**
```
Minority Population % = (Total - White Non-Hispanic) / Total × 100
```

**How to Get:**
```python
url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,B03002_001E,B03002_003E,B03002_012E&for=county:*&in=state:08&key={CENSUS_API_KEY}"
```

**Integration Effort**: 30 minutes (similar to median income)

---

### 5. RURAL/URBAN CLASSIFICATION (Medium Priority - Easy to Obtain)

**Why Needed:**
- Rural areas face unique challenges: provider recruitment, transportation, economies of scale
- Different intervention strategies for urban vs rural gaps
- Federal programs often have rural set-asides

**Data Source:**
- **Source**: USDA Economic Research Service
- **Dataset**: Rural-Urban Continuum Codes (RUCC)
- **URL**: https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/
- **Geographic Level**: County (FIPS code)
- **File Format**: Excel download

**Classification:**
- **1-3**: Metropolitan counties
  - 1: Metro, 1M+ population
  - 2: Metro, 250K-1M population
  - 3: Metro, <250K population
- **4-9**: Nonmetropolitan counties
  - 4-6: Urban population 2,500-20,000
  - 7-9: Completely rural or <2,500 urban

**Download:**
1. Visit: https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/
2. Download Excel file (updated 2023)
3. Filter to Colorado (State FIPS = 08)

**File Structure:**
```csv
FIPS,State,County_Name,Population_2010,RUCC_2013
08001,CO,Adams,441603,1
08003,CO,Alamosa,15445,6
```

**Integration Effort**: 30 minutes (download, filter, join on FIPS)

---

### 6. COMMUTING PATTERNS (Nice-to-Have - Moderate Effort)

**Why Needed:**
- Parents may work in one county but need childcare in another
- Helps understand regional labor markets
- Identifies counties that serve as "employment hubs"

**Data Source:**
- **Source**: U.S. Census Bureau - LEHD Origin-Destination Employment Statistics (LODES)
- **Dataset**: Workplace Area Characteristics (WAC) and Residence Area Characteristics (RAC)
- **URL**: https://lehd.ces.census.gov/data/
- **Geographic Level**: County (can go to census tract/block)
- **Latest Available**: 2021

**What It Shows:**
- Where people live vs. where they work
- Example: Many Elbert County residents commute to Denver for work → need childcare near Denver

**Download:**
```
# Colorado workplace data
https://lehd.ces.census.gov/data/lodes/LODES8/co/wac/co_wac_S000_JT00_2021.csv.gz
```

**Integration Effort**: 2-3 hours (complex dataset, needs spatial analysis)

---

### 7. CHILDCARE DESERTS EXISTING ANALYSIS (Optional - For Validation)

**Why Needed:**
- Validate our analysis against existing research
- Identify any methodological differences
- Leverage existing policy frameworks

**Data Source:**
- **Source**: Center for American Progress
- **Report**: "Mapping America's Childcare Deserts" (2018, updated periodically)
- **URL**: https://childcaredeserts.org/
- **Coverage**: National, county-level

**Definition of Childcare Desert:**
- >3 children per licensed slot
- Or census tracts with no licensed providers

**Use Case:**
- Compare our gap % metric to their "desert" classification
- Ensure we're not missing counties they've identified as critical

**Integration Effort**: 1 hour (review methodology, compare results)

---

## Implementation Roadmap

### Phase 2A: Quick Wins (2-3 hours total)

**Priority 1 - Income & Poverty (Census ACS)**
1. Fetch median household income (B19013_001E)
2. Fetch child poverty rate (B17001 variables)
3. Add to county detail view
4. Create "Low Income" filter (< $60k median)
5. Create "High Poverty" filter (> 15% child poverty)

**Deliverable:**
- Two new filters in sidebar
- Income/poverty displayed in county cards
- Flag counties where affordability is the barrier

---

### Phase 2B: Vulnerability Index (4-6 hours total)

**Priority 2 - Social Vulnerability Index**
1. Download CDC SVI 2022 data (CSV)
2. Filter to Colorado counties
3. Join on FIPS code
4. Add SVI percentile to dataset
5. Create "High Vulnerability" filter (SVI > 75th percentile)

**Priority 3 - Race/Ethnicity**
1. Fetch demographics (B03002 variables)
2. Calculate minority percentage
3. Add to county detail view
4. Create "Minority-Majority" filter (> 50% non-white)

**Deliverable:**
- SVI-based filtering
- Demographic profile in county cards
- Equity-weighted sorting option

---

### Phase 2C: Rural/Urban Context (1-2 hours)

**Priority 4 - RUCC Classification**
1. Download USDA RUCC data
2. Join on FIPS code
3. Add rural/urban flag to dataset
4. Create "Rural Counties" filter
5. Show different benchmarks for urban vs rural

**Deliverable:**
- Rural/urban classification visible
- Separate stats for metro vs non-metro

---

### Phase 2D: Advanced (Optional, 3-4 hours)

**Priority 5 - Composite Priority Score**
1. Calculate weighted score:
   - 35%: Gap severity
   - 35%: Growth rate
   - 15%: Equity (poverty + SVI)
   - 15%: Scale (absolute gap)
2. Rank counties by priority score
3. Create "Top 10 Priorities" dashboard

**Priority 6 - Commuting Patterns**
1. Download LODES data
2. Analyze cross-county commuting
3. Flag counties with high out-commuting

---

## Data Collection Scripts (Recommended)

Create new scripts in `data_pipeline/`:

### `fetch_equity_data.py`
```python
"""
Fetch equity and vulnerability data from Census and CDC
"""

def fetch_median_income():
    """Fetch B19013 from Census ACS"""
    pass

def fetch_child_poverty():
    """Fetch B17001 from Census ACS"""
    pass

def fetch_race_ethnicity():
    """Fetch B03002 from Census ACS"""
    pass

def download_svi_data():
    """Download and process CDC SVI CSV"""
    pass

def download_rucc_data():
    """Download and process USDA RUCC data"""
    pass
```

### `integrate_equity_metrics.py`
```python
"""
Integrate equity data with existing county_capacity.csv
"""

def merge_equity_data():
    """Join all equity metrics to county dataset"""
    pass

def calculate_equity_score():
    """Calculate composite equity concern score"""
    pass

def calculate_priority_score():
    """Calculate final priority ranking"""
    pass
```

---

## Estimated Total Effort

| Phase | Features | Data Sources | Time | Priority |
|-------|----------|--------------|------|----------|
| **Phase 2A** | Income & Poverty | Census ACS | 2-3 hrs | **HIGH** |
| **Phase 2B** | SVI & Demographics | CDC SVI, Census | 4-6 hrs | **HIGH** |
| **Phase 2C** | Rural/Urban | USDA RUCC | 1-2 hrs | **MEDIUM** |
| **Phase 2D** | Priority Score | Composite | 3-4 hrs | **MEDIUM** |
| **Phase 2E** | Commuting | LODES | 3-4 hrs | **LOW** |
| **Total** | Complete Equity Analysis | All sources | **13-19 hrs** | - |

---

## Quick Start: Next Steps

**This Week (2-3 hours):**
1. Reuse existing Census API key (we have it!)
2. Create `fetch_equity_data.py`
3. Fetch median income and child poverty
4. Add to county cards
5. Deploy updated dashboard

**You'll immediately be able to say:**
- "Weld County has critical gap (77.3%) + high growth (+29%) but median income $71k → families can contribute to solutions"
- "Alamosa County has moderate gap (34.5%) + median income $39k → needs heavy subsidies"

---

## Data Sources Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ QUICK ACCESS LINKS                                          │
├─────────────────────────────────────────────────────────────┤
│ Census API (Income, Poverty, Demographics)                  │
│ → https://api.census.gov/data/2022/acs/acs5                 │
│ → API Key: [already have it!]                               │
│                                                              │
│ CDC Social Vulnerability Index (SVI)                        │
│ → https://www.atsdr.cdc.gov/placeandhealth/svi/             │
│ → Direct Download: CSV, updated 2022                        │
│                                                              │
│ USDA Rural-Urban Continuum Codes (RUCC)                     │
│ → https://www.ers.usda.gov/data-products/rural-urban-con... │
│ → Excel download, updated 2023                              │
│                                                              │
│ LEHD Commuting Data (LODES)                                 │
│ → https://lehd.ces.census.gov/data/                         │
│ → CSV files by state                                        │
└─────────────────────────────────────────────────────────────┘
```

---

**Ready to implement Phase 2A?** All the data sources are publicly available and free. The Census API integration will be nearly identical to what we already built for population data!
