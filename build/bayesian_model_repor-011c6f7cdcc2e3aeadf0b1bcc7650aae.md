# Bayesian Panel Data Model: Analysis of HALE and Life Expectancy Gender Gaps (Extended Through 2023 with IHME HALE)

## Purpose

This report presents results from a Bayesian hierarchical panel model that analyzes gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy using both temporal variation and cross-country variation simultaneously. Unlike the cross-sectional Elastic Net models, this panel approach leverages data from all country-year combinations, providing more statistical power and allowing us to assess whether predictors that matter cross-sectionally also matter within countries over time.

**This extended analysis uses IHME HALE data (2000-2023) instead of WHO HALE data**, providing methodological consistency with the IHME predictor indicators and extending the temporal range through 2023. The Life Expectancy model continues to use WHO data (2000-2021) as WHO LE remains the gold standard for life expectancy estimates.

**Key Questions Addressed:**
- Do the same predictors that matter cross-sectionally also matter within countries over time?
- Does alcohol matter because countries differ from each other, or because countries that reduce alcohol mortality see their gaps narrow?
- Do predictors (e.g., cardiovascular mortality) predict gaps within a country over time?
- How do Bayesian posterior estimates compare to the cross-sectional Elastic Net coefficients?
- How did COVID-19 affect gender gaps in life expectancy?
- Do the relationships between predictors and gaps hold through the post-acute COVID period (2022-2023)?

## Model Design

### Data Structure

The panel dataset transforms from country-level (one row per country) to panel structure (one row per country-year):

- **HALE Model Time Period**: 2000-2023 (using IHME HALE data, includes full COVID period)
- **Life Expectancy Model Time Period**: 2000-2021 (using WHO LE data, limited by data availability)
- **Countries**: OECD countries excluding Turkey (37 countries; Turkey excluded because it's not available in IHME HALE data)
- **Observations**: 
  - HALE model: 888 country-year combinations (37 countries × 24 years)
  - LE model: 814 country-year combinations (37 countries × 22 years)
- **Target Variables**: 
  - `HALE_gap`: Female HALE - Male HALE (in years, positive means women live longer) - **IHME source**
  - `LE_gap`: Female Life Expectancy - Male Life Expectancy (in years, positive means women live longer) - **WHO source**
- **Predictors**: Gap columns only for each indicator (standardized across all country-year observations; Mid predictors excluded based on model comparison)

### Rationale for Using IHME HALE

**Why switch from WHO HALE to IHME HALE?**

1. **Methodological Consistency**: All predictor variables (alcohol, suicide, homicide, cardiovascular, etc.) come from IHME's Global Burden of Disease (GBD) database. Using IHME HALE ensures that the target variable and predictors are methodologically consistent, using the same data collection processes, estimation methods, and quality standards.

2. **Extended Temporal Coverage**: IHME HALE data extends through 2023, providing two additional years of post-acute-COVID data compared to WHO's 2021 cutoff. This allows us to assess whether COVID-19's effects on gender gaps persisted or attenuated in 2022-2023.

3. **Data Quality**: The correlation between WHO and IHME HALE is very high (r > 0.95), indicating excellent agreement. Both sources are high-quality, but IHME provides the advantages above.

4. **Reproducibility**: Using a single data source (IHME) for all cause-specific mortality measures and HALE improves transparency and reproducibility.

**Note**: The Life Expectancy model continues to use WHO LE data because WHO is the gold standard for life expectancy estimates, and WHO LE data is universally recognized and cited.

### Standardization Strategy

**Predictors (Standardized - Full Z-Scores):**
- For each predictor `X_j` (Gap versions only; Mid predictors excluded):
  - Compute mean `X̄_j` and standard deviation `s_j` across **all country-year observations** in the panel
  - Transform to z-scores: `X*_{ijt} = (X_{ijt} - X̄_j) / s_j`
- **Important**: 
  - Do **not** standardize within country or within year
  - Use a **single global transformation** for the entire panel
  - This preserves genuine level differences between countries and across time
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
- For HALE: `t` ∈ 2000–2023; for LE: `t` ∈ 2000–2021

**Model:**
```
y*_{it} ~ N(α_i + X*_{it}β, σ)
α_i ~ N(0, σ_α)
```

**Priors:**
- `β ~ N(0, 1)` - Regularizing prior on coefficients
- `α_i ~ N(0, σ_α)` - Country intercepts centered at zero (since target is centered)
- `σ_α ~ HalfNormal(1)` - Prior on between-country intercept variation
- `σ ~ HalfNormal(1)` - Prior on residual standard deviation

### Why This Model?

1. **Answers the primary scientific question**: Does alcohol matter because countries differ from each other, or because countries that reduce alcohol mortality see their gaps narrow? This model can answer both.

2. **Seamlessly extends the cross-sectional Elastic Net model**: Provides posterior distributions for β instead of penalized point estimates, with natural interpretation as global "effect size" averaged over space and time.

3. **Preserves counterfactual framework**: Produces posterior predictive distributions for country-level counterfactuals.

4. **Computationally feasible**: Hierarchical linear model runs efficiently in PyMC using the nutpie sampler.

5. **Uses both within-country and between-country variation**: Leverages both sources of information.

6. **Controls for time-invariant country-level factors**: Random intercepts account for country-specific characteristics.

7. **Includes full COVID period**: By extending through 2023 for HALE, we can assess whether COVID-19's effects persisted or attenuated.

## Model Implementation

### Software and Methods

- **Bayesian Inference**: PyMC (Python) with nutpie sampler
- **MCMC Sampling**: 4 chains, 1000 draws per chain
- **Convergence Diagnostics**: R-hat, effective sample size (ESS)
- **Posterior Analysis**: ArviZ for diagnostics and visualization

### Data Preparation

The panel datasets include:

**HALE Model (IHME data, 2000-2023):**
- All years 2000-2023 for OECD countries excluding Turkey
- Sample size: 888 country-year observations (37 countries × 24 years)

**Life Expectancy Model (WHO data, 2000-2021):**
- All years 2000-2021 for OECD countries excluding Turkey
- Sample size: 814 country-year observations (37 countries × 22 years)

**Predictors (both models):**
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
  - COVID-19 (IHME)
- **Predictors**: Gap (gender difference) columns only
- Complete panels: No missing data
- **Number of predictors**: 12

**Note on COVID-19 Predictor:**
COVID-19 death rates are included as a predictor to assess how the pandemic affected gender gaps. COVID-19 data is available for 2020-2023 (IHME), with zeros for all years before 2020. The HALE model now includes the full COVID period and early post-acute phase (2020-2023), while the LE model includes only the acute phase (2020-2021).

## Results: HALE Gap Model

**Model Specification:**
- **Data Source**: IHME HALE (methodologically consistent with predictors)
- **Time Period**: 2000-2023 (24 years, includes full COVID period)
- **Predictors**: Gap predictors only (12 predictors, including COVID-19)
- **Year Effects**: Not included
- **Countries**: OECD countries excluding Turkey (37 countries, 888 observations)
- **Model Performance**: WAIC = 1.01 (ELPD), LOO = 0.64 (ELPD), p_waic = 55.1, p_loo = 55.5

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with:
- Max R-hat = 1.01 (all parameters)
- Min ESS (bulk) = 807
- Adequate effective sample sizes (ESS > 800 for all parameters)

### Predictor Coefficients (Beta)

The following table shows the posterior distributions of predictor coefficients. Since predictors are standardized (z-scores), coefficients represent the effect of a 1-standard-deviation change in the predictor on the gender gap in HALE (in years).

```{include} tables/beta_coefficients_hale_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**

**Strongest Positive Effects** (larger gender gaps in predictor → larger HALE gap, i.e., women live longer):
1. **Gap_RoadTraffic** (β = 0.465, 94% HDI: [0.424, 0.505]): The strongest predictor. Countries with larger male-female gaps in road traffic mortality have larger gender gaps in HALE.
2. **Gap_Suicide** (β = 0.365, 94% HDI: [0.300, 0.432]): The second strongest predictor. Gender gaps in suicide mortality are strongly associated with gender gaps in HALE.
3. **Gap_ChronicRespiratory** (β = 0.368, 94% HDI: [0.310, 0.431]): Gender gaps in chronic respiratory disease mortality show a strong association, **notably stronger than in the WHO-based 2021 model**.
4. **Gap_Homicide** (β = 0.309, 94% HDI: [0.271, 0.348]): Gender gaps in homicide mortality are associated with HALE gaps, **but weaker than in the WHO-based model**.
5. **Gap_Neoplasms** (β = 0.237, 94% HDI: [0.152, 0.322]): Gender gaps in cancer mortality contribute to HALE gaps, **substantially weaker than in the WHO-based model**.

**Moderate Positive Effects:**
- **Gap_UnintentionalInjury** (β = 0.194, 94% HDI: [0.135, 0.254]): Gender gaps in unintentional injury mortality contribute to HALE gaps, **stronger than in WHO model**.
- **Gap_LiverDisease** (β = 0.190, 94% HDI: [0.143, 0.244]): Gender gaps in liver disease mortality contribute to HALE gaps.
- **Gap_Alcohol** (β = 0.130, 94% HDI: [0.075, 0.184]): Gender gaps in alcohol-related mortality have a moderate positive effect.
- **Gap_COVID** (β = 0.060, 94% HDI: [0.044, 0.075]): **COVID-19 gender gaps continue to have a small but positive effect on HALE gaps**, similar to the WHO-based model but now with 2 additional years of data.
- **Gap_DrugDisorder** (β = 0.055, 94% HDI: [0.021, 0.085]): Gender gaps in drug use disorder mortality have a small positive effect, **weaker than in WHO model**.

**Negative Effects** (larger gender gaps in predictor → smaller HALE gap):
- **Gap_Cardiovascular** (β = -0.274, 94% HDI: [-0.318, -0.232]): This negative coefficient reflects a **competing risks** or **"risk of last resort"** mechanism. As Gap_Cardiovascular increases (men's CVD risk rises relative to women's), the female-male HALE gap tends to be smaller. This is because cardiovascular disease primarily affects people who have survived other causes. In settings where women's overall health is good, they survive other causes and live to older ages where CVD dominates, making Gap_Cardiovascular smaller and the HALE gap larger. **The effect is slightly stronger than in the WHO-based model**.

- **Gap_Diabetes** (β = -0.129, 94% HDI: [-0.165, -0.092]): Similar to cardiovascular disease, diabetes follows a competing risks pattern. **The effect is identical to the WHO-based model**.

**Interpretation:**
- All coefficients have 94% HDIs that exclude zero, indicating robust effects.
- The model explains gender gaps in HALE primarily through external causes (road traffic, suicide, respiratory disease) and moderately through homicide and cancer.
- **COVID-19 shows a small but positive effect**, indicating that the pandemic's contribution to gender gaps persisted through 2023.
- Cardiovascular and diabetes show negative coefficients, reflecting a **competing risks** mechanism.
- **Notable shifts from WHO-based model**: Chronic Respiratory became more important, while Homicide and Neoplasms became less important. This may reflect either true differences in IHME vs WHO HALE or the effects of including 2022-2023 data.

### Predictor Importance on the Original Scale

Standardized coefficients allow direct comparison of effect sizes, but they do not account for how much each predictor typically varies across countries and years. To capture both effect size and real-world variation, we compute an **importance measure**:

**Importance = |β_standardized| × SD_original**

This quantity reflects how much a predictor can contribute to **explaining variation** in gender gaps given the amount of variation that predictor exhibits in the data.

```{include} tables/importance_measures_hale_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**
- **Neoplasms** has the highest importance, reflecting both a substantial effect size and large variation across countries and years.
- **Cardiovascular** has high importance despite a negative coefficient, reflecting its large variation.
- **Chronic Respiratory** ranks high, reflecting its strong effect in the IHME-based model.
- **COVID-19** has relatively low importance, reflecting its small coefficient and limited temporal variation (only 4 years of non-zero data).

## Results: Life Expectancy Gap Model

**Model Specification:**
- **Data Source**: WHO Life Expectancy (gold standard for LE estimates)
- **Time Period**: 2000-2021 (22 years, limited by WHO data availability)
- **Predictors**: Gap predictors only (12 predictors, including COVID-19)
- **Year Effects**: Not included
- **Countries**: OECD countries excluding Turkey (37 countries, 814 observations)
- **Model Performance**: WAIC = -173.25 (ELPD), LOO = -169.46 (ELPD), p_waic = 76.8, p_loo = 73.0

**Note**: The Life Expectancy model uses the same time period and data sources as the previous 2021 report, so **results are identical to the 2021 report**. We continue to use WHO LE data because it is the gold standard for life expectancy estimates.

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with:
- Max R-hat = 1.00 (all parameters)
- Min ESS (bulk) = 1113
- Excellent effective sample sizes

### Predictor Coefficients (Beta)

```{include} tables/beta_coefficients_le_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**
The pattern of coefficients for Life Expectancy is similar to HALE, with COVID-19 showing a small positive effect. The relative ordering of predictors is largely consistent between HALE and Life Expectancy models.

## Comparison with WHO-Based 2021 Model

### Key Changes in HALE Model

**Data Source Changes:**
- **2021 Model**: WHO HALE, 2000-2021 (22 years, 814 observations)
- **2023 Model**: IHME HALE, 2000-2023 (24 years, 888 observations)
- **Rationale**: Methodological consistency with IHME predictors, extended temporal coverage

### Coefficient Comparison

Comparing the IHME-based 2023 model to the WHO-based 2021 model:

| Predictor | WHO 2021 (β) | IHME 2023 (β) | Change | Interpretation |
|-----------|--------------|---------------|--------|----------------|
| **Gap_Homicide** | 0.384 | 0.309 | **-0.075** | **Largest drop** - may reflect narrowing homicide gaps in recent years or methodological differences |
| **Gap_Suicide** | 0.424 | 0.365 | **-0.059** | Moderate decrease with IHME data |
| **Gap_Neoplasms** | 0.349 | 0.237 | **-0.112** | **Major drop** - cancer gap effects weaker in IHME data or changing over time |
| **Gap_ChronicRespiratory** | 0.301 | 0.368 | **+0.067** | **Increased** - respiratory disease gaps more important with IHME data/extended period |
| **Gap_UnintentionalInjury** | 0.152 | 0.194 | **+0.042** | Increased importance |
| **Gap_Cardiovascular** | -0.252 | -0.274 | **-0.022** | Slightly stronger protective (competing risk) effect |
| **Gap_RoadTraffic** | 0.476 | 0.465 | -0.011 | Small decrease, remains strongest predictor |
| **Gap_Alcohol** | 0.145 | 0.130 | -0.015 | Small decrease |
| **Gap_LiverDisease** | 0.209 | 0.190 | -0.019 | Small decrease |
| **Gap_DrugDisorder** | 0.081 | 0.055 | **-0.026** | Reduced effect |
| **Gap_Diabetes** | -0.129 | -0.129 | **0.000** | **Identical** - remarkably stable |
| **Gap_COVID** | 0.054 | 0.060 | +0.006 | Slightly higher with 2 more years of data |

**Key Observations:**

1. **Coefficient Stability**: Despite changing data sources and adding 2 years, most coefficients remain within 0.02-0.04 of their previous values, indicating robust relationships.

2. **Notable Shifts**:
   - **Neoplasms** (-0.112): Large decrease suggests either methodological differences between WHO and IHME HALE or evolving cancer dynamics
   - **Homicide** (-0.075): Substantial decrease may reflect narrowing violence gaps or measurement differences
   - **Chronic Respiratory** (+0.067): Increased importance, possibly due to COVID-19's respiratory impact or IHME methodology

3. **Stable Predictors**:
   - **Diabetes** (0.000): Identical coefficient suggests very stable competing-risk relationship
   - **Road Traffic** (-0.011): Small change, remains the strongest predictor
   - **COVID-19** (+0.006): Similar effect with longer temporal coverage

4. **Model Performance**:
   - Both models achieve excellent fit (R² > 0.98)
   - IHME-based model has 74 more observations (888 vs 814)
   - Slightly different WAIC reflects different data, not worse fit

### Life Expectancy Model: No Changes

The Life Expectancy model results are **identical to the 2021 report** because:
- Same data source (WHO Life Expectancy, gold standard)
- Same time period (2000-2021, limited by WHO data availability)
- Same 814 observations (37 countries × 22 years)

We maintain WHO LE data for consistency with international standards and because it remains the most widely recognized source for life expectancy estimates.

## R² and Residual Analysis

### R² Summary

The Bayesian panel models achieve excellent fit:

```{include} tables/r2_comparison_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**
- **HALE Gap Model** (IHME, 2000-2023): R² = 0.98-0.99
  - The model explains >98% of variance in HALE gap across all country-years
  - Mean Absolute Error (MAE) ≈ 0.17-0.20 years
  - Residual standard deviation ≈ 0.23-0.26 years

- **Life Expectancy Gap Model** (WHO, 2000-2021): R² = 0.978 (same as 2021 report)
  - The model explains 97.8% of variance in LE gap
  - MAE = 0.189 years
  - Residual standard deviation = 0.275 years

**Interpretation:**
- Both models achieve exceptionally high R² values (>0.97)
- The IHME HALE model performs comparably to the WHO-based model despite different data sources
- Extended temporal range (24 vs 22 years for HALE) does not compromise model fit

### Residual Analysis

Residual analysis for the IHME-based HALE model shows:

```{include} tables/residual_summary_hale_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**
- Mean residual: Near zero (as expected)
- Standard deviation: Similar to WHO-based model
- No extreme outliers like Israel 2021 in the WHO data
- More balanced residual distribution across all years

**Residual Diagnostics:**

```{figure} figs/residuals_vs_predicted_hale_ihme_nomid_nogrw_y2023_covid.png
:name: residuals_vs_predicted_hale_ihme
:width: 100%

Residuals vs. predicted values for HALE gap model (IHME, 2000-2023).
```

```{figure} figs/residuals_vs_year_hale_ihme_nomid_nogrw_y2023_covid.png
:name: residuals_vs_year_hale_ihme
:width: 100%

Residuals vs. year for HALE gap model (IHME, 2000-2023).
```

## Counterfactual Analysis: United States

This section presents counterfactual analysis for the United States using 2023 as the reference year for HALE (the latest available year in the IHME dataset) and 2021 for Life Expectancy (the latest available year in the WHO dataset).

For each gap predictor, we compute what would happen to the predicted gap if we adjusted that predictor to the best attainable value observed across all country-years, while keeping all other predictors constant. The analysis uses posterior distributions to quantify uncertainty.

### Key Findings: USA HALE Gap (2023)

**Gap-Closing Factors** (negative values = reduce HALE gap):

1. **Road Traffic** (-0.868 years [-0.943, -0.792]): The largest opportunity for reducing the HALE gap. If the USA could achieve Iceland's 2017 road traffic gender gap (1.92), the HALE gap would shrink by nearly 1 year.

2. **Suicide** (-0.522 years [-0.618, -0.429]): The second-largest factor. Achieving Greece's 2002 suicide gender gap (4.05) would reduce the HALE gap by over half a year.

3. **Drug Disorders** (-0.467 years [-0.715, -0.180]): A major contributor. Achieving Japan's 2013 drug disorder gap (essentially zero) would reduce the HALE gap by nearly half a year.

4. **Homicide** (-0.203 years [-0.229, -0.178]): Reducing the homicide gender gap to zero would reduce the HALE gap by about 0.2 years.

5. **Liver Disease** (-0.163 years [-0.209, -0.122]): Achieving Iceland's 2001 liver disease gap would provide a modest reduction.

6. **Alcohol** (-0.150 years [-0.211, -0.086]): Achieving Colombia's 2016 alcohol gap would reduce the HALE gap by about 0.15 years.

7. **Neoplasms** (-0.145 years [-0.198, -0.093]): Eliminating the cancer gender gap would provide a modest reduction.

8. **Unintentional Injury** (-0.075 years [-0.099, -0.052]): A smaller but measurable opportunity.

9. **COVID-19** (-0.007 years [-0.009, -0.005]): By 2023, COVID-19's contribution to the gap is minimal, indicating recovery from the pandemic's acute phase.

**Gap-Widening Factors** (positive values = increase HALE gap):

1. **Diabetes** (+0.281 years [0.200, 0.362]): The competing risk effect. Eliminating the diabetes gender gap would actually **widen** the HALE gap, reflecting that diabetes primarily affects people who survive other causes.

2. **Cardiovascular** (+0.227 years [0.193, 0.264]): Similar competing risk pattern. Women who survive other causes live to older ages where cardiovascular disease dominates.

3. **Chronic Respiratory** (+0.217 years [0.182, 0.254]): Women have worse chronic respiratory disease outcomes, widening the gap.

**Total Potential:**
- Sum of gap-closing factors: **≈2.4 years** (if all could be achieved simultaneously)
- Sum of gap-widening factors: **≈0.7 years** (competing risks)
- Net potential reduction: **≈1.7 years** from current USA HALE gap

### Comparison with 2021 WHO-Based Analysis

Notable changes when comparing IHME 2023 results to WHO 2021 results:

- **COVID-19 Effect Resolved**: Dropped from -0.200 years (2021, acute pandemic) to -0.007 years (2023), showing pandemic recovery
- **Drug Disorders**: Decreased importance (-0.708 → -0.467 years, -34%)
- **Neoplasms**: Decreased importance (-0.236 → -0.145 years, -39%)
- **Homicide**: Decreased importance (-0.279 → -0.203 years, -27%)
- **Chronic Respiratory**: Increased importance (+0.122 → +0.217 years, +78%), possibly reflecting long-term COVID effects
- **Road Traffic**: Remains #1 factor with stable magnitude (-0.926 → -0.868 years)

These changes reflect a combination of:
- Methodological differences between WHO and IHME HALE measurements
- Temporal changes in USA patterns (2021 → 2023)
- Model coefficient differences (e.g., Neoplasms β: 0.349 → 0.237)

### Counterfactual Effects for All Indicators

**HALE Gap Counterfactuals (2023):**

```{include} tables/counterfactuals_usa_2023_hale_bayesian.html
```

**Life Expectancy Gap Counterfactuals (2021):**

```{include} tables/counterfactuals_usa_2021_le_bayesian.html
```

### Counterfactual Visualizations

**HALE Gap (2023):**

```{figure} figs/counterfactual_effects_usa_2023_hale_bayesian.png
:name: counterfactual_hale_2023
:width: 100%

Forest plot showing counterfactual effects for USA HALE gap (2023) with 94% credible intervals.
```

```{figure} figs/counterfactual_effects_usa_2023_hale_by_type_bayesian.png
:name: counterfactual_hale_2023_by_type
:width: 100%

Two-panel plot separating gap-closing (left) and gap-widening (right) factors for USA HALE gap (2023).
```

```{figure} figs/counterfactual_effects_usa_2023_hale_bar_bayesian.png
:name: counterfactual_hale_2023_bar
:width: 100%

Bar chart of counterfactual effects sorted by magnitude for USA HALE gap (2023).
```

**Life Expectancy Gap (2021):**

```{figure} figs/counterfactual_effects_usa_2021_le_bayesian.png
:name: counterfactual_le_2021
:width: 100%

Forest plot showing counterfactual effects for USA Life Expectancy gap (2021) with 94% credible intervals.
```

```{figure} figs/counterfactual_effects_usa_2021_le_by_type_bayesian.png
:name: counterfactual_le_2021_by_type
:width: 100%

Two-panel plot separating gap-closing (left) and gap-widening (right) factors for USA Life Expectancy gap (2021).
```

```{figure} figs/counterfactual_effects_usa_2021_le_bar_bayesian.png
:name: counterfactual_le_2021_bar
:width: 100%

Bar chart of counterfactual effects sorted by magnitude for USA Life Expectancy gap (2021).
```

### Positive-Contributing Factors Over Time

The following analysis shows how gap-closing factors (positive-contributing indicators) have evolved over time for the United States. Each factor's contribution is computed as the reduction in the gap that would occur if that factor were set to its best attainable value.

**HALE Gap - Positive Contributions Over Time (IHME, 2000-2023):**

```{figure} figs/positive_contributions_stacked_area_usa_hale.png
:name: positive_contributions_hale_2023
:width: 100%

Stacked area chart showing contributions of gap-closing factors over time for USA HALE gap (2000-2023). The chart shows how different factors have contributed to explaining the HALE gap across the full temporal range.
```

```{include} tables/positive_contributions_usa_hale_over_time.html
```

```{figure} figs/positive_contributions_percentage_usa_hale.png
:name: positive_contributions_percentage_hale_2023
:width: 100%

Percentage of actual HALE gap explained by positive-contributing (gap-closing) factors over time. This shows what proportion of the observed gap could be reduced by addressing these factors.
```

**Life Expectancy Gap - Positive Contributions Over Time (WHO, 2000-2021):**

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:name: positive_contributions_le_2021
:width: 100%

Stacked area chart showing contributions of gap-closing factors over time for USA Life Expectancy gap (2000-2021).
```

```{include} tables/positive_contributions_usa_le_over_time.html
```

```{figure} figs/positive_contributions_percentage_usa_le.png
:name: positive_contributions_percentage_le_2021
:width: 100%

Percentage of actual Life Expectancy gap explained by positive-contributing (gap-closing) factors over time.
```

## Conclusions

### Key Findings

1. **Successful Data Source Transition**: The switch from WHO HALE to IHME HALE was successful, maintaining methodological consistency with all predictor variables while extending temporal coverage to 2023.

2. **Extended COVID-19 Period**: Including 2022-2023 data shows that COVID-19's effect on gender gaps persisted into the post-acute phase, with a small but consistent positive coefficient (β = 0.060).

3. **Coefficient Stability with Notable Shifts**: Most coefficients remained stable when switching data sources, but three showed substantial changes:
   - **Neoplasms decreased** (-0.112): Cancer gaps may be less important in IHME data or evolved 2021-2023
   - **Homicide decreased** (-0.075): Violence gaps may be narrowing or measured differently
   - **Chronic Respiratory increased** (+0.067): Respiratory disease gaps became more important, possibly due to COVID-19's long-term effects

4. **Diabetes Coefficient Perfectly Stable**: The diabetes coefficient (β = -0.129) was identical across WHO and IHME data sources, demonstrating a remarkably robust competing-risk relationship.

5. **Model Performance**: Both IHME-based HALE and WHO-based LE models achieve excellent fit (R² > 0.97), explaining nearly all systematic variation in gender gaps.

6. **Separate Time Ranges Work Well**: The IHME HALE model (2000-2023) and WHO LE model (2000-2021) operate independently with their own optimal temporal ranges, maximizing data utilization while maintaining data quality.

### Advantages of IHME HALE Data

1. **Methodological Consistency**: All variables (HALE and predictors) come from the same IHME GBD methodology
2. **Extended Temporal Range**: Two additional years (2022-2023) capture post-acute COVID dynamics
3. **No Extreme Outliers**: Unlike WHO data (Israel 2021), IHME data showed no extreme residuals
4. **Maintained Quality**: High correlation with WHO HALE (r > 0.95) confirms data quality

### Limitations and Future Work

1. **Data Source Differences**: Some coefficient changes may reflect methodological differences between WHO and IHME rather than temporal evolution. Future work could decompose these effects.

2. **Limited Post-COVID Data**: Only 4 years of COVID data (2020-2023) limits assessment of long-term pandemic effects.

3. **Life Expectancy Data Gap**: WHO LE data ends at 2021, creating a 2-year gap with IHME HALE. Consider using IHME LE for consistency when new data becomes available.

4. **Turkey Exclusion**: Turkey is excluded from this analysis because it's not available in IHME HALE data. Previous analyses included Turkey with WHO data.

### Recommendations

1. **Use IHME HALE as Primary Target**: For future analyses, use IHME HALE to maintain methodological consistency with IHME predictors and maximize temporal coverage.

2. **Monitor Coefficient Evolution**: As more post-2023 data becomes available, track whether the coefficient shifts (especially Neoplasms and Chronic Respiratory) represent lasting changes or transient effects.

3. **Consider IHME LE for Consistency**: When IHME publishes life expectancy estimates through 2023, consider switching to IHME LE to maintain complete methodological consistency.

4. **Update Annually**: As IHME updates its GBD database, rerun models to incorporate new data and assess temporal stability.

5. **Investigate Respiratory Disease**: The increased importance of chronic respiratory disease gaps warrants further investigation, particularly regarding COVID-19's long-term respiratory effects.


