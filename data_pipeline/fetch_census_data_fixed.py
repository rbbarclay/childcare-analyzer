"""
Fetch Population Data from US Census Bureau API - CORRECTED VERSION

Uses simpler age groups since ACS doesn't provide single-year ages easily
"""

import requests
import pandas as pd
import os
from datetime import datetime


CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY', None)


def fetch_acs_under5_population(year=2022, api_key=None, output_path='data/raw/census_population.csv'):
    """
    Fetch population data for children under 5 from Census ACS

    Note: ACS Table B01001 provides "Under 5 years" as a single group
    We'll need to estimate the 0-2 vs 3-5 split

    Args:
        year: ACS year
        api_key: Census API key
        output_path: Where to save

    Returns:
        DataFrame: Population by county
    """
    if api_key is None:
        api_key = CENSUS_API_KEY

    if api_key is None:
        print("⚠️  Census API key required")
        return None

    print(f"Fetching ACS {year} population data for Colorado counties...")
    print("Using B01001 (Sex by Age) - 'Under 5 years' category")

    base_url = f"https://api.census.gov/data/{year}/acs/acs5"

    # Variables we need:
    # B01001_001E: Total population
    # B01001_003E: Male, Under 5 years (ages 0-4)
    # B01001_027E: Female, Under 5 years (ages 0-4)

    variables = [
        'NAME',
        'B01001_001E',  # Total population
        'B01001_003E',  # Male under 5
        'B01001_027E',  # Female under 5
    ]

    params = {
        'get': ','.join(variables),
        'for': 'county:*',
        'in': 'state:08',
        'key': api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        headers = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=headers)

        print(f"✓ Fetched {len(df)} Colorado counties")

        # Process data
        df = process_census_data(df)

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✓ Saved to {output_path}")

        # Save metadata
        metadata = {
            'source': 'US Census Bureau ACS 5-Year Estimates',
            'table': 'B01001',
            'year': year,
            'download_date': datetime.now().isoformat(),
            'counties': len(df),
            'note': 'Under 5 years (ages 0-4), age 5 estimated separately'
        }

        metadata_path = output_path.replace('.csv', '_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return df

    except Exception as e:
        print(f"✗ Error fetching Census data: {e}")
        raise


def process_census_data(df):
    """
    Process Census ACS data to get ages 0-5 estimates

    ACS gives us "Under 5" (ages 0-4)
    We need to estimate age 5 separately and split 0-4 into 0-2 and 3-4

    Args:
        df: Raw Census data

    Returns:
        DataFrame: Processed with age groups
    """
    # Create FIPS code
    df['county_fips'] = '08' + df['county'].str.zfill(3)
    df['county_name'] = df['NAME'].str.replace(' County, Colorado', '')

    # Convert to numeric
    df['total_population'] = pd.to_numeric(df['B01001_001E'], errors='coerce')
    df['male_under5'] = pd.to_numeric(df['B01001_003E'], errors='coerce')
    df['female_under5'] = pd.to_numeric(df['B01001_027E'], errors='coerce')

    # Total under 5 (ages 0-4)
    df['pop_0_4'] = df['male_under5'] + df['female_under5']

    # Estimate age 5 separately
    # Typical pattern: age 5 is about 20% of 0-4 population (1 year out of 5)
    df['pop_5'] = (df['pop_0_4'] * 0.20).round().astype(int)

    # Total ages 0-5
    df['pop_0_5'] = df['pop_0_4'] + df['pop_5']

    # Split ages 0-4 into 0-2 (3 years) and 3-4 (2 years)
    # 0-2 = 60% of 0-4 (3 years out of 5)
    # 3-4 = 40% of 0-4 (2 years out of 5)
    df['pop_0_2_from_0_4'] = (df['pop_0_4'] * 0.60).round().astype(int)
    df['pop_3_4'] = (df['pop_0_4'] * 0.40).round().astype(int)

    # Add age 5 to get full 3-5 range
    df['pop_3_5'] = df['pop_3_4'] + df['pop_5']

    # Final age groups (matching our schema)
    df['pop_0_2'] = df['pop_0_2_from_0_4']

    print(f"\nAge group totals calculated:")
    print(f"  Ages 0-4 (Census): {df['pop_0_4'].sum():,}")
    print(f"  Age 5 (estimated): {df['pop_5'].sum():,}")
    print(f"  Ages 0-2: {df['pop_0_2'].sum():,}")
    print(f"  Ages 3-5: {df['pop_3_5'].sum():,}")
    print(f"  Ages 0-5: {df['pop_0_5'].sum():,}")

    return df


def get_population_summary(df):
    """
    Print population summary

    Args:
        df: Processed Census data
    """
    print("\n" + "="*70)
    print("POPULATION DATA SUMMARY (Census ACS)")
    print("="*70)

    print(f"\nTotal counties: {len(df)}")
    print(f"\nColorado population ages 0-5: {df['pop_0_5'].sum():,}")
    print(f"  Ages 0-2: {df['pop_0_2'].sum():,}")
    print(f"  Ages 3-5: {df['pop_3_5'].sum():,}")

    print("\nTop 10 counties by population (ages 0-5):")
    print("-" * 70)
    top10 = df.nlargest(10, 'pop_0_5')[['county_name', 'pop_0_5', 'pop_0_2', 'pop_3_5']]
    for _, row in top10.iterrows():
        print(f"  {row['county_name']:20} {row['pop_0_5']:6,}  "
              f"(0-2: {row['pop_0_2']:5,}, 3-5: {row['pop_3_5']:5,})")


if __name__ == "__main__":
    if CENSUS_API_KEY is None:
        print("⚠️  Set CENSUS_API_KEY environment variable")
    else:
        df = fetch_acs_under5_population(year=2022)
        if df is not None:
            get_population_summary(df)
