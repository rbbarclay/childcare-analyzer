"""
Fetch Population Forecast Data from Colorado State Demography Office

Data Source: Colorado State Demography Office (demography.dola.colorado.gov)
Forecasts: County population projections 2025-2029 by age
"""

import requests
import pandas as pd
import os
from datetime import datetime


def fetch_colorado_forecasts(output_path='data/raw/population_forecast.csv'):
    """
    Fetch population forecast data from Colorado State Demography Office

    The Colorado State Demography Office provides population projections
    by county and age group. Data is typically available through:
    - Direct CSV downloads
    - Interactive data tools
    - API (if available)

    Args:
        output_path: Path to save forecast data

    Returns:
        DataFrame: Population forecasts by county and age
    """
    print("Fetching Colorado population forecasts...")

    print("""
    ⚠️  MANUAL DATA RETRIEVAL MAY BE REQUIRED

    Colorado State Demography Office data sources:

    1. Main site: https://demography.dola.colorado.gov

    2. Specific tools to check:
       - Colorado Demographic Dashboard
       - County Lookup Tool
       - Download Center

    3. Dataset to find:
       - "County Population Forecasts by Age"
       - Years: 2025-2029 (or latest available)
       - Age groups: Single year or 5-year cohorts including 0-5

    4. Look for:
       - Direct CSV download
       - Excel files with forecast tables
       - API endpoint (if available)

    Common direct links to try:
    - https://storage.googleapis.com/co-publicdata/demog/ (check for forecast files)
    - https://gis.dola.colorado.gov/lookups/ (interactive tools)
    """)

    # Option 1: Try common forecast data URL patterns
    # NOTE: These are examples - actual URLs need to be verified
    potential_urls = [
        "https://storage.googleapis.com/co-publicdata/demog/population_forecast_county.csv",
        "https://demography.dola.colorado.gov/assets/html/county_forecasts.csv",
    ]

    for url in potential_urls:
        try:
            print(f"\nTrying: {url}")
            df = pd.read_csv(url)
            print(f"✓ Success! Downloaded {len(df)} records")

            # Save data
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)

            print(f"✓ Saved to {output_path}")
            return df

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

    print("\n⚠️  Automatic download failed. Manual steps needed:")
    print("""
    To get forecast data manually:

    1. Visit: https://demography.dola.colorado.gov
    2. Navigate to data downloads or forecast tools
    3. Export county population forecasts by age (2025-2029)
    4. Save CSV to: data/raw/population_forecast.csv
    5. Ensure columns include:
       - County name or FIPS code
       - Year (2025-2029)
       - Age or age group
       - Population (forecast)
    """)

    return None


def create_simple_forecast(census_df, growth_rate=0.005, forecast_years=[2025, 2026, 2027, 2028, 2029]):
    """
    Create simple population forecast using constant growth rate

    This is a FALLBACK if official forecasts are unavailable.
    Assumes constant annual growth rate (default 0.5% per year)

    Args:
        census_df: Current population data from Census
        growth_rate: Annual growth rate (default 0.005 = 0.5%)
        forecast_years: Years to forecast

    Returns:
        DataFrame: Simple population forecasts
    """
    print(f"\n⚠️  Using SIMPLE FORECAST with {growth_rate*100:.1f}% annual growth")
    print("   This is a fallback - official forecasts are preferred!")

    base_year = 2022  # Assume Census data is from 2022
    forecasts = []

    for year in forecast_years:
        years_ahead = year - base_year
        growth_factor = (1 + growth_rate) ** years_ahead

        forecast = census_df.copy()
        forecast['year'] = year
        forecast['pop_0_2'] = (forecast['pop_0_2'] * growth_factor).round().astype(int)
        forecast['pop_3_5'] = (forecast['pop_3_5'] * growth_factor).round().astype(int)
        forecast['pop_0_5'] = forecast['pop_0_2'] + forecast['pop_3_5']

        forecasts.append(forecast)

    forecast_df = pd.concat(forecasts, ignore_index=True)

    print(f"\n✓ Created simple forecasts for {len(forecast_years)} years")
    print(f"  Base year {base_year} population (0-5): {census_df['pop_0_5'].sum():,}")
    print(f"  Year {max(forecast_years)} forecast (0-5): {forecast_df[forecast_df['year']==max(forecast_years)]['pop_0_5'].sum():,}")

    return forecast_df


def explore_forecast_structure(df):
    """
    Explore structure of forecast data

    Args:
        df: Forecast data DataFrame
    """
    print("\n" + "=" * 60)
    print("FORECAST DATA STRUCTURE")
    print("=" * 60)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")

    if 'year' in df.columns:
        print(f"\nYears available: {sorted(df['year'].unique())}")

    print("\nFirst few rows:")
    print(df.head())


if __name__ == "__main__":
    # Try to fetch official forecasts
    df = fetch_colorado_forecasts()

    if df is not None:
        explore_forecast_structure(df)
    else:
        print("\n" + "=" * 60)
        print("FALLBACK OPTION AVAILABLE")
        print("=" * 60)
        print("""
        If official forecasts cannot be obtained, we can:
        1. Use simple growth rate projections from Census data
        2. This is less accurate but sufficient for prototype

        To use fallback, load Census data first:
        >>> from fetch_census_data import fetch_acs_population
        >>> census_df = fetch_acs_population()
        >>> forecast_df = create_simple_forecast(census_df)
        """)
