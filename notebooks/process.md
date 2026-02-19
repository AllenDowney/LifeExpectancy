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

# Data Processing

This notebook processes life expectancy and mortality indicator data to create the panel dataset used by the Bayesian models.

**Outputs:**
- `interim/panel_le.h5` — Panel data for Python (bayesian_model.ipynb)
- `interim/panel_le.csv` — Panel data for R (bayesian_model.Rmd)


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
    decorate, underride, configure_plot_style,
    code_to_who_country, code_to_wef_country, write_html_table,
    load_and_inventory, compute_gender_gap, summarize_gap, scatter_plot,
    get_oecd, summarize_years, plot_cdfs, plot_distributions,
    column_name_mapping, oecd_codes
)

configure_plot_style()

# Set cutoff year for temporal analysis (excludes 2020+ to avoid COVID-19 distortions)
cutoff_year = 2019
```

```python
from utils import setup_beep_on_error
setup_beep_on_error()
```

```python
import os

# Open debug log file for the entire notebook
os.makedirs('logs', exist_ok=True)
log_path = f'logs/process_{cutoff_year}.txt'
log_file = open(log_path, 'w')

log_file.write("Data Processing Log\n")
log_file.write("=" * 80 + "\n")
log_file.write(f"Notebook: process.md\n")
log_file.write(f"Cutoff Year: {cutoff_year}\n")
log_file.write(f"Started: {pd.Timestamp.now()}\n")
log_file.write("=" * 80 + "\n\n")

print(f"Log file opened: {log_path}")
```

```python
def log_and_print(message, log=None):
    """
    Helper function to write to log file and print to notebook.
    
    Parameters:
    -----------
    message : str
        Message to log and print
    log : file object, optional
        Log file handle (uses global log_file if None)
    """
    if log is None:
        log = globals().get('log_file', None)
    
    if log:
        log.write(message + "\n")
        log.flush()
    
    print(message)
```

## WHO HALE data

**Healthy Life Expectancy (HALE) at birth** - The average number of years that a person can expect to live in "full health" by taking into account years lived in less than full health due to disease and/or injury. This is the **target variable** for the analysis. The gender gap (Male HALE - Female HALE) measures the difference in healthy life expectancy between men and women.

**Indicator Code**: WHOSIS_000002  
**Relevance**: Direct measure of the outcome we're trying to explain. Gender differences in HALE reflect the cumulative impact of all mortality and morbidity factors that differentially affect men and women.

Downloaded using the GHO OData API (who_data.py)

https://www.who.int/data/gho/info/gho-odata-api

```python
filename = '../data/who_hale_data.csv'
hale, years = load_and_inventory(filename)
```

```python
d = {'SEX_BTSX': 'Both', 'SEX_FMLE': 'Female', 'SEX_MLE': 'Male', }
hale['Sex'] = hale['Sex'].replace(d)
```

```python
hale.head()
```

```python
col = 'HALE_Years'
hale_gap = summarize_gap(hale, col, cutoff_year=cutoff_year)
plt.savefig('figs/hale_scatter.png', dpi=300, bbox_inches='tight')
```

```python

```

```python
plot_distributions(hale_gap, indicator_name='HALE_Years')
plt.savefig('figs/hale_distributions.png', dpi=300, bbox_inches='tight')
```

## IHME HALE Data Exploration

**Purpose**: Explore IHME HALE data as a potential replacement for WHO HALE data. IHME provides longer temporal coverage (1990-2023 vs 2000-2021 for WHO) which could be valuable for temporal analysis.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-results/)

**Evaluation Criteria**:
- Data structure compatibility with WHO format
- Correlation with WHO values for overlapping years
- Country coverage comparison
- Temporal coverage advantages
- Data quality assessment

```python
# Load IHME HALE data
filename = '../data/IHME-GBD_2023_DATA-fc42b373-1.csv'
ihme_hale_raw = pd.read_csv(filename)

print(f"IHME HALE data shape: {ihme_hale_raw.shape}")
print(f"\nColumns: {list(ihme_hale_raw.columns)}")
print(f"\nFirst few rows:")
ihme_hale_raw.head()
```

```python
# Check data structure using actual column names from the file
log_and_print("\n" + "="*80)
log_and_print("IHME HALE Data Structure")
log_and_print("="*80)
log_and_print(f"Locations: {ihme_hale_raw['location_name'].nunique()} unique countries")
log_and_print(f"Years: {ihme_hale_raw['year'].min()} - {ihme_hale_raw['year'].max()}")
log_and_print(f"Sex categories: {list(ihme_hale_raw['sex_name'].unique())}")
log_and_print(f"Age groups: {list(ihme_hale_raw['age_name'].unique())}")
log_and_print(f"Measures: {list(ihme_hale_raw['measure_name'].unique())}")
log_and_print(f"Metrics: {list(ihme_hale_raw['metric_name'].unique())}")
```

```python
# Convert IHME HALE data to WHO-compatible format
def convert_ihme_hale_to_who_format(df):
    """
    Convert IHME HALE data to WHO-compatible format.
    
    IHME format: location_name, year, sex_name, val, upper, lower
    WHO format: Country (code), Year, Sex, HALE_Years, HALE_Years_High, HALE_Years_Low
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
    
    # Filter to years >= 2000 for fair comparison with WHO
    df = df.query('year >= 2000')
    
    # Map IHME country names to WHO country names
    df['location_name'] = df['location_name'].replace(ihme_country_name_mapping)
    
    # Convert country names to codes
    df['Code'] = df['location_name'].map(who_country_to_code)
    
    # Filter out rows where country mapping failed
    df = df[df['Code'].notna()].copy()
    
    # Map sex values
    sex_mapping = {'Male': 'Male', 'Female': 'Female', 'Both': 'Both'}
    df['Sex'] = df['sex_name'].map(sex_mapping)
    
    # Rename columns to match WHO format
    df = df.rename(columns={
        'year': 'Year',
        'val': 'HALE_Years',
        'upper': 'HALE_Years_High',
        'lower': 'HALE_Years_Low',
        'location_name': 'Country'
    })
    
    # Add WHO-style metadata columns
    df['IndicatorCode'] = 'IHME_HALE'
    df['IndicatorName'] = 'Healthy life expectancy (HALE) at birth (years) - IHME'
    df['CountryCode'] = 'COUNTRY'
    
    # Select and reorder columns to match WHO format
    columns_to_keep = [
        'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
        'HALE_Years', 'HALE_Years_Low', 'HALE_Years_High', 'Country'
    ]
    df = df[columns_to_keep].copy()
    
    # Sort by country, sex, and year
    df = df.sort_values(['Country', 'Sex', 'Year']).reset_index(drop=True)
    
    return df

ihme_hale = convert_ihme_hale_to_who_format(ihme_hale_raw)
years = ihme_hale['Year'].unique()

log_and_print("\n" + "="*80)
log_and_print("Converted IHME HALE Data Summary")
log_and_print("="*80)
log_and_print(f"Shape: {ihme_hale.shape}")
log_and_print(f"Years: {years.min():.0f} - {years.max():.0f}")
log_and_print(f"Countries: {ihme_hale['Country'].nunique()}")
log_and_print(f"Sex categories: {ihme_hale['Sex'].unique()}")
```

```python
ihme_hale.head(10)
```

```python
# Create gap summary for IHME HALE
col = 'HALE_Years'
ihme_hale_gap = summarize_gap(ihme_hale, col, cutoff_year=cutoff_year)
plt.savefig('figs/ihme_hale_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(ihme_hale_gap, indicator_name='HALE_Years_IHME')
plt.savefig('figs/ihme_hale_distributions.png', dpi=300, bbox_inches='tight')
```

### Comparison: WHO vs IHME HALE Data

```python
# Compare WHO and IHME HALE values for overlapping countries and years
# Get OECD countries for both datasets
who_hale_oecd = get_oecd(hale_gap)
ihme_hale_oecd = get_oecd(ihme_hale_gap)

# Find common countries
common_countries = who_hale_oecd.index.intersection(ihme_hale_oecd.index)

log_and_print("\n" + "="*80)
log_and_print("WHO vs IHME HALE - Country Coverage Comparison")
log_and_print("="*80)
log_and_print(f"WHO HALE: {len(who_hale_oecd)} OECD countries")
log_and_print(f"IHME HALE: {len(ihme_hale_oecd)} OECD countries")
log_and_print(f"Common countries: {len(common_countries)}")
log_and_print(f"\nCountries in WHO but not IHME: {set(who_hale_oecd.index) - set(ihme_hale_oecd.index)}")
log_and_print(f"Countries in IHME but not WHO: {set(ihme_hale_oecd.index) - set(who_hale_oecd.index)}")
```

```python
# Compare HALE values (Male, Female, Gap) for common countries
comparison_df = pd.DataFrame({
    'WHO_Male': who_hale_oecd.loc[common_countries, 'HALE_Years_Male'],
    'IHME_Male': ihme_hale_oecd.loc[common_countries, 'HALE_Years_Male'],
    'WHO_Female': who_hale_oecd.loc[common_countries, 'HALE_Years_Female'],
    'IHME_Female': ihme_hale_oecd.loc[common_countries, 'HALE_Years_Female'],
    'WHO_Gap': who_hale_oecd.loc[common_countries, 'Gap_HALE_Years'],
    'IHME_Gap': ihme_hale_oecd.loc[common_countries, 'Gap_HALE_Years']
})

# Calculate correlations
log_and_print("\n" + "="*80)
log_and_print("Correlations between WHO and IHME HALE values")
log_and_print("="*80)
log_and_print(f"Male HALE: r = {comparison_df['WHO_Male'].corr(comparison_df['IHME_Male']):.4f}")
log_and_print(f"Female HALE: r = {comparison_df['WHO_Female'].corr(comparison_df['IHME_Female']):.4f}")
log_and_print(f"HALE Gap: r = {comparison_df['WHO_Gap'].corr(comparison_df['IHME_Gap']):.4f}")
```

```python
# Scatter plot: WHO vs IHME Male HALE
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Male HALE
ax = axes[0]
ax.scatter(comparison_df['WHO_Male'], comparison_df['IHME_Male'], 
           color='C0', alpha=0.6, s=50)
# Add diagonal line
lims = [comparison_df[['WHO_Male', 'IHME_Male']].min().min(),
        comparison_df[['WHO_Male', 'IHME_Male']].max().max()]
ax.plot(lims, lims, 'k--', alpha=0.3, zorder=0)
ax.set_xlabel('WHO Male HALE (years)')
ax.set_ylabel('IHME Male HALE (years)')
ax.set_title(f'Male HALE: WHO vs IHME (r={comparison_df["WHO_Male"].corr(comparison_df["IHME_Male"]):.3f})')
ax.grid(True, alpha=0.3)

# Female HALE
ax = axes[1]
ax.scatter(comparison_df['WHO_Female'], comparison_df['IHME_Female'], 
           color='C3', alpha=0.6, s=50)
lims = [comparison_df[['WHO_Female', 'IHME_Female']].min().min(),
        comparison_df[['WHO_Female', 'IHME_Female']].max().max()]
ax.plot(lims, lims, 'k--', alpha=0.3, zorder=0)
ax.set_xlabel('WHO Female HALE (years)')
ax.set_ylabel('IHME Female HALE (years)')
ax.set_title(f'Female HALE: WHO vs IHME (r={comparison_df["WHO_Female"].corr(comparison_df["IHME_Female"]):.3f})')
ax.grid(True, alpha=0.3)

# HALE Gap
ax = axes[2]
ax.scatter(comparison_df['WHO_Gap'], comparison_df['IHME_Gap'], 
           color='C2', alpha=0.6, s=50)
lims = [comparison_df[['WHO_Gap', 'IHME_Gap']].min().min(),
        comparison_df[['WHO_Gap', 'IHME_Gap']].max().max()]
ax.plot(lims, lims, 'k--', alpha=0.3, zorder=0)
ax.set_xlabel('WHO HALE Gap (years)')
ax.set_ylabel('IHME HALE Gap (years)')
ax.set_title(f'HALE Gap: WHO vs IHME (r={comparison_df["WHO_Gap"].corr(comparison_df["IHME_Gap"]):.3f})')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figs/who_ihme_hale_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
```

```python
# Calculate differences (WHO - IHME) and summary statistics
comparison_df['Male_Diff'] = comparison_df['WHO_Male'] - comparison_df['IHME_Male']
comparison_df['Female_Diff'] = comparison_df['WHO_Female'] - comparison_df['IHME_Female']
comparison_df['Gap_Diff'] = comparison_df['WHO_Gap'] - comparison_df['IHME_Gap']

log_and_print("\n" + "="*80)
log_and_print("Difference Statistics (WHO - IHME)")
log_and_print("="*80)
log_and_print("\nMale HALE:")
log_and_print(str(comparison_df['Male_Diff'].describe()))
log_and_print("\nFemale HALE:")
log_and_print(str(comparison_df['Female_Diff'].describe()))
log_and_print("\nHALE Gap:")
log_and_print(str(comparison_df['Gap_Diff'].describe()))
```

```python
# Show countries with largest discrepancies
comparison_df['Country'] = [code_to_who_country[code] for code in common_countries]
comparison_df_sorted = comparison_df.sort_values('Gap_Diff', key=abs, ascending=False)

print("Top 10 Countries with Largest HALE Gap Discrepancies (|WHO - IHME|):")
print(comparison_df_sorted[['Country', 'WHO_Gap', 'IHME_Gap', 'Gap_Diff']].head(10))
```

```python
# Temporal coverage comparison
log_and_print("\n" + "="*80)
log_and_print("Temporal Coverage Comparison")
log_and_print("="*80)
log_and_print(f"\nWHO HALE:")
log_and_print(f"  Years available: {hale['Year'].min():.0f} - {hale['Year'].max():.0f}")
log_and_print(f"  Total years: {hale['Year'].nunique()}")

log_and_print(f"\nIHME HALE:")
log_and_print(f"  Years available: {ihme_hale['Year'].min():.0f} - {ihme_hale['Year'].max():.0f}")
log_and_print(f"  Total years: {ihme_hale['Year'].nunique()}")

log_and_print(f"\nTemporal Coverage Advantage:")
log_and_print(f"  IHME provides {ihme_hale['Year'].nunique() - hale['Year'].nunique()} additional years of data")
log_and_print(f"  Earlier start: {hale['Year'].min():.0f} (WHO) vs {ihme_hale['Year'].min():.0f} (IHME)")
log_and_print(f"  Later end: {hale['Year'].max():.0f} (WHO) vs {ihme_hale['Year'].max():.0f} (IHME)")
```

### Decision: Should We Swap WHO HALE for IHME HALE?

```python
# Summary of comparison results
log_and_print("\n" + "="*80)
log_and_print("DECISION CRITERIA EVALUATION:")
log_and_print("="*80)

# Correlation statistics (for information, not decision criteria)
male_corr = comparison_df['WHO_Male'].corr(comparison_df['IHME_Male'])
female_corr = comparison_df['WHO_Female'].corr(comparison_df['IHME_Female'])
gap_corr = comparison_df['WHO_Gap'].corr(comparison_df['IHME_Gap'])

log_and_print(f"\nCorrelation between WHO and IHME (informational):")
log_and_print(f"   Male HALE: r = {male_corr:.4f} (R² = {male_corr**2:.4f})")
log_and_print(f"   Female HALE: r = {female_corr:.4f} (R² = {female_corr**2:.4f})")
log_and_print(f"   HALE Gap: r = {gap_corr:.4f} (R² = {gap_corr**2:.4f})")
log_and_print(f"\nNote: Correlation measures agreement, not accuracy.")
log_and_print(f"High correlation (r > 0.94) confirms data sources are measuring similar constructs.")

# Systematic difference (not bias, since neither is ground truth)
male_diff = comparison_df['Male_Diff'].mean()
female_diff = comparison_df['Female_Diff'].mean()
gap_diff = comparison_df['Gap_Diff'].mean()

log_and_print(f"\nMean differences (WHO - IHME):")
log_and_print(f"   Male HALE: {male_diff:+.3f} years")
log_and_print(f"   Female HALE: {female_diff:+.3f} years")
log_and_print(f"   HALE Gap: {gap_diff:+.3f} years")
log_and_print(f"\nNote: Differences indicate methodological variation, not error in either source.")

# Country coverage
who_only = set(who_hale_oecd.index) - set(ihme_hale_oecd.index)
ihme_only = set(ihme_hale_oecd.index) - set(who_hale_oecd.index)
log_and_print(f"\nCountry Coverage:")
log_and_print(f"   Common OECD countries: {len(common_countries)}")
log_and_print(f"   WHO only: {who_only} ({'excluded from analysis anyway' if 'TUR' in who_only else 'N/A'})")
log_and_print(f"   IHME only: {ihme_only if ihme_only else 'None'}")
log_and_print(f"   Effective coverage: Equal (both have 37 countries after excluding Turkey)")

# Temporal coverage
years_advantage = ihme_hale['Year'].nunique() - hale['Year'].nunique()
log_and_print(f"\nTemporal Coverage:")
log_and_print(f"   WHO: {hale['Year'].min():.0f}-{hale['Year'].max():.0f} ({hale['Year'].nunique()} years)")
log_and_print(f"   IHME: {ihme_hale['Year'].min():.0f}-{ihme_hale['Year'].max():.0f} ({ihme_hale['Year'].nunique()} years)")
log_and_print(f"   IHME advantage: {years_advantage} additional years (including COVID period 2020-2023)")

# Methodological considerations
log_and_print(f"\nMethodological Consistency:")
log_and_print(f"   WHO HALE: Separate estimation from cause-of-death data")
log_and_print(f"   IHME HALE: Integrated with GBD 2023 framework")
log_and_print(f"   All predictors: IHME sources (cardiovascular, neoplasms, respiratory, etc.)")
log_and_print(f"   Internal consistency: IHME HALE + IHME predictors = same methodology")

# Overall recommendation
log_and_print("\n" + "="*80)
log_and_print("RECOMMENDATION:")
log_and_print("="*80)

log_and_print("✓ PROCEED WITH IHME HALE AS PRIMARY TARGET")
log_and_print("\nRationale:")
log_and_print("  1. METHODOLOGICAL CONSISTENCY: All predictors come from IHME GBD 2023")
log_and_print("     - Same disability weights across causes")
log_and_print("     - Same population estimates")
log_and_print("     - Coherent analytical framework")
log_and_print("  2. TEMPORAL COVERAGE: 24 years (2000-2023) vs 20 years (2000-2019)")
log_and_print("     - Includes COVID-19 period (2020-2023)")
log_and_print("     - More recent estimates (GBD 2023)")
log_and_print("  3. DATA QUALITY: High correlation (r > 0.94) confirms construct validity")
log_and_print(f"     - Differences reflect methodology, not inaccuracy")
log_and_print("  4. COUNTRY COVERAGE: Equal after excluding Turkey (37 OECD countries)")
log_and_print("\nImplementation:")
log_and_print("  - Save BOTH WHO and IHME HALE to HDF5 for flexibility")
log_and_print("  - Use IHME HALE as primary target in models")
log_and_print("  - WHO HALE available for sensitivity analysis")

log_file.flush()
```

## WHO Life Expectancy data

**Life Expectancy at birth** - The average number of years that a person can expect to live, regardless of health status. This is the **secondary target variable** for the analysis, allowing comparison of which factors explain the gender gap in overall life expectancy versus healthy life expectancy. The gender gap (Female LE - Male LE) measures the difference in life expectancy between women and men.

**Indicator Code**: WHOSIS_000001  
**Relevance**: Life expectancy captures all years lived (healthy and unhealthy), while HALE focuses on healthy years only. Both are calculated from birth, so both should be affected by the same mortality patterns. The relative importance of early-life vs adult mortality may differ between the two outcomes.

Downloaded using the GHO OData API (who_data.py)

https://www.who.int/data/gho/info/gho-odata-api

```python
filename = '../data/who_life_expectancy_data.csv'
le, years = load_and_inventory(filename)
```

```python
d = {'SEX_BTSX': 'Both', 'SEX_FMLE': 'Female', 'SEX_MLE': 'Male', }
le['Sex'] = le['Sex'].replace(d)
```

```python
le.head()
```

```python
col = 'LifeExpectancy_Years'
le_gap = summarize_gap(le, col, cutoff_year=cutoff_year)
plt.savefig('figs/life_expectancy_scatter.png', dpi=300, bbox_inches='tight')
```

```python

```

```python
plot_distributions(le_gap, indicator_name='LifeExpectancy_Years')
plt.savefig('figs/life_expectancy_distributions.png', dpi=300, bbox_inches='tight')
```

## NOTE: WHO predictor sections removed

The WHO predictor sections (smoking, suicide, alcohol, poisoning, road traffic, maternal mortality, homicide, IPV, U5MR, cardiovascular, diabetes, NCD mortality) have been removed. We use IHME data for all predictors as it provides better temporal coverage (1990-2023 vs 2000-2021 for WHO).

## IHME Predictor Indicators

## IHME

### Drug Use Disorders (IHME) - USED IN MODEL

**Drug use disorder death rates (per 100,000 population)** - Deaths from drug use disorders, including overdoses, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Drug overdoses, particularly opioid overdoses, are a major cause of death in some OECD countries (especially the US) and may contribute significantly to the HALE gender gap. **This IHME indicator is used in the model** instead of WHO Poisoning because it provides better temporal coverage (1990-2023 vs 2000-2021 for WHO) and captures drug overdose deaths more comprehensively. This indicator captures overdose deaths that may not be fully captured in the WHO poisoning indicator. Data includes separate male and female values, allowing for gender gap analysis.

```python
def load_ihme_indicator(filename_male, filename_female, value_col_name, indicator_code, indicator_name):
    """
    Load IHME indicator data from separate male and female files and convert to WHO-compatible format.
    
    Converts IHME CSV format (Location=country name, Sex="Male"/"Female") to WHO format
    (Country=country code, Sex="Male"/"Female", etc.). Filters to years >= 2000.
    
    Parameters
    ----------
    filename_male : str
        Path to the IHME CSV file with male data.
    filename_female : str
        Path to the IHME CSV file with female data.
    value_col_name : str
        Name for the value column (e.g., 'DrugDisorderDeathRate', 'DiabetesDeathRate').
    indicator_code : str
        Indicator code for the IHME indicator (e.g., 'IHME_DRUG_DISORDERS', 'IHME_DIABETES_TYPE2').
    indicator_name : str
        Human-readable indicator name (e.g., 'Drug use disorders, death rate per 100,000').
        
    Returns
    -------
    df : pandas.DataFrame
        DataFrame in WHO-compatible format with columns: IndicatorCode, IndicatorName,
        Code, CountryCode, Year, Sex, value_col_name, value_col_name_Low, 
        value_col_name_High, Country.
    years : numpy.ndarray
        Array of unique years present in the filtered dataset.
    """
    # Create reverse mapping from country name to code
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    
    # Map IHME country names that differ from WHO names
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States'
    }
    
    def process_ihme_file(filename, sex_value):
        """Helper function to process a single IHME file."""
        df = pd.read_csv(filename)
        
        # Filter to years >= 2000 (include all available years, let models choose which to use)
        df = df.query('Year >= 2000')
        
        # Filter to "All ages" (if Age column exists)
        if 'Age' in df.columns:
            df = df.query('Age == "All ages"')
        
        # Map IHME country names to WHO country names
        df['Location'] = df['Location'].replace(ihme_country_name_mapping)
        
        # Convert country names to codes
        df['Code'] = df['Location'].map(who_country_to_code)
        
        # Filter out rows where country mapping failed (not in our country list)
        df = df[df['Code'].notna()].copy()
        
        # Set Sex column to the specified value (Male or Female)
        df['Sex'] = sex_value
        
        # Rename and create columns to match WHO format
        df['IndicatorCode'] = indicator_code
        df['IndicatorName'] = indicator_name
        df['CountryCode'] = 'COUNTRY'
        df[value_col_name] = df['Value']
        df[f'{value_col_name}_Low'] = df['Lower bound']
        df[f'{value_col_name}_High'] = df['Upper bound']
        df['Country'] = df['Location']
        
        # Select and reorder columns to match WHO format
        columns_to_keep = [
            'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
            value_col_name, f'{value_col_name}_Low', f'{value_col_name}_High',
            'Country'
        ]
        df = df[columns_to_keep].copy()
        
        return df
    
    # Load and process both files
    df_male = process_ihme_file(filename_male, 'Male')
    df_female = process_ihme_file(filename_female, 'Female')
    
    # Concatenate male and female data
    df = pd.concat([df_male, df_female], ignore_index=True)
    
    # Sort by country, sex, and year
    df = df.sort_values(['Country', 'Sex', 'Year']).reset_index(drop=True)
    
    years = df['Year'].unique()
    
    print(df.shape)
    print(f"Years: {years.min():.0f} - {years.max():.0f}")
    print(f"Countries: {df['Country'].nunique()}")
    print(f"Sex categories: {df['Sex'].unique()}")
    
    return df, years
```

```python
filename_male = '../data/ihme_drug_disorder_deaths_male.csv'
filename_female = '../data/ihme_drug_disorder_deaths_female.csv'
drug_disorders, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='DrugDisorderDeathRate',
    indicator_code='IHME_DRUG_DISORDERS',
    indicator_name='Drug use disorders, death rate per 100,000'
)
```

```python
drug_disorders.head()
```

```python
col = 'DrugDisorderDeathRate'
drug_disorders = drug_disorders.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
drug_disorders_gap = summarize_gap(drug_disorders, col, cutoff_year=cutoff_year)
plt.savefig('figs/drug_disorders_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(drug_disorders_gap, indicator_name='DrugDisorder')
plt.savefig('figs/drug_disorders_distributions.png', dpi=300, bbox_inches='tight')
```

### Diabetes Type 2 (IHME)

**Diabetes type 2 death rates (per 100,000 population)** - Deaths from diabetes mellitus type 2, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: This is an alternative to the WHO diabetes death rate indicator (SA_0000001440) which only has data for 2004. IHME data may have better temporal coverage, allowing for more recent data to be used in the analysis. Diabetes is a chronic condition that can contribute to the gender gap in mortality, though the relationship may vary by country and healthcare access. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_diabetes_deaths_male.csv'
filename_female = '../data/ihme_diabetes_deaths_female.csv'
diabetes_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='DiabetesDeathRate',
    indicator_code='IHME_DIABETES_TYPE2',
    indicator_name='Diabetes mellitus type 2, death rate per 100,000'
)
```

```python
diabetes_ihme.head()
```

```python
col = 'DiabetesDeathRate'
diabetes_ihme = diabetes_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
diabetes_ihme_gap = summarize_gap(diabetes_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/diabetes_ihme_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(diabetes_ihme_gap, indicator_name='Diabetes')
plt.savefig('figs/diabetes_ihme_distributions.png', dpi=300, bbox_inches='tight')
```

### Cardiovascular Diseases (IHME)

**Cardiovascular diseases death rates (per 100,000 population)** - Deaths from cardiovascular diseases, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Cardiovascular diseases are a major cause of death and may contribute significantly to the HALE gender gap. This is an alternative to the WHO cardiovascular disease death rate indicators which only have data for 2004. IHME data may have better temporal coverage, allowing for more recent data to be used in the analysis. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_cardiovascular_deaths_male.csv'
filename_female = '../data/ihme_cardiovascular_deaths_female.csv'
cardiovascular_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='CardioDeathRate',
    indicator_code='IHME_CARDIOVASCULAR',
    indicator_name='Cardiovascular diseases, death rate per 100,000'
)
```

```python
cardiovascular_ihme.head()
```

```python
col = 'CardioDeathRate'
cardiovascular_ihme = cardiovascular_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
cardiovascular_ihme_gap = summarize_gap(cardiovascular_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/cardiovascular_ihme_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(cardiovascular_ihme_gap, indicator_name='Cardiovascular')
plt.savefig('figs/cardiovascular_ihme_distributions.png', dpi=300, bbox_inches='tight')
```

### Neoplasms (Cancer) (IHME)

**Neoplasms (cancer) death rates (per 100,000 population)** - Deaths from neoplasms (cancer), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Neoplasms (cancer) are a major cause of death and may contribute significantly to the HALE gender gap. Different types of cancer have different gender patterns (e.g., lung cancer is often higher in men, breast cancer is female-specific). This indicator provides comprehensive cancer death rates with better temporal coverage than WHO indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_neoplasms_deaths_male.csv'
filename_female = '../data/ihme_neoplasms_deaths_female.csv'
neoplasms_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='NeoplasmsDeathRate',
    indicator_code='IHME_NEOPLASMS',
    indicator_name='Neoplasms (cancer), death rate per 100,000'
)
```

```python
neoplasms_ihme.head()
```

```python
col = 'NeoplasmsDeathRate'
neoplasms_ihme = neoplasms_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
neoplasms_ihme_gap = summarize_gap(neoplasms_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/neoplasms_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(neoplasms_ihme_gap, indicator_name='Neoplasms')
plt.savefig('figs/neoplasms_distributions.png', dpi=300, bbox_inches='tight')
```

### Chronic Respiratory Diseases (IHME)

**Chronic respiratory diseases death rates (per 100,000 population)** - Deaths from chronic respiratory diseases (including COPD, asthma, and other chronic lung conditions), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Chronic respiratory diseases are a major cause of death and may contribute significantly to the HALE gender gap. These diseases often have gender differences due to factors such as smoking patterns, occupational exposures, and environmental factors. This indicator provides comprehensive chronic respiratory disease death rates with better temporal coverage than WHO indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_chronic_respiratory_deaths_male.csv'
filename_female = '../data/ihme_chronic_respiratory_deaths_female.csv'
chronic_respiratory_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='ChronicRespiratoryDeathRate',
    indicator_code='IHME_CHRONIC_RESPIRATORY',
    indicator_name='Chronic respiratory diseases, death rate per 100,000'
)
```

```python
chronic_respiratory_ihme.head()
```

```python
col = 'ChronicRespiratoryDeathRate'
chronic_respiratory_ihme = chronic_respiratory_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
chronic_respiratory_ihme_gap = summarize_gap(chronic_respiratory_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/chronic_respiratory_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(chronic_respiratory_ihme_gap, indicator_name='ChronicRespiratory')
plt.savefig('figs/chronic_respiratory_distributions.png', dpi=300, bbox_inches='tight')
```

### Liver Disease (Cirrhosis and Other Chronic Liver Diseases) (IHME)

**Liver disease death rates (per 100,000 population)** - Deaths from cirrhosis and other chronic liver diseases, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Liver disease (cirrhosis and other chronic liver diseases) is a significant cause of death and may contribute to the HALE gender gap. Men typically have higher rates of liver disease mortality than women, often due to higher alcohol consumption, hepatitis infections, and other risk factors. This indicator provides comprehensive liver disease death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage. Liver disease is often related to alcohol consumption, but also includes non-alcoholic causes such as viral hepatitis, non-alcoholic fatty liver disease, and other chronic liver conditions. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_liver_disease_deaths_male.csv'
filename_female = '../data/ihme_liver_disease_deaths_female.csv'
liver_disease_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='LiverDiseaseDeathRate',
    indicator_code='IHME_LIVER_DISEASE',
    indicator_name='Cirrhosis and other chronic liver diseases, death rate per 100,000'
)
```

```python
liver_disease_ihme.head()
```

```python
col = 'LiverDiseaseDeathRate'
liver_disease_ihme = liver_disease_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
liver_disease_ihme_gap = summarize_gap(liver_disease_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/liver_disease_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(liver_disease_ihme_gap, indicator_name='LiverDisease')
plt.savefig('figs/liver_disease_distributions.png', dpi=300, bbox_inches='tight')
```

### COVID-19 (IHME)

**COVID-19 death rates (per 100,000 population)** - Deaths from COVID-19, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: COVID-19 is a significant cause of death that emerged in 2020 and may contribute to the HALE gender gap. COVID-19 mortality patterns show gender differences, with men typically having higher death rates than women in most countries. This indicator provides comprehensive COVID-19 death rates with temporal coverage from 2020-2023. Note: Data includes zeros for all years before 2020 (1990-2019) since COVID-19 did not exist before 2020. This indicator is particularly relevant for understanding recent changes in the gender gap in life expectancy and HALE, as the pandemic had substantial impacts on mortality patterns. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_covid19_deaths_male.csv'
filename_female = '../data/ihme_covid19_deaths_female.csv'
covid19_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='COVID19DeathRate',
    indicator_code='IHME_COVID19',
    indicator_name='COVID-19, death rate per 100,000'
)
```

```python
covid19_ihme.head()
```

```python
col = 'COVID19DeathRate'
covid19_ihme = covid19_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
covid19_ihme_gap = summarize_gap(covid19_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/covid19_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(covid19_ihme_gap, indicator_name='COVID19')
plt.savefig('figs/covid19_distributions.png', dpi=300, bbox_inches='tight')
```

### Unintentional Injuries (IHME)

**Unintentional injuries death rates (per 100,000 population)** - Deaths from unintentional injuries (including falls, drowning, fires, and other accidents), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Unintentional injuries are a significant cause of death and may contribute to the HALE gender gap. These injuries often show gender differences due to occupational exposures, risk-taking behaviors, and activity patterns. This indicator provides comprehensive unintentional injury death rates with better temporal coverage (1990-2023) than many WHO indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_unintentional_injuries_deaths_male.csv'
filename_female = '../data/ihme_unintentional_injuries_deaths_female.csv'
unintentional_injuries_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='UnintentionalInjuriesDeathRate',
    indicator_code='IHME_UNINTENTIONAL_INJURIES',
    indicator_name='Unintentional injuries, death rate per 100,000'
)
```

```python
unintentional_injuries_ihme.head()
```

```python
col = 'UnintentionalInjuriesDeathRate'
unintentional_injuries_ihme = unintentional_injuries_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
unintentional_injuries_ihme_gap = summarize_gap(unintentional_injuries_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/unintentional_injuries_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(unintentional_injuries_ihme_gap, indicator_name='UnintentionalInjury')
plt.savefig('figs/unintentional_injuries_distributions.png', dpi=300, bbox_inches='tight')
```

### Alcohol Use Disorders (IHME) - USED IN MODEL

**Alcohol use disorders death rates (per 100,000 population)** - Deaths from alcohol use disorders, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Alcohol use disorders are a significant cause of death and may contribute to the HALE gender gap. Men typically have higher rates of alcohol-related mortality than women. This indicator provides comprehensive alcohol use disorder death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO alcohol-attributable death rate indicator (SA_0000001832) which only has data for 2019. **This IHME version is used in the model** because it provides much better temporal coverage, allowing for temporal analysis and more recent data. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_alcohol_use_disorders_deaths_male.csv'
filename_female = '../data/ihme_alcohol_use_disorders_deaths_female.csv'
alcohol_use_disorders_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='AlcoholUseDisordersDeathRate',
    indicator_code='IHME_ALCOHOL_USE_DISORDERS',
    indicator_name='Alcohol use disorders, death rate per 100,000'
)
```

```python
alcohol_use_disorders_ihme.head()
```

```python
col = 'AlcoholUseDisordersDeathRate'
alcohol_use_disorders_ihme = alcohol_use_disorders_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
alcohol_use_disorders_ihme_gap = summarize_gap(alcohol_use_disorders_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/alcohol_ihme_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(alcohol_use_disorders_ihme_gap, indicator_name='Alcohol')
plt.savefig('figs/alcohol_ihme_distributions.png', dpi=300, bbox_inches='tight')
```

### Self-Harm (IHME) - USED IN MODEL

**Self-harm (suicide) death rates (per 100,000 population)** - Deaths from self-harm (suicide), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Self-harm (suicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher suicide rates than women in most countries. This indicator provides comprehensive self-harm death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO suicide rate indicator (MH_12) which has data for 2000-2021. **This IHME version is used in the model** because it provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_self_harm_deaths_male.csv'
filename_female = '../data/ihme_self_harm_deaths_female.csv'
self_harm_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='SelfHarmDeathRate',
    indicator_code='IHME_SELF_HARM',
    indicator_name='Self-harm (suicide), death rate per 100,000'
)
```

```python
self_harm_ihme.head()
```

```python
col = 'SelfHarmDeathRate'
self_harm_ihme = self_harm_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
self_harm_ihme_gap = summarize_gap(self_harm_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/self_harm_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(self_harm_ihme_gap, indicator_name='Suicide')
plt.savefig('figs/self_harm_distributions.png', dpi=300, bbox_inches='tight')
```

### Interpersonal Violence (IHME) - USED IN MODEL

**Interpersonal violence (homicide) death rates (per 100,000 population)** - Deaths from interpersonal violence (homicide), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Interpersonal violence (homicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher homicide rates than women in most countries. This indicator provides comprehensive interpersonal violence death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO homicide rate indicator (VIOLENCE_HOMICIDERATE) which has data for 2000-2021. **This IHME version is used in the model** because it provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_interpersonal_violence_deaths_male.csv'
filename_female = '../data/ihme_interpersonal_violence_deaths_female.csv'
interpersonal_violence_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='InterpersonalViolenceDeathRate',
    indicator_code='IHME_INTERPERSONAL_VIOLENCE',
    indicator_name='Interpersonal violence (homicide), death rate per 100,000'
)
```

```python
interpersonal_violence_ihme.head()
```

```python
col = 'InterpersonalViolenceDeathRate'
interpersonal_violence_ihme = interpersonal_violence_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
interpersonal_violence_ihme_gap = summarize_gap(interpersonal_violence_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/interpersonal_violence_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(interpersonal_violence_ihme_gap, indicator_name='Homicide')
plt.savefig('figs/interpersonal_violence_distributions.png', dpi=300, bbox_inches='tight')
```

### Road Injuries (IHME) - USED IN MODEL

**Road injuries (road traffic crash) death rates (per 100,000 population)** - Deaths from road injuries (road traffic crashes), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Road injuries (road traffic crashes) are a significant cause of death and contribute to the HALE gender gap. Men typically have 2-4 times higher road traffic death rates than women in most countries due to higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. This indicator provides comprehensive road injury death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO road traffic crash death rate indicator (SA_0000001459) which only has data for 2019. **This IHME version is used in the model** because it provides much better temporal coverage (1990-2023 vs 2019 only) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_road_injuries_deaths_male.csv'
filename_female = '../data/ihme_road_injuries_deaths_female.csv'
road_injuries_ihme, years = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='RoadInjuriesDeathRate',
    indicator_code='IHME_ROAD_INJURIES',
    indicator_name='Road injuries (road traffic crashes), death rate per 100,000'
)
```

```python
road_injuries_ihme.head()
```

```python
col = 'RoadInjuriesDeathRate'
road_injuries_ihme = road_injuries_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
road_injuries_ihme_gap = summarize_gap(road_injuries_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/road_injuries_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(road_injuries_ihme_gap, indicator_name='RoadTraffic')
plt.savefig('figs/road_injuries_distributions.png', dpi=300, bbox_inches='tight')
```

### Maternal Disorders (IHME)

**Maternal disorders death rates (per 100,000 population)** - Deaths from maternal disorders, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Maternal disorders (maternal mortality) are a significant cause of death for women and can contribute to the HALE gender gap, especially in lower-income countries. High maternal mortality can significantly reduce female life expectancy, explaining why some countries have smaller gender gaps. This indicator provides comprehensive maternal disorder death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO maternal mortality ratio indicator (MDG_0000000026) which has data for 1985-2023. Note: WHO indicator uses ratio per 100,000 live births, while IHME uses rate per 100,000 population, so they measure slightly different things. IHME data may be useful for temporal analysis and provides consistent methodology with other IHME indicators. Inherently female-specific, so only female values are used in analysis.

```python
filename_female = '../data/ihme_maternal_disorders_deaths_female.csv'
# Maternal disorders is female-only, so we need to handle it differently
# Load the female file and create a compatible format
maternal_disorders_ihme_female = pd.read_csv(filename_female)

# Filter to years >= 2000 (include all available years, let models choose which to use)
maternal_disorders_ihme_female = maternal_disorders_ihme_female.query('Year >= 2000')

# Filter to "All ages" (if Age column exists)
if 'Age' in maternal_disorders_ihme_female.columns:
    maternal_disorders_ihme_female = maternal_disorders_ihme_female.query('Age == "All ages"')

# Map IHME country names to WHO country names
who_country_to_code = {country: code for code, country in code_to_who_country.items()}
ihme_country_name_mapping = {
    'Republic of Korea': 'South Korea',
    'United States of America': 'United States'
}
maternal_disorders_ihme_female['Location'] = maternal_disorders_ihme_female['Location'].replace(ihme_country_name_mapping)

# Convert country names to codes
maternal_disorders_ihme_female['Code'] = maternal_disorders_ihme_female['Location'].map(who_country_to_code)

# Filter out rows where country mapping failed
maternal_disorders_ihme_female = maternal_disorders_ihme_female[maternal_disorders_ihme_female['Code'].notna()].copy()

# Set Sex column to Female
maternal_disorders_ihme_female['Sex'] = 'Female'

# Rename and create columns to match WHO format
maternal_disorders_ihme_female['IndicatorCode'] = 'IHME_MATERNAL_DISORDERS'
maternal_disorders_ihme_female['IndicatorName'] = 'Maternal disorders, death rate per 100,000'
maternal_disorders_ihme_female['CountryCode'] = 'COUNTRY'
maternal_disorders_ihme_female['MaternalDisordersDeathRate'] = maternal_disorders_ihme_female['Value']
maternal_disorders_ihme_female['MaternalDisordersDeathRate_Low'] = maternal_disorders_ihme_female['Lower bound']
maternal_disorders_ihme_female['MaternalDisordersDeathRate_High'] = maternal_disorders_ihme_female['Upper bound']
maternal_disorders_ihme_female['Country'] = maternal_disorders_ihme_female['Location']

# Select and reorder columns to match WHO format
columns_to_keep = [
    'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
    'MaternalDisordersDeathRate', 'MaternalDisordersDeathRate_Low', 'MaternalDisordersDeathRate_High',
    'Country'
]
maternal_disorders_ihme = maternal_disorders_ihme_female[columns_to_keep].copy()

# Sort by country and year
maternal_disorders_ihme = maternal_disorders_ihme.sort_values(['Country', 'Year']).reset_index(drop=True)

years = maternal_disorders_ihme['Year'].unique()

print(maternal_disorders_ihme.shape)
print(f"Years: {years.min():.0f} - {years.max():.0f}")
print(f"Countries: {maternal_disorders_ihme['Country'].nunique()}")
print(f"Sex categories: {maternal_disorders_ihme['Sex'].unique()}")
```

```python
maternal_disorders_ihme.head()
```

```python
col = 'MaternalDisordersDeathRate'
maternal_disorders_ihme = maternal_disorders_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
maternal_disorders_ihme_gap = summarize_gap(maternal_disorders_ihme, col, sexes=['Female'], cutoff_year=cutoff_year)
plt.savefig('figs/maternal_disorders_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(maternal_disorders_ihme_gap, indicator_name='MaternalDisorders')
plt.savefig('figs/maternal_disorders_distributions.png', dpi=300, bbox_inches='tight')
```

### All-Cause Deaths Under 5 Years of Age (IHME) - USED IN MODEL

**All-cause deaths under 5 years of age (per 100,000 population)** - Deaths from all causes for children under 5 years of age, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: All-cause mortality for children under 5 years of age is relevant to the HALE gender gap because HALE is calculated from birth, so early-life mortality directly affects HALE calculations. If child mortality differs by gender, it directly contributes to the HALE gender gap. Infant and child mortality is typically higher in males (biological vulnerability + some behavioral factors). **This IHME version is used in the model** because it provides better temporal coverage (1990-2023) and consistent methodology with other IHME indicators. This is different from the WHO under-five mortality rate (U5MR, MDG_0000000007) which measures deaths per 1,000 live births. The IHME indicator measures deaths per 100,000 population, providing a complementary perspective on early-life mortality. Data includes separate male and female values, allowing for gender gap analysis.

```python
filename_male = '../data/ihme_all_causes_under5_deaths_male.csv'
filename_female = '../data/ihme_all_causes_under5_deaths_female.csv'
# All-cause under 5 needs special handling because it's for "<5 years" age group, not "All ages"
# We'll create a modified version of load_ihme_indicator that filters for "<5 years" instead

def load_ihme_indicator_under5(filename_male, filename_female, value_col_name, indicator_code, indicator_name):
    """
    Load IHME indicator data for under-5 age group from separate male and female files.
    
    Similar to load_ihme_indicator but filters for "<5 years" age group instead of "All ages".
    """
    # Create reverse mapping from country name to code
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    
    # Map IHME country names that differ from WHO names
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States'
    }
    
    def process_ihme_file(filename, sex_value):
        """Helper function to process a single IHME file."""
        df = pd.read_csv(filename)
        
        # Filter to years >= 2000 (include all available years, let models choose which to use)
        df = df.query('Year >= 2000')
        
        # Filter to "<5 years" age group
        if 'Age' in df.columns:
            df = df.query('Age == "<5 years"')
        
        # Map IHME country names to WHO country names
        df['Location'] = df['Location'].replace(ihme_country_name_mapping)
        
        # Convert country names to codes
        df['Code'] = df['Location'].map(who_country_to_code)
        
        # Filter out rows where country mapping failed (not in our country list)
        df = df[df['Code'].notna()].copy()
        
        # Set Sex column to the specified value (Male or Female)
        df['Sex'] = sex_value
        
        # Rename and create columns to match WHO format
        df['IndicatorCode'] = indicator_code
        df['IndicatorName'] = indicator_name
        df['CountryCode'] = 'COUNTRY'
        df[value_col_name] = df['Value']
        df[f'{value_col_name}_Low'] = df['Lower bound']
        df[f'{value_col_name}_High'] = df['Upper bound']
        df['Country'] = df['Location']
        
        # Select and reorder columns to match WHO format
        columns_to_keep = [
            'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
            value_col_name, f'{value_col_name}_Low', f'{value_col_name}_High',
            'Country'
        ]
        df = df[columns_to_keep].copy()
        
        return df
    
    # Load and process both files
    df_male = process_ihme_file(filename_male, 'Male')
    df_female = process_ihme_file(filename_female, 'Female')
    
    # Concatenate male and female data
    df = pd.concat([df_male, df_female], ignore_index=True)
    
    # Sort by country, sex, and year
    df = df.sort_values(['Country', 'Sex', 'Year']).reset_index(drop=True)
    
    years = df['Year'].unique()
    
    print(df.shape)
    print(f"Years: {years.min():.0f} - {years.max():.0f}")
    print(f"Countries: {df['Country'].nunique()}")
    print(f"Sex categories: {df['Sex'].unique()}")
    
    return df, years

all_causes_under5_ihme, years = load_ihme_indicator_under5(
    filename_male, filename_female,
    value_col_name='AllCausesUnder5DeathRate',
    indicator_code='IHME_ALL_CAUSES_UNDER5',
    indicator_name='All-cause deaths under 5 years, death rate per 100,000'
)
```

```python
all_causes_under5_ihme.head()
```

```python
col = 'AllCausesUnder5DeathRate'
all_causes_under5_ihme = all_causes_under5_ihme.rename(columns=column_name_mapping)
col = column_name_mapping.get(col, col)
all_causes_under5_ihme_gap = summarize_gap(all_causes_under5_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/all_causes_under5_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(all_causes_under5_ihme_gap, indicator_name='Childhood')
plt.savefig('figs/all_causes_under5_distributions.png', dpi=300, bbox_inches='tight')
```



## Data Preparation for Regression Analysis

### Prepare Target Variables (HALE and Life Expectancy Gender Gaps)

```python
# Calculate HALE gender gap from existing hale_gap DataFrame
# Gap = Female - Male (positive means females have higher HALE)
hale_gap['HALE_gap'] = hale_gap['HALE_Years_Female'] - hale_gap['HALE_Years_Male']

# Filter to OECD countries
hale_oecd = get_oecd(hale_gap)

# Display summary
hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].describe()
```

```python
# Calculate Life Expectancy gender gap from existing le_gap DataFrame
# Gap = Female - Male (positive means females have higher Life Expectancy)
le_gap['LifeExpectancy_gap'] = le_gap['LifeExpectancy_Years_Female'] - le_gap['LifeExpectancy_Years_Male']

# Filter to OECD countries
le_oecd = get_oecd(le_gap)

# Display summary
le_oecd[['LifeExpectancy_Years_Male', 'LifeExpectancy_Years_Female', 'LifeExpectancy_gap']].describe()
```


### Merge All Predictors into Single Dataset

```python
# Start with HALE and LE
analysis_df = hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].copy()

analysis_df = analysis_df.join(le_oecd[['LifeExpectancy_Years_Male', 'LifeExpectancy_Years_Female', 'LifeExpectancy_gap']], how='outer')
```

```python
# Unified mapping from indicator names to complete _gap datasets
# This is the single source of truth for all indicators used in the analysis
indicator_datasets = {
    'Alcohol': alcohol_use_disorders_ihme_gap,  # Using IHME version, renamed to 'Alcohol' via column_name_mapping
    'ChronicRespiratory': chronic_respiratory_ihme_gap,
    'UnintentionalInjury': unintentional_injuries_ihme_gap,
    'RoadTraffic': road_injuries_ihme_gap,  # Using IHME version, renamed to 'RoadTraffic' via column_name_mapping
    'Diabetes': diabetes_ihme_gap,
    'Cardiovascular': cardiovascular_ihme_gap,
    # 'Childhood': all_causes_under5_ihme_gap,  # Removed - low importance and limited temporal coverage. WHO U5MR (per 1,000 live births) is methodologically appropriate but has limited temporal coverage. IHME version (per 100,000 population) is confounded with age structure and fertility.
    'DrugDisorder': drug_disorders_gap,  # Using IHME version, replacing WHO Poisoning
    'Homicide': interpersonal_violence_ihme_gap,  # Using IHME version, renamed to 'Homicide' via column_name_mapping
    # 'Poisoning': poison_gap,  # Removed - using DrugDisorder (IHME) instead
    'Suicide': self_harm_ihme_gap,  # Using IHME version, renamed to 'Suicide' via column_name_mapping
    # 'MaternalMortality': maternal_gap,  # Removed - positive coefficient is suspect (higher female mortality should close gap, not widen it). Likely capturing general healthcare quality with limited variation in rich countries.
    'Neoplasms': neoplasms_ihme_gap,
    'LiverDisease': liver_disease_ihme_gap,  # Using IHME version
    'COVID': covid19_ihme_gap,  # Using IHME version
}

# Create predictor_dfs by applying OECD filtering to indicator_datasets
# Note: We will exclude Country and Year columns before merging
# We keep Mid (midpoint) and Gap columns as predictors, plus Male/Female columns for counterfactual analysis
predictor_dfs = {name: get_oecd(df) for name, df in indicator_datasets.items()}
```

```python
# Summary table of year coverage for each indicator
year_summary_df = summarize_years(predictor_dfs)
year_summary_df
```

```python
for name, df in predictor_dfs.items():
    drop_cols = ['Country', 'Year']
    # Keep Male, Female, Mid, and Gap columns for counterfactual analysis
    # Only drop Country and Year columns
    if drop_cols:
        predictor_dfs[name] = df.drop(columns=drop_cols)

# Check shapes after dropping Country and Year
for name, predictor_df in predictor_dfs.items():
    print(name, predictor_df.shape)
```

```python
# Merge all predictors on index (Country codes)
for name, df in predictor_dfs.items():
    analysis_df = analysis_df.join(df, how='outer')

# Display shape and column names
analysis_df.shape
```

```python
analysis_df.head()
```

```python
# Create missing data report
missing_report = pd.DataFrame({
    'Indicator': analysis_df.columns,
    'Missing_Count': [analysis_df[col].isna().sum() for col in analysis_df.columns],
    'Missing_Pct': [analysis_df[col].isna().sum() / len(analysis_df) * 100 for col in analysis_df.columns],
    'Available_Count': [analysis_df[col].notna().sum() for col in analysis_df.columns]
}).sort_values('Missing_Count', ascending=False)

missing_report
```

```python
# Show which countries have complete data for all indicators
complete_cases = analysis_df.dropna()
complete_cases.shape[0], f"{complete_cases.shape[0] / len(analysis_df) * 100:.1f}% of countries have complete data"
```


### Create Final Analysis Dataset

```python
# Use complete-case analysis for primary model
analysis_complete = analysis_df.dropna()

# Document excluded countries
excluded_countries = set(analysis_df.index) - set(analysis_complete.index)
excluded_countries if excluded_countries else "No countries excluded - all OECD countries have complete data"
```

```python
# Separate target and predictors
# Create both target variables (WHO source)
target_hale_who = analysis_complete['HALE_gap']
target_le_who = analysis_complete['LifeExpectancy_gap']

# Also create IHME HALE targets for comparison
# Get IHME HALE gap for the same countries (OECD)
# Use intersection of indices to handle Turkey (which is in WHO but not IHME)
common_countries_for_targets = analysis_complete.index.intersection(ihme_hale_oecd.index)
target_hale_ihme = ihme_hale_oecd.loc[common_countries_for_targets, 'Gap_HALE_Years']

# For backwards compatibility, keep original names pointing to WHO
target_hale = target_hale_who
target_le = target_le_who

# Keep all predictor columns including Male, Female, Mid, and Gap for counterfactual analysis
# Only drop the target variable columns
predictors = analysis_complete.drop(columns=[
    'HALE_gap', 'HALE_Years_Male', 'HALE_Years_Female',
    'LifeExpectancy_gap', 'LifeExpectancy_Years_Male', 'LifeExpectancy_Years_Female'
])

# Display final dataset info
pd.DataFrame({
    'Dataset': ['Complete Cases'],
    'Countries': [len(analysis_complete)],
    'Target_Variables_WHO': ['HALE_gap, LifeExpectancy_gap'],
    'Target_Variables_IHME': ['HALE_gap (available)'],
    'Number_of_Predictors': [len(predictors.columns)],
    'Predictor_Names': [', '.join(predictors.columns)]
})
```


## Descriptive Statistics

### HALE Gender Gap 


```python
# Summary statistics for target variable (HALE gap)
target_hale.describe()
```

```python
# Distribution of HALE gap across OECD countries
plt.hist(target_hale, bins=15, color='C3', edgecolor='white')
decorate(xlabel='HALE Gap (Female - Male, years)', 
         ylabel='Number of Countries',
         title='Distribution of HALE Gender Gap Across OECD Countries')
plt.savefig('figs/hale_gap_distribution.png', dpi=300, bbox_inches='tight')
```

```python
# Identify potential outliers using IQR method
Q1 = target_hale.quantile(0.25)
Q3 = target_hale.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = target_hale[(target_hale < lower_bound) | (target_hale > upper_bound)]
outliers_df = pd.DataFrame({
    'Country': outliers.index,
    'HALE_Gap': outliers.values
}).sort_values('HALE_Gap')

outliers_df if not outliers_df.empty else "No outliers detected using IQR method"
```

### Life Expectancy Gender Gap 


```python
# Summary statistics for target variable (Life Expectancy gap)
target_le.describe()
```

```python
# Distribution of Life Expectancy gap across OECD countries
plt.hist(target_le, bins=15, color='C0', edgecolor='white')
decorate(xlabel='Life Expectancy Gap (Female - Male, years)', 
         ylabel='Number of Countries',
         title='Distribution of Life Expectancy Gender Gap Across OECD Countries')
plt.savefig('figs/life_expectancy_gap_distribution.png', dpi=300, bbox_inches='tight')
```

```python
# Identify potential outliers using IQR method
Q1 = target_le.quantile(0.25)
Q3 = target_le.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = target_le[(target_le < lower_bound) | (target_le > upper_bound)]
outliers_df = pd.DataFrame({
    'Country': outliers.index,
    'LifeExpectancy_Gap': outliers.values
}).sort_values('LifeExpectancy_Gap')

outliers_df if not outliers_df.empty else "No outliers detected using IQR method"
```

### Comparison of HALE and Life Expectancy Gaps

```python
# Compare the two target variables
comparison_df = pd.DataFrame({
    'HALE_Gap': target_hale,
    'LifeExpectancy_Gap': target_le
})

comparison_df.describe()
```

```python
# Scatter plot comparing HALE gap vs Life Expectancy gap
plt.scatter(target_hale, target_le, color='C3', alpha=0.6)
decorate(xlabel='HALE Gap (Female - Male, years)', 
         ylabel='Life Expectancy Gap (Female - Male, years)',
         title='HALE Gap vs Life Expectancy Gap Across OECD Countries')
plt.savefig('figs/hale_vs_le_gap_comparison.png', dpi=300, bbox_inches='tight')
```

```python
# Correlation between the two target variables
correlation = target_hale.corr(target_le)
print(f"Correlation between HALE gap and Life Expectancy gap: {correlation:.3f}")
```


### Extreme Values and Country Rankings

```python
# Get list of indicators from indicator_datasets
indicator_names = list(indicator_datasets.keys())

# Create tables for each indicator showing top 5 and bottom 5 countries
indicator_extremes = {}

for indicator_name in indicator_names:
    # Get the dataframe directly from indicator_datasets
    df_gap = indicator_datasets[indicator_name]
    
    # Find Male and Female columns dynamically (they end with _Male or _Female)
    male_cols = [col for col in df_gap.columns if col.endswith('_Male')]
    female_cols = [col for col in df_gap.columns if col.endswith('_Female')]
    
    # Get the base name from the first male column (remove _Male suffix)
    if male_cols and female_cols:
        # Use the first matching pair
        male_col = male_cols[0]
        female_col = female_cols[0]
        # Verify they have the same base name
        base_name_male = male_col[:-5]  # Remove '_Male'
        base_name_female = female_col[:-7]  # Remove '_Female'
        if base_name_male == base_name_female:
            # Create summary for this indicator
            indicator_data = df_gap[[male_col, female_col]].copy()
            indicator_data['Country'] = df_gap['Country']
            
            # For male values
            male_sorted = indicator_data.sort_values(male_col, ascending=False)
            male_top5 = male_sorted.head(5)[['Country', male_col]].copy()
            male_bottom5 = male_sorted.tail(5)[['Country', male_col]].copy()
            
            # For female values
            female_sorted = indicator_data.sort_values(female_col, ascending=False)
            female_top5 = female_sorted.head(5)[['Country', female_col]].copy()
            female_bottom5 = female_sorted.tail(5)[['Country', female_col]].copy()
            
            indicator_extremes[indicator_name] = {
                'male_top5': male_top5,
                'male_bottom5': male_bottom5,
                'female_top5': female_top5,
                'female_bottom5': female_bottom5
            }

# Display results for a few key indicators
key_indicators = ['Alcohol', 'Homicide', 'Cardiovascular', 'Suicide']
for indicator in key_indicators:
    if indicator in indicator_extremes:
        print(f"\n{'='*60}")
        print(f"{indicator} - Extreme Values")
        print(f"{'='*60}")
        print(f"\nTop 5 Countries - Male Values:")
        display(indicator_extremes[indicator]['male_top5'])
        print(f"\nBottom 5 Countries - Male Values:")
        display(indicator_extremes[indicator]['male_bottom5'])
        print(f"\nTop 5 Countries - Female Values:")
        display(indicator_extremes[indicator]['female_top5'])
        print(f"\nBottom 5 Countries - Female Values:")
        display(indicator_extremes[indicator]['female_bottom5'])
```

#### For Gender Gaps: Largest and Smallest Gaps

```python
gap_extremes = {}

for indicator_name in indicator_names:
    # Get the dataframe directly from indicator_datasets
    df_gap = indicator_datasets[indicator_name]
    
    # Find columns dynamically
    gap_cols = [col for col in df_gap.columns if col.startswith('Gap_')]
    male_cols = [col for col in df_gap.columns if col.endswith('_Male')]
    female_cols = [col for col in df_gap.columns if col.endswith('_Female')]
    
    # Find matching columns (same base name)
    if gap_cols and male_cols and female_cols:
        # Get the base name from the gap column (remove 'Gap_' prefix)
        gap_col = gap_cols[0]
        base_name = gap_col[4:]  # Remove 'Gap_' prefix
        
        # Find matching male and female columns
        male_col = f'{base_name}_Male'
        female_col = f'{base_name}_Female'
        
        if male_col in df_gap.columns and female_col in df_gap.columns:
            # Create summary with country names
            gap_data = df_gap[[male_col, female_col, gap_col]].copy()
            gap_data['Country'] = df_gap['Country']
            
            # Sort by gap (largest positive gaps first)
            # Note: Gap is computed as Male - Female, so positive means males have higher rates
            gap_sorted = gap_data.sort_values(gap_col, ascending=False)
            
            gap_top5 = gap_sorted.head(5).copy()
            gap_bottom5 = gap_sorted.tail(5).copy()
            
            gap_extremes[indicator_name] = {
                'top5': gap_top5,
                'bottom5': gap_bottom5
            }

# Display results for key indicators
for indicator in key_indicators:
    if indicator in gap_extremes:
        print(f"\n{'='*60}")
        print(f"{indicator} - Gender Gap Extremes (Male - Female)")
        print(f"{'='*60}")
        gap_info = gap_extremes[indicator]
        # Get column names dynamically from the DataFrame
        top5_df = gap_info['top5']
        # Find Male, Female, and Gap columns
        male_col = [col for col in top5_df.columns if col.endswith('_Male')][0] if any(col.endswith('_Male') for col in top5_df.columns) else None
        female_col = [col for col in top5_df.columns if col.endswith('_Female')][0] if any(col.endswith('_Female') for col in top5_df.columns) else None
        gap_col = [col for col in top5_df.columns if col.startswith('Gap_')][0] if any(col.startswith('Gap_') for col in top5_df.columns) else None
        
        cols_to_show = ['Country']
        if male_col:
            cols_to_show.append(male_col)
        if female_col:
            cols_to_show.append(female_col)
        if gap_col:
            cols_to_show.append(gap_col)
        
        print(f"\nTop 5 Countries - Largest Gaps (Male > Female):")
        display(gap_info['top5'][cols_to_show])
        print(f"\nBottom 5 Countries - Smallest Gaps (Female > Male):")
        display(gap_info['bottom5'][cols_to_show])
```

#### For HALE Gap: All Countries Ranked

```python
# Create ranked table of all countries by HALE gap
hale_ranked = analysis_complete[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].copy()
hale_ranked = hale_ranked.sort_values('HALE_gap', ascending=False).reset_index()
hale_ranked['Rank'] = range(1, len(hale_ranked) + 1)
# Rename: Country (code) -> Code, add Country (name)
hale_ranked = hale_ranked.rename(columns={'Country': 'Code'})
hale_ranked['Country'] = hale_ranked['Code'].map(code_to_who_country)

# Create output version without Rank column (Rank kept internally for comparison table)
hale_ranked_output = hale_ranked[['Country', 'HALE_Years_Male', 
                                   'HALE_Years_Female', 'HALE_gap']].copy()

print("All Countries Ranked by HALE Gap (Female - Male)")
print("="*80)
hale_ranked_output
```

```python
# Write HALE gap by country table to HTML (without Rank column)
write_html_table(hale_ranked_output, f"tables/hale_gap_by_country_{cutoff_year}.html")
```

```python
# Summary statistics for HALE gap
print("\nHALE Gap Summary Statistics:")
print("="*50)
print(f"Mean HALE Gap: {hale_ranked['HALE_gap'].mean():.2f} years")
print(f"Median HALE Gap: {hale_ranked['HALE_gap'].median():.2f} years")
print(f"Standard Deviation: {hale_ranked['HALE_gap'].std():.2f} years")
print(f"Range: {hale_ranked['HALE_gap'].min():.2f} to {hale_ranked['HALE_gap'].max():.2f} years")
print(f"\nCountries with Largest HALE Gap (Top 5):")
hale_ranked_output.head(5)
print(f"\nCountries with Smallest HALE Gap (Bottom 5):")
hale_ranked_output.tail(5)
```

#### For Life Expectancy Gap: All Countries Ranked

```python
# Create ranked table of all countries by Life Expectancy gap
le_ranked = analysis_complete[['LifeExpectancy_Years_Male', 'LifeExpectancy_Years_Female', 'LifeExpectancy_gap']].copy()
le_ranked = le_ranked.sort_values('LifeExpectancy_gap', ascending=False).reset_index()
le_ranked['Rank'] = range(1, len(le_ranked) + 1)
# Rename: Country (code) -> Code, add Country (name)
le_ranked = le_ranked.rename(columns={'Country': 'Code'})
le_ranked['Country'] = le_ranked['Code'].map(code_to_who_country)

# Create output version without Rank column (Rank kept internally for comparison table)
le_ranked_output = le_ranked[['Country', 'LifeExpectancy_Years_Male', 
                              'LifeExpectancy_Years_Female', 'LifeExpectancy_gap']].copy()

print("All Countries Ranked by Life Expectancy Gap (Female - Male)")
print("="*80)
le_ranked_output
```

```python
# Write Life Expectancy gap by country table to HTML (without Rank column)
write_html_table(le_ranked_output, f"tables/le_gap_by_country_{cutoff_year}.html")
```

```python
# Summary statistics for Life Expectancy gap
print("\nLife Expectancy Gap Summary Statistics:")
print("="*50)
print(f"Mean Life Expectancy Gap: {le_ranked['LifeExpectancy_gap'].mean():.2f} years")
print(f"Median Life Expectancy Gap: {le_ranked['LifeExpectancy_gap'].median():.2f} years")
print(f"Standard Deviation: {le_ranked['LifeExpectancy_gap'].std():.2f} years")
print(f"Range: {le_ranked['LifeExpectancy_gap'].min():.2f} to {le_ranked['LifeExpectancy_gap'].max():.2f} years")
print(f"\nCountries with Largest Life Expectancy Gap (Top 5):")
le_ranked_output.head(5)
print(f"\nCountries with Smallest Life Expectancy Gap (Bottom 5):")
le_ranked_output.tail(5)
```

### Summary Statistics by Indicator

```python
# Create summary table with rate and gap statistics for each indicator
def compute_indicator_stats(indicator_name, df_gap):
    """Compute statistics for a single indicator."""
    # Get OECD countries only for consistency
    df_oecd = get_oecd(df_gap)
    
    # Find Mid and Gap columns dynamically
    mid_cols = [col for col in df_gap.columns if col.startswith('Mid_')]
    gap_cols = [col for col in df_gap.columns if col.startswith('Gap_')]
    
    # Handle normal case: indicators with both Mid and Gap columns
    if mid_cols and gap_cols:
        mid_col = mid_cols[0]
        gap_col = gap_cols[0]
        
        # Extract midpoint and gap values
        midpoints = df_oecd[mid_col].dropna()
        gaps = df_oecd[gap_col].dropna()
        
        if len(midpoints) > 0 and len(gaps) > 0:
            return {
                'Indicator': indicator_name,
                'Median Rate': midpoints.median(),
                'Min Rate': midpoints.min(),
                'Max Rate': midpoints.max(),
                'Median Gap': gaps.median(),
                'Min Gap': gaps.min(),
                'Max Gap': gaps.max()
            }
    
    # Handle special case: MaternalMortality (female-only, no Gap/Mid columns)
    # Use the Female value as both midpoint and gap
    elif indicator_name == 'MaternalMortality':
        female_cols = [col for col in df_gap.columns if col.endswith('_Female')]
        if female_cols:
            female_col = female_cols[0]
            values = df_oecd[female_col].dropna()
            
            if len(values) > 0:
                return {
                    'Indicator': indicator_name,
                    'Median Rate': values.median(),
                    'Min Rate': values.min(),
                    'Max Rate': values.max(),
                    'Median Gap': -values.median(),
                    'Min Gap': -values.min(),
                    'Max Gap': -values.max()
                }
    
    return None
```

```python
# Process predictor indicators
predictor_summary = []
for indicator_name, df_gap in indicator_datasets.items():
    stats = compute_indicator_stats(indicator_name, df_gap)
    if stats:
        predictor_summary.append(stats)

# Process target variables
target_summary = []
target_indicators = {
    'HALE': hale_gap,
    'Life Expectancy': le_gap
}
for indicator_name, df_gap in target_indicators.items():
    stats = compute_indicator_stats(indicator_name, df_gap)
    if stats:
        target_summary.append(stats)
```

```python
# Create DataFrames (keep Indicator as a column, not index)
predictor_df = pd.DataFrame(predictor_summary)
target_df = pd.DataFrame(target_summary)

# Split predictor table into rates and gaps
predictor_rates = predictor_df[['Indicator', 'Median Rate', 'Min Rate', 'Max Rate']].copy()
predictor_gaps = predictor_df[['Indicator', 'Median Gap', 'Min Gap', 'Max Gap']].copy()

# Calculate correlations with target variables
# For rates: use Mid_ columns, for gaps: use Gap_ columns
# Special case: MaternalMortality uses Female column for both
predictor_rates['Corr HALE'] = np.nan
predictor_rates['Corr LE'] = np.nan
predictor_gaps['Corr HALE'] = np.nan
predictor_gaps['Corr LE'] = np.nan

for idx, indicator in enumerate(predictor_rates['Indicator']):
    if indicator == 'MaternalMortality':
        # MaternalMortality: use Female column for both rates and gaps (if present)
        female_col = 'MaternalMortality_Female'
        if female_col in predictors.columns:
            predictor_rates.loc[idx, 'Corr HALE'] = predictors[female_col].corr(target_hale)
            predictor_rates.loc[idx, 'Corr LE'] = predictors[female_col].corr(target_le)
            predictor_gaps.loc[idx, 'Corr HALE'] = predictors[female_col].corr(target_hale)
            predictor_gaps.loc[idx, 'Corr LE'] = predictors[female_col].corr(target_le)
        else:
            # MaternalMortality not in predictors, skip correlation calculation
            predictor_rates.loc[idx, 'Corr HALE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE'] = np.nan
            predictor_gaps.loc[idx, 'Corr HALE'] = np.nan
            predictor_gaps.loc[idx, 'Corr LE'] = np.nan
    else:
        # Find the corresponding Mid_ and Gap_ columns in predictors DataFrame
        mid_col = f'Mid_{indicator}'
        gap_col = f'Gap_{indicator}'
        
        # Calculate correlations for rates (using Mid_ columns)
        if mid_col in predictors.columns:
            predictor_rates.loc[idx, 'Corr HALE'] = predictors[mid_col].corr(target_hale)
            predictor_rates.loc[idx, 'Corr LE'] = predictors[mid_col].corr(target_le)
        else:
            predictor_rates.loc[idx, 'Corr HALE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE'] = np.nan
        
        # Calculate correlations for gaps (using Gap_ columns)
        if gap_col in predictors.columns:
            predictor_gaps.loc[idx, 'Corr HALE'] = predictors[gap_col].corr(target_hale)
            predictor_gaps.loc[idx, 'Corr LE'] = predictors[gap_col].corr(target_le)
        else:
            predictor_gaps.loc[idx, 'Corr HALE'] = np.nan
            predictor_gaps.loc[idx, 'Corr LE'] = np.nan

# Split target table into rates and gaps, reverse gap signs, and adjust column names
target_rates = target_df[['Indicator', 'Median Rate', 'Min Rate', 'Max Rate']].copy()
target_rates.columns = ['Indicator', 'Median', 'Min', 'Max']
target_gaps = target_df[['Indicator', 'Median Gap', 'Min Gap', 'Max Gap']].copy()
# Reverse sign of gaps (from Male - Female to Female - Male)
target_gaps['Median Gap'] = -target_gaps['Median Gap']
target_gaps['Min Gap'] = -target_gaps['Min Gap']
target_gaps['Max Gap'] = -target_gaps['Max Gap']
# After negation, min and max are swapped, so swap the column values
target_gaps['Min Gap'], target_gaps['Max Gap'] = target_gaps['Max Gap'], target_gaps['Min Gap']
target_gaps.columns = ['Indicator', 'Median Gap', 'Min Gap', 'Max Gap']
```

```python
print("Predictor Indicators - Rates:")
predictor_rates = predictor_rates.sort_values(by='Median Rate', ascending=False).reset_index(drop=True)
predictor_rates
```

```python
print("Predictor Indicators - Gaps:")
predictor_gaps = predictor_gaps.sort_values(by='Median Gap', ascending=False).reset_index(drop=True)
predictor_gaps
```

```python
print("Target Variables - Rates:")
target_rates.sort_values(by='Median', ascending=False).reset_index(drop=True)
```

```python
print("Target Variables - Gaps:")
target_gaps
```

```python

```

```python
write_html_table(predictor_rates, f"tables/predictor_rates_{cutoff_year}.html")
write_html_table(predictor_gaps,  f"tables/predictor_gaps_{cutoff_year}.html")

write_html_table(target_rates,    f"tables/target_rates_{cutoff_year}.html")
write_html_table(target_gaps,     f"tables/target_gaps_{cutoff_year}.html")
```

```python
# Create table showing correlation between Rate (Mid) and Gap for each indicator
rate_gap_correlations = []

for indicator in predictor_rates['Indicator']:
    # Skip MaternalMortality - it doesn't have a Gap column (female-only)
    if indicator == 'MaternalMortality':
        continue
    
    # Find the corresponding Mid_ and Gap_ columns in predictors DataFrame
    rate_col = f'Mid_{indicator}'
    gap_col = f'Gap_{indicator}'
    
    # Calculate correlation between rate and gap
    if rate_col in predictors.columns and gap_col in predictors.columns:
        corr = predictors[rate_col].corr(predictors[gap_col])
        rate_gap_correlations.append({
            'Indicator': indicator,
            'Correlation': corr
        })

# Create DataFrame and format (keep Indicator as a column)
rate_gap_corr_df = pd.DataFrame(rate_gap_correlations)

# Sort by correlation (descending)
rate_gap_corr_df = rate_gap_corr_df.sort_values('Correlation', ascending=False).reset_index(drop=True)
```

```python
write_html_table(rate_gap_corr_df, f"tables/rate_gap_correlation_{cutoff_year}.html")
```

```python
# Create table showing top 10 correlations between rates (Mid columns)
# Get all Mid_ columns
mid_cols = [col for col in predictors.columns if col.startswith('Mid_')]

# Calculate correlation matrix for rates
rates_corr_matrix = predictors[mid_cols].corr()

# Extract upper triangle (excluding diagonal) and convert to list of pairs
rates_corr_pairs = []
for i in range(len(rates_corr_matrix.columns)):
    for j in range(i+1, len(rates_corr_matrix.columns)):
        indicator1 = rates_corr_matrix.columns[i].replace('Mid_', '')
        indicator2 = rates_corr_matrix.columns[j].replace('Mid_', '')
        corr_val = rates_corr_matrix.iloc[i, j]
        rates_corr_pairs.append({
            'Rate 1': indicator1,
            'Rate 2': indicator2,
            'Correlation': corr_val
        })

# Create DataFrame and sort by absolute correlation
rates_corr_df = pd.DataFrame(rates_corr_pairs)
rates_corr_df['Abs Correlation'] = rates_corr_df['Correlation'].abs()
rates_corr_df = rates_corr_df.sort_values('Abs Correlation', ascending=False).head(10)

# Drop the absolute value column
rates_corr_df = rates_corr_df[['Rate 1', 'Rate 2', 'Correlation']].reset_index(drop=True)
```

```python
write_html_table(rates_corr_df,     f"tables/rate_rate_correlation_top10_{cutoff_year}.html")
```

```python
# Create table showing top 10 correlations between gaps (Gap columns)
# Get all Gap_ columns (excluding MaternalMortality which doesn't have a Gap column)
gap_cols = [col for col in predictors.columns if col.startswith('Gap_')]

# Calculate correlation matrix for gaps
gaps_corr_matrix = predictors[gap_cols].corr()

# Extract upper triangle (excluding diagonal) and convert to list of pairs
gaps_corr_pairs = []
for i in range(len(gaps_corr_matrix.columns)):
    for j in range(i+1, len(gaps_corr_matrix.columns)):
        indicator1 = gaps_corr_matrix.columns[i].replace('Gap_', '')
        indicator2 = gaps_corr_matrix.columns[j].replace('Gap_', '')
        corr_val = gaps_corr_matrix.iloc[i, j]
        gaps_corr_pairs.append({
            'Gap 1': indicator1,
            'Gap 2': indicator2,
            'Correlation': corr_val
        })

# Create DataFrame and sort by absolute correlation
gaps_corr_df = pd.DataFrame(gaps_corr_pairs)
gaps_corr_df['Abs Correlation'] = gaps_corr_df['Correlation'].abs()
gaps_corr_df = gaps_corr_df.sort_values('Abs Correlation', ascending=False).head(10)

# Drop the absolute value column
gaps_corr_df = gaps_corr_df[['Gap 1', 'Gap 2', 'Correlation']].reset_index(drop=True)
```

```python
write_html_table(gaps_corr_df,     f"tables/gap_gap_correlation_top10_{cutoff_year}.html")
```

## OWID Life Expectancy Data

**Purpose**: Explore Our World in Data (OWID) Life Expectancy data as extended temporal coverage alternative to WHO LE. OWID combines Human Mortality Database (pre-1950) and UN World Population Prospects (1950-2023) to provide data through 2023 (vs 2021 for WHO).

**Data Source**: Our World in Data (https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex)

**Key Advantages**:
- Extended temporal coverage through 2023 (+2 years beyond WHO)
- 100% complete data for all OECD countries
- High-quality sources (HMD + UN WPP)

```python
# Load OWID Life Expectancy data
owid_le_file = '../data/owid_life_expectancy_by_sex.csv'
owid_le_raw = pd.read_csv(owid_le_file)

log_and_print("\n" + "="*80)
log_and_print("OWID Life Expectancy Data Structure")
log_and_print("="*80)
log_and_print(f"Shape: {owid_le_raw.shape}")
log_and_print(f"Columns: {list(owid_le_raw.columns)}")
log_and_print(f"Years: {owid_le_raw['Year'].min()} - {owid_le_raw['Year'].max()}")
log_and_print(f"Entities: {owid_le_raw['Entity'].nunique()}")
log_and_print(f"With country codes: {owid_le_raw['Code'].notna().sum()} rows")
```

```python
owid_le_raw.head(10)
```

### Convert OWID LE to Model-Compatible Format

Convert OWID format to match the structure expected by `bayesian_model.md`, filtering to OECD countries and 2000-2023.

```python
def convert_owid_le_to_temporal_format(df, min_year=2000, max_year=2023):
    """
    Convert OWID Life Expectancy data to temporal format for Bayesian model.
    
    OWID format: Entity, Code, Year, life_expectancy__sex_female__age_0, life_expectancy__sex_male__age_0
    Target format: Code, Year, Male, Female (with LE values)
    
    Parameters
    ----------
    df : pd.DataFrame
        OWID LE data
    min_year : int
        Minimum year to include (default: 2000)
    max_year : int
        Maximum year to include (default: 2023)
        
    Returns
    -------
    df_temporal : pd.DataFrame
        Long-format DataFrame with Code, Year, Sex, LifeExpectancy_Years
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

owid_le_temporal = convert_owid_le_to_temporal_format(owid_le_raw, min_year=2000, max_year=2023)

log_and_print("\n" + "="*80)
log_and_print("OWID LE Temporal Format (for Bayesian Model)")
log_and_print("="*80)
log_and_print(f"Shape: {owid_le_temporal.shape}")
log_and_print(f"Years: {owid_le_temporal['Year'].min():.0f} - {owid_le_temporal['Year'].max():.0f}")
log_and_print(f"Countries: {owid_le_temporal['Code'].nunique()}")
log_and_print(f"OECD codes: {sorted(owid_le_temporal['Code'].unique())}")
log_and_print(f"Sex categories: {owid_le_temporal['Sex'].unique()}")
log_and_print(f"Data completeness: {owid_le_temporal['LifeExpectancy_Years'].notna().sum()} / {len(owid_le_temporal)} ({100*owid_le_temporal['LifeExpectancy_Years'].notna().mean():.1f}%)")
```

```python
owid_le_temporal.head(10)
```

```python
# Compute gender gap statistics for OWID LE
from utils import compute_gender_gap

owid_le_gap = compute_gender_gap(owid_le_temporal, 'LifeExpectancy_Years', sexes=['Male', 'Female'])
# Calculate gap as Female - Male (positive gap means women live longer)
owid_le_gap['LE_gap'] = -owid_le_gap['Gap_LifeExpectancy_Years']

log_and_print("\n" + "="*80)
log_and_print("OWID LE Gender Gap Statistics (2000-2023)")
log_and_print("="*80)
log_and_print(f"Shape: {owid_le_gap.shape}")
log_and_print(f"Mean gap (Female - Male): {owid_le_gap['LE_gap'].mean():.2f} years")
log_and_print(f"Median gap: {owid_le_gap['LE_gap'].median():.2f} years")
log_and_print(f"Std gap: {owid_le_gap['LE_gap'].std():.2f} years")
log_and_print(f"Range: {owid_le_gap['LE_gap'].min():.2f} to {owid_le_gap['LE_gap'].max():.2f} years")
```

```python
# Compare WHO vs OWID LE for overlapping years (2000-2021)
# Use the already-loaded 'le' dataframe from earlier in the notebook
# Note: 'le' has already been processed with Sex mapping to 'Male', 'Female', 'Both'

# Prepare WHO data for comparison (using already-loaded 'le' dataframe)
le_who_compare = le[
    (le['Year'] >= 2000) & 
    (le['Year'] <= 2021) & 
    (le['Sex'].isin(['Male', 'Female']))
][['Code', 'Year', 'Sex', 'LifeExpectancy_Years']].copy()
le_who_compare = le_who_compare.rename(columns={'LifeExpectancy_Years': 'LE_WHO'})

# Prepare OWID data for comparison
owid_le_compare = owid_le_temporal[
    (owid_le_temporal['Year'] <= 2021)
][['Code', 'Year', 'Sex', 'LifeExpectancy_Years']].copy()
owid_le_compare = owid_le_compare.rename(columns={'LifeExpectancy_Years': 'LE_OWID'})

# Merge for comparison
le_comparison = owid_le_compare.merge(
    le_who_compare,
    on=['Code', 'Year', 'Sex'],
    how='inner'
)

# Compute correlation and differences
correlation = le_comparison[['LE_WHO', 'LE_OWID']].corr().iloc[0, 1]
diff = le_comparison['LE_OWID'] - le_comparison['LE_WHO']

log_and_print("\n" + "="*80)
log_and_print("WHO vs OWID LE Comparison (2000-2021)")
log_and_print("="*80)
log_and_print(f"Overlapping observations: {len(le_comparison)}")
log_and_print(f"Correlation: {correlation:.6f}")
log_and_print(f"Mean difference (OWID - WHO): {diff.mean():.4f} years")
log_and_print(f"Median difference: {diff.median():.4f} years")
log_and_print(f"Std difference: {diff.std():.4f} years")
log_and_print(f"Max abs difference: {diff.abs().max():.4f} years")
log_and_print(f"\nConclusion: {'High agreement' if correlation > 0.999 else 'Moderate agreement'} between WHO and OWID")
```

## Prepare IHME HALE for Bayesian Model

Convert IHME HALE to temporal format compatible with `bayesian_model.md`, filtering to OECD countries and 2000-2023.

```python
def convert_ihme_hale_to_temporal_format(df, min_year=2000, max_year=2023):
    """
    Convert IHME HALE data to temporal format for Bayesian model.
    
    IHME format: location_name, year, sex_name, val, upper, lower
    Target format: Code, Year, Sex, HALE_Years
    
    Parameters
    ----------
    df : pd.DataFrame
        IHME HALE raw data
    min_year : int
        Minimum year to include (default: 2000)
    max_year : int
        Maximum year to include (default: 2023)
        
    Returns
    -------
    df_temporal : pd.DataFrame
        Long-format DataFrame with Code, Year, Sex, HALE_Years
    """
    # Create reverse mapping from country name to code
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    
    # Map IHME country names that differ from WHO names
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States',
        'Türkiye': 'Turkey'
    }
    
    # Map sex values
    sex_mapping_ihme = {'Male': 'Male', 'Female': 'Female', 'Both': 'Both'}
    
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
    df['Sex'] = df['sex_name'].map(sex_mapping_ihme)
    
    # Rename columns to match expected format
    df = df.rename(columns={
        'year': 'Year',
        'val': 'HALE_Years'
    })
    
    # Select and reorder columns
    df_temporal = df[['Code', 'Year', 'Sex', 'HALE_Years']].copy()
    
    # Sort by country, sex, year
    df_temporal = df_temporal.sort_values(['Code', 'Sex', 'Year']).reset_index(drop=True)
    
    return df_temporal

ihme_hale_temporal = convert_ihme_hale_to_temporal_format(ihme_hale_raw, min_year=2000, max_year=2023)

log_and_print("\n" + "="*80)
log_and_print("IHME HALE Temporal Format (for Bayesian Model)")
log_and_print("="*80)
log_and_print(f"Shape: {ihme_hale_temporal.shape}")
log_and_print(f"Years: {ihme_hale_temporal['Year'].min():.0f} - {ihme_hale_temporal['Year'].max():.0f}")
log_and_print(f"Countries: {ihme_hale_temporal['Code'].nunique()}")
log_and_print(f"OECD codes: {sorted(ihme_hale_temporal['Code'].unique())}")
log_and_print(f"Sex categories: {ihme_hale_temporal['Sex'].unique()}")
log_and_print(f"Data completeness: {ihme_hale_temporal['HALE_Years'].notna().sum()} / {len(ihme_hale_temporal)} ({100*ihme_hale_temporal['HALE_Years'].notna().mean():.1f}%)")
```

```python
ihme_hale_temporal.head(10)
```

```python
# Compute gender gap statistics for IHME HALE
ihme_hale_gap = compute_gender_gap(ihme_hale_temporal, 'HALE_Years', sexes=['Male', 'Female'])
# Calculate gap as Female - Male (positive gap means women live longer)
ihme_hale_gap['HALE_gap'] = -ihme_hale_gap['Gap_HALE_Years']

log_and_print("\n" + "="*80)
log_and_print("IHME HALE Gender Gap Statistics (2000-2023)")
log_and_print("="*80)
log_and_print(f"Shape: {ihme_hale_gap.shape}")
log_and_print(f"Mean gap (Female - Male): {ihme_hale_gap['HALE_gap'].mean():.2f} years")
log_and_print(f"Median gap: {ihme_hale_gap['HALE_gap'].median():.2f} years")
log_and_print(f"Std gap: {ihme_hale_gap['HALE_gap'].std():.2f} years")
log_and_print(f"Range: {ihme_hale_gap['HALE_gap'].min():.2f} to {ihme_hale_gap['HALE_gap'].max():.2f} years")
```

## Create Panel Data for Bayesian Model

This section creates a panel dataset with temporal data for all countries and years, which is used by both `bayesian_model.md` (Python) and `bayesian_model.Rmd` (R).

### Configuration

```python
# Panel data configuration
PANEL_CUTOFF_YEAR = 2023  # Include COVID years for panel analysis
INCLUDE_COVID_DATA = True
COUNTRIES_TO_EXCLUDE = ['TUR']  # Turkey not in some datasets
```

### Helper Functions

```python
def compute_temporal_gaps(df, value_col, sexes=['Male', 'Female']):
    """
    Compute gender gaps for all years (not just most recent).
    Wrapper around compute_gender_gap that preserves temporal structure.
    """
    return compute_gender_gap(df, value_col, sexes)


def load_ihme_indicator_temporal(base_filename, value_col_name, indicator_code, indicator_name, max_year=2023):
    """
    Load IHME indicator data and compute temporal gaps for all years.
    
    Parameters
    ----------
    base_filename : str
        Base filename without path, sex suffix, or extension
    value_col_name : str
        Name of the value column
    indicator_code : str
        Indicator code
    indicator_name : str
        Human-readable indicator name
    max_year : int
        Maximum year to include
        
    Returns
    -------
    df_temporal : pandas.DataFrame
        DataFrame with temporal gaps computed for all years
    """
    from utils import load_ihme_indicator
    
    filename_male = f'../data/{base_filename}_male.csv'
    filename_female = f'../data/{base_filename}_female.csv'
    df = load_ihme_indicator(
        filename_male, filename_female,
        value_col_name=value_col_name,
        indicator_code=indicator_code,
        indicator_name=indicator_name,
        min_year=2000,
        max_year=max_year
    )
    df = df.rename(columns=column_name_mapping)
    col = column_name_mapping.get(value_col_name, value_col_name)
    df_temporal = compute_temporal_gaps(df, col, sexes=['Male', 'Female'])
    return df_temporal


def merge_predictor(df_temporal, indicator_name):
    """Merge a predictor indicator into the panel dataset."""
    cols_to_merge = ['Code', 'Year']
    mid_col = [c for c in df_temporal.columns if c.startswith('Mid_')]
    gap_col = [c for c in df_temporal.columns if c.startswith('Gap_')]
    cols_to_merge.extend(mid_col)
    cols_to_merge.extend(gap_col)
    
    df_subset = df_temporal[cols_to_merge].copy()
    df_subset = df_subset.rename(columns={'Code': 'country'})
    return df_subset
```

### Load Life Expectancy Temporal Data

```python
# Compute LE gaps for all years (temporal structure)
le_temporal = compute_temporal_gaps(owid_le_temporal, 'LifeExpectancy_Years', sexes=['Male', 'Female'])
# Gap is Male - Female, negate to get Female - Male (positive = women live longer)
le_temporal['LE_gap'] = -le_temporal['Gap_LifeExpectancy_Years']

# Filter to OECD and cutoff year
le_temporal = le_temporal[le_temporal['Code'].isin(oecd_codes)].copy()
le_temporal = le_temporal[le_temporal['Year'] <= PANEL_CUTOFF_YEAR].copy()

print(f"LE temporal data: {le_temporal.shape}")
print(f"Years: {le_temporal['Year'].min():.0f} - {le_temporal['Year'].max():.0f}")
print(f"Countries: {le_temporal['Code'].nunique()}")
```

### Load IHME Predictor Indicators (Temporal)

```python
# Load all IHME indicators with temporal structure
print("Loading IHME indicators for panel data...")

alcohol_temporal = load_ihme_indicator_temporal(
    'ihme_alcohol_use_disorders_deaths', 'AlcoholUseDisordersDeathRate',
    'IHME_ALCOHOL_USE_DISORDERS', 'Alcohol use disorders',
    max_year=PANEL_CUTOFF_YEAR)

self_harm_temporal = load_ihme_indicator_temporal(
    'ihme_self_harm_deaths', 'SelfHarmDeathRate',
    'IHME_SELF_HARM', 'Self-harm (suicide)',
    max_year=PANEL_CUTOFF_YEAR)

interpersonal_violence_temporal = load_ihme_indicator_temporal(
    'ihme_interpersonal_violence_deaths', 'InterpersonalViolenceDeathRate',
    'IHME_INTERPERSONAL_VIOLENCE', 'Interpersonal violence (homicide)',
    max_year=PANEL_CUTOFF_YEAR)

road_injuries_temporal = load_ihme_indicator_temporal(
    'ihme_road_injuries_deaths', 'RoadInjuriesDeathRate',
    'IHME_ROAD_INJURIES', 'Road injuries',
    max_year=PANEL_CUTOFF_YEAR)

cardiovascular_temporal = load_ihme_indicator_temporal(
    'ihme_cardiovascular_deaths', 'CardioDeathRate',
    'IHME_CARDIOVASCULAR', 'Cardiovascular diseases',
    max_year=PANEL_CUTOFF_YEAR)

diabetes_temporal = load_ihme_indicator_temporal(
    'ihme_diabetes_deaths', 'DiabetesDeathRate',
    'IHME_DIABETES_TYPE2', 'Diabetes mellitus',
    max_year=PANEL_CUTOFF_YEAR)

neoplasms_temporal = load_ihme_indicator_temporal(
    'ihme_neoplasms_deaths', 'NeoplasmsDeathRate',
    'IHME_NEOPLASMS', 'Neoplasms (cancer)',
    max_year=PANEL_CUTOFF_YEAR)

chronic_respiratory_temporal = load_ihme_indicator_temporal(
    'ihme_chronic_respiratory_deaths', 'ChronicRespiratoryDeathRate',
    'IHME_CHRONIC_RESPIRATORY', 'Chronic respiratory diseases',
    max_year=PANEL_CUTOFF_YEAR)

liver_disease_temporal = load_ihme_indicator_temporal(
    'ihme_liver_disease_deaths', 'LiverDiseaseDeathRate',
    'IHME_LIVER_DISEASE', 'Liver disease',
    max_year=PANEL_CUTOFF_YEAR)

unintentional_injuries_temporal = load_ihme_indicator_temporal(
    'ihme_unintentional_injuries_deaths', 'UnintentionalInjuriesDeathRate',
    'IHME_UNINTENTIONAL_INJURIES', 'Unintentional injuries',
    max_year=PANEL_CUTOFF_YEAR)

drug_disorders_temporal = load_ihme_indicator_temporal(
    'ihme_drug_disorder_deaths', 'DrugDisorderDeathRate',
    'IHME_DRUG_DISORDERS', 'Drug use disorders',
    max_year=PANEL_CUTOFF_YEAR)

if INCLUDE_COVID_DATA:
    covid_temporal = load_ihme_indicator_temporal(
        'ihme_covid19_deaths', 'COVID19DeathRate',
        'IHME_COVID19', 'COVID-19',
        max_year=PANEL_CUTOFF_YEAR)

print("All IHME indicators loaded.")
```

### Create Panel Dataset

```python
# List of predictors to merge
predictors_to_merge = [
    (alcohol_temporal, 'Alcohol'),
    (self_harm_temporal, 'SelfHarm'),
    (interpersonal_violence_temporal, 'InterpersonalViolence'),
    (road_injuries_temporal, 'RoadInjuries'),
    (cardiovascular_temporal, 'Cardiovascular'),
    (diabetes_temporal, 'Diabetes'),
    (neoplasms_temporal, 'Neoplasms'),
    (chronic_respiratory_temporal, 'ChronicRespiratory'),
    (liver_disease_temporal, 'LiverDisease'),
    (unintentional_injuries_temporal, 'UnintentionalInjuries'),
    (drug_disorders_temporal, 'DrugDisorder'),
]

if INCLUDE_COVID_DATA:
    predictors_to_merge.append((covid_temporal, 'COVID19'))

# Start with LE gap as base
panel_le = le_temporal[['Code', 'Year', 'LE_gap']].copy()
panel_le = panel_le.rename(columns={'Code': 'country'})

# Merge all predictors
for df_temp, name in predictors_to_merge:
    df_merge = merge_predictor(df_temp, name)
    panel_le = panel_le.merge(df_merge, on=['country', 'Year'], how='left')
    print(f"Merged {name}: panel now has {panel_le.shape[1]} columns")

# Filter to OECD countries
panel_le = panel_le[panel_le['country'].isin(oecd_codes)].copy()
print(f"\nAfter OECD filter: {panel_le.shape}")

# Exclude countries
if COUNTRIES_TO_EXCLUDE:
    n_before = len(panel_le)
    panel_le = panel_le[~panel_le['country'].isin(COUNTRIES_TO_EXCLUDE)].copy()
    print(f"After excluding {COUNTRIES_TO_EXCLUDE}: {panel_le.shape} (removed {n_before - len(panel_le)} rows)")

# Drop rows with missing LE_gap
panel_le = panel_le.dropna(subset=['LE_gap']).copy()

# Sort by country and year
panel_le = panel_le.sort_values(['country', 'Year']).reset_index(drop=True)

print(f"\nFinal panel: {panel_le.shape}")
print(f"Countries: {panel_le['country'].nunique()}")
print(f"Years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
print(f"Missing values: {panel_le.isnull().sum().sum()}")
```

```python
panel_le.head()
```

### Save Panel Data

```python
# Save panel data for bayesian_model notebooks
# HDF5 for Python, CSV for R

# Save to HDF5
panel_hdf_file = 'interim/panel_le.h5'
panel_le.to_hdf(panel_hdf_file, key='panel', mode='w')
print(f"Panel saved to HDF5: {panel_hdf_file}")

# Save to CSV
panel_csv_file = 'interim/panel_le.csv'
panel_le.to_csv(panel_csv_file, index=False)
print(f"Panel saved to CSV: {panel_csv_file}")

log_and_print("\n" + "="*80)
log_and_print("PANEL DATA SAVED")
log_and_print("="*80)
log_and_print(f"HDF5: {panel_hdf_file}")
log_and_print(f"CSV: {panel_csv_file}")
log_and_print(f"Shape: {panel_le.shape}")
log_and_print(f"Countries: {panel_le['country'].nunique()}")
log_and_print(f"Years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
log_and_print("="*80)
```

```python
from utils import beep

beep()
```

```python
# Close log file
log_and_print("\n" + "="*80)
log_and_print(f"Notebook completed: {pd.Timestamp.now()}")
log_and_print("="*80)
log_file.close()
print(f"\nLog file closed: {log_path}")
```
