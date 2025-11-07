"""
Calculate Childcare Capacity Gaps for Colorado Counties

Combines supply (licensed capacity) and demand (population estimates)
to calculate gaps by county and age group
"""

import pandas as pd
import os


def calculate_need_estimate(population, age_group):
    """
    Calculate estimated childcare need based on population

    Uses participation rate assumptions:
    - Ages 0-2: 60% (working parents + childcare preference)
    - Ages 3-5: 70% (higher pre-K participation)

    Args:
        population: int, number of children in age group
        age_group: str, "0-2" or "3-5"

    Returns:
        int, estimated number of children needing care
    """
    participation_rates = {
        "0-2": 0.60,
        "3-5": 0.70
    }

    rate = participation_rates.get(age_group, 0.65)
    return int(population * rate)


def calculate_gap(need_estimate, licensed_capacity):
    """
    Calculate gap between need and supply

    Args:
        need_estimate: Estimated demand
        licensed_capacity: Available supply

    Returns:
        tuple: (gap, gap_pct)
            gap: Positive = shortage, Negative = oversupply
            gap_pct: Gap as percentage of need
    """
    gap = need_estimate - licensed_capacity

    if need_estimate > 0:
        gap_pct = gap / need_estimate
    else:
        gap_pct = 0.0

    return gap, gap_pct


def classify_severity(gap_pct):
    """
    Classify gap severity based on percentage

    Returns:
        tuple: (severity_label, color_code)
    """
    if gap_pct > 0.30:
        return "Critical", "#d32f2f"
    elif gap_pct > 0.20:
        return "Significant", "#f57c00"
    elif gap_pct > 0.10:
        return "Moderate", "#fbc02d"
    elif gap_pct > 0.05:
        return "Low", "#9ccc65"
    else:
        return "Adequate", "#66bb6a"


def merge_supply_demand(supply_df, demand_df):
    """
    Merge supply and demand data by county

    Args:
        supply_df: County capacity data (from analyze_capacity.py)
        demand_df: Population data (from fetch_colorado_population.py)

    Returns:
        DataFrame: Merged data ready for gap calculation
    """
    print("="*70)
    print("MERGING SUPPLY AND DEMAND DATA")
    print("="*70)

    # Ensure consistent county names (capitalize)
    supply_df['county_name'] = supply_df['county_name'].str.title()
    demand_df['county_name'] = demand_df['county_name'].str.title()

    # For now, we'll create separate rows for each age group
    # This matches our target schema: one row per county-age_group combination

    records = []

    for _, supply_row in supply_df.iterrows():
        county_name = supply_row['county_name']

        # Find matching population data
        pop_row = demand_df[demand_df['county_name'] == county_name]

        if len(pop_row) == 0:
            print(f"  ⚠️  No population data for {county_name}")
            continue

        pop_row = pop_row.iloc[0]

        # Ages 0-2
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', ''),
            'year': 2025,  # Current year
            'age_group': '0-2',
            'population': pop_row['pop_0_2'],
            'licensed_capacity': supply_row['licensed_capacity_0_2'],
            'facility_count': supply_row['facility_count']
        })

        # Ages 3-5
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', ''),
            'year': 2025,
            'age_group': '3-5',
            'population': pop_row['pop_3_5'],
            'licensed_capacity': supply_row['licensed_capacity_3_5'],
            'facility_count': supply_row['facility_count']
        })

        # Ages 0-5 (combined)
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', ''),
            'year': 2025,
            'age_group': '0-5',
            'population': pop_row['pop_0_5'],
            'licensed_capacity': supply_row['licensed_capacity_0_5'],
            'facility_count': supply_row['facility_count']
        })

    merged_df = pd.DataFrame(records)

    print(f"\n✓ Merged data for {len(merged_df) // 3} counties")
    print(f"  Total records: {len(merged_df)} (3 age groups per county)")

    return merged_df


def calculate_all_gaps(merged_df):
    """
    Calculate gaps for all counties and age groups

    Args:
        merged_df: Merged supply/demand data

    Returns:
        DataFrame: Complete gap analysis
    """
    print("\n" + "="*70)
    print("CALCULATING CAPACITY GAPS")
    print("="*70)

    df = merged_df.copy()

    # Calculate need estimates
    df['participation_rate'] = df['age_group'].map({'0-2': 0.60, '3-5': 0.70, '0-5': 0.65})
    df['need_estimate'] = (df['population'] * df['participation_rate']).round().astype(int)

    # Calculate gaps
    df['gap'] = df['need_estimate'] - df['licensed_capacity']
    df['gap_pct'] = df.apply(
        lambda row: row['gap'] / row['need_estimate'] if row['need_estimate'] > 0 else 0,
        axis=1
    )

    # Classify severity
    df[['severity', 'color_code']] = df['gap_pct'].apply(
        lambda x: pd.Series(classify_severity(x))
    )

    # Add metadata
    df['data_source'] = 'CO Open Data + CO Demography Office'
    df['last_updated'] = pd.Timestamp.now().strftime('%Y-%m-%d')

    print("\n✓ Calculated gaps for all counties")
    print(f"\nSeverity distribution (all age groups):")
    print(df['severity'].value_counts().to_string())

    return df


def analyze_gap_results(gap_df):
    """
    Analyze and print gap calculation results

    Args:
        gap_df: DataFrame with gap calculations
    """
    print("\n" + "="*70)
    print("GAP ANALYSIS RESULTS")
    print("="*70)

    # Overall statistics
    total_pop = gap_df[gap_df['age_group'] == '0-5']['population'].sum()
    total_capacity = gap_df[gap_df['age_group'] == '0-5']['licensed_capacity'].sum()
    total_need = gap_df[gap_df['age_group'] == '0-5']['need_estimate'].sum()
    total_gap = gap_df[gap_df['age_group'] == '0-5']['gap'].sum()

    print(f"\nSTATEWIDE (Ages 0-5):")
    print(f"  Population:          {total_pop:>10,} children")
    print(f"  Licensed Capacity:   {total_capacity:>10,} slots")
    print(f"  Estimated Need:      {total_need:>10,} slots")
    print(f"  GAP:                 {total_gap:>10,} slots")
    print(f"  Gap %:               {(total_gap/total_need)*100:>9.1f}%")

    # By age group
    print(f"\nBY AGE GROUP:")
    for age_group in ['0-2', '3-5']:
        age_data = gap_df[gap_df['age_group'] == age_group]
        ag_pop = age_data['population'].sum()
        ag_cap = age_data['licensed_capacity'].sum()
        ag_need = age_data['need_estimate'].sum()
        ag_gap = age_data['gap'].sum()

        print(f"\n  Ages {age_group}:")
        print(f"    Population:        {ag_pop:>10,}")
        print(f"    Capacity:          {ag_cap:>10,}")
        print(f"    Need:              {ag_need:>10,}")
        print(f"    Gap:               {ag_gap:>10,} ({(ag_gap/ag_need)*100:>5.1f}%)")

    # Top 10 counties with largest gaps
    print(f"\n\nTOP 10 COUNTIES WITH LARGEST GAPS (Ages 0-5):")
    print("-"*70)

    top_gaps = gap_df[gap_df['age_group'] == '0-5'].nlargest(10, 'gap')

    for _, row in top_gaps.iterrows():
        print(f"{row['county_name']:20} "
              f"Gap: {row['gap']:>6,} ({row['gap_pct']*100:>5.1f}%)  "
              f"[{row['severity']}]")

    # Counties with oversupply
    print(f"\n\nCOUNTIES WITH OVERSUPPLY (Ages 0-5):")
    print("-"*70)

    oversupply = gap_df[(gap_df['age_group'] == '0-5') & (gap_df['gap'] < 0)]

    if len(oversupply) > 0:
        for _, row in oversupply.iterrows():
            print(f"{row['county_name']:20} "
                  f"Oversupply: {abs(row['gap']):>5,} slots ({row['gap_pct']*100:>6.1f}%)")
    else:
        print("  None - all counties have gaps")

    return {
        'total_gap': total_gap,
        'total_need': total_need,
        'gap_pct': (total_gap / total_need) * 100 if total_need > 0 else 0
    }


def save_county_capacity(gap_df, output_path='data/processed/county_capacity.csv'):
    """
    Save final county capacity dataset

    This is the main output file used by the Streamlit app

    Args:
        gap_df: DataFrame with complete gap analysis
        output_path: Where to save
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Select and order columns for final output
    columns_order = [
        'county_fips',
        'county_name',
        'year',
        'age_group',
        'population',
        'licensed_capacity',
        'participation_rate',
        'need_estimate',
        'gap',
        'gap_pct',
        'severity',
        'color_code',
        'facility_count',
        'data_source',
        'last_updated'
    ]

    final_df = gap_df[columns_order].copy()

    # Sort by county name and age group
    final_df = final_df.sort_values(['county_name', 'age_group'])

    # Save
    final_df.to_csv(output_path, index=False)

    print(f"\n\n✓ Saved final county capacity dataset to {output_path}")
    print(f"  {len(final_df)} records ({len(final_df) // 3} counties × 3 age groups)")

    return final_df


if __name__ == "__main__":
    print("Loading data...")

    # Load supply data
    supply_df = pd.read_csv('data/processed/county_capacity_supply.csv')
    print(f"  Supply: {len(supply_df)} counties")

    # Load demand data (prefer Census data if available)
    if os.path.exists('data/raw/census_population.csv'):
        demand_df = pd.read_csv('data/raw/census_population.csv')
        data_source = "Census ACS 2022"
        print(f"  Demand: {len(demand_df)} counties (Census ACS 2022)")
    else:
        demand_df = pd.read_csv('data/raw/colorado_population.csv')
        data_source = "Estimates 2023"
        print(f"  Demand: {len(demand_df)} counties (Estimates)")

    # Merge
    merged_df = merge_supply_demand(supply_df, demand_df)

    # Calculate gaps
    gap_df = calculate_all_gaps(merged_df)

    # Analyze results
    stats = analyze_gap_results(gap_df)

    # Save final output
    final_df = save_county_capacity(gap_df)

    print("\n" + "="*70)
    print("✓ GAP CALCULATION COMPLETE")
    print("="*70)
    print(f"\nColorado has a statewide gap of {stats['total_gap']:,} childcare slots")
    print(f"That's {stats['gap_pct']:.1f}% of estimated need")
