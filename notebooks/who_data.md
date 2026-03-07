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

# WHO Data Analysis

This notebook loads and analyzes WHO HALE and Life Expectancy data, comparing them to IHME and OWID alternatives to inform data source decisions for the Bayesian models.

**Purpose**: Exploratory analysis and validation of WHO data sources. The main pipeline (`process.md`) uses IHME HALE and OWID LE for the panel; this notebook documents the rationale and validates agreement across sources.

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
    column_name_mapping, oecd_codes,
    log_and_print, set_log_file,
    convert_ihme_hale_to_who_format, convert_owid_le_to_temporal_format
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
log_path = f'logs/who_data_{cutoff_year}.txt'
log_file = open(log_path, 'w')

log_file.write("WHO Data Analysis Log\n")
log_file.write("=" * 80 + "\n")
log_file.write(f"Notebook: who_data.md\n")
log_file.write(f"Cutoff Year: {cutoff_year}\n")
log_file.write(f"Started: {pd.Timestamp.now()}\n")
log_file.write("=" * 80 + "\n\n")

set_log_file(log_file)
print(f"Log file opened: {log_path}")
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

## OWID Life Expectancy and WHO vs OWID Comparison

**Purpose**: Explore Our World in Data (OWID) Life Expectancy data as extended temporal coverage alternative to WHO LE. Compare WHO and OWID for overlapping years to validate agreement.

**Data Source**: Our World in Data (https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex)

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
owid_le_temporal = convert_owid_le_to_temporal_format(owid_le_raw, min_year=2000, max_year=2023)
```

```python
# Compare WHO vs OWID LE for overlapping years (2000-2021)
le_who_compare = le[
    (le['Year'] >= 2000) & 
    (le['Year'] <= 2021) & 
    (le['Sex'].isin(['Male', 'Female']))
][['Code', 'Year', 'Sex', 'LifeExpectancy_Years']].copy()
le_who_compare = le_who_compare.rename(columns={'LifeExpectancy_Years': 'LE_WHO'})

owid_le_compare = owid_le_temporal[
    (owid_le_temporal['Year'] <= 2021)
][['Code', 'Year', 'Sex', 'LifeExpectancy_Years']].copy()
owid_le_compare = owid_le_compare.rename(columns={'LifeExpectancy_Years': 'LE_OWID'})

le_comparison = owid_le_compare.merge(
    le_who_compare,
    on=['Code', 'Year', 'Sex'],
    how='inner'
)

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
