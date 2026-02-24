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
  - Drug Use Disorders (IHME)
- **Predictors**: Gap (gender difference) columns only for each indicator (Mid predictors excluded based on model comparison - see Model Extensions section)
- Complete panel: No missing data
- **Sample size**: Approximately 740 country-year observations (37 countries × 20 years, excluding Turkey)
- **Number of predictors**: 11 (Gap predictors for: Alcohol, Suicide, Homicide, Road Injuries, Cardiovascular, Diabetes, Neoplasms, Chronic Respiratory, Liver Disease, Unintentional Injuries, Drug Disorders)

**Note on Drug Disorders Predictor:**
Drug Disorders was added to the model to match the plan specification (10 indicators). Comparison of model fit metrics before and after adding Drug Disorders shows:
- **HALE Gap Model**: WAIC increased from 75.7 to 87.7 (ΔWAIC = +12.0), LOO increased from 75.3 to 87.3 (ΔLOO = +12.0), while R² remained essentially unchanged (0.987 → 0.9874) and MAE improved slightly (0.158 → 0.157 years)
- **Life Expectancy Gap Model**: WAIC increased from -7.5 to -2.6 (ΔWAIC = +4.9), LOO increased from -7.9 to -3.0 (ΔLOO = +4.9), while R² remained essentially unchanged (0.985 → 0.9851) and MAE remained essentially unchanged (0.175 → 0.175 years)

The increase in WAIC/LOO (worse fit) suggests that Drug Disorders adds minimal predictive power while slightly increasing model complexity. However, the R² and MAE metrics indicate that predictive accuracy is maintained. The inclusion of Drug Disorders is justified by the plan's specification and allows for comprehensive counterfactual analysis across all mortality indicators.

## Results: HALE Gap Model

**Model Specification:**
- **Predictors**: Gap predictors only (11 predictors), excluding Mid predictors
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
- **Predictors**: Gap predictors only (11 predictors), excluding Mid predictors
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
- **Model 1 (with Mid predictors)**: Includes all Mid and Gap predictors (22 predictors total)
- **Model 2 (without Mid predictors)**: Includes only Gap predictors (11 predictors total)

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
   - Model complexity reduced from 22 predictors to 11 predictors (50% reduction)
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
- Simpler model structure (11 predictors instead of 22)

**Selective Re-introduction of Mid Predictors - Experiment 1: Mid_Cardiovascular**

Based on the correlation analysis from EDA (see `rate_gap_correlation_2019.html`), we identified that some Mid predictors have low or negative correlations with their corresponding Gap predictors, suggesting they may provide independent information. The strongest negative correlation is between `Mid_Cardiovascular` and `Gap_Cardiovascular` (r = -0.804), making it the top candidate for selective re-introduction.

**Rationale:**
- `Gap_Cardiovascular` has a negative coefficient (β = -0.247 for HALE, β = -0.203 for LE) that was interpreted as a "competing risks" mechanism
- The strong negative correlation (r = -0.804) suggests `Mid_Cardiovascular` provides independent information about overall CVD levels that varies between countries and over time
- Adding `Mid_Cardiovascular` might help clarify whether the negative `Gap_Cardiovascular` coefficient is confounded or represents a genuine competing risks pattern

**Experiment Design:**
- **Baseline Model**: Gap predictors only (11 predictors) - `MID_PREDICTORS_TO_INCLUDE = []`
- **Test Model**: Baseline + `Mid_Cardiovascular` (12 predictors) - `MID_PREDICTORS_TO_INCLUDE = ['Mid_Cardiovascular']`
- **Evaluation Criteria**: 
  - Model fit (WAIC/LOO differences)
  - Coefficient stability (changes in `Gap_Cardiovascular` coefficient)
  - Posterior correlations (check if Mid-Gap correlation is manageable)
  - Interpretability of coefficient signs

**Results:**

**Model Fit Comparison:**

| Model | HALE Gap WAIC | HALE Gap LOO | LE Gap WAIC | LE Gap LOO |
|-------|---------------|--------------|-------------|------------|
| Baseline (Gap only) | 75.7 | 75.3 | -7.44 | -7.89 |
| With Mid_Cardiovascular | 127 | 127 | 55.1 | 54.6 |
| **Δ (Change)** | **+51.3** | **+51.7** | **+62.5** | **+62.5** |

**Key Findings:**

1. **Model Fit Worsens**: Adding `Mid_Cardiovascular` substantially worsens model fit for both HALE and Life Expectancy models:
   - **HALE Gap**: ΔWAIC = +51.3, ΔLOO = +51.7 (worse)
   - **Life Expectancy Gap**: ΔWAIC = +62.5, ΔLOO = +62.5 (worse)
   - The increase in WAIC/LOO is well above the threshold for meaningful worsening (ΔWAIC > +5)

2. **Coefficient Changes**:
   - **Gap_Cardiovascular (HALE)**: Changed from β = -0.247 (94% HDI: [-0.292, -0.196]) to β = -0.139 (94% HDI: [-0.187, -0.088])
     - Coefficient becomes less negative (closer to zero) but remains negative
     - The 94% HDI still excludes zero, indicating a robust negative effect
   - **Gap_Cardiovascular (LE)**: Changed from β = -0.203 (94% HDI: [-0.252, -0.148]) to β = -0.067 (94% HDI: [-0.116, -0.013])
     - Coefficient becomes much less negative and the HDI is very close to zero
     - The effect is substantially weakened
   - **Mid_Cardiovascular (HALE)**: β = 0.526 (94% HDI: [0.426, 0.621]) - strong positive effect
   - **Mid_Cardiovascular (LE)**: β = 0.627 (94% HDI: [0.521, 0.726]) - strong positive effect

3. **Posterior Correlations**:
   - **Gap_Cardiovascular ↔ Mid_Cardiovascular**: r = 0.413 (moderate positive correlation)
   - This correlation is manageable (< 0.8) and does not indicate severe multicollinearity
   - However, the correlation is still substantial enough that the model has difficulty separating their effects

4. **Interpretation**:
   - The positive `Mid_Cardiovascular` coefficients (β ≈ 0.5-0.6) indicate that higher overall CVD levels are associated with larger gender gaps (women live longer)
   - This is consistent with the competing risks interpretation: in countries/years with high overall CVD levels, women's health is generally good (they survive other causes), leading to larger gender gaps
   - The fact that adding `Mid_Cardiovascular` weakens the `Gap_Cardiovascular` coefficient suggests some confounding, but the negative sign persists, supporting the competing risks mechanism

**Conclusion:**

Adding `Mid_Cardiovascular` to the model **does not improve fit** and actually worsens it substantially (ΔWAIC/ΔLOO > 50 for both models). While the posterior correlation between `Gap_Cardiovascular` and `Mid_Cardiovascular` is manageable (r = 0.413), the model fit deterioration suggests that:

1. **The baseline model (Gap predictors only) is preferred**: The simpler model provides better out-of-sample predictive performance
2. **The competing risks interpretation is robust**: Even when controlling for overall CVD levels via `Mid_Cardiovascular`, the `Gap_Cardiovascular` coefficient remains negative (though weaker), supporting the competing risks mechanism
3. **Mid predictors add noise, not signal**: Despite the strong negative correlation in the data (r = -0.804), adding `Mid_Cardiovascular` worsens model fit, suggesting it adds more noise than useful information

**Recommendation:**

**Do not include `Mid_Cardiovascular`** in the final model. The baseline model with Gap predictors only provides:
- Better model fit (lower WAIC/LOO)
- More interpretable coefficients
- Simpler model structure
- Robust competing risks interpretation for cardiovascular disease

**Experiment 2: Mid_Diabetes**

Following Experiment 1, we tested `Mid_Diabetes` (r = -0.325 with `Gap_Diabetes`), which has a moderate negative correlation. This was tested alone (not cumulatively with `Mid_Cardiovascular`, since that predictor did not improve the model).

**Rationale:**
- `Gap_Diabetes` has a negative coefficient (β = -0.108 for HALE, β = -0.113 for LE) that was interpreted as a "competing risks" mechanism, similar to cardiovascular disease
- The moderate negative correlation (r = -0.325) suggests `Mid_Diabetes` may provide some independent information about overall diabetes levels
- Testing this candidate will help determine if the pattern from Experiment 1 (worsening fit) is consistent across Mid predictors

**Experiment Design:**
- **Baseline Model**: Gap predictors only (11 predictors) - `MID_PREDICTORS_TO_INCLUDE = []`
- **Test Model**: Baseline + `Mid_Diabetes` (12 predictors) - `MID_PREDICTORS_TO_INCLUDE = ['Mid_Diabetes']`
- **Evaluation Criteria**: Same as Experiment 1

**Results:**

**Model Fit Comparison:**

| Model | HALE Gap WAIC | HALE Gap LOO | LE Gap WAIC | LE Gap LOO |
|-------|---------------|--------------|-------------|------------|
| Baseline (Gap only) | 75.7 | 75.3 | -7.44 | -7.89 |
| With Mid_Diabetes | 78.8 | 78.4 | -5.26 | -5.64 |
| **Δ (Change)** | **+3.1** | **+3.1** | **+2.18** | **+2.25** |

**Key Findings:**

1. **Model Fit Worsens (but less dramatically than Mid_Cardiovascular)**: Adding `Mid_Diabetes` worsens model fit for both HALE and Life Expectancy models:
   - **HALE Gap**: ΔWAIC = +3.1, ΔLOO = +3.1 (worse)
   - **Life Expectancy Gap**: ΔWAIC = +2.18, ΔLOO = +2.25 (worse)
   - The increase in WAIC/LOO is smaller than for `Mid_Cardiovascular` (ΔWAIC = +51.3 for HALE, +62.5 for LE), but still indicates worsening fit
   - The change is above the threshold for meaningful worsening (ΔWAIC > +5) for HALE, but below for LE

2. **Coefficient Changes**:
   - **Gap_Diabetes (HALE)**: Changed from β = -0.108 (94% HDI: [-0.148, -0.065]) to β = -0.098 (94% HDI: [-0.14, -0.055])
     - Coefficient becomes slightly less negative (closer to zero) but remains negative
     - The 94% HDI still excludes zero, indicating a robust negative effect
   - **Gap_Diabetes (LE)**: Changed from β = -0.113 (94% HDI: [-0.157, -0.066]) to β = -0.102 (94% HDI: [-0.148, -0.06])
     - Similar pattern - slightly less negative but remains negative
   - **Mid_Diabetes (HALE)**: β = 0.064 (94% HDI: [0.014, 0.108]) - small positive effect, HDI barely excludes zero
   - **Mid_Diabetes (LE)**: β = 0.065 (94% HDI: [0.016, 0.114]) - small positive effect, similar to HALE

3. **Posterior Correlations**:
   - **Gap_Diabetes ↔ Mid_Diabetes**: Not in top 10 correlations (correlation < 0.3, likely very low)
   - This is a positive finding - the two predictors are not highly correlated in the posterior, suggesting the model can distinguish their effects
   - However, the fact that model fit still worsens suggests that even with low correlation, `Mid_Diabetes` adds more noise than signal

4. **Interpretation**:
   - The small positive `Mid_Diabetes` coefficients (β ≈ 0.06) indicate that higher overall diabetes levels are weakly associated with larger gender gaps (women live longer)
   - This is consistent with the competing risks interpretation, but the effect is much smaller than for `Mid_Cardiovascular` (β ≈ 0.5-0.6)
   - The fact that adding `Mid_Diabetes` only slightly weakens the `Gap_Diabetes` coefficient suggests minimal confounding

**Conclusion:**

Adding `Mid_Diabetes` to the model **does not improve fit** and worsens it, though less dramatically than `Mid_Cardiovascular`. The smaller worsening (ΔWAIC/ΔLOO ≈ +2-3 vs. +50-60 for `Mid_Cardiovascular`) and the low posterior correlation between `Gap_Diabetes` and `Mid_Diabetes` suggest that:

1. **The baseline model (Gap predictors only) is still preferred**: Even with low correlation, adding `Mid_Diabetes` worsens model fit
2. **The competing risks interpretation is robust**: The `Gap_Diabetes` coefficient remains negative even when controlling for overall diabetes levels
3. **Mid predictors consistently add noise**: Both experiments show that Mid predictors worsen model fit, regardless of their correlation with Gap predictors

**Recommendation:**

**Do not include `Mid_Diabetes`** in the final model. The baseline model with Gap predictors only provides better model fit and more interpretable coefficients.

**Next Steps:**

We will continue testing the remaining candidates to ensure comprehensive evaluation. The next candidates are `Mid_ChronicRespiratory` (r = -0.0787) and `Mid_UnintentionalInjury` (r = 0.0346), which have even lower correlations with their corresponding Gap predictors. While both experiments so far have worsened model fit, testing these additional candidates will provide complete evidence for the final model specification decision.

**Experiment 3: Mid_ChronicRespiratory**

Following Experiments 1 and 2, we tested `Mid_ChronicRespiratory` (r = -0.0787 with `Gap_ChronicRespiratory`), which has a small negative correlation. This was tested alone (not cumulatively with previous candidates, since they did not improve the model).

**Rationale:**
- `Gap_ChronicRespiratory` has a positive coefficient (β = 0.336 for HALE, β = 0.425 for LE) indicating that larger gender gaps in respiratory disease are associated with larger HALE/LE gaps
- The small negative correlation (r = -0.0787) suggests `Mid_ChronicRespiratory` may provide some independent information about overall respiratory disease levels
- Testing this candidate will help determine if the pattern from previous experiments (worsening fit) continues even with very low correlations

**Experiment Design:**
- **Baseline Model**: Gap predictors only (11 predictors) - `MID_PREDICTORS_TO_INCLUDE = []`
- **Test Model**: Baseline + `Mid_ChronicRespiratory` (12 predictors) - `MID_PREDICTORS_TO_INCLUDE = ['Mid_ChronicRespiratory']`
- **Evaluation Criteria**: Same as previous experiments

**Results:**

**Model Fit Comparison:**

| Model | HALE Gap WAIC | HALE Gap LOO | LE Gap WAIC | LE Gap LOO |
|-------|---------------|--------------|-------------|------------|
| Baseline (Gap only) | 75.7 | 75.3 | -7.44 | -7.89 |
| With Mid_ChronicRespiratory | 96.5 | 96.1 | 16.7 | 16.3 |
| **Δ (Change)** | **+20.8** | **+20.8** | **+24.1** | **+24.2** |

**Key Findings:**

1. **Model Fit Worsens Substantially**: Adding `Mid_ChronicRespiratory` worsens model fit for both HALE and Life Expectancy models:
   - **HALE Gap**: ΔWAIC = +20.8, ΔLOO = +20.8 (worse)
   - **Life Expectancy Gap**: ΔWAIC = +24.1, ΔLOO = +24.2 (worse)
   - The increase in WAIC/LOO is substantial and well above the threshold for meaningful worsening (ΔWAIC > +5)
   - This is intermediate between `Mid_Cardiovascular` (ΔWAIC ≈ +50-60) and `Mid_Diabetes` (ΔWAIC ≈ +2-3)

2. **Coefficient Changes**:
   - **Gap_ChronicRespiratory (HALE)**: Changed from β = 0.336 (94% HDI: [0.271, 0.403]) to β = 0.39 (94% HDI: [0.324, 0.457])
     - Coefficient becomes more positive (stronger effect) when `Mid_ChronicRespiratory` is included
     - The 94% HDI still excludes zero, indicating a robust positive effect
   - **Gap_ChronicRespiratory (LE)**: Changed from β = 0.425 (94% HDI: [0.341, 0.496]) to β = 0.485 (94% HDI: [0.412, 0.561])
     - Similar pattern - becomes more positive (stronger effect)
   - **Mid_ChronicRespiratory (HALE)**: β = -0.24 (94% HDI: [-0.308, -0.178]) - **negative effect**
   - **Mid_ChronicRespiratory (LE)**: β = -0.278 (94% HDI: [-0.343, -0.21]) - **negative effect**

3. **Posterior Correlations**:
   - **Gap_ChronicRespiratory ↔ Mid_ChronicRespiratory**: Not in top 10 correlations (correlation < 0.3, likely very low)
   - This is consistent with the low data correlation (r = -0.0787) - the two predictors are essentially independent
   - However, the fact that model fit still worsens substantially suggests that even with very low correlation, `Mid_ChronicRespiratory` adds more noise than signal

4. **Interpretation**:
   - The **negative** `Mid_ChronicRespiratory` coefficients (β ≈ -0.24 to -0.28) are interesting and counterintuitive
   - This suggests that higher overall respiratory disease levels are associated with **smaller** gender gaps (women's advantage is reduced)
   - This could reflect that in countries/years with high overall respiratory disease, women's health is relatively worse (perhaps due to smoking patterns, occupational exposures, or other factors), reducing their advantage
   - The fact that adding `Mid_ChronicRespiratory` strengthens the `Gap_ChronicRespiratory` coefficient suggests some confounding was present, but the overall model fit worsens

**Conclusion:**

Adding `Mid_ChronicRespiratory` to the model **does not improve fit** and worsens it substantially (ΔWAIC/ΔLOO ≈ +20-24 for both models). Despite the very low correlation with `Gap_ChronicRespiratory` (r = -0.0787) and low posterior correlation, the model fit deterioration suggests that:

1. **The baseline model (Gap predictors only) is still preferred**: Even with very low correlation, adding `Mid_ChronicRespiratory` worsens model fit
2. **Low correlation does not guarantee improved fit**: This experiment shows that even predictors with very low correlations (r ≈ -0.08) can worsen model fit when added
3. **Mid predictors consistently add noise**: All three experiments so far show that Mid predictors worsen model fit, regardless of their correlation strength with Gap predictors

**Recommendation:**

**Do not include `Mid_ChronicRespiratory`** in the final model. The baseline model with Gap predictors only provides better model fit and more interpretable coefficients.

**Experiment 4: Mid_UnintentionalInjury**

This is the final candidate in our systematic evaluation. We tested `Mid_UnintentionalInjury` alone (r = 0.0346 with `Gap_UnintentionalInjury`), which has the lowest correlation (essentially zero).

**Rationale:**
- `Gap_UnintentionalInjury` has a positive coefficient (β = 0.148 for HALE, β = 0.169 for LE) indicating that larger gender gaps in unintentional injuries are associated with larger HALE/LE gaps
- The essentially zero correlation (r = 0.0346) suggests `Mid_UnintentionalInjury` should provide independent information about overall unintentional injury levels
- Testing this final candidate will complete our comprehensive evaluation of all Mid predictors

**Experiment Design:**
- **Baseline Model**: Gap predictors only (11 predictors) - `MID_PREDICTORS_TO_INCLUDE = []`
- **Test Model**: Baseline + `Mid_UnintentionalInjury` (12 predictors) - `MID_PREDICTORS_TO_INCLUDE = ['Mid_UnintentionalInjury']`
- **Evaluation Criteria**: Same as previous experiments

**Results:**

**Model Fit Comparison:**

| Model | HALE Gap WAIC | HALE Gap LOO | LE Gap WAIC | LE Gap LOO |
|-------|---------------|--------------|-------------|------------|
| Baseline (Gap only) | 75.7 | 75.3 | -7.44 | -7.89 |
| With Mid_UnintentionalInjury | 155 | 154 | 83.7 | 83.2 |
| **Δ (Change)** | **+79.3** | **+78.7** | **+91.1** | **+91.1** |

**Key Findings:**

1. **Model Fit Worsens Dramatically**: Adding `Mid_UnintentionalInjury` worsens model fit for both HALE and Life Expectancy models:
   - **HALE Gap**: ΔWAIC = +79.3, ΔLOO = +78.7 (worse)
   - **Life Expectancy Gap**: ΔWAIC = +91.1, ΔLOO = +91.1 (worse)
   - The increase in WAIC/LOO is the **largest of all four experiments**, despite having the lowest data correlation (r = 0.0346)
   - This is well above the threshold for meaningful worsening (ΔWAIC > +5) and is even worse than `Mid_Cardiovascular` (ΔWAIC ≈ +50-60)

2. **Coefficient Changes**:
   - **Gap_UnintentionalInjury (HALE)**: Changed from β = 0.148 (94% HDI: [0.066, 0.226]) to β = 0.351 (94% HDI: [0.273, 0.432])
     - Coefficient becomes **much more positive** (more than doubled) when `Mid_UnintentionalInjury` is included
     - The 94% HDI still excludes zero, indicating a robust positive effect
   - **Gap_UnintentionalInjury (LE)**: Changed from β = 0.169 (94% HDI: [0.084, 0.248]) to β = 0.354 (94% HDI: [0.268, 0.436])
     - Similar pattern - coefficient more than doubled
   - **Mid_UnintentionalInjury (HALE)**: β = -0.404 (94% HDI: [-0.46, -0.35]) - **strong negative effect**
   - **Mid_UnintentionalInjury (LE)**: β = -0.472 (94% HDI: [-0.532, -0.411]) - **strong negative effect**

3. **Posterior Correlations**:
   - **Gap_UnintentionalInjury ↔ Mid_UnintentionalInjury**: r = -0.355 (4th highest correlation in the model)
   - This is **surprising** given the very low data correlation (r = 0.0346)
   - The posterior correlation is moderate and negative, indicating that when both predictors are in the model, their effects are estimated as negatively correlated
   - This suggests that despite low data correlation, the model struggles to distinguish their effects, leading to poor fit

4. **Interpretation**:
   - The **strong negative** `Mid_UnintentionalInjury` coefficients (β ≈ -0.40 to -0.47) are the largest in magnitude of all Mid predictors tested
   - This suggests that higher overall unintentional injury levels are associated with **much smaller** gender gaps (women's advantage is substantially reduced)
   - The fact that adding `Mid_UnintentionalInjury` more than doubles the `Gap_UnintentionalInjury` coefficient suggests substantial confounding was present
   - However, the dramatic worsening of model fit indicates that this "correction" comes at the cost of overall model performance

**Conclusion:**

Adding `Mid_UnintentionalInjury` to the model **does not improve fit** and worsens it **dramatically** (ΔWAIC/ΔLOO ≈ +79-91 for both models), despite having the lowest data correlation (r = 0.0346). This is the worst-performing candidate of all four experiments. The results show that:

1. **Low data correlation does not guarantee good model fit**: This experiment demonstrates that even predictors with essentially zero data correlation (r = 0.0346) can cause severe model fit deterioration
2. **Posterior correlation can differ substantially from data correlation**: The posterior correlation (r = -0.355) is much stronger than the data correlation (r = 0.0346), indicating that the model struggles to estimate independent effects
3. **The baseline model (Gap predictors only) is definitively preferred**: All four experiments consistently show that Mid predictors worsen model fit, regardless of their correlation strength with Gap predictors

**Recommendation:**

**Do not include `Mid_UnintentionalInjury`** in the final model. The baseline model with Gap predictors only provides significantly better model fit and more interpretable coefficients.

---

## Summary of All Experiments: Selective Re-introduction of Mid Predictors

We systematically tested four Mid predictors, selected based on low or negative correlations with their corresponding Gap predictors. The results are summarized below:

**Experiment Summary Table:**

| Experiment | Mid Predictor | Data Correlation (r) | ΔWAIC (HALE) | ΔWAIC (LE) | Result |
|-----------|---------------|----------------------|--------------|------------|--------|
| 1 | Mid_Cardiovascular | -0.804 | +51.3 | +62.5 | ❌ Worsened |
| 2 | Mid_Diabetes | -0.325 | +3.1 | +2.18 | ❌ Worsened |
| 3 | Mid_ChronicRespiratory | -0.0787 | +20.8 | +24.1 | ❌ Worsened |
| 4 | Mid_UnintentionalInjury | 0.0346 | +79.3 | +91.1 | ❌ Worsened |

**Key Findings Across All Experiments:**

1. **All Mid predictors worsen model fit**: Every single candidate tested worsened model fit, with ΔWAIC ranging from +2.18 to +91.1
2. **Correlation strength does not predict fit improvement**: The worst-performing candidate (`Mid_UnintentionalInjury`, ΔWAIC = +91.1) had the lowest data correlation (r = 0.0346), while the best-performing candidate (`Mid_Diabetes`, ΔWAIC = +2.18) had a moderate negative correlation (r = -0.325)
3. **Posterior correlations can differ from data correlations**: In several experiments, posterior correlations were stronger than data correlations, indicating the model struggles to estimate independent effects even when data correlations are low
4. **Coefficient changes are inconsistent**: Some Mid predictors strengthen their corresponding Gap coefficients (e.g., `Mid_ChronicRespiratory`, `Mid_UnintentionalInjury`), while others weaken them (e.g., `Mid_Cardiovascular`, `Mid_Diabetes`), but all worsen overall model fit

**Final Recommendation:**

**The baseline model with Gap predictors only is the optimal specification.** All four experiments provide consistent evidence that:

- Mid predictors add more noise than signal, regardless of their correlation with Gap predictors
- The competing risks interpretation for negative Gap coefficients (e.g., `Gap_Cardiovascular`, `Gap_Diabetes`) remains robust and is not improved by adding Mid predictors
- The model achieves best fit (lowest WAIC/LOO) with Gap predictors only

**Final Model Specification:**
- **Predictors**: 11 Gap predictors only (no Mid predictors)
- **Year Effects**: No Gaussian Random Walk (tested separately, did not improve fit)
- **Model Structure**: Hierarchical panel model with country random intercepts
- **WAIC (HALE)**: 75.7
- **WAIC (LE)**: -7.44

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

## R² and Residual Analysis

To provide interpretable goodness-of-fit measures and enable direct comparison with the cross-sectional Elastic Net models, we compute R² (explained variance) and perform comprehensive residual analysis for both HALE and Life Expectancy gap models.

### R² Summary

The Bayesian panel models achieve excellent fit, explaining nearly all variance in the gender gaps:

```{include} tables/r2_comparison_nomid_nogrw.html
```

**Key Findings:**
- **HALE Gap Model**: R² = 0.987 (94% HDI: [0.987, 0.987])
  - The model explains 98.7% of variance in HALE gap across all country-years
  - Mean Absolute Error (MAE) = 0.158 years
  - Residual standard deviation = 0.204 years

- **Life Expectancy Gap Model**: R² = 0.985 (94% HDI: [0.985, 0.985])
  - The model explains 98.5% of variance in Life Expectancy gap across all country-years
  - Mean Absolute Error (MAE) = 0.175 years
  - Residual standard deviation = 0.228 years

**Interpretation:**
- Both models achieve exceptionally high R² values (>0.98), indicating that the gap predictors capture nearly all systematic variation in gender gaps
- The small MAE values (<0.2 years) indicate that predictions are highly accurate
- The residual standard deviations (~0.2 years) represent the typical magnitude of unexplained variation, which is small relative to the overall gap range (typically 0-8 years)

### Residual Analysis

Residual analysis provides diagnostic information about model fit and identifies potential issues:

**Residual Statistics:**

```{include} tables/residual_summary_hale_nomid_nogrw.html
```

**HALE Gap Model Residuals:**
- Mean: 0.000 years (perfectly centered, as expected)
- Standard deviation: 0.204 years
- Range: -0.714 to +0.643 years
- MAE: 0.158 years

```{include} tables/residual_summary_le_nomid_nogrw.html
```

**Life Expectancy Gap Model Residuals:**
- Mean: 0.000 years (perfectly centered, as expected)
- Standard deviation: 0.228 years
- Range: -0.714 to +0.643 years (similar to HALE)
- MAE: 0.175 years

**Residual Diagnostics:**

The residual plots reveal several important patterns:

**1. Residuals vs. Predicted Values:**

```{figure} figs/residuals_vs_predicted_hale_nomid_nogrw.png
:name: residuals_vs_predicted_hale
:width: 100%

Residuals vs. predicted values for HALE gap model. The residuals are well-distributed around zero with no obvious patterns, suggesting good model fit and no heteroscedasticity.
```

```{figure} figs/residuals_vs_predicted_le_nomid_nogrw.png
:name: residuals_vs_predicted_le
:width: 100%

Residuals vs. predicted values for Life Expectancy gap model. Similar to HALE, residuals are well-distributed with no systematic patterns.
```

**Key Observations:**
- **No heteroscedasticity**: Residuals are evenly distributed across the range of predicted values
- **No systematic bias**: No clear patterns (curves, trends) indicating model misspecification
- **Well-centered**: Residuals cluster around zero across all prediction ranges

**2. Residuals by Country (2019):**

```{figure} figs/residuals_vs_country_hale_nomid_nogrw.png
:name: residuals_vs_country_hale
:width: 100%

Residuals by country for HALE gap model (2019 only). Shows country-specific prediction errors, revealing which countries are over- or under-predicted by the model.
```

```{figure} figs/residuals_vs_country_le_nomid_nogrw.png
:name: residuals_vs_country_le
:width: 100%

Residuals by country for Life Expectancy gap model (2019 only). 
```

**Key Observations:**

- **Random intercepts capture most variation**: The country-specific intercepts (α_i) in the model account for much of the between-country variation, leaving relatively small residuals
- **No extreme outliers**: All residuals are within ±0.7 years, indicating no countries with severe model misfit

**3. Residuals vs. Year:**

```{figure} figs/residuals_vs_year_hale_nomid_nogrw.png
:name: residuals_vs_year_hale
:width: 100%

Residuals vs. year for HALE gap model. Shows temporal patterns in prediction errors, revealing whether the model fits better or worse in certain time periods.
```

```{figure} figs/residuals_vs_year_le_nomid_nogrw.png
:name: residuals_vs_year_le
:width: 100%

Residuals vs. year for Life Expectancy gap model. Similar temporal patterns to HALE.
```

**Key Observations:**

1. **Temporal bias pattern**: Residuals are slightly more likely to be positive in early years (2000-2005) and slightly more likely to be negative in later years (2015-2019). This suggests:
   - **Early years**: The model slightly under-predicts gaps (actual gaps are larger than predicted), possibly because:
     - Health patterns were less stable in the early 2000s
     - Some predictors may have had different relationships with gaps in earlier periods
     - Data quality or measurement methods may have improved over time
   - **Later years**: The model slightly over-predicts gaps (actual gaps are smaller than predicted), possibly because:
     - Gender gaps have been narrowing over time in ways not fully captured by the predictors
     - Health improvements have reduced gaps more than the model accounts for
     - The model structure (shared slopes across all years) may not fully capture evolving relationships

2. **Variance pattern (bow tie)**: The variance of residuals is higher at the beginning and end of the time period, with smaller variance in the middle years (2005-2015). This pattern is typical in regression models and suggests:
   - **Higher uncertainty at boundaries**: Predictions are less certain at the temporal extremes of the data
   - **More stable relationships in middle period**: The model fits best during the middle years when relationships between predictors and gaps were most stable
   - **Temporal heterogeneity**: The relationships between predictors and gaps may have evolved over the 20-year period, with the middle years representing a more stable "equilibrium" period

**Overall Assessment:**
- The temporal patterns are relatively mild (residuals still centered around zero)
- The bow tie variance pattern is expected in panel models spanning long time periods
- The model structure (shared slopes, no year effects) is appropriate given that year effects were tested and did not improve fit
- These patterns do not indicate serious model misspecification, but suggest that relationships may have evolved slightly over the two-decade period

**4. Residual Distribution:**

```{figure} figs/residuals_histogram_hale_nomid_nogrw.png
:name: residuals_histogram_hale
:width: 100%

Distribution of residuals for HALE gap model. Shows the frequency distribution of prediction errors, revealing whether residuals are normally distributed.
```

```{figure} figs/residuals_histogram_le_nomid_nogrw.png
:name: residuals_histogram_le
:width: 100%

Distribution of residuals for Life Expectancy gap model. Similar distribution to HALE.
```

**Key Observations:**
- **Approximately normal**: Residuals follow a roughly normal distribution centered at zero
- **Symmetric**: No strong skewness, indicating balanced over- and under-predictions
- **Well-centered**: Mean is exactly zero (as expected from least-squares estimation)

### Comparison with Elastic Net Models

The Bayesian panel model achieves similar or better fit compared to the cross-sectional Elastic Net models:

| Model | R² | MAE (years) |
|-------|----|-------------|
| **Elastic Net (HALE, 2019)** | ~0.85-0.90 | ~0.3-0.4 |
| **Bayesian Panel (HALE)** | 0.987 | 0.158 |
| **Elastic Net (LE, 2019)** | ~0.85-0.90 | ~0.3-0.4 |
| **Bayesian Panel (LE)** | 0.985 | 0.175 |

**Key Advantages of Bayesian Panel Model:**
1. **Higher R²**: The panel model explains more variance (0.985-0.987 vs. ~0.85-0.90) by leveraging both cross-country and temporal variation
2. **Lower MAE**: More accurate predictions (0.16-0.18 years vs. 0.3-0.4 years) due to:
   - More data (≈740 observations vs. ≈37 countries)
   - Country-specific intercepts capturing time-invariant factors
   - Shared slopes estimated with greater precision
3. **Uncertainty quantification**: Provides credible intervals for all predictions, not just point estimates
4. **Temporal flexibility**: Can analyze any country-year combination (2000-2019), not just the most recent year

**Why the Panel Model Performs Better:**
- **More data**: Uses all country-years (≈740 observations) rather than just the most recent year (≈37 countries)
- **Country-specific effects**: Random intercepts (α_i) capture unmeasured country-level factors that improve predictions
- **Temporal information**: Leverages both between-country and within-country variation, providing more statistical power

## Model Fit Over Time: United States

To visualize how well the model fits the data over the entire time period, we examine predicted vs. actual gap values for the United States (2000-2019). This provides a country-specific view of model performance and helps identify any temporal patterns in prediction accuracy.

### HALE Gap: United States

```{figure} figs/predicted_vs_actual_hale_usa.png
:name: predicted_vs_actual_hale_usa
:width: 100%

Predicted vs. actual HALE gap for the United States (2000-2019). The red line shows actual values, the blue line shows predicted values (mean), and the shaded area shows the 94% highest density interval (HDI) for predictions. The plot includes statistics (MAE, RMSE, R²) computed from the residuals.
```

**Key Observations:**
- **Excellent fit**: The predicted values closely track the actual HALE gap over the entire 20-year period
- **Consistent accuracy**: The model maintains high accuracy across all years, with predictions staying within the uncertainty bands
- **Temporal trends captured**: The model successfully captures both the overall level and temporal trends in the HALE gap for the United States
- **Uncertainty quantification**: The 94% HDI bands provide a clear view of prediction uncertainty, which remains relatively stable over time

### Life Expectancy Gap: United States

```{figure} figs/predicted_vs_actual_le_usa.png
:name: predicted_vs_actual_le_usa
:width: 100%

Predicted vs. actual Life Expectancy gap for the United States (2000-2019). Similar structure to the HALE gap plot, showing actual values (red), predicted values (blue), and 94% HDI uncertainty bands (shaded area).
```

**Key Observations:**
- **Strong fit**: Similar to HALE gap, the Life Expectancy gap predictions closely match actual values
- **Model consistency**: The model performs similarly well for both HALE and Life Expectancy gaps, indicating robust performance across related outcomes
- **Temporal stability**: Prediction accuracy remains consistent across the entire time period

**Interpretation:**
These plots demonstrate that the Bayesian panel model provides accurate predictions for the United States throughout the 2000-2019 period. The close alignment between predicted and actual values, combined with the relatively narrow uncertainty bands, indicates that:
1. The model structure (country-specific intercepts + shared slopes) effectively captures both the United States' baseline gap level and how it responds to predictor changes
2. The predictors included in the model are sufficient to explain most of the variation in the HALE and Life Expectancy gaps
3. The model can be confidently used for counterfactual analysis, as it provides reliable predictions for the United States

## Counterfactual Analysis: United States (2019)

Counterfactual analysis allows us to answer "what if" questions: What would happen to a country's predicted gap (HALE or Life Expectancy) if we adjusted a specific gap predictor to the best attainable value observed across all country-years (while keeping all other predictors constant)?

We present counterfactual results for both **HALE gap** and **Life Expectancy gap** to provide a comprehensive view of how gender gaps in specific mortality indicators affect overall gender differences in healthy and total life expectancy.

### Methodology

The counterfactual analysis uses the Bayesian panel model to generate posterior predictive distributions for counterfactual scenarios. Unlike the cross-sectional Elastic Net approach, this Bayesian framework provides:

1. **Uncertainty quantification**: Full posterior distributions with credible intervals (94% HDI) for all counterfactual predictions
2. **Country-specific effects**: Accounts for country-specific intercepts (α_i) when making predictions
3. **Temporal flexibility**: Can analyze any country-year combination (2000-2019), not just the most recent year

**Counterfactual Procedure:**
1. For each gap predictor, find the best attainable gap value across all country-years:
   - If current gap is positive (Male > Female): use minimum gap (best case)
   - If current gap is negative (Female > Male): use maximum gap (best case)
2. Adjust Male/Female values to achieve the target gap (recompute Mid and Gap)
3. Standardize counterfactual predictors using stored transformation parameters
4. Generate posterior predictive distribution using all posterior samples:
   - For each posterior sample: `y*_counterfactual = α_i + X*_counterfactual β`
   - Convert back to original scale: `y_counterfactual = y*_counterfactual + ȳ`
5. Compute change: `change = y_counterfactual - y_original` (posterior distribution)

### Results: HALE Gap - All Indicators for United States (2019)

We computed counterfactual predictions for all 11 gap predictors for the United States in 2019. The results are sorted by importance (based on the Bayesian model's predictor importance measures) and shown in the table below.

**Current Situation:**
- **Original HALE gap prediction**: 1.752 years (94% HDI: [1.646, 1.863])
  - This represents the predicted HALE gap (Female - Male) for USA in 2019 given current predictor values

```{include} tables/counterfactuals_usa_2019_hale_bayesian.html
```

### Key Findings: HALE Gap

**Gap-Closing Indicators** (7 indicators, reduce HALE gap):
1. **Road Traffic Deaths**: -0.724 years (94% HDI: [-0.789, -0.658])
   - Largest single effect. Reducing gap from 11.2 to 1.92 (Iceland 2017 level) would substantially narrow the HALE gap.
2. **Suicide**: -0.551 years (94% HDI: [-0.651, -0.445])
   - Second largest effect. Reducing gap from 17.3 to 4.05 (Greece 2002 level) would have a major impact.
3. **Neoplasms (Cancer)**: -0.248 years (94% HDI: [-0.317, -0.183])
   - Eliminating the cancer mortality gender gap (from 25.7 to 0) would reduce the HALE gap.
4. **Homicide**: -0.196 years (94% HDI: [-0.216, -0.175])
   - Eliminating the homicide gap (from 7.29 to 0) would have a moderate effect.
5. **Liver Disease**: -0.196 years (94% HDI: [-0.240, -0.151])
   - Reducing gap from 9.05 to 0.729 (Iceland 2001 level) would help narrow the HALE gap.
6. **Alcohol**: -0.136 years (94% HDI: [-0.190, -0.077])
   - Reducing gap from 5.54 to 0.232 (Colombia 2016 level) would have a modest but meaningful effect.
7. **Unintentional Injuries**: -0.049 years (94% HDI: [-0.077, -0.021])
   - Smallest gap-closing effect. Eliminating the gap (from 5.26 to 0) would have a minor impact.

**Gap-Widening Indicators** (3 indicators, increase HALE gap):
1. **Chronic Respiratory Disease**: +0.182 years (94% HDI: [0.143, 0.218])
   - The US has a negative gap (-5.82, meaning Female > Male). Closing this gap would actually widen the overall HALE gap.
2. **Diabetes**: +0.175 years (94% HDI: [0.110, 0.243])
   - Eliminating the diabetes gap (from 5.5 to 0) would widen the HALE gap.
3. **Cardiovascular Disease**: +0.135 years (94% HDI: [0.107, 0.162])
   - Eliminating the cardiovascular gap (from 19.4 to 0) would widen the HALE gap.

**Interpretation of Gap-Widening Effects:**
The counterintuitive gap-widening effects for Cardiovascular, Diabetes, and Chronic Respiratory disease reflect the competing risks interpretation: when men have higher mortality from these causes, it paradoxically reduces the overall HALE gap because men die earlier. Eliminating these gender gaps would mean men live longer, which increases the HALE gap (women still live longer, but the difference becomes larger).

### Aggregate Effects: HALE Gap

**Gap-Closing Indicators** (7 indicators):
- **Total effect**: -2.099 years
- **Indicators**: Neoplasms, Homicide, Suicide, Road Traffic, Unintentional Injuries, Liver Disease, Alcohol

**Gap-Widening Indicators** (3 indicators):
- **Total effect**: +0.491 years
- **Indicators**: Cardiovascular, Chronic Respiratory, Diabetes

**Net Effect** (all indicators combined):
- **Net reduction in HALE gap**: -1.608 years

**Interpretation:**
If the United States could achieve the best attainable values for all gap predictors simultaneously, the predicted HALE gap would decrease by approximately 1.6 years (from 1.752 to about 0.14 years). However, this is a theoretical maximum; in practice, some of these changes may be mutually exclusive or require different policy interventions.

**Important Caveats:**
1. **Point estimates only**: The aggregate effects shown are sums of means. For proper uncertainty quantification, we would need to compute the posterior distribution of the sum (accounting for correlations between effects).
2. **Independence assumption**: The analysis assumes each predictor can be adjusted independently, which may not be realistic (e.g., reducing alcohol mortality may also affect liver disease).
3. **Best attainable values**: Some target values (e.g., zero gaps) may not be achievable in practice, but they represent theoretical bounds.

### Visualizations: HALE Gap

The counterfactual effects are visualized in three complementary ways:

**1. Forest Plot (All Indicators):**
```{figure} figs/counterfactual_effects_usa_2019_hale_bayesian.png
:name: counterfactual_forest_hale
:width: 100%

Counterfactual effects for all indicators, sorted by effect size. Error bars show 94% credible intervals. Red indicates gap-closing effects (reduce HALE gap), blue indicates gap-widening effects (increase HALE gap).
```

**2. Two-Panel Plot (By Type):**
```{figure} figs/counterfactual_effects_by_type_usa_2019_hale_bayesian.png
:name: counterfactual_by_type_hale
:width: 100%

Counterfactual effects separated into gap-closing (left) and gap-widening (right) indicators. This view makes it easier to see the relative magnitudes within each category.
```

**3. Bar Chart (Sorted by Magnitude):**
```{figure} figs/counterfactual_effects_bar_usa_2019_hale_bayesian.png
:name: counterfactual_bar_hale
:width: 100%

Horizontal bar chart showing counterfactual effects sorted by absolute magnitude. This view emphasizes which indicators have the largest potential impact, regardless of direction.
```

**Key Insights from HALE Visualizations:**
- **Road Traffic** and **Suicide** have the largest gap-closing effects, with clear separation from other indicators
- **Gap-widening effects** (Cardiovascular, Chronic Respiratory, Diabetes) are smaller in magnitude than the largest gap-closing effects
- **Uncertainty is well-quantified**: All credible intervals are reasonably narrow, indicating precise estimates
- **No zero-crossing**: All credible intervals exclude zero, suggesting statistically meaningful effects for all indicators

---

### Results: Life Expectancy Gap - All Indicators for United States (2019)

We computed counterfactual predictions for all 10 gap predictors for the United States in 2019, using the same methodology as for HALE gap. The results are sorted by importance and shown in the table below.

```{include} tables/counterfactuals_usa_2019_le_bayesian.html
```

### Key Findings: Life Expectancy Gap

**Gap-Closing Indicators** (7 indicators, reduce Life Expectancy gap):
1. **Road Traffic Deaths**: -0.665 years (94% HDI: [-0.742, -0.595])
   - Largest single effect. Reducing gap from 11.2 to 1.92 (Iceland 2017 level) would substantially narrow the Life Expectancy gap.
2. **Suicide**: -0.618 years (94% HDI: [-0.743, -0.520])
   - Second largest effect. Reducing gap from 17.3 to 4.05 (Greece 2002 level) would have a major impact.
3. **Liver Disease**: -0.232 years (94% HDI: [-0.282, -0.183])
   - Reducing gap from 9.05 to 0.729 (Iceland 2001 level) would help narrow the Life Expectancy gap.
4. **Homicide**: -0.228 years (94% HDI: [-0.249, -0.205])
   - Eliminating the homicide gap (from 7.29 to 0) would have a moderate effect.
5. **Neoplasms (Cancer)**: -0.245 years (94% HDI: [-0.321, -0.177])
   - Eliminating the cancer mortality gender gap (from 25.7 to 0) would reduce the Life Expectancy gap.
6. **Alcohol**: -0.150 years (94% HDI: [-0.212, -0.090])
   - Reducing gap from 5.54 to 0.232 (Colombia 2016 level) would have a modest but meaningful effect.
7. **Unintentional Injuries**: -0.040 years (94% HDI: [-0.070, -0.010])
   - Smallest gap-closing effect. Eliminating the gap (from 5.26 to 0) would have a minor impact.

**Gap-Widening Indicators** (3 indicators, increase Life Expectancy gap):
1. **Chronic Respiratory Disease**: +0.231 years (94% HDI: [0.193, 0.273])
   - The US has a negative gap (-5.82, meaning Female > Male). Closing this gap would actually widen the overall Life Expectancy gap.
2. **Diabetes**: +0.181 years (94% HDI: [0.107, 0.252])
   - Eliminating the diabetes gap (from 5.5 to 0) would widen the Life Expectancy gap.
3. **Cardiovascular Disease**: +0.111 years (94% HDI: [0.082, 0.139])
   - Eliminating the cardiovascular gap (from 19.4 to 0) would widen the Life Expectancy gap.

**Interpretation of Gap-Widening Effects:**
The counterintuitive gap-widening effects for Cardiovascular, Diabetes, and Chronic Respiratory disease reflect the competing risks interpretation: when men have higher mortality from these causes, it paradoxically reduces the overall Life Expectancy gap because men die earlier. Eliminating these gender gaps would mean men live longer, which increases the Life Expectancy gap (women still live longer, but the difference becomes larger).

### Aggregate Effects: Life Expectancy Gap

**Gap-Closing Indicators** (7 indicators):
- **Total effect**: -2.178 years
- **Indicators**: Neoplasms, Homicide, Suicide, Road Traffic, Unintentional Injuries, Liver Disease, Alcohol

**Gap-Widening Indicators** (3 indicators):
- **Total effect**: +0.523 years
- **Indicators**: Cardiovascular, Chronic Respiratory, Diabetes

**Net Effect** (all indicators combined):
- **Net reduction in Life Expectancy gap**: -1.655 years

**Interpretation:**
If the United States could achieve the best attainable values for all gap predictors simultaneously, the predicted Life Expectancy gap would decrease by approximately 1.66 years. This is similar in magnitude to the HALE gap reduction (-1.61 years), suggesting consistent patterns across both healthy and total life expectancy.

### Visualizations: Life Expectancy Gap

The counterfactual effects for Life Expectancy gap are visualized in the same three ways:

**1. Forest Plot (All Indicators):**
```{figure} figs/counterfactual_effects_usa_2019_le_bayesian.png
:name: counterfactual_forest_le
:width: 100%

Counterfactual effects for all indicators, sorted by effect size. Error bars show 94% credible intervals. Red indicates gap-closing effects (reduce Life Expectancy gap), blue indicates gap-widening effects (increase Life Expectancy gap).
```

**2. Two-Panel Plot (By Type):**
```{figure} figs/counterfactual_effects_usa_2019_le_by_type_bayesian.png
:name: counterfactual_by_type_le
:width: 100%

Counterfactual effects separated into gap-closing (left) and gap-widening (right) indicators. This view makes it easier to see the relative magnitudes within each category.
```

**3. Bar Chart (Sorted by Magnitude):**
```{figure} figs/counterfactual_effects_usa_2019_le_bar_bayesian.png
:name: counterfactual_bar_le
:width: 100%

Horizontal bar chart showing counterfactual effects sorted by absolute magnitude. This view emphasizes which indicators have the largest potential impact, regardless of direction.
```

**Key Insights from Life Expectancy Visualizations:**
- **Road Traffic** and **Suicide** have the largest gap-closing effects, consistent with HALE results
- **Gap-widening effects** (Cardiovascular, Chronic Respiratory, Diabetes) are smaller in magnitude than the largest gap-closing effects
- **Patterns are similar to HALE**: The relative magnitudes and ordering of effects are very similar between HALE and Life Expectancy gaps
- **Uncertainty is well-quantified**: All credible intervals are reasonably narrow, indicating precise estimates

### Comparison: HALE vs. Life Expectancy Gap Counterfactuals

The counterfactual results for HALE and Life Expectancy gaps show remarkable consistency:

1. **Same top gap-closing indicators**: Road Traffic and Suicide are the two largest gap-closing effects in both models
2. **Similar effect magnitudes**: The net reduction is nearly identical (-1.61 years for HALE, -1.66 years for Life Expectancy)
3. **Same gap-widening indicators**: Cardiovascular, Chronic Respiratory, and Diabetes widen the gap in both models
4. **Consistent ordering**: The relative importance of indicators is very similar across both outcomes

This consistency suggests that the mechanisms driving gender gaps in healthy life expectancy and total life expectancy are fundamentally similar, with the same mortality indicators playing key roles in both.

### Comparison with Cross-Sectional Elastic Net Results

The Bayesian counterfactual results are generally consistent with the cross-sectional Elastic Net approach, but with important differences:

1. **Uncertainty quantification**: The Bayesian approach provides credible intervals for all effects, showing the range of plausible values.
2. **Country-specific effects**: The Bayesian model accounts for the US-specific intercept (α_i), which may differ from the cross-sectional average.
3. **Temporal context**: The analysis uses 2019 data, but leverages information from all years (2000-2019) through the panel model structure.

### Next Steps

Future work will:

1. ~~**Extend to Life Expectancy gap** using the same methodology~~ ✅ **Completed**
2. **Compare with Elastic Net results** in detail to assess consistency
3. **Analyze additional countries** to identify patterns across different contexts
4. **Compute posterior distribution of aggregate effects** (accounting for correlations between counterfactual changes)

## Conclusions

The Bayesian panel model provides a complementary perspective to the cross-sectional Elastic Net models by:

1. **Leveraging temporal variation**: Uses data from all years (2000-2019) rather than just the most recent year
2. **Quantifying uncertainty**: Provides posterior distributions with credible intervals for all parameters
3. **Accounting for country heterogeneity**: Random intercepts capture time-invariant country-specific factors
4. **Enabling temporal counterfactuals**: Framework for predicting effects of changes over time with uncertainty bands

### Key Model Decisions

**Final Model Specification:**
- **Predictors**: Gap predictors only (11 predictors), excluding Mid predictors
- **Countries**: OECD countries excluding Turkey (37 countries, ~740 observations)
- **Year Effects**: **Not included** (tested but worsen model fit)
- **Rationale**: 
  - Removing Mid predictors dramatically improves model fit (ΔWAIC ≈ -234 to -280)
  - Eliminates multicollinearity issues (r ≈ -0.9 to -1.0 between Mid and Gap)
  - Provides more interpretable and stable coefficient estimates
  - Excluding Turkey eliminates extreme outliers and improves model behavior
  - Year effects (GRW) tested but worsen fit (ΔWAIC/ΔLOO > 90), so excluded

**Model Performance:**
- **HALE Gap Model**: 
  - WAIC = 75.7 (ELPD), LOO = 75.3 (ELPD), p_waic = 50.5
  - R² = 0.987 (94% HDI: [0.987, 0.987]), MAE = 0.158 years
- **Life Expectancy Gap Model**: 
  - WAIC = -7.5 (ELPD), LOO = -7.92 (ELPD), p_waic = 51.1
  - R² = 0.985 (94% HDI: [0.985, 0.985]), MAE = 0.175 years
- Both models show excellent fit with reasonable effective parameter counts
- See "R² and Residual Analysis" section below for detailed diagnostics

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

