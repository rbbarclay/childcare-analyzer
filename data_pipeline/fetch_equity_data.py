"""
Fetch Equity and Vulnerability Data from Census ACS

Data Sources:
- Median Household Income (B19013_001E)
- Child Poverty Rate (B17001 variables)
- Race/Ethnicity Demographics (B03002 variables)

Census API: https://api.census.gov/data/2022/acs/acs5
"""

import requests
import pandas as pd
import os


def fetch_median_income(api_key, output_path='data/raw/median_income.csv'):
    """
    Fetch median household income by county

    Args:
        api_key: Census API key
        output_path: Where to save the data

    Returns:
        DataFrame with county_name, county_fips, median_income
    """
    print("=" * 70)
    print("FETCHING MEDIAN HOUSEHOLD INCOME")
    print("=" * 70)

    # Census API endpoint
    url = (
        f"https://api.census.gov/data/2022/acs/acs5?"
        f"get=NAME,B19013_001E&"
        f"for=county:*&"
        f"in=state:08&"
        f"key={api_key}"
    )

    try:
        print(f"\nFetching from Census ACS 2022...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        print(f"\n✓ Downloaded data for {len(df)} counties")

        # Clean and format
        df['median_income'] = pd.to_numeric(df['B19013_001E'], errors='coerce')
        df['county_name'] = df['NAME'].str.replace(' County, Colorado', '')
        df['state_fips'] = df['state']
        df['county_fips_short'] = df['county']
        df['county_fips'] = '08' + df['county_fips_short'].str.zfill(3)

        # Select final columns
        final_df = df[['county_name', 'county_fips', 'median_income']].copy()

        # Sort by county name
        final_df = final_df.sort_values('county_name').reset_index(drop=True)

        print(f"\nMedian Income Summary:")
        print(f"  Highest: {final_df['county_name'].iloc[final_df['median_income'].idxmax()]} (${final_df['median_income'].max():,.0f})")
        print(f"  Lowest: {final_df['county_name'].iloc[final_df['median_income'].idxmin()]} (${final_df['median_income'].min():,.0f})")
        print(f"  State Average: ${final_df['median_income'].mean():,.0f}")

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)

        print(f"\n✓ Saved to {output_path}")

        return final_df

    except Exception as e:
        print(f"\n✗ Error fetching median income: {e}")
        return None


def fetch_child_poverty_rate(api_key, output_path='data/raw/child_poverty.csv'):
    """
    Fetch child poverty rate by county (ages 0-5)

    Uses B17001 variables:
    - B17001_004E: Male, under 6, below poverty
    - B17001_018E: Female, under 6, below poverty
    - B17001_003E: Male, under 6, total
    - B17001_017E: Female, under 6, total

    Args:
        api_key: Census API key
        output_path: Where to save the data

    Returns:
        DataFrame with county_name, county_fips, child_poverty_rate
    """
    print("\n" + "=" * 70)
    print("FETCHING CHILD POVERTY RATE (Ages 0-5)")
    print("=" * 70)

    # Census API endpoint
    url = (
        f"https://api.census.gov/data/2022/acs/acs5?"
        f"get=NAME,B17001_004E,B17001_018E,B17001_003E,B17001_017E&"
        f"for=county:*&"
        f"in=state:08&"
        f"key={api_key}"
    )

    try:
        print(f"\nFetching from Census ACS 2022...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        print(f"\n✓ Downloaded data for {len(df)} counties")

        # Convert to numeric
        df['male_poverty'] = pd.to_numeric(df['B17001_004E'], errors='coerce')
        df['female_poverty'] = pd.to_numeric(df['B17001_018E'], errors='coerce')
        df['male_total'] = pd.to_numeric(df['B17001_003E'], errors='coerce')
        df['female_total'] = pd.to_numeric(df['B17001_017E'], errors='coerce')

        # Calculate poverty rate
        df['children_in_poverty'] = df['male_poverty'] + df['female_poverty']
        df['children_total'] = df['male_total'] + df['female_total']
        df['child_poverty_rate'] = (df['children_in_poverty'] / df['children_total'] * 100).round(1)

        # Handle division by zero
        df['child_poverty_rate'] = df['child_poverty_rate'].fillna(0)

        # Format county info
        df['county_name'] = df['NAME'].str.replace(' County, Colorado', '')
        df['county_fips_short'] = df['county']
        df['county_fips'] = '08' + df['county_fips_short'].str.zfill(3)

        # Select final columns
        final_df = df[[
            'county_name',
            'county_fips',
            'children_in_poverty',
            'children_total',
            'child_poverty_rate'
        ]].copy()

        # Sort by county name
        final_df = final_df.sort_values('county_name').reset_index(drop=True)

        print(f"\nChild Poverty Rate Summary:")
        print(f"  Highest: {final_df['county_name'].iloc[final_df['child_poverty_rate'].idxmax()]} ({final_df['child_poverty_rate'].max():.1f}%)")
        print(f"  Lowest: {final_df['county_name'].iloc[final_df['child_poverty_rate'].idxmin()]} ({final_df['child_poverty_rate'].min():.1f}%)")
        print(f"  State Average: {final_df['child_poverty_rate'].mean():.1f}%")

        # Count high-poverty counties (>15%)
        high_poverty = len(final_df[final_df['child_poverty_rate'] > 15])
        print(f"  Counties with >15% poverty: {high_poverty}")

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)

        print(f"\n✓ Saved to {output_path}")

        return final_df

    except Exception as e:
        print(f"\n✗ Error fetching child poverty: {e}")
        return None


def integrate_equity_data(
    income_df,
    poverty_df,
    county_capacity_path='data/processed/county_capacity.csv',
    output_path='data/processed/county_capacity_with_equity.csv'
):
    """
    Integrate equity data with county capacity dataset

    Args:
        income_df: Median income DataFrame
        poverty_df: Child poverty DataFrame
        county_capacity_path: Path to main dataset
        output_path: Where to save integrated data

    Returns:
        DataFrame with equity metrics added
    """
    print("\n" + "=" * 70)
    print("INTEGRATING EQUITY DATA")
    print("=" * 70)

    # Load county capacity data
    capacity_df = pd.read_csv(county_capacity_path)

    print(f"\nLoaded {len(capacity_df)} records from county capacity")

    # Ensure county_fips is string in all dataframes for consistent merging
    capacity_df['county_fips'] = capacity_df['county_fips'].astype(str).str.zfill(5)
    income_df['county_fips'] = income_df['county_fips'].astype(str).str.zfill(5)
    poverty_df['county_fips'] = poverty_df['county_fips'].astype(str).str.zfill(5)

    # Merge income data
    capacity_df = capacity_df.merge(
        income_df[['county_fips', 'median_income']],
        on='county_fips',
        how='left'
    )

    # Merge poverty data
    capacity_df = capacity_df.merge(
        poverty_df[['county_fips', 'child_poverty_rate']],
        on='county_fips',
        how='left'
    )

    # Create equity flags
    capacity_df['low_income'] = capacity_df['median_income'] < 60000
    capacity_df['high_poverty'] = capacity_df['child_poverty_rate'] > 15.0

    # Calculate equity concern score (0-100)
    # Higher = more equity concern
    def calculate_equity_score(row):
        score = 0

        # Income component (0-35 points)
        if pd.notna(row['median_income']):
            if row['median_income'] < 40000:
                score += 35
            elif row['median_income'] < 50000:
                score += 25
            elif row['median_income'] < 60000:
                score += 15
            elif row['median_income'] < 70000:
                score += 5

        # Poverty component (0-35 points)
        if pd.notna(row['child_poverty_rate']):
            if row['child_poverty_rate'] > 25:
                score += 35
            elif row['child_poverty_rate'] > 20:
                score += 25
            elif row['child_poverty_rate'] > 15:
                score += 15
            elif row['child_poverty_rate'] > 10:
                score += 5

        return score

    capacity_df['equity_score'] = capacity_df.apply(calculate_equity_score, axis=1)

    # Classify equity concern level
    def classify_equity_concern(score):
        if score >= 50:
            return "High Concern"
        elif score >= 30:
            return "Moderate Concern"
        elif score >= 15:
            return "Low Concern"
        else:
            return "Minimal Concern"

    capacity_df['equity_concern'] = capacity_df['equity_score'].apply(classify_equity_concern)

    # Save integrated data
    capacity_df.to_csv(output_path, index=False)

    print(f"\n✓ Integrated equity data")
    print(f"  Total records: {len(capacity_df)}")
    print(f"  Equity Concern Distribution:")

    concern_counts = capacity_df['equity_concern'].value_counts()
    for concern, count in concern_counts.items():
        print(f"    {concern}: {count} records")

    print(f"\n✓ Saved to {output_path}")

    return capacity_df


if __name__ == "__main__":
    import sys

    # Check for API key
    if len(sys.argv) < 2:
        print("\nUsage: python fetch_equity_data.py <CENSUS_API_KEY>")
        print("\nAlternatively, set CENSUS_API_KEY environment variable:")
        print("  export CENSUS_API_KEY=your_key_here")
        print("  python fetch_equity_data.py")

        # Try to get from environment
        api_key = os.environ.get('CENSUS_API_KEY')
        if not api_key:
            sys.exit(1)
    else:
        api_key = sys.argv[1]

    print("\n" + "=" * 70)
    print("PHASE 2A: INCOME & POVERTY DATA INTEGRATION")
    print("=" * 70)

    # Fetch median income
    income_df = fetch_median_income(api_key)

    if income_df is None:
        print("\n✗ Failed to fetch median income data")
        sys.exit(1)

    # Fetch child poverty rate
    poverty_df = fetch_child_poverty_rate(api_key)

    if poverty_df is None:
        print("\n✗ Failed to fetch child poverty data")
        sys.exit(1)

    # Integrate with county capacity data
    integrated_df = integrate_equity_data(income_df, poverty_df)

    print("\n" + "=" * 70)
    print("✓ PHASE 2A COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Update Streamlit app to use county_capacity_with_equity.csv")
    print("  2. Add equity filters to sidebar")
    print("  3. Display income/poverty in county cards")
    print("\nData files created:")
    print("  - data/raw/median_income.csv")
    print("  - data/raw/child_poverty.csv")
    print("  - data/processed/county_capacity_with_equity.csv")
