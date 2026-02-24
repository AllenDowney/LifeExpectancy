# Bayesian Panel Data Model: Analysis of HALE and Life Expectancy Gender Gaps (Extended Through 2021 with COVID-19)

## Purpose

This report presents results from a Bayesian hierarchical panel model that analyzes gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy using both temporal variation (2000-2021, including COVID-19 pandemic years) and cross-country variation simultaneously. Unlike the cross-sectional Elastic Net models, this panel approach leverages data from all country-year combinations, providing more statistical power and allowing us to assess whether predictors that matter cross-sectionally also matter within countries over time. 

**This extended analysis includes COVID-19 as a predictor**, allowing us to examine how the pandemic affected gender gaps in life expectancy. The analysis extends through 2021 (the most recent year for which HALE and Life Expectancy data are available from WHO), including the first two years of the COVID-19 pandemic.

**Key Questions Addressed:**
- Do the same predictors that matter cross-sectionally also matter within countries over time?
- Does alcohol matter because countries differ from each other, or because countries that reduce alcohol mortality see their gaps narrow?
- Do predictors (e.g., cardiovascular mortality) predict gaps within a country over time?
- How do Bayesian posterior estimates compare to the cross-sectional Elastic Net coefficients?
- **How did COVID-19 affect gender gaps in life expectancy?**
- **Do the relationships between predictors and gaps hold during the pandemic period?**

## Model Design

### Data Structure

The panel dataset transforms from country-level (one row per country) to panel structure (one row per country-year):

- **Time Period**: 2000-2021 (includes COVID-19 pandemic years 2020-2021)
- **Countries**: OECD countries excluding Turkey (37 countries; Turkey excluded due to outlier status - see Influential Observations section)
- **Observations**: Approximately 814 country-year combinations (37 countries × 22 years)
- **Target Variables**: 
  - `HALE_gap`: Female HALE - Male HALE (in years, positive means women live longer)
  - `LE_gap`: Female Life Expectancy - Male Life Expectancy (in years, positive means women live longer)
- **Predictors**: Gap columns only for each indicator (standardized across all country-year observations; Mid predictors excluded based on model comparison - see Model Extensions section)

### Standardization Strategy

**Predictors (Standardized - Full Z-Scores):**
- For each predictor `X_j` (Gap versions only; Mid predictors excluded - see Model Extensions section):
  - Compute mean `X̄_j` and standard deviation `s_j` across **all country-year observations** in the panel (OECD excluding Turkey, 2000-2021)
  - Transform to z-scores: `X*_{ijt} = (X_{ijt} - X̄_j) / s_j`
- **Important**: 
  - Do **not** standardize within country or within year
  - Use a **single global transformation** for the entire panel (2000-2021)
  - This preserves genuine level differences between countries and across time, which are part of the signal
- **Benefits**:
  - Priors are coherent: `β_j ~ N(0, 1)` means "1-SD change in predictor → ~1 year change in gap"
  - Coefficients are directly comparable across predictors
  - Indicator-level importance is straightforward: `|β_j|` in standardized space
  - Consistent with cross-sectional Elastic Net approach (time-extended version)

**Targets (Centered Only, Do Not Scale):**
- For HALE_gap and LE_gap separately:
  - Compute global mean across all country-years: `ȳ = mean(y_{it})`
  - Center (but do not scale): `y*_{it} = y_{it} - ȳ`
  - Keep units in **years** (not standardized)
- **Why center but not scale**:
  - **Interpretability**: Effects remain in "years" (e.g., "1-SD reduction in alcohol → 0.6-year reduction in gap")
  - **Numerical behavior**: Gap scale is modest (0-8 years), no scaling needed for numerical stability
  - **Priors**: With standardized predictors and unscaled (centered) target:
    - `β_j ~ N(0, 1)` is sensible: most effects within ±2 years per 1-SD change
    - `σ ~ HalfNormal(1)` reflects ~1 year unexplained variation

### Model Specification

**Model Structure:**
Bayesian hierarchical model with country-level random intercepts and shared slopes.

**Notation:**
- `y_{it}` = HALE gap (or LE gap) for country i in year t (centered: `y*_{it} = y_{it} - ȳ`)
- `X*_{it}` = vector of standardized predictors (Gap columns, z-scores across full panel)
- `α_i` = country-specific random intercept
- `β` = shared slope coefficients (same across all countries)
- `t` ∈ 2000–2021

**Model:**
```
y*_{it} ~ N(α_i + X*_{it}β, σ)
α_i ~ N(0, σ_α)
```

**Priors:**
- `β ~ N(0, 1)` - Regularizing prior on coefficients (1-SD change in predictor → ~1 year change in gap)
- `α_i ~ N(0, σ_α)` - Country intercepts centered at zero (since target is centered)
- `σ_α ~ HalfNormal(1)` - Prior on between-country intercept variation
- `σ ~ HalfNormal(1)` - Prior on residual standard deviation (~1 year unexplained variation)

### Why This Model?

1. **Answers the primary scientific question**: Does alcohol matter because countries differ from each other, or because countries that reduce alcohol mortality see their gaps narrow? This model can answer both.

2. **Seamlessly extends the cross-sectional Elastic Net model**: Provides posterior distributions for β instead of penalized point estimates, with natural interpretation as global "effect size" averaged over space and time, and shrinkage through hierarchical priors (like Bayesian ridge regression).

3. **Preserves counterfactual framework**: Produces posterior predictive distributions for country-level counterfactuals, changes through time, and uncertainty bands for temporal counterfactuals.

4. **Computationally feasible**: With ≈ 814 observations and 12 predictors, a hierarchical linear model runs efficiently in PyMC using the nutpie sampler.

5. **Uses both within-country and between-country variation**: Unlike fixed-effects models that eliminate all between-country variation, this approach leverages both sources of information.

6. **Controls for time-invariant country-level factors**: Random intercepts account for country-specific characteristics (culture, baseline health systems, risk environments) that don't change over time.

7. **Includes COVID-19**: By extending through 2021 and including COVID-19 as a predictor, we can assess how the pandemic affected gender gaps and whether the relationships between other predictors and gaps held during this period.

## Model Implementation

### Software and Methods

- **Bayesian Inference**: PyMC (Python) with nutpie sampler
- **MCMC Sampling**: 4 chains with default tuning and draws
- **Convergence Diagnostics**: R-hat, effective sample size (ESS)
- **Posterior Analysis**: ArviZ for diagnostics and visualization

### Data Preparation

The panel dataset includes:
- All years 2000-2021 for OECD countries (excluding Turkey - see Influential Observations section for justification)
- All predictor indicators used in the final cross-sectional model:
  - Alcohol Use Disorders (IHME)
  - Self-Harm/Suicide (IHME)
  - Interpersonal Violence/Homicide (IHME)
  - Road Injuries (IHME)
  - Cardiovascular Disease (IHME)
  - Diabetes (IHME)
  - Neoplasms/Cancer (IHME)
  - Chronic Respiratory Disease (IHME)
  - Liver Disease (IHME)
  - Unintentional Injuries (IHME)
  - Drug Use Disorders (IHME)
  - **COVID-19 (IHME)** - Added for extended analysis through 2021
- **Predictors**: Gap (gender difference) columns only for each indicator (Mid predictors excluded based on model comparison - see Model Extensions section)
- Complete panel: No missing data
- **Sample size**: Approximately 814 country-year observations (37 countries × 22 years, excluding Turkey)
- **Number of predictors**: 12 (Gap predictors for: Alcohol, Suicide, Homicide, Road Injuries, Cardiovascular, Diabetes, Neoplasms, Chronic Respiratory, Liver Disease, Unintentional Injuries, Drug Disorders, COVID-19)

**Note on COVID-19 Predictor:**
COVID-19 death rates are included as a predictor to assess how the pandemic affected gender gaps. COVID-19 data is available for 2020-2021, with zeros for all years before 2020 (since COVID-19 did not exist). The gender gap in COVID-19 mortality (Gap_COVID = Male COVID-19 death rate - Female COVID-19 death rate) is standardized across all country-years (2000-2021), which means the pre-2020 zeros are included in the standardization. This is appropriate because we want to assess the effect of COVID-19 gender gaps relative to the full temporal range.

## Results: HALE Gap Model

**Model Specification:**
- **Predictors**: Gap predictors only (12 predictors, including COVID-19), excluding Mid predictors
- **Year Effects**: Not included (tested but worsen model fit)
- **Countries**: OECD countries excluding Turkey (37 countries, ~814 observations)
- **Model Performance**: WAIC = -38.1 (ELPD), LOO = -36.8 (ELPD), p_waic = 66.5
- **Note**: The extended time period (2000-2021) includes COVID-19 pandemic years, which introduces additional variation and some influential observations (see Residual Analysis section)

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with R-hat = 1.0 for all parameters and adequate effective sample sizes (ESS > 2000 for all parameters).

### Predictor Coefficients (Beta)

The following table shows the posterior distributions of predictor coefficients. Since predictors are standardized (z-scores), coefficients represent the effect of a 1-standard-deviation change in the predictor on the gender gap in HALE (in years).

```{include} tables/beta_coefficients_hale_nomid_nogrw_y2021_covid.html
```

**Key Findings:**

**Strongest Positive Effects** (larger gender gaps in predictor → larger HALE gap, i.e., women live longer):
1. **Gap_RoadTraffic** (β = 0.476, 94% HDI: [0.426, 0.519]): The strongest predictor. Countries with larger male-female gaps in road traffic mortality have larger gender gaps in HALE. This is likely due to men driving more total miles (greater exposure) rather than risk-taking behavior, though both factors may contribute.
2. **Gap_Suicide** (β = 0.424, 94% HDI: [0.344, 0.5]): The second strongest predictor. Gender gaps in suicide mortality are strongly associated with gender gaps in HALE, reflecting the substantial contribution of suicide to male mortality.
3. **Gap_Homicide** (β = 0.384, 94% HDI: [0.341, 0.423]): Gender gaps in homicide mortality are strongly associated with HALE gaps, consistent with higher male homicide rates.
4. **Gap_Neoplasms** (β = 0.349, 94% HDI: [0.251, 0.454]): Gender gaps in cancer mortality contribute to HALE gaps, though with more uncertainty than the top three predictors.
5. **Gap_ChronicRespiratory** (β = 0.301, 94% HDI: [0.228, 0.367]): Gender gaps in chronic respiratory disease mortality are associated with HALE gaps.

**Moderate Positive Effects:**
- **Gap_LiverDisease** (β = 0.209, 94% HDI: [0.153, 0.266]): Gender gaps in liver disease mortality contribute to HALE gaps.
- **Gap_Alcohol** (β = 0.145, 94% HDI: [0.081, 0.211]): Gender gaps in alcohol-related mortality have a moderate positive effect.
- **Gap_UnintentionalInjury** (β = 0.152, 94% HDI: [0.069, 0.231]): Gender gaps in unintentional injury mortality contribute to HALE gaps, though with substantial uncertainty (HDI includes values near zero).
- **Gap_DrugDisorder** (β = 0.081, 94% HDI: [0.043, 0.117]): Gender gaps in drug use disorder mortality have a small positive effect.
- **Gap_COVID** (β = 0.054, 94% HDI: [0.037, 0.072]): **COVID-19 gender gaps have a small but positive effect on HALE gaps**. This indicates that countries with larger male-female gaps in COVID-19 mortality (men dying more from COVID-19) tend to have larger gender gaps in HALE. The effect is modest but statistically robust (HDI excludes zero), suggesting that COVID-19 contributed to gender gaps in life expectancy during the pandemic period.

**Negative Effects** (larger gender gaps in predictor → smaller HALE gap):
- **Gap_Cardiovascular** (β = -0.252, 94% HDI: [-0.301, -0.204]): This negative coefficient reflects a **competing risks** or **"risk of last resort"** mechanism. 

  **Sign conventions:**
  - HALE gap = Female - Male (positive means women live longer)
  - Gap_Cardiovascular = Male - Female for cardiovascular mortality (positive means men have higher risk)
  
  **What the negative coefficient means:**
  As Gap_Cardiovascular increases (men's CVD risk rises relative to women's), the female-male HALE gap tends to be smaller. Equivalently, in countries/years where the HALE gap is large (women doing especially well), Gap_Cardiovascular is typically small or even negative (women's CVD risk is closer to, or higher than, men's).
  
  **The "risk of last resort" mechanism:**
  Cardiovascular disease primarily affects people who have already survived many other causes of death. In settings where women's overall health is relatively good:
  - Women avoid or survive many other causes (maternal causes, infections, violence, etc.)
  - They live to older ages and are more exposed to late-life CVD
  - As a result, Gap_Cardiovascular tends to shrink or even flip sign (women's CVD risk approaches or exceeds men's)
  - At the same time, the HALE gap is large, because women enjoy advantages across many causes
  
  In settings where women's health is relatively worse:
  - Women face substantial risks from earlier-life causes (e.g., maternal mortality, poor access to care)
  - Fewer women survive to the ages where CVD dominates
  - Men still accumulate substantial CVD risk at older ages
  - So Gap_Cardiovascular tends to be large and positive (men much worse off for CVD)
  - But the HALE gap is smaller, because women lose more years to other causes
  
  **The pattern:** Large female-male HALE gaps tend to occur where the male-female CVD gap is small or negative. Large male-female CVD gaps tend to occur where women's overall advantage is weaker. This pattern produces the negative regression coefficient.

- **Gap_Diabetes** (β = -0.129, 94% HDI: [-0.171, -0.084]): Similar to cardiovascular disease, diabetes may also follow a competing risks pattern, though the effect is smaller. When women's health is good overall, more survive to die of diabetes, making the gap smaller and the overall HALE gap larger.

**Interpretation:**
- All coefficients have 94% HDIs that exclude zero, indicating robust effects.
- The model explains gender gaps in HALE primarily through external causes (road traffic, suicide, homicide) and neoplasms.
- **COVID-19 shows a small but positive effect**, indicating that the pandemic contributed to gender gaps in life expectancy, with men experiencing higher COVID-19 mortality than women.
- Cardiovascular and diabetes show negative coefficients, reflecting a **competing risks** mechanism: cardiovascular disease and diabetes are "risks of last resort" that primarily affect people who have survived other causes. When women's health is good overall, they survive other causes and live to older ages where CVD/diabetes dominate, making these gaps smaller and the overall HALE gap larger. When these gaps are large (positive), it indicates women are dying of other causes first, signaling worse overall health and a smaller HALE gap.
- The standardized coefficients allow direct comparison: a 1-SD increase in Gap_RoadTraffic is associated with a 0.476-year increase in the HALE gap.

### Predictor Importance on the Original Scale

Standardized coefficients allow direct comparison of effect sizes, but they do not account for how much each predictor typically varies across countries and years. To capture both effect size and real-world variation, we compute an **importance measure**:

**Importance = |β_standardized| × SD_original**

This quantity is **not** a causal effect or a prediction. Instead, it reflects how much a predictor can contribute to **explaining variation** in gender gaps given the amount of variation that predictor exhibits in the data.

```{include} tables/importance_measures_hale_nomid_nogrw_y2021_covid.html
```

**Key Findings:**
- **Neoplasms** has the highest importance (13.35 years), reflecting both a substantial effect size (β = 0.349) and large variation across countries and years (SD = 38.3).
- **Cardiovascular** has the second highest importance (9.19 years) despite a negative coefficient, reflecting its large variation (SD = 36.4).
- **Homicide** ranks third (5.25 years), followed by **Suicide** (4.16 years).
- **COVID-19** has relatively low importance (0.59 years), ranking 9th out of 12 predictors. This reflects its small coefficient (β = 0.054) and the fact that it only has non-zero values for 2020-2021, limiting its variation across the full time period.

**Interpretation:**
- Importance scores rank predictors by their contribution to explaining variation in gender gaps.
- COVID-19's low importance does not mean it's unimportant—it means that, given its limited temporal variation (only 2 years of data), it contributes less to explaining overall variation than predictors with longer time series.
- The importance measure should be interpreted alongside the standardized coefficients: COVID-19 has a small but statistically robust effect (β = 0.054), but its contribution to explaining variation is limited by its short time series.

## Results: Life Expectancy Gap Model

**Model Specification:**
- **Predictors**: Gap predictors only (12 predictors, including COVID-19), excluding Mid predictors
- **Year Effects**: Not included (tested but worsen model fit)
- **Countries**: OECD countries excluding Turkey (37 countries, ~814 observations)
- **Model Performance**: WAIC = -175 (ELPD), LOO = -170 (ELPD), p_waic = 75.9

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with R-hat = 1.0 for all parameters and adequate effective sample sizes (ESS > 2000 for all parameters).

### Predictor Coefficients (Beta)

```{include} tables/beta_coefficients_le_nomid_nogrw_y2021_covid.html
```

**Key Findings:**
The pattern of coefficients for Life Expectancy is similar to HALE, with COVID-19 showing a small positive effect. The relative ordering of predictors is largely consistent between HALE and Life Expectancy models.

## R² and Residual Analysis

To provide interpretable goodness-of-fit measures and enable direct comparison with the cross-sectional Elastic Net models, we compute R² (explained variance) and perform comprehensive residual analysis for both HALE and Life Expectancy gap models.

### R² Summary

The Bayesian panel models achieve excellent fit, explaining nearly all variance in the gender gaps:

```{include} tables/r2_comparison_nomid_nogrw_y2021_covid.html
```

**Key Findings:**
- **HALE Gap Model**: R² = 0.983 (94% HDI: [0.982, 0.983])
  - The model explains 98.3% of variance in HALE gap across all country-years
  - Mean Absolute Error (MAE) = 0.169 years
  - Residual standard deviation = 0.235 years

- **Life Expectancy Gap Model**: R² = 0.978 (94% HDI: [0.977, 0.979])
  - The model explains 97.8% of variance in Life Expectancy gap across all country-years
  - Mean Absolute Error (MAE) = 0.189 years
  - Residual standard deviation = 0.275 years

**Comparison with 2019 Model:**
- The extended model (2000-2021) has slightly lower R² than the 2019 model (0.983 vs. 0.987 for HALE, 0.978 vs. 0.985 for LE), reflecting the additional variation introduced by the COVID-19 pandemic years.
- MAE is slightly higher (0.169 vs. 0.158 for HALE, 0.189 vs. 0.175 for LE), indicating that predictions are slightly less accurate when including pandemic years.
- Residual standard deviation is higher (0.235 vs. 0.204 for HALE, 0.275 vs. 0.228 for LE), reflecting increased unexplained variation during the pandemic period.

**Interpretation:**
- Both models still achieve exceptionally high R² values (>0.97), indicating that the gap predictors capture nearly all systematic variation in gender gaps, even when including pandemic years.
- The small increase in MAE and residual standard deviation suggests that the pandemic introduced some additional variation that is not fully captured by the predictors, but the model still performs well overall.

### Residual Analysis

Residual analysis provides diagnostic information about model fit and identifies potential issues:

**Residual Statistics:**

```{include} tables/residual_summary_hale_nomid_nogrw_y2021_covid.html
```

**HALE Gap Model Residuals:**
- Mean: -0.0002 years (essentially zero, as expected)
- Standard deviation: 0.235 years
- Range: **-2.74 to +0.835 years** (note the large negative residual)
- MAE: 0.169 years

**Key Finding: Large Residual in 2021**

The residual analysis reveals a **very large negative residual of -2.74 years** for one observation. This is substantially larger than the typical residual range (most residuals are within ±0.7 years). Investigation of the influential observations table reveals that **Israel (ISR) in 2021** has an extremely large negative residual and a very high Pareto k value (1.66, well above the 0.7 threshold), indicating that this observation is highly influential and problematic for the model.

**Why Israel 2021 May Be an Outlier:**

1. **COVID-19 impact**: Israel experienced a significant COVID-19 wave in 2021, and the model may not fully capture the complex interactions between COVID-19 and other causes of death during this period.

2. **Data quality**: The 2021 data for Israel may have measurement issues, reporting delays, or systematic biases related to the pandemic.

3. **Unique pandemic response**: Israel's specific pandemic response (e.g., early vaccination campaign, unique policy measures) may have created patterns in gender gaps that differ from other countries in ways not captured by the predictors.

4. **Model limitations**: The model assumes stable relationships across all years, but the pandemic may have fundamentally altered some relationships in ways that the model cannot capture.

**Recommendation for Further Investigation:**

The large residual for Israel 2021 warrants further investigation:
- Examine the actual HALE gap values for Israel in 2021 vs. predicted values
- Compare Israel's COVID-19 mortality patterns to other countries
- Check for data quality issues in the 2021 WHO HALE data for Israel
- Consider whether Israel should be excluded from the 2021 analysis or whether the model needs modification to better capture pandemic effects

**Other Influential Observations:**

The influential observations table shows several 2021 observations among the top 10 most influential:
- **Israel 2021** (ISR, 2021): LOO contribution = -71.9, Pareto k = 1.66 (extremely high, indicating severe model misfit)
- **Latvia 2021** (LVA, 2021): LOO contribution = -10.0, Pareto k = 0.692 (just below threshold)
- **Mexico 2021** (MEX, 2021): LOO contribution = -8.21, Pareto k = 0.998 (above threshold)
- **Lithuania 2021** (LTU, 2021): LOO contribution = -4.03, Pareto k = 0.382

The concentration of 2021 observations among the most influential suggests that the pandemic period introduced additional variation that is not fully captured by the model.

**Residual Diagnostics:**

```{figure} figs/residuals_vs_predicted_hale_nomid_nogrw_y2021_covid.png
:name: residuals_vs_predicted_hale_covid
:width: 100%

Residuals vs. predicted values for HALE gap model (2000-2021). The large negative residual for Israel 2021 is visible as an outlier.
```

```{figure} figs/residuals_vs_year_hale_nomid_nogrw_y2021_covid.png
:name: residuals_vs_year_hale_covid
:width: 100%

Residuals vs. year for HALE gap model (2000-2021). The 2021 residuals show increased variance, with Israel 2021 as a clear outlier.
```

**Key Observations:**
- **2021 shows increased variance**: The residuals for 2021 show greater spread than previous years, reflecting the additional variation introduced by the pandemic.
- **Israel 2021 is a clear outlier**: The -2.74 year residual for Israel 2021 stands out dramatically from the rest of the data.
- **Other 2021 observations**: While other 2021 observations show larger residuals than typical, they are not as extreme as Israel.

## Comparison with 2019 Model

### Coefficient Stability

Comparing the 2021 model (with COVID-19) to the 2019 model (pre-COVID) reveals that most coefficients are remarkably stable:

| Predictor | 2019 Model (β) | 2021 Model (β) | Change |
|-----------|----------------|----------------|--------|
| Gap_RoadTraffic | 0.464 | 0.476 | +0.012 |
| Gap_Suicide | 0.422 | 0.424 | +0.002 |
| Gap_Homicide | 0.374 | 0.384 | +0.010 |
| Gap_Neoplasms | 0.372 | 0.349 | -0.023 |
| Gap_ChronicRespiratory | 0.336 | 0.301 | -0.035 |
| Gap_LiverDisease | 0.233 | 0.209 | -0.024 |
| Gap_Alcohol | 0.158 | 0.145 | -0.013 |
| Gap_UnintentionalInjury | 0.149 | 0.152 | +0.003 |
| Gap_Cardiovascular | -0.247 | -0.252 | -0.005 |
| Gap_Diabetes | -0.108 | -0.129 | -0.021 |
| Gap_DrugDisorder | 0.081 | 0.081 | 0.000 |

**Key Findings:**
- **Coefficients are largely stable**: Most coefficients changed by less than 0.025, indicating that the relationships between predictors and gender gaps remained consistent even when including pandemic years.
- **Small decreases in some coefficients**: Neoplasms, Chronic Respiratory, and Liver Disease show small decreases, possibly reflecting that these causes became relatively less important during the pandemic period.
- **COVID-19 effect is small**: The addition of COVID-19 as a predictor did not substantially alter the coefficients of other predictors, suggesting that COVID-19's effect is largely independent of the other causes.

### Model Performance Comparison

| Metric | 2019 Model | 2021 Model | Change |
|--------|------------|------------|--------|
| **HALE R²** | 0.987 | 0.983 | -0.004 |
| **HALE MAE** | 0.158 | 0.169 | +0.011 |
| **HALE Residual SD** | 0.204 | 0.235 | +0.031 |
| **LE R²** | 0.985 | 0.978 | -0.007 |
| **LE MAE** | 0.175 | 0.189 | +0.014 |
| **LE Residual SD** | 0.228 | 0.275 | +0.047 |

**Key Findings:**
- **Slight decrease in R²**: The extended model explains slightly less variance, reflecting the additional variation introduced by the pandemic.
- **Slight increase in MAE**: Predictions are slightly less accurate when including pandemic years.
- **Increased residual variance**: The pandemic period introduced additional unexplained variation, but the model still performs well overall.

## Counterfactual Analysis: United States

This section presents counterfactual analysis for the United States using 2021 as the reference year (the latest available year in the dataset). For each gap predictor, we compute what would happen to the predicted gap if we adjusted that predictor to zero (complete gender equality) while keeping all other predictors constant.

### Counterfactual Effects for All Indicators

The following tables show counterfactual effects for all indicators for the United States in 2021:

**HALE Gap Counterfactuals:**
- [Counterfactual Analysis Table: HALE Gap (2021)](tables/counterfactuals_usa_2021_hale_bayesian.html)

**Life Expectancy Gap Counterfactuals:**
- [Counterfactual Analysis Table: Life Expectancy Gap (2021)](tables/counterfactuals_usa_2021_le_bayesian.html)

### Counterfactual Visualizations

The following figures show counterfactual effects visualized in different ways:

**HALE Gap:**
- [Forest Plot: All Indicators](figs/counterfactual_effects_usa_2021_hale_bayesian.png)
- [Two-Panel Plot: Gap-Closing vs Gap-Widening](figs/counterfactual_effects_usa_2021_hale_by_type_bayesian.png)
- [Bar Chart: Sorted by Magnitude](figs/counterfactual_effects_usa_2021_hale_bar_bayesian.png)

**Life Expectancy Gap:**
- [Forest Plot: All Indicators](figs/counterfactual_effects_usa_2021_le_bayesian.png)
- [Two-Panel Plot: Gap-Closing vs Gap-Widening](figs/counterfactual_effects_usa_2021_le_by_type_bayesian.png)
- [Bar Chart: Sorted by Magnitude](figs/counterfactual_effects_usa_2021_le_bar_bayesian.png)

### Positive-Contributing Factors Over Time

The following analysis shows how positive-contributing factors (gap-closing indicators) contribute to reducing the gender gap over time for the United States. Each factor's contribution is computed as the reduction in the gap that would occur if that factor were set to zero (complete gender equality), with all other factors held constant.

**Key Features:**
- **Stacked area chart**: Shows the contribution of each gap-closing factor over time
- **Predicted vs Actual totals**: Overlays the predicted and actual gap values to show how contributions relate to the overall gap

**HALE Gap - Positive Contributions Over Time:**
- [Stacked Area Chart](figs/positive_contributions_stacked_area_usa_hale.png)
- [Contributions Table](tables/positive_contributions_usa_hale_over_time.html)
- [Percentage of Actual Gap](figs/positive_contributions_percentage_usa_hale.png)

**Life Expectancy Gap - Positive Contributions Over Time:**
- [Stacked Area Chart](figs/positive_contributions_stacked_area_usa_le.png)
- [Contributions Table](tables/positive_contributions_usa_le_over_time.html)
- [Percentage of Actual Gap](figs/positive_contributions_percentage_usa_le.png)

The stacked area charts show that multiple factors contribute to reducing the gender gap, with contributions varying over time. The predicted and actual totals demonstrate how well the model captures the overall gap and how the sum of individual factor contributions relates to the total gap.

The percentage plots show what proportion of the actual gap is accounted for by the positive-contributing (gap-closing) factors. If the percentage is less than 100%, the remaining gap is due to gap-widening factors, the country-specific intercept, the global mean, and any residual variation. This helps quantify how much of the observed gap could potentially be addressed by eliminating gender differences in the positive-contributing factors.

## Conclusions

### Key Findings

1. **COVID-19 has a small but positive effect on gender gaps**: The coefficient for Gap_COVID (β = 0.054) indicates that countries with larger male-female gaps in COVID-19 mortality tend to have larger gender gaps in HALE and Life Expectancy. This is consistent with the observation that men experienced higher COVID-19 mortality than women in most countries.

2. **Relationships remain stable during pandemic**: The coefficients for other predictors are largely unchanged when including pandemic years, suggesting that the relationships between predictors and gender gaps held during the pandemic period.

3. **Model fit remains excellent**: Despite the additional variation introduced by the pandemic, the model still explains >97% of variance in gender gaps.

4. **2021 shows increased residual variance**: The pandemic period introduced additional unexplained variation, with Israel 2021 showing an extremely large residual that warrants further investigation.

### Limitations and Future Work

1. **Israel 2021 outlier**: The large residual for Israel 2021 suggests that either:
   - The data for Israel in 2021 has quality issues
   - Israel's pandemic experience was unique in ways not captured by the model
   - The model needs modification to better capture pandemic effects

2. **Limited COVID-19 data**: COVID-19 only has 2 years of data (2020-2021), limiting our ability to assess its long-term effects on gender gaps.

3. **Pandemic interactions**: The model does not explicitly model interactions between COVID-19 and other causes of death, which may be important during the pandemic period.

4. **Temporal stability assumption**: The model assumes stable relationships across all years, but the pandemic may have fundamentally altered some relationships.

### Recommendations

1. **Investigate Israel 2021**: The large residual for Israel 2021 should be investigated to determine whether it reflects data quality issues, unique country characteristics, or model limitations.

2. **Consider excluding problematic observations**: If Israel 2021 is found to have data quality issues, consider excluding it from the analysis or using robust methods that downweight influential observations.

3. **Monitor future data**: As more post-pandemic data becomes available, reassess the model to see if relationships return to pre-pandemic patterns or if the pandemic created lasting changes.

4. **Consider pandemic-specific models**: Future work could develop models that explicitly account for pandemic effects, such as interactions between COVID-19 and other causes or time-varying coefficients during the pandemic period.

