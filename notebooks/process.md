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
- `interim/panel_hale.h5` — HALE panel (all predictors, for bayesian_model)
- `interim/panel_le.h5` — LE panel (all predictors, for bayesian_model)

**Run headlessly (jupytext + papermill):** from a terminal (adjust `~/LifeExpectancy` if your clone is elsewhere). Paste into a shell; do not add this as an executable notebook cell.

```
cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && \
  jupytext --to ipynb process.md --output process.ipynb && \
  papermill process.ipynb process_executed.ipynb
```

The executed notebook is `notebooks/process_executed.ipynb`.

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
    compute_gender_gap, summarize_gap, scatter_plot,
    get_oecd, summarize_years, plot_cdfs, plot_distributions,
    column_name_mapping, oecd_codes,
    load_ihme_indicator, raw_to_temporal_gaps,
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
log_path = f'logs/process_{cutoff_year}.txt'
log_file = open(log_path, 'w')

log_file.write("Data Processing Log\n")
log_file.write("=" * 80 + "\n")
log_file.write(f"Notebook: process.md\n")
log_file.write(f"Cutoff Year: {cutoff_year}\n")
log_file.write(f"Started: {pd.Timestamp.now()}\n")
log_file.write("=" * 80 + "\n\n")

set_log_file(log_file)
print(f"Log file opened: {log_path}")
```

## Load Target Data (IHME HALE, OWID LE)

IHME HALE and OWID LE are used for both the panel dataset and the cross-sectional Data Preparation. See `who_data.md` for WHO vs IHME/OWID comparison and decision rationale.

```python
# IHME HALE
ihme_hale_raw = pd.read_csv('../data/IHME-GBD_2023_DATA-fc42b373-1.csv')
ihme_hale = convert_ihme_hale_to_who_format(ihme_hale_raw)
hale_gap = summarize_gap(ihme_hale, 'HALE_Years', cutoff_year=cutoff_year)
hale_gap['HALE_gap'] = hale_gap['HALE_Years_Female'] - hale_gap['HALE_Years_Male']
hale_oecd = get_oecd(hale_gap)
ihme_hale_oecd = hale_oecd

# OWID Life Expectancy
owid_le_raw = pd.read_csv('../data/owid_life_expectancy_by_sex.csv')
owid_le_temporal = convert_owid_le_to_temporal_format(owid_le_raw, min_year=2000, max_year=2023)
le_gap = summarize_gap(owid_le_temporal, 'LifeExpectancy_Years', cutoff_year=cutoff_year)
le_gap['LifeExpectancy_gap'] = le_gap['LifeExpectancy_Years_Female'] - le_gap['LifeExpectancy_Years_Male']
le_oecd = get_oecd(le_gap)
```

## NOTE: WHO predictor sections removed

The WHO predictor sections (smoking, suicide, alcohol, poisoning, road traffic, maternal mortality, homicide, IPV, U5MR, cardiovascular, diabetes, NCD mortality) have been removed. We use IHME data for all predictors as it provides better temporal coverage (1990-2023 vs 2000-2021 for WHO).

## IHME Predictor Indicators

### Load IHME Indicators

Each indicator is loaded once. Raw versions are used for EDA (summarize_gap, plots); temporal versions (Mid_*, Gap_*) are used for the panel merge.

```python
# Load all IHME indicators once (max_year=2023)
def _load_ihme(name, base, value_col, code, desc, age_filter='All ages'):
    """Load indicator, create raw (renamed) and temporal versions."""
    raw = load_ihme_indicator(
        f'../data/{base}_male.csv', f'../data/{base}_female.csv',
        value_col_name=value_col, indicator_code=code, indicator_name=desc,
        max_year=2023, age_filter=age_filter
    )
    renamed = raw.rename(columns=column_name_mapping)
    temporal = raw_to_temporal_gaps(raw, value_col)
    return renamed, temporal

# Standard indicators (All ages)
drug_disorders, drug_disorders_temporal = _load_ihme(
    'drug_disorders', 'ihme_drug_disorder_deaths', 'DrugDisorderDeathRate',
    'IHME_DRUG_DISORDERS', 'Drug use disorders')
diabetes_ihme, diabetes_temporal = _load_ihme(
    'diabetes', 'ihme_diabetes_deaths', 'DiabetesDeathRate',
    'IHME_DIABETES_TYPE2', 'Diabetes mellitus type 2')
cardiovascular_ihme, cardiovascular_temporal = _load_ihme(
    'cardiovascular', 'ihme_cardiovascular_deaths', 'CardioDeathRate',
    'IHME_CARDIOVASCULAR', 'Cardiovascular diseases')
neoplasms_ihme, neoplasms_temporal = _load_ihme(
    'neoplasms', 'ihme_neoplasms_deaths', 'NeoplasmsDeathRate',
    'IHME_NEOPLASMS', 'Neoplasms (cancer)')
chronic_respiratory_ihme, chronic_respiratory_temporal = _load_ihme(
    'chronic_respiratory', 'ihme_chronic_respiratory_deaths', 'ChronicRespiratoryDeathRate',
    'IHME_CHRONIC_RESPIRATORY', 'Chronic respiratory diseases')
liver_disease_ihme, liver_disease_temporal = _load_ihme(
    'liver_disease', 'ihme_liver_disease_deaths', 'LiverDiseaseDeathRate',
    'IHME_LIVER_DISEASE', 'Liver disease')
covid19_ihme, covid_temporal = _load_ihme(
    'covid19', 'ihme_covid19_deaths', 'COVID19DeathRate',
    'IHME_COVID19', 'COVID-19')
unintentional_injuries_ihme, unintentional_injuries_temporal = _load_ihme(
    'unintentional_injuries', 'ihme_unintentional_injuries_deaths', 'UnintentionalInjuriesDeathRate',
    'IHME_UNINTENTIONAL_INJURIES', 'Unintentional injuries')
conflict_terrorism_ihme, conflict_terrorism_temporal = _load_ihme(
    'conflict_terrorism', 'ihme_conflict_and_terrorism_deaths', 'ConflictAndTerrorismDeathRate',
    'IHME_CONFLICT_TERRORISM', 'Conflict and terrorism')
alcohol_use_disorders_ihme, alcohol_temporal = _load_ihme(
    'alcohol', 'ihme_alcohol_use_disorders_deaths', 'AlcoholUseDisordersDeathRate',
    'IHME_ALCOHOL_USE_DISORDERS', 'Alcohol use disorders')
self_harm_ihme, self_harm_temporal = _load_ihme(
    'self_harm', 'ihme_self_harm_deaths', 'SelfHarmDeathRate',
    'IHME_SELF_HARM', 'Self-harm (suicide)')
interpersonal_violence_ihme, interpersonal_violence_temporal = _load_ihme(
    'interpersonal_violence', 'ihme_interpersonal_violence_deaths', 'InterpersonalViolenceDeathRate',
    'IHME_INTERPERSONAL_VIOLENCE', 'Interpersonal violence (homicide)')
road_injuries_ihme, road_injuries_temporal = _load_ihme(
    'road_injuries', 'ihme_road_injuries_deaths', 'RoadInjuriesDeathRate',
    'IHME_ROAD_INJURIES', 'Road injuries')

# All-cause under 5 (age_filter='<5 years')
all_causes_under5_ihme, all_causes_under5_temporal = _load_ihme(
    'all_causes_under5', 'ihme_all_causes_under5_deaths', 'AllCausesUnder5DeathRate',
    'IHME_ALL_CAUSES_UNDER5', 'All-cause deaths under 5 years', age_filter='<5 years')

print("Loaded 15 IHME indicators (raw + temporal)")
```

### Drug Use Disorders (IHME) 

**Drug use disorder death rates (per 100,000 population)** - Deaths from drug use disorders, including overdoses, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Drug overdoses, particularly opioid overdoses, are a major cause of death in some OECD countries (especially the US) and may contribute significantly to the HALE gender gap. **This IHME indicator is used in the model** instead of WHO Poisoning because it provides better temporal coverage (1990-2023 vs 2000-2021 for WHO) and captures drug overdose deaths more comprehensively. This indicator captures overdose deaths that may not be fully captured in the WHO poisoning indicator. Data includes separate male and female values, allowing for gender gap analysis.

```python
drug_disorders.head()
```

```python
col = column_name_mapping.get('DrugDisorderDeathRate', 'DrugDisorder')
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
diabetes_ihme.head()
```

```python
col = column_name_mapping.get('DiabetesDeathRate', 'Diabetes')
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
cardiovascular_ihme.head()
```

```python
col = column_name_mapping.get('CardioDeathRate', 'Cardiovascular')
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
neoplasms_ihme.head()
```

```python
col = column_name_mapping.get('NeoplasmsDeathRate', 'Neoplasms')
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
chronic_respiratory_ihme.head()
```

```python
col = column_name_mapping.get('ChronicRespiratoryDeathRate', 'ChronicRespiratory')
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
liver_disease_ihme.head()
```

```python
col = column_name_mapping.get('LiverDiseaseDeathRate', 'LiverDisease')
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
covid19_ihme.head()
```

```python
col = column_name_mapping.get('COVID19DeathRate', 'COVID')
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
unintentional_injuries_ihme = load_ihme_indicator(
    filename_male, filename_female,
    value_col_name='UnintentionalInjuriesDeathRate',
    indicator_code='IHME_UNINTENTIONAL_INJURIES',
    indicator_name='Unintentional injuries, death rate per 100,000',
    max_year=2023
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

### Conflict and Terrorism (IHME)

**Conflict and terrorism death rates (per 100,000 population)** - Deaths from conflict and terrorism, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Conflict and terrorism deaths may contribute to the HALE/LE gender gap, as men typically have higher exposure to conflict-related mortality (military, combat, terrorism). This indicator provides death rates with excellent temporal coverage (1990-2023, 34 years) and OECD country coverage. Rates are generally very low in OECD countries but may be relevant for understanding gender gaps in countries with historical conflict exposure. Data includes separate male and female values, allowing for gender gap analysis.

```python
conflict_terrorism_ihme.head()
```

```python
col = column_name_mapping.get('ConflictAndTerrorismDeathRate', 'ConflictTerrorism')
conflict_terrorism_ihme_gap = summarize_gap(conflict_terrorism_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/conflict_terrorism_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(conflict_terrorism_ihme_gap, indicator_name='ConflictTerrorism')
plt.savefig('figs/conflict_terrorism_distributions.png', dpi=300, bbox_inches='tight')
```

### Alcohol Use Disorders (IHME) 

**Alcohol use disorders death rates (per 100,000 population)** - Deaths from alcohol use disorders, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Alcohol use disorders are a significant cause of death and may contribute to the HALE gender gap. Men typically have higher rates of alcohol-related mortality than women. This indicator provides comprehensive alcohol use disorder death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO alcohol-attributable death rate indicator (SA_0000001832) which only has data for 2019. **This IHME version is used in the model** because it provides much better temporal coverage, allowing for temporal analysis and more recent data. Data includes separate male and female values, allowing for gender gap analysis.

```python
alcohol_use_disorders_ihme.head()
```

```python
col = column_name_mapping.get('AlcoholUseDisordersDeathRate', 'Alcohol')
alcohol_use_disorders_ihme_gap = summarize_gap(alcohol_use_disorders_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/alcohol_ihme_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(alcohol_use_disorders_ihme_gap, indicator_name='Alcohol')
plt.savefig('figs/alcohol_ihme_distributions.png', dpi=300, bbox_inches='tight')
```

### Self-Harm (IHME)

**Self-harm (suicide) death rates (per 100,000 population)** - Deaths from self-harm (suicide), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Self-harm (suicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher suicide rates than women in most countries. This indicator provides comprehensive self-harm death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO suicide rate indicator (MH_12) which has data for 2000-2021. **This IHME version is used in the model** because it provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
self_harm_ihme.head()
```

```python
col = column_name_mapping.get('SelfHarmDeathRate', 'Suicide')
self_harm_ihme_gap = summarize_gap(self_harm_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/self_harm_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(self_harm_ihme_gap, indicator_name='Suicide')
plt.savefig('figs/self_harm_distributions.png', dpi=300, bbox_inches='tight')
```

### Interpersonal Violence (IHME)

**Interpersonal violence (homicide) death rates (per 100,000 population)** - Deaths from interpersonal violence (homicide), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Interpersonal violence (homicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher homicide rates than women in most countries. This indicator provides comprehensive interpersonal violence death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO homicide rate indicator (VIOLENCE_HOMICIDERATE) which has data for 2000-2021. **This IHME version is used in the model** because it provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
interpersonal_violence_ihme.head()
```

```python
col = column_name_mapping.get('InterpersonalViolenceDeathRate', 'Homicide')
interpersonal_violence_ihme_gap = summarize_gap(interpersonal_violence_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/interpersonal_violence_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(interpersonal_violence_ihme_gap, indicator_name='Homicide')
plt.savefig('figs/interpersonal_violence_distributions.png', dpi=300, bbox_inches='tight')
```

### Road Injuries (IHME)

**Road injuries (road traffic crash) death rates (per 100,000 population)** - Deaths from road injuries (road traffic crashes), from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: Road injuries (road traffic crashes) are a significant cause of death and contribute to the HALE gender gap. Men typically have 2-4 times higher road traffic death rates than women in most countries due to higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. This indicator provides comprehensive road injury death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO road traffic crash death rate indicator (SA_0000001459) which only has data for 2019. **This IHME version is used in the model** because it provides much better temporal coverage (1990-2023 vs 2019 only) and consistent methodology with other IHME indicators. Data includes separate male and female values, allowing for gender gap analysis.

```python
road_injuries_ihme.head()
```

```python
col = column_name_mapping.get('RoadInjuriesDeathRate', 'RoadTraffic')
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

### All-Cause Deaths Under 5 Years of Age (IHME)

**All-cause deaths under 5 years of age (per 100,000 population)** - Deaths from all causes for children under 5 years of age, from IHME Global Burden of Disease data.

**Data Source**: IHME Global Burden of Disease (https://vizhub.healthdata.org/gbd-compare/)  
**Relevance**: All-cause mortality for children under 5 years of age is relevant to the HALE gender gap because HALE is calculated from birth, so early-life mortality directly affects HALE calculations. If child mortality differs by gender, it directly contributes to the HALE gender gap. Infant and child mortality is typically higher in males (biological vulnerability + some behavioral factors). **This IHME version is used in the model** because it provides better temporal coverage (1990-2023) and consistent methodology with other IHME indicators. This is different from the WHO under-five mortality rate (U5MR, MDG_0000000007) which measures deaths per 1,000 live births. The IHME indicator measures deaths per 100,000 population, providing a complementary perspective on early-life mortality. Data includes separate male and female values, allowing for gender gap analysis.

```python
all_causes_under5_ihme.head()
```

```python
col = column_name_mapping.get('AllCausesUnder5DeathRate', 'Childhood')
all_causes_under5_ihme_gap = summarize_gap(all_causes_under5_ihme, col, cutoff_year=cutoff_year)
plt.savefig('figs/all_causes_under5_scatter.png', dpi=300, bbox_inches='tight')
```

```python
plot_distributions(all_causes_under5_ihme_gap, indicator_name='Childhood')
plt.savefig('figs/all_causes_under5_distributions.png', dpi=300, bbox_inches='tight')
```



## Data Preparation for Regression Analysis

### Prepare Target Variables (HALE and Life Expectancy Gender Gaps)

Target variables created from IHME HALE and OWID LE (loaded above).

```python
hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].describe()
```

```python
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
# Prepare all data; bayesian_model.md filters which predictors to use
indicator_datasets = {
    'Alcohol': alcohol_use_disorders_ihme_gap,
    'ChronicRespiratory': chronic_respiratory_ihme_gap,
    'UnintentionalInjury': unintentional_injuries_ihme_gap,
    'RoadTraffic': road_injuries_ihme_gap,
    'Diabetes': diabetes_ihme_gap,
    'Cardiovascular': cardiovascular_ihme_gap,
    'Childhood': all_causes_under5_ihme_gap,
    'ConflictTerrorism': conflict_terrorism_ihme_gap,
    'DrugDisorder': drug_disorders_gap,
    'Homicide': interpersonal_violence_ihme_gap,
    'Suicide': self_harm_ihme_gap,
    'MaternalDisorders': maternal_disorders_ihme_gap,
    'Neoplasms': neoplasms_ihme_gap,
    'LiverDisease': liver_disease_ihme_gap,
    'COVID': covid19_ihme_gap,
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
# (Excluded countries documented in bayesian_model.md when it filters)
analysis_complete = analysis_df.dropna()
```

```python
# Separate target and predictors (IHME HALE, OWID LE)
target_hale = analysis_complete['HALE_gap']
target_le = analysis_complete['LifeExpectancy_gap']

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
    'Target_Variables': ['HALE_gap (IHME), LifeExpectancy_gap (OWID)'],
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
    
    # Handle special case: MaternalDisorders (female-only, no Gap/Mid columns)
    elif indicator_name == 'MaternalDisorders':
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
# Special case: MaternalDisorders uses Female column for both
# Corr LE = LE gender gap vs predictor (gap or female rate); Corr LE male/female = LE at birth vs Mid (rates)
le_male_level = analysis_complete['LifeExpectancy_Years_Male']
le_female_level = analysis_complete['LifeExpectancy_Years_Female']

predictor_rates['Corr HALE'] = np.nan
predictor_rates['Corr LE'] = np.nan
predictor_rates['Corr LE male'] = np.nan
predictor_rates['Corr LE female'] = np.nan
predictor_gaps['Corr HALE'] = np.nan
predictor_gaps['Corr LE'] = np.nan

for idx, indicator in enumerate(predictor_rates['Indicator']):
    if indicator == 'MaternalDisorders':
        female_col = 'MaternalDisorders_Female'
        if female_col in predictors.columns:
            predictor_rates.loc[idx, 'Corr HALE'] = predictors[female_col].corr(target_hale)
            predictor_rates.loc[idx, 'Corr LE'] = predictors[female_col].corr(target_le)
            predictor_rates.loc[idx, 'Corr LE male'] = predictors[female_col].corr(le_male_level)
            predictor_rates.loc[idx, 'Corr LE female'] = predictors[female_col].corr(le_female_level)
            predictor_gaps.loc[idx, 'Corr HALE'] = predictors[female_col].corr(target_hale)
            predictor_gaps.loc[idx, 'Corr LE'] = predictors[female_col].corr(target_le)
        else:
            predictor_rates.loc[idx, 'Corr HALE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE male'] = np.nan
            predictor_rates.loc[idx, 'Corr LE female'] = np.nan
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
            predictor_rates.loc[idx, 'Corr LE male'] = predictors[mid_col].corr(le_male_level)
            predictor_rates.loc[idx, 'Corr LE female'] = predictors[mid_col].corr(le_female_level)
        else:
            predictor_rates.loc[idx, 'Corr HALE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE'] = np.nan
            predictor_rates.loc[idx, 'Corr LE male'] = np.nan
            predictor_rates.loc[idx, 'Corr LE female'] = np.nan
        
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
    if indicator == 'MaternalDisorders':
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
# Get all Gap_ columns (excluding MaternalDisorders which doesn't have a Gap column)
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

**Purpose**: OWID LE (loaded above) provides extended temporal coverage through 2023. Used for both Data Preparation and the panel.

```python
# OWID LE already loaded above; show structure
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

This section creates panel datasets with temporal data for all predictors, used by `bayesian_model.md`.

### Helper Functions

```python
def compute_temporal_gaps(df, value_col, sexes=['Male', 'Female']):
    """
    Compute gender gaps for all years (not just most recent).
    Wrapper around compute_gender_gap that preserves temporal structure.
    """
    return compute_gender_gap(df, value_col, sexes)


def load_maternal_disorders_temporal(max_year=2023):
    """Load IHME maternal disorders (female-only) and create temporal panel structure."""
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    ihme_country_mapping = {'Republic of Korea': 'South Korea', 'United States of America': 'United States'}
    df = pd.read_csv('../data/ihme_maternal_disorders_deaths_female.csv')
    df = df[(df['Year'] >= 2000) & (df['Year'] <= max_year)]
    if 'Age' in df.columns:
        df = df[df['Age'] == 'All ages']
    df['Location'] = df['Location'].replace(ihme_country_mapping)
    df['Code'] = df['Location'].map(who_country_to_code)
    df = df[df['Code'].notna()].copy()
    out = df[['Code', 'Year', 'Value']].copy()
    out = out.rename(columns={'Value': 'MaternalDisorders_Female'})
    out['Mid_MaternalDisorders'] = out['MaternalDisorders_Female']
    out['Gap_MaternalDisorders'] = out['MaternalDisorders_Female']
    return out[['Code', 'Year', 'Mid_MaternalDisorders', 'Gap_MaternalDisorders']]


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

# Filter to OECD countries (year filtering done in bayesian_model.md)
le_temporal = le_temporal[le_temporal['Code'].isin(oecd_codes)].copy()

print(f"LE temporal data: {le_temporal.shape}")
print(f"Years: {le_temporal['Year'].min():.0f} - {le_temporal['Year'].max():.0f}")
print(f"Countries: {le_temporal['Code'].nunique()}")
```

### IHME Predictor Indicators (Temporal)

IHME predictors are loaded once in the consolidated "Load All IHME Indicators (Once)" section. Maternal disorders uses a separate loader (female-only).

```python
# Use pre-loaded *_temporal from consolidated load section; maternal disorders loaded separately
maternal_disorders_temporal = load_maternal_disorders_temporal(max_year=2023)

# predictors_to_merge uses *_temporal from consolidated load (all predictors including COVID)
print("IHME predictors ready for panel merge.")
```

### Create Panel Dataset

```python
# List of predictors to merge (all candidates; model selects which to use)
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
    (conflict_terrorism_temporal, 'ConflictTerrorism'),
    (all_causes_under5_temporal, 'Childhood'),
    (maternal_disorders_temporal, 'MaternalDisorders'),
    (covid_temporal, 'COVID19'),
]

# Create HALE panel
hale_temporal = compute_temporal_gaps(ihme_hale_temporal, 'HALE_Years', sexes=['Male', 'Female'])
hale_temporal['HALE_gap'] = -hale_temporal['Gap_HALE_Years']

panel_hale = hale_temporal[['Code', 'Year', 'HALE_gap']].copy()
panel_hale = panel_hale.rename(columns={'Code': 'country'})

for df_temp, name in predictors_to_merge:
    df_merge = merge_predictor(df_temp, name)
    panel_hale = panel_hale.merge(df_merge, on=['country', 'Year'], how='left')
    print(f"Merged {name} into HALE: panel now has {panel_hale.shape[1]} columns")

# Filter to OECD countries
panel_hale = panel_hale[panel_hale['country'].isin(oecd_codes)].copy()
panel_hale = panel_hale.dropna(subset=['HALE_gap']).copy()
panel_hale = panel_hale.sort_values(['country', 'Year']).reset_index(drop=True)

print(f"\nHALE panel: {panel_hale.shape}")
print(f"Countries: {panel_hale['country'].nunique()}")
print(f"Years: {panel_hale['Year'].min():.0f}-{panel_hale['Year'].max():.0f}")

# Create LE panel
panel_le = le_temporal[['Code', 'Year', 'LE_gap']].copy()
panel_le = panel_le.rename(columns={'Code': 'country'})

for df_temp, name in predictors_to_merge:
    df_merge = merge_predictor(df_temp, name)
    panel_le = panel_le.merge(df_merge, on=['country', 'Year'], how='left')
    print(f"Merged {name} into LE: panel now has {panel_le.shape[1]} columns")

# Filter to OECD countries
panel_le = panel_le[panel_le['country'].isin(oecd_codes)].copy()
panel_le = panel_le.dropna(subset=['LE_gap']).copy()
panel_le = panel_le.sort_values(['country', 'Year']).reset_index(drop=True)

print(f"\nLE panel: {panel_le.shape}")
print(f"Countries: {panel_le['country'].nunique()}")
print(f"Years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
print(f"Missing values: {panel_le.isnull().sum().sum()}")
```

```python
panel_le.head()
```

### Save Panel Data

```python
# Save panel data for bayesian_model
panel_hale_file = 'interim/panel_hale.h5'
panel_le_file = 'interim/panel_le.h5'

panel_hale.to_hdf(panel_hale_file, key='panel', mode='w')
panel_le.to_hdf(panel_le_file, key='panel', mode='w')

print(f"HALE panel saved: {panel_hale_file}")
print(f"LE panel saved: {panel_le_file}")

log_and_print("\n" + "="*80)
log_and_print("PANEL DATA SAVED")
log_and_print("="*80)
log_and_print(f"HALE: {panel_hale_file} ({panel_hale.shape[0]} rows, {panel_hale.shape[1]} cols)")
log_and_print(f"LE:   {panel_le_file} ({panel_le.shape[0]} rows, {panel_le.shape[1]} cols)")
log_and_print(f"Countries: {panel_hale['country'].nunique()} (HALE), {panel_le['country'].nunique()} (LE)")
log_and_print(f"Years: {panel_hale['Year'].min():.0f}-{panel_hale['Year'].max():.0f}")
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
