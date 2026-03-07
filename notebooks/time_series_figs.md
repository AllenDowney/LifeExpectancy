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

from empiricaldist import Cdf
from scipy.stats import linregress

from utils import (
    decorate,
    configure_plot_style, get_oecd, compute_gender_gap,
    oecd_codes, code_to_who_country, load_ihme_indicator,
    load_ihme_indicator_temporal,
    column_name_mapping
)
from fig_utils import plot_gap_timeseries
# AIBM style: each figure uses title (left-aligned), subtitle (OECD countries, years), subtext (source), logo

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

def extremes_overall(df, gap_col):
    """Return rows with the single largest and single smallest gap in the dataset."""
    idx_max = df[gap_col].idxmax()
    idx_min = df[gap_col].idxmin()
    return pd.concat([df.loc[[idx_min]], df.loc[[idx_max]]], ignore_index=True)

def extremes_in_year(df, gap_col, year):
    """Return full sorted table for a given year (smallest gap first)."""
    return df.query(f'Year == {year}').sort_values(by=gap_col).reset_index(drop=True)

def slopes_by_country(df, gap_col):
    """Compute linear trend (slope per year) of gap_col by country. Returns DataFrame with Code, Slope."""
    from scipy.stats import linregress
    rows = []
    for code, group in df.groupby('Code'):
        r = linregress(group['Year'], group[gap_col])
        rows.append((code, r.slope))
    return pd.DataFrame(rows, columns=['Code', 'Slope'])

def summarize_trends(df, gap_col, year_ref=2023, slope_decade_scale=10):
    """Print and return OECD average by year, slope (per decade), and extremes for year_ref."""
    from scipy.stats import linregress
    df_oecd = get_oecd(df.set_index('Code')).reset_index()
    avg_by_year = df_oecd.groupby('Year')[gap_col].mean()
    r = linregress(avg_by_year.index, avg_by_year.values)
    slope_per_decade = r.slope * slope_decade_scale
    print(f"OECD average: {avg_by_year.iloc[0]:.2f} ({avg_by_year.index[0]:.0f}) → {avg_by_year.iloc[-1]:.2f} ({avg_by_year.index[-1]:.0f})")
    print(f"OECD slope: {r.slope:.4f} per year ({slope_per_decade:.2f} per decade)")
    in_year = df.query(f'Year == {year_ref}')
    print(f"Extremes in {year_ref}: min {in_year[gap_col].min():.2f} ({in_year.loc[in_year[gap_col].idxmin(), 'Code']}), max {in_year[gap_col].max():.2f} ({in_year.loc[in_year[gap_col].idxmax(), 'Code']})")
    return avg_by_year

def plot_usa_rates_and_trends(df, gap_col, ylabel='Rate per 100,000', code='USA'):
    """Plot male and female rates over time for one country and print linear trend slopes."""
    base = gap_col.replace('Gap_', '')
    male_col = f'{base}_Male'
    female_col = f'{base}_Female'
    group = df.query(f'Code == "{code}"').copy()
    if male_col not in group.columns or female_col not in group.columns:
        raise ValueError(f"Expected columns {male_col}, {female_col}; got {list(group.columns)}")
    plt.figure()
    plt.plot(group['Year'], group[male_col], label='Male')
    plt.plot(group['Year'], group[female_col], label='Female')
    plt.legend()
    decorate(ylabel=ylabel)
    plt.show()
    r_m = linregress(group['Year'], group[male_col])
    r_f = linregress(group['Year'], group[female_col])
    print(f'Male:   slope = {r_m.slope:.4f} per year')
    print(f'Female: slope = {r_f.slope:.4f} per year')
    return group

def compute_oecd_slopes(df, gap_col):
    """Compute OECD-average male, female, and gap slopes (per year). Returns (male_slope, female_slope, gap_slope)."""
    base = gap_col.replace('Gap_', '')
    male_col = f'{base}_Male'
    female_col = f'{base}_Female'
    df_oecd = get_oecd(df.set_index('Code')).reset_index()
    avg_male = df_oecd.groupby('Year')[male_col].mean()
    avg_female = df_oecd.groupby('Year')[female_col].mean()
    avg_gap = df_oecd.groupby('Year')[gap_col].mean()
    r_m = linregress(avg_male.index, avg_male.values)
    r_f = linregress(avg_female.index, avg_female.values)
    r_g = linregress(avg_gap.index, avg_gap.values)
    return r_m.slope, r_f.slope, r_g.slope

def get_extremes_for_cause(df, gap_col, slopes_df, year_ref=2023):
    """Get 6 extreme countries: lowest/highest gap ever, lowest/highest gap in year_ref, lowest/highest slope."""
    idx_min = df[gap_col].idxmin()
    idx_max = df[gap_col].idxmax()
    row_min = df.loc[idx_min]
    row_max = df.loc[idx_max]
    in_year = df[df['Year'] == year_ref]
    if in_year.empty:
        return None
    idx_min_yr = in_year[gap_col].idxmin()
    idx_max_yr = in_year[gap_col].idxmax()
    row_min_yr = df.loc[idx_min_yr]
    row_max_yr = df.loc[idx_max_yr]
    slope_min = slopes_df.loc[slopes_df['Slope'].idxmin()]
    slope_max = slopes_df.loc[slopes_df['Slope'].idxmax()]
    return {
        'lowest_gap_ever_code': row_min['Code'],
        'lowest_gap_ever_val': row_min[gap_col],
        'lowest_gap_ever_year': int(row_min['Year']),
        'highest_gap_ever_code': row_max['Code'],
        'highest_gap_ever_val': row_max[gap_col],
        'highest_gap_ever_year': int(row_max['Year']),
        'lowest_gap_2023_code': row_min_yr['Code'],
        'lowest_gap_2023_val': row_min_yr[gap_col],
        'highest_gap_2023_code': row_max_yr['Code'],
        'highest_gap_2023_val': row_max_yr[gap_col],
        'lowest_slope_code': slope_min['Code'],
        'lowest_slope_val': slope_min['Slope'],
        'highest_slope_code': slope_max['Code'],
        'highest_slope_val': slope_max['Slope'],
    }

# Tables to collect slopes and extremes for each cause (populated as notebook executes)
slopes_table = []
extremes_table = []
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
```

### Life Expectancy gap: extremes and trends

```python
# Single largest and smallest gap in the full series
extremes_overall(le_temporal, 'LE_gap')
```

```python
# 2023: all countries sorted by LE gap (smallest first)
extremes_in_year(le_temporal, 'LE_gap', 2023)
```

```python
# OECD average and extremes in 2023
summarize_trends(le_temporal, 'LE_gap', year_ref=2023)
```

```python
# Slopes by country (negative = gap closing): fastest closing
slopes_le = slopes_by_country(le_temporal, 'LE_gap')
slopes_le.sort_values(by='Slope').head(10)
```

```python
# Slopes: slowest closing / widening
slopes_le.sort_values(by='Slope').tail(10)
```

```python
ext_le = get_extremes_for_cause(le_temporal, 'LE_gap', slopes_le)
extremes_table.append({'Cause': 'Life Expectancy', **ext_le})
```

## Plot Selected Countries

```python
# Selected countries to highlight
selected_countries = ['USA', 'GBR', 'NOR', 'FRA', 'CAN', 'LTU', 'JPN']

# Plot Life Expectancy gap for selected countries
fig, ax = plot_gap_timeseries(
    le_temporal.reset_index(),
    'LE_gap',
    selected_countries=selected_countries,
    label_lines=True,
    title='Life Expectancy Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Life Expectancy Gap (years)',
    subtext='Source: Our World in Data (OWID) – Combines Human Mortality Database (2025) and UN World Population Prospects (2024).',
    logo=True
)
plt.savefig('figs/le_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```



## Load Alcohol Death Rate Data

```python
# Load IHME Alcohol Use Disorders data
alcohol_temporal = load_ihme_indicator_temporal(
    'ihme_alcohol_use_disorders_deaths',
    'AlcoholUseDisordersDeathRate',
    'IHME_ALCOHOL_USE_DISORDERS',
    'Alcohol use disorders, death rate per 100,000'
)

print(f"Alcohol temporal data: {alcohol_temporal.shape}")
print(f"Years: {alcohol_temporal['Year'].min():.0f} - {alcohol_temporal['Year'].max():.0f}")
print(f"Countries: {alcohol_temporal['Code'].nunique()}")
alcohol_temporal.query('Year == 2023').sort_values(by='Gap_Alcohol')
```

### Alcohol gap: extremes and trends

```python
extremes_overall(alcohol_temporal, 'Gap_Alcohol')
```

```python
extremes_in_year(alcohol_temporal, 'Gap_Alcohol', 2023)
```

```python
summarize_trends(alcohol_temporal, 'Gap_Alcohol', year_ref=2023)
```

```python
slopes_alcohol = slopes_by_country(alcohol_temporal, 'Gap_Alcohol')
slopes_alcohol.sort_values(by='Slope').head(10)
```

```python
slopes_alcohol.sort_values(by='Slope').tail(10)
```

```python
ext_alcohol = get_extremes_for_cause(alcohol_temporal, 'Gap_Alcohol', slopes_alcohol)
extremes_table.append({'Cause': 'Alcohol', **ext_alcohol})
```

## Plot Alcohol Gender Gap

```python
# USA + extremes: low ever COL, high ever EST, low 2023 COL, high 2023 EST, low slope EST, high slope SVN
selected_countries = ['USA', 'COL', 'EST', 'SVN']

fig, ax = plot_gap_timeseries(
    alcohol_temporal.reset_index(),
    'Gap_Alcohol',
    selected_countries=selected_countries,
    label_lines=True,
    title='Alcohol Use Disorders, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Alcohol Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/alcohol_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female alcohol death rates over time

```python
plot_usa_rates_and_trends(alcohol_temporal, 'Gap_Alcohol', ylabel='Alcohol death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(alcohol_temporal, 'Gap_Alcohol')
slopes_table.append({'Cause': 'Alcohol', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
fig, ax = plot_gap_timeseries(
    road_injuries_temporal.reset_index(),
    'Gap_RoadTraffic',
    selected_countries=selected_countries,
    label_lines=True,
    title='Road Traffic, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Road Traffic Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/road_traffic_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Road Traffic gap: extremes and trends

```python
extremes_overall(road_injuries_temporal, 'Gap_RoadTraffic')
```

```python
extremes_in_year(road_injuries_temporal, 'Gap_RoadTraffic', 2023)
```

```python
summarize_trends(road_injuries_temporal, 'Gap_RoadTraffic', year_ref=2023)
```

```python
slopes_rt = slopes_by_country(road_injuries_temporal, 'Gap_RoadTraffic')
slopes_rt.sort_values(by='Slope').head(10)
```

```python
slopes_rt.sort_values(by='Slope').tail(10)
```

```python
ext_rt = get_extremes_for_cause(road_injuries_temporal, 'Gap_RoadTraffic', slopes_rt)
extremes_table.append({'Cause': 'Road Traffic', **ext_rt})
```

### USA: male and female road traffic death rates over time

```python
plot_usa_rates_and_trends(road_injuries_temporal, 'Gap_RoadTraffic', ylabel='Road traffic death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(road_injuries_temporal, 'Gap_RoadTraffic')
slopes_table.append({'Cause': 'Road Traffic', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Unintentional Injury Death Rate Data

```python
# Load IHME Unintentional Injuries data
unintentional_temporal = load_ihme_indicator_temporal(
    'ihme_unintentional_injuries_deaths',
    'UnintentionalInjuriesDeathRate',
    'IHME_UNINTENTIONAL_INJURIES',
    'Unintentional injuries, death rate per 100,000'
)

print(f"Unintentional Injury temporal data: {unintentional_temporal.shape}")
print(f"Years: {unintentional_temporal['Year'].min():.0f} - {unintentional_temporal['Year'].max():.0f}")
print(f"Countries: {unintentional_temporal['Code'].nunique()}")
unintentional_temporal.query('Year == 2023').sort_values(by='Gap_UnintentionalInjury')
```

### Unintentional Injury gap: extremes and trends

```python
extremes_overall(unintentional_temporal, 'Gap_UnintentionalInjury')
```

```python
extremes_in_year(unintentional_temporal, 'Gap_UnintentionalInjury', 2023)
```

```python
summarize_trends(unintentional_temporal, 'Gap_UnintentionalInjury', year_ref=2023)
```

```python
slopes_unintentional = slopes_by_country(unintentional_temporal, 'Gap_UnintentionalInjury')
slopes_unintentional.sort_values(by='Slope').head(10)
```

```python
slopes_unintentional.sort_values(by='Slope').tail(10)
```

```python
ext_unintentional = get_extremes_for_cause(unintentional_temporal, 'Gap_UnintentionalInjury', slopes_unintentional)
extremes_table.append({'Cause': 'Unintentional Injury', **ext_unintentional})
```

## Plot Unintentional Injury Gender Gap

```python
# USA + extremes: low ever NLD, high ever LTU, low 2023 NLD, high 2023 LTU, low slope EST, high slope ITA
selected_countries = ['USA', 'EST', 'ITA', 'LTU', 'NLD']

fig, ax = plot_gap_timeseries(
    unintentional_temporal.reset_index(),
    'Gap_UnintentionalInjury',
    selected_countries=selected_countries,
    label_lines=True,
    title='Unintentional Injury, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Unintentional Injury Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/unintentional_injury_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female unintentional injury rates over time

```python
plot_usa_rates_and_trends(unintentional_temporal, 'Gap_UnintentionalInjury', ylabel='Unintentional injury death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(unintentional_temporal, 'Gap_UnintentionalInjury')
slopes_table.append({'Cause': 'Unintentional Injury', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
fig, ax = plot_gap_timeseries(
    homicide_temporal.reset_index(),
    'Gap_Homicide',
    selected_countries=selected_countries,
    label_lines=True,
    title='Homicide, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Homicide Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.ylim(-1, 65)
plt.savefig('figs/homicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Homicide gap: extremes and trends

```python
extremes_overall(homicide_temporal, 'Gap_Homicide')
```

```python
extremes_in_year(homicide_temporal, 'Gap_Homicide', 2023)
```

```python
summarize_trends(homicide_temporal, 'Gap_Homicide', year_ref=2023)
```

```python
slopes_homicide = slopes_by_country(homicide_temporal, 'Gap_Homicide')
```

```python
cdf = Cdf.from_seq(slopes_homicide['Slope'])
```

```python
slopes_homicide.sort_values(by='Slope').head(10)
```

```python
slopes_homicide.sort_values(by='Slope').tail(10)
```

```python
ext_homicide = get_extremes_for_cause(homicide_temporal, 'Gap_Homicide', slopes_homicide)
extremes_table.append({'Cause': 'Homicide', **ext_homicide})
```

### USA: male and female homicide rates over time

```python
plot_usa_rates_and_trends(homicide_temporal, 'Gap_Homicide', ylabel='Homicide death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(homicide_temporal, 'Gap_Homicide')
slopes_table.append({'Cause': 'Homicide', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
fig, ax = plot_gap_timeseries(
    suicide_temporal.reset_index(),
    'Gap_Suicide',
    selected_countries=selected_countries,
    label_lines=True,
    title='Suicide, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Suicide Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/suicide_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Suicide gap: extremes and trends

```python
extremes_overall(suicide_temporal, 'Gap_Suicide')
```

```python
extremes_in_year(suicide_temporal, 'Gap_Suicide', 2023)
```

```python
summarize_trends(suicide_temporal, 'Gap_Suicide', year_ref=2023)
```

```python
slopes_suicide = slopes_by_country(suicide_temporal, 'Gap_Suicide')
slopes_suicide.sort_values(by='Slope').head(10)
```

```python
slopes_suicide.sort_values(by='Slope').tail(10)
```

```python
ext_suicide = get_extremes_for_cause(suicide_temporal, 'Gap_Suicide', slopes_suicide)
extremes_table.append({'Cause': 'Suicide', **ext_suicide})
```

### USA: male and female suicide rates over time

```python
plot_usa_rates_and_trends(suicide_temporal, 'Gap_Suicide', ylabel='Suicide death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(suicide_temporal, 'Gap_Suicide')
slopes_table.append({'Cause': 'Suicide', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Cardiovascular Death Rate Data

```python
# Load IHME Cardiovascular data
cardiovascular_temporal = load_ihme_indicator_temporal(
    'ihme_cardiovascular_deaths',
    'CardioDeathRate',
    'IHME_CARDIOVASCULAR',
    'Cardiovascular diseases, death rate per 100,000'
)

print(f"Cardiovascular temporal data: {cardiovascular_temporal.shape}")
print(f"Years: {cardiovascular_temporal['Year'].min():.0f} - {cardiovascular_temporal['Year'].max():.0f}")
print(f"Countries: {cardiovascular_temporal['Code'].nunique()}")
cardiovascular_temporal.query('Year == 2023').sort_values(by='Gap_Cardiovascular')
```

### Cardiovascular gap: extremes and trends

```python
extremes_overall(cardiovascular_temporal, 'Gap_Cardiovascular')
```

```python
extremes_in_year(cardiovascular_temporal, 'Gap_Cardiovascular', 2023)
```

```python
summarize_trends(cardiovascular_temporal, 'Gap_Cardiovascular', year_ref=2023)
```

```python
slopes_cardiovascular = slopes_by_country(cardiovascular_temporal, 'Gap_Cardiovascular')
slopes_cardiovascular.sort_values(by='Slope').head(10)
```

```python
slopes_cardiovascular.sort_values(by='Slope').tail(10)
```

```python
ext_cardiovascular = get_extremes_for_cause(cardiovascular_temporal, 'Gap_Cardiovascular', slopes_cardiovascular)
extremes_table.append({'Cause': 'Cardiovascular', **ext_cardiovascular})
```

## Plot Cardiovascular Gender Gap

```python
# USA + extremes: low ever LVA, high ever ISL, low 2023 LVA, high 2023 ISL, low slope LVA, high slope DEU
selected_countries = ['USA', 'DEU', 'ISL', 'LVA']

fig, ax = plot_gap_timeseries(
    cardiovascular_temporal.reset_index(),
    'Gap_Cardiovascular',
    selected_countries=selected_countries,
    label_lines=True,
    title='Cardiovascular Disease, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Cardiovascular Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/cardiovascular_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female cardiovascular rates over time

```python
plot_usa_rates_and_trends(cardiovascular_temporal, 'Gap_Cardiovascular', ylabel='Cardiovascular death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(cardiovascular_temporal, 'Gap_Cardiovascular')
slopes_table.append({'Cause': 'Cardiovascular', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Diabetes Death Rate Data

```python
# Load IHME Diabetes data
diabetes_temporal = load_ihme_indicator_temporal(
    'ihme_diabetes_deaths',
    'DiabetesDeathRate',
    'IHME_DIABETES_TYPE2',
    'Diabetes mellitus type 2, death rate per 100,000'
)

print(f"Diabetes temporal data: {diabetes_temporal.shape}")
print(f"Years: {diabetes_temporal['Year'].min():.0f} - {diabetes_temporal['Year'].max():.0f}")
print(f"Countries: {diabetes_temporal['Code'].nunique()}")
diabetes_temporal.query('Year == 2023').sort_values(by='Gap_Diabetes')
```

### Diabetes gap: extremes and trends

```python
extremes_overall(diabetes_temporal, 'Gap_Diabetes')
```

```python
extremes_in_year(diabetes_temporal, 'Gap_Diabetes', 2023)
```

```python
summarize_trends(diabetes_temporal, 'Gap_Diabetes', year_ref=2023)
```

```python
slopes_diabetes = slopes_by_country(diabetes_temporal, 'Gap_Diabetes')
slopes_diabetes.sort_values(by='Slope').head(10)
```

```python
slopes_diabetes.sort_values(by='Slope').tail(10)
```

```python
ext_diabetes = get_extremes_for_cause(diabetes_temporal, 'Gap_Diabetes', slopes_diabetes)
extremes_table.append({'Cause': 'Diabetes', **ext_diabetes})
```

## Plot Diabetes Gender Gap

```python
# USA + extremes: low ever LVA, high ever MEX, low 2023 LVA, high 2023 MEX, low slope KOR, high slope DEU
selected_countries = ['USA', 'DEU', 'KOR', 'LVA', 'MEX']

fig, ax = plot_gap_timeseries(
    diabetes_temporal.reset_index(),
    'Gap_Diabetes',
    selected_countries=selected_countries,
    label_lines=True,
    title='Diabetes, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Diabetes Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/diabetes_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female diabetes rates over time

```python
plot_usa_rates_and_trends(diabetes_temporal, 'Gap_Diabetes', ylabel='Diabetes death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(diabetes_temporal, 'Gap_Diabetes')
slopes_table.append({'Cause': 'Diabetes', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
fig, ax = plot_gap_timeseries(
    cancer_temporal.reset_index(),
    'Gap_Neoplasms',
    selected_countries=selected_countries,
    label_lines=True,
    title='Cancer, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Cancer Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/cancer_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Cancer (Neoplasms) gap: extremes and trends

```python
extremes_overall(cancer_temporal, 'Gap_Neoplasms')
```

```python
extremes_in_year(cancer_temporal, 'Gap_Neoplasms', 2023)
```

```python
summarize_trends(cancer_temporal, 'Gap_Neoplasms', year_ref=2023)
```

```python
slopes_cancer = slopes_by_country(cancer_temporal, 'Gap_Neoplasms')
slopes_cancer.sort_values(by='Slope').head(10)
```

```python
slopes_cancer.sort_values(by='Slope').tail(10)
```

```python
ext_cancer = get_extremes_for_cause(cancer_temporal, 'Gap_Neoplasms', slopes_cancer)
extremes_table.append({'Cause': 'Cancer', **ext_cancer})
```

### USA: male and female cancer (neoplasms) rates over time

```python
plot_usa_rates_and_trends(cancer_temporal, 'Gap_Neoplasms', ylabel='Cancer death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(cancer_temporal, 'Gap_Neoplasms')
slopes_table.append({'Cause': 'Cancer', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Chronic Respiratory Death Rate Data

```python
# Load IHME Chronic Respiratory data
chronic_respiratory_temporal = load_ihme_indicator_temporal(
    'ihme_chronic_respiratory_deaths',
    'ChronicRespiratoryDeathRate',
    'IHME_CHRONIC_RESPIRATORY',
    'Chronic respiratory diseases, death rate per 100,000'
)

print(f"Chronic Respiratory temporal data: {chronic_respiratory_temporal.shape}")
print(f"Years: {chronic_respiratory_temporal['Year'].min():.0f} - {chronic_respiratory_temporal['Year'].max():.0f}")
print(f"Countries: {chronic_respiratory_temporal['Code'].nunique()}")
chronic_respiratory_temporal.query('Year == 2023').sort_values(by='Gap_ChronicRespiratory')
```

### Chronic Respiratory gap: extremes and trends

```python
extremes_overall(chronic_respiratory_temporal, 'Gap_ChronicRespiratory')
```

```python
extremes_in_year(chronic_respiratory_temporal, 'Gap_ChronicRespiratory', 2023)
```

```python
summarize_trends(chronic_respiratory_temporal, 'Gap_ChronicRespiratory', year_ref=2023)
```

```python
slopes_chronic_resp = slopes_by_country(chronic_respiratory_temporal, 'Gap_ChronicRespiratory')
slopes_chronic_resp.sort_values(by='Slope').head(10)
```

```python
slopes_chronic_resp.sort_values(by='Slope').tail(10)
```

```python
ext_chronic_resp = get_extremes_for_cause(chronic_respiratory_temporal, 'Gap_ChronicRespiratory', slopes_chronic_resp)
extremes_table.append({'Cause': 'Chronic Respiratory', **ext_chronic_resp})
```

## Plot Chronic Respiratory Gender Gap

```python
# USA + extremes: low ever ISL, high ever BEL, low 2023 ISL, high 2023 JPN, low slope BEL, high slope JPN
selected_countries = ['USA', 'BEL', 'ISL', 'JPN']

fig, ax = plot_gap_timeseries(
    chronic_respiratory_temporal.reset_index(),
    'Gap_ChronicRespiratory',
    selected_countries=selected_countries,
    label_lines=True,
    title='Chronic Respiratory Disease, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Chronic Respiratory Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/chronic_respiratory_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female chronic respiratory rates over time

```python
plot_usa_rates_and_trends(chronic_respiratory_temporal, 'Gap_ChronicRespiratory', ylabel='Chronic respiratory death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(chronic_respiratory_temporal, 'Gap_ChronicRespiratory')
slopes_table.append({'Cause': 'Chronic Respiratory', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Liver Disease Death Rate Data

```python
# Load IHME Liver Disease data
liver_disease_temporal = load_ihme_indicator_temporal(
    'ihme_liver_disease_deaths',
    'LiverDiseaseDeathRate',
    'IHME_LIVER_DISEASE',
    'Liver disease, death rate per 100,000'
)

print(f"Liver Disease temporal data: {liver_disease_temporal.shape}")
print(f"Years: {liver_disease_temporal['Year'].min():.0f} - {liver_disease_temporal['Year'].max():.0f}")
print(f"Countries: {liver_disease_temporal['Code'].nunique()}")
liver_disease_temporal.query('Year == 2023').sort_values(by='Gap_LiverDisease')
```

### Liver Disease gap: extremes and trends

```python
extremes_overall(liver_disease_temporal, 'Gap_LiverDisease')
```

```python
extremes_in_year(liver_disease_temporal, 'Gap_LiverDisease', 2023)
```

```python
summarize_trends(liver_disease_temporal, 'Gap_LiverDisease', year_ref=2023)
```

```python
slopes_liver = slopes_by_country(liver_disease_temporal, 'Gap_LiverDisease')
slopes_liver.sort_values(by='Slope').head(10)
```

```python
slopes_liver.sort_values(by='Slope').tail(10)
```

```python
ext_liver = get_extremes_for_cause(liver_disease_temporal, 'Gap_LiverDisease', slopes_liver)
extremes_table.append({'Cause': 'Liver Disease', **ext_liver})
```

## Plot Liver Disease Gender Gap

```python
# USA + extremes: low ever ISL, high ever HUN, low 2023 ISL, high 2023 HUN, low slope HUN, high slope EST
selected_countries = ['USA', 'EST', 'HUN', 'ISL']

fig, ax = plot_gap_timeseries(
    liver_disease_temporal.reset_index(),
    'Gap_LiverDisease',
    selected_countries=selected_countries,
    label_lines=True,
    title='Liver Disease, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Liver Disease Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/liver_disease_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### USA: male and female liver disease rates over time

```python
plot_usa_rates_and_trends(liver_disease_temporal, 'Gap_LiverDisease', ylabel='Liver disease death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(liver_disease_temporal, 'Gap_LiverDisease')
slopes_table.append({'Cause': 'Liver Disease', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
selected_countries = ['USA', 'NOR', 'KOR', 'LTU', 'CAN', 'EST']

# Plot Drug Disorders gap for selected countries
fig, ax = plot_gap_timeseries(
    drug_disorders_temporal.reset_index(),
    'Gap_DrugDisorder',
    selected_countries=selected_countries,
    label_lines=True,
    title='Drug Use Disorders, Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Drug Disorders Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/drug_disorders_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Drug Disorders gap: extremes and trends

```python
extremes_overall(drug_disorders_temporal, 'Gap_DrugDisorder')
```

```python
extremes_in_year(drug_disorders_temporal, 'Gap_DrugDisorder', 2023)
```

```python
summarize_trends(drug_disorders_temporal, 'Gap_DrugDisorder', year_ref=2023)
```

```python
slopes_drug = slopes_by_country(drug_disorders_temporal, 'Gap_DrugDisorder')
slopes_drug.sort_values(by='Slope').head(10)
```

```python
slopes_drug.sort_values(by='Slope').tail(10)
```

```python
ext_drug = get_extremes_for_cause(drug_disorders_temporal, 'Gap_DrugDisorder', slopes_drug)
extremes_table.append({'Cause': 'Drug Disorders', **ext_drug})
```

### USA: male and female drug disorder death rates over time

```python
plot_usa_rates_and_trends(drug_disorders_temporal, 'Gap_DrugDisorder', ylabel='Drug disorder death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(drug_disorders_temporal, 'Gap_DrugDisorder')
slopes_table.append({'Cause': 'Drug Disorders', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

## Load Child Mortality (Under-5) Death Rate Data

```python
# Load IHME All-Cause Under-5 deaths (child mortality)
# Uses age_filter='<5 years' for under-5 mortality
childhood_temporal = load_ihme_indicator_temporal(
    'ihme_all_causes_under5_deaths',
    'AllCausesUnder5DeathRate',
    'IHME_ALL_CAUSES_UNDER5',
    'All-cause deaths under 5 years, death rate per 100,000',
    age_filter='<5 years'
)

print(f"Child mortality (under-5) temporal data: {childhood_temporal.shape}")
print(f"Years: {childhood_temporal['Year'].min():.0f} - {childhood_temporal['Year'].max():.0f}")
print(f"Countries: {childhood_temporal['Code'].nunique()}")
childhood_temporal.query('Year == 2023').sort_values(by='Gap_Childhood')
```

## Plot Child Mortality Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'IRL', 'MEX', 'TUR']

# Plot Child mortality gap for selected countries
fig, ax = plot_gap_timeseries(
    childhood_temporal.reset_index(),
    'Gap_Childhood',
    selected_countries=selected_countries,
    label_lines=True,
    title='Child Mortality (Under-5), Death Rate Gender Gap',
    subtitle='OECD countries, 2000–2023',
    ylabel='Child Mortality Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/childhood_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Child mortality gap: extremes and trends

```python
extremes_overall(childhood_temporal, 'Gap_Childhood')
```

```python
extremes_in_year(childhood_temporal, 'Gap_Childhood', 2023)
```

```python
summarize_trends(childhood_temporal, 'Gap_Childhood', year_ref=2023)
```

```python
slopes_childhood = slopes_by_country(childhood_temporal, 'Gap_Childhood')
slopes_childhood.sort_values(by='Slope').head(10)
```

```python
slopes_childhood.sort_values(by='Slope').tail(10)
```

```python
ext_childhood = get_extremes_for_cause(childhood_temporal, 'Gap_Childhood', slopes_childhood)
extremes_table.append({'Cause': 'Child Mortality', **ext_childhood})
```

### USA: male and female child mortality rates over time

```python
plot_usa_rates_and_trends(childhood_temporal, 'Gap_Childhood', ylabel='Child mortality (under-5) death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(childhood_temporal, 'Gap_Childhood')
slopes_table.append({'Cause': 'Child Mortality', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
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
covid_temporal.query('Year == 2020').sort_values(by='Gap_COVID')
```

## Plot COVID-19 Gender Gap

```python
# Selected countries to highlight
selected_countries = ['USA', 'NOR', 'KOR', 'LTU', 'CAN']

# Plot COVID-19 gap for selected countries
fig, ax = plot_gap_timeseries(
    covid_temporal.reset_index(),
    'Gap_COVID',
    selected_countries=selected_countries,
    label_lines=True,
    title='COVID-19, Death Rate Gender Gap',
    subtitle='OECD countries, 2020–2023',
    ylabel='COVID-19 Death Rate Gap (per 100,000)',
    subtext='Source: Global Burden of Disease from IHME',
    logo=True
)
plt.savefig('figs/covid19_gap_timeseries_selected.png', dpi=150, bbox_inches='tight')
plt.show()
```

### COVID-19 gap: extremes and trends

```python
extremes_overall(covid_temporal, 'Gap_COVID')
```

```python
extremes_in_year(covid_temporal, 'Gap_COVID', 2023)
```

```python
summarize_trends(covid_temporal, 'Gap_COVID', year_ref=2023)
```

```python
slopes_covid = slopes_by_country(covid_temporal, 'Gap_COVID')
slopes_covid.sort_values(by='Slope').head(10)
```

```python
slopes_covid.sort_values(by='Slope').tail(10)
```

```python
ext_covid = get_extremes_for_cause(covid_temporal, 'Gap_COVID', slopes_covid)
extremes_table.append({'Cause': 'COVID-19', **ext_covid})
```

### USA: male and female COVID-19 death rates over time

```python
plot_usa_rates_and_trends(covid_temporal, 'Gap_COVID', ylabel='COVID-19 death rate per 100,000')
```

```python
m_slope, f_slope, g_slope = compute_oecd_slopes(covid_temporal, 'Gap_COVID')
slopes_table.append({'Cause': 'COVID-19', 'Male_slope': m_slope, 'Female_slope': f_slope, 'Gap_slope': g_slope})
```

```python
covid_temporal.query('Code=="USA"')['Gap_COVID']
```

## Summary: Cause Characterization by Gap Trend and Driver

```python
# Build slopes DataFrame and add characterization
slopes_df = pd.DataFrame(slopes_table)

# 1) Gap growing or shrinking
slopes_df['Gap_direction'] = slopes_df['Gap_slope'].apply(
    lambda s: 'growing' if s > 0 else ('shrinking' if s < 0 else 'stable')
)

# 2) Driver: male, female, or both (based on relative magnitude of slopes)
# Gap = Male - Female, so Gap_slope ≈ Male_slope - Female_slope
# If gap growing: male rates rising faster than female, or female falling faster than male
# Driver = 'male' if |male_slope| >> |female_slope|, 'female' if |female_slope| >> |male_slope|, else 'both'
def classify_driver(row):
    m, f = abs(row['Male_slope']), abs(row['Female_slope'])
    if m > 2 * f:
        return 'male'
    if f > 2 * m:
        return 'female'
    return 'both'

slopes_df['Driver'] = slopes_df.apply(classify_driver, axis=1)

# Display table
slopes_df[['Cause', 'Male_slope', 'Female_slope', 'Gap_slope', 'Gap_direction', 'Driver']]
```

```python
# Log summary to file
import os
log_path = 'logs/time_series_slopes_summary.txt'
os.makedirs('logs', exist_ok=True)
with open(log_path, 'w') as f:
    f.write("OECD-Average Slopes (per year) and Cause Characterization\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'Cause':<20} {'Male_slope':>12} {'Female_slope':>12} {'Gap_slope':>12} {'Direction':<10} {'Driver':<8}\n")
    f.write("-" * 70 + "\n")
    for _, row in slopes_df.iterrows():
        f.write(f"{row['Cause']:<20} {row['Male_slope']:>12.4f} {row['Female_slope']:>12.4f} {row['Gap_slope']:>12.4f} {row['Gap_direction']:<10} {row['Driver']:<8}\n")
    f.write("=" * 70 + "\n")
    f.write("\nGap_direction: growing = male-female gap widening; shrinking = gap narrowing.\n")
    f.write("Driver: which sex's rate change dominates the gap trend (male, female, or both).\n")
print(f"Summary logged to {log_path}")
```

```python
# Log extremes (highest/lowest gap ever, 2023, slopes) per cause
extremes_log_path = 'logs/time_series_extremes_by_cause.txt'
with open(extremes_log_path, 'w') as f:
    f.write("Extremes by Cause: Highest/Lowest Gaps (ever, 2023) and Slopes\n")
    f.write("=" * 80 + "\n")
    for rec in extremes_table:
        c = rec['Cause']
        f.write(f"\n{c}\n")
        f.write(f"  Lowest gap ever:   {rec['lowest_gap_ever_val']:.2f} ({rec['lowest_gap_ever_code']}, {rec['lowest_gap_ever_year']})\n")
        f.write(f"  Highest gap ever:  {rec['highest_gap_ever_val']:.2f} ({rec['highest_gap_ever_code']}, {rec['highest_gap_ever_year']})\n")
        f.write(f"  Lowest gap 2023:   {rec['lowest_gap_2023_val']:.2f} ({rec['lowest_gap_2023_code']})\n")
        f.write(f"  Highest gap 2023:  {rec['highest_gap_2023_val']:.2f} ({rec['highest_gap_2023_code']})\n")
        f.write(f"  Lowest slope:      {rec['lowest_slope_val']:.4f} ({rec['lowest_slope_code']})\n")
        f.write(f"  Highest slope:     {rec['highest_slope_val']:.4f} ({rec['highest_slope_code']})\n")
print(f"Extremes logged to {extremes_log_path}")
```

```python
# Save table to CSV for reuse
slopes_df.to_csv('tables/time_series_slopes_by_cause.csv', index=False)
print("Table saved to tables/time_series_slopes_by_cause.csv")
```
