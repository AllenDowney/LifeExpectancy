# Bayesian Panel Data Model: Analysis of HALE and Life Expectancy Gender Gaps

## Purpose

This report presents results from a Bayesian hierarchical panel model that analyzes gender gaps in Healthy Life Expectancy (HALE) and Life Expectancy using both temporal variation (2000-2019) and cross-country variation simultaneously. Unlike the cross-sectional Elastic Net models, this panel approach leverages data from all country-year combinations, providing more statistical power and allowing us to assess whether predictors that matter cross-sectionally also matter within countries over time.

**Key Questions Addressed:**
- Do the same predictors that matter cross-sectionally also matter within countries over time?
- Does alcohol matter because countries differ from each other, or because countries that reduce alcohol mortality see their gaps narrow?
- Do predictors (e.g., cardiovascular mortality) predict gaps within a country over time?
- How do Bayesian posterior estimates compare to the cross-sectional Elastic Net coefficients?

## Model Design

### Data Structure

The panel dataset transforms from country-level (one row per country) to panel structure (one row per country-year):

- **Time Period**: 2000-2019 (excluding 2020+ to avoid COVID-19 pandemic distortions)
- **Countries**: OECD countries (38 countries)
- **Observations**: Approximately 760 country-year combinations (38 countries × 20 years)
- **Target Variables**: 
  - `HALE_gap`: Female HALE - Male HALE (in years, positive means women live longer)
  - `LE_gap`: Female Life Expectancy - Male Life Expectancy (in years, positive means women live longer)
- **Predictors**: All Mid and Gap columns for each indicator (standardized across all country-year observations)

### Standardization Strategy

**Predictors (Standardized - Full Z-Scores):**
- For each predictor `X_j` (both Mid and Gap versions):
  - Compute mean `X̄_j` and standard deviation `s_j` across **all country-year observations** in the panel (OECD, 2000-2019)
  - Transform to z-scores: `X*_{ijt} = (X_{ijt} - X̄_j) / s_j`
- **Important**: 
  - Do **not** standardize within country or within year
  - Use a **single global transformation** for the entire panel (2000-2019)
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
- `X*_{it}` = vector of standardized predictors (Mid + Gap columns, z-scores across full panel)
- `α_i` = country-specific random intercept
- `β` = shared slope coefficients (same across all countries)
- `t` ∈ 2000–2019

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

4. **Computationally feasible**: With ≈ 760 observations and 12–18 predictors, a hierarchical linear model runs efficiently in PyMC using the nutpie sampler.

5. **Uses both within-country and between-country variation**: Unlike fixed-effects models that eliminate all between-country variation, this approach leverages both sources of information.

6. **Controls for time-invariant country-level factors**: Random intercepts account for country-specific characteristics (culture, baseline health systems, risk environments) that don't change over time.

### Why Not Fixed Effects or Random Slopes?

**Why Not Fixed Effects:**
- Fixed-effects models eliminate all between-country variation, which we know is large and informative
- Uses only within-country variation (changes over time), discarding valuable cross-country information

**Why Not Random Slopes (Initially):**
- Random slopes require much more data per country than available (≈20 years × OECD ≈ 38 countries)
- Estimating slope variance would be unstable and will obscure interpretation
- Can be added later if needed (see Model Extensions below)

## Model Implementation

### Software and Methods

- **Bayesian Inference**: PyMC (Python) with nutpie sampler
- **MCMC Sampling**: 4 chains with default tuning and draws
- **Convergence Diagnostics**: R-hat, effective sample size (ESS)
- **Posterior Analysis**: ArviZ for diagnostics and visualization

### Data Preparation

The panel dataset includes:
- All years 2000-2019 for each OECD country
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
- Both Mid (overall rate) and Gap (gender difference) columns for each indicator
- Complete panel: No missing data

## Results: HALE Gap Model

### Model Diagnostics

```{include} tables/beta_coefficients_hale.html
```

```{include} tables/alpha_coefficients_hale.html
```

### Posterior Distributions

The following forest plots show the posterior distributions of predictor coefficients and country-specific intercepts:

```{figure} figs/posterior_forest_beta_hale.png
:name: beta_forest_hale
:width: 100%

Posterior Distributions of Predictor Coefficients (HALE Gap)
```

```{figure} figs/posterior_forest_alpha_hale.png
:name: alpha_forest_hale
:width: 100%

Posterior Distributions of Country-Specific Intercepts (HALE Gap)
```

### Posterior Correlations

**Top 10 Correlations Among Beta Coefficients (Predictor Slopes):**

```{include} tables/beta_correlations_top10_hale.html
```

**Top 10 Correlations Among Alpha Coefficients (Country Intercepts):**

```{include} tables/alpha_correlations_top10_hale.html
```

**Summary of Posterior Correlations (HALE Gap Model):**

**Beta Correlations (Predictor Slopes):**
- **Very high negative correlations** (r ≈ -0.9 to -1.0) between Mid and Gap for the same indicator:
  - Homicide: r = -0.998
  - Alcohol: r = -0.973
  - Liver Disease: r = -0.95
  - Road Traffic: r = -0.944
  - Suicide: r = -0.885
- This pattern indicates that when overall rates (Mid) are high, gender gaps (Gap) tend to be low, and vice versa. This is expected: when a cause of death is rare overall, small absolute differences between genders can appear as large relative gaps.
- **Moderate correlations** between different predictors:
  - Mid_Alcohol and Gap_UnintentionalInjury: r = -0.448 (suggesting alcohol-related patterns)
  - Mid_Neoplasms and Mid_UnintentionalInjury: r = -0.431
  - Gap_Alcohol and Gap_UnintentionalInjury: r = 0.39 (positive correlation between gender gaps)

**Alpha Correlations (Country Intercepts):**
- **Baltic States cluster**: High positive correlations (r ≈ 0.67-0.72) between Estonia (EST), Latvia (LVA), and Lithuania (LTU), suggesting similar unmeasured country-level factors affecting gender gaps.
- **Latin American cluster**: High positive correlations (r ≈ 0.62-0.68) between Chile (CHL), Colombia (COL), Costa Rica (CRI), and Mexico (MEX), indicating shared regional characteristics.
- **Strong negative correlation**: Hungary (HUN) and Israel (ISR) show r = -0.647, suggesting opposite patterns in their country-specific effects.
- These correlations reflect shared cultural, economic, or health system factors that affect gender gaps similarly within regions.

### Comparison with Cross-Sectional Elastic Net Model

The following visualization compares Bayesian posterior distributions with Elastic Net point estimates for the top predictors:

```{figure} figs/bayesian_elasticnet_comparison_hale.png
:name: comparison_hale
:width: 100%

Bayesian Posterior Distributions vs Elastic Net Coefficients (HALE Gap)
```

**Key Observations:**
- The figure shows posterior distributions (with 95% HDI) for each predictor coefficient
- Blue dashed line: Elastic Net coefficient (point estimate)
- Green solid line: Bayesian posterior mean
- Green shaded region: 95% highest density interval (HDI)
- When the Elastic Net coefficient falls within the Bayesian HDI, it suggests agreement between the two approaches
- When the Elastic Net coefficient falls outside the HDI, it may indicate differences in how the models interpret the data

## Results: Life Expectancy Gap Model

### Model Diagnostics

```{include} tables/beta_coefficients_le.html
```

```{include} tables/alpha_coefficients_le.html
```

### Posterior Distributions

The following forest plots show the posterior distributions of predictor coefficients and country-specific intercepts:

```{figure} figs/posterior_forest_beta_le.png
:name: beta_forest_le
:width: 100%

Posterior Distributions of Predictor Coefficients (Life Expectancy Gap)
```

```{figure} figs/posterior_forest_alpha_le.png
:name: alpha_forest_le
:width: 100%

Posterior Distributions of Country-Specific Intercepts (Life Expectancy Gap)
```

### Posterior Correlations

**Top 10 Correlations Among Beta Coefficients (Predictor Slopes):**

```{include} tables/beta_correlations_top10_le.html
```

**Top 10 Correlations Among Alpha Coefficients (Country Intercepts):**

```{include} tables/alpha_correlations_top10_le.html
```

**Summary of Posterior Correlations (Life Expectancy Gap Model):**

**Beta Correlations (Predictor Slopes):**
- **Very high negative correlations** (r ≈ -0.9 to -1.0) between Mid and Gap for the same indicator, similar to HALE model:
  - Homicide: r = -0.998
  - Alcohol: r = -0.974
  - Liver Disease: r = -0.952
  - Road Traffic: r = -0.941
  - Suicide: r = -0.889
- The same pattern holds: high overall rates are associated with smaller gender gaps in absolute terms.
- **Moderate correlations** between different predictors:
  - Mid_Alcohol and Gap_UnintentionalInjury: r = -0.453
  - Mid_Neoplasms and Mid_UnintentionalInjury: r = -0.447
  - Gap_Alcohol and Gap_UnintentionalInjury: r = 0.396
  - Gap_Cardiovascular and Gap_Neoplasms: r = -0.388

**Alpha Correlations (Country Intercepts):**
- **Baltic States cluster**: High positive correlations (r ≈ 0.68-0.73) between Estonia (EST), Latvia (LVA), and Lithuania (LTU), consistent with HALE model.
- **Latin American cluster**: High positive correlations (r ≈ 0.65-0.71) between Chile (CHL), Colombia (COL), Costa Rica (CRI), and Mexico (MEX), similar to HALE model.
- **Strong negative correlation**: Hungary (HUN) and Israel (ISR) show r = -0.663, consistent with HALE model.
- **Additional cluster**: Denmark (DNK) and United Kingdom (GBR) show r = 0.617, suggesting shared characteristics in these Northern European countries.
- The patterns are remarkably consistent between HALE and Life Expectancy models, indicating robust regional and country-level effects.

### Comparison with Cross-Sectional Elastic Net Model

The following visualization compares Bayesian posterior distributions with Elastic Net point estimates for the top predictors:

```{figure} figs/bayesian_elasticnet_comparison_le.png
:name: comparison_le
:width: 100%

Bayesian Posterior Distributions vs Elastic Net Coefficients (Life Expectancy Gap)
```

## Interpretation

### Coefficient Estimates

**Comparison with Cross-Sectional Model:**
- The Bayesian panel model provides posterior distributions for each coefficient, allowing us to assess uncertainty
- When Elastic Net coefficients fall within the Bayesian 95% HDI, it suggests the cross-sectional relationships are robust to temporal analysis
- Differences between the two approaches may indicate:
  - **Temporal effects**: Predictors that matter cross-sectionally may not predict changes within countries over time. If a predictor shows a strong cross-sectional relationship but a weak or null relationship in the panel model, it suggests the effect is primarily due to between-country differences rather than within-country changes.
  - **Shrinkage**: Bayesian priors may shrink coefficients toward zero compared to Elastic Net, especially for predictors with less evidence. This is a feature, not a bug—it reflects uncertainty and prevents overfitting.
  - **Sample size**: Panel model uses more data (≈760 observations vs ≈38 countries), potentially providing more stable estimates with narrower credible intervals.
  - **Regularization differences**: Elastic Net uses L1/L2 penalties, while Bayesian model uses hierarchical priors. Both regularize, but in different ways.

**Key Interpretations:**
- **Coefficients in standardized space**: Since predictors are standardized (z-scores), a coefficient of β = 0.5 means that a 1-standard-deviation increase in the predictor is associated with a 0.5-year increase in the gender gap (in the original units of years).
- **Sign of coefficients**: 
  - For Gap predictors (Male - Female): Positive coefficients mean that larger male-female gaps in the predictor are associated with larger gaps in HALE/LE (women live longer).
  - For Mid predictors (overall rates): Positive coefficients mean that higher overall rates are associated with larger gender gaps in HALE/LE.
- **Credible intervals**: The 95% HDI provides a range of plausible values. If the HDI excludes zero, we can be confident the effect is non-zero (though this is not a formal hypothesis test).

### Posterior Correlations

**Beta Correlations (Predictor Slopes):**
- High correlations (|r| > 0.7) between predictor coefficients indicate that the effects are difficult to estimate independently
- This is expected for related predictors (e.g., Mid and Gap for the same indicator, or indicators that tend to co-occur)
- High correlations may also indicate multicollinearity, suggesting that some predictors capture similar information
- **Interpretation**: When two predictors are highly correlated in their posterior distributions, it means the model cannot easily distinguish their individual effects. This is informative—it suggests these predictors may be measuring similar underlying constructs or may have similar relationships with the outcome.
- **Policy implications**: If two predictors are highly correlated, interventions targeting one may also affect the other, making it difficult to isolate their individual impacts.

**Alpha Correlations (Country Intercepts):**
- High correlations between country intercepts indicate that countries with similar baseline gaps tend to have similar country-specific effects
- This may reflect shared cultural, economic, or health system characteristics
- Countries with highly correlated intercepts may benefit from similar policy interventions
- **Geographic clustering**: If neighboring countries or countries with similar economic development have highly correlated intercepts, it suggests regional or economic factors play a role beyond the measured predictors.
- **Cultural factors**: High correlations may reflect unmeasured cultural factors that affect gender gaps similarly across countries.

### Country-Specific Intercepts

The alpha coefficients represent country-specific random intercepts, capturing:
- Time-invariant country characteristics that affect gender gaps
- Baseline differences between countries after accounting for predictor variables
- Cultural, economic, or health system factors that don't change over time

Countries with:
- **High positive intercepts**: Have larger gender gaps than predicted by the model (women live longer than expected given their predictor values). This suggests unmeasured factors (e.g., cultural norms, healthcare access, social policies) that favor longer female life expectancy.
- **Low negative intercepts**: Have smaller gender gaps than predicted (gaps are narrower than expected given their predictor values). This suggests factors that reduce the gender gap beyond what the predictors explain.

**Interpretation of Intercept Variation:**
- The `sigma_alpha` parameter quantifies how much countries differ in their baseline gaps after accounting for predictors
- A large `sigma_alpha` indicates substantial country heterogeneity that is not explained by the measured predictors
- A small `sigma_alpha` suggests that the predictors capture most of the between-country variation

### Model Performance

The panel model leverages both:
- **Between-country variation**: Differences in predictor values and gaps across countries
- **Within-country variation**: Changes in predictor values and gaps over time within each country

This dual-source approach provides:
- More statistical power than cross-sectional models (≈760 observations vs ≈38 countries)
- Ability to assess whether predictors matter both cross-sectionally and temporally
- Uncertainty quantification through posterior distributions
- Framework for temporal counterfactual analysis

**Advantages over Cross-Sectional Models:**
1. **Temporal validation**: Can assess whether cross-sectional relationships hold when examining changes over time
2. **Reduced confounding**: By using both between- and within-country variation, the model can better isolate true causal relationships
3. **Uncertainty quantification**: Provides full posterior distributions, not just point estimates
4. **Counterfactual framework**: Enables prediction of how gaps would change if predictors changed, with uncertainty bands

**Limitations:**
1. **Assumes shared slopes**: All countries have the same relationship between predictors and gaps. This may not hold if relationships vary substantially by country.
2. **No time trends**: The basic model does not account for global temporal trends that affect all countries (e.g., overall health improvements). Year fixed effects can be added to address this.
3. **No temporal autocorrelation**: Assumes independence across years within countries. AR(1) structure can be added if needed.

## Model Extensions (Future Work)

After implementing the basic random-intercept model, potential extensions include:

**(A) Predictor Selection Based on Correlations:**
- **Problem**: The posterior correlations reveal very high negative correlations (r ≈ -0.9 to -1.0) between Mid and Gap predictors for the same indicator (Homicide, Alcohol, Liver Disease, Road Traffic, Suicide). This suggests the model cannot easily distinguish the individual contributions of these paired predictors.
- **Hypothesis**: When Mid and Gap for the same indicator are highly correlated in their posterior distributions, it may indicate that:
  - The two predictors capture redundant information
  - The model cannot reliably separate their effects
  - Removing one (likely the Mid predictor) may simplify the model without losing predictive power
- **Approach**:
  1. **Compute fit metrics** for the current full model:
     - WAIC (Widely Applicable Information Criterion)
     - LOO-CV (Leave-One-Out Cross-Validation)
     - Posterior predictive checks
     - R² and RMSE
  2. **Test a series of reduced models** by removing Mid predictors for indicators where Mid-Gap correlation exceeds a threshold (e.g., |r| > 0.9):
     - Model 1: Remove Mid_Homicide (keep Gap_Homicide)
     - Model 2: Remove Mid_Alcohol (keep Gap_Alcohol)
     - Model 3: Remove Mid_LiverDisease (keep Gap_LiverDisease)
     - Model 4: Remove Mid_RoadTraffic (keep Gap_RoadTraffic)
     - Model 5: Remove Mid_Suicide (keep Gap_Suicide)
     - Model 6: Remove all highly correlated Mid predictors simultaneously
  3. **Compare models** using:
     - WAIC/LOO differences (ΔWAIC, ΔLOO)
     - Posterior predictive checks
     - Coefficient stability (do remaining coefficients change substantially?)
     - Predictive performance on held-out data
- **Rationale**: If removing Mid predictors does not meaningfully worsen model fit, it suggests that Gap predictors capture the relevant information and Mid predictors add little beyond what is already explained. This would simplify interpretation and potentially improve coefficient estimates by reducing multicollinearity.

**(B) Year Fixed Effects:**
- Add `γ_t` to model: `y*_{it} = α_i + γ_t + X*_{it}β + ε_{it}`
- Controls for global temporal trends (e.g., global health improvements affecting all countries)
- Test whether this improves model fit (WAIC/LOO comparison)

**(C) AR(1) Structure:**
- Add autoregressive structure on residuals or intercepts
- Models temporal autocorrelation (year-to-year persistence)
- May improve predictions if residuals are correlated over time

**(D) Random Slopes:**
- Allow coefficients to vary by country: `β_i ~ N(μ_β, σ_β)`
- Test whether random slopes improve WAIC/LOO
- Only add if there is sufficient evidence that relationships vary by country

## Conclusions

The Bayesian panel model provides a complementary perspective to the cross-sectional Elastic Net models by:

1. **Leveraging temporal variation**: Uses data from all years (2000-2019) rather than just the most recent year
2. **Quantifying uncertainty**: Provides posterior distributions with credible intervals for all parameters
3. **Accounting for country heterogeneity**: Random intercepts capture time-invariant country-specific factors
4. **Enabling temporal counterfactuals**: Framework for predicting effects of changes over time with uncertainty bands

Key findings will be documented as results become available from the model fitting process.

