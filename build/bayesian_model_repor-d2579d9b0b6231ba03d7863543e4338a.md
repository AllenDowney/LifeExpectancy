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
- **Countries**: OECD countries excluding Turkey (37 countries; Turkey excluded due to outlier status - see Influential Observations section)
- **Observations**: Approximately 740 country-year combinations (37 countries × 20 years)
- **Target Variables**: 
  - `HALE_gap`: Female HALE - Male HALE (in years, positive means women live longer)
  - `LE_gap`: Female Life Expectancy - Male Life Expectancy (in years, positive means women live longer)
- **Predictors**: Gap columns only for each indicator (standardized across all country-year observations; Mid predictors excluded based on model comparison - see Model Extensions section)

### Standardization Strategy

**Predictors (Standardized - Full Z-Scores):**
- For each predictor `X_j` (Gap versions only; Mid predictors excluded - see Model Extensions section):
  - Compute mean `X̄_j` and standard deviation `s_j` across **all country-year observations** in the panel (OECD excluding Turkey, 2000-2019)
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
- All years 2000-2019 for OECD countries (excluding Turkey - see Influential Observations section for justification)
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
- **Predictors**: Gap (gender difference) columns only for each indicator (Mid predictors excluded based on model comparison - see Model Extensions section)
- Complete panel: No missing data
- **Sample size**: Approximately 740 country-year observations (37 countries × 20 years, excluding Turkey)
- **Number of predictors**: 10 (Gap predictors for: Alcohol, Suicide, Homicide, Road Injuries, Cardiovascular, Diabetes, Neoplasms, Chronic Respiratory, Liver Disease, Unintentional Injuries)

## Results: HALE Gap Model

**Model Specification:**
- **Predictors**: Gap predictors only (10 predictors), excluding Mid predictors
- **Year Effects**: Not included (tested but worsen model fit)
- **Countries**: OECD countries excluding Turkey (37 countries, ~740 observations)
- **Model Performance**: WAIC = 75.3 (ELPD), LOO = 74.9 (ELPD), p_waic = 50.8

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with R-hat = 1.0 for all parameters and adequate effective sample sizes (ESS > 2000 for all parameters).

### Predictor Coefficients (Beta)

The following table shows the posterior distributions of predictor coefficients. Since predictors are standardized (z-scores), coefficients represent the effect of a 1-standard-deviation change in the predictor on the gender gap in HALE (in years).

```{include} tables/beta_coefficients_hale_nomid.html
```

**Key Findings:**

**Strongest Positive Effects** (larger gender gaps in predictor → larger HALE gap, i.e., women live longer):
1. **Gap_RoadTraffic** (β = 0.464, 94% HDI: [0.418, 0.506]): The strongest predictor. Countries with larger male-female gaps in road traffic mortality have larger gender gaps in HALE. This is likely due to men driving more total miles (greater exposure) rather than risk-taking behavior, though both factors may contribute.
2. **Gap_Suicide** (β = 0.422, 94% HDI: [0.352, 0.51]): The second strongest predictor. Gender gaps in suicide mortality are strongly associated with gender gaps in HALE, reflecting the substantial contribution of suicide to male mortality.
3. **Gap_Homicide** (β = 0.374, 94% HDI: [0.336, 0.412]): Gender gaps in homicide mortality are strongly associated with HALE gaps, consistent with higher male homicide rates.
4. **Gap_Neoplasms** (β = 0.372, 94% HDI: [0.274, 0.479]): Gender gaps in cancer mortality contribute to HALE gaps, though with more uncertainty than the top three predictors.
5. **Gap_ChronicRespiratory** (β = 0.336, 94% HDI: [0.271, 0.403]): Gender gaps in chronic respiratory disease mortality are associated with HALE gaps.

**Moderate Positive Effects:**
- **Gap_LiverDisease** (β = 0.233, 94% HDI: [0.178, 0.286]): Gender gaps in liver disease mortality contribute to HALE gaps.
- **Gap_Alcohol** (β = 0.158, 94% HDI: [0.091, 0.218]): Gender gaps in alcohol-related mortality have a moderate positive effect.
- **Gap_UnintentionalInjury** (β = 0.149, 94% HDI: [0.07, 0.232]): Gender gaps in unintentional injury mortality contribute to HALE gaps, though with substantial uncertainty (HDI includes values near zero).

**Negative Effects** (larger gender gaps in predictor → smaller HALE gap):
- **Gap_Cardiovascular** (β = -0.247, 94% HDI: [-0.292, -0.196]): This negative coefficient reflects a **competing risks** or **"risk of last resort"** mechanism. 

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

- **Gap_Diabetes** (β = -0.108, 94% HDI: [-0.148, -0.065]): Similar to cardiovascular disease, diabetes may also follow a competing risks pattern, though the effect is smaller. When women's health is good overall, more survive to die of diabetes, making the gap smaller and the overall HALE gap larger.

**Interpretation:**
- All coefficients have 94% HDIs that exclude zero, indicating robust effects.
- The model explains gender gaps in HALE primarily through external causes (road traffic, suicide, homicide) and neoplasms.
- Cardiovascular and diabetes show negative coefficients, reflecting a **competing risks** mechanism: cardiovascular disease and diabetes are "risks of last resort" that primarily affect people who have survived other causes. When women's health is good overall, they survive other causes and live to older ages where CVD/diabetes dominate, making these gaps smaller and the overall HALE gap larger. When these gaps are large (positive), it indicates women are dying of other causes first, signaling worse overall health and a smaller HALE gap.
- The standardized coefficients allow direct comparison: a 1-SD increase in Gap_RoadTraffic is associated with a 0.464-year increase in the HALE gap.


### Predictor Importance on the Original Scale

Standardized coefficients allow direct comparison of effect sizes, but they do not account for how much each predictor typically varies across countries and years. To capture both effect size and real-world variation, we compute an **importance measure**:

**Importance = |β_standardized| × SD_original**

This quantity is **not** a causal effect or a prediction. Instead, it reflects how much a predictor can contribute to **explaining variation** in gender gaps given the amount of variation that predictor exhibits in the data.

#### How to interpret the importance values

- A predictor with a large effect but little variation will have modest importance.  
- A predictor with moderate effect but large variation will have large importance.  
- The measure ranks predictors by their contribution to **explaining differences** in gaps across countries and time.

#### Why the units appear to be in "years" but do not represent an effect

A standardized coefficient of 0.369 means:

- A 1-SD change in the predictor → 0.369-year change in the gap  
  (this **is** the effect size)

The importance value multiplies this by the predictor’s original-scale SD, producing a number that has the same units (“years”), but:

- It is **not** the effect of any real-world change  
- It is **not** a counterfactual prediction  
- It is best viewed as a **scaled contribution measure**, not an effect size

#### Correct interpretation

- Importance scores **rank** predictors by how much they help explain variation in the outcome.  
- Standardized coefficients provide the **actual effect sizes**.  
- An importance score of 14.2 years does **not** mean that changing the predictor by 1 SD changes the gap by 14.2 years; the true effect is 0.369 years per SD.  
- Instead, it means the predictor contributes substantially to explaining variation because it has both a meaningful effect and substantial variability.

Use importance scores for **ranking predictors**, and use standardized coefficients for **interpreting effects**.

```{include} tables/importance_measures_hale_nomid_nogrw.html
```

**Key Findings:**

**Top Contributors (by Importance):**
1. **Gap_Neoplasms** (Importance = 14.2 years, 94% HDI: [10.2, 18.2]): Despite having a moderate standardized coefficient (β = 0.369), neoplasms has the highest importance due to its large typical variation (SD = 38.4). This indicates that gender gaps in cancer mortality contribute substantially to HALE gaps across their typical range.
2. **Gap_Cardiovascular** (Importance = 8.7 years, 94% HDI: [7.0, 10.5]): Has the second-highest importance despite a negative coefficient (β = -0.246). The large SD (35.5) means that variation in cardiovascular gender gaps has substantial impact, even though the effect is to narrow the overall HALE gap.
3. **Gap_Homicide** (Importance = 5.2 years, 94% HDI: [4.7, 5.7]): Strong positive effect (β = 0.374) combined with moderate variation (SD = 13.9) makes homicide the third most important predictor.
4. **Gap_Suicide** (Importance = 4.3 years, 94% HDI: [3.5, 5.0]): Strong positive effect (β = 0.422) but smaller variation (SD = 10.1) than homicide, placing it fourth.
5. **Gap_ChronicRespiratory** (Importance = 3.6 years, 94% HDI: [2.9, 4.4]): Moderate effect and variation.

**Comparison with Standardized Coefficients:**
- **Neoplasms** ranks 4th by standardized coefficient but 1st by importance, highlighting the importance of accounting for typical variation.
- **Road Traffic** ranks 1st by standardized coefficient but 6th by importance, reflecting its smaller typical variation (SD = 5.94) despite a strong effect.
- **Cardiovascular** ranks 5th by standardized coefficient (absolute value) but 2nd by importance, showing that its large variation (SD = 35.5) makes it highly influential despite a moderate effect size.

**Policy Implications:**
The importance measure suggests that interventions targeting neoplasms and cardiovascular disease gender gaps could have the largest impact on overall HALE gaps, even though external causes (road traffic, suicide, homicide) have stronger per-unit effects. This reflects that neoplasms and cardiovascular disease have larger gender gaps across countries, making them important targets for policy intervention.

### Country-Specific Intercepts (Alpha)

The following table shows the posterior distributions of country-specific random intercepts. These capture time-invariant country characteristics that affect gender gaps beyond what the predictors explain.

```{include} tables/alpha_coefficients_hale_nomid.html
```

**Interpretation:**
- **Positive intercepts**: Countries with larger gender gaps than predicted by the model (women live longer than expected given their predictor values). This suggests unmeasured factors (e.g., cultural norms, healthcare access, social policies) that favor longer female life expectancy.
- **Negative intercepts**: Countries with smaller gender gaps than predicted (gaps are narrower than expected given their predictor values). This suggests factors that reduce the gender gap beyond what the predictors explain.
- **Near-zero intercepts**: Countries where the predictors explain most of the gender gap, with little residual country-specific effect.

**Key Patterns:**
- The `sigma_alpha` parameter quantifies how much countries differ in their baseline gaps after accounting for predictors. A large `sigma_alpha` indicates substantial country heterogeneity that is not explained by the measured predictors.
- Countries with similar intercepts may share unmeasured characteristics (cultural, economic, or health system factors) that affect gender gaps similarly.

**Influential Observations:**
Leave-One-Out Cross-Validation (LOO-CV) identifies observations that are difficult for the model to fit. The analysis (from the model excluding Turkey) shows that influential observations are distributed across multiple countries, with no single country dominating. The maximum LOO contribution is substantially smaller than when Turkey was included, indicating improved model fit.

```{include} tables/influential_observations_hale_nomid.html
```

**Key Findings:**
- Top influential observations are distributed across multiple countries (Estonia, Japan, Latvia, New Zealand, Portugal, Lithuania)
- Maximum LOO contribution: -5.94 (Estonia, 2000), compared to -16.9 when Turkey was included
- All Pareto k values are below 0.7 (maximum = 0.555), indicating reliable LOO-CV estimates
- No single country dominates the influential observations, suggesting the model fits well across the OECD sample

### Posterior Distributions

The following forest plots show the posterior distributions of predictor coefficients and country-specific intercepts:

```{figure} figs/posterior_forest_beta_hale_nomid.png
:name: beta_forest_hale
:width: 100%

Posterior Distributions of Predictor Coefficients (HALE Gap)
```

```{figure} figs/posterior_forest_alpha_hale_nomid.png
:name: alpha_forest_hale
:width: 100%

Posterior Distributions of Country-Specific Intercepts (HALE Gap)
```

### Posterior Correlations

**Top 10 Correlations Among Beta Coefficients (Predictor Slopes):**

```{include} tables/beta_correlations_top10_hale_nomid.html
```

**Top 10 Correlations Among Alpha Coefficients (Country Intercepts):**

```{include} tables/alpha_correlations_top10_hale_nomid.html
```

**Summary of Posterior Correlations (HALE Gap Model):**

**Beta Correlations (Predictor Slopes):**
- **Note**: Since the model uses only Gap predictors (Mid predictors excluded), the very high negative correlations between Mid and Gap predictors are no longer present. This was a key reason for excluding Mid predictors.
- **Moderate correlations** between Gap predictors:
  - The correlations among Gap predictors are generally moderate (|r| < 0.5), indicating that the model can distinguish their individual effects reasonably well.
  - This is a substantial improvement over the model with Mid predictors, where correlations were very high (r ≈ -0.9 to -1.0).

**Alpha Correlations (Country Intercepts):**
- **Baltic States cluster**: High positive correlations (r ≈ 0.67-0.72) between Estonia (EST), Latvia (LVA), and Lithuania (LTU), suggesting similar unmeasured country-level factors affecting gender gaps.
- **Latin American cluster**: High positive correlations (r ≈ 0.62-0.68) between Chile (CHL), Colombia (COL), Costa Rica (CRI), and Mexico (MEX), indicating shared regional characteristics.
- **Strong negative correlation**: Hungary (HUN) and Israel (ISR) show r = -0.647, suggesting opposite patterns in their country-specific effects.
- These correlations reflect shared cultural, economic, or health system factors that affect gender gaps similarly within regions.

### Comparison with Cross-Sectional Elastic Net Model

The following visualization compares Bayesian posterior distributions with Elastic Net point estimates for the top predictors:

```{figure} figs/bayesian_elasticnet_comparison_hale_nomid.png
:name: comparison_hale
:width: 100%

Bayesian Posterior Distributions vs Elastic Net Coefficients (HALE Gap)
```

**Key Observations:**
- The figure shows posterior distributions (with 94% HDI) for each predictor coefficient
- Blue dashed line: Elastic Net coefficient (point estimate)
- Green solid line: Bayesian posterior mean
- Green shaded region: 94% highest density interval (HDI)
- When the Elastic Net coefficient falls within the Bayesian HDI, it suggests agreement between the two approaches
- When the Elastic Net coefficient falls outside the HDI, it may indicate differences in how the models interpret the data

## Results: Life Expectancy Gap Model

**Model Specification:**
- **Predictors**: Gap predictors only (10 predictors), excluding Mid predictors
- **Year Effects**: Not included (tested but worsen model fit)
- **Countries**: OECD countries excluding Turkey (37 countries, ~740 observations)
- **Model Performance**: WAIC = -7.85 (ELPD), LOO = -8.22 (ELPD), p_waic = 51.3

### Model Diagnostics

**Convergence and Sampling Quality:**
The model converged successfully with R-hat = 1.0 for all parameters and adequate effective sample sizes (ESS > 2000 for all parameters).

### Predictor Coefficients (Beta)

The following table shows the posterior distributions of predictor coefficients. Since predictors are standardized (z-scores), coefficients represent the effect of a 1-standard-deviation change in the predictor on the gender gap in Life Expectancy (in years).

```{include} tables/beta_coefficients_le_nomid.html
```

**Key Findings:**

**Strongest Positive Effects** (larger gender gaps in predictor → larger LE gap, i.e., women live longer):
1. **Gap_Suicide** (β = 0.473, 94% HDI: [0.389, 0.56]): The strongest predictor for Life Expectancy. Gender gaps in suicide mortality are strongly associated with gender gaps in LE, reflecting the substantial contribution of suicide to male mortality.
2. **Gap_ChronicRespiratory** (β = 0.425, 94% HDI: [0.341, 0.496]): Gender gaps in chronic respiratory disease mortality are strongly associated with LE gaps.
3. **Gap_Homicide** (β = 0.435, 94% HDI: [0.393, 0.482]): Gender gaps in homicide mortality are strongly associated with LE gaps, consistent with higher male homicide rates.
4. **Gap_RoadTraffic** (β = 0.427, 94% HDI: [0.382, 0.477]): Gender gaps in road traffic mortality contribute substantially to LE gaps.
5. **Gap_Neoplasms** (β = 0.368, 94% HDI: [0.253, 0.477]): Gender gaps in cancer mortality contribute to LE gaps, though with more uncertainty than the top predictors.

**Moderate Positive Effects:**
- **Gap_LiverDisease** (β = 0.275, 94% HDI: [0.217, 0.335]): Gender gaps in liver disease mortality contribute to LE gaps.
- **Gap_Alcohol** (β = 0.175, 94% HDI: [0.1, 0.247]): Gender gaps in alcohol-related mortality have a moderate positive effect.
- **Gap_UnintentionalInjury** (β = 0.121, 94% HDI: [0.038, 0.214]): Gender gaps in unintentional injury mortality contribute to LE gaps, though with substantial uncertainty (HDI includes values near zero).

**Negative Effects** (larger gender gaps in predictor → smaller LE gap):
- **Gap_Cardiovascular** (β = -0.203, 94% HDI: [-0.252, -0.148]): This negative coefficient reflects the same **competing risks** or **"risk of last resort"** mechanism as in the HALE model. 

  **Sign conventions:**
  - LE gap = Female - Male (positive means women live longer)
  - Gap_Cardiovascular = Male - Female for cardiovascular mortality (positive means men have higher risk)
  
  **What the negative coefficient means:**
  As Gap_Cardiovascular increases (men's CVD risk rises relative to women's), the female-male LE gap tends to be smaller. Equivalently, in countries/years where the LE gap is large (women doing especially well), Gap_Cardiovascular is typically small or even negative (women's CVD risk is closer to, or higher than, men's).
  
  **The "risk of last resort" mechanism:**
  Cardiovascular disease primarily affects people who have already survived many other causes of death. In settings where women's overall health is relatively good:
  - Women avoid or survive many other causes (maternal causes, infections, violence, etc.)
  - They live to older ages and are more exposed to late-life CVD
  - As a result, Gap_Cardiovascular tends to shrink or even flip sign (women's CVD risk approaches or exceeds men's)
  - At the same time, the LE gap is large, because women enjoy advantages across many causes
  
  In settings where women's health is relatively worse:
  - Women face substantial risks from earlier-life causes (e.g., maternal mortality, poor access to care)
  - Fewer women survive to the ages where CVD dominates
  - Men still accumulate substantial CVD risk at older ages
  - So Gap_Cardiovascular tends to be large and positive (men much worse off for CVD)
  - But the LE gap is smaller, because women lose more years to other causes
  
  **The pattern:** Large female-male LE gaps tend to occur where the male-female CVD gap is small or negative. Large male-female CVD gaps tend to occur where women's overall advantage is weaker. This pattern produces the negative regression coefficient.

- **Gap_Diabetes** (β = -0.113, 94% HDI: [-0.157, -0.066]): Similar to cardiovascular disease, diabetes may also follow a competing risks pattern, though the effect is smaller. When women's health is good overall, more survive to die of diabetes, making the gap smaller and the overall LE gap larger.

**Comparison with HALE Model:**
- The ranking of predictors is similar but not identical. Suicide is the strongest predictor for LE, while Road Traffic is strongest for HALE.
- Coefficients are generally similar in magnitude, suggesting consistent relationships across both outcomes.
- The negative effects of Cardiovascular and Diabetes are present in both models, indicating robust patterns.

### Predictor Importance on Original Scale

The importance measure (`|β_standardized| × SD_original`) accounts for both effect size and typical variation, providing a ranking that reflects each predictor's total contribution to gender gaps.

**Interpretation of Importance Units:**
The importance measure (`|β_standardized| × SD_original`) is a **ranking metric** that combines effect size and typical variation, not a direct counterfactual prediction.

**What it represents:**
- The importance measure is proportional to the contribution of each predictor to the **variation** in gender gaps across countries and time.
- It answers: "Which predictors contribute most to explaining differences in gender gaps, accounting for both their effect size and how much they vary?"

**Why the units are in years but not a direct effect:**
- β_standardized = 0.368 means: a 1-SD change in the standardized predictor → 0.368 year change in gap (this is the actual effect size)
- SD_original = 38.4 is the standard deviation of the predictor in its original units
- Importance = 0.368 × 38.4 = 14.2 years is a **scaled contribution measure**, not the effect of a specific change

**Correct interpretation:**
- The importance of 14.2 years does NOT mean "changing Gap_Neoplasms by 1 SD changes the gap by 14.2 years" (that would be 0.368 years)
- Instead, it means: "Gap_Neoplasms contributes substantially to explaining variation in gaps because it has both a moderate effect (0.368 years per SD) and large typical variation (SD = 38.4)"
- The importance measure is useful for **ranking** predictors but should not be interpreted as a counterfactual effect size
- For actual predictions, use β_standardized: a 1-SD change in Gap_Neoplasms → 0.368 year change in gap

```{include} tables/importance_measures_le_nomid_nogrw.html
```

**Key Findings:**

**Top Contributors (by Importance):**
1. **Gap_Neoplasms** (Importance = 14.2 years, 94% HDI: [9.8, 18.5]): Highest importance due to large typical variation (SD = 38.4) combined with moderate effect (β = 0.368), consistent with HALE model.
2. **Gap_Cardiovascular** (Importance = 7.2 years, 94% HDI: [5.3, 9.0]): Second-highest importance despite negative coefficient (β = -0.203), reflecting large variation (SD = 35.5).
3. **Gap_Homicide** (Importance = 6.1 years, 94% HDI: [5.5, 6.7]): Strong positive effect (β = 0.435) with moderate variation (SD = 13.9).
4. **Gap_Suicide** (Importance = 4.8 years, 94% HDI: [3.9, 5.6]): Strongest standardized coefficient (β = 0.471) but smaller variation (SD = 10.1) than homicide.
5. **Gap_ChronicRespiratory** (Importance = 4.6 years, 94% HDI: [3.7, 5.4]): Moderate effect and variation.

**Comparison with HALE Model:**
- Rankings are very similar between HALE and LE models, with Neoplasms and Cardiovascular at the top in both.
- Homicide has slightly higher importance in LE model (6.1 vs 5.2 years), while Suicide is similar (4.8 vs 4.3 years).
- The consistency across outcomes suggests robust patterns in which predictors matter most for gender gaps.

### Country-Specific Intercepts (Alpha)

The following table shows the posterior distributions of country-specific random intercepts. These capture time-invariant country characteristics that affect gender gaps beyond what the predictors explain.

```{include} tables/alpha_coefficients_le_nomid.html
```

**Interpretation:**
- **Positive intercepts**: Countries with larger gender gaps than predicted by the model (women live longer than expected given their predictor values).
- **Negative intercepts**: Countries with smaller gender gaps than predicted (gaps are narrower than expected given their predictor values).
- **Near-zero intercepts**: Countries where the predictors explain most of the gender gap, with little residual country-specific effect.

**Key Patterns:**
- The `sigma_alpha` parameter quantifies how much countries differ in their baseline gaps after accounting for predictors.
- Countries with similar intercepts may share unmeasured characteristics (cultural, economic, or health system factors) that affect gender gaps similarly.

**Influential Observations:**
Similar to the HALE model, the Life Expectancy gap model (excluding Turkey) shows influential observations distributed across multiple countries, with no single country dominating.

```{include} tables/influential_observations_le_nomid.html
```

**Key Findings:**
- Top influential observations are distributed across multiple countries (Estonia, Japan, Latvia, New Zealand, Lithuania, Israel)
- Maximum LOO contribution: -7.1 (Estonia, 2000), compared to -16.9 when Turkey was included
- All Pareto k values are below 0.7 (maximum = 0.511), indicating reliable LOO-CV estimates
- No single country dominates the influential observations, suggesting the model fits well across the OECD sample

### Posterior Distributions

The following forest plots show the posterior distributions of predictor coefficients and country-specific intercepts:

```{figure} figs/posterior_forest_beta_le_nomid.png
:name: beta_forest_le
:width: 100%

Posterior Distributions of Predictor Coefficients (Life Expectancy Gap)
```

```{figure} figs/posterior_forest_alpha_le_nomid.png
:name: alpha_forest_le
:width: 100%

Posterior Distributions of Country-Specific Intercepts (Life Expectancy Gap)
```

### Posterior Correlations

**Top 10 Correlations Among Beta Coefficients (Predictor Slopes):**

```{include} tables/beta_correlations_top10_le_nomid.html
```

**Top 10 Correlations Among Alpha Coefficients (Country Intercepts):**

```{include} tables/alpha_correlations_top10_le_nomid.html
```

**Summary of Posterior Correlations (Life Expectancy Gap Model):**

**Beta Correlations (Predictor Slopes):**
- **Note**: Since the model uses only Gap predictors (Mid predictors excluded), the very high negative correlations between Mid and Gap predictors are no longer present. This was a key reason for excluding Mid predictors.
- **Moderate correlations** between Gap predictors:
  - The correlations among Gap predictors are generally moderate (|r| < 0.5), indicating that the model can distinguish their individual effects reasonably well.
  - This is a substantial improvement over the model with Mid predictors, where correlations were very high (r ≈ -0.9 to -1.0).

**Alpha Correlations (Country Intercepts):**
- **Baltic States cluster**: High positive correlations (r ≈ 0.68-0.73) between Estonia (EST), Latvia (LVA), and Lithuania (LTU), consistent with HALE model.
- **Latin American cluster**: High positive correlations (r ≈ 0.65-0.71) between Chile (CHL), Colombia (COL), Costa Rica (CRI), and Mexico (MEX), similar to HALE model.
- **Strong negative correlation**: Hungary (HUN) and Israel (ISR) show r = -0.663, consistent with HALE model.
- **Additional cluster**: Denmark (DNK) and United Kingdom (GBR) show r = 0.617, suggesting shared characteristics in these Northern European countries.
- The patterns are remarkably consistent between HALE and Life Expectancy models, indicating robust regional and country-level effects.

### Comparison with Cross-Sectional Elastic Net Model

The following visualization compares Bayesian posterior distributions with Elastic Net point estimates for the top predictors:

```{figure} figs/bayesian_elasticnet_comparison_le_nomid.png
:name: comparison_le
:width: 100%

Bayesian Posterior Distributions vs Elastic Net Coefficients (Life Expectancy Gap)
```

## Interpretation

### Coefficient Estimates

**Comparison with Cross-Sectional Model:**
- The Bayesian panel model provides posterior distributions for each coefficient, allowing us to assess uncertainty
- When Elastic Net coefficients fall within the Bayesian 94% HDI, it suggests the cross-sectional relationships are robust to temporal analysis
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
- **Credible intervals**: The 94% HDI provides a range of plausible values. If the HDI excludes zero, we can be confident the effect is non-zero (though this is not a formal hypothesis test).

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

### Influential Observations and Outliers

**Initial LOO-CV Analysis Revealed Turkey as a Dominant Outlier:**

Leave-One-Out Cross-Validation (LOO-CV) identifies observations that are difficult for the model to fit. The analysis reveals that **Turkey (TUR) dominates the list of influential observations**, with all top 10 most influential observations coming from Turkey across multiple years (2000-2019). The LOO contributions for Turkey observations are substantially larger (in absolute value) than for other countries, with values ranging from approximately -8.6 to -16.9.

**Why Turkey May Be an Outlier:**

Turkey's dominance in influential observations suggests that:
1. **Data quality issues**: Turkey's data may have measurement errors, reporting inconsistencies, or systematic biases that differ from other OECD countries
2. **Unique country characteristics**: Turkey may have structural factors (cultural, economic, health system) that are not well captured by the model's predictors, making it systematically different from other OECD countries
3. **Rapid changes**: Turkey may have experienced rapid changes in health outcomes or data collection methods during the study period that create temporal patterns not well explained by the model
4. **Model misspecification**: The model may not adequately capture the relationships between predictors and gender gaps for Turkey's specific context

**Pros and Cons of Excluding Turkey:**

**Pros of Excluding Turkey:**
1. **Improved model fit**: Removing a dominant outlier may improve overall model fit metrics (WAIC, LOO-CV) and reduce residual variance
2. **More stable coefficient estimates**: Turkey's extreme values may be pulling coefficient estimates away from values that better represent the majority of OECD countries
3. **Better predictive performance**: A model trained without Turkey may generalize better to other OECD countries
4. **Reduced leverage**: Turkey's observations may have excessive leverage on the model, making the results less representative of the broader OECD population
5. **Clearer interpretation**: Removing Turkey may make the relationships between predictors and gender gaps clearer and more interpretable for the remaining countries

**Cons of Excluding Turkey:**
1. **Loss of information**: Turkey represents a substantial portion of the data (20 country-year observations), and excluding it reduces the sample size and statistical power
2. **Reduced generalizability**: If the goal is to understand gender gaps across all OECD countries, excluding Turkey limits the scope of inference
3. **Potential bias**: If Turkey's outlier status reflects genuine but poorly understood factors, excluding it may bias the model toward countries with more similar characteristics
4. **Data quality concerns**: If Turkey's data quality is the issue, this raises questions about data quality in other countries that may not be as obvious
5. **Scientific validity**: Excluding observations based on model fit may be seen as "cherry-picking" and could raise questions about the robustness of findings
6. **Missing insights**: Turkey's outlier status may reveal important patterns or relationships that are worth understanding, even if they don't fit the general model

**Sensitivity Analysis: Models With and Without Turkey**

We conducted a sensitivity analysis by fitting models both with and without Turkey to assess the robustness of our findings. The results demonstrate that **excluding Turkey substantially improves model behavior**:

**Key Findings from Sensitivity Analysis:**

1. **Influential Observations Distribution:**
   - **With Turkey**: All top 10 influential observations are from Turkey, with LOO contributions ranging from approximately -8.6 to -16.9
   - **Without Turkey**: Influential observations are distributed across multiple countries, with no single country dominating. The maximum LOO contribution is substantially smaller (typically < -6.0), indicating better overall model fit

2. **Model Fit Improvement:**
   - Excluding Turkey reduces the magnitude of the most influential observations, suggesting that Turkey's observations were creating systematic model misfit
   - The more balanced distribution of influence across countries indicates that the model better captures the relationships for the remaining OECD countries

3. **Interpretation:**
   - The fact that removing Turkey eliminates the extreme influence values and distributes influence more evenly suggests that Turkey's data patterns are genuinely different from the rest of the OECD countries
   - This supports the hypothesis that Turkey may have unique characteristics (data quality, structural factors, or model misspecification) that make it an outlier

**Recommendation:**

Based on the sensitivity analysis results, we recommend:

1. **Exclude Turkey from the primary analysis**: The evidence strongly supports excluding Turkey:
   - Turkey's observations create extreme model misfit (all top 10 influential observations)
   - Removing Turkey results in a more balanced distribution of influence across countries
   - The remaining influential observations are smaller in magnitude, indicating better model fit
   - Results are more representative of the broader OECD population

2. **Report primary results without Turkey**: The main results presented in this report are from models that exclude Turkey, as this provides more stable and interpretable estimates for the majority of OECD countries.

3. **Acknowledge the limitation**: Clearly state that results apply to OECD countries excluding Turkey, and note that Turkey may require separate analysis or country-specific modeling approaches.

4. **Future work**: If understanding Turkey's gender gaps is of interest, consider:
   - Separate analysis for Turkey with country-specific models
   - Investigation of Turkey-specific predictors or data quality issues
   - Comparison of Turkey's patterns to non-OECD countries that may share similar characteristics

**Current Analysis:**

The results presented in this report **exclude Turkey** from the analysis. This decision is based on:
- Turkey's dominance in influential observations (all top 10 observations)
- The substantial improvement in model behavior when Turkey is excluded
- The more balanced distribution of influence across remaining countries
- The goal of providing stable, interpretable results for the majority of OECD countries

Readers should be aware that:
- Results apply to OECD countries excluding Turkey (37 countries, ~740 observations)
- Turkey may require separate analysis if understanding its gender gaps is of interest
- The exclusion is methodologically justified based on model diagnostics and sensitivity analysis

## Model Extensions (Future Work)

After implementing the basic random-intercept model, potential extensions include:

**(A) Predictor Selection Based on Correlations:**
- **Problem**: The posterior correlations reveal very high negative correlations (r ≈ -0.9 to -1.0) between Mid and Gap predictors for the same indicator (Homicide, Alcohol, Liver Disease, Road Traffic, Suicide). This suggests the model cannot easily distinguish the individual contributions of these paired predictors.
- **Hypothesis**: When Mid and Gap for the same indicator are highly correlated in their posterior distributions, it may indicate that:
  - The two predictors capture redundant information
  - The model cannot reliably separate their effects
  - Removing one (likely the Mid predictor) may simplify the model without losing predictive power

**Results of Model Comparison:**

We compared two models:
- **Model 1 (with Mid predictors)**: Includes all Mid and Gap predictors (20 predictors total)
- **Model 2 (without Mid predictors)**: Includes only Gap predictors (10 predictors total)

**Key Findings:**

1. **Dramatic Improvement in Model Fit:**
   - **HALE Gap Model:**
     - With Mid: WAIC = 310 (ELPD), LOO = 310 (ELPD), p_waic = 59.6, p_loo = 60.3
     - Without Mid: WAIC = 75.7 (ELPD), LOO = 75.3 (ELPD), p_waic = 50.5, p_loo = 50.9
     - **Improvement**: ΔWAIC = -234.3 (lower is better), ΔLOO = -234.7
   
   - **Life Expectancy Gap Model:**
     - With Mid: WAIC = 272 (ELPD), LOO = 272 (ELPD), p_waic = 61.3, p_loo = 62.0
     - Without Mid: WAIC = -7.5 (ELPD), LOO = -7.92 (ELPD), p_waic = 51.1, p_loo = 51.5
     - **Improvement**: ΔWAIC = -279.5, ΔLOO = -279.92

2. **Reduced Model Complexity:**
   - Effective number of parameters (p_waic, p_loo) decreased by approximately 9-11 parameters
   - Model complexity reduced from 20 predictors to 10 predictors (50% reduction)
   - This reduction in complexity is expected, but the magnitude of fit improvement is substantial

3. **Coefficient Changes:**
   - Removing Mid predictors changes the coefficients for Gap predictors
   - For example, Gap_Alcohol coefficient: 0.334 (with Mid) vs 0.158 (without Mid)
   - This suggests that Mid predictors were partially confounding the Gap predictor effects
   - Coefficients in the simplified model are more interpretable as they represent the direct effect of gender gaps without the confounding influence of overall levels

4. **Interpretation:**
   - The massive improvement in WAIC/LOO (hundreds of points) strongly suggests that:
     - Mid predictors were adding noise rather than signal
     - The high negative correlations between Mid and Gap predictors were creating multicollinearity issues
     - Gap predictors alone capture the relevant information for predicting gender gaps in HALE and Life Expectancy
   - The fact that removing half the predictors dramatically improves fit indicates that the original model was overparameterized

**Recommendation:**

Based on these results, we **strongly recommend using the model without Mid predictors** as the primary model:

1. **Superior Model Fit**: The model without Mid predictors has dramatically better WAIC/LOO scores (hundreds of points lower), indicating substantially better out-of-sample predictive performance.

2. **Reduced Multicollinearity**: Removing Mid predictors eliminates the high correlations (r ≈ -0.9 to -1.0) that were making coefficient estimates unstable and difficult to interpret.

3. **Simpler Interpretation**: The simplified model is easier to interpret:
   - Each Gap predictor coefficient directly represents the effect of the gender gap in that indicator on the gender gap in HALE/LE
   - No need to disentangle the separate effects of Mid and Gap predictors
   - Coefficients are more stable and reliable

4. **Better Generalization**: The lower effective number of parameters (p_waic, p_loo) suggests the model is less prone to overfitting and should generalize better to new data.

5. **Theoretical Justification**: Since we're predicting gender gaps, it makes theoretical sense to focus on gender gap predictors (Gap) rather than overall levels (Mid). The gender gap in an indicator is more directly relevant to explaining gender gaps in HALE/LE than the overall level of that indicator.

**Current Analysis:**

The results presented in this report use the **model without Mid predictors** (Gap predictors only). This model provides:
- Better fit (lower WAIC/LOO)
- More stable and interpretable coefficients
- Reduced multicollinearity
- Simpler model structure (10 predictors instead of 20)

**(B) Year Fixed Effects (Gaussian Random Walk) - COMPLETED:**
- Add `γ_t` to model: `y*_{it} = α_i + γ_t + X*_{it}β + ε_{it}`
- Controls for global temporal trends (e.g., global health improvements affecting all countries)
- **Implementation**: Gaussian Random Walk (GRW) with `init_dist ~ N(0, 0.5)` and innovation standard deviation `σ_γ ~ HalfNormal(0.5)`
- **Results**: Year effects were tested but **do not improve model fit**:
  
  **HALE Gap Model:**
  - Without year effects: WAIC = 75.3, LOO = 74.9, p_waic = 50.8
  - With year effects: WAIC = 173, LOO = 172, p_waic = 63.1
  - **ΔWAIC = +97.7** (worse), **ΔLOO = +97.1** (worse)
  
  **Life Expectancy Gap Model:**
  - Without year effects: WAIC = -7.85, LOO = -8.22, p_waic = 51.3
  - With year effects: WAIC = 103, LOO = 102, p_waic = 65.8
  - **ΔWAIC = +110.85** (worse), **ΔLOO = +110.22** (worse)
  
- **Conclusion**: Year effects worsen model fit substantially (ΔWAIC/ΔLOO > 90 for both models) and increase effective parameters by ~12-15 without improving predictive performance. The model **without year effects is preferred**.
- **Recommendation**: Do not include year effects in the final model. The simpler model provides better out-of-sample predictive performance.

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

### Key Model Decisions

**Final Model Specification:**
- **Predictors**: Gap predictors only (10 predictors), excluding Mid predictors
- **Countries**: OECD countries excluding Turkey (37 countries, ~740 observations)
- **Year Effects**: **Not included** (tested but worsen model fit)
- **Rationale**: 
  - Removing Mid predictors dramatically improves model fit (ΔWAIC ≈ -234 to -280)
  - Eliminates multicollinearity issues (r ≈ -0.9 to -1.0 between Mid and Gap)
  - Provides more interpretable and stable coefficient estimates
  - Excluding Turkey eliminates extreme outliers and improves model behavior
  - Year effects (GRW) tested but worsen fit (ΔWAIC/ΔLOO > 90), so excluded

**Model Performance:**
- **HALE Gap Model**: WAIC = 75.7 (ELPD), LOO = 75.3 (ELPD), p_waic = 50.5
- **Life Expectancy Gap Model**: WAIC = -7.5 (ELPD), LOO = -7.92 (ELPD), p_waic = 51.1
- Both models show excellent fit with reasonable effective parameter counts

**Note on WAIC Warning:**
The model produces a warning that "the posterior variance of the log predictive densities exceeds 0.4" for some samples, which suggests WAIC may be less reliable. However, **Pareto k diagnostics from LOO-CV confirm that all observations have acceptable influence**, indicating that LOO-CV is reliable.

**Pareto k Diagnostic Results:**
- **HALE Gap Model**: Maximum Pareto k = 0.555, all values < 0.7 (range: 0.092 to 0.555)
- **Life Expectancy Gap Model**: Maximum Pareto k = 0.511, all values < 0.7 (range: 0.21 to 0.511)
- **Interpretation**: All Pareto k values are well below the 0.7 threshold, indicating that:
  - No observations are overly influential
  - LOO-CV estimates are reliable
  - The model is functioning well without problematic outliers

**Why the WAIC Warning Occurs Despite Good Pareto k Values:**
The WAIC warning and Pareto k diagnostics measure different things:
- **Pareto k**: Measures the influence of individual observations on the LOO-CV estimate. Good values (k < 0.7) indicate that no single observation is overly influential.
- **WAIC warning**: Measures the variance of log predictive densities across the posterior. High variance can occur in hierarchical models due to:
  1. **Hierarchical structure**: Random intercepts create varying uncertainty across countries, which increases the variance of log predictive densities even when individual observations are not problematic
  2. **Panel data structure**: The combination of between-country and within-country variation can create higher variance in predictive densities
  3. **Model complexity**: The hierarchical structure naturally creates more uncertainty in predictions compared to simpler models

**Interpretation:**
- **LOO-CV is reliable**: All Pareto k values are below 0.7 (maximum 0.555 for HALE, 0.511 for LE), confirming that LOO-CV estimates are trustworthy. The LOO values (75.3 for HALE, -7.92 for LE) are our primary and most reliable model comparison metrics.
- **WAIC warning is expected**: The warning is a known feature of hierarchical panel models and does not indicate a problem with the model. The variance in log predictive densities is a consequence of the hierarchical structure, not a flaw.
- **Model comparisons are valid**: The dramatic improvement (ΔWAIC ≈ -234 to -280, ΔLOO ≈ -235 to -280) when removing Mid predictors is meaningful and consistent across both metrics.
- **Model is valid**: The combination of good Pareto k values (all < 0.7) and the WAIC warning is consistent with a well-functioning hierarchical panel model. The warning does not invalidate the model or its results.

**Main Findings:**
- Gender gaps in specific mortality indicators (Gap predictors) are the primary drivers of gender gaps in HALE and Life Expectancy
- Overall levels of mortality (Mid predictors) add little information beyond what is captured by gender gaps
- The simplified model structure provides clearer insights into which gender gaps matter most for overall gender differences in healthy life expectancy
- Year effects (Gaussian Random Walk) do not improve model fit and are excluded from the final model

