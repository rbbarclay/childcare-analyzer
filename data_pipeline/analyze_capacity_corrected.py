"""
CORRECTED: Analyze Colorado Childcare Capacity for Ages 0-5 ONLY

Key corrections:
- TOTAL_LICENSED_CAPACITY includes school-age (6-12), which we DON'T want
- Need to carefully sum only capacity for ages 0-5
- Exclude school-age-only facilities
"""

import pandas as pd
import numpy as np


def calculate_0_5_capacity_correct(facilities_df):
    """
    Calculate capacity for ages 0-5 ONLY (excluding school-age)

    Approach:
    1. Infant (0-12 months) capacity
    2. Toddler (13-35 months, roughly 1-3 years) capacity
    3. Preschool (3-5 years) capacity
    4. Home-based (mixed ages, estimate split)
    5. EXCLUDE school-age only facilities
    """
    df = facilities_df.copy()

    print("="*70)
    print("CORRECTED CAPACITY CALCULATION - AGES 0-5 ONLY")
    print("="*70)

    # Fill NaN with 0
    capacity_cols = [
        'LICENSED CENTER INFANT CAPACITY',
        'LICENSED CENTER TODDLER CAPACITY',
        'LICENSED CENTER PRESCHOOL CAPACITY',
        'LICENSED HOME CAPACITY',
        'LICENSED SCHOOL AGE CAPACITY',
        'TOTAL LICENSED CAPACITY'
    ]

    for col in capacity_cols:
        df[col] = df[col].fillna(0)

    print("\n1. UNDERSTANDING THE DATA:")
    print("-" * 70)
    print(f"   Total facilities: {len(df):,}")
    print(f"   Total licensed capacity (ALL ages): {df['TOTAL LICENSED CAPACITY'].sum():>10,.0f}")

    # Identify school-age-only facilities
    school_age_only = (
        (df['LICENSED SCHOOL AGE CAPACITY'] > 0) &
        (df['LICENSED CENTER INFANT CAPACITY'] == 0) &
        (df['LICENSED CENTER TODDLER CAPACITY'] == 0) &
        (df['LICENSED CENTER PRESCHOOL CAPACITY'] == 0) &
        (df['LICENSED HOME CAPACITY'] == 0)
    )

    print(f"\n   School-age ONLY facilities: {school_age_only.sum():,}")
    print(f"   School-age ONLY capacity: {df[school_age_only]['LICENSED SCHOOL AGE CAPACITY'].sum():>10,.0f}")
    print("   ↑ This should be EXCLUDED from ages 0-5 calculations")

    print("\n2. CENTER-BASED CAPACITY (Ages 0-5):")
    print("-" * 70)

    # Ages 0-2: Infant + Toddler
    infant_capacity = df['LICENSED CENTER INFANT CAPACITY'].sum()
    toddler_capacity = df['LICENSED CENTER TODDLER CAPACITY'].sum()
    capacity_0_2_center = infant_capacity + toddler_capacity

    print(f"   Infant (0-12 months):  {infant_capacity:>10,.0f}")
    print(f"   Toddler (13-35 months): {toddler_capacity:>10,.0f}")
    print(f"   Total ages 0-2:        {capacity_0_2_center:>10,.0f}")

    # Ages 3-5: Preschool
    preschool_capacity = df['LICENSED CENTER PRESCHOOL CAPACITY'].sum()
    print(f"\n   Preschool (3-5 years): {preschool_capacity:>10,.0f}")

    print("\n3. HOME-BASED CAPACITY (Mixed ages, need to estimate):")
    print("-" * 70)

    home_capacity_total = df['LICENSED HOME CAPACITY'].sum()
    print(f"   Total home capacity: {home_capacity_total:>10,.0f}")
    print("   ")
    print("   Estimation approach:")
    print("   - Home-based care typically serves ages 0-5 (not school-age)")
    print("   - Split: 40% ages 0-2, 60% ages 3-5 (typical ratios)")

    home_0_2 = home_capacity_total * 0.40
    home_3_5 = home_capacity_total * 0.60

    print(f"   Estimated ages 0-2: {home_0_2:>10,.0f}")
    print(f"   Estimated ages 3-5: {home_3_5:>10,.0f}")

    print("\n4. TOTAL CAPACITY FOR AGES 0-5:")
    print("-" * 70)

    df['capacity_0_2'] = capacity_0_2_center + home_0_2
    df['capacity_3_5'] = preschool_capacity + home_3_5
    df['capacity_0_5'] = df['capacity_0_2'] + df['capacity_3_5']

    total_0_2 = df['capacity_0_2'].iloc[0]  # These are constants
    total_3_5 = df['capacity_3_5'].iloc[0]
    total_0_5 = total_0_2 + total_3_5

    print(f"   Ages 0-2:  {total_0_2:>10,.0f} slots")
    print(f"   Ages 3-5:  {total_3_5:>10,.0f} slots")
    print(f"   Ages 0-5:  {total_0_5:>10,.0f} slots")

    print("\n5. VALIDATION:")
    print("-" * 70)
    total_licensed = df['TOTAL LICENSED CAPACITY'].sum()
    school_age_capacity = df['LICENSED SCHOOL AGE CAPACITY'].sum()

    print(f"   Total licensed (all ages):        {total_licensed:>10,.0f}")
    print(f"   School-age capacity:              {school_age_capacity:>10,.0f}")
    print(f"   Approx non-school-age:            {total_licensed - school_age_capacity:>10,.0f}")
    print(f"   Our ages 0-5 calculation:         {total_0_5:>10,.0f}")
    print(f"   ")
    print("   ✓ Our number should be LESS than total (excludes school-age)")
    print(f"   ✓ Difference: {total_licensed - total_0_5:>10,.0f} (school-age + other)")

    return df, {
        'capacity_0_2': total_0_2,
        'capacity_3_5': total_3_5,
        'capacity_0_5': total_0_5,
        'total_licensed_all_ages': total_licensed,
        'school_age_only': school_age_capacity
    }


def recalculate_county_aggregates(facilities_df):
    """
    Recalculate county-level aggregates with corrected capacity
    """
    df = facilities_df.copy()

    # Fill NaN
    df['LICENSED CENTER INFANT CAPACITY'] = df['LICENSED CENTER INFANT CAPACITY'].fillna(0)
    df['LICENSED CENTER TODDLER CAPACITY'] = df['LICENSED CENTER TODDLER CAPACITY'].fillna(0)
    df['LICENSED CENTER PRESCHOOL CAPACITY'] = df['LICENSED CENTER PRESCHOOL CAPACITY'].fillna(0)
    df['LICENSED HOME CAPACITY'] = df['LICENSED HOME CAPACITY'].fillna(0)

    # Calculate facility-level capacity for 0-5
    df['facility_capacity_0_2'] = (
        df['LICENSED CENTER INFANT CAPACITY'] +
        df['LICENSED CENTER TODDLER CAPACITY'] +
        df['LICENSED HOME CAPACITY'] * 0.40
    )

    df['facility_capacity_3_5'] = (
        df['LICENSED CENTER PRESCHOOL CAPACITY'] +
        df['LICENSED HOME CAPACITY'] * 0.60
    )

    df['facility_capacity_0_5'] = df['facility_capacity_0_2'] + df['facility_capacity_3_5']

    # Aggregate by county
    county_capacity = df.groupby('COUNTY').agg({
        'facility_capacity_0_2': 'sum',
        'facility_capacity_3_5': 'sum',
        'facility_capacity_0_5': 'sum',
        'PROVIDER NAME': 'count'
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

    county_capacity = county_capacity.sort_values('licensed_capacity_0_5', ascending=False)

    print("\n" + "="*70)
    print("CORRECTED COUNTY-LEVEL CAPACITY (Ages 0-5)")
    print("="*70)

    print(f"\nAggregated capacity for {len(county_capacity)} counties")
    print("\nTop 10 counties:")
    print("-" * 70)

    for _, row in county_capacity.head(10).iterrows():
        print(f"{row['county_name']:20} "
              f"{row['licensed_capacity_0_5']:>6,} slots "
              f"[0-2: {row['licensed_capacity_0_2']:>5,}, 3-5: {row['licensed_capacity_3_5']:>5,}] "
              f"({row['facility_count']:>4} facilities)")

    return county_capacity


if __name__ == "__main__":
    # Load facilities
    facilities = pd.read_csv('data/raw/childcare_facilities.csv')

    print(f"Loaded {len(facilities):,} childcare facilities\n")

    # Corrected capacity calculation
    facilities, summary = calculate_0_5_capacity_correct(facilities)

    # Recalculate county aggregates
    county_capacity = recalculate_county_aggregates(facilities)

    # Save corrected data
    county_capacity.to_csv('data/processed/county_capacity_supply_CORRECTED.csv', index=False)
    print(f"\n✓ Saved corrected data to data/processed/county_capacity_supply_CORRECTED.csv")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nCapacity for ages 0-5 ONLY: {summary['capacity_0_5']:>10,.0f} slots")
    print(f"  (vs {summary['total_licensed_all_ages']:,.0f} total licensed all ages)")
    print(f"\nDifference: {summary['total_licensed_all_ages'] - summary['capacity_0_5']:>10,.0f} slots")
    print("  ^ This is school-age (6-12+), camps, and other non-0-5 capacity")
