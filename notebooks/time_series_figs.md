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

### USA: male and female road traffic death rates over time

```python
plot_usa_rates_and_trends(road_injuries_temporal, 'Gap_RoadTraffic', ylabel='Road traffic death rate per 100,000')
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

### USA: male and female homicide rates over time

```python
plot_usa_rates_and_trends(homicide_temporal, 'Gap_Homicide', ylabel='Homicide death rate per 100,000')
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

### USA: male and female suicide rates over time

```python
plot_usa_rates_and_trends(suicide_temporal, 'Gap_Suicide', ylabel='Suicide death rate per 100,000')
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

### USA: male and female cancer (neoplasms) rates over time

```python
plot_usa_rates_and_trends(cancer_temporal, 'Gap_Neoplasms', ylabel='Cancer death rate per 100,000')
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

### USA: male and female drug disorder death rates over time

```python
plot_usa_rates_and_trends(drug_disorders_temporal, 'Gap_DrugDisorder', ylabel='Drug disorder death rate per 100,000')
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

### USA: male and female COVID-19 death rates over time

```python
plot_usa_rates_and_trends(covid_temporal, 'Gap_COVID', ylabel='COVID-19 death rate per 100,000')
```

```python
covid_temporal.query('Code=="USA"')['Gap_COVID']
```
