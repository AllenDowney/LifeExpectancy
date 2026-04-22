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

# Bayesian Panel Data Model

This notebook implements a Bayesian hierarchical panel model to analyze HALE and Life Expectancy gender gaps using both temporal variation and cross-country variation simultaneously. The temporal range is configurable (default: 2000-2019, can be extended to 2023 to include COVID years). **Panel data is loaded from `process.md` output** (`interim/panel_hale.h5`, `interim/panel_le.h5`). Run `process.md` first.

## Overview

The panel data approach provides more statistical power and allows us to model how relationships between indicators and gender gaps evolve over time, while accounting for country-specific characteristics.

**Model Structure:**
- Bayesian hierarchical model with country-level random intercepts
- Shared slopes for all predictors (same across all countries)
- Uses both within-country and between-country variation
- Controls for time-invariant country-level factors

**Run headlessly (jupytext + papermill):** from a terminal (adjust `~/LifeExpectancy` if your clone is elsewhere):

```
cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && \
  jupytext --to ipynb bayesian_model.md --output bayesian_model.ipynb && \
  papermill bayesian_model.ipynb bayesian_model_executed.ipynb
```

The parameters cell sets `FORCE_RUN = False` by default (reuse `nc/trace_hale*.nc` / `trace_le*.nc` when present). Append e.g. `-p FORCE_RUN True` on the `papermill` line to ignore cache and resample.

MCMC and post-processing can take a long time; the executed notebook is `notebooks/bayesian_model_executed.ipynb`.

```python
%load_ext autoreload
%autoreload 2
```

```python
import numpy as np
import pandas as pd
import pymc as pm
import matplotlib.pyplot as plt
import arviz as az

from utils import (
    decorate, underride, configure_plot_style, AIBM_COLORS,
    write_html_table, code_to_who_country
)
from model_utils import load_idata_or_sample

configure_plot_style()
```

```python
import sys
import IPython
from utils import beep

def beep_on_error(shell, etype, evalue, tb, tb_offset=None):
    beep()  
    # Call the original handler so the traceback still appears
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)

ip = IPython.get_ipython()
ip.set_custom_exc((Exception,), beep_on_error)
```

## Model Configuration

```python
# ============================================================================
# MODEL CONFIGURATION: TEMPORAL CUTOFF AND COVID DATA
# ============================================================================
# Global variable: Whether to include COVID-19 data as a predictor
# Set to True to include COVID-19 death rates as a predictor and extend analysis to 2023
# Set to False to exclude COVID-19 and use pre-COVID baseline (2000-2019)
# Note: Both IHME HALE and OWID LE extend to 2023, enabling full COVID-19 analysis
INCLUDE_COVID_DATA = True

# Cutoff year is automatically determined by COVID flag
# Both IHME HALE and OWID LE extend to 2023
# True -> 2023 (includes all COVID years), False -> 2019 (pre-COVID baseline)
CUTOFF_YEAR = 2023 if INCLUDE_COVID_DATA else 2019

# Global variable: List of countries to exclude from analysis
# Set to empty list [] to include all countries
# Note: Turkey (TUR) is not in IHME HALE data, so it's automatically excluded when using IHME
COUNTRIES_TO_EXCLUDE = ['TUR']

# Predictors to include (Gap_* columns from process panel)
# Names must match process output (see utils.column_name_mapping)
PREDICTORS_TO_INCLUDE = [
    'Alcohol',
    'Suicide',
    'Homicide',
    'RoadTraffic',  
    'Cardiovascular', 
    'Diabetes',
    'Neoplasms',
    'ChronicRespiratory',
    'LiverDisease',
    'UnintentionalInjury',
    'DrugDisorder',
    'Childhood',        # Experiment 3b: frail male hypothesis
    # 'MaternalDisorders',  # Experiment 3a: toggle
    # 'ConflictTerrorism',  # Experiment 1: tested with Childhood; exclude (negligible)
]
if INCLUDE_COVID_DATA:
    PREDICTORS_TO_INCLUDE = PREDICTORS_TO_INCLUDE + ['COVID']  # COVID19->COVID in process

print(f"Model Configuration:")
print(f"  HALE Data Source: IHME (GBD 2023, 2000-2023)")
print(f"  LE Data Source: OWID (HMD + UN WPP, 2000-2023)")
print(f"  Include COVID Data: {INCLUDE_COVID_DATA}")
print(f"  Cutoff Year: {CUTOFF_YEAR} (automatically set based on COVID flag)")
print(f"  Countries Excluded: {COUNTRIES_TO_EXCLUDE}")
print(f"  Predictors: {PREDICTORS_TO_INCLUDE}")
```

```python tags=["parameters"]
# Papermill: `-p FORCE_RUN True` forces new MCMC even when `nc/trace_*.nc` exists
FORCE_RUN = False
```

```python
# Human-readable labels for importance tables (Gap_* variable name -> display label)
PREDICTOR_DISPLAY_LABELS = {
    'Gap_Alcohol': 'Alcohol',
    'Gap_Suicide': 'Suicide',
    'Gap_Homicide': 'Homicide',
    'Gap_RoadTraffic': 'Road traffic',
    'Gap_Cardiovascular': 'Cardiovascular disease',
    'Gap_Diabetes': 'Diabetes',
    'Gap_Neoplasms': 'Cancer',
    'Gap_ChronicRespiratory': 'Chronic respiratory',
    'Gap_LiverDisease': 'Liver disease',
    'Gap_UnintentionalInjury': 'Unintentional injury',
    'Gap_DrugDisorder': 'Drug disorders',
    'Gap_Childhood': 'Child mortality',
    'Gap_COVID': 'COVID-19',
    'Gap_MaternalDisorders': 'Maternal disorders',
    'Gap_ConflictTerrorism': 'Conflict and terrorism',
}
```

```python
# Setup logging
import os

# Create descriptive log filename
covid_suffix = 'with_covid' if INCLUDE_COVID_DATA else 'pre_covid'
log_path = f'logs/bayesian_model_ihme_{covid_suffix}_{CUTOFF_YEAR}.txt'

log_file = open(log_path, 'w')
print(f"Logging to: {log_path}")

def log_and_print(message, log_file=None):
    """
    Helper function to write to log file and print to notebook.
    """
    if log_file is None:
        log_file = globals().get('log_file', None)
    
    if log_file:
        log_file.write(message + "\n")
        log_file.flush()
    
    print(message)

# Log configuration
log_and_print("="*80)
log_and_print("BAYESIAN PANEL MODEL - HALE AND LIFE EXPECTANCY GENDER GAPS")
log_and_print("="*80)
log_and_print(f"Timestamp: {pd.Timestamp.now()}")
log_and_print(f"HALE Data Source: IHME")
log_and_print(f"Include COVID Data: {INCLUDE_COVID_DATA}")
log_and_print(f"Analysis Period: 2000-{CUTOFF_YEAR}")
log_and_print(f"Countries Excluded: {COUNTRIES_TO_EXCLUDE}")
log_and_print("="*80)
```

## Data Preparation

### Load Panel Data

Panel data is created by `process.md`. Run process first. Panels include all targets and predictors; model selects which predictors to use.

```python
# Load panels from process output
panel_hale = pd.read_hdf('interim/panel_hale.h5', key='panel')
panel_le = pd.read_hdf('interim/panel_le.h5', key='panel')

print(f"Loaded HALE panel: {panel_hale.shape}")
print(f"Loaded LE panel: {panel_le.shape}")

# Apply country exclusions (if any)
if COUNTRIES_TO_EXCLUDE:
    n_before_h = len(panel_hale)
    n_before_l = len(panel_le)
    panel_hale = panel_hale[~panel_hale['country'].isin(COUNTRIES_TO_EXCLUDE)].copy()
    panel_le = panel_le[~panel_le['country'].isin(COUNTRIES_TO_EXCLUDE)].copy()
    print(f"Excluded {COUNTRIES_TO_EXCLUDE}: HALE {n_before_h} -> {len(panel_hale)}, LE {n_before_l} -> {len(panel_le)}")

# Filter to cutoff year
panel_hale = panel_hale[(panel_hale['Year'] >= 2000) & (panel_hale['Year'] <= CUTOFF_YEAR)].copy()
panel_le = panel_le[(panel_le['Year'] >= 2000) & (panel_le['Year'] <= CUTOFF_YEAR)].copy()

# Drop rows with missing target
panel_hale = panel_hale.dropna(subset=['HALE_gap']).copy()
panel_le = panel_le.dropna(subset=['LE_gap']).copy()

panel_hale = panel_hale.sort_values(['country', 'Year']).reset_index(drop=True)
panel_le = panel_le.sort_values(['country', 'Year']).reset_index(drop=True)

print(f"\nFinal HALE panel: {panel_hale.shape}")
print(f"Final LE panel: {panel_le.shape}")
panel_hale.head()
```

```python
# Log data loading summary
log_and_print("\n" + "="*80)
log_and_print("PANEL DATA LOADED")
log_and_print("="*80)
log_and_print(f"HALE: {panel_hale.shape[0]} rows, {panel_hale['country'].nunique()} countries")
log_and_print(f"  Years: {panel_hale['Year'].min():.0f}-{panel_hale['Year'].max():.0f}")
log_and_print(f"LE: {panel_le.shape[0]} rows, {panel_le['country'].nunique()} countries")
log_and_print(f"  Years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
log_and_print("="*80)
```

## Prepare Panel Data for Modeling

Now we'll use the `prepare_panel_data` function to standardize predictors and center targets:

```python
def prepare_panel_data(df, predictor_cols, target_col):
    """
    Prepare panel data for Bayesian modeling.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Long-format DataFrame with columns:
        - 'country' (str)
        - 'year' (int)
        - target_col (float, HALE_gap or LE_gap in years)
        - predictor_cols (float)
    
    Returns
    -------
    data_dict : dict
        Dictionary with:
            X          : (N, P) ndarray of standardized predictors
            y_centered : (N,) ndarray of centered target
            country_idx: (N,) int array in [0, n_country-1]
            year_idx   : (N,) int array in [0, n_year-1]
            coords     : dict for PyMC Model(coords=...)
            meta       : dict with means/SDs for later use
    """
    df = df.copy()
    
    # Unique levels
    countries = np.sort(df["country"].unique())
    years = np.sort(df["year"].unique())
    predictors = list(predictor_cols)
    
    country_indexer = {c: i for i, c in enumerate(countries)}
    year_indexer = {y: i for i, y in enumerate(years)}
    
    df["country_idx"] = df["country"].map(country_indexer)
    df["year_idx"] = df["year"].map(year_indexer)
    
    # Extract raw matrices/vectors
    X_raw = df[predictor_cols].to_numpy(dtype=float)
    y_raw = df[target_col].to_numpy(dtype=float)
    country_idx = df["country_idx"].to_numpy(dtype=int)
    year_idx = df["year_idx"].to_numpy(dtype=int)
    
    # Standardize predictors across all country–year rows
    X_mean = X_raw.mean(axis=0)
    X_std = X_raw.std(axis=0, ddof=0)
    # Guard against any zero variance columns
    X_std_safe = np.where(X_std == 0, 1.0, X_std)
    X = (X_raw - X_mean) / X_std_safe
    
    # Center target (keep units in years)
    y_mean = y_raw.mean()
    y_centered = y_raw - y_mean
    
    N, P = X.shape
    
    coords = {
        "obs": np.arange(N),
        "country": countries,
        "year": years,
        "predictor": predictors,
    }
    
    data_dict = {
        "X": X,
        "y_centered": y_centered,
        "country_idx": country_idx,
        "year_idx": year_idx,
        "coords": coords,
        "meta": {
            "X_mean": X_mean,
            "X_std": X_std_safe,
            "y_mean": y_mean,
            "countries": countries,
            "years": years,
            "predictors": predictors,
        },
    }
    
    return data_dict
```

```python
# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
# Mid predictors to include (e.g., ['Mid_Cardiovascular', 'Mid_Diabetes'])
# [] = baseline (Gap predictors only)
MID_PREDICTORS_TO_INCLUDE = []  

# Global variable: Whether to include year effects (Gaussian Random Walk)
# Set to True to include year effects to control for global temporal trends
# Set to False to exclude year effects (current model)
INCLUDE_YEAR_EFFECTS = False

# Helper function to generate output filenames with appropriate suffix
def get_output_filename(base_path, mid_predictors_list=None, include_year_effects=False, 
                        cutoff_year=None, include_covid_data=None):
    """
    Generate output filename with appropriate suffixes based on configuration.
    
    Parameters
    ----------
    base_path : str
        Base file path (e.g., 'tables/beta_coefficients_hale.html')
    mid_predictors_list : list, optional
        List of Mid predictors to include (e.g., ['Mid_Cardiovascular'])
        If None or empty, uses 'nomid' suffix
    include_year_effects : bool
        Whether year effects (GRW) are included in the model
    cutoff_year : int, optional
        Cutoff year for analysis. If None, uses global CUTOFF_YEAR.
    include_covid_data : bool, optional
        Whether COVID data is included. If None, uses global INCLUDE_COVID_DATA.
        
    Returns
    -------
    filename : str
        Filename with appropriate suffixes inserted before extension
        Examples:
        - No Mid, 2019: 'beta_coefficients_hale_ihme_nomid_nogrw_y2019_nocovid.html'
        - With COVID, 2021: 'beta_coefficients_hale_ihme_nomid_nogrw_y2021_covid.html'
    """
    import os
    path_parts = base_path.rsplit('.', 1)
    has_ext = len(path_parts) == 2
    
    # Use global values if not provided
    if cutoff_year is None:
        cutoff_year = CUTOFF_YEAR
    if include_covid_data is None:
        include_covid_data = INCLUDE_COVID_DATA
    
    # Generate Mid predictor suffix
    if mid_predictors_list is None or len(mid_predictors_list) == 0:
        mid_suffix = 'nomid'
    else:
        # Create short names for each Mid predictor
        short_names = {
            'Mid_Cardiovascular': 'cardio',
            'Mid_Diabetes': 'diabetes',
            'Mid_ChronicRespiratory': 'respiratory',
            'Mid_UnintentionalInjury': 'unintentional',
            'Mid_Neoplasms': 'neoplasms',
        }
        # Generate suffix from list (e.g., 'midcardio_diabetes')
        mid_parts = []
        for mid_pred in sorted(mid_predictors_list):  # Sort for consistency
            short_name = short_names.get(mid_pred, mid_pred.replace('Mid_', '').lower())
            mid_parts.append(short_name)
        mid_suffix = 'mid' + '_'.join(mid_parts)
    
    # Generate year effects suffix
    grw_suffix = 'yesgrw' if include_year_effects else 'nogrw'
    
    # Generate cutoff year suffix
    year_suffix = f'y{cutoff_year}'
    
    # Generate COVID suffix
    covid_suffix = 'covid' if include_covid_data else 'nocovid'
    
    # HALE data source (IHME only)
    hale_suffix = 'ihme'
    
    # Combine suffixes
    if has_ext:
        base, ext = path_parts
        return f"{base}_{hale_suffix}_{mid_suffix}_{grw_suffix}_{year_suffix}_{covid_suffix}.{ext}"
    else:
        return f"{base_path}_{hale_suffix}_{mid_suffix}_{grw_suffix}_{year_suffix}_{covid_suffix}"

# Prepare predictor columns from PREDICTORS_TO_INCLUDE (Gap_* columns from process panel)
predictor_cols = [f'Gap_{p}' for p in PREDICTORS_TO_INCLUDE]

# Verify all requested predictors exist in panel
missing = [c for c in predictor_cols if c not in panel_hale.columns]
if missing:
    raise ValueError(f"Predictors not found in panel (run process.md first): {missing}")

# Add selected Mid predictors
if MID_PREDICTORS_TO_INCLUDE:
    for mid_pred in MID_PREDICTORS_TO_INCLUDE:
        if mid_pred in panel_hale.columns:
            predictor_cols.append(mid_pred)
            print(f"  Adding: {mid_pred}")
        else:
            print(f"  WARNING: {mid_pred} not found in panel columns")
    
    print(f"\nIncluding Mid predictors: YES ({len(MID_PREDICTORS_TO_INCLUDE)} predictor(s))")
    print(f"  Selected: {MID_PREDICTORS_TO_INCLUDE}")
else:
    print(f"Including Mid predictors: NO (Gap predictors only)")

print(f"\nNumber of predictors: {len(predictor_cols)}")
print(f"Predictors: {sorted(predictor_cols)}")
```

```python
# Prepare data for HALE gap model (uses panel_hale)
# Drop rows with missing predictor values
panel_hale_model = panel_hale.dropna(subset=predictor_cols).copy()
panel_hale_model = panel_hale_model.rename(columns={'Year': 'year'})

data_hale = prepare_panel_data(
    panel_hale_model,
    predictor_cols=predictor_cols,
    target_col='HALE_gap'
)

print(f"HALE model data:")
print(f"  Observations: {data_hale['X'].shape[0]}")
print(f"  Predictors: {data_hale['X'].shape[1]}")
print(f"  Countries: {len(data_hale['coords']['country'])}")
print(f"  Years: {len(data_hale['coords']['year'])}")
print(f"  Year range: {min(data_hale['meta']['years'])}-{max(data_hale['meta']['years'])}")
if COUNTRIES_TO_EXCLUDE:
    print(f"  Excluded: {COUNTRIES_TO_EXCLUDE}")
```

```python
# Prepare data for Life Expectancy gap model (uses panel_le)
# Drop rows with missing predictor values
panel_le_model = panel_le.dropna(subset=predictor_cols).copy()
panel_le_model = panel_le_model.rename(columns={'Year': 'year'})

data_le = prepare_panel_data(
    panel_le_model,
    predictor_cols=predictor_cols,
    target_col='LE_gap'
)

print(f"Life Expectancy model data:")
print(f"  Observations: {data_le['X'].shape[0]}")
print(f"  Predictors: {data_le['X'].shape[1]}")
print(f"  Countries: {len(data_le['coords']['country'])}")
print(f"  Years: {len(data_le['coords']['year'])}")
print(f"  Year range: {min(data_le['meta']['years'])}-{max(data_le['meta']['years'])}")
if COUNTRIES_TO_EXCLUDE:
    print(f"  Excluded: {COUNTRIES_TO_EXCLUDE}")
```


## Build Bayesian Model Function

Now we'll define the function to build the Bayesian hierarchical model with random intercepts:

```python
def build_random_intercept_panel_model(data, include_year_effects=False):
    """
    Build a Bayesian hierarchical panel model with:
      - Random intercepts by country
      - Shared slopes for all predictors
      - Optional year effects (Gaussian Random Walk) to control for global temporal trends
      - Centered outcome y (HALE_gap or LE_gap) in years
      - Standardized predictors
    
    Parameters
    ----------
    data : dict
        Output of prepare_panel_data(...)
    include_year_effects : bool
        If True, include Gaussian Random Walk year effects to control for global temporal trends
    
    Returns
    -------
    model : pymc.Model
        PyMC model object
    """
    X = data["X"]
    y_centered = data["y_centered"]
    country_idx = data["country_idx"]
    year_idx = data["year_idx"]
    coords = data["coords"]
    
    with pm.Model(coords=coords) as model:
        # Register index arrays and design matrix as Data
        country_idx_data = pm.Data("country_idx", country_idx, dims="obs")
        year_idx_data = pm.Data("year_idx", year_idx, dims="obs")
        X_data = pm.Data("X", X, dims=("obs", "predictor"))
        y_data = pm.Data("y", y_centered, dims="obs")
        
        # Hyperpriors for country intercepts
        mu_alpha = pm.Normal("mu_alpha", mu=0.0, sigma=5.0)
        sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=1.0)
        
        # Country-specific random intercepts
        alpha_raw = pm.Normal("alpha_raw", mu=0.0, sigma=1.0, dims="country")
        alpha = pm.Deterministic(
            "alpha",
            mu_alpha + alpha_raw * sigma_alpha,
            dims="country",
        )
        
        # Optional year effects (Gaussian Random Walk)
        if include_year_effects:
            # Standard deviation for random walk innovations
            sigma_gamma = pm.HalfNormal("sigma_gamma", sigma=0.5)
            # Gaussian Random Walk for year effects
            # init_dist specifies the distribution for the initial value
            # sigma=sigma_gamma controls the step size (innovation standard deviation)
            gamma = pm.GaussianRandomWalk(
                "gamma", 
                init_dist=pm.Normal.dist(mu=0.0, sigma=0.5),
                sigma=sigma_gamma, 
                dims="year"
            )
        else:
            gamma = None
        
        # Global slopes for standardized predictors
        beta = pm.Normal("beta", mu=0.0, sigma=1.0, dims="predictor")
        
        # Residual standard deviation (on y_centered scale, i.e., years)
        sigma = pm.HalfNormal("sigma", sigma=1.0)
        
        # Linear predictor: random intercept by country + (optional) year effects + global slopes
        if include_year_effects:
            mu = pm.Deterministic(
                "mu",
                alpha[country_idx_data] + gamma[year_idx_data] + pm.math.dot(X_data, beta),
                dims="obs"
            )
        else:
            mu = pm.Deterministic(
                "mu",
                alpha[country_idx_data] + pm.math.dot(X_data, beta),
                dims="obs"
            )
        
        # Likelihood
        y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y_data, dims="obs")
    
    return model
```

## HALE Gap Model

### Build Model

```python
# Build model for HALE gap
model_hale = build_random_intercept_panel_model(data_hale, include_year_effects=INCLUDE_YEAR_EFFECTS)
if INCLUDE_YEAR_EFFECTS:
    print("Year effects (GRW): INCLUDED")
else:
    print("Year effects (GRW): NOT INCLUDED")
```

```python
# NetCDF paths for posterior cache (same stem logic as end-of-notebook exports)
from pathlib import Path

nc_dir = Path('nc')
nc_dir.mkdir(parents=True, exist_ok=True)
trace_filename_hale = nc_dir / f"{get_output_filename('trace_hale', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)}.nc"
trace_filename_le = nc_dir / f"{get_output_filename('trace_le', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)}.nc"
suffix = get_output_filename('', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
```

### Sample from Posterior

```python
# Sample or load cached HALE posterior (see papermill parameter FORCE_RUN)
with model_hale:
    trace_hale = load_idata_or_sample(
        model_hale,
        str(trace_filename_hale),
        force_run=FORCE_RUN,
        nuts_sampler='nutpie',
    )

# Log-likelihood for WAIC/LOO (skip if already in NetCDF from a prior run)
with model_hale:
    if "log_likelihood" not in trace_hale.groups():
        pm.compute_log_likelihood(trace_hale)
```

```python
# Log HALE model summary
log_and_print("\n" + "="*80)
log_and_print("HALE MODEL - SAMPLING COMPLETE")
log_and_print("="*80)
summary = az.summary(trace_hale, var_names=["mu_alpha", "sigma_alpha", "sigma"])
log_and_print(f"Samples: {trace_hale.posterior.sizes['draw']} draws x {trace_hale.posterior.sizes['chain']} chains")
log_and_print(f"Max R-hat: {summary['r_hat'].max():.4f}")
log_and_print(f"Min ESS (bulk): {summary['ess_bulk'].min():.0f}")
log_and_print("="*80)
```

### Model Diagnostics

Check convergence and sampling quality:

```python
# HALE model diagnostics
az.summary(trace_hale, var_names=["mu_alpha", "sigma_alpha", "sigma", "beta"])
```

```python
# Plot trace plots for key parameters (HALE)
az.plot_trace(trace_hale, var_names=["mu_alpha", "sigma_alpha", "sigma"], compact=True)
plt.tight_layout()
plt.show()
```

### Posterior Analysis

Extract and analyze posterior distributions:

```python
# Extract posterior means and credible intervals for beta coefficients (HALE)
beta_summary_hale = az.summary(trace_hale, var_names=["beta"])
beta_summary_hale.index = data_hale["meta"]["predictors"]
beta_summary_hale
```

```python
# Write beta coefficients table to HTML
beta_summary_hale_formatted = beta_summary_hale.reset_index().rename(columns={'index': 'Predictor'})
write_html_table(beta_summary_hale_formatted, get_output_filename('tables/beta_coefficients_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Compute importance measures on original scale
# Extract posterior samples for beta coefficients
beta_samples_hale = trace_hale.posterior["beta"].values.reshape(-1, len(data_hale["meta"]["predictors"]))

# Get SD values used for standardization
X_std_hale = data_hale["meta"]["X_std"]
predictors_hale = data_hale["meta"]["predictors"]

# Compute importance measure: |β_standardized| × SD_original
importance_samples_hale = np.abs(beta_samples_hale) * X_std_hale[np.newaxis, :]

# Create summary table
importance_summary_hale = pd.DataFrame({
    'Predictor': predictors_hale,
    'SD_original': X_std_hale,
    'Beta_standardized_mean': beta_summary_hale['mean'].values,
    'Beta_standardized_hdi_3%': beta_summary_hale['hdi_3%'].values,
    'Beta_standardized_hdi_97%': beta_summary_hale['hdi_97%'].values,
    'Importance_mean': importance_samples_hale.mean(axis=0),
    'Importance_hdi_3%': np.percentile(importance_samples_hale, 3, axis=0),
    'Importance_hdi_97%': np.percentile(importance_samples_hale, 97, axis=0),
})

# Format for display
importance_summary_hale_formatted = importance_summary_hale.copy()
importance_summary_hale_formatted['Beta_standardized'] = (
    importance_summary_hale['Beta_standardized_mean'].round(3).astype(str) + 
    ' [' + importance_summary_hale['Beta_standardized_hdi_3%'].round(3).astype(str) + 
    ', ' + importance_summary_hale['Beta_standardized_hdi_97%'].round(3).astype(str) + ']'
)
importance_summary_hale_formatted['Importance'] = (
    importance_summary_hale['Importance_mean'].round(3).astype(str) + 
    ' [' + importance_summary_hale['Importance_hdi_3%'].round(3).astype(str) + 
    ', ' + importance_summary_hale['Importance_hdi_97%'].round(3).astype(str) + ']'
)

# Select columns for output table and sort by importance
importance_table_hale = importance_summary_hale_formatted[[
    'Predictor', 'SD_original', 'Beta_standardized', 'Importance'
]].copy()
importance_table_hale = importance_table_hale.loc[
    importance_summary_hale.sort_values('Importance_mean', ascending=False).index
].reset_index(drop=True)

# Create human-readable version for HTML export
importance_table_hale_display = importance_table_hale.copy()
importance_table_hale_display['Cause'] = importance_table_hale_display['Predictor'].map(
    lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)
)
importance_table_hale_display = importance_table_hale_display[['Cause', 'SD_original', 'Beta_standardized', 'Importance']].rename(
    columns={'SD_original': 'Standard deviation', 'Beta_standardized': 'Coefficient'}
)

print("Importance Measures on Original Scale (HALE Gap Model):")
print(importance_table_hale.to_string(index=False))

# Log for experiments (coefficients and importance)
log_and_print("\n" + "="*80)
log_and_print("HALE GAP MODEL - COEFFICIENTS (β mean ± sd, 94% HDI)")
log_and_print("="*80)
for pred in beta_summary_hale.index:
    r = beta_summary_hale.loc[pred]
    log_and_print(f"  {pred}: β={r['mean']:.4f} ± {r['sd']:.4f}, 94% HDI [{r['hdi_3%']:.4f}, {r['hdi_97%']:.4f}]")
log_and_print("\nHALE GAP MODEL - IMPORTANCE (ranked)")
log_and_print("-"*80)
for _, row in importance_table_hale.iterrows():
    log_and_print(f"  {row['Predictor']}: {row['Importance']}")
log_and_print("="*80)

# Write to HTML (human-readable labels)
write_html_table(importance_table_hale_display, get_output_filename('tables/importance_measures_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Plot posterior distributions of beta coefficients (HALE)
az.plot_forest(trace_hale, var_names=["beta"], combined=True, figsize=(10, 12))
plt.title("Posterior Distributions of Predictor Coefficients (HALE Gap)")
plt.tight_layout()
plt.savefig(get_output_filename('figs/posterior_forest_beta_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS), dpi=300, bbox_inches='tight')
plt.show()
```

```python
# Extract posterior means and credible intervals for alpha coefficients (country intercepts, HALE)
alpha_summary_hale = az.summary(trace_hale, var_names=["alpha"])
alpha_summary_hale.index = data_hale["meta"]["countries"]
alpha_summary_hale
```

```python
# Write alpha coefficients table to HTML
alpha_summary_hale_formatted = alpha_summary_hale.reset_index().rename(columns={'index': 'Country'})
write_html_table(alpha_summary_hale_formatted, get_output_filename('tables/alpha_coefficients_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Plot posterior distributions of country-specific intercepts (alpha) (HALE)
az.plot_forest(trace_hale, var_names=["alpha"], combined=True, figsize=(8, 12))
plt.title("Posterior Distributions of Country-Specific Intercepts (HALE Gap)")
plt.tight_layout()
plt.savefig(get_output_filename('figs/posterior_forest_alpha_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS), dpi=300, bbox_inches='tight')
plt.show()
```

### Correlations

#### Top 10 posterior correlations between slope pairs (β), HALE

Pearson **r** between MCMC draws for each pair of standardized slope coefficients; pairs ranked by **|r|** (strongest linear association in either direction). A heatmap and pair plot for a selected set of causes are computed for the **LE** model only (see below).

```python
# Extract posterior samples for beta coefficients (if not already done)
beta_extracted_hale = az.extract(trace_hale)
beta_samples_df_hale = pd.DataFrame(
    beta_extracted_hale['beta'].T,
    columns=data_hale["meta"]["predictors"]
)

# Compute correlation matrix for beta coefficients
beta_corr_hale = beta_samples_df_hale.corr()

# Extract upper triangle (excluding diagonal) and convert to long format
beta_corr_triu = np.triu(beta_corr_hale.values, k=1)
beta_corr_long = []
for i in range(len(beta_corr_hale.index)):
    for j in range(i + 1, len(beta_corr_hale.columns)):
        if not np.isnan(beta_corr_triu[i, j]):
            beta_corr_long.append({
                'Predictor1': beta_corr_hale.index[i],
                'Predictor2': beta_corr_hale.columns[j],
                'Correlation': beta_corr_triu[i, j]
            })

beta_corr_df_hale = pd.DataFrame(beta_corr_long)
beta_corr_df_hale['Abs_Correlation'] = beta_corr_df_hale['Correlation'].abs()
beta_corr_top10_hale = beta_corr_df_hale.nlargest(10, 'Abs_Correlation')[
    ['Predictor1', 'Predictor2', 'Correlation']
].sort_values('Correlation', key=abs, ascending=False).reset_index(drop=True)

beta_corr_top10_hale_display = pd.DataFrame({
    'Rank': range(1, len(beta_corr_top10_hale) + 1),
    'Cause 1': beta_corr_top10_hale['Predictor1'].map(lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)),
    'Cause 2': beta_corr_top10_hale['Predictor2'].map(lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)),
    'r': beta_corr_top10_hale['Correlation'],
})

print('Top 10 β-posterior correlations (HALE gender gap), by |r|:')
for _, row in beta_corr_top10_hale_display.iterrows():
    print(f"  {row['Rank']:>2}. r={row['r']:+.3f}   {row['Cause 1']}  ↔  {row['Cause 2']}")
beta_corr_top10_hale_display
```

```python
# Write beta correlations table to HTML
write_html_table(
    beta_corr_top10_hale_display,
    get_output_filename('tables/beta_correlations_top10_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS),
)
```

```python
# Extract posterior samples for alpha coefficients (country intercepts)
alpha_extracted_hale = az.extract(trace_hale)
alpha_samples_df_hale = pd.DataFrame(
    alpha_extracted_hale['alpha'].T,
    columns=data_hale["meta"]["countries"]
)

# Compute correlation matrix for alpha coefficients
alpha_corr_hale = alpha_samples_df_hale.corr()

# Extract upper triangle (excluding diagonal) and convert to long format
alpha_corr_triu = np.triu(alpha_corr_hale.values, k=1)
alpha_corr_long = []
for i in range(len(alpha_corr_hale.index)):
    for j in range(i + 1, len(alpha_corr_hale.columns)):
        if not np.isnan(alpha_corr_triu[i, j]):
            alpha_corr_long.append({
                'Country1': alpha_corr_hale.index[i],
                'Country2': alpha_corr_hale.columns[j],
                'Correlation': alpha_corr_triu[i, j]
            })

alpha_corr_df_hale = pd.DataFrame(alpha_corr_long)
alpha_corr_df_hale['Abs_Correlation'] = alpha_corr_df_hale['Correlation'].abs()
alpha_corr_top10_hale = alpha_corr_df_hale.nlargest(10, 'Abs_Correlation')[
    ['Country1', 'Country2', 'Correlation']
].sort_values('Correlation', key=abs, ascending=False)

print("Top 10 correlations among alpha coefficients (country intercepts, HALE):")
alpha_corr_top10_hale
```

```python
# Write alpha correlations table to HTML
write_html_table(alpha_corr_top10_hale, get_output_filename('tables/alpha_correlations_top10_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

## Life Expectancy Gap Model

### Build Model

```python
# Build model for Life Expectancy gap
model_le = build_random_intercept_panel_model(data_le, include_year_effects=INCLUDE_YEAR_EFFECTS)
if INCLUDE_YEAR_EFFECTS:
    print("Year effects (GRW): INCLUDED")
else:
    print("Year effects (GRW): NOT INCLUDED")
```

### Sample from Posterior

```python
# Sample or load cached LE posterior (same FORCE_RUN; paths set with HALE block above)
with model_le:
    trace_le = load_idata_or_sample(
        model_le,
        str(trace_filename_le),
        force_run=FORCE_RUN,
        nuts_sampler='nutpie',
    )

with model_le:
    if "log_likelihood" not in trace_le.groups():
        pm.compute_log_likelihood(trace_le)
```

```python
# Log LE model summary
log_and_print("\n" + "="*80)
log_and_print("LIFE EXPECTANCY MODEL - SAMPLING COMPLETE")
log_and_print("="*80)
summary = az.summary(trace_le, var_names=["mu_alpha", "sigma_alpha", "sigma"])
log_and_print(f"Samples: {trace_le.posterior.sizes['draw']} draws x {trace_le.posterior.sizes['chain']} chains")
log_and_print(f"Max R-hat: {summary['r_hat'].max():.4f}")
log_and_print(f"Min ESS (bulk): {summary['ess_bulk'].min():.0f}")
log_and_print("="*80)
```

### Model Diagnostics

Check convergence and sampling quality:

```python
# Life Expectancy model diagnostics
az.summary(trace_le, var_names=["mu_alpha", "sigma_alpha", "sigma", "beta"])
```

```python
# Plot trace plots for key parameters (Life Expectancy)
az.plot_trace(trace_le, var_names=["mu_alpha", "sigma_alpha", "sigma"], compact=True)
plt.tight_layout()
plt.show()
```

### Posterior Analysis

Extract and analyze posterior distributions:

```python
# Extract posterior means and credible intervals for beta coefficients (Life Expectancy)
beta_summary_le = az.summary(trace_le, var_names=["beta"])
beta_summary_le.index = data_le["meta"]["predictors"]
beta_summary_le
```

```python
# Write beta coefficients table to HTML
beta_summary_le_formatted = beta_summary_le.reset_index().rename(columns={'index': 'Predictor'})
write_html_table(beta_summary_le_formatted, get_output_filename('tables/beta_coefficients_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Compute importance measures on original scale
# Extract posterior samples for beta coefficients
beta_samples_le = trace_le.posterior["beta"].values.reshape(-1, len(data_le["meta"]["predictors"]))

# Get SD values used for standardization
X_std_le = data_le["meta"]["X_std"]
predictors_le = data_le["meta"]["predictors"]

# Compute importance measure: |β_standardized| × SD_original
importance_samples_le = np.abs(beta_samples_le) * X_std_le[np.newaxis, :]

# Create summary table
importance_summary_le = pd.DataFrame({
    'Predictor': predictors_le,
    'SD_original': X_std_le,
    'Beta_standardized_mean': beta_summary_le['mean'].values,
    'Beta_standardized_hdi_3%': beta_summary_le['hdi_3%'].values,
    'Beta_standardized_hdi_97%': beta_summary_le['hdi_97%'].values,
    'Importance_mean': importance_samples_le.mean(axis=0),
    'Importance_hdi_3%': np.percentile(importance_samples_le, 3, axis=0),
    'Importance_hdi_97%': np.percentile(importance_samples_le, 97, axis=0),
})

# Format for display
importance_summary_le_formatted = importance_summary_le.copy()
importance_summary_le_formatted['Beta_standardized'] = (
    importance_summary_le['Beta_standardized_mean'].round(3).astype(str) + 
    ' [' + importance_summary_le['Beta_standardized_hdi_3%'].round(3).astype(str) + 
    ', ' + importance_summary_le['Beta_standardized_hdi_97%'].round(3).astype(str) + ']'
)
importance_summary_le_formatted['Importance'] = (
    importance_summary_le['Importance_mean'].round(3).astype(str) + 
    ' [' + importance_summary_le['Importance_hdi_3%'].round(3).astype(str) + 
    ', ' + importance_summary_le['Importance_hdi_97%'].round(3).astype(str) + ']'
)

# Select columns for output table and sort by importance
importance_table_le = importance_summary_le_formatted[[
    'Predictor', 'SD_original', 'Beta_standardized', 'Importance'
]].copy()
importance_table_le = importance_table_le.loc[
    importance_summary_le.sort_values('Importance_mean', ascending=False).index
].reset_index(drop=True)

# Create human-readable version for HTML export
importance_table_le_display = importance_table_le.copy()
importance_table_le_display['Cause'] = importance_table_le_display['Predictor'].map(
    lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)
)
importance_table_le_display = importance_table_le_display[['Cause', 'SD_original', 'Beta_standardized', 'Importance']].rename(
    columns={'SD_original': 'Standard deviation', 'Beta_standardized': 'Coefficient'}
)

print("Importance Measures on Original Scale (Life Expectancy Gap Model):")
print(importance_table_le.to_string(index=False))

# Log for experiments (coefficients and importance)
log_and_print("\n" + "="*80)
log_and_print("LIFE EXPECTANCY GAP MODEL - COEFFICIENTS (β mean ± sd, 94% HDI)")
log_and_print("="*80)
for pred in beta_summary_le.index:
    r = beta_summary_le.loc[pred]
    log_and_print(f"  {pred}: β={r['mean']:.4f} ± {r['sd']:.4f}, 94% HDI [{r['hdi_3%']:.4f}, {r['hdi_97%']:.4f}]")
log_and_print("\nLIFE EXPECTANCY GAP MODEL - IMPORTANCE (ranked)")
log_and_print("-"*80)
for _, row in importance_table_le.iterrows():
    log_and_print(f"  {row['Predictor']}: {row['Importance']}")
log_and_print("="*80)

# Write to HTML (human-readable labels)
write_html_table(importance_table_le_display, get_output_filename('tables/importance_measures_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Plot posterior distributions of beta coefficients (Life Expectancy)
az.plot_forest(trace_le, var_names=["beta"], combined=True, figsize=(10, 12))
plt.title("Posterior Distributions of Predictor Coefficients (Life Expectancy Gap)")
plt.tight_layout()
plt.savefig(get_output_filename('figs/posterior_forest_beta_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS), dpi=300, bbox_inches='tight')
plt.show()
```

```python
# Extract posterior means and credible intervals for alpha coefficients (country intercepts, Life Expectancy)
alpha_summary_le = az.summary(trace_le, var_names=["alpha"])
alpha_summary_le.index = data_le["meta"]["countries"]
alpha_summary_le
```

```python
# Write alpha coefficients table to HTML
alpha_summary_le_formatted = alpha_summary_le.reset_index().rename(columns={'index': 'Country'})
write_html_table(alpha_summary_le_formatted, get_output_filename('tables/alpha_coefficients_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

```python
# Plot posterior distributions of country-specific intercepts (alpha) (Life Expectancy)
az.plot_forest(trace_le, var_names=["alpha"], combined=True, figsize=(8, 12))
plt.title("Posterior Distributions of Country-Specific Intercepts (Life Expectancy Gap)")
plt.tight_layout()
plt.savefig(get_output_filename('figs/posterior_forest_alpha_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS), dpi=300, bbox_inches='tight')
plt.show()
```

### Correlations

#### Top 10 posterior correlations between slope pairs (β), life expectancy

Same definition as HALE: **r** across MCMC draws per pair, ranked by **|r|**.

```python
# Extract posterior samples for beta coefficients (if not already done)
beta_extracted_le = az.extract(trace_le)
beta_samples_df_le = pd.DataFrame(
    beta_extracted_le['beta'].T,
    columns=data_le["meta"]["predictors"]
)

# Compute correlation matrix for beta coefficients
beta_corr_le = beta_samples_df_le.corr()

# Extract upper triangle (excluding diagonal) and convert to long format
beta_corr_triu = np.triu(beta_corr_le.values, k=1)
beta_corr_long = []
for i in range(len(beta_corr_le.index)):
    for j in range(i + 1, len(beta_corr_le.columns)):
        if not np.isnan(beta_corr_triu[i, j]):
            beta_corr_long.append({
                'Predictor1': beta_corr_le.index[i],
                'Predictor2': beta_corr_le.columns[j],
                'Correlation': beta_corr_triu[i, j]
            })

beta_corr_df_le = pd.DataFrame(beta_corr_long)
beta_corr_df_le['Abs_Correlation'] = beta_corr_df_le['Correlation'].abs()
beta_corr_top10_le = beta_corr_df_le.nlargest(10, 'Abs_Correlation')[
    ['Predictor1', 'Predictor2', 'Correlation']
].sort_values('Correlation', key=abs, ascending=False).reset_index(drop=True)

beta_corr_top10_le_display = pd.DataFrame({
    'Rank': range(1, len(beta_corr_top10_le) + 1),
    'Cause 1': beta_corr_top10_le['Predictor1'].map(lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)),
    'Cause 2': beta_corr_top10_le['Predictor2'].map(lambda x: PREDICTOR_DISPLAY_LABELS.get(x, x)),
    'r': beta_corr_top10_le['Correlation'],
})

print('Top 10 β-posterior correlations (LE gender gap), by |r|:')
for _, row in beta_corr_top10_le_display.iterrows():
    print(f"  {row['Rank']:>2}. r={row['r']:+.3f}   {row['Cause 1']}  ↔  {row['Cause 2']}")
beta_corr_top10_le_display
```

```python
# Write beta correlations table to HTML
write_html_table(
    beta_corr_top10_le_display,
    get_output_filename('tables/beta_correlations_top10_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS),
)
```

#### Posterior correlation among selected slopes (β), LE model

Causes chosen so the pair grid includes the **strongest negative** posterior associations among $\beta$ (MCMC draws; standardized predictors) in exploratory runs.

**Heatmap** (correlation coefficients) and **pair plot** (KDE on diagonal, scatters off-diagonal) use the columns below.

```python
from fig_utils import (
    plot_beta_posterior_correlation_heatmap,
    plot_beta_posterior_joint_grid_strongest_negative,
    plot_beta_posterior_pair_scatter,
)

BETA_CORR_SELECTED_COLS_LE = [
    'Gap_Neoplasms',
    'Gap_ChronicRespiratory',
    'Gap_Homicide',
    'Gap_Childhood',
    'Gap_Suicide',
    'Gap_UnintentionalInjury',
    'Gap_RoadTraffic',
    'Gap_Cardiovascular',
]

_missing_sel_le = [c for c in BETA_CORR_SELECTED_COLS_LE if c not in beta_samples_df_le.columns]
if _missing_sel_le:
    raise ValueError(f'β posterior subset (LE): columns not in model: {_missing_sel_le}')

_beta_pair_labels_le = [PREDICTOR_DISPLAY_LABELS.get(c, c) for c in BETA_CORR_SELECTED_COLS_LE]

beta_corr_selected_le = beta_samples_df_le[BETA_CORR_SELECTED_COLS_LE].corr()

fig, _ = plot_beta_posterior_correlation_heatmap(
    beta_corr_selected_le,
    title='Posterior correlation of slope parameters',
    subtitle='Life expectancy gender gap model — selected causes',
    subtext='Pearson r between MCMC draws of β (standardized predictors). Source: OWID LE panel.',
    logo=True,
    display_labels=_beta_pair_labels_le,
)
plt.savefig(
    get_output_filename('figs/beta_posterior_corr_selected_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS),
    dpi=300,
    bbox_inches='tight',
)
plt.show()
```

```python
fig = plot_beta_posterior_pair_scatter(
    beta_samples_df_le,
    BETA_CORR_SELECTED_COLS_LE,
    title='Posterior joint distribution of slope parameters',
    subtitle='Life expectancy gender gap model — selected causes',
    subtext='Each point is one posterior draw. Source: OWID LE panel.',
    display_labels=_beta_pair_labels_le,
    logo=True,
)
plt.savefig(
    get_output_filename('figs/beta_posterior_pair_selected_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS),
    dpi=300,
    bbox_inches='tight',
)
plt.show()
```

Joint distributions for the **nine** predictor pairs with the **most negative** posterior correlation among $\beta$ (full predictor set, not only the selected-cause block). Each panel is a scatter of MCMC draws; label shows Pearson **r** between those draws.

```python
fig, neg_pairs_top9_le = plot_beta_posterior_joint_grid_strongest_negative(
    beta_samples_df_le,
    n_panels=9,
    n_rows=3,
    n_cols=3,
    title='Strongest negative posterior slope associations',
    subtitle='Life expectancy gender gap — most negative pairwise correlations (MCMC draws)',
    subtext='Each panel: joint scatter for one pair of standardized slopes. OWID LE panel.',
    label_map=PREDICTOR_DISPLAY_LABELS,
    logo=True,
    figsize=(8, 8),
)
print('3×3 grid panels (most negative r first):')
for i, (a, b, r) in enumerate(neg_pairs_top9_le, 1):
    la = PREDICTOR_DISPLAY_LABELS.get(a, a)
    lb = PREDICTOR_DISPLAY_LABELS.get(b, b)
    print(f'  {i}. r={r:+.3f}  {la}  vs  {lb}')
plt.savefig(
    get_output_filename('figs/beta_posterior_joint_negcorr_3x3_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS),
    dpi=300,
    bbox_inches='tight',
)
plt.show()
```

```python
# Extract posterior samples for alpha coefficients (country intercepts)
alpha_extracted_le = az.extract(trace_le)
alpha_samples_df_le = pd.DataFrame(
    alpha_extracted_le['alpha'].T,
    columns=data_le["meta"]["countries"]
)

# Compute correlation matrix for alpha coefficients
alpha_corr_le = alpha_samples_df_le.corr()

# Extract upper triangle (excluding diagonal) and convert to long format
alpha_corr_triu = np.triu(alpha_corr_le.values, k=1)
alpha_corr_long = []
for i in range(len(alpha_corr_le.index)):
    for j in range(i + 1, len(alpha_corr_le.columns)):
        if not np.isnan(alpha_corr_triu[i, j]):
            alpha_corr_long.append({
                'Country1': alpha_corr_le.index[i],
                'Country2': alpha_corr_le.columns[j],
                'Correlation': alpha_corr_triu[i, j]
            })

alpha_corr_df_le = pd.DataFrame(alpha_corr_long)
alpha_corr_df_le['Abs_Correlation'] = alpha_corr_df_le['Correlation'].abs()
alpha_corr_top10_le = alpha_corr_df_le.nlargest(10, 'Abs_Correlation')[
    ['Country1', 'Country2', 'Correlation']
].sort_values('Correlation', key=abs, ascending=False)

print("Top 10 correlations among alpha coefficients (country intercepts, Life Expectancy):")
alpha_corr_top10_le
```

```python
# Write alpha correlations table to HTML
write_html_table(alpha_corr_top10_le, get_output_filename('tables/alpha_correlations_top10_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

## Model Evaluation: Posterior Predictive Checks, WAIC, and LOO-CV

### Helper Functions for Model Evaluation

```python
def generate_posterior_predictive_samples(model, trace):
    """
    Generate posterior predictive samples from a PyMC model.
    
    Parameters
    ----------
    model : pymc.Model
        PyMC model object
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
        
    Returns
    -------
    ppc : arviz.InferenceData
        InferenceData object with posterior predictive samples
    """
    with model:
        ppc = pm.sample_posterior_predictive(trace, extend_inferencedata=True)
    return ppc


def extract_ppc_data(ppc, y_obs):
    """
    Extract and reshape posterior predictive data.
    
    Parameters
    ----------
    ppc : arviz.InferenceData
        InferenceData object with posterior predictive samples
    y_obs : array-like
        Observed data
        
    Returns
    -------
    y_ppc_flat : ndarray
        Flattened posterior predictive samples (chains * draws, obs)
    """
    y_ppc = ppc.posterior_predictive["y_obs"].values
    # Reshape: (chains, draws, obs) -> (chains * draws, obs)
    y_ppc_flat = y_ppc.reshape(-1, y_ppc.shape[-1])
    return y_ppc_flat


def plot_ppc_distributions(ppc, y_obs, y_ppc_flat, title, xlabel, output_filename):
    """
    Plot posterior predictive check: distribution comparison and Q-Q plot.
    
    Parameters
    ----------
    ppc : arviz.InferenceData
        InferenceData object with posterior predictive samples
    y_obs : array-like
        Observed data
    y_ppc_flat : ndarray
        Flattened posterior predictive samples
    title : str
        Title prefix for plots
    xlabel : str
        X-axis label
    output_filename : str
        Filename to save the figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Overlay of observed vs posterior predictive distributions
    ax = axes[0]
    az.plot_ppc(ppc, ax=ax, num_pp_samples=100)
    ax.set_title(f"Posterior Predictive Check: Distribution Comparison ({title})")
    ax.set_xlabel(xlabel)
    
    # Plot 2: Q-Q plot comparing observed vs posterior predictive quantiles
    ax = axes[1]
    # Compute quantiles for observed data and all posterior predictive samples (pooled)
    qs = np.linspace(0, 100, 100)
    obs_quantiles = np.percentile(y_obs, qs)
    # Pool all posterior predictive draws and compute quantiles
    ppc_quantiles = np.percentile(y_ppc_flat.ravel(), qs)
    ax.scatter(obs_quantiles, ppc_quantiles, alpha=0.6, color=AIBM_COLORS['crimson'])
    # Add diagonal line
    min_val = min(obs_quantiles.min(), ppc_quantiles.min())
    max_val = max(obs_quantiles.max(), ppc_quantiles.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect fit')
    ax.set_xlabel("Observed Quantiles")
    ax.set_ylabel("Posterior Predictive Quantiles")
    ax.set_title(f"Q-Q Plot: Observed vs Posterior Predictive ({title})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    # Update output filename with suffix
    output_filename_suffixed = get_output_filename(output_filename, MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
    plt.savefig(output_filename_suffixed, dpi=300, bbox_inches='tight')
    plt.show()


def plot_ppc_test_statistics(y_obs, y_ppc_flat, output_filename):
    """
    Plot posterior predictive check: test statistics comparison.
    
    Parameters
    ----------
    y_obs : array-like
        Observed data
    y_ppc_flat : ndarray
        Flattened posterior predictive samples
    output_filename : str
        Filename to save the figure
    """
    # Compute test statistics
    obs_mean = y_obs.mean()
    ppc_mean = y_ppc_flat.mean(axis=1)
    
    obs_std = y_obs.std()
    ppc_std = y_ppc_flat.std(axis=1)
    
    obs_min = y_obs.min()
    ppc_min = y_ppc_flat.min(axis=1)
    
    obs_max = y_obs.max()
    ppc_max = y_ppc_flat.max(axis=1)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    test_stats = [
        ("Mean", obs_mean, ppc_mean),
        ("Standard Deviation", obs_std, ppc_std),
        ("Minimum", obs_min, ppc_min),
        ("Maximum", obs_max, ppc_max),
    ]
    
    for i, (name, obs_val, ppc_vals) in enumerate(test_stats):
        ax = axes[i]
        ax.hist(ppc_vals, bins=50, alpha=0.7, color=AIBM_COLORS['blue'], label='Posterior Predictive')
        ax.axvline(obs_val, color=AIBM_COLORS['crimson'], linewidth=2, linestyle='--', 
                   label=f'Observed: {obs_val:.3f}')
        # Compute p-value (proportion of ppc values more extreme than observed)
        p_value = np.mean(np.abs(ppc_vals - ppc_vals.mean()) >= np.abs(obs_val - ppc_vals.mean()))
        ax.set_xlabel(name)
        ax.set_ylabel('Density')
        ax.set_title(f'{name} Test Statistic\n(p-value: {p_value:.3f})')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    # Update output filename with suffix
    output_filename_suffixed = get_output_filename(output_filename, MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
    plt.savefig(output_filename_suffixed, dpi=300, bbox_inches='tight')
    plt.show()


def compute_model_metrics(model, trace, model_name):
    """
    Compute WAIC and LOO-CV metrics for a model.
    
    Parameters
    ----------
    model : pymc.Model
        PyMC model object
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
    model_name : str
        Name of the model (for printing)
        
    Returns
    -------
    waic : arviz.Waic
        WAIC object
    loo : arviz.Loo
        LOO object
    """
    with model:
        waic = az.waic(trace, pointwise=True)  # elpd_waic
        loo = az.loo(trace, pointwise=True)    # elpd_loo
    
    waic_elpd = waic.elpd_waic
    loo_elpd = loo.elpd_loo
    
    print(f"{model_name} - Model Comparison Metrics:")
    print(f"WAIC (ELPD): {waic_elpd:.2f} (SE: {waic.se:.2f})")
    print(f"LOO (ELPD):  {loo_elpd:.2f} (SE: {loo.se:.2f})")
    print(f"\nEffective number of parameters:")
    print(f"  WAIC p_waic: {waic.p_waic:.2f}")
    print(f"  LOO  p_loo:  {loo.p_loo:.2f}")
    
    return waic, loo


def plot_waic_loo(waic, loo, model_name, output_filename):
    """
    Plot WAIC and LOO pointwise contributions.
    
    Parameters
    ----------
    waic : arviz.Waic
        WAIC object
    loo : arviz.Loo
        LOO object
    model_name : str
        Name of the model (for plot titles)
    output_filename : str
        Filename to save the figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # WAIC pointwise
    ax = axes[0]
    ax.scatter(range(len(waic.waic_i)), waic.waic_i, alpha=0.6, color=AIBM_COLORS['crimson'])
    ax.axhline(0, color='k', linestyle='--', linewidth=1)
    ax.set_xlabel("Observation Index")
    ax.set_ylabel("Pointwise WAIC Contribution")
    ax.set_title(f"Pointwise WAIC Contributions ({model_name})")
    ax.grid(True, alpha=0.3)
    
    # LOO pointwise
    ax = axes[1]
    ax.scatter(range(len(loo.loo_i)), loo.loo_i, alpha=0.6, color=AIBM_COLORS['blue'])
    ax.axhline(0, color='k', linestyle='--', linewidth=1)
    ax.set_xlabel("Observation Index")
    ax.set_ylabel("Pointwise LOO Contribution")
    ax.set_title(f"Pointwise LOO Contributions ({model_name})")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    # Update output filename with suffix
    output_filename_suffixed = get_output_filename(output_filename, MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
    plt.savefig(output_filename_suffixed, dpi=300, bbox_inches='tight')
    plt.show()


def check_pareto_k(loo, data, model_name, threshold=0.7):
    """
    Check Pareto k values to identify problematic observations.
    
    Pareto k > 0.7 indicates potentially problematic observations where
    LOO-CV may be unreliable.
    
    Parameters
    ----------
    loo : arviz.Loo
        LOO object
    data : dict
        Data dictionary from prepare_panel_data
    model_name : str
        Name of the model (for printing)
    threshold : float
        Threshold for problematic observations (default: 0.7)
        
    Returns
    -------
    problematic : pandas.DataFrame
        DataFrame with observations having Pareto k > threshold
    """
    pareto_k = loo.pareto_k
    
    # Find problematic observations
    problematic_mask = pareto_k > threshold
    n_problematic = problematic_mask.sum()
    
    print(f"\nPareto k diagnostics ({model_name}):")
    print(f"  Observations with k > {threshold}: {n_problematic} ({100*n_problematic/len(pareto_k):.1f}%)")
    print(f"  Maximum Pareto k: {pareto_k.max():.3f}")
    print(f"  Mean Pareto k: {pareto_k.mean():.3f}")
    print(f"  Median Pareto k: {np.median(pareto_k):.3f}")
    
    if n_problematic > 0:
        problematic_df = pd.DataFrame({
            'Observation': np.where(problematic_mask)[0],
            'Pareto_k': pareto_k[problematic_mask],
            'Country': [data["meta"]["countries"][data["country_idx"][i]] 
                       for i in np.where(problematic_mask)[0]],
            'Year': [data["meta"]["years"][data["year_idx"][i]] 
                    for i in np.where(problematic_mask)[0]]
        })
        problematic_df = problematic_df.sort_values('Pareto_k', ascending=False)
        print(f"\n  Top problematic observations (k > {threshold}):")
        print(problematic_df.head(10).to_string(index=False))
        return problematic_df
    else:
        print(f"  No observations exceed threshold (k > {threshold})")
        return pd.DataFrame()


def identify_influential_observations(loo, data, model_name, output_filename, top_n=10):
    """
    Identify observations with high influence (high |LOO contribution|).
    
    Parameters
    ----------
    loo : arviz.Loo
        LOO object
    data : dict
        Data dictionary from prepare_panel_data
    model_name : str
        Name of the model (for printing)
    output_filename : str
        Filename to save HTML table
    top_n : int
        Number of top influential observations to return (default: 10)
        
    Returns
    -------
    top_influential : pandas.DataFrame
        DataFrame with top influential observations
    """
    loo_i_df = pd.DataFrame({
        'Observation': range(len(loo.loo_i)),
        'LOO_i': loo.loo_i,
        'Abs_LOO_i': np.abs(loo.loo_i),
        'Pareto_k': loo.pareto_k
    })
    
    # Get top N most influential observations
    top_influential = loo_i_df.nlargest(top_n, 'Abs_LOO_i')
    print(f"Top {top_n} most influential observations ({model_name}):")
    print(top_influential)
    
    # Add country and year information
    top_influential['Country'] = [data["meta"]["countries"][data["country_idx"][i]] 
                                  for i in top_influential['Observation']]
    top_influential['Year'] = [data["meta"]["years"][data["year_idx"][i]] 
                              for i in top_influential['Observation']]
    
    # Write to HTML table (update filename with suffix)
    output_filename_suffixed = get_output_filename(output_filename, MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
    write_html_table(
        top_influential[['Country', 'Year', 'LOO_i', 'Pareto_k']].rename(
            columns={'LOO_i': 'LOO Contribution', 'Pareto_k': 'Pareto k'}
        ),
        output_filename_suffixed
    )
    
    return top_influential[['Observation', 'Country', 'Year', 'LOO_i', 'Abs_LOO_i', 'Pareto_k']]
```

### HALE Gap Model Evaluation

#### Posterior Predictive Checks

Posterior predictive checks compare observed data to data simulated from the posterior distribution to assess model fit.

```python
# Generate posterior predictive samples for HALE model
ppc_hale = generate_posterior_predictive_samples(model_hale, trace_hale)
```

```python
# Extract observed and posterior predictive data
y_obs_hale = data_hale["y_centered"]
y_ppc_hale_flat = extract_ppc_data(ppc_hale, y_obs_hale)
```

```python
# Plot posterior predictive check: distribution comparison and Q-Q plot
plot_ppc_distributions(
    ppc_hale, y_obs_hale, y_ppc_hale_flat,
    title="HALE Gap",
    xlabel="HALE Gap (centered, years)",
    output_filename='figs/ppc_hale.png'
)
```

```python
# Posterior predictive check: test statistics
plot_ppc_test_statistics(
    y_obs_hale, y_ppc_hale_flat,
    output_filename='figs/ppc_test_stats_hale.png'
)
```

#### WAIC and LOO-CV

Compute Widely Applicable Information Criterion (WAIC) and Leave-One-Out Cross-Validation (LOO-CV) to assess model fit and compare models.

```python
# Compute WAIC and LOO-CV for HALE model
waic_hale, loo_hale = compute_model_metrics(model_hale, trace_hale, "HALE Gap Model")
```

```python
# Plot WAIC and LOO pointwise contributions
plot_waic_loo(
    waic_hale, loo_hale,
    model_name="HALE Gap",
    output_filename='figs/waic_loo_hale.png'
)
```

```python
# Check Pareto k values for problematic observations
problematic_hale = check_pareto_k(loo_hale, data_hale, model_name="HALE Gap")
```

```python
# Identify observations with high influence (high |LOO contribution|)
top_influential_hale = identify_influential_observations(
    loo_hale, data_hale,
    model_name="HALE Gap",
    output_filename='tables/influential_observations_hale.html'
)
top_influential_hale
```

### Life Expectancy Gap Model Evaluation

#### Posterior Predictive Checks

```python
# Generate posterior predictive samples for Life Expectancy model
ppc_le = generate_posterior_predictive_samples(model_le, trace_le)
```

```python
# Extract observed and posterior predictive data
y_obs_le = data_le["y_centered"]
y_ppc_le_flat = extract_ppc_data(ppc_le, y_obs_le)
```

```python
# Plot posterior predictive check: distribution comparison and Q-Q plot
plot_ppc_distributions(
    ppc_le, y_obs_le, y_ppc_le_flat,
    title="Life Expectancy Gap",
    xlabel="Life Expectancy Gap (centered, years)",
    output_filename='figs/ppc_le.png'
)
```

```python
# Posterior predictive check: test statistics
plot_ppc_test_statistics(
    y_obs_le, y_ppc_le_flat,
    output_filename='figs/ppc_test_stats_le.png'
)
```

#### WAIC and LOO-CV

```python
# Compute WAIC and LOO-CV for Life Expectancy model
waic_le, loo_le = compute_model_metrics(model_le, trace_le, "Life Expectancy Gap Model")
```

```python
# Plot WAIC and LOO pointwise contributions
plot_waic_loo(
    waic_le, loo_le,
    model_name="Life Expectancy Gap",
    output_filename='figs/waic_loo_le.png'
)
```

```python
# Log model comparison metrics
log_and_print("\n" + "="*80)
log_and_print("MODEL COMPARISON METRICS")
log_and_print("="*80)
log_and_print("HALE Gap Model:")
log_and_print(f"  WAIC (ELPD): {waic_hale.elpd_waic:.2f} (SE: {waic_hale.se:.2f})")
log_and_print(f"  LOO (ELPD):  {loo_hale.elpd_loo:.2f} (SE: {loo_hale.se:.2f})")
log_and_print(f"  p_waic: {waic_hale.p_waic:.2f}, p_loo: {loo_hale.p_loo:.2f}")
log_and_print("\nLife Expectancy Gap Model:")
log_and_print(f"  WAIC (ELPD): {waic_le.elpd_waic:.2f} (SE: {waic_le.se:.2f})")
log_and_print(f"  LOO (ELPD):  {loo_le.elpd_loo:.2f} (SE: {loo_le.se:.2f})")
log_and_print(f"  p_waic: {waic_le.p_waic:.2f}, p_loo: {loo_le.p_loo:.2f}")
log_and_print("="*80)
```

```python
# Check Pareto k values for problematic observations
problematic_le = check_pareto_k(loo_le, data_le, model_name="Life Expectancy Gap")
```

```python
# Identify observations with high influence (high |LOO contribution|)
top_influential_le = identify_influential_observations(
    loo_le, data_le,
    model_name="Life Expectancy Gap",
    output_filename='tables/influential_observations_le.html'
)
top_influential_le
```

### Model Comparison Summary

```python
# Create summary table comparing HALE and Life Expectancy models
# Both WAIC and LOO are on ELPD scale
model_comparison = pd.DataFrame({
    'Model': ['HALE Gap', 'Life Expectancy Gap'],
    'WAIC (ELPD)': [waic_hale.elpd_waic, waic_le.elpd_waic],
    'WAIC_SE': [waic_hale.se, waic_le.se],
    'LOO (ELPD)': [loo_hale.elpd_loo, loo_le.elpd_loo],
    'LOO_SE': [loo_hale.se, loo_le.se],
    'p_waic': [waic_hale.p_waic, waic_le.p_waic],
    'p_loo': [loo_hale.p_loo, loo_le.p_loo],
})

print("Model Comparison Summary:")
print(model_comparison.to_string(index=False))

# Log for experiments
log_and_print("\n" + "="*80)
log_and_print("MODEL COMPARISON SUMMARY")
log_and_print("="*80)
log_and_print(model_comparison.to_string(index=False))
log_and_print("="*80)
```

```python
# Write model comparison table to HTML
write_html_table(model_comparison, get_output_filename('tables/model_comparison_metrics.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS))
```

## R² and Residual Analysis

Compute R² (explained variance) and perform residual analysis for comparison with Elastic Net models and diagnostic purposes.

### Helper Functions for R² and Residual Analysis

```python
def compute_predictions_and_residuals(trace, data, include_year_effects=False):
    """
    Compute posterior mean predictions and residuals for all observations.
    
    Parameters
    ----------
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
    data : dict
        Data dictionary with 'X' (standardized), 'y_centered', 'meta', etc.
    include_year_effects : bool
        Whether year effects were included in the model
        
    Returns
    -------
    dict
        Dictionary with predictions, residuals, and metadata
    """
    # Extract posterior samples
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(data['meta']['predictors']))
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(data['meta']['countries']))
    
    # Get data
    X_std = data['X']  # Already standardized
    y_centered = data['y_centered']
    y_mean = data['meta']['y_mean']
    y_original = y_centered + y_mean  # Reconstruct original scale
    country_idx = data['country_idx']
    
    # Get year indices if year effects were included
    if include_year_effects:
        year_idx = data['year_idx']
        gamma_samples = trace.posterior['gamma'].values.reshape(-1, len(data['meta']['years']))
    else:
        year_idx = None
        gamma_samples = None
    
    # Compute predictions for each posterior sample
    n_samples = beta_samples.shape[0]
    n_obs = len(y_centered)
    predictions_centered = np.zeros((n_samples, n_obs))
    
    for i in range(n_samples):
        # Get country-specific intercepts
        alpha_i = alpha_samples[i, country_idx]
        
        # Linear predictor: alpha + X @ beta
        mu_centered = alpha_i + np.dot(X_std, beta_samples[i])
        
        # Add year effects if included
        if include_year_effects:
            gamma_i = gamma_samples[i, year_idx]
            mu_centered = mu_centered + gamma_i
        
        predictions_centered[i] = mu_centered
    
    # Convert to original scale
    predictions_original = predictions_centered + y_mean
    
    # Compute posterior mean predictions
    y_pred_mean = np.mean(predictions_original, axis=0)
    
    # Compute residuals (on original scale)
    residuals = y_original - y_pred_mean
    
    # Compute posterior distribution of R²
    r2_samples = []
    for i in range(n_samples):
        y_pred_i = predictions_original[i]
        ss_res = np.sum((y_original - y_pred_i) ** 2)
        ss_tot = np.sum((y_original - y_mean) ** 2)
        r2_i = 1 - (ss_res / ss_tot)
        r2_samples.append(r2_i)
    
    r2_samples = np.array(r2_samples)
    r2_mean = np.mean(r2_samples)
    r2_hdi = az.hdi(r2_samples, hdi_prob=0.94)
    
    return {
        'y_pred_mean': y_pred_mean,
        'y_pred_samples': predictions_original,
        'residuals': residuals,
        'r2_mean': r2_mean,
        'r2_samples': r2_samples,
        'r2_hdi': r2_hdi,
        'y_original': y_original,
        'y_mean': y_mean,
    }


def plot_residuals_vs_predicted(y_pred, residuals, title, output_filename):
    """
    Plot residuals vs. predicted values.
    
    Parameters
    ----------
    y_pred : array-like
        Predicted values
    residuals : array-like
        Residuals
    title : str
        Plot title
    output_filename : str
        Output filename for saved figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_pred, residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax.set_xlabel('Predicted Value (years)', fontsize=12)
    ax.set_ylabel('Residual (years)', fontsize=12)
    ax.set_title(f'Residuals vs. Predicted Values: {title}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.show()


def plot_residuals_vs_country(residuals, country_idx, countries, years_data, title, output_filename):
    """
    Plot residuals by country for 2019 only.
    
    Parameters
    ----------
    residuals : array-like
        Residuals
    country_idx : array-like
        Country indices for each observation
    countries : array-like
        List of country codes
    years_data : array-like
        Year for each observation
    title : str
        Plot title
    output_filename : str
        Output filename for saved figure
    """
    # Create DataFrame for easier plotting
    df = pd.DataFrame({
        'Country': [countries[i] for i in country_idx],
        'Residual': residuals,
        'Year': years_data
    })
    
    # Filter to 2019 only
    df_2019 = df[df['Year'] == 2019].copy()
    
    # Sort by residual value
    df_2019_sorted = df_2019.sort_values('Residual')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    y_pos = np.arange(len(df_2019_sorted))
    colors = [AIBM_COLORS['crimson'] if x < 0 else AIBM_COLORS['blue'] for x in df_2019_sorted['Residual'].values]
    ax.barh(y_pos, df_2019_sorted['Residual'].values, color=colors, alpha=0.7)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_2019_sorted['Country'].values)
    ax.set_xlabel('Residual (years)', fontsize=12)
    ax.set_title(f'Residuals by Country (2019): {title}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.show()


def plot_residuals_vs_year(residuals, years_data, title, output_filename):
    """
    Plot residuals vs. year.
    
    Parameters
    ----------
    residuals : array-like
        Residuals
    years_data : array-like
        Year for each observation
    title : str
        Plot title
    output_filename : str
        Output filename for saved figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(years_data, residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Residual (years)', fontsize=12)
    ax.set_title(f'Residuals vs. Year: {title}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.show()


def plot_residual_histogram(residuals, title, output_filename):
    """
    Plot histogram of residuals.
    
    Parameters
    ----------
    residuals : array-like
        Residuals
    title : str
        Plot title
    output_filename : str
        Output filename for saved figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(residuals, bins=20, color=AIBM_COLORS['crimson'], edgecolor='white', alpha=0.7)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)
    ax.axvline(x=np.mean(residuals), color='black', linestyle='-', linewidth=2, label=f'Mean: {np.mean(residuals):.3f}')
    ax.set_xlabel('Residual (years)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Distribution of Residuals: {title}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.show()
```

### HALE Gap Model: R² and Residuals

```python
# Compute predictions and residuals for HALE model
results_hale = compute_predictions_and_residuals(
    trace_hale, data_hale, include_year_effects=INCLUDE_YEAR_EFFECTS
)

# Print R² summary
print("HALE Gap Model: R² Summary")
print("="*60)
print(f"R² (mean): {results_hale['r2_mean']:.4f}")
print(f"R² (94% HDI): [{results_hale['r2_hdi'][0]:.4f}, {results_hale['r2_hdi'][1]:.4f}]")
print(f"\nResidual Statistics:")
print(f"  Mean: {np.mean(results_hale['residuals']):.4f} years")
print(f"  Std: {np.std(results_hale['residuals']):.4f} years")
print(f"  Min: {np.min(results_hale['residuals']):.4f} years")
print(f"  Max: {np.max(results_hale['residuals']):.4f} years")
print(f"  MAE: {np.mean(np.abs(results_hale['residuals'])):.4f} years")
```

```python
# Residuals vs. Predicted Values
plot_residuals_vs_predicted(
    results_hale['y_pred_mean'],
    results_hale['residuals'],
    "HALE Gap",
    get_output_filename('figs/residuals_vs_predicted_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residuals vs. Country (2019 only)
# Get year data for each observation
years_data_hale = np.array([data_hale['meta']['years'][i] for i in data_hale['year_idx']])
plot_residuals_vs_country(
    results_hale['residuals'],
    data_hale['country_idx'],
    data_hale['meta']['countries'],
    years_data_hale,
    "HALE Gap",
    get_output_filename('figs/residuals_vs_country_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residuals vs. Year
plot_residuals_vs_year(
    results_hale['residuals'],
    years_data_hale,
    "HALE Gap",
    get_output_filename('figs/residuals_vs_year_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residual Histogram
plot_residual_histogram(
    results_hale['residuals'],
    "HALE Gap",
    get_output_filename('figs/residuals_histogram_hale.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Create residual summary table for HALE
residual_summary_hale = pd.DataFrame({
    'Statistic': ['Mean', 'Std', 'Min', '25%', 'Median', '75%', 'Max', 'MAE'],
    'Value (years)': [
        np.mean(results_hale['residuals']),
        np.std(results_hale['residuals']),
        np.min(results_hale['residuals']),
        np.percentile(results_hale['residuals'], 25),
        np.median(results_hale['residuals']),
        np.percentile(results_hale['residuals'], 75),
        np.max(results_hale['residuals']),
        np.mean(np.abs(results_hale['residuals']))
    ]
})

residual_summary_hale['Value (years)'] = residual_summary_hale['Value (years)'].round(4)
residual_summary_hale
```

```python
# Write residual summary to HTML
write_html_table(
    residual_summary_hale,
    get_output_filename('tables/residual_summary_hale.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

### Life Expectancy Gap Model: R² and Residuals

```python
# Compute predictions and residuals for Life Expectancy model
results_le = compute_predictions_and_residuals(
    trace_le, data_le, include_year_effects=INCLUDE_YEAR_EFFECTS
)

# Print R² summary
print("Life Expectancy Gap Model: R² Summary")
print("="*60)
print(f"R² (mean): {results_le['r2_mean']:.4f}")
print(f"R² (94% HDI): [{results_le['r2_hdi'][0]:.4f}, {results_le['r2_hdi'][1]:.4f}]")
print(f"\nResidual Statistics:")
print(f"  Mean: {np.mean(results_le['residuals']):.4f} years")
print(f"  Std: {np.std(results_le['residuals']):.4f} years")
print(f"  Min: {np.min(results_le['residuals']):.4f} years")
print(f"  Max: {np.max(results_le['residuals']):.4f} years")
print(f"  MAE: {np.mean(np.abs(results_le['residuals'])):.4f} years")
```

```python
# Residuals vs. Predicted Values
plot_residuals_vs_predicted(
    results_le['y_pred_mean'],
    results_le['residuals'],
    "Life Expectancy Gap",
    get_output_filename('figs/residuals_vs_predicted_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residuals vs. Country (2019 only)
# Get year data for each observation
years_data_le = np.array([data_le['meta']['years'][i] for i in data_le['year_idx']])
plot_residuals_vs_country(
    results_le['residuals'],
    data_le['country_idx'],
    data_le['meta']['countries'],
    years_data_le,
    "Life Expectancy Gap",
    get_output_filename('figs/residuals_vs_country_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residuals vs. Year
plot_residuals_vs_year(
    results_le['residuals'],
    years_data_le,
    "Life Expectancy Gap",
    get_output_filename('figs/residuals_vs_year_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Residual Histogram
plot_residual_histogram(
    results_le['residuals'],
    "Life Expectancy Gap",
    get_output_filename('figs/residuals_histogram_le.png', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

```python
# Create residual summary table for Life Expectancy
residual_summary_le = pd.DataFrame({
    'Statistic': ['Mean', 'Std', 'Min', '25%', 'Median', '75%', 'Max', 'MAE'],
    'Value (years)': [
        np.mean(results_le['residuals']),
        np.std(results_le['residuals']),
        np.min(results_le['residuals']),
        np.percentile(results_le['residuals'], 25),
        np.median(results_le['residuals']),
        np.percentile(results_le['residuals'], 75),
        np.max(results_le['residuals']),
        np.mean(np.abs(results_le['residuals']))
    ]
})

residual_summary_le['Value (years)'] = residual_summary_le['Value (years)'].round(4)
residual_summary_le
```

```python
# Write residual summary to HTML
write_html_table(
    residual_summary_le,
    get_output_filename('tables/residual_summary_le.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

### R² Comparison Summary

```python
# Create R² comparison table
r2_comparison = pd.DataFrame({
    'Model': ['HALE Gap', 'Life Expectancy Gap'],
    'R² (mean)': [results_hale['r2_mean'], results_le['r2_mean']],
    'R² (94% HDI lower)': [results_hale['r2_hdi'][0], results_le['r2_hdi'][0]],
    'R² (94% HDI upper)': [results_hale['r2_hdi'][1], results_le['r2_hdi'][1]],
    'MAE (years)': [
        np.mean(np.abs(results_hale['residuals'])),
        np.mean(np.abs(results_le['residuals']))
    ],
    'Residual Std (years)': [
        np.std(results_hale['residuals']),
        np.std(results_le['residuals'])
    ]
})

r2_comparison = r2_comparison.round(4)
print("R² and Residual Summary:")
print("="*60)
print(r2_comparison.to_string(index=False))
```

```python
# Write R² comparison to HTML
write_html_table(
    r2_comparison,
    get_output_filename('tables/r2_comparison.html', MID_PREDICTORS_TO_INCLUDE, INCLUDE_YEAR_EFFECTS)
)
```

## Save Model Results for Counterfactual Analysis

Save all necessary data for counterfactual analysis in a separate notebook:

```python
import json
from pathlib import Path

# Output directory for panels and metadata (``suffix``, ``trace_filename_*``, ``nc_dir`` set before sampling)
output_dir = Path('interim')
```

### Traces (NetCDF on disk)

Posterior draws are written by `load_idata_or_sample` when `FORCE_RUN` is True or the cache file is missing. Do **not** delete `nc/trace_*.nc` here when re-running with cached chains.

```python
print(f"HALE trace: {trace_filename_hale.resolve()}")
print(f"LE trace:   {trace_filename_le.resolve()}")
```

### Save Metadata

```python
# Save metadata for HALE model
meta_hale = {
    'X_mean': data_hale['meta']['X_mean'].tolist(),  # Convert numpy array to list for JSON
    'X_std': data_hale['meta']['X_std'].tolist(),
    'y_mean': float(data_hale['meta']['y_mean']),  # Convert numpy scalar to float
    'countries': data_hale['meta']['countries'].tolist(),
    'years': data_hale['meta']['years'].tolist(),
    'predictors': data_hale['meta']['predictors'],
    'model_config': {
        'hale_data_source': 'IHME',
        'mid_predictors_included': MID_PREDICTORS_TO_INCLUDE,
        'include_year_effects': INCLUDE_YEAR_EFFECTS,
        'countries_excluded': COUNTRIES_TO_EXCLUDE,
        'cutoff_year': CUTOFF_YEAR,
        'include_covid_data': INCLUDE_COVID_DATA,
    }
}

meta_filename_hale = output_dir / f'metadata_hale{suffix}.json'
with open(meta_filename_hale, 'w') as f:
    json.dump(meta_hale, f, indent=2)
print(f"Saved HALE metadata to: {meta_filename_hale}")

# Save metadata for Life Expectancy model
meta_le = {
    'X_mean': data_le['meta']['X_mean'].tolist(),
    'X_std': data_le['meta']['X_std'].tolist(),
    'y_mean': float(data_le['meta']['y_mean']),
    'countries': data_le['meta']['countries'].tolist(),
    'years': data_le['meta']['years'].tolist(),
    'predictors': data_le['meta']['predictors'],
    'model_config': {
        'hale_data_source': 'IHME',
        'mid_predictors_included': MID_PREDICTORS_TO_INCLUDE,
        'include_year_effects': INCLUDE_YEAR_EFFECTS,
        'countries_excluded': COUNTRIES_TO_EXCLUDE,
        'cutoff_year': CUTOFF_YEAR,
        'include_covid_data': INCLUDE_COVID_DATA,
    }
}

meta_filename_le = output_dir / f'metadata_le{suffix}.json'
with open(meta_filename_le, 'w') as f:
    json.dump(meta_le, f, indent=2)
print(f"Saved Life Expectancy metadata to: {meta_filename_le}")
```

### Save Panel Datasets

```python
# Save both panel datasets with all Mid and Gap columns for counterfactual analysis
# These datasets are needed to:
# 1. Look up current values for any country-year
# 2. Reconstruct Male/Female values from Mid and Gap (Male = Mid + Gap/2, Female = Mid - Gap/2)
# 3. Find gap extremes across all country-years

# Save HALE panel (2000-2023)
panel_hale_filename = output_dir / f'panel_hale{suffix}.h5'
panel_hale.to_hdf(panel_hale_filename, key='panel_data', mode='w')
print(f"Saved HALE panel dataset to: {panel_hale_filename}")
print(f"  Shape: {panel_hale.shape}")
print(f"  Years: {panel_hale['Year'].min():.0f}-{panel_hale['Year'].max():.0f}")

# Save LE panel (2000-2021)
panel_le_filename = output_dir / f'panel_le{suffix}.h5'
panel_le.to_hdf(panel_le_filename, key='panel_data', mode='w')
print(f"Saved LE panel dataset to: {panel_le_filename}")
print(f"  Shape: {panel_le.shape}")
print(f"  Years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
```

### Summary

```python
log_and_print("\n" + "="*60)
log_and_print("Summary of Saved Files for Counterfactual Analysis")
log_and_print("="*60)
log_and_print(f"\nOutput directory: {output_dir}")
log_and_print(f"\nFiles saved:")
log_and_print(f"  1. HALE trace (NetCDF): {trace_filename_hale.name}")
log_and_print(f"  2. Life Expectancy trace (NetCDF): {trace_filename_le.name}")
log_and_print(f"  3. HALE metadata (JSON): {meta_filename_hale.name}")
log_and_print(f"  4. Life Expectancy metadata (JSON): {meta_filename_le.name}")
log_and_print(f"  5. HALE panel dataset (HDF5): {panel_hale_filename.name}")
log_and_print(f"  6. LE panel dataset (HDF5): {panel_le_filename.name}")
log_and_print(f"\nNote: Model objects are not saved (PyMC models cannot be pickled).")
log_and_print(f"      The traces and metadata contain all information needed for counterfactual analysis.")
log_and_print(f"\nModel configuration:")
log_and_print(f"  - HALE data source: IHME (GBD 2023)")
log_and_print(f"  - LE data source: OWID (HMD + UN WPP)")
log_and_print(f"  - HALE years: {panel_hale['Year'].min():.0f}-{panel_hale['Year'].max():.0f}")
log_and_print(f"  - LE years: {panel_le['Year'].min():.0f}-{panel_le['Year'].max():.0f}")
log_and_print(f"  - Include COVID data: {INCLUDE_COVID_DATA}")
log_and_print(f"  - Mid predictors included: {MID_PREDICTORS_TO_INCLUDE}")
log_and_print(f"  - Year effects included: {INCLUDE_YEAR_EFFECTS}")
log_and_print(f"  - Countries excluded: {COUNTRIES_TO_EXCLUDE}")
log_and_print(f"\nAll files are ready for counterfactual analysis in bayes_counter.md")
log_and_print("="*60)
log_and_print(f"\nNotebook completed successfully: {pd.Timestamp.now()}")

# Close log file
log_file.close()
print(f"\nLog file saved: {log_path}")
```

## Next Steps

- ✅ Posterior predictive checks
- ✅ WAIC and LOO-CV
- Counterfactual analysis with uncertainty quantification
- Model extensions (year fixed effects, AR(1) structure)



```python
from utils import beep

beep()
```
