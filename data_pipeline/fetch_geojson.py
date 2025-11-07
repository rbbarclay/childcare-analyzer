"""
Fetch Colorado County GeoJSON Boundaries
Downloads US counties GeoJSON and filters to Colorado (FIPS codes starting with "08")
"""

import requests
import json
import os


def fetch_colorado_counties(output_path='data/geo/colorado_counties.geojson'):
    """
    Fetch Colorado county boundaries from Plotly's public GeoJSON dataset

    Args:
        output_path: Path to save the filtered Colorado counties GeoJSON

    Returns:
        dict: GeoJSON FeatureCollection of Colorado counties
    """
    print("Fetching US counties GeoJSON from Plotly datasets...")

    # Public GeoJSON source with US county boundaries
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        all_counties = response.json()

        print(f"Downloaded {len(all_counties['features'])} US counties")

        # Filter to Colorado counties (FIPS codes starting with "08")
        co_counties = {
            "type": "FeatureCollection",
            "features": [
                feature for feature in all_counties["features"]
                if feature.get("id", "").startswith("08")
            ]
        }

        print(f"Filtered to {len(co_counties['features'])} Colorado counties")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to file
        with open(output_path, 'w') as f:
            json.dump(co_counties, f, indent=2)

        print(f"✓ Saved Colorado counties GeoJSON to {output_path}")

        # Validate we have all 64 counties
        if len(co_counties['features']) != 64:
            print(f"⚠️  WARNING: Expected 64 Colorado counties, found {len(co_counties['features'])}")

        return co_counties

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching GeoJSON: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing GeoJSON: {e}")
        raise


def list_colorado_counties(geojson_path='data/geo/colorado_counties.geojson'):
    """
    List all Colorado counties in the GeoJSON file

    Args:
        geojson_path: Path to Colorado counties GeoJSON
    """
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)

    print("\nColorado Counties in GeoJSON:")
    print("-" * 50)

    counties = []
    for feature in geojson['features']:
        fips = feature['id']
        # Try to get county name from properties
        name = feature.get('properties', {}).get('NAME', 'Unknown')
        counties.append((fips, name))

    # Sort by FIPS code
    counties.sort()

    for fips, name in counties:
        print(f"{fips}: {name}")

    print("-" * 50)
    print(f"Total: {len(counties)} counties")

    return counties


if __name__ == "__main__":
    # Fetch and save GeoJSON
    geojson = fetch_colorado_counties()

    # List all counties
    list_colorado_counties()
