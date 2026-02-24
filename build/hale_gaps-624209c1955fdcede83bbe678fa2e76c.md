# The Gender Gap in Life Expectancy

## Introduction

In most countries, women live longer than men. This difference is often assumed to be natural and inevitable. In some contexts, like the World Economic Forum's Global Gender Gap Report, a smaller gap is sometimes interpreted as evidence of discrimination against women.

But the gap varies substantially between countries and has changed over time, which suggests that it might not be entirely natural, or if it is, it can be mitigated. For example, in the Netherlands the gap is now close to zero.

The goal of this investigation is to explore differences in life expectancy and health-adjusted life expectancy (HALE) between countries, in order to identify the factors that contribute to the observed gender gaps and to understand what it would take to close those gaps by improving health outcomes for both men and women.

We use Elastic Net regression to model the gender gap in life expectancy and HALE as a function of cause-specific mortality indicators. This approach handles the high correlation among predictors and identifies which patterns of mortality are most strongly associated with the life expectancy gap. Details of the methodology are described in the Methodology section below.

## Data

The analysis uses data from two sources:

1. WHO Global Health Observatory (GHO) API: Provides HALE, life expectancy, and various cause-specific mortality indicators. Data is accessed programmatically via the GHO OData API.

2. IHME Global Burden of Disease: Provides additional cause-specific mortality indicators with better temporal coverage than WHO for some indicators, including cardiovascular disease, diabetes, chronic respiratory disease, and others.

For each indicator, we use the most recent available year per country, with data from 2000-2019. We exclude 2020 and later years to avoid distortions from the COVID-19 pandemic, which had significant impacts on mortality patterns that may not reflect underlying health factors. Using 2019 or earlier data provides a more stable baseline for understanding the gender gap.

The analysis focuses on OECD countries (38 countries) to ensure consistent data quality and comparability. For each country, we compute gender gaps by taking the difference between female and male values for each indicator.

## Target Variables

The analysis focuses on two target variables:

- HALE Gap: The difference in Healthy Life Expectancy between women and men (Female - Male, in years)
- Life Expectancy Gap: The difference in Life Expectancy between women and men (Female - Male, in years)


The following table shows the median across countries, minimum, and maximum values for HALE and Life Expectancy across OECD countries.

```{include} tables/target_rates.html
```


The following table shows the median, minimum, and maximum gender gaps (Female - Male) for HALE and Life Expectancy across OECD countries.

```{include} tables/target_gaps.html
```

## Predictors

We use the term "indicators" to refer to the variables we collect from WHO and IHME, and "predictors" to refer to the role a variable plays in a model. Not all indicators are necessarily predictors in a given model.

The following tables summarize the predictor indicators used to explain variation in the HALE and Life Expectancy gender gaps. Each indicator includes:

- Median Rate: The median across countries of the overall rate (computed as the average of male and female rates)
- Min Rate / Max Rate: The range of overall rates across countries
- Median Gap: The median gender gap (Male - Female for predictors) across countries
- Min Gap / Max Gap: The range of gender gaps across countries
- Corr HALE: Correlation with HALE gap
- Corr LE: Correlation with Life Expectancy gap


The following table shows statistics for the overall rates (computed as the midpoint, or average, of male and female rates) for each predictor indicator.

```{include} tables/predictor_rates.html
```


The following table shows statistics for the gender gaps (Male - Female) for each predictor indicator.

```{include} tables/predictor_gaps.html
```

### Rate-Gap Correlation

The following table shows the correlation between the overall rate and the gender gap for each predictor indicator. This helps identify indicators where countries with higher overall rates also tend to have larger gender gaps.

```{include} tables/rate_gap_correlation.html
```

### Top Correlations Among Predictors

The following tables show the strongest correlations between predictor indicators. These correlations help explain why we use Elastic Net regression instead of ordinary least squares, as many indicators are highly correlated with each other.


The following table shows the top correlations between the overall rates of different indicators.

```{include} tables/rate_rate_correlation_top10.html
```


The following table shows the top correlations between the gender gaps of different indicators.

```{include} tables/gap_gap_correlation_top10.html
```

## Methodology

### Why Use Elastic Net Instead of Ordinary Least Squares?

Before fitting any model, we can look at the correlations among the predictors. Many of the indicators are strongly correlated with each other. For example, across OECD countries:

- The median Childhood mortality rate is highly correlated with Homicide (ρ ≈ 0.86) and RoadTraffic (ρ ≈ 0.79).
- Alcohol is strongly correlated with Cardiovascular disease (ρ ≈ 0.83) and Poisoning (ρ ≈ 0.75), and moderately with Suicide (ρ ≈ 0.55).
- Cardiovascular disease is also correlated with Poisoning (ρ ≈ 0.66).
- UnintentionalInjury is correlated with Cardiovascular disease (ρ ≈ 0.54) and Suicide (ρ ≈ 0.49), and negatively with Childhood (ρ ≈ −0.50).

The same pattern appears in the gaps (female–male differences):

- The Childhood gap and Homicide gap are extremely highly correlated (ρ ≈ 0.92).
- The Alcohol gap is strongly correlated with the Suicide gap (ρ ≈ 0.79) and the UnintentionalInjury gap (ρ ≈ 0.76).
- The RoadTraffic and Homicide gaps are also strongly correlated (ρ ≈ 0.76).

So we have clusters of indicators that move together, both in their overall rates and in their gender gaps.


If we put all of these predictors into a single ordinary least squares (OLS) regression, the model is forced to divide the explanatory “credit” among highly correlated variables. In that setting:

- Small amounts of noise can change which variable gets the larger coefficient.
- Coefficients within a correlated cluster can flip sign or change magnitude dramatically.
- The allocation of effect size among correlated predictors is essentially arbitrary.

As a result, an OLS model with all indicators included does not give a stable or interpretable answer to the question “which factors matter most?”.



Elastic Net regression combines two kinds of regularization:

- An L2 (ridge) component that stabilizes coefficients and allows correlated predictors to share weight.
- An L1 (lasso) component that shrinks some coefficients all the way to zero when they do not improve predictive performance.

The model is tuned by cross-validation, so the amount of regularization is chosen to maximize out-of-sample predictive accuracy, not to fit the particular noise pattern in this dataset.

In practice, this means:

- Correlated predictors are handled coherently, with coefficients shrunk toward each other and toward zero.
- Predictors that do not add predictive information beyond the ones already in the model are often assigned coefficients very close to zero.
- The remaining non-zero coefficients identify a smaller set of predictors that are genuinely helpful for predicting the life expectancy gap.



In this application, many of the predictors are not just "associated" with the outcome in an abstract sense; they contribute to it almost by construction. Life Expectancy and HALE are computed from sex-specific mortality rates, so:

If the male death rate from Homicide, RoadTraffic, Alcohol, or Suicide is higher than the female rate, that directly pushes male life expectancy and HALE down relative to female.

The gaps in these predictors (female–male differences) therefore have a near-mechanical connection to the gap in life expectancy and HALE.

In other words, whenever we see a large female–male gap in one of these cause-specific mortality rates, we expect it to contribute to the female–male gap in life expectancy and HALE.

That does not mean that every non-zero coefficient in the regression can be interpreted as a clean causal effect. It does mean, however, that:

Predictors with a stronger direct influence on sex-specific mortality should generally be more predictive of the life expectancy gap.

Predictors that are only loosely or indirectly associated with these mortality differences should contribute less to out-of-sample prediction.


Putting these pieces together:

- We know from the correlation tables that indicators like Homicide, RoadTraffic, Childhood mortality, Alcohol, Poisoning, and Suicide form strongly correlated clusters, both in their overall rates and in their gaps.
- An OLS model would split coefficients among these indicators in an unstable and arbitrary way.
- Elastic Net instead uses predictive performance to decide which members of each correlated cluster carry the most useful information about the life expectancy gap.

As a result, when Elastic Net assigns substantial weight to a predictor like Alcohol or Homicide, and shrinks others in the same cluster toward zero, we can interpret that as:

> This indicator captures the key variation in sex-specific mortality that matters for explaining differences in life expectancy between women and men, given the other indicators in the model.

This does not prove causality in the strong sense, but it does provide a principled way to:

- handle collinearity among cause-specific mortality indicators,
- highlight which patterns of mortality and injury are most strongly associated with the life expectancy gap,
- and down-weight predictors that are merely redundant proxies for the ones that are truly driving the differences we observe.


## Results

### Life Expectancy Gap

We fit three regularized regression models (Ridge, Lasso, and Elastic Net) to predict the Life Expectancy gender gap using cause-specific mortality indicators. All models use 5-fold cross-validation for model selection and evaluation.

#### Model Performance

The following table compares the three models using cross-validation R² and mean absolute error:

```{include} tables/model_comparison_le.html
```

Elastic Net performs best with a cross-validation R² of 0.851, meaning it explains about 85% of the variance in the life expectancy gap across OECD countries. The mean absolute error is 0.375 years, indicating that on average, the model's predictions are off by about 4.5 months.

Elastic Net selects 17 out of 25 predictors as having non-zero coefficients, effectively performing feature selection while maintaining good predictive performance. The following table shows how many predictors each model uses:

```{include} tables/feature_selection_summary_le.html
```

#### Feature Importance

To understand which factors contribute most to the life expectancy gap, we calculate feature importance as the absolute value of the coefficient multiplied by the standard deviation of the predictor. This measures each predictor's contribution to gap variation on the original scale.

The following figure shows all predictors with non-zero coefficients by importance:

```{figure} figs/predictor_importance_le.png
---
width: 600px
alt: Predictors by importance for Life Expectancy gap
---
Predictors by importance. The Alcohol gap (Gap_Alcohol) dominates, with an importance of 19.1, far exceeding all other predictors.
```

The Alcohol gap is by far the most important predictor, with an importance of 19.1. This means that differences in alcohol-attributable death rates between men and women are the strongest driver of the life expectancy gender gap across OECD countries.

#### Indicator-Level Importance

When we aggregate importance by indicator (combining Mid and Gap predictors), we can see which health indicators matter most overall:

```{include} tables/indicator_importance_le.html
```

The following figure visualizes indicator-level importance:

```{figure} figs/indicator_importance_le.png
---
width: 600px
alt: Indicator importance for Life Expectancy gap
---
Indicator-level importance, showing which health indicators contribute most to explaining the life expectancy gender gap.
```

The top three indicators are:

1. **Alcohol** (total importance: 19.1) — The gender gap in alcohol-attributable deaths is the dominant factor. This comes entirely from the gap component, not the overall rate.

2. **Neoplasms** (total importance: 12.1) — The gender gap in cancer death rates is the second most important factor, also coming entirely from the gap component. Some part of this gap is due to past smoking patterns, as men historically smoked more than women. As smoking rates continue to decline, this gap will likely shrink without further intervention, though efforts to reduce smoking should continue.

3. **Cardiovascular disease** (total importance: 10.4) — Cardiovascular disease contributes substantially, but this comes from the overall rate (Mid), not the gender gap. This suggests that countries with higher overall cardiovascular death rates tend to have larger life expectancy gaps, regardless of the gender difference in cardiovascular mortality. Note that cardiovascular disease rates are often higher for women than men because cardiovascular risk increases with age, and women are more likely to live long enough to develop cardiovascular disease.

The remaining indicators have much smaller importance values, with Chronic Respiratory disease (5.0), Unintentional Injury (3.4), and Suicide (0.9) being the next most important. Like neoplasms, some part of the Chronic Respiratory disease gap is due to past smoking patterns, so it will likely shrink as smoking rates continue to decline, though efforts to reduce smoking should continue.

#### Model Diagnostics

The model shows good fit with no obvious systematic patterns in the residuals. The following figure shows residuals plotted against predicted values:

```{figure} figs/residuals_vs_predicted_le.png
---
width: 600px
alt: Residuals vs predicted values
---
Residuals plotted against predicted life expectancy gap values. The points are scattered around zero with no obvious patterns, suggesting the model captures the relationship well.
```

The following table shows country-level predictions and residuals:

```{include} tables/residuals_by_country_le.html
```

#### Comparison with Ordinary Least Squares

For comparison, we also fit an ordinary least squares (OLS) model using only the 17 predictors selected by Elastic Net. The following table compares performance:

```{include} tables/performance_comparison_le.html
```

Both models perform similarly, with OLS achieving a slightly higher R² (0.977 vs 0.974) and lower MAE (0.199 vs 0.219 years) on the training data. However, the cross-validation R² of 0.851 for Elastic Net is a better estimate of out-of-sample performance. The difference between in-sample and cross-validation R² indicates some overfitting, which is expected with a small sample size (38 countries) and many predictors.

#### Key Findings

The analysis reveals that alcohol-attributable deaths are the primary driver of the life expectancy gender gap in OECD countries. The gender gap in alcohol-related mortality (where men have higher rates than women) accounts for more than half of the total importance across all indicators.

Cancer (neoplasms) is the second most important factor, also driven by the gender gap rather than overall rates. Cardiovascular disease contributes substantially, but through overall rates rather than gender differences.

These findings suggest that policies and interventions targeting alcohol-related mortality, particularly among men, could have the largest impact on reducing the life expectancy gender gap. The fact that the Alcohol gap dominates the model, and that it comes entirely from the gap component (not the overall rate), indicates that gender differences in alcohol consumption and related mortality are central to understanding why women live longer than men in most countries.

#### Counterfactual Analysis

To understand what it would take to close the life expectancy gender gap, we perform a counterfactual analysis that asks: "What would happen to a country's predicted life expectancy gap if we adjusted each gap predictor to the best attainable value observed across OECD countries?"

#### Methodology

For each gap predictor, we identify the best attainable value based on the current gap:

- If the current gap is positive (Male > Female), we find the country with the smallest gap (minimum), which represents the best case where the gender difference is minimized.
- If the current gap is negative (Female > Male), we find the country with the largest gap (maximum, most positive), which represents the best case where the gender difference is minimized in the opposite direction.

If the target gap has the opposite sign of the current gap (meaning no country has achieved a better value in the desired direction), we conservatively set the target to zero.

To achieve the target gap, we adjust the underlying male or female values:

- If the gap is positive (Male > Female), we bring men toward women's level by reducing the male rate.
- If the gap is negative (Female > Male), we bring women toward men's level by reducing the female rate.

After adjusting the male and female values, we recompute the Mid (average) and Gap values, then use the model to generate a counterfactual prediction. The difference between the original and counterfactual predictions shows how much the life expectancy gap would change if that particular predictor gap were reduced to the best attainable level.

This approach is conservative in two ways:

1. We only adjust gap variables, not overall rates, because we're more confident that gap variables have a causal relationship with the life expectancy gap.
2. We use other countries as evidence of what's attainable: if another country has achieved a smaller gap, that's evidence it's possible. If no country has achieved a better gap in the desired direction, we set the target to zero rather than assuming complete elimination is possible.

#### Results for the United States

The following table shows counterfactual results for the United States, sorted by importance (the same importance measure used in the feature importance analysis):

```{include} tables/counterfactuals_usa_le.html
```

Note that the table is sorted by importance, which indicates in general how effective it is to reduce a particular gap. The counterfactual results (the "Change in LE gap" column) indicate how much reducing that gap would specifically affect the life expectancy gap in the United States, which depends on how far the United States is from the minimal attainable gap for that indicator. For example, Alcohol has high importance and also shows a large counterfactual effect for the United States because the U.S. has a large Alcohol gap (38.8) relative to the best attainable level (9.9 in Türkiye).

The results show that reducing the Alcohol gap from 38.8 to 9.9 (the level achieved in Türkiye) would reduce the predicted life expectancy gap by 0.96 years, the largest single impact. Reducing the Neoplasms gap to zero would reduce the gap by an additional 0.23 years. Together, these two factors account for the majority of the potential reduction.

Several indicators show negative changes (gap-closing effects), while a few show positive changes (gap-widening effects). The positive changes occur when reducing a gap predictor would actually increase the life expectancy gap, which can happen when the relationship between predictors and the outcome is complex due to correlations among indicators.

#### Aggregate Effects

When we sum the effects across all indicators, we can see the total potential impact:

- **Gap-closing indicators** (negative changes): The sum of all indicators that would reduce the life expectancy gap is approximately **-1.93 years**. These include Alcohol (-0.96), Neoplasms (-0.23), Suicide (-0.39), Childhood (-0.16), UnintentionalInjury (-0.11), and several smaller effects.

- **Gap-widening indicators** (positive changes): The sum of all indicators that would increase the life expectancy gap is approximately **+0.37 years**. These include Diabetes (+0.21), Chronic Respiratory disease (+0.15), and Cardiovascular disease (+0.004).

The net effect of closing all gaps to their best attainable levels would be a reduction of approximately **1.56 years** in the predicted life expectancy gap (the difference between the gap-closing total and the gap-widening total). This represents a substantial portion of the current gap, though the exact percentage depends on the country's current gap value.

This analysis is based on conservative assumptions about what's attainable. The fact that multiple countries have achieved smaller gaps in various indicators provides evidence that these reductions are feasible.

### Healthy Life Expectancy (HALE) Gap

We fit the same three regularized regression models (Ridge, Lasso, and Elastic Net) to predict the HALE gender gap using cause-specific mortality indicators. All models use 5-fold cross-validation for model selection and evaluation.

#### Model Performance

The following table compares the three models using cross-validation R² and mean absolute error:

```{include} tables/model_comparison_hale.html
```

Elastic Net performs best with a cross-validation R² of 0.730, meaning it explains about 73% of the variance in the HALE gap across OECD countries. The mean absolute error is 0.510 years, indicating that on average, the model's predictions are off by about 6 months.

Elastic Net selects 19 out of 25 predictors as having non-zero coefficients, effectively performing feature selection while maintaining good predictive performance. The following table shows how many predictors each model uses:

```{include} tables/feature_selection_summary_hale.html
```

#### Feature Importance

To understand which factors contribute most to the HALE gap, we calculate feature importance as the absolute value of the coefficient multiplied by the standard deviation of the predictor. This measures each predictor's contribution to gap variation on the original scale.

The following figure shows all predictors with non-zero coefficients by importance:

```{figure} figs/predictor_importance_hale.png
---
width: 600px
alt: Predictors by importance for HALE gap
---
Predictors by importance. The Neoplasms overall rate (Mid_Neoplasms) dominates, with an importance of 21.9, followed by the Alcohol gap (Gap_Alcohol) with an importance of 17.5.
```

Unlike the Life Expectancy model, where the Alcohol gap dominates, the HALE model shows that the overall Neoplasms rate (Mid_Neoplasms) is the most important predictor, with an importance of 21.9. The Alcohol gap (Gap_Alcohol) is the second most important, with an importance of 17.5.

#### Indicator-Level Importance

When we aggregate importance by indicator (combining Mid and Gap predictors), we can see which health indicators matter most overall:

```{include} tables/indicator_importance_hale.html
```

The following figure visualizes indicator-level importance:

```{figure} figs/indicator_importance_hale.png
---
width: 600px
alt: Indicator importance for HALE gap
---
Indicator-level importance, showing which health indicators contribute most to explaining the HALE gender gap.
```

The top three indicators are:

1. **Neoplasms** (total importance: 30.8) — Cancer is the dominant factor for HALE, with contributions from both the overall rate (21.9) and the gender gap (8.9). This is different from Life Expectancy, where Neoplasms was second and came entirely from the gap component. Some part of the neoplasms gap is due to past smoking patterns, as men historically smoked more than women. As smoking rates continue to decline, this gap will likely shrink without further intervention, though efforts to reduce smoking should continue.

2. **Alcohol** (total importance: 18.7) — The gender gap in alcohol-attributable deaths is the second most important factor, coming almost entirely from the gap component (17.5), with a small contribution from the overall rate (1.2).

3. **Chronic Respiratory disease** (total importance: 7.0) — Chronic respiratory disease contributes substantially, with contributions from both the overall rate (4.9) and the gender gap (2.2). Like neoplasms, some part of the Chronic Respiratory disease gap is due to past smoking patterns, so it will likely shrink as smoking rates continue to decline, though efforts to reduce smoking should continue.

The remaining indicators have much smaller importance values, with Unintentional Injury (4.4), Homicide (2.2), and Suicide (2.0) being the next most important.

#### Model Diagnostics

The model shows good fit with no obvious systematic patterns in the residuals. The following figure shows residuals plotted against predicted values:

```{figure} figs/residuals_vs_predicted_hale.png
---
width: 600px
alt: Residuals vs predicted values for HALE
---
Residuals plotted against predicted HALE gap values. The points are scattered around zero with no obvious patterns, suggesting the model captures the relationship well.
```

The following table shows country-level predictions and residuals:

```{include} tables/residuals_by_country_hale.html
```

#### Comparison with Ordinary Least Squares

For comparison, we also fit an ordinary least squares (OLS) model using only the 19 predictors selected by Elastic Net. The following table compares performance:

```{include} tables/performance_comparison_hale.html
```

Both models perform similarly, with OLS achieving a slightly higher R² (0.976 vs 0.958) and lower MAE (0.201 vs 0.283 years) on the training data. However, the cross-validation R² of 0.730 for Elastic Net is a better estimate of out-of-sample performance. The difference between in-sample and cross-validation R² indicates some overfitting, which is expected with a small sample size (38 countries) and many predictors.

#### Key Findings

The analysis reveals that cancer (neoplasms) is the primary driver of the HALE gender gap in OECD countries, with the overall cancer rate being the most important predictor. This is different from Life Expectancy, where alcohol was the dominant factor. The gender gap in alcohol-related mortality is the second most important factor for HALE, similar to its role in Life Expectancy.

The fact that the overall Neoplasms rate dominates the HALE model suggests that countries with higher overall cancer rates tend to have larger HALE gaps, regardless of gender differences in cancer mortality. This may reflect the impact of cancer on both mortality and morbidity, which affects HALE more directly than Life Expectancy.

These findings suggest that policies and interventions targeting cancer prevention and treatment, as well as alcohol-related mortality, could have the largest impact on reducing the HALE gender gap.

#### Counterfactual Analysis

To understand what it would take to close the HALE gender gap, we perform the same counterfactual analysis as for Life Expectancy.

##### Methodology

The methodology is identical to that used for Life Expectancy: for each gap predictor, we identify the best attainable value observed across OECD countries and adjust male or female values accordingly to achieve that target gap.

##### Results for the United States

The following table shows counterfactual results for the United States, sorted by importance:

```{include} tables/counterfactuals_usa_hale.html
```

The results show that reducing the Alcohol gap from 38.8 to 9.9 (the level achieved in Türkiye) would reduce the predicted HALE gap by 0.86 years, the largest single impact. Reducing the Suicide gap from 14.9 to 4.0 (the level achieved in Türkiye) would reduce the gap by 0.79 years. Reducing the Neoplasms gap to zero would reduce the gap by 0.22 years.

Several indicators show negative changes (gap-closing effects), while a few show positive changes (gap-widening effects). The positive changes occur when reducing a gap predictor would actually increase the HALE gap, which can happen when the relationship between predictors and the outcome is complex due to correlations among indicators.

##### Aggregate Effects

When we sum the effects across all indicators, we can see the total potential impact:

- **Gap-closing indicators** (negative changes): The sum of all indicators that would reduce the HALE gap is approximately **-2.44 years**. These include Suicide (-0.79), Alcohol (-0.86), Neoplasms (-0.22), Childhood (-0.20), RoadTraffic (-0.20), Homicide (-0.10), and several smaller effects.

- **Gap-widening indicators** (positive changes): The sum of all indicators that would increase the HALE gap is approximately **+0.32 years**. These include Chronic Respiratory disease (+0.17), Diabetes (+0.12), and UnintentionalInjury (+0.03).

The net effect of closing all gaps to their best attainable levels would be a reduction of approximately **2.12 years** in the predicted HALE gap (the difference between the gap-closing total and the gap-widening total). This represents a substantial portion of the current gap, though the exact percentage depends on the country's current gap value.

This analysis is based on conservative assumptions about what's attainable. The fact that multiple countries have achieved smaller gaps in various indicators provides evidence that these reductions are feasible.

## Comparison of Life Expectancy and HALE Results

The models for Life Expectancy and HALE show both similarities and important differences in which factors drive the gender gaps.

### Model Performance

The Life Expectancy model performs slightly better than the HALE model:
- **Life Expectancy**: Cross-validation R² of 0.851, MAE of 0.375 years
- **HALE**: Cross-validation R² of 0.730, MAE of 0.510 years

The lower performance for HALE may reflect the additional complexity of modeling healthy years, which depends on both mortality and morbidity patterns, whereas Life Expectancy depends primarily on mortality.

### Feature Selection

Both models select a similar number of predictors:
- **Life Expectancy**: 17 out of 25 predictors (68%)
- **HALE**: 19 out of 25 predictors (76%)

The HALE model uses slightly more predictors, suggesting that more factors are relevant for explaining healthy life expectancy than overall life expectancy.

### Indicator Importance

The most striking difference is in the relative importance of indicators:

**Life Expectancy:**
1. Alcohol (19.1) — dominated by the gap component
2. Neoplasms (12.1) — entirely from the gap component
3. Cardiovascular disease (10.4) — entirely from the overall rate

**HALE:**
1. Neoplasms (30.8) — dominated by the overall rate (21.9), with gap component (8.9)
2. Alcohol (18.7) — almost entirely from the gap component (17.5)
3. Chronic Respiratory disease (7.0) — from both overall rate and gap

The key differences are:

1. **Neoplasms**: For Life Expectancy, the Neoplasms gap is the second most important factor, but for HALE, the overall Neoplasms rate is the most important factor. This suggests that overall cancer rates affect healthy years more than they affect total years, possibly because cancer affects both mortality and morbidity (quality of life).

2. **Alcohol**: Alcohol remains highly important in both models, but it's the dominant factor for Life Expectancy and the second most important for HALE. The Alcohol gap component is similar in both models (around 17-19), but it's relatively more important for Life Expectancy.

3. **Cardiovascular disease**: Cardiovascular disease is the third most important factor for Life Expectancy (10.4, from overall rate), but it has zero importance for HALE. This suggests that cardiovascular mortality affects total years lived but may not affect healthy years as much, possibly because cardiovascular deaths often occur at older ages after periods of morbidity. Note that cardiovascular disease rates are often higher for women than men because cardiovascular risk increases with age, and women are more likely to live long enough to develop cardiovascular disease.

4. **Chronic Respiratory disease**: Chronic respiratory disease is more important for HALE (7.0) than for Life Expectancy (5.0), reflecting its impact on both mortality and morbidity.

### Counterfactual Analysis

The counterfactual analysis shows similar patterns but different magnitudes:

**Life Expectancy:**
- Gap-closing total: -1.93 years
- Gap-widening total: +0.37 years
- Net reduction: 1.56 years

**HALE:**
- Gap-closing total: -2.44 years
- Gap-widening total: +0.32 years
- Net reduction: 2.12 years

The potential reduction is larger for HALE (2.12 years) than for Life Expectancy (1.56 years), suggesting that interventions targeting the identified factors could have a greater impact on healthy years than on total years. This makes sense if these interventions not only reduce mortality but also improve quality of life.

The largest single counterfactual effects differ:
- **Life Expectancy**: Alcohol gap reduction (-0.96 years)
- **HALE**: Alcohol gap reduction (-0.86 years), followed by Suicide gap reduction (-0.79 years)

### Implications

These differences suggest that:

1. **Cancer prevention and treatment** may be particularly important for improving healthy life expectancy, as the overall cancer rate is the dominant factor for HALE but less important for Life Expectancy.

2. **Alcohol-related interventions** are important for both outcomes, but relatively more important for total life expectancy than for healthy life expectancy.

3. **Cardiovascular disease** affects total years but may not significantly affect healthy years, possibly because cardiovascular deaths often occur after periods of morbidity.

4. **Chronic respiratory disease** has a greater impact on healthy years than on total years, reflecting its effects on quality of life.

Overall, the models suggest that different interventions may be needed to maximize total life expectancy versus healthy life expectancy, though many interventions (particularly those targeting alcohol and cancer) benefit both outcomes.