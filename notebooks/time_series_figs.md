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

# Time Series Analysis: Life Expectancy Gap - Selected Countries

This minimal notebook loads life expectancy data and creates a plot showing selected countries with direct line labels.

## Setup

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import (
    configure_plot_style, get_oecd, compute_gender_gap,
    oecd_codes, code_to_who_country, load_ihme_indicator,
    column_name_mapping
)
from fig_utils import plot_gap_timeseries

configure_plot_style()

# Set maximum year for analysis (includes COVID-19 period 2020-2023)
max_year = 2023
min_year = 2000
```

## Helper Functions

```python
def compute_temporal_gaps(df, value_col, sexes=['Male', 'Female']):
    """
    Compute gender gaps for all years (not just most recent).
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with Year, Code, Sex, and value_col columns
    value_col : str
        Name of the value column
    sexes : list
        List of sex values to compare
        
    Returns
    -------
    df_gaps : pandas.DataFrame
        DataFrame with Gap and Mid columns for all years
    """
    return compute_gender_gap(df, value_col, sexes)

def convert_owid_le_to_temporal_format(df, min_year=2000, max_year=2023):
    """
    Convert OWID Life Expectancy data to temporal format.
    
    OWID format: Entity, Code, Year, life_expectancy__sex_female__age_0, life_expectancy__sex_male__age_0
    Target format: Code, Year, Sex, LifeExpectancy_Years
    """
    # Filter to years of interest
    df = df[(df['Year'] >= min_year) & (df['Year'] <= max_year)].copy()
    
    # Filter to OECD countries only
    df = df[df['Code'].isin(oecd_codes)].copy()
    
    # Reshape from wide to long format
    # Male data
    male_df = df[['Code', 'Year', 'life_expectancy__sex_male__age_0']].copy()
    male_df['Sex'] = 'Male'
    male_df = male_df.rename(columns={'life_expectancy__sex_male__age_0': 'LifeExpectancy_Years'})
    
    # Female data
    female_df = df[['Code', 'Year', 'life_expectancy__sex_female__age_0']].copy()
    female_df['Sex'] = 'Female'
    female_df = female_df.rename(columns={'life_expectancy__sex_female__age_0': 'LifeExpectancy_Years'})
    
    # Combine
    df_temporal = pd.concat([male_df, female_df], ignore_index=True)
    
    # Sort by country, sex, year
    df_temporal = df_temporal.sort_values(['Code', 'Sex', 'Year']).reset_index(drop=True)
    
    return df_temporal

def load_ihme_indicator_temporal(base_filename, value_col_name, indicator_code, indicator_name):
    """
    Load IHME indicator data and compute temporal gaps for all years.
    
    Parameters
    ----------
    base_filename : str
        Base filename without path, sex suffix, or extension (e.g., 'ihme_road_injuries_deaths')
    value_col_name : str
        Name of the value column (e.g., 'RoadInjuriesDeathRate')
    indicator_code : str
        Indicator code (e.g., 'IHME_ROAD_INJURIES')
    indicator_name : str
        Human-readable indicator name
        
    Returns
    -------
    df_temporal : pandas.DataFrame
        DataFrame with temporal gaps computed for all years
    """
    filename_male = f'../data/{base_filename}_male.csv'
    filename_female = f'../data/{base_filename}_female.csv'
    df = load_ihme_indicator(
        filename_male, filename_female,
        value_col_name=value_col_name,
        indicator_code=indicator_code,
        indicator_name=indicator_name,
        min_year=min_year,
        max_year=max_year
    )
    df = df.rename(columns=column_name_mapping)
    col = column_name_mapping.get(value_col_name, value_col_name)
    df_temporal = compute_temporal_gaps(df, col, sexes=['Male', 'Female'])
    return df_temporal
```

## Load Life Expectancy Data

```python
# Load OWID Life Expectancy data
owid_le_file = '../data/owid_life_expectancy_by_sex.csv'
owid_le_raw = pd.read_csv(owid_le_file)

# Convert to temporal format
le_temporal = convert_owid_le_to_temporal_format(owid_le_raw, min_year=min_year, max_year=max_year)

# Compute gaps for all years (preserve temporal structure)
# Note: compute_gender_gap computes Gap as Male - Female, but we want Female - Male
le_temporal = compute_temporal_gaps(le_temporal, 'LifeExpectancy_Years', sexes=['Male', 'Female'])
# Calculate gap as Female - Male (positive gap means women live longer)
# Gap_LifeExpectancy_Years is Male - Female, so we negate it
le_temporal['LE_gap'] = -le_temporal['Gap_LifeExpectancy_Years']

print(f"Life Expectancy temporal data: {le_temporal.shape}")
print(f"Years: {le_temporal['Year'].min():.0f} - {le_temporal['Year'].max():.0f}")
print(f"Countries: {le_temporal['Code'].nunique()}")
le_temporal.query('Year == 2023').sort_values(by='Gap_LifeExpectancy_Years')
```

## Plot Selected Countries

```python
# Selected countries to highlight
selected_countries = ['USA', 'GBR', 'NOR', 'FRA', 'CAN', 'LTU', 'JPN']

# Plot Life Expectancy gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    le_temporal.reset_index(),
    'LE_gap',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Life Expectancy Gender Gap Over Time: Selected Countries',
    ylabel='Life Expectancy Gap (years)'
)
plt.savefig('figs/le_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

## Load Road Traffic Death Rate Data

```python
# Load IHME Road Traffic Injuries data
road_injuries_temporal = load_ihme_indicator_temporal(
    'ihme_road_injuries_deaths',
    'RoadInjuriesDeathRate',
    'IHME_ROAD_INJURIES',
    'Road injuries (road traffic crashes), death rate per 100,000'
)

print(f"Road Traffic temporal data: {road_injuries_temporal.shape}")
print(f"Years: {road_injuries_temporal['Year'].min():.0f} - {road_injuries_temporal['Year'].max():.0f}")
print(f"Countries: {road_injuries_temporal['Code'].nunique()}")
road_injuries_temporal.query('Year == 2023').sort_values(by='Gap_RoadTraffic')
```

## Plot Road Traffic Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'CRI', 'CAN', 'LTU', 'MEX']


# Plot Road Traffic gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    road_injuries_temporal.reset_index(),
    'Gap_RoadTraffic',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Road Traffic Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='Road Traffic Death Rate Gap (per 100,000)'
)
plt.savefig('figs/road_traffic_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
road_injuries_temporal.query('Code=="USA"')['Gap_RoadTraffic']
```

## Load Homicide Death Rate Data

```python
# Load IHME Interpersonal Violence (Homicide) data
homicide_temporal = load_ihme_indicator_temporal(
    'ihme_interpersonal_violence_deaths',
    'InterpersonalViolenceDeathRate',
    'IHME_INTERPERSONAL_VIOLENCE',
    'Interpersonal violence (homicide), death rate per 100,000'
)

print(f"Homicide temporal data: {homicide_temporal.shape}")
print(f"Years: {homicide_temporal['Year'].min():.0f} - {homicide_temporal['Year'].max():.0f}")
print(f"Countries: {homicide_temporal['Code'].nunique()}")
homicide_temporal.query('Year == 2023').sort_values(by='Gap_Homicide')
```

## Plot Homicide Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'COL', 'LTU', 'MEX', 'CRI']

# Plot Homicide gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    homicide_temporal.reset_index(),
    'Gap_Homicide',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Homicide Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='Homicide Death Rate Gap (per 100,000)'
)
plt.ylim(-1, 65)
plt.savefig('figs/homicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
homicide_temporal.query('Code=="USA"')['Gap_Homicide']
```

## Load Suicide Death Rate Data

```python
# Load IHME Self-Harm (Suicide) data
suicide_temporal = load_ihme_indicator_temporal(
    'ihme_self_harm_deaths',
    'SelfHarmDeathRate',
    'IHME_SELF_HARM',
    'Self-harm (suicide), death rate per 100,000'
)

print(f"Suicide temporal data: {suicide_temporal.shape}")
print(f"Years: {suicide_temporal['Year'].min():.0f} - {suicide_temporal['Year'].max():.0f}")
print(f"Countries: {suicide_temporal['Code'].nunique()}")
suicide_temporal.query('Year == 2023').sort_values(by='Gap_Suicide')
```

## Plot Suicide Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'TUR', 'LTU', 'CAN', 'KOR']

# Plot Suicide gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    suicide_temporal.reset_index(),
    'Gap_Suicide',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Suicide Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='Suicide Death Rate Gap (per 100,000)'
)
plt.savefig('figs/suicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
suicide_temporal.query('Code=="USA"')['Gap_Suicide']
```

## Load Cancer Death Rate Data

```python
# Load IHME Neoplasms (Cancer) data
cancer_temporal = load_ihme_indicator_temporal(
    'ihme_neoplasms_deaths',
    'NeoplasmsDeathRate',
    'IHME_NEOPLASMS',
    'Neoplasms (cancer), death rate per 100,000'
)

print(f"Cancer temporal data: {cancer_temporal.shape}")
print(f"Years: {cancer_temporal['Year'].min():.0f} - {cancer_temporal['Year'].max():.0f}")
print(f"Countries: {cancer_temporal['Code'].nunique()}")
cancer_temporal.query('Year == 2023').sort_values(by='Gap_Neoplasms')
```

## Plot Cancer Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'JPN', 'LTU', 'NLD', 'COL']

# Plot Cancer gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    cancer_temporal.reset_index(),
    'Gap_Neoplasms',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Cancer Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='Cancer Death Rate Gap (per 100,000)'
)
plt.savefig('figs/cancer_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
cancer_temporal.query('Code=="USA"')['Gap_Neoplasms']
```

## Load Drug Disorders Death Rate Data

```python
# Load IHME Drug Disorders data
drug_disorders_temporal = load_ihme_indicator_temporal(
    'ihme_drug_disorder_deaths',
    'DrugDisorderDeathRate',
    'IHME_DRUG_DISORDERS',
    'Drug use disorders, death rate per 100,000'
)

print(f"Drug Disorders temporal data: {drug_disorders_temporal.shape}")
print(f"Years: {drug_disorders_temporal['Year'].min():.0f} - {drug_disorders_temporal['Year'].max():.0f}")
print(f"Countries: {drug_disorders_temporal['Code'].nunique()}")
drug_disorders_temporal.query('Year == 2023').sort_values(by='Gap_DrugDisorder')
```

## Plot Drug Disorders Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'KOR', 'LTU', 'CAN']

# Plot Drug Disorders gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    drug_disorders_temporal.reset_index(),
    'Gap_DrugDisorder',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='Drug Disorders Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='Drug Disorders Death Rate Gap (per 100,000)'
)
plt.savefig('figs/drug_disorders_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
drug_disorders_temporal.query('Code=="USA"')['Gap_DrugDisorder']
```

## Load COVID-19 Death Rate Data

```python
# Load IHME COVID-19 data
covid_temporal = load_ihme_indicator_temporal(
    'ihme_covid19_deaths',
    'COVID19DeathRate',
    'IHME_COVID19',
    'COVID-19, death rate per 100,000'
)

print(f"COVID-19 temporal data: {covid_temporal.shape}")
print(f"Years: {covid_temporal['Year'].min():.0f} - {covid_temporal['Year'].max():.0f}")
print(f"Countries: {covid_temporal['Code'].nunique()}")
covid_temporal.query('Year == 2023').sort_values(by='Gap_COVID')
```

## Plot COVID-19 Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'KOR', 'LTU', 'CAN']

# Plot COVID-19 gap for selected countries
# Non-selected countries will be shown in gray, selected countries in colors
# Labels will be placed directly on the right side of the figure
fig, ax = plot_gap_timeseries(
    covid_temporal.reset_index(),
    'Gap_COVID',
    selected_countries=selected_countries,
    label_lines=True,  # Use direct labels instead of legend
    title='COVID-19 Death Rate Gender Gap Over Time: Selected Countries',
    ylabel='COVID-19 Death Rate Gap (per 100,000)'
)
plt.savefig('figs/covid19_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
covid_temporal.query('Code=="USA"')['Gap_COVID']
```
