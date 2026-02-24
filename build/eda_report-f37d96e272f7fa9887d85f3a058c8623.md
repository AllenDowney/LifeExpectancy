# Exploratory Data Analysis: Summary Report

## Purpose

This report summarizes the exploratory data analysis of gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy, along with the predictors used in the Bayesian panel data model. The analysis focuses on OECD countries using the most recent available data up to 2019 (excluding 2020+ to avoid COVID-19 pandemic distortions).

## Target Variables

### Healthy Life Expectancy (HALE)

**HALE at birth** measures the average number of years that a person can expect to live in "full health" by taking into account years lived in less than full health due to disease and/or injury. This is the primary target variable for the analysis.

The gender gap is calculated as Female HALE - Male HALE (positive values indicate women live longer in full health).

```{figure} figs/hale_scatter.png
:name: hale_scatter
:width: 100%

HALE: Female vs Male and Gap vs Overall (OECD Countries)
```

### Life Expectancy

**Life Expectancy at birth** measures the average number of years that a person can expect to live, regardless of health status. This is the secondary target variable, allowing comparison of which factors explain the gender gap in overall life expectancy versus healthy life expectancy.

The gender gap is calculated as Female Life Expectancy - Male Life Expectancy (positive values indicate women live longer).

```{figure} figs/life_expectancy_scatter.png
:name: le_scatter
:width: 100%

Life Expectancy: Female vs Male and Gap vs Overall (OECD Countries)
```

## Predictors

The following predictors are used in the Bayesian panel data model. All indicators are from IHME (Institute for Health Metrics and Evaluation) Global Burden of Disease data, providing consistent methodology and temporal coverage (1990-2023).

### Alcohol Use Disorders

**Alcohol use disorders death rates (per 100,000 population)** - Deaths from alcohol use disorders. Men typically have higher rates of alcohol-related mortality than women.

```{figure} figs/alcohol_ihme_scatter.png
:name: alcohol_scatter
:width: 100%

Alcohol Use Disorders: Female vs Male and Gap vs Overall (OECD Countries)
```

### Self-Harm (Suicide)

**Self-harm (suicide) death rates (per 100,000 population)** - Deaths from self-harm (suicide). Men typically have much higher suicide rates than women in most countries.

```{figure} figs/self_harm_scatter.png
:name: suicide_scatter
:width: 100%

Self-Harm (Suicide): Female vs Male and Gap vs Overall (OECD Countries)
```

### Interpersonal Violence (Homicide)

**Interpersonal violence (homicide) death rates (per 100,000 population)** - Deaths from interpersonal violence (homicide). Men typically have much higher homicide rates than women in most countries.

```{figure} figs/interpersonal_violence_scatter.png
:name: homicide_scatter
:width: 100%

Interpersonal Violence (Homicide): Female vs Male and Gap vs Overall (OECD Countries)
```

### Road Injuries

**Road injuries (road traffic crash) death rates (per 100,000 population)** - Deaths from road injuries (road traffic crashes). Men typically have 2-4 times higher road traffic death rates than women due to higher exposure to driving and occupational hazards.

```{figure} figs/road_injuries_scatter.png
:name: road_traffic_scatter
:width: 100%

Road Injuries: Female vs Male and Gap vs Overall (OECD Countries)
```

### Cardiovascular Disease

**Cardiovascular diseases death rates (per 100,000 population)** - Deaths from cardiovascular diseases. Men typically have higher rates of cardiovascular disease and heart attacks.

```{figure} figs/cardiovascular_ihme_scatter.png
:name: cardiovascular_scatter
:width: 100%

Cardiovascular Disease: Female vs Male and Gap vs Overall (OECD Countries)
```

### Diabetes

**Diabetes mellitus type 2 death rates (per 100,000 population)** - Deaths from diabetes mellitus type 2. Diabetes is a chronic condition that can contribute to the gender gap in mortality.

```{figure} figs/diabetes_ihme_scatter.png
:name: diabetes_scatter
:width: 100%

Diabetes: Female vs Male and Gap vs Overall (OECD Countries)
```

### Neoplasms (Cancer)

**Neoplasms (cancer) death rates (per 100,000 population)** - Deaths from neoplasms (cancer). Different types of cancer have different gender patterns (e.g., lung cancer is often higher in men, breast cancer is female-specific).

```{figure} figs/neoplasms_scatter.png
:name: neoplasms_scatter
:width: 100%

Neoplasms (Cancer): Female vs Male and Gap vs Overall (OECD Countries)
```

### Chronic Respiratory Disease

**Chronic respiratory diseases death rates (per 100,000 population)** - Deaths from chronic respiratory diseases (including COPD, asthma, and other chronic lung conditions). These diseases often have gender differences due to factors such as smoking patterns and occupational exposures.

```{figure} figs/chronic_respiratory_scatter.png
:name: chronic_respiratory_scatter
:width: 100%

Chronic Respiratory Disease: Female vs Male and Gap vs Overall (OECD Countries)
```

### Liver Disease

**Liver disease death rates (per 100,000 population)** - Deaths from cirrhosis and other chronic liver diseases. Men typically have higher rates of liver disease mortality than women, often due to higher alcohol consumption and hepatitis infections.

```{figure} figs/liver_disease_scatter.png
:name: liver_disease_scatter
:width: 100%

Liver Disease: Female vs Male and Gap vs Overall (OECD Countries)
```

### Unintentional Injuries

**Unintentional injuries death rates (per 100,000 population)** - Deaths from unintentional injuries (including falls, drowning, fires, and other accidents). These injuries often show gender differences due to occupational exposures and risk-taking behaviors.

```{figure} figs/unintentional_injuries_scatter.png
:name: unintentional_injuries_scatter
:width: 100%

Unintentional Injuries: Female vs Male and Gap vs Overall (OECD Countries)
```

## Summary Statistics

### Target Variables by Country

The following tables show HALE and Life Expectancy gender gaps for all OECD countries, ranked by gap size.

```{include} tables/hale_gap_by_country_2019.html
```

**Summary:**
- Countries are ranked by HALE gap (Female - Male), with positive values indicating women live longer in full health
- The table shows Male HALE, Female HALE, and the gender gap for each country
- Countries with larger gaps have greater gender differences in healthy life expectancy

```{include} tables/le_gap_by_country_2019.html
```

**Summary:**
- Countries are ranked by Life Expectancy gap (Female - Male), with positive values indicating women live longer overall
- The table shows Male Life Expectancy, Female Life Expectancy, and the gender gap for each country
- Life Expectancy gaps are typically larger than HALE gaps, reflecting that women's advantage in total years lived is greater than their advantage in healthy years

### Predictors: Rates and Gaps

The following tables summarize the distribution of predictors across OECD countries, showing both overall rates (midpoint between male and female values) and gender gaps.

```{include} tables/predictor_rates_2019.html
```

**Summary:**
- Shows median, minimum, and maximum rates for each predictor across OECD countries
- Rates represent the midpoint (average) between male and female values
- Includes correlations with HALE gap and Life Expectancy gap
- Higher correlations indicate stronger relationships between predictor rates and gender gaps in outcomes

```{include} tables/predictor_gaps_2019.html
```

**Summary:**
- Shows median, minimum, and maximum gender gaps for each predictor
- Gaps are calculated as Male - Female (positive values indicate men have higher rates)
- Includes correlations with HALE gap and Life Expectancy gap
- Predictor gaps with strong correlations are likely important drivers of gender gaps in HALE and Life Expectancy

### Target Variables: Rates and Gaps

```{include} tables/target_rates_2019.html
```

**Summary:**
- Shows median, minimum, and maximum values for HALE and Life Expectancy across OECD countries
- Represents overall levels of healthy life expectancy and life expectancy
- Provides context for understanding the scale of gender gaps relative to overall levels

```{include} tables/target_gaps_2019.html
```

**Summary:**
- Shows median, minimum, and maximum gender gaps for HALE and Life Expectancy
- Gaps are calculated as Female - Male (positive values indicate women live longer)
- HALE gaps are typically smaller than Life Expectancy gaps, indicating that women's advantage in healthy years is less than their advantage in total years lived

## Relationships Between Predictors

### Rate-Gap Correlations

The following table shows correlations between overall rates (Mid) and gender gaps (Gap) for each predictor.

```{include} tables/rate_gap_correlation_2019.html
```

**Summary:**
- High positive correlations indicate that predictors with higher overall rates also tend to have larger gender gaps
- High negative correlations indicate that predictors with higher overall rates tend to have smaller gender gaps (or vice versa)
- These correlations help understand whether gender gaps are driven by overall levels or are independent of them

### Inter-Predictor Correlations

The following tables show correlations between predictors, helping identify which predictors tend to co-occur or are related.

```{include} tables/rate_rate_correlation_top10_2019.html
```

**Summary:**
- Shows the top 10 correlations between overall rates (Mid columns) of different predictors
- High correlations indicate that certain mortality causes tend to occur together across countries
- For example, cardiovascular disease and diabetes may be highly correlated due to shared risk factors

```{include} tables/gap_gap_correlation_top10_2019.html
```

**Summary:**
- Shows the top 10 correlations between gender gaps (Gap columns) of different predictors
- High correlations indicate that gender gaps in different predictors tend to co-occur
- For example, gender gaps in external causes (road traffic, homicide, suicide) may be correlated, reflecting shared patterns of risk-taking behavior or occupational exposure

## Key Findings

### Gender Gaps in Target Variables

1. **HALE Gap**: Women consistently live longer in full health than men across OECD countries, with gaps ranging from approximately 1 to 6 years.

2. **Life Expectancy Gap**: Women consistently live longer overall than men, with gaps typically larger than HALE gaps (ranging from approximately 2 to 8 years).

3. **Relationship**: The correlation between HALE gap and Life Expectancy gap is strong, indicating that countries with larger gender differences in total life expectancy also tend to have larger gender differences in healthy life expectancy.

### Gender Gaps in Predictors

1. **External Causes**: Gender gaps are largest for external causes of death (road traffic, homicide, suicide), with men having substantially higher rates than women.

2. **Chronic Diseases**: Gender gaps in chronic diseases (cardiovascular, neoplasms, chronic respiratory) vary by disease type and country, with some showing larger gaps than others.

3. **Substance-Related**: Gender gaps in alcohol use disorders and liver disease are substantial, with men having higher rates, consistent with higher alcohol consumption patterns.

### Relationships Between Predictors and Outcomes

1. **Strong Correlations**: Predictor gaps with strong correlations to HALE and Life Expectancy gaps are likely important drivers of gender differences in these outcomes.

2. **Rate vs Gap**: The relationship between overall rates and gender gaps varies by indicator, with some showing strong correlations and others showing independence.

3. **Co-occurrence**: High correlations between predictors suggest shared underlying factors (e.g., socioeconomic conditions, healthcare access, cultural norms) that affect multiple mortality causes simultaneously.

## Data Quality and Coverage

- **Temporal Coverage**: All indicators use data from 2000-2019, with the most recent available year selected for each country
- **Country Coverage**: Analysis focuses on OECD countries, providing a relatively homogeneous set of high-income countries
- **Data Sources**: 
  - Target variables (HALE, Life Expectancy): WHO Global Health Observatory
  - Predictors: IHME Global Burden of Disease (provides consistent methodology and better temporal coverage than WHO alternatives)
- **Missing Data**: Complete-case analysis is used, with countries missing any indicator excluded from the final analysis dataset

## Next Steps

This exploratory analysis provides the foundation for:
1. **Bayesian Panel Data Modeling**: Using both temporal and cross-country variation to identify predictors of gender gaps
2. **Counterfactual Analysis**: Understanding how changes in predictor values would affect gender gaps
3. **Policy Implications**: Identifying which factors are most important for reducing gender gaps in healthy life expectancy

