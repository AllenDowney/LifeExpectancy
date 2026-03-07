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

# Bayesian Counterfactual Analysis: Life Expectancy Gap

This notebook performs counterfactual analysis for the Life Expectancy gap using the Bayesian panel model results. For each gap predictor, we compute what would happen to a country's predicted Life Expectancy gap if we adjusted that predictor to the best attainable value observed across all country-years.

**Data Source Note**: The 2023 model uses OWID Life Expectancy data (2000-2023), which combines Human Mortality Database and UN World Population Prospects. This extends temporal coverage beyond WHO LE data (2000-2021), matching the IHME HALE temporal range.

## Overview

**Counterfactual Question**: What would happen to a country's Life Expectancy gap if we adjusted a specific gap predictor to the best attainable value (while keeping all other predictors constant)?

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
    write_html_table
)
from counterfactual_utils import (
    compute_importance_summary,
    create_counterfactual_visualizations,
    plot_counterfactual_forest,
    plot_counterfactual_by_type,
    plot_counterfactual_bar,
    format_counterfactual_table,
    compute_gap_extremes,
    counterfactual_predictions_bayesian,
    plot_predicted_vs_actual_over_time,
    compute_positive_contributions_over_time,
    plot_positive_contributions_stacked_area,
    plot_positive_contributions_percentage
)

configure_plot_style()
```

## Load Saved Model Results

```python
# ============================================================================
# MODEL CONFIGURATION: Select which model version to use
# ============================================================================
# Options:
#   '2019_nocovid' - Pre-COVID baseline (2000-2019, no COVID-19 predictor)
#   '2021_covid'   - WHO LE, extended analysis (2000-2021, includes COVID-19 predictor)
#   '2023_covid'   - OWID LE, full COVID period (2000-2023, includes COVID-19 predictor) - RECOMMENDED
#   'legacy'       - Legacy model (older format, if exists)
MODEL_VERSION = '2019_nocovid'  
MODEL_VERSION = '2021_covid'
MODEL_VERSION = '2023_covid'  # New default - uses OWID LE data through 2023

# Map model version to suffix
MODEL_SUFFIX_MAP = {
    '2019_nocovid': '_nomid_nogrw_y2019_nocovid',
    '2021_covid': '_nomid_nogrw_y2021_covid',
    '2023_covid': '_ihme_nomid_nogrw_y2023_covid',  # Note: suffix includes 'ihme' for consistency with HALE model naming
    'legacy': '_nomid_nogrw'  # Older format, may not exist
}

# Get the suffix for the selected model version
MODEL_SUFFIX = MODEL_SUFFIX_MAP.get(MODEL_VERSION, '_ihme_nomid_nogrw_y2023_covid')

print(f"Model Configuration:")
print(f"  Selected version: {MODEL_VERSION}")
print(f"  Model suffix: {MODEL_SUFFIX}")

# Path to saved results
results_dir = Path('interim')
nc_dir = Path('nc')
```

```python
# Load metadata
meta_filename = results_dir / f'metadata_le{MODEL_SUFFIX}.json'
with open(meta_filename, 'r') as f:
    metadata = json.load(f)

print("Metadata loaded:")
print(f"  Countries: {len(metadata['countries'])}")
print(f"  Years: {len(metadata['years'])} (range: {min(metadata['years'])}-{max(metadata['years'])})")
print(f"  Predictors: {len(metadata['predictors'])}")
print(f"  Model config: {metadata['model_config']}")
```

```python
# Load trace (posterior samples)
trace_filename = nc_dir / f'trace_le{MODEL_SUFFIX}.nc'
trace = az.from_netcdf(trace_filename)
print(f"\nTrace loaded from: {trace_filename}")
print(f"Number of chains: {trace.posterior.sizes['chain']}")
print(f"Number of draws per chain: {trace.posterior.sizes['draw']}")
print(f"Total samples: {trace.posterior.sizes['chain'] * trace.posterior.sizes['draw']}")
```

```python
# Load panel dataset
# Note: 2023 model uses separate panel files for HALE and LE (panel_le{suffix}.h5)
#       Older models use combined panel file (panel_dataset{suffix}.h5)
if MODEL_VERSION == '2023_covid':
    panel_filename = results_dir / f'panel_le{MODEL_SUFFIX}.h5'
else:
    panel_filename = results_dir / f'panel_dataset{MODEL_SUFFIX}.h5'

panel_df = pd.read_hdf(panel_filename, key='panel_data')
print(f"\nPanel dataset loaded from: {panel_filename}")
print(f"Shape: {panel_df.shape}")
print(f"Columns: {list(panel_df.columns)[:10]}...")  # Show first 10 columns
```

```python
# Verify data alignment
print("\nData verification:")
print(f"  Panel countries: {panel_df['country'].nunique()}")
print(f"  Metadata countries: {len(metadata['countries'])}")
print(f"  Panel years: {sorted(panel_df['Year'].unique())[:5]}...")  # Show first 5
print(f"  Metadata years: {metadata['years'][:5]}...")  # Show first 5
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

print("Transformation parameters:")
print(f"  X_mean shape: {X_mean.shape}")
print(f"  X_std shape: {X_std.shape}")
print(f"  y_mean: {y_mean:.4f} years")
print(f"  Number of predictors: {len(predictors)}")
```

## Gap Extremes Table

Find the minimum and maximum gap values for each gap predictor across all country-years:

```python
# Compute extremes for each gap predictor using helper function
gap_extremes = compute_gap_extremes(panel_df)

# Display as DataFrame
gap_extremes_df = pd.DataFrame(gap_extremes).T
gap_extremes_df = gap_extremes_df.sort_index()
print(f"Found {len(gap_extremes)} gap predictors")
gap_extremes_df
```

## Counterfactual Prediction Function

The counterfactual prediction function is imported from `counterfactual_utils`. It computes what would happen to a country's predicted gap if we adjusted a specific gap predictor to the best attainable value observed across all country-years.

## Test Counterfactual Function

Test the function with a simple example:

```python
# Test with USA in 2019, Alcohol gap
test_country = 'USA'
test_year = 2019
test_predictor = 'Gap_Alcohol'

result = counterfactual_predictions_bayesian(
    test_country, test_year, test_predictor,
    trace, metadata, panel_df, gap_extremes,
    country_to_idx, year_to_idx
)

print(f"Counterfactual Analysis: {code_to_who_country.get(test_country, test_country)} ({test_country}) in {test_year}")
print(f"Indicator: {result['indicator']}")
print(f"\nCurrent {result['indicator']} gap (predictor): {result['current_gap']:.3f}")
print(f"Note: This is the gap for the {result['indicator']} predictor, not the Life Expectancy gap itself")
if result['target_country']:
    print(f"Target gap: {result['target_gap']:.3f} (from {code_to_who_country.get(result['target_country'], result['target_country'])} in {result['target_year']})")
else:
    print(f"Target gap: {result['target_gap']:.3f} (set to zero)")
print(f"\nPredicted Life Expectancy gap (original, before counterfactual):")
print(f"  Mean: {result['original_summary']['mean']:.3f} years")
print(f"  94% HDI: [{result['original_summary']['hdi_3%']:.3f}, {result['original_summary']['hdi_97%']:.3f}]")
print(f"\nPredicted Life Expectancy gap (counterfactual, after adjustment):")
print(f"  Mean: {result['counterfactual_summary']['mean']:.3f} years")
print(f"  94% HDI: [{result['counterfactual_summary']['hdi_3%']:.3f}, {result['counterfactual_summary']['hdi_97%']:.3f}]")
print(f"\nChange in Life Expectancy gap:")
print(f"  Mean: {result['change_summary']['mean']:.3f} years")
print(f"  94% HDI: [{result['change_summary']['hdi_3%']:.3f}, {result['change_summary']['hdi_97%']:.3f}]")
```

## Spot Check: Actual vs Predicted Life Expectancy Gap for USA (2019)

Verify that the predicted Life Expectancy gap matches expectations and compare with the actual value:

```python
# Get actual Life Expectancy gap for USA in 2019
usa_2019_mask = (panel_df['country'] == 'USA') & (panel_df['Year'] == 2019)
if usa_2019_mask.any():
    actual_le_gap = panel_df[usa_2019_mask]['LE_gap'].iloc[0]
    print(f"Actual Life Expectancy gap for USA (2019): {actual_le_gap:.3f} years")
else:
    print("Warning: No data found for USA in 2019")
    actual_le_gap = None

# Compute predicted Life Expectancy gap using the same method as counterfactual function
# Get current country-year row
current_row = panel_df[usa_2019_mask].iloc[0]

# Get transformation parameters
X_mean = np.array(metadata['X_mean'])
X_std = np.array(metadata['X_std'])
y_mean = metadata['y_mean']
predictors = metadata['predictors']
countries = np.array(metadata['countries'])

# Get country index
country_idx_val = country_to_idx['USA']

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

print(f"\nPredicted Life Expectancy gap for USA (2019):")
print(f"  Mean: {pred_mean:.3f} years")
print(f"  94% HDI: [{pred_hdi[0]:.3f}, {pred_hdi[1]:.3f}]")

if actual_le_gap is not None:
    residual = actual_le_gap - pred_mean
    print(f"\nResidual (Actual - Predicted): {residual:.3f} years")
    print(f"  This should match the residual from the residual analysis section")
    print(f"  (within rounding error)")
    
# Also verify this matches the counterfactual function's original prediction
# (using the test result from above)
print(f"\n" + "="*60)
print("Verification: Compare with counterfactual function output")
print("="*60)
print(f"Counterfactual function 'original_prediction' mean: {result['original_summary']['mean']:.3f} years")
print(f"Spot check computed prediction mean: {pred_mean:.3f} years")
print(f"Difference: {abs(result['original_summary']['mean'] - pred_mean):.6f} years")
print(f"  (Should be < 0.001, i.e., essentially identical)")
```

## Compute Importance Measures

Load or compute importance measures to sort counterfactuals by importance:

```python
# Compute importance summary using helper function
importance_summary = compute_importance_summary(trace, metadata)
importance_summary
```

## Counterfactual Analysis for All Predictors: United States

Generate counterfactual predictions for all gap predictors for USA using the latest available year:

```python
# Determine latest available year for USA
usa_data = panel_df[panel_df['country'] == 'USA'].copy()
latest_year = max(usa_data['Year'].unique())
print(f"Using {latest_year} as the reference year for counterfactual analysis")

# Generate counterfactual results for all predictors
gap_predictors = [col for col in panel_df.columns if col.startswith('Gap_')]
counterfactual_results = []

for gap_pred in gap_predictors:
    try:
        result = counterfactual_predictions_bayesian(
            'USA', latest_year, gap_pred,
            trace, metadata, panel_df, gap_extremes,
            country_to_idx, year_to_idx
        )
        counterfactual_results.append(result)
    except (KeyError, ValueError) as e:
        print(f"Warning: Skipping {gap_pred}: {e}")
        continue

# Format into table using helper function
counterfactuals, counterfactuals_full = format_counterfactual_table(
    counterfactual_results, importance_summary, code_to_who_country, target_name='Life Expectancy gap'
)

print(f"Counterfactual Analysis: United States (USA) in {latest_year}")
print("="*80)
print(f"\nNumber of indicators analyzed: {len(counterfactuals)}")
print(f"\nResults (sorted by importance):")
counterfactuals
```

```python
# Write counterfactual table to HTML
output_filename = f'tables/counterfactuals_usa_{latest_year}_le_bayesian.html'
write_html_table(counterfactuals, output_filename)
print(f"Saved counterfactual table to: {output_filename}")
```

```python
# Forest Plot: All Indicators
plot_counterfactual_forest(
    counterfactual_results,
    output_prefix=f'counterfactual_effects_usa_{latest_year}_le',
    target_name='Life Expectancy gap'
)
```

```python
# Two-Panel Plot: Gap-Closing vs Gap-Widening
plot_counterfactual_by_type(
    counterfactual_results,
    output_prefix=f'counterfactual_effects_usa_{latest_year}_le',
    target_name='Life Expectancy gap'
)
```

```python
# Bar Chart: Sorted by Magnitude
plot_counterfactual_bar(
    counterfactual_results,
    output_prefix=f'counterfactual_effects_usa_{latest_year}_le',
    target_name='Life Expectancy gap'
)
```

## Aggregate Effects

Compute aggregate effects (sum of gap-closing and gap-widening indicators) using the same counterfactual results:

```python
# Use the same counterfactual_results to ensure consistency with plots
# Separate gap-closing (negative change) and gap-widening (positive change) indicators
gap_closing = counterfactuals_full[counterfactuals_full['Change mean'] < 0].copy()
gap_widening = counterfactuals_full[counterfactuals_full['Change mean'] > 0].copy()

print("Gap-Closing Indicators (negative change = reduces Life Expectancy gap):")
print(f"  Number of indicators: {len(gap_closing)}")
if len(gap_closing) > 0:
    total_closing = gap_closing['Change mean'].sum()
    print(f"  Total effect (sum of means): {total_closing:.3f} years")
    print(f"  Indicators: {', '.join(gap_closing['Indicator'].tolist())}")

print(f"\nGap-Widening Indicators (positive change = increases Life Expectancy gap):")
print(f"  Number of indicators: {len(gap_widening)}")
if len(gap_widening) > 0:
    total_widening = gap_widening['Change mean'].sum()
    print(f"  Total effect (sum of means): {total_widening:.3f} years")
    print(f"  Indicators: {', '.join(gap_widening['Indicator'].tolist())}")

# Compute net effect
net_effect = counterfactuals_full['Change mean'].sum()
print(f"\nNet Effect (all indicators combined): {net_effect:.3f} years")
print(f"\nNote: These are point estimates (means). For uncertainty quantification,")
print(f"      we would need to compute the posterior distribution of the sum.")
```

```python
# Verify that the sum of predictor contributions equals the predicted gap
# Get USA data for latest year
usa_latest = panel_df[(panel_df['country'] == 'USA') & (panel_df['Year'] == latest_year)].iloc[0]

# Get transformation parameters
X_mean = np.array(metadata['X_mean'])
X_std = np.array(metadata['X_std'])
y_mean = metadata['y_mean']
predictors = metadata['predictors']
countries = np.array(metadata['countries'])

# Get country index
country_idx_val = country_to_idx['USA']

# Build predictor vector (standardized)
X_current = np.array([usa_latest[p] for p in predictors])
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

print(f"\nVerification: Sum of Predictor Contributions")
print(f"="*60)
print(f"Predicted gap: {predicted_gap:.6f} years")
print(f"Country intercept (α_i): {alpha_i_mean:.6f} years")
print(f"Global mean (y_mean): {y_mean:.6f} years")
print(f"Sum of predictor contributions (X*β): {sum_predictor_contributions:.6f} years")
print(f"Expected sum (predicted - α_i - y_mean): {expected_sum:.6f} years")
print(f"Difference: {abs(sum_predictor_contributions - expected_sum):.6f} years")
print(f"\n✓ Verification: Sum of contributions matches predicted gap structure")
print(f"  (within numerical precision)")
```

```python
# Verify the relationship between counterfactual effects and predicted gap
# If all gaps were zero (in original scale), we need to properly standardize them
# When gap = 0 in original scale, standardized value = (0 - X_mean) / X_std = -X_mean / X_std

# Build predictor vector with all gaps set to zero (in original scale)
X_all_zero = usa_latest[predictors].copy()
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

print(f"\nVerification: Counterfactual Effects vs Predicted Gap")
print(f"="*60)
print(f"Current predicted gap: {predicted_gap:.6f} years")
print(f"Predicted gap if all gaps were zero: {predicted_if_all_zero:.6f} years")
print(f"Expected if all standardized predictors zero (α_i + y_mean): {expected_if_all_zero:.6f} years")
print(f"Difference (current - all gaps zero): {difference_current_vs_zero:.6f} years")
print(f"Sum of predictor contributions (X*β): {sum_predictor_contributions:.6f} years")
print(f"Sum of counterfactual effects (from counterfactual analysis): {sum_counterfactual_effects:.6f} years")
print(f"Expected sum of counterfactual effects (computed from standardization): {expected_counterfactual_sum:.6f} years")
print(f"\nNote: Counterfactual effects account for Mid adjustments when gaps are set to zero,")
print(f"      which may cause differences from the simple standardization calculation.")
```

## Predicted vs Actual Life Expectancy Gap Over Time: United States

Plot the predicted vs actual Life Expectancy gap over time for the United States to visualize model fit:

```python
# Plot predicted vs actual Life Expectancy gap for USA over time
plot_predicted_vs_actual_over_time(
    country='USA',
    trace=trace,
    metadata=metadata,
    panel_df=panel_df,
    country_to_idx=country_to_idx,
    target_name='Life Expectancy gap',
    target_col='LE_gap',
    output_filename='figs/predicted_vs_actual_le_usa.png',
    subtext='Source: Bayesian hierarchical panel model. IHME cause-specific mortality, OWID Life Expectancy.',
    logo=True
)
```

## Positive-Contributing Factors Over Time: United States

Create a stacked area chart showing the contribution of each gap-closing factor over time for the USA, along with predicted and actual totals. This analysis excludes COVID-19 from gap-closing factors since it widens the gap.

```python
# Compute positive contributions over time
# Reference year will be automatically set to the latest available year
# Use the pre-computed counterfactuals_full to ensure exact consistency with aggregate effects
contributions_df = compute_positive_contributions_over_time(
    country='USA',
    trace=trace,
    metadata=metadata,
    panel_df=panel_df,
    gap_extremes=gap_extremes,
    country_to_idx=country_to_idx,
    year_to_idx=year_to_idx,
    target_name='Life Expectancy gap',
    target_col='LE_gap',
    counterfactuals_full=counterfactuals_full
)

contributions_df.head()
```

```python
# Write contributions dataframe to HTML table
output_filename = 'tables/positive_contributions_usa_le_over_time.html'
write_html_table(contributions_df, output_filename)
print(f"Saved contributions table to: {output_filename}")
```

```python
# Create stacked area chart
plot_positive_contributions_stacked_area(
    contributions_df,
    target_name='Life Expectancy gap',
    country='USA',
    output_filename='figs/positive_contributions_stacked_area_usa_le.png'
)
```

```python
# Plot total positive contributions as percentage of actual gap over time
plot_positive_contributions_percentage(
    contributions_df,
    target_name='Life Expectancy gap',
    country='USA',
    output_filename='figs/positive_contributions_percentage_usa_le.png'
)
```

