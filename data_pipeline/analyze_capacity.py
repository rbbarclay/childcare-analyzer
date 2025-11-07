"""
Analyze Colorado Childcare Capacity by Age Group and County

Maps facility-level capacity data to our age groups (0-2, 3-5)
"""

import pandas as pd
import numpy as np


def analyze_capacity_by_age_group(facilities_df):
    """
    Analyze how capacity maps to our age groups

    Our age groups:
    - Ages 0-2: Infants (0-12mo) + Toddlers (13-35mo)
    - Ages 3-5: Preschool (3-5 years)

    Dataset fields:
    - LICENSED CENTER INFANT CAPACITY: 0-12 months
    - LICENSED CENTER TODDLER CAPACITY: 13-35 months (roughly 1-3 years)
    - LICENSED CENTER PRESCHOOL CAPACITY: 3-5 years
    - LICENSED HOME CAPACITY: Mixed ages (need to estimate split)
    """
    df = facilities_df.copy()

    print("="*70)
    print("CAPACITY MAPPING ANALYSIS")
    print("="*70)

    # Fill NaN with 0 for capacity calculations
    capacity_cols = [
        'LICENSED CENTER INFANT CAPACITY',
        'LICENSED CENTER TODDLER CAPACITY',
        'LICENSED CENTER PRESCHOOL CAPACITY',
        'LICENSED HOME CAPACITY',
        'TOTAL LICENSED CAPACITY'
    ]

    for col in capacity_cols:
        df[col] = df[col].fillna(0)

    # Calculate age-specific capacity
    print("\n1. CENTER-BASED CAPACITY (Age-specific)")
    print("-" * 70)

    # Ages 0-2: Infant + Toddler
    df['capacity_0_2_center'] = (
        df['LICENSED CENTER INFANT CAPACITY'] +
        df['LICENSED CENTER TODDLER CAPACITY']
    )

    # Ages 3-5: Preschool
    df['capacity_3_5_center'] = df['LICENSED CENTER PRESCHOOL CAPACITY']

    total_0_2_center = df['capacity_0_2_center'].sum()
    total_3_5_center = df['capacity_3_5_center'].sum()

    print(f"   Ages 0-2 (Infant + Toddler): {total_0_2_center:,.0f} slots")
    print(f"   Ages 3-5 (Preschool):        {total_3_5_center:,.0f} slots")

    # Home-based capacity
    print("\n2. HOME-BASED CAPACITY (Mixed ages - requires estimation)")
    print("-" * 70)

    total_home = df['LICENSED HOME CAPACITY'].sum()
    print(f"   Total home capacity: {total_home:,.0f} slots")
    print("   ⚠️  Home-based care doesn't specify age groups")
    print("   📊 Estimation approach:")
    print("      - Assume 40% for ages 0-2")
    print("      - Assume 60% for ages 3-5")
    print("      (Based on typical family child care ratios)")

    # Estimate home capacity split
    df['capacity_0_2_home'] = df['LICENSED HOME CAPACITY'] * 0.40
    df['capacity_3_5_home'] = df['LICENSED HOME CAPACITY'] * 0.60

    total_0_2_home = df['capacity_0_2_home'].sum()
    total_3_5_home = df['capacity_3_5_home'].sum()

    print(f"   Estimated ages 0-2: {total_0_2_home:,.0f} slots")
    print(f"   Estimated ages 3-5: {total_3_5_home:,.0f} slots")

    # Combined totals
    print("\n3. COMBINED LICENSED CAPACITY BY AGE GROUP")
    print("-" * 70)

    df['capacity_0_2'] = df['capacity_0_2_center'] + df['capacity_0_2_home']
    df['capacity_3_5'] = df['capacity_3_5_center'] + df['capacity_3_5_home']
    df['capacity_0_5'] = df['capacity_0_2'] + df['capacity_3_5']

    total_0_2 = df['capacity_0_2'].sum()
    total_3_5 = df['capacity_3_5'].sum()
    total_0_5 = df['capacity_0_5'].sum()

    print(f"   Ages 0-2:  {total_0_2:>10,.0f} slots")
    print(f"   Ages 3-5:  {total_3_5:>10,.0f} slots")
    print(f"   Ages 0-5:  {total_0_5:>10,.0f} slots")
    print(f"\n   Total licensed: {df['TOTAL LICENSED CAPACITY'].sum():>10,.0f} slots")

    # Coverage check
    coverage = (total_0_5 / df['TOTAL LICENSED CAPACITY'].sum()) * 100
    print(f"   Coverage: {coverage:.1f}% of total licensed capacity")

    if coverage < 80:
        print("\n   ⚠️  WARNING: Low coverage - check data quality")
        print("   Some capacity may be in school-age or other categories")

    return df


def aggregate_by_county(facilities_df):
    """
    Aggregate capacity by county and age group

    Returns:
        DataFrame with county-level capacity
    """
    print("\n" + "="*70)
    print("COUNTY-LEVEL CAPACITY AGGREGATION")
    print("="*70)

    # Group by county
    county_capacity = facilities_df.groupby('COUNTY').agg({
        'capacity_0_2': 'sum',
        'capacity_3_5': 'sum',
        'capacity_0_5': 'sum',
        'PROVIDER NAME': 'count'  # Facility count
    }).reset_index()

    county_capacity.columns = [
        'county_name',
        'licensed_capacity_0_2',
        'licensed_capacity_3_5',
        'licensed_capacity_0_5',
        'facility_count'
    ]

    # Round to integers
    for col in ['licensed_capacity_0_2', 'licensed_capacity_3_5', 'licensed_capacity_0_5']:
        county_capacity[col] = county_capacity[col].round().astype(int)

    # Sort by total capacity
    county_capacity = county_capacity.sort_values('licensed_capacity_0_5', ascending=False)

    print(f"\nAggregated capacity for {len(county_capacity)} counties")
    print("\nTop 10 counties by total capacity (ages 0-5):")
    print("-" * 70)

    top10 = county_capacity.head(10)
    for _, row in top10.iterrows():
        print(f"{row['county_name']:20} "
              f"{row['licensed_capacity_0_5']:>6,} slots "
              f"({row['facility_count']:>4} facilities) "
              f"[0-2: {row['licensed_capacity_0_2']:>5,}, 3-5: {row['licensed_capacity_3_5']:>5,}]")

    # Check for counties with very low capacity
    print("\nCounties with <100 total slots (potential data issues):")
    print("-" * 70)
    low_capacity = county_capacity[county_capacity['licensed_capacity_0_5'] < 100]

    if len(low_capacity) > 0:
        for _, row in low_capacity.iterrows():
            print(f"   {row['county_name']:20} {row['licensed_capacity_0_5']:>3} slots "
                  f"({row['facility_count']} facilities)")
    else:
        print("   None - all counties have reasonable capacity")

    return county_capacity


def save_capacity_summary(county_capacity, output_path='data/processed/county_capacity_supply.csv'):
    """
    Save county-level capacity summary

    Args:
        county_capacity: DataFrame with county aggregations
        output_path: Where to save
    """
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    county_capacity.to_csv(output_path, index=False)
    print(f"\n✓ Saved county capacity summary to {output_path}")


if __name__ == "__main__":
    # Load facilities data
    facilities = pd.read_csv('data/raw/childcare_facilities.csv')

    print(f"Loaded {len(facilities):,} childcare facilities\n")

    # Analyze capacity by age group
    facilities = analyze_capacity_by_age_group(facilities)

    # Aggregate by county
    county_capacity = aggregate_by_county(facilities)

    # Save results
    save_capacity_summary(county_capacity)

    print("\n" + "="*70)
    print("✓ ANALYSIS COMPLETE")
    print("="*70)
