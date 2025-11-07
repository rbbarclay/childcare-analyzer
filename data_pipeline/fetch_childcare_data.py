"""
Fetch Childcare Facilities Data from Colorado Open Data Portal

Data Source: data.colorado.gov
Dataset: Child Care Facility and Licensed Capacity
"""

import requests
import pandas as pd
import os
from datetime import datetime


def fetch_childcare_facilities(output_path='data/raw/childcare_facilities.csv'):
    """
    Fetch childcare facilities data from Colorado Open Data Portal

    The dataset should include:
    - Facility name, address, county
    - License type/status
    - Licensed capacity by age group

    Args:
        output_path: Path to save raw CSV data

    Returns:
        DataFrame: Raw childcare facilities data
    """
    print("Fetching childcare facilities from Colorado Open Data Portal...")

    # Colorado Open Data Portal - Socrata API endpoint
    # NOTE: We need to find the actual dataset ID on data.colorado.gov
    # Common Socrata API pattern: https://data.colorado.gov/resource/{dataset_id}.json

    # This is a placeholder - we'll need to identify the correct dataset
    # Searching for: "child care" or "childcare" on data.colorado.gov

    # Option 1: Use Socrata API (if we have dataset ID)
    # base_url = "https://data.colorado.gov/resource/XXXX-XXXX.json"

    # Option 2: Direct CSV download (if available)
    # Some datasets have direct CSV export URLs

    # For now, let's try to search for the dataset
    print("""
    ⚠️  MANUAL STEP REQUIRED:

    To fetch childcare facilities data, please:

    1. Visit: https://data.colorado.gov
    2. Search for: "child care facilities" or "licensed childcare"
    3. Look for dataset with facility-level capacity data
    4. Find either:
       - Socrata API endpoint (resource ID)
       - Direct CSV download URL

    Common dataset names to look for:
    - "Child Care Facility and Licensed Capacity"
    - "Licensed Child Care Facilities"
    - "Early Childhood Facilities"

    Once identified, update this script with the correct endpoint.
    """)

    # Example structure for when we have the URL:
    # url = "https://data.colorado.gov/resource/XXXX-XXXX.csv"
    # params = {
    #     '$limit': 10000,  # Increase limit to get all records
    #     '$order': 'county'
    # }

    # For demonstration, let's create a function that will work once we have the URL
    return None


def fetch_via_socrata_api(dataset_id, limit=10000):
    """
    Fetch data from Colorado Open Data Portal using Socrata API

    Args:
        dataset_id: Socrata dataset ID (format: XXXX-XXXX)
        limit: Maximum records to fetch

    Returns:
        DataFrame: Fetched data
    """
    url = f"https://data.colorado.gov/resource/{dataset_id}.json"

    params = {
        '$limit': limit,
        '$order': ':id'
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data)

        print(f"✓ Fetched {len(df)} records from Socrata API")
        return df

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching from Socrata API: {e}")
        raise


def fetch_via_csv_url(csv_url, output_path='data/raw/childcare_facilities.csv'):
    """
    Fetch childcare data via direct CSV download URL

    Args:
        csv_url: Direct URL to CSV file
        output_path: Path to save downloaded CSV

    Returns:
        DataFrame: Downloaded data
    """
    print(f"Downloading CSV from: {csv_url}")

    try:
        df = pd.read_csv(csv_url)
        print(f"✓ Downloaded {len(df)} records")
        print(f"  Columns: {list(df.columns)}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save raw data
        df.to_csv(output_path, index=False)
        print(f"✓ Saved to {output_path}")

        # Add metadata
        metadata = {
            'source_url': csv_url,
            'download_date': datetime.now().isoformat(),
            'record_count': len(df),
            'columns': list(df.columns)
        }

        metadata_path = output_path.replace('.csv', '_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return df

    except Exception as e:
        print(f"✗ Error downloading CSV: {e}")
        raise


def explore_dataset_structure(df):
    """
    Explore and print structure of childcare dataset

    Args:
        df: DataFrame to explore
    """
    print("\n" + "=" * 60)
    print("DATASET STRUCTURE")
    print("=" * 60)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn Names and Types:")
    print("-" * 60)
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")

    print("\nFirst few rows:")
    print("-" * 60)
    print(df.head())

    print("\nMissing values:")
    print("-" * 60)
    missing = df.isnull().sum()
    print(missing[missing > 0])

    # Check for county column
    county_cols = [col for col in df.columns if 'county' in col.lower()]
    if county_cols:
        print(f"\nCounty column(s) found: {county_cols}")
        print("\nUnique counties:")
        for col in county_cols:
            print(f"  {col}: {df[col].nunique()} unique values")
            print(f"    Sample: {df[col].unique()[:5]}")


if __name__ == "__main__":
    # Instructions for manual data retrieval
    print(__doc__)

    # Once we have the dataset URL/ID, uncomment and use:
    # df = fetch_via_csv_url("ACTUAL_URL_HERE")
    # explore_dataset_structure(df)
