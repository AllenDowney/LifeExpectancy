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

# Bayesian Counterfactual Analysis: HALE Gap

This notebook performs counterfactual analysis for the HALE gap using the Bayesian panel model results. For each gap predictor, we compute what would happen to a country's predicted HALE gap if we adjusted that predictor to the best attainable value observed across all country-years.

**Data Source Note**: Recommended run uses IHME HALE (2000–2023), aligned in time with the LE pipeline (IHME causes; LE outcome uses OWID).

## Overview

**Counterfactual Question**: What would happen to a country's HALE gap if we adjusted a specific gap predictor to the best attainable value (while keeping all other predictors constant)?

**Key Features**:
- Uses posterior distributions (not just point estimates) to quantify uncertainty
- Accounts for country-specific intercepts (α_i) when making predictions
- Provides credible intervals (94% HDI) for all counterfactual predictions

```python
%load_ext autoreload
%autoreload 2
```

```python
import numpy as np
import pandas as pd
import arviz as az
import matplotlib.pyplot as plt
from pathlib import Path
import json

from utils import (
    decorate, configure_plot_style, AIBM_COLORS,
    code_to_who_country, codes_to_country_names,
    write_html_table,
    log_and_print, set_log_file
)
from fig_utils import PREDICTOR_LABELS
from counterfactual_utils import (
    compute_importance_summary,
    plot_counterfactual_forest,
    plot_country_intercepts,
    format_counterfactual_table,
    compute_gap_extremes,
    counterfactual_predictions_bayesian,
    plot_predicted_vs_actual_over_time,
    compute_positive_contributions_over_time,
    plot_positive_contributions_stacked_area,
    plot_positive_contributions_percentage,
    publish_datawrapper_table,
)

configure_plot_style()
```

## Load Saved Model Results

```python tags=["parameters"]
# ============================================================================
# MODEL CONFIGURATION: Override with papermill (run from notebooks/).
#   jupytext --to ipynb bayes_counter_hale.md --output bayes_counter_hale.ipynb
#   papermill bayes_counter_hale.ipynb bayes_counter_hale_<CC>.ipynb \
#     -p COUNTRY_CODE USA -p MODEL_VERSION 2023_ihme -p UPLOAD_TO_DATAWRAPPER False
# Papermill executes the notebook and writes the output to the second path (see plan.md).
# ============================================================================
# Options:
#   '2019_nocovid' - Pre-COVID baseline (2000-2019, WHO HALE, no COVID predictor)
#   '2021_covid'   - WHO HALE (2000-2021, includes COVID-19 predictor)
#   '2023_ihme'    - IHME HALE (2000-2023, includes COVID-19) — RECOMMENDED
MODEL_VERSION = '2023_ihme'

# Country for counterfactual analysis (ISO 3-letter code: USA, LTU, NLD, etc.)
COUNTRY_CODE = 'USA'

# If True, upload blog tables to Datawrapper (requires DATAWRAPPER_API_TOKEN; pip install datawrapper).
# See datawrapper.md. Default False so CI and papermill runs do not call the API.
UPLOAD_TO_DATAWRAPPER = False

# Map model version to suffix
MODEL_SUFFIX_MAP = {
    '2019_nocovid': '_nomid_nogrw_y2019_nocovid',
    '2021_covid': '_nomid_nogrw_y2021_covid',
    '2023_ihme': '_ihme_nomid_nogrw_y2023_covid',  # IHME HALE through 2023
    'legacy': '_nomid_nogrw'  # Older format, may not exist
}

# Get the suffix for the selected model version
MODEL_SUFFIX = MODEL_SUFFIX_MAP.get(MODEL_VERSION, '_ihme_nomid_nogrw_y2023_covid')

# Setup logging
import os
os.makedirs('logs', exist_ok=True)
log_path = f'logs/bayes_counter_hale_{MODEL_VERSION}_{COUNTRY_CODE.lower()}.txt'
log_file = open(log_path, 'w')
log_file.write("Bayesian Counterfactual Analysis: HALE Gap\n")
log_file.write("=" * 80 + "\n")
log_file.write(f"Model version: {MODEL_VERSION}\n")
log_file.write(f"Country: {COUNTRY_CODE}\n")
log_file.write(f"Started: {pd.Timestamp.now()}\n")
log_file.write("=" * 80 + "\n\n")
set_log_file(log_file)
log_and_print(f"Model Configuration:")
log_and_print(f"  Selected version: {MODEL_VERSION}")
log_and_print(f"  Model suffix: {MODEL_SUFFIX}")
log_and_print(f"  Country: {COUNTRY_CODE} ({code_to_who_country.get(COUNTRY_CODE, COUNTRY_CODE)})")
log_and_print(f"  Logging to: {log_path}")

# Path to saved results
results_dir = Path('interim')
nc_dir = Path('nc')
```

```python
# Load metadata
meta_filename = results_dir / f'metadata_hale{MODEL_SUFFIX}.json'
with open(meta_filename, 'r') as f:
    metadata = json.load(f)

log_and_print("Metadata loaded:")
log_and_print(f"  Countries: {len(metadata['countries'])}")
log_and_print(f"  Years: {len(metadata['years'])} (range: {min(metadata['years'])}-{max(metadata['years'])})")
log_and_print(f"  Predictors: {len(metadata['predictors'])}")
log_and_print(f"  Model config: {metadata['model_config']}")
```

```python
# Load trace (posterior samples)
trace_filename = nc_dir / f'trace_hale{MODEL_SUFFIX}.nc'
trace = az.from_netcdf(trace_filename)
log_and_print(f"\nTrace loaded from: {trace_filename}")
log_and_print(f"Number of chains: {trace.posterior.sizes['chain']}")
log_and_print(f"Number of draws per chain: {trace.posterior.sizes['draw']}")
log_and_print(f"Total samples: {trace.posterior.sizes['chain'] * trace.posterior.sizes['draw']}")
```

```python
# Load panel dataset
# Note: IHME 2023 HALE uses panel_hale{suffix}.h5; older runs may use combined panel_dataset
if MODEL_VERSION == '2023_ihme':
    panel_filename = results_dir / f'panel_hale{MODEL_SUFFIX}.h5'
else:
    panel_filename = results_dir / f'panel_dataset{MODEL_SUFFIX}.h5'

panel_df = pd.read_hdf(panel_filename, key='panel_data')
log_and_print(f"\nPanel dataset loaded from: {panel_filename}")
log_and_print(f"Shape: {panel_df.shape}")
log_and_print(f"Columns: {list(panel_df.columns)[:10]}...")  # Show first 10 columns
```

```python
# Verify data alignment
log_and_print("\nData verification:")
log_and_print(f"  Panel countries: {panel_df['country'].nunique()}")
log_and_print(f"  Metadata countries: {len(metadata['countries'])}")
log_and_print(f"  Panel years: {sorted(panel_df['Year'].unique())[:5]}...")  # Show first 5
log_and_print(f"  Metadata years: {metadata['years'][:5]}...")  # Show first 5
```

## Extract Transformation Parameters

```python
# Extract standardization parameters (convert back to numpy arrays)
X_mean = np.array(metadata['X_mean'])
X_std = np.array(metadata['X_std'])
y_mean = metadata['y_mean']

# Extract predictor names and country/year mappings
predictors = metadata['predictors']
countries = np.array(metadata['countries'])
years = np.array(metadata['years'])

# Create indexers for country and year
country_to_idx = {c: i for i, c in enumerate(countries)}
year_to_idx = {y: i for i, y in enumerate(years)}

log_and_print("Transformation parameters:")
log_and_print(f"  X_mean shape: {X_mean.shape}")
log_and_print(f"  X_std shape: {X_std.shape}")
log_and_print(f"  y_mean: {y_mean:.4f} years")
log_and_print(f"  Number of predictors: {len(predictors)}")
```

## Gap Extremes Table

Find the minimum and maximum gap values for each gap predictor across all country-years:

```python
# Compute extremes for each gap predictor using helper function
gap_extremes = compute_gap_extremes(panel_df)

# Display as DataFrame
gap_extremes_df = pd.DataFrame(gap_extremes).T
gap_extremes_df = gap_extremes_df.sort_index()
log_and_print(f"Found {len(gap_extremes)} gap predictors")
gap_extremes_df
```

### Presentation Version for Blog

Minimums only, with country names and human-readable cause labels:

```python
# Build presentation table: minimums only, country names, human-readable labels
# Exclude MaternalDisorders and ConflictTerrorism (not in model)
model_gap_predictors = [p for p in metadata['predictors'] if p.startswith('Gap_')]
gap_extremes_model = {k: v for k, v in gap_extremes.items() if k in model_gap_predictors}
gap_extremes_presentation = []
for gap_pred, ext in gap_extremes_model.items():
    cause_label = PREDICTOR_LABELS.get(gap_pred, gap_pred.replace('Gap_', '').replace('_', ' '))
    country_name = code_to_who_country.get(ext['min_country'], ext['min_country'])
    gap_extremes_presentation.append({
        'Cause': cause_label,
        'Minimum gap': round(ext['min_gap'], 2),
        'Country': country_name,
        'Year': str(int(ext['min_year']))  # string to avoid scientific notation in HTML
    })

gap_extremes_blog_df = pd.DataFrame(gap_extremes_presentation).sort_values('Minimum gap',
                                                                           ascending=False)
gap_extremes_blog_df = gap_extremes_blog_df.reset_index(drop=True)
write_html_table(gap_extremes_blog_df, 'tables/gap_extremes_min_blog_hale.html')
log_and_print(f"Saved presentation table to: tables/gap_extremes_min_blog_hale.html")

if UPLOAD_TO_DATAWRAPPER:
    if not os.getenv('DATAWRAPPER_API_TOKEN'):
        log_and_print('[Datawrapper] Skipping gap extremes: DATAWRAPPER_API_TOKEN not set')
    else:
        dw_info = publish_datawrapper_table(
            gap_extremes_blog_df,
            title='',
            intro=(
                'Minimum cause-specific death rate gaps (male minus female) by country-year, '
                'training sample. IHME cause-specific mortality, IHME HALE.'
            ),
        )
        log_and_print(f"[Datawrapper] Gap extremes — publish: {dw_info['public_url']}")
        log_and_print(f"[Datawrapper] Gap extremes — edit: {dw_info['edit_url']}")

gap_extremes_blog_df
```

## Counterfactual Prediction Function

The counterfactual prediction function is imported from `counterfactual_utils`. It computes what would happen to a country's predicted gap if we adjusted a specific gap predictor to the best attainable value observed across all country-years.

## Test Counterfactual Function

Test the function with a simple example:

```python
# Test with selected country and year, Alcohol gap
test_country = COUNTRY_CODE
test_year = 2019
test_predictor = 'Gap_Alcohol'

result = counterfactual_predictions_bayesian(
    test_country, test_year, test_predictor,
    trace, metadata, panel_df, gap_extremes,
    country_to_idx, year_to_idx
)

log_and_print(f"Counterfactual Analysis: {code_to_who_country.get(test_country, test_country)} ({test_country}) in {test_year}")
log_and_print(f"Indicator: {result['indicator']}")
log_and_print(f"\nCurrent {result['indicator']} gap (predictor): {result['current_gap']:.3f}")
log_and_print(f"Note: This is the gap for the {result['indicator']} predictor, not the HALE gap itself")
if result['target_country']:
    log_and_print(f"Target gap: {result['target_gap']:.3f} (from {code_to_who_country.get(result['target_country'], result['target_country'])} in {result['target_year']})")
else:
    log_and_print(f"Target gap: {result['target_gap']:.3f} (set to zero)")
log_and_print(f"\nPredicted HALE gap (original, before counterfactual):")
log_and_print(f"  Mean: {result['original_summary']['mean']:.3f} years")
log_and_print(f"  94% HDI: [{result['original_summary']['hdi_3%']:.3f}, {result['original_summary']['hdi_97%']:.3f}]")
log_and_print(f"\nPredicted HALE gap (counterfactual, after adjustment):")
log_and_print(f"  Mean: {result['counterfactual_summary']['mean']:.3f} years")
log_and_print(f"  94% HDI: [{result['counterfactual_summary']['hdi_3%']:.3f}, {result['counterfactual_summary']['hdi_97%']:.3f}]")
log_and_print(f"\nChange in HALE gap:")
log_and_print(f"  Mean: {result['change_summary']['mean']:.3f} years")
log_and_print(f"  94% HDI: [{result['change_summary']['hdi_3%']:.3f}, {result['change_summary']['hdi_97%']:.3f}]")
```

## Spot Check: Actual vs Predicted HALE Gap

Verify that the predicted HALE gap matches expectations and compare with the actual value:

```python
# Get actual HALE gap for selected country in test year
test_mask = (panel_df['country'] == COUNTRY_CODE) & (panel_df['Year'] == test_year)
if test_mask.any():
    actual_hale_gap = panel_df[test_mask]['HALE_gap'].iloc[0]
    log_and_print(f"Actual HALE gap for {code_to_who_country.get(COUNTRY_CODE, COUNTRY_CODE)} ({COUNTRY_CODE}) in {test_year}: {actual_hale_gap:.3f} years")
else:
    log_and_print(f"Warning: No data found for {COUNTRY_CODE} in {test_year}")
    actual_hale_gap = None

# Compute predicted HALE gap using the same method as counterfactual function
# Get current country-year row
current_row = panel_df[test_mask].iloc[0]

# Get transformation parameters
X_mean = np.array(metadata['X_mean'])
X_std = np.array(metadata['X_std'])
y_mean = metadata['y_mean']
predictors = metadata['predictors']
countries = np.array(metadata['countries'])

# Get country index
country_idx_val = country_to_idx[COUNTRY_CODE]

# Build predictor vector (standardized)
X_current = np.array([current_row[p] for p in predictors])
X_current_std = (X_current - X_mean) / X_std

# Extract posterior samples
beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))

# Compute predictions for each posterior sample
alpha_i_samples = alpha_samples[:, country_idx_val]
pred_centered = alpha_i_samples + np.dot(X_current_std, beta_samples.T)
pred_original = pred_centered + y_mean

# Compute summary
pred_mean = np.mean(pred_original)
pred_hdi = az.hdi(pred_original, hdi_prob=0.94)

log_and_print(f"\nPredicted HALE gap for {code_to_who_country.get(COUNTRY_CODE, COUNTRY_CODE)} ({COUNTRY_CODE}) in {test_year}:")
log_and_print(f"  Mean: {pred_mean:.3f} years")
log_and_print(f"  94% HDI: [{pred_hdi[0]:.3f}, {pred_hdi[1]:.3f}]")

if actual_hale_gap is not None:
    residual = actual_hale_gap - pred_mean
    log_and_print(f"\nResidual (Actual - Predicted): {residual:.3f} years")
    log_and_print(f"  This should match the residual from the residual analysis section")
    log_and_print(f"  (within rounding error)")
    
# Also verify this matches the counterfactual function's original prediction
# (using the test result from above)
log_and_print(f"\n" + "="*60)
log_and_print("Verification: Compare with counterfactual function output")
log_and_print("="*60)
log_and_print(f"Counterfactual function 'original_prediction' mean: {result['original_summary']['mean']:.3f} years")
log_and_print(f"Spot check computed prediction mean: {pred_mean:.3f} years")
log_and_print(f"Difference: {abs(result['original_summary']['mean'] - pred_mean):.6f} years")
log_and_print(f"  (Should be < 0.001, i.e., essentially identical)")
```

## Compute Importance Measures

Load or compute importance measures to sort counterfactuals by importance:

```python
# Compute importance summary using helper function
importance_summary = compute_importance_summary(trace, metadata)
importance_summary
```

## Counterfactual Analysis for All Predictors

Generate counterfactual predictions for all gap predictors for the selected country using the latest available year:

```python
# Determine latest available year for selected country
country_data = panel_df[panel_df['country'] == COUNTRY_CODE].copy()
latest_year = max(country_data['Year'].unique())
country_name = code_to_who_country.get(COUNTRY_CODE, COUNTRY_CODE)
country_lower = COUNTRY_CODE.lower()
log_and_print(f"Using {latest_year} as the reference year for counterfactual analysis")

# Generate counterfactual results for all predictors
gap_predictors = [col for col in panel_df.columns if col.startswith('Gap_')]
counterfactual_results = []

for gap_pred in gap_predictors:
    try:
        result = counterfactual_predictions_bayesian(
            COUNTRY_CODE, latest_year, gap_pred,
            trace, metadata, panel_df, gap_extremes,
            country_to_idx, year_to_idx
        )
        counterfactual_results.append(result)
    except (KeyError, ValueError) as e:
        log_and_print(f"Warning: Skipping {gap_pred}: {e}")
        continue

# Format into table using helper function
counterfactuals, counterfactuals_full = format_counterfactual_table(
    counterfactual_results, importance_summary, code_to_who_country, target_name='HALE gap'
)

log_and_print(f"Counterfactual Analysis: {country_name} ({COUNTRY_CODE}) in {latest_year}")
log_and_print("="*80)
log_and_print(f"\nNumber of indicators analyzed: {len(counterfactuals)}")
log_and_print(f"\nResults (sorted by importance):")
counterfactuals
```

```python
# Write counterfactual table to HTML
output_filename = f'tables/counterfactuals_{country_lower}_{latest_year}_hale_bayesian.html'
write_html_table(counterfactuals, output_filename)
log_and_print(f"Saved counterfactual table to: {output_filename}")
```

### Presentation Version for Blog

Death rate gap (not Indicator), human-readable labels, no index, last column shows mean only (no error bounds):

```python
# Build presentation table from counterfactuals_full
change_col = 'Change in HALE gap (years)'
counterfactuals_presentation = counterfactuals_full[
    ['Indicator', 'Current gap', 'Target gap', 'Target Country-Year', 'Change mean']
].copy()
# Rename columns for blog
counterfactuals_presentation = counterfactuals_presentation.rename(columns={
    'Indicator': 'Cause',
    'Change mean': change_col
})
# Sort by change (ascending: largest gap-closing first, then gap-widening)
counterfactuals_presentation = counterfactuals_presentation.sort_values(change_col)
# Apply human-readable labels to Death rate gap column
counterfactuals_presentation['Cause'] = counterfactuals_presentation['Cause'].apply(
    lambda x: PREDICTOR_LABELS.get(f'Gap_{x}', x)
)
# Numeric copy for Datawrapper (string cells are typed as text and skip number formats)
counterfactuals_for_datawrapper = counterfactuals_presentation.copy()
# Format change as mean only (2 decimal places) for HTML / blog table
counterfactuals_presentation[change_col] = counterfactuals_presentation[change_col].apply(
    lambda x: f'{x:.2f}'
)
# Reset index to remove integer index (when written to HTML, index=False in write_html_table handles this)
counterfactuals_blog_filename = f'tables/counterfactuals_{country_lower}_{latest_year}_hale_blog.html'
write_html_table(counterfactuals_presentation.reset_index(drop=True), counterfactuals_blog_filename)
log_and_print(f"Saved presentation table to: {counterfactuals_blog_filename}")

# Upload presentation table for whichever country this run uses (see datawrapper.md for token).
if UPLOAD_TO_DATAWRAPPER:
    if not os.getenv('DATAWRAPPER_API_TOKEN'):
        log_and_print('[Datawrapper] Skipping counterfactuals blog table: DATAWRAPPER_API_TOKEN not set')
    else:
        dw_info = publish_datawrapper_table(
            counterfactuals_for_datawrapper.reset_index(drop=True),
            title='',
            intro=(
                f'{country_name} ({COUNTRY_CODE}) {latest_year}: counterfactual effect on predicted '
                f'healthy life expectancy gender gap if each cause matched the best observed country-year gap. '
                f'Bayesian hierarchical model; IHME HALE and causes.'
            ),
            column_number_formats={'Change in HALE gap (years)': '0.00'},
        )
        log_and_print(f"[Datawrapper] Counterfactuals blog — publish: {dw_info['public_url']}")
        log_and_print(f"[Datawrapper] Counterfactuals blog — edit: {dw_info['edit_url']}")

counterfactuals_presentation
```

```python
# Forest Plot: All Indicators
plot_counterfactual_forest(
    counterfactual_results,
    output_prefix=f'counterfactual_effects_{country_lower}_{latest_year}_hale',
    target_name='HALE gap',
    country=COUNTRY_CODE,
    year=latest_year,
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
```

```python
# Country Intercepts Forest Plot
plot_country_intercepts(
    trace,
    metadata,
    target_name='HALE gap',
    output_prefix=f'country_intercepts_hale',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
```


## Aggregate Effects

Compute aggregate effects (sum of gap-closing and gap-widening indicators) using the same counterfactual results:

```python
# Use the same counterfactual_results to ensure consistency with plots
# Separate gap-closing (negative change) and gap-widening (positive change) indicators
gap_closing = counterfactuals_full[counterfactuals_full['Change mean'] < 0].copy()
gap_widening = counterfactuals_full[counterfactuals_full['Change mean'] > 0].copy()

log_and_print("Gap-Closing Indicators (negative change = reduces HALE gap):")
log_and_print(f"  Number of indicators: {len(gap_closing)}")
if len(gap_closing) > 0:
    total_closing = gap_closing['Change mean'].sum()
    log_and_print(f"  Total effect (sum of means): {total_closing:.3f} years")
    log_and_print(f"  Indicators: {', '.join(gap_closing['Indicator'].tolist())}")

log_and_print(f"\nGap-Widening Indicators (positive change = increases HALE gap):")
log_and_print(f"  Number of indicators: {len(gap_widening)}")
if len(gap_widening) > 0:
    total_widening = gap_widening['Change mean'].sum()
    log_and_print(f"  Total effect (sum of means): {total_widening:.3f} years")
    log_and_print(f"  Indicators: {', '.join(gap_widening['Indicator'].tolist())}")

# Compute net effect
net_effect = counterfactuals_full['Change mean'].sum()
log_and_print(f"\nNet Effect (all indicators combined): {net_effect:.3f} years")
log_and_print(f"\nNote: These are point estimates (means). For uncertainty quantification,")
log_and_print(f"      we would need to compute the posterior distribution of the sum.")

# Predicted gap for summary (from counterfactual results)
predicted_gap = counterfactual_results[0]['original_summary']['mean'] if counterfactual_results else None

# Top gap-closing factor (largest effect)
if len(gap_closing) > 0:
    top_row = gap_closing.loc[gap_closing['Change mean'].idxmin()]
    top_factor = top_row['Indicator']
    top_effect = float(top_row['Change mean'])
    top_factor_label = PREDICTOR_LABELS.get(f'Gap_{top_factor}', top_factor)
else:
    top_factor = top_factor_label = None
    top_effect = None

total_gap_reducing = abs(total_closing) if len(gap_closing) > 0 else 0.0
pct_of_gap = 100 * total_gap_reducing / predicted_gap if predicted_gap and predicted_gap > 0 else None

# Update country summary JSON (add or replace this country)
summary_path = Path('tables/country_summary_hale.json')
if summary_path.exists():
    with open(summary_path) as f:
        summary = json.load(f)
else:
    summary = {}
summary[COUNTRY_CODE] = {
    'country_name': country_name,
    'current_gap': round(predicted_gap, 3) if predicted_gap is not None else None,
    'top_factor': top_factor,
    'top_factor_label': top_factor_label,
    'top_effect': round(top_effect, 3) if top_effect is not None else None,
    'total_gap_reducing': round(total_gap_reducing, 3),
    'pct_of_gap': round(pct_of_gap, 1) if pct_of_gap is not None else None,
    'total_gap_widening': round(gap_widening['Change mean'].sum(), 3) if len(gap_widening) > 0 else 0.0,
    'net_effect': round(net_effect, 3),
    'n_gap_closing': len(gap_closing),
    'n_gap_widening': len(gap_widening),
    'latest_year': int(latest_year),
}
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
log_and_print(f"\nUpdated country summary: {summary_path}")
```

```python
# Verify that the sum of predictor contributions equals the predicted gap
# Get selected country data for latest year
country_latest = panel_df[(panel_df['country'] == COUNTRY_CODE) & (panel_df['Year'] == latest_year)].iloc[0]

# Get transformation parameters
X_mean = np.array(metadata['X_mean'])
X_std = np.array(metadata['X_std'])
y_mean = metadata['y_mean']
predictors = metadata['predictors']
countries = np.array(metadata['countries'])

# Get country index
country_idx_val = country_to_idx[COUNTRY_CODE]

# Build predictor vector (standardized)
X_current = np.array([country_latest[p] for p in predictors])
X_current_std = (X_current - X_mean) / X_std

# Extract posterior samples
beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))
alpha_i_samples = alpha_samples[:, country_idx_val]

# Compute predicted gap
pred_centered = alpha_i_samples + np.dot(X_current_std, beta_samples.T)
pred_original = pred_centered + y_mean
predicted_gap = np.mean(pred_original)
alpha_i_mean = np.mean(alpha_i_samples)

# Compute individual predictor contributions: X_j * β_j for each predictor
beta_mean = np.mean(beta_samples, axis=0)
predictor_contributions = X_current_std * beta_mean
predictor_contributions_dict = dict(zip(predictors, predictor_contributions))

# Sum of all predictor contributions
sum_predictor_contributions = np.sum(predictor_contributions)

# Verify: predicted_gap = α_i + sum(X*β) + y_mean
# So: sum(X*β) = predicted_gap - α_i - y_mean
expected_sum = predicted_gap - alpha_i_mean - y_mean

log_and_print(f"\nVerification: Sum of Predictor Contributions")
log_and_print(f"="*60)
log_and_print(f"Predicted gap: {predicted_gap:.6f} years")
log_and_print(f"Country intercept (α_i): {alpha_i_mean:.6f} years")
log_and_print(f"Global mean (y_mean): {y_mean:.6f} years")
log_and_print(f"Sum of predictor contributions (X*β): {sum_predictor_contributions:.6f} years")
log_and_print(f"Expected sum (predicted - α_i - y_mean): {expected_sum:.6f} years")
log_and_print(f"Difference: {abs(sum_predictor_contributions - expected_sum):.6f} years")
log_and_print(f"\n✓ Verification: Sum of contributions matches predicted gap structure")
log_and_print(f"  (within numerical precision)")
```

```python
# Verify the relationship between counterfactual effects and predicted gap
# If all gaps were zero (in original scale), we need to properly standardize them
# When gap = 0 in original scale, standardized value = (0 - X_mean) / X_std = -X_mean / X_std

# Build predictor vector with all gaps set to zero (in original scale)
X_all_zero = country_latest[predictors].copy()
# Set all gap predictors to zero
for pred in predictors:
    if pred.startswith('Gap_'):
        X_all_zero[pred] = 0.0
    # Note: Mid predictors are adjusted when gaps are set to zero, but for this
    # verification we'll keep them as-is to see the effect of just the gaps

# Standardize the "all gaps zero" predictors
X_all_zero_array = np.array([X_all_zero[p] for p in predictors])
X_all_zero_std = (X_all_zero_array - X_mean) / X_std

# Compute prediction if all gaps were zero
pred_zero_centered = alpha_i_samples + np.dot(X_all_zero_std, beta_samples.T)
pred_zero_original = pred_zero_centered + y_mean
predicted_if_all_zero = np.mean(pred_zero_original)

# This should equal α_i + y_mean only if all standardized predictors are zero
# But since setting gaps to zero doesn't make standardized predictors zero, they won't match exactly
expected_if_all_zero = alpha_i_mean + y_mean

# The difference between current prediction and "all gaps zero" prediction
difference_current_vs_zero = predicted_gap - predicted_if_all_zero

# Sum of all counterfactual effects (from counterfactual_results)
# Each counterfactual effect is: change when setting that gap to zero
sum_counterfactual_effects = net_effect  # This is the sum from counterfactuals_full

# Also compute what the sum should be based on individual contributions
# When we set gap_j to zero, the standardized value changes from X_j_std to -X_mean_j / X_std_j
# So the change in contribution is: (-X_mean_j / X_std_j - X_j_std) * β_j
gap_predictors_only = [p for p in predictors if p.startswith('Gap_')]
gap_indices = [predictors.index(p) for p in gap_predictors_only]
expected_counterfactual_sum = 0.0
for gap_idx in gap_indices:
    gap_pred = predictors[gap_idx]
    # Current standardized value
    X_j_std_current = X_current_std[gap_idx]
    # Standardized value if gap = 0
    X_j_std_zero = (0.0 - X_mean[gap_idx]) / X_std[gap_idx]
    # Change in contribution
    change = (X_j_std_zero - X_j_std_current) * beta_mean[gap_idx]
    expected_counterfactual_sum += change

log_and_print(f"\nVerification: Counterfactual Effects vs Predicted Gap")
log_and_print(f"="*60)
log_and_print(f"Current predicted gap: {predicted_gap:.6f} years")
log_and_print(f"Predicted gap if all gaps were zero: {predicted_if_all_zero:.6f} years")
log_and_print(f"Expected if all standardized predictors zero (α_i + y_mean): {expected_if_all_zero:.6f} years")
log_and_print(f"Difference (current - all gaps zero): {difference_current_vs_zero:.6f} years")
log_and_print(f"Sum of predictor contributions (X*β): {sum_predictor_contributions:.6f} years")
log_and_print(f"Sum of counterfactual effects (from counterfactual analysis): {sum_counterfactual_effects:.6f} years")
log_and_print(f"Expected sum of counterfactual effects (computed from standardization): {expected_counterfactual_sum:.6f} years")
log_and_print(f"\nNote: Counterfactual effects account for Mid adjustments when gaps are set to zero,")
log_and_print(f"      which may cause differences from the simple standardization calculation.")
```

## Predicted vs Actual HALE Gap Over Time

Plot the predicted vs actual HALE gap over time to visualize model fit:

```python
# Plot predicted vs actual HALE gap over time
plot_predicted_vs_actual_over_time(
    country=COUNTRY_CODE,
    trace=trace,
    metadata=metadata,
    panel_df=panel_df,
    country_to_idx=country_to_idx,
    target_name='HALE gap',
    target_col='HALE_gap',
    output_filename=f'figs/predicted_vs_actual_hale_{country_lower}.png',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
```

## Positive-Contributing Factors Over Time

Create a stacked area chart showing the contribution of each gap-closing factor over time, along with predicted and actual totals. This analysis excludes COVID-19 from gap-closing factors since it widens the gap.

```python
# Compute positive contributions over time
# Reference year will be automatically set to the latest available year
# Use the pre-computed counterfactuals_full to ensure exact consistency with aggregate effects
contributions_df = compute_positive_contributions_over_time(
    country=COUNTRY_CODE,
    trace=trace,
    metadata=metadata,
    panel_df=panel_df,
    gap_extremes=gap_extremes,
    country_to_idx=country_to_idx,
    year_to_idx=year_to_idx,
    target_name='HALE gap',
    target_col='HALE_gap',
    counterfactuals_full=counterfactuals_full
)

contributions_df.head()
```

```python
# Total contribution of gap-closing factors: compare contributions_df vs aggregate effects
# Both use best attainable (consistent); contributions_df recomputes per year for the time series
gap_closing_cols = [c for c in contributions_df.columns if c not in ['Predicted Total', 'Actual Total']]
contrib_total_latest = contributions_df[gap_closing_cols].iloc[-1].sum()  # Latest year
latest_contrib_year = contributions_df.index[-1]

log_and_print(f"\nTotal gap-closing contribution (contributions_df, {latest_contrib_year}): {contrib_total_latest:.3f} years")
log_and_print(f"  Sum of columns: {', '.join(gap_closing_cols)}")
log_and_print(f"\nAggregate effects (counterfactuals_full, best attainable, {latest_year}): {abs(total_closing):.3f} years")
log_and_print(f"  Difference: {contrib_total_latest - abs(total_closing):.3f} years")
log_and_print(f"\nBoth use best attainable from gap_extremes; small differences may arise from year alignment.")

# Factor-by-factor comparison (contributions_df vs counterfactuals_full)
log_and_print(f"\nFactor-by-factor comparison ({latest_contrib_year}):")
for ind in gap_closing_cols:
    contrib_val = contributions_df[ind].iloc[-1]
    cf_row = gap_closing[gap_closing['Indicator'] == ind]
    cf_val = abs(cf_row['Change mean'].iloc[0]) if len(cf_row) > 0 else np.nan
    diff = contrib_val - cf_val if not np.isnan(cf_val) else np.nan
    log_and_print(f"  {ind}: contrib={contrib_val:.3f}, counterfactual={cf_val:.3f}, diff={diff:.3f}")
```

```python
# For this country: factor whose potential contribution increased/decreased most (2000 vs 2023)
year_start, year_end = 2000, 2023
factor_cols = [c for c in contributions_df.columns if c not in ['Predicted Total', 'Actual Total']]
y_start = year_start if year_start in contributions_df.index else contributions_df.index.min()
y_end = year_end if year_end in contributions_df.index else contributions_df.index.max()
get_label = lambda f: PREDICTOR_LABELS.get(f'Gap_{f}', f.replace('_', ' '))

if y_start != y_end:
    contrib_s = contributions_df.loc[y_start, factor_cols]
    contrib_e = contributions_df.loc[y_end, factor_cols]
    changes = contrib_e - contrib_s
    idx_max = changes.idxmax()
    idx_min = changes.idxmin()
    change_row = {
        'Country': country_name,
        'Largest increase': get_label(idx_max),
        'Increase (yr)': round(changes[idx_max], 3),
        'Largest decrease': get_label(idx_min),
        'Decrease (yr)': round(changes[idx_min], 3),
        'Years': f'{int(y_start)}–{int(y_end)}'
    }
    # Update shared JSON (each papermill run adds/updates this country)
    change_path = Path('tables/contribution_changes_2000_2023_hale.json')
    if change_path.exists():
        with open(change_path) as f:
            change_data = json.load(f)
    else:
        change_data = {}
    change_data[COUNTRY_CODE] = change_row
    with open(change_path, 'w') as f:
        json.dump(change_data, f, indent=2)
    change_df = pd.DataFrame(change_data.values())
    write_html_table(change_df, 'tables/contribution_changes_2000_2023_hale.html')
    log_and_print(f"Updated contribution changes: {change_path}")
    change_row
else:
    log_and_print(f"Skipped contribution change (single year: {y_start})")
```

```python
# Write contributions dataframe to HTML table
output_filename = f'tables/positive_contributions_{country_lower}_hale_over_time.html'
write_html_table(contributions_df, output_filename)
log_and_print(f"Saved contributions table to: {output_filename}")
```

```python
# Create stacked area chart
plot_positive_contributions_stacked_area(
    contributions_df,
    target_name='HALE gap',
    country=COUNTRY_CODE,
    output_filename=f'figs/positive_contributions_stacked_area_{country_lower}_hale.png',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
```

```python
# Plot total positive contributions as percentage of actual gap over time
plot_positive_contributions_percentage(
    contributions_df,
    target_name='HALE gap',
    country=COUNTRY_CODE,
    output_filename=f'figs/positive_contributions_percentage_{country_lower}_hale.png',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, IHME HALE.',
    logo=True
)
```

