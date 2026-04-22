---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.20.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# CausalPy: Model 1 + Model 1c (residualized gaps, LE gap)

**Model 1:** **`Gap_*` + country FE → `LE_gap`** — globally standardized raw gaps, no year term. Signal mixes **between-country** and **within-country** variation (and time).

**Model 1b** (not run here): **year FE** → estimand closer to **within-year, cross-country** contrasts; see `logs/causal_model_le_1b_*.txt`.

**Model 1c (residualization):** For each cause, subtract that country’s **long-run average** gap: **`Gap_*_resid = Gap_* − E[Gap_* | country]`** over **all years** in the panel (group-mean removal; equivalent to residuals from each gap regressed on country dummies). **Z-score** those residuals, then **`LE_gap ~ resid_* + country FE`** (Option A).

**Estimand (1c):** Model 1c estimates how **deviations from each country’s long-run average gap** (that cause, over all years) are associated with **`LE_gap`**, with the same **country FE** on **`LE_gap`** as Model 1. Equivalently: *If a country-year’s gap is higher than that country’s usual level for that cause, is **`LE_gap`** higher?* Not the same as Model 1 (**total** association) or Model 1b (**within-year**, cross-country).

**Decomposition (explicit):** Model 1c **splits** each **`Gap_*`** into a **country-level** component (the group mean) and a **within-country deviation** (the residual). It then estimates the **association between the deviation component** and **`LE_gap`** (alongside the same **country FE** on **`LE_gap`** as Model 1). The DAG matches the code: **country** → **gaps** and **LE_gap**; residualization operationalizes removing the **country-mean** part of gaps before entering the LE regression.

| Model | Role | In this notebook |
|-------|------|------------------|
| **1** | Standardized raw gaps + country FE | **Draw DAG + fit** |
| **1b** | + year FE | *Not run; see `logs/causal_model_le_1b_*.txt`* |
| **1c** | Residualized gaps + country FE | **DAG + fit** |
| **2 / 3** | Expanded / competing risks | *Planned* |

Panel: **`interim/panel_le.h5`**. Exclusions: **`Gap_MaternalDisorders`**, **`Gap_ConflictTerrorism`**.

**Triangulation (three specs):**

| Model | Contrast | What gap slopes emphasize |
|-------|----------|---------------------------|
| **1** | None (baseline) | **Total** association: between-country, within-country, and time (mixed) |
| **1b** | + year FE | **Within-year**, cross-country (not run here; see logs) |
| **1c** | Country-mean gaps removed | **Within-country over time** vs each country’s long-run mean gap |

**What to look for:** **Large** **`resid_*`** after Model 1 was large → **within-country** signal survives. **Shrinkage** → **a large share** of Model 1 reflected **persistent between-country** differences, not **within-country** change. **No sign flip** + **similar R²** → **diagnostic** of a **clean** decomposition. Pair with **1 vs 1b** (e.g. road traffic: **1b** can **over-correct** time; **1c** is a **middle** ground).

**Run headlessly:**

```
cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && \
  jupytext --to ipynb causal_model.md --output causal_model.ipynb && \
  papermill causal_model.ipynb causal_model_executed.ipynb
```

Outputs: `figs/dag_model1_minimal.png`, `figs/dag_model1c_country_causes_gaps.png`, `figs/causalpy_le_linear_forest_model1_gap_betas.png`, `figs/causalpy_le_linear_forest_model1c_resid_gap_betas.png`, `logs/causal_model_le_<covid>_<year>.txt`.

```python
%load_ext autoreload
%autoreload 2
```

```python
import contextlib
import io
import pathlib

import arviz as az
import causalpy as cp
import graphviz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from causalpy.pymc_models import LinearRegression

from utils import configure_plot_style, gap_predictor_columns, log_and_print, set_log_file

configure_plot_style()
```

## Configuration (align with `bayesian_model.md`)

```python
INCLUDE_COVID_DATA = True
CUTOFF_YEAR = 2023 if INCLUDE_COVID_DATA else 2019
COUNTRIES_TO_EXCLUDE = ["TUR"]

_GAP_EXCLUDE_LE_MODEL1 = frozenset({"Gap_MaternalDisorders", "Gap_ConflictTerrorism"})
```

## Setup logging

```python
import os

os.makedirs("logs", exist_ok=True)
covid_suffix = "with_covid" if INCLUDE_COVID_DATA else "pre_covid"
log_path = f"logs/causal_model_le_{covid_suffix}_{CUTOFF_YEAR}.txt"

log_file = open(log_path, "w")
set_log_file(log_file)

log_and_print(f"Logging to: {log_path}")
log_and_print("=" * 80)
log_and_print("CAUSALPY — MODEL 1 + MODEL 1C (RESIDUALIZED GAPS)")
log_and_print("=" * 80)
log_and_print(f"Timestamp: {pd.Timestamp.now()}")
log_and_print(f"CausalPy {cp.__version__}")
log_and_print(f"Include COVID Data: {INCLUDE_COVID_DATA}")
log_and_print(f"Analysis period: 2000–{CUTOFF_YEAR}")
log_and_print(f"Countries excluded: {COUNTRIES_TO_EXCLUDE}")
log_and_print("=" * 80)
```

## Load panel

```python
panel_le = pd.read_hdf("interim/panel_le.h5", key="panel")

if COUNTRIES_TO_EXCLUDE:
    panel_le = panel_le[~panel_le["country"].isin(COUNTRIES_TO_EXCLUDE)].copy()

panel_le = panel_le[
    (panel_le["Year"] >= 2000) & (panel_le["Year"] <= CUTOFF_YEAR)
].copy()
panel_le = panel_le.dropna(subset=["LE_gap"]).copy()
panel_le = panel_le.sort_values(["country", "Year"]).reset_index(drop=True)

_all_gap = gap_predictor_columns(panel_le)
predictor_cols = [c for c in _all_gap if c not in _GAP_EXCLUDE_LE_MODEL1]
log_and_print(f"Excluded Gap_* predictors: {sorted(_GAP_EXCLUDE_LE_MODEL1)}")
log_and_print(
    f"Gap_* predictors in model ({len(predictor_cols)}): {predictor_cols}"
)

panel_model = panel_le.dropna(subset=predictor_cols).copy()
log_and_print(f"Rows after complete cases: {len(panel_model)}")
```

```python
log_and_print("\n" + "=" * 80)
log_and_print("PANEL DATA LOADED (LE)")
log_and_print("=" * 80)
log_and_print(
    f"LE: {panel_le.shape[0]} rows, {panel_le['country'].nunique()} countries"
)
log_and_print(
    f"  Years: {panel_le['Year'].min():.0f}–{panel_le['Year'].max():.0f}"
)
log_and_print(f"Complete-case rows for model: {len(panel_model)}")
log_and_print("=" * 80)
```

## Model 1 — Design matrix (standardized gaps + country FE)

```python
# Model 1: intercept + globally standardized Gap_* + country FE (no year)
n = len(panel_model)
X_gap = panel_model[predictor_cols].to_numpy(dtype=float)
x_mean = X_gap.mean(axis=0)
x_std = np.where(X_gap.std(axis=0, ddof=0) == 0, 1.0, X_gap.std(axis=0, ddof=0))
X_z = (X_gap - x_mean) / x_std

country_dums = pd.get_dummies(panel_model["country"], prefix="c", drop_first=True)

const = np.ones((n, 1))
X_mat = np.hstack([const, X_z, country_dums.to_numpy()])

coeff_names_m1 = ["const"] + predictor_cols + list(country_dums.columns)

y_raw = panel_model["LE_gap"].to_numpy(dtype=float)
y_mean = float(y_raw.mean())
y_centered = y_raw - y_mean

n_obs = n
obs_ind = np.arange(n_obs, dtype=int)

X = xr.DataArray(
    X_mat,
    dims=["obs_ind", "coeffs"],
    coords={"obs_ind": obs_ind, "coeffs": coeff_names_m1},
)
y = xr.DataArray(
    y_centered[:, None],
    dims=["obs_ind", "treated_units"],
    coords={"obs_ind": obs_ind, "treated_units": ["LE_gap"]},
)
coords_m1 = {
    "coeffs": coeff_names_m1,
    "obs_ind": obs_ind,
    "treated_units": ["LE_gap"],
}
```

```python
log_and_print("\n" + "=" * 80)
log_and_print("DESIGN MATRIX (MODEL 1 — GLOBAL Z ON RAW GAPS)")
log_and_print("=" * 80)
log_and_print(f"n_obs: {n_obs}")
log_and_print(f"n_coefficients: {len(coeff_names_m1)}")
log_and_print(
    f"  const + Gap_* ({len(predictor_cols)}) + country FE ({country_dums.shape[1]})"
)
log_and_print(f"LE_gap centered (mean subtracted): {y_mean:.6f}")
log_and_print("=" * 80)
```

## Model 1 — Minimal DAG (draw)

**Structure:** **`Gap_*` → `LE_gap`**, **`country` → `LE_gap`**.

```python
def model1_dot_string(predictor_cols):
    lines = [
        "digraph {",
        "    # Outcome",
        "    LE_gap;",
        "    # Controls",
        "    country;",
        "    # Predictors",
    ]
    for c in predictor_cols:
        lines.append(f'    "{c}";')
    lines.append("")
    for c in predictor_cols:
        lines.append(f'    "{c}" -> LE_gap;')
    lines.append("    country -> LE_gap;")
    lines.append("}")
    return "\n".join(lines)


out_dir = pathlib.Path("figs")
out_dir.mkdir(parents=True, exist_ok=True)

dag_m1 = model1_dot_string(predictor_cols)
log_and_print("\nDOT (Model 1 minimal):\n" + dag_m1)

g1 = graphviz.Source(dag_m1)
p1 = g1.render(
    filename="dag_model1_minimal",
    directory=str(out_dir),
    format="png",
    cleanup=True,
)
log_and_print(f"Saved: {p1}")
g1
```

## Model 1 — CausalPy `LinearRegression` (run)

```python
lr = LinearRegression(
    sample_kwargs={
        "chains": 2,
        "draws": 1000,
        "tune": 1000,
        "random_seed": 42,
        "nuts_sampler": "nutpie",
    }
)
lr.fit(X, y, coords=coords_m1)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    lr.print_coefficients(coeff_names_m1)
log_and_print("\n" + "=" * 80)
log_and_print("CAUSALPY — MODEL 1 (GLOBAL Z, COUNTRY FE)")
log_and_print("=" * 80)
log_and_print(buf.getvalue())

score_m1 = lr.score(X, y)
log_and_print("Bayesian R^2 (per CausalPy / ArviZ):")
log_and_print(score_m1.to_string())
log_and_print("=" * 80)
```

## Plot posterior — Model 1, `Gap_*` only

```python
_h = max(4.0, 0.35 * len(predictor_cols))
fig, ax = plt.subplots(figsize=(8, _h))
az.plot_forest(
    lr.idata,
    var_names=["beta"],
    combined=True,
    coords={"coeffs": predictor_cols},
    ax=ax,
)
ax.set_title(
    "Model 1: β for globally standardized Gap_* (country FE; no year FE)"
)
plt.tight_layout()

forest_m1 = out_dir / "causalpy_le_linear_forest_model1_gap_betas.png"
fig.savefig(forest_m1, dpi=150, bbox_inches="tight")
log_and_print(f"Saved forest plot: {forest_m1.resolve()}")
plt.show()
```

## Model 1c — Residualize gaps by country, then regress (conceptual + fit)

**Step 1:** For each raw **`Gap_*`**, **`resid = Gap_* − mean(Gap_* | country)`** where the mean is over **all country-years** for that country (long-run average for that cause).

**Step 2:** **Z-score** residuals across all rows (comparable scales).

**Step 3:** **`LE_gap ~ const + resid_* + country FE`** — same centered **`LE_gap`**, same **country dummies**, same **CausalPy** engine as Model 1.

**Technical note:** **`resid_*`** is **orthogonal to country** by construction, but the design still includes **`country_dums`**. That is intentional: the FE mostly identify the **LE intercept** level by country; the **`resid_*`** slopes are **approximately** what you would get **without** country FE on the residualized predictors, while **posteriors** (or sampling variability) on those slopes are **slightly stabilized** by retaining the same **country FE** on **`LE_gap`**. Not a bug—expected when **partialling** country out of **X** but retaining country in **Y**’s adjustment.

**Why this level of complexity:** Same outcome, centering, FE layout, and sampler as Model 1 → **comparisons are meaningful**. No year FE (avoids over-controlling trends the way 1b did). **DAG → code:** this is the first spec where the **graph changes the regression** (not only the picture).

```python
df = panel_model.copy()
for col in predictor_cols:
    df[f"{col}_resid"] = df[col] - df.groupby("country")[col].transform("mean")

resid_cols = [f"{c}_resid" for c in predictor_cols]
X_resid = df[resid_cols].to_numpy(dtype=float)
rm = X_resid.mean(axis=0)
rs = np.where(X_resid.std(axis=0, ddof=0) == 0, 1.0, X_resid.std(axis=0, ddof=0))
X_resid_z = (X_resid - rm) / rs

X_mat_1c = np.hstack([const, X_resid_z, country_dums.to_numpy()])
coeff_names_1c = ["const"] + resid_cols + list(country_dums.columns)

X_1c = xr.DataArray(
    X_mat_1c,
    dims=["obs_ind", "coeffs"],
    coords={"obs_ind": obs_ind, "coeffs": coeff_names_1c},
)
coords_1c = {
    "coeffs": coeff_names_1c,
    "obs_ind": obs_ind,
    "treated_units": ["LE_gap"],
}
```

```python
log_and_print("\n" + "=" * 80)
log_and_print("DESIGN MATRIX (MODEL 1C — COUNTRY-RESIDUALIZED GAPS, Z-SCORED)")
log_and_print("=" * 80)
log_and_print(f"n_obs: {n_obs}")
log_and_print(f"n_coefficients: {len(coeff_names_1c)}")
log_and_print(
    f"  const + Gap_*_resid z ({len(predictor_cols)}) + country FE ({country_dums.shape[1]})"
)
log_and_print("=" * 80)
```

## Model 1c — DAG (country → gaps and LE)

```python
def model1c_dot_string(predictor_cols):
    lines = [
        "digraph {",
        "    LE_gap;",
        "    country;",
    ]
    for c in predictor_cols:
        lines.append(f'    "{c}";')
    lines.append("")
    for c in predictor_cols:
        lines.append(f'    country -> "{c}";')
    lines.append("")
    for c in predictor_cols:
        lines.append(f'    "{c}" -> LE_gap;')
    lines.append("    country -> LE_gap;")
    lines.append("}")
    return "\n".join(lines)


dag_m1c = model1c_dot_string(predictor_cols)
log_and_print("\nDOT (Model 1c):\n" + dag_m1c)

g1c = graphviz.Source(dag_m1c)
p1c = g1c.render(
    filename="dag_model1c_country_causes_gaps",
    directory=str(out_dir),
    format="png",
    cleanup=True,
)
log_and_print(f"Saved: {p1c}")
g1c
```

## Model 1c — CausalPy `LinearRegression` (run)

```python
lr_1c = LinearRegression(
    sample_kwargs={
        "chains": 2,
        "draws": 1000,
        "tune": 1000,
        "random_seed": 42,
        "nuts_sampler": "nutpie",
    }
)
lr_1c.fit(X_1c, y, coords=coords_1c)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    lr_1c.print_coefficients(coeff_names_1c)
log_and_print("\n" + "=" * 80)
log_and_print("CAUSALPY — MODEL 1C (RESID GAPS + COUNTRY FE)")
log_and_print("=" * 80)
log_and_print(buf.getvalue())

score_1c = lr_1c.score(X_1c, y)
log_and_print("Bayesian R^2 (per CausalPy / ArviZ):")
log_and_print(score_1c.to_string())
log_and_print("=" * 80)
```

## Plot posterior — Model 1c, residualized gap slopes only

```python
_h = max(4.0, 0.35 * len(predictor_cols))
fig, ax = plt.subplots(figsize=(8, _h))
az.plot_forest(
    lr_1c.idata,
    var_names=["beta"],
    combined=True,
    coords={"coeffs": resid_cols},
    ax=ax,
)
ax.set_title(
    "Model 1c: β for z-scored country-residualized gaps (LE_gap centered; country FE)"
)
plt.tight_layout()

forest_1c = out_dir / "causalpy_le_linear_forest_model1c_resid_gap_betas.png"
fig.savefig(forest_1c, dpi=150, bbox_inches="tight")
log_and_print(f"Saved forest plot: {forest_1c.resolve()}")
plt.show()
```

```python
log_and_print("\n" + "=" * 80)
log_and_print("CAUSAL_MODEL NOTEBOOK FINISHED")
log_and_print("=" * 80)
log_file.close()
set_log_file(None)
print(f"Log file closed: {log_path}")
```
