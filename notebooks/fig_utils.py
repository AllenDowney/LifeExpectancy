"""Figure utilities for time series plotting."""

import os
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import arviz as az
from scipy import stats
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
    'Gap_ChronicRespiratory': 'Lung Disease',
    'Gap_LiverDisease': 'Liver Disease',
    'Gap_UnintentionalInjury': 'Injury',
    'Gap_DrugDisorder': 'Drug Disorders',
    'Gap_COVID': 'COVID-19',
    'Gap_Childhood': 'Childhood (under-five)',
}

# Point colors for talk / EDA scatters by relationship type (AIBM brand palette)
CORRELATION_SCATTER_KIND_COLORS = {
    'rate_gap': AIBM_COLORS['green'],      # Mid (level) vs Gap
    'gap_gap': AIBM_COLORS['purple'],
    'level_level': AIBM_COLORS['orange'],
}


def plot_correlation_scatter_aibm(
    df,
    x_col,
    y_col,
    title,
    subtitle,
    xlabel,
    ylabel,
    subtext,
    trend_line=True,
    logo=True,
    point_color=None,
    correlation_kind=None,
    figsize=(8, 5),
    annotate_stats=True,
):
    """
    Scatter of two columns (e.g. IHME Mid/Gap predictors) with AIBM title block and branding.

    ``df`` should share an index (e.g. country ``Code``); rows with NA in either column are dropped.

    ``correlation_kind`` — if set and ``point_color`` is omitted, uses
    ``CORRELATION_SCATTER_KIND_COLORS``: ``'rate_gap'``, ``'gap_gap'``, ``'level_level'``.
    """
    if point_color is None:
        if correlation_kind is not None:
            if correlation_kind not in CORRELATION_SCATTER_KIND_COLORS:
                raise ValueError(
                    f"correlation_kind must be one of {list(CORRELATION_SCATTER_KIND_COLORS)!r}"
                )
            point_color = CORRELATION_SCATTER_KIND_COLORS[correlation_kind]
        else:
            point_color = AIBM_COLORS['crimson']
    xy = df[[x_col, y_col]].dropna()
    x = xy[x_col].values
    y = xy[y_col].values
    n = len(x)
    if n < 2:
        raise ValueError(f'Need at least 2 complete rows; got {n}')

    r_pearson = float(np.corrcoef(x, y)[0, 1]) if n > 1 else float('nan')
    lr = stats.linregress(x, y)

    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, s=36, alpha=0.75, color=point_color, edgecolors='white', linewidths=0.4, zorder=2)

    if trend_line:
        xs = np.linspace(np.nanmin(x), np.nanmax(x), 50)
        ax.plot(xs, lr.intercept + lr.slope * xs, color=AIBM_COLORS['dark_gray'],
                linewidth=1.8, linestyle='-', zorder=1, alpha=0.9)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    add_title(title, subtitle, pad=22, x=0, y=1.02)

    if annotate_stats:
        stat_txt = f'$r$ = {r_pearson:.2f}\n$n$ = {n}'
        ax.text(0.03, 0.97, stat_txt, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', color=AIBM_COLORS['dark_gray'])

    if subtext:
        add_subtext(subtext, x=0, y=-0.22, align_to_axes=True)
    if logo:
        logo_path = 'logo-hq-small.png'
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.24), align_to_axes=True)

    plt.tight_layout()
    return fig, ax


def plot_beta_posterior_correlation_heatmap(
    corr_df,
    title,
    subtitle,
    subtext,
    display_labels=None,
    logo=True,
    figsize=(6.5, 5.5),
):
    """
    Heatmap of Pearson correlations (typically a subset of ``beta_samples_df.corr()``).

    Parameters
    ----------
    corr_df : pandas.DataFrame
        Square correlation matrix with predictor names as index/columns (e.g. ``Gap_RoadTraffic``).
    display_labels : list of str, optional
        Y-axis / X-axis labels in column order; default ``PREDICTOR_LABELS`` short names.
    """
    import seaborn as sns

    cols = list(corr_df.columns)
    if list(corr_df.index) != cols:
        corr_df = corr_df.loc[cols, cols]
    if display_labels is None:
        display_labels = [PREDICTOR_LABELS.get(c, c.replace('Gap_', '').replace('_', ' ')) for c in cols]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        corr_df,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0.0,
        vmin=-1.0,
        vmax=1.0,
        square=True,
        linewidths=0.5,
        linecolor=AIBM_COLORS['light_gray'],
        xticklabels=display_labels,
        yticklabels=display_labels,
        ax=ax,
        cbar_kws={'shrink': 0.85, 'label': 'Posterior correlation (r)'},
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    add_title(title, subtitle, pad=24, x=0, y=1.05)
    if subtext:
        add_subtext(subtext, x=0, y=-0.32, align_to_axes=True)
    if logo:
        logo_path = 'logo-hq-small.png'
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.34), align_to_axes=True)
    plt.tight_layout()
    return fig, ax


def plot_beta_posterior_pair_scatter(
    beta_samples_df,
    cols,
    title,
    subtitle,
    subtext,
    display_labels=None,
    logo=True,
    figsize=None,
    scatter_kwargs=None,
    kde_kwargs=None,
):
    """
    ArviZ-style pair plot: KDE on the diagonal, scatter below diagonal for β posterior draws.

    Parameters
    ----------
    beta_samples_df : pandas.DataFrame
        Columns are Gap_* predictor ids; values are flattened posterior draws (e.g. from ``az.extract``).
    cols : list of str
        Subset of column names, defining order of rows/columns in the pair grid.
    display_labels : list of str, optional
        Axis labels in the same order as ``cols``; default uses ``PREDICTOR_LABELS`` short names.
    scatter_kwargs, kde_kwargs : dict, optional
        Passed to ArviZ ``plot_pair`` (merged with defaults for scatter).
    """
    scatter_kwargs = dict(scatter_kwargs or {})
    scatter_defaults = {"alpha": 0.22, "s": 5, "color": AIBM_COLORS["crimson"]}
    scatter_defaults.update(scatter_kwargs)

    missing = [c for c in cols if c not in beta_samples_df.columns]
    if missing:
        raise ValueError(f"Missing columns in beta_samples_df: {missing}")
    sub = beta_samples_df[cols]
    if display_labels is None:
        display_labels = [
            PREDICTOR_LABELS.get(c, c.replace("Gap_", "").replace("_", " ")) for c in cols
        ]
    if len(display_labels) != len(cols):
        raise ValueError("display_labels must match cols length")

    # One ArviZ variable per cause (flat over chain × draw)
    posterior = {
        display_labels[i]: sub[cols[i]].values[np.newaxis, :] for i in range(len(cols))
    }
    idata = az.from_dict(posterior=posterior)

    n = len(cols)
    if figsize is None:
        figsize = (max(7.0, 1.85 * n), max(7.0, 1.85 * n))

    az.plot_pair(
        idata,
        var_names=display_labels,
        kind=["scatter", "kde"],
        divergences=False,
        figsize=figsize,
        textsize=8,
        scatter_kwargs=scatter_defaults,
        kde_kwargs=dict(kde_kwargs or {}),
    )
    fig = plt.gcf()
    fig.subplots_adjust(top=0.92, bottom=0.07)
    fig.suptitle(
        title,
        fontsize=13,
        fontweight="bold",
        x=0.02,
        y=0.98,
        ha="left",
        va="top",
    )
    fig.text(0.02, 0.935, subtitle, fontsize=10, ha="left", va="top", color="0.25")
    if subtext:
        fig.text(0.02, 0.01, subtext, fontsize=8, ha="left", va="bottom", color="0.35", wrap=True)
    if logo:
        logo_path = "logo-hq-small.png"
        if os.path.isfile(logo_path):
            plt.sca(fig.axes[-1])
            add_logo(filename=logo_path, location=(1.0, 0.02), align_to_axes=False)
    return fig


def plot_beta_posterior_joint_grid_strongest_negative(
    beta_samples_df,
    n_panels=9,
    n_rows=3,
    n_cols=3,
    title="",
    subtitle="",
    subtext="",
    label_map=None,
    logo=True,
    figsize=(8, 8),
    scatter_kwargs=None,
):
    """
    3×3 (or ``n_rows``×``n_cols``) grid of scatter plots for the most negative Pearson
    correlations between distinct β posterior draws (upper triangle of ``.corr()``).

    Parameters
    ----------
    beta_samples_df : pandas.DataFrame
        Columns are predictor ids; each row is one posterior draw (stacked chains).
    n_panels : int
        Number of pairs to show (default 9 for a 3×3 grid).
    label_map : dict, optional
        Maps column name -> axis label; defaults to ``PREDICTOR_LABELS``-style short names.

    Returns
    -------
    fig : matplotlib.figure.Figure
    pairs : list of tuple
        ``(col_a, col_b, r)`` for each panel, in plot order (most negative ``r`` first).
    """
    scatter_kw = {"alpha": 0.2, "s": 5, "color": AIBM_COLORS["crimson"], **(scatter_kwargs or {})}

    corr = beta_samples_df.corr()
    cols = list(beta_samples_df.columns)
    neg_pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = float(corr.iloc[i, j])
            if r < 0.0 and not np.isnan(r):
                neg_pairs.append((cols[i], cols[j], r))
    neg_pairs.sort(key=lambda t: t[2])

    if len(neg_pairs) < n_panels:
        raise ValueError(
            f"Need at least {n_panels} negatively correlated β pairs; found {len(neg_pairs)}."
        )
    top = neg_pairs[:n_panels]

    def _lbl(c):
        if label_map is not None and c in label_map:
            return label_map[c]
        return PREDICTOR_LABELS.get(c, c.replace("Gap_", "").replace("_", " "))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, squeeze=False)
    axes = axes.ravel()

    for ax, (c1, c2, r) in zip(axes, top):
        x = beta_samples_df[c1].values
        y = beta_samples_df[c2].values
        ax.scatter(x, y, **scatter_kw)
        ax.set_xlabel(_lbl(c1))
        ax.set_ylabel(_lbl(c2))
        ax.text(
            0.04,
            0.96,
            f"r = {r:.2f}",
            transform=ax.transAxes,
            va="top",
            color="0.25",
        )

    for k in range(len(top), len(axes)):
        axes[k].set_visible(False)

    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.07, wspace=0.4, hspace=0.42)
    fig.suptitle(
        title,
        fontweight="bold",
        x=0.02,
        y=0.98,
        ha="left",
        va="top",
    )
    fig.text(0.02, 0.95, subtitle, ha="left", va="top", color="0.25")
    if subtext:
        fig.text(0.02, -0.02, subtext, ha="left", va="bottom", color="0.35", wrap=True)
    if logo:
        logo_path = "logo-hq-small.png"
        if os.path.isfile(logo_path):
            plt.sca(fig.axes[len(top) - 1])
            add_logo(filename=logo_path, location=(1.0, -0.02), align_to_axes=False)
    return fig, top


# Color mapping for countries - ensures consistent colors across plots
COUNTRY_COLORS = {
    # Major countries with distinctive colors
    'USA': '#002868',      # USA flag blue
    'GBR': '#C8102E',      # UK flag red
    'JPN': '#2ca02c',      # Green
    'DEU': '#FFCC00',      # Germany (presentation)
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

def add_direct_line_labels(ax, label_data, extension_frac=0.12, min_extension=2.5, x_min=None, x_max=None,
                           label_y_nudge=None):
    """
    Add direct labels on the right side of a time series plot.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to add labels to
    label_data : list of dict
        Each dict has keys: x, y, text, color (e.g. endpoint of each line). Optional key
        ``code`` (ISO 3-letter) for ``label_y_nudge`` lookup.
    extension_frac : float
        Fraction of x-range to extend for label space
    min_extension : float
        Minimum x-axis extension in data units
    x_min, x_max : float, optional
        Data range for axis and spine. If None, use current axes limits (avoids bug when
        all label points share the same x, e.g. last year only).
    label_y_nudge : dict, optional
        Map country code -> vertical offset in **y-axis data units** (e.g. years for a gap plot).
        Applied when ``label_data`` entries include ``code``.
    """
    if not label_data:
        return
    if x_min is None or x_max is None:
        x_min, x_max = ax.get_xlim()
    x_range = x_max - x_min
    extension = max(x_range * extension_frac, min_extension)
    ax.set_xlim(x_min, x_max + extension)
    label_x = x_max + extension * 0.1
    nudge = label_y_nudge or {}
    sorted_data = sorted(label_data, key=lambda d: d['y'] + nudge.get(d.get('code'), 0), reverse=True)
    for d in sorted_data:
        dy = nudge.get(d.get('code'), 0)
        ax.text(label_x, d['y'] + dy, f'  {d["text"]}', color=d['color'], fontsize=9,
                va='center', ha='left', zorder=3)
    # Restrict bottom spine to data range (not extended area)
    ax.spines['bottom'].set_bounds(x_min, x_max)


def male_female_colors_from_country(code):
    """
    Male = darker tint, female = lighter tint of the country's signature color
    (same hue family as ``COUNTRY_COLORS``).
    """
    base = mcolors.to_rgb(get_country_color(code))
    male = tuple(min(1.0, c * 0.68) for c in base)
    female = tuple(min(1.0, c + (1.0 - c) * 0.42) for c in base)
    return mcolors.to_hex(male), mcolors.to_hex(female)


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
                        logo=None, label_y_nudge=None):
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
    label_y_nudge : dict, optional
        Country code -> vertical shift for end-of-line labels (y-axis data units), e.g.
        ``{'GBR': 0.04, 'NOR': -0.04}``.
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
                    'color': color,
                    'code': code,
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
        add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year, label_y_nudge=label_y_nudge)
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


def plot_male_female_levels_timeseries(
    df,
    value_col,
    countries=None,
    selected_countries=None,
    label_lines=True,
    title=None,
    subtitle=None,
    ylabel=None,
    subtext=None,
    logo=None,
    label_y_nudge=None,
    background_alpha=0.22,
    line_width_bg=0.85,
    line_width_hi=1.55,
    male_color=None,
    female_color=None,
    selected_color_mode='aibm',
    yticks=None,
    ylim=None,
):
    """
    Plot male and female level time series (one line per sex per country).

    Non-selected countries are drawn in AIBM green (male) and purple (female) at low alpha.
    Selected countries use full opacity; optional direct labels on the right (no legend).

    Parameters
    ----------
    df : pandas.DataFrame
        Wide OECD-style frame: ``Code``, ``Year``, ``Country``,
        ``{value_col}_Male``, ``{value_col}_Female``.
    value_col : str
        Base name, e.g. ``'HALE_Years'`` → columns ``HALE_Years_Male``, ``HALE_Years_Female``.
    countries : list, optional
        Country codes to include; default all OECD in ``df``.
    selected_countries : list, optional
        Highlight these codes (alpha 1, labels if ``label_lines``).
    label_lines : bool
        If True, label endpoints on the right with sex-colored text (``Name (M)`` / ``Name (F)``).
    background_alpha : float
        Alpha for non-highlighted country lines.
    male_color, female_color : str, optional
        Colors for **background** countries only. Defaults: ``AIBM_COLORS['green']``, ``AIBM_COLORS['purple']``.
    selected_color_mode : str
        ``'aibm'`` — highlighted lines use the same green/purple as background (full alpha).
        ``'country'`` — male/female lines use darker/lighter tints of ``COUNTRY_COLORS[code]``.
    yticks : array-like, optional
        If set, ``ax.set_yticks(yticks)`` and integer tick labels (no decimal places).
    ylim : tuple, optional
        ``(ymin, ymax)`` passed to ``ax.set_ylim``.
    label_y_nudge : dict, optional
        Vertical nudge in y-axis units, keyed by label ``code`` (e.g. ``'NOR_M'``, ``'NOR_F'``).
    """
    if selected_color_mode not in ('aibm', 'country'):
        raise ValueError("selected_color_mode must be 'aibm' or 'country'")

    bg_male = male_color or AIBM_COLORS['green']
    bg_female = female_color or AIBM_COLORS['purple']
    male_col = f'{value_col}_Male'
    female_col = f'{value_col}_Female'
    for c in (male_col, female_col):
        if c not in df.columns:
            raise ValueError(f"Expected column {c!r} in dataframe.")

    df = df.reset_index() if 'Code' in df.index.names else df.copy()
    df_temp = df.set_index('Code')
    df_oecd = get_oecd(df_temp).reset_index()

    if 'Country' not in df_oecd.columns:
        df_oecd['Country'] = df_oecd['Code'].map(code_to_who_country)

    if countries is None:
        countries = df_oecd['Code'].unique()
    if selected_countries is None:
        selected_countries = list(countries)

    all_oecd = df_oecd['Code'].unique()
    fig, ax = plt.subplots(figsize=(8, 4))
    non_selected = [c for c in all_oecd if c not in selected_countries]

    for code in non_selected:
        block = df_oecd[df_oecd['Code'] == code]
        if block.empty:
            continue
        ax.plot(
            block['Year'], block[male_col],
            color=bg_male, alpha=background_alpha, linewidth=line_width_bg, zorder=1,
        )
        ax.plot(
            block['Year'], block[female_col],
            color=bg_female, alpha=background_alpha, linewidth=line_width_bg, zorder=1,
        )

    label_data = []

    for code in selected_countries:
        block = df_oecd[df_oecd['Code'] == code]
        if block.empty:
            continue
        country_name = block['Country'].iloc[0]
        last_year = block['Year'].max()
        last_m = block[block['Year'] == last_year][male_col].iloc[0]
        last_f = block[block['Year'] == last_year][female_col].iloc[0]

        if selected_color_mode == 'country':
            hi_male, hi_female = male_female_colors_from_country(code)
        else:
            hi_male, hi_female = bg_male, bg_female

        ax.plot(
            block['Year'], block[male_col],
            color=hi_male, alpha=1.0, linewidth=line_width_hi, zorder=2,
        )
        ax.plot(
            block['Year'], block[female_col],
            color=hi_female, alpha=1.0, linewidth=line_width_hi, zorder=2,
        )

        if label_lines:
            label_data.append({
                'x': last_year,
                'y': last_m,
                'text': f'{country_name} (M)',
                'color': hi_male,
                'code': f'{code}_M',
            })
            label_data.append({
                'x': last_year,
                'y': last_f,
                'text': f'{country_name} (F)',
                'color': hi_female,
                'code': f'{code}_F',
            })

    if label_lines and label_data:
        max_year = df_oecd['Year'].max()
        min_year = df_oecd['Year'].min()
        add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year, label_y_nudge=label_y_nudge)
        year_range = max_year - min_year
        tick_step = 1 if year_range <= 5 else 5
        ax.set_xticks(np.arange(min_year, max_year + 1, tick_step))
        ax.spines['left'].set_visible(False)

    if ylim is not None:
        ax.set_ylim(ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _p: f'{int(round(x))}'))

    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel or value_col)
    plot_title = title or f'{value_col} over time'
    if subtitle is not None:
        add_title(plot_title, subtitle, pad=25, x=0, y=1.04)
    else:
        ax.set_title(plot_title, loc='left')
    ax.grid(True, alpha=0.3)

    if subtext:
        add_subtext(subtext, x=0, y=-0.18, align_to_axes=True)
    if logo:
        logo_path = logo if isinstance(logo, str) else 'logo-hq-small.png'
        if os.path.isfile(logo_path):
            add_logo(filename=logo_path, location=(0.99, -0.21), align_to_axes=True)

    plt.tight_layout()
    return fig, ax


def plot_rate_timeseries(df, rate_col, countries=None, oecd_avg=True, title=None, ylabel=None,
                         selected_countries=None, label_lines=True, subtitle=None, subtext=None,
                         logo=None, label_y_nudge=None):
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
    subtitle, subtext, logo : optional
        AIBM-style title block and branding (same as ``plot_gap_timeseries``).
    label_y_nudge : dict, optional
        Country code -> vertical shift for end-of-line labels in y-axis data units.
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
                    'color': color,
                    'code': code,
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
        add_direct_line_labels(ax, label_data, x_min=min_year, x_max=max_year, label_y_nudge=label_y_nudge)
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
