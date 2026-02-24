# Time Series Analysis: Trends in Health Indicators and Gender Gaps (2000-2019)

## Purpose

This report examines temporal trends in health indicators and gender gaps across OECD countries from 2000 to 2019. By analyzing data across all years in this period, we can observe:

- How gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy (LE) have evolved over time
- Trends in overall mortality rates (Mid values) for each health indicator
- Trends in gender gaps (Gap values) for each health indicator
- Which countries have shown the most improvement or deterioration in specific indicators
- Which indicators show the strongest trends (increasing or decreasing) over the two-decade period

This temporal analysis complements the cross-sectional modeling approach by revealing dynamic patterns that may not be apparent in single-year snapshots. Understanding these trends helps identify:

- Areas where progress has been made (narrowing gaps, declining rates)
- Areas of concern (widening gaps, increasing rates)
- Countries that serve as positive examples of improvement
- Indicators with the strongest temporal trends that may require targeted interventions

## Methodology

### Data Sources and Time Period

- **Time Period**: 2000-2019 (excluding 2020+ to avoid COVID-19 pandemic distortions)
- **Data Sources**:
  - **WHO Global Health Observatory**: HALE and Life Expectancy data
  - **IHME Global Burden of Disease**: Cause-specific mortality indicators (cardiovascular disease, diabetes, chronic respiratory disease, neoplasms, alcohol use disorders, self-harm/suicide, interpersonal violence/homicide, road injuries, unintentional injuries, liver disease)

### Data Processing

For each indicator, we:

1. **Load temporal data**: Preserve all years from 2000-2019 (not just the most recent year)
2. **Compute gender gaps**: For each year, calculate the difference between male and female values
   - For predictors: Gap = Male - Female (positive gap means higher male rates)
   - For targets (HALE/LE): Gap = Female - Male (positive gap means women live longer)
3. **Compute midpoint values**: Average of male and female values, representing overall rates
4. **Filter to OECD countries**: Focus on 38 OECD countries for consistency and data quality

### Statistical Analysis

For each indicator and country, we compute:

- **Mean**: Average value across all years (2000-2019)
- **Slope**: Linear trend over time 

For each indicator, we identify countries with:

- **Highest Mean**: Country with the highest average value over the period
- **Lowest Mean**: Country with the lowest average value over the period
- **Highest Slope**: Country with the largest positive slope (most increasing trend)
- **Lowest Slope**: Country with the most negative slope (most decreasing trend)


## HALE and Life Expectancy

### HALE Time Series (Overall Rates)

The following figures show changes in HALE in all countries and in selected countries.

```{figure} figs/hale_timeseries_all.png
:name: hale_all
:width: 100%

HALE Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/hale_timeseries_selected.png
:name: hale_selected
:width: 100%

HALE Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Increasing trends**: Most countries show increasing HALE over time, reflecting overall improvements in population health
- **Wide variation**: HALE ranges from around 60 years to over 70 years across OECD countries
- **Convergence**: Some convergence is evident, with countries with lower initial HALE showing faster improvement

### Life Expectancy Time Series (Overall Rates)

The following figures show changes in life expectancy in all countries and in selected countries.

```{figure} figs/le_timeseries_all.png
:name: le_all
:width: 100%

Life Expectancy Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/le_timeseries_selected.png
:name: le_selected
:width: 100%

Life Expectancy Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Increasing trends**: Life Expectancy has increased across most OECD countries over the two-decade period
- **Wide variation**: Life Expectancy ranges from around 70 years to over 80 years
- **Overall improvement**: The OECD average shows steady improvement, reflecting successful public health interventions

**Relationship between Levels and Gaps:**
- Countries with higher overall HALE/LE don't necessarily have smaller gaps
- Some countries (e.g., Netherlands) achieve both high levels and small gaps
- The gap analysis complements the level analysis by highlighting gender equity dimensions


### HALE Gap Trends

The HALE gap represents the difference in Healthy Life Expectancy between women and men (Female - Male, in years). A positive gap means women have longer healthy life expectancy.

```{figure} figs/hale_gap_timeseries_all.png
:name: hale_gap_all
:width: 100%

HALE Gender Gap Over Time (2000-2019) - All OECD Countries
```

The figure above shows HALE gap trends for all OECD countries. Several patterns are evident:

- **Wide variation**: Gaps range from near zero (Netherlands, Switzerland) to over 6 years (Latvia, Lithuania)
- **Stability**: Most countries show relatively stable gaps over time, with gradual changes
- **Convergence**: Some countries (notably in Northern Europe) have gaps close to zero, demonstrating that large gaps are not inevitable

```{figure} figs/hale_gap_timeseries_selected.png
:name: hale_gap_selected
:width: 100%

HALE Gender Gap Over Time (2000-2019) - Selected Countries
```

The selected countries view highlights key examples:
- **Netherlands**: Consistently near-zero gap, showing that gender equity in healthy life expectancy is achievable
- **United States**: Moderate gap (~3-4 years) with slight narrowing over time
- **Latvia/Lithuania**: Large gaps (6-7 years) that have remained relatively stable
- **OECD Average**: Shows a gradual narrowing trend, suggesting overall improvement

### Life Expectancy Gap Trends

The Life Expectancy gap represents the difference in overall Life Expectancy between women and men (Female - Male, in years).

```{figure} figs/le_gap_timeseries_all.png
:name: le_gap_all
:width: 100%

Life Expectancy Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/le_gap_timeseries_selected.png
:name: le_gap_selected
:width: 100%

Life Expectancy Gender Gap Over Time (2000-2019) - Selected Countries
```

Life Expectancy gaps show similar patterns to HALE gaps, but are generally larger (since they include years lived in poor health). The OECD average shows a gradual narrowing trend over the two-decade period.

### Value Changes: 2000 to 2019

The following table shows how HALE values changed for each country over the two-decade period:

```{include} tables/hale_value_changes_2000_2019.html
```

The following table shows how Life Expectancy values changed for each country over the two-decade period:

```{include} tables/le_value_changes_2000_2019.html
```

**Key Findings from Value Changes:**

- **Most countries show increases**: The vast majority of OECD countries have seen their HALE and Life Expectancy increase from 2000 to 2019
- **Substantial improvements**: Many countries gained 2-4 years in HALE and 3-5 years in Life Expectancy over the period
- **Variation in improvement rates**: Some countries show faster improvement than others, reflecting different public health trajectories
- **Overall progress**: The widespread increases demonstrate overall improvements in population health across OECD countries

### Gap Changes: 2000 to 2019

The following table shows how HALE gaps changed for each country over the two-decade period:

```{include} tables/hale_gap_changes_2000_2019.html
```

The following table shows how Life Expectancy gaps changed for each country over the two-decade period:

```{include} tables/le_gap_changes_2000_2019.html
```

**Key Findings from Gap Changes:**

- **Most countries show narrowing gaps**: The majority of OECD countries have seen their gender gaps decrease from 2000 to 2019
- **Variation in magnitude**: Changes range from substantial narrowing (>1 year) to slight widening
- **Consistent patterns**: Countries that narrowed HALE gaps also tended to narrow LE gaps
- **Positive examples**: Several countries (e.g., Netherlands, Switzerland) maintain or achieved near-zero gaps

**Relationship between Value and Gap Changes:**
- Countries can improve in both absolute values and gender equity simultaneously
- Some countries show large increases in HALE/LE while also narrowing gender gaps
- The combination of increasing values and narrowing gaps represents the best outcome—improving health for everyone while reducing disparities

### Summary
#### Overall Values (HALE and Life Expectancy)

```{include} tables/target_values_summary_timeseries.html
```

#### Gender Gaps (HALE Gap and Life Expectancy Gap)

```{include} tables/target_gaps_summary_timeseries.html
```


## Health Indicator Trends

This section examines temporal trends for each of the 10 health indicators used in the predictive models. For each indicator, we show:

1. **Overall rates (Mid values)**: Average of male and female rates, representing the overall mortality burden
2. **Gender gaps (Gap values)**: Difference between male and female rates (Male - Female)

### Alcohol Use Disorders

Alcohol use disorders represent deaths directly attributable to alcohol consumption.

```{figure} figs/alcohol_rate_timeseries_all.png
:name: alcohol_rate_all
:width: 100%

Alcohol Use Disorders Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/alcohol_rate_timeseries_selected.png
:name: alcohol_rate_selected
:width: 100%

Alcohol Use Disorders Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/alcohol_gap_timeseries_all.png
:name: alcohol_gap_all
:width: 100%

Alcohol Use Disorders Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/alcohol_gap_timeseries_selected.png
:name: alcohol_gap_selected
:width: 100%

Alcohol Use Disorders Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **High variation across countries**: Rates range from very low (<5 per 100,000) to moderate (15-25 per 100,000)
- **Large gender gaps**: Men consistently have much higher alcohol-related death rates than women
- **Declining trends in some countries**: Several countries show decreasing rates over time, suggesting successful public health interventions

### Cardiovascular Disease

Cardiovascular disease is one of the leading causes of death globally.

```{figure} figs/cardiovascular_rate_timeseries_all.png
:name: cardiovascular_rate_all
:width: 100%

Cardiovascular Disease Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/cardiovascular_rate_timeseries_selected.png
:name: cardiovascular_rate_selected
:width: 100%

Cardiovascular Disease Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/cardiovascular_gap_timeseries_all.png
:name: cardiovascular_gap_all
:width: 100%

Cardiovascular Disease Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/cardiovascular_gap_timeseries_selected.png
:name: cardiovascular_gap_selected
:width: 100%

Cardiovascular Disease Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **High overall rates**: Cardiovascular disease has the highest death rates among all indicators
- **Declining trends**: Most countries show substantial declines in cardiovascular death rates, reflecting successful prevention and treatment efforts
- **Moderate gender gaps**: Men have higher rates, but the gap is smaller than for some other indicators (e.g., alcohol, suicide)
- **Narrowing gaps**: Gender gaps have narrowed in many countries, suggesting improvements in men's cardiovascular health

### Chronic Respiratory Disease

Chronic respiratory diseases include conditions like COPD and asthma.

```{figure} figs/chronic_respiratory_rate_timeseries_all.png
:name: chronic_respiratory_rate_all
:width: 100%

Chronic Respiratory Disease Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/chronic_respiratory_rate_timeseries_selected.png
:name: chronic_respiratory_rate_selected
:width: 100%

Chronic Respiratory Disease Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/chronic_respiratory_gap_timeseries_all.png
:name: chronic_respiratory_gap_all
:width: 100%

Chronic Respiratory Disease Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/chronic_respiratory_gap_timeseries_selected.png
:name: chronic_respiratory_gap_selected
:width: 100%

Chronic Respiratory Disease Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Moderate rates**: Lower than cardiovascular but still significant
- **Declining trends**: Most countries show decreasing rates over time
- **Gender gaps**: Men generally have higher rates, with gaps varying by country

### Suicide (Self-Harm)

Suicide represents intentional self-harm deaths.

```{figure} figs/suicide_rate_timeseries_all.png
:name: suicide_rate_all
:width: 100%

Suicide Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/suicide_rate_timeseries_selected.png
:name: suicide_rate_selected
:width: 100%

Suicide Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/suicide_gap_timeseries_all.png
:name: suicide_gap_all
:width: 100%

Suicide Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/suicide_gap_timeseries_selected.png
:name: suicide_gap_selected
:width: 100%

Suicide Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Large gender gaps**: Men have much higher suicide rates than women in all countries
- **Variation across countries**: Rates vary substantially, with some countries showing much higher rates
- **Mixed trends**: Some countries show declining rates (successful prevention), while others show increases (concerning trend)
- **Critical intervention target**: Given the large gaps and their importance in explaining HALE/LE gaps, suicide prevention is a high priority

### Homicide (Interpersonal Violence)

Homicide represents deaths from intentional interpersonal violence.

```{figure} figs/homicide_rate_timeseries_all.png
:name: homicide_rate_all
:width: 100%

Homicide Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/homicide_rate_timeseries_selected.png
:name: homicide_rate_selected
:width: 100%

Homicide Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/homicide_gap_timeseries_all.png
:name: homicide_gap_all
:width: 100%

Homicide Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/homicide_gap_timeseries_selected.png
:name: homicide_gap_selected
:width: 100%

Homicide Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Low overall rates**: Homicide rates are generally low in OECD countries (<5 per 100,000 in most)
- **Large gender gaps**: Men have much higher homicide rates than women
- **Declining trends**: Most countries show substantial declines, reflecting improvements in public safety
- **High variation**: Some countries (e.g., Mexico, United States) have notably higher rates

### Road Traffic Injuries

Road traffic injuries represent deaths from motor vehicle accidents.

```{figure} figs/road_traffic_rate_timeseries_all.png
:name: road_traffic_rate_all
:width: 100%

Road Traffic Injury Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/road_traffic_rate_timeseries_selected.png
:name: road_traffic_rate_selected
:width: 100%

Road Traffic Injury Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/road_traffic_gap_timeseries_all.png
:name: road_traffic_gap_all
:width: 100%

Road Traffic Injury Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/road_traffic_gap_timeseries_selected.png
:name: road_traffic_gap_selected
:width: 100%

Road Traffic Injury Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Declining trends**: Most countries show substantial declines in road traffic deaths, reflecting improvements in vehicle safety, road infrastructure, and traffic laws
- **Large gender gaps**: Men have much higher rates than women
- **Success story**: Road traffic injuries have become less important in explaining gender gaps over time, suggesting successful interventions

### Liver Disease

Liver disease includes deaths from cirrhosis, hepatitis, and other liver conditions.

```{figure} figs/liver_disease_rate_timeseries_all.png
:name: liver_disease_rate_all
:width: 100%

Liver Disease Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/liver_disease_rate_timeseries_selected.png
:name: liver_disease_rate_selected
:width: 100%

Liver Disease Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/liver_disease_gap_timeseries_all.png
:name: liver_disease_gap_all
:width: 100%

Liver Disease Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/liver_disease_gap_timeseries_selected.png
:name: liver_disease_gap_selected
:width: 100%

Liver Disease Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Moderate rates**: Lower than cardiovascular but still significant
- **Gender gaps**: Men generally have higher rates
- **Mixed trends**: Some countries show declining rates, while others are stable or increasing

### Neoplasms (Cancer)

Neoplasms represent deaths from all types of cancer.

```{figure} figs/neoplasms_rate_timeseries_all.png
:name: neoplasms_rate_all
:width: 100%

Cancer Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/neoplasms_rate_timeseries_selected.png
:name: neoplasms_rate_selected
:width: 100%

Cancer Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/neoplasms_gap_timeseries_all.png
:name: neoplasms_gap_all
:width: 100%

Cancer Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/neoplasms_gap_timeseries_selected.png
:name: neoplasms_gap_selected
:width: 100%

Cancer Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **High overall rates**: Cancer is one of the leading causes of death
- **Declining trends**: Many countries show declining cancer death rates, reflecting improvements in prevention, screening, and treatment
- **Gender gaps vary**: Some countries show higher male rates, while others show higher female rates (depending on cancer types)
- **Increasing importance**: Cancer has become the dominant factor in explaining gender gaps in HALE and LE (see temporal analysis report)

### Unintentional Injuries

Unintentional injuries include deaths from accidents not classified elsewhere (falls, poisonings, etc.).

```{figure} figs/unintentional_injury_rate_timeseries_all.png
:name: unintentional_injury_rate_all
:width: 100%

Unintentional Injury Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/unintentional_injury_rate_timeseries_selected.png
:name: unintentional_injury_rate_selected
:width: 100%

Unintentional Injury Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/unintentional_injury_gap_timeseries_all.png
:name: unintentional_injury_gap_all
:width: 100%

Unintentional Injury Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/unintentional_injury_gap_timeseries_selected.png
:name: unintentional_injury_gap_selected
:width: 100%

Unintentional Injury Gender Gap Over Time (2000-2019) - Selected Countries
```

**Key Observations:**
- **Moderate rates**: Significant but lower than cardiovascular and cancer
- **Large gender gaps**: Men have much higher rates than women
- **Declining trends**: Most countries show declining rates, suggesting improvements in safety

### Diabetes

Diabetes represents deaths from diabetes mellitus (primarily type 2).

```{figure} figs/diabetes_rate_timeseries_all.png
:name: diabetes_rate_all
:width: 100%

Diabetes Death Rate Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/diabetes_rate_timeseries_selected.png
:name: diabetes_rate_selected
:width: 100%

Diabetes Death Rate Over Time (2000-2019) - Selected Countries
```

```{figure} figs/diabetes_gap_timeseries_all.png
:name: diabetes_gap_all
:width: 100%

Diabetes Gender Gap Over Time (2000-2019) - All OECD Countries
```

```{figure} figs/diabetes_gap_timeseries_selected.png
:name: diabetes_gap_selected
:width: 100%

Diabetes Gender Gap Over Time (2000-2019) - All OECD Countries
```

**Key Observations:**
- **Moderate rates**: Lower than cardiovascular and cancer but still significant
- **Increasing trends**: Many countries show increasing diabetes rates, reflecting the global diabetes epidemic
- **Gender gaps vary**: Gaps vary by country and may be narrowing in some areas

## Summary: Indicator Superlatives

The following tables summarize which countries have the highest and lowest means and slopes for each indicator, providing insights into:

1. **Which countries have the best/worst outcomes** (highest/lowest means)
2. **Which countries are improving most/least** (highest/lowest slopes)

### Overall Rates (Mid Values)

```{include} tables/indicator_rates_summary_timeseries.html
```

**Key Insights from Rates Summary:**

- **Cardiovascular disease**: Shows the highest overall rates, but most countries have declining trends (negative slopes)
- **Cancer (Neoplasms)**: High rates with mixed trends—some countries improving, others stable
- **Road traffic injuries**: Generally show strong declining trends, reflecting successful safety interventions
- **Suicide**: Mixed trends—some countries showing concerning increases, others showing improvements
- **Diabetes**: Many countries show increasing trends, reflecting the global diabetes epidemic

### Gender Gaps (Gap Values)

```{include} tables/indicator_gaps_summary_timeseries.html
```

**Key Insights from Gaps Summary:**

- **Large gaps persist**: Most indicators show substantial gender gaps, with men having higher rates
- **Suicide and homicide**: Show the largest gender gaps, with men having much higher rates
- **Mixed trends**: Some indicators show narrowing gaps (improvement), while others show widening gaps (concern)
- **Alcohol and liver disease**: Show large gaps with varying trends across countries

## Key Findings and Conclusions

### Overall Trends

1. **Gender gaps are narrowing**: Both HALE and Life Expectancy gaps show gradual narrowing trends across OECD countries, suggesting overall improvement in gender equity in health outcomes.

2. **Success stories**: Several countries (notably Netherlands, Switzerland) have achieved or maintained near-zero gender gaps in HALE, demonstrating that large gaps are not inevitable.

3. **Variation persists**: Despite overall improvement, substantial variation remains across countries, with gaps ranging from near zero to over 6 years.

### Indicator-Specific Findings

1. **Cardiovascular disease**: 
   - Declining rates across most countries (success story)
   - Gender gaps narrowing (improvement in men's cardiovascular health)
   - Declining importance in explaining gender gaps over time

2. **Cancer (Neoplasms)**:
   - Increasing importance in explaining gender gaps (now dominant factor)
   - Declining rates in many countries (improvements in prevention/treatment)
   - Gender gaps vary by country and cancer type

3. **Suicide**:
   - Large gender gaps persist (men have much higher rates)
   - Mixed trends across countries (some improving, some worsening)
   - Critical intervention target given its importance in explaining gaps

4. **Road traffic injuries**:
   - Strong declining trends (successful safety interventions)
   - Declining importance in explaining gender gaps
   - Demonstrates that targeted interventions can be effective

5. **Diabetes**:
   - Increasing rates in many countries (global epidemic)
   - Requires continued attention and intervention

### Policy Implications

1. **Priority interventions**:
   - **Suicide prevention**: Highest potential impact on gender gaps
   - **Cancer prevention and treatment**: Dominant factor in explaining gaps
   - **Unintentional injury prevention**: Consistently important across time periods

2. **Success stories to learn from**:
   - **Cardiovascular disease**: Successful prevention and treatment programs
   - **Road traffic injuries**: Effective safety regulations and infrastructure improvements
   - **Countries with near-zero gaps**: Netherlands, Switzerland provide models for other countries

3. **Areas of concern**:
   - **Diabetes**: Increasing rates require attention
   - **Suicide**: Mixed trends suggest need for targeted prevention programs
   - **Persistent gaps**: Large gender gaps in several indicators suggest need for gender-specific interventions


---

## Notes

- All analyses use data from 2000-2019, excluding 2020+ to avoid COVID-19 pandemic distortions
- OECD countries (38 countries) are included for consistency and data quality
- Gender gaps are calculated as Male - Female for predictors, Female - Male for targets (HALE/LE)
- Linear trends (slopes) provide a simple summary but may not capture non-linear patterns
- Mean values provide overall burden but may mask important temporal variation
