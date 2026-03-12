"""Figure utilities for time series plotting."""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import arviz as az
from utils import get_oecd, code_to_who_country, add_title, add_subtext, add_logo, AIBM_COLORS

# Map Gap_* column names to human-readable labels for coefficient/importance plots
PREDICTOR_LABELS = {
    'Gap_Alcohol': 'Alcohol',
    'Gap_Suicide': 'Suicide',
    'Gap_Homicide': 'Homicide',
    'Gap_RoadTraffic': 'Road Traffic',
    'Gap_Cardiovascular': 'Cardiovascular',
    'Gap_Diabetes': 'Diabetes',
    'Gap_Neoplasms': 'Cancer',
    'Gap_ChronicRespiratory': 'Chronic Respiratory',
    'Gap_LiverDisease': 'Liver Disease',
    'Gap_UnintentionalInjury': 'Injury',
    'Gap_DrugDisorder': 'Drug Disorders',
    'Gap_COVID': 'COVID-19',
}

# Color mapping for countries - ensures consistent colors across plots
COUNTRY_COLORS = {
    # Major countries with distinctive colors
    'USA': '#002868',      # USA flag blue
    'GBR': '#C8102E',      # UK flag red
    'JPN': '#2ca02c',      # Green
    'DEU': '#ff7f0e',      # Orange
    'FRA': '#9467bd',      # Purple
    'CAN': '#8c564b',      # Brown
    'AUS': '#e377c2',      # Pink
    'KOR': '#ED1C27',      # Red
    'ITA': '#bcbd22',      # Olive
    'ESP': '#17becf',      # Cyan
    'NLD': '#FF6600',      # Orange
    'BEL': '#c5b0d5',      # Light purple
    'SWE': '#006AA7',      # Flag blue
    'NOR': '#00205B',      # Flag blue
    'DNK': '#dbdb8d',      # Light yellow-green
    'FIN': '#9edae5',      # Light cyan
    'CHE': '#ffbb78',      # Light orange
    'AUT': '#98df8a',      # Light green
    'POL': '#ff9896',      # Light red
    'PRT': '#c5b0d5',      # Light purple
    'GRC': '#c49c94',      # Light brown
    'IRL': '#009A44',      # Flag green
    'NZL': '#dbdb8d',      # Light yellow-green
    'ISL': '#9edae5',      # Light cyan
    'LUX': '#ffbb78',      # Light orange
    'CZE': '#98df8a',      # Light green
    'HUN': '#d62728',      # Red
    'SVK': '#2ca02c',      # Green
    'SVN': '#ff7f0e',      # Orange
    'EST': '#9467bd',      # Purple
    'LVA': '#8c564b',      # Brown
    'LTU': '#046A38',      # Green
    'ISR': '#7f7f7f',      # Gray
    'CHL': '#bcbd22',      # Olive
    'COL': '#FFCD00',      # Colombia yellow 
    'CRI': '#ff9896',      # Light red
    'MEX': '#006341',      # Flag green
    'TUR': '#C8102E',      # Flag red
}

def add_direct_line_labels(ax, label_data, extension_frac=0.12, min_extension=2.5, x_min=None, x_max=None):
    """
    Add direct labels on the right side of a time series plot.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to add labels to
    label_data : list of dict
        Each dict has keys: x, y, text, color (e.g. endpoint of each line)
    extension_frac : float
        Fraction of x-range to extend for label space
    min_extension : float
        Minimum x-axis extension in data units
    x_min, x_max : float, optional
        Data range for axis and spine. If None, use current axes limits (avoids bug when
        all label points share the same x, e.g. last year only).
    """
    if not label_data:
        return
    if x_min is None or x_max is None:
        x_min, x_max = ax.get_xlim()
    x_range = x_max - x_min
    extension = max(x_range * extension_frac, min_extension)
    ax.set_xlim(x_min, x_max + extension)
    label_x = x_max + extension * 0.1
    sorted_data = sorted(label_data, key=lambda d: d['y'], reverse=True)
    for d in sorted_data:
        ax.text(label_x, d['y'], f'  {d["text"]}', color=d['color'], fontsize=9,
                va='center', ha='left', zorder=3)
    # Restrict bottom spine to data range (not extended area)
    ax.spines['bottom'].set_bounds(x_min, x_max)


def get_country_color(code, default_color='gray'):
    """
    Get the signature color for a country code.
    
    Parameters
    ----------
    code : str
        Country code (e.g., 'USA', 'GBR')
    default_color : str
        Default color to use if country not in mapping
        
    Returns
    -------
    str
        Color code (hex or named color)
    """
    return COUNTRY_COLORS.get(code, default_color)


def plot_gap_timeseries(df, gap_col, countries=None, oecd_avg=True, title=None, ylabel=None, 
                        selected_countries=None, label_lines=True, subtitle=None, subtext=None,
                        logo=None):
    """
    Plot gap time series for selected countries and OECD average.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with Year, Code, Country, and gap_col columns
    gap_col : str
        Name of the gap column to plot
    countries : list, optional
        List of country codes to plot. If None, plots all OECD countries.
    oecd_avg : bool
        Whether to include OECD average line
    title : str, optional
        Plot title (AIBM style: left-aligned)
    ylabel : str, optional
        Y-axis label
    selected_countries : list, optional
        List of country codes to highlight with colors. Others will be gray.
        If None, uses the countries parameter.
    label_lines : bool
        If True, label lines directly on the right side instead of using a legend.
        If False, use a traditional legend.
    subtitle : str, optional
        Subtitle below main title (AIBM style)
    subtext : str, optional
        Source/caption text below plot (e.g., "Source: OWID")
    logo : str or bool, optional
        If True, add logo from logo-hq-small.png. If str, path to logo file.
        Skipped if file does not exist.
    """
    # Filter to OECD countries
    # get_oecd expects Code as index, so set it temporarily
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Add Country column if missing
    if 'Country' not in df_oecd.columns:
        df_oecd['Country'] = df_oecd['Code'].map(code_to_who_country)
    
    # Determine which countries to plot
    if countries is None:
        countries = df_oecd['Code'].unique()
    
    # Determine which countries are selected (for coloring)
    if selected_countries is None:
        selected_countries = countries
    
    # Create figure with extra space on the right for labels if needed
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Get all OECD countries for background
    all_oecd = df_oecd['Code'].unique()
    
    # Plot non-selected countries in gray (background)
    non_selected = [c for c in all_oecd if c not in selected_countries]
    for code in non_selected:
        country_data = df_oecd[df_oecd['Code'] == code]
        if not country_data.empty:
            ax.plot(country_data['Year'], country_data[gap_col], 
                   color='gray', alpha=0.3, linewidth=0.8, zorder=1)
    
    # Plot selected countries with colors
    label_data = []  # Store label information for later placement
    
    for code in selected_countries:
        country_data = df_oecd[df_oecd['Code'] == code]
        if not country_data.empty:
            country_name = country_data['Country'].iloc[0]
            color = get_country_color(code)
            line = ax.plot(country_data['Year'], country_data[gap_col], 
                          color=color, alpha=0.9, linewidth=1.5, 
                          label=country_name, zorder=2)
            
            # Store label information for later placement
            if label_lines:
                # Get the last data point
                last_year = country_data['Year'].max()
                last_value = country_data[country_data['Year'] == last_year][gap_col].iloc[0]
                label_data.append({
                    'x': last_year,
                    'y': last_value,
                    'text': country_name,
                    'color': color
                })
    
    # Plot OECD average (no direct label)
    if oecd_avg:
        oecd_avg_by_year = df_oecd.groupby('Year')[gap_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color=AIBM_COLORS['dark_gray'], linewidth=1.5, linestyle='--', 
               label='OECD Average', zorder=2)

    # Formatting
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel or gap_col)
    # AIBM style: title left-aligned; use add_title for title+subtitle, else ax.set_title with loc="left"
    plot_title = title or f'{gap_col} Over Time'
    if subtitle is not None:
        add_title(plot_title, subtitle, pad=25, x=0, y=1.04)
    else:
        ax.set_title(plot_title, loc="left")
    ax.grid(True, alpha=0.3)
    
    # Only show legend if not using direct labels
    if not label_lines:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    else:
        max_year = df_oecd['Year'].max()
        min_year = df_oecd['Year'].min()
        add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year)
        year_range = max_year - min_year
        tick_step = 1 if year_range <= 5 else 5
        ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
        ax.spines['left'].set_visible(False)
    
    # AIBM style: subtext and logo below plot (aligned with axes)
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo:
        logo_path = logo if isinstance(logo, str) else "logo-hq-small.png"
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.21), align_to_axes=True)
    
    plt.tight_layout()
    return fig, ax


def plot_rate_timeseries(df, rate_col, countries=None, oecd_avg=True, title=None, ylabel=None,
                         selected_countries=None, label_lines=True, subtitle=None, subtext=None,
                         logo=None):
    """
    Plot rate time series for selected countries and OECD average.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with Year, Code, Country, and rate_col columns
    rate_col : str
        Name of the rate column to plot
    countries : list, optional
        List of country codes to plot. If None, plots all OECD countries.
    oecd_avg : bool
        Whether to include OECD average line
    title : str, optional
        Plot title
    ylabel : str, optional
        Y-axis label
    selected_countries : list, optional
        List of country codes to highlight with colors. Others will be gray.
        If None, uses the countries parameter.
    label_lines : bool
        If True, label lines directly on the right side instead of using a legend.
        If False, use a traditional legend.
    """
    # Filter to OECD countries
    df = df.reset_index() if 'Code' in df.index.names else df
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()
    
    # Add Country column if missing
    if 'Country' not in df_oecd.columns:
        df_oecd['Country'] = df_oecd['Code'].map(code_to_who_country)
    
    # Determine which countries to plot
    if countries is None:
        countries = df_oecd['Code'].unique()
    
    # Determine which countries are selected (for coloring)
    if selected_countries is None:
        selected_countries = countries
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Get all OECD countries for background
    all_oecd = df_oecd['Code'].unique()
    
    # Plot non-selected countries in gray (background)
    non_selected = [c for c in all_oecd if c not in selected_countries]
    for code in non_selected:
        country_data = df_oecd[df_oecd['Code'] == code]
        if not country_data.empty:
            ax.plot(country_data['Year'], country_data[rate_col], 
                   color='gray', alpha=0.3, linewidth=0.8, zorder=1)
    
    # Plot selected countries with colors
    label_data = []  # Store label information for later placement
    
    for code in selected_countries:
        country_data = df_oecd[df_oecd['Code'] == code]
        if not country_data.empty:
            country_name = country_data['Country'].iloc[0]
            color = get_country_color(code)
            line = ax.plot(country_data['Year'], country_data[rate_col], 
                          color=color, alpha=0.9, linewidth=1.5, 
                          label=country_name, zorder=2)
            
            # Store label information for later placement
            if label_lines:
                # Get the last data point
                last_year = country_data['Year'].max()
                last_value = country_data[country_data['Year'] == last_year][rate_col].iloc[0]
                label_data.append({
                    'x': last_year,
                    'y': last_value,
                    'text': country_name,
                    'color': color
                })
    
    # Plot OECD average (no direct label)
    if oecd_avg:
        oecd_avg_by_year = df_oecd.groupby('Year')[rate_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color=AIBM_COLORS['dark_gray'], linewidth=1.5, linestyle='--', 
               label='OECD Average', zorder=2)
    
    # Formatting
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel or rate_col)
    # AIBM style: title left-aligned
    plot_title = title or f'{rate_col} Over Time'
    if subtitle is not None:
        add_title(plot_title, subtitle, pad=25, x=0, y=1.04)
    else:
        ax.set_title(plot_title, loc="left")
    ax.grid(True, alpha=0.3)
    
    # Only show legend if not using direct labels
    if not label_lines:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    else:
        max_year = df_oecd['Year'].max()
        min_year = df_oecd['Year'].min()
        add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year)
        year_range = max_year - min_year
        tick_step = 1 if year_range <= 5 else 5
        ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
        ax.spines['left'].set_visible(False)
    
    # AIBM style: subtext and logo below plot (aligned with axes)
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo:
        logo_path = logo if isinstance(logo, str) else "logo-hq-small.png"
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.21), align_to_axes=True)
    
    plt.tight_layout()
    return fig, ax


def plot_coefficients_bar(beta_samples, predictors, metric='coefficient', x_std=None,
                         title=None, subtitle=None, subtext=None, logo=None,
                         predictor_labels=None, figsize=(7, 3.5)):
    """
    Plot coefficient or importance bar chart for Bayesian model predictors (AIBM style).

    Parameters
    ----------
    beta_samples : array-like, shape (n_samples, n_predictors)
        Posterior samples of beta coefficients (e.g., from trace.posterior['beta'])
    predictors : list of str
        Predictor names (e.g., ['Gap_Alcohol', 'Gap_Suicide', ...])
    metric : str, optional
        'coefficient' — plot posterior mean and HDI of coefficients (can be negative)
        'importance' — plot |coefficient| × SD (requires x_std)
    x_std : array-like, shape (n_predictors,), optional
        Standard deviation of each predictor on original scale. Required when metric='importance'.
    title : str, optional
        Main title
    subtitle : str, optional
        Subtitle below title
    subtext : str, optional
        Source/caption below plot
    logo : bool or str, optional
        If True, add logo. If str, path to logo file.
    predictor_labels : dict, optional
        Map predictor names to display labels. If None, uses PREDICTOR_LABELS.
    figsize : tuple of float
        Figure size (width, height). Default (7, 3.5) for compact plot.

    Returns
    -------
    fig, ax : matplotlib figure and axes
    """
    labels = predictor_labels or PREDICTOR_LABELS
    beta_samples = np.asarray(beta_samples)

    if metric == 'coefficient':
        values_mean = beta_samples.mean(axis=0)
        values_hdi_3 = np.percentile(beta_samples, 3, axis=0)
        values_hdi_97 = np.percentile(beta_samples, 97, axis=0)
        xlabel = 'Coefficient — change in LE gap (years) per SD in predictor'
        show_zero_line = True
    elif metric == 'importance':
        if x_std is None:
            raise ValueError("x_std is required when metric='importance'")
        x_std = np.asarray(x_std)
        importance_samples = np.abs(beta_samples) * x_std[np.newaxis, :]
        values_mean = importance_samples.mean(axis=0)
        values_hdi_3 = np.percentile(importance_samples, 3, axis=0)
        values_hdi_97 = np.percentile(importance_samples, 97, axis=0)
        xlabel = 'Importance — |coefficient| × SD of predictor'
        show_zero_line = False
    else:
        raise ValueError(f"metric must be 'coefficient' or 'importance', got {metric!r}")

    # Build DataFrame and sort by magnitude (strongest first)
    df = pd.DataFrame({
        'predictor': predictors,
        'mean': values_mean,
        'hdi_lo': values_hdi_3,
        'hdi_hi': values_hdi_97,
    })
    df['label'] = df['predictor'].map(lambda p: labels.get(p, p.replace('Gap_', '')))
    df['abs_mean'] = df['mean'].abs()
    df = df.sort_values('abs_mean', ascending=True).reset_index(drop=True)

    # Colors: for coefficients, positive vs negative; for importance, all same (positive)
    if metric == 'coefficient':
        colors = [AIBM_COLORS['light_orange'] if m >= 0 else AIBM_COLORS['light_blue'] for m in df['mean']]
    else:
        colors = [AIBM_COLORS['light_orange']] * len(df)

    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(len(df))
    ax.barh(y_pos, df['mean'],
            xerr=[df['mean'] - df['hdi_lo'], df['hdi_hi'] - df['mean']],
            color=colors, capsize=3, error_kw={'linewidth': 1, 'alpha': 0.5})
    if show_zero_line:
        ax.axvline(0, color='gray', linewidth=0.8, linestyle='-')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['label'], fontsize=9)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylim(-0.5, len(df) - 0.5)

    # AIBM style: title, subtitle, subtext, logo
    if title:
        if subtitle is not None:
            add_title(title, subtitle, pad=25, x=0, y=1.04)
        else:
            ax.set_title(title, loc="left")
    if subtext:
        add_subtext(subtext, x=0, y=-0.22, align_to_axes=True)
    if logo:
        logo_path = logo if isinstance(logo, str) else "logo-hq-small.png"
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(1.0, -0.25), align_to_axes=True)

    plt.tight_layout()
    return fig, ax


def plot_fitted_vs_actual_timeseries(
    ax, country, trace, metadata, panel_df, country_to_idx,
    target_col='LE_gap', target_name='Life Expectancy gap',
    add_predicted_to_legend=True
):
    """
    Plot actual and fitted (predicted) gap over time for one country on the given axes.

    Actual: line only, country signature color. Predicted: markers with 94% HDI error bars, gray.
    Designed to be called multiple times with the same ax to overlay multiple countries.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    country : str
        Country code (e.g., 'USA', 'ISL')
    trace : arviz.InferenceData
        Posterior trace from Bayesian model
    metadata : dict
        Model metadata with X_mean, X_std, y_mean, predictors, countries
    panel_df : pd.DataFrame
        Panel dataset with country, Year, and target_col
    country_to_idx : dict
        Mapping from country codes to indices
    target_col : str
        Column name for target variable
    target_name : str
        Name for axis labels
    add_predicted_to_legend : bool
        If True, add predicted series to legend. Set False when overlaying multiple countries
        to avoid duplicate "Predicted" entries.
    """
    country_data = panel_df[panel_df['country'] == country].copy()
    country_data = country_data.sort_values('Year')
    if len(country_data) == 0:
        raise ValueError(f"No data found for country: {country}")

    X_mean = np.array(metadata['X_mean'])
    X_std = np.array(metadata['X_std'])
    y_mean = metadata['y_mean']
    predictors = metadata['predictors']
    countries = np.array(metadata['countries'])

    beta_samples = trace.posterior['beta'].values.reshape(-1, len(predictors))
    alpha_samples = trace.posterior['alpha'].values.reshape(-1, len(countries))
    alpha_i = alpha_samples[:, country_to_idx[country]]

    years = country_data['Year'].values
    actual_values = country_data[target_col].values
    predicted_means = []
    predicted_lower = []
    predicted_upper = []

    for _, row in country_data.iterrows():
        X_current = np.array([row[p] for p in predictors])
        X_std_row = (X_current - X_mean) / X_std
        pred_centered = alpha_i + np.dot(X_std_row, beta_samples.T)
        pred_original = pred_centered + y_mean
        hdi = az.hdi(pred_original, hdi_prob=0.94)
        predicted_means.append(np.mean(pred_original))
        predicted_lower.append(hdi[0])
        predicted_upper.append(hdi[1])

    predicted_means = np.array(predicted_means)
    predicted_lower = np.array(predicted_lower)
    predicted_upper = np.array(predicted_upper)

    # Actual: line only, country signature color
    color = get_country_color(country)
    country_label = code_to_who_country.get(country, country)
    ax.plot(years, actual_values, '-', color=color, label=country_label, linewidth=1.5, zorder=3)

    # Predicted: vertical lines between lower and upper bounds (94% HDI), gray
    pred_label = 'Predicted (94% HDI)' if add_predicted_to_legend else None
    ax.vlines(years, predicted_lower, predicted_upper, color=color, alpha=0.5,
        label=pred_label, linewidth=1.5, zorder=2)

    # Return label info for direct labeling (last point of actual line)
    label_info = {
        'x': float(years[-1]), 'y': float(actual_values[-1]),
        'text': country_label, 'color': color
    }
    return label_info
