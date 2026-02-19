---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.20.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Neoplasms (Cancer) Drilldown Analysis

This notebook performs a drilldown analysis into neoplasms to identify which specific cancers and risk factors are driving the gender gap in Life Expectancy and HALE.

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display

from utils import (
    decorate, configure_plot_style, AIBM_COLORS, write_html_table
)

configure_plot_style()
```

## Data Loading

We have two data files from IHME GBD 2023 for the United States, separated by sex. These files contain death rates attributable to specific risk factors.

```python
location = 'usa' # 'usa', 'iceland', or 'oecd'
male_file = f'../data/ihme_cancer_drilldown_{location}_male.csv'
female_file = f'../data/ihme_cancer_drilldown_{location}_female.csv'

male_df = pd.read_csv(male_file)
female_df = pd.read_csv(female_file)

# Replace NaN with 0 in the Value column before analysis
male_df['Value'] = male_df['Value'].fillna(0)
female_df['Value'] = female_df['Value'].fillna(0)

print(f"Male data shape: {male_df.shape}")
print(f"Female data shape: {female_df.shape}")
```

### Basic Inventory

Let's look at the structure of the data.

```python
male_df.head()
```

### Column Analysis

```python
print("Columns in the dataset:")
for col in male_df.columns:
    print(f"- {col}")
```

### Unique Values

Let's see what categories we are working with.

```python
print("Unique Causes:")
male_df['Cause of death or injury'].unique()
```

```python
print("Unique Risk Factors:")
male_df['Risk factor'].unique()
```

```python
print("Unique Measures:")
male_df['Measure'].unique()
```

## Missing Value Analysis

Let's check for missing values in both datasets.

```python
def check_missing(df, name):
    print(f"\nMissing values in {name}:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("No missing values found.")
    else:
        display(missing[missing > 0])

check_missing(male_df, "Male Data")
check_missing(female_df, "Female Data")
```

### Data Availability by Cause and Risk Factor

Not all cancers have data for all three risk categories (Behavioral, Metabolic, Environmental). Let's see which ones do.

```python
def check_data_availability(df, name):
    print(f"\nData availability for {name} (Measure='Deaths per 100,000', Value > 0):")
    deaths_rate = df[df['Measure'] == 'Deaths per 100,000']
    availability = deaths_rate.groupby(['Cause of death or injury', 'Risk factor'])['Value'].apply(lambda x: (x > 0).sum()).unstack().fillna(0)
    display(availability)
    return availability

male_availability = check_data_availability(male_df, "Male")
female_availability = check_data_availability(female_df, "Female")
```

## Risk Factor Fractions

Before aggregating the data, let's see what fraction of the attributable death rate for each cancer is assigned to each risk factor category.

```python
def get_risk_fractions(df):
    # Filter for death rates
    df_filtered = df[df['Measure'] == 'Deaths per 100,000'].copy()
    
    # Pivot to get risk factors as columns
    pivot = df_filtered.pivot_table(
        index='Cause of death or injury', 
        columns='Risk factor', 
        values='Value', 
        fill_value=0
    )
    
    # Calculate total attributable rate for each cancer
    row_totals = pivot.sum(axis=1)
    
    # Calculate fractions (avoiding division by zero)
    fractions = pivot.divide(row_totals, axis=0).fillna(0)
    
    return fractions

print("Risk Factor Fractions (Male):")
male_fractions = get_risk_fractions(male_df)
male_fractions.head(10)
```

```python
print("Risk Factor Fractions (Female):")
female_fractions = get_risk_fractions(female_df)
female_fractions.head(10)
```

## Data Processing

We focus on the "Deaths per 100,000" measure. To find the total death rate attributable to the risk factors included in this dataset, we sum across the risk categories (Behavioral, Metabolic, Environmental/occupational) for each cancer type.

```python
def process_cancer_data(df):
    # Filter for death rates
    df_filtered = df[df['Measure'] == 'Deaths per 100,000'].copy()
    
    # Sum across risk factors to get total attributable death rate per cancer
    df_agg = df_filtered.groupby('Cause of death or injury')['Value'].sum().reset_index()
    
    return df_agg

male_rates = process_cancer_data(male_df)
female_rates = process_cancer_data(female_df)

# Merge male and female rates
merged_rates = pd.merge(
    male_rates, female_rates, 
    on='Cause of death or injury', 
    suffixes=('_Male', '_Female'),
    how='outer'
)

# Fill any remaining NaNs after the outer merge (for sex-specific cancers)
merged_rates = merged_rates.fillna(0)

# Rename columns for clarity
merged_rates.columns = ['Neoplasm', 'Male Rate', 'Female Rate']
```

## Computing the Gender Gap

We calculate the difference between male and female death rates. A positive difference indicates a higher death rate for males.

```python
# Calculate the difference
merged_rates['Difference'] = merged_rates['Male Rate'] - merged_rates['Female Rate']

# Sort by the absolute value of the difference to find the biggest drivers
merged_rates['abs_diff'] = merged_rates['Difference'].abs()
gap_table = merged_rates.sort_values(by='abs_diff', ascending=False).drop(columns=['abs_diff'])

# Display the top contributors
gap_table.head(10)
```

## Exporting Results

We export the full gap table to an HTML file for inclusion in the project's technical report.

```python
# Write to HTML
write_html_table(gap_table, f'tables/neoplasms_gap_{location}.html')
print(f"Table written to tables/neoplasms_gap_{location}.html")
```

## Risk Factor Analysis

While the table above shows the total attributable gap, we can also look at which risk factor categories are the primary drivers.

```python
def get_risk_breakdown(df, sex):
    df_filtered = df[df['Measure'] == 'Deaths per 100,000'].copy()
    breakdown = df_filtered.pivot_table(
        index='Cause of death or injury', 
        columns='Risk factor', 
        values='Value', 
        fill_value=0
    )
    breakdown.columns = [f"{col}_{sex}" for col in breakdown.columns]
    return breakdown

male_risk = get_risk_breakdown(male_df, 'Male')
female_risk = get_risk_breakdown(female_df, 'Female')

risk_merged = pd.concat([male_risk, female_risk], axis=1).fillna(0)

# Calculate gap by risk factor
for risk in ['Behavioral risks', 'Environmental/occupational risks', 'Metabolic risks']:
    risk_merged[f'Gap_{risk}'] = risk_merged[f'{risk}_Male'] - risk_merged[f'{risk}_Female']

# Select and sort gap columns
gap_cols = [col for col in risk_merged.columns if col.startswith('Gap_')]
risk_gap_summary = risk_merged[gap_cols].copy()
risk_gap_summary['Total Gap'] = risk_gap_summary.sum(axis=1)

# Add Neoplasm column and sort
risk_gap_summary.index.name = 'Neoplasm'
risk_gap_summary = risk_gap_summary.reset_index()
risk_gap_summary = risk_gap_summary.sort_values(by='Total Gap', ascending=False, key=abs)

# Export risk gap summary to HTML
write_html_table(risk_gap_summary, f'tables/neoplasms_risk_gap_{location}.html')
print(f"Risk gap table written to tables/neoplasms_risk_gap_{location}.html")

risk_gap_summary
```

```python
# compute the sum of Total Gap for all positive gaps and all negative gaps 
pos_sum = risk_gap_summary.loc[risk_gap_summary['Total Gap'] > 0, 'Total Gap'].sum()
neg_sum = risk_gap_summary.loc[risk_gap_summary['Total Gap'] < 0, 'Total Gap'].sum()

print(f"Sum of positive gaps: {pos_sum:.2f}")
print(f"Sum of negative gaps: {neg_sum:.2f}")
```

```python
# display the index of the rows where Total Gap is exactly zero 
risk_gap_summary[risk_gap_summary['Total Gap'] == 0].index
```
