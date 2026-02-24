# Data Inventory

## Data Collection Summary

### Smoking/Tobacco Use Indicators (Downloaded)

Three smoking prevalence indicators have been downloaded from WHO GHO API:

1. **M_Est_smk_curr_std** - Age-standardized current tobacco smoking prevalence (%)
   - **Records**: 5,181 (includes projections)
   - **Years**: 2000-2030 (observed: 2000, 2005, 2007, 2010, 2015, 2018, 2020, 2021, 2022; projected: 2025, 2030)
   - **Countries**: 172
   - **Sex categories**: Both sexes, Female, Male
   - **File**: `data/who_smoking_data.csv`
   - **Status**: ✅ Recommended - age-standardized, good temporal coverage
   - **Note**: Years 2025 and 2030 are projections (marked in Comments field). Filter these out for analysis of observed data only.

2. **M_Est_cig_curr_std** - Age-standardized current cigarette smoking prevalence (%)
   - **Records**: 4,950 (likely includes projections)
   - **Years**: 2000-2030 (includes projected years 2025, 2030)
   - **Countries**: 165
   - **Sex categories**: Both sexes, Female, Male
   - **File**: `data/who_smoking_cigarette_std.csv`
   - **Status**: ✅ Good - cigarette-specific, age-standardized
   - **Note**: Check Comments field to identify projected vs. observed data

3. **Adult_curr_tob_smoking** - Current tobacco smoking among adults (%)
   - **Records**: 570
   - **Years**: 2001-2022
   - **Countries**: 190 (most countries)
   - **Sex categories**: Both sexes, Female, Male
   - **File**: `data/who_smoking_adult.csv`
   - **Status**: ✅ Good country coverage but fewer records and shorter time span

**Recommendation**: Use `M_Est_smk_curr_std` as the primary smoking predictor - it has the best combination of temporal coverage, age-standardization, and sufficient country coverage.

### Suicide Rate Indicators (Identified)

Five suicide-related indicators have been identified from WHO GHO API:

1. **MH_12** - Age-standardized suicide rates (per 100,000 population)
   - **Records**: 12,936
   - **Years**: 2000-2021
   - **Countries**: 196
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Recommended - age-standardized, excellent country coverage, good temporal coverage
   - **Note**: Age-standardized rates are preferred for HALE analysis since HALE is also age-standardized

2. **SDGSUICIDE** - Crude suicide rates (per 100,000 population)
   - **Records**: 19,041
   - **Years**: 2000-2021
   - **Countries**: 196
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Good - crude rates, excellent country coverage
   - **Note**: Crude rates may be less comparable across countries with different age structures

3. **SDG_SH_STA_SCIDEN** - Number of suicide deaths
   - **Status**: ⚠️ Less useful - absolute numbers rather than rates

4. **PRISON_D3_DEATHS_SUICIDE_MRATE** - In-prison suicide mortality rate
   - **Status**: ⚠️ Not relevant - prison-specific, not general population

5. **PRISON_B16_SUICIDERISK** - In-prison standardized protocol for suicide
   - **Status**: ⚠️ Not relevant - protocol indicator, not a rate

**Recommendation**: Use `MH_12` as the primary suicide rate predictor - it has age-standardized rates (matching HALE methodology), excellent country coverage (196 countries), gender breakdowns, and good temporal coverage (2000-2021).

### Alcohol-Attributable Death Rate Indicators (Identified)

Multiple alcohol-related death rate indicators have been identified from WHO GHO API:

1. **SA_0000001832** - Alcohol-attributable all-cause deaths per 100,000, age standardized
   - **Records**: 540
   - **Years**: 2019
   - **Countries**: 180
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Downloaded but not used in final model - replaced with IHME Alcohol Use Disorders (B.7.1) for better temporal coverage
   - **Note**: Age-standardized rates match HALE methodology. This indicator uses **Population Attributable Fraction (PAF)** methodology to estimate **all deaths where alcohol is a contributing factor**, including:
     - Direct alcohol-related deaths (alcohol poisoning, alcohol dependence syndrome, alcohol withdrawal)
     - Indirect alcohol-related deaths where alcohol is a contributing factor:
       - Liver disease (cirrhosis, alcoholic liver disease)
       - Some cancers (oral, pharyngeal, esophageal, liver, colorectal, breast)
       - Accidents and injuries (road traffic crashes, falls, drownings) where alcohol was involved
       - Violence (homicide, suicide) where alcohol was a contributing factor
       - Cardiovascular diseases where alcohol contributed
       - Other conditions where alcohol is a risk factor
   - **Definitional Difference from IHME**: WHO's "alcohol-attributable" definition is much broader than IHME's "alcohol use disorders" definition. WHO includes indirect alcohol-related deaths (e.g., liver disease deaths attributable to alcohol, even if liver disease is listed as the primary cause), while IHME only includes deaths where alcohol use disorders are the primary cause of death. This explains why WHO alcohol gap values are much higher than IHME values (e.g., USA: 38.8 vs 5.54, an 86% difference). See `alcohol_data_comparison.md` for detailed explanation.
   - **Limitation**: Only has data for 2019, which limits temporal analysis but provides a good snapshot for cross-country comparison.

2. **SA_0000001437** - Age-standardized death rates, alcohol use disorders, per 100,000
   - **Records**: 714
   - **Years**: 2002, 2004 (only 2 years)
   - **Countries**: 186
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Limited temporal coverage - only 2 years of data, older years (2002, 2004)
   - **Note**: More specific than SA_0000001832 (focuses on alcohol use disorders rather than all alcohol-attributable deaths), but limited temporal coverage makes it less useful for analysis.

3. **SA_0000001833** - Alcohol-attributable DALYs per 100,000 people (age standardized)
   - **Years**: 2019
   - **Countries**: 182
   - **Records**: 1,092
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Good - DALYs (Disability-Adjusted Life Years) provide a measure of both mortality and morbidity, but death rates are more directly comparable to HALE

4. **SA_0000001457_AA** - Liver cirrhosis, alcohol-attributable, age-standardized death rates
   - **Years**: 2019
   - **Countries**: 180
   - **Records**: 1,080
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Good - specific cause of death, but narrower scope than all-cause alcohol-attributable deaths

**Recommendation**: The model uses **IHME Alcohol Use Disorders (B.7.1)** instead of WHO `SA_0000001832` because IHME provides much better temporal coverage (1990-2023 vs 2019 only) and consistent methodology with other IHME indicators. However, it's important to note that IHME's definition is much narrower (only direct alcohol use disorder deaths) compared to WHO's broader "alcohol-attributable" definition (which includes indirect alcohol-related deaths like liver disease, some cancers, and accidents where alcohol was involved). This definitional difference explains why alcohol gap values are much lower in IHME data (e.g., USA: 5.54 vs 38.8 in WHO, an 86% difference) and why alcohol importance decreased when switching from WHO to IHME data. See `alcohol_data_comparison.md` for detailed explanation of these definitional differences.

### Unintentional Poisoning Mortality Rate Indicators (Identified)

Multiple unintentional poisoning-related indicators have been identified from WHO GHO API:

1. **SDGPOISON** - Mortality rate attributed to unintentional poisoning (per 100,000 population)
   - **Records**: 12,936
   - **Years**: 2000-2021 (22 years)
   - **Countries**: 196
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Recommended - excellent temporal coverage, excellent country coverage, gender breakdowns, includes confidence intervals
   - **Note**: This is a crude rate (not explicitly age-standardized), but has excellent temporal and country coverage. Unintentional poisoning includes accidental poisonings from chemicals, drugs, and other substances, which can contribute to the gender gap in mortality. Men often have higher rates of accidental deaths, including poisonings.

2. **SA_0000001450** - Age-standardized death rates, poisoning, per 100,000
   - **Records**: 731
   - **Years**: 2002, 2004 (only 2 years)
   - **Countries**: 185
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Limited temporal coverage - only 2 years of data, older years (2002, 2004)
   - **Note**: Age-standardized rates are preferred for HALE analysis, but limited temporal coverage makes it less useful than SDGPOISON.

3. **SA_0000001458** - Age-standardized death rates (15+ years), poisoning, per 100,000
   - **Years**: 2002, 2004 (only 2 years)
   - **Status**: ⚠️ Limited temporal coverage - similar to SA_0000001450 but for ages 15+

4. **SA_0000001837** - Alcohol poisoning deaths, per 100,000 population
   - **Status**: ⚠️ Narrow scope - only alcohol-related poisonings, not all unintentional poisonings

**Recommendation**: Use `SDGPOISON` as the primary unintentional poisoning mortality rate predictor - it has excellent temporal coverage (2000-2021), excellent country coverage (196 countries), gender breakdowns, and includes confidence intervals. While it's not explicitly age-standardized, the comprehensive temporal and country coverage make it more valuable for analysis than the age-standardized indicators with only 2 years of data. Unintentional poisoning is relevant to the gender gap as men often have higher rates of accidental deaths.

## IHME Global Burden of Disease Data

Data downloaded from IHME Global Burden of Disease (GBD) Compare tool: https://vizhub.healthdata.org/gbd-compare/

**Note**: IHME data provides separate male and female files, allowing for gender gap analysis. Data is downloaded for OECD countries only. All indicators use "All ages" to match HALE methodology (calculated from birth). All IHME indicators include separate male and female values, allowing for gender gap analysis. Country names in IHME data use "Republic of Korea" and "United States of America" which are mapped to "South Korea" and "United States" respectively for compatibility with WHO country name mappings.

### Drug Use Disorders Death Rates (Downloaded)

**Indicator**: B.7.2 Drug Use Disorders  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.7.2 Drug Use Disorders
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_drug_disorder_deaths_male.csv`
- `data/ihme_drug_disorder_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Drug overdoses, particularly opioid overdoses, are a major cause of death in some OECD countries (especially the US) and may contribute significantly to the HALE gender gap. This indicator captures overdose deaths that may not be fully captured in the WHO poisoning indicator.  
**Model Results**: Drug Use Disorders has **importance = 0** in both models, meaning it is not selected by Elastic Net and does not contribute to explaining gender gaps. This suggests that drug-related mortality may not be a major factor in explaining gender gaps in Life Expectancy or HALE, at least with the current data and model structure. The WHO poisoning indicator (SDGPOISON) was removed from the model, and Drug Use Disorders remains but is not selected. See `validation.md` section "Removing WHO Poisoning: Keeping Only IHME DrugDisorder" for detailed analysis.

### Alcohol Use Disorders Death Rates (Downloaded)

**Indicator**: B.7.1 Alcohol use disorders  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.7.1 Alcohol use disorders
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_alcohol_use_disorders_deaths_male.csv`
- `data/ihme_alcohol_use_disorders_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Alcohol use disorders are a significant cause of death and may contribute to the HALE gender gap. Men typically have higher rates of alcohol-related mortality than women. This indicator provides comprehensive alcohol use disorder death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is used in the model instead of the WHO alcohol-attributable death rate indicator (SA_0000001832) which only has data for 2019. IHME data provides much better temporal coverage, allowing for more recent data and temporal analysis.

**Definitional Difference from WHO**: IHME uses **"alcohol use disorders"** which refers to deaths where alcohol use disorders are the **primary or direct cause of death** (ICD-10 F10 codes). This includes:
- Acute alcohol intoxication
- Alcohol dependence syndrome (as primary cause)
- Alcohol withdrawal (as primary cause)
- Other alcohol-related mental and behavioral disorders

**What IHME Excludes** (that WHO includes):
- Liver disease deaths (even if alcohol-related) - these are coded under liver disease causes
- Cancer deaths (even if alcohol-related) - these are coded under cancer causes
- Accident deaths (even if alcohol was involved) - these are coded under injury causes
- Other conditions where alcohol is a contributing factor but not the primary cause

**Why the Difference Matters**: The IHME definition is much narrower than WHO's "alcohol-attributable" definition, which explains why IHME alcohol gap values are much lower than WHO values (e.g., USA: 5.54 vs 38.8, an 86% difference). This narrower definition also explains why Alcohol dropped from #1 to lower importance when switching from WHO to IHME data - the IHME definition captures a much smaller subset of alcohol-related mortality. However, IHME's better temporal coverage (1990-2023 vs 2019 only) and consistent methodology with other IHME indicators make it preferable for the current analysis. See `alcohol_data_comparison.md` for detailed explanation of these definitional differences.

### Self-Harm (Suicide) Death Rates (Downloaded)

**Indicator**: B.7.3 Self-harm  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.7.3 Self-harm
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_self_harm_deaths_male.csv`
- `data/ihme_self_harm_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Self-harm (suicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher suicide rates than women in most countries. This indicator provides comprehensive self-harm death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is used in the model instead of the WHO suicide rate indicator (MH_12) which has data for 2000-2021. IHME data provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators.  
**Model Results**: Suicide importance increased substantially when switching from WHO to IHME data (+139% for Life Expectancy, +42% for HALE), suggesting IHME data captures suicide-related mortality more effectively. Suicide ranks #4 in Life Expectancy model and #5 in HALE model. See `validation.md` section "Suicide: WHO → IHME" for detailed analysis.

### Interpersonal Violence (Homicide) Death Rates (Downloaded)

**Indicator**: B.7.4 Interpersonal violence  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.7.4 Interpersonal violence
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_interpersonal_violence_deaths_male.csv`
- `data/ihme_interpersonal_violence_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Interpersonal violence (homicide) is a significant cause of death and contributes to the HALE gender gap. Men typically have much higher homicide rates than women in most countries. This indicator provides comprehensive interpersonal violence death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is used in the model instead of the WHO homicide rate indicator (VIOLENCE_HOMICIDERATE) which has data for 2000-2021. IHME data provides better temporal coverage (starting from 1990) and consistent methodology with other IHME indicators.  
**Model Results**: Homicide importance decreased when switching from WHO to IHME data (-28% for HALE), and **homicide was not selected by Elastic Net for the Life Expectancy model** (importance = 0), meaning it does not contribute to explaining the Life Expectancy gap when using IHME data. For HALE, homicide ranks #5 with moderate importance (3.04). This suggests that IHME homicide data may be less predictive than WHO data, or that other indicators (particularly Suicide) capture similar variance. See `validation.md` section "Homicide: WHO → IHME" for detailed analysis.

### Road Injuries (Road Traffic Crash) Death Rates (Downloaded)

**Indicator**: Road injuries  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: Road injuries
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_road_injuries_deaths_male.csv`
- `data/ihme_road_injuries_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Road injuries (road traffic crashes) are a significant cause of death and contribute to the HALE gender gap. Men typically have 2-4 times higher road traffic death rates than women in most countries due to higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. This indicator provides comprehensive road injury death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is used in the model instead of the WHO road traffic crash death rate indicator (SA_0000001459) which only has data for 2019. IHME data provides much better temporal coverage, allowing for temporal analysis and more recent data.  
**Model Results**: Road traffic has very low importance in both models (0.111 for Life Expectancy, ranked #8; 0.633 for HALE, ranked #9), suggesting it is not a major predictive factor for gender gaps. For Life Expectancy, only the Mid component was selected (Gap component = 0), meaning the gender gap in road traffic deaths does not contribute to explaining the Life Expectancy gap. See `validation.md` section "Road Traffic: WHO → IHME" for detailed analysis.

### Maternal Disorders Death Rates (Downloaded)

**Indicator**: Maternal disorders  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Female only (inherently female-specific)

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: Maternal disorders
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Female
- Metric: Rate

**Files**:
- `data/ihme_maternal_disorders_deaths_female.csv`

**Status**: ⚠️ Downloaded but **removed from final model** - removed due to counterintuitive positive coefficient  
**Relevance**: Maternal disorders (maternal mortality) are a significant cause of death for women and can contribute to the HALE gender gap, especially in lower-income countries. High maternal mortality can significantly reduce female life expectancy, explaining why some countries have smaller gender gaps. This indicator provides comprehensive maternal disorder death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries). This is an alternative to the WHO maternal mortality ratio indicator (MDG_0000000026) which has data for 1985-2023. Note: WHO indicator uses ratio per 100,000 live births, while IHME uses rate per 100,000 population, so they measure slightly different things.  
**Why Removed**: Maternal mortality had a **counterintuitive positive coefficient** in the models, which implies that higher maternal mortality is associated with a larger LE/HALE gap. This is counterintuitive because if something increases female mortality, it should **close** the gap (since gap = Female - Male). The positive coefficient suggests a spurious association, possibly because maternal mortality is capturing something about general healthcare quality rather than a direct causal relationship. Removing it had minimal impact on model performance but improved interpretability. After removal, Cardiovascular and Homicide gained substantial importance in the HALE model, suggesting maternal mortality may have been suppressing these indicators. See `validation.md` section "Removing Maternal Mortality Indicator" for detailed analysis.  
**Note**: Maternal disorders are inherently female-specific (deaths during pregnancy, childbirth, or within 42 days of termination of pregnancy).

### All-Cause Deaths Under 5 Years of Age (Downloaded)

**Indicator**: All causes (under 5 years)  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: <5 years  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: All causes
- Measure: Deaths
- Locations: OECD
- Age: <5 years
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_all_causes_under5_deaths_male.csv`
- `data/ihme_all_causes_under5_deaths_female.csv`

**Status**: ⚠️ Downloaded but **not used in final model** - removed due to methodological concerns  
**Relevance**: All-cause mortality for children under 5 years of age is relevant to the HALE gender gap because HALE is calculated from birth, so early-life mortality directly affects HALE calculations. If child mortality differs by gender, it directly contributes to the HALE gender gap. Infant and child mortality is typically higher in males (biological vulnerability + some behavioral factors). This indicator provides comprehensive all-cause under-5 mortality rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage (40 countries).

**Definitional Difference from WHO**: This indicator measures deaths per 100,000 population, which is fundamentally different from the WHO under-five mortality rate (MDG_0000000007) which measures deaths per 1,000 live births. 

**Methodological Concern - Confounding**: The IHME indicator (deaths per 100,000 population) is **confounded with age structure and fertility rates**. Countries with:
- A larger proportion of the population in child-bearing age
- Higher fertility rates

will have more people under age 5 in the population, and therefore more deaths under 5, even if the underlying risk of death for children is the same. This confounding makes it difficult to interpret the IHME indicator as a pure measure of early-life mortality risk. The WHO indicator (deaths per 1,000 live births) controls for these factors by using live births as the denominator, making it a more direct measure of early-life mortality risk independent of demographic structure.

**Why Removed**: Both WHO and IHME under-five mortality indicators were removed from the final model because:
- Very low importance in both models (0.0558 in Life Expectancy model, not in top 10 for HALE model)
- Minimal impact on model performance when removed
- Limited temporal coverage for WHO version
- Methodological concerns with IHME version (confounding with age structure and fertility)

See `validation.md` section "Removing Childhood Indicator (Under-Five Mortality)" for detailed analysis of the removal and its effects.

### Diabetes Type 2 Death Rates (Downloaded)

**Indicator**: B.8.1.2 Diabetes mellitus type 2  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.8.1.2 Diabetes mellitus type 2
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_diabetes_deaths_male.csv`
- `data/ihme_diabetes_deaths_female.csv`

**Status**: ⚠️ Downloaded but not yet integrated into model  
**Note**: This is an alternative to the WHO diabetes death rate indicator (SA_0000001440) which only has data for 2004. IHME data may have better temporal coverage.

### Cardiovascular Diseases Death Rates (Downloaded)

**Indicator**: B.2 Cardiovascular diseases  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.2 Cardiovascular diseases
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_cardiovascular_deaths_male.csv`
- `data/ihme_cardiovascular_deaths_female.csv`

**Status**: ⚠️ Downloaded but not yet integrated into model  
**Relevance**: Cardiovascular diseases are a major cause of death and may contribute significantly to the HALE gender gap. This is an alternative to the WHO cardiovascular disease death rate indicators which only have data for 2004. IHME data may have better temporal coverage, allowing for more recent data to be used in the analysis.

### Neoplasms (Cancer) Death Rates (Downloaded)

**Indicator**: B.1 Neoplasms  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.1 Neoplasms
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_neoplasms_deaths_male.csv`
- `data/ihme_neoplasms_deaths_female.csv`

**Status**: ⚠️ Downloaded but not yet integrated into model  
**Relevance**: Neoplasms (cancer) are a major cause of death and may contribute significantly to the HALE gender gap. Different types of cancer have different gender patterns (e.g., lung cancer is often higher in men, breast cancer is female-specific). This indicator provides comprehensive cancer death rates with better temporal coverage than WHO indicators.

### Chronic Respiratory Diseases Death Rates (Downloaded)

**Indicator**: B.3 Chronic respiratory diseases  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: B.3 Chronic respiratory diseases
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_chronic_respiratory_deaths_male.csv`
- `data/ihme_chronic_respiratory_deaths_female.csv`

**Status**: ⚠️ Downloaded but not yet integrated into model  
**Relevance**: Chronic respiratory diseases (including COPD, asthma, and other chronic lung conditions) are a major cause of death and may contribute significantly to the HALE gender gap. These diseases often have gender differences due to factors such as smoking patterns, occupational exposures, and environmental factors. This indicator provides comprehensive chronic respiratory disease death rates with better temporal coverage than WHO indicators.

### Liver Disease (Cirrhosis and Other Chronic Liver Diseases) Death Rates (Downloaded)

**Indicator**: Cirrhosis and other chronic liver diseases  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: Cirrhosis and other chronic liver diseases
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_liver_disease_deaths_male.csv`
- `data/ihme_liver_disease_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Liver disease (cirrhosis and other chronic liver diseases) is a significant cause of death and may contribute to the HALE gender gap. Men typically have higher rates of liver disease mortality than women, often due to higher alcohol consumption, hepatitis infections, and other risk factors. This indicator provides comprehensive liver disease death rates with excellent temporal coverage (1990-2023, 34 years) and good country coverage. Liver disease is often related to alcohol consumption, but also includes non-alcoholic causes such as viral hepatitis, non-alcoholic fatty liver disease, and other chronic liver conditions.

### COVID-19 Death Rates (Downloaded)

**Indicator**: COVID-19  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: COVID-19
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_covid19_deaths_male.csv`
- `data/ihme_covid19_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: COVID-19 is a significant cause of death that emerged in 2020 and may contribute to the HALE gender gap. COVID-19 mortality patterns show gender differences, with men typically having higher death rates than women in most countries. This indicator provides comprehensive COVID-19 death rates with temporal coverage from 2020-2023. Note: Data includes zeros for all years before 2020 (1990-2019) since COVID-19 did not exist before 2020. This indicator is particularly relevant for understanding recent changes in the gender gap in life expectancy and HALE, as the pandemic had substantial impacts on mortality patterns.  
**Note**: Years 1990-2019 contain zeros (COVID-19 did not exist), with actual data starting in 2020.

### Unintentional Injuries Death Rates (Downloaded)

**Indicator**: Unintentional injuries  
**Measure**: Deaths  
**Metric**: Rate (per 100,000 population)  
**Locations**: OECD countries  
**Age**: All ages  
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: Unintentional injuries
- Measure: Deaths
- Locations: OECD
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_unintentional_injuries_deaths_male.csv`
- `data/ihme_unintentional_injuries_deaths_female.csv`

**Status**: ✅ Downloaded and integrated into model  
**Relevance**: Unintentional injuries (including falls, drowning, fires, and other accidents) are a significant cause of death and may contribute to the HALE gender gap. These injuries often show gender differences due to occupational exposures, risk-taking behaviors, and activity patterns. This indicator provides comprehensive unintentional injury death rates with better temporal coverage (1990-2023) than many WHO indicators.

### Road Traffic Crash Death Rate Indicators (Identified)

Multiple road traffic-related death rate indicators have been identified from WHO GHO API:

1. **SA_0000001459** - Road traffic crash deaths, age-standardized death rates (15+), per 100,000 population
   - **Records**: 1,080
   - **Years**: 2019
   - **Countries**: 180
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Recommended - age-standardized, good country coverage, gender breakdowns, recent data (2019)
   - **Note**: Age-standardized rates for ages 15+ match HALE methodology (HALE is also age-standardized). Road traffic deaths are a major contributor to the gender gap in mortality, as men typically have much higher rates due to higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. The limitation is that it only has data for 2019, but this provides a good cross-sectional snapshot for the analysis.

2. **RS_198** - Estimated road traffic death rate (per 100,000 population)
   - **Years**: 2021 (only 1 year)
   - **Countries**: 204
   - **Sex categories**: None (no gender breakdown)
   - **Status**: ⚠️ Not suitable - no gender breakdown available

3. **SA_0000001452** - Age-standardized death rates, road traffic accidents, per 100,000
   - **Years**: 2002, 2004 (only 2 years)
   - **Countries**: 192
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Limited temporal coverage - only 2 years of older data (2002, 2004)

4. **SA_0000001459_AA** - Road traffic crash deaths, alcohol-attributable, age-standardized death rates
   - **Years**: 2019
   - **Countries**: 180
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Narrow scope - only alcohol-attributable road traffic deaths, not all road traffic deaths

**Recommendation**: The model uses **IHME Road Injuries** instead of WHO `SA_0000001459` because IHME provides much better temporal coverage (1990-2023 vs 2019 only) and consistent methodology with other IHME indicators. However, road traffic has very low importance in both models (0.111 for Life Expectancy, ranked #8; 0.633 for HALE, ranked #9), suggesting it is not a major predictive factor for gender gaps. For Life Expectancy, only the Mid component was selected (Gap component = 0), meaning the gender gap in road traffic deaths does not contribute to explaining the Life Expectancy gap. See `validation.md` section "Road Traffic: WHO → IHME" for detailed analysis.

### Maternal Mortality Ratio Indicators (Identified)

Multiple maternal mortality indicators have been identified from WHO GHO API:

1. **MDG_0000000026** - Maternal mortality ratio (per 100,000 live births)
   - **Records**: 7,878 (full dataset), 4,848 (2000-2023)
   - **Years**: 1985-2023 (excellent temporal coverage)
   - **Countries**: 202
   - **Sex categories**: N/A (inherently female-specific)
   - **Status**: ⚠️ **Downloaded but removed from final model** - removed due to counterintuitive positive coefficient
   - **Note**: Maternal mortality is inherently female-specific (deaths during pregnancy, childbirth, or within 42 days of termination of pregnancy). This indicator was tested in the model but removed because it had a **counterintuitive positive coefficient**, which implies that higher maternal mortality is associated with a larger LE/HALE gap. This is counterintuitive because if something increases female mortality, it should **close** the gap (since gap = Female - Male). The positive coefficient suggests a spurious association, possibly because maternal mortality is capturing something about general healthcare quality rather than a direct causal relationship. Removing it had minimal impact on model performance but improved interpretability. See `validation.md` section "Removing Maternal Mortality Indicator" for detailed analysis.

2. **MDG_0000000032** - Maternal mortality ratio (per 100,000 live births) - Country reported estimates
   - **Years**: 1987, 2000, 2002-2009 (limited temporal coverage)
   - **Countries**: 169
   - **Status**: ⚠️ Limited temporal coverage - only 10 years of data, older years, fewer countries than MDG_0000000026

3. **MORT_MATERNALNUM** - Number of maternal deaths
   - **Status**: ⚠️ Less useful - absolute numbers rather than rates (rates are more comparable across countries)

**Recommendation**: Maternal mortality was tested in the model but **removed from the final model** due to a counterintuitive positive coefficient. The indicator had moderate importance (1.89 in Life Expectancy model, ranked #5; 2.15 in HALE model, ranked #7), but the positive coefficient suggests a spurious association rather than a direct causal relationship. Removing it had minimal impact on model performance (R² decreased slightly for LE, improved slightly for HALE) but improved model interpretability. After removal, Cardiovascular and Homicide gained substantial importance in the HALE model, suggesting maternal mortality may have been suppressing these indicators. See `validation.md` section "Removing Maternal Mortality Indicator" for detailed analysis.

### Homicide Rate Indicators (Identified)

Two homicide-related indicators have been identified from WHO GHO API:

1. **VIOLENCE_HOMICIDERATE** - Estimates of rates of homicides per 100,000 population
   - **Records**: 12,936
   - **Years**: 2000-2021 (excellent temporal coverage)
   - **Countries**: 196
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Implemented - excellent temporal coverage, excellent country coverage, gender breakdowns, includes confidence intervals
   - **Note**: This is a crude rate (not explicitly age-standardized), but has excellent temporal and country coverage. Homicide rates are typically much higher in men than women across most countries, making it a major contributor to the gender gap in mortality. Homicide reflects violence, conflict, and social factors that differentially affect men and women.

2. **VIOLENCE_HOMICIDENUM** - Estimates of number of homicides
   - **Years**: 2000-2019 (slightly less recent than rate indicator)
   - **Countries**: 194
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Less useful - absolute numbers rather than rates (rates are more comparable across countries), and has less recent data (up to 2019 vs 2021)

**Recommendation**: The model uses **IHME Interpersonal Violence (B.7.4)** instead of WHO `VIOLENCE_HOMICIDERATE` because IHME provides better temporal coverage (1990-2023 vs 2000-2021) and consistent methodology with other IHME indicators. However, **homicide was not selected by Elastic Net for the Life Expectancy model** (importance = 0) when using IHME data, meaning it does not contribute to explaining the Life Expectancy gap. For HALE, homicide has moderate importance (ranked #5). This suggests that IHME homicide data may be less predictive than WHO data, or that other indicators (particularly Suicide) capture similar variance. See `validation.md` section "Homicide: WHO → IHME" for detailed analysis.

### Diabetes Death Rate Indicators (Identified)

Multiple diabetes-related indicators have been identified from WHO GHO API:

1. **SA_0000001440** - Age-standardized death rates, diabetes mellitus, per 100,000
   - **Records**: 573
   - **Years**: 2004 (only 1 year)
   - **Countries**: 191
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Implemented - age-standardized, good country coverage, gender breakdowns
   - **Note**: Age-standardized rates match HALE methodology (HALE is also age-standardized). Diabetes is a chronic condition that can contribute to the gender gap in mortality, though the relationship may vary by country and healthcare access. The limitation is that it only has data for 2004, similar to cardiovascular disease indicators, which limits temporal analysis but provides a good cross-sectional snapshot for the analysis.

2. **SA_0000001421** - Age-standardized DALYs, diabetes mellitus, per 100,000
   - **Records**: 573
   - **Years**: 2004 (only 1 year)
   - **Countries**: 191
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Limited temporal coverage - only 2004 data, DALYs (Disability-Adjusted Life Years) provide a measure of both mortality and morbidity, but death rates are more directly comparable to HALE
   - **Note**: DALYs capture both mortality and morbidity, but for HALE gender gap analysis, death rates are more directly relevant since HALE focuses on healthy life expectancy.

3. **NCDMORT3070** - Probability (%) of dying between age 30 and exact age 70 from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease
   - **Records**: 12,936
   - **Years**: 2000-2021 (excellent temporal coverage - 22 years)
   - **Countries**: 196
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ✅ Implemented - excellent temporal coverage, excellent country coverage, gender breakdowns
   - **Note**: Combines multiple causes of death (cardiovascular disease, cancer, diabetes, chronic respiratory disease), so it's less specific than individual cause indicators. However, it has much better temporal coverage (2000-2021) than diabetes-specific indicators (which only have 2004 data). This makes it useful for model comparison - trading off specificity for temporal coverage. The combined indicator may capture overall NCD mortality patterns that contribute to the HALE gender gap.

4. **NCD_DIABETES_PREVALENCE_AGESTD** - Prevalence of diabetes, age-standardized
   - **Status**: ⚠️ Not suitable - prevalence indicator (not a death rate), measures disease burden but not mortality

5. **NCD_DIABETES_TREATMENT_AGESTD** - Diabetes treatment coverage, age-standardized
   - **Status**: ⚠️ Not suitable - treatment coverage indicator, not a mortality measure

6. **Other indicators** - Multiple policy/registry indicators (NCD_CCS_DiabetesReg, NCD_CCS_DiabetesTest, etc.)
   - **Status**: ⚠️ Not suitable - policy/regulatory indicators, not mortality data

**Recommendation**: 
- **Primary choice**: Use `SA_0000001440` as the diabetes-specific death rate predictor - it has age-standardized rates (matching HALE methodology), good country coverage (191 countries), gender breakdowns, and captures diabetes mortality directly. ✅ **Implemented** - Data download functionality added to `who_data.py`. The limitation is that it only has data for 2004, similar to cardiovascular disease indicators, but this provides a good cross-sectional snapshot for the analysis.
- **Alternative for temporal analysis**: Use `NCDMORT3070` as an alternative predictor when temporal coverage is needed - it combines cardiovascular disease, cancer, diabetes, and chronic respiratory disease, so it's less specific but has excellent temporal coverage (2000-2021) and excellent country coverage (196 countries). ✅ **Implemented** - Data download functionality added to `who_data.py`. This allows model comparison, trading off specificity for temporal coverage. The combined indicator may capture overall NCD mortality patterns that contribute to the HALE gender gap.

**Model Strategy**: Consider testing both indicators in the regression model to compare:
- `SA_0000001440` (diabetes-specific, 2004 only) - for cross-sectional analysis with specific cause attribution
- `NCDMORT3070` (combined NCD causes, 2000-2021) - for temporal analysis and capturing broader NCD mortality patterns

### Intimate Partner Violence (IPV) Indicators (Identified)

Multiple intimate partner violence indicators have been identified from WHO GHO API. Note: IPV is a **prevalence indicator** (percentage of women experiencing violence), not a direct death rate. It affects women's health and mortality indirectly through mental health, injuries, and other health consequences.

1. **SDGIPV** - Proportion of ever-partnered women and girls aged 15-49 years subjected to physical and/or sexual violence by a current or former intimate partner in the previous 12 months
   - **Records**: 577
   - **Years**: 2000-2017
   - **Countries**: 126
   - **Sex categories**: Female (inherently female-specific)
   - **Status**: ✅ Implemented - good temporal coverage, good country coverage, matches SDG indicator 5.2.1
   - **Note**: This is a prevalence indicator (percentage), not a death rate. IPV affects women's health indirectly through mental health impacts, injuries, and other health consequences. It may contribute to the gender gap in HALE through its effects on women's physical and mental health, though the relationship is complex and indirect.

2. **SDGIPV12M** - Proportion of ever-partnered women and girls aged 15–49 years subjected to physical and/or sexual violence by a current or former intimate partner in the previous 12 months
   - **Years**: 2018 (only 1 year)
   - **Countries**: 163
   - **Status**: ⚠️ Limited temporal coverage - only 2018 data, but good country coverage

3. **SDGIPVLT** - Proportion of ever-partnered women and girls aged 15–49 years subjected to physical and/or sexual violence by a current or former intimate partner in their lifetime
   - **Years**: 2018 (only 1 year)
   - **Countries**: 158
   - **Status**: ⚠️ Limited temporal coverage - only 2018 data, lifetime prevalence (broader than 12-month)

4. **RHR_IPV** - Intimate partner violence prevalence among ever partnered women (%)
   - **Years**: 2010 (only 1 year)
   - **Countries**: 29
   - **Status**: ⚠️ Very limited coverage - only 2010, only 29 countries

5. **SA_0000001455** - Age-standardized death rates, violence, per 100,000
   - **Years**: 2002, 2004 (only 2 years)
   - **Countries**: 192
   - **Sex categories**: Both sexes, Female, Male
   - **Status**: ⚠️ Limited temporal coverage - only 2 years, but age-standardized and has gender breakdowns. This captures all violence-related deaths (not just IPV), which may include homicide and other forms of violence.

**Recommendation**: Use `SDGIPV` as the primary intimate partner violence indicator - it has the best temporal coverage (2000-2017) and good country coverage (126 countries). ✅ **Implemented** - Data download functionality added to `who_data.py`. However, note that IPV is a prevalence indicator affecting women's health indirectly, not a direct cause of death. It may be less directly relevant to HALE gender gap analysis than direct mortality indicators, but could be useful for understanding broader health impacts on women. Consider whether the indirect relationship to mortality makes it suitable for the regression analysis, or if it should be analyzed separately.

### Infant and Child Mortality Indicators (Explored)

Multiple indicators related to infant, neonatal, and under-five mortality have been identified from WHO GHO API. Note: These indicators measure mortality in early life (birth to age 5), which may be less directly relevant to HALE gender gap analysis since HALE focuses on adult health outcomes. However, early-life mortality patterns can reflect underlying health disparities and may be relevant for understanding population-level gender differences.

#### Infant Mortality Indicators (with gender breakdowns):

1. **imr** - Infant mortality rate (deaths per 1000 live births)
   - **Years**: 1932-2023 (excellent temporal coverage)
   - **Countries**: 249
   - **Sex categories**: Both sexes, Female, Male
   - **Total records**: 43,513
   - **Status**: ✅ Excellent coverage - has gender breakdowns, very long temporal coverage, comprehensive country coverage

2. **MDG_0000000001** - Infant mortality rate (probability of dying between birth and age 1 per 1000 live births)
   - **Years**: 1932-2023 (excellent temporal coverage)
   - **Countries**: 249
   - **Sex categories**: Both sexes, Female, Male
   - **Total records**: 43,513
   - **Status**: ✅ Excellent coverage - similar to `imr`, has gender breakdowns, very long temporal coverage

3. **CM_02** - Number of infant deaths
   - **Years**: 1951-2023
   - **Countries**: 249
   - **Sex categories**: Both sexes, Female, Male
   - **Total records**: 42,716
   - **Status**: ⚠️ Less useful - absolute numbers rather than rates (rates are more comparable across countries), and has less recent historical data (starts 1951 vs 1932)

#### Under-Five Mortality Indicators (with gender breakdowns):

1. **u5mr** - Under-five mortality rate (deaths per 1000 live births)
   - **Years**: 1932-2023 (excellent temporal coverage)
   - **Countries**: 249
   - **Sex categories**: Both sexes, Female, Male
   - **Total records**: 63,070
   - **Status**: ✅ Excellent coverage - has gender breakdowns, very long temporal coverage, comprehensive country coverage

2. **MDG_0000000007** - Under-five mortality rate (probability of dying by age 5 per 1000 live births)
   - **Years**: 1932-2023 (excellent temporal coverage)
   - **Countries**: 249
   - **Sex categories**: Both sexes, Female, Male
   - **Total records**: 63,070 (30,648 with sex dimension when filtered)
   - **Status**: ⚠️ **Downloaded but removed from final model** - Data download functionality added to `who_data.py`. Excellent coverage with clean gender breakdowns (5,976 Male, 5,976 Female records). Much better data quality than `u5mr` when filtered for sex dimension. However, removed from final model due to very low importance (0.0558 in Life Expectancy model, not in top 10 for HALE model) and minimal impact on model performance. See `validation.md` section "Removing Childhood Indicator (Under-Five Mortality)" for detailed analysis.

**Recommendation**: 

**For HALE gender gap analysis**: These indicators **SHOULD be considered** for inclusion in the regression model because:
1. **HALE is calculated from birth** - HALE (Healthy Life Expectancy) measures expected years of healthy life at birth, so it includes all mortality from birth to death. If infant/child mortality differs by gender, it directly affects the HALE calculation and contributes to the gender gap.
2. **Goal is to explain the gap** - The purpose of the model is to estimate what portion of the HALE gender gap is explainable by each factor. If infant/child mortality contributes to the gap, it should be included to properly attribute its contribution.
3. **Gender differences exist** - Infant mortality is typically higher in males, and this gender difference will affect HALE calculations. Under-five mortality also shows gender differences that should be accounted for.

**However**, note that:
- **Relative contribution may be smaller** - In most countries, adult mortality patterns (smoking, cardiovascular disease, accidents, violence) likely contribute more to the HALE gender gap than infant/child mortality, especially in high-income countries. But the relative contribution should be determined empirically, not assumed.
- **More important in lower-income countries** - In countries with high infant/child mortality rates, these factors may contribute more substantially to the HALE gender gap.
- **Different causal pathways** - Early-life mortality is driven by different factors (infectious diseases, malnutrition, birth complications) than adult mortality (chronic diseases, accidents, violence, lifestyle factors), so including both provides a more complete picture.

**Recommendation for HALE model**: 
- **Under-five mortality rate was tested but removed from final model** - `MDG_0000000007` was tested in the model but removed due to very low importance and minimal impact on model performance. The indicator had importance of 0.0558 in the Life Expectancy model (ranked #10) and was not in the top 10 for the HALE model. Removing it had minimal impact on model performance (R² improved slightly for Life Expectancy, essentially unchanged for HALE), confirming it was not contributing meaningfully to model fit.
  - **Why MDG_0000000007 over u5mr** (if used): While both indicators have similar metadata (249 countries, 1932-2023), `MDG_0000000007` provides much better data quality when filtered for sex dimension:
    - `MDG_0000000007`: 30,648 records with sex dimension (5,976 Male, 5,976 Female, 18,696 Both sexes), clean structure with proper gender breakdowns
    - `u5mr`: Only 724 records with sex dimension, many records have other dimension types (age groups, regions, wealth quintiles) mixed in, making the data messy and harder to work with
    - Both have the same temporal and country coverage, but `MDG_0000000007` has cleaner, more usable data for gender gap analysis
- **IHME alternative not suitable**: The IHME "All-Cause Deaths Under 5 Years of Age" indicator (per 100,000 population) was also tested but excluded because it is confounded with age structure and fertility rates. Countries with more people of child-bearing age and higher fertility will have more people under 5 in the population, and therefore more deaths under 5, even if the underlying risk of death for children is the same. The WHO indicator (per 1,000 live births) controls for these factors, but even with this methodological advantage, it had very low importance in the models.
- See `validation.md` section "Removing Childhood Indicator (Under-Five Mortality)" for detailed analysis of the removal and its effects on model performance and importance rankings.

### Occupational Attributable Death Indicators (Identified)

Multiple occupational-related death indicators have been identified from WHO GHO API. Note: Occupational hazards are a major contributor to the gender gap in mortality, as men are more likely to work in dangerous occupations (construction, mining, manufacturing) with higher rates of workplace accidents, injuries, and exposure to hazardous materials.

#### Occupational Risk Factors Indicators:

1. **OCC_1** - Occupational risk factors attributable deaths
   - **Years**: 2004 (only 1 year)
   - **Country/Regions**: 8 (not actual countries)
   - **Sex categories**: None (no gender breakdown)
   - **Status**: ⚠️ Very limited - only 2004 data, only 8 country/regions, no gender breakdown

2. **OCC_3** - Occupational risk factors attributable deaths per 100'000 capita
   - **Years**: 2004 (only 1 year)
   - **Country/Regions**: 8 (not actual countries)
   - **Sex categories**: None (no gender breakdown)
   - **Status**: ⚠️ Very limited - only 2004 data, only 8 country/regions, no gender breakdown

3. **OCC_2** - Occupational risk factors attributable DALYs ('000)
   - **Status**: ⚠️ Less useful - DALYs rather than deaths, absolute numbers rather than rates

4. **OCC_4** - Occupational risk factors attributable DALYs per 100'000 capita
   - **Status**: ⚠️ Less useful - DALYs rather than deaths

#### Occupational Injuries Indicators:

1. **OCC_19** - Occupational injuries attributable deaths
   - **Years**: 2004 (only 1 year)
   - **Country/Regions**: 8 (not actual countries)
   - **Sex categories**: None (no gender breakdown)
   - **Status**: ⚠️ Very limited - only 2004 data, only 8 country/regions, no gender breakdown

2. **OCC_21** - Occupational injuries attributable deaths per 100'000 capita
   - **Years**: 2004 (only 1 year)
   - **Country/Regions**: 8 (not actual countries)
   - **Sex categories**: None (no gender breakdown)
   - **Status**: ⚠️ Very limited - only 2004 data, only 8 country/regions, no gender breakdown

3. **OCC_20** - Occupational injuries attributable DALYs ('000)
   - **Status**: ⚠️ Less useful - DALYs rather than deaths, absolute numbers rather than rates

4. **OCC_22** - Occupational injuries attributable DALYs per 100'000 capita
   - **Status**: ⚠️ Less useful - DALYs rather than deaths

#### Occupational Airborne Particulates Indicators:

1. **OCC_5** - Occupational airborne particulates attributable deaths
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

2. **OCC_7** - Occupational airborne particulates attributable deaths per 100'000 capita
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

3. **OCC_6** - Occupational airborne particulates attributable DALYs ('000)
   - **Status**: ⚠️ Less useful - DALYs rather than deaths, absolute numbers rather than rates

4. **OCC_8** - Occupational airborne particulates attributable DALYs per 100'000 capita
   - **Status**: ⚠️ Less useful - DALYs rather than deaths

#### Occupational Carcinogens Indicators:

1. **OCC_9** - Occupational carcinogens attributable deaths
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

2. **OCC_11** - Occupational carcinogens attributable deaths per 100'000 capita
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

3. **OCC_10** - Occupational carcinogens attributable DALYs ('000)
   - **Status**: ⚠️ Less useful - DALYs rather than deaths, absolute numbers rather than rates

4. **OCC_12** - Occupational carcinogens attributable DALYs per 100'000 capita
   - **Status**: ⚠️ Less useful - DALYs rather than deaths

#### Occupational Ergonomic Stressors Indicators:

1. **OCC_15** - Occupational ergonomic stressors attributable deaths
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

2. **OCC_17** - Occupational ergonomic stressors attributable deaths per 100'000 capita
   - **Status**: ⚠️ Very limited coverage expected (similar to other OCC indicators)

3. **OCC_16** - Occupational ergonomic stressors attributable DALYs ('000)
   - **Status**: ⚠️ Less useful - DALYs rather than deaths, absolute numbers rather than rates

4. **OCC_18** - Occupational ergonomic stressors attributable DALYs per 100'000 capita
   - **Status**: ⚠️ Less useful - DALYs rather than deaths

#### Other Occupational Indicators:

- **HWF_0017** - Environmental and Occupational Health and Hygiene Professionals (number)
  - **Status**: ⚠️ Not suitable - workforce indicator, not mortality data

- **HWF_0018** - Environmental and Occupational Health Inspectors and Associates (number)
  - **Status**: ⚠️ Not suitable - workforce indicator, not mortality data

- **MH_22** - Occupational therapists in mental health sector (per 100,000)
  - **Status**: ⚠️ Not suitable - workforce indicator, not mortality data

- **OHS_POLICYSTATUS** - Existence of national policy instruments for occupational health and safety for health workers
  - **Status**: ⚠️ Not suitable - policy indicator, not mortality data

**Recommendation**: 

**For HALE gender gap analysis**: The occupational attributable death indicators identified are **NOT suitable** for the regression model because:

1. **No gender breakdowns** - None of the occupational death indicators have sex categories (Male, Female, Both sexes), which is essential for analyzing gender gaps. This is a critical limitation since occupational hazards are known to differentially affect men and women.

2. **Very limited temporal coverage** - All indicators checked (OCC_1, OCC_3, OCC_19, OCC_21) only have data for 2004 (1 year), which severely limits temporal analysis and cross-country comparison.

3. **Very limited country/region coverage** - Only 8 country/regions have data (not actual countries), which is insufficient for a comprehensive cross-country analysis of HALE gender gaps.

4. **Missing key information** - The indicators don't provide the gender-specific data needed to calculate male vs. female differences or ratios, which are required for the regression model.

**Alternative approaches**:
- **Road traffic crash death rates** (SA_0000001459) - Already implemented ✅ - While not exclusively occupational, road traffic deaths capture occupational exposure (e.g., professional drivers, delivery workers) and have gender breakdowns. However, it only has 2019 data.
- **Unintentional poisoning mortality rates** (SDGPOISON) - Already implemented ✅ - May capture some occupational exposures (chemical accidents, workplace poisonings) and has excellent temporal (2000-2021) and country coverage (196 countries) with gender breakdowns.
- **Consider proxy indicators** - Since direct occupational death indicators are not available with gender breakdowns, the model may need to rely on indirect measures or acknowledge this as a limitation. Occupational hazards are a known contributor to the gender gap, but cannot be directly quantified with available WHO data.

**Status**: ⚠️ **Not suitable for model** - No gender breakdowns, very limited temporal and country coverage. Occupational hazards remain an important theoretical factor but cannot be directly measured with available WHO GHO data.

## Drilldown Data

Data for investigating specific drivers of gender gaps within broader categories (separate from the primary cross-country regression models).

### Cancer (Neoplasms) Drilldown (Downloaded)

**Indicator**: Drilldown into Neoplasms (Level 3 or Level 4 causes)
**Measure**: Death rates per 100,000
**Locations**: United States, Iceland, and OECD (Total)
**Age**: All ages
**Sex**: Separate files for Male and Female

**GBD Compare Tool Settings**:
- Display: Cause
- Cause: Drilldown into Neoplasms (Level 3 or Level 4 causes)
- Measure: Death rates per 100,000
- Locations: United States of America / Iceland / OECD Countries
- Age: All
- Sex: Both (downloaded separately as Male and Female)
- Metric: Rate

**Files**:
- `data/ihme_cancer_drilldown_usa_male.csv`
- `data/ihme_cancer_drilldown_usa_female.csv`
- `data/ihme_cancer_drilldown_iceland_male.csv`
- `data/ihme_cancer_drilldown_iceland_female.csv`
- `data/ihme_cancer_drilldown_oecd_male.csv`
- `data/ihme_cancer_drilldown_oecd_female.csv`

**Status**: ✅ Downloaded for specific drilldown analysis
**Relevance**: Neoplasms are the biggest driver of gender gaps in LE and HALE. This data allows for identifying which specific types of cancer (e.g., lung cancer, liver cancer, colorectal cancer, etc.) contribute most to the gap, providing more granular insights than the top-level "Neoplasms" category. Comparing US data with the OECD total helps contextualize the findings.

## Target Variables

### HALE (Healthy Life Expectancy) - Primary Target Variable

**Indicator**: WHOSIS_000002 - Healthy life expectancy (HALE) at birth (years)  
**Source**: WHO GHO API  
**File**: `data/who_hale_data.csv`  
**Status**: ✅ Implemented

**Data Details**:
- **Records**: 12,936 (full dataset)
- **Years**: 2000-2021 (22 years)
- **Countries**: 196
- **Sex categories**: Both sexes, Female, Male
- **Coverage**: Excellent temporal and country coverage

**Relevance**: HALE measures the average number of years that a person can expect to live in "full health" by taking into account years lived in less than full health due to disease and/or injury. This is the **primary target variable** for the analysis. The gender gap (Female HALE - Male HALE) measures the difference in healthy life expectancy between women and men.

### Life Expectancy - Secondary Target Variable

**Indicator**: WHOSIS_000001 - Life expectancy at birth (years)  
**Source**: WHO GHO API  
**File**: `data/who_life_expectancy_data.csv`  
**Status**: ✅ Implemented

**Data Details**:
- **Records**: 12,936 (full dataset)
- **Years**: 2000-2021 (22 years)
- **Countries**: 196
- **Sex categories**: Both sexes, Female, Male
- **Coverage**: Excellent temporal and country coverage, matches HALE coverage

**Relevance**: Life expectancy at birth measures the average number of years a person can expect to live, regardless of health status. This is the **secondary target variable** for the analysis, allowing comparison of which factors explain the gender gap in overall life expectancy versus healthy life expectancy. The gender gap (Female LE - Male LE) measures the difference in life expectancy between women and men.

**Key Differences from HALE**:
- Life expectancy captures all years lived (healthy and unhealthy), while HALE focuses on healthy years only
- Both are calculated from birth, so both should be affected by the same mortality patterns
- The relative importance of early-life vs adult mortality may differ between the two outcomes
- Factors affecting morbidity but not mortality may be less relevant for life expectancy

**Note on Temporal Coverage Limitation**: HALE and Life Expectancy data from WHO are currently only available through 2021. This limits the temporal coverage of analyses that include COVID-19 data, even though COVID-19 death rate data from IHME extends to 2023. When including COVID-19 as a predictor, the analysis cutoff year is set to 2021 (rather than 2023) to match the availability of the target variables. This ensures that all countries have complete data for both predictors and targets in the same years.

## Promising Indicators Checklist

Based on the [WHO GHO Indicators Index](https://www.who.int/data/gho/data/indicators/indicators-index), the following indicators are most relevant for analyzing HALE gender gaps. They are likely to differ between men and women and are related to causes of death.

### Already Implemented ✅
- [x] **HALE (Healthy Life Expectancy)** - Primary target variable (WHOSIS_000002)
- [x] **Life Expectancy** - Secondary target variable (WHOSIS_000001)
- [x] **Cardiovascular disease death rates** - Age-standardized, by gender
- [x] **Smoking prevalence** - Age-standardized tobacco smoking, by gender (M_Est_smk_curr_std)
- [x] **Suicide rates** - Age-standardized, by gender (MH_12)
- [x] **Alcohol-attributable death rates** - Age-standardized, by gender (SA_0000001832)
- [x] **Unintentional poisoning mortality rates** - By gender (SDGPOISON)
- [x] **Road traffic crash death rates** - Age-standardized (15+), by gender (SA_0000001459)
- [x] **Maternal mortality ratio** - Per 100,000 live births, female-specific (MDG_0000000026)
- [x] **Homicide rates** - By gender (VIOLENCE_HOMICIDERATE)
- [x] **Intimate partner violence prevalence** - Female-specific, prevalence indicator (SDGIPV)
- [x] **Under-five mortality rate** - By gender (MDG_0000000007) - ⚠️ **Removed from final model** - Tested but removed due to very low importance (0.0558 in LE model, not in top 10 for HALE) and minimal impact on model performance. IHME alternative also tested but excluded due to confounding with age structure and fertility rates. See validation.md for details.
- [x] **Diabetes death rates** - Age-standardized, by gender (SA_0000001440) - Note: Only 2004 data available, similar to cardiovascular disease indicators
- [x] **NCD mortality (30-70 years)** - Combined cardiovascular, cancer, diabetes, chronic respiratory disease (NCDMORT3070) - Note: Less specific than individual cause indicators but has excellent temporal coverage (2000-2021)
- [x] **Liver disease/cirrhosis death rates** - Age-standardized, by gender (IHME: Cirrhosis and other chronic liver diseases, 1990-2023)
- [x] **COVID-19 death rates** - By gender (IHME: COVID-19, 2020-2023) - Note: Data includes zeros for pre-2020 years

### High Priority - To Investigate
- [ ] **Tuberculosis deaths** - May have gender differences; TB deaths (excluding HIV)
- [ ] **HIV/AIDS mortality rates** - Can have gender differences, especially in certain regions
- [ ] **Chronic respiratory disease death rates** - Age-standardized, by gender (COPD, asthma, etc.)
- [ ] **Kidney disease death rates** - Age-standardized, by gender
- [ ] **Cancer death rates (specific types)** - Lung cancer, liver cancer, etc. (gender-specific patterns)

### Medium Priority - To Investigate
- [ ] **Air pollution attributable death rates** - May have gender differences due to occupational exposure
- [x] **Occupational injury death rates** - Likely much higher in men ⚠️ **Investigated** - Found multiple occupational indicators (OCC_1, OCC_3, OCC_19, OCC_21, etc.) but none have gender breakdowns, only 2004 data, and only 8 country/regions (not actual countries). Not suitable for model. See "Occupational Attributable Death Indicators" section above for details.
- [ ] **Drowning death rates** - May have gender differences
- [ ] **Fire/burn death rates** - May have gender differences
- [ ] **Falls death rates** - May have gender differences, especially in elderly
- [ ] **Ischemic heart disease death rates** - More specific than general cardiovascular
- [ ] **Stroke death rates** - Age-standardized, by gender

### Lower Priority - May Be Useful
- [ ] **Adult mortality rate (15-60 years)** - Probability of dying, by gender
- [ ] **Adolescent mortality rate** - May show early gender differences
- [ ] **Underweight prevalence (adults)** - BMI < 18.5, may affect mortality differently by gender
- [ ] **Obesity prevalence** - May have different mortality implications by gender

**Notes:**
- Focus on indicators with age-standardized rates when available (matches HALE methodology)
- Prioritize indicators with gender breakdowns (Male, Female, Both sexes)
- Consider temporal coverage - indicators with multiple years are preferred
- Some indicators may need to be searched by alternative names or codes

## WHO and IHME Indicator Correspondence

This table shows how WHO and IHME indicators correspond to each other, helping identify alternatives and complementary data sources.

| Indicator Category | WHO Indicator | WHO Code | WHO Temporal Coverage | IHME Indicator | IHME Code | IHME Temporal Coverage | Relationship |
|-------------------|---------------|----------|----------------------|----------------|-----------|----------------------|--------------|
| **Target Variables** |
| HALE | Healthy Life Expectancy | WHOSIS_000002 | 2000-2021 | — | — | — | WHO only (primary source) |
| Life Expectancy | Life Expectancy at Birth | WHOSIS_000001 | 2000-2021 | — | — | — | WHO only (primary source) |
| **Alcohol-Related** |
| Alcohol-attributable deaths | Alcohol-attributable all-cause deaths | SA_0000001832 | 2019 only | Alcohol use disorders | B.7.1 | 1990-2023 | IHME used in model (better temporal coverage, but narrower definition - see alcohol_data_comparison.md) |
| **Suicide/Self-Harm** |
| Suicide rates | Age-standardized suicide rates | MH_12 | 2000-2021 | Self-harm | B.7.3 | 1990-2023 | IHME used in model (better temporal coverage, importance increased) |
| **Violence/Homicide** |
| Homicide rates | Estimates of homicide rates | VIOLENCE_HOMICIDERATE | 2000-2021 | Interpersonal violence | B.7.4 | 1990-2023 | IHME used in model (better temporal coverage, but dropped out of LE model) |
| **Road Traffic** |
| Road traffic crashes | Road traffic crash deaths (15+) | SA_0000001459 | 2019 only | Road injuries | Road injuries | 1990-2023 | IHME used in model (much better temporal coverage, but very low importance) |
| **Maternal Mortality** |
| Maternal mortality ratio | Maternal mortality ratio | MDG_0000000026 | 1985-2023 | Maternal disorders | Maternal disorders | 1990-2023 | Both removed from model - counterintuitive positive coefficient (see validation.md) |
| **Child Mortality** |
| Under-five mortality rate | Under-five mortality rate | MDG_0000000007 | 1932-2023 | All-cause deaths under 5 | All causes (<5 years) | 1990-2023 | Both removed from model - WHO had very low importance; IHME confounded with age structure/fertility (see validation.md) |
| **Diabetes** |
| Diabetes death rates | Age-standardized diabetes death rates | SA_0000001440 | 2004 only | Diabetes type 2 | B.8.1.2 | 1990-2023 | IHME alternative (much better temporal coverage) |
| **Cardiovascular Disease** |
| Cardiovascular disease | Age-standardized cardiovascular death rates | Various (WHS2_161, etc.) | 2004 only | Cardiovascular diseases | B.2 | 1990-2023 | IHME alternative (much better temporal coverage) |
| **Chronic Respiratory Disease** |
| — | — | — | — | Chronic respiratory diseases | B.3 | 1990-2023 | IHME only (no WHO equivalent with good coverage) |
| **Liver Disease** |
| — | — | — | — | Cirrhosis and other chronic liver diseases | Cirrhosis and other chronic liver diseases | 1990-2023 | IHME only (no WHO equivalent with good coverage) |
| **COVID-19** |
| — | — | — | — | COVID-19 | COVID-19 | 2020-2023 | IHME only (no WHO equivalent with good coverage) |
| **Cancer** |
| — | — | — | — | Neoplasms (cancer) | B.1 | 1990-2023 | IHME only (no WHO equivalent with good coverage) |
| **Injuries** |
| Unintentional poisoning | Mortality rate from unintentional poisoning | SDGPOISON | 2000-2021 | — | — | — | WHO removed from model (not selected) |
| Unintentional injuries | — | — | — | Unintentional injuries | Unintentional injuries | 1990-2023 | IHME used in model (broader than WHO poisoning) |
| **Drug Use** |
| Unintentional poisoning | Mortality rate from unintentional poisoning | SDGPOISON | 2000-2021 | Drug use disorders | B.7.2 | 1990-2023 | IHME used in model (WHO poisoning removed, but IHME DrugDisorder has 0 importance - not selected) |
| **Other** |
| Smoking prevalence | Age-standardized tobacco smoking | M_Est_smk_curr_std | 2000-2030 | — | — | — | WHO only (prevalence indicator, not mortality) |
| NCD mortality (30-70) | Probability of dying 30-70 from NCDs | NCDMORT3070 | 2000-2021 | — | — | — | WHO only (combined indicator) |
| Intimate partner violence | IPV prevalence | SDGIPV | 2000-2017 | — | — | — | WHO only (prevalence indicator, not mortality) |

### Notes on Correspondence:

1. **IHME alternatives with better temporal coverage**: Alcohol use disorders, Self-harm, Interpersonal violence, Road injuries, Diabetes type 2, and Cardiovascular diseases all have IHME versions with much better temporal coverage (1990-2023) compared to their WHO counterparts (often 2004 or 2019 only).

2. **Complementary indicators**: 
   - Maternal mortality: WHO uses ratio per 100,000 live births; IHME uses rate per 100,000 population
   - Under-five mortality: WHO uses rate per 1,000 live births; IHME all-cause under-5 uses rate per 100,000 population

3. **IHME-only indicators**: Chronic respiratory diseases, Liver disease (cirrhosis and other chronic liver diseases), COVID-19, Neoplasms, Unintentional injuries, and Drug use disorders are available from IHME but have no good WHO equivalent with adequate temporal coverage.

4. **WHO-only indicators**: Smoking prevalence, NCD mortality (30-70), Intimate partner violence, and Unintentional poisoning are available from WHO but have no IHME equivalent.

5. **Target variables**: HALE and Life Expectancy are only available from WHO and serve as the primary target variables for the analysis.

