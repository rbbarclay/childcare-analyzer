"""
Master Data Pipeline Orchestrator
Runs all data fetching, cleaning, and processing steps
"""

import os
import sys
from datetime import datetime

# Import data fetching modules
from fetch_geojson import fetch_colorado_counties
from fetch_census_data import fetch_acs_population, CENSUS_API_KEY
from fetch_forecast_data import fetch_colorado_forecasts, create_simple_forecast
# from fetch_childcare_data import fetch_childcare_facilities


def check_prerequisites():
    """
    Check if all prerequisites are met before running pipeline

    Returns:
        dict: Status of each prerequisite
    """
    print("=" * 70)
    print("PREREQUISITE CHECK")
    print("=" * 70)

    status = {
        'census_api_key': CENSUS_API_KEY is not None,
        'directories_exist': all([
            os.path.exists('data/raw'),
            os.path.exists('data/processed'),
            os.path.exists('data/geo')
        ])
    }

    print(f"\n✓ Data directories: {'PASS' if status['directories_exist'] else 'FAIL'}")
    print(f"{'✓' if status['census_api_key'] else '✗'} Census API key: {'SET' if status['census_api_key'] else 'NOT SET'}")

    if not status['census_api_key']:
        print("\n  ⚠️  Census API key missing!")
        print("  Get free key: https://api.census.gov/data/key_signup.html")
        print("  Set via: export CENSUS_API_KEY='your_key'")

    print("\n" + "=" * 70)

    return status


def run_pipeline(use_simple_forecast=False):
    """
    Run the complete data pipeline

    Args:
        use_simple_forecast: If True, use simple growth projection instead of official forecasts

    Returns:
        dict: Status of each pipeline step
    """
    print("\n" + "=" * 70)
    print(f"COLORADO CHILDCARE CAPACITY ANALYZER - DATA PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = {}

    # Step 1: Fetch GeoJSON
    print("\n[1/5] Fetching Colorado county boundaries (GeoJSON)...")
    print("-" * 70)
    try:
        fetch_colorado_counties()
        results['geojson'] = 'SUCCESS'
    except Exception as e:
        print(f"✗ Error: {e}")
        results['geojson'] = 'FAILED'

    # Step 2: Fetch Census Population Data
    print("\n[2/5] Fetching Census population data (ACS)...")
    print("-" * 70)
    try:
        census_df = fetch_acs_population(year=2022)
        if census_df is not None:
            results['census'] = 'SUCCESS'
            results['census_df'] = census_df
        else:
            results['census'] = 'SKIPPED - No API key'
    except Exception as e:
        print(f"✗ Error: {e}")
        results['census'] = 'FAILED'

    # Step 3: Fetch Population Forecasts
    print("\n[3/5] Fetching population forecasts...")
    print("-" * 70)
    try:
        if use_simple_forecast and 'census_df' in results:
            print("Using simple growth projection...")
            forecast_df = create_simple_forecast(results['census_df'])
            results['forecast'] = 'SUCCESS (Simple)'
            results['forecast_df'] = forecast_df
        else:
            forecast_df = fetch_colorado_forecasts()
            if forecast_df is not None:
                results['forecast'] = 'SUCCESS'
                results['forecast_df'] = forecast_df
            else:
                results['forecast'] = 'MANUAL STEP REQUIRED'
    except Exception as e:
        print(f"✗ Error: {e}")
        results['forecast'] = 'FAILED'

    # Step 4: Fetch Childcare Facilities Data
    print("\n[4/5] Fetching childcare facilities data...")
    print("-" * 70)
    print("⚠️  MANUAL STEP REQUIRED - See data_pipeline/fetch_childcare_data.py")
    print("   This requires identifying the correct dataset on data.colorado.gov")
    results['childcare'] = 'MANUAL STEP REQUIRED'

    # Step 5: Summary
    print("\n[5/5] Pipeline Summary")
    print("=" * 70)
    for step, status in results.items():
        if step.endswith('_df'):
            continue  # Skip DataFrame entries
        icon = '✓' if 'SUCCESS' in status else ('⚠' if 'MANUAL' in status or 'SKIPPED' in status else '✗')
        print(f"{icon} {step.upper():20} {status}")

    print("\n" + "=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    return results


def main():
    """
    Main entry point for data pipeline
    """
    # Check prerequisites
    prereq_status = check_prerequisites()

    # Ask user for confirmation
    print("\nOptions:")
    print("  1. Run with Census API (requires API key)")
    print("  2. Run with simple forecast fallback")
    print("  3. Skip and see next steps")

    if not prereq_status['census_api_key']:
        print("\n⚠️  No Census API key detected. Using option 2 automatically.")
        choice = '3'
    else:
        choice = input("\nSelect option (1/2/3): ").strip()

    if choice == '1':
        results = run_pipeline(use_simple_forecast=False)
    elif choice == '2':
        results = run_pipeline(use_simple_forecast=True)
    else:
        print("\n" + "=" * 70)
        print("NEXT STEPS TO COMPLETE DATA SETUP")
        print("=" * 70)
        print("""
1. Get Census API Key (REQUIRED):
   - Visit: https://api.census.gov/data/key_signup.html
   - Set: export CENSUS_API_KEY='your_key'

2. Identify Colorado Childcare Data:
   - Visit: https://data.colorado.gov
   - Search: "child care facilities" or "licensed childcare"
   - Find dataset with facility-level capacity data
   - Update fetch_childcare_data.py with correct URL/ID

3. Get Colorado Population Forecasts (OPTIONAL - has fallback):
   - Visit: https://demography.dola.colorado.gov
   - Download county population forecasts 2025-2029
   - Save to: data/raw/population_forecast.csv

4. Run this pipeline again:
   - python data_pipeline/run_data_pipeline.py

For more details, see:
   - data_pipeline/fetch_census_data.py
   - data_pipeline/fetch_childcare_data.py
   - data_pipeline/fetch_forecast_data.py
        """)


if __name__ == "__main__":
    main()
