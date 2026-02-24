# Bayesian Panel Data Model: Analysis of HALE and Life Expectancy Gender Gaps (Extended Through 2023 with IHME HALE)

## Purpose

This report presents results from a Bayesian hierarchical panel model that analyzes gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy using both temporal variation and cross-country variation simultaneously. Unlike the cross-sectional Elastic Net models, this panel approach leverages data from all country-year combinations, providing more statistical power and allowing us to assess whether predictors that matter cross-sectionally also matter within countries over time.

**This extended analysis uses IHME HALE data (2000-2023) instead of WHO HALE data**, providing methodological consistency with the IHME predictor indicators and extending the temporal range through 2023. The Life Expectancy model now uses OWID data (2000-2023), which combines Human Mortality Database and UN World Population Prospects, extending coverage through 2023 to match the IHME HALE temporal range.

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

- **HALE Model Time Period**: 2000-2023 (using IHME HALE data, includes full COVID period and post-acute phase)
- **Life Expectancy Model Time Period**: 2000-2023 (using OWID LE data, matches HALE temporal coverage)
- **Countries**: OECD countries excluding Turkey (37 countries; Turkey excluded as an outlier with very low likelihood in the Bayesian model)
- **Observations**: 
  - HALE model: 888 country-year combinations (37 countries × 24 years)
  - LE model: 888 country-year combinations (37 countries × 24 years)
- **Target Variables**: 
  - `HALE_gap`: Female HALE - Male HALE (mean = 2.94 years) - **IHME source**
  - `LE_gap`: Female Life Expectancy - Male Life Expectancy (mean = 5.72 years) - **OWID source**
- **Predictors**: Gap columns only for each indicator (standardized across all country-year observations; Mid predictors excluded based on model comparison)

### Rationale for Using IHME HALE

**Why switch from WHO HALE to IHME HALE?**

1. **Methodological Consistency**: All predictor variables (alcohol, suicide, homicide, cardiovascular, etc.) come from IHME's Global Burden of Disease (GBD) database. Using IHME HALE ensures that the target variable and predictors are methodologically consistent, using the same data collection processes, estimation methods, and quality standards.

2. **Extended Temporal Coverage**: IHME HALE data extends through 2023, providing two additional years of post-acute-COVID data compared to WHO's 2021 cutoff. This allows us to assess whether COVID-19's effects on gender gaps persisted or attenuated in 2022-2023.

3. **Data Quality**: The correlation between WHO and IHME HALE is very high (r > 0.95), indicating excellent agreement. Both sources are high-quality, but IHME provides the advantages above.

4. **Reproducibility**: Using a single data source (IHME) for all cause-specific mortality measures and HALE improves transparency and reproducibility.

**Note on OWID Life Expectancy Data**: The Life Expectancy model now uses OWID data, which combines Human Mortality Database (HMD) and UN World Population Prospects. This provides extended temporal coverage through 2023 (vs 2021 for WHO), matching the IHME HALE temporal range. OWID LE shows high correlation with WHO LE (r = 0.993) and provides 100% complete data for all OECD countries.

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

**Life Expectancy Model (OWID data, 2000-2023):**
- All years 2000-2023 for OECD countries excluding Turkey
- Sample size: 888 country-year observations (37 countries × 24 years)

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
COVID-19 death rates are included as a predictor to assess how the pandemic affected gender gaps. COVID-19 data is available for 2020-2023 (IHME), with zeros for all years before 2020. Both HALE and LE models now include the full COVID period and post-acute recovery phase (2020-2023), enabling assessment of whether pandemic effects persisted or attenuated.

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
1. **Gap_RoadTraffic** (β = 0.464, 94% HDI: [0.425, 0.506]): The strongest predictor. Countries with larger male-female gaps in road traffic mortality have larger gender gaps in HALE.
2. **Gap_ChronicRespiratory** (β = 0.368, 94% HDI: [0.303, 0.427]): Gender gaps in chronic respiratory disease mortality show a strong association, **notably stronger than in the WHO-based 2021 model** (β = 0.301).
3. **Gap_Suicide** (β = 0.363, 94% HDI: [0.292, 0.427]): The third strongest predictor. Gender gaps in suicide mortality are strongly associated with gender gaps in HALE.
4. **Gap_Homicide** (β = 0.309, 94% HDI: [0.270, 0.347]): Gender gaps in homicide mortality are associated with HALE gaps, **weaker than in the WHO-based model** (β = 0.384).
5. **Gap_Neoplasms** (β = 0.237, 94% HDI: [0.153, 0.321]): Gender gaps in cancer mortality contribute to HALE gaps, **substantially weaker than in the WHO-based model** (β = 0.349).

**Moderate Positive Effects:**
- **Gap_UnintentionalInjury** (β = 0.195, 94% HDI: [0.131, 0.255]): Gender gaps in unintentional injury mortality contribute to HALE gaps, **stronger than in WHO model** (β = 0.152).
- **Gap_LiverDisease** (β = 0.191, 94% HDI: [0.138, 0.241]): Gender gaps in liver disease mortality contribute to HALE gaps, similar to WHO model (β = 0.209).
- **Gap_Alcohol** (β = 0.131, 94% HDI: [0.077, 0.184]): Gender gaps in alcohol-related mortality have a moderate positive effect, similar to WHO model (β = 0.145).
- **Gap_COVID** (β = 0.060, 94% HDI: [0.044, 0.075]): **COVID-19 gender gaps continue to have a small but positive effect on HALE gaps** through 2023, similar to the WHO-based 2021 model (β = 0.054).
- **Gap_DrugDisorder** (β = 0.056, 94% HDI: [0.024, 0.086]): Gender gaps in drug use disorder mortality have a small positive effect, **weaker than in WHO model** (β = 0.081).

**Negative Effects** (larger gender gaps in predictor → smaller HALE gap):
- **Gap_Cardiovascular** (β = -0.273, 94% HDI: [-0.316, -0.228]): This negative coefficient reflects a **competing risks** or **"risk of last resort"** mechanism. As Gap_Cardiovascular increases (men's CVD risk rises relative to women's), the female-male HALE gap tends to be smaller. This is because cardiovascular disease primarily affects people who have survived other causes. In settings where women's overall health is good, they survive other causes and live to older ages where CVD dominates, making Gap_Cardiovascular smaller and the HALE gap larger. **The effect is slightly stronger than in the WHO-based model** (β = -0.252).

- **Gap_Diabetes** (β = -0.130, 94% HDI: [-0.167, -0.093]): Similar to cardiovascular disease, diabetes follows a competing risks pattern. **The effect is nearly identical to the WHO-based model** (β = -0.129).

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
- **Data Source**: OWID Life Expectancy (HMD + UN WPP, extends through 2023)
- **Time Period**: 2000-2023 (24 years, matching IHME HALE temporal coverage)
- **Predictors**: Gap predictors only (12 predictors, including COVID-19)
- **Year Effects**: Not included
- **Countries**: OECD countries excluding Turkey (37 countries, 888 observations)
- **Model Performance**: WAIC = -143.57 (ELPD), LOO = -143.90 (ELPD), p_waic = 55.1, p_loo = 55.4

**Note**: The Life Expectancy model has been updated to use OWID LE data (2000-2023), which provides extended temporal coverage matching the IHME HALE model. OWID LE shows high correlation with WHO LE (r = 0.993) and extends the analysis through the post-acute COVID recovery period.

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with:
- Max R-hat = 1.01 (all parameters)
- Min ESS (bulk) = 807
- Excellent effective sample sizes (all > 800)

### Predictor Coefficients (Beta)

```{include} tables/beta_coefficients_le_ihme_nomid_nogrw_y2023_covid.html
```

**Key Findings:**
The pattern of coefficients for Life Expectancy is broadly similar to HALE, with some notable differences:
- **Homicide** is more important for LE (β = 0.440) than HALE (β = 0.309), suggesting homicide primarily affects lifespan rather than healthy years
- **COVID-19** shows a larger effect on LE (β = 0.108) than HALE (β = 0.060), indicating the pandemic affected overall lifespan more than healthy lifespan
- **Competing risk effects** are weaker for LE: Cardiovascular (β = -0.188) and Diabetes (β = -0.106) compared to HALE

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
| **Gap_Neoplasms** | 0.349 | 0.237 | **-0.112** | **Largest drop** - cancer gap effects weaker in IHME data or changing over time |
| **Gap_Homicide** | 0.384 | 0.309 | **-0.075** | **Major drop** - may reflect narrowing homicide gaps in recent years or methodological differences |
| **Gap_Suicide** | 0.424 | 0.363 | **-0.061** | Moderate decrease with IHME data |
| **Gap_ChronicRespiratory** | 0.301 | 0.368 | **+0.067** | **Increased** - respiratory disease gaps more important with IHME data/extended period |
| **Gap_UnintentionalInjury** | 0.152 | 0.195 | **+0.043** | Increased importance |
| **Gap_DrugDisorder** | 0.081 | 0.056 | **-0.025** | Reduced effect |
| **Gap_Cardiovascular** | -0.252 | -0.273 | **-0.021** | Slightly stronger protective (competing risk) effect |
| **Gap_LiverDisease** | 0.209 | 0.191 | -0.018 | Small decrease |
| **Gap_Alcohol** | 0.145 | 0.131 | -0.014 | Small decrease |
| **Gap_RoadTraffic** | 0.476 | 0.464 | -0.012 | Small decrease, remains strongest predictor |
| **Gap_COVID** | 0.054 | 0.060 | +0.006 | Slightly higher with 2 more years of data |
| **Gap_Diabetes** | -0.129 | -0.130 | **-0.001** | **Nearly identical** - remarkably stable |

**Key Observations:**

1. **Coefficient Stability**: Despite changing data sources (WHO → IHME HALE) and adding 2 years, most coefficients remain within 0.02-0.04 of their previous values, indicating robust relationships across datasets and time periods.

2. **Notable Shifts**:
   - **Neoplasms** (-0.112): Largest decrease suggests either methodological differences between WHO and IHME HALE or evolving cancer dynamics from 2021-2023
   - **Homicide** (-0.075): Major decrease may reflect narrowing violence gaps in recent years or measurement differences between data sources
   - **Chronic Respiratory** (+0.067): Increased importance, possibly due to COVID-19's lingering respiratory impact through 2023 or IHME methodology

3. **Remarkably Stable Predictors**:
   - **Diabetes** (-0.001): Nearly identical coefficient across data sources suggests very stable competing-risk relationship
   - **Road Traffic** (-0.012): Minimal change, remains the strongest predictor
   - **Cardiovascular** (-0.021): Competing risk effect remains consistent
   - **COVID-19** (+0.006): Similar effect with longer temporal coverage (2020-2023 vs 2020-2021)

4. **Model Performance**:
   - Both models achieve excellent fit (R² > 0.98)
   - IHME-based model has 74 more observations (888 vs 814) due to extended temporal range
   - Both models have similar number of effective parameters (~55-56)
   - Slightly different WAIC reflects different data sources and temporal coverage, not worse fit quality

### Life Expectancy Model: Extended Through 2023

The Life Expectancy model has been **updated with OWID LE data** (2000-2023), providing:
- Extended temporal coverage through 2023 (+2 years beyond WHO's 2021 cutoff)
- Matching temporal range with IHME HALE model (both now 2000-2023)
- 888 observations (37 countries × 24 years), up from 814 in the WHO-based model
- Data source: OWID combines Human Mortality Database and UN World Population Prospects
- High correlation with WHO LE (r = 0.993) confirms data quality

**Key LE Model Coefficients (2023, sorted by magnitude):**
- **Gap_RoadTraffic**: β = 0.446 [0.398, 0.492] - Strongest predictor
- **Gap_Homicide**: β = 0.440 [0.398, 0.485] - Second strongest
- **Gap_Suicide**: β = 0.364 [0.289, 0.441]
- **Gap_Neoplasms**: β = 0.313 [0.203, 0.409]
- **Gap_ChronicRespiratory**: β = 0.296 [0.230, 0.374]
- **Gap_Cardiovascular**: β = -0.188 [-0.240, -0.140] - Competing risk effect
- **Gap_COVID**: β = 0.108 [0.089, 0.127] - Larger effect than HALE model

The LE model coefficients are broadly consistent with the HALE model, with COVID-19 showing a larger effect on LE gaps (β = 0.108) than on HALE gaps (β = 0.060), suggesting the pandemic affected overall lifespan more than healthy lifespan.

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

- **Life Expectancy Gap Model** (OWID, 2000-2023): R² = 0.98-0.99
  - The model explains >98% of variance in LE gap across all country-years
  - MAE ≈ 0.19-0.22 years
  - Residual standard deviation ≈ 0.26-0.29 years

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

This section presents counterfactual analysis for the United States using **2023 as the reference year for both HALE and Life Expectancy** (the latest available year in both the IHME HALE and OWID LE datasets).

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

### Key Findings: USA Life Expectancy Gap (2023)

**Gap-Closing Factors** (negative values = reduce LE gap):

1. **Road Traffic** (-0.833 years [-0.919, -0.743]): The largest opportunity for reducing the LE gap, similar to HALE. If the USA could achieve Iceland's 2017 road traffic gender gap, the LE gap would shrink by over 0.8 years.

2. **Drug Disorders** (-0.770 years [-1.080, -0.464]): The second-largest factor for LE (vs third for HALE). Drug disorders have a **larger effect on LE than HALE** (0.77 vs 0.47 years), suggesting they affect lifespan more than healthy lifespan.

3. **Suicide** (-0.521 years [-0.632, -0.414]): Nearly identical effect to HALE (-0.522 years), showing suicide affects both lifespan and healthy lifespan equally.

4. **Homicide** (-0.289 years [-0.319, -0.262]): **Larger effect on LE than HALE** (0.29 vs 0.20 years), as homicides disproportionately affect younger individuals, reducing total lifespan more than healthy years.

5. **Liver Disease** (-0.215 years [-0.271, -0.167]): Slightly larger effect on LE than HALE (0.22 vs 0.16 years).

6. **Neoplasms** (-0.193 years [-0.252, -0.125]): **Larger effect on LE than HALE** (0.19 vs 0.15 years), suggesting cancer affects total lifespan more than healthy lifespan.

7. **Alcohol** (-0.159 years [-0.232, -0.085]): Similar to HALE effect (0.15 years).

8. **Unintentional Injury** (-0.063 years [-0.091, -0.035]): Similar to HALE effect (0.08 years).

9. **COVID-19** (-0.013 years [-0.015, -0.011]): By 2023, COVID-19's contribution is minimal but **nearly double the HALE effect** (0.013 vs 0.007 years), indicating the pandemic affected lifespan more than healthy lifespan.

**Gap-Widening Factors** (positive values = increase LE gap):

1. **Diabetes** (+0.232 years [0.132, 0.323]): Competing risk effect, **smaller for LE than HALE** (0.23 vs 0.28 years).

2. **Chronic Respiratory** (+0.175 years [0.136, 0.220]): Competing risk effect, **smaller for LE than HALE** (0.18 vs 0.22 years).

3. **Cardiovascular** (+0.157 years [0.116, 0.200]): Competing risk effect, **smaller for LE than HALE** (0.16 vs 0.23 years).

**Total Potential:**
- Sum of gap-closing factors: **≈3.1 years** (if all could be achieved simultaneously)
- Sum of gap-widening factors: **≈0.6 years** (competing risks)
- Net potential reduction: **≈2.5 years** from current USA LE gap

### Comparison: HALE vs LE Counterfactuals (2023)

**Key Differences:**

1. **Drug Disorders**: Much larger effect on LE (-0.770 years) than HALE (-0.467 years), a difference of **0.30 years**. This suggests drug-related deaths disproportionately reduce total lifespan compared to healthy years, possibly because they affect younger individuals who would otherwise have many healthy years ahead.

2. **Homicide**: Larger effect on LE (-0.289 years) than HALE (-0.203 years), a difference of **0.09 years**. Similar to drug disorders, homicides affect younger individuals, reducing total lifespan more than healthy years.

3. **Cardiovascular**: Larger competing-risk effect for HALE (+0.227 years) than LE (+0.157 years), a difference of **0.07 years**. This suggests cardiovascular disease disproportionately affects healthy years in older age.

4. **Diabetes**: Larger competing-risk effect for HALE (+0.281 years) than LE (+0.232 years), a difference of **0.05 years**. Similar pattern to cardiovascular disease.

5. **Suicide, Road Traffic, Alcohol**: Nearly identical effects for both HALE and LE, indicating these factors affect lifespan and healthy lifespan proportionally.

**Overall Pattern:**
- **Causes affecting younger individuals** (drug disorders, homicide) have larger effects on LE than HALE
- **Competing-risk causes in older age** (diabetes, cardiovascular) have larger effects on HALE than LE
- **Behavioral/external causes** (suicide, road traffic, alcohol) affect both outcomes proportionally
- **Net potential gap reduction is larger for LE (2.5 years) than HALE (1.7 years)**, reflecting the larger effects of drug disorders and homicide on total lifespan

### Counterfactual Effects for All Indicators

**HALE Gap Counterfactuals (2023):**

```{include} tables/counterfactuals_usa_2023_hale_bayesian.html
```

**Life Expectancy Gap Counterfactuals (2023):**

```{include} tables/counterfactuals_usa_2023_le_bayesian.html
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

**Life Expectancy Gap (2023):**

```{figure} figs/counterfactual_effects_usa_2023_le_bayesian.png
:name: counterfactual_le_2023
:width: 100%

Forest plot showing counterfactual effects for USA Life Expectancy gap (2023) with 94% credible intervals.
```

```{figure} figs/counterfactual_effects_usa_2023_le_by_type_bayesian.png
:name: counterfactual_le_2023_by_type
:width: 100%

Two-panel plot separating gap-closing (left) and gap-widening (right) factors for USA Life Expectancy gap (2023).
```

```{figure} figs/counterfactual_effects_usa_2023_le_bar_bayesian.png
:name: counterfactual_le_2023_bar
:width: 100%

Bar chart of counterfactual effects sorted by magnitude for USA Life Expectancy gap (2023).
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

**Life Expectancy Gap - Positive Contributions Over Time (OWID, 2000-2023):**

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:name: positive_contributions_le_2023
:width: 100%

Stacked area chart showing contributions of gap-closing factors over time for USA Life Expectancy gap (2000-2023). The extended temporal range now includes the full COVID period and post-acute recovery.
```

```{include} tables/positive_contributions_usa_le_over_time.html
```

```{figure} figs/positive_contributions_percentage_usa_le.png
:name: positive_contributions_percentage_le_2023
:width: 100%

Percentage of actual Life Expectancy gap explained by positive-contributing (gap-closing) factors over time through 2023.
```

## Conclusions

### Key Findings

1. **Successful Data Source Transition**: The switch from WHO HALE to IHME HALE was successful, maintaining methodological consistency with all predictor variables while extending temporal coverage to 2023.

2. **Extended COVID-19 Period**: Including 2022-2023 data shows that COVID-19's effect on gender gaps persisted into the post-acute phase, with a small but consistent positive coefficient (β = 0.060).

3. **Coefficient Stability with Notable Shifts**: Most coefficients remained stable when switching data sources, but three showed substantial changes:
   - **Neoplasms decreased** (-0.112): Cancer gaps may be less important in IHME data or evolved 2021-2023
   - **Homicide decreased** (-0.075): Violence gaps may be narrowing or measured differently
   - **Chronic Respiratory increased** (+0.067): Respiratory disease gaps became more important, possibly due to COVID-19's long-term effects

4. **Diabetes Coefficient Nearly Identical**: The diabetes coefficient was virtually unchanged (β = -0.129 → -0.130), demonstrating a remarkably robust competing-risk relationship across data sources.

5. **Model Performance**: Both IHME-based HALE and OWID-based LE models achieve excellent fit (R² > 0.98), explaining nearly all systematic variation in gender gaps across all country-years.

6. **Aligned Temporal Coverage**: Both models now span 2000-2023 with 888 observations each, enabling direct comparison of HALE vs LE gap drivers throughout the full COVID period and post-acute recovery phase.

### Advantages of IHME HALE and OWID LE Data

**IHME HALE:**
1. **Methodological Consistency**: All variables (HALE and predictors) come from the same IHME GBD methodology
2. **Extended Temporal Range**: Two additional years (2022-2023) beyond WHO capture post-acute COVID dynamics
3. **No Extreme Outliers**: Unlike WHO data (Israel 2021), IHME data showed no extreme residuals
4. **Maintained Quality**: High correlation with WHO HALE (r > 0.95) confirms data quality

**OWID LE:**
1. **Extended Temporal Coverage**: Extends through 2023, matching IHME HALE temporal range (vs 2021 for WHO LE)
2. **Complete OECD Coverage**: 100% complete data for all 38 OECD countries including Turkey
3. **High-Quality Sources**: Combines authoritative data from Human Mortality Database and UN World Population Prospects
4. **Validated Quality**: High correlation with WHO LE (r = 0.993) confirms excellent agreement
5. **Temporal Alignment**: Both HALE and LE models now span identical time periods (2000-2023)

### Limitations and Future Work

1. **Data Source Differences**: Some coefficient changes may reflect methodological differences between WHO HALE and IHME HALE rather than temporal evolution. Similarly, OWID LE combines multiple sources (HMD + UN WPP) vs WHO's direct estimates. Future work could decompose these methodological effects.

2. **Limited Post-COVID Data**: Only 4 years of COVID data (2020-2023) limits assessment of long-term pandemic effects. As more post-2023 data becomes available, tracking whether coefficient shifts persist will be valuable.

3. **Turkey Exclusion**: Turkey is excluded from this analysis because it was identified as an outlier with very low likelihood in the Bayesian model. This decision was made based on model diagnostics, not data availability.

4. **OWID vs WHO LE Comparison**: OWID LE shows high correlation with WHO LE (r = 0.993) but some country-year combinations differ by up to 3 years. Most differences are within expected bounds for different estimation methodologies.

### Recommendations

1. **Continue with IHME HALE**: Maintain IHME HALE as the primary target for future analyses to ensure methodological consistency with IHME predictors and maximize temporal coverage.

2. **Continue with OWID LE**: Use OWID LE data for extended temporal coverage matching IHME HALE. The high correlation with WHO LE (r = 0.993) confirms data quality while providing the advantage of complete temporal alignment.

3. **Monitor Coefficient Evolution**: As more post-2023 data becomes available, track whether the coefficient shifts (especially Neoplasms and Chronic Respiratory) represent lasting changes or transient effects.

4. **Update Annually**: As IHME updates its GBD database and OWID incorporates new UN WPP data, rerun models to incorporate new data and assess temporal stability.

5. **Investigate Respiratory Disease**: The increased importance of chronic respiratory disease gaps warrants further investigation, particularly regarding COVID-19's long-term respiratory effects through 2023.

6. **COVID-19 Effect Monitoring**: The larger COVID effect in LE (β = 0.108) vs HALE (β = 0.060) suggests pandemic impacts on lifespan exceeded impacts on healthy lifespan. Monitor whether this pattern persists or changes in future years.

7. **Age-Dependent Effects**: Counterfactual analysis reveals that causes affecting younger individuals (drug disorders, homicide) have larger effects on LE than HALE, while competing-risk causes in older age (diabetes, cardiovascular) have larger effects on HALE than LE. This pattern provides insights into how different causes affect lifespan vs healthy lifespan across the life course.


