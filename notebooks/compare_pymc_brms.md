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

# Compare PyMC vs brms Model Results

This notebook compares the Bayesian hierarchical panel model results from:
- **PyMC** (`bayesian_model_py.md`) - Python implementation
- **brms** (`bayesian_model_r.Rmd`) - R implementation

Both models use the same:
- Data preprocessing (standardized predictors, centered target)
- Priors (Normal(0,1) for beta, Normal(0,5) for intercept, HalfNormal(1) for SDs)
- Model structure (random intercepts by country, shared slopes)

```python
%load_ext autoreload
%autoreload 2
```

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import scipy.stats as stats
from scipy.stats import pearsonr

from utils import (
    decorate, underride, configure_plot_style,
    log_and_print, set_log_file
)

configure_plot_style()
```

```python
from utils import setup_beep_on_error
setup_beep_on_error()
```

## Setup Logging

```python
# Setup logging and output directories
import os
os.makedirs('logs', exist_ok=True)
os.makedirs('tables', exist_ok=True)
os.makedirs('figs', exist_ok=True)

log_path = 'logs/compare_pymc_brms.txt'
log_file = open(log_path, 'w')
set_log_file(log_file)

log_and_print("="*80)
log_and_print("COMPARING PyMC vs brms MODEL RESULTS")
log_and_print("="*80)
log_and_print(f"Timestamp: {pd.Timestamp.now()}")
log_and_print("="*80)
```

## Load Results

### Load PyMC Results

```python
# Load PyMC posterior samples
beta_pymc = pd.read_csv('../data/beta_samples_pymc.csv')
alpha_pymc = pd.read_csv('../data/alpha_samples_pymc.csv')
hyperparams_pymc = pd.read_csv('../data/hyperparams_pymc.csv')

# Load PyMC preprocessing parameters
with open('../data/preprocessing_params_pymc.json', 'r') as f:
    preprocessing_pymc = json.load(f)

log_and_print("\n" + "="*80)
log_and_print("PyMC RESULTS LOADED")
log_and_print("="*80)
log_and_print(f"Beta samples: {beta_pymc.shape[0]} draws × {beta_pymc.shape[1]} predictors")
log_and_print(f"Alpha samples: {alpha_pymc.shape[0]} draws × {alpha_pymc.shape[1]} countries")
log_and_print(f"Hyperparameters: {hyperparams_pymc.shape[0]} draws")
log_and_print(f"Predictors: {', '.join(beta_pymc.columns[:5])}... ({len(beta_pymc.columns)} total)")
log_and_print("="*80)
```

### Load brms Results

```python
# Load brms posterior samples
beta_brms = pd.read_csv('../data/beta_samples_brms.csv')
alpha_brms = pd.read_csv('../data/alpha_samples_brms.csv')
hyperparams_brms = pd.read_csv('../data/hyperparams_brms.csv')

# Load brms preprocessing parameters
with open('../data/preprocessing_params_brms.json', 'r') as f:
    preprocessing_brms = json.load(f)

log_and_print("\n" + "="*80)
log_and_print("brms RESULTS LOADED")
log_and_print("="*80)
log_and_print(f"Beta samples: {beta_brms.shape[0]} draws × {beta_brms.shape[1]} predictors")
log_and_print(f"Alpha samples: {alpha_brms.shape[0]} draws × {alpha_brms.shape[1]} countries")
log_and_print(f"Hyperparameters: {hyperparams_brms.shape[0]} draws")
log_and_print(f"Predictors: {', '.join(beta_brms.columns[:5])}... ({len(beta_brms.columns)} total)")
log_and_print("="*80)
```

### Verify Data Compatibility

```python
# Check that predictors match
pymc_predictors = set(beta_pymc.columns)
brms_predictors = set(beta_brms.columns)

if pymc_predictors == brms_predictors:
    log_and_print("\n✓ Predictors match between PyMC and brms")
    predictors = sorted(list(pymc_predictors))
else:
    log_and_print("\n⚠ Predictor mismatch!")
    log_and_print(f"  PyMC only: {pymc_predictors - brms_predictors}")
    log_and_print(f"  brms only: {brms_predictors - pymc_predictors}")
    predictors = sorted(list(pymc_predictors & brms_predictors))
    log_and_print(f"  Common predictors: {len(predictors)}")

# Check country matching
pymc_countries = set(alpha_pymc.columns)
brms_countries = set(alpha_brms.columns)

if pymc_countries == brms_countries:
    log_and_print("✓ Countries match between PyMC and brms")
    countries = sorted(list(pymc_countries))
else:
    log_and_print("⚠ Country mismatch!")
    log_and_print(f"  PyMC only: {pymc_countries - brms_countries}")
    log_and_print(f"  brms only: {brms_countries - pymc_countries}")
    countries = sorted(list(pymc_countries & brms_countries))
    log_and_print(f"  Common countries: {len(countries)}")

# Align columns to match
beta_pymc_aligned = beta_pymc[predictors]
beta_brms_aligned = beta_brms[predictors]
alpha_pymc_aligned = alpha_pymc[countries]
alpha_brms_aligned = alpha_brms[countries]
```

## Compare Preprocessing Parameters

```python
log_and_print("\n" + "="*80)
log_and_print("PREPROCESSING PARAMETERS COMPARISON")
log_and_print("="*80)

# Helper function to extract float value (handles both float and list)
def get_float_value(value):
    """Extract float from value, handling both float and list types."""
    if isinstance(value, list):
        return float(value[0])
    return float(value)

# Compare standardization parameters
log_and_print("\nPredictor Standardization (X_mean):")
for pred in predictors[:5]:  # Show first 5
    pymc_mean = get_float_value(preprocessing_pymc['X_mean'][pred])
    brms_mean = get_float_value(preprocessing_brms['X_mean'][pred])
    diff = abs(pymc_mean - brms_mean)
    log_and_print(f"  {pred}: PyMC={pymc_mean:.6f}, brms={brms_mean:.6f}, diff={diff:.6f}")
    if diff > 1e-6:
        log_and_print(f"    ⚠ Warning: Difference > 1e-6")

log_and_print("\nPredictor Standardization (X_std):")
for pred in predictors[:5]:  # Show first 5
    pymc_std = get_float_value(preprocessing_pymc['X_std'][pred])
    brms_std = get_float_value(preprocessing_brms['X_std'][pred])
    diff = abs(pymc_std - brms_std)
    log_and_print(f"  {pred}: PyMC={pymc_std:.6f}, brms={brms_std:.6f}, diff={diff:.6f}")
    if diff > 1e-6:
        log_and_print(f"    ⚠ Warning: Difference > 1e-6")

# Compare target centering
pymc_y_mean = get_float_value(preprocessing_pymc['y_mean'])
brms_y_mean = get_float_value(preprocessing_brms['y_mean'])
y_mean_diff = abs(pymc_y_mean - brms_y_mean)
log_and_print(f"\nTarget Centering (y_mean):")
log_and_print(f"  PyMC: {pymc_y_mean:.6f}")
log_and_print(f"  brms: {brms_y_mean:.6f}")
log_and_print(f"  Difference: {y_mean_diff:.6f}")
if y_mean_diff > 1e-6:
    log_and_print(f"  ⚠ Warning: Difference > 1e-6")

# Compare sampling parameters
log_and_print(f"\nSampling Parameters:")
log_and_print(f"  PyMC: {preprocessing_pymc['sampling_params']}")
log_and_print(f"  brms: {preprocessing_brms['sampling_params']}")
log_and_print("="*80)
```

## Compare Beta Coefficients (Predictor Effects)

```python
log_and_print("\n" + "="*80)
log_and_print("BETA COEFFICIENTS COMPARISON")
log_and_print("="*80)

# Compute posterior means and credible intervals
beta_comparison = pd.DataFrame({
    'predictor': predictors,
    'pymc_mean': beta_pymc_aligned.mean().values,
    'brms_mean': beta_brms_aligned.mean().values,
    'pymc_q2.5': beta_pymc_aligned.quantile(0.025).values,
    'pymc_q97.5': beta_pymc_aligned.quantile(0.975).values,
    'brms_q2.5': beta_brms_aligned.quantile(0.025).values,
    'brms_q97.5': beta_brms_aligned.quantile(0.975).values,
})

# Compute differences
beta_comparison['mean_diff'] = beta_comparison['pymc_mean'] - beta_comparison['brms_mean']
beta_comparison['mean_diff_pct'] = 100 * beta_comparison['mean_diff'] / beta_comparison['pymc_mean'].abs()
beta_comparison['mean_diff_pct'] = beta_comparison['mean_diff_pct'].replace([np.inf, -np.inf], np.nan)

# Sort by absolute mean difference (create abs column for sorting)
beta_comparison['abs_mean_diff'] = beta_comparison['mean_diff'].abs()
beta_comparison = beta_comparison.sort_values('abs_mean_diff', ascending=False)

log_and_print("\nPosterior Mean Comparison (sorted by absolute difference):")
log_and_print(beta_comparison[['predictor', 'pymc_mean', 'brms_mean', 'mean_diff']].to_string(index=False))

# Overall correlation
corr_mean, pval_mean = pearsonr(beta_comparison['pymc_mean'], beta_comparison['brms_mean'])
log_and_print(f"\nCorrelation of posterior means: r = {corr_mean:.6f} (p = {pval_mean:.2e})")

# Maximum difference
max_diff_idx = beta_comparison['mean_diff'].abs().idxmax()
max_diff = beta_comparison.loc[max_diff_idx]
log_and_print(f"\nLargest difference:")
log_and_print(f"  Predictor: {max_diff['predictor']}")
log_and_print(f"  PyMC mean: {max_diff['pymc_mean']:.6f}")
log_and_print(f"  brms mean: {max_diff['brms_mean']:.6f}")
log_and_print(f"  Difference: {max_diff['mean_diff']:.6f} ({max_diff['mean_diff_pct']:.2f}%)")

log_and_print("="*80)
```

### Visualize Beta Comparison

```python
# Plot: Posterior means comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot: PyMC vs brms means
ax = axes[0]
ax.scatter(beta_comparison['pymc_mean'], beta_comparison['brms_mean'], alpha=0.7, s=100)
ax.plot([beta_comparison['pymc_mean'].min(), beta_comparison['pymc_mean'].max()],
        [beta_comparison['pymc_mean'].min(), beta_comparison['pymc_mean'].max()],
        'r--', linewidth=2, label='y=x')
ax.set_xlabel('PyMC Posterior Mean', fontsize=12)
ax.set_ylabel('brms Posterior Mean', fontsize=12)
ax.set_title('Beta Coefficients: Posterior Means', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Add predictor labels for largest differences
# Sort by absolute difference and get top 3
beta_comparison_abs = beta_comparison.copy()
beta_comparison_abs['abs_mean_diff'] = beta_comparison_abs['mean_diff'].abs()
top_diff = beta_comparison_abs.nlargest(3, 'abs_mean_diff')
for _, row in top_diff.iterrows():
    ax.annotate(row['predictor'], 
                (row['pymc_mean'], row['brms_mean']),
                xytext=(5, 5), textcoords='offset points', fontsize=9)

# Bar plot: Differences
ax = axes[1]
beta_comparison_sorted = beta_comparison.sort_values('abs_mean_diff')
ax.barh(range(len(beta_comparison_sorted)), beta_comparison_sorted['mean_diff'].values)
ax.set_yticks(range(len(beta_comparison_sorted)))
ax.set_yticklabels(beta_comparison_sorted['predictor'], fontsize=9)
ax.set_xlabel('Difference (PyMC - brms)', fontsize=12)
ax.set_title('Beta Coefficients: Mean Differences', fontsize=14, fontweight='bold')
ax.axvline(x=0, color='r', linestyle='--', linewidth=1)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('figs/beta_comparison_pymc_brms.png', dpi=300, bbox_inches='tight')
plt.show()

log_and_print("\n✓ Saved: figs/beta_comparison_pymc_brms.png")
```

## Compare Alpha Coefficients (Country Intercepts)

```python
log_and_print("\n" + "="*80)
log_and_print("ALPHA COEFFICIENTS (COUNTRY INTERCEPTS) COMPARISON")
log_and_print("="*80)

# Compute posterior means
alpha_comparison = pd.DataFrame({
    'country': countries,
    'pymc_mean': alpha_pymc_aligned.mean().values,
    'brms_mean': alpha_brms_aligned.mean().values,
})

alpha_comparison['mean_diff'] = alpha_comparison['pymc_mean'] - alpha_comparison['brms_mean']
# Sort by absolute mean difference (create abs column for sorting)
alpha_comparison['abs_mean_diff'] = alpha_comparison['mean_diff'].abs()
alpha_comparison = alpha_comparison.sort_values('abs_mean_diff', ascending=False)

# Overall correlation
corr_alpha, pval_alpha = pearsonr(alpha_comparison['pymc_mean'], alpha_comparison['brms_mean'])
log_and_print(f"\nCorrelation of posterior means: r = {corr_alpha:.6f} (p = {pval_alpha:.2e})")

# Maximum difference
max_diff_alpha_idx = alpha_comparison['mean_diff'].abs().idxmax()
max_diff_alpha = alpha_comparison.loc[max_diff_alpha_idx]
log_and_print(f"\nLargest difference:")
log_and_print(f"  Country: {max_diff_alpha['country']}")
log_and_print(f"  PyMC mean: {max_diff_alpha['pymc_mean']:.6f}")
log_and_print(f"  brms mean: {max_diff_alpha['brms_mean']:.6f}")
log_and_print(f"  Difference: {max_diff_alpha['mean_diff']:.6f}")

log_and_print("\nTop 10 differences:")
log_and_print(alpha_comparison.head(10)[['country', 'pymc_mean', 'brms_mean', 'mean_diff']].to_string(index=False))

log_and_print("="*80)
```

### Visualize Alpha Comparison

```python
# Plot: Country intercepts comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

# Scatter plot
ax = axes[0]
ax.scatter(alpha_comparison['pymc_mean'], alpha_comparison['brms_mean'], alpha=0.7, s=100)
ax.plot([alpha_comparison['pymc_mean'].min(), alpha_comparison['pymc_mean'].max()],
        [alpha_comparison['pymc_mean'].min(), alpha_comparison['pymc_mean'].max()],
        'r--', linewidth=2, label='y=x')
ax.set_xlabel('PyMC Posterior Mean', fontsize=12)
ax.set_ylabel('brms Posterior Mean', fontsize=12)
ax.set_title('Country Intercepts: Posterior Means', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Bar plot: Differences
ax = axes[1]
alpha_comparison_sorted = alpha_comparison.sort_values('abs_mean_diff')
ax.barh(range(len(alpha_comparison_sorted)), alpha_comparison_sorted['mean_diff'].values)
ax.set_yticks(range(len(alpha_comparison_sorted)))
ax.set_yticklabels(alpha_comparison_sorted['country'], fontsize=9)
ax.set_xlabel('Difference (PyMC - brms)', fontsize=12)
ax.set_title('Country Intercepts: Mean Differences', fontsize=14, fontweight='bold')
ax.axvline(x=0, color='r', linestyle='--', linewidth=1)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('figs/alpha_comparison_pymc_brms.png', dpi=300, bbox_inches='tight')
plt.show()

log_and_print("\n✓ Saved: figs/alpha_comparison_pymc_brms.png")
```

## Compare Hyperparameters

```python
log_and_print("\n" + "="*80)
log_and_print("HYPERPARAMETERS COMPARISON")
log_and_print("="*80)

# Compare each hyperparameter
for param in ['mu_alpha', 'sigma_alpha', 'sigma']:
    pymc_mean = hyperparams_pymc[param].mean()
    brms_mean = hyperparams_brms[param].mean()
    pymc_q2_5 = hyperparams_pymc[param].quantile(0.025)
    pymc_q97_5 = hyperparams_pymc[param].quantile(0.975)
    brms_q2_5 = hyperparams_brms[param].quantile(0.025)
    brms_q97_5 = hyperparams_brms[param].quantile(0.975)
    
    mean_diff = pymc_mean - brms_mean
    corr, pval = pearsonr(hyperparams_pymc[param], hyperparams_brms[param])
    
    log_and_print(f"\n{param}:")
    log_and_print(f"  PyMC: mean={pymc_mean:.6f}, 95%% CI=[{pymc_q2_5:.6f}, {pymc_q97_5:.6f}]")
    log_and_print(f"  brms: mean={brms_mean:.6f}, 95%% CI=[{brms_q2_5:.6f}, {brms_q97_5:.6f}]")
    log_and_print(f"  Difference: {mean_diff:.6f}")
    log_and_print(f"  Correlation: r={corr:.6f} (p={pval:.2e})")

log_and_print("="*80)
```

### Visualize Hyperparameters Comparison

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, param in enumerate(['mu_alpha', 'sigma_alpha', 'sigma']):
    ax = axes[idx]
    ax.scatter(hyperparams_pymc[param], hyperparams_brms[param], alpha=0.3, s=20)
    min_val = min(hyperparams_pymc[param].min(), hyperparams_brms[param].min())
    max_val = max(hyperparams_pymc[param].max(), hyperparams_brms[param].max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='y=x')
    ax.set_xlabel('PyMC', fontsize=12)
    ax.set_ylabel('brms', fontsize=12)
    ax.set_title(f'{param}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figs/hyperparams_comparison_pymc_brms.png', dpi=300, bbox_inches='tight')
plt.show()

log_and_print("\n✓ Saved: figs/hyperparams_comparison_pymc_brms.png")
```

## Summary Statistics

```python
log_and_print("\n" + "="*80)
log_and_print("SUMMARY STATISTICS")
log_and_print("="*80)

# Beta coefficients
beta_corr_all = []
for pred in predictors:
    corr, _ = pearsonr(beta_pymc_aligned[pred], beta_brms_aligned[pred])
    beta_corr_all.append(corr)

log_and_print(f"\nBeta Coefficients:")
log_and_print(f"  Mean correlation: {np.mean(beta_corr_all):.6f}")
log_and_print(f"  Min correlation: {np.min(beta_corr_all):.6f}")
log_and_print(f"  Max correlation: {np.max(beta_corr_all):.6f}")

# Alpha coefficients
alpha_corr_all = []
for country in countries:
    corr, _ = pearsonr(alpha_pymc_aligned[country], alpha_brms_aligned[country])
    alpha_corr_all.append(corr)

log_and_print(f"\nAlpha Coefficients (Country Intercepts):")
log_and_print(f"  Mean correlation: {np.mean(alpha_corr_all):.6f}")
log_and_print(f"  Min correlation: {np.min(alpha_corr_all):.6f}")
log_and_print(f"  Max correlation: {np.max(alpha_corr_all):.6f}")

# Hyperparameters
hyperparams_corr = {}
for param in ['mu_alpha', 'sigma_alpha', 'sigma']:
    corr, _ = pearsonr(hyperparams_pymc[param], hyperparams_brms[param])
    hyperparams_corr[param] = corr

log_and_print(f"\nHyperparameters:")
for param, corr in hyperparams_corr.items():
    log_and_print(f"  {param}: r={corr:.6f}")

log_and_print("="*80)
```

## Save Comparison Results

```python
# Save comparison tables
beta_comparison.to_csv('tables/beta_comparison_pymc_brms.csv', index=False)
alpha_comparison.to_csv('tables/alpha_comparison_pymc_brms.csv', index=False)

log_and_print("\n✓ Saved comparison tables:")
log_and_print("  tables/beta_comparison_pymc_brms.csv")
log_and_print("  tables/alpha_comparison_pymc_brms.csv")
```

## Close Log File

```python
log_and_print(f"\nLog file saved: {log_path}")
log_file.close()
```

```python
from utils import beep
beep()
```

