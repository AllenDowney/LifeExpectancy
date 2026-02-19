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

from utils import decorate, underride, configure_plot_style, AIBM_COLORS, code_to_who_country, code_to_wef_country, write_html_table, codes_to_country_names

configure_plot_style()

# Set cutoff year for temporal analysis (excludes 2020+ to avoid COVID-19 distortions)
cutoff_year = 2019
```

## Load Saved Data

```python
# Code to read the saved data back from HDF5 file
hdf_file = f'../data/hale_analysis_data_{cutoff_year}.h5'

# Read data back
with pd.HDFStore(hdf_file, mode='r') as store:
    predictors_full = store['predictors']
    target = store['target_le']
```

```python
# Select only Gap and Mid columns for modeling (exclude Male and Female columns)
# Male and Female columns are kept in predictors_full for counterfactual analysis
gap_mid_cols = [col for col in predictors_full.columns if col.startswith('Gap_') or col.startswith('Mid_')]
# Add female-only indicators if present (e.g., MaternalMortality_Female)
if 'MaternalMortality_Female' in predictors_full.columns:
    gap_mid_cols += ['MaternalMortality_Female']
predictors = predictors_full[gap_mid_cols].copy()

# Display predictor information
print(f"Number of predictors: {len(predictors.columns)}")
print(f"Number of countries: {len(predictors)}")
print(f"\nSample of predictor column names:")
print(list(predictors.columns[:10]))
print(f"\nTotal columns in predictors_full (including Male/Female): {len(predictors_full.columns)}")
```

## Model Fitting


```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold
from sklearn.metrics import r2_score, mean_absolute_error

# Prepare data: X (predictors) and y (target)
# Predictors are already in Mid + Gap format (from eda.md)
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

### Fit Multiple Models

```python
# Define parameter grids for each model
ridge_params = {'ridge__alpha': np.logspace(-2, 4, 50)}  # Regularization strength
lasso_params = {'lasso__alpha': np.logspace(-3, 1, 50)}
elastic_net_params = {
    'elasticnet__alpha': np.logspace(-3, 1, 20),
    'elasticnet__l1_ratio': np.linspace(0.1, 0.9, 9)  # 0=Ridge, 1=Lasso
}

# Create pipelines with StandardScaler and models
ridge_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge', Ridge())
])

lasso_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lasso', Lasso(max_iter=10000))
])

elastic_net_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('elasticnet', ElasticNet(max_iter=10000))
])
```

```python
# Fit Ridge Regression with cross-validation
print("Fitting Ridge Regression...")
ridge_grid = GridSearchCV(ridge_pipeline, ridge_params, cv=cv, 
                          scoring='r2', n_jobs=-1, verbose=1)
ridge_grid.fit(X, y)

ridge_best_score = ridge_grid.best_score_
ridge_best_params = ridge_grid.best_params_
ridge_best_model = ridge_grid.best_estimator_

pd.DataFrame({
    'Model': ['Ridge'],
    'Best_CV_R2': [ridge_best_score],
    'Best_Alpha': [ridge_best_params['ridge__alpha']]
})
```

```python
# Fit Lasso Regression with cross-validation
print("Fitting Lasso Regression...")
lasso_grid = GridSearchCV(lasso_pipeline, lasso_params, cv=cv,
                          scoring='r2', n_jobs=-1, verbose=1)
lasso_grid.fit(X, y)

lasso_best_score = lasso_grid.best_score_
lasso_best_params = lasso_grid.best_params_
lasso_best_model = lasso_grid.best_estimator_

pd.DataFrame({
    'Model': ['Lasso'],
    'Best_CV_R2': [lasso_best_score],
    'Best_Alpha': [lasso_best_params['lasso__alpha']]
})
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

## Model Performance Summary

```python
# Calculate MAE from cross-validation for each model
ridge_mae_scores = -cross_val_score(ridge_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')
lasso_mae_scores = -cross_val_score(lasso_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')
elastic_net_mae_scores = -cross_val_score(elastic_net_best_model, X, y, cv=cv, scoring='neg_mean_absolute_error')

# Compare cross-validation scores
model_comparison = pd.DataFrame({
    'Model': ['Ridge', 'Lasso', 'Elastic Net'],
    'CV_R2_Score': [ridge_best_score, lasso_best_score, elastic_net_best_score],
    'CV_MAE_Mean': [
        ridge_mae_scores.mean(),
        lasso_mae_scores.mean(),
        elastic_net_mae_scores.mean()
    ],
    'CV_MAE_Std': [
        ridge_mae_scores.std(),
        lasso_mae_scores.std(),
        elastic_net_mae_scores.std()
    ]
})

model_comparison_sorted = model_comparison.sort_values('CV_R2_Score', ascending=False)
model_comparison_sorted
```

```python
# Write model comparison table to HTML
write_html_table(model_comparison_sorted, f'tables/model_comparison_le_{cutoff_year}.html')
```

```python
primary_model = elastic_net_best_model
primary_model_name = 'Elastic Net'
```

```python
# Calculate predictions and residuals
y_pred = primary_model.predict(X)
y_pred = pd.Series(y_pred, index=y.index)
residuals = y - y_pred
```

```python
# Calculate R² on full dataset (in-sample/training R²)
# Note: This is higher than cross-validation R² because the model is evaluated on the same
# data it was trained on. The cross-validation R² (~0.74) is a better estimate of 
# out-of-sample performance (generalization). The difference indicates some overfitting,
# which is expected with a small sample size (n~30-40 countries) and many predictors.
r2_full = primary_model.score(X, y)
print(f"R² on full dataset (in-sample): {r2_full:.4f}")
print(f"Cross-validation R² (out-of-sample): {elastic_net_best_score:.4f}")
print(f"MAE: {mean_absolute_error(y, y_pred):.4f} years")
```

```python
# Display model performance summary
print("\n" + "="*60)
print("Elastic Net Model Performance Summary (Mid + Gap)")
print("="*60)
print(f"Cross-validation R²: {elastic_net_best_score:.4f}")
print(f"In-sample R²: {r2_full:.4f}")
print(f"MAE: {mean_absolute_error(y, y_pred):.4f} years")
print(f"Number of predictors: {len(X.columns)}")
print(f"Number of non-zero coefficients: {np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ != 0)}")
```

```python
# Extract coefficients from each model (on standardized scale)
ridge_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'Ridge_Coefficient': ridge_best_model.named_steps['ridge'].coef_
}).sort_values('Ridge_Coefficient', key=abs, ascending=False)

lasso_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'Lasso_Coefficient': lasso_best_model.named_steps['lasso'].coef_
}).sort_values('Lasso_Coefficient', key=abs, ascending=False)

elastic_net_coefs = pd.DataFrame({
    'Predictor': X.columns,
    'ElasticNet_Coefficient': elastic_net_best_model.named_steps['elasticnet'].coef_
}).sort_values('ElasticNet_Coefficient', key=abs, ascending=False)

# Merge coefficient comparisons
coef_comparison = ridge_coefs.merge(lasso_coefs, on='Predictor').merge(elastic_net_coefs, on='Predictor')
coef_comparison
```

```python
# Write coefficient comparison table to HTML (only non-zero coefficients)
coef_comparison_nonzero = coef_comparison[
    (coef_comparison['Ridge_Coefficient'] != 0) | 
    (coef_comparison['Lasso_Coefficient'] != 0) | 
    (coef_comparison['ElasticNet_Coefficient'] != 0)
].copy()
write_html_table(coef_comparison_nonzero, f'tables/coefficient_comparison_le_{cutoff_year}.html')
```

```python
# Count non-zero coefficients (feature selection in Lasso/Elastic Net)
feature_selection_summary = pd.DataFrame({
    'Model': ['Ridge', 'Lasso', 'Elastic Net'],
    'Total_Predictors': [len(X.columns), len(X.columns), len(X.columns)],
    'Non_Zero_Coefficients': [
        np.sum(ridge_best_model.named_steps['ridge'].coef_ != 0),
        np.sum(lasso_best_model.named_steps['lasso'].coef_ != 0),
        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ != 0)
    ],
    'Zero_Coefficients': [
        np.sum(ridge_best_model.named_steps['ridge'].coef_ == 0),
        np.sum(lasso_best_model.named_steps['lasso'].coef_ == 0),
        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ == 0)
    ]
})

feature_selection_summary
```

```python
# Write feature selection summary table to HTML
write_html_table(feature_selection_summary, f'tables/feature_selection_summary_le_{cutoff_year}.html')
```

## Model Diagnostics


```python
# Residual vs. Predicted values plot
plt.scatter(y_pred, residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
decorate(xlabel='Predicted HALE Gap (years)',
         ylabel='Residuals (years)',
         title='Residuals vs. Predicted Values (Elastic Net Model - Mid+Gap Format)')

plt.savefig(f'figs/residuals_vs_predicted_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```

```python
# Histogram of residuals
plt.hist(residuals, bins=15, color=AIBM_COLORS['crimson'], edgecolor='white', alpha=0.7)
plt.axvline(x=0, color='gray', linestyle='--', linewidth=1)
decorate(xlabel='Residuals (years)',
         ylabel='Frequency',
         title='Distribution of Residuals (Elastic Net Model)')

plt.savefig(f'figs/residuals_distribution_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```


```python
# Identify potential outliers (residuals > 2 standard deviations)
outlier_threshold = 2 * residuals.std()
outliers = residuals[abs(residuals) > outlier_threshold]

outlier_df = pd.DataFrame({
    'Country': codes_to_country_names(outliers.index),
    'Actual_HALE_Gap': y[outliers.index],
    'Predicted_HALE_Gap': y_pred[outliers.index],
    'Residual': outliers.values,
    'Abs_Residual': abs(outliers.values)
}).sort_values('Abs_Residual', ascending=False)

outlier_df if not outlier_df.empty else "No outliers detected (|residual| > 2 std)"
```

```python
# Residuals by country (sorted by absolute residual)
residuals_by_country = pd.DataFrame({
    'Country': codes_to_country_names(residuals.index),
    'Actual_HALE_Gap': y.values,
    'Predicted_HALE_Gap': y_pred,
    'Residual': residuals.values,
    'Abs_Residual': abs(residuals.values)
}).sort_values('Abs_Residual', ascending=False)

residuals_by_country.head(10)
```

```python
# Write residuals by country table to HTML
write_html_table(residuals_by_country, f'tables/residuals_by_country_le_{cutoff_year}.html')
```

```python
# Check for patterns: plot residuals vs. each predictor (top predictors by absolute coefficient)
# Get top predictors by absolute coefficient value
coef_abs = pd.Series(elastic_net_best_model.named_steps['elasticnet'].coef_, index=X.columns).abs()
top_predictors = coef_abs.nlargest(5).index.values

fig, axes = plt.subplots(2, 3)
axes = axes.flatten()

for i, pred in enumerate(top_predictors):
    if i < len(axes):
        axes[i].scatter(X[pred], residuals, color=AIBM_COLORS['crimson'], alpha=0.6)
        axes[i].axhline(y=0, color='gray', linestyle='--', linewidth=1)
        axes[i].set_xlabel(pred)
        axes[i].set_ylabel('Residuals')
        axes[i].set_title(f'Residuals vs. {pred}')
        axes[i].grid(True, alpha=0.3)

# Hide unused subplots
for i in range(len(top_predictors), len(axes)):
    axes[i].set_visible(False)

plt.tight_layout()
plt.savefig(f'figs/residuals_vs_predictors_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```

## Importance Analysis


```python
# Create dictionary mapping predictor names to Elastic Net coefficients
# This makes it easier to look up coefficients by predictor name
elastic_net_coefs_dict = dict(zip(X.columns, elastic_net_best_model.named_steps['elasticnet'].coef_))
```

```python
# Feature importance = |coefficient| × std(predictor)
# This measures the contribution of each predictor to the HALE gap variation
# Since predictors are standardized, we multiply by the original standard deviation
# to get importance on the original scale

predictor_importance = []

for predictor in X.columns:
    coef = elastic_net_coefs_dict.get(predictor, 0)
    
    # Get the original (unstandardized) standard deviation
    # The scaler was fit on X, so we can get the std from predictors DataFrame
    if predictor in predictors.columns:
        std_original = predictors[predictor].std()
        importance = abs(coef) * std_original
    else:
        std_original = 0
        importance = 0
    
    predictor_importance.append({
        'Predictor': predictor,
        'Coefficient': coef,
        'Std_Original': std_original,
        'Importance': importance
    })

importance_df = pd.DataFrame(predictor_importance).sort_values('Importance', ascending=False)
importance_df
```

```python
# Write non-zero importance rows to HTML
importance_nonzero = importance_df[importance_df['Importance'] != 0].copy()
write_html_table(importance_nonzero, f'tables/predictor_importance_le_{cutoff_year}.html')
importance_nonzero
```

### Visualize Predictor Importance

```python
# Create bar chart of all predictors with non-zero coefficients by importance
non_zero_importance = importance_df[importance_df['Importance'] != 0].copy()

colors = [AIBM_COLORS['crimson'] if x > 0 else AIBM_COLORS['blue'] 
          for x in non_zero_importance['Coefficient']]
plt.barh(range(len(non_zero_importance)), non_zero_importance['Importance'], color=colors)
plt.yticks(range(len(non_zero_importance)), non_zero_importance['Predictor'])
plt.gca().invert_yaxis()
decorate(xlabel='Importance (|Coefficient| × Std)',
         ylabel='Predictor',
         title='Predictors by Importance (Elastic Net Model - Mid+Gap)')

plt.savefig(f'figs/predictor_importance_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```

### Importance by Indicator

```python
# Extract indicator names from Mid_ and Gap_ columns
all_indicators = set()
for col in predictors.columns:
    if col.startswith('Mid_'):
        indicator_name = col[4:]  # Remove 'Mid_' prefix
        all_indicators.add(indicator_name)
    elif col.startswith('Gap_'):
        indicator_name = col[4:]  # Remove 'Gap_' prefix
        all_indicators.add(indicator_name)

# Indicators with both Mid and Gap (most indicators)
mid_gap_indicators = sorted([ind for ind in all_indicators 
                             if f'Mid_{ind}' in predictors.columns and f'Gap_{ind}' in predictors.columns])

# Female-only indicators (e.g., MaternalMortality)
# Automatically include if present in predictors
female_only_indicators = []
if 'MaternalMortality_Female' in predictors.columns:
    female_only_indicators = ['MaternalMortality']
female_only_indicators
```

```python
# Aggregate importance by indicator (sum of Mid and Gap importance)
indicator_importance = {}

for indicator in mid_gap_indicators:
    mid_col = f'Mid_{indicator}'
    gap_col = f'Gap_{indicator}'
    
    mid_imp = importance_df[importance_df['Predictor'] == mid_col]['Importance'].values
    gap_imp = importance_df[importance_df['Predictor'] == gap_col]['Importance'].values
    
    if len(mid_imp) > 0 and len(gap_imp) > 0:
        total_importance = mid_imp[0] + gap_imp[0]
        indicator_importance[indicator] = {
            'Mid_Importance': mid_imp[0],
            'Gap_Importance': gap_imp[0],
            'Total_Importance': total_importance
        }

# Add female-only indicators (if any)
for indicator in female_only_indicators:
    # Check for any column matching this indicator
    matching_cols = [col for col in predictors.columns if indicator in col]
    print(matching_cols)
    if matching_cols:
        col = matching_cols[0]
        col_imp = importance_df[importance_df['Predictor'] == col]['Importance'].values
        if len(col_imp) > 0:
            indicator_importance[indicator] = {
                'Mid_Importance': np.nan,
                'Gap_Importance': np.nan,
                'Total_Importance': col_imp[0]
            }

indicator_importance_df = pd.DataFrame(indicator_importance).T
indicator_importance_df = indicator_importance_df.sort_values('Total_Importance', ascending=False)
indicator_importance_df
```

```python
# Write indicator importance table to HTML
indicator_importance_formatted = indicator_importance_df.reset_index().rename(columns={'index': 'Indicator'})
write_html_table(indicator_importance_formatted, f'tables/indicator_importance_le_{cutoff_year}.html')
indicator_importance_formatted
```

### Visualize Indicator Importance

```python
# Bar chart of indicator-level importance
colors_bar = [AIBM_COLORS['crimson'] for _ in range(len(indicator_importance_df))]
plt.barh(range(len(indicator_importance_df)), indicator_importance_df['Total_Importance'], 
         color=colors_bar)
plt.yticks(range(len(indicator_importance_df)), indicator_importance_df.index)
plt.gca().invert_yaxis()
decorate(xlabel='Total Importance (Sum of Mid + Gap)',
         ylabel='Indicator',
         title='Indicator Importance (Elastic Net Model - Mid+Gap Format)')

plt.savefig(f'figs/indicator_importance_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```

## Statsmodels Linear Regression with Selected Predictors

```python
import statsmodels.api as sm

# Extract predictors with non-zero coefficients from Elastic Net
elastic_net_coefs = elastic_net_best_model.named_steps['elasticnet'].coef_
non_zero_mask = elastic_net_coefs != 0
selected_predictors = X.columns[non_zero_mask].tolist()

print(f"Selected predictors (non-zero Elastic Net coefficients): {len(selected_predictors)}")
print(selected_predictors)
```

```python
# Standardize the selected predictors to match Elastic Net preprocessing
# Create a new StandardScaler and fit it only on the selected predictors
# (We can't reuse the Elastic Net scaler because it was fit on all predictors)
from sklearn.preprocessing import StandardScaler

# Create subset of X with only selected predictors
X_selected = X[selected_predictors].copy()

# Create and fit a new scaler on the selected predictors only
ols_scaler = StandardScaler()
X_selected_standardized = pd.DataFrame(
    ols_scaler.fit_transform(X_selected),
    index=X_selected.index,
    columns=X_selected.columns
)

# Add constant term for intercept
X_selected_with_const = sm.add_constant(X_selected_standardized)

# Fit OLS regression on standardized predictors
ols_model = sm.OLS(y, X_selected_with_const).fit()

# Display summary
ols_model.summary()
```

```python
# Compare coefficients: Elastic Net vs OLS (both on standardized scale)
# Note: Both models now use standardized predictors, so coefficients are directly comparable
coef_comparison_selected = pd.DataFrame({
    'Predictor': selected_predictors,
    'ElasticNet_Coefficient': elastic_net_coefs[non_zero_mask],
    'OLS_Coefficient': ols_model.params[selected_predictors].values,
    'OLS_PValue': ols_model.pvalues[selected_predictors].values,
    'OLS_StdErr': ols_model.bse[selected_predictors].values
})

coef_comparison_selected['Difference'] = coef_comparison_selected['OLS_Coefficient'] - coef_comparison_selected['ElasticNet_Coefficient']
coef_comparison_selected = coef_comparison_selected.sort_values('ElasticNet_Coefficient', key=abs, ascending=False)
coef_comparison_selected
```

```python
# Write Elastic Net vs OLS coefficient comparison to HTML
write_html_table(coef_comparison_selected, f'tables/elasticnet_ols_coefficient_comparison_le_{cutoff_year}.html')
```

```python
# Save Elastic Net coefficients to CSV for comparison with Bayesian model
# Save all coefficients (including zeros) for complete comparison
elastic_net_coefs_all = pd.DataFrame({
    'Predictor': X.columns,
    'ElasticNet_Coefficient': elastic_net_best_model.named_steps['elasticnet'].coef_
})

# Merge with importance
elastic_net_coefs_all = elastic_net_coefs_all.merge(
    importance_df[['Predictor', 'Importance']], 
    on='Predictor', 
    how='left'
).sort_values('ElasticNet_Coefficient', key=abs, ascending=False)

elastic_net_coefs_all.to_csv(f'../data/elasticnet_coefficients_le_{cutoff_year}.csv', index=False)
print(f"Saved Elastic Net coefficients to: data/elasticnet_coefficients_le_{cutoff_year}.csv")
```

```python
# Save selected coefficients comparison (Elastic Net vs OLS) to CSV
coef_comparison_selected.to_csv(f'../data/coefficient_comparison_le_{cutoff_year}.csv', index=False)
print(f"Saved coefficient comparison to: data/coefficient_comparison_le_{cutoff_year}.csv")
```

```python
# Compare model performance
ols_r2 = ols_model.rsquared
ols_adj_r2 = ols_model.rsquared_adj
ols_mae = mean_absolute_error(y, ols_model.fittedvalues)

performance_comparison = pd.DataFrame({
    'Model': ['Elastic Net', 'OLS (Selected Predictors)'],
    'R²': [r2_full, ols_r2],
    'Adjusted R²': [np.nan, ols_adj_r2],
    'MAE': [mean_absolute_error(y, y_pred), ols_mae],
    'Number of Predictors': [len(X.columns), len(selected_predictors)],
    'Non-Zero Coefficients': [np.sum(elastic_net_coefs != 0), len(selected_predictors)]
})

performance_comparison
```

```python
# Write performance comparison table to HTML
write_html_table(performance_comparison, f'tables/performance_comparison_le_{cutoff_year}.html')
```

## Country-Level Predictions Comparison

```python
# Generate predictions from both models
# Note: Both models use standardized predictors, so we need to standardize X for OLS predictions
elastic_net_predictions = elastic_net_best_model.predict(X)
ols_predictions = ols_model.predict(X_selected_with_const)  # Already standardized above

# Create comparison table
predictions_comparison = pd.DataFrame({
    'Country': codes_to_country_names(y.index),
    'Actual_HALE_Gap': y.values,
    'ElasticNet_Prediction': elastic_net_predictions,
    'OLS_Prediction': ols_predictions,
    'EN_Residual': y.values - elastic_net_predictions,
    'OLS_Residual': y.values - ols_predictions,
    'Prediction_Difference': ols_predictions - elastic_net_predictions,
    'Abs_Prediction_Difference': np.abs(ols_predictions - elastic_net_predictions)
})

# Sort by absolute prediction difference to see where models disagree most
predictions_comparison = predictions_comparison.sort_values('Abs_Prediction_Difference', ascending=False)

predictions_comparison
```

```python
# Write predictions comparison table to HTML
write_html_table(predictions_comparison, f'tables/predictions_comparison_le_{cutoff_year}.html')
```

```python
# Summary statistics of prediction differences
print("Summary of Prediction Differences (OLS - Elastic Net):")
print("="*60)
print(f"Mean difference: {predictions_comparison['Prediction_Difference'].mean():.4f} years")
print(f"Median difference: {predictions_comparison['Prediction_Difference'].median():.4f} years")
print(f"Std deviation: {predictions_comparison['Prediction_Difference'].std():.4f} years")
print(f"Min difference: {predictions_comparison['Prediction_Difference'].min():.4f} years")
print(f"Max difference: {predictions_comparison['Prediction_Difference'].max():.4f} years")
print(f"Mean absolute difference: {predictions_comparison['Abs_Prediction_Difference'].mean():.4f} years")
print(f"\nCountries with largest prediction differences:")
predictions_comparison[['Country', 'Actual_HALE_Gap', 'ElasticNet_Prediction', 
                              'OLS_Prediction', 'Prediction_Difference']].head(10)
```

```python
# Visualize prediction differences
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter plot: EN vs OLS predictions
axes[0].scatter(elastic_net_predictions, ols_predictions, 
                color=AIBM_COLORS['crimson'], alpha=0.6)
axes[0].plot([elastic_net_predictions.min(), elastic_net_predictions.max()],
             [elastic_net_predictions.min(), elastic_net_predictions.max()],
             'k--', linewidth=1, label='Perfect agreement')
axes[0].set_xlabel('Elastic Net Prediction (years)')
axes[0].set_ylabel('OLS Prediction (years)')
axes[0].set_title('Elastic Net vs OLS Predictions')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Histogram of prediction differences
axes[1].hist(predictions_comparison['Prediction_Difference'], bins=15,
             color=AIBM_COLORS['crimson'], edgecolor='white', alpha=0.7)
axes[1].axvline(x=0, color='gray', linestyle='--', linewidth=1)
axes[1].set_xlabel('Prediction Difference (OLS - EN, years)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Prediction Differences')

plt.tight_layout()
plt.savefig(f'figs/predictions_comparison_le_{cutoff_year}.png', dpi=300, bbox_inches='tight')
```

```python
# Compare residuals from both models
residuals_comparison = pd.DataFrame({
    'Country': codes_to_country_names(y.index),
    'EN_Residual': y.values - elastic_net_predictions,
    'OLS_Residual': y.values - ols_predictions,
    'Residual_Difference': (y.values - ols_predictions) - (y.values - elastic_net_predictions)
})

residuals_comparison = residuals_comparison.sort_values('Residual_Difference', key=abs, ascending=False)
print("Residual Comparison (Actual - Predicted):")
print("="*60)
print(f"EN MAE: {mean_absolute_error(y, elastic_net_predictions):.4f} years")
print(f"OLS MAE: {mean_absolute_error(y, ols_predictions):.4f} years")
print(f"\nCountries with largest residual differences:")
residuals_comparison.head(10)
```

## Counterfactual Analysis

Counterfactual analysis allows us to answer "what if" questions: What would happen to a country's predicted life expectancy gap if we adjusted a gap predictor to the best attainable value?

For each gap predictor, we find the best case:
- If the current gap is positive (Male > Female), we find the country with the smallest gap (minimum)
- If the current gap is negative (Female > Male), we find the country with the largest gap (maximum, most positive)

To achieve that target gap, we adjust either male or female values:
- If the gap is positive (Male > Female), we bring men toward women's level
- If the gap is negative (Female > Male), we bring women toward men's level

After adjusting Male/Female values, we recompute Mid and Gap values, then use the model to generate the counterfactual prediction.

```python
# Find minimum and maximum gap for each gap predictor across all countries
gap_predictors = [col for col in X.columns if col.startswith('Gap_')]
gap_extremes = {}
for gap_pred in gap_predictors:
    gap_data = X[gap_pred].dropna()
    gap_extremes[gap_pred] = {
        'min_gap': gap_data.min(),
        'min_country': gap_data.idxmin(),
        'max_gap': gap_data.max(),
        'max_country': gap_data.idxmax()
    }

gap_extremes_df = pd.DataFrame(gap_extremes).T
gap_extremes_df
```

```python
def counterfactual_predictions(country, gap_predictor):
    """
    Generate counterfactual prediction by adjusting Male/Female values to achieve best case gap.
    
    Parameters:
    -----------
    country : str
        Country code (e.g., 'USA', 'GBR')
    gap_predictor : str
        Name of the gap predictor column (e.g., 'Gap_Alcohol')
        
    Returns:
    --------
    dict
        Dictionary with counterfactual results including original and adjusted values
    """
    # Extract indicator name from gap predictor (e.g., 'Gap_Alcohol' -> 'Alcohol')
    indicator_name = gap_predictor.replace('Gap_', '')
    
    # Get original Male and Female values from predictors_full
    male_col = f'{indicator_name}_Male'
    female_col = f'{indicator_name}_Female'
    
    original_male = predictors_full.loc[country, male_col]
    original_female = predictors_full.loc[country, female_col]
    original_gap = original_male - original_female
    
    # Determine target gap based on current gap sign
    # If current gap is positive, find minimum gap (best case: smallest positive gap)
    # If current gap is negative, find maximum gap (best case: largest positive gap)
    if original_gap > 0:
        target_gap = gap_extremes[gap_predictor]['min_gap']
        target_country = gap_extremes[gap_predictor]['min_country']
    else:
        target_gap = gap_extremes[gap_predictor]['max_gap']
        target_country = gap_extremes[gap_predictor]['max_country']
    
    # If target gap has opposite sign of current gap, set target to zero
    if (original_gap > 0 and target_gap < 0) or (original_gap < 0 and target_gap > 0):
        target_gap = 0.0
        target_country = ""
    
    # Determine which direction to adjust
    if original_gap > 0:
        # Positive gap: bring men toward women's level
        adjusted_male = original_female + target_gap
        adjusted_female = original_female
    else:
        # Negative gap: bring women toward men's level
        adjusted_male = original_male
        adjusted_female = original_male - target_gap
    
    # Recompute Mid and Gap from adjusted Male/Female
    adjusted_mid = (adjusted_male + adjusted_female) / 2
    adjusted_gap = adjusted_male - adjusted_female
    
    # Get all current predictor values for the country
    counterfactual_data = X.loc[country].copy()
    
    # Update Mid and Gap for this indicator
    mid_col = f'Mid_{indicator_name}'
    counterfactual_data[mid_col] = adjusted_mid
    counterfactual_data[gap_predictor] = adjusted_gap
    
    # Generate prediction
    original_prediction = primary_model.predict(X.loc[country].to_frame().T)[0]
    counterfactual_prediction = primary_model.predict(counterfactual_data.to_frame().T)[0]
    
    return {
        'country': country,
        'indicator': indicator_name,
        'original_male': original_male,
        'original_female': original_female,
        'original_gap': original_gap,
        'target_gap': target_gap,
        'adjusted_male': adjusted_male,
        'adjusted_female': adjusted_female,
        'adjusted_mid': adjusted_mid,
        'adjusted_gap': adjusted_gap,
        'original_prediction': original_prediction,
        'counterfactual_prediction': counterfactual_prediction,
        'change_in_gap': counterfactual_prediction - original_prediction,
        'target_country': target_country
    }
```

```python
# Example: Counterfactual analysis for USA with Alcohol gap
test_country = 'USA'
test_predictor = 'Gap_Alcohol'

result = counterfactual_predictions(test_country, test_predictor)

# Display summary
print(f"Counterfactual Analysis: {code_to_who_country.get(test_country, test_country)} ({test_country})")
print(f"Indicator: {result['indicator']}")
print(f"\nOriginal values:")
print(f"  Male: {result['original_male']:.3f}")
print(f"  Female: {result['original_female']:.3f}")
print(f"  Gap (Male - Female): {result['original_gap']:.3f}")
if result['target_country']:
    if result['original_gap'] > 0:
        gap_type = "minimum"
    else:
        gap_type = "maximum"
    print(f"\nTarget gap ({gap_type} observed, from {code_to_who_country.get(result['target_country'], result['target_country'])}): {result['target_gap']:.3f}")
else:
    print(f"\nTarget gap (set to zero because best case has opposite sign): {result['target_gap']:.3f}")
print(f"\nAdjusted values to achieve target gap:")
print(f"  Male: {result['adjusted_male']:.3f}")
print(f"  Female: {result['adjusted_female']:.3f}")
print(f"  Gap (Male - Female): {result['adjusted_gap']:.3f}")
print(f"\nPredictions:")
print(f"  Original: {result['original_prediction']:.3f} years")
print(f"  Counterfactual: {result['counterfactual_prediction']:.3f} years")
print(f"  Change: {result['change_in_gap']:.3f} years")
```

```python
# Generate counterfactuals for all gap predictors for a country
def counterfactuals_for_country(country):
    """
    Generate counterfactual predictions for all gap predictors for a given country.
    
    Returns DataFrame with results sorted by importance (descending).
    """
    results = []
    for gap_pred in gap_predictors:
        try:
            result = counterfactual_predictions(country, gap_pred)
            indicator_name = result['indicator']
            
            # Get importance for this indicator
            if indicator_name in indicator_importance_df.index:
                importance = indicator_importance_df.loc[indicator_name, 'Total_Importance']
            else:
                importance = 0.0
            
            # Get country name for target country
            target_country_code = result['target_country']
            if target_country_code:
                target_country_name = code_to_who_country.get(target_country_code, target_country_code)
            else:
                target_country_name = ""
            
            results.append({
                'Indicator': indicator_name,
                'Current gap': result['original_gap'],
                'Target gap': result['target_gap'],
                'Target Country': target_country_name,
                'Change in LE gap': result['change_in_gap'],
                'Importance': importance
            })
        except (KeyError, ValueError):
            # Skip if indicator doesn't have Male/Female columns (e.g., MaternalMortality)
            continue
    
    df = pd.DataFrame(results)
    # Sort by importance (descending), then select only the columns we want
    df = df.sort_values('Importance', ascending=False)
    df = df[['Indicator', 'Current gap', 'Target gap', 'Target Country', 'Change in LE gap']]
    return df

# Example: All counterfactuals for USA
usa_counterfactuals = counterfactuals_for_country('USA')
usa_counterfactuals
```

```python
# Write counterfactual table to HTML
write_html_table(usa_counterfactuals, f'tables/counterfactuals_usa_le_{cutoff_year}.html')
```

```python
target['USA']
```

```python
gap_closer = usa_counterfactuals['Change in LE gap'] < 0
usa_counterfactuals.loc[gap_closer]
```

```python
total = usa_counterfactuals.loc[gap_closer, 'Change in LE gap'].sum()
total
```

```python
total / target['USA'] * 100
```

```python
gap_widener = usa_counterfactuals['Change in LE gap'] > 0
usa_counterfactuals.loc[gap_widener]
```

```python
usa_counterfactuals.loc[gap_widener, 'Change in LE gap'].sum()
```

This is based on conservative assumptions:

* Only the gap variables are causal -- for the overall rate variables, we're not sure about the nature of the relationship

* It might not be attainable to close all gaps completely, but we take other countries as evidence: if they have eliminated or remove a gap, that's evidence it's possible. If they are closer to zero, that evidence the gap can be reduced to the level they have achieved.

```python
from utils import beep

beep()
```
