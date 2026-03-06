# What Drives the Life Expectancy Gender Gap?

*This is Part 2 in a series on gender gaps in life expectancy, what causes them, and what we can do about it.*

---

In the [previous article](https://allendowney.substack.com/p/the-gender-gap-in-life-expectancy), we showed that the gender gap in life expectancy varies between countries and across time, from 2.5 years in Israel to 12.7 years in Lithuania.
As a first step toward understanding these differences, we looked death rates from several causes with large gender haps: drug disorders, homicide, suicide, and road traffic.
We find that gender gaps in these death rates are contingent -- that is, they are driven by history, economics, culture, and public policy.

Now we'll put the pieces together to see how changes in cause-specific death rates affect the life expectancy gap.

## The Approach

We built a Bayesian hierarchical panel model that uses both temporal and cross-country variation.
It includes 13 cause-specific mortality indicators from the [Global Burden of Disease (GBD)](https://www.healthdata.org/research-analysis/gbd) study: alcohol, suicide, homicide, road traffic injuries, cardiovascular disease, diabetes, cancer (neoplasms), chronic respiratory disease, liver disease, unintentional injury, drug disorders, childhood mortality (under-5), and COVID-19.

% TODO: in a section about variations of the model, mention the variables we considered and excluded

We chose these causes because we expect them to explain at least some part of the life expectancy gap.

The following figure shows gender gaps in death rates due to liver disease.

```{figure} figs/liver_disease_gap_timeseries_selected.png
:width: 80%

Drug use disorders, death rate gender gap  (2000–2023), OECD countries.
Source: Global Burden of Disease from IHME.
```

Between 2000 and 2015, the gender gap in Hungary decreased substantially.
At the same time, the gap in Estonia was increasing.
And we expect these changes in death rates to contribute directly to changes in life expectancy -- that is, a decreasing gap in liver disease should cause a smaller gap in life expectancy, and likewise with an increasing gap.

How much it contributes depends in part on the age of the people affected.
Conditions that affect younger people have a stronger effect on life expectancy.
It also depends on the magnitude of the gap relative to other causes of death.
For example, the OECD average gap for liver disease is about 12 per 100,000, which is larger than the gap for drug use disorders, about 3, and smaller than the gap for cancer, about 60.

## Results

More details about the model follow, but let's start with the results.

For each cause of death, the panel model estimates a coefficient (β) that shows how much the life expectancy gap changes for each one-standard-deviation increase in cause-specific gap.

Positive coefficients mean that when the cause-specific gap is larger (men die at higher rates than women), the life expectancy gap is larger (women live longer).

The following figure shows the estimated effect of each predictor on the gender gap in life expectancy.
The bars show posterior means; the error bars show 94% credible intervals.

```{figure} figs/blog2_coefficients_le.png
:width: 80%

Predictor coefficients for the life expectancy gender gap (2000–2023).
Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.
```

Road traffic deaths have the strongest effect, followed by homicide and suicide.
A one-standard-deviation increase in the road traffic gap is associated with about 0.6 additional years in the life expectancy gap.

External causes — injuries, violence, self-harm — collectively dominate.

All coefficients have credible intervals that exclude zero, which means they are unlikely to be the result of random sampling.

Two predictors have *negative* coefficients: cardiovascular disease and diabetes.
Explain...





## Importance

The coefficients in the previous section are expressed in years per standard deviation -- for example, if a country is average in every way except that it's one standard deviation above the mean in road traffic deaths, we expect its life expectancy gap to be 0.6 years above average.

The standard deviations of the death rate gaps summarize variability between countries and across time, which *might* indicate how amenable they are to change.
The following table shows coefficient (years per SD), standard deviation of the predictor (per 100,000), and importance for each cause.

```{include} ../notebooks/tables/importance_measures_le_ihme_nomid_nogrw_y2023_covid.html
```

Coefficients tell us the *effect size* — how much the gap changes per unit change in the predictor.
But *importance* — how much a factor matters in the real world — also depends on how much the predictor varies across countries and years.

We define importance as |coefficient| × standard deviation of the predictor.
The following figure shows importance for each cause.

```{figure} figs/blog2_importance_le.png
:width: 80%

Predictor importance for the life expectancy gender gap (2000–2023).
Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.
```

Cancer (neoplasms) has a moderate coefficient but the highest importance, because cancer gender gaps vary substantially across countries.
Road traffic has both a large coefficient *and* high variation, making it the top priority overall.
Cardiovascular disease has high importance despite its negative coefficient, reflecting its large variation and the competing-risk mechanism — countries with larger cardiovascular gaps have smaller life expectancy gaps, and vice versa.

## Model Fit

The model fits the data well.
The following figure shows predicted versus actual life expectancy gaps over time for four countries: Iceland, the United States, Lithuania, and France.
The colored lines show actual values; the gray vertical segments show the 94% credible interval for the model's predictions.

```{figure} figs/blog2_residuals_timeseries_le.png
:width: 80%

Predicted vs actual life expectancy gap (2000–2023), selected countries.
Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.
```

The model tracks the observed gaps closely, including the COVID period and the opioid-driven increase in the United States.

The following figure shows residuals by country — the difference between actual and predicted gaps — for all 37 countries.
Countries are sorted by the width of the residual distribution (IQR); the best-fitting countries are at the top.

```{figure} figs/blog2_residuals_by_country_le.png
:width: 80%

Model residuals by country (sorted by IQR, best fit at top).
Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.
```

Mean absolute error is approximately 0.19–0.22 years; residual standard deviation is approximately 0.26–0.29 years.

## Model Details

We use panel data from 2000–2023, providing 888 observations across 37 OECD countries and 24 years.

The model uses a Bayesian hierarchical structure with country random intercepts and shared slopes. Predictors are standardized (z-scores); the target (life expectancy gap) is centered.

**Turkey excluded**: Not in IHME HALE data; when included (OWID LE), identified as a statistical outlier. Final sample: 37 OECD countries.

**Gap predictors only**: We tested including overall mortality levels (midpoints) for each cause. These were highly correlated with the gaps (r ≈ -0.9 to -1.0 for many indicators), causing multicollinearity. Systematic tests of four midpoint predictors with lower correlations all worsened fit. The final model uses only gap predictors.

**Conflict and terrorism excluded**: We tested conflict and terrorism deaths as a predictor. In OECD countries, these rates are very low and the gender gap in this cause is tiny. The coefficient was essentially zero (94% credible interval spans zero), importance was negligible (ranked last), and model fit was unchanged. We excluded it because it adds no explanatory power for OECD analysis.

**Maternal disorders excluded**: We tested maternal disorders (maternal mortality) as a predictor. It produced a *counterintuitive* positive coefficient — higher maternal mortality was associated with a larger life expectancy gap — which contradicts the expected direction (maternal deaths are female-only, so higher rates should narrow the gap). The coefficient had wide uncertainty, importance was negligible (ranked last), and the association appeared spurious (possibly capturing shared variance with healthcare quality). We excluded it for interpretability.

**No year effects**: We tested a Gaussian Random Walk for temporal trends. It worsened predictive performance (ΔWAIC +97 to +110). The model without year effects is simpler and preferred.

## What This Means

Road traffic injuries have the strongest causal effect on gender gaps in life expectancy, followed by homicide and suicide.
Coefficients tell us the effect size; importance (which accounts for real-world variation) shows that cancer gaps are also highly important despite a moderate coefficient.
External causes — injuries, violence — collectively dominate in terms of effect size.

The Bayesian model successfully identifies which causes matter most, providing both point estimates and uncertainty quantification.
It also reveals competing-risk effects for cardiovascular disease and diabetes: reducing those gaps would not narrow the life expectancy gap; it would widen it.

In the next article, we will use these results to estimate how much of the gap could be closed through targeted interventions — and what would happen if we reduced gender gaps in specific causes to the levels achieved elsewhere.

---

*Next: [Counterfactuals: How much of the gap could we close?]*
