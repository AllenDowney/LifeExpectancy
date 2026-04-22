"""Utility functions for Bayesian counterfactual analysis.

This module provides reusable functions for counterfactual analysis that work
for both HALE and Life Expectancy gap models.
"""

import os
import numpy as np
import pandas as pd
import arviz as az
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import colors as mcolors
from matplotlib.ticker import MaxNLocator

from utils import decorate, AIBM_COLORS, code_to_who_country, add_title, add_subtext, add_logo
from fig_utils import get_country_color, add_direct_line_labels, PREDICTOR_LABELS


def compute_gap_extremes(panel_df):
    """
    Compute minimum and maximum gap values for each gap predictor across all country-years.
    
    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel dataset with gap predictor columns (starting with 'Gap_')
        
    Returns
    -------
    dict
        Dictionary mapping gap predictor names to dictionaries with:
        - 'min_gap': minimum gap value
        - 'min_country': country code with minimum gap
        - 'min_year': year with minimum gap
        - 'max_gap': maximum gap value
        - 'max_country': country code with maximum gap
        - 'max_year': year with maximum gap
    """
    # Get all gap predictor columns
    gap_predictors = [col for col in panel_df.columns if col.startswith('Gap_')]
    
    # Compute extremes for each gap predictor
    gap_extremes = {}
    for gap_pred in gap_predictors:
        gap_data = panel_df[gap_pred].dropna()
        if len(gap_data) > 0:
            min_val = gap_data.min()
            max_val = gap_data.max()
            min_idx = gap_data.idxmin()
            max_idx = gap_data.idxmax()
            
            # Get country-year for extremes
            min_row = panel_df.loc[min_idx]
            max_row = panel_df.loc[max_idx]
            
            gap_extremes[gap_pred] = {
                'min_gap': min_val,
                'min_country': min_row['country'],
                'min_year': int(min_row['Year']),
                'max_gap': max_val,
                'max_country': max_row['country'],
                'max_year': int(max_row['Year']),
            }
    
    return gap_extremes


def counterfactual_predictions_bayesian(
    country, year, gap_predictor, trace, metadata, panel_df, gap_extremes, 
    country_to_idx, year_to_idx, target_zero=False
):
    """
    Generate counterfactual prediction by adjusting a gap predictor to best attainable value.
    
    Parameters
    ----------
    country : str
        Country code (e.g., 'USA', 'GBR')
    year : int
        Year (e.g., 2019)
    gap_predictor : str
        Name of the gap predictor column (e.g., 'Gap_Alcohol')
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
    metadata : dict
        Metadata dictionary with transformation parameters
    panel_df : pd.DataFrame
        Panel dataset with all predictor values
    gap_extremes : dict
        Dictionary with gap extremes for each predictor (from compute_gap_extremes)
    country_to_idx : dict
        Dictionary mapping country codes to indices
    year_to_idx : dict
        Dictionary mapping years to indices
    target_zero : bool, default False
        If True, always set target gap to zero. If False, use best attainable value.
        
    Returns
    -------
    dict
        Dictionary with counterfactual results including:
        - country, year, indicator: identifiers
        - current_gap, target_gap: gap values
        - target_country, target_year: target country-year
        - original_prediction: posterior distribution of original prediction
        - counterfactual_prediction: posterior distribution of counterfactual prediction
        - change: posterior distribution of change (counterfactual - original)
        - original_summary, counterfactual_summary, change_summary: dicts with mean and 94% HDI
    """
    # Get current country-year row
    country_year_mask = (panel_df['country'] == country) & (panel_df['Year'] == year)
    if not country_year_mask.any():
        raise ValueError(f"No data found for {country} in year {year}")
    
    current_row = panel_df[country_year_mask].iloc[0]
    
    # Extract indicator name from gap predictor (e.g., 'Gap_Alcohol' -> 'Alcohol')
    indicator_name = gap_predictor.replace('Gap_', '')
    
    # Get current gap value
    current_gap = current_row[gap_predictor]
    
    # Determine target gap
    if target_zero:
        target_gap = 0.0
        target_country = ""
        target_year = None
    else:
        # Use best attainable from gap_extremes
        if current_gap > 0:
            target_gap = gap_extremes[gap_predictor]['min_gap']
            target_country = gap_extremes[gap_predictor]['min_country']
            target_year = gap_extremes[gap_predictor]['min_year']
        else:
            target_gap = gap_extremes[gap_predictor]['max_gap']
            target_country = gap_extremes[gap_predictor]['max_country']
            target_year = gap_extremes[gap_predictor]['max_year']
        
        # If best attainable has opposite sign (e.g. min is negative when reducing a positive gap),
        # use zero instead — we want to eliminate the gap, not reverse it
        if (current_gap >= 0 and target_gap < 0) or (current_gap <= 0 and target_gap > 0):
            target_gap = 0.0
            target_country = ""
            target_year = None
    
    # Reconstruct current Male/Female from Mid and Gap
    mid_col = f'Mid_{indicator_name}'
    if mid_col not in current_row.index:
        raise ValueError(f"Mid column {mid_col} not found for {indicator_name}")
    
    current_mid = current_row[mid_col]
    current_male = current_mid + current_gap / 2
    current_female = current_mid - current_gap / 2
    
    # Adjust Male/Female to achieve target gap
    if current_gap > 0:
        # Positive gap: bring men toward women's level
        adjusted_male = current_female + target_gap
        adjusted_female = current_female
    else:
        # Negative gap: bring women toward men's level
        adjusted_male = current_male
        adjusted_female = current_male - target_gap
    
    # Recompute Mid and Gap from adjusted Male/Female
    adjusted_mid = (adjusted_male + adjusted_female) / 2
    adjusted_gap = adjusted_male - adjusted_female
    
    # Get all current predictor values (standardized)
    X_mean = np.array(metadata['X_mean'])
    X_std = np.array(metadata['X_std'])
    y_mean = metadata['y_mean']
    predictors = metadata['predictors']
    countries = np.array(metadata['countries'])
    years = np.array(metadata['years'])
    
    # Get country and year indices
    country_idx = country_to_idx[country]
    year_idx = year_to_idx[year]
    
    # Build original predictor vector (standardized)
    X_original = np.array([current_row[p] for p in predictors])
    X_original_std = (X_original - X_mean) / X_std
    
    # Build counterfactual predictor vector (standardized)
    X_counterfactual = X_original.copy()
    # Update the gap predictor
    gap_idx = predictors.index(gap_predictor)
    X_counterfactual[gap_idx] = adjusted_gap
    # Update the mid predictor if it exists
    if mid_col in predictors:
        mid_idx = predictors.index(mid_col)
        X_counterfactual[mid_idx] = adjusted_mid
    X_counterfactual_std = (X_counterfactual - X_mean) / X_std
    
    # Extract posterior samples
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))  # (n_samples, n_predictors)
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))  # (n_samples, n_countries)
    
    # Compute predictions for each posterior sample
    # Original: y* = α_i + X* β
    alpha_i_samples = alpha_samples[:, country_idx]
    original_pred_centered = alpha_i_samples + np.dot(X_original_std, beta_samples.T)
    original_pred = original_pred_centered + y_mean
    
    # Counterfactual: y* = α_i + X*_cf β
    counterfactual_pred_centered = alpha_i_samples + np.dot(X_counterfactual_std, beta_samples.T)
    counterfactual_pred = counterfactual_pred_centered + y_mean
    
    # Compute change
    change = counterfactual_pred - original_pred
    
    # Compute summary statistics (mean and 94% HDI)
    def compute_summary(samples):
        mean = np.mean(samples)
        hdi = az.hdi(samples, hdi_prob=0.94)
        return {
            'mean': mean,
            'hdi_3%': hdi[0],
            'hdi_97%': hdi[1],
        }
    
    return {
        'country': country,
        'year': year,
        'indicator': indicator_name,
        'current_gap': current_gap,
        'target_gap': target_gap,
        'target_country': target_country,
        'target_year': target_year,
        'original_prediction': original_pred,
        'counterfactual_prediction': counterfactual_pred,
        'change': change,
        'original_summary': compute_summary(original_pred),
        'counterfactual_summary': compute_summary(counterfactual_pred),
        'change_summary': compute_summary(change),
    }


def compute_importance_summary(trace, metadata):
    """
    Compute importance measures from posterior samples.
    
    Parameters
    ----------
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
    metadata : dict
        Metadata dictionary with transformation parameters
        
    Returns
    -------
    pd.DataFrame
        DataFrame with importance measures sorted by importance (descending)
    """
    predictors = metadata['predictors']
    
    # Extract posterior samples for beta coefficients
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
    
    # Get SD values used for standardization
    X_std = np.array(metadata['X_std'])
    
    # Compute importance measure: |β_standardized| × SD_original
    importance_samples = np.abs(beta_samples) * X_std[np.newaxis, :]
    
    # Create importance summary
    importance_summary = pd.DataFrame({
        'Predictor': predictors,
        'Importance_mean': importance_samples.mean(axis=0),
        'Importance_hdi_3%': np.percentile(importance_samples, 3, axis=0),
        'Importance_hdi_97%': np.percentile(importance_samples, 97, axis=0),
    })
    
    # Sort by importance (descending)
    importance_summary = importance_summary.sort_values('Importance_mean', ascending=False)
    
    return importance_summary


def _prepare_viz_dataframe(counterfactual_results):
    """Helper function to prepare visualization DataFrame."""
    return pd.DataFrame({
        'Indicator': [r['indicator'] for r in counterfactual_results],
        'Change_mean': [r['change_summary']['mean'] for r in counterfactual_results],
        'Change_lower': [r['change_summary']['hdi_3%'] for r in counterfactual_results],
        'Change_upper': [r['change_summary']['hdi_97%'] for r in counterfactual_results],
    })


def plot_counterfactual_forest(
    counterfactual_results, 
    output_prefix='counterfactual_effects_usa_2019',
    target_name='HALE gap',
    country='USA',
    year=2019,
    subtext=None,
    logo=False
):
    """
    Create forest plot of counterfactual effects (all indicators).
    
    Parameters
    ----------
    counterfactual_results : list
        List of counterfactual result dictionaries from counterfactual_predictions_bayesian
    output_prefix : str
        Prefix for output filenames (e.g., 'counterfactual_effects_usa_2019_hale')
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    country : str
        Country code for title (e.g., 'USA')
    year : int
        Reference year for title
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo
        
    Returns
    -------
    str
        Path to saved figure file
    """
    # Create DataFrame with full results
    viz_df = _prepare_viz_dataframe(counterfactual_results)
    
    # Sort by mean change
    viz_df = viz_df.sort_values('Change_mean', ascending=False)
    
    # Forest plot (all indicators)
    fig, ax = plt.subplots(figsize=(8, 4))
    
    y_pos = np.arange(len(viz_df))
    colors = [AIBM_COLORS['crimson'] if x < 0 else AIBM_COLORS['blue'] 
              for x in viz_df['Change_mean']]
    
    # Plot error bars (94% HDI)
    for i, (idx, row) in enumerate(viz_df.iterrows()):
        ax.errorbar(row['Change_mean'], i, 
                    xerr=[[row['Change_mean'] - row['Change_lower']], 
                          [row['Change_upper'] - row['Change_mean']]],
                    fmt='s', color=colors[i], capsize=4, capthick=1, 
                    markersize=4, elinewidth=1)
    
    # Add vertical line at zero
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    # Set labels (human-readable: use PREDICTOR_LABELS, fallback to spaces)
    ax.set_yticks(y_pos)
    # Indicator is short form (e.g. 'Alcohol') but PREDICTOR_LABELS uses 'Gap_Alcohol'
    y_labels = [PREDICTOR_LABELS.get(f'Gap_{ind}', ind.replace('_', ' ')) for ind in viz_df['Indicator']]
    ax.set_yticklabels(y_labels)
    ax.set_xlabel(f'Change in {target_name} (years)')
    country_name = code_to_who_country.get(country, country)
    add_title(f'Counterfactual Effects: {country_name}', 
              f'Hypothetical change in life expectancy gap for each cause specific death rate, {country_name} ({year})', 
              pad=25, x=0, y=1.03)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add legend
    legend_elements = [
        Patch(facecolor=AIBM_COLORS['crimson'], label='Gap-Closing (reduces gap)'),
        Patch(facecolor=AIBM_COLORS['blue'], label='Gap-Widening (increases gap)')
    ]
    # ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.21), align_to_axes=True)
    
    plt.tight_layout()
    filename = f'figs/{output_prefix}_bayesian.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    return filename


def plot_country_intercepts(
    trace, metadata,
    target_name='Life Expectancy gap',
    output_prefix='country_intercepts',
    subtext=None,
    logo=False
):
    """
    Create forest plot of country intercepts (random effects) with 94% credible intervals.

    Similar in style to plot_counterfactual_forest: horizontal plot with error bars,
    vertical line at zero (grand mean), AIBM styling.

    Parameters
    ----------
    trace : arviz.InferenceData
        Posterior trace from MCMC sampling
    metadata : dict
        Metadata with 'countries' and 'y_mean'
    target_name : str
        Name of target variable for axis label
    output_prefix : str
        Prefix for output filename; figure saved to figs/{output_prefix}_intercepts.png
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo

    Returns
    -------
    str
        Path to saved figure file
    """
    countries = np.array(metadata['countries'])

    # Extract alpha samples: (n_samples, n_countries)
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))

    # Compute mean and 94% HDI per country (alpha is in centered space)
    alpha_mean = alpha_samples.mean(axis=0)
    hdi_vals = np.percentile(alpha_samples, [3, 97], axis=0)
    alpha_lower = hdi_vals[0]
    alpha_upper = hdi_vals[1]

    # Sort by mean intercept (descending: highest baseline first)
    sort_idx = np.argsort(alpha_mean)[::-1]
    countries_sorted = countries[sort_idx]
    alpha_mean_sorted = alpha_mean[sort_idx]
    alpha_lower_sorted = alpha_lower[sort_idx]
    alpha_upper_sorted = alpha_upper[sort_idx]

    # Forest plot
    fig, ax = plt.subplots(figsize=(7, 9))
    y_pos = np.arange(len(countries_sorted))
    colors = [AIBM_COLORS['crimson'] if x < 0 else AIBM_COLORS['blue']
              for x in alpha_mean_sorted]

    for i in range(len(countries_sorted)):
        ax.errorbar(alpha_mean_sorted[i], i,
                    xerr=[[alpha_mean_sorted[i] - alpha_lower_sorted[i]],
                          [alpha_upper_sorted[i] - alpha_mean_sorted[i]]],
                    fmt='d', color=colors[i], capsize=4, capthick=1,
                    markersize=4, elinewidth=1)

    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([code_to_who_country.get(c, c) for c in countries_sorted])
    ax.set_ylim(len(countries_sorted) - 0.5, -0.5)  # Tighten y-axis to data (no extra margin)
    ax.set_xlabel(f'Country intercept (years)')
    add_title('Country Intercepts', 
              f'{target_name} random effects by country, 94% credible intervals', 
              pad=25, x=0, y=1.01)

    if subtext:
        add_subtext(subtext, x=0, y=-0.06, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.06), align_to_axes=True)

    plt.tight_layout()
    filename = f'figs/{output_prefix}_intercepts.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    return filename


def plot_counterfactual_by_type(
    counterfactual_results, 
    output_prefix='counterfactual_effects_usa_2019',
    target_name='HALE gap',
    country='USA',
    year=2019,
    subtext=None,
    logo=False
):
    """
    Create two-panel plot of counterfactual effects (gap-closing vs gap-widening).
    
    Parameters
    ----------
    counterfactual_results : list
        List of counterfactual result dictionaries from counterfactual_predictions_bayesian
    output_prefix : str
        Prefix for output filenames (e.g., 'counterfactual_effects_usa_2019_hale')
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    country : str
        Country code for title (e.g., 'USA')
    year : int
        Reference year for title
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo
        
    Returns
    -------
    str
        Path to saved figure file
    """
    # Create DataFrame with full results
    viz_df = _prepare_viz_dataframe(counterfactual_results)
    
    # Two-panel plot (by type)
    gap_closing_viz = viz_df[viz_df['Change_mean'] < 0].copy().sort_values('Change_mean', ascending=True)
    gap_widening_viz = viz_df[viz_df['Change_mean'] > 0].copy().sort_values('Change_mean', ascending=False)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    
    # Gap-closing indicators (left panel)
    if len(gap_closing_viz) > 0:
        y_pos1 = np.arange(len(gap_closing_viz))
        for i, (idx, row) in enumerate(gap_closing_viz.iterrows()):
            ax1.errorbar(row['Change_mean'], i, 
                        xerr=[[row['Change_mean'] - row['Change_lower']], 
                              [row['Change_upper'] - row['Change_mean']]],
                        fmt='o', color=AIBM_COLORS['crimson'], capsize=5, capthick=2, 
                        markersize=8, elinewidth=2)
        ax1.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        ax1.set_yticks(y_pos1)
        ax1.set_yticklabels([PREDICTOR_LABELS.get(f'Gap_{ind}' if not str(ind).startswith('Gap_') else ind, ind.replace('_', ' ')) for ind in gap_closing_viz['Indicator']])
        ax1.set_xlabel(f'Change in {target_name} (years)', fontsize=11)
        ax1.set_title('Gap-Closing Indicators\n(Reduce Gap)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.invert_xaxis()  # Invert so negative values go left
    
    # Gap-widening indicators (right panel)
    if len(gap_widening_viz) > 0:
        y_pos2 = np.arange(len(gap_widening_viz))
        for i, (idx, row) in enumerate(gap_widening_viz.iterrows()):
            ax2.errorbar(row['Change_mean'], i, 
                        xerr=[[row['Change_mean'] - row['Change_lower']], 
                              [row['Change_upper'] - row['Change_mean']]],
                        fmt='o', color=AIBM_COLORS['blue'], capsize=5, capthick=2, 
                        markersize=8, elinewidth=2)
        ax2.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        ax2.set_yticks(y_pos2)
        ax2.set_yticklabels([PREDICTOR_LABELS.get(f'Gap_{ind}' if not str(ind).startswith('Gap_') else ind, ind.replace('_', ' ')) for ind in gap_widening_viz['Indicator']])
        ax2.set_xlabel(f'Change in {target_name} (years)', fontsize=11)
        ax2.set_title('Gap-Widening Indicators\n(Increase Gap)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
    
    country_name = code_to_who_country.get(country, country)
    plt.suptitle(f'Counterfactual Effects by Type: {country_name}\n{country} ({year}), 94% Credible Intervals', 
                 fontsize=14, fontweight='bold', y=1.02)
    if subtext:
        add_subtext(subtext, x=0, y=-0.12, align_to_axes=False)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.15), align_to_axes=False)
    plt.tight_layout()
    filename = f'figs/{output_prefix}_by_type_bayesian.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    return filename


def plot_counterfactual_bar(
    counterfactual_results, 
    output_prefix='counterfactual_effects_usa_2019',
    target_name='HALE gap',
    country='USA',
    year=2019,
    subtext=None,
    logo=False
):
    """
    Create bar chart of counterfactual effects (sorted by magnitude).
    
    Parameters
    ----------
    counterfactual_results : list
        List of counterfactual result dictionaries from counterfactual_predictions_bayesian
    output_prefix : str
        Prefix for output filenames (e.g., 'counterfactual_effects_usa_2019_hale')
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    country : str
        Country code for title (e.g., 'USA')
    year : int
        Reference year for title
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo
        
    Returns
    -------
    str
        Path to saved figure file
    """
    # Create DataFrame with full results
    viz_df = _prepare_viz_dataframe(counterfactual_results)
    
    # Bar chart (sorted by magnitude)
    viz_df_abs = viz_df.copy()
    viz_df_abs['Abs_change'] = viz_df_abs['Change_mean'].abs()
    viz_df_abs = viz_df_abs.sort_values('Abs_change', ascending=True)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    y_pos = np.arange(len(viz_df_abs))
    colors = [AIBM_COLORS['crimson'] if x < 0 else AIBM_COLORS['blue'] 
              for x in viz_df_abs['Change_mean']]
    
    # Create horizontal bar chart
    bars = ax.barh(y_pos, viz_df_abs['Change_mean'], color=colors, alpha=0.7)
    
    # Add error bars
    for i, (idx, row) in enumerate(viz_df_abs.iterrows()):
        ax.errorbar(row['Change_mean'], i, 
                    xerr=[[row['Change_mean'] - row['Change_lower']], 
                          [row['Change_upper'] - row['Change_mean']]],
                    fmt='none', color='black', capsize=3, capthick=1, 
                    elinewidth=1, alpha=0.6)
    
    # Add vertical line at zero
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    # Set labels (human-readable: use PREDICTOR_LABELS, fallback to spaces)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([PREDICTOR_LABELS.get(f'Gap_{ind}' if not str(ind).startswith('Gap_') else ind, ind.replace('_', ' ')) for ind in viz_df_abs['Indicator']])
    ax.set_xlabel(f'Change in {target_name} (years)', fontsize=12)
    country_name = code_to_who_country.get(country, country)
    add_title(f'Counterfactual Effects: {country_name}', f'Sorted by magnitude, {country} ({year}), 94% Credible Intervals', pad=25, x=0, y=1.04)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add legend
    legend_elements = [
        Patch(facecolor=AIBM_COLORS['crimson'], label='Gap-Closing (reduces gap)'),
        Patch(facecolor=AIBM_COLORS['blue'], label='Gap-Widening (increases gap)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.21), align_to_axes=True)
    
    plt.tight_layout()
    filename = f'figs/{output_prefix}_bar_bayesian.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()
    return filename


def create_counterfactual_visualizations(
    counterfactual_results, 
    output_prefix='counterfactual_effects_usa_2019',
    target_name='HALE gap',
    country='USA',
    year=2019,
    subtext=None,
    logo=False
):
    """
    Create three visualization plots for counterfactual analysis results.
    
    This is a convenience function that calls all three individual plot functions.
    For displaying figures in notebooks, use the individual functions in separate cells.
    
    Parameters
    ----------
    counterfactual_results : list
        List of counterfactual result dictionaries from counterfactual_predictions_bayesian
    output_prefix : str
        Prefix for output filenames (e.g., 'counterfactual_effects_usa_2019_hale')
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
        
    Returns
    -------
    dict
        Dictionary with paths to saved figure files
    """
    saved_files = {}
    saved_files['forest'] = plot_counterfactual_forest(counterfactual_results, output_prefix, target_name, country, year, subtext, logo)
    saved_files['by_type'] = plot_counterfactual_by_type(counterfactual_results, output_prefix, target_name, country, year, subtext, logo)
    saved_files['bar'] = plot_counterfactual_bar(counterfactual_results, output_prefix, target_name, country, year, subtext, logo)
    return saved_files


def format_counterfactual_table(
    counterfactual_results, 
    importance_summary, 
    code_to_country_dict=code_to_who_country,
    target_name='gap'
):
    """
    Format counterfactual results into a table DataFrame.
    
    Parameters
    ----------
    counterfactual_results : list
        List of counterfactual result dictionaries
    importance_summary : pd.DataFrame
        DataFrame with importance measures
    code_to_country_dict : dict
        Dictionary mapping country codes to country names
    target_name : str
        Name of target variable for column header (e.g., 'HALE gap' or 'Life Expectancy gap')
        
    Returns
    -------
    tuple
        (formatted_df, full_df) where formatted_df is for display and full_df has all columns
    """
    results = []
    
    for result in counterfactual_results:
        indicator_name = result['indicator']
        gap_pred = f'Gap_{indicator_name}'
        
        # Get importance for this predictor
        importance_row = importance_summary[importance_summary['Predictor'] == gap_pred]
        if len(importance_row) > 0:
            importance = importance_row['Importance_mean'].iloc[0]
        else:
            importance = 0.0
        
        # Get country name for target country
        target_country_code = result['target_country']
        if target_country_code:
            target_country_name = code_to_country_dict.get(target_country_code, target_country_code)
            if result['target_year']:
                target_info = f"{target_country_name} ({result['target_year']})"
            else:
                target_info = target_country_name
        else:
            target_info = ""
        
        # Format change with uncertainty
        change_mean = result['change_summary']['mean']
        change_lower = result['change_summary']['hdi_3%']
        change_upper = result['change_summary']['hdi_97%']
        change_str = f"{change_mean:.3f} [{change_lower:.3f}, {change_upper:.3f}]"
        
        results.append({
            'Indicator': indicator_name,
            'Current gap': result['current_gap'],
            'Target gap': result['target_gap'],
            'Target Country-Year': target_info,
            f'Change in {target_name} (years)': change_str,
            'Change mean': change_mean,  # For sorting
            'Importance': importance,  # For sorting
        })
    
    df = pd.DataFrame(results)
    # Sort by importance (descending), then by absolute change (descending)
    df['Abs_change'] = df['Change mean'].abs()
    df = df.sort_values(['Importance', 'Abs_change'], ascending=False)
    df = df.drop('Abs_change', axis=1)  # Remove temporary column
    
    # Select columns for output (exclude sorting columns)
    change_col = f'Change in {target_name} (years)'
    df_output = df[['Indicator', 'Current gap', 'Target gap', 'Target Country-Year', change_col]].copy()
    
    return df_output, df


def plot_predicted_vs_actual_over_time(
    country, trace, metadata, panel_df, country_to_idx, 
    target_name='HALE gap', target_col='HALE_gap', output_filename=None,
    subtext=None, logo=False
):
    """
    Plot predicted vs actual gap over time for a specific country.
    
    Parameters
    ----------
    country : str
        Country code (e.g., 'USA')
    trace : arviz.InferenceData
        Posterior trace from Bayesian model
    metadata : dict
        Model metadata with X_mean, X_std, y_mean, predictors, countries
    panel_df : pd.DataFrame
        Panel dataset with country, Year, and target_col columns
    country_to_idx : dict
        Mapping from country codes to indices
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    target_col : str
        Column name in panel_df for target variable (e.g., 'HALE_gap' or 'LE_gap')
    output_filename : str or Path, optional
        Filename to save the figure. If None, figure is not saved.
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo
        
    Returns
    -------
    fig, ax : matplotlib figure and axes
    """
    # Get data for this country
    country_data = panel_df[panel_df['country'] == country].copy()
    country_data = country_data.sort_values('Year')
    
    if len(country_data) == 0:
        raise ValueError(f"No data found for country: {country}")
    
    # Get transformation parameters
    X_mean = np.array(metadata['X_mean'])
    X_std = np.array(metadata['X_std'])
    y_mean = metadata['y_mean']
    predictors = metadata['predictors']
    countries = np.array(metadata['countries'])
    
    # Get country index
    country_idx_val = country_to_idx[country]
    
    # Extract posterior samples
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))
    alpha_i_samples = alpha_samples[:, country_idx_val]
    
    # Compute predictions for each year
    years = country_data['Year'].values
    actual_values = country_data[target_col].values
    predicted_means = []
    predicted_lower = []
    predicted_upper = []
    
    for idx, row in country_data.iterrows():
        # Build predictor vector (standardized)
        X_current = np.array([row[p] for p in predictors])
        X_current_std = (X_current - X_mean) / X_std
        
        # Compute predictions for each posterior sample
        pred_centered = alpha_i_samples + np.dot(X_current_std, beta_samples.T)
        pred_original = pred_centered + y_mean
        
        # Compute summary
        pred_mean = np.mean(pred_original)
        pred_hdi = az.hdi(pred_original, hdi_prob=0.94)
        
        predicted_means.append(pred_mean)
        predicted_lower.append(pred_hdi[0])
        predicted_upper.append(pred_hdi[1])
    
    predicted_means = np.array(predicted_means)
    predicted_lower = np.array(predicted_lower)
    predicted_upper = np.array(predicted_upper)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot actual values: line only, no markers, country signature color
    color = get_country_color(country)
    ax.plot(years, actual_values, '-', color=color, 
            label='Actual', linewidth=2, zorder=3)
    
    # Plot predicted values: markers with error bars, no lines, gray
    yerr_lo = predicted_means - predicted_lower
    yerr_hi = predicted_upper - predicted_means
    ax.errorbar(years, predicted_means, yerr=[yerr_lo, yerr_hi], 
                fmt='o', color='gray', label='Predicted (94% HDI)', 
                capsize=3, markersize=6, zorder=3)
    
    # Formatting
    country_name = code_to_who_country.get(country, country)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel(f'{target_name} (years)', fontsize=12)
    ax.set_title(f'Predicted vs Actual {target_name}: {country_name} ({country})', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add statistics text box
    residuals = actual_values - predicted_means
    mae = np.mean(np.abs(residuals))
    rmse = np.sqrt(np.mean(residuals**2))
    r2 = 1 - np.sum(residuals**2) / np.sum((actual_values - np.mean(actual_values))**2)
    
    stats_text = f'MAE: {mae:.3f} years\nRMSE: {rmse:.3f} years\nR²: {r2:.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    if subtext:
        add_subtext(subtext, x=0, y=-0.22, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(1.0, -0.25), align_to_axes=True)
    
    plt.tight_layout()
    
    if output_filename:
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    return fig, ax


def compute_residuals_panel(trace, metadata, panel_df, target_col='LE_gap'):
    """
    Compute predicted values and residuals for all observations in the panel.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: country, Year, actual, predicted, residual
    """
    X_mean = np.array(metadata['X_mean'])
    X_std = np.array(metadata['X_std'])
    y_mean = metadata['y_mean']
    predictors = metadata['predictors']
    countries = np.array(metadata['countries'])
    country_to_idx = {c: i for i, c in enumerate(countries)}
    
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))
    
    results = []
    for idx, row in panel_df.iterrows():
        country = row['country']
        year = row['Year']
        actual = row[target_col]
        X_current = np.array([row[p] for p in predictors])
        X_current_std = (X_current - X_mean) / X_std
        alpha_i = alpha_samples[:, country_to_idx[country]]
        pred_centered = alpha_i + np.dot(X_current_std, beta_samples.T)
        pred_original = pred_centered + y_mean
        predicted = np.mean(pred_original)
        results.append({'country': country, 'Year': year, 'actual': actual, 'predicted': predicted, 'residual': actual - predicted})
    
    return pd.DataFrame(results)


def plot_residuals_by_country(residuals_df, target_name='Life Expectancy gap', 
                              country_labels=None, output_filename=None,
                              title=None, subtitle=None, subtext=None, logo=False):
    """
    Horizontal boxplot of residuals by country, sorted by IQR (best fit at top).
    AIBM style: title, subtitle, subtext, logo when provided.
    
    Parameters
    ----------
    residuals_df : pd.DataFrame
        From compute_residuals_panel, with columns: country, residual
    target_name : str
        Name of target for axis label
    country_labels : dict, optional
        Mapping from country code to display name (e.g., code_to_who_country)
    output_filename : str or Path, optional
        Where to save the figure
    title : str, optional
        Main title (AIBM style)
    subtitle : str, optional
        Subtitle below main title
    subtext : str, optional
        Source/caption below plot
    logo : bool, optional
        If True, add logo
    """
    # Compute IQR per country; sort ascending so smallest (best fit) is last = top of plot
    iqr = residuals_df.groupby('country')['residual'].apply(lambda x: x.quantile(0.75) - x.quantile(0.25))
    country_order = iqr.sort_values().index.tolist()[::-1]
    
    # Build data for boxplot: list of residual arrays in order
    data = [residuals_df.loc[residuals_df['country'] == c, 'residual'].values for c in country_order]
    labels = [country_labels.get(c, c) if country_labels else c for c in country_order]
    
    fig, ax = plt.subplots(figsize=(8, 9))
    line_props = dict(color=AIBM_COLORS['dark_gray'], linewidth=0.8)
    bp = ax.boxplot(
        data, vert=False, patch_artist=True, labels=labels,
        boxprops=dict(facecolor=AIBM_COLORS['light_purple'], alpha=0.7, edgecolor=AIBM_COLORS['dark_gray'], linewidth=0.8),
        whiskerprops=line_props,
        capprops=line_props,
        medianprops=line_props,
        flierprops=dict(marker='o', markersize=5, markerfacecolor=AIBM_COLORS['light_purple'], markeredgecolor='none')
    )
    
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel(f'Residual ({target_name}, years)')
    ax.grid(True, axis='x', alpha=0.3)
    
    # AIBM style
    plot_title = title or 'Model residuals by country'
    if subtitle is not None:
        add_title(plot_title, subtitle, pad=25, x=0, y=1.015)
    else:
        ax.set_title(plot_title, loc='left', fontsize=14, fontweight='bold')
    if subtext:
        add_subtext(subtext, x=0, y=-0.07, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(1.0, -0.08), align_to_axes=True)
    
    plt.tight_layout()
    
    if output_filename:
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    
    return fig, ax


def compute_positive_contributions_over_time(
    country, trace, metadata, panel_df, gap_extremes,
    country_to_idx, year_to_idx, target_name='gap',
    target_col=None, reference_year=None, counterfactual_results=None,
    counterfactuals_full=None, target_zero=False
):
    """
    Compute positive-contributing factors (gap-closing) over time for a country.
    
    Parameters
    ----------
    country : str
        Country code (e.g., 'USA')
    trace : arviz.InferenceData
        Posterior trace from Bayesian model
    metadata : dict
        Model metadata with X_mean, X_std, y_mean, predictors, countries
    panel_df : pd.DataFrame
        Panel dataset with country, Year, and target_col columns
    gap_extremes : dict
        Dictionary with gap extremes for each predictor
    country_to_idx : dict
        Mapping from country codes to indices
    year_to_idx : dict
        Mapping from years to indices
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    target_col : str
        Column name in panel_df for target variable (e.g., 'HALE_gap' or 'LE_gap').
        If None, will infer from target_name.
    reference_year : int, optional
        Year to use for identifying gap-closing factors. If None, uses the latest
        available year in the data.
    counterfactual_results : list, optional
        Pre-computed counterfactual results from the main analysis. If provided,
        these will be used to identify gap-closing factors instead of recomputing.
    counterfactuals_full : pd.DataFrame, optional
        Pre-computed full counterfactuals DataFrame. If provided, will be used
        to identify gap-closing factors (ensures exact consistency with aggregate effects).
        Takes precedence over counterfactual_results if both are provided.
    target_zero : bool, default False
        If True, use zero as target gap for each factor. If False, use best attainable
        from gap_extremes (consistent with aggregate effects and forest plot).
        
    Returns
    -------
    pd.DataFrame
        DataFrame with years as index, gap-closing factors as columns, plus
        'Predicted Total' and 'Actual Total' columns
    """
    # Infer target column if not provided
    if target_col is None:
        if 'HALE' in target_name:
            target_col = 'HALE_gap'
        elif 'Life Expectancy' in target_name or 'LE' in target_name:
            target_col = 'LE_gap'
        else:
            raise ValueError(f"Cannot infer target_col from target_name: {target_name}")
    
    # Get all years for country
    country_data = panel_df[panel_df['country'] == country].copy()
    country_years = sorted(country_data['Year'].unique())
    
    # Determine reference year: use latest available year
    if reference_year is None:
        reference_year = max(country_years)
    
    print(f"Computing contributions for {country} across {len(country_years)} years...")
    print(f"Using {reference_year} as reference year for identifying gap-closing factors")
    print(f"Target: {'zero' if target_zero else 'best attainable'} (consistent with aggregate effects)")
    
    # Identify gap-closing factors
    if counterfactuals_full is not None:
        # Use pre-computed counterfactuals_full DataFrame (most reliable - ensures exact consistency)
        # Filter to gap-closing factors (negative change = reduces gap)
        gap_closing = counterfactuals_full[counterfactuals_full['Change mean'] < 0].copy()
        gap_closing_factors = gap_closing['Indicator'].tolist()
        print(f"Using pre-computed counterfactuals_full DataFrame to identify gap-closing factors")
    elif counterfactual_results is not None:
        # Use pre-computed counterfactual results
        # Filter to gap-closing factors (negative change = reduces gap)
        # Exclude COVID from gap-closing factors (check both indicator name and gap predictor name)
        gap_closing_factors = []
        for r in counterfactual_results:
            indicator = r['indicator']
            gap_pred = f'Gap_{indicator}'
            # Exclude COVID variants
            if indicator in ['COVID', 'COVID19'] or gap_pred in ['Gap_COVID', 'Gap_COVID19']:
                continue
            # Only include gap-closing factors (negative change)
            if r['change_summary']['mean'] < 0:
                gap_closing_factors.append(indicator)
        print(f"Using pre-computed counterfactual results to identify gap-closing factors")
    else:
        # Compute counterfactual results for reference year
        gap_predictors = [col for col in panel_df.columns if col.startswith('Gap_')]
        # Exclude COVID from gap-closing factors (it widens the gap)
        gap_predictors = [p for p in gap_predictors if p not in ['Gap_COVID', 'Gap_COVID19']]
        
        reference_results = []
        for gap_pred in gap_predictors:
            # Check if this predictor exists in the model
            if gap_pred not in metadata['predictors']:
                continue
            result = counterfactual_predictions_bayesian(
                country, reference_year, gap_pred,
                trace, metadata, panel_df, gap_extremes,
                country_to_idx, year_to_idx
            )
            reference_results.append(result)
        
        # Identify gap-closing factors (negative change = reduces gap)
        gap_closing_factors = [
            r['indicator'] for r in reference_results 
            if r['change_summary']['mean'] < 0
        ]
    
    print(f"Found {len(gap_closing_factors)} gap-closing factors:")
    print(f"  {', '.join(gap_closing_factors)}")
    
    # Get transformation parameters
    X_mean = np.array(metadata['X_mean'])
    X_std = np.array(metadata['X_std'])
    y_mean = metadata['y_mean']
    predictors = metadata['predictors']
    countries = np.array(metadata['countries'])
    
    # Get country index
    country_idx_val = country_to_idx[country]
    
    # Extract posterior samples
    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))
    alpha_i_samples = alpha_samples[:, country_idx_val]
    
    # Compute contributions for each year
    contributions_data = []
    predicted_means = []
    actual_values = []
    
    for year in country_years:
        year_data = country_data[country_data['Year'] == year]
        if len(year_data) == 0:
            continue
        
        # Get actual value
        actual_gap = year_data[target_col].iloc[0]
        actual_values.append(actual_gap)
        
        # Compute predicted gap for this year
        current_row = year_data.iloc[0]
        X_current = np.array([current_row[p] for p in predictors])
        X_current_std = (X_current - X_mean) / X_std
        
        pred_centered = alpha_i_samples + np.dot(X_current_std, beta_samples.T)
        pred_original = pred_centered + y_mean
        pred_mean = np.mean(pred_original)
        predicted_means.append(pred_mean)
        
        # Compute contributions for each gap-closing factor
        year_contributions = {'Year': year}
        
        for indicator in gap_closing_factors:
            gap_pred = f'Gap_{indicator}'
            # All indicators in gap_closing_factors should be valid since they come from counterfactual_results
            # which were already computed successfully. But check anyway to be safe.
            if gap_pred not in metadata['predictors']:
                print(f"Warning: {gap_pred} not in model predictors, skipping")
                continue
            result = counterfactual_predictions_bayesian(
                country, year, gap_pred,
                trace, metadata, panel_df, gap_extremes,
                country_to_idx, year_to_idx,
                target_zero=target_zero
            )
            # Contribution is the absolute value of the change (since change is negative)
            contribution = abs(result['change_summary']['mean'])
            year_contributions[indicator] = contribution
        
        contributions_data.append(year_contributions)
    
    # Create DataFrame
    contributions_df = pd.DataFrame(contributions_data)
    contributions_df = contributions_df.set_index('Year')
    
    # Add predicted and actual totals
    contributions_df['Predicted Total'] = predicted_means
    contributions_df['Actual Total'] = actual_values
    
    print(f"\nContributions DataFrame shape: {contributions_df.shape}")
    print(f"Years: {contributions_df.index.min()} - {contributions_df.index.max()}")
    
    return contributions_df


def plot_positive_contributions_stacked_area(
    contributions_df, target_name='gap', country='USA',
    output_filename=None,
    subtext=None,
    logo=False,
    show_predicted_actual=False,
    direct_labels=True
):
    """
    Plot stacked area chart of positive contributions over time.
    
    Parameters
    ----------
    contributions_df : pd.DataFrame
        DataFrame from compute_positive_contributions_over_time
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    country : str
        Country code for title
    output_filename : str or Path, optional
        Filename to save the figure. If None, figure is not saved.
    subtext : str, optional
        Source/caption below plot (AIBM style)
    logo : bool, optional
        If True, add AIBM logo
    show_predicted_actual : bool, default True
        If True, plot Predicted Total and Actual Total lines. If False, show stacked areas only.
    direct_labels : bool, default True
        If True, label each area band directly on the right side (no legend for areas).
        
    Returns
    -------
    fig, ax : matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Get factor columns (exclude totals)
    factor_cols = [col for col in contributions_df.columns 
                   if col not in ['Predicted Total', 'Actual Total']]
    
    # Sort factors by contribution in 2023 (or latest year if 2023 not in data)
    sort_year = 2023 if 2023 in contributions_df.index else contributions_df.index.max()
    factor_contrib_2023 = contributions_df.loc[sort_year, factor_cols].sort_values(ascending=False)
    factor_cols_sorted = factor_contrib_2023.index.tolist()
    
    # Create color map for factors
    n_factors = len(factor_cols_sorted)
    colors = plt.cm.Set3(np.linspace(0, 1, n_factors))
    
    # Plot stacked area chart for factors
    ax.stackplot(contributions_df.index, 
                 *[contributions_df[col] for col in factor_cols_sorted],
                 labels=factor_cols_sorted,
                 colors=colors,
                 alpha=0.7)
    
    # Plot predicted and actual totals as lines (optional)
    if show_predicted_actual:
        ax.plot(contributions_df.index, contributions_df['Predicted Total'], 
                'o-', color=AIBM_COLORS['blue'], linewidth=2.5, markersize=8,
                label='Predicted Total', zorder=10)
        ax.plot(contributions_df.index, contributions_df['Actual Total'], 
                's-', color=AIBM_COLORS['crimson'], linewidth=2.5, markersize=8,
                label='Actual Total', zorder=10)
    
    # Direct labels for stacked areas: midpoint of each band at right edge
    x_min_data = contributions_df.index.min()
    x_max_data = contributions_df.index.max()
    # y offsets to nudge overlapping labels (data units) - per country, add as needed
    label_nudge_by_country = {
        'USA': {'UnintentionalInjury': 0.06, 'COVID': 0.14},
        # Add other countries: 'COUNTRY': {'Factor': nudge, ...}
    }
    nudges = label_nudge_by_country.get(country, {})
    if direct_labels:
        cumsum = 0.0
        label_data = []
        for i, factor in enumerate(factor_cols_sorted):
            val = contributions_df[factor].iloc[-1]
            mid_y = cumsum + val / 2.0 + nudges.get(factor, 0)
            label = PREDICTOR_LABELS.get(f'Gap_{factor}', factor.replace('_', ' '))
            label_data.append({'x': x_max_data, 
                               'y': mid_y, 
                               'text': label, 
                               'color': AIBM_COLORS['dark_gray']})
            cumsum += val
        add_direct_line_labels(ax, label_data, x_min=x_min_data, x_max=x_max_data)

    # Restrict x-ticks to data range (avoid 2025 tick from extended axis)
    year_range = x_max_data - x_min_data
    tick_step = 5 if year_range > 10 else 2
    ticks = list(np.arange(x_min_data, x_max_data + 1, tick_step))
    if ticks[-1] != x_max_data:
        ticks.append(int(x_max_data))
    ax.set_xticks(ticks)

    # Y-axis: cap top at data max + small margin (avoid empty space when max < 4)
    data_max = contributions_df[factor_cols_sorted].sum(axis=1).max()
    if show_predicted_actual:
        data_max = max(data_max, contributions_df['Actual Total'].max(), contributions_df['Predicted Total'].max())
    ylim_top = data_max * 1.05
    ax.set_ylim(0, ylim_top)

    # Integer y-ticks only (no 0.5, 1.5, etc.) and remove 0 (collides with first date)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    yticks = [t for t in ax.get_yticks() if t != 0]
    ax.set_yticks(yticks)
    ax.set_ylim(0, ylim_top)  # Re-apply; MaxNLocator/set_yticks can expand limits

    # Formatting
    country_name = code_to_who_country.get(country, country)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel(f'{target_name} (years)', fontsize=12)
    subtitle = ('Stacked contributions and predicted/actual totals (2000-2023)' 
                if show_predicted_actual else 'Stacked contributions (2000-2023)')
    add_title(f'Positive-Contributing Factors: {country_name}', 
              subtitle, pad=25, x=0, y=1.02)
    if show_predicted_actual:
        if direct_labels:
            # Only legend for Predicted/Actual; areas are direct-labeled
            handles, leg_labels = ax.get_legend_handles_labels()
            keep = [h for h, l in zip(handles, leg_labels) if l in ('Predicted Total', 'Actual Total')]
            # ax.legend(handles=keep, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, ncol=1)
        else:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, ncol=1)
    # Grid at integer ticks only, extend only to 2023 (not into label area)
    grid_color = AIBM_COLORS['light_gray']
    grid_alpha = 0.7
    x_grid_max = min(2023, x_max_data)
    for x in ax.get_xticks():
        if x_min_data <= x <= x_grid_max:
            ax.axvline(x, color=grid_color, alpha=grid_alpha, zorder=0)
    ax.hlines(ax.get_yticks(), x_min_data, x_grid_max, color=grid_color, alpha=grid_alpha, zorder=0)
    
    if subtext:
        add_subtext(subtext, x=0, y=-0.15, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.18), align_to_axes=True)
    
    plt.tight_layout()
    
    if output_filename:
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    return fig, ax


def plot_positive_contributions_percentage(
    contributions_df, target_name='gap', country='USA',
    output_filename=None,
    subtext=None,
    logo=False
):
    """
    Plot total positive contributions as percentage of actual gap over time.
    
    Parameters
    ----------
    contributions_df : pd.DataFrame
        DataFrame from compute_positive_contributions_over_time
    target_name : str
        Name of target variable for labels (e.g., 'HALE gap' or 'Life Expectancy gap')
    country : str
        Country code for title
    output_filename : str or Path, optional
        Filename to save the figure. If None, figure is not saved.
        
    Returns
    -------
    fig, ax : matplotlib figure and axes
    pd.Series : percentage values over time
    """
    # Get factor columns (exclude totals)
    factor_cols = [col for col in contributions_df.columns 
                   if col not in ['Predicted Total', 'Actual Total']]
    
    # Sum all positive-contributing factors for each year
    total_positive_contributions = contributions_df[factor_cols].sum(axis=1)
    
    # Compute percentage of actual gap
    percentage_of_actual = (total_positive_contributions / contributions_df['Actual Total']) * 100
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(contributions_df.index, percentage_of_actual, 
            'o-', color=AIBM_COLORS['green'], linewidth=2.5, markersize=8)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Percentage of Actual Gap', fontsize=12)
    country_name = code_to_who_country.get(country, country)
    add_title(f'Positive Contributions as % of Actual {target_name}', f'{country_name} over time', pad=25, x=0, y=1.04)
    ax.grid(True, alpha=0.3)
    
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo and os.path.isfile('logo-hq-small.png'):
        add_logo(filename='logo-hq-small.png', location=(0.99, -0.21), align_to_axes=True)
    
    # Add horizontal line at 100% for reference
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='100%')
    
    # Add text annotation with summary statistics
    mean_pct = percentage_of_actual.mean()
    ax.text(0.02, 0.98, f'Mean: {mean_pct:.1f}%', transform=ax.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    if output_filename:
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    # Display summary statistics
    print(f"\nSummary Statistics:")
    print(f"  Mean percentage: {mean_pct:.2f}%")
    print(f"  Min percentage: {percentage_of_actual.min():.2f}%")
    print(f"  Max percentage: {percentage_of_actual.max():.2f}%")
    print(f"  Range: {percentage_of_actual.max() - percentage_of_actual.min():.2f} percentage points")
    
    return fig, ax, percentage_of_actual


def publish_datawrapper_table(
    df,
    title='',
    intro='',
    access_token=None,
    column_number_formats=None,
    default_float_number_format='0.0',
):
    """
    Create a Datawrapper table visualization, upload ``df``, and publish.

    Requires the ``datawrapper`` package (``pip install datawrapper``) and
    ``DATAWRAPPER_API_TOKEN`` in the environment unless ``access_token`` is
    passed. Matches the workflow in ``datawrapper.md`` at the repo root.

    For **table** charts, number formats live in ``metadata.visualize.columns``
    (each column can set ``"format": "0.0"`` etc.), not in
    ``metadata.data["column-format"]``. After ``add_data``, this function
    ``PATCH``es ``metadata.visualize.columns`` with those strings (see Datawrapper
    Academy: custom number formats).

    Parameters
    ----------
    df : pd.DataFrame
        Table rows (column headers become Datawrapper columns).
    title : str
        Chart title (often left empty; use ``intro`` for caption text).
    intro : str
        Short description shown above the table (Datawrapper ``metadata.describe.intro``).
    access_token : str, optional
        API token; defaults to ``os.environ['DATAWRAPPER_API_TOKEN']``.
    column_number_formats : dict mapping str to str, optional
        Overrides for specific columns. These take precedence over
        ``default_float_number_format`` for float columns (see Datawrapper
        Academy: custom number formats).
    default_float_number_format : str or None
        If a string (default ``0.0``), every float column not listed in
        ``column_number_formats`` gets that format. If ``None``, only columns
        named in ``column_number_formats`` are patched.

    Returns
    -------
    dict
        ``chart_id``, ``public_url`` (embed page), and ``edit_url``.
    """
    import requests
    from datawrapper import Datawrapper

    token = access_token or os.getenv('DATAWRAPPER_API_TOKEN')
    if not token:
        raise RuntimeError(
            'Set DATAWRAPPER_API_TOKEN or pass access_token= to publish_datawrapper_table'
        )

    dw = Datawrapper(access_token=token)
    kwargs = dict(title=title or '', chart_type='tables')
    if intro:
        kwargs['metadata'] = {'describe': {'intro': intro}}
    chart_info = dw.create_chart(**kwargs)
    chart_id = chart_info['id']
    dw.add_data(chart_id=chart_id, data=df)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    merged_formats = dict(column_number_formats or {})
    if default_float_number_format is not None:
        for col in df.columns:
            if col in merged_formats:
                continue
            if pd.api.types.is_float_dtype(df[col]):
                merged_formats[col] = default_float_number_format

    if merged_formats:
        # Tables read formats from Refine (visualize), not Check (data.column-format).
        patch_columns = {
            col: {'format': fmt}
            for col, fmt in merged_formats.items()
            if col in df.columns
        }
        if patch_columns:
            patch_url = f'https://api.datawrapper.de/v3/charts/{chart_id}'
            patch = {'metadata': {'visualize': {'columns': patch_columns}}}
            r = requests.patch(patch_url, headers=headers, json=patch)
            r.raise_for_status()

    publish_url = f'https://api.datawrapper.de/v3/charts/{chart_id}/publish'
    response = requests.post(publish_url, headers=headers)
    response.raise_for_status()
    body = response.json()
    public_url = body.get('url')
    edit_url = f'https://www.datawrapper.de/_/{chart_id}/'
    return {
        'chart_id': chart_id,
        'public_url': public_url,
        'edit_url': edit_url,
    }

