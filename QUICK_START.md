# Quick Start: Building with Claude Code

This guide shows you how to use the project documentation to build the Colorado Early Childhood Capacity Analyzer using Claude Code or another AI coding assistant.

---

## Step 1: Gather Your Files

You should have these documentation files ready:

1. ✅ `README.md` - Project overview
2. ✅ `PRD.md` - Complete product requirements
3. ✅ `LEAN_CANVAS.md` - Business model
4. ✅ `DATA_SCHEMA.md` - Technical specifications
5. ✅ `IMPLEMENTATION_GUIDE.md` - Step-by-step build instructions
6. ✅ `requirements.txt` - Python dependencies
7. ✅ `.gitignore` - Git ignore rules

---

## Step 2: Initial Prompt for Claude Code

Copy and paste this prompt when starting with Claude Code:

```
I need you to build a rapid prototype web application called the "Colorado Early Childhood Capacity Analyzer". This tool will help state officials identify gaps in childcare and pre-K capacity across Colorado counties.

CORE FUNCTIONALITY:
- Display an interactive map of Colorado showing capacity gaps by county (color-coded by severity)
- Show a ranked list of counties with the largest gaps
- Allow filtering by age group (0-2, 3-5, all) and time period (current 2025, forecast 2029)
- Provide detailed county views with provider lists and demographic breakdowns
- Enable data export to CSV

TECHNICAL REQUIREMENTS:
- Use Python with Streamlit for the web interface
- Use Plotly for the interactive choropleth map
- Use Pandas for all data processing
- Start with sample/mock data initially - we'll integrate real data sources later
- Keep code modular and well-commented

ARCHITECTURE:
1. Data layer: Scripts to ingest, clean, and calculate capacity gaps
2. Business logic: Gap calculation engine (need estimate vs. licensed capacity)
3. Presentation layer: Streamlit UI with map, tables, filters, and detail views

I have comprehensive documentation including:
- PRD.md (Product Requirements Document)
- DATA_SCHEMA.md (Technical specifications)
- IMPLEMENTATION_GUIDE.md (Step-by-step build instructions)
- LEAN_CANVAS.md (Business context)

START BY:
1. Reading all the documentation files I'm providing
2. Creating the project structure with organized folders
3. Building the data processing pipeline with sample data
4. Creating the basic Streamlit app with the map and county list
5. Adding filtering and detail view functionality

Please confirm you understand the requirements, then propose a project structure and implementation plan.
```

---

## Step 3: Provide Documentation Files

After sending the initial prompt, provide these files to Claude Code:

**Primary files (must provide):**
1. `PRD.md` - For understanding features and requirements
2. `DATA_SCHEMA.md` - For data models and calculations
3. `IMPLEMENTATION_GUIDE.md` - For step-by-step instructions

**Supporting files (helpful but optional):**
4. `README.md` - For project context
5. `LEAN_CANVAS.md` - For understanding the business problem
6. `requirements.txt` - For Python dependencies

---

## Step 4: Development Phases

Work with Claude Code through these phases:

### Phase 1: Setup (30 minutes)
```
Create the project structure as outlined in IMPLEMENTATION_GUIDE.md.
Set up the directory structure, create __init__.py files, and set up requirements.txt.
```

### Phase 2: Sample Data (1-2 hours)
```
Create the sample data generator as specified in IMPLEMENTATION_GUIDE.md Section 2.1.
Generate realistic data for all 64 Colorado counties with varying gap severities.
Also fetch the Colorado counties GeoJSON for mapping.
```

### Phase 3: Data Processing (1-2 hours)
```
Implement the calculation functions in data_pipeline/calculate.py as specified in IMPLEMENTATION_GUIDE.md Section 2.3.
Include: calculate_need_estimate(), calculate_gap(), classify_severity().
```

### Phase 4: Basic App (2-3 hours)
```
Create the main Streamlit app following the structure in IMPLEMENTATION_GUIDE.md Section 3.1.
Include: header, sidebar filters, data loading with caching.
```

### Phase 5: Map Visualization (2-3 hours)
```
Build the choropleth map component as specified in IMPLEMENTATION_GUIDE.md Section 3.2.
Use Plotly to create an interactive map with color-coded counties.
```

### Phase 6: County Table (1 hour)
```
Create the county ranking table component from IMPLEMENTATION_GUIDE.md Section 3.3.
Make it sortable and add CSV export functionality.
```

### Phase 7: Testing & Polish (1-2 hours)
```
Test all functionality against the checklist in IMPLEMENTATION_GUIDE.md Phase 4.
Add the About page and any missing documentation.
```

---

## Step 5: Common Follow-up Prompts

Use these prompts as needed during development:

**If you need clarification:**
```
Please review the PRD.md section on [specific feature] and explain how we should implement it.
```

**If you encounter an error:**
```
I'm getting this error: [error message]. Based on the implementation guide, what's the likely cause and how should we fix it?
```

**If you want to add a feature:**
```
Looking at the PRD, I'd like to add [feature]. Can you implement this following the patterns established in the existing code?
```

**If you need to test:**
```
Based on the testing checklist in IMPLEMENTATION_GUIDE.md Phase 4, let's test [specific functionality]. What test cases should we run?
```

**When ready to deploy:**
```
Following the deployment instructions in IMPLEMENTATION_GUIDE.md Phase 6, let's deploy this to Streamlit Cloud. What are the steps?
```

---

## Step 6: Key Points to Emphasize

When working with Claude Code, emphasize these points:

1. **Follow the data schema exactly** as defined in DATA_SCHEMA.md
2. **Use the calculations** specified in DATA_SCHEMA.md Section 4
3. **Implement all user stories** from PRD.md Section 5
4. **Keep code modular** as shown in IMPLEMENTATION_GUIDE.md
5. **Start with sample data** before integrating real sources

---

## Step 7: Expected Timeline

**For an AI coding assistant:**
- Setup & structure: 30 minutes
- Sample data generation: 1-2 hours
- Core app with map: 3-4 hours
- County table & filters: 1-2 hours
- County detail views: 2-3 hours
- Testing & polish: 1-2 hours

**Total: ~10-15 hours of AI-assisted development**

**For a human developer:**
- Add 50-100% more time for research, debugging, and learning

---

## Step 8: Validation Checklist

Before showing to stakeholders, verify:

✅ Map displays all 64 Colorado counties  
✅ Colors match severity scale (red = critical, green = adequate)  
✅ Filters update map and table dynamically  
✅ County table shows top 20 gaps  
✅ CSV export works  
✅ Forecast view shows 2029 data  
✅ About page explains methodology  
✅ No console errors  
✅ Loads in < 5 seconds  
✅ Works in Chrome, Firefox, Safari  

---

## Troubleshooting

### If Claude Code seems confused:
- Point it back to specific sections of the documentation
- Example: "Please refer to PRD.md Section 5, User Story US-1.1 for the map requirements"

### If the implementation is too complex:
- Simplify by focusing on MVP first
- Example: "Let's implement just the map and county list first, we'll add detail views later"

### If data calculations are wrong:
- Reference DATA_SCHEMA.md Section 4 explicitly
- Example: "The gap calculation should follow DATA_SCHEMA.md Section 4.2 exactly"

### If you need to pivot:
- Provide context from LEAN_CANVAS.md
- Example: "Based on LEAN_CANVAS.md, the core problem is X, so let's focus the solution on Y"

---

## What to Do After Building

1. **Test with stakeholder** following LEAN_CANVAS.md validation plan
2. **Gather feedback** on features and usability
3. **Iterate** on highest-priority items
4. **Document learnings** for future development
5. **Plan next version** based on stakeholder needs

---

## Additional Resources

- Streamlit Documentation: https://docs.streamlit.io
- Plotly Documentation: https://plotly.com/python/
- Pandas Documentation: https://pandas.pydata.org/docs/
- Colorado Open Data Portal: https://data.colorado.gov
- Census Data API: https://www.census.gov/data/developers/data-sets.html

---

## Success Indicators

You'll know you're on track when:

✅ Claude Code references the documentation when making decisions  
✅ The code structure matches IMPLEMENTATION_GUIDE.md  
✅ Data models match DATA_SCHEMA.md  
✅ Features align with PRD.md user stories  
✅ The app actually runs without errors  
✅ You can demo all core functionality  

---

## Final Tips

1. **Be specific** in your prompts - reference exact sections of documentation
2. **Build incrementally** - get one feature working before moving to next
3. **Test frequently** - don't wait until the end to test
4. **Keep documentation open** - refer to it constantly
5. **Commit often** - save your progress regularly
6. **Ask for explanations** - understand what the AI is building, don't blindly accept code

---

**Good luck with your build!** 🚀

If you get stuck, revisit the IMPLEMENTATION_GUIDE.md for detailed technical guidance, or the PRD.md for requirements clarification.
