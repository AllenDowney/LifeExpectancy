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

# Bayesian LE / HALE Model: Figures for Blog

This notebook loads saved LE and HALE model traces and produces bar-chart figures in the same style as [`jb/blog2_model.md`](../jb/blog2_model.md) (coefficients and importance). LE outputs keep legacy names (`blog2_*_le.png`). HALE outputs use neutral names without a post number: `coefficients_hale.png`, `importance_hale.png`.

## Setup

```python
%load_ext autoreload
%autoreload 2
```

```python
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

import arviz as az

from utils import configure_plot_style, code_to_who_country, add_title, add_subtext, add_logo
from fig_utils import plot_coefficients_bar, plot_fitted_vs_actual_timeseries, add_direct_line_labels
from counterfactual_utils import compute_residuals_panel, plot_residuals_by_country

configure_plot_style()
```

## Load Model Results

```python
# Paths to saved model outputs (from bayesian_model.ipynb)
nc_dir = Path('nc')
interim_dir = Path('interim')
figs_dir = Path('figs')

# Model suffix for 2023 IHME model with COVID
MODEL_SUFFIX = '_ihme_nomid_nogrw_y2023_covid'

trace_file = nc_dir / f'trace_le{MODEL_SUFFIX}.nc'
meta_file = interim_dir / f'metadata_le{MODEL_SUFFIX}.json'

trace = az.from_netcdf(trace_file)
with open(meta_file) as f:
    metadata = json.load(f)

predictors = metadata['predictors']
print(f"Loaded trace: {trace_file.name}")
print(f"Predictors: {len(predictors)}")
```

## Coefficient Bar Chart

Horizontal bar chart showing posterior mean and 94% credible interval for each predictor coefficient. Sorted by coefficient magnitude (absolute value) so the strongest effects appear at the top. AIBM style: title, subtitle, subtext, logo.

```python
beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
fig, ax = plot_coefficients_bar(
    beta_samples,
    predictors,
    title='Predictor Coefficients: Life Expectancy Gender Gap',
    subtitle='OECD countries, 2000–2023',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.',
    logo=True
)
plt.savefig(figs_dir / 'blog2_coefficients_le.png', dpi=150, bbox_inches='tight')
plt.show()
```

## Importance Bar Chart

Importance = |coefficient| × SD of predictor (on original scale). Accounts for both effect size and how much the predictor varies across countries and years. Sorted by importance (highest first).

```python
# X_std from metadata: standard deviation of each predictor on original scale
x_std = np.array(metadata['X_std'])

fig, ax = plot_coefficients_bar(
    beta_samples,
    predictors,
    metric='importance',
    x_std=x_std,
    title='Predictor Importance: Life Expectancy Gender Gap',
    subtitle='OECD countries, 2000–2023.',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.',
    logo=True
)
plt.savefig(figs_dir / 'blog2_importance_le.png', dpi=150, bbox_inches='tight')
plt.show()
```

## HALE: coefficient and importance bar charts

Same plotting utilities as LE, using `trace_hale{MODEL_SUFFIX}.nc` and `metadata_hale{MODEL_SUFFIX}.json`.

```python
trace_hale_file = nc_dir / f'trace_hale{MODEL_SUFFIX}.nc'
meta_hale_file = interim_dir / f'metadata_hale{MODEL_SUFFIX}.json'

trace_hale = az.from_netcdf(trace_hale_file)
with open(meta_hale_file) as f:
    metadata_hale = json.load(f)

predictors_hale = metadata_hale['predictors']
beta_samples_hale = trace_hale.posterior['beta'].values.reshape(-1, len(predictors_hale))
print(f"Loaded HALE trace: {trace_hale_file.name}, {len(predictors_hale)} predictors")
```

```python
fig, ax = plot_coefficients_bar(
    beta_samples_hale,
    predictors_hale,
    title='Predictor Coefficients: HALE Gender Gap',
    subtitle='OECD countries, 2000–2023',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
plt.savefig(figs_dir / 'coefficients_hale.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
x_std_hale = np.array(metadata_hale['X_std'])

fig, ax = plot_coefficients_bar(
    beta_samples_hale,
    predictors_hale,
    metric='importance',
    x_std=x_std_hale,
    title='Predictor Importance: HALE Gender Gap',
    subtitle='OECD countries, 2000–2023.',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
plt.savefig(figs_dir / 'importance_hale.png', dpi=150, bbox_inches='tight')
plt.show()
```

## Residual Time Series: Selected countries

Fitted vs actual LE gap over time for selected countries on the same axes. Actual: line only, country signature color. Predicted: markers with 94% HDI error bars, gray. Direct labels on the right (no legend). AIBM style. Matches time_series_figs layout: figsize (8, 4), same xlim, no left spine, same label offset.

```python
# Load panel data (required for fitted vs actual plot)
panel_file = interim_dir / f'panel_le{MODEL_SUFFIX}.h5'
panel_df = pd.read_hdf(panel_file, key='panel_data')

country_to_idx = {c: i for i, c in enumerate(metadata['countries'])}

min_year = int(panel_df['Year'].min())
max_year = int(panel_df['Year'].max())

fig, ax = plt.subplots(figsize=(8, 4))
label_data = []
for country in ['ISL', 'USA', 'LTU', 'FRA']:
    info = plot_fitted_vs_actual_timeseries(
        ax, country, trace, metadata, panel_df, country_to_idx,
        target_col='LE_gap', target_name='Life Expectancy gap',
        add_predicted_to_legend=False
    )
    label_data.append(info)
add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year)
ax.spines['left'].set_visible(False)
year_range = max_year - min_year
tick_step = 1 if year_range <= 5 else 5
ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
ax.set_xlabel('Year')
ax.set_ylabel('Life Expectancy gap (years)')
add_title('Predicted vs Actual LE Gap', 'Selected countries, predicted markers show 94% confidence interval', pad=25, x=0, y=1.04)
add_subtext('Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.', x=0, y=-0.18, align_to_axes=True)
if os.path.isfile('logo-hq-small.png'):
    add_logo(filename='logo-hq-small.png', location=(0.99, -0.21), align_to_axes=True)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(figs_dir / 'blog2_residuals_timeseries_le.png', dpi=150, bbox_inches='tight')
plt.show()
```

## Residuals by Country

Horizontal boxplot of residuals by country, sorted by IQR (smallest = best fit at top). AIBM style.

```python
residuals_df = compute_residuals_panel(trace, metadata, panel_df, target_col='LE_gap')

fig, ax = plot_residuals_by_country(
    residuals_df,
    target_name='Life Expectancy gap',
    country_labels=code_to_who_country,
    output_filename=None,
    title='Model residuals by country',
    subtitle='Sorted by IQR (best fit at top)',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.',
    logo=True
)
plt.savefig(figs_dir / 'blog2_residuals_by_country_le.png', dpi=150, bbox_inches='tight')
plt.show()
```

## HALE: residual time series and by country

Same diagnostics as for LE (`blog2_residuals_*_le.png`), using `trace_hale`, `metadata_hale`, and `panel_hale{MODEL_SUFFIX}.h5`. Outputs: `residuals_timeseries_hale.png`, `residuals_by_country_hale.png`.

```python
panel_hale_file = interim_dir / f'panel_hale{MODEL_SUFFIX}.h5'
panel_df_hale = pd.read_hdf(panel_hale_file, key='panel_data')
country_to_idx_hale = {c: i for i, c in enumerate(metadata_hale['countries'])}

min_year_h = int(panel_df_hale['Year'].min())
max_year_h = int(panel_df_hale['Year'].max())

fig, ax = plt.subplots(figsize=(8, 4))
label_data_hale = []
for country in ['ISL', 'USA', 'LTU', 'FRA']:
    info = plot_fitted_vs_actual_timeseries(
        ax, country, trace_hale, metadata_hale, panel_df_hale, country_to_idx_hale,
        target_col='HALE_gap', target_name='HALE gap',
        add_predicted_to_legend=False
    )
    label_data_hale.append(info)
add_direct_line_labels(ax, label_data_hale, x_min=min_year_h, x_max=max_year_h)
ax.spines['left'].set_visible(False)
year_range_h = max_year_h - min_year_h
tick_step_h = 1 if year_range_h <= 5 else 5
ax.set_xticks(np.arange(min_year_h, max_year_h + 1, tick_step_h))
ax.set_xlabel('Year')
ax.set_ylabel('HALE gap (years)')
add_title(
    'Predicted vs Actual HALE Gap',
    'Selected countries; predicted markers show 94% credible interval',
    pad=25, x=0, y=1.04
)
add_subtext(
    'Source: Bayesian hierarchical panel model. IHME cause-specific mortality and HALE.',
    x=0, y=-0.18, align_to_axes=True
)
if os.path.isfile('logo-hq-small.png'):
    add_logo(filename='logo-hq-small.png', location=(0.99, -0.21), align_to_axes=True)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(figs_dir / 'residuals_timeseries_hale.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
residuals_df_hale = compute_residuals_panel(
    trace_hale, metadata_hale, panel_df_hale, target_col='HALE_gap'
)

fig, ax = plot_residuals_by_country(
    residuals_df_hale,
    target_name='HALE gap',
    country_labels=code_to_who_country,
    output_filename=None,
    title='Model residuals by country (HALE)',
    subtitle='Sorted by IQR (best fit at top)',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality and HALE.',
    logo=True
)
plt.savefig(figs_dir / 'residuals_by_country_hale.png', dpi=150, bbox_inches='tight')
plt.show()
```
