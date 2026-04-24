# Causal framing and CausalPy Models 1 / 1b / 1c: results note

This note summarizes **fixed-effects associational** regressions in **`notebooks/causal_model.md`**, framed by **minimal DAGs**, alongside the main **Bayesian hierarchical** LE model (`notebooks/bayesian_model.md`). It compares **standardized `Gap_*` slopes** (and **residualized** **`Gap_*_resid`** in Model 1c) to the **LE** posterior from the Bayesian notebook.

**Core point:** These runs are **regression implementations of minimal causal hypotheses**, not **fully identified causal estimates**. The DAGs make **structure** explicit; the fitted lines are **associational** unless stronger identification is argued.

---

## What we have done so far

 **`notebooks/causal_model.md`** (same data pipeline for both):

- Panel: **`interim/panel_le.h5`**, **`Gap_*`** from **`utils.gap_predictor_columns`**, excluding **`Gap_MaternalDisorders`** and **`Gap_ConflictTerrorism`**.  
- Outcome: **`LE_gap`** centered (global mean subtracted).  
- Estimator: CausalPy **`LinearRegression`** (Normal priors on coefficients via PyMC).  
- **Model 1 + Model 1c (current notebook):** **country FE** on **`LE_gap`**; **no year FE**. **Model 1** uses globally z-scored raw **`Gap_*`**. **Model 1c** uses **`Gap_*_resid = Gap_* − mean(Gap_* | country)`** over **all years**, z-scored, then **`LE_gap ~ resid_* + country FE`**. Log: **`causal_model_le_with_covid_2023.txt`**. Figures: **`dag_model1_minimal.png`**, **`dag_model1c_country_causes_gaps.png`**, **`causalpy_le_linear_forest_model1_gap_betas.png`**, **`causalpy_le_linear_forest_model1c_resid_gap_betas.png`**.  
- **Model 1b (separate run, not in current notebook):** **country FE + year FE**. Log: **`causal_model_le_1b_with_covid_2023.txt`**. Figures: **`dag_model1b_minimal.png`**, **`causalpy_le_linear_forest_model1b_gap_betas.png`**.

**Planned:** expanded DAG (Model 2); competing-risks DAG (Model 3). **`causalpy`** 0.8.x has no **`CausalModel`** export; DAGs use **`graphviz.Source`** + DOT.

---

## Model 1 vs Model 1b (CausalPy only)

**Design**

| | Model 1 | Model 1b |
|---|---------|----------|
| Country | FE (36 dummies) | FE (36 dummies) |
| Year | **Omitted** | **FE (23 dummies; 2000 reference)** |
| Total coefficients (incl. const, σ) | 50 | 73 |

**Runs reviewed:** Model 1 + 1c log **2026-04-10** (`causal_model_le_with_covid_2023.txt`); Model 1b log **2026-04-10** (`causal_model_le_1b_with_covid_2023.txt`).

| Quantity | Model 1 | Model 1b |
|----------|---------|----------|
| In-sample R² (CausalPy / ArviZ) | **0.978550** | **0.984973** |
| Same data rows | 888 | 888 |

**Posterior means for standardized `Gap_*` (94% HDI in logs):** **Δ = Model 1b − Model 1.**

| Predictor | Model 1 mean | Model 1b mean | Δ |
|-----------|--------------|---------------|---|
| Gap_Alcohol | 0.11 | 0.12 | 0.01 |
| Gap_COVID | 0.11 | 0.12 | 0.01 |
| Gap_Cardiovascular | −0.15 | −0.024 | 0.13 |
| Gap_Childhood | 0.076 | −0.24 | −0.32 |
| Gap_ChronicRespiratory | 0.31 | 0.17 | −0.14 |
| Gap_Diabetes | −0.092 | −0.021 | 0.07 |
| Gap_DrugDisorder | 0.087 | 0.14 | 0.05 |
| Gap_Homicide | 0.43 | 0.43 | 0.00 |
| Gap_LiverDisease | 0.25 | 0.20 | −0.05 |
| Gap_Neoplasms | 0.26 | 0.29 | 0.03 |
| Gap_RoadTraffic | 0.44 | 0.091 | −0.35 |
| Gap_Suicide | 0.34 | 0.28 | −0.06 |
| Gap_UnintentionalInjury | 0.12 | 0.22 | 0.10 |

**Sources (checked against logs, 2026-04-10):** Model 1 — `notebooks/logs/causal_model_le_with_covid_2023.txt`, block `CAUSALPY — MODEL 1 (GLOBAL Z, COUNTRY FE)`, lines **75–87** (posterior means). Model 1b — `notebooks/logs/causal_model_le_1b_with_covid_2023.txt`, lines **77–89**. R²: Model 1 **unit_0_r2** line **127**; Model 1b **unit_0_r2** line **152**.

**Interpretation:** Adding **year fixed effects** changes the **estimand**: slopes are closer to associations **after netting out** a **shared** time pattern in **`LE_gap`** (and implicitly co-moving gap structures). That is **not** the same regression as Model 1, so **large moves**—especially **road traffic**, **childhood**, **chronic respiratory**, and **cardiovascular**—are expected. In **1b**, **cardiovascular** and **diabetes** posterior means are **near zero** and their **94% HDIs overlap zero** (see log); **childhood** turns **negative** with an interval **away** from the Model 1 / Bayesian story. **Homicide** is **stable** across 1 and 1b (≈0.43). **Do not** read Model 1b as a “closer” or “better” causal fit than Model 1 without an explicit estimand; it is a **different** partialing-out of time.

**On R²:** Values are **high** because of **dense FE** and **many predictors**. Treat as **in-sample flexibility**, not **validation** of a causal story.

---

## Model 1c (within-country deviations vs country mean)

**Estimand:** Model 1c estimates how **deviations from a country’s long-run average** cause-specific **gap** are associated with **`LE_gap`**, with the same **country FE** on the outcome as Model 1. (Outcome: **`LE_gap`** globally centered; **country dummies** absorb country-specific levels of **`LE_gap`**, so slopes on **`resid_*`** speak to **within-country** variation in gaps **relative to** each country’s mean.) This is **not** the same question as Model 1 (**total** association mixing **between-** and **within-country** signal) or Model 1b (**within-year, cross-country** contrasts after year FE).

**Decomposition:** Each **`Gap_*`** is split into a **country-level** component (the group mean) and a **within-country deviation**; the regression relates the **deviation** to **`LE_gap`**. **`resid_*`** is **orthogonal to country** by construction; **country FE** remain in the **`LE_gap`** equation (mostly shifting **intercepts**; slopes on **`resid_*`** ≈ a model without FE on **X**, with posteriors **slightly stabilized**).

### Triangulation: three CausalPy specs

| Model | What differs | What the gap slopes emphasize |
|-------|----------------|--------------------------------|
| **1** | Baseline (no country-mean removal of gaps; no year FE) | **Total** association: **between-country**, **within-country**, and **time** mixed in global z-scoring |
| **1b** | **Year FE** | **Within-year**, **cross-country** variation (shared time trends removed) |
| **1c** | **Country-mean** gaps removed before z-scoring | **Within-country over time** (relative to each country’s long-run mean gap) |

Together: **Model 1** = broadest associational pattern; **1b** answers what happens when **time** is netted out; **1c** answers what happens when **persistent country** structure in gaps is netted out.

**Log (same run as Model 1):** **`notebooks/logs/causal_model_le_with_covid_2023.txt`** — **2026-04-10**, CausalPy **0.8.0**, **888** rows.

| Quantity | Model 1 | Model 1c |
|----------|---------|----------|
| In-sample R² (CausalPy / ArviZ) | **0.978550** | **0.978560** |

**Posterior means (94% HDIs in log); Δ = Model 1 − Model 1c:**

| Predictor | Model 1 mean | Model 1c (`*_resid`) mean | Δ |
|-----------|--------------|---------------------------|---|
| Gap_Alcohol | 0.11 | 0.032 | 0.08 |
| Gap_COVID | 0.11 | 0.11 | 0.00 |
| Gap_Cardiovascular | −0.15 | −0.066 | −0.08 |
| Gap_Childhood | 0.076 | 0.031 | 0.05 |
| Gap_ChronicRespiratory | 0.31 | 0.10 | 0.21 |
| Gap_Diabetes | −0.092 | −0.051 | −0.04 |
| Gap_DrugDisorder | 0.087 | 0.044 | 0.04 |
| Gap_Homicide | 0.43 | 0.17 | 0.26 |
| Gap_LiverDisease | 0.25 | 0.073 | 0.18 |
| Gap_Neoplasms | 0.26 | 0.049 | 0.21 |
| Gap_RoadTraffic | 0.44 | 0.24 | 0.20 |
| Gap_Suicide | 0.34 | 0.11 | 0.23 |
| Gap_UnintentionalInjury | 0.12 | 0.043 | 0.08 |

### What the joint pattern implies

**No sign changes**, **substantial shrinkage** for many causes, and **R² essentially unchanged** is a **strong diagnostic** combination:

- **Stable signs** → Model 1 is picking up **real** cross-cause structure, not arbitrary sign noise.
- **Shrinkage** → **Residualization is removing the between-country component of gaps cleanly**; a **large share** of the Model 1 association for several major causes reflects **persistent differences between countries** rather than **changes within countries over time**—stronger than “a country-level component.”
- **Unchanged R²** is **not trivial**: **`LE_gap`** is explained **as well** when predictors are **within-country deviations** (plus country FE) as when they are **global** z-scored gaps. So the fit **does not** depend on **between-country** contrast in **X** to achieve the same in-sample **R²**; **within-country** variation in gaps still carries **substantial** signal for **`LE_gap`**, which **supports** the credibility of the within-country interpretation.

### Key causes (posterior means)

**Homicide (0.43 → 0.17):** Model 1 mixes **“countries with higher homicide gaps tend to have higher LE gaps”** with **within-country** co-movement. After removing country-mean gaps, a **positive** association **remains** but **smaller**: **within-country** deviations still matter—**credible** and **interpretable**.

**Road traffic (triangulation with 1b):**

| Model | Road traffic (posterior mean) |
|-------|-------------------------------|
| Model 1 | **0.44** |
| Model 1b | **0.091** |
| Model 1c | **0.24** |

**Year FE (1b)** pull the coefficient **down** sharply (shared time trend in road safety); **country-mean removal (1c)** leaves a **middle** ground: **within-country** deviations in the road-traffic gap stay **meaningfully** associated with **`LE_gap`**. That **aligns** with the view that **shared time trends** in road safety reflect **real** (e.g. policy- and technology-driven) change **not** captured as pure confounding by year FE alone—and that **1c** is the spec that **preserves** a **within-country** road signal **without** the **over-correction** that **1b** can impose on this cause. (Still **associational**; not a causal identification proof.)

**Chronic respiratory, neoplasms, suicide (large shrinkage):** Posterior means move from **0.31 / 0.26 / 0.34** toward **0.10 / 0.049 / 0.11**—consistent with **smoking history, health systems, demographics**, and other **slow-moving, country-specific** factors **quantifying** how much of Model 1 was **between-country**.

**COVID (0.11 → 0.11):** **Unchanged** at the mean. COVID’s **variation** is **mostly temporal**, not a **long-run country characteristic** of the gap—so the Model 1 slope is **not** driven by **country means**; a useful **sanity check**.

**Cardiovascular and diabetes (still negative, smaller |β|):** The **“protective”** (negative) association is **partly** **country-level** structure **but not entirely**—consistent with a **competing-risks** / composition reading.

### Big picture

Model 1c shows that while **much** of the cross-cause pattern in Model 1 is driven by **persistent differences between countries**, a **substantial within-country** relationship **remains** for several **important** causes—notably **road traffic**, **homicide**, and **suicide**. That supports the **interpretation** that **changes in these causes within countries over time** are **meaningfully associated** with **`LE_gap`** in a **principled** decomposition, **after** removing long-run **country-level** structure in the gaps.

Comparing **`resid_*`** to **Bayesian `Gap_*`** posteriors below is **not** apples-to-apples (**different predictors**).

---

## Comparison to the Bayesian **LE** model (not HALE)

**Reference table:** **`notebooks/tables/beta_coefficients_le_ihme_nomid_nogrw_y2023_covid.html`** — IHME, no Mid predictors, **no year GRW** (`INCLUDE_YEAR_EFFECTS = False`), cutoff **2023**, COVID included. Posterior **means** below are from that export.

**Structural difference:** The Bayesian LE model uses **random intercepts** by country and **does not** include a **year random walk** in this reference run. **Model 1b** **does** include **year FE**. So **Model 1** was **closer in spirit** to “country heterogeneity + shared slopes, no explicit year term” than **1b** is. Comparing **1b** to Bayesian mixes **different time adjustment** choices.

### Model 1 vs Bayesian LE (posterior mean); Δ = CausalPy − Bayesian

| Predictor | Model 1 | Bayesian LE | Δ |
|-----------|---------|-------------|---|
| Gap_Alcohol | 0.11 | 0.13 | −0.02 |
| Gap_COVID | 0.11 | 0.113 | −0.003 |
| Gap_Cardiovascular | −0.15 | −0.185 | +0.035 |
| Gap_Childhood | 0.076 | 0.061 | +0.015 |
| Gap_ChronicRespiratory | 0.31 | 0.299 | +0.011 |
| Gap_Diabetes | −0.092 | −0.091 | −0.001 |
| Gap_DrugDisorder | 0.087 | 0.091 | −0.004 |
| Gap_Homicide | 0.43 | 0.421 | +0.009 |
| Gap_LiverDisease | 0.25 | 0.254 | −0.004 |
| Gap_Neoplasms | 0.26 | 0.32 | −0.06 |
| Gap_RoadTraffic | 0.44 | 0.432 | +0.008 |
| Gap_Suicide | 0.34 | 0.363 | −0.023 |
| Gap_UnintentionalInjury | 0.12 | 0.152 | −0.032 |

**What matched (Model 1):** **Same sign** at posterior **mean** for all **13** gaps vs Bayesian (two **negative**: cardiovascular, diabetes); **similar top-tier ranking** (road traffic, homicide, suicide, chronic respiratory, neoplasms). **HDI** caveats still apply (e.g. **childhood** in Bayesian table has **wide** intervals). **FE vs pooling:** agreement between **Model 1** and Bayesian **supports** that the **headline cross-cause pattern** is **not solely** an artifact of **partial pooling** in the hierarchical model.

### Model 1b vs Bayesian LE (posterior mean); Δ = CausalPy − Bayesian

| Predictor | Model 1b | Bayesian LE | Δ |
|-----------|----------|-------------|---|
| Gap_Alcohol | 0.12 | 0.13 | −0.01 |
| Gap_COVID | 0.12 | 0.113 | +0.007 |
| Gap_Cardiovascular | −0.024 | −0.185 | +0.161 |
| Gap_Childhood | −0.24 | 0.061 | −0.301 |
| Gap_ChronicRespiratory | 0.17 | 0.299 | −0.129 |
| Gap_Diabetes | −0.021 | −0.091 | +0.07 |
| Gap_DrugDisorder | 0.14 | 0.091 | +0.049 |
| Gap_Homicide | 0.43 | 0.421 | +0.009 |
| Gap_LiverDisease | 0.20 | 0.254 | −0.054 |
| Gap_Neoplasms | 0.29 | 0.32 | −0.03 |
| Gap_RoadTraffic | 0.091 | 0.432 | −0.341 |
| Gap_Suicide | 0.28 | 0.363 | −0.083 |
| Gap_UnintentionalInjury | 0.22 | 0.152 | +0.068 |

**Takeaway:** **1b** still **aligns** with Bayesian on **homicide** and **roughly** on alcohol / COVID / neoplasms, but **differs sharply** on **road traffic**, **childhood**, **chronic respiratory**, and **cardiovascular**—consistent with **year FE** absorbing **global** time trends that overlap those cause structures. For **Bayesian-aligned** robustness of **shared slopes** without a year term in CausalPy, **Model 1** is the cleaner **apples-to-apples** contrast; **1b** answers a **different** question.

---

## Main takeaway

- **Model 1** is a **useful robustness check** against the Bayesian LE model: **country FE** + **no year** term, **similar** standardized **mean** pattern and **signs** vs hierarchical **LE** (with HDI scrutiny where needed).  
- **Model 1c** is **arguably the most informative** of the three CausalPy specs: it **implements** the DAG **and** delivers a **clean** **between-country vs within-country** read on gaps. **Key result:** for several major causes, a **substantial fraction** of the Model 1 signal reflects **persistent between-country** differences **not** **within-country** dynamics; **yet** **within-country** associations **remain** for causes such as **road traffic**, **homicide**, and **suicide**. **COVID** unchanged at the mean **sanity-checks** that the Model 1 slope is **not** driven by **country means**. **Road traffic** triangulates **1 / 1b / 1c** in a way that **supports** treating **shared time** in road safety as **substantive** and **preserves** a **policy-relevant** **within-country** signal under **1c**—without claiming full causal identification.  
- **Model 1b** is the **two-way FE** analogue (**country + year**); it **changes** gap slopes **materially** and answers a **different** estimand than **1** or **1c**; **tension** between **1** and **1b** is **partly resolved** by **1c** (country structure vs time trends).  
- All three CausalPy specs remain **associational** models framed by **DAGs**, not **fully identified causal** analyses.  
- **Quantitative decomposition** and **model-based counterfactual calculations** (structural, model-implied sense) should still rely on **`bayesian_model.md`** for **partial pooling**, **full posteriors**, and existing workflows.

---

## Files

| Artifact | Path |
|----------|------|
| Notebook (source) | `notebooks/causal_model.md` |
| Log: Model 1 + 1c | `notebooks/logs/causal_model_le_with_covid_2023.txt` |
| Log: Model 1b | `notebooks/logs/causal_model_le_1b_with_covid_2023.txt` |
| DAG: Model 1 | `notebooks/figs/dag_model1_minimal.png` |
| DAG: Model 1c | `notebooks/figs/dag_model1c_country_causes_gaps.png` |
| DAG: Model 1b | `notebooks/figs/dag_model1b_minimal.png` |
| Forest: Model 1 | `notebooks/figs/causalpy_le_linear_forest_model1_gap_betas.png` |
| Forest: Model 1c | `notebooks/figs/causalpy_le_linear_forest_model1c_resid_gap_betas.png` |
| Forest: Model 1b | `notebooks/figs/causalpy_le_linear_forest_model1b_gap_betas.png` |
| Bayesian LE β (reference) | `notebooks/tables/beta_coefficients_le_ihme_nomid_nogrw_y2023_covid.html` |
