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

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import decorate, underride, configure_plot_style, AIBM_COLORS, code_to_who_country, code_to_wef_country

configure_plot_style()
```

```python
def load_and_inventory(filename):
    """
    Load a WHO health indicator CSV file and print inventory information.
    
    Filters the data to include only records from year 2000 to 2019 (excludes 2020+)
    to avoid COVID-19 pandemic distortions, and country-level data (excludes regional aggregates).
    Adds a 'CountryName' column mapping country codes to country names using code_to_who_country.
    
    Parameters
    ----------
    filename : str
        Path to the CSV file containing WHO health indicator data.
        
    Returns
    -------
    df : pandas.DataFrame
        Filtered DataFrame containing country-level data from 2000-2019,
        with an additional 'CountryName' column.
    years : numpy.ndarray
        Array of unique years present in the filtered dataset.
    """
    # Filter to 2000-2019 to exclude COVID-19 pandemic years (2020+)
    df = pd.read_csv(filename).query('Year >= 2000 and Year <= 2019 and CountryCode == "COUNTRY"')
    
    # Add country name column using code_to_who_country mapping
    # The 'Country' column contains country codes (e.g., 'USA', 'GBR')
    df['CountryName'] = df['Country'].map(code_to_who_country)
    
    print(df.shape)

    try:
        print(df['IndicatorCode'].unique())
        print(df['IndicatorName'].unique())
    except KeyError:
        pass

    sexes = df['Sex'].unique()
    print(sexes)
    print(df['Comments'].unique())
    years = df['Year'].unique()
    print(years)
    print(df['Country'].unique())
    
    return df, years
```

```python
from functools import reduce

def compute_gender_gap(df, value_col, sexes):
    """
    Return a DataFrame with separate columns for each sex and a gap column,
    handling cases where one or more sexes are missing.

    Parameters
    ----------
    df : pandas.DataFrame
        Must include 'Country', 'Year', 'Sex', and the specified value_col.
        May also include 'CountryName' which will be preserved.
    value_col : str
        Name of the column containing the numeric value to compare between sexes.
    sexes : list of str
        List of values in the 'Sex' column, e.g. ['SEX_MLE', 'SEX_FMLE'].
        The first two entries are used to compute the gap (second - first).

    Returns
    -------
    df_by_sex : pandas.DataFrame
        Contains columns for each available sex and a gap column (second - first)
        if both sexes are present. Also includes 'CountryName' (added via mapping) and 'Year'.
    """
    # Determine which columns to keep
    # Base columns: Country, Year, and the value column (which will be renamed)
    # CountryName will be added later via mapping
    base_cols = ['Country', 'Year']
    
    dfs = []

    # Build a renamed DataFrame for each sex, only if it exists
    # Select only the columns we want to keep before merging
    for sex in sexes:
        temp = df[df['Sex'] == sex]
        if not temp.empty:
            # Select only the columns we need: base columns + value column
            cols_to_select = base_cols + [value_col]
            temp = temp[cols_to_select].copy()
            # Rename the value column to include the sex
            temp = temp.rename(columns={value_col: f"{value_col}_{sex}"})
            dfs.append(temp)

    # If no data at all, return empty DataFrame
    if not dfs:
        return pd.DataFrame(columns=['Country', 'Year'])

    # Merge all available sexes
    merge_on = ['Country', 'Year']
    df_by_sex = reduce(lambda left, right: left.merge(right, on=merge_on, how='outer'), dfs)

    # Compute the gap only if both sexes are available
    if len(sexes) >= 2:
        col1 = f"{value_col}_{sexes[0]}"
        col2 = f"{value_col}_{sexes[1]}"
        if col1 in df_by_sex.columns and col2 in df_by_sex.columns:
            df_by_sex[f"{value_col}_Gap"] = df_by_sex[col2] - df_by_sex[col1]

    df_by_sex['CountryName'] = df_by_sex['Country'].map(code_to_who_country)

    return df_by_sex

```

```python
def summarize_gap(df, col, sexes=None):
    """
    Compute gender gap and create summary visualization using most recent data per country.
    
    Computes gender gaps using compute_gender_gap, then selects the most recent year
    available for each country (which may differ by country). Creates a scatter plot
    comparing values between sexes (if multiple sexes are provided).
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing health indicator data with 'Country', 'Year', 'Sex',
        and the value column specified by col. May also include 'CountryName'.
    col : str
        Name of the column containing the numeric value to compare between sexes.
    sexes : list of str
        List of sex values to compare (e.g., ['Male', 'Female']).
        
    Returns
    -------
    df_gap : pandas.DataFrame
        DataFrame with gender gap computed for all years. Includes 'CountryName' and 'Year' columns.
    df_recent : pandas.DataFrame
        DataFrame with the most recent available year for each country, indexed by Country.
        Includes 'CountryName' and 'Year' columns.
    """
    sexes = sexes or ['Male', 'Female']
    df_gap = compute_gender_gap(df, col, sexes)
    
    # Get the most recent year for each country
    most_recent_years = df_gap.groupby('Country')['Year'].max().reset_index()
    df_recent = df_gap.merge(most_recent_years, on=['Country', 'Year'])
    
    # Set index to Country, but keep CountryName and Year as columns
    df_recent = df_recent.set_index('Country')
    
    if len(sexes) > 1:
        cols = [f'{col}_{sex}' for sex in sexes]
        high = df_recent[cols].max().max()
        domain = [0, high]
        scatter_plot(df_recent, cols, domain)
        decorate(xlabel=f'{col}, Male', 
                 ylabel=f'{col}, Female', title=f'All Countries')
    
    return df_gap, df_recent
```

```python
def scatter_plot(df, cols, domain, **options):
    """
    Create a scatter plot comparing two columns with a diagonal reference line.
    
    Plots the values from two columns against each other, with a diagonal
    reference line (y=x) to show equality. Uses a square aspect ratio by default.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame indexed by country, containing the columns to plot.
    cols : list of str
        List of two column names to plot on x and y axes.
    domain : list of float
        Two-element list [min, max] defining the plot domain for both axes.
    **options : dict
        Additional keyword arguments passed to decorate() for plot customization
        (e.g., xlabel, ylabel, title).
    """
    plt.plot(df[cols[0]], df[cols[1]], '.', color=AIBM_COLORS['crimson'])
    plt.plot(domain, domain, color='gray', alpha=0.5)
    
    underride(options, aspect='equal')
    decorate(**options)
```

```python
from utils import oecd_codes
import warnings

def get_oecd(df):
    """
    Filter DataFrame to include only OECD member countries.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame indexed by country codes.
        
    Returns
    -------
    pandas.DataFrame
        Subset of the input DataFrame containing only OECD countries.
        
    Note
    -----
    Warns if any expected OECD countries are missing from the data.
    """
    available_countries = set(df.index)
    expected_oecd = set(oecd_codes)
    missing_countries = expected_oecd - available_countries
    
    if missing_countries:
        warnings.warn(
            f"Missing {len(missing_countries)} OECD countries in data: {sorted(missing_countries)}",
            UserWarning
        )
    
    return df.loc[df.index.intersection(oecd_codes)]
```

```python
def summarize_years(predictor_dfs):
    """
    Create a summary table of year coverage for each indicator in predictor_dfs.
    
    Parameters
    ----------
    predictor_dfs : dict
        Dictionary mapping indicator names to DataFrames containing predictor data.
        Each DataFrame should have a 'Year' column.
        
    Returns
    -------
    pandas.DataFrame
        Summary table with columns: Indicator, Low_Year, High_Year, Most_Common_Year,
        N_Countries_Most_Common, Total_Countries.
    """
    year_summary = []
    
    for name, df in predictor_dfs.items():
        years = df['Year'].dropna()
        if len(years) > 0:
            year_counts = years.value_counts()
            most_common_year = year_counts.index[0]
            n_countries_most_common = year_counts.iloc[0]
            
            year_summary.append({
                'Indicator': name,
                'Low_Year': int(years.min()),
                'High_Year': int(years.max()),
                'Most_Common_Year': int(most_common_year),
                'N_Countries_Most_Common': int(n_countries_most_common),
                'Total_Countries': len(df)
            })
        else:
            year_summary.append({
                'Indicator': name,
                'Low_Year': np.nan,
                'High_Year': np.nan,
                'Most_Common_Year': np.nan,
                'N_Countries_Most_Common': 0,
                'Total_Countries': len(df)
            })
            
    return pd.DataFrame(year_summary)
```

```python
from empiricaldist import Cdf

def plot_cdfs(df, label='', **options):
    """
    Plot cumulative distribution functions (CDFs) for columns ending in 'ale'.
    
    Creates CDF plots for all columns in the DataFrame that end with 'ale'
    (typically 'Male' and 'Female' columns). Each CDF is plotted with a label
    combining the column name and the provided label.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing numeric columns to plot as CDFs.
    label : str, optional
        Additional label text to append to each CDF plot label (default: '').
    **options : dict
        Additional keyword arguments for plot customization.
    """
    cols = [col for col in df.columns if col.endswith('ale')]
    for col in cols:
        vals = df[col].dropna()
        if vals.count() == 0:
            break
        cdf = Cdf.from_seq(df[col])
        cdf.plot(label=f'{col} {label}', **options)
```

```python
def plot_distributions(recent, **options):
    """
    Plot CDFs comparing all countries vs OECD countries.
    
    Creates cumulative distribution function plots for both all countries
    and OECD countries subset, allowing comparison of distributions.
    
    Parameters
    ----------
    recent : pandas.DataFrame
        DataFrame indexed by country codes, containing columns ending in 'ale'
        (typically 'Male' and 'Female' columns).
    **options : dict
        Additional keyword arguments passed to decorate() for plot customization
        (e.g., xlabel, title). The ylabel is automatically set to 'CDF'.
    """
    plot_cdfs(recent, label='All countries')
    plot_cdfs(get_oecd(recent), label='OECD')
    
    # Extract indicator name from column names (remove _Male or _Female suffix)
    cols = [col for col in recent.columns if col.endswith('ale')]
    if cols:
        # Get the first column and extract the indicator name
        first_col = cols[0]
        # Remove _Male or _Female suffix to get the indicator name
        indicator_name = first_col.rsplit('_')[:-1] if '_' in first_col else first_col
        xlabel = indicator_name
    else:
        xlabel = ''
    
    underride(options, xlabel=xlabel, ylabel='CDF')
    decorate(**options)
```

## WHO HALE data

**Healthy Life Expectancy (HALE) at birth** - The average number of years that a person can expect to live in "full health" by taking into account years lived in less than full health due to disease and/or injury. This is the **target variable** for the analysis. The gender gap (Female HALE - Male HALE) measures the difference in healthy life expectancy between women and men.

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
year = years[-1]
hale_gap, hale_recent = summarize_gap(hale, col)
```

```python

```

```python
plot_distributions(hale_recent)
```

## Smoking

**Age-standardized current tobacco smoking prevalence (%)** - Percentage of population aged 15+ who currently smoke any tobacco product, age-standardized for cross-country comparison.

**Indicator Code**: M_Est_smk_curr_std  
**Relevance**: Historically, men have had significantly higher smoking rates than women. Smoking is a major contributor to cardiovascular disease, lung cancer, and respiratory diseases. As smoking rates have converged between genders in some countries, the life expectancy gap has narrowed, suggesting smoking is one of the most important modifiable factors contributing to the HALE gender gap.

```python
filename = '../data/who_smoking_data.csv'
smoking, years = load_and_inventory(filename)
```

```python
smoking.head()
```

```python
col = 'SmokingPrevalence'
year = years[-1]
smoking_gap, smoking_recent = summarize_gap(smoking, col)
```

```python
plot_distributions(smoking_recent)
```

## Suicide

**Age-standardized suicide rates (per 100,000 population)** - Deaths from intentional self-harm, age-standardized for cross-country comparison.

**Indicator Code**: MH_12  
**Relevance**: Suicide rates are typically higher in men across most countries, directly contributing to the gender gap in mortality. Suicide reflects mental health and social factors that differentially affect men and women, and is strongly linked to mortality.

```python
filename = '../data/who_suicide_rates.csv'
suicide, years = load_and_inventory(filename)
```

```python
suicide.head()
```

```python
col = 'SuicideRate'
year = years[-1]
suicide_gap, suicide_recent = summarize_gap(suicide, col)
```

```python
plot_distributions(suicide_recent)
```

## Alcohol

**Alcohol-attributable all-cause deaths per 100,000 (age-standardized)** - Deaths from all causes that are attributable to alcohol consumption, including direct alcohol-related deaths and alcohol-attributable deaths from other causes (e.g., accidents, liver disease).

**Indicator Code**: SA_0000001832  
**Relevance**: Men typically have higher rates of alcohol consumption and alcohol-related diseases. Alcohol contributes to liver disease, accidents, and various health conditions, directly impacting mortality. Age-standardized rates match HALE methodology for cross-country comparison.

```python
filename = '../data/who_alcohol_death_rates.csv'
alcohol, years = load_and_inventory(filename)
```

```python
alcohol.head()
```

```python
col = 'AlcoholDeathRate'
year = years[-1]
alcohol_gap, alcohol_recent = summarize_gap(alcohol, col)
```

```python
plot_distributions(alcohol_recent)
```

## Poison

**Mortality rate attributed to unintentional poisoning (per 100,000 population)** - Deaths from accidental poisonings from chemicals, drugs, and other substances.

**Indicator Code**: SDGPOISON  
**Relevance**: Men often have higher rates of accidental deaths, including poisonings. This reflects occupational hazards and risk-taking behaviors that contribute to the gender gap in mortality. Has excellent temporal coverage (2000-2021) and country coverage (196 countries).

```python
filename = '../data/who_poisoning_rates.csv'
poison, years = load_and_inventory(filename)
```

```python
poison.head()
```

```python
col = 'PoisoningRate'
year = years[-1]
poison_gap, poison_recent = summarize_gap(poison, col)
```

```python
plot_distributions(poison_recent)
```

## Traffic

**Road traffic crash deaths, age-standardized death rates (15+), per 100,000 population** - Deaths from road traffic accidents, age-standardized for ages 15+.

**Indicator Code**: SA_0000001459  
**Relevance**: Road traffic deaths are typically 2-4 times higher in men across most countries, making it a major contributor to the gender gap in mortality. Reflects higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. Age-standardized rates for ages 15+ match HALE methodology.

```python
filename = '../data/who_road_traffic_death_rates.csv'
traffic, years = load_and_inventory(filename)
```

```python
traffic.head()
```

```python
col = 'RoadTrafficDeathRate'
year = years[-1]
traffic_gap, traffic_recent = summarize_gap(traffic, col)
```

```python
plot_distributions(traffic_recent)
```

## Maternal mortality

**Maternal mortality ratio (per 100,000 live births)** - Deaths of women during pregnancy, childbirth, or within 42 days of termination of pregnancy, per 100,000 live births.

**Indicator Code**: MDG_0000000026  
**Relevance**: Critical for understanding cases where the HALE gender gap is small due to high female mortality, especially in lower-income countries. High maternal mortality can significantly reduce the HALE gender gap by lowering female life expectancy. Inherently female-specific, so only female values are used in analysis.

```python
filename = '../data/who_maternal_mortality_ratio.csv'
maternal, years = load_and_inventory(filename)
```

```python
maternal.head()
```

```python
col = 'MaternalMortalityRatio'
year = years[-1]
maternal_gap, maternal_recent = summarize_gap(maternal, col, sexes=['Female'])
```

```python
plot_distributions(maternal_recent)
```

## Homicide

**Estimates of rates of homicides per 100,000 population** - Deaths from intentional homicide, including estimates with confidence intervals.

**Indicator Code**: VIOLENCE_HOMICIDERATE  
**Relevance**: Homicide rates are typically much higher in men across most countries, making it a major contributor to the gender gap in mortality. Homicide reflects violence, conflict, and social factors that differentially affect men and women. Has excellent temporal coverage (2000-2021) and country coverage (196 countries).

```python
filename = '../data/who_homicide_rates.csv'
homicide, years = load_and_inventory(filename)
```

```python
homicide.head()
```

```python
col = 'HomicideRate'
year = years[-1]
homicide_gap, homicide_recent = summarize_gap(homicide, col)
```

```python
plot_distributions(homicide_recent)
```

## Intimate Partner Violence

**Proportion of ever-partnered women and girls aged 15-49 years subjected to physical and/or sexual violence by a current or former intimate partner in the previous 12 months (%)** - Prevalence indicator measuring the percentage of women experiencing intimate partner violence.

**Indicator Code**: SDGIPV  
**Relevance**: Note: This is a **prevalence indicator** (percentage), not a direct death rate. IPV affects women's health indirectly through mental health impacts, injuries, and other health consequences. It may contribute to the gender gap in HALE through its effects on women's physical and mental health, though the relationship is complex and indirect. Inherently female-specific, so only female values are used in analysis.

```python
filename = '../data/who_ipv_prevalence.csv'
ipv, years = load_and_inventory(filename)
```

```python
ipv.head()
```

```python
col = 'IPVPrevalence'
year = years[-1]
ipv_gap, ipv_recent = summarize_gap(ipv, col, sexes=['Female'])
```

```python
plot_distributions(ipv_recent)
```

## Under five mortality rate

**Under-five mortality rate (probability of dying by age 5 per 1000 live births)** - Deaths of children under age 5 per 1,000 live births, with gender breakdowns.

**Indicator Code**: MDG_0000000007  
**Relevance**: HALE is calculated from birth, so under-five mortality directly affects HALE calculations. If child mortality differs by gender, it directly contributes to the HALE gender gap. Infant mortality is typically higher in males (biological vulnerability + some behavioral factors). More important in lower-income countries with high child mortality. Note: MDG_0000000007 chosen over u5mr for better data quality when filtered for sex dimension.

```python
filename = '../data/who_u5mr.csv'
u5mr, years = load_and_inventory(filename)
```

```python
u5mr.head()
```

```python
col = 'U5MR'
year = years[-1]
u5mr_gap, u5mr_recent = summarize_gap(u5mr, col)
```

```python
plot_distributions(u5mr_recent)
```

## Cardiovascular Disease

**Age-standardized cardiovascular disease death rates (per 100,000)** - Deaths from cardiovascular diseases (heart disease, stroke, etc.), age-standardized for cross-country comparison.

**Indicator Code**: Multiple codes tried (WHS2_161, etc.) - see `who_data.py` for implementation details  
**Relevance**: Men typically have higher rates of cardiovascular disease and heart attacks, contributing significantly to the gender gap in mortality. Risk factors include smoking, diet, and potentially biological differences. May capture effects of smoking and other risk factors. Age-standardized rates match HALE methodology.

```python
filename = '../data/who_cardiovascular_death_rates.csv'
cardio, years = load_and_inventory(filename)
```

```python
# Rename DeathRate to CardioDeathRate to avoid ambiguity
cardio = cardio.rename(columns={'DeathRate': 'CardioDeathRate'})
cardio.head()
```

```python
col = 'CardioDeathRate'
year = years[-1]
cardio_gap, cardio_recent = summarize_gap(cardio, col)
```

```python
plot_distributions(cardio_recent)
```

## Diabetes

**Age-standardized death rates, diabetes mellitus (per 100,000)** - Deaths from diabetes, age-standardized for cross-country comparison.

**Indicator Code**: SA_0000001440  
**Relevance**: Diabetes is a chronic condition that can contribute to the gender gap in mortality, though the relationship may vary by country and healthcare access. Age-standardized rates match HALE methodology. **Limitation**: Only has data for 2004 (similar to cardiovascular disease indicators), which limits temporal analysis but provides a good cross-sectional snapshot.

```python
filename = '../data/who_diabetes_death_rates.csv'
diabetes, years = load_and_inventory(filename)
```

```python
diabetes.head()
```

```python
col = 'DiabetesDeathRate'
year = years[-1]
diabetes_gap, diabetes_recent = summarize_gap(diabetes, col)
```

```python
plot_distributions(diabetes_recent)
```

## NCD Mortality (30-70 years)

**Probability (%) of dying between age 30 and exact age 70 from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease** - Combined non-communicable disease mortality indicator.

**Indicator Code**: NCDMORT3070  
**Relevance**: Combines multiple causes of death (cardiovascular disease, cancer, diabetes, chronic respiratory disease), so it's less specific than individual cause indicators. However, it has much better temporal coverage (2000-2021) than diabetes-specific indicators (which only have 2004 data). This makes it useful for model comparison - trading off specificity for temporal coverage. The combined indicator may capture overall NCD mortality patterns that contribute to the HALE gender gap.

```python
filename = '../data/who_ncd_mortality_30_70.csv'
ncdmort, years = load_and_inventory(filename)
```

```python
ncdmort.head()
```

```python
col = 'NCDMortality30_70'
year = years[-1]
ncdmort_gap, ncdmort_recent = summarize_gap(ncdmort, col)
```

```python
plot_distributions(ncdmort_recent)
```

## Drug Use Disorders (IHME)

**Drug use disorder death rates (per 100,000 population)** - Deaths from drug use disorders, including overdoses, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Drug overdoses, particularly opioid overdoses, are a major cause of death in some OECD countries (especially the US) and may contribute significantly to the HALE gender gap. This indicator captures overdose deaths that may not be fully captured in the WHO poisoning indicator. Data includes separate male and female values, allowing for gender gap analysis.

```python
def load_ihme_indicator(filename_male, filename_female, value_col_name, indicator_code, indicator_name):
    """
    Load IHME indicator data from separate male and female files and convert to WHO-compatible format.
    
    Converts IHME CSV format (Location=country name, Sex="Male"/"Female") to WHO format
    (Country=country code, Sex="Male"/"Female", etc.). Filters to 2000-2019.
    
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
        Country, CountryCode, Year, Sex, value_col_name, value_col_name_Low, 
        value_col_name_High, CountryName.
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
        
        # Filter to 2000-2019 (exclude 2020+ for COVID-19 reasons)
        df = df.query('Year >= 2000 and Year <= 2019')
        
        # Filter to "All ages" (if Age column exists)
        if 'Age' in df.columns:
            df = df.query('Age == "All ages"')
        
        # Map IHME country names to WHO country names
        df['Location'] = df['Location'].replace(ihme_country_name_mapping)
        
        # Convert country names to codes
        df['Country'] = df['Location'].map(who_country_to_code)
        
        # Filter out rows where country mapping failed (not in our country list)
        df = df[df['Country'].notna()].copy()
        
        # Set Sex column to the specified value (Male or Female)
        df['Sex'] = sex_value
        
        # Rename and create columns to match WHO format
        df['IndicatorCode'] = indicator_code
        df['IndicatorName'] = indicator_name
        df['CountryCode'] = 'COUNTRY'
        df[value_col_name] = df['Value']
        df[f'{value_col_name}_Low'] = df['Lower bound']
        df[f'{value_col_name}_High'] = df['Upper bound']
        df['CountryName'] = df['Location']
        
        # Select and reorder columns to match WHO format
        columns_to_keep = [
            'IndicatorCode', 'IndicatorName', 'Country', 'CountryCode', 'Year', 'Sex',
            value_col_name, f'{value_col_name}_Low', f'{value_col_name}_High',
            'CountryName'
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
year = years[-1]
drug_disorders_gap, drug_disorders_recent = summarize_gap(drug_disorders, col)
```

```python
plot_distributions(drug_disorders_recent)
```

## Diabetes Type 2 (IHME)

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
year = years[-1]
diabetes_ihme_gap, diabetes_ihme_recent = summarize_gap(diabetes_ihme, col)
```

```python
plot_distributions(diabetes_ihme_recent)
```

## Cardiovascular Diseases (IHME)

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
year = years[-1]
cardiovascular_ihme_gap, cardiovascular_ihme_recent = summarize_gap(cardiovascular_ihme, col)
```

```python
plot_distributions(cardiovascular_ihme_recent)
```

## Neoplasms (Cancer) (IHME)

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
year = years[-1]
neoplasms_ihme_gap, neoplasms_ihme_recent = summarize_gap(neoplasms_ihme, col)
```

```python
plot_distributions(neoplasms_ihme_recent)
```

## Chronic Respiratory Diseases (IHME)

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
year = years[-1]
chronic_respiratory_ihme_gap, chronic_respiratory_ihme_recent = summarize_gap(chronic_respiratory_ihme, col)
```

```python
plot_distributions(chronic_respiratory_ihme_recent)
```

## Unintentional Injuries (IHME)

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
year = years[-1]
unintentional_injuries_ihme_gap, unintentional_injuries_ihme_recent = summarize_gap(unintentional_injuries_ihme, col)
```

```python
plot_distributions(unintentional_injuries_ihme_recent)
```

## Phase 1: Data Preparation for Regression Analysis

### Step 1.2: Prepare Target Variable (HALE Gender Gap)

```python
# Calculate HALE gender gap from existing hale_recent DataFrame
hale_recent['HALE_gap'] = hale_recent['HALE_Years_Female'] - hale_recent['HALE_Years_Male']

# Filter to OECD countries
hale_oecd = get_oecd(hale_recent)

# Display summary
hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].describe()
```

```python
# Diagnostic: Check Israel's (ISR) HALE values
if 'ISR' in hale_recent.index:
    isr_data = hale_recent.loc[['ISR']]
    print("=== Israel (ISR) HALE Data ===")
    print(isr_data[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']])
    if 'CountryName' in isr_data.columns:
        print(f"Country Name: {isr_data['CountryName'].iloc[0]}")
    
    # Check if this is an outlier
    print(f"\nHALE Gap: {isr_data['HALE_gap'].iloc[0]:.2f} years")
    print(f"Male HALE: {isr_data['HALE_Years_Male'].iloc[0]:.2f} years")
    print(f"Female HALE: {isr_data['HALE_Years_Female'].iloc[0]:.2f} years")
    
    # Compare to other countries
    print(f"\nCountries with negative HALE gap (men > women):")
    negative_gap = hale_recent[hale_recent['HALE_gap'] < 0]
    if len(negative_gap) > 0:
        print(negative_gap[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].sort_values('HALE_gap'))
    else:
        print("No other countries with negative gap found")
    
    # Check raw HALE data for Israel to see if there's a data issue
    print(f"\n=== Checking raw HALE data for Israel ===")
    if 'ISR' in hale.index:
        isr_raw = hale[hale['Country'] == 'ISR'].sort_values('Year')
        print(f"Years available: {sorted(isr_raw['Year'].unique())}")
        print(f"\nRaw data by year and sex:")
        print(isr_raw[['Year', 'Sex', 'HALE_Years']].pivot(index='Year', columns='Sex', values='HALE_Years'))
else:
    print("Israel (ISR) not found in hale_recent")
```

### Step 1.4: Merge All Predictors into Single Dataset

```python
# Start with HALE data as base
analysis_df = hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].copy()

# Merge all predictor DataFrames (already filtered to OECD in earlier sections)
# Note: We will exclude gap columns (_Gap), CountryName, and Year columns before merging
# Gap columns are perfectly collinear with male/female columns
predictor_dfs = {
    #'SmokingPrevalence': get_oecd(smoking_recent),
    'CardioDeathRate': get_oecd(cardiovascular_ihme_recent),
    'ChronicRespiratoryDeathRate': get_oecd(chronic_respiratory_ihme_recent),
    'SuicideRate': get_oecd(suicide_recent),
    'AlcoholDeathRate': get_oecd(alcohol_recent),
    'PoisoningRate': get_oecd(poison_recent),
    'RoadTrafficDeathRate': get_oecd(traffic_recent),
    'HomicideRate': get_oecd(homicide_recent),
    'MaternalMortalityRatio': get_oecd(maternal_recent),
    'U5MR': get_oecd(u5mr_recent),
    'DiabetesDeathRate': get_oecd(diabetes_ihme_recent),
    #'NCDMortality30_70': get_oecd(ncdmort_recent),
    'DrugDisorderDeathRate': get_oecd(drug_disorders_recent),
    'UnintentionalInjuriesDeathRate': get_oecd(unintentional_injuries_ihme_recent),
}
```

```python
# Summary table of year coverage for each indicator
year_summary_df = summarize_years(predictor_dfs)
year_summary_df
```

```python

for name, df in predictor_dfs.items():
    drop_cols = ['CountryName', 'Year']
    drop_cols += [col for col in df.columns if col.endswith('_Gap')]
    if drop_cols:
        predictor_dfs[name] = df.drop(columns=drop_cols)

# Check shapes after removing gaps
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

```python
#bad = analysis_df['IPVPrevalence_Female'].isna()
#analysis_df.loc[bad].index.map(code_to_who_country)
```

### Step 1.5: Create Final Analysis Dataset

```python
# Use complete-case analysis for primary model
analysis_complete = analysis_df.dropna()

# Document excluded countries
excluded_countries = set(analysis_df.index) - set(analysis_complete.index)
excluded_countries if excluded_countries else "No countries excluded - all OECD countries have complete data"
```

```python
# Separate target and predictors
target = analysis_complete['HALE_gap']
predictors = analysis_complete.drop(columns=['HALE_gap', 'HALE_Years_Male', 'HALE_Years_Female'])

# Display final dataset info
pd.DataFrame({
    'Dataset': ['Complete Cases'],
    'Countries': [len(analysis_complete)],
    'Target_Variable': ['HALE_gap'],
    'Number_of_Predictors': [len(predictors.columns)],
    'Predictor_Names': [', '.join(predictors.columns)]
})
```

```python
# Summary of Phase 1 completion
pd.DataFrame({
    'Step': ['1.2: Target Variable', '1.4: Merge', '1.5: Complete Cases'],
    'Status': ['Complete', 'Complete', 'Complete'],
    'Countries': [len(hale_oecd), len(analysis_df), len(analysis_complete)],
    'Variables': [3, len(analysis_df.columns), len(analysis_complete.columns)]
})
```

**Note**: Predictor standardization will be done as part of the regression pipeline (e.g., using `StandardScaler` in scikit-learn's pipeline), not as a separate preprocessing step.

## Phase 2: Exploratory Data Analysis

### Step 2.1: Descriptive Statistics

```python
target.sort_values()
```

```python
# Summary statistics for target variable (HALE gap)
target.describe()
```

```python
# Summary statistics for all predictors
predictors.describe()
```

```python
# Distribution of HALE gap across OECD countries
plt.hist(target, bins=15, color=AIBM_COLORS['crimson'], edgecolor='white')
decorate(xlabel='HALE Gap (Female - Male, years)', 
         ylabel='Number of Countries',
         title='Distribution of HALE Gender Gap Across OECD Countries')
```

```python
# Identify potential outliers using IQR method
Q1 = target.quantile(0.25)
Q3 = target.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = target[(target < lower_bound) | (target > upper_bound)]
outliers_df = pd.DataFrame({
    'Country': outliers.index,
    'HALE_Gap': outliers.values
}).sort_values('HALE_Gap')

outliers_df if not outliers_df.empty else "No outliers detected using IQR method"
```

### Step 2.2: Correlation Analysis

```python
# Calculate correlation matrix of all predictors
correlation_matrix = predictors.corr()

# Display correlation matrix
correlation_matrix
```

```python
# Visualize correlation matrix as heatmap
import seaborn as sns

plt.figure(figsize=(12, 12))
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # Mask upper triangle
sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', 
            center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
decorate(title='Correlation Matrix of Predictors (Lower Triangle)')
```

```python
# Identify highly correlated predictor pairs (|correlation| > 0.7)
high_corr_pairs = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr_val = correlation_matrix.iloc[i, j]
        if abs(corr_val) > 0.7:
            high_corr_pairs.append({
                'Predictor_1': correlation_matrix.columns[i],
                'Predictor_2': correlation_matrix.columns[j],
                'Correlation': corr_val
            })

high_corr_df = pd.DataFrame(high_corr_pairs).sort_values('Correlation', key=abs, ascending=False)
high_corr_df if not high_corr_df.empty else "No highly correlated pairs (|r| > 0.7) found"
```

```python
# Summary of correlation analysis
pd.DataFrame({
    'Analysis': ['Total Predictors', 'High Correlations (|r| > 0.7)', 'Max Correlation', 'Min Correlation'],
    'Value': [
        len(predictors.columns),
        len(high_corr_pairs) if high_corr_pairs else 0,
        correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max(),
        correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].min()
    ]
})
```

### Step 2.3: Extreme Values and Country Rankings

#### For Each Indicator: Highest and Lowest Values

```python
# Get list of indicators from predictor_dfs
indicator_names = list(predictor_dfs.keys())

# Create tables for each indicator showing top 5 and bottom 5 countries
indicator_extremes = {}

for indicator_name in indicator_names:
    # Get the recent dataframe for this indicator
    # We need to find which recent dataframe corresponds to this indicator
    # Check if it's in the predictor_dfs (which uses get_oecd on recent dataframes)
    df_recent = predictor_dfs[indicator_name]
    
    # Get male and female column names
    male_col = f'{indicator_name}_Male'
    female_col = f'{indicator_name}_Female'
    
    if male_col in df_recent.columns and female_col in df_recent.columns:
        # Create summary for this indicator
        indicator_data = df_recent[[male_col, female_col]].copy()
        if 'CountryName' in df_recent.columns:
            indicator_data['CountryName'] = df_recent['CountryName']
        else:
            # Map country codes to names
            indicator_data['CountryName'] = indicator_data.index.map(code_to_who_country)
        
        # For male values
        male_sorted = indicator_data.sort_values(male_col, ascending=False)
        male_top5 = male_sorted.head(5)[['CountryName', male_col]].copy()
        male_top5['Rank'] = range(1, 6)
        male_bottom5 = male_sorted.tail(5)[['CountryName', male_col]].copy()
        male_bottom5['Rank'] = range(len(male_sorted)-4, len(male_sorted)+1)
        
        # For female values
        female_sorted = indicator_data.sort_values(female_col, ascending=False)
        female_top5 = female_sorted.head(5)[['CountryName', female_col]].copy()
        female_top5['Rank'] = range(1, 6)
        female_bottom5 = female_sorted.tail(5)[['CountryName', female_col]].copy()
        female_bottom5['Rank'] = range(len(female_sorted)-4, len(female_sorted)+1)
        
        indicator_extremes[indicator_name] = {
            'male_top5': male_top5,
            'male_bottom5': male_bottom5,
            'female_top5': female_top5,
            'female_bottom5': female_bottom5
        }

# Display results for a few key indicators
key_indicators = ['AlcoholDeathRate', 'HomicideRate', 'CardioDeathRate', 'SuicideRate']
for indicator in key_indicators:
    if indicator in indicator_extremes:
        print(f"\n{'='*60}")
        print(f"{indicator} - Extreme Values")
        print(f"{'='*60}")
        print(f"\nTop 5 Countries - Male Values:")
        print(indicator_extremes[indicator]['male_top5'].to_string(index=False))
        print(f"\nBottom 5 Countries - Male Values:")
        print(indicator_extremes[indicator]['male_bottom5'].to_string(index=False))
        print(f"\nTop 5 Countries - Female Values:")
        print(indicator_extremes[indicator]['female_top5'].to_string(index=False))
        print(f"\nBottom 5 Countries - Female Values:")
        print(indicator_extremes[indicator]['female_bottom5'].to_string(index=False))
```

#### For Gender Gaps: Largest and Smallest Gaps

```python
# Create a mapping from indicator names to their recent dataframes and value column names
# This maps the predictor_dfs keys to the actual _recent dataframes and their value columns
indicator_to_recent = {
    'CardioDeathRate': ('cardiovascular_ihme_recent', 'CardioDeathRate'),
    'ChronicRespiratoryDeathRate': ('chronic_respiratory_ihme_recent', 'ChronicRespiratoryDeathRate'),
    'SuicideRate': ('suicide_recent', 'SuicideRate'),
    'AlcoholDeathRate': ('alcohol_recent', 'AlcoholDeathRate'),
    'PoisoningRate': ('poison_recent', 'PoisoningRate'),
    'RoadTrafficDeathRate': ('traffic_recent', 'RoadTrafficDeathRate'),
    'HomicideRate': ('homicide_recent', 'HomicideRate'),
    'U5MR': ('u5mr_recent', 'U5MR'),
    'DiabetesDeathRate': ('diabetes_ihme_recent', 'DiabetesDeathRate'),
    'DrugDisorderDeathRate': ('drug_disorders_recent', 'DrugDisorderDeathRate'),
    'UnintentionalInjuriesDeathRate': ('unintentional_injuries_ihme_recent', 'UnintentionalInjuriesDeathRate'),
}

gap_extremes = {}

for indicator_name in indicator_names:
    if indicator_name in indicator_to_recent:
        recent_var_name, value_col = indicator_to_recent[indicator_name]
        
        # Get the recent dataframe (already filtered to OECD and most recent year)
        if recent_var_name in globals():
            df_recent = globals()[recent_var_name]
            
            # Get column names
            male_col = f'{value_col}_Male'
            female_col = f'{value_col}_Female'
            gap_col = f'{value_col}_Gap'
            
            if gap_col in df_recent.columns:
                # Create summary with country names
                gap_data = df_recent[[male_col, female_col, gap_col]].copy()
                if 'CountryName' in df_recent.columns:
                    gap_data['CountryName'] = df_recent['CountryName']
                else:
                    gap_data['CountryName'] = df_recent.index.map(code_to_who_country)
                
                # Sort by gap (largest positive gaps first)
                # Note: Gap is computed as Female - Male, so positive means females have higher rates
                gap_sorted = gap_data.sort_values(gap_col, ascending=False)
                
                gap_top5 = gap_sorted.head(5).copy()
                gap_top5['Rank'] = range(1, 6)
                gap_bottom5 = gap_sorted.tail(5).copy()
                gap_bottom5['Rank'] = range(len(gap_sorted)-4, len(gap_sorted)+1)
                
                gap_extremes[indicator_name] = {
                    'top5': gap_top5,
                    'bottom5': gap_bottom5
                }

# Display results for key indicators
for indicator in key_indicators:
    if indicator in gap_extremes:
        print(f"\n{'='*60}")
        print(f"{indicator} - Gender Gap Extremes (Female - Male)")
        print(f"{'='*60}")
        gap_info = gap_extremes[indicator]
        print(f"\nTop 5 Countries - Largest Gaps (Female > Male):")
        cols_to_show = ['CountryName', 'Rank', f'{indicator_to_recent[indicator][1]}_Male', 
                       f'{indicator_to_recent[indicator][1]}_Female', f'{indicator_to_recent[indicator][1]}_Gap']
        print(gap_info['top5'][cols_to_show].to_string(index=False))
        print(f"\nBottom 5 Countries - Smallest Gaps (Male > Female):")
        print(gap_info['bottom5'][cols_to_show].to_string(index=False))
```

#### For HALE Gap: All Countries Ranked

```python
# Create ranked table of all countries by HALE gap
hale_ranked = analysis_complete[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].copy()
hale_ranked['CountryName'] = hale_ranked.index.map(code_to_who_country)
hale_ranked = hale_ranked.sort_values('HALE_gap', ascending=False).reset_index()
hale_ranked['Rank'] = range(1, len(hale_ranked) + 1)

# Reorder columns
hale_ranked = hale_ranked[['Rank', 'Country', 'CountryName', 'HALE_Years_Male', 
                           'HALE_Years_Female', 'HALE_gap']]

print("All Countries Ranked by HALE Gap (Female - Male)")
print("="*80)
print(hale_ranked.to_string(index=False))
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
print(hale_ranked.head(5)[['Rank', 'CountryName', 'HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].to_string(index=False))
print(f"\nCountries with Smallest HALE Gap (Bottom 5):")
print(hale_ranked.tail(5)[['Rank', 'CountryName', 'HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].to_string(index=False))
```

### Step 2.4: Save Data for Future Use

```python
# Save predictors and target to HDF5 file for future use
import pandas as pd

# Create a dictionary with all the data we want to save
data_to_save = {
    'predictors': predictors,
    'target': target,
    'analysis_complete': analysis_complete,
    'hale_ranked': hale_ranked
}

# Save to HDF5 file
hdf_file = '../data/hale_analysis_data.h5'
with pd.HDFStore(hdf_file, mode='w') as store:
    store['predictors'] = predictors
    store['target'] = target
```

### Step 2.5: Load Saved Data

```python
# Code to read the saved data back from HDF5 file
hdf_file = '../data/hale_analysis_data.h5'

# Read data back
with pd.HDFStore(hdf_file, mode='r') as store:
    predictors_loaded = store['predictors']
    target_loaded = store['target']
```

### Step 2.6: Statsmodels Linear Regression (Non-Negligible Indicators Only)

```python
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS

# Define indicators with non-negligible importance (total importance > 1.0)
# Based on coefficient-based importance results
non_negligible_indicators = [
    'AlcoholDeathRate',           # 77.60
    'CardioDeathRate',             # 26.92
    'ChronicRespiratoryDeathRate', # 22.79
    'UnintentionalInjuriesDeathRate', # 3.10
    'SuicideRate',                 # 2.12
    'MaternalMortalityRatio',      # 1.29 (female-only)
    'RoadTrafficDeathRate',        # 1.00
]

# Select predictors for non-negligible indicators
# Include both male and female columns for each indicator (except maternal mortality)
selected_predictors = []
for indicator in non_negligible_indicators:
    male_col = f'{indicator}_Male'
    female_col = f'{indicator}_Female'
    
    if indicator == 'MaternalMortalityRatio':
        # Maternal mortality is female-only
        if female_col in predictors.columns:
            selected_predictors.append(female_col)
    else:
        # Include both male and female
        if male_col in predictors.columns:
            selected_predictors.append(male_col)
        if female_col in predictors.columns:
            selected_predictors.append(female_col)

# Create subset of predictors with only non-negligible indicators
X_selected = predictors[selected_predictors].copy()

print(f"Selected {len(selected_predictors)} predictors from {len(non_negligible_indicators)} indicators")
print(f"Predictors: {selected_predictors}")
print(f"\nData shape: {X_selected.shape}")
```

```python
# Add constant term for intercept (statsmodels doesn't add it by default)
X_with_const = sm.add_constant(X_selected)

# Fit OLS regression model
ols_model = OLS(target, X_with_const).fit()

# Display summary
print(ols_model.summary())
```

```python
# Extract key statistics
print("\n" + "="*60)
print("Model Summary Statistics")
print("="*60)
print(f"R-squared: {ols_model.rsquared:.4f}")
print(f"Adjusted R-squared: {ols_model.rsquared_adj:.4f}")
print(f"F-statistic: {ols_model.fvalue:.4f}")
print(f"F-statistic p-value: {ols_model.f_pvalue:.4e}")
print(f"Number of observations: {ols_model.nobs}")
print(f"Number of predictors: {len(selected_predictors)}")
print(f"\nAIC: {ols_model.aic:.2f}")
print(f"BIC: {ols_model.bic:.2f}")
```

```python
# Display coefficients with p-values
coef_summary = pd.DataFrame({
    'Coefficient': ols_model.params,
    'Std Error': ols_model.bse,
    't-value': ols_model.tvalues,
    'P>|t|': ols_model.pvalues,
    'Conf Int [0.025': ols_model.conf_int()[0],
    '0.975]': ols_model.conf_int()[1]
})

# Sort by absolute coefficient value (excluding intercept)
coef_no_const = coef_summary.drop('const')
coef_sorted = coef_no_const.reindex(
    coef_no_const['Coefficient'].abs().sort_values(ascending=False).index
)
coef_summary_sorted = pd.concat([coef_sorted, coef_summary.loc[['const']]])

print("\nCoefficients (sorted by absolute value):")
print(coef_summary_sorted)
```

```python
# Identify significant predictors (p < 0.05)
significant = coef_summary[coef_summary['P>|t|'] < 0.05].sort_values('P>|t|')
print(f"\nSignificant predictors (p < 0.05): {len(significant)} out of {len(coef_summary)}")
print(significant[['Coefficient', 'P>|t|']])
```

```python
# Check for multicollinearity: correlations with CardioDeathRate
print("\n" + "="*60)
print("Multicollinearity Analysis: CardioDeathRate Correlations")
print("="*60)

cardio_correlations = X_selected.corr()[['CardioDeathRate_Male', 'CardioDeathRate_Female']].abs()
cardio_correlations = cardio_correlations.sort_values('CardioDeathRate_Female', ascending=False)
print("\nCorrelations with CardioDeathRate predictors:")
print(cardio_correlations)
```

```python
# Calculate Variance Inflation Factors (VIF) to detect multicollinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Calculate VIF for each predictor
vif_data = pd.DataFrame()
vif_data["Predictor"] = X_with_const.columns
vif_data["VIF"] = [variance_inflation_factor(X_with_const.values, i) 
                   for i in range(X_with_const.shape[1])]

# Sort by VIF (higher VIF indicates more multicollinearity)
vif_data = vif_data.sort_values('VIF', ascending=False)
print("\n" + "="*60)
print("Variance Inflation Factors (VIF)")
print("="*60)
print("VIF > 10 indicates high multicollinearity")
print("VIF > 5 suggests moderate multicollinearity")
print(vif_data)
```

```python
# Why CardioDeathRate has small, non-significant coefficients:
# 1. High correlation with other predictors (especially AlcoholDeathRate or ChronicRespiratoryDeathRate)
# 2. In OLS, when predictors are highly correlated, their individual coefficients become unstable
# 3. The variance explained by CardioDeathRate is already captured by other predictors
# 4. Elastic Net (which gave high importance) uses regularization to handle multicollinearity,
#    allowing correlated predictors to contribute even when individually they're not significant in OLS

print("\n" + "="*60)
print("Explanation for CardioDeathRate Coefficients")
print("="*60)
print("""
CardioDeathRate shows high importance (26.92) in Elastic Net but tiny, non-significant 
coefficients in OLS. This is likely due to:

1. **Multicollinearity**: CardioDeathRate is highly correlated with other predictors
   (especially AlcoholDeathRate or ChronicRespiratoryDeathRate)

2. **Regularization difference**: 
   - Elastic Net uses regularization (L1 + L2), which can handle multicollinearity
   - OLS doesn't use regularization, so when predictors are correlated, their individual
     contributions become unstable and non-significant

3. **Variance already explained**: The variance that CardioDeathRate explains is largely
   redundant with other predictors already in the model

4. **Small sample size**: With only 38 observations and 13 predictors, OLS has limited
   power to distinguish between highly correlated predictors

The high VIF values (if present) would confirm multicollinearity as the cause.
""")
```

## Phase 3: Model Fitting

### Step 3.1: Model Selection Setup

```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold
from sklearn.metrics import r2_score, mean_absolute_error

# Prepare data: X (predictors) and y (target)
X = predictors.copy()
y = target.copy()

# Display data shape
pd.DataFrame({
    'Data': ['Predictors (X)', 'Target (y)'],
    'Shape': [X.shape, y.shape],
    'Countries': [X.shape[0], y.shape[0]]
})
```

```python
# Set up cross-validation (5-fold for small sample size)
cv = KFold(n_splits=5, shuffle=True, random_state=42)

# Display CV setup
f"Using {cv.n_splits}-fold cross-validation for model selection"
```

### Step 3.2: Fit Multiple Models

```python
# Define parameter grids for each model
ridge_params = {'ridge__alpha': np.logspace(-2, 4, 50)}  # Regularization strength
lasso_params = {'lasso__alpha': np.logspace(-3, 1, 50)}
elastic_net_params = {
    'elasticnet__alpha': np.logspace(-3, 1, 20),
    'elasticnet__l1_ratio': np.linspace(0.1, 0.9, 9)  # 0=Ridge, 1=Lasso
}

# Create pipelines with StandardScaler and models
ridge_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge', Ridge())
])

lasso_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lasso', Lasso(max_iter=10000))
])

elastic_net_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('elasticnet', ElasticNet(max_iter=10000))
])
```

```python
# Fit Ridge Regression with cross-validation
print("Fitting Ridge Regression...")
ridge_grid = GridSearchCV(ridge_pipeline, ridge_params, cv=cv, 
                          scoring='r2', n_jobs=-1, verbose=1)
ridge_grid.fit(X, y)

ridge_best_score = ridge_grid.best_score_
ridge_best_params = ridge_grid.best_params_
ridge_best_model = ridge_grid.best_estimator_

pd.DataFrame({
    'Model': ['Ridge'],
    'Best_CV_R2': [ridge_best_score],
    'Best_Alpha': [ridge_best_params['ridge__alpha']]
})
```

```python
# Fit Lasso Regression with cross-validation
print("Fitting Lasso Regression...")
lasso_grid = GridSearchCV(lasso_pipeline, lasso_params, cv=cv,
                          scoring='r2', n_jobs=-1, verbose=1)
lasso_grid.fit(X, y)

lasso_best_score = lasso_grid.best_score_
lasso_best_params = lasso_grid.best_params_
lasso_best_model = lasso_grid.best_estimator_

pd.DataFrame({
    'Model': ['Lasso'],
    'Best_CV_R2': [lasso_best_score],
    'Best_Alpha': [lasso_best_params['lasso__alpha']]
})
```

```python
# Fit Elastic Net with cross-validation
print("Fitting Elastic Net...")
elastic_net_grid = GridSearchCV(elastic_net_pipeline, elastic_net_params, cv=cv,
                                 scoring='r2', n_jobs=-1, verbose=1)
elastic_net_grid.fit(X, y)

elastic_net_best_score = elastic_net_grid.best_score_
elastic_net_best_params = elastic_net_grid.best_params_
elastic_net_best_model = elastic_net_grid.best_estimator_

pd.DataFrame({
    'Model': ['Elastic Net'],
    'Best_CV_R2': [elastic_net_best_score],
    'Best_Alpha': [elastic_net_best_params['elasticnet__alpha']],
    'Best_L1_Ratio': [elastic_net_best_params['elasticnet__l1_ratio']]
})
```

### Step 3.3: Model Comparison

```python
# Calculate MAE from cross-validation for each model
ridge_mae_scores = -cross_val_score(ridge_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')
lasso_mae_scores = -cross_val_score(lasso_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')
elastic_net_mae_scores = -cross_val_score(elastic_net_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')

# Compare cross-validation scores
model_comparison = pd.DataFrame({
    'Model': ['Ridge', 'Lasso', 'Elastic Net'],
    'CV_R2_Score': [ridge_best_score, lasso_best_score, elastic_net_best_score],
    'CV_MAE_Mean': [
        ridge_mae_scores.mean(),
        lasso_mae_scores.mean(),
        elastic_net_mae_scores.mean()
    ],
    'CV_MAE_Std': [
        ridge_mae_scores.std(),
        lasso_mae_scores.std(),
        elastic_net_mae_scores.std()
    ]
})

model_comparison.sort_values('CV_R2_Score', ascending=False)
```

```python
# Extract coefficients from each model (on standardized scale)
ridge_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'Ridge_Coefficient': ridge_best_model.named_steps['ridge'].coef_
}).sort_values('Ridge_Coefficient', key=abs, ascending=False)

lasso_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'Lasso_Coefficient': lasso_best_model.named_steps['lasso'].coef_
}).sort_values('Lasso_Coefficient', key=abs, ascending=False)

elastic_net_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'ElasticNet_Coefficient': elastic_net_best_model.named_steps['elasticnet'].coef_
}).sort_values('ElasticNet_Coefficient', key=abs, ascending=False)

# Merge coefficient comparisons
coef_comparison = ridge_coefs.merge(lasso_coefs, on='Predictor').merge(elastic_net_coefs, on='Predictor')
coef_comparison
```

```python
# Count non-zero coefficients (feature selection in Lasso/Elastic Net)
feature_selection_summary = pd.DataFrame({
    'Model': ['Ridge', 'Lasso', 'Elastic Net'],
    'Total_Predictors': [len(X.columns), len(X.columns), len(X.columns)],
    'Non_Zero_Coefficients': [
        np.sum(ridge_best_model.named_steps['ridge'].coef_ != 0),
        np.sum(lasso_best_model.named_steps['lasso'].coef_ != 0),
        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ != 0)
    ],
    'Zero_Coefficients': [
        np.sum(ridge_best_model.named_steps['ridge'].coef_ == 0),
        np.sum(lasso_best_model.named_steps['lasso'].coef_ == 0),
        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ == 0)
    ]
})

feature_selection_summary
```

```python
primary_model = elastic_net_best_model
primary_model_name = 'Elastic Net'
```

## Phase 4: Model Diagnostics

### Step 4.2: Residual Analysis

```python
# Calculate predictions and residuals
y_pred = primary_model.predict(X)
y_pred = pd.Series(y_pred, index=y.index)
residuals = y - y_pred

# Calculate R² on full dataset (in-sample/training R²)
# Note: This is higher than cross-validation R² because the model is evaluated on the same
# data it was trained on. The cross-validation R² (~0.74) is a better estimate of 
# out-of-sample performance (generalization). The difference indicates some overfitting,
# which is expected with a small sample size (n~30-40 countries) and many predictors.
r2_full = primary_model.score(X, y)
print(f"R² on full dataset (in-sample): {r2_full:.4f}")
print(f"Cross-validation R² (out-of-sample): {elastic_net_best_score:.4f}")
print(f"MAE: {mean_absolute_error(y, y_pred):.4f} years")
```

```python
# Residual vs. Predicted values plot
plt.scatter(y_pred, residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
decorate(xlabel='Predicted HALE Gap (years)',
         ylabel='Residuals (years)',
         title='Residuals vs. Predicted Values (Elastic Net Model)')
```

```python
# Q-Q plot for residual normality
from scipy import stats

stats.probplot(residuals, dist="norm", plot=plt)
decorate(xlabel='Theoretical Quantiles',
         ylabel='Sample Quantiles',
         title='Q-Q Plot: Residual Normality Check')
```

```python
# Histogram of residuals
plt.hist(residuals, bins=15, color=AIBM_COLORS['crimson'], edgecolor='white', alpha=0.7)
plt.axvline(x=0, color='gray', linestyle='--', linewidth=1)
decorate(xlabel='Residuals (years)',
         ylabel='Frequency',
         title='Distribution of Residuals (Elastic Net Model)')
```

```python
# Residual statistics
residual_stats = pd.DataFrame({
    'Statistic': ['Mean', 'Std', 'Min', '25%', 'Median', '75%', 'Max', 'Skewness', 'Kurtosis'],
    'Value': [
        residuals.mean(),
        residuals.std(),
        residuals.min(),
        residuals.quantile(0.25),
        residuals.median(),
        residuals.quantile(0.75),
        residuals.max(),
        stats.skew(residuals),
        stats.kurtosis(residuals)
    ]
})
residual_stats
```

```python
# Identify potential outliers (residuals > 2 standard deviations)
outlier_threshold = 2 * residuals.std()
outliers = residuals[abs(residuals) > outlier_threshold]

outlier_df = pd.DataFrame({
    'Country': outliers.index,
    'Actual_HALE_Gap': y[outliers.index],
    'Predicted_HALE_Gap': y_pred[outliers.index],
    'Residual': outliers.values,
    'Abs_Residual': abs(outliers.values)
}).sort_values('Abs_Residual', ascending=False)

outlier_df if not outlier_df.empty else "No outliers detected (|residual| > 2 std)"
```

```python
# Residuals by country (sorted by absolute residual)
residuals_by_country = pd.DataFrame({
    'Country': residuals.index,
    'Actual_HALE_Gap': y.values,
    'Predicted_HALE_Gap': y_pred,
    'Residual': residuals.values,
    'Abs_Residual': abs(residuals.values)
}).sort_values('Abs_Residual', ascending=False)

residuals_by_country.head(10)
```

```python
# Check for patterns: plot residuals vs. each predictor (top predictors by absolute coefficient)
# Get top predictors by absolute coefficient value
coef_abs = pd.Series(elastic_net_best_model.named_steps['elasticnet'].coef_, index=X.columns).abs()
top_predictors = coef_abs.nlargest(5).index.values

fig, axes = plt.subplots(2, 3)
axes = axes.flatten()

for i, pred in enumerate(top_predictors):
    if i < len(axes):
        axes[i].scatter(X[pred], residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
        axes[i].axhline(y=0, color='gray', linestyle='--', linewidth=1)
        axes[i].set_xlabel(pred)
        axes[i].set_ylabel('Residuals')
        axes[i].set_title(f'Residuals vs. {pred}')
        axes[i].grid(True, alpha=0.3)

# Hide unused subplots
for i in range(len(top_predictors), len(axes)):
    axes[i].set_visible(False)

plt.tight_layout()
```

### Check for Influential Observations

```python
# For influence measures (Cook's distance, leverage), we fit an OLS model
# on the standardized data to calculate these diagnostics
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.outliers_influence import OLSInfluence

# Get standardized predictors (using the scaler from the pipeline)
X_std = primary_model.named_steps['scaler'].transform(X)

# Fit OLS model on standardized data
ols_model = OLS(y.values, X_std).fit()
influence = OLSInfluence(ols_model)

# Calculate Cook's distance and leverage
cooks_d = influence.cooks_distance[0]  # Cook's distance
leverage = influence.hat_matrix_diag  # Leverage (diagonal of hat matrix)

# Create DataFrame with influence measures
influence_df = pd.DataFrame({
    'Country': y.index,
    'Cook_Distance': cooks_d,
    'Leverage': leverage,
    'Residual': residuals.values,
    'Abs_Residual': abs(residuals.values)
}).sort_values('Cook_Distance', ascending=False)

influence_df
```

```python
# Identify influential observations
# Common thresholds:
# - Cook's distance > 4/n (where n is number of observations)
# - Leverage > 2*(p+1)/n (where p is number of predictors)
n = len(y)
p = X.shape[1]

cooks_threshold = 4 / n
leverage_threshold = 2 * (p + 1) / n

influential = influence_df[
    (influence_df['Cook_Distance'] > cooks_threshold) | 
    (influence_df['Leverage'] > leverage_threshold)
].copy()

print(f"Cook's distance threshold: {cooks_threshold:.4f}")
print(f"Leverage threshold: {leverage_threshold:.4f}")
print(f"\nNumber of influential observations: {len(influential)}")

influential if not influential.empty else "No influential observations detected"
```

```python
# Plot Cook's distance with country codes on y-axis
plt.scatter(influence_df['Cook_Distance'], range(len(influence_df)), 
           color=AIBM_COLORS['crimson'], alpha=0.6)
plt.axvline(x=cooks_threshold, color='gray', linestyle='--', linewidth=1, label=f'Threshold ({cooks_threshold:.4f})')
plt.yticks(range(len(influence_df)), influence_df['Country'])
decorate(xlabel="Cook's Distance",
         ylabel='Country Code',
         title="Cook's Distance for Each Country")
plt.legend()
```

```python
# Plot Leverage with country codes on y-axis
plt.scatter(influence_df['Leverage'], range(len(influence_df)), 
           color=AIBM_COLORS['crimson'], alpha=0.6)
plt.axvline(x=leverage_threshold, color='gray', linestyle='--', linewidth=1, label=f'Threshold ({leverage_threshold:.4f})')
plt.yticks(range(len(influence_df)), influence_df['Country'])
decorate(xlabel='Leverage',
         ylabel='Country Code',
         title='Leverage for Each Country')
plt.legend()
```

```python
# Plot Cook's distance vs. Leverage
plt.scatter(influence_df['Leverage'], influence_df['Cook_Distance'], 
           color=AIBM_COLORS['crimson'], alpha=0.6)
plt.axhline(y=cooks_threshold, color='gray', linestyle='--', linewidth=1, alpha=0.5)
plt.axvline(x=leverage_threshold, color='gray', linestyle='--', linewidth=1, alpha=0.5)

# Highlight influential observations
if not influential.empty:
    plt.scatter(influential['Leverage'], influential['Cook_Distance'], 
               color=AIBM_COLORS['blue'], s=100, alpha=0.8, label='Influential')
    # Add country labels for influential observations
    for idx, row in influential.iterrows():
        plt.annotate(row['Country'], 
                    (row['Leverage'], row['Cook_Distance']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

decorate(xlabel='Leverage',
         ylabel="Cook's Distance",
         title="Cook's Distance vs. Leverage")
plt.legend()
```

```python
# Summary of influential observations
if not influential.empty:
    print("Influential Observations Summary:")
    print(f"Total: {len(influential)}")
    print(f"\nBy Cook's Distance > {cooks_threshold:.4f}:")
    high_cooks = influence_df[influence_df['Cook_Distance'] > cooks_threshold]
    print(f"  {len(high_cooks)} countries: {sorted(high_cooks['Country'].tolist())}")
    
    print(f"\nBy Leverage > {leverage_threshold:.4f}:")
    high_leverage = influence_df[influence_df['Leverage'] > leverage_threshold]
    print(f"  {len(high_leverage)} countries: {sorted(high_leverage['Country'].tolist())}")
else:
    print("No influential observations detected using standard thresholds.")
```

## Summary: Indicator Analysis and Counterfactual Predictions

### Extract Elastic Net Coefficients

```python
# Get coefficients from Elastic Net model (on standardized scale)
elastic_net_coefs_dict = dict(zip(X.columns, elastic_net_best_model.named_steps['elasticnet'].coef_))

# Get the scaler to understand standardization
scaler = elastic_net_best_model.named_steps['scaler']
```

### Calculate Summary for Each Indicator

```python
# Group predictors by indicator
indicator_summary = []

# Indicators with both male and female values
# Get indicator names from predictor_dfs, excluding maternal mortality (female-only)
male_female_indicators = [name for name in predictor_dfs.keys() 
                          if name != 'MaternalMortalityRatio']

for indicator in male_female_indicators:
    male_col = f'{indicator}_Male'
    female_col = f'{indicator}_Female'
    
    if male_col in predictors.columns and female_col in predictors.columns:
        # Get coefficients (on standardized scale)
        coef_male = elastic_net_coefs_dict.get(male_col, 0)
        coef_female = elastic_net_coefs_dict.get(female_col, 0)
        
        # Calculate actual gap (Male - Female) from raw data
        # Use mean across all countries for summary
        male_mean = predictors[male_col].mean()
        female_mean = predictors[female_col].mean()
        actual_gap = male_mean - female_mean
        
        # Calculate predicted change in HALE gap if male = female
        # The model uses standardized predictors, so we need to:
        # 1. Calculate standardized values for current (male_mean, female_mean)
        # 2. Calculate standardized values if male = female (both = female_mean)
        # 3. Calculate the difference
        
        std_male = predictors[male_col].std()
        std_female = predictors[female_col].std()
        
        if std_male > 0 and std_female > 0:
            # Current standardized values (mean of column is used for standardization)
            # Since we're using the mean, current standardized values are approximately 0
            # But we need the actual standardized values for the mean values
            male_std_current = (male_mean - male_mean) / std_male  # = 0
            female_std_current = (female_mean - female_mean) / std_female  # = 0
            
            # If male = female (both equal to female_mean), calculate new standardized values
            male_std_new = (female_mean - male_mean) / std_male
            female_std_new = (female_mean - female_mean) / std_female  # = 0 (unchanged)
            
            # Change in standardized values
            delta_male_std = male_std_new - male_std_current
            delta_female_std = female_std_new - female_std_current  # = 0
            
            # Predicted change in HALE gap
            predicted_change = coef_male * delta_male_std + coef_female * delta_female_std
        else:
            predicted_change = 0
        
        indicator_summary.append({
            'Indicator': indicator,
            'Actual_Gap_Male_Minus_Female': actual_gap,
            'Coefficient_Male': coef_male,
            'Coefficient_Female': coef_female,
            'Predicted_Change_in_HALE_Gap_Years': predicted_change,
            'Male_Mean': male_mean,
            'Female_Mean': female_mean
        })

# Add female-only indicators
female_only_indicators = ['MaternalMortalityRatio']
for indicator in female_only_indicators:
    female_col = f'{indicator}_Female'
    
    if female_col in predictors.columns:
        coef_female = elastic_net_coefs_dict.get(female_col, 0)
        female_mean = predictors[female_col].mean()
        
        indicator_summary.append({
            'Indicator': indicator,
            'Actual_Gap_Male_Minus_Female': np.nan,  # No gap (female-only)
            'Coefficient_Male': np.nan,
            'Coefficient_Female': coef_female,
            'Predicted_Change_in_HALE_Gap_Years': np.nan,  # Not applicable
            'Male_Mean': np.nan,
            'Female_Mean': female_mean
        })

summary_df = pd.DataFrame(indicator_summary)
summary_df = summary_df.sort_values('Predicted_Change_in_HALE_Gap_Years', 
                                    key=abs, ascending=False, na_position='last')
summary_df
```

### Interpretation

```python
# Add interpretation column
summary_df['Interpretation'] = summary_df.apply(lambda row: 
    f"If {row['Indicator']} male value equals female value, "
    f"predicted HALE gap changes by {row['Predicted_Change_in_HALE_Gap_Years']:.3f} years"
    if not pd.isna(row['Predicted_Change_in_HALE_Gap_Years']) 
    else "Female-only indicator (no male comparison)", axis=1)

# Display formatted summary
display_cols = ['Indicator', 'Actual_Gap_Male_Minus_Female', 'Coefficient_Male', 
                'Coefficient_Female', 'Predicted_Change_in_HALE_Gap_Years', 'Interpretation']
summary_df[display_cols]
```

### Top Contributors to HALE Gap

```python
# Show indicators with largest predicted impact (absolute value)
top_contributors = summary_df.sort_values('Predicted_Change_in_HALE_Gap_Years', 
                                          key=abs, ascending=False)
top_contributors[['Indicator', 'Actual_Gap_Male_Minus_Female', 
                  'Coefficient_Male', 'Coefficient_Female', 
                  'Predicted_Change_in_HALE_Gap_Years']]
```

## Predictor Importance Analysis

### Calculate Feature Importance

```python
# Feature importance = |coefficient| × std(predictor)
# This measures the contribution of each predictor to the HALE gap variation
# Since predictors are standardized, we multiply by the original standard deviation
# to get importance on the original scale

predictor_importance = []

for predictor in X.columns:
    coef = elastic_net_coefs_dict.get(predictor, 0)
    
    # Get the original (unstandardized) standard deviation
    # The scaler was fit on X, so we can get the std from predictors DataFrame
    if predictor in predictors.columns:
        std_original = predictors[predictor].std()
        importance = abs(coef) * std_original
    else:
        std_original = 0
        importance = 0
    
    predictor_importance.append({
        'Predictor': predictor,
        'Coefficient': coef,
        'Std_Original': std_original,
        'Importance': importance
    })

importance_df = pd.DataFrame(predictor_importance).sort_values('Importance', ascending=False)
importance_df
```

### Visualize Predictor Importance

```python
# Create bar chart of top predictors by importance
top_n = 15
top_importance = importance_df.head(top_n)

colors = [AIBM_COLORS['crimson'] if x > 0 else AIBM_COLORS['blue'] 
          for x in top_importance['Coefficient']]
plt.barh(range(len(top_importance)), top_importance['Importance'], color=colors)
plt.yticks(range(len(top_importance)), top_importance['Predictor'])
plt.gca().invert_yaxis()
decorate(xlabel='Importance (|Coefficient| × Std)',
         ylabel='Predictor',
         title=f'Top {top_n} Predictors by Importance (Elastic Net Model)')
```

### Importance by Indicator

```python
# Aggregate importance by indicator (sum of male and female importance)
indicator_importance = {}

for indicator in male_female_indicators:
    male_col = f'{indicator}_Male'
    female_col = f'{indicator}_Female'
    
    male_imp = importance_df[importance_df['Predictor'] == male_col]['Importance'].values
    female_imp = importance_df[importance_df['Predictor'] == female_col]['Importance'].values
    
    if len(male_imp) > 0 and len(female_imp) > 0:
        total_importance = male_imp[0] + female_imp[0]
        indicator_importance[indicator] = {
            'Male_Importance': male_imp[0],
            'Female_Importance': female_imp[0],
            'Total_Importance': total_importance
        }

# Add female-only indicators
for indicator in female_only_indicators:
    female_col = f'{indicator}_Female'
    female_imp = importance_df[importance_df['Predictor'] == female_col]['Importance'].values
    
    if len(female_imp) > 0:
        indicator_importance[indicator] = {
            'Male_Importance': np.nan,
            'Female_Importance': female_imp[0],
            'Total_Importance': female_imp[0]
        }

indicator_importance_df = pd.DataFrame(indicator_importance).T
indicator_importance_df = indicator_importance_df.sort_values('Total_Importance', ascending=False)
indicator_importance_df
```

### Visualize Indicator Importance

```python
# Bar chart of indicator-level importance
colors_bar = [AIBM_COLORS['crimson'] for _ in range(len(indicator_importance_df))]
plt.barh(range(len(indicator_importance_df)), indicator_importance_df['Total_Importance'], 
         color=colors_bar)
plt.yticks(range(len(indicator_importance_df)), indicator_importance_df.index)
plt.gca().invert_yaxis()
decorate(xlabel='Total Importance (Sum of Male + Female)',
         ylabel='Indicator',
         title='Indicator Importance (Elastic Net Model)')
```

## Permutation Importance Analysis

Permutation importance measures how much the model's performance decreases when a feature's values are randomly shuffled. This provides an alternative measure of feature importance that is model-agnostic and accounts for feature interactions.

### Calculate Permutation Importance

```python
from sklearn.inspection import permutation_importance

# Calculate permutation importance using the primary model
# Use the same cross-validation setup for consistency
perm_importance = permutation_importance(
    primary_model, X, y,
    scoring='r2',
    n_repeats=10,  # Number of times to permute each feature
    random_state=42,
    n_jobs=-1
)

# Create DataFrame with permutation importance results
perm_importance_df = pd.DataFrame({
    'Predictor': X.columns,
    'Permutation_Importance_Mean': perm_importance.importances_mean,
    'Permutation_Importance_Std': perm_importance.importances_std
}).sort_values('Permutation_Importance_Mean', ascending=False)

perm_importance_df
```

### Visualize Permutation Importance

```python
# Create bar chart of top predictors by permutation importance
top_n = 15
top_perm_importance = perm_importance_df.head(top_n)

plt.barh(range(len(top_perm_importance)), 
         top_perm_importance['Permutation_Importance_Mean'],
         xerr=top_perm_importance['Permutation_Importance_Std'],
         color=AIBM_COLORS['crimson'],
         capsize=3)
plt.yticks(range(len(top_perm_importance)), top_perm_importance['Predictor'])
plt.gca().invert_yaxis()
decorate(xlabel='Permutation Importance (Mean Decrease in R²)',
         ylabel='Predictor',
         title=f'Top {top_n} Predictors by Permutation Importance (Elastic Net Model)')
```

### Compare Permutation Importance with Coefficient-Based Importance

```python
# Merge permutation importance with coefficient-based importance
comparison_df = importance_df.merge(
    perm_importance_df[['Predictor', 'Permutation_Importance_Mean']],
    on='Predictor',
    how='inner'
)

# Calculate correlation between the two importance measures
correlation = comparison_df['Importance'].corr(comparison_df['Permutation_Importance_Mean'])

# Create scatter plot comparing the two importance measures
plt.scatter(comparison_df['Importance'], 
           comparison_df['Permutation_Importance_Mean'],
           color=AIBM_COLORS['crimson'], alpha=0.6)
decorate(xlabel='Coefficient-Based Importance (|Coefficient| × Std)',
         ylabel='Permutation Importance (Mean Decrease in R²)',
         title=f'Comparison of Importance Measures\n(Correlation: {correlation:.3f})')
```

### Permutation Importance by Indicator

```python
# Aggregate permutation importance by indicator (sum of male and female importance)
indicator_perm_importance = {}

for indicator in male_female_indicators:
    male_col = f'{indicator}_Male'
    female_col = f'{indicator}_Female'
    
    male_perm = perm_importance_df[perm_importance_df['Predictor'] == male_col]['Permutation_Importance_Mean'].values
    female_perm = perm_importance_df[perm_importance_df['Predictor'] == female_col]['Permutation_Importance_Mean'].values
    
    if len(male_perm) > 0 and len(female_perm) > 0:
        total_perm_importance = male_perm[0] + female_perm[0]
        indicator_perm_importance[indicator] = {
            'Male_Perm_Importance': male_perm[0],
            'Female_Perm_Importance': female_perm[0],
            'Total_Perm_Importance': total_perm_importance
        }

# Add female-only indicators
for indicator in female_only_indicators:
    female_col = f'{indicator}_Female'
    female_perm = perm_importance_df[perm_importance_df['Predictor'] == female_col]['Permutation_Importance_Mean'].values
    
    if len(female_perm) > 0:
        indicator_perm_importance[indicator] = {
            'Male_Perm_Importance': np.nan,
            'Female_Perm_Importance': female_perm[0],
            'Total_Perm_Importance': female_perm[0]
        }

indicator_perm_importance_df = pd.DataFrame(indicator_perm_importance).T
indicator_perm_importance_df = indicator_perm_importance_df.sort_values('Total_Perm_Importance', ascending=False)
indicator_perm_importance_df
```

### Visualize Indicator-Level Permutation Importance

```python
# Bar chart of indicator-level permutation importance
colors_bar = [AIBM_COLORS['crimson'] for _ in range(len(indicator_perm_importance_df))]
plt.barh(range(len(indicator_perm_importance_df)), 
         indicator_perm_importance_df['Total_Perm_Importance'], 
         color=colors_bar)
plt.yticks(range(len(indicator_perm_importance_df)), indicator_perm_importance_df.index)
plt.gca().invert_yaxis()
decorate(xlabel='Total Permutation Importance (Sum of Male + Female)',
         ylabel='Indicator',
         title='Indicator Permutation Importance (Elastic Net Model)')
```

### Compare Coefficient-Based vs Permutation Importance by Indicator

```python
# Merge indicator-level importance from both methods
indicator_comparison = indicator_importance_df.merge(
    indicator_perm_importance_df[['Total_Perm_Importance']],
    left_index=True,
    right_index=True,
    how='inner'
)

# Calculate correlation
indicator_correlation = indicator_comparison['Total_Importance'].corr(
    indicator_comparison['Total_Perm_Importance']
)

# Create scatter plot
plt.scatter(indicator_comparison['Total_Importance'],
           indicator_comparison['Total_Perm_Importance'],
           color=AIBM_COLORS['crimson'], alpha=0.6)
decorate(xlabel='Coefficient-Based Total Importance',
         ylabel='Permutation Total Importance',
         title=f'Indicator-Level Importance Comparison\n(Correlation: {indicator_correlation:.3f})')
```

```python

```

```python

```
