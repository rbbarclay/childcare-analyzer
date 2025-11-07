# Product Requirements Document
## Colorado Early Childhood Capacity Analyzer - Prototype v0.1

**Document Owner**: Product Team  
**Last Updated**: November 6, 2025  
**Status**: Ready for Development

---

## 1. EXECUTIVE SUMMARY

The Colorado Early Childhood Capacity Analyzer is a web-based data application designed to help the Colorado Department of Early Childhood identify and prioritize gaps in childcare and pre-K capacity across the state.

**Primary User**: Executive Director, Colorado Department of Early Childhood  
**Primary Use Case**: Identify which communities are underserved to effectively allocate resources and partner with communities

**Key Features**:
- Interactive map showing capacity gaps by county
- Forecasting capacity needs 4 years ahead
- Prioritized list of gaps to address
- Demographic breakdown by location, race, and age

---

## 2. PROBLEM STATEMENT

State officials lack clear visibility into which Colorado communities have insufficient childcare/pre-K capacity. Current processes rely on:
- Manual spreadsheet analysis across multiple data sources
- Anecdotal reports from regions
- Reactive responses when crises occur
- Inability to see demographic equity gaps in aggregate data

This leads to:
- Inefficient resource allocation
- Delayed responses to community needs
- Potential inequitable distribution of services
- Missed opportunities for proactive planning

---

## 3. SUCCESS CRITERIA

**Prototype Success** (2 weeks from delivery):
- ✅ Executive Director uses tool in at least one decision-making meeting
- ✅ Tool identifies at least 3 actionable insights not previously known
- ✅ Director approves continued development OR provides clear feedback

**Usage Metrics**:
- Logins per month
- Counties explored
- Filters applied
- CSV exports downloaded

---

## 4. USER PERSONAS

### Primary: Sarah - Executive Director
- **Role**: Colorado Department of Early Childhood Executive Director
- **Goals**: Allocate resources effectively, demonstrate impact to legislature, ensure equity
- **Pain Points**: Too much fragmented data, decisions feel reactive, unclear where to focus
- **Technical Proficiency**: Moderate (comfortable with dashboards, not a data analyst)
- **Use Context**: Quarterly planning meetings, budget requests, responding to community concerns

### Secondary: Marcus - Policy Analyst  
- **Role**: Senior Policy Analyst
- **Goals**: Provide accurate analysis, identify trends, support evidence-based recommendations
- **Pain Points**: Manual compilation takes days, hard to update forecasts, can't compare scenarios
- **Technical Proficiency**: High (Excel power user, some SQL/Python)
- **Use Context**: Deep-dive analysis, briefing materials, data requests

---

## 5. CORE USER STORIES

### Epic 1: Understand Current Capacity Gaps

**US-1.1**: As an Executive Director, I want to see a map of Colorado showing capacity gaps by county so that I can quickly identify which regions need attention.

**Acceptance Criteria:**
- Map displays all 64 Colorado counties
- Counties are color-coded by gap severity (see scale below)
- Clicking a county displays key stats in a side panel
- Map loads in < 3 seconds

**Gap Severity Scale:**
- 🔴 Critical (Red): >30% of children lack access
- 🟠 Significant (Orange): 20-30% gap
- 🟡 Moderate (Yellow): 10-20% gap
- 🟢 Low (Light Green): 5-10% gap  
- 🟢 Adequate (Green): <5% gap

---

**US-1.2**: As a Policy Analyst, I want to see a ranked list of counties with the largest capacity gaps so that I can prioritize detailed analysis.

**Acceptance Criteria:**
- Table shows top 20 counties by absolute number of children underserved
- Columns: County Name, Total Gap (# children), Gap %, Population Under 5, Licensed Capacity
- Sortable by any column
- Exportable to CSV

---

**US-1.3**: As an Executive Director, I want to filter the view by age group (infants/toddlers 0-2 vs. pre-K 3-5) so that I can understand where different types of capacity are needed.

**Acceptance Criteria:**
- Toggle buttons: "Ages 0-2" | "Ages 3-5" | "All Ages 0-5"
- Map and list update dynamically when toggled
- Current selection is visually indicated
- Data calculations adjust appropriately (different capacity ratios by age)

---

### Epic 2: Forecast Future Needs

**US-2.1**: As an Executive Director, I want to see projected capacity gaps for 4 years from now so that I can plan proactively.

**Acceptance Criteria:**
- Time period selector: "Current (2025)" | "Forecast (2029)"
- Map and list update to show forecasted data
- Forecast assumes current capacity remains constant (note this assumption visibly)
- Clear indication when viewing forecast vs. current

---

**US-2.2**: As a Policy Analyst, I want to see how the gap in a specific county will change over time so that I can assess urgency.

**Acceptance Criteria:**
- County detail view includes simple line chart
- X-axis: years (2025-2029)
- Y-axis: gap size (# of children)
- Shows two lines: forecasted need, current capacity (flat line)

---

### Epic 3: Understand Demographic Equity

**US-3.1**: As an Executive Director, I want to see capacity gaps broken down by race/ethnicity for a selected county so that I can understand equity issues.

**Acceptance Criteria:**
- County detail view includes demographic table
- Shows: Population count and % by race/ethnicity, gap by race/ethnicity (if data available)
- Race/ethnicity categories match Census categories
- Clear note if demographic-specific capacity data unavailable

---

### Epic 4: Research & Context

**US-4.1**: As a Policy Analyst, I want to see a list of all licensed childcare providers in a selected county so that I can understand the landscape.

**Acceptance Criteria:**
- Searchable table: Provider Name, Address, Type (Center/Home), Licensed Capacity (by age group)
- Filterable by provider type
- Shows data source and last updated date

---

## 6. FUNCTIONAL REQUIREMENTS

### 6.1 Data Processing

**REQ-1**: Calculate licensed capacity by county and age group
- Aggregate facility-level capacity data
- Age groups: 0-2 years, 3-5 years, 0-5 years combined
- Handle facilities with mixed age groups

**REQ-2**: Calculate capacity need using standard ratios
- Ages 0-2: Assume 60% of population needs care (working parents proxy)
- Ages 3-5: Assume 70% of population needs care (higher pre-K participation)
- NOTE: These are assumptions for prototype; should be validated with domain experts

**REQ-3**: Calculate gap = need - supply for each county
- Gap expressed as absolute number and percentage
- Flag negative gaps (oversupply) separately

**REQ-4**: Generate 4-year forecasts
- Use population projection data by county and age
- Assume current capacity remains constant (note this assumption)
- Calculate future gaps using same need ratios

### 6.2 Visualization & Interaction

**REQ-5**: Render interactive choropleth map
- Colorado county boundaries
- Color scale for gap severity (5 levels)
- Hover tooltips with quick stats
- Click to select county and show detail view

**REQ-6**: Display county detail panel
- Key metrics: population, capacity, gap (# and %)
- Demographic breakdown table (if data available)
- List of providers in county
- Time-series chart (if forecast view)

**REQ-7**: Provide data export functionality
- Export filtered tables to CSV
- Include metadata (filters applied, export date)

**REQ-8**: Display data freshness indicators
- Show "Data as of [date]" for each source
- Flag if data is >6 months old

---

## 7. NON-FUNCTIONAL REQUIREMENTS

**Performance**
- NFR-1: Initial page load < 5 seconds
- NFR-2: Map interactions (pan, zoom, filter) feel responsive (< 1 sec)
- NFR-3: Handle all 64 Colorado counties without performance degradation

**Usability**
- NFR-4: Accessible via modern web browsers (Chrome, Firefox, Safari, Edge)
- NFR-5: Responsive design (works on laptop, tablet; mobile is nice-to-have)
- NFR-6: No login required for prototype

**Maintainability**
- NFR-7: Code should be well-commented for future development
- NFR-8: Data refresh process should be documented step-by-step

---

## 8. TECHNICAL STACK

**Frontend & Application Framework**
- **Streamlit**: Python-based web framework for rapid prototyping
- Rationale: Fastest path to interactive dashboard, no separate frontend/backend needed

**Data Processing**
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

**Visualization**
- **Plotly**: Interactive charts and choropleth maps
- Rationale: Native Streamlit integration, excellent interactivity

**Geospatial**
- **GeoPandas**: Geographic data handling (optional, for advanced features)

**Data Storage** (Prototype)
- **CSV/Parquet files**: Processed data stored locally
- **No database required**: Simplifies deployment for prototype

**Deployment**
- **Streamlit Cloud** (recommended): Free hosting for Streamlit apps
- Alternative: Heroku, Render, Railway, or local deployment

---

## 9. DATA SOURCES

### Primary Sources (Essential)

**1. Child Care Facility Data**
- **Source**: data.colorado.gov - "Child Care Facility and Licensed Capacity"
- **Provides**: Facility location, type, licensed slots by age
- **Assessment**: Essential - this is supply data
- **Refresh**: Quarterly

**2. Population Data (Current)**
- **Source**: U.S. Census Bureau - American Community Survey (ACS)
- **Table**: B01001 (Sex by Age) at county level
- **Provides**: Population by age cohorts (under 5, by single year)
- **Assessment**: Essential - this is demand data

**3. Population Forecasts**
- **Source**: Colorado State Demography Office (data.colorado.gov)
- **Provides**: Projected population for 2025-2029 by county and age
- **Assessment**: Essential - enables forecast feature

### Secondary Sources (For Enhanced Features)

**4. Demographic Data**
- **Source**: Census ACS - Table B03002 (Hispanic/Latino by Race)
- **Assessment**: Important for equity analysis

**5. Poverty Data**
- **Source**: Census ACS - Table B17024 (Age by Poverty Status)
- **Assessment**: Helps identify vulnerable populations

---

## 10. DATA SCHEMA

### Table: county_capacity

| Field | Type | Description |
|-------|------|-------------|
| county_name | string | Colorado county name |
| county_fips | string | 5-digit FIPS code |
| year | integer | Year of data (2025, 2026, etc.) |
| age_group | string | "0-2", "3-5", or "0-5" |
| population | integer | Number of children in age group |
| licensed_capacity | integer | Total licensed slots |
| need_estimate | integer | Estimated # children needing care |
| gap | integer | need_estimate - licensed_capacity |
| gap_pct | float | gap / need_estimate |

### Table: providers

| Field | Type | Description |
|-------|------|-------------|
| provider_id | string | Unique identifier |
| name | string | Facility name |
| county | string | County |
| address | string | Full address |
| type | string | "Center" or "Home" |
| capacity_0_2 | integer | Licensed capacity ages 0-2 |
| capacity_3_5 | integer | Licensed capacity ages 3-5 |
| latitude | float | For mapping (if available) |
| longitude | float | For mapping (if available) |

### Table: county_demographics (optional)

| Field | Type | Description |
|-------|------|-------------|
| county_name | string | Colorado county name |
| year | integer | Year of data |
| age_group | string | Age cohort |
| race_ethnicity | string | Census category |
| population | integer | Count |

---

## 11. CALCULATIONS & ASSUMPTIONS

### Capacity Need Formula

```
need_estimate = population × participation_rate

Where:
- population = number of children in age group in county
- participation_rate = 
    - 0.60 (60%) for ages 0-2
    - 0.70 (70%) for ages 3-5
```

### Gap Calculation

```
gap = need_estimate - licensed_capacity
gap_pct = gap / need_estimate

Interpretation:
- Positive gap = shortage (need exceeds supply)
- Negative gap = oversupply (supply exceeds need)
```

### Severity Classification

```
if gap_pct > 0.30: severity = "Critical"
elif gap_pct > 0.20: severity = "Significant"
elif gap_pct > 0.10: severity = "Moderate"
elif gap_pct > 0.05: severity = "Low"
else: severity = "Adequate"
```

### Forecast Assumption

```
forecast_gap(year) = forecast_need(year) - current_capacity

Note: Assumes capacity remains constant at 2025 levels
This is a conservative assumption that highlights growing needs
```

---

## 12. USER INTERFACE STRUCTURE

### Main Dashboard Page

**Header Section**
- Application title: "Colorado Early Childhood Capacity Analyzer"
- Links: [About] [Data Sources] [Export]

**Filter Section**
- Age Group: Radio buttons for "All (0-5)" | "Ages 0-2" | "Ages 3-5"
- Time Period: Radio buttons for "Current (2025)" | "Forecast (2029)"

**Content Section (Two Columns)**

**Left Column (60% width): Interactive Map**
- Choropleth map of Colorado counties
- Color-coded by gap severity
- Legend showing severity scale
- Hover tooltips with quick stats
- Click to select county

**Right Column (40% width): County Rankings**
- Title: "Top 20 Counties by Gap"
- Sortable table with columns:
  - Rank
  - County Name
  - Gap (# children)
  - Gap %
  - Population (0-5)
  - Licensed Capacity
- Load more button (for counties beyond top 20)
- Export to CSV button

### County Detail Page

**Navigation**
- Back to Map button
- County Name as header

**Summary Statistics (Cards)**
- Population (ages 0-5)
- Licensed Capacity  
- Estimated Need
- GAP (highlighted, # and %)

**Time Series Chart** (if forecast mode)
- Line chart: years (2025-2029) vs. gap size
- Two lines: forecasted need, current capacity

**Demographics Table**
- Race/Ethnicity breakdown
- Population count and percentage
- Gap by demographic (if available)

**Provider List**
- Search/filter box
- Table: Name, Type, Address, Capacity 0-2, Capacity 3-5
- Sortable columns

### About Page

**Sections**:
- Purpose of the tool
- Methodology & calculations
- Data sources with links
- Assumptions & limitations
- Last updated date
- Contact information

---

## 13. IMPLEMENTATION PHASES

### Phase 1: Setup & Data Pipeline (Days 1-2)
- [ ] Set up project structure
- [ ] Create sample/mock data for development
- [ ] Build data processing functions (calculate gaps)
- [ ] Create county_capacity and providers datasets
- [ ] Validate calculations with sample data

### Phase 2: Basic UI (Days 3-4)
- [ ] Set up Streamlit app structure
- [ ] Create filter controls (age group, time period)
- [ ] Build county rankings table with sorting
- [ ] Implement CSV export functionality
- [ ] Add basic styling

### Phase 3: Map Visualization (Days 5-6)
- [ ] Create Colorado county GeoJSON
- [ ] Build Plotly choropleth map
- [ ] Implement color-coding by severity
- [ ] Add hover tooltips
- [ ] Connect map to filters (reactivity)

### Phase 4: County Detail View (Days 7-8)
- [ ] Create county selection mechanism (from map click)
- [ ] Build county detail page layout
- [ ] Display summary statistics
- [ ] Show provider list for selected county
- [ ] Add time series chart for forecast view

### Phase 5: Demographics & Polish (Days 9-10)
- [ ] Integrate demographic data (if available)
- [ ] Add demographic breakdown table to county detail
- [ ] Create About page with methodology
- [ ] Add data freshness indicators
- [ ] Final testing and bug fixes

### Phase 6: Deploy & Document (Days 11-12)
- [ ] Deploy to Streamlit Cloud (or chosen platform)
- [ ] Create user guide (1-2 pages)
- [ ] Document data refresh process
- [ ] Prepare demo for stakeholders
- [ ] Gather initial feedback

---

## 14. OUT OF SCOPE (Prototype v0.1)

**Explicitly NOT included:**
- ❌ User authentication/authorization
- ❌ Write-back capability (commenting, annotation)
- ❌ Real-time data updates (manual refresh only)
- ❌ Mobile-optimized interface
- ❌ Affordability/cost analysis
- ❌ Quality ratings integration
- ❌ Sub-county geographic analysis (zip codes, census tracts)
- ❌ Transportation/drive-time modeling
- ❌ Waitlist or actual enrollment data
- ❌ Multi-state comparison
- ❌ Advanced forecasting (scenarios, what-if modeling)
- ❌ Integration with other state systems
- ❌ Historical trend analysis (before 2025)

---

## 15. RISKS & MITIGATIONS

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Data quality issues (missing, outdated) | High | Medium | Thorough data audit upfront; document limitations clearly |
| Capacity need assumptions are wrong | High | Medium | Make assumptions transparent; get expert validation; allow adjustment |
| User finds prototype too simplistic | Medium | Low | Set expectations that this is proof-of-concept |
| Data refresh too manual | Medium | High | Document process; plan automation in v1.0 |
| Population forecasts unavailable | High | Low | Check immediately; fallback to simple projection |
| No demographic capacity data | Medium | Medium | Show demographic need only; note as future enhancement |

---

## 16. ACCEPTANCE CRITERIA (Prototype Complete)

The prototype is ready for stakeholder demo when:

✅ Map displays all 64 counties with color-coded gaps  
✅ User can toggle between age groups and time periods  
✅ Top 20 gap list updates dynamically with filters  
✅ Clicking a county shows detail panel with key stats  
✅ Forecast view shows 4-year projection  
✅ Provider list displays for selected county  
✅ Data can be exported to CSV  
✅ "About" page documents methodology and limitations  
✅ Application is deployed and accessible via URL  
✅ Basic user guide exists (1-2 pages)

---

## 17. GLOSSARY

- **Licensed Capacity**: The maximum number of children a facility is legally permitted to serve
- **Gap**: The difference between estimated need and available licensed capacity
- **Need Estimate**: Population × participation rate assumption
- **Capacity Ratio / Participation Rate**: The assumed percentage of a population cohort that requires childcare/pre-K services
- **Oversupply**: When licensed capacity exceeds estimated need (negative gap)
- **Severity**: Classification of gap size (Critical, Significant, Moderate, Low, Adequate)
- **Forecast**: Projection of future capacity gaps based on population growth

---

## 18. APPENDIX: SAMPLE CALCULATIONS

### Example: Denver County, Ages 3-5, Current Year

**Given:**
- Population ages 3-5: 20,000 children
- Licensed capacity (aggregated): 15,000 slots
- Participation rate: 70%

**Calculations:**
1. Estimated need = 20,000 × 0.70 = 14,000 slots needed
2. Gap = 14,000 - 15,000 = -1,000 (oversupply)
3. Gap % = -1,000 / 14,000 = -7.1%
4. Severity = "Adequate" (gap < 5%)

**Interpretation**: Denver County has adequate capacity for ages 3-5 in the current year, with a slight oversupply.

### Example: Rural County, Ages 0-2, Forecast 2029

**Given:**
- Current population ages 0-2 (2025): 500 children
- Forecast population ages 0-2 (2029): 600 children
- Current licensed capacity: 200 slots
- Participation rate: 60%

**Calculations:**
1. Current need (2025) = 500 × 0.60 = 300 slots
2. Current gap = 300 - 200 = 100 children (33% gap)
3. Forecast need (2029) = 600 × 0.60 = 360 slots
4. Forecast gap = 360 - 200 = 160 children (44% gap)
5. Severity = "Critical" (gap > 30%)

**Interpretation**: This rural county has a critical shortage now that will worsen significantly by 2029 if capacity doesn't increase.

---

**End of PRD**
