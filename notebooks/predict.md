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

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import decorate, underride, configure_plot_style, AIBM_COLORS, code_to_who_country, code_to_wef_country

configure_plot_style()
```

## Step 1: Load Data

```python
# Code to read the saved data back from HDF5 file
hdf_file = '../data/hale_analysis_data.h5'

# Read data back
with pd.HDFStore(hdf_file, mode='r') as store:
    predictors_original = store['predictors']
    target = store['target']
```

## Step 2: Prepare Predictors (Male + Gap Reparameterization)

```python
# Transform predictors from Male/Female format to Male/Gap format
# This reparameterization provides better interpretability:
# - Male coefficient: effect of overall level
# - Gap coefficient: direct effect of gender gap (Male - Female)
# This makes it easier to answer: "What happens if we close the gap?"

predictors = predictors_original.copy()

# Extract all indicator names
all_indicators = set()
for col in predictors.columns:
    if col.endswith('_Male') or col.endswith('_Female'):
        indicator_name = col.rsplit('_', 1)[0]
        all_indicators.add(indicator_name)

# Exclude maternal mortality (female-only) from transformation
male_female_indicators = [name for name in sorted(all_indicators) 
                          if name != 'MaternalMortalityRatio']

# Transform each indicator: keep Male, create Gap = Male - Female, drop Female
for indicator in male_female_indicators:
    male_col = f'{indicator}_Male'
    female_col = f'{indicator}_Female'
    gap_col = f'{indicator}_Gap'
    
    if male_col in predictors.columns and female_col in predictors.columns:
        # Create gap column (Male - Female)
        predictors[gap_col] = predictors[male_col] - predictors[female_col]
        # Drop female column
        predictors = predictors.drop(columns=[female_col])

print(f"Reparameterized predictors: {len(male_female_indicators)} indicators transformed")
print(f"Original columns: {len(predictors_original.columns)}")
print(f"New columns: {len(predictors.columns)}")
print(f"\nSample of new column names:")
print([col for col in predictors.columns if '_Gap' in col][:5])
```

## Step 3: Train Elastic Net Model

```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn import set_config

# Configure sklearn to output pandas DataFrames to preserve feature names
set_config(transform_output="pandas")

# Prepare data: X (predictors) and y (target)
# Use the reparameterized predictors (Male + Gap format)
X = predictors.copy()
y = target.copy()

# Display data shape
pd.DataFrame({
    'Data': ['Predictors (X)', 'Target (y)'],
    'Shape': [X.shape, y.shape],
    'Countries': [X.shape[0], y.shape[0]]
})
```

```python
# Set up cross-validation (5-fold for small sample size)
cv = KFold(n_splits=5, shuffle=True, random_state=42)

# Display CV setup
f"Using {cv.n_splits}-fold cross-validation for model selection"
```

```python
# Define parameter grid for Elastic Net
elastic_net_params = {
    'elasticnet__alpha': np.logspace(-3, 1, 20),
    'elasticnet__l1_ratio': np.linspace(0.1, 0.9, 9)  # 0=Ridge, 1=Lasso
}

# Create pipeline with StandardScaler and Elastic Net model
elastic_net_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('elasticnet', ElasticNet(max_iter=10000))
])
```

```python
# Fit Elastic Net with cross-validation
print("Fitting Elastic Net...")
elastic_net_grid = GridSearchCV(elastic_net_pipeline, elastic_net_params, cv=cv,
                                 scoring='r2', n_jobs=-1, verbose=1)
elastic_net_grid.fit(X, y)

elastic_net_best_score = elastic_net_grid.best_score_
elastic_net_best_params = elastic_net_grid.best_params_
elastic_net_best_model = elastic_net_grid.best_estimator_

pd.DataFrame({
    'Model': ['Elastic Net'],
    'Best_CV_R2': [elastic_net_best_score],
    'Best_Alpha': [elastic_net_best_params['elasticnet__alpha']],
    'Best_L1_Ratio': [elastic_net_best_params['elasticnet__l1_ratio']]
})
```

```python
# Store the trained model and data for counterfactual analysis
# The model is now ready for predictions
print(f"Elastic Net model trained successfully!")
print(f"Cross-validation R²: {elastic_net_best_score:.4f}")
print(f"Model ready for counterfactual predictions")
```

## Step 3.5: Create ZRO Country (Zero Gap Reference)

```python
# Create a reference country "ZRO" with zero gaps and mean level values
# This represents perfect gender equality (0 gap) with average levels
# We'll use this as the "best case" for counterfactuals when actual minimum gaps are negative

zro_data = X.copy().iloc[0:0].copy()  # Empty DataFrame with same columns

# Set gap variables to 0
for col in X.columns:
    if col.endswith('_Gap'):
        zro_data.loc['ZRO', col] = 0.0
    else:
        # For level variables (Male), use the mean
        zro_data.loc['ZRO', col] = X[col].mean()

# Add ZRO to X
X_with_zro = pd.concat([X, zro_data], axis=0)

print(f"Created ZRO country with:")
print(f"  - {len([c for c in X.columns if c.endswith('_Gap')])} gap variables set to 0")
print(f"  - {len([c for c in X.columns if not c.endswith('_Gap')])} level variables set to mean")
print(f"X shape: {X.shape} -> X_with_zro shape: {X_with_zro.shape}")

# Update X to include ZRO for counterfactual analysis
X = X_with_zro
```

## Step 4: Gap Predictor Analysis Table

```python
# Identify all gap predictors (columns ending with '_Gap')
gap_predictors = [col for col in X.columns if col.endswith('_Gap')]
print(f"Found {len(gap_predictors)} gap predictors")
```

```python
# Create a function to convert country codes to names
def get_country_name(country_code):
    """Convert country code to readable name, trying multiple sources"""
    # Try WHO country mapping first
    name = code_to_who_country.get(country_code, None)
    if name:
        return name
    # Try WEF country mapping
    name = code_to_wef_country.get(country_code, None)
    if name:
        return name
    # If not found, return the code itself
    return country_code
```

```python
# For each gap predictor, find country with lowest and highest gap value
gap_analysis = []

for gap_col in gap_predictors:
    # Get non-null values for this gap predictor, excluding ZRO from min/max calculations
    gap_data = X[gap_col].dropna()
    gap_data_real = gap_data[gap_data.index != 'ZRO'] if 'ZRO' in gap_data.index else gap_data
    
    if len(gap_data_real) > 0:
        # Find country with lowest gap (best case - smallest gap) among real countries
        min_idx = gap_data_real.idxmin()
        min_value = gap_data_real.min()
        
        # If minimum is negative, use ZRO (0) as the best case instead
        if min_value < 0:
            min_country_code = 'ZRO'
            min_country_name = 'ZRO (Zero Gap)'
            min_value = 0.0
        else:
            min_country_code = min_idx
            min_country_name = get_country_name(min_idx)
        
        # Find country with highest gap (worst case - largest gap) among real countries
        max_idx = gap_data_real.idxmax()
        max_country_code = max_idx
        max_country_name = get_country_name(max_idx)
        max_value = gap_data_real.max()
        
        gap_analysis.append({
            'Gap_Predictor': gap_col,
            'Lowest_Gap_Country': min_country_name,
            'Lowest_Gap_Country_Code': min_country_code,
            'Lowest_Gap_Value': min_value,
            'Highest_Gap_Country': max_country_name,
            'Highest_Gap_Country_Code': max_country_code,
            'Highest_Gap_Value': max_value,
            'Range': max_value - min_value,
            'N_Countries': len(gap_data_real)
        })

# Create DataFrame
gap_analysis_df = pd.DataFrame(gap_analysis)

# Sort by predictor name for easier reading
gap_analysis_df = gap_analysis_df.sort_values('Gap_Predictor').reset_index(drop=True)

gap_analysis_df
```

### Gap Predictor Impact Analysis

The Elastic Net model coefficients are on a standardized scale (because predictors are standardized before fitting). To interpret the impact of each gap predictor:

- **Coefficient**: Years of HALE gap per standard deviation of the predictor (standardized scale)
- **Coefficient / Std_Dev**: Converts to original scale → years of HALE gap per unit of the original predictor (e.g., per 100,000 for death rates)
- **Coefficient × Range / Std_Dev** (or equivalently **Coefficient_per_Unit × Range**): Total effect in years of HALE gap when moving from the minimum (best case) to maximum (worst case) value of the predictor. This converts the range to standardized units (range/std_dev) then multiplies by the coefficient.

This allows us to compare the potential impact of closing each gap from worst to best across all countries.

```python
# Create table with coefficient, standard deviation, and range information for gap predictors
# Get coefficients from Elastic Net model (on standardized scale)
elastic_net_coefs = elastic_net_best_model.named_steps['elasticnet'].coef_
coef_dict = dict(zip(X.columns, elastic_net_coefs))

# Get the scaler from the pipeline to use its scale factors
scaler = elastic_net_best_model.named_steps['scaler']
scaler_scale = scaler.scale_  # This is the standard deviation used for scaling

# Calculate standard deviations for each gap predictor using scaler scale
gap_predictor_stats = []
for predictor in gap_predictors:
    if predictor in X.columns:
        coef = coef_dict[predictor]
        median_val = X[predictor].median()
        # Use standard deviation from scaler (this is what was used for standardization)
        predictor_idx = X.columns.get_loc(predictor)
        std_dev = scaler_scale[predictor_idx]
        coef_per_unit = coef / std_dev
        
        # Get range from gap_analysis_df
        if predictor in gap_analysis_df['Gap_Predictor'].values:
            row = gap_analysis_df[gap_analysis_df['Gap_Predictor'] == predictor].iloc[0]
            range_val = row['Range']
        else:
            range_val = X[predictor].max() - X[predictor].min()
        
        # Total effect of moving from min to max
        # Range in standardized units = range / std_dev
        # Effect = coefficient × (range / std_dev) = coefficient × range / std_dev
        # This is equivalent to: (coefficient / std_dev) × range = coef_per_unit × range
        coef_times_range = coef_per_unit * range_val
        
        gap_predictor_stats.append({
            'Gap_Predictor': predictor,
            'Median': median_val,
            'Std_Dev': std_dev,
            'Coefficient': coef,
            'Coefficient_per_Unit': coef_per_unit,
            'Range': range_val,
            'Coefficient_x_Range': coef_times_range
        })

gap_predictor_stats_df = pd.DataFrame(gap_predictor_stats)
gap_predictor_stats_df = gap_predictor_stats_df.sort_values('Gap_Predictor').reset_index(drop=True)

gap_predictor_stats_df = gap_predictor_stats_df.sort_values(by='Coefficient_x_Range', ascending=False)
gap_predictor_stats_df
```

```python
nonzero = gap_predictor_stats_df['Coefficient'] != 0
nonzero_predictors = gap_predictor_stats_df.loc[nonzero, 'Gap_Predictor'].reset_index(drop=True)
```

## Step 5: Counterfactual Prediction Function

### What is Counterfactual Analysis?

Counterfactual analysis allows us to answer "what if" questions: **What would happen to a country's predicted HALE gap if we changed a single predictor while keeping all other predictors constant?**

For each gap predictor, we:
1. Take a country's current values for all predictors
2. Vary only the selected predictor from its minimum (best case) to maximum (worst case) value across all countries
3. Generate predictions for each value in this range
4. Visualize how the predicted HALE gap changes

This helps identify which predictors have the largest potential impact on closing the HALE gap for a given country.

```python
def counterfactual_predictions(country, predictor, n_points=50):
    """
    Generate counterfactual predictions for a country by varying a single predictor.
    
    The function:
    1. Gets the country's current values for all predictors
    2. Determines the range to test (min to max value across all countries for gap predictors)
    3. Creates n_points evenly spaced values across this range
    4. For each value, replaces the selected predictor while keeping others constant
    5. Generates predictions using the trained Elastic Net model
    6. Returns results with metadata including endpoint country codes
    
    Parameters:
    -----------
    country : str
        Country code (e.g., 'USA', 'GBR')
    predictor : str
        Name of the predictor column to vary (e.g., 'AlcoholDeathRate_Gap')
    n_points : int, default=50
        Number of points in the range to evaluate
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns:
        - predictor_value: The value of the predictor being varied
        - predicted_hale_gap: The predicted HALE gap for that counterfactual
        - change_from_original: Change in predicted HALE gap from original prediction
        - country, country_code, predictor: Metadata
        - original_value, original_prediction: Country's current values
        - min_country_code, max_country_code: Countries defining the range endpoints
    """
    # Check if country exists in the data
    if country not in X.index:
        raise ValueError(f"Country '{country}' not found in data. Available countries: {list(X.index)}")
    
    # Check if predictor exists
    if predictor not in X.columns:
        raise ValueError(f"Predictor '{predictor}' not found. Available predictors: {list(X.columns)}")
    
    # Get the country's current data
    country_data = X.loc[country].copy()
    original_value = country_data[predictor]
    
    # Determine the range of values to test and get endpoint country codes
    # For gap predictors, use the range from gap_analysis_df
    if predictor.endswith('_Gap') and predictor in gap_analysis_df['Gap_Predictor'].values:
        row = gap_analysis_df[gap_analysis_df['Gap_Predictor'] == predictor].iloc[0]
        min_value = row['Lowest_Gap_Value']
        max_value = row['Highest_Gap_Value']
        min_country_code = row['Lowest_Gap_Country_Code']
        max_country_code = row['Highest_Gap_Country_Code']
    else:
        # For other predictors, use the min/max from the actual data
        # Exclude ZRO from min/max calculations for non-gap predictors
        predictor_data = X[predictor].dropna()
        if len(predictor_data) == 0:
            raise ValueError(f"Predictor '{predictor}' has no valid data")
        # Exclude ZRO for non-gap predictors
        predictor_data_no_zro = predictor_data[predictor_data.index != 'ZRO'] if 'ZRO' in predictor_data.index else predictor_data
        min_value = predictor_data_no_zro.min()
        max_value = predictor_data_no_zro.max()
        min_country_code = predictor_data_no_zro.idxmin()
        max_country_code = predictor_data_no_zro.idxmax()
    
    # For gap predictors, ensure we don't go below 0 (use ZRO as minimum)
    if predictor.endswith('_Gap'):
        if min_value < 0:
            min_value = 0.0
            min_country_code = 'ZRO'
    
    # Create range of values to test
    predictor_values = np.linspace(min_value, max_value, n_points)
    
    # Get original prediction (convert Series to DataFrame to preserve feature names)
    original_prediction = elastic_net_best_model.predict(country_data.to_frame().T)[0]
    
    # Generate counterfactual predictions
    results = []
    for pred_value in predictor_values:
        # Create counterfactual data
        counterfactual_data = country_data.copy()
        counterfactual_data[predictor] = pred_value
        
        # Generate prediction (convert Series to DataFrame to preserve feature names)
        prediction = elastic_net_best_model.predict(counterfactual_data.to_frame().T)[0]
        
        results.append({
            'predictor_value': pred_value,
            'predicted_hale_gap': prediction,
            'change_from_original': prediction - original_prediction
        })
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Add metadata
    results_df['country'] = get_country_name(country)
    results_df['country_code'] = country
    results_df['predictor'] = predictor
    results_df['original_value'] = original_value
    results_df['original_prediction'] = original_prediction
    results_df['min_country_code'] = min_country_code
    results_df['max_country_code'] = max_country_code
    
    return results_df
```

```python
# Visualize counterfactual predictions
def plot_counterfactual(counterfactual_results):
    """Plot counterfactual predictions"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Get original values
    original_val = counterfactual_results['original_value'].iloc[0]
    original_pred = counterfactual_results['original_prediction'].iloc[0]
    predictor_name = counterfactual_results['predictor'].iloc[0]
    country_name = counterfactual_results['country'].iloc[0]
    country_code = counterfactual_results['country_code'].iloc[0]
    min_country_code = counterfactual_results['min_country_code'].iloc[0]
    max_country_code = counterfactual_results['max_country_code'].iloc[0]
    
    # Get endpoint values and predictions
    min_val = counterfactual_results['predictor_value'].min()
    max_val = counterfactual_results['predictor_value'].max()
    min_pred = counterfactual_results.loc[counterfactual_results['predictor_value'].idxmin(), 'predicted_hale_gap']
    max_pred = counterfactual_results.loc[counterfactual_results['predictor_value'].idxmax(), 'predicted_hale_gap']
    min_change = counterfactual_results.loc[counterfactual_results['predictor_value'].idxmin(), 'change_from_original']
    max_change = counterfactual_results.loc[counterfactual_results['predictor_value'].idxmax(), 'change_from_original']
    
    # Plot 1: Predicted HALE gap vs predictor value
    plt.sca(axes[0])
    plt.plot(counterfactual_results['predictor_value'], 
             counterfactual_results['predicted_hale_gap'],
             color=AIBM_COLORS['crimson'], linewidth=2, label='Counterfactual predictions')
    
    # Mark original point
    plt.plot(original_val, original_pred, 'o', 
             color=AIBM_COLORS['blue'], markersize=10, label='Original')
    
    # Annotate endpoints
    plt.plot(min_val, min_pred, 's', 
             color=AIBM_COLORS['green'], markersize=8, label='Min endpoint')
    plt.annotate(min_country_code, xy=(min_val, min_pred), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    plt.plot(max_val, max_pred, 's', 
             color=AIBM_COLORS['orange'], markersize=8, label='Max endpoint')
    plt.annotate(max_country_code, xy=(max_val, max_pred), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Annotate original point
    plt.annotate(country_code, xy=(original_val, original_pred), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9, 
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    decorate(xlabel=f"{predictor_name}",
             ylabel='Predicted HALE Gap (years)',
             title=f"{predictor_name}, {country_name}")
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Change from original vs predictor value
    plt.sca(axes[1])
    plt.plot(counterfactual_results['predictor_value'], 
             counterfactual_results['change_from_original'],
             color=AIBM_COLORS['crimson'], linewidth=2)
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    plt.plot(original_val, 0, 'o', 
             color=AIBM_COLORS['blue'], markersize=10)
    
    # Annotate endpoints
    plt.plot(min_val, min_change, 's', 
             color=AIBM_COLORS['green'], markersize=8)
    plt.annotate(min_country_code, xy=(min_val, min_change), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    plt.plot(max_val, max_change, 's', 
             color=AIBM_COLORS['orange'], markersize=8)
    plt.annotate(max_country_code, xy=(max_val, max_change), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Annotate original point
    plt.annotate(country_code, xy=(original_val, 0), 
                 xytext=(5, 5), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    decorate(xlabel=f"{predictor_name}",
             ylabel='Change in Predicted HALE Gap (years)',
             title='Change from Original Prediction')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()

```

```python
# Test the function with an example
# Let's test with a country and a gap predictor with nonzero coefficient
test_country = 'USA'
test_predictor = nonzero_predictors[0] if len(nonzero_predictors) > 0 else gap_predictors[0]

print(f"Testing counterfactual predictions:")
print(f"Country: {get_country_name(test_country)} ({test_country})")
print(f"Predictor: {test_predictor}")

counterfactual_results = counterfactual_predictions(test_country, test_predictor, n_points=10)

# Display summary
print(f"\nOriginal value: {counterfactual_results['original_value'].iloc[0]:.4f}")
print(f"Original prediction: {counterfactual_results['original_prediction'].iloc[0]:.4f} years")
print(f"\nRange tested: {counterfactual_results['predictor_value'].min():.4f} to {counterfactual_results['predictor_value'].max():.4f}")
print(f"Prediction range: {counterfactual_results['predicted_hale_gap'].min():.4f} to {counterfactual_results['predicted_hale_gap'].max():.4f} years")
print(f"Change range: {counterfactual_results['change_from_original'].min():.4f} to {counterfactual_results['change_from_original'].max():.4f} years")
```

## Step 6: Counterfactual Analysis for USA - All Gap Predictors

### Counterfactual Analysis for USA

We now generate counterfactual predictions for the United States across all gap predictors that have nonzero coefficients in the Elastic Net model. This allows us to see which predictors have the largest potential impact on reducing the HALE gap for the USA.

For each predictor, we vary it from the minimum (best case) to maximum (worst case) value observed across all countries, while keeping all other predictors at USA's current values.

```python
# Generate counterfactual predictions for target country across all gap predictors with nonzero coefficients
target_country = 'USA'
print(f"Generating counterfactual predictions for {get_country_name(target_country)} ({target_country})")
print(f"Total gap predictors: {len(nonzero_predictors)}")
```

```python
# Loop through all gap predictors and generate counterfactuals
counterfactuals = {}

for predictor in nonzero_predictors:
    print(f"\nProcessing: {predictor}")
    try:
        results = counterfactual_predictions(target_country, predictor, n_points=50)
        counterfactuals[predictor] = results
        print(f"  ✓ Generated {len(results)} counterfactual points")
        print(f"  Range: {results['predictor_value'].min():.4f} to {results['predictor_value'].max():.4f}")
        print(f"  Prediction range: {results['predicted_hale_gap'].min():.4f} to {results['predicted_hale_gap'].max():.4f} years")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n✓ Successfully generated counterfactuals for {len(counterfactuals)} predictors")
```

### Visualizing Counterfactual Predictions

Each plot shows two panels:
- **Left panel**: Predicted HALE gap vs. predictor value. The blue dot shows USA's current position, and the line shows how the prediction would change if we varied this predictor.
- **Right panel**: Change in predicted HALE gap from USA's original prediction. This shows the potential improvement (negative values) or worsening (positive values) from changing this predictor.

The annotations show:
- **Green square**: Country with the minimum (best) value for this predictor
- **Orange square**: Country with the maximum (worst) value for this predictor  
- **Blue circle**: USA's current value

```python
# Plot counterfactual for first predictor (highest impact by Coefficient_x_Range)
if len(nonzero_predictors) > 0:
    predictor = nonzero_predictors[0]
    plot_counterfactual(counterfactuals[predictor])
```

```python
# Plot counterfactual for second predictor
if len(nonzero_predictors) > 1:
    predictor = nonzero_predictors[1]
    plot_counterfactual(counterfactuals[predictor])
```

```python
# Plot counterfactual for third predictor
if len(nonzero_predictors) > 2:
    predictor = nonzero_predictors[2]
    plot_counterfactual(counterfactuals[predictor])
```

```python
# Plot counterfactual for fourth predictor
if len(nonzero_predictors) > 3:
    predictor = nonzero_predictors[3]
    plot_counterfactual(counterfactuals[predictor])
```

```python
# Plot counterfactual for fifth predictor
if len(nonzero_predictors) > 4:
    predictor = nonzero_predictors[4]
    plot_counterfactual(counterfactuals[predictor])
```

## Step 7: Potential Impact Summary Table

### Potential HALE Gap Reduction for USA

This table shows the potential decrease in HALE gap if the USA could achieve the best-case (lowest gap) value for each predictor, while keeping all other predictors at current USA values.

```python
# Create summary table showing potential impact for each nonzero predictor
impact_summary = []

for predictor in nonzero_predictors:
    if predictor in counterfactuals:
        # Get current value and prediction for target country
        results = counterfactuals[predictor]
        current_value = results['original_value'].iloc[0]
        current_prediction = results['original_prediction'].iloc[0]
        
        # Get best case (minimum gap) country and value
        if predictor in gap_analysis_df['Gap_Predictor'].values:
            row = gap_analysis_df[gap_analysis_df['Gap_Predictor'] == predictor].iloc[0]
            best_country_code = row['Lowest_Gap_Country_Code']
            best_value = row['Lowest_Gap_Value']
            # ZRO is already handled in gap_analysis_df, so best_value will be 0 if min was negative
        else:
            # Fallback if not in gap_analysis_df
            predictor_data = X[predictor].dropna()
            # Exclude ZRO for non-gap predictors
            predictor_data_no_zro = predictor_data[predictor_data.index != 'ZRO'] if 'ZRO' in predictor_data.index else predictor_data
            best_country_code = predictor_data_no_zro.idxmin()
            best_value = predictor_data_no_zro.min()
            # For gap predictors not in gap_analysis_df, ensure we use 0 if min is negative
            if predictor.endswith('_Gap') and best_value < 0:
                best_country_code = 'ZRO'
                best_value = 0.0
        
        # Get prediction if target country had the best value
        # Find the row in counterfactual results closest to best_value
        best_prediction_row = results.iloc[(results['predictor_value'] - best_value).abs().idxmin()]
        best_prediction = best_prediction_row['predicted_hale_gap']
        
        # Calculate potential decrease (positive = improvement, negative = would worsen)
        potential_decrease = current_prediction - best_prediction
        
        impact_summary.append({
            'Gap_Predictor': predictor,
            'Current_Gap': current_value,
            'Best_Country': best_country_code,
            'Best_Gap_Value': best_value,
            'Current_Prediction': current_prediction,
            'Best_Case_Prediction': best_prediction,
            'Potential_Decrease': potential_decrease
        })

impact_df = pd.DataFrame(impact_summary)
impact_df = impact_df.sort_values('Potential_Decrease', ascending=False).reset_index(drop=True)

impact_df
```

```python
# Summary statistics
country_name = get_country_name(target_country)
print(f"Summary of Potential HALE Gap Reductions for {country_name}:")
print(f"Total predictors analyzed: {len(impact_df)}")
print(f"Average potential decrease: {impact_df['Potential_Decrease'].mean():.3f} years")
print(f"Maximum potential decrease: {impact_df['Potential_Decrease'].max():.3f} years")
print(f"Sum of potential decreases (if all improved simultaneously): {impact_df['Potential_Decrease'].sum():.3f} years")
print(f"\nNote: Sum assumes linearity and independence of effects, which may not hold in practice.")
```
