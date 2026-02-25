"""Figure utilities for time series plotting."""

import os
import matplotlib.pyplot as plt
import numpy as np
from utils import get_oecd, code_to_who_country, add_title, add_subtext, add_logo, AIBM_COLORS

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
    'IRL': '#f7b6d3',      # Light pink
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
    'MEX': '#C8102E',      # Mexico flag red
    'TUR': '#C8102E',      # Flag red
}

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
    
    # Plot OECD average
    if oecd_avg:
        oecd_avg_by_year = df_oecd.groupby('Year')[gap_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color=AIBM_COLORS['dark_gray'], linewidth=1.5, linestyle='--', 
               label='OECD Average', zorder=2)
        if label_lines:
            last_year = oecd_avg_by_year.index.max()
            last_value = oecd_avg_by_year.iloc[-1]
            
    
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
        # Adjust x-axis limits to make room for labels on the right
        # Get the actual data range from the dataframe
        max_year = df_oecd['Year'].max()
        min_year = df_oecd['Year'].min()
        year_range = max_year - min_year
        
        # Extend x-axis by a reasonable amount (about 10-15% of the range, or at least 2-3 years)
        extension = max(year_range * 0.12, 2.5)
        ax.set_xlim(min_year, max_year + extension)
        
        # Place labels at a fixed position relative to the max year
        label_x = max_year + extension * 0.1  # Position labels in the extended area
        
        # Sort labels by y-value to arrange them vertically
        label_data_sorted = sorted(label_data, key=lambda d: d['y'], reverse=True)
        
        # Place labels with spacing
        for label_info in label_data_sorted:
            ax.text(label_x, label_info['y'], f'  {label_info["text"]}', 
                   color=label_info['color'], fontsize=9, va='center', ha='left',
                   style='italic' if 'OECD' in label_info['text'] else 'normal',
                   zorder=3)
        
        # Spine and ticks only up to data end (not into label area)
        ax.spines['bottom'].set_bounds(min_year, max_year)
        tick_step = 1 if year_range <= 5 else 5
        ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
    
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
    
    # Plot OECD average
    if oecd_avg:
        oecd_avg_by_year = df_oecd.groupby('Year')[rate_col].mean()
        ax.plot(oecd_avg_by_year.index, oecd_avg_by_year.values,
               color=AIBM_COLORS['dark_gray'], linewidth=1.5, linestyle='--', 
               label='OECD Average', zorder=2)
        if label_lines:
            last_year = oecd_avg_by_year.index.max()
            last_value = oecd_avg_by_year.iloc[-1]
            label_data.append({
                'x': last_year,
                'y': last_value,
                'text': 'OECD Avg',
                'color': AIBM_COLORS['dark_gray']
            })
    
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
        # Adjust x-axis limits to make room for labels on the right
        # Get the actual data range from the dataframe
        max_year = df_oecd['Year'].max()
        min_year = df_oecd['Year'].min()
        year_range = max_year - min_year
        
        # Extend x-axis by a reasonable amount (about 10-15% of the range, or at least 2-3 years)
        extension = max(year_range * 0.12, 2.5)
        ax.set_xlim(min_year, max_year + extension)
        
        # Place labels at a fixed position relative to the max year
        label_x = max_year + extension * 0.3  # Position labels in the extended area
        
        # Sort labels by y-value to arrange them vertically
        label_data_sorted = sorted(label_data, key=lambda d: d['y'], reverse=True)
        
        # Place labels with spacing
        for label_info in label_data_sorted:
            ax.text(label_x, label_info['y'], f'  {label_info["text"]}', 
                   color=label_info['color'], fontsize=9, va='center', 
                   style='italic' if 'OECD' in label_info['text'] else 'normal',
                   zorder=3)
        
        # Spine and ticks only up to data end (not into label area)
        ax.spines['bottom'].set_bounds(min_year, max_year)
        tick_step = 1 if year_range <= 5 else 5
        ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
    
    # AIBM style: subtext and logo below plot (aligned with axes)
    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo:
        logo_path = logo if isinstance(logo, str) else "logo-hq-small.png"
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.21), align_to_axes=True)
    
    plt.tight_layout()
    return fig, ax

