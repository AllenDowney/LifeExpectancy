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

# Time Series Analysis: Trends in Health Indicators and Gender Gaps

This notebook visualizes trends over time for health indicators, gender gaps, and target variables (HALE gap and Life Expectancy gap). It provides comprehensive time series visualizations showing how health patterns have evolved from 2000 to 2023 (including COVID-19 period).

## Setup

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
from scipy.stats import linregress

from utils import (
    decorate, underride, configure_plot_style, AIBM_COLORS, 
    code_to_who_country, code_to_wef_country, write_html_table,
    load_and_inventory, compute_gender_gap, summarize_gap, scatter_plot,
    get_oecd, summarize_years, plot_cdfs, plot_distributions,
    column_name_mapping, oecd_codes, load_ihme_indicator
)

configure_plot_style()

# Set maximum year for analysis (includes COVID-19 period 2020-2023)
max_year = 2023
min_year = 2000
```

## Helper Functions

```python
def load_temporal_data(filename, sex_mapping=None, value_col=None, indicator_type='WHO'):
    """
    Load temporal data for time series analysis, preserving all years.
    
    Parameters
    ----------
    filename : str
        Path to the CSV file
    sex_mapping : dict, optional
        Mapping to convert sex codes to standard names (e.g., {'SEX_MLE': 'Male'})
    value_col : str, optional
        Name of the value column (for IHME data, will be set automatically)
    indicator_type : str
        'WHO' or 'IHME'
        
    Returns
    -------
    df : pandas.DataFrame
        DataFrame with all years preserved, ready for time series analysis
    """
    if indicator_type == 'WHO':
        df, years = load_and_inventory(filename)
        if sex_mapping:
            df['Sex'] = df['Sex'].replace(sex_mapping)
    else:  # IHME - will be loaded separately using load_ihme_indicator
        raise ValueError("For IHME data, use load_ihme_indicator directly")
    
    return df

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
```

## Load Target Variables

### HALE Data (IHME - extends to 2023)

Using IHME HALE data for extended temporal coverage through 2023 (vs 2000-2021 for WHO).

```python
# Load IHME HALE data
filename = '../data/IHME-GBD_2023_DATA-fc42b373-1.csv'
ihme_hale_raw = pd.read_csv(filename)

# Convert IHME HALE to temporal format
def convert_ihme_hale_to_temporal_format(df, min_year=2000, max_year=2023):
    """
    Convert IHME HALE data to temporal format.
    
    IHME format: location_name, year, sex_name, val, upper, lower
    Target format: Code, Year, Sex, HALE_Years
    """
    # Create reverse mapping from country name to code
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    
    # Map IHME country names that differ from WHO names
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States',
        'Türkiye': 'Turkey'
    }
    
    # Start with a copy
    df = df.copy()
    
    # Filter to years of interest
    df = df[(df['year'] >= min_year) & (df['year'] <= max_year)].copy()
    
    # Map IHME country names to WHO country names
    df['location_name'] = df['location_name'].replace(ihme_country_name_mapping)
    
    # Convert country names to codes
    df['Code'] = df['location_name'].map(who_country_to_code)
    
    # Filter out rows where country mapping failed
    df = df[df['Code'].notna()].copy()
    
    # Filter to OECD countries only
    df = df[df['Code'].isin(oecd_codes)].copy()
    
    # Map sex values
    df['Sex'] = df['sex_name'].map({'Male': 'Male', 'Female': 'Female', 'Both': 'Both'})
    
    # Rename columns
    df = df.rename(columns={'year': 'Year', 'val': 'HALE_Years'})
    
    # Select and reorder columns
    df_temporal = df[['Code', 'Year', 'Sex', 'HALE_Years']].copy()
    
    # Sort by country, sex, year
    df_temporal = df_temporal.sort_values(['Code', 'Sex', 'Year']).reset_index(drop=True)
    
    return df_temporal

hale_temporal = convert_ihme_hale_to_temporal_format(ihme_hale_raw, min_year=min_year, max_year=max_year)
```

```python
# Compute gaps for all years (preserve temporal structure)
# Note: compute_gender_gap computes Gap as Male - Female, but we want Female - Male
hale_temporal = compute_temporal_gaps(hale_temporal, 'HALE_Years', sexes=['Male', 'Female'])
# Calculate gap as Female - Male (positive gap means women live longer)
# Gap_HALE_Years is Male - Female, so we negate it
hale_temporal['HALE_gap'] = -hale_temporal['Gap_HALE_Years']
print(f"HALE temporal data: {hale_temporal.shape}")
print(f"Years: {hale_temporal['Year'].min():.0f} - {hale_temporal['Year'].max():.0f}")
print(f"Countries: {hale_temporal['Code'].nunique()}")
hale_temporal.head()
```

### Life Expectancy Data (OWID - extends to 2023)

Using OWID Life Expectancy data for extended temporal coverage through 2023 (vs 2000-2021 for WHO).

```python
# Load OWID Life Expectancy data
owid_le_file = '../data/owid_life_expectancy_by_sex.csv'
owid_le_raw = pd.read_csv(owid_le_file)

# Convert OWID LE to temporal format
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

le_temporal = convert_owid_le_to_temporal_format(owid_le_raw, min_year=min_year, max_year=max_year)
```

```python
# Compute gaps for all years (preserve temporal structure)
# Note: compute_gender_gap computes Gap as Male - Female, but we want Female - Male
le_temporal = compute_temporal_gaps(le_temporal, 'LifeExpectancy_Years', sexes=['Male', 'Female'])
# Calculate gap as Female - Male (positive gap means women live longer)
# Gap_LifeExpectancy_Years is Male - Female, so we negate it
le_temporal['LE_gap'] = -le_temporal['Gap_LifeExpectancy_Years']
print(f"Life Expectancy temporal data: {le_temporal.shape}")
print(f"Years: {le_temporal['Year'].min():.0f} - {le_temporal['Year'].max():.0f}")
print(f"Countries: {le_temporal['Code'].nunique()}")
le_temporal.head()
```

## Load Predictor Indicators

We'll load all indicators used in the final model. For time series analysis, we need to preserve all years, so we use `compute_temporal_gaps` instead of `summarize_gap`.

### Alcohol Use Disorders (IHME)

```python
def load_ihme_indicator_temporal(base_filename, value_col_name, indicator_code, indicator_name):
    """
    Load IHME indicator data and compute temporal gaps for all years.
    
    Parameters
    ----------
    base_filename : str
        Base filename without path, sex suffix, or extension (e.g., 'ihme_alcohol_use_disorders_deaths')
    value_col_name : str
        Name of the value column (e.g., 'AlcoholUseDisordersDeathRate')
    indicator_code : str
        Indicator code (e.g., 'IHME_ALCOHOL_USE_DISORDERS')
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

alcohol_temporal = load_ihme_indicator_temporal(
    'ihme_alcohol_use_disorders_deaths',
    'AlcoholUseDisordersDeathRate',
    'IHME_ALCOHOL_USE_DISORDERS',
    'Alcohol use disorders, death rate per 100,000'
)
alcohol_temporal.head()
```

### Cardiovascular Disease (IHME)

```python
cardiovascular_temporal = load_ihme_indicator_temporal(
    'ihme_cardiovascular_deaths',
    'CardioDeathRate',
    'IHME_CARDIOVASCULAR',
    'Cardiovascular diseases, death rate per 100,000'
)
cardiovascular_temporal.head()
```

### Chronic Respiratory Disease (IHME)

```python
chronic_respiratory_temporal = load_ihme_indicator_temporal(
    'ihme_chronic_respiratory_deaths',
    'ChronicRespiratoryDeathRate',
    'IHME_CHRONIC_RESPIRATORY',
    'Chronic respiratory diseases, death rate per 100,000'
)
chronic_respiratory_temporal.head()
```

### Self-Harm/Suicide (IHME)

```python
self_harm_temporal = load_ihme_indicator_temporal(
    'ihme_self_harm_deaths',
    'SelfHarmDeathRate',
    'IHME_SELF_HARM',
    'Self-harm (suicide), death rate per 100,000'
)
self_harm_temporal.head()
```

### Interpersonal Violence/Homicide (IHME)

```python
interpersonal_violence_temporal = load_ihme_indicator_temporal(
    'ihme_interpersonal_violence_deaths',
    'InterpersonalViolenceDeathRate',
    'IHME_INTERPERSONAL_VIOLENCE',
    'Interpersonal violence (homicide), death rate per 100,000'
)
interpersonal_violence_temporal.head()
```

### Road Injuries (IHME)

```python
road_injuries_temporal = load_ihme_indicator_temporal(
    'ihme_road_injuries_deaths',
    'RoadInjuriesDeathRate',
    'IHME_ROAD_INJURIES',
    'Road injuries (road traffic crashes), death rate per 100,000'
)
road_injuries_temporal.head()
```

### Liver Disease (IHME)

```python
liver_disease_temporal = load_ihme_indicator_temporal(
    'ihme_liver_disease_deaths',
    'LiverDiseaseDeathRate',
    'IHME_LIVER_DISEASE',
    'Cirrhosis and other chronic liver diseases, death rate per 100,000'
)
liver_disease_temporal.head()
```

### Neoplasms (IHME)

```python
neoplasms_temporal = load_ihme_indicator_temporal(
    'ihme_neoplasms_deaths',
    'NeoplasmsDeathRate',
    'IHME_NEOPLASMS',
    'Neoplasms (cancer), death rate per 100,000'
)
neoplasms_temporal.head()
```

### Unintentional Injuries (IHME)

```python
unintentional_injuries_temporal = load_ihme_indicator_temporal(
    'ihme_unintentional_injuries_deaths',
    'UnintentionalInjuriesDeathRate',
    'IHME_UNINTENTIONAL_INJURIES',
    'Unintentional injuries, death rate per 100,000'
)
unintentional_injuries_temporal.head()
```

### Diabetes Type 2 (IHME)

```python
diabetes_temporal = load_ihme_indicator_temporal(
    'ihme_diabetes_deaths',
    'DiabetesDeathRate',
    'IHME_DIABETES_TYPE2',
    'Diabetes mellitus type 2, death rate per 100,000'
)
diabetes_temporal.head()
```

## Indicator Statistics Over Time

### Compute Means and Slopes for Each Indicator

```python
def compute_indicator_stats(df_temporal, mid_col, gap_col):
    """
    Compute statistics for each country: mean and slope (trend) over time.
    
    Parameters
    ----------
    df_temporal : pandas.DataFrame
        DataFrame with Year, Code, Country, and value columns
    mid_col : str
        Name of the Mid (rate) column
    gap_col : str
        Name of the Gap column
        
    Returns
    -------
    stats_df : pandas.DataFrame
        DataFrame with Code, Country, and statistics columns
    """
    # Filter to OECD countries
    df = df_temporal.reset_index() if 'Code' in df_temporal.index.names else df_temporal
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    stats_list = []
    
    for code in df_oecd['Code'].unique():
        country_data = df_oecd[df_oecd['Code'] == code].copy()
        country_data = country_data.sort_values('Year')
        
        if len(country_data) < 2:
            continue  # Need at least 2 years to compute slope
        
        country_name = country_data['Country'].iloc[0]
        
        # Compute means
        mid_mean = country_data[mid_col].mean()
        gap_mean = country_data[gap_col].mean()
        
        # Compute slopes using linregress
        years = country_data['Year'].values
        mid_values = country_data[mid_col].values
        gap_values = country_data[gap_col].values
        
        mid_slope, _, _, _, _ = linregress(years, mid_values)
        gap_slope, _, _, _, _ = linregress(years, gap_values)
        
        stats_list.append({
            'Code': code,
            'Country': country_name,
            f'{mid_col}_mean': mid_mean,
            f'{mid_col}_slope': mid_slope,
            f'{gap_col}_mean': gap_mean,
            f'{gap_col}_slope': gap_slope
        })
    
    return pd.DataFrame(stats_list)

# Dictionary to store statistics for each indicator
indicator_stats = {}

# Process each indicator
indicators = {
    'Alcohol': (alcohol_temporal, 'Mid_Alcohol', 'Gap_Alcohol'),
    'Cardiovascular': (cardiovascular_temporal, 'Mid_Cardiovascular', 'Gap_Cardiovascular'),
    'ChronicRespiratory': (chronic_respiratory_temporal, 'Mid_ChronicRespiratory', 'Gap_ChronicRespiratory'),
    'Suicide': (self_harm_temporal, 'Mid_Suicide', 'Gap_Suicide'),
    'Homicide': (interpersonal_violence_temporal, 'Mid_Homicide', 'Gap_Homicide'),
    'RoadTraffic': (road_injuries_temporal, 'Mid_RoadTraffic', 'Gap_RoadTraffic'),
    'LiverDisease': (liver_disease_temporal, 'Mid_LiverDisease', 'Gap_LiverDisease'),
    'Neoplasms': (neoplasms_temporal, 'Mid_Neoplasms', 'Gap_Neoplasms'),
    'UnintentionalInjury': (unintentional_injuries_temporal, 'Mid_UnintentionalInjury', 'Gap_UnintentionalInjury'),
    'Diabetes': (diabetes_temporal, 'Mid_Diabetes', 'Gap_Diabetes')
}

for indicator_name, (df_temporal, mid_col, gap_col) in indicators.items():
    stats_df = compute_indicator_stats(df_temporal, mid_col, gap_col)
    indicator_stats[indicator_name] = {
        'stats': stats_df,
        'mid_col': mid_col,
        'gap_col': gap_col
    }
```

### Create Summary Tables

```python
# Create summary tables for Mid (rates)
mid_summary = []

for indicator_name, data in indicator_stats.items():
    stats_df = data['stats']
    mid_col = data['mid_col']
    
    mid_mean_col = f'{mid_col}_mean'
    mid_slope_col = f'{mid_col}_slope'
    
    # Find countries with extremes
    highest_mean_idx = stats_df[mid_mean_col].idxmax()
    lowest_mean_idx = stats_df[mid_mean_col].idxmin()
    highest_slope_idx = stats_df[mid_slope_col].idxmax()
    lowest_slope_idx = stats_df[mid_slope_col].idxmin()
    
    mid_summary.append({
        'Indicator': indicator_name,
        'Highest Mean Country': stats_df.loc[highest_mean_idx, 'Country'],
        'Highest Mean Value': stats_df.loc[highest_mean_idx, mid_mean_col],
        'Lowest Mean Country': stats_df.loc[lowest_mean_idx, 'Country'],
        'Lowest Mean Value': stats_df.loc[lowest_mean_idx, mid_mean_col],
        'Highest Slope Country': stats_df.loc[highest_slope_idx, 'Country'],
        'Highest Slope Value': stats_df.loc[highest_slope_idx, mid_slope_col],
        'Lowest Slope Country': stats_df.loc[lowest_slope_idx, 'Country'],
        'Lowest Slope Value': stats_df.loc[lowest_slope_idx, mid_slope_col]
    })

mid_summary_df = pd.DataFrame(mid_summary)
mid_summary_df
```

```python
# Create summary table for Gap (gaps)
gap_summary = []

for indicator_name, data in indicator_stats.items():
    stats_df = data['stats']
    gap_col = data['gap_col']
    
    gap_mean_col = f'{gap_col}_mean'
    gap_slope_col = f'{gap_col}_slope'
    
    # Find countries with extremes
    highest_mean_idx = stats_df[gap_mean_col].idxmax()
    lowest_mean_idx = stats_df[gap_mean_col].idxmin()
    highest_slope_idx = stats_df[gap_slope_col].idxmax()
    lowest_slope_idx = stats_df[gap_slope_col].idxmin()
    
    gap_summary.append({
        'Indicator': indicator_name,
        'Highest Mean Country': stats_df.loc[highest_mean_idx, 'Country'],
        'Highest Mean Value': stats_df.loc[highest_mean_idx, gap_mean_col],
        'Lowest Mean Country': stats_df.loc[lowest_mean_idx, 'Country'],
        'Lowest Mean Value': stats_df.loc[lowest_mean_idx, gap_mean_col],
        'Highest Slope Country': stats_df.loc[highest_slope_idx, 'Country'],
        'Highest Slope Value': stats_df.loc[highest_slope_idx, gap_slope_col],
        'Lowest Slope Country': stats_df.loc[lowest_slope_idx, 'Country'],
        'Lowest Slope Value': stats_df.loc[lowest_slope_idx, gap_slope_col]
    })

gap_summary_df = pd.DataFrame(gap_summary)
gap_summary_df
```

```python
# Export summary tables to HTML
write_html_table(mid_summary_df, 'tables/indicator_rates_summary_timeseries.html')
write_html_table(gap_summary_df, 'tables/indicator_gaps_summary_timeseries.html')
```

## Target Variable Time Series

### HALE Gap Time Series

```python
def plot_gap_timeseries(df, gap_col, countries=None, oecd_avg=True, title=None, ylabel=None):
    """
    Plot gap time series for selected countries and OECD average.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with Year, Code, Country, and gap_col columns
    gap_col : str
        Name of the gap column to plot
    countries : list, optional
        List of country codes to plot. If None, plots all OECD countries.
    oecd_avg : bool
        Whether to include OECD average line
    title : str, optional
        Plot title
    ylabel : str, optional
        Y-axis label
    """
    # Filter to OECD countries
    # get_oecd expects Code as index, so set it temporarily
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Filter to countries of interest
    if countries is None:
        countries = df_oecd['Code'].unique()
    
    df_plot = df_oecd[df_oecd['Code'].isin(countries)].copy()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot individual countries
    for code in countries:
        country_data = df_plot[df_plot['Code'] == code]
        if not country_data.empty:
            country_name = country_data['Country'].iloc[0]
            ax.plot(country_data['Year'], country_data[gap_col], 
                   alpha=0.8, linewidth=1, label=country_name)
    
    # Plot OECD average
    if oecd_avg:
        oecd_avg_by_year = df_plot.groupby('Year')[gap_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color='black', linewidth=2, linestyle='--', label='OECD Average')
    
    # Formatting
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel or gap_col)
    ax.set_title(title or f'{gap_col} Over Time')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.tight_layout()
    return fig, ax

def plot_rate_timeseries(df, rate_col, countries=None, oecd_avg=True, title=None, ylabel=None):
    """
    Plot rate time series for selected countries and OECD average.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with Year, Code, Country, and rate_col columns
    rate_col : str
        Name of the rate column to plot
    countries : list, optional
        List of country codes to plot. If None, plots all OECD countries.
    oecd_avg : bool
        Whether to include OECD average line
    title : str, optional
        Plot title
    ylabel : str, optional
        Y-axis label
    """
    # Filter to OECD countries
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Filter to countries of interest
    if countries is None:
        countries = df_oecd['Code'].unique()
    
    df_plot = df_oecd[df_oecd['Code'].isin(countries)].copy()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot individual countries
    for code in countries:
        country_data = df_plot[df_plot['Code'] == code]
        if not country_data.empty:
            country_name = country_data['Country'].iloc[0]
            ax.plot(country_data['Year'], country_data[rate_col], 
                   alpha=0.8, linewidth=1, label=country_name)
    
    # Plot OECD average
    if oecd_avg:
        oecd_avg_by_year = df_plot.groupby('Year')[rate_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color='black', linewidth=2, linestyle='--', label='OECD Average')
    
    # Formatting
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel or rate_col)
    ax.set_title(title or f'{rate_col} Over Time')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.tight_layout()
    return fig, ax

# Plot HALE gap time series for all OECD countries
fig, ax = plot_gap_timeseries(
    hale_temporal.reset_index(),
    'HALE_gap',
    title='HALE Gender Gap Over Time (Female - Male)',
    ylabel='HALE Gap (years)'
)
plt.savefig('figs/hale_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Life Expectancy Gap Time Series

```python
# Plot Life Expectancy gap time series for all OECD countries
fig, ax = plot_gap_timeseries(
    le_temporal.reset_index(),
    'LE_gap',
    title='Life Expectancy Gender Gap Over Time (Female - Male)',
    ylabel='Life Expectancy Gap (years)'
)
plt.savefig('figs/le_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

### HALE Gap: Selected Countries

```python
# Plot HALE gap for selected countries of interest
selected_countries = ['USA', 'GBR', 'JPN', 'DEU', 'FRA', 'CAN', 'AUS', 'KOR']
fig, ax = plot_gap_timeseries(
    hale_temporal.reset_index(),
    'HALE_gap',
    countries=selected_countries,
    title='HALE Gender Gap Over Time: Selected Countries',
    ylabel='HALE Gap (years)'
)
plt.savefig('figs/hale_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Life Expectancy Gap: Selected Countries

```python
# Plot Life Expectancy gap for selected countries
fig, ax = plot_gap_timeseries(
    le_temporal.reset_index(),
    'LE_gap',
    countries=selected_countries,
    title='Life Expectancy Gender Gap Over Time: Selected Countries',
    ylabel='Life Expectancy Gap (years)'
)
plt.savefig('figs/le_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### HALE Time Series (Overall Rates)

```python
# Plot HALE (midpoint) time series for all OECD countries
fig, ax = plot_rate_timeseries(
    hale_temporal.reset_index(),
    'Mid_HALE_Years',
    title='HALE Over Time (Average of Male and Female)',
    ylabel='HALE (years)'
)
plt.savefig('figs/hale_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
# Plot HALE for selected countries
fig, ax = plot_rate_timeseries(
    hale_temporal.reset_index(),
    'Mid_HALE_Years',
    countries=selected_countries,
    title='HALE Over Time: Selected Countries',
    ylabel='HALE (years)'
)
plt.savefig('figs/hale_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Life Expectancy Time Series (Overall Rates)

```python
# Plot Life Expectancy (midpoint) time series for all OECD countries
fig, ax = plot_rate_timeseries(
    le_temporal.reset_index(),
    'Mid_LifeExpectancy_Years',
    title='Life Expectancy Over Time (Average of Male and Female)',
    ylabel='Life Expectancy (years)'
)
plt.savefig('figs/le_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
# Plot Life Expectancy for selected countries
fig, ax = plot_rate_timeseries(
    le_temporal.reset_index(),
    'Mid_LifeExpectancy_Years',
    countries=selected_countries,
    title='Life Expectancy Over Time: Selected Countries',
    ylabel='Life Expectancy (years)'
)
plt.savefig('figs/le_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Gap Changes Summary Table

```python
def compute_gap_changes(df, gap_col):
    """
    Compute gap changes from min_year to max_year for each country.
    
    Uses global min_year and max_year variables.
    
    Returns DataFrame with Country, gap_start, gap_end, change, and pct_change.
    """
    # get_oecd expects Code as index, so set it temporarily
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Get data for start and end years
    start_data = df_oecd[df_oecd['Year'] == min_year][['Code', 'Country', gap_col]].copy()
    end_data = df_oecd[df_oecd['Year'] == max_year][['Code', 'Country', gap_col]].copy()
    
    # Merge
    changes = start_data.merge(end_data, on=['Code', 'Country'], suffixes=('_start', '_end'))
    changes['change'] = changes[f'{gap_col}_end'] - changes[f'{gap_col}_start']
    changes['pct_change'] = (changes['change'] / changes[f'{gap_col}_start'].abs()) * 100
    
    # Sort by end year gap value (descending)
    changes = changes.sort_values(f'{gap_col}_end', ascending=False)
    
    return changes

# Compute HALE gap changes
hale_changes = compute_gap_changes(hale_temporal.reset_index(), 'HALE_gap')
hale_changes[['Country', 'HALE_gap_start', 'HALE_gap_end', 'change']]
```

```python
# Compute Life Expectancy gap changes
le_changes = compute_gap_changes(le_temporal.reset_index(), 'LE_gap')
le_changes[['Country', 'LE_gap_start', 'LE_gap_end', 'change']]
```

```python
# Export gap changes to HTML table
hale_changes_display = hale_changes[['Country', 'HALE_gap_start', 'HALE_gap_end', 'change']].copy()
hale_changes_display.columns = [f'Country', f'Gap {min_year}', f'Gap {max_year}', 'Change']
hale_changes_display = hale_changes_display.round(2)
write_html_table(hale_changes_display, f'tables/hale_gap_changes_{min_year}_{max_year}.html')

le_changes_display = le_changes[['Country', 'LE_gap_start', 'LE_gap_end', 'change']].copy()
le_changes_display.columns = [f'Country', f'Gap {min_year}', f'Gap {max_year}', 'Change']
le_changes_display = le_changes_display.round(2)
write_html_table(le_changes_display, f'tables/le_gap_changes_{min_year}_{max_year}.html')
```

### HALE and Life Expectancy Value Changes

```python
def compute_value_changes(df, value_col):
    """
    Compute value changes from min_year to max_year for each country.
    
    Uses global min_year and max_year variables.
    
    Returns DataFrame with Country, value_start, value_end, change, and pct_change.
    """
    # get_oecd expects Code as index, so set it temporarily
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Get data for start and end years
    start_data = df_oecd[df_oecd['Year'] == min_year][['Code', 'Country', value_col]].copy()
    end_data = df_oecd[df_oecd['Year'] == max_year][['Code', 'Country', value_col]].copy()
    
    # Merge
    changes = start_data.merge(end_data, on=['Code', 'Country'], suffixes=('_start', '_end'))
    changes['change'] = changes[f'{value_col}_end'] - changes[f'{value_col}_start']
    changes['pct_change'] = (changes['change'] / changes[f'{value_col}_start']) * 100
    
    # Sort by end year value (descending)
    changes = changes.sort_values(f'{value_col}_end', ascending=False)
    
    return changes

# Compute HALE value changes
hale_value_changes = compute_value_changes(hale_temporal.reset_index(), 'Mid_HALE_Years')
hale_value_changes[['Country', 'Mid_HALE_Years_start', 'Mid_HALE_Years_end', 'change']]
```

```python
# Compute Life Expectancy value changes
le_value_changes = compute_value_changes(le_temporal.reset_index(), 'Mid_LifeExpectancy_Years')
le_value_changes[['Country', 'Mid_LifeExpectancy_Years_start', 'Mid_LifeExpectancy_Years_end', 'change']]
```

```python
# Export value changes to HTML table
hale_value_changes_display = hale_value_changes[['Country', 'Mid_HALE_Years_start', 'Mid_HALE_Years_end', 'change']].copy()
hale_value_changes_display.columns = [f'Country', f'HALE {min_year}', f'HALE {max_year}', 'Change']
hale_value_changes_display = hale_value_changes_display.round(2)
write_html_table(hale_value_changes_display, f'tables/hale_value_changes_{min_year}_{max_year}.html')

le_value_changes_display = le_value_changes[['Country', 'Mid_LifeExpectancy_Years_start', 'Mid_LifeExpectancy_Years_end', 'change']].copy()
le_value_changes_display.columns = [f'Country', f'Life Expectancy {min_year}', f'Life Expectancy {max_year}', 'Change']
le_value_changes_display = le_value_changes_display.round(2)
write_html_table(le_value_changes_display, f'tables/le_value_changes_{min_year}_{max_year}.html')
```

## Target Variable Statistics: HALE and Life Expectancy

### Compute Statistics for HALE and LE

```python
def compute_target_stats(df_temporal, value_col):
    """
    Compute statistics for each country: mean and slope (trend) over time.
    
    Parameters
    ----------
    df_temporal : pandas.DataFrame
        DataFrame with Year, Code, Country, and value column
    value_col : str
        Name of the value column to analyze
        
    Returns
    -------
    stats_df : pandas.DataFrame
        DataFrame with Code, Country, mean, and slope columns
    """
    # Filter to OECD countries
    df = df_temporal.reset_index() if 'Code' in df_temporal.index.names else df_temporal
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    stats_list = []
    
    for code in df_oecd['Code'].unique():
        country_data = df_oecd[df_oecd['Code'] == code].copy()
        country_data = country_data.sort_values('Year')
        
        if len(country_data) < 2:
            continue  # Need at least 2 years to compute slope
        
        country_name = country_data['Country'].iloc[0]
        
        # Compute mean
        mean_value = country_data[value_col].mean()
        
        # Compute slope using linregress
        years = country_data['Year'].values
        values = country_data[value_col].values
        
        slope, _, _, _, _ = linregress(years, values)
        
        stats_list.append({
            'Code': code,
            'Country': country_name,
            'Mean': mean_value,
            'Slope': slope
        })
    
    return pd.DataFrame(stats_list)

# Compute statistics for HALE
hale_stats = compute_target_stats(hale_temporal.reset_index(), 'Mid_HALE_Years')
hale_stats.head()
```

```python
# Compute statistics for Life Expectancy
le_stats = compute_target_stats(le_temporal.reset_index(), 'Mid_LifeExpectancy_Years')
le_stats.head()
```

```python
# Compute statistics for HALE gap
hale_gap_stats = compute_target_stats(hale_temporal.reset_index(), 'HALE_gap')
hale_gap_stats.head()
```

```python
# Compute statistics for Life Expectancy gap
le_gap_stats = compute_target_stats(le_temporal.reset_index(), 'LE_gap')
le_gap_stats.head()
```

### Create Summary Tables for HALE and LE Values

```python
def create_target_summary(stats_df, target_name):
    """
    Create summary table with highest/lowest mean and slope.
    
    Parameters
    ----------
    stats_df : pandas.DataFrame
        DataFrame with Mean and Slope columns
    target_name : str
        Name of the target variable (e.g., 'HALE', 'Life Expectancy')
        
    Returns
    -------
    summary_dict : dict
        Dictionary with superlative information
    """
    # Find countries with extremes
    highest_mean_idx = stats_df['Mean'].idxmax()
    lowest_mean_idx = stats_df['Mean'].idxmin()
    highest_slope_idx = stats_df['Slope'].idxmax()
    lowest_slope_idx = stats_df['Slope'].idxmin()
    
    return {
        'Target': target_name,
        'Highest Mean Country': stats_df.loc[highest_mean_idx, 'Country'],
        'Highest Mean Value': stats_df.loc[highest_mean_idx, 'Mean'],
        'Lowest Mean Country': stats_df.loc[lowest_mean_idx, 'Country'],
        'Lowest Mean Value': stats_df.loc[lowest_mean_idx, 'Mean'],
        'Highest Slope Country': stats_df.loc[highest_slope_idx, 'Country'],
        'Highest Slope Value': stats_df.loc[highest_slope_idx, 'Slope'],
        'Lowest Slope Country': stats_df.loc[lowest_slope_idx, 'Country'],
        'Lowest Slope Value': stats_df.loc[lowest_slope_idx, 'Slope']
    }

# Create summary for HALE and LE values
target_values_summary = [
    create_target_summary(hale_stats, 'HALE'),
    create_target_summary(le_stats, 'Life Expectancy')
]

target_values_summary_df = pd.DataFrame(target_values_summary)
target_values_summary_df
```

```python
# Export to HTML
write_html_table(target_values_summary_df, 'tables/target_values_summary_timeseries.html')
```

### Create Summary Tables for HALE and LE Gaps

```python
# Create summary for HALE and LE gaps
target_gaps_summary = [
    create_target_summary(hale_gap_stats, 'HALE Gap'),
    create_target_summary(le_gap_stats, 'Life Expectancy Gap')
]

target_gaps_summary_df = pd.DataFrame(target_gaps_summary)
target_gaps_summary_df
```

```python
# Export to HTML
write_html_table(target_gaps_summary_df, 'tables/target_gaps_summary_timeseries.html')
```

## Indicator Time Series

### Alcohol Use Disorders

#### Rates for All Countries

```python
# Plot Alcohol rate (Mid) time series for all OECD countries
fig, ax = plot_rate_timeseries(
    alcohol_temporal.reset_index(),
    'Mid_Alcohol',
    title='Alcohol Use Disorders Death Rate Over Time (Overall Rate)',
    ylabel='Alcohol Death Rate (per 100,000)'
)
plt.savefig('figs/alcohol_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
# Plot Alcohol rate (Mid) for selected countries
fig, ax = plot_rate_timeseries(
    alcohol_temporal.reset_index(),
    'Mid_Alcohol',
    countries=selected_countries,
    title='Alcohol Use Disorders Death Rate Over Time: Selected Countries',
    ylabel='Alcohol Death Rate (per 100,000)'
)
plt.savefig('figs/alcohol_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
# Plot Alcohol gap time series for all OECD countries
fig, ax = plot_gap_timeseries(
    alcohol_temporal.reset_index(),
    'Gap_Alcohol',
    title='Alcohol Use Disorders Gender Gap Over Time (Male - Female)',
    ylabel='Alcohol Death Rate Gap (per 100,000)'
)
plt.savefig('figs/alcohol_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
# Plot Alcohol gap for selected countries
fig, ax = plot_gap_timeseries(
    alcohol_temporal.reset_index(),
    'Gap_Alcohol',
    countries=selected_countries,
    title='Alcohol Use Disorders Gender Gap Over Time: Selected Countries',
    ylabel='Alcohol Death Rate Gap (per 100,000)'
)
plt.savefig('figs/alcohol_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Cardiovascular Disease

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    cardiovascular_temporal.reset_index(),
    'Mid_Cardiovascular',
    title='Cardiovascular Disease Death Rate Over Time (Overall Rate)',
    ylabel='Cardiovascular Death Rate (per 100,000)'
)
plt.savefig('figs/cardiovascular_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    cardiovascular_temporal.reset_index(),
    'Mid_Cardiovascular',
    countries=selected_countries,
    title='Cardiovascular Disease Death Rate Over Time: Selected Countries',
    ylabel='Cardiovascular Death Rate (per 100,000)'
)
plt.savefig('figs/cardiovascular_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    cardiovascular_temporal.reset_index(),
    'Gap_Cardiovascular',
    title='Cardiovascular Disease Gender Gap Over Time (Male - Female)',
    ylabel='Cardiovascular Death Rate Gap (per 100,000)'
)
plt.savefig('figs/cardiovascular_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    cardiovascular_temporal.reset_index(),
    'Gap_Cardiovascular',
    countries=selected_countries,
    title='Cardiovascular Disease Gender Gap Over Time: Selected Countries',
    ylabel='Cardiovascular Death Rate Gap (per 100,000)'
)
plt.savefig('figs/cardiovascular_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Chronic Respiratory Disease

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    chronic_respiratory_temporal.reset_index(),
    'Mid_ChronicRespiratory',
    title='Chronic Respiratory Disease Death Rate Over Time (Overall Rate)',
    ylabel='Chronic Respiratory Death Rate (per 100,000)'
)
plt.savefig('figs/chronic_respiratory_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    chronic_respiratory_temporal.reset_index(),
    'Mid_ChronicRespiratory',
    countries=selected_countries,
    title='Chronic Respiratory Disease Death Rate Over Time: Selected Countries',
    ylabel='Chronic Respiratory Death Rate (per 100,000)'
)
plt.savefig('figs/chronic_respiratory_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    chronic_respiratory_temporal.reset_index(),
    'Gap_ChronicRespiratory',
    title='Chronic Respiratory Disease Gender Gap Over Time (Male - Female)',
    ylabel='Chronic Respiratory Death Rate Gap (per 100,000)'
)
plt.savefig('figs/chronic_respiratory_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    chronic_respiratory_temporal.reset_index(),
    'Gap_ChronicRespiratory',
    countries=selected_countries,
    title='Chronic Respiratory Disease Gender Gap Over Time: Selected Countries',
    ylabel='Chronic Respiratory Death Rate Gap (per 100,000)'
)
plt.savefig('figs/chronic_respiratory_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Self-Harm/Suicide

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    self_harm_temporal.reset_index(),
    'Mid_Suicide',
    title='Self-Harm (Suicide) Death Rate Over Time (Overall Rate)',
    ylabel='Suicide Death Rate (per 100,000)'
)
plt.savefig('figs/suicide_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    self_harm_temporal.reset_index(),
    'Mid_Suicide',
    countries=selected_countries,
    title='Self-Harm (Suicide) Death Rate Over Time: Selected Countries',
    ylabel='Suicide Death Rate (per 100,000)'
)
plt.savefig('figs/suicide_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    self_harm_temporal.reset_index(),
    'Gap_Suicide',
    title='Self-Harm (Suicide) Gender Gap Over Time (Male - Female)',
    ylabel='Suicide Death Rate Gap (per 100,000)'
)
plt.savefig('figs/suicide_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    self_harm_temporal.reset_index(),
    'Gap_Suicide',
    countries=selected_countries,
    title='Self-Harm (Suicide) Gender Gap Over Time: Selected Countries',
    ylabel='Suicide Death Rate Gap (per 100,000)'
)
plt.savefig('figs/suicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Interpersonal Violence/Homicide

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    interpersonal_violence_temporal.reset_index(),
    'Mid_Homicide',
    title='Interpersonal Violence (Homicide) Death Rate Over Time (Overall Rate)',
    ylabel='Homicide Death Rate (per 100,000)'
)
plt.savefig('figs/homicide_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    interpersonal_violence_temporal.reset_index(),
    'Mid_Homicide',
    countries=selected_countries,
    title='Interpersonal Violence (Homicide) Death Rate Over Time: Selected Countries',
    ylabel='Homicide Death Rate (per 100,000)'
)
plt.savefig('figs/homicide_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    interpersonal_violence_temporal.reset_index(),
    'Gap_Homicide',
    title='Interpersonal Violence (Homicide) Gender Gap Over Time (Male - Female)',
    ylabel='Homicide Death Rate Gap (per 100,000)'
)
plt.savefig('figs/homicide_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    interpersonal_violence_temporal.reset_index(),
    'Gap_Homicide',
    countries=selected_countries,
    title='Interpersonal Violence (Homicide) Gender Gap Over Time: Selected Countries',
    ylabel='Homicide Death Rate Gap (per 100,000)'
)
plt.savefig('figs/homicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Road Injuries

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    road_injuries_temporal.reset_index(),
    'Mid_RoadTraffic',
    title='Road Injuries Death Rate Over Time (Overall Rate)',
    ylabel='Road Traffic Death Rate (per 100,000)'
)
plt.savefig('figs/road_traffic_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    road_injuries_temporal.reset_index(),
    'Mid_RoadTraffic',
    countries=selected_countries,
    title='Road Injuries Death Rate Over Time: Selected Countries',
    ylabel='Road Traffic Death Rate (per 100,000)'
)
plt.savefig('figs/road_traffic_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    road_injuries_temporal.reset_index(),
    'Gap_RoadTraffic',
    title='Road Injuries Gender Gap Over Time (Male - Female)',
    ylabel='Road Traffic Death Rate Gap (per 100,000)'
)
plt.savefig('figs/road_traffic_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    road_injuries_temporal.reset_index(),
    'Gap_RoadTraffic',
    countries=selected_countries,
    title='Road Injuries Gender Gap Over Time: Selected Countries',
    ylabel='Road Traffic Death Rate Gap (per 100,000)'
)
plt.savefig('figs/road_traffic_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Liver Disease

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    liver_disease_temporal.reset_index(),
    'Mid_LiverDisease',
    title='Liver Disease Death Rate Over Time (Overall Rate)',
    ylabel='Liver Disease Death Rate (per 100,000)'
)
plt.savefig('figs/liver_disease_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    liver_disease_temporal.reset_index(),
    'Mid_LiverDisease',
    countries=selected_countries,
    title='Liver Disease Death Rate Over Time: Selected Countries',
    ylabel='Liver Disease Death Rate (per 100,000)'
)
plt.savefig('figs/liver_disease_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    liver_disease_temporal.reset_index(),
    'Gap_LiverDisease',
    title='Liver Disease Gender Gap Over Time (Male - Female)',
    ylabel='Liver Disease Death Rate Gap (per 100,000)'
)
plt.savefig('figs/liver_disease_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    liver_disease_temporal.reset_index(),
    'Gap_LiverDisease',
    countries=selected_countries,
    title='Liver Disease Gender Gap Over Time: Selected Countries',
    ylabel='Liver Disease Death Rate Gap (per 100,000)'
)
plt.savefig('figs/liver_disease_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Neoplasms

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    neoplasms_temporal.reset_index(),
    'Mid_Neoplasms',
    title='Neoplasms (Cancer) Death Rate Over Time (Overall Rate)',
    ylabel='Neoplasms Death Rate (per 100,000)'
)
plt.savefig('figs/neoplasms_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    neoplasms_temporal.reset_index(),
    'Mid_Neoplasms',
    countries=selected_countries,
    title='Neoplasms (Cancer) Death Rate Over Time: Selected Countries',
    ylabel='Neoplasms Death Rate (per 100,000)'
)
plt.savefig('figs/neoplasms_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    neoplasms_temporal.reset_index(),
    'Gap_Neoplasms',
    title='Neoplasms (Cancer) Gender Gap Over Time (Male - Female)',
    ylabel='Neoplasms Death Rate Gap (per 100,000)'
)
plt.savefig('figs/neoplasms_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    neoplasms_temporal.reset_index(),
    'Gap_Neoplasms',
    countries=selected_countries,
    title='Neoplasms (Cancer) Gender Gap Over Time: Selected Countries',
    ylabel='Neoplasms Death Rate Gap (per 100,000)'
)
plt.savefig('figs/neoplasms_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Unintentional Injuries

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    unintentional_injuries_temporal.reset_index(),
    'Mid_UnintentionalInjury',
    title='Unintentional Injuries Death Rate Over Time (Overall Rate)',
    ylabel='Unintentional Injuries Death Rate (per 100,000)'
)
plt.savefig('figs/unintentional_injury_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    unintentional_injuries_temporal.reset_index(),
    'Mid_UnintentionalInjury',
    countries=selected_countries,
    title='Unintentional Injuries Death Rate Over Time: Selected Countries',
    ylabel='Unintentional Injuries Death Rate (per 100,000)'
)
plt.savefig('figs/unintentional_injury_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    unintentional_injuries_temporal.reset_index(),
    'Gap_UnintentionalInjury',
    title='Unintentional Injuries Gender Gap Over Time (Male - Female)',
    ylabel='Unintentional Injuries Death Rate Gap (per 100,000)'
)
plt.savefig('figs/unintentional_injury_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    unintentional_injuries_temporal.reset_index(),
    'Gap_UnintentionalInjury',
    countries=selected_countries,
    title='Unintentional Injuries Gender Gap Over Time: Selected Countries',
    ylabel='Unintentional Injuries Death Rate Gap (per 100,000)'
)
plt.savefig('figs/unintentional_injury_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Diabetes Type 2

#### Rates for All Countries

```python
fig, ax = plot_rate_timeseries(
    diabetes_temporal.reset_index(),
    'Mid_Diabetes',
    title='Diabetes Type 2 Death Rate Over Time (Overall Rate)',
    ylabel='Diabetes Death Rate (per 100,000)'
)
plt.savefig('figs/diabetes_rate_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Rates for Selected Countries

```python
fig, ax = plot_rate_timeseries(
    diabetes_temporal.reset_index(),
    'Mid_Diabetes',
    countries=selected_countries,
    title='Diabetes Type 2 Death Rate Over Time: Selected Countries',
    ylabel='Diabetes Death Rate (per 100,000)'
)
plt.savefig('figs/diabetes_rate_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for All Countries

```python
fig, ax = plot_gap_timeseries(
    diabetes_temporal.reset_index(),
    'Gap_Diabetes',
    title='Diabetes Type 2 Gender Gap Over Time (Male - Female)',
    ylabel='Diabetes Death Rate Gap (per 100,000)'
)
plt.savefig('figs/diabetes_gap_timeseries_all.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Gaps for Selected Countries

```python
fig, ax = plot_gap_timeseries(
    diabetes_temporal.reset_index(),
    'Gap_Diabetes',
    countries=selected_countries,
    title='Diabetes Type 2 Gender Gap Over Time: Selected Countries',
    ylabel='Diabetes Death Rate Gap (per 100,000)'
)
plt.savefig('figs/diabetes_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

