# Gender Gaps in Life Expectancy

## Introduction

In most countries, women live longer than men. This difference is often assumed to be natural and inevitable -- and sometimes desirable. For example, in the World Economic Forum's Global Gender Gap Report, a smaller gap is interpreted as evidence of discrimination against women.

But the gap varies substantially between countries and has changed over time, which suggests that it might not be entirely natural, or if it is, it can be mitigated. For example, in the Netherlands the gap in healthy life expectancy is now close to zero.

The goal of this investigation is to explore differences in life expectancy and health-adjusted life expectancy (HALE) between countries, to identify the factors that contribute to the observed gender gaps, and to estimated the changes needed to close those gaps by improving health outcomes for both men and women.

We use Elastic Net regression to model the gender gap in life expectancy and HALE as a function of cause-specific mortality indicators. This approach handles the high correlation among predictors and identifies patterns of mortality most strongly associated with the life expectancy gap. 

## Data

The analysis uses data from two sources:

1. WHO Global Health Observatory (GHO) API: Provides HALE and life expectancy. Data is accessed programmatically via the GHO OData API.

2. IHME Global Burden of Disease: Provides most cause-specific mortality indicators with better temporal coverage than WHO, including cardiovascular disease, diabetes, chronic respiratory disease, neoplasms (cancer), alcohol use disorders, self-harm (suicide), interpersonal violence (homicide), road injuries, unintentional injuries, liver disease, and drug use disorders.

For each indicator, we use the most recent available data from 2000-2019. We exclude 2020 and later years to avoid distortions from the COVID-19 pandemic, which had significant impacts on mortality patterns that may not reflect underlying health factors. Using 2019 or earlier data provides a more stable baseline for understanding the gender gap.

The analysis focuses on OECD countries (38 countries) to ensure consistent data quality and comparability. For each country, we compute gender gaps by taking the difference between female and male values for each indicator.

Early-life mortality indicators (infant and under-five mortality) were considered but excluded from the final model because they had very low importance and limited temporal coverage. The IHME alternative (all-cause deaths under 5, per 100,000 population) was also considered but excluded because it is confounded with age structure and fertility rates, making it methodologically inappropriate for cross-country comparison.

## Target Variables

The analysis focuses on two target variables:

- HALE Gap: The difference in Healthy Life Expectancy between women and men (Female - Male, in years)
- Life Expectancy Gap: The difference in Life Expectancy between women and men (Female - Male, in years)

The following table shows the median, minimum, and maximum values for HALE and Life Expectancy across OECD countries.

```{include} tables/target_rates.html
```


The following table shows the median, minimum, and maximum gender gaps (Female - Male) for HALE and Life Expectancy across OECD countries.

```{include} tables/target_gaps.html
```

The following table shows the HALE and Life Expectancy gaps for all OECD countries, sorted by HALE gap:

```{include} tables/gap_comparison_by_country.html
```

In several countries, mostly in Northern Europe, the HALE gap is effectively zero, and the gap in life expectancy is three years or less.
These countries are evidence that there is nothing inevitable about these gaps, and no unavoidable reason for gaps as high as 5 years in the United States or 9 years in Latvia and Lithuania.

## Predictors

The following tables summarize the predictors used to explain variation in the HALE and Life Expectancy gender gaps. Each predictor includes:

- Median Rate: The median across countries of the overall rate (computed as the average of male and female rates)
- Min Rate / Max Rate: The range of overall rates across countries
- Median Gap: The median gender gap (Male - Female for predictors) across countries
- Min Gap / Max Gap: The range of gender gaps across countries
- Corr HALE: Correlation with HALE gap
- Corr LE: Correlation with Life Expectancy gap


For each predictor, the following table shows **overall rates** in deaths per 100,000 people (computed as the average of male and female rates).

```{include} tables/predictor_rates.html
```

The highest death rates are from cancer (neoplasms) and cardiovascular disease, followed by chronic respiratory disease.
Death rates due to alcohol use disorders are much smaller than the highest rates, but as we'll see, cancer-related deaths and other factors are the primary contributors to gender gaps in life expectancy.

Several predictors are strongly correlated with life expectancy gaps, notably Neoplasms and Unintentional Injury.
Most of the correlations are positive, indicating that countries with higher death rates also have larger gender gaps.


The following table shows **gender gaps** (Male - Female) in death rates for each predictor.

```{include} tables/predictor_gaps.html
```

Many of the death rates gaps are strongly correlated with life expectancy gaps, which is not surprising -- in a country where more men suffer from alcohol-related disease, for example, we expect a larger gap in both HALE and life expectancy.

### Correlations

Many of these predictors are also related to each other.
The following table shows the top correlations between the overall rates of different indicators.

```{include} tables/rate_rate_correlation_top10.html
```

The following table shows the top correlations between the gender gaps of different indicators.

```{include} tables/gap_gap_correlation_top10.html
```

The following table shows the correlation between the overall rate and the gender gap for each predictor. This identifies indicators where countries with higher overall rates also tend to have larger gender gaps.

```{include} tables/rate_gap_correlation.html
```

So there are clusters of indicators that move together, both in their overall rates and in their gender gaps.

## Methodology

If we put all of these predictors into a single ordinary least squares (OLS) regression, the model is forced to divide the explanatory “credit” among highly correlated variables. In that setting:

- Small amounts of noise can change which variable gets the larger coefficient.
- Coefficients within a correlated cluster can flip sign or change magnitude dramatically.
- The allocation of effect size among correlated predictors is essentially arbitrary.

As a result, an OLS model with all indicators included does not give a stable or interpretable answer to the question “which factors matter most?”.

Elastic Net regression can help. It combines two kinds of regularization:

- An L2 (ridge) component that stabilizes coefficients and allows correlated predictors to share weight.
- An L1 (lasso) component that shrinks some coefficients all the way to zero when they do not improve predictive performance.

The model is tuned by cross-validation, so the amount of regularization is chosen to maximize out-of-sample predictive accuracy, not to fit the particular noise pattern in the dataset.

In practice, this means:

- Correlated predictors are handled coherently, with coefficients shrunk toward each other and toward zero.
- Predictors that do not add predictive information beyond the ones already in the model are often assigned coefficients very close to zero.
- The remaining non-zero coefficients identify a smaller set of predictors that are genuinely helpful for predicting the life expectancy gap.

That does not mean that every non-zero coefficient in the regression can be interpreted as a causal effect. But it does mean:

* Predictors with a stronger direct influence on sex-specific mortality should generally be more predictive of the life expectancy gap.

* Predictors that are only loosely or indirectly associated with these mortality differences should contribute less to out-of-sample prediction.

So when Elastic Net assigns substantial weight to a predictor like Alcohol or Neoplasms, we can take that as evidence that these factors are causative, which suggests that efforts to close gaps in these death rates would also close gaps in life expectancy.


## Results


### Life expectancy gap

We fit three regularized regression models (Ridge, Lasso, and Elastic Net) to predict the Life Expectancy gender gap as a function of cause-specific death rates and gender gaps in those rates. All models use 5-fold cross-validation for model selection and evaluation.

The following table compares the three models using cross-validation R² and mean absolute error:

```{include} tables/model_comparison_le.html
```

Elastic Net performs best with a cross-validation R² of 0.879, meaning it explains about 88% of the variance in the life expectancy gap across OECD countries. The mean absolute error is 0.326 years, indicating that on average, the model's predictions are off by about 4 months.

Elastic Net selects 13 out of 23 predictors as having non-zero coefficients, effectively performing feature selection while maintaining good predictive performance. The following table shows how many predictors each model uses:

```{include} tables/feature_selection_summary_le.html
```


To understand which factors contribute most to the life expectancy gap, we calculate feature importance as the absolute value of the coefficient multiplied by the standard deviation of the predictor. This measures each predictor's contribution to gap variation on the original scale.

The following figure shows all predictors with non-zero coefficients by importance:

```{figure} figs/predictor_importance_le.png
---
width: 600px
alt: Predictors by importance for Life Expectancy gap
---
Predictors by importance.
```

The Neoplasms gap is the most important predictor, with an importance of 11.4. This means that differences in cancer death rates between men and women are the strongest driver of the life expectancy gender gap across OECD countries.

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

The top indicators are:

1. **Neoplasms** (total importance: 11.4) — Cancer death rates are the dominant factor, with importance coming entirely from the gap component, not the overall rate. Some part of this gap is due to past smoking patterns, as men historically smoked more than women. As smoking rates continue to decline, this gap will likely shrink without further intervention, though efforts to reduce smoking should continue.

2. **Unintentional Injury** (total importance: 5.11) — Unintentional injuries are the second most important factor, with importance coming entirely from the gap component. These injuries often show gender differences due to occupational exposures, risk-taking behaviors, and activity patterns.

3. **Chronic Respiratory disease** (total importance: 2.22) — Chronic respiratory disease contributes moderately, with contributions from both the overall rate and the gender gap. Like neoplasms, some part of the Chronic Respiratory disease gap is due to past smoking patterns, so it will likely shrink as smoking rates continue to decline.

4. **Liver Disease** (total importance: 2.08) — Liver disease death rates contribute moderately, with importance coming mostly from the gap component. Liver disease is often related to alcohol consumption, but also includes non-alcoholic causes such as viral hepatitis and non-alcoholic fatty liver disease.

5. **Homicide** (total importance: 1.84) — Homicide contributes moderately, with contributions from both the overall rate and the gender gap. Homicide rates are typically much higher in men than women across most countries. Homicide gained substantial importance after removing the childhood mortality indicator, suggesting it may have been capturing some shared variance.

6. **Suicide** (total importance: 1.82) — Suicide rates contribute moderately, with importance coming entirely from the gap component. Suicide rates are typically much higher in men than women across most countries.

7. **Alcohol** (total importance: 1.53) — Alcohol use disorder death rates contribute moderately, with importance coming mostly from the gap component. The importance is lower than in previous analyses because the current model uses IHME data, which defines alcohol-related mortality more narrowly than WHO's broader "alcohol-attributable" definition.

Cardiovascular disease has zero importance in this model, meaning it was not selected by Elastic Net as a predictive factor for the life expectancy gap.


#### Residuals

The following table shows country-level predictions and residuals:

```{include} tables/residuals_by_country_le.html
```

The model shows good fit with residuals distributed around zero across countries.

The model shows good fit with no obvious systematic patterns in the residuals. The following figure shows residuals plotted against predicted values:

```{figure} figs/residuals_vs_predicted_le.png
---
width: 600px
alt: Residuals vs predicted values
---
Residuals plotted against predicted life expectancy gap values.
```

The points are scattered around zero with no obvious patterns, suggesting the model captures the relationship well.


#### Comparison with Ordinary Least Squares

For comparison, we also fit an ordinary least squares (OLS) model using only the 17 predictors selected by Elastic Net. The following table compares performance:

```{include} tables/performance_comparison_le.html
```

Both models perform similarly, with OLS achieving a slightly higher R² and lower MAE on the training data. However, the cross-validation R² of 0.872 for Elastic Net is a better estimate of out-of-sample performance. The difference between in-sample and cross-validation R² indicates some overfitting, which is expected with a small sample size (38 countries) and many predictors.



#### Counterfactual Analysis

To understand what it would take to close the life expectancy gender gap, we perform a counterfactual analysis that asks: "What would happen to a country's predicted life expectancy gap if we adjusted each gap predictor to the best attainable value?"

For each gap predictor, we identify the best attainable value by comparing the current gap to observed gaps in other countries:

- If the current gap is positive (Male > Female), we find the country with the smallest gap (most negative).
- If the current gap is negative (Female > Male), we find the country with the largest gap (most positive).

If the target gap has the opposite sign of the current gap, we infer that it is possible for the gap to be zero, so we set the target to zero.

To achieve the target gap, we adjust the underlying male or female values:

- If the gap is positive (Male > Female), we bring men toward women's level by reducing the male rate.
- If the gap is negative (Female > Male), we bring women toward men's level by reducing the female rate.

After adjusting the male and female values, we recompute the Mid and Gap values, then use the model to generate a counterfactual prediction. The difference between the original and counterfactual predictions shows how much the life expectancy gap would change if that predictor gap were reduced to the best attainable level (assuming that the relationship is causative).

This approach is conservative in two ways:

1. We only adjust gap variables, not overall rates, because we're more confident that gap variables have a causal relationship with the life expectancy gap.

2. We use other countries as evidence of what's attainable. If no country has closed or reversed the gap, we assume that the lowest observed gap is the lowest attainable.

The following table shows counterfactual results for the United States.

```{include} tables/counterfactuals_usa_le.html
```

The table is sorted by importance, which indicates in general how effective it is to reduce a particular gap. The counterfactual results (the "Change in LE gap" column) indicate how much reducing that gap would specifically affect the life expectancy gap in the United States, which depends on how far the United States is from the target gap for that indicator.

The results show that reducing the Suicide gap from 17.3 to 4.51 (the level observed in Türkiye) would reduce the predicted life expectancy gap by 0.548 years, the largest single impact. Reducing the Unintentional Injury gap to zero would reduce the LE gap by an additional 0.311 years. Reducing the Alcohol gap from 5.54 to 0.306 (the level observed in Colombia) would reduce the gap by 0.251 years. Reducing the Neoplasms gap to zero would reduce the gap by 0.214 years.

Most indicators show negative changes (gap-closing effects), but a few show positive changes (gap-widening effects). The positive changes occur when reducing a gap predictor would increase the life expectancy gap, which can happen when the relationship between predictors and the outcome is complex due to correlations among indicators.

When we sum the effects across all indicators, we can see the total potential impact:

- **Gap-closing indicators** (negative changes): The sum of all indicators that would reduce the life expectancy gap includes Suicide (-0.548), Unintentional Injury (-0.311), Alcohol (-0.251), Neoplasms (-0.214), Liver Disease (-0.198), Homicide (-0.083), and Road Traffic (-0.12).

- **Gap-widening indicators** (positive changes): The sum of all indicators that would increase the life expectancy gap includes Diabetes (+0.427) and Chronic Respiratory disease (+0.053).

The net effect of closing all gaps to their target levels would be a reduction in the predicted life expectancy gap. This represents a substantial part of the current gap.


### Healthy Life Expectancy (HALE) Gap

We fit the same three regularized regression models (Ridge, Lasso, and Elastic Net) to predict the HALE gender gap.
The following table compares the three models using cross-validation R² and mean absolute error:

```{include} tables/model_comparison_hale.html
```

Elastic Net performs best with a cross-validation R² of 0.778, meaning it explains about 78% of the variance in the HALE gap across OECD countries. The mean absolute error is 0.422 years, indicating that on average, the model's predictions are off by about 5 months.

The following table shows how many predictors each model uses:

```{include} tables/feature_selection_summary_hale.html
```
Elastic Net selects 20 out of 23 predictors as having non-zero coefficients.
The following figure shows all predictors with non-zero coefficients by importance:

```{figure} figs/predictor_importance_hale.png
---
width: 600px
alt: Predictors by importance for HALE gap
---
Predictors by importance.
```

The Neoplasms gap is the most important predictor, with an importance of 12.1. The Neoplasms overall rate is next, with an importance of 11.7.

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

The top indicators are:

1. **Neoplasms** (total importance: 28.2) — Cancer is the dominant factor for HALE, with contributions from both the overall rate and the gender gap. Some part of the neoplasms gap is due to past smoking patterns, as men historically smoked more than women. Neoplasms gained importance after removing the childhood mortality indicator, suggesting it better captures its relationship with the HALE gap without that indicator.

2. **Cardiovascular disease** (total importance: 5.55) — Cardiovascular disease is the second most important factor, with contributions from both the overall rate and the gender gap. In many countries, cardiovascular disease rates are higher for women because cardiovascular risk increases with age, and women are more likely to live long enough to develop cardiovascular disease. Cardiovascular importance decreased after removing childhood mortality, suggesting some interaction between these indicators.

3. **Unintentional Injury** (total importance: 5.69) — Unintentional injuries contribute substantially, with contributions from both the overall rate and the gender gap. These injuries often show gender differences due to occupational exposures, risk-taking behaviors, and activity patterns.

4. **Chronic Respiratory disease** (total importance: 5.22) — Chronic respiratory disease contributes substantially, with contributions from both the overall rate and the gender gap. Like neoplasms, some part of the Chronic Respiratory disease gap is due to past smoking patterns.

5. **Homicide** (total importance: 3.92) — Homicide contributes moderately, with contributions from both the overall rate and the gender gap. Homicide rates are typically much higher in men than women across most countries. Homicide gained substantial importance after removing the childhood mortality indicator, suggesting it may have been capturing some shared variance.

6. **Suicide** (total importance: 2.96) — Suicide contributes moderately, with contributions from both the overall rate and the gender gap. Suicide rates are typically much higher in men than women across most countries.

7. **Liver Disease** (total importance: 2.52) — Liver disease death rates contribute moderately, with contributions from both the overall rate and the gender gap. Liver disease is often related to alcohol consumption, but also includes non-alcoholic causes.

8. **Alcohol** (total importance: 1.73) — Alcohol use disorder death rates contribute moderately, with importance coming mostly from the gap component. The importance is lower than in previous analyses because the current model uses IHME data, which defines alcohol-related mortality more narrowly than WHO's broader "alcohol-attributable" definition.

9. **Diabetes** (total importance: 1.69) — Diabetes contributes moderately, with contributions from both the overall rate and the gender gap. Diabetes gained importance after removing the childhood mortality indicator.

#### Residual


The following table shows country-level predictions and residuals:

```{include} tables/residuals_by_country_hale.html
```

The following figure shows residuals plotted against predicted values:

```{figure} figs/residuals_vs_predicted_hale.png
---
width: 600px
alt: Residuals vs predicted values for HALE
---
Residuals plotted against predicted HALE gap values.
```

The model shows good fit with no obvious systematic patterns in the residuals. 

#### Comparison with Ordinary Least Squares

For comparison, we also fit an ordinary least squares (OLS) model using only the 19 predictors selected by Elastic Net. The following table compares performance:

```{include} tables/performance_comparison_hale.html
```

Both models perform similarly, with OLS achieving a slightly higher R² and lower MAE on the training data. However, the cross-validation R² of 0.78 for Elastic Net is a better estimate of out-of-sample performance and predictive validity.


#### Counterfactual Analysis

The methodology here is the same as for Life Expectancy.

The following table shows counterfactual results for the United States.

```{include} tables/counterfactuals_usa_hale.html
```

The table is sorted by importance, which indicates in general how effective it is to reduce a particular gap. The counterfactual results (the "Change in HALE gap" column) indicate how much reducing that gap would specifically affect the HALE gap in the United States, which depends on how far the United States is from the target gap for that indicator.

The results show that reducing the Suicide gap from 17.3 to 4.51 (the level observed in Türkiye) would reduce the predicted HALE gap by 0.76 years, the largest single impact. Reducing the Neoplasms gap to zero would reduce the HALE gap by an additional 0.256 years. Reducing the Alcohol gap from 5.54 to 0.306 (the level observed in Colombia) would reduce the gap by 0.272 years. Reducing the Homicide gap to zero would reduce the gap by 0.218 years.

Most indicators show negative changes (gap-closing effects), but a few show positive changes (gap-widening effects). The positive changes occur when reducing a gap predictor would increase the HALE gap, which can happen when the relationship between predictors and the outcome is complex due to correlations among indicators.

When we sum the effects across all indicators, we can see the total potential impact:

- **Gap-closing indicators** (negative changes): The sum of all indicators that would reduce the HALE gap includes Suicide (-0.76), Neoplasms (-0.256), Alcohol (-0.272), Homicide (-0.218), Liver Disease (-0.189), Road Traffic (-0.167), Drug Disorder (-0.142), and Unintentional Injury (-0.082).

- **Gap-widening indicators** (positive changes): The sum of all indicators that would increase the HALE gap includes Diabetes (+0.341) and Chronic Respiratory disease (+0.082).

The net effect of closing all gaps to their target levels would be a reduction in the predicted HALE gap. This represents a substantial part of the current gap.


## Comparison of Life Expectancy and HALE Results

The Life Expectancy model performs better than the HALE model:

- **Life Expectancy**: Cross-validation R² of 0.879, MAE of 0.326 years

- **HALE**: Cross-validation R² of 0.778, MAE of 0.422 years

The lower performance for HALE may reflect the additional complexity of modeling healthy years, which depends on both mortality and morbidity patterns, whereas Life Expectancy depends entirely on mortality.

Both models select a similar number of predictors:

- **Life Expectancy**: 13 out of 23 predictors (57%)
- **HALE**: 20 out of 23 predictors (87%)

The HALE model uses more predictors, suggesting that more factors are relevant for explaining healthy life expectancy than overall life expectancy.

The relative importance of indicators differs between the two models:

**Life Expectancy:**
1. Neoplasms (11.4) — entirely from the gap component
2. Unintentional Injury (4.93) — entirely from the gap component
3. Chronic Respiratory disease (2.22) — from both overall rate and gap
4. Liver Disease (2.08) — mostly from the gap component
5. Homicide (1.84) — from both overall rate and gap
6. Suicide (1.82) — entirely from the gap component
7. Alcohol (1.53) — mostly from the gap component

**HALE:**
1. Neoplasms (28.2) — from both overall rate and gap
2. Cardiovascular disease (5.55) — from both overall rate and gap
3. Unintentional Injury (5.69) — from both overall rate and gap
4. Chronic Respiratory disease (5.22) — from both overall rate and gap
5. Homicide (3.92) — from both overall rate and gap
6. Suicide (2.96) — from both overall rate and gap
7. Liver Disease (2.52) — from both overall rate and gap
8. Alcohol (1.73) — mostly from the gap component
9. Diabetes (1.69) — from both overall rate and gap

Neoplasms (cancer) is the most important factor in both models, but its relative importance is much higher for HALE. Cardiovascular disease is important for HALE but was not selected for Life Expectancy. Alcohol has lower importance in both models than in previous analyses, reflecting the use of IHME data which defines alcohol-related mortality more narrowly.

The counterfactual analysis shows that Suicide has the largest single impact in both models, followed by Neoplasms and Alcohol. The patterns are similar but the magnitudes differ between the two outcomes.



### Implications

These differences suggest that:

1. **Cancer prevention and treatment** is the most important factor for both outcomes, but particularly critical for healthy life expectancy, as neoplasms have much higher importance for HALE (28.2) than for Life Expectancy (11.4).

2. **Cardiovascular disease** affects healthy years (importance 5.55 for HALE) but was not selected as a predictive factor for total life expectancy, suggesting it may have different relationships with mortality versus healthy years.

3. **Suicide prevention** has substantial importance in both models and shows the largest counterfactual impact, suggesting it is a critical intervention target.

4. **Unintentional injuries** are important for both outcomes, ranking second for Life Expectancy and third for HALE.

5. **Alcohol-related interventions** remain important but have lower importance than in previous analyses, reflecting the use of IHME data which defines alcohol-related mortality more narrowly than WHO's broader "alcohol-attributable" definition.

