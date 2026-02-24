# Model Validation: Replacing WHO Indicators with IHME Indicators

## Purpose

This document compares the results of replacing WHO indicators with IHME indicators one at a time to validate that data source changes don't introduce unexpected artifacts or substantially alter model conclusions. Each replacement is tested independently by re-running the analysis and comparing results to the baseline (all WHO indicators).

This validation process serves as a form of model validation, ensuring that:
- Model conclusions remain stable when using alternative data sources
- Definitional differences between WHO and IHME indicators are understood
- Any substantial changes in results are documented and explained

## Validation Framework

For each indicator replacement, we compare the following metrics:

**Model Performance:**
- Cross-validation R² for both Life Expectancy and HALE models
- Mean Absolute Error (MAE) for both models
- Number of non-zero coefficients selected by Elastic Net

**Feature Importance:**
- Indicator importance (total, Mid component, Gap component) for both Life Expectancy and HALE
- Ranking of the indicator relative to other indicators
- Changes in importance of other indicators

**Counterfactual Analysis:**
- Counterfactual effect for USA (change in gap when reducing indicator gap to best attainable level)
- Aggregate gap-closing and gap-widening totals
- Net reduction in predicted gap

**Key Questions for Each Replacement:**
1. Does the indicator maintain its relative importance ranking?
2. Are the counterfactual effects similar in magnitude?
3. Do the model performance metrics (R², MAE) change significantly?
4. Are definitional differences between WHO and IHME indicators understood?

## Alcohol: WHO → IHME

### Replacement Details

- **WHO Indicator**: `SA_0000001832` - Alcohol-attributable all-cause deaths per 100,000 (age-standardized)
- **WHO Temporal Coverage**: 2019 only
- **IHME Indicator**: `B.7.1` - Alcohol use disorders, death rate per 100,000
- **IHME Temporal Coverage**: 1990-2023
- **Definitional Difference**: WHO includes all deaths where alcohol is a contributing factor (e.g., accidents, liver disease, some cancers), while IHME focuses on deaths directly from alcohol use disorders (e.g., alcohol dependence, alcohol poisoning). See `alcohol_data_comparison.md` for detailed explanation of these differences.

1. Does Alcohol remain the most important indicator for Life Expectancy gap?
2. Does Alcohol remain the second most important indicator for HALE gap (after Neoplasms)?
3. Are the counterfactual effects similar in magnitude?
4. Do the model performance metrics (R², MAE) change significantly?

### Baseline Results (WHO Alcohol)

### Life Expectancy Gap Model

- **Cross-validation R²**: 0.851
- **Mean Absolute Error (MAE)**: 0.375 years
- **Non-zero coefficients**: 17 out of 25 predictors
- **Alcohol indicator importance**: 19.1 (ranked #1)
  - Mid component: 0 (entirely from gap component)
  - Gap component: 19.1
- **Top 3 indicators**:
  1. Alcohol (19.1)
  2. Neoplasms (12.1)
  3. Cardiovascular disease (10.4)

**Counterfactual Analysis (USA)**:
- Alcohol current gap: 38.8
- Alcohol target gap: 9.9 (Türkiye)
- Alcohol counterfactual effect: **-0.96 years** (largest single impact)
- Gap-closing total: -1.93 years
- Gap-widening total: +0.37 years
- **Net reduction: 1.56 years**

### HALE Gap Model

- **Cross-validation R²**: 0.730
- **Mean Absolute Error (MAE)**: 0.510 years
- **Non-zero coefficients**: 19 out of 25 predictors
- **Alcohol indicator importance**: 18.7 (ranked #2)
  - Mid component: 1.2
  - Gap component: 17.5
- **Top 3 indicators**:
  1. Neoplasms (30.8)
  2. Alcohol (18.7)
  3. Chronic Respiratory disease (7.0)

**Counterfactual Analysis (USA)**:
- Alcohol current gap: 38.8
- Alcohol target gap: 9.9 (Türkiye)
- Alcohol counterfactual effect: **-0.86 years** (largest single impact)
- Gap-closing total: -2.44 years
- Gap-widening total: +0.32 years
- **Net reduction: 2.12 years**

### New Results (IHME Alcohol)

### Life Expectancy Gap Model

- **Cross-validation R²**: 0.873 (↑ +0.022, +2.6% improvement)
- **Mean Absolute Error (MAE)**: 0.306 years (↓ -0.069, 18% improvement)
- **Non-zero coefficients**: Not explicitly shown, but model performance improved
- **Alcohol indicator importance**: 2.36 (ranked #4)
  - Mid component: 0.265
  - Gap component: 2.09
- **Top 3 indicators**:
  1. Neoplasms (16.3)
  2. UnintentionalInjury (5.95)
  3. ChronicRespiratory (2.81)
  4. **Alcohol (2.36)** ← dropped from #1 to #4

**Counterfactual Analysis (USA)**:
- Alcohol current gap: **5.54** (vs baseline 38.8 - massive difference!)
- Alcohol target gap: **0.306** (Colombia, vs baseline 9.9 in Türkiye)
- Alcohol counterfactual effect: **-0.37 years** (vs baseline -0.96 years, 61% reduction)
- Note: Counterfactual totals not calculated in new results

### HALE Gap Model

- **Cross-validation R²**: 0.776 (↑ +0.046, +6.3% improvement)
- **Mean Absolute Error (MAE)**: 0.456 years (↓ -0.054, 11% improvement)
- **Non-zero coefficients**: Not explicitly shown
- **Alcohol indicator importance**: 2.26 (ranked #5, tied with Suicide)
  - Mid component: 0.632
  - Gap component: 1.63
- **Top 3 indicators**:
  1. Neoplasms (28.6)
  2. Cardiovascular (10.9)
  3. UnintentionalInjury (6.27)
  4. ChronicRespiratory (5.08)
  5. **Alcohol (2.26, tied with Suicide)** ← dropped from #2 to #5

**Counterfactual Analysis (USA)**:
- Alcohol current gap: **5.54** (vs baseline 38.8 - massive difference!)
- Alcohol target gap: **0.306** (Colombia, vs baseline 9.9 in Türkiye)
- Alcohol counterfactual effect: **-0.358 years** (vs baseline -0.86 years, 58% reduction)
- Note: Suicide now has largest counterfactual effect (-0.899 years)

### Comparison and Conclusions

#### Major Differences Identified

#### 1. Alcohol Gap Values Are Dramatically Different

**Critical Finding**: The alcohol gap values are completely different between WHO and IHME data:
- **WHO**: USA alcohol gap = 38.8
- **IHME**: USA alcohol gap = 5.54

This represents an **86% reduction** in the measured gap. This is not a small difference—it's a fundamental difference in how alcohol-related mortality is measured.

**Possible Explanations**:
- **Definitional differences**: WHO "Alcohol-attributable all-cause deaths" includes all deaths where alcohol is a contributing factor (e.g., accidents, liver disease, some cancers), while IHME "Alcohol use disorders" may only include deaths directly from alcohol use disorders (e.g., alcohol dependence, alcohol poisoning).
- **Attribution methodology**: WHO may use population-attributable fraction (PAF) methods to estimate alcohol-attributable deaths, while IHME may use more restrictive diagnostic criteria.
- **Data sources**: Different underlying data sources and estimation methods between WHO and IHME.

#### 2. Alcohol Importance Dropped Substantially

**Life Expectancy**:
- Baseline: Alcohol ranked #1 with importance 19.1
- New: Alcohol ranked #4 with importance 2.36
- **Change**: -87.6% reduction in importance, dropped 3 ranks

**HALE**:
- Baseline: Alcohol ranked #2 with importance 18.7
- New: Alcohol ranked #5 (tied) with importance 2.26
- **Change**: -87.9% reduction in importance, dropped 3 ranks

This is a **major change** that exceeds the 10% threshold for significant differences defined in the validation criteria.

#### 3. Model Performance Improved

Both models show improved performance with IHME data:
- **Life Expectancy R²**: 0.851 → 0.873 (+2.6%)
- **Life Expectancy MAE**: 0.375 → 0.306 years (-18%)
- **HALE R²**: 0.730 → 0.776 (+6.3%)
- **HALE MAE**: 0.510 → 0.456 years (-11%)

This improvement may reflect:
- Better data quality in IHME estimates
- More consistent methodology across indicators
- Better temporal coverage allowing for more recent data

#### 4. Counterfactual Effects Reduced

**Life Expectancy**:
- Baseline: -0.96 years
- New: -0.37 years
- **Change**: -61% reduction

**HALE**:
- Baseline: -0.86 years
- New: -0.358 years
- **Change**: -58% reduction

The counterfactual effects are substantially smaller, reflecting the much smaller alcohol gaps in the IHME data.

#### 5. Ranking Changes

**Life Expectancy top indicators**:
- Baseline: Alcohol (#1), Neoplasms (#2), Cardiovascular (#3)
- New: Neoplasms (#1), UnintentionalInjury (#2), ChronicRespiratory (#3), Alcohol (#4)

**HALE top indicators**:
- Baseline: Neoplasms (#1), Alcohol (#2), ChronicRespiratory (#3)
- New: Neoplasms (#1), Cardiovascular (#2), UnintentionalInjury (#3), ChronicRespiratory (#4), Alcohol (#5)

Neoplasms remains the top indicator for HALE, but Alcohol has dropped out of the top 3 for both models.

#### Answers to Key Questions

1. **Does Alcohol remain the most important indicator for Life Expectancy gap?**
   - **NO** — Alcohol dropped from #1 to #4, with importance reduced by 87.6%

2. **Does Alcohol remain the second most important indicator for HALE gap?**
   - **NO** — Alcohol dropped from #2 to #5, with importance reduced by 87.9%

3. **Are the counterfactual effects similar in magnitude?**
   - **NO** — Counterfactual effects reduced by 58-61%, reflecting much smaller alcohol gaps in IHME data

4. **Do the model performance metrics (R², MAE) change significantly?**
   - **YES, but positively** — Both R² and MAE improved, suggesting better model fit with IHME data


#### Implications

The replacement of WHO alcohol data with IHME alcohol data has **substantial impacts** on model results:

1. **Alcohol is no longer the dominant factor** — The dramatic reduction in alcohol importance suggests that the WHO "alcohol-attributable all-cause deaths" definition captures a much broader set of alcohol-related mortality than IHME "alcohol use disorders."

2. **Other indicators gain importance** — With Alcohol's reduced importance, other indicators (Neoplasms, UnintentionalInjury, ChronicRespiratory) become relatively more important.

3. **Model performance improved** — Despite the change in Alcohol's role, overall model performance improved, suggesting the IHME data may be more consistent or higher quality.

4. **Counterfactual analysis implications** — The much smaller alcohol gaps in IHME data suggest that either:
   - The IHME definition is more restrictive (only direct alcohol use disorders)
   - The WHO definition is more comprehensive (includes all alcohol-attributable deaths)
   - There are methodological differences in how the two organizations estimate alcohol-related mortality

#### Recommendations

1. **Investigate definitional differences** — The 86% difference in alcohol gap values requires investigation into how WHO and IHME define and measure alcohol-related mortality.

2. **Consider using both definitions** — Depending on the research question, one definition may be more appropriate:
   - **WHO definition** (alcohol-attributable all-cause deaths): Better for understanding the full burden of alcohol on mortality
   - **IHME definition** (alcohol use disorders): Better for understanding direct alcohol-related health conditions

3. **Document the choice** — The choice between WHO and IHME alcohol data significantly affects model conclusions. This choice should be clearly documented and justified based on the research question.

4. **Update reporting** — If using IHME data, the conclusions in `hale_gaps.md` need to be updated to reflect that Alcohol is no longer the dominant factor, and other indicators (particularly Neoplasms and UnintentionalInjury) are relatively more important.

5. **Validate other indicators** — Before replacing other indicators (suicide, homicide, road traffic), validate that the definitional differences are understood and acceptable.

#### Next Steps

1. Compare WHO and IHME alcohol data definitions and methodologies
2. Check country coverage differences
3. Decide whether to use IHME or WHO alcohol data based on research objectives
4. If using IHME, update `hale_gaps.md` with new results
5. Proceed with caution when replacing other indicators

---

## Suicide: WHO → IHME

### Replacement Details

- **WHO Indicator**: `MH_12` - Age-standardized suicide rates (per 100,000 population)
- **WHO Temporal Coverage**: 2000-2021
- **IHME Indicator**: `B.7.3` - Self-harm, death rate per 100,000
- **IHME Temporal Coverage**: 1990-2023
- **Definitional Difference**: Both measure intentional self-harm (suicide), but IHME may use different methodology or data sources. The terminology "self-harm" vs "suicide" may reflect different classification systems, though they should capture the same underlying cause of death.

### Key Questions

1. Does Suicide maintain its relative importance ranking?
2. Are the counterfactual effects similar in magnitude?
3. Do the model performance metrics (R², MAE) change significantly?
4. Are definitional differences between WHO and IHME indicators understood?

### Baseline Results (WHO Suicide)

**Life Expectancy Gap Model:**
- **Suicide indicator importance**: 0.98 (mentioned as one of the smaller importance values, not in top 3)
- **Ranking**: Not in top 3 (top 3 were: Alcohol 19.1, Neoplasms 12.1, Cardiovascular 10.4)
- **Counterfactual Analysis (USA)**: -0.39 years (mentioned as part of gap-closing indicators)

**HALE Gap Model:**
- **Suicide indicator importance**: 2.0 (mentioned as one of the smaller importance values)
- **Ranking**: Not in top 3 (top 3 were: Neoplasms 30.8, Alcohol 18.7, Chronic Respiratory 7.0)
- **Counterfactual Analysis (USA)**: -0.79 years (largest single impact mentioned, reducing gap from 14.9 to 4.0 in Türkiye)

### New Results (IHME Self-Harm)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.876 (↑ +0.025 from baseline 0.851, +2.9% improvement)
- **Mean Absolute Error (MAE)**: 0.301 years (↓ -0.074 from baseline 0.375, 20% improvement)
- **Suicide indicator importance**: 2.34 (ranked #4)
  - Mid component: 0.134
  - Gap component: 2.21
- **Top 4 indicators**:
  1. Neoplasms (14.6)
  2. UnintentionalInjury (6.15)
  3. ChronicRespiratory (2.74)
  4. **Suicide (2.34)** ← increased from baseline 0.98 (+139% increase)

**Counterfactual Analysis (USA)**:
- Suicide current gap: **17.3** (vs baseline ~14.9, +16% increase)
- Suicide target gap: **4.51** (Türkiye, vs baseline 4.0, +13% increase)
- Suicide counterfactual effect: **-0.682 years** (vs baseline -0.39 years, +75% increase)

**HALE Gap Model:**
- **Cross-validation R²**: 0.777 (↑ +0.047 from baseline 0.730, +6.4% improvement)
- **Mean Absolute Error (MAE)**: 0.428 years (↓ -0.082 from baseline 0.510, 16% improvement)
- **Suicide indicator importance**: 2.84 (ranked #5)
  - Mid component: 1.0
  - Gap component: 1.84
- **Top 5 indicators**:
  1. Neoplasms (19.3)
  2. Cardiovascular (13.3)
  3. UnintentionalInjury (5.86)
  4. ChronicRespiratory (4.69)
  5. **Suicide (2.84)** ← increased from baseline 2.0 (+42% increase)

**Counterfactual Analysis (USA)**:
- Suicide current gap: **17.3** (vs baseline ~14.9, +16% increase)
- Suicide target gap: **4.51** (Türkiye, vs baseline 4.0, +13% increase)
- Suicide counterfactual effect: **-0.77 years** (vs baseline -0.79 years, -2.5% change, very similar)

### Comparison and Conclusions

#### Major Differences Identified

**1. Suicide Importance Increased**

**Life Expectancy**:
- Baseline: 0.98 (not in top 3)
- New: 2.34 (ranked #4)
- **Change**: +139% increase in importance, now in top 4

**HALE**:
- Baseline: 2.0
- New: 2.84 (ranked #5)
- **Change**: +42% increase in importance

This is a **significant increase** that exceeds the 10% threshold for significant differences, though the magnitude is smaller than the alcohol change.

**2. Suicide Gap Values Are Slightly Higher**

- **Baseline**: USA suicide gap ~14.9
- **New**: USA suicide gap 17.3
- **Change**: +16% increase

This is a moderate difference, much smaller than the alcohol gap difference (86%). The target gap also increased slightly (4.0 → 4.51, +13%).

**3. Model Performance Improved**

Both models show improved performance with IHME data:
- **Life Expectancy R²**: 0.851 → 0.876 (+2.9%)
- **Life Expectancy MAE**: 0.375 → 0.301 years (-20%)
- **HALE R²**: 0.730 → 0.777 (+6.4%)
- **HALE MAE**: 0.510 → 0.428 years (-16%)

**4. Counterfactual Effects**

**Life Expectancy**:
- Baseline: -0.39 years
- New: -0.682 years
- **Change**: +75% increase (larger effect)

**HALE**:
- Baseline: -0.79 years
- New: -0.77 years
- **Change**: -2.5% (very similar, essentially unchanged)

The Life Expectancy counterfactual effect increased substantially, while the HALE effect remained very similar.

#### Answers to Key Questions

1. **Does Suicide maintain its relative importance ranking?**
   - **PARTIALLY** — Suicide importance increased significantly (+139% for LE, +42% for HALE), moving it into the top 4-5 indicators. It was not in the top 3 in the baseline, and remains outside the top 3 in the new results, but its relative importance has increased.

2. **Are the counterfactual effects similar in magnitude?**
   - **MIXED** — For Life Expectancy, the counterfactual effect increased by 75% (-0.39 → -0.682 years). For HALE, the effect remained very similar (-0.79 → -0.77 years, -2.5% change).

3. **Do the model performance metrics (R², MAE) change significantly?**
   - **YES, but positively** — Both R² and MAE improved for both models, suggesting better model fit with IHME data.


5. **Are definitional differences between WHO and IHME indicators understood?**
   - **PARTIALLY** — Both measure intentional self-harm/suicide, but the 16% difference in gap values suggests there may be methodological differences in how the data is collected or estimated.

#### Implications

The replacement of WHO suicide data with IHME self-harm data has **moderate impacts** on model results:

1. **Suicide importance increased** — The increase in importance (+139% for LE, +42% for HALE) suggests that IHME data may capture suicide-related mortality more effectively or consistently than WHO data, or that the slightly higher gap values in IHME data make suicide a more predictive factor.

2. **Counterfactual effects vary by outcome** — The Life Expectancy counterfactual effect increased substantially (+75%), while the HALE effect remained nearly identical. This suggests that suicide may have a stronger relationship with overall life expectancy than with healthy life expectancy when using IHME data.

3. **Model performance improved** — Overall model performance improved, suggesting the IHME data may be more consistent or higher quality.

4. **Gap values are similar but not identical** — The 16% difference in suicide gap values is moderate compared to the 86% difference seen with alcohol, suggesting that WHO and IHME definitions of suicide/self-harm are more similar than their definitions of alcohol-related mortality.

#### Recommendations

1. **Investigate the 16% difference** — While smaller than the alcohol difference, the 16% difference in suicide gap values should be understood. This may reflect:
   - Different data sources or estimation methods
   - Different classification systems for intentional self-harm
   - Temporal differences (IHME may use more recent data)

2. **Consider the increased importance** — The substantial increase in suicide importance suggests that IHME data may be more predictive. This could be due to better data quality, more consistent methodology, or the slightly higher gap values making suicide a stronger predictor.

3. **Document the choice** — The choice between WHO and IHME suicide data affects model conclusions, though less dramatically than the alcohol choice. Document the rationale for using IHME data (better temporal coverage, consistent methodology with other IHME indicators).

4. **Proceed with other replacements** — The suicide replacement shows moderate but acceptable changes. The improvements in model performance and the reasonable similarity in gap values suggest that IHME data is a good alternative to WHO data for suicide/self-harm.

---

## Homicide: WHO → IHME

### Replacement Details

- **WHO Indicator**: `VIOLENCE_HOMICIDERATE` - Estimates of rates of homicides per 100,000 population
- **WHO Temporal Coverage**: 2000-2021
- **IHME Indicator**: `B.7.4` - Interpersonal violence, death rate per 100,000
- **IHME Temporal Coverage**: 1990-2023
- **Definitional Difference**: Both measure intentional homicide/interpersonal violence, but IHME may use different methodology or data sources. The terminology "interpersonal violence" vs "homicide" may reflect different classification systems, though they should capture the same underlying cause of death.

### Key Questions

1. Does Homicide maintain its relative importance ranking?
2. Are the counterfactual effects similar in magnitude?
3. Do the model performance metrics (R², MAE) change significantly?
4. Are definitional differences between WHO and IHME indicators understood?

### Baseline Results (WHO Homicide)

**Life Expectancy Gap Model:**
- **Homicide indicator importance**: Not explicitly stated, but mentioned as one of the smaller importance values (not in top 3)
- **Ranking**: Not in top 3 (top 3 were: Alcohol 19.1, Neoplasms 12.1, Cardiovascular 10.4)
- **Counterfactual Analysis (USA)**: Not explicitly stated for Life Expectancy

**HALE Gap Model:**
- **Homicide indicator importance**: 2.2 (mentioned as one of the smaller importance values)
- **Ranking**: Not in top 3 (top 3 were: Neoplasms 30.8, Alcohol 18.7, Chronic Respiratory 7.0)
- **Counterfactual Analysis (USA)**: -0.10 years (mentioned as part of gap-closing indicators)

### New Results (IHME Interpersonal Violence)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.876 (same as with suicide replacement, ↑ +0.025 from baseline 0.851, +2.9% improvement)
- **Mean Absolute Error (MAE)**: 0.301 years (same as with suicide replacement, ↓ -0.074 from baseline 0.375, 20% improvement)
- **Homicide indicator importance**: **0** (not selected by Elastic Net, ranked last)
  - Mid component: 0
  - Gap component: 0
- **Top indicators** (same as with suicide replacement):
  1. Neoplasms (14.6)
  2. UnintentionalInjury (6.15)
  3. ChronicRespiratory (2.74)
  4. Suicide (2.34)
  5. Alcohol (2.33)

**Counterfactual Analysis (USA)**:
- Homicide current gap: **7.15**
- Homicide target gap: **0**
- Homicide counterfactual effect: **0** (no effect, indicator not selected by model)

**HALE Gap Model:**
- **Cross-validation R²**: 0.777 (same as with suicide replacement, ↑ +0.047 from baseline 0.730, +6.4% improvement)
- **Mean Absolute Error (MAE)**: 0.428 years (same as with suicide replacement, ↓ -0.082 from baseline 0.510, 16% improvement)
- **Homicide indicator importance**: 1.58 (ranked #8)
  - Mid component: 0.536
  - Gap component: 1.04
- **Top indicators** (same as with suicide replacement):
  1. Neoplasms (19.3)
  2. Cardiovascular (13.3)
  3. UnintentionalInjury (5.86)
  4. ChronicRespiratory (4.69)
  5. Suicide (2.84)
  6. Alcohol (2.1)
  7. MaternalMortality (1.63)
  8. **Homicide (1.58)** ← decreased from baseline 2.2 (-28% decrease)

**Counterfactual Analysis (USA)**:
- Homicide current gap: **7.15**
- Homicide target gap: **0**
- Homicide counterfactual effect: **-0.0758 years** (vs baseline -0.10 years, -24% decrease)

### Comparison and Conclusions

#### Major Differences Identified

**1. Homicide Dropped Out of Life Expectancy Model**

**Critical Finding**: Homicide was **not selected by Elastic Net** for the Life Expectancy model when using IHME data. This means the model determined that homicide does not contribute significantly to explaining the Life Expectancy gap when using IHME data.

**Possible Explanations**:
- IHME interpersonal violence data may have different values or distributions that make it less predictive
- The model may have found that other indicators (particularly Suicide, which increased in importance) capture the same variance
- IHME data may have different country coverage, affecting which countries are included in the analysis
- The Elastic Net regularization may have selected other indicators that are more predictive

**2. Homicide Importance Decreased for HALE**

**HALE**:
- Baseline: 2.2
- New: 1.58 (ranked #8)
- **Change**: -28% decrease in importance

This is a **significant decrease** that exceeds the 10% threshold for significant differences.

**3. Model Performance Unchanged**

Both models show the same performance as with the suicide replacement:
- **Life Expectancy R²**: 0.876 (same as suicide replacement)
- **Life Expectancy MAE**: 0.301 years (same as suicide replacement)
- **HALE R²**: 0.777 (same as suicide replacement)
- **HALE MAE**: 0.428 years (same as suicide replacement)

This suggests that the homicide replacement did not affect overall model performance, likely because homicide was not a major contributor to model fit.

**4. Counterfactual Effects**

**Life Expectancy**:
- Baseline: Not explicitly stated
- New: 0 (indicator not selected)
- **Change**: N/A (indicator not selected)

**HALE**:
- Baseline: -0.10 years
- New: -0.0758 years
- **Change**: -24% decrease

The HALE counterfactual effect decreased, reflecting the lower importance of homicide in the model.

#### Answers to Key Questions

1. **Does Homicide maintain its relative importance ranking?**
   - **NO** — Homicide dropped out of the Life Expectancy model entirely (not selected by Elastic Net), and decreased in importance for HALE (-28%, from 2.2 to 1.58).

2. **Are the counterfactual effects similar in magnitude?**
   - **NO** — For Life Expectancy, the counterfactual effect is 0 (indicator not selected). For HALE, the effect decreased by 24% (-0.10 → -0.0758 years).

3. **Do the model performance metrics (R², MAE) change significantly?**
   - **NO** — Model performance remained the same as with the suicide replacement, suggesting homicide was not a major contributor to model fit.


5. **Are definitional differences between WHO and IHME indicators understood?**
   - **PARTIALLY** — Both measure intentional homicide/interpersonal violence, but the fact that IHME homicide was not selected for the Life Expectancy model suggests there may be meaningful differences in how the data is collected, estimated, or distributed.

#### Implications

The replacement of WHO homicide data with IHME interpersonal violence data has **significant impacts** on model results:

1. **Homicide is no longer a factor in Life Expectancy model** — The fact that Elastic Net did not select homicide for the Life Expectancy model suggests that either:
   - IHME homicide data is less predictive than WHO data
   - Other indicators (particularly Suicide) capture the same variance
   - The data distributions or country coverage differ in ways that reduce homicide's predictive power

2. **Homicide importance decreased for HALE** — The 28% decrease in importance for HALE suggests that IHME homicide data is less predictive than WHO data, though it remains a selected indicator.

3. **Model performance unaffected** — The fact that model performance did not change suggests that homicide was not a critical factor for model fit, and other indicators (particularly Suicide, which increased in importance) may capture similar variance.

4. **Gap values are similar** — The homicide gap value (7.15) appears in the counterfactual analysis, suggesting the values are reasonable, but the model determined they are not predictive enough to include.

#### Recommendations

1. **Investigate why homicide was not selected** — The fact that homicide was not selected for the Life Expectancy model requires investigation:
   - Compare WHO and IHME homicide gap values and distributions
   - Check for multicollinearity with other indicators (particularly Suicide)
   - Verify country coverage differences
   - Examine whether IHME data quality or methodology differs significantly

2. **Consider the relationship with Suicide** — The increase in Suicide importance (+139% for LE, +42% for HALE) may have come at the expense of Homicide. These indicators may be capturing similar variance, and Elastic Net selected Suicide as the more predictive indicator.

3. **Document the choice** — The choice between WHO and IHME homicide data affects model conclusions, particularly for Life Expectancy where homicide is no longer a factor. Document the rationale for using IHME data and note that homicide is not selected for the Life Expectancy model.

4. **Proceed with caution** — The fact that homicide was not selected for the Life Expectancy model suggests that IHME homicide data may be less suitable than WHO data, or that the model structure has changed in ways that make homicide less relevant. Consider whether to use WHO homicide data for Life Expectancy if homicide is an important factor for the research question.

---

## Road Traffic: WHO → IHME

### Replacement Details

- **WHO Indicator**: `SA_0000001459` - Road traffic crash deaths, age-standardized death rates (15+), per 100,000 population
- **WHO Temporal Coverage**: 2019 only
- **IHME Indicator**: Road injuries, death rate per 100,000
- **IHME Temporal Coverage**: 1990-2023
- **Definitional Difference**: Both measure road traffic crash/injury deaths, but IHME may use different methodology or data sources. WHO data is age-standardized for ages 15+, while IHME data covers all ages. The terminology "road injuries" vs "road traffic crashes" may reflect different classification systems, though they should capture the same underlying cause of death.

### Key Questions

1. Does RoadTraffic maintain its relative importance ranking?
2. Are the counterfactual effects similar in magnitude?
3. Do the model performance metrics (R², MAE) change significantly?
4. Are definitional differences between WHO and IHME indicators understood?

### Baseline Results (WHO Road Traffic)

**Life Expectancy Gap Model:**
- **RoadTraffic indicator importance**: Not explicitly stated in baseline results
- **Ranking**: Not in top 3 (top 3 were: Alcohol 19.1, Neoplasms 12.1, Cardiovascular 10.4)
- **Counterfactual Analysis (USA)**: Not explicitly stated for Life Expectancy

**HALE Gap Model:**
- **RoadTraffic indicator importance**: Not explicitly stated, but mentioned as having a counterfactual effect
- **Ranking**: Not in top 3 (top 3 were: Neoplasms 30.8, Alcohol 18.7, Chronic Respiratory 7.0)
- **Counterfactual Analysis (USA)**: -0.20 years (mentioned as part of gap-closing indicators)

### New Results (IHME Road Injuries)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.87 (↓ -0.006 from homicide replacement 0.876, but ↑ +0.019 from baseline 0.851, +2.2% improvement)
- **Mean Absolute Error (MAE)**: 0.309 years (↑ +0.008 from homicide replacement 0.301, but ↓ -0.066 from baseline 0.375, 18% improvement)
- **RoadTraffic indicator importance**: 0.111 (ranked #8, very low)
  - Mid component: 0.111
  - Gap component: 0 (not selected)
- **Top indicators**:
  1. Neoplasms (14.3)
  2. UnintentionalInjury (6.12)
  3. ChronicRespiratory (2.72)
  4. Alcohol (2.33)
  5. Suicide (2.27)

**Counterfactual Analysis (USA)**:
- RoadTraffic current gap: **11.2**
- RoadTraffic target gap: **2.04** (Iceland)
- RoadTraffic counterfactual effect: **-0.0391 years** (very small effect)

**HALE Gap Model:**
- **Cross-validation R²**: 0.809 (↑ +0.032 from homicide replacement 0.777, ↑ +0.079 from baseline 0.730, +10.8% improvement)
- **Mean Absolute Error (MAE)**: 0.423 years (same as homicide replacement, ↓ -0.087 from baseline 0.510, 17% improvement)
- **RoadTraffic indicator importance**: 0.633 (ranked #9)
  - Mid component: 0.568
  - Gap component: 0.0648
- **Top indicators**:
  1. Neoplasms (19.6)
  2. Cardiovascular (13.5)
  3. UnintentionalInjury (5.73)
  4. ChronicRespiratory (4.49)
  5. Suicide (2.81)
  6. Alcohol (2.06)
  7. Homicide (1.73)
  8. MaternalMortality (1.35)
  9. **RoadTraffic (0.633)** ← very low importance

**Counterfactual Analysis (USA)**:
- RoadTraffic current gap: **11.2**
- RoadTraffic target gap: **2.04** (Iceland)
- RoadTraffic counterfactual effect: **-0.226 years** (vs baseline -0.20 years, +13% increase)

### Comparison and Conclusions

#### Major Differences Identified

**1. RoadTraffic Has Very Low Importance**

**Life Expectancy**:
- New: 0.111 (ranked #8, very low)
- **Note**: Only Mid component selected (0.111), Gap component not selected (0)

**HALE**:
- New: 0.633 (ranked #9, very low)
- Both Mid (0.568) and Gap (0.0648) components selected, but total importance is very low

RoadTraffic has very low importance in both models, suggesting it is not a major predictive factor for either Life Expectancy or HALE gaps.

**2. Model Performance**

**Life Expectancy**:
- R²: 0.851 → 0.87 (+2.2% improvement from baseline)
- MAE: 0.375 → 0.309 years (-18% improvement from baseline)
- **Note**: Slightly decreased from homicide replacement (0.876 → 0.87), but still improved from baseline

**HALE**:
- R²: 0.730 → 0.809 (+10.8% improvement from baseline)
- MAE: 0.510 → 0.423 years (-17% improvement from baseline)
- **Note**: Improved from homicide replacement (0.777 → 0.809)

The HALE model performance improved substantially with the road traffic replacement, while Life Expectancy performance remained similar to previous replacements.

**3. Counterfactual Effects**

**Life Expectancy**:
- New: -0.0391 years (very small effect)
- **Note**: Baseline not explicitly stated, but the effect is very small

**HALE**:
- Baseline: -0.20 years
- New: -0.226 years
- **Change**: +13% increase (slightly larger effect)

The HALE counterfactual effect increased slightly, while the Life Expectancy effect is very small.

**4. Gap Component Not Selected for Life Expectancy**

**Critical Finding**: For the Life Expectancy model, only the Mid component of RoadTraffic was selected (0.111), while the Gap component was not selected (0). This suggests that:
- The average road traffic death rate (Mid) has some predictive power
- The gender gap in road traffic deaths (Gap) does not contribute to explaining the Life Expectancy gap when using IHME data
- This differs from HALE, where both components are selected (though with low importance)

#### Answers to Key Questions

1. **Does RoadTraffic maintain its relative importance ranking?**
   - **YES, but with very low importance** — RoadTraffic has very low importance in both models (0.111 for LE, 0.633 for HALE), ranking #8-9. It was not in the top 3 in the baseline, and remains outside the top 3 in the new results.

2. **Are the counterfactual effects similar in magnitude?**
   - **MIXED** — For Life Expectancy, the counterfactual effect is very small (-0.0391 years). For HALE, the effect is similar to baseline (-0.20 → -0.226 years, +13% increase).

3. **Do the model performance metrics (R², MAE) change significantly?**
   - **YES, but positively** — Both R² and MAE improved for both models compared to baseline. HALE R² improved substantially (+10.8%), while Life Expectancy R² improved modestly (+2.2%).


5. **Are definitional differences between WHO and IHME indicators understood?**
   - **PARTIALLY** — Both measure road traffic crash/injury deaths, but WHO data is age-standardized for ages 15+ while IHME covers all ages. The very low importance suggests that road traffic may not be a major factor in explaining gender gaps, or that the age standardization difference affects the predictive power.

#### Implications

The replacement of WHO road traffic data with IHME road injuries data has **minimal impacts** on model results:

1. **RoadTraffic has very low importance** — The very low importance values (0.111 for LE, 0.633 for HALE) suggest that road traffic deaths are not a major predictive factor for gender gaps in Life Expectancy or HALE, at least when using IHME data.

2. **Gap component not selected for Life Expectancy** — The fact that only the Mid component was selected for Life Expectancy suggests that the gender gap in road traffic deaths does not contribute to explaining the Life Expectancy gap when using IHME data. This may reflect:
   - The age standardization difference (WHO: 15+, IHME: all ages)
   - Different data distributions or country coverage
   - The gender gap in road traffic deaths may be less predictive than the average rate

3. **Model performance improved** — Overall model performance improved, particularly for HALE (+10.8% R² improvement). This suggests that IHME data may be more consistent or higher quality, even though RoadTraffic itself has low importance.

4. **Counterfactual effects are small** — The counterfactual effects are small for both models, reflecting the low importance of RoadTraffic. The HALE effect is slightly larger than baseline (+13%), but still relatively small.

#### Recommendations

1. **Accept the low importance** — The very low importance of RoadTraffic suggests it is not a major factor in explaining gender gaps. This is acceptable and may reflect that road traffic deaths, while important for overall mortality, do not contribute significantly to gender gaps in Life Expectancy or HALE.

2. **Consider age standardization** — The fact that WHO data is age-standardized for ages 15+ while IHME covers all ages may affect the predictive power. However, given the very low importance, this difference is unlikely to be critical.

3. **Document the choice** — The choice between WHO and IHME road traffic data has minimal impact on model conclusions due to the low importance of RoadTraffic. Document the rationale for using IHME data (better temporal coverage, consistent methodology with other IHME indicators).

4. **Proceed with confidence** — The road traffic replacement shows minimal changes and improved model performance. The IHME data appears to be a good alternative to WHO data for road traffic, though RoadTraffic itself is not a major factor in the models.

---

## Removing WHO Poisoning: Keeping Only IHME DrugDisorder

### Replacement Details

- **Removed Indicator**: WHO `SDGPOISON` - Mortality rate attributed to unintentional poisoning (per 100,000 population)
- **WHO Temporal Coverage**: 2000-2021
- **Kept Indicator**: IHME Drug Use Disorders - Drug use disorder death rates (per 100,000 population)
- **IHME Temporal Coverage**: 1990-2023
- **Rationale**: Both indicators were in the baseline model, but DrugDisorder provides better temporal coverage and captures drug overdose deaths more comprehensively. This experiment tests the effect of removing Poisoning while keeping DrugDisorder.

### Key Questions

1. Does removing Poisoning affect model performance?
2. Does DrugDisorder maintain its importance (or gain importance)?
3. Are there any changes in other indicators' importance?

### Baseline Results (Both Poisoning and DrugDisorder)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.87
- **Mean Absolute Error (MAE)**: 0.309 years
- **Poisoning indicator importance**: 0 (not selected by Elastic Net)
- **DrugDisorder indicator importance**: 0 (not selected by Elastic Net)

**HALE Gap Model:**
- **Cross-validation R²**: 0.809
- **Mean Absolute Error (MAE)**: 0.423 years
- **Poisoning indicator importance**: 0 (not selected by Elastic Net)
- **DrugDisorder indicator importance**: 0 (not selected by Elastic Net)

### New Results (Only DrugDisorder, No Poisoning)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.87 (no change)
- **Mean Absolute Error (MAE)**: 0.309 years (no change)
- **DrugDisorder indicator importance**: **0** (still not selected by Elastic Net)
- **Poisoning**: Removed from model

**HALE Gap Model:**
- **Cross-validation R²**: 0.809 (no change)
- **Mean Absolute Error (MAE)**: 0.423 years (no change)
- **DrugDisorder indicator importance**: **0** (still not selected by Elastic Net)
- **Poisoning**: Removed from model

### Comparison and Conclusions

#### Major Findings

**1. No Impact on Model Performance**

Both models show **identical performance** before and after removing Poisoning:
- **Life Expectancy R²**: 0.87 → 0.87 (no change)
- **Life Expectancy MAE**: 0.309 → 0.309 years (no change)
- **HALE R²**: 0.809 → 0.809 (no change)
- **HALE MAE**: 0.423 → 0.423 years (no change)

**2. Neither Indicator Was Selected**

**Critical Finding**: Both Poisoning and DrugDisorder had **importance = 0** in the baseline model, meaning Elastic Net did not select either indicator. After removing Poisoning, DrugDisorder still has **importance = 0**, meaning it is still not selected.

This indicates that:
- Neither indicator contributes significantly to explaining the gender gaps in Life Expectancy or HALE
- Removing Poisoning has no effect because it wasn't contributing to the model
- DrugDisorder does not gain importance after Poisoning is removed, suggesting they don't capture the same variance

**3. Counterfactual Effects**

**Life Expectancy**:
- DrugDisorder counterfactual: 0 (indicator not selected)
- Poisoning counterfactual: 0 (removed, was also 0 in baseline)

**HALE**:
- DrugDisorder counterfactual: 0 (indicator not selected)
- Poisoning counterfactual: 0 (removed, was also 0 in baseline)

#### Answers to Key Questions

1. **Does removing Poisoning affect model performance?**
   - **NO** — Model performance is identical (R² and MAE unchanged). This is expected since Poisoning was not selected by Elastic Net in the baseline.

2. **Does DrugDisorder maintain its importance (or gain importance)?**
   - **NO CHANGE** — DrugDisorder still has importance = 0 (not selected). It does not gain importance after Poisoning is removed, suggesting they don't capture overlapping variance.

3. **Are there any changes in other indicators' importance?**
   - **NO** — All other indicators maintain the same importance values as in the baseline (with Road Traffic replacement).

#### Implications

The removal of WHO Poisoning has **no impact** on model results:

1. **Poisoning was not contributing** — The fact that Poisoning had importance = 0 in the baseline means it was not selected by Elastic Net and was not contributing to model fit. Removing it has no effect.

2. **DrugDisorder also not contributing** — DrugDisorder also has importance = 0, meaning it is not selected by Elastic Net either. This suggests that drug-related mortality (whether captured by Poisoning or DrugDisorder) does not contribute significantly to explaining gender gaps in Life Expectancy or HALE.

3. **No redundancy** — The fact that DrugDisorder does not gain importance after Poisoning is removed suggests they don't capture the same variance. However, since neither is selected, this is not a critical finding.

4. **Model is robust** — The model performance is unchanged, confirming that neither indicator was important for model fit.

#### Recommendations

1. **Accept the removal** — Removing Poisoning has no negative impact since it wasn't contributing to the model. The model now uses only DrugDisorder (IHME), which provides better temporal coverage.

2. **Note that DrugDisorder is also not selected** — While DrugDisorder remains in the model, it is not selected by Elastic Net (importance = 0). This suggests that drug-related mortality may not be a major factor in explaining gender gaps, at least with the current data and model structure.

3. **Document the choice** — The removal of Poisoning is justified by:
   - Better temporal coverage in DrugDisorder (1990-2023 vs 2000-2021)
   - More comprehensive capture of drug overdose deaths
   - No impact on model performance (since Poisoning wasn't selected)

4. **Consider future analysis** — If drug-related mortality becomes more important in future analyses or with different model specifications, both indicators could be re-evaluated. However, for the current analysis, neither contributes significantly.

---

## Adding Liver Disease Indicator (IHME)

### Addition Details

- **New Indicator**: IHME `B.7.2` - Cirrhosis and other chronic liver diseases, death rate per 100,000
- **IHME Temporal Coverage**: 1990-2023
- **Rationale**: Liver disease is a significant cause of death that may contribute to gender gaps. Men typically have higher rates of liver disease mortality than women, often due to higher alcohol consumption, hepatitis infections, and other risk factors. This indicator provides comprehensive liver disease death rates with excellent temporal coverage and good country coverage. Liver disease is often related to alcohol consumption, but also includes non-alcoholic causes such as viral hepatitis, non-alcoholic fatty liver disease, and other chronic liver conditions.

### Key Questions

1. Does adding Liver Disease improve model performance?
2. What is the importance of Liver Disease relative to other indicators?
3. Are the counterfactual effects meaningful?
4. How does Liver Disease relate to Alcohol (since many liver disease deaths are alcohol-related)?

### Baseline Results (Before Adding Liver Disease)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.87
- **Mean Absolute Error (MAE)**: 0.309 years
- **Top indicators**:
  1. Neoplasms (14.3)
  2. UnintentionalInjury (6.12)
  3. ChronicRespiratory (2.72)
  4. Alcohol (2.33)
  5. Suicide (2.27)

**HALE Gap Model:**
- **Cross-validation R²**: 0.809
- **Mean Absolute Error (MAE)**: 0.423 years
- **Top indicators**:
  1. Neoplasms (19.6)
  2. Cardiovascular (13.5)
  3. UnintentionalInjury (5.73)
  4. ChronicRespiratory (4.49)
  5. Suicide (2.81)
  6. Alcohol (2.06)

### New Results (With Liver Disease Added)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.877 (↑ +0.007 from baseline 0.87, +0.8% improvement)
- **Mean Absolute Error (MAE)**: 0.318 years (↑ +0.009 from baseline 0.309, +2.9% increase)
- **LiverDiseaseDeathRate indicator importance**: 2.12 (ranked #4)
  - Mid component: 0.295
  - Gap component: 1.82
- **Top indicators**:
  1. Neoplasms (12.0)
  2. UnintentionalInjury (4.96)
  3. ChronicRespiratory (2.57)
  4. **LiverDiseaseDeathRate (2.12)** ← newly added
  5. MaternalMortality (1.89)
  6. Suicide (1.82)
  7. Alcohol (1.62)

**Counterfactual Analysis (USA)**:
- LiverDiseaseDeathRate current gap: **9.05**
- LiverDiseaseDeathRate target gap: **1.29** (Iceland)
- LiverDiseaseDeathRate counterfactual effect: **-0.213 years**

**HALE Gap Model:**
- **Cross-validation R²**: 0.761 (Elastic Net) (↓ -0.048 from baseline 0.809, -5.9% decrease)
- **Mean Absolute Error (MAE)**: 0.402 years (↓ -0.021 from baseline 0.423, -5.0% improvement)
- **LiverDiseaseDeathRate indicator importance**: 2.39 (ranked #6)
  - Mid component: 1.1
  - Gap component: 1.29
- **Top indicators**:
  1. Neoplasms (23.8)
  2. UnintentionalInjury (5.59)
  3. ChronicRespiratory (4.89)
  4. Cardiovascular (3.48)
  5. Suicide (2.78)
  6. **LiverDiseaseDeathRate (2.39)** ← newly added
  7. MaternalMortality (2.15)
  8. Homicide (1.9)
  9. Alcohol (1.8)

**Counterfactual Analysis (USA)**:
- LiverDiseaseDeathRate current gap: **9.05**
- LiverDiseaseDeathRate target gap: **1.29** (Iceland)
- LiverDiseaseDeathRate counterfactual effect: **-0.2 years**

### Comparison and Conclusions

#### Major Findings

**1. Liver Disease Has Moderate Importance**

**Life Expectancy**:
- New: 2.12 (ranked #4)
- Both Mid (0.295) and Gap (1.82) components selected
- Importance is moderate, ranking just below ChronicRespiratory (2.57) and above MaternalMortality (1.89)

**HALE**:
- New: 2.39 (ranked #6)
- Both Mid (1.1) and Gap (1.29) components selected
- Importance is moderate, ranking between Suicide (2.78) and MaternalMortality (2.15)

Liver Disease has moderate importance in both models, suggesting it contributes meaningfully to explaining gender gaps in Life Expectancy and HALE.

**2. Model Performance Changes**

**Life Expectancy**:
- R²: 0.87 → 0.877 (+0.8% improvement)
- MAE: 0.309 → 0.318 years (+2.9% increase, slight degradation)
- **Note**: R² improved slightly, but MAE increased slightly. The improvement in R² suggests better model fit, while the slight increase in MAE may reflect increased model complexity.

**HALE**:
- R²: 0.809 → 0.761 (Elastic Net) (-5.9% decrease)
- MAE: 0.423 → 0.402 years (-5.0% improvement)
- **Note**: R² decreased, but MAE improved. The decrease in R² may reflect that Elastic Net selected a different model configuration, while the improvement in MAE suggests better prediction accuracy.

**3. Counterfactual Effects Are Meaningful**

**Life Expectancy**:
- Counterfactual effect: **-0.213 years** (moderate effect)
- USA gap: 9.05 → target: 1.29 (Iceland)
- This represents a meaningful reduction in the gender gap

**HALE**:
- Counterfactual effect: **-0.2 years** (moderate effect)
- USA gap: 9.05 → target: 1.29 (Iceland)
- Similar magnitude to Life Expectancy, suggesting consistent impact

**4. Relationship to Alcohol**

**Key Observation**: Liver Disease (importance 2.12 for LE, 2.39 for HALE) has **higher importance than Alcohol** (importance 1.62 for LE, 1.8 for HALE) in both models. This is interesting because:

- Many liver disease deaths are alcohol-related
- However, Liver Disease captures **all** liver disease deaths (alcoholic and non-alcoholic), while Alcohol (IHME) only captures direct alcohol use disorder deaths
- This suggests that Liver Disease may be capturing some of the alcohol-related mortality that was previously captured by WHO's broader "alcohol-attributable" definition

**5. Impact on Other Indicators**

**Life Expectancy**:
- Neoplasms: 14.3 → 12.0 (decreased, but still #1)
- UnintentionalInjury: 6.12 → 4.96 (decreased, but still #2)
- ChronicRespiratory: 2.72 → 2.57 (slightly decreased, still #3)
- Alcohol: 2.33 → 1.62 (decreased from #4 to #7)

**HALE**:
- Neoplasms: 19.6 → 23.8 (increased, still #1)
- Cardiovascular: 13.5 → 3.48 (decreased significantly, from #2 to #4)
- UnintentionalInjury: 5.73 → 5.59 (slightly decreased, still #2)
- ChronicRespiratory: 4.49 → 4.89 (slightly increased, still #3)
- Alcohol: 2.06 → 1.8 (slightly decreased, from #6 to #9)

The addition of Liver Disease appears to have redistributed some importance, particularly affecting Alcohol and Cardiovascular indicators.

#### Answers to Key Questions

1. **Does adding Liver Disease improve model performance?**
   - **MIXED** — Life Expectancy R² improved slightly (+0.8%), but MAE increased slightly (+2.9%). HALE R² decreased (-5.9%), but MAE improved (-5.0%). The changes are relatively small, suggesting that Liver Disease adds some predictive power but doesn't dramatically change model performance.

2. **What is the importance of Liver Disease relative to other indicators?**
   - **MODERATE** — Liver Disease ranks #4 for Life Expectancy (importance 2.12) and #6 for HALE (importance 2.39). It has moderate importance, ranking above Alcohol in both models.

3. **Are the counterfactual effects meaningful?**
   - **YES** — Counterfactual effects are moderate (-0.213 years for LE, -0.2 years for HALE), suggesting that reducing liver disease gender gaps could meaningfully reduce overall gender gaps.

4. **How does Liver Disease relate to Alcohol?**
   - **COMPLEX** — Liver Disease has higher importance than Alcohol in both models, which is interesting because many liver disease deaths are alcohol-related. However, Liver Disease captures all liver disease deaths (alcoholic and non-alcoholic), while Alcohol (IHME) only captures direct alcohol use disorder deaths. This suggests that Liver Disease may be capturing some of the alcohol-related mortality that was previously captured by WHO's broader "alcohol-attributable" definition.

#### Implications

The addition of Liver Disease as an indicator has **moderate impacts** on model results:

1. **Liver Disease has moderate importance** — The moderate importance values (2.12 for LE, 2.39 for HALE) suggest that liver disease contributes meaningfully to explaining gender gaps in Life Expectancy and HALE.

2. **Model performance changes are small** — The changes in R² and MAE are relatively small, suggesting that Liver Disease adds some predictive power but doesn't dramatically change model performance.

3. **Counterfactual effects are meaningful** — The counterfactual effects (-0.213 years for LE, -0.2 years for HALE) suggest that reducing liver disease gender gaps could meaningfully reduce overall gender gaps.

4. **Relationship to Alcohol is complex** — Liver Disease has higher importance than Alcohol in both models, which may reflect that Liver Disease captures a broader set of alcohol-related mortality than the narrow IHME "alcohol use disorders" definition.

5. **Some redistribution of importance** — The addition of Liver Disease appears to have redistributed some importance, particularly affecting Alcohol and Cardiovascular indicators.

#### Recommendations

1. **Keep Liver Disease in the model** — The moderate importance and meaningful counterfactual effects suggest that Liver Disease should be included in the model.

2. **Consider the relationship to Alcohol** — The fact that Liver Disease has higher importance than Alcohol suggests that it may be capturing some of the alcohol-related mortality that was previously captured by WHO's broader "alcohol-attributable" definition. This is consistent with the understanding that many liver disease deaths are alcohol-related.

3. **Document the choice** — The addition of Liver Disease adds a meaningful indicator that captures an important cause of death with good temporal coverage and country coverage. Document the rationale for including it.

4. **Monitor model performance** — The small changes in model performance suggest that Liver Disease adds value without dramatically changing the model. Continue to monitor model performance as other indicators are added or modified.

---

## Removing Maternal Mortality Indicator

### Removal Details

- **Removed Indicator**: WHO `MDG_0000000026` - Maternal mortality ratio (per 100,000 live births)
- **Rationale**: Maternal mortality has a moderate positive coefficient in most models, which implies that higher maternal mortality is associated with a larger LE/HALE gap. This is **counterintuitive** because if something increases female mortality, it should **close** the gap (since gap = Female - Male). The positive coefficient suggests a spurious association. One explanation is that maternal mortality is capturing something about the general quality of health care — there is not much variation between rich countries, and only a few countries with high maternal mortality are driving the possibly spurious association.

### Key Questions

1. Does removing Maternal Mortality affect model performance (R², MAE)?
2. How do other indicators' importance values change after removal?
3. Are there any changes in the ranking of top indicators?
4. Does removing Maternal Mortality improve model interpretability (by removing counterintuitive associations)?

### Baseline Results (With Maternal Mortality)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.877
- **Mean Absolute Error (MAE)**: 0.318 years
- **MaternalMortality indicator importance**: 1.89 (ranked #5)
- **Top indicators**:
  1. Neoplasms (12.0)
  2. UnintentionalInjury (4.96)
  3. ChronicRespiratory (2.57)
  4. LiverDiseaseDeathRate (2.12)
  5. **MaternalMortality (1.89)** ← to be removed
  6. Suicide (1.82)
  7. Alcohol (1.62)

**HALE Gap Model:**
- **Cross-validation R²**: 0.761 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.402 years
- **MaternalMortality indicator importance**: 2.15 (ranked #7)
- **Top indicators**:
  1. Neoplasms (23.8)
  2. UnintentionalInjury (5.59)
  3. ChronicRespiratory (4.89)
  4. Cardiovascular (3.48)
  5. Suicide (2.78)
  6. LiverDiseaseDeathRate (2.39)
  7. **MaternalMortality (2.15)** ← to be removed
  8. Homicide (1.9)
  9. Alcohol (1.8)

### New Results (Without Maternal Mortality)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.872 (↓ -0.005 from baseline 0.877, -0.6% decrease)
- **Mean Absolute Error (MAE)**: 0.341 years (↑ +0.023 from baseline 0.318, +7.2% increase)
- **MaternalMortality**: Removed from model
- **Top indicators**:
  1. Neoplasms (11.4, was 12.0)
  2. UnintentionalInjury (5.11, was 4.96)
  3. ChronicRespiratory (2.09, was 2.57)
  4. LiverDiseaseDeathRate (1.98, was 2.12)
  5. Suicide (1.86, was 1.82)
  6. Alcohol (1.6, was 1.62)
  7. Homicide (1.08, newly selected)
  8. Diabetes (0.838)
  9. RoadTraffic (0.339)
  10. Childhood (0.0558)

**Counterfactual Analysis (USA)**:
- MaternalMortality: Removed (no counterfactual effect)

**HALE Gap Model:**
- **Cross-validation R²**: 0.78 (Elastic Net) (↑ +0.019 from baseline 0.761, +2.5% improvement)
- **Mean Absolute Error (MAE)**: 0.417 years (↑ +0.015 from baseline 0.402, +3.7% increase)
- **MaternalMortality**: Removed from model
- **Top indicators**:
  1. Neoplasms (23.7, was 23.8)
  2. Cardiovascular (7.33, was 3.48) ← **major increase**
  3. UnintentionalInjury (5.55, was 5.59)
  4. ChronicRespiratory (4.73, was 4.89)
  5. Homicide (3.04, was 1.9) ← **major increase**
  6. Suicide (2.81, was 2.78)
  7. LiverDiseaseDeathRate (2.29, was 2.39)
  8. Alcohol (1.71, was 1.8)
  9. Diabetes (1.27)
  10. RoadTraffic (0.474)

**Counterfactual Analysis (USA)**:
- MaternalMortality: Removed (no counterfactual effect)

### Comparison and Conclusions

#### Major Findings

**1. Model Performance Changes Are Small**

**Life Expectancy**:
- R²: 0.877 → 0.872 (-0.6% decrease, very small)
- MAE: 0.318 → 0.341 years (+7.2% increase)
- **Note**: Small decrease in R² and small increase in MAE suggest minimal impact on model performance

**HALE**:
- R²: 0.761 → 0.78 (Elastic Net) (+2.5% improvement)
- MAE: 0.402 → 0.417 years (+3.7% increase)
- **Note**: R² improved slightly, but MAE increased slightly. The improvement in R² suggests better model fit, while the increase in MAE may reflect increased model complexity or different regularization.

**2. Importance Redistribution After Removal**

**Life Expectancy**:
- Most indicators showed small decreases in importance:
  - Neoplasms: 12.0 → 11.4 (-5%)
  - ChronicRespiratory: 2.57 → 2.09 (-19%)
  - LiverDiseaseDeathRate: 2.12 → 1.98 (-7%)
  - Alcohol: 1.62 → 1.6 (-1%)
- Homicide was newly selected (1.08), suggesting it gained importance after MaternalMortality removal
- Overall, the changes are relatively small, suggesting MaternalMortality was not capturing unique variance

**HALE**:
- **Cardiovascular showed a major increase**: 3.48 → 7.33 (+111% increase, from #4 to #2)
- **Homicide showed a major increase**: 1.9 → 3.04 (+60% increase, from #8 to #5)
- Other indicators showed small changes:
  - Neoplasms: 23.8 → 23.7 (essentially unchanged)
  - UnintentionalInjury: 5.59 → 5.55 (small decrease)
  - ChronicRespiratory: 4.89 → 4.73 (small decrease)
  - Suicide: 2.78 → 2.81 (small increase)
  - LiverDiseaseDeathRate: 2.39 → 2.29 (small decrease)
  - Alcohol: 1.8 → 1.71 (small decrease)

**3. Cardiovascular and Homicide Gained Substantial Importance in HALE Model**

**Critical Finding**: After removing MaternalMortality, Cardiovascular and Homicide showed substantial increases in importance in the HALE model:

- **Cardiovascular**: +111% increase (3.48 → 7.33), moved from #4 to #2
- **Homicide**: +60% increase (1.9 → 3.04), moved from #8 to #5

This suggests that MaternalMortality may have been capturing some variance that is now being captured by Cardiovascular and Homicide. This could indicate:
- Multicollinearity between MaternalMortality and these indicators
- MaternalMortality was acting as a proxy for general healthcare quality, which is also related to Cardiovascular and Homicide outcomes
- The positive coefficient for MaternalMortality was indeed spurious, and removing it allows other indicators to better capture the true relationships

**4. Homicide Was Newly Selected for Life Expectancy Model**

**Life Expectancy**:
- Homicide was not selected in the baseline model (with MaternalMortality)
- After removing MaternalMortality, Homicide was selected with importance 1.08 (ranked #7)

This suggests that MaternalMortality may have been suppressing Homicide's selection in the Life Expectancy model, possibly due to multicollinearity or shared variance.

**5. Counterfactual Effects**

Since MaternalMortality was removed, there are no counterfactual effects to compare. However, the removal of MaternalMortality's counterfactual effect (which would have been positive, counterintuitively) improves model interpretability.

#### Answers to Key Questions

1. **Does removing Maternal Mortality affect model performance (R², MAE)?**
   - **MINIMAL IMPACT** — Life Expectancy R² decreased slightly (-0.6%), while HALE R² improved slightly (+2.5%). MAE increased slightly for both models (+7.2% for LE, +3.7% for HALE). The changes are relatively small, suggesting MaternalMortality was not critical for model fit.

2. **How do other indicators' importance values change after removal?**
   - **MIXED** — For Life Expectancy, most indicators showed small decreases in importance, while Homicide was newly selected. For HALE, Cardiovascular and Homicide showed substantial increases (+111% and +60% respectively), while other indicators showed small changes.

3. **Are there any changes in the ranking of top indicators?**
   - **YES, for HALE** — Cardiovascular moved from #4 to #2, and Homicide moved from #8 to #5. For Life Expectancy, the top rankings remained similar, with Homicide newly entering at #7.

4. **Does removing Maternal Mortality improve model interpretability?**
   - **YES** — Removing the counterintuitive positive coefficient for MaternalMortality improves model interpretability. The fact that Cardiovascular and Homicide gained importance after removal suggests that MaternalMortality may have been capturing spurious associations related to general healthcare quality.

#### Implications

The removal of Maternal Mortality has **moderate impacts** on model results:

1. **Model performance is largely unchanged** — The small changes in R² and MAE suggest that MaternalMortality was not critical for model fit, supporting the decision to remove it due to the counterintuitive coefficient.

2. **Cardiovascular and Homicide gained substantial importance in HALE model** — The large increases in importance for Cardiovascular (+111%) and Homicide (+60%) suggest that MaternalMortality may have been suppressing these indicators, possibly due to multicollinearity or shared variance related to healthcare quality.

3. **Homicide was newly selected for Life Expectancy model** — This suggests that MaternalMortality was suppressing Homicide's selection, and removing it allows Homicide to contribute to the model.

4. **Removal improves interpretability** — Removing the counterintuitive positive coefficient for MaternalMortality improves model interpretability, as higher female mortality should close the gap, not widen it.

5. **Spurious association hypothesis supported** — The fact that removing MaternalMortality allows other indicators (particularly Cardiovascular and Homicide) to gain importance supports the hypothesis that MaternalMortality was capturing a spurious association related to general healthcare quality rather than a direct causal relationship.

#### Recommendations

1. **Keep Maternal Mortality removed** — The removal of MaternalMortality improves model interpretability by eliminating the counterintuitive positive coefficient. The small impact on model performance and the redistribution of importance to other indicators (particularly Cardiovascular and Homicide) support this decision.

2. **Investigate the relationship with Cardiovascular and Homicide** — The substantial increases in importance for Cardiovascular and Homicide after removing MaternalMortality suggest there may be shared variance related to healthcare quality. This relationship should be investigated further.

3. **Document the rationale** — The removal of MaternalMortality is justified by:
   - Counterintuitive positive coefficient (higher female mortality should close gap, not widen it)
   - Minimal impact on model performance
   - Improvement in model interpretability
   - Redistribution of importance to other indicators that may better capture the underlying relationships

4. **Monitor model performance** — The small changes in model performance suggest that removing MaternalMortality does not harm model fit. Continue to monitor model performance as other indicators are added or modified.

5. **Consider the healthcare quality proxy hypothesis** — The fact that Cardiovascular and Homicide gained importance after removing MaternalMortality supports the hypothesis that MaternalMortality was acting as a proxy for general healthcare quality. This relationship should be considered when interpreting model results.

---

## Replacing WHO Under-Five Mortality with IHME All-Cause Under 5

### Replacement Details

- **Replaced Indicator**: WHO `MDG_0000000007` - Under-five mortality rate (per 1,000 live births)
- **New Indicator**: IHME `All-Cause Deaths Under 5 Years of Age` - All-cause deaths under 5 years (per 100,000 population)
- **Rationale**: The IHME indicator provides better temporal coverage (1990-2023) and consistent methodology with other IHME indicators. **Note**: The two indicators use different measurement units (WHO: per 1,000 live births; IHME: per 100,000 population), so direct comparison of absolute values is not meaningful, but gender gaps can still be compared.

### Key Questions

1. Does replacing WHO U5MR with IHME All-Cause Under 5 affect model performance (R², MAE)?
2. How does the Childhood indicator's importance change after replacement?
3. Are there any changes in the ranking of top indicators?
4. Does the replacement improve model interpretability or temporal coverage?

### Baseline Results (With WHO U5MR)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.872
- **Mean Absolute Error (MAE)**: 0.341 years
- **Childhood indicator importance**: 0.0558 (ranked #10, very low)
- **Top indicators**:
  1. Neoplasms (11.4)
  2. UnintentionalInjury (5.11)
  3. ChronicRespiratory (2.09)
  4. LiverDiseaseDeathRate (1.98)
  5. Suicide (1.86)
  6. Alcohol (1.6)
  7. Homicide (1.08)
  8. Diabetes (0.838)
  9. RoadTraffic (0.339)
  10. **Childhood (0.0558)**

**HALE Gap Model:**
- **Cross-validation R²**: 0.78 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.417 years
- **Childhood indicator importance**: Not in top 10 (very low, < 0.5)
- **Top indicators**:
  1. Neoplasms (23.7)
  2. Cardiovascular (7.33)
  3. UnintentionalInjury (5.55)
  4. ChronicRespiratory (4.73)
  5. Homicide (3.04)
  6. Suicide (2.81)
  7. LiverDiseaseDeathRate (2.29)
  8. Alcohol (1.71)
  9. Diabetes (1.27)
  10. RoadTraffic (0.474)

### New Results (With IHME All-Cause Under 5)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.881 (↑ +0.009 from baseline 0.872, +1.0% improvement)
- **Mean Absolute Error (MAE)**: 0.321 years (↓ -0.020 from baseline 0.341, -5.9% improvement)
- **Childhood indicator importance**: 2.65 (ranked #4, **major increase** from 0.0558)
- **Top indicators**:
  1. Neoplasms (12.9)
  2. UnintentionalInjury (4.89)
  3. ChronicRespiratory (2.99)
  4. **Childhood (2.65)** ← **major increase** from 0.0558 (+4,650%)
  5. Suicide (2.18)
  6. LiverDiseaseDeathRate (1.96)
  7. Alcohol (1.51)
  8. Homicide (1.35)
  9. Diabetes (0.848)
  10. Cardiovascular (0.465)
  11. RoadTraffic (0.267)
  12. DrugDisorder (0.033)

**Counterfactual Analysis (USA)**:
- Childhood counterfactual effect: -0.263 years (reducing gap from 24.7 to 2.89, targeting Ireland)

**HALE Gap Model:**
- **Cross-validation R²**: 0.769 (Elastic Net) (↓ -0.011 from baseline 0.78, -1.4% decrease)
- **Mean Absolute Error (MAE)**: 0.431 years (↑ +0.014 from baseline 0.417, +3.4% increase)
- **Childhood indicator importance**: 3.55 (ranked #5, **major increase** from not in top 10)
- **Top indicators**:
  1. Neoplasms (23.2)
  2. Cardiovascular (7.38)
  3. UnintentionalInjury (5.42)
  4. ChronicRespiratory (4.83)
  5. **Childhood (3.55)** ← **newly prominent** (was not in top 10)
  6. Homicide (3.16)
  7. Suicide (2.81)
  8. LiverDiseaseDeathRate (2.28)
  9. Alcohol (1.71)
  10. Diabetes (1.36)
  11. RoadTraffic (0.495)
  12. DrugDisorder (0.244)

**Counterfactual Analysis (USA)**:
- Childhood counterfactual effect: -0.156 years (reducing gap from 24.7 to 2.89, targeting Ireland)

### Comparison and Conclusions

#### Major Findings

**1. Significant Increase in Childhood Indicator Importance (But Potentially Spurious)**

The replacement of WHO U5MR with IHME All-Cause Under 5 led to a **dramatic increase** in the Childhood indicator's importance:

- **Life Expectancy Model**: Importance increased from 0.0558 to 2.65 (+4,650%), moving from rank #10 to rank #4.
- **HALE Model**: Importance increased from not in top 10 (< 0.5) to 3.55 (ranked #5), making it a top-5 indicator.

However, this increase may be **spurious** due to confounding: the IHME indicator (deaths per 100,000 population) is confounded with age structure and fertility rates. Countries with more people of child-bearing age and higher fertility will have more people under 5 in the population, and therefore more deaths under 5, even if the underlying risk of death for children is the same. The WHO indicator (deaths per 1,000 live births) controls for these factors by using live births as the denominator, making it a more direct measure of early-life mortality risk.

**2. Mixed Model Performance Changes**

The replacement resulted in mixed changes in model performance:

- **Life Expectancy R²**: 0.872 → 0.881 (+1.0% improvement)
- **Life Expectancy MAE**: 0.341 → 0.321 years (-5.9% improvement)
- **HALE R²**: 0.78 → 0.769 (-1.4% decrease)
- **HALE MAE**: 0.417 → 0.431 years (+3.4% increase)

The Life Expectancy model improved, while the HALE model showed a small decrease in performance. The changes are relatively small and within acceptable limits.

**3. Other Indicators Show Small Changes**

Most other indicators showed small changes in importance and rankings:
- Neoplasms remained the top indicator in both models
- UnintentionalInjury, ChronicRespiratory, Suicide, and LiverDiseaseDeathRate maintained their high rankings
- Cardiovascular decreased in importance in the LE model (from not selected to 0.465) but remained #2 in the HALE model

**4. Measurement Unit Differences and Confounding**

**Important Note**: The WHO and IHME indicators use different measurement units:
- **WHO U5MR**: Deaths per 1,000 live births
- **IHME All-Cause Under 5**: Deaths per 100,000 population

These different units reflect fundamentally different approaches to measuring early-life mortality. The **IHME indicator (per 100,000 population) is confounded with age structure and fertility rates**: countries with more people of child-bearing age and higher fertility will have more people under 5 in the population, and therefore more deaths under 5, even if the underlying risk of death for children is the same. The **WHO indicator (per 1,000 live births) controls for these factors** by using live births as the denominator, making it a more direct measure of early-life mortality risk independent of demographic structure.

#### Answers to Key Questions

1. **Does replacing WHO U5MR with IHME All-Cause Under 5 affect model performance (R², MAE)?**
   - **MIXED IMPACT** — Life Expectancy model improved (R² +1.0%, MAE -5.9%), while HALE model showed small decreases (R² -1.4%, MAE +3.4%). Overall, the changes are small and acceptable.

2. **How does the Childhood indicator's importance change after replacement?**
   - **MAJOR INCREASE (BUT POTENTIALLY SPURIOUS)** — Childhood importance increased dramatically: from 0.0558 to 2.65 in LE model (+4,650%), and from not in top 10 to 3.55 in HALE model (ranked #5). However, this increase may be spurious due to confounding with age structure and fertility rates, rather than reflecting true variation in early-life mortality risk.

3. **Are there any changes in the ranking of top indicators?**
   - **YES** — Childhood moved from rank #10 (LE) or not in top 10 (HALE) to rank #4 (LE) and #5 (HALE). Other indicators showed small changes in rankings, but the top indicators (Neoplasms, UnintentionalInjury, ChronicRespiratory) remained stable.

4. **Does the replacement improve model interpretability or temporal coverage?**
   - **NO, DUE TO CONFOUNDING** — While the IHME indicator provides better temporal coverage (1990-2023), the confounding with age structure and fertility rates makes it less interpretable. The WHO indicator (per 1,000 live births) is methodologically more appropriate because it controls for these confounding factors, even though it has less temporal coverage.

#### Implications

The replacement of WHO U5MR with IHME All-Cause Under 5 reveals important methodological considerations:

1. **Confounding with Age Structure and Fertility**: The IHME indicator (deaths per 100,000 population) is **confounded with age structure and fertility rates**. Countries with:
   - A larger proportion of the population in child-bearing age
   - Higher fertility rates
   
   will have more people under age 5 in the population, and therefore more deaths under 5, even if the underlying risk of death for children is the same. This confounding makes it difficult to interpret the IHME indicator as a pure measure of early-life mortality risk.

2. **WHO Indicator Controls for Confounding**: The WHO indicator (deaths per 1,000 live births) **controls for age structure and fertility** by using live births as the denominator. This makes it a more direct measure of the risk of death for children, independent of how many children are in the population.

3. **Why IHME Shows Higher Importance**: The dramatic increase in Childhood indicator importance with the IHME version (from 0.0558 to 2.65 in LE model) may be **partially or entirely due to this confounding**. The IHME indicator may be capturing variation in fertility rates and age structure across countries, which could be correlated with gender gaps in life expectancy through mechanisms unrelated to early-life mortality risk itself.

4. **Measurement Unit Considerations**: The different measurement units (per 1,000 live births vs per 100,000 population) reflect fundamentally different approaches to measuring early-life mortality, with the WHO approach being more appropriate for isolating mortality risk from demographic structure.

#### Recommendations

1. **Retain WHO indicator**: Despite the dramatic increase in importance with the IHME indicator, **the WHO U5MR indicator should be retained** in the final model because:
   - It controls for age structure and fertility, providing a more direct measure of early-life mortality risk
   - The higher importance of the IHME indicator may be spurious, driven by confounding with demographic factors rather than true variation in mortality risk
   - The WHO indicator's methodology (deaths per 1,000 live births) is more appropriate for cross-country comparisons of child mortality risk

2. **Document the confounding issue**: Clearly document that the IHME All-Cause Under 5 indicator (deaths per 100,000 population) is confounded with age structure and fertility, and that this confounding likely explains why it shows higher importance in the model.

3. **Accept lower importance for WHO indicator**: The lower importance of the WHO U5MR indicator (0.0558 in LE model, not in top 10 for HALE) may reflect that:
   - Early-life mortality has less variation across OECD countries (most have low child mortality)
   - The indicator is appropriately measuring mortality risk without demographic confounding
   - The lower importance is not necessarily a problem, as it may reflect the true, smaller contribution of early-life mortality to gender gaps in OECD countries

4. **Consider temporal coverage trade-off**: While the WHO indicator has less temporal coverage than IHME, the methodological appropriateness (controlling for age structure and fertility) outweighs the temporal coverage advantage for this analysis.

---

## Removing Childhood Indicator (Under-Five Mortality)

### Removal Details

- **Removed Indicator**: WHO `MDG_0000000007` - Under-five mortality rate (per 1,000 live births)
- **Rationale**: The Childhood indicator had very low importance (0.0558 in LE model, not in top 10 for HALE) and limited temporal coverage. Additionally, the IHME alternative (All-Cause Deaths Under 5, per 100,000 population) is confounded with age structure and fertility rates, making it methodologically inappropriate. Given the low importance and the lack of a suitable alternative with better temporal coverage, removing the indicator entirely simplifies the model without sacrificing meaningful predictive power.

### Key Questions

1. Does removing Childhood affect model performance (R², MAE)?
2. How do other indicators' importance values change after removal?
3. Are there any changes in the ranking of top indicators?
4. Does removing Childhood simplify the model without losing important information?

### Baseline Results (With Childhood - WHO U5MR)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.872
- **Mean Absolute Error (MAE)**: 0.341 years
- **Childhood indicator importance**: 0.0558 (ranked #10, very low)
- **Top indicators**:
  1. Neoplasms (11.4)
  2. UnintentionalInjury (5.11)
  3. ChronicRespiratory (2.09)
  4. LiverDiseaseDeathRate (1.98)
  5. Suicide (1.86)
  6. Alcohol (1.6)
  7. Homicide (1.08)
  8. Diabetes (0.838)
  9. RoadTraffic (0.339)
  10. **Childhood (0.0558)**

**HALE Gap Model:**
- **Cross-validation R²**: 0.78 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.417 years
- **Childhood indicator importance**: Not in top 10 (very low, < 0.5)
- **Top indicators**:
  1. Neoplasms (23.7)
  2. Cardiovascular (7.33)
  3. UnintentionalInjury (5.55)
  4. ChronicRespiratory (4.73)
  5. Homicide (3.04)
  6. Suicide (2.81)
  7. LiverDiseaseDeathRate (2.29)
  8. Alcohol (1.71)
  9. Diabetes (1.27)
  10. RoadTraffic (0.474)

### New Results (Without Childhood)

**Life Expectancy Gap Model:**
- **Cross-validation R²**: 0.879 (↑ +0.007 from baseline 0.872, +0.8% improvement)
- **Mean Absolute Error (MAE)**: 0.326 years (↓ -0.015 from baseline 0.341, -4.4% improvement)
- **Childhood**: Removed from model
- **Top indicators**:
  1. Neoplasms (11.4, unchanged)
  2. UnintentionalInjury (4.93, was 5.11, -3.5% decrease)
  3. ChronicRespiratory (2.22, was 2.09, +6.2% increase)
  4. LiverDiseaseDeathRate (2.08, was 1.98, +5.1% increase)
  5. Homicide (1.84, was 1.08, +70% increase) ← **major increase**
  6. Suicide (1.82, was 1.86, -2.2% decrease)
  7. Alcohol (1.53, was 1.6, -4.4% decrease)
  8. Diabetes (0.848, unchanged)
  9. RoadTraffic (0.442, was 0.339, +30% increase)
  10. Cardiovascular (0, was not selected, now not selected)

**Counterfactual Analysis (USA)**:
- Childhood: Removed (no counterfactual effect)

**HALE Gap Model:**
- **Cross-validation R²**: 0.778 (Elastic Net) (↓ -0.002 from baseline 0.78, -0.3% decrease)
- **Mean Absolute Error (MAE)**: 0.422 years (↑ +0.005 from baseline 0.417, +1.2% increase)
- **Childhood**: Removed from model
- **Top indicators**:
  1. Neoplasms (28.2, was 23.7, +19% increase) ← **major increase**
  2. UnintentionalInjury (5.69, was 5.55, +2.5% increase)
  3. Cardiovascular (5.55, was 7.33, -24% decrease) ← **major decrease**
  4. ChronicRespiratory (5.22, was 4.73, +10% increase)
  5. Homicide (3.92, was 3.04, +29% increase) ← **major increase**
  6. Suicide (2.96, was 2.81, +5.3% increase)
  7. LiverDiseaseDeathRate (2.52, was 2.29, +10% increase)
  8. Alcohol (1.73, was 1.71, +1.2% increase)
  9. Diabetes (1.69, was 1.27, +33% increase) ← **major increase**
  10. RoadTraffic (0.468, was 0.474, -1.3% decrease)

**Counterfactual Analysis (USA)**:
- Childhood: Removed (no counterfactual effect)

### Comparison and Conclusions

#### Major Findings

**1. Minimal Impact on Model Performance**

The removal of Childhood resulted in very small changes in model performance:

- **Life Expectancy R²**: 0.872 → 0.879 (+0.8% improvement)
- **Life Expectancy MAE**: 0.341 → 0.326 years (-4.4% improvement)
- **HALE R²**: 0.78 → 0.778 (-0.3% decrease, essentially unchanged)
- **HALE MAE**: 0.417 → 0.422 years (+1.2% increase)

The changes are very small and within acceptable limits, confirming that Childhood was not contributing meaningfully to model fit.

**2. Some Redistribution of Importance**

The removal of Childhood led to some redistribution of importance, with notable changes in both models:

**Life Expectancy Model:**
- **Homicide**: Increased from 1.08 to 1.84 (+70% increase), moving from rank #7 to #5
- **RoadTraffic**: Increased from 0.339 to 0.442 (+30% increase)
- **ChronicRespiratory**: Increased from 2.09 to 2.22 (+6.2% increase)
- **LiverDiseaseDeathRate**: Increased from 1.98 to 2.08 (+5.1% increase)
- Most other indicators showed small changes or remained stable

**HALE Model:**
- **Neoplasms**: Increased from 23.7 to 28.2 (+19% increase), strengthening its position as #1
- **Homicide**: Increased from 3.04 to 3.92 (+29% increase), moving from rank #5 to #5 (but higher importance)
- **Diabetes**: Increased from 1.27 to 1.69 (+33% increase)
- **Cardiovascular**: Decreased from 7.33 to 5.55 (-24% decrease), moving from rank #2 to #3
- **ChronicRespiratory**: Increased from 4.73 to 5.22 (+10% increase)
- **LiverDiseaseDeathRate**: Increased from 2.29 to 2.52 (+10% increase)

**3. Homicide Gained Importance in Both Models**

**Critical Finding**: Homicide showed substantial increases in importance in both models after removing Childhood:
- **Life Expectancy**: +70% increase (1.08 → 1.84), moving from rank #7 to #5
- **HALE**: +29% increase (3.04 → 3.92), maintaining rank #5 but with higher importance

This suggests that Childhood may have been capturing some variance that is now being attributed to Homicide, or that removing Childhood allows Homicide to better capture its true relationship with gender gaps.

**4. Neoplasms Strengthened in HALE Model**

**HALE Model**: Neoplasms importance increased from 23.7 to 28.2 (+19% increase), further strengthening its position as the top indicator. This suggests that removing Childhood allows Neoplasms to better capture its relationship with the HALE gap.

**5. Cardiovascular Decreased in HALE Model**

**HALE Model**: Cardiovascular importance decreased from 7.33 to 5.55 (-24% decrease), moving from rank #2 to #3. This suggests that Childhood may have been interacting with Cardiovascular in some way, or that the removal allows other indicators (particularly Neoplasms) to capture more variance.

#### Answers to Key Questions

1. **Does removing Childhood affect model performance (R², MAE)?**
   - **MINIMAL IMPACT** — Life Expectancy R² improved slightly (+0.8%), MAE improved (-4.4%). HALE R² decreased very slightly (-0.3%), MAE increased slightly (+1.2%). The changes are very small and within acceptable limits, confirming that Childhood was not contributing meaningfully to model fit.

2. **How do other indicators' importance values change after removal?**
   - **MIXED CHANGES** — Homicide showed substantial increases in both models (+70% for LE, +29% for HALE). Neoplasms increased in HALE model (+19%). Cardiovascular decreased in HALE model (-24%). Most other indicators showed small changes. The redistribution suggests that Childhood may have been interacting with other indicators or capturing some shared variance.

3. **Are there any changes in the ranking of top indicators?**
   - **MINOR CHANGES** — In the Life Expectancy model, Homicide moved from #7 to #5. In the HALE model, Cardiovascular moved from #2 to #3, while Neoplasms strengthened its #1 position. The top indicators remained largely stable, with minor shifts in rankings.

4. **Does removing Childhood simplify the model without losing important information?**
   - **YES** — The minimal impact on model performance and the very low importance of Childhood (0.0558 in LE, not in top 10 for HALE) confirm that removing it simplifies the model without losing meaningful predictive power. The redistribution of importance to other indicators (particularly Homicide and Neoplasms) suggests that the model is more robust without Childhood.

#### Implications

The removal of Childhood has **minimal impacts** on model results:

1. **Model performance is essentially unchanged** — The very small changes in R² and MAE confirm that Childhood was not contributing meaningfully to model fit, supporting the decision to remove it.

2. **Some redistribution of importance** — The removal led to some redistribution of importance, with Homicide gaining substantial importance in both models and Neoplasms strengthening in the HALE model. This suggests that Childhood may have been interacting with these indicators or capturing some shared variance.

3. **Model simplification** — Removing Childhood simplifies the model by eliminating an indicator with very low importance and limited temporal coverage, without sacrificing meaningful predictive power.

4. **No suitable alternative** — The lack of a suitable alternative (IHME version is confounded with age structure and fertility) supports the decision to remove Childhood entirely rather than replace it.

#### Recommendations

1. **Confirm removal**: The removal of Childhood is justified and should be maintained in the final model, given:
   - Very low importance (0.0558 in LE, not in top 10 for HALE)
   - Minimal impact on model performance
   - Limited temporal coverage
   - Lack of a suitable alternative (IHME version is methodologically inappropriate due to confounding)

2. **Document the rationale**: Clearly document that Childhood was removed because:
   - It had very low importance in both models
   - It has limited temporal coverage
   - The IHME alternative is confounded with age structure and fertility
   - Removing it simplifies the model without sacrificing meaningful predictive power

3. **Note the redistribution**: The redistribution of importance to other indicators (particularly Homicide and Neoplasms) should be noted, as it suggests that Childhood may have been interacting with these indicators or capturing some shared variance.

4. **Accept the model simplification**: The minimal impact on model performance confirms that removing Childhood is a reasonable simplification that does not harm model fit.


