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
- Alcohol is strongly correlated with Cardiovascular (ρ ≈ 0.83) and Poisoning (ρ ≈ 0.75), and moderately with Suicide (ρ ≈ 0.55).
- Cardiovascular is also correlated with Poisoning (ρ ≈ 0.66).
- UnintentionalInjury is correlated with Cardiovascular (ρ ≈ 0.54) and Suicide (ρ ≈ 0.49), and negatively with Childhood (ρ ≈ −0.50).

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

We fit three regularized regression models (Ridge, Lasso, and Elastic Net) to predict the Life Expectancy gender gap using cause-specific mortality indicators. All models use 5-fold cross-validation for model selection and evaluation.

### Model Performance

The following table compares the three models using cross-validation R² and mean absolute error:

```{include} tables/model_comparison.html
```

Elastic Net performs best with a cross-validation R² of 0.851, meaning it explains about 85% of the variance in the life expectancy gap across OECD countries. The mean absolute error is 0.375 years, indicating that on average, the model's predictions are off by about 4.5 months.

Elastic Net selects 17 out of 25 predictors as having non-zero coefficients, effectively performing feature selection while maintaining good predictive performance. The following table shows how many predictors each model uses:

```{include} tables/feature_selection_summary.html
```

### Feature Importance

To understand which factors contribute most to the life expectancy gap, we calculate feature importance as the absolute value of the coefficient multiplied by the standard deviation of the predictor. This measures each predictor's contribution to gap variation on the original scale.

The following figure shows the top 15 predictors by importance:

```{figure} figs/predictor_importance.png
---
width: 600px
alt: Top 15 predictors by importance for Life Expectancy gap
---
Top 15 predictors by importance. The Alcohol gap (Gap_Alcohol) dominates, with an importance of 19.1, far exceeding all other predictors.
```

The Alcohol gap is by far the most important predictor, with an importance of 19.1. This means that differences in alcohol-attributable death rates between men and women are the strongest driver of the life expectancy gender gap across OECD countries.

### Indicator-Level Importance

When we aggregate importance by indicator (combining Mid and Gap predictors), we can see which health indicators matter most overall:

```{include} tables/indicator_importance.html
```

The following figure visualizes indicator-level importance:

```{figure} figs/indicator_importance.png
---
width: 600px
alt: Indicator importance for Life Expectancy gap
---
Indicator-level importance, showing which health indicators contribute most to explaining the life expectancy gender gap.
```

The top three indicators are:

1. **Alcohol** (total importance: 19.1) — The gender gap in alcohol-attributable deaths is the dominant factor. This comes entirely from the gap component, not the overall rate.

2. **Neoplasms** (total importance: 12.1) — The gender gap in cancer death rates is the second most important factor, also coming entirely from the gap component.

3. **Cardiovascular** (total importance: 10.4) — Cardiovascular disease contributes substantially, but this comes from the overall rate (Mid), not the gender gap. This suggests that countries with higher overall cardiovascular death rates tend to have larger life expectancy gaps, regardless of the gender difference in cardiovascular mortality.

The remaining indicators have much smaller importance values, with Chronic Respiratory (5.0), Unintentional Injury (3.4), and Suicide (0.9) being the next most important.

### Model Diagnostics

The model shows good fit with no obvious systematic patterns in the residuals. The following figure shows residuals plotted against predicted values:

```{figure} figs/residuals_vs_predicted.png
---
width: 600px
alt: Residuals vs predicted values
---
Residuals plotted against predicted life expectancy gap values. The points are scattered around zero with no obvious patterns, suggesting the model captures the relationship well.
```

The distribution of residuals is approximately normal:

```{figure} figs/residuals_distribution.png
---
width: 600px
alt: Distribution of residuals
---
Histogram of residuals showing an approximately normal distribution centered at zero.
```

The following table shows country-level predictions and residuals:

```{include} tables/residuals_by_country.html
```

### Comparison with Ordinary Least Squares

For comparison, we also fit an ordinary least squares (OLS) model using only the 17 predictors selected by Elastic Net. The following table compares performance:

```{include} tables/performance_comparison.html
```

Both models perform similarly, with OLS achieving a slightly higher R² (0.977 vs 0.974) and lower MAE (0.199 vs 0.219 years) on the training data. However, the cross-validation R² of 0.851 for Elastic Net is a better estimate of out-of-sample performance. The difference between in-sample and cross-validation R² indicates some overfitting, which is expected with a small sample size (38 countries) and many predictors.

The following figure compares predictions from both models:

```{figure} figs/predictions_comparison.png
---
width: 600px
alt: Elastic Net vs OLS predictions
---
Comparison of predictions from Elastic Net and OLS models. The left panel shows that predictions are highly correlated, and the right panel shows the distribution of differences.
```

### Key Findings

The analysis reveals that alcohol-attributable deaths are the primary driver of the life expectancy gender gap in OECD countries. The gender gap in alcohol-related mortality (where men have higher rates than women) accounts for more than half of the total importance across all indicators.

Cancer (neoplasms) is the second most important factor, also driven by the gender gap rather than overall rates. Cardiovascular disease contributes substantially, but through overall rates rather than gender differences.

These findings suggest that policies and interventions targeting alcohol-related mortality, particularly among men, could have the largest impact on reducing the life expectancy gender gap. The fact that the Alcohol gap dominates the model, and that it comes entirely from the gap component (not the overall rate), indicates that gender differences in alcohol consumption and related mortality are central to understanding why women live longer than men in most countries.