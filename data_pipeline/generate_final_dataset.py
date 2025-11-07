"""
Generate Final County Capacity Dataset with Current + Forecast Data

Creates county_capacity.csv with both 2025 (current) and 2029 (forecast) data
"""

import pandas as pd
import os
from calculate_gaps import (
    calculate_need_estimate,
    calculate_gap,
    classify_severity,
    merge_supply_demand,
    calculate_all_gaps
)


def generate_forecast_gaps(supply_df, forecast_df, year=2029):
    """
    Generate gap calculations for forecast year

    Assumes capacity remains constant at current (2025) levels

    Args:
        supply_df: Current capacity by county
        forecast_df: Forecasted population
        year: Forecast year

    Returns:
        DataFrame: Gap analysis for forecast year
    """
    print(f"\n{'='*70}")
    print(f"GENERATING {year} FORECAST GAPS")
    print(f"{'='*70}")
    print(f"\n⚠️  Assumption: Licensed capacity remains constant at 2025 levels")
    print("   This is a conservative forecast that highlights growing needs\n")

    # Filter forecast to specific year
    year_forecast = forecast_df[forecast_df['year'] == year].copy()

    # Merge with supply
    records = []

    for _, supply_row in supply_df.iterrows():
        county_name = supply_row['county_name']

        # Find matching forecast
        pop_row = year_forecast[year_forecast['county_name'] == county_name]

        if len(pop_row) == 0:
            print(f"  ⚠️  No forecast for {county_name}")
            continue

        pop_row = pop_row.iloc[0]

        # Ages 0-2
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', supply_row.get('county_fips', '')),
            'year': year,
            'age_group': '0-2',
            'population': pop_row['pop_0_2'],
            'licensed_capacity': supply_row['licensed_capacity_0_2'],  # CONSTANT
            'facility_count': supply_row['facility_count']
        })

        # Ages 3-5
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', supply_row.get('county_fips', '')),
            'year': year,
            'age_group': '3-5',
            'population': pop_row['pop_3_5'],
            'licensed_capacity': supply_row['licensed_capacity_3_5'],  # CONSTANT
            'facility_count': supply_row['facility_count']
        })

        # Ages 0-5
        records.append({
            'county_name': county_name,
            'county_fips': pop_row.get('county_fips', supply_row.get('county_fips', '')),
            'year': year,
            'age_group': '0-5',
            'population': pop_row['pop_0_5'],
            'licensed_capacity': supply_row['licensed_capacity_0_5'],  # CONSTANT
            'facility_count': supply_row['facility_count']
        })

    merged_df = pd.DataFrame(records)

    print(f"✓ Forecast data for {len(merged_df) // 3} counties")

    return merged_df


def combine_current_and_forecast(current_gaps, forecast_gaps):
    """
    Combine current year and forecast year gap data

    Args:
        current_gaps: 2025 gap calculations
        forecast_gaps: 2029 gap calculations

    Returns:
        DataFrame: Combined dataset
    """
    print(f"\n{'='*70}")
    print("COMBINING CURRENT AND FORECAST DATA")
    print(f"{'='*70}")

    # Concatenate
    combined = pd.concat([current_gaps, forecast_gaps], ignore_index=True)

    # Sort by county, year, age group
    combined = combined.sort_values(['county_name', 'year', 'age_group'])

    print(f"\n✓ Combined dataset:")
    print(f"  Years: {sorted(combined['year'].unique())}")
    print(f"  Counties: {combined['county_name'].nunique()}")
    print(f"  Total records: {len(combined)}")
    print(f"  Expected: {combined['county_name'].nunique()} counties × 2 years × 3 age groups = {combined['county_name'].nunique() * 2 * 3}")

    return combined


def analyze_forecast_changes(combined_df):
    """
    Analyze how gaps change from current to forecast

    Args:
        combined_df: Combined current + forecast data
    """
    print(f"\n{'='*70}")
    print("FORECAST IMPACT ANALYSIS")
    print(f"{'='*70}")

    # Compare 2025 vs 2029 for ages 0-5
    data_2025 = combined_df[(combined_df['year'] == 2025) & (combined_df['age_group'] == '0-5')]
    data_2029 = combined_df[(combined_df['year'] == 2029) & (combined_df['age_group'] == '0-5')]

    total_gap_2025 = data_2025['gap'].sum()
    total_gap_2029 = data_2029['gap'].sum()
    gap_increase = total_gap_2029 - total_gap_2025

    print(f"\nSTATEWIDE (Ages 0-5):")
    print(f"  2025 Gap: {total_gap_2025:>10,} slots")
    print(f"  2029 Gap: {total_gap_2029:>10,} slots")
    print(f"  Increase: {gap_increase:>10,} slots ({(gap_increase/total_gap_2025)*100:>5.1f}%)")

    # Counties with biggest gap increases
    print(f"\n\nTOP 10 COUNTIES WITH LARGEST GAP INCREASES:")
    print("-"*70)

    merged = data_2025[['county_name', 'gap']].merge(
        data_2029[['county_name', 'gap']],
        on='county_name',
        suffixes=('_2025', '_2029')
    )
    merged['gap_increase'] = merged['gap_2029'] - merged['gap_2025']
    merged['pct_increase'] = (merged['gap_increase'] / merged['gap_2025']) * 100

    top10 = merged.nlargest(10, 'gap_increase')

    for _, row in top10.iterrows():
        print(f"{row['county_name']:20} "
              f"2025: {row['gap_2025']:>6,.0f} → 2029: {row['gap_2029']:>6,.0f} "
              f"(+{row['gap_increase']:>4,.0f}, +{row['pct_increase']:>4.1f}%)")

    # Counties where gap improves (if any)
    improving = merged[merged['gap_increase'] < 0]
    if len(improving) > 0:
        print(f"\n\nCOUNTIES WHERE GAP IMPROVES (unlikely but possible):")
        print("-"*70)
        for _, row in improving.iterrows():
            print(f"{row['county_name']:20} {row['gap_2025']:>6,.0f} → {row['gap_2029']:>6,.0f}")
    else:
        print(f"\n\n✓ No counties improve - all gaps worsen (as expected with constant capacity)")


def save_final_dataset(combined_df, output_path='data/processed/county_capacity.csv'):
    """
    Save final county capacity dataset with current + forecast

    Args:
        combined_df: Combined data
        output_path: Where to save
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Select and order columns
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

    final_df = combined_df[columns_order].copy()

    # Save
    final_df.to_csv(output_path, index=False)

    print(f"\n\n{'='*70}")
    print("✓ FINAL DATASET SAVED")
    print(f"{'='*70}")
    print(f"\nFile: {output_path}")
    print(f"Records: {len(final_df)}")
    print(f"  {len(final_df[final_df['year'] == 2025])} records for 2025 (current)")
    print(f"  {len(final_df[final_df['year'] == 2029])} records for 2029 (forecast)")
    print(f"\nReady for Streamlit visualization!")


if __name__ == "__main__":
    print("GENERATING COMPLETE DATASET WITH FORECASTS")
    print("="*70)

    # Load supply data
    supply_df = pd.read_csv('data/processed/county_capacity_supply.csv')
    print(f"\n✓ Loaded supply data: {len(supply_df)} counties")

    # Load current population (Census 2022 → 2025)
    if os.path.exists('data/raw/census_population.csv'):
        current_pop = pd.read_csv('data/raw/census_population.csv')
        print(f"✓ Loaded Census population data: {len(current_pop)} counties")
    else:
        current_pop = pd.read_csv('data/raw/colorado_population.csv')
        print(f"✓ Loaded population estimates: {len(current_pop)} counties")

    # Load forecast population
    forecast_pop = pd.read_csv('data/raw/population_forecast.csv')
    print(f"✓ Loaded population forecasts: {len(forecast_pop[forecast_pop['year'] == 2029])} counties (2029)")

    # Generate 2025 (current) gaps
    print(f"\n{'='*70}")
    print("STEP 1: CURRENT YEAR (2025) GAPS")
    print(f"{'='*70}")

    # Set year to 2025 for current data
    current_pop_2025 = current_pop.copy()
    if 'year' not in current_pop_2025.columns:
        current_pop_2025['year'] = 2025

    merged_2025 = merge_supply_demand(supply_df, current_pop_2025)
    gaps_2025 = calculate_all_gaps(merged_2025)

    # Generate 2029 (forecast) gaps
    print(f"\n{'='*70}")
    print("STEP 2: FORECAST YEAR (2029) GAPS")
    print(f"{'='*70}")

    merged_2029 = generate_forecast_gaps(supply_df, forecast_pop, year=2029)
    gaps_2029 = calculate_all_gaps(merged_2029)

    # Combine
    combined = combine_current_and_forecast(gaps_2025, gaps_2029)

    # Analyze changes
    analyze_forecast_changes(combined)

    # Save
    save_final_dataset(combined)

    print(f"\n{'='*70}")
    print("✓ COMPLETE - Dataset ready for visualization")
    print(f"{'='*70}")
