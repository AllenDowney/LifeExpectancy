# Healthy Life Expectancy and the Gender Gap — draft

*This is Part 5 in a series on gender gaps in life expectancy, what causes them, and what we can do about it.*

*Draft for review: same HALE outputs as the Bayesian panel model (IHME HALE and causes, 2000–2023), parallel to [Part 2](blog2_model.md) (LE coefficients and importance), [Part 3](blog3_counterfactual.md) (counterfactuals), and [Part 4](blog4_international.md) (intercepts). Narrative and wrap-up text still to finish.*

Figures below **alternate life expectancy (LE)** and **healthy life expectancy (HALE)** so pairs are easy to compare. (LE panels use OWID life expectancy; HALE uses IHME GBD 2023. Same model structure and cause gaps for both.)

---

## 1. Gap in time and place (LE, then HALE)

**Life expectancy gap (OWID).** Same ensemble post as [Part 1](blog1_time_series.md).

```{figure} figs/le_gap_timeseries_selected.png
:width: 80%

LE gender gap (2000–2023), selected OECD countries in color, remainder in gray.
```

**Healthy life expectancy gap (IHME).** Same highlighted countries as the LE panel.

```{figure} figs/hale_gap_timeseries_blog_match.png
:width: 80%

HALE gender gap (2000–2023), same highlighted countries as above; other OECD countries in gray. Generated from `notebooks/time_series_figs.md`.
```

---

## 2. Model: coefficients, importance, and residuals

The Bayesian hierarchical panel shares cause-specific death-rate gaps as predictors; only the outcome differs (LE gap vs HALE gap). Below: posterior mean and 94% credible intervals for β, then \|β\| × cross-country–year SD (importance), then residual checks (predicted vs actual for four countries; residuals by country). LE figures match [Part 2](blog2_model.md); HALE figures come from `notebooks/bayesian_le_figs.md`.

**Coefficients — LE.**

```{figure} figs/blog2_coefficients_le.png
:width: 80%

Predictor coefficients for the **life expectancy** gender gap (posterior mean and 94% intervals). OECD, 2000–2023.
```

**Coefficients — HALE.**

```{figure} figs/coefficients_hale.png
:width: 80%

Predictor coefficients for the **HALE** gender gap (posterior mean and 94% intervals). OECD, 2000–2023.
```

**Coefficient ordering (LE vs HALE).** With the same cause-specific gap predictors, ranking by posterior mean \|β\| (largest first) lines up for the two outcomes but is not identical. **Road traffic** is strongest in both; **suicide** and **alcohol** keep the same slots (third and ninth). **Chronic respiratory (lung disease)** is second for HALE but fifth for LE. **Homicide** and **cancer** rank higher for LE (2nd and 4th) than for HALE (4th and 6th). **Cardiovascular** moves from seventh (LE) to fifth (HALE); **liver disease** from sixth to eighth. **Injury** is eighth for LE and seventh for HALE. **Diabetes** is twelfth for LE and tenth for HALE. The smallest \|β\| is **childhood (under-five)** in both. In the lower tail, LE orders **diabetes**, **drug disorders**, then **COVID-19**; HALE orders **drug disorders**, **COVID-19**, then **diabetes**.

**Importance — LE.**

```{figure} figs/blog2_importance_le.png
:width: 80%

Predictor importance for the LE gap (\|β\| × SD on the original scale).
```

**Importance — HALE.**

```{figure} figs/importance_hale.png
:width: 80%

Predictor importance for the HALE gap (\|β\| × SD on the original scale).
```

**Residuals: predicted vs actual — LE.** Colored lines = actual; gray vertical segments = 94% credible intervals for the fitted level ([Part 2](blog2_model.md), Iceland, USA, Lithuania, France).

```{figure} figs/blog2_residuals_timeseries_le.png
:width: 80%

LE: predicted vs actual gap (2000–2023), selected countries.
```

**Residuals: predicted vs actual — HALE.** Same country set as LE.

```{figure} figs/residuals_timeseries_hale.png
:width: 80%

HALE: predicted vs actual gap (2000–2023), selected countries.
```

**Residuals by country — LE.**

```{figure} figs/blog2_residuals_by_country_le.png
:width: 80%

LE model residuals by country (years); boxes summarize spread over 2000–2023 (sorted so tighter fits toward the top).
```

**Residuals by country — HALE.**

```{figure} figs/residuals_by_country_hale.png
:width: 80%

HALE model residuals by country (years); same layout as LE.
```

---

## 3. Counterfactuals (USA, 2023): LE then HALE

Same “best attainable gap” logic as [Part 3](blog3_counterfactual.md) for LE; parallel HALE run in `notebooks/bayes_counter_hale.md`. Tables and figures alternate.

**Minimum observed rate gaps (LE).**

```{include} tables/gap_extremes_min_blog_le.html
```

**Minimum observed rate gaps (HALE).**

```{include} tables/gap_extremes_min_blog_hale.html
```

**Counterfactual changes if each gap matched its best observed level — LE (table).**

```{include} tables/counterfactuals_usa_2023_le_blog.html
```

**Counterfactual changes — HALE (table).**

```{include} tables/counterfactuals_usa_2023_hale_blog.html
```

**Counterfactual effects (figure) — LE.**

```{figure} figs/counterfactual_effects_usa_2023_le_bayesian.png
:width: 80%

LE: hypothetical change in predicted gap if each cause-specific death-rate gap matched the best observed country-year, USA 2023, with 94% credible intervals.
```

**Counterfactual effects (figure) — HALE.**

```{figure} figs/counterfactual_effects_usa_2023_hale_bayesian.png
:width: 80%

HALE: same counterfactual definition for the HALE gap, USA 2023.
```

**Positive contributions over time (stacked) — LE.**

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:width: 80%

LE: positive (gap-closing) contributions over time, USA — stacked components vs predicted and actual LE gap.
```

**Positive contributions over time (stacked) — HALE.**

```{figure} figs/positive_contributions_stacked_area_usa_hale.png
:width: 80%

HALE: stacked gap-closing contributions vs predicted and actual HALE gap, USA.
```

**Contributions as % of actual gap — LE.**

```{figure} figs/positive_contributions_percentage_usa_le.png
:width: 80%

LE: gap-closing contributions as a percentage of the actual LE gap, USA over time.
```

**Contributions as % of actual gap — HALE.**

```{figure} figs/positive_contributions_percentage_usa_hale.png
:width: 80%

HALE: gap-closing contributions as a percentage of the actual HALE gap, USA over time.
```

**Predicted vs actual — LE (USA).**

```{figure} figs/predicted_vs_actual_le_usa.png
:width: 80%

LE: predicted vs actual gap, United States.
```

**Predicted vs actual — HALE (USA).**

```{figure} figs/predicted_vs_actual_hale_usa.png
:width: 80%

HALE: predicted vs actual gap, United States.
```

---

## 4. Country intercepts (LE, then HALE)

Parallel to [Part 4](blog4_international.md): country-specific random effects.

**LE.**

```{figure} figs/country_intercepts_le_intercepts.png
:width: 80%

Country intercepts for the LE gap model, 94% credible intervals.
```

**HALE.**

```{figure} figs/country_intercepts_hale_intercepts.png
:width: 80%

Country intercepts for the HALE gap model, 94% credible intervals.
```

---

## 5. LE vs HALE (optional overview)

```{figure} figs/gap_comparison_hale_vs_le.png
:width: 80%

Comparison of gender gaps: HALE vs life expectancy (exploratory figure; caption to refine with narrative).
```

---

## 6. Series wrap-up

(To add: GGGR / index-critique and analogy from `blog_plan.md`, Part 5 “Series wrap-up” block.)

---

## Regenerating artifacts

- **LE / HALE coefficient, importance, and HALE residual PNGs:** from `notebooks/`, run  
  `jupytext --to ipynb bayesian_le_figs.md --output bayesian_le_figs.ipynb` then  
  `papermill bayesian_le_figs.ipynb bayesian_le_figs_executed.ipynb`  
  (LE: `blog2_*_le.png`; HALE: `coefficients_hale.png`, `importance_hale.png`, `residuals_timeseries_hale.png`, `residuals_by_country_hale.png`.)
- **Counterfactuals / intercepts:** `notebooks/bayes_counter_le.md` and `notebooks/bayes_counter_hale.md` → papermill.
- **Fit posteriors:** `notebooks/bayesian_model.md` (suffix `*_ihme_nomid_nogrw_y2023_covid`).
