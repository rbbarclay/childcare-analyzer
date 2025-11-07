"""
Fetch Population Data from US Census Bureau API

Data Source: US Census Bureau - American Community Survey (ACS)
Table: B01001 - Sex by Age
Geographic Level: County (Colorado)
"""

import requests
import pandas as pd
import os
from datetime import datetime


# Census API requires a free API key
# Get one at: https://api.census.gov/data/key_signup.html
CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY', None)


def fetch_acs_population(year=2022, api_key=None, output_path='data/raw/census_population.csv'):
    """
    Fetch population data by age from Census ACS 5-Year Estimates

    Table B01001: Sex by Age
    Age cohorts needed:
    - Under 1 year (B01001_003E for Male, B01001_027E for Female)
    - 1 year (B01001_004E Male, B01001_028E Female)
    - 2 years (B01001_005E Male, B01001_029E Female)
    - 3 years (B01001_006E Male, B01001_030E Female)
    - 4 years (B01001_007E Male, B01001_031E Female)
    - 5 years (B01001_008E Male, B01001_032E Female)

    Args:
        year: ACS year (use 5-year estimates, e.g., 2022 for 2018-2022)
        api_key: Census API key (or set CENSUS_API_KEY env variable)
        output_path: Path to save raw CSV

    Returns:
        DataFrame: Population by age and county
    """
    if api_key is None:
        api_key = CENSUS_API_KEY

    if api_key is None:
        print("""
        ⚠️  CENSUS API KEY REQUIRED

        To fetch Census data, you need a free API key:

        1. Visit: https://api.census.gov/data/key_signup.html
        2. Sign up for a free key
        3. Set environment variable: export CENSUS_API_KEY='your_key_here'
        4. Or pass api_key parameter to this function

        Without an API key, you can:
        - Download data manually from data.census.gov
        - Use the Census data.census.gov interface to export CSV
        """)
        return None

    print(f"Fetching ACS {year} population data for Colorado counties...")

    # ACS 5-Year Estimates API endpoint
    base_url = f"https://api.census.gov/data/{year}/acs/acs5"

    # Variables we need (age cohorts 0-5, by sex)
    # B01001_003E through B01001_008E: Male ages under 1, 1, 2, 3, 4, 5
    # B01001_027E through B01001_032E: Female ages under 1, 1, 2, 3, 4, 5
    variables = [
        'NAME',  # County name
        # Males
        'B01001_003E',  # Male: Under 1 year
        'B01001_004E',  # Male: 1 year
        'B01001_005E',  # Male: 2 years
        'B01001_006E',  # Male: 3 years
        'B01001_007E',  # Male: 4 years
        'B01001_008E',  # Male: 5 years
        # Females
        'B01001_027E',  # Female: Under 1 year
        'B01001_028E',  # Female: 1 year
        'B01001_029E',  # Female: 2 years
        'B01001_030E',  # Female: 3 years
        'B01001_031E',  # Female: 4 years
        'B01001_032E',  # Female: 5 years
    ]

    params = {
        'get': ','.join(variables),
        'for': 'county:*',
        'in': 'state:08',  # Colorado FIPS code is 08
        'key': api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # First row is headers
        headers = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=headers)

        print(f"✓ Fetched {len(df)} Colorado counties")

        # Clean up data
        df = clean_census_data(df)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save raw data
        df.to_csv(output_path, index=False)
        print(f"✓ Saved to {output_path}")

        # Save metadata
        metadata = {
            'source': 'US Census Bureau ACS 5-Year Estimates',
            'table': 'B01001',
            'year': year,
            'download_date': datetime.now().isoformat(),
            'counties': len(df),
            'columns': list(df.columns)
        }

        metadata_path = output_path.replace('.csv', '_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return df

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching Census data: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        raise


def clean_census_data(df):
    """
    Clean and process Census ACS data

    Args:
        df: Raw Census data DataFrame

    Returns:
        DataFrame: Cleaned data with calculated age groups
    """
    # Create FIPS code
    df['county_fips'] = '08' + df['county'].str.zfill(3)
    df['county_name'] = df['NAME'].str.replace(' County, Colorado', '')

    # Convert population columns to numeric
    pop_cols = [col for col in df.columns if col.startswith('B01001_')]
    for col in pop_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate age groups
    # Under 1 year
    df['age_0_male'] = df['B01001_003E']
    df['age_0_female'] = df['B01001_027E']

    # 1 year
    df['age_1_male'] = df['B01001_004E']
    df['age_1_female'] = df['B01001_028E']

    # 2 years
    df['age_2_male'] = df['B01001_005E']
    df['age_2_female'] = df['B01001_029E']

    # 3 years
    df['age_3_male'] = df['B01001_006E']
    df['age_3_female'] = df['B01001_030E']

    # 4 years
    df['age_4_male'] = df['B01001_007E']
    df['age_4_female'] = df['B01001_031E']

    # 5 years
    df['age_5_male'] = df['B01001_008E']
    df['age_5_female'] = df['B01001_032E']

    # Sum by single year
    for age in range(6):
        df[f'age_{age}'] = df[f'age_{age}_male'] + df[f'age_{age}_female']

    # Calculate age group totals
    df['pop_0_2'] = df['age_0'] + df['age_1'] + df['age_2']
    df['pop_3_5'] = df['age_3'] + df['age_4'] + df['age_5']
    df['pop_0_5'] = df['pop_0_2'] + df['pop_3_5']

    print(f"\nAge group totals calculated:")
    print(f"  Ages 0-2: {df['pop_0_2'].sum():,}")
    print(f"  Ages 3-5: {df['pop_3_5'].sum():,}")
    print(f"  Ages 0-5: {df['pop_0_5'].sum():,}")

    return df


def get_population_summary(df):
    """
    Print summary statistics of population data

    Args:
        df: Cleaned Census data DataFrame
    """
    print("\n" + "=" * 60)
    print("POPULATION DATA SUMMARY")
    print("=" * 60)

    print(f"\nTotal counties: {len(df)}")
    print(f"\nColorado population ages 0-5: {df['pop_0_5'].sum():,}")
    print(f"  Ages 0-2: {df['pop_0_2'].sum():,}")
    print(f"  Ages 3-5: {df['pop_3_5'].sum():,}")

    print("\nTop 10 counties by population (ages 0-5):")
    print("-" * 60)
    top10 = df.nlargest(10, 'pop_0_5')[['county_name', 'pop_0_5', 'pop_0_2', 'pop_3_5']]
    for _, row in top10.iterrows():
        print(f"  {row['county_name']:20} {row['pop_0_5']:6,}  (0-2: {row['pop_0_2']:5,}, 3-5: {row['pop_3_5']:5,})")


if __name__ == "__main__":
    # Check for API key
    if CENSUS_API_KEY is None:
        print("⚠️  No Census API key found. Set CENSUS_API_KEY environment variable.")
        print("   Get a free key at: https://api.census.gov/data/key_signup.html")
    else:
        # Fetch data
        df = fetch_acs_population(year=2022)

        if df is not None:
            get_population_summary(df)
