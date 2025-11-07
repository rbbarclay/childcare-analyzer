# Colorado Early Childhood Capacity Analyzer

**A data application to help state officials identify and prioritize gaps in childcare and pre-K capacity across Colorado.**

---

## Overview

The Colorado Early Childhood Capacity Analyzer is a web-based tool designed to answer the critical question: **"Where are Colorado's childcare capacity gaps, and which communities should we prioritize?"**

### Key Features

🗺️ **Interactive Map** - Visual heat map of capacity gaps across all 64 Colorado counties

📊 **Prioritized Gap Analysis** - Ranked list of counties with the largest shortages

🔮 **4-Year Forecasting** - Proactive planning with population-based projections

🎯 **Demographic Insights** - Equity analysis by location, race, and age

📈 **County Deep-Dives** - Detailed views with provider lists and trend analysis

---

## The Problem

State officials currently lack clear visibility into childcare capacity gaps. Decision-making relies on:
- Manual spreadsheet analysis across fragmented data sources
- Anecdotal reports from regional offices
- Reactive responses to crises
- Difficulty identifying demographic inequities

This leads to inefficient resource allocation and missed opportunities for proactive planning.

---

## The Solution

This tool combines:
- **Childcare facility licensing data** (supply)
- **Census population data** (demand)
- **Population forecasts** (future demand)

...into a single, interactive dashboard that makes capacity gaps visible, measurable, and actionable.

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Census API key (free from https://api.census.gov/data/key_signup.html)

### Installation

```bash
# Clone the repository
git clone [repository-url]
cd childcare-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Census API key
export CENSUS_API_KEY='your_key_here'

# Run the data pipeline to fetch real data
python data_pipeline/run_data_pipeline.py

# Launch the Streamlit app (when UI is built)
streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`

### Data Setup

**Current Status:**
- ✅ **GeoJSON**: Colorado county boundaries automatically downloaded
- ⚠️ **Census API**: Requires free API key (get at https://api.census.gov/data/key_signup.html)
- 🔍 **Childcare Data**: Manual research needed on data.colorado.gov
- ⚠️ **Forecasts**: Optional (has simple projection fallback)

See `data_pipeline/DATA_SOURCES_RESEARCH.md` for detailed data setup instructions.

---

## Project Structure

```
co-childcare-analyzer/
│
├── data/
│   ├── raw/                    # Raw source data (gitignored)
│   ├── processed/              # Cleaned, calculated data for app
│   └── geo/                    # Geographic boundaries (GeoJSON)
│
├── data_pipeline/
│   ├── ingest.py              # Data download/fetch scripts
│   ├── clean.py               # Data cleaning & standardization
│   ├── calculate.py           # Gap calculations & forecasting
│   ├── export.py              # Save processed datasets
│   └── run_pipeline.py        # Main pipeline orchestrator
│
├── app/
│   ├── app.py                 # Main Streamlit application
│   ├── components/            # Reusable UI components
│   └── utils.py               # Helper functions
│
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   ├── LEAN_CANVAS.md         # Business model canvas
│   ├── DATA_SCHEMA.md         # Technical specifications
│   └── USER_GUIDE.md          # End-user documentation
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## How It Works

### 1. Data Collection
- Downloads childcare facility data from Colorado Open Data Portal
- Fetches population data from US Census Bureau
- Retrieves population forecasts from Colorado State Demography Office

### 2. Gap Calculation

```
need_estimate = population × participation_rate
gap = need_estimate - licensed_capacity
```

**Participation Rates:**
- Ages 0-2: 60% (assumes 60% of families need care)
- Ages 3-5: 70% (higher due to pre-K participation)

### 3. Visualization
- Counties color-coded by gap severity
- Interactive filters (age group, time period)
- Detailed county views with provider lists

---

## Key Concepts

### Gap Severity Scale

| Severity | Gap Percentage | Color | Meaning |
|----------|---------------|-------|---------|
| **Critical** | >30% | 🔴 Red | Severe shortage (1 in 3 children lack access) |
| **Significant** | 20-30% | 🟠 Orange | Major shortage |
| **Moderate** | 10-20% | 🟡 Yellow | Noticeable gap |
| **Low** | 5-10% | 🟢 Light Green | Minor gap |
| **Adequate** | <5% | 🟢 Green | Reasonable match |

### Age Groups
- **Ages 0-2**: Infants and toddlers (center-based or home-based care)
- **Ages 3-5**: Pre-K aged children (preschool programs)
- **Ages 0-5**: Combined view of all early childhood

### Time Periods
- **Current (2025)**: Today's capacity gaps
- **Forecast (2029)**: Projected gaps assuming constant capacity

---

## Data Sources

### Primary Sources

1. **Child Care Facilities**
   - Source: Colorado Department of Early Childhood via data.colorado.gov
   - Provides: Facility locations, types, licensed capacity by age

2. **Population Data**
   - Source: US Census Bureau - American Community Survey
   - Provides: Current population by county and age

3. **Population Forecasts**
   - Source: Colorado State Demography Office
   - Provides: Projected population growth by county

### Data Quality Notes
- Facility data refreshed quarterly
- Some counties may have incomplete capacity data
- Demographic-specific capacity data not currently available

---

## Assumptions & Limitations

### Key Assumptions
✓ Participation rates (60% for 0-2, 70% for 3-5) are estimates  
✓ Licensed capacity ≠ actual enrollment  
✓ Forecasts assume current capacity remains constant  
✓ All licensed slots treated as equally accessible  

### Known Limitations
⚠️ No affordability analysis (cost barriers not reflected)  
⚠️ No quality differentiation (all licensed capacity weighted equally)  
⚠️ County-level only (doesn't capture drive time or local access)  
⚠️ No waitlist or actual demand data  
⚠️ No special needs capacity tracking  

See `docs/DATA_SCHEMA.md` for complete technical details.

---

## Documentation

- **[PRD.md](docs/PRD.md)** - Complete product requirements and user stories
- **[LEAN_CANVAS.md](docs/LEAN_CANVAS.md)** - Business model and validation plan
- **[DATA_SCHEMA.md](docs/DATA_SCHEMA.md)** - Technical specifications and data models
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - End-user documentation (to be created)

---

## Technology Stack

- **Framework**: Streamlit (Python web framework)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly (interactive charts and maps)
- **Geospatial**: GeoPandas (optional)
- **Storage**: CSV files (prototype), scalable to database

---

## Development Status

### ✅ Phase 1: Data Infrastructure (IN PROGRESS)
- [x] Project structure created
- [x] GeoJSON fetcher working (64 Colorado counties)
- [x] Census API fetcher ready (requires API key)
- [x] Forecast fetcher ready (with fallback)
- [ ] Identify Colorado childcare dataset on data.colorado.gov
- [ ] Data cleaning and processing pipeline
- [ ] Gap calculation engine
- [ ] Generate county_capacity.csv

### 📋 Phase 2: Streamlit UI (NEXT)
- [ ] Basic app layout with filters
- [ ] Interactive choropleth map
- [ ] County rankings table
- [ ] County detail views
- [ ] CSV export functionality

### 📋 Phase 3: Polish & Deploy (FUTURE)
- [ ] About page with methodology
- [ ] Data quality validation
- [ ] Testing and bug fixes
- [ ] Deploy to Streamlit Cloud
- [ ] User documentation

---

## Contributing

This is currently a rapid prototype for stakeholder validation. Future contributions may include:

- Data quality improvements
- Additional visualizations
- Enhanced forecasting models
- Integration with other state systems
- Multi-state expansion

---

## License

[To be determined based on stakeholder requirements]

---

## Contact

For questions or feedback:
- Project Owner: [Your Name/Organization]
- Email: [Your Email]
- Colorado Department of Early Childhood: [Contact Info]

---

## Acknowledgments

- Colorado Department of Early Childhood
- Colorado State Demography Office
- US Census Bureau
- Colorado Open Data Portal

---

## Version History

- **v0.1** (November 2025) - Initial prototype with sample data
- **v0.2** (TBD) - Integration with real data sources
- **v1.0** (TBD) - Production release

---

**Last Updated**: November 6, 2025
