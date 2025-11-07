"""
Fetch Population Forecast Data from Colorado State Demography Office

Data Source: Colorado Department of Local Affairs (DOLA)
Dataset: Population Projections in Colorado (q5vp-adf3)
URL: https://data.colorado.gov/Demographics/Population-Projections-in-Colorado/q5vp-adf3
Years: 1990-2040 (includes forecasts through 2040)
"""

import requests
import pandas as pd
import os
from datetime import datetime


def fetch_dola_forecasts(output_path='data/raw/dola_population_forecast.csv'):
    """
    Fetch official population forecasts from Colorado DOLA

    Downloads the complete DOLA Population Projections dataset (q5vp-adf3)
    which includes forecasts from 1990 to 2040 by county and individual age.

    Args:
        output_path: Path to save raw forecast data

    Returns:
        DataFrame: Raw population forecasts by county, year, and age
    """
    print("=" * 70)
    print("FETCHING COLORADO DOLA POPULATION FORECASTS")
    print("=" * 70)

    url = "https://data.colorado.gov/api/views/q5vp-adf3/rows.csv?accessType=DOWNLOAD"

    try:
        print(f"\nDownloading from: data.colorado.gov")
        print(f"Dataset: Population Projections in Colorado (q5vp-adf3)")

        df = pd.read_csv(url)

        print(f"\n✓ Downloaded {len(df):,} records")
        print(f"  Years: {df['year'].min()} - {df['year'].max()}")
        print(f"  Counties: {df['county'].nunique()}")
        print(f"  Data types: {df['dataType'].unique().tolist()}")

        # Save raw data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"\n✓ Saved raw data to {output_path}")

        return df

    except Exception as e:
        print(f"\n✗ Failed to download DOLA forecasts: {e}")
        print("\nManual download option:")
        print(f"  1. Visit: https://data.colorado.gov/Demographics/Population-Projections-in-Colorado/q5vp-adf3")
        print(f"  2. Click 'Export' → 'CSV'")
        print(f"  3. Save to: {output_path}")

        return None


def process_dola_forecasts(dola_df, forecast_year=2029, output_path='data/raw/population_forecast.csv'):
    """
    Process DOLA forecasts to extract specific year by age groups

    Aggregates individual age data into our target age groups (0-2, 3-5, 0-5)
    for a specific forecast year.

    Args:
        dola_df: Raw DOLA forecast data
        forecast_year: Year to extract (default 2029)
        output_path: Where to save processed forecasts

    Returns:
        DataFrame: Processed forecasts with columns:
            - county_name
            - county_fips (5-digit string with '08' prefix)
            - year
            - pop_0_2, pop_3_5, pop_0_5
    """
    print("\n" + "=" * 70)
    print(f"PROCESSING DOLA FORECASTS FOR {forecast_year}")
    print("=" * 70)

    # Filter to forecast year and forecast type
    df = dola_df[
        (dola_df['year'] == forecast_year) &
        (dola_df['dataType'] == 'Forecast')
    ].copy()

    print(f"\nFiltered to {len(df):,} records for year {forecast_year}")

    if len(df) == 0:
        print(f"\n⚠️  No forecast data found for year {forecast_year}")
        return None

    # Calculate population for each age group by county
    records = []

    for county in df['county'].unique():
        county_data = df[df['county'] == county]
        fips_code = county_data['fipsCode'].iloc[0]

        # Sum population for each age group
        pop_0_2 = county_data[county_data['age'] <= 2]['totalPopulation'].sum()
        pop_3_5 = county_data[(county_data['age'] >= 3) & (county_data['age'] <= 5)]['totalPopulation'].sum()
        pop_0_5 = pop_0_2 + pop_3_5

        records.append({
            'county_name': county,
            'fips_code': fips_code,
            'year': forecast_year,
            'pop_0_2': int(pop_0_2),
            'pop_3_5': int(pop_3_5),
            'pop_0_5': int(pop_0_5)
        })

    final_df = pd.DataFrame(records)

    # Format FIPS code to match our existing data (5-digit with '08' prefix)
    final_df['county_fips'] = '08' + final_df['fips_code'].astype(str).str.zfill(3)

    # Select and order final columns
    final_df = final_df[[
        'county_name',
        'county_fips',
        'year',
        'pop_0_2',
        'pop_3_5',
        'pop_0_5'
    ]].copy()

    # Sort by county name
    final_df = final_df.sort_values('county_name').reset_index(drop=True)

    print(f"\n✓ Processed {len(final_df)} counties")
    print(f"\nSummary for {forecast_year}:")
    print(f"  Total population ages 0-5: {final_df['pop_0_5'].sum():,}")
    print(f"  Population ages 0-2: {final_df['pop_0_2'].sum():,}")
    print(f"  Population ages 3-5: {final_df['pop_3_5'].sum():,}")

    # Save processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"\n✓ Saved processed forecasts to {output_path}")

    return final_df


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
    print("\nStarting official DOLA forecast data integration...")

    # Step 1: Fetch DOLA forecasts
    dola_df = fetch_dola_forecasts()

    if dola_df is not None:
        # Step 2: Process forecasts for 2029
        forecast_df = process_dola_forecasts(dola_df, forecast_year=2029)

        if forecast_df is not None:
            print("\n" + "=" * 70)
            print("✓ DOLA FORECAST INTEGRATION COMPLETE")
            print("=" * 70)
            print(f"\nProcessed data saved to: data/raw/population_forecast.csv")
            print(f"This file is ready to be used by generate_final_dataset.py")
            print("\nNext step:")
            print("  Run: python data_pipeline/generate_final_dataset.py")
        else:
            print("\n✗ Failed to process forecasts")
    else:
        print("\n" + "=" * 70)
        print("FALLBACK OPTION")
        print("=" * 70)
        print("""
        If DOLA forecasts cannot be downloaded, you can use the simple
        growth rate fallback:

        >>> from fetch_census_data_fixed import fetch_acs_population
        >>> census_df = pd.read_csv('data/raw/census_population.csv')
        >>> forecast_df = create_simple_forecast(census_df)
        """)
