#!/usr/bin/env python3
"""
Download Life Expectancy by Sex data from Our World in Data.

This script fetches both the data and metadata for life expectancy at birth
disaggregated by sex from OWID's API.
"""

import pandas as pd
import requests
import json
from pathlib import Path

# Output directory
output_dir = Path('../data')
output_dir.mkdir(exist_ok=True)

print("Fetching life expectancy data from Our World in Data...")

# Fetch the data
df = pd.read_csv(
    "https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex.csv?v=1&csvType=full&useColumnShortNames=true",
    storage_options={'User-Agent': 'Our World In Data data fetch/1.0'}
)

print(f"Data fetched: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())

# Save data to CSV
data_file = output_dir / 'owid_life_expectancy_by_sex.csv'
df.to_csv(data_file, index=False)
print(f"\nData saved to: {data_file}")

# Fetch the metadata
print("\nFetching metadata...")
metadata = requests.get(
    "https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex.metadata.json?v=1&csvType=full&useColumnShortNames=true"
).json()

# Save metadata to JSON
metadata_file = output_dir / 'owid_life_expectancy_by_sex_metadata.json'
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata saved to: {metadata_file}")

print("\nData summary:")
print(f"  Years: {df['Year'].min()} - {df['Year'].max()}")
print(f"  Entities: {df['Entity'].nunique()} unique")
print(f"  Sample entities: {df['Entity'].unique()[:10].tolist()}")

print("\nDone!")

