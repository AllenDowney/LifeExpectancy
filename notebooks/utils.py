"""Utility functions for data analysis and visualization."""

import os
import re
from matplotlib import font_manager

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.stats import beta, norm

# =============================================================================
# Matplotlib Configuration
# =============================================================================

AIBM_COLORS = {
    # AIBM brand colors
    "light_gray": "#F3F4F3",
    "medium_gray": "#767676",
    "green": "#0B8569",
    "light_green": "#AAC9B8",
    "orange": "#C55300",
    "light_orange": "#F4A26B",
    "purple": "#9657A5",
    "light_purple": "#CFBCD0",
    "blue": "#4575D6",
    "light_blue": "#C9D3E8",
    # Additional colors from coolers.co
    "dark_gray": "#404040",
    "dark_purple": "#28112B",
    "dark_green": "#002500",
    "amber": "#F5BB00",
    "oxford_blue": "#000022",
    "bittersweet": "#FF6666",
    "crimson": "#D62839",
}


def configure_plot_style():
    """Configure the default matplotlib style for AIBM plots.

    This function sets up the default style for plots, including:
    - Figure size and DPI
    - Color scheme
    - Font settings
    - Grid and spine settings
    - Tick settings

    The settings can be overridden for individual plots as needed.
    """
    # Figure size and DPI
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["figure.figsize"] = [6.0, 3.5]  # inches

    # Default color cycle
    colors = [
        AIBM_COLORS["green"],
        AIBM_COLORS["purple"],
        AIBM_COLORS["blue"],
        AIBM_COLORS["orange"],
    ]
    cycler = plt.cycler(color=colors)
    plt.rc("axes", prop_cycle=cycler)

    # Font settings
    # Try to use PT Sans, fall back to system fonts if not available
    if "PT Sans" in [f.name for f in font_manager.fontManager.ttflist]:
        plt.rcParams["font.family"] = "PT Sans"
    else:
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "DejaVu Sans",
            "Arial",
            "Helvetica",
            "sans-serif",
        ]

    plt.rcParams["legend.fontsize"] = "small"

    # Tick and label colors
    plt.rcParams["axes.edgecolor"] = AIBM_COLORS["medium_gray"]
    plt.rcParams["xtick.color"] = AIBM_COLORS["medium_gray"]
    plt.rcParams["ytick.color"] = AIBM_COLORS["medium_gray"]
    plt.rcParams["axes.labelcolor"] = AIBM_COLORS["medium_gray"]

    # Default spine settings (can be overridden per plot)
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.left"] = True  # Keep left spine by default
    plt.rcParams["axes.spines.bottom"] = True  # Keep bottom spine by default

    # Default grid settings (can be overridden per plot)
    plt.rcParams["grid.color"] = AIBM_COLORS["light_gray"]
    plt.rcParams["grid.linestyle"] = "-"
    plt.rcParams["grid.linewidth"] = 1
    plt.rcParams["axes.grid"] = False  # Disable grid by default
    plt.rcParams["axes.grid.axis"] = "y"

    # Tick mark settings
    plt.rcParams["xtick.major.size"] = 0
    plt.rcParams["xtick.minor.size"] = 0
    plt.rcParams["ytick.major.size"] = 0
    plt.rcParams["ytick.minor.size"] = 0


# Apply the default style
configure_plot_style()

# =============================================================================
# File I/O Functions
# =============================================================================


def write_table(table, label, **options):
    """Write a table in LaTex format.

    Args:
        table: DataFrame
        label: string
        options: passed to DataFrame.to_latex
    """
    filename = f"tables/{label}.tex"
    os.makedirs("tables", exist_ok=True)
    with open(filename, "w", encoding="utf8") as fp:
        s = table.to_latex(**options)
        fp.write(s)


def write_pmf(pmf, label):
    """Write a Pmf object as a table.

    Args:
        pmf: Pmf
        label: string
    """
    df = pd.DataFrame()
    df["qs"] = pmf.index
    df["ps"] = pmf.values
    write_table(df, label, index=False)


def savefig(prefix, fig_number, extra_artists=[], dpi=150):
    """Save the current figure with the given filename.

    Args:
        prefix: string prefix for filename
        fig_number: The figure number
        extra_artists: List of additional artist to include in the bounding box
        dpi: Dots per inch for the saved image
    """
    filename = f"{prefix}{fig_number:02d}"
    if extra_artists:
        plt.savefig(
            filename, dpi=dpi, bbox_inches="tight", bbox_extra_artists=extra_artists
        )
    else:
        plt.savefig(filename, dpi=dpi)


# =============================================================================
# Data Manipulation Functions
# =============================================================================


def underride(d, **options):
    """Add key-value pairs to d only if key is not in d.

    Args:
        d: dictionary
        options: keyword args to add to d

    Returns:
        Updated dictionary
    """
    for key, val in options.items():
        d.setdefault(key, val)
    return d


def value_counts(seq, **options):
    """Make a series of values and the number of times they appear.

    Returns a DataFrame because they get rendered better in Jupyter.

    Args:
        seq: sequence
        options: passed to pd.Series.value_counts

    Returns:
        pd.DataFrame with value counts
    """
    options = underride(options, dropna=False)
    series = pd.Series(seq).value_counts(**options).sort_index()
    series.index.name = "values"
    series.name = "counts"
    return pd.DataFrame(series)


def value_count_frame(data, columns, normalize=False):
    """Make a DataFrame of value counts.

    Args:
        data: DataFrame
        columns: list of column names
        normalize: whether to normalize the counts

    Returns:
        DataFrame with value counts
    """
    dfs = []
    for col in columns:
        df = value_counts(data[col], normalize=normalize)
        df.columns = [col]
        dfs.append(df)
    return pd.concat(dfs, axis=1)


def find_columns(df, prefix):
    """Find columns that start with a given prefix.

    Args:
        df: DataFrame
        prefix: string prefix

    Returns:
        list of column names
    """
    return [
        col
        for col in df.columns
        if col.startswith(prefix)
        and not col.endswith("skp")
        and not col.endswith("timing")
    ]


def round_into_bins(series, bin_width, low=0, high=None):
    """Rounds values down to the bin they belong in.

    series: pd.Series
    bin_width: number, width of the bins

    returns: Series of bin values (with NaN preserved)
    """
    if high is None:
        high = series.max()

    bins = np.arange(low, high + bin_width, bin_width)
    indices = np.digitize(series, bins)
    result = pd.Series(bins[indices - 1], index=series.index, dtype="float")

    result[series.isna()] = np.nan
    return result


# =============================================================================
# Categorical Data Functions
# =============================================================================


def extract_categorical_mapping(series):
    """Extract a mapping from categorical codes to descriptions.

    Args:
        series: pandas Series

    Returns:
        pd.Series mapping from codes to descriptions
    """
    mapping = {}

    for item in series.unique():  # Process unique categorical values
        match = re.match(r"([-\d]+)\.\s(.+)", str(item).strip())
        if match:
            code, description = match.groups()
            mapping[int(code)] = description

    return pd.Series(mapping).sort_index()


def make_categorical_mappings(df, skip_cols=["age"]):
    """Make a mapping from variable names to dictionaries of codes and values.

    Args:
        df: DataFrame
        skip_cols: list of string column names to skip

    Returns:
        dictionary that maps from column names to dictionaries
    """
    mappings = {}
    for col in df.columns:
        if col in skip_cols:
            continue
        mapping = extract_categorical_mapping(df[col])
        if len(mapping) > 0:
            mappings[col] = mapping
    return mappings


def map_codes_to_categories(cat_series: pd.Series, code_series: pd.Series) -> pd.Series:
    """Map numeric codes to category labels.

    Args:
        cat_series: Series containing category labels
        code_series: Series containing numeric codes

    Returns:
        Series with mapped category labels
    """
    # Extract the mapping
    mapping = extract_categorical_mapping(cat_series)

    # Map the codes to categories
    return code_series.map(mapping)


# =============================================================================
# Statistical Functions
# =============================================================================


def estimate_proportion_jeffreys(success_series, confidence_level=0.95):
    """Estimate proportion using Jeffreys prior.

    Args:
        success_series: Boolean series (True = success)
        confidence_level: Confidence level (e.g., 0.95)

    Returns:
        tuple: (proportion, lower_bound, upper_bound)
    """
    success_series = success_series.astype(float)
    n = len(success_series)
    k = success_series.sum()

    # Jeffreys prior: Beta(0.5, 0.5)
    alpha = k + 0.5
    beta = n - k + 0.5

    # Calculate posterior mean
    proportion = alpha / (alpha + beta)

    # Calculate credible interval
    lower = beta.ppf((1 - confidence_level) / 2, alpha, beta)
    upper = beta.ppf(1 - (1 - confidence_level) / 2, alpha, beta)

    return proportion, lower, upper


def estimate_proportion_wilson(success_series, weights_series, confidence_level=0.95):
    """Estimate weighted proportion with Wilson score interval adjusted using effective sample size.

    Args:
        success_series: Boolean series (True = success)
        weights_series: Corresponding weights
        confidence_level: Confidence level (e.g., 0.95)

    Returns:
        tuple: (weighted_proportion, lower_bound, upper_bound)
    """
    success_series = success_series.astype(float)
    weights_series = weights_series.astype(float)

    weighted_successes = (success_series * weights_series).sum()
    total_weight = weights_series.sum()

    # Estimate effective sample size
    n_eff = total_weight**2 / (weights_series**2).sum()

    # Z-score for confidence interval
    z = norm.ppf(1 - (1 - confidence_level) / 2)

    denominator = 1 + z**2 / n_eff
    center = (p + z**2 / (2 * n_eff)) / denominator
    margin = (z * np.sqrt((p * (1 - p) + z**2 / (4 * n_eff)) / n_eff)) / denominator

    lower = center - margin
    upper = center + margin

    return p, lower, upper


def estimate_columns(df, columns, values):
    """Estimate proportions for multiple columns.

    Args:
        df: DataFrame
        columns: list of column names
        values: list of values to estimate

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for col in columns:
        for value in values:
            success = df[col] == value
            p, lower, upper = estimate_proportion_wilson(success, df["weight"])
            estimates.append(
                {
                    "column": col,
                    "value": value,
                    "proportion": p,
                    "lower": lower,
                    "upper": upper,
                }
            )
    return pd.DataFrame(estimates)


def estimate_value_map(df, columns, value_map):
    """Estimate proportions using a value mapping.

    Args:
        df: DataFrame
        columns: list of column names
        value_map: dictionary mapping values to labels

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for col in columns:
        for value, label in value_map.items():
            success = df[col] == value
            p, lower, upper = estimate_proportion_wilson(success, df["weight"])
            estimates.append(
                {
                    "column": col,
                    "value": value,
                    "label": label,
                    "proportion": p,
                    "lower": lower,
                    "upper": upper,
                }
            )
    return pd.DataFrame(estimates)


def estimate_gender_map(columns, gender_map, value_map):
    """Estimate proportions by gender.

    Args:
        columns: list of column names
        gender_map: dictionary mapping gender codes to labels
        value_map: dictionary mapping values to labels

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for col in columns:
        for gender, gender_label in gender_map.items():
            for value, label in value_map.items():
                success = (df[col] == value) & (df["gender"] == gender)
                p, lower, upper = estimate_proportion_wilson(success, df["weight"])
                estimates.append(
                    {
                        "column": col,
                        "gender": gender,
                        "gender_label": gender_label,
                        "value": value,
                        "label": label,
                        "proportion": p,
                        "lower": lower,
                        "upper": upper,
                    }
                )
    return pd.DataFrame(estimates)


def estimate_ordinal(df, column, values, cumulative=False, confidence_level=0.84):
    """Estimate proportions for ordinal data.

    Args:
        df: DataFrame
        column: column name
        values: list of values
        cumulative: whether to compute cumulative proportions
        confidence_level: confidence level

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for value in values:
        if cumulative:
            success = df[column] >= value
        else:
            success = df[column] == value
        p, lower, upper = estimate_proportion_wilson(success, df["weight"])
        estimates.append(
            {
                "value": value,
                "proportion": p,
                "lower": lower,
                "upper": upper,
            }
        )
    return pd.DataFrame(estimates)


def ordinal_gender_map(
    gender_map, column, values, cumulative=False, confidence_level=0.84
):
    """Estimate ordinal proportions by gender.

    Args:
        gender_map: dictionary mapping gender codes to labels
        column: column name
        values: list of values
        cumulative: whether to compute cumulative proportions
        confidence_level: confidence level

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for gender, gender_label in gender_map.items():
        for value in values:
            if cumulative:
                success = (df[column] >= value) & (df["gender"] == gender)
            else:
                success = (df[column] == value) & (df["gender"] == gender)
            p, lower, upper = estimate_proportion_wilson(success, df["weight"])
            estimates.append(
                {
                    "gender": gender,
                    "gender_label": gender_label,
                    "value": value,
                    "proportion": p,
                    "lower": lower,
                    "upper": upper,
                }
            )
    return pd.DataFrame(estimates)


def ordinal_age_gender_map(
    age_map, column, values, cumulative=False, confidence_level=0.84
):
    """Estimate ordinal proportions by age and gender.

    Args:
        age_map: dictionary mapping age codes to labels
        column: column name
        values: list of values
        cumulative: whether to compute cumulative proportions
        confidence_level: confidence level

    Returns:
        DataFrame with estimates
    """
    estimates = []
    for age, age_label in age_map.items():
        for gender, gender_label in gender_map.items():
            for value in values:
                if cumulative:
                    success = (
                        (df[column] >= value)
                        & (df["age"] == age)
                        & (df["gender"] == gender)
                    )
                else:
                    success = (
                        (df[column] == value)
                        & (df["age"] == age)
                        & (df["gender"] == gender)
                    )
                p, lower, upper = estimate_proportion_wilson(success, df["weight"])
                estimates.append(
                    {
                        "age": age,
                        "age_label": age_label,
                        "gender": gender,
                        "gender_label": gender_label,
                        "value": value,
                        "proportion": p,
                        "lower": lower,
                        "upper": upper,
                    }
                )
    return pd.DataFrame(estimates)


# =============================================================================
# Basic Plotting Functions
# =============================================================================


def decorate(**options):
    """Decorate the current axes.

    Call decorate with keyword arguments like
    decorate(title='Title',
             xlabel='x',
             ylabel='y')

    The keyword arguments can be any of the axis properties
    https://matplotlib.org/api/axes_api.html
    """
    legend = options.pop("legend", True)
    loc = options.pop("loc", "best")
    ax = plt.gca()
    ax.set(**options)

    handles, labels = ax.get_legend_handles_labels()
    if handles and legend:
        ax.legend(handles, labels, loc=loc)

    plt.tight_layout()


def anchor_legend(x, y):
    """Place the upper left corner of the legend box.

    Args:
        x: x coordinate
        y: y coordinate
    """
    plt.legend(bbox_to_anchor=(x, y), loc="upper left", ncol=1)
    plt.tight_layout()


def add_text(x, y, text, **options):
    """Add text to the current axes.

    Args:
        x: float
        y: float
        text: string
        options: keyword arguments passed to plt.text
    """
    ax = plt.gca()
    underride(
        options,
        transform=ax.transAxes,
        color="0.2",
        ha="left",
        va="bottom",
        fontsize=9,
    )
    plt.text(x, y, text, **options)


def remove_spines():
    """Remove the spines of a plot but keep the ticks visible."""
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Ensure ticks stay visible
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")


def add_logo(filename="logo-hq-small.png", location=(1.0, -0.35), size=(0.5, 0.25), align_to_axes=False):
    """Add a logo inside an inset axis positioned relative to the main plot.

    Args:
        filename: path to logo image
        location: tuple of (x, y) coordinates
        size: tuple of (width, height)
        align_to_axes: if True, position relative to axes (aligns with title/subtitle);
            if False, position relative to figure (default)

    Returns:
        The inset axis containing the logo
    """
    logo = mpimg.imread(filename)

    # Create an inset axis in the given location
    ax = plt.gca()
    fig = ax.figure
    transform = ax.transAxes if align_to_axes else fig.transFigure
    ax_inset = inset_axes(
        ax,
        width=size[0],
        height=size[1],
        loc="lower right",
        bbox_to_anchor=location,
        bbox_transform=transform,
        borderpad=0,
    )

    # Display the logo
    ax_inset.imshow(logo)
    ax_inset.axis("off")
    
    # Restore the original axes as current
    plt.sca(ax)

    return ax_inset


def add_subtext(text, x=0, y=-0.35, align_to_axes=False):
    """Add a text label below the current plot.

    Args:
        text: string
        x: x coordinate
        y: y coordinate
        align_to_axes: if True, position relative to axes (aligns with title/subtitle);
            if False, position relative to figure (default)

    Returns:
        The text object
    """
    ax = plt.gca()
    fig = ax.figure
    transform = ax.transAxes if align_to_axes else fig.transFigure
    va = "top" if align_to_axes else "bottom"
    return plt.figtext(
        x, y, text, ha="left", va=va, fontsize=8, transform=transform
    )


def add_title(title, subtitle, pad=25, x=0, y=1.02):
    """Add a title and subtitle to the current plot.

    Args:
        title: Title of the plot
        subtitle: Subtitle of the plot
        pad: Padding between the title and subtitle
        x: x coordinate for subtitle
        y: y coordinate for subtitle
    """
    plt.title(title, loc="left", pad=pad)
    add_text(x, y, subtitle)


def reverse_color_map(color_map):
    """Reverse the order of colors in a color map.

    Args:
        color_map: dictionary mapping values to colors

    Returns:
        dictionary with reversed color order
    """
    return {k: v for k, v in reversed(list(color_map.items()))}


# =============================================================================
# Survey Data Visualization Functions
# =============================================================================


def plot_responses(
    summary, gender, response, issue_names, style, label_response=True, **options
):
    """Plot survey responses.

    Args:
        summary: DataFrame with response data
        gender: gender code
        response: response code
        issue_names: list of issue names
        style: dictionary of style parameters
        label_response: whether to label the response
        options: additional plotting options
    """
    # Filter data for this gender and response
    data = summary[
        (summary["gender"] == gender) & (summary["value"] == response)
    ].copy()

    # Plot each issue
    for i, issue in enumerate(issue_names):
        row = data[data["column"] == issue].iloc[0]
        plot_estimate(i, row, style, label_response, **options)


def plot_responses_by_gender(summary, response, issue_names, **options):
    """Plot survey responses by gender.

    Args:
        summary: DataFrame with response data
        response: response code
        issue_names: list of issue names
        options: additional plotting options
    """
    # Define styles for each gender
    styles = {
        1: dict(color=AIBM_COLORS["blue"], label="Men"),
        2: dict(color=AIBM_COLORS["orange"], label="Women"),
    }

    # Plot responses for each gender
    for gender in [1, 2]:
        plot_responses(
            summary, gender, response, issue_names, styles[gender], **options
        )


def stacked_bar_chart(y, estimate, color_map, **options):
    """Create a stacked bar chart.

    Args:
        y: y coordinate
        estimate: DataFrame with estimates
        color_map: dictionary mapping values to colors
        options: additional plotting options
    """
    # Plot each segment
    for value, color in color_map.items():
        row = estimate[estimate["value"] == value].iloc[0]
        plt.barh(y, row["proportion"], color=color, **options)


def plot_age_gender_summary(
    summary, age_map, group_name_map, color_map, response_map, y=0
):
    """Plot summary by age and gender.

    Args:
        summary: DataFrame with summary data
        age_map: dictionary mapping age codes to labels
        group_name_map: dictionary mapping group codes to names
        color_map: dictionary mapping values to colors
        response_map: dictionary mapping response codes to labels
        y: starting y coordinate
    """
    # Plot each age group
    for age, age_label in age_map.items():
        # Plot each gender
        for gender, gender_label in group_name_map.items():
            # Filter data for this age and gender
            data = summary[
                (summary["age"] == age) & (summary["gender"] == gender)
            ].copy()

            # Plot responses
            for response, label in response_map.items():
                row = data[data["value"] == response].iloc[0]
                plot_estimate(y, row, color_map[response], label, **options)
                y += 1


def plot_estimate(y, row, style, label, **options):
    """Plot a single estimate.

    Args:
        y: y coordinate
        row: DataFrame row with estimate data
        style: dictionary of style parameters
        label: label for the estimate
        options: additional plotting options
    """
    # Plot the estimate
    plt.barh(y, row["proportion"], **style, **options)

    # Add error bars
    plt.errorbar(
        row["proportion"],
        y,
        xerr=[[row["proportion"] - row["lower"]], [row["upper"] - row["proportion"]]],
        fmt="none",
        color="black",
        capsize=3,
    )

    # Add label
    if label:
        plt.text(
            row["proportion"] + 0.01,
            y,
            label,
            va="center",
            ha="left",
            fontsize=9,
        )


def plot_estimates(estimate, style, label, **options):
    """Plot multiple estimates.

    Args:
        estimate: DataFrame with estimates
        style: dictionary of style parameters
        label: label for the estimates
        options: additional plotting options
    """
    # Plot each estimate
    for i, row in estimate.iterrows():
        plot_estimate(i, row, style, label, **options)


def add_responses(response_map):
    """Add response labels to the plot.

    Args:
        response_map: dictionary mapping response codes to labels
    """
    # Add each response label
    for response, label in response_map.items():
        plt.text(
            0,
            response,
            label,
            va="center",
            ha="right",
            fontsize=9,
        )


def plot_estimates_by_age_gender(summary, age_map, group_name_map, **options):
    """Plot estimates by age and gender.

    Args:
        summary: DataFrame with summary data
        age_map: dictionary mapping age codes to labels
        group_name_map: dictionary mapping group codes to names
        options: additional plotting options
    """
    # Plot each age group
    for age, age_label in age_map.items():
        # Plot each gender
        for gender, gender_label in group_name_map.items():
            # Filter data for this age and gender
            data = summary[
                (summary["age"] == age) & (summary["gender"] == gender)
            ].copy()

            # Plot estimates
            plot_estimates(data, gender_label, **options)


code_to_wef_country = {
    "ALB": "Albania",
    "DZA": "Algeria",
    "AGO": "Angola",
    "ARG": "Argentina",
    "ARM": "Armenia",
    "AUS": "Australia",
    "AUT": "Austria",
    "AZE": "Azerbaijan",
    "BHR": "Bahrain",
    "BGD": "Bangladesh",
    "BRB": "Barbados",
    "BLR": "Belarus",
    "BEL": "Belgium",
    "BLZ": "Belize",
    "BEN": "Benin",
    "BTN": "Bhutan",
    "BOL": "Bolivia",
    "BIH": "Bosnia-Herzegovina",
    "BWA": "Botswana",
    "BRA": "Brazil",
    "BRN": "Brunei",
    "BGR": "Bulgaria",
    "BFA": "Burkina Faso",
    "BDI": "Burundi",
    "KHM": "Cambodia",
    "CMR": "Cameroon",
    "CAN": "Canada",
    "CPV": "Cape Verde",
    "TCD": "Chad",
    "CHL": "Chile",
    "CHN": "China",
    "COL": "Colombia",
    "COM": "Comoros",
    "COD": "D.R. Congo",
    "CRI": "Costa Rica",
    "CIV": "Côte D'Ivoire",
    "HRV": "Croatia",
    "CYP": "Cyprus",
    "CZE": "Czechia",
    "DNK": "Denmark",
    "DOM": "Dominican Republic",
    "ECU": "Ecuador",
    "EGY": "Egypt",
    "SLV": "El Salvador",
    "EST": "Estonia",
    "SWZ": "Eswatini",
    "ETH": "Ethiopia",
    "FJI": "Fiji",
    "FIN": "Finland",
    "FRA": "France",
    "GMB": "Gambia",
    "GEO": "Georgia",
    "DEU": "Germany",
    "GHA": "Ghana",
    "GRC": "Greece",
    "GTM": "Guatemala",
    "GIN": "Guinea",
    "GUY": "Guyana",
    "HND": "Honduras",
    "HUN": "Hungary",
    "ISL": "Iceland",
    "IND": "India",
    "IDN": "Indonesia",
    "IRN": "Iran",
    "IRL": "Ireland",
    "ISR": "Israel",
    "ITA": "Italy",
    "JAM": "Jamaica",
    "JPN": "Japan",
    "JOR": "Jordan",
    "KAZ": "Kazakhstan",
    "KEN": "Kenya",
    "KWT": "Kuwait",
    "KGZ": "Kyrgyzstan",
    "LAO": "Laos",
    "LVA": "Latvia",
    "LBN": "Lebanon",
    "LSO": "Lesotho",
    "LBR": "Liberia",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MDG": "Madagascar",
    "MYS": "Malaysia",
    "MDV": "Maldives",
    "MLI": "Mali",
    "MLT": "Malta",
    "MUS": "Mauritius",
    "MEX": "Mexico",
    "MDA": "Moldova",
    "MNG": "Mongolia",
    "MNE": "Montenegro",
    "MAR": "Morocco",
    "MOZ": "Mozambique",
    "NAM": "Namibia",
    "NPL": "Nepal",
    "NLD": "Netherlands",
    "NZL": "New Zealand",
    "NIC": "Nicaragua",
    "NER": "Niger",
    "NGA": "Nigeria",
    "MKD": "North Macedonia",
    "NOR": "Norway",
    "OMN": "Oman",
    "PAK": "Pakistan",
    "PAN": "Panama",
    "PRY": "Paraguay",
    "PER": "Peru",
    "PHL": "Philippines",
    "POL": "Poland",
    "PRT": "Portugal",
    "QAT": "Qatar",
    "ROU": "Romania",
    "RWA": "Rwanda",
    "SAU": "Saudi Arabia",
    "SEN": "Senegal",
    "SRB": "Serbia",
    "SLE": "Sierra Leone",
    "SGP": "Singapore",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "ZAF": "South Africa",
    "KOR": "South Korea",
    "ESP": "Spain",
    "LKA": "Sri Lanka",
    "SDN": "Sudan",
    "SUR": "Suriname",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "TJK": "Tajikistan",
    "THA": "Thailand",
    "TLS": "Timor-Leste",
    "TGO": "Togo",
    "TUN": "Tunisia",
    "TUR": "Türkiye",
    "UGA": "Uganda",
    "UKR": "Ukraine",
    "ARE": "United Arab Emirates",
    "GBR": "United Kingdom",
    "TZA": "Tanzania",
    "USA": "United States",
    "URY": "Uruguay",
    "UZB": "Uzbekistan",
    "VUT": "Vanuatu",
    "VNM": "Vietnam",
    "ZMB": "Zambia",
    "ZWE": "Zimbabwe",
    # Additional countries not in original list
    "ABW": "Aruba",
    "CAF": "Central African Republic",
    "COG": "Congo",
    "CUB": "Cuba",
    "CYM": "Cayman Islands",
    "ERI": "Eritrea",
    "GAB": "Gabon",
    "GNB": "Guinea-Bissau",
    "GNQ": "Equatorial Guinea",
    "GUM": "Guam",
    "HTI": "Haiti",
    "MAC": "Macao",
    "MMR": "Myanmar",
    "MRT": "Mauritania",
    "MWI": "Malawi",
    "NCL": "New Caledonia",
    "PNG": "Papua New Guinea",
    "PRI": "Puerto Rico",
    "PRK": "North Korea",
    "SSD": "South Sudan",
    "STP": "São Tomé and Príncipe",
    "SYC": "Seychelles",
    "SYR": "Syria",
    "TKM": "Turkmenistan",
    "TTO": "Trinidad and Tobago",
    "VEN": "Venezuela",
    "YEM": "Yemen",
}

wef_country_to_code = {country: code for code, country in code_to_wef_country.items()}

# Create a copy for WHO data with additional countries
code_to_who_country = code_to_wef_country.copy()

# Add missing country codes for WHO data
code_to_who_country.update({
    "AFG": "Afghanistan",
    "AND": "Andorra",
    "ATG": "Antigua and Barbuda",
    "BHS": "Bahamas",
    "COK": "Cook Islands",
    "DJI": "Djibouti",
    "FSM": "Federated States of Micronesia",
    "GRD": "Grenada",
    "IRQ": "Iraq",
    "KIR": "Kiribati",
    "LBY": "Libya",
    "LCA": "Saint Lucia",
    "MHL": "Marshall Islands",
    "NRU": "Nauru",
    "PLW": "Palau",
    "PSE": "Palestine",
    "RUS": "Russia",
    "SLB": "Solomon Islands",
    "SOM": "Somalia",
    "TON": "Tonga",
    "TUV": "Tuvalu",
    "VCT": "Saint Vincent and the Grenadines",
    "WSM": "Samoa",
})

oecd_codes = ['AUS', 'AUT', 'BEL', 'CAN', 'CHE', 'CHL', 'COL', 'CRI', 'CZE',
              'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GRC', 'HUN', 'IRL',
              'ISL', 'ISR', 'ITA', 'JPN', 'KOR', 'LTU', 'LUX', 'LVA', 'MEX',
              'NLD', 'NOR', 'NZL', 'POL', 'PRT', 'SVK', 'SVN', 'SWE', 'TUR', 'USA']


def codes_to_country_names(codes, mapping=None):
    """Convert country codes to country names.
    
    Args:
        codes: List, Series, Index, or array-like of country codes (e.g., 'USA', 'GBR')
        mapping: Dictionary mapping codes to names. If None, uses code_to_who_country.
        
    Returns:
        List of country names. If a code is not found in the mapping, returns the code itself.
    """
    if mapping is None:
        mapping = code_to_who_country
    
    if isinstance(codes, pd.Series) or isinstance(codes, pd.Index):
        codes = codes.tolist()
    
    return [mapping.get(code, code) for code in codes]




def read_wef_file(filename):
    """Read the WEF file and return a DataFrame.
    
    Args:
        filename: name of the WEF file
    """
    df = pd.read_csv(filename)

    df["country"] = df["country"].replace(
        {
            "United States of America": "United States",
            "Brunei Darussalam": "Brunei",
            "Moldova, Republic of": "Moldova",
            "Congo, Democratic Republic of t": "D.R. Congo",
            "United Republic of Tanzania": "Tanzania",
            "Viet Nam": "Vietnam",
            "Bosnia and Herzegovina": "Bosnia-Herzegovina",
            "Lao PDR": "Laos",
        }
    )
    df.index = df["country"].map(wef_country_to_code)
    df.index.name = "code"
    return df


def save_revised_scores(df, notebook_name, suffix='revised_scores'):
    """Save revised scores dataframe to CSV file.
    
    Args:
        df: DataFrame with revised scores
        notebook_name: name of the notebook
        suffix: suffix to add to the filename
    """
    columns = ['country', 'score', 'revised_score']
    df = df[columns]
    
    # Create filename
    filename = f"{notebook_name}_{suffix}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved revised scores to {filename}")


def plot_revised_scores(df, symbols=['x', 'o'], **options):
    """Plot revised scores for countries.
        
    Args:
        df: DataFrame with revised scores
    """
    n = len(df)
    height = 15 * n / 100
    fig, ax = plt.subplots(figsize=(6, height))
    plt.hlines(
        df["country"], df["score"], df["revised_score"], 
        color=AIBM_COLORS["light_gray"]
    )
    underride(options, ms=5, color=AIBM_COLORS["orange"])
    plt.plot(df["score"], df["country"], symbols[0], label='WEF score',
             **options)
    plt.plot(df["revised_score"], df["country"], symbols[1], label='revised score',
             **options)
    ax.invert_yaxis()
    plt.ylim(n + 1, -1)
    embolden_countries(['United States'])


def plot_revised_ranks(df, **options):
    """Plot revised ranks for countries.
        
    Args:
        df: DataFrame with revised ranks
    """
    n = len(df)
    height = 15 * n / 100
    fig, ax = plt.subplots(figsize=(6, height))
    plt.hlines(
        df["country"], df["rank"], df["revised_rank"], 
        color=AIBM_COLORS["light_gray"]
    )
    underride(options, color=AIBM_COLORS["purple"])
    plt.plot(df["rank"], df["country"], "|", **options)
    plt.plot(df["revised_rank"], df["country"], "o", **options)
    ax.invert_yaxis()
    plt.ylim(n + 1, -1)
    embolden_countries(['United States'])
    
def embolden_countries(countries):
    # Make selected countries bold
    ax = plt.gca()
    ytick_labels = ax.get_yticklabels()
    for i, label in enumerate(ytick_labels):
        if label.get_text() in countries:
            plt.setp(label, fontweight='bold')


def plot_score_distributions(df, **options):
    kde_options = dict(cut=0, bw_adjust=0.7)

    sns.kdeplot(df['score'], label='WEF truncated scores', **kde_options)
    sns.kdeplot(df['revised_score'], label='Revised symmetric scores', **kde_options)

    decorate(**options)
    add_subtext("Source: World Economic Forum", y=-0.25)
    logo = add_logo(location=(1.0, -0.25))


def make_weights(column, label):
    std = column.std() 
    weights = pd.DataFrame(std, index=[label], columns=['std'])
    weights['inv std'] = 0.01 / std
    return weights

def make_weight_table(table, label):
    weights_orig = make_weights(table['score'], label)
    weights_revised = make_weights(table['revised_score'], label)
    weights = pd.concat([weights_orig, weights_revised],
                        axis=1, 
                        keys=['original', 'revised'])
    return weights

def make_rank_table(df):
    columns = ['country', 'ratio', 'rank', 'revised_rank', 'score', 'revised_score']
    df['revised_rank'] = df['revised_score'].rank(method='min', ascending=False)
    table = df[columns]
    return table

def plot_percentages(df):
    df['male'] = df['left'].where(df['score'] == 1, df['right'])
    df['female'] = df['right'].where(df['score'] == 1, df['left'])

    plot_indicators(df)

def save_percentages(df, notebook_name, suffix='percentages', sort=True):
    """Save percentages dataframe to CSV file.
    
    Args:
        df: DataFrame with percentages
        notebook_name: name of the notebook
        suffix: suffix to add to the filename
        sort: whether to sort the dataframe by female percentage
    """
    df['male'] = df['left'].where(df['score'] == 1, df['right'])
    df['female'] = df['right'].where(df['score'] == 1, df['left'])

    save_indicators(df, notebook_name, suffix, sort)

def plot_indicators(df, sort=True):
    """Plot percentages for indicators.
    
    Args:
        df: DataFrame with percentages
        sort: whether to sort the dataframe by female percentage
    """
    if sort:
        df_sorted = df.sort_values(by='female', ascending=False)
    else:
        df_sorted = df
    country = df_sorted['country']
    male = df_sorted['male']
    female = df_sorted['female']

    fig, ax = plt.subplots(figsize=(6, 6))
    plt.hlines(country, male, female, color=AIBM_COLORS['light_gray'])
    plt.plot(male, country, 's', color=AIBM_COLORS['green'], label='Male')
    plt.plot(female, country, 'o', color=AIBM_COLORS['purple'], label='Female')
    
    n = len(df_sorted)
    decorate(ylim=[n + 0.5, -0.5])

    add_subtext("Source: WEF Global Gender Gap Report", y=-0.05)
    logo = add_logo(location=(1.0, -0.05))
    embolden_countries(['United States'])

def save_indicators(df, notebook_name, suffix='indicators', sort=True):
    """Save indicators dataframe to CSV file.
    
    Args:
        df: DataFrame with indicators
        notebook_name: name of the notebook
        suffix: suffix to add to the filename
        sort: whether to sort the dataframe by female percentage
    """
    if sort:
        df = df.sort_values(by='female', ascending=False)
    columns = ['country', 'male', 'female']
    df = df[columns]
    filename = f"{notebook_name}_{suffix}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved indicators to {filename}")


# =============================================================================
# HTML Table Formatting Functions
# =============================================================================

def fmt_3sig(x):
    """Format a number to 3 significant digits.
    
    Args:
        x: value to format (can be numeric or string)
        
    Returns:
        Formatted string with 3 significant digits, or empty string for NaN,
        or original value if it can't be converted to float
    """
    if pd.isna(x):
        return ""
    try:
        return f"{float(x):.3g}"
    except Exception:
        return x  # leave strings untouched


def style_correlations(styler, df):
    """Highlight min/max values in correlation columns.
    
    Highlights the maximum correlation in light green and the minimum
    correlation in light red/pink.
    
    Args:
        styler: pandas Styler object
        df: DataFrame to style
        
    Returns:
        Styled Styler object
    """
    corr_cols = [c for c in df.columns if "Corr" in c]
    if not corr_cols:
        return styler
    
    for col in corr_cols:
        series = df[col]
        if series.notna().any():
            vmin = series.min()
            vmax = series.max()
            
            def color(val):
                if pd.isna(val):
                    return ""
                if val == vmax:
                    return "background-color: #90EE90"  # light green
                if val == vmin:
                    return "background-color: #FFB6C1"  # light red
                return ""
            
            styler = styler.map(color, subset=[col])
    return styler


def make_table(df):
    """Create a styled HTML table from a DataFrame.
    
    Formats numbers to 3 significant digits, centers text, and applies
    correlation highlighting if correlation columns are present.
    
    Args:
        df: DataFrame to style
        
    Returns:
        Styled Styler object ready for HTML export
    """
    styler = (
        df.style
        .format(fmt_3sig)                                    # numeric formatting
        .set_properties(**{"text-align": "center"})          # align body cells
        .set_table_styles(                                   
            [{"selector": "th", "props": [("text-align", "center")]}]  # align headers
        )
    )
    
    # Apply correlation highlighting if needed
    styler = style_correlations(styler, df)
    
    return styler


def write_html_table(df, path):
    """Write a DataFrame as a styled HTML table.
    
    Args:
        df: DataFrame to write
        path: file path for the HTML output
    """
    # Create styled table and export
    # Use hide() method to explicitly hide the index, as Styler.to_html() 
    # may not always respect index=False parameter
    styler = make_table(df)
    styler = styler.hide(axis='index')
    styler.to_html(path)


from IPython.display import Audio, display
from functools import reduce
import warnings

def beep(duration = 0.5, frequency = 440):
    sample_rate = 22050

    t = np.linspace(0, duration, int(sample_rate * duration))
    beep = np.sin(2 * np.pi * frequency * t)

    display(Audio(beep, rate=sample_rate, autoplay=True))


def setup_beep_on_error():
    """
    Configure IPython to beep when an exception occurs.
    Call this at the start of a notebook to get audio feedback on errors.
    """
    import IPython
    
    def beep_on_error(shell, etype, evalue, tb, tb_offset=None):
        beep()
        # Call the original handler so the traceback still appears
        shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
    
    ip = IPython.get_ipython()
    if ip is not None:
        ip.set_custom_exc((Exception,), beep_on_error)


# Global log file reference (set by notebooks)
_log_file = None

def set_log_file(log_file):
    """Set the global log file for log_and_print to use."""
    global _log_file
    _log_file = log_file


def log_and_print(message, log_file=None):
    """
    Print message to notebook AND write to log file.
    
    Use this instead of print() in notebooks to ensure output is captured
    in both the notebook and the log file for later review.
    
    Parameters
    ----------
    message : str
        Message to log and print
    log_file : file object, optional
        Log file handle. If None, uses global _log_file set by set_log_file().
    """
    global _log_file
    
    if log_file is None:
        log_file = _log_file
    
    if log_file:
        log_file.write(message + "\n")
        log_file.flush()
    
    print(message)


# =============================================================================
# HALE Analysis Functions
# =============================================================================

def load_and_inventory(filename, cutoff_year=2019):
    """
    Load a WHO health indicator CSV file and print inventory information.
    
    Filters the data to include only records from year 2000 to cutoff_year (default: 2019),
    and country-level data (excludes regional aggregates).
    Adds a 'Country' column mapping country codes to country names using code_to_who_country.
    
    Parameters
    ----------
    filename : str
        Path to the CSV file containing WHO health indicator data.
    cutoff_year : int, optional
        Maximum year to include in the filtered data. Default is 2019.
        Note: When including COVID-19 data, cutoff_year should be set to 2021 to match
        HALE and Life Expectancy data availability (which are only available through 2021).
        
    Returns
    -------
    df : pandas.DataFrame
        Filtered DataFrame containing country-level data from 2000 to cutoff_year,
        with an additional 'Country' column.
    years : numpy.ndarray
        Array of unique years present in the filtered dataset.
    """
    # Filter to 2000-cutoff_year and country-level data only
    df = pd.read_csv(filename).query(f'Year >= 2000 and Year <= {cutoff_year} and CountryCode == "COUNTRY"')
    
    # Add country name column using code_to_who_country mapping
    # The 'Country' column contains country codes (e.g., 'USA', 'GBR')
    # Rename 'Country' (codes) to 'Code', then add 'Country' (names)
    df = df.rename(columns={'Country': 'Code'})
    df['Country'] = df['Code'].map(code_to_who_country)
    
    print(df.shape)

    sexes = df['Sex'].unique()
    print(sexes)
    print(df['Comments'].unique())
    years = df['Year'].unique()
    print(years)
    
    return df, years


def compute_gender_gap(df, value_col, sexes):
    """
    Return a DataFrame with separate columns for each sex, a gap column, and a midpoint column,
    handling cases where one or more sexes are missing.

    Parameters
    ----------
    df : pandas.DataFrame
        Must include 'Code' (country codes), 'Year', 'Sex', and the specified value_col.
        May also include 'Country' (country names) which will be preserved.
    value_col : str
        Name of the column containing the numeric value to compare between sexes.
    sexes : list of str
        List of values in the 'Sex' column, e.g. ['SEX_MLE', 'SEX_FMLE'].
        The first two entries are used to compute the gap (first - second) and midpoint (average).

    Returns
    -------
    df_by_sex : pandas.DataFrame
        Contains columns for each available sex, a gap column (Gap_{value_col} = first - second, i.e., Male - Female),
        and a midpoint column (Mid_{value_col} = average of first and second) if both sexes
        are present. Also includes 'Country' (added via mapping) and 'Year'.
    """
    # Determine which columns to keep
    # Base columns: Code (country codes), Year, and the value column (which will be renamed)
    # Country (country names) will be added later via mapping
    base_cols = ['Code', 'Year']
    
    dfs = []

    # Build a renamed DataFrame for each sex, only if it exists
    # Select only the columns we want to keep before merging
    for sex in sexes:
        temp = df[df['Sex'] == sex]
        if not temp.empty:
            # Select only the columns we need: base columns + value column
            cols_to_select = base_cols + [value_col]
            temp = temp[cols_to_select].copy()
            # Rename the value column to include the sex
            temp = temp.rename(columns={value_col: f"{value_col}_{sex}"})
            dfs.append(temp)

    # If no data at all, return empty DataFrame
    if not dfs:
        return pd.DataFrame(columns=['Code', 'Year'])

    # Merge all available sexes
    merge_on = ['Code', 'Year']
    df_by_sex = reduce(lambda left, right: left.merge(right, on=merge_on, how='outer'), dfs)

    # Compute the gap and midpoint only if both sexes are available
    # Gap = Male - Female (first - second, where first is typically Male)
    if len(sexes) >= 2:
        col1 = f"{value_col}_{sexes[0]}"
        col2 = f"{value_col}_{sexes[1]}"
        if col1 in df_by_sex.columns and col2 in df_by_sex.columns:
            df_by_sex[f"Gap_{value_col}"] = df_by_sex[col1] - df_by_sex[col2]
            df_by_sex[f"Mid_{value_col}"] = (df_by_sex[col1] + df_by_sex[col2]) / 2

    df_by_sex['Country'] = df_by_sex['Code'].map(code_to_who_country)

    return df_by_sex


def summarize_gap(df, col, sexes=None, cutoff_year=None):
    """
    Compute gender gap and create summary visualization using most recent data per country.
    
    Computes gender gaps using compute_gender_gap, then selects the most recent year
    available for each country up to cutoff_year (if provided). Creates two scatter plots
    for OECD countries: Female vs Male, and Gap vs Mid (Overall).
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing health indicator data with 'Code' (country codes), 'Year', 'Sex',
        and the value column specified by col. May also include 'Country' (country names).
    col : str
        Name of the column containing the numeric value to compare between sexes.
    sexes : list of str
        List of sex values to compare (e.g., ['Male', 'Female']).
    cutoff_year : int, optional
        Maximum year to include. If provided, selects the most recent year <= cutoff_year
        for each country. If None, uses the most recent available year for each country.
        
    Returns
    -------
    df_gap : pandas.DataFrame
        DataFrame with the most recent available year (up to cutoff_year) for each country,
        indexed by Code. Includes 'Country' and 'Year' columns, plus gender-specific columns
        (e.g., '{col}_Male', '{col}_Female'), gap columns (e.g., 'Gap_{col}'), and midpoint
        columns (e.g., 'Mid_{col}'). Returns all countries, not just OECD.
    """
    sexes = sexes or ['Male', 'Female']
    df_gap = compute_gender_gap(df, col, sexes)
    
    # Filter to cutoff_year if provided
    if cutoff_year is not None:
        df_gap = df_gap[df_gap['Year'] <= cutoff_year]
    
    # Get the most recent year for each country (after cutoff filtering)
    most_recent_years = df_gap.groupby('Code')['Year'].max().reset_index()
    df_gap = df_gap.merge(most_recent_years, on=['Code', 'Year'])
    
    # Set index to Code, but keep Country and Year as columns
    df_gap = df_gap.set_index('Code')
    
    if len(sexes) > 1:
        cols = [f'{col}_{sex}' for sex in sexes]
        # Get OECD countries for plotting
        df_gap_oecd = get_oecd(df_gap)
        
        # Create figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Female vs Male
        plt.sca(ax1)
        high = df_gap_oecd[cols].max().max()
        domain = [0, high]
        scatter_plot(df_gap_oecd, [cols[0], cols[1]], domain)
        decorate(xlabel=f'{col}, Male', 
                 ylabel=f'{col}, Female', 
                 title=f'OECD Countries: Female vs Male')
        
        # Plot 2: Gap vs Mid (Overall)
        plt.sca(ax2)
        gap_col = f'Gap_{col}'
        mid_col = f'Mid_{col}'
        # Compute domain that encompasses both Gap and Mid
        gap_min = df_gap_oecd[gap_col].min()
        gap_max = df_gap_oecd[gap_col].max()
        mid_min = df_gap_oecd[mid_col].min()
        mid_max = df_gap_oecd[mid_col].max()
        
        # Use the full range that covers both variables
        overall_min = min(gap_min, mid_min, 0)  # Include 0 for reference
        overall_max = max(gap_max, mid_max)
        domain = [overall_min, overall_max]
        
        scatter_plot(df_gap_oecd, [mid_col, gap_col], domain)
        decorate(xlabel=f'{col}, Overall (Mid)', 
                 ylabel=f'{col}, Gap', 
                 title=f'OECD Countries: Gap vs Overall')
        
        plt.tight_layout()
    
    return df_gap


def scatter_plot(df, cols, domain, **options):
    """
    Create a scatter plot comparing two columns with a diagonal reference line.
    
    Plots the values from two columns against each other, with a diagonal
    reference line (y=x) to show equality. Uses a square aspect ratio by default.
    Labels specific countries: USA, DEU, LTU, NDL.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame indexed by country, containing the columns to plot.
    cols : list of str
        List of two column names to plot on x and y axes.
    domain : list of float
        Two-element list [min, max] defining the plot domain for both axes.
    **options : dict
        Additional keyword arguments passed to decorate() for plot customization
        (e.g., xlabel, ylabel, title).
    """
    plt.plot(df[cols[0]], df[cols[1]], '.', color=AIBM_COLORS['crimson'])
    plt.plot(domain, domain, color='gray', alpha=0.5)
    
    # Label specific countries
    countries_to_label = ['USA', 'DEU', 'LTU', 'NLD']
    for country in countries_to_label:
        if country in df.index:
            x_val = df.loc[country, cols[0]]
            y_val = df.loc[country, cols[1]]
            if pd.notna(x_val) and pd.notna(y_val):
                plt.annotate(country, (x_val, y_val), 
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9, alpha=0.8)
    
    underride(options, aspect='equal')
    decorate(**options)


def get_oecd(df):
    """
    Filter DataFrame to include only OECD member countries.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame indexed by country codes.
        
    Returns
    -------
    pandas.DataFrame
        Subset of the input DataFrame containing only OECD countries.
        
    Note
    -----
    Warns if any expected OECD countries are missing from the data.
    """
    available_countries = set(df.index)
    expected_oecd = set(oecd_codes)
    missing_countries = expected_oecd - available_countries
    
    if missing_countries:
        warnings.warn(
            f"Missing {len(missing_countries)} OECD countries in data: {sorted(missing_countries)}",
            UserWarning
        )
    
    return df.loc[df.index.intersection(oecd_codes)]


def summarize_years(predictor_dfs):
    """
    Create a summary table of year coverage for each indicator in predictor_dfs.
    
    Parameters
    ----------
    predictor_dfs : dict
        Dictionary mapping indicator names to DataFrames containing predictor data.
        Each DataFrame should have a 'Year' column.
        
    Returns
    -------
    pandas.DataFrame
        Summary table with columns: Indicator, Low_Year, High_Year, Most_Common_Year,
        N_Countries_Most_Common, Total_Countries.
    """
    year_summary = []
    
    for name, df in predictor_dfs.items():
        years = df['Year'].dropna()
        if len(years) > 0:
            year_counts = years.value_counts()
            most_common_year = year_counts.index[0]
            n_countries_most_common = year_counts.iloc[0]
            
            year_summary.append({
                'Indicator': name,
                'Low_Year': int(years.min()),
                'High_Year': int(years.max()),
                'Most_Common_Year': int(most_common_year),
                'N_Countries_Most_Common': int(n_countries_most_common),
                'Total_Countries': len(df)
            })
        else:
            year_summary.append({
                'Indicator': name,
                'Low_Year': np.nan,
                'High_Year': np.nan,
                'Most_Common_Year': np.nan,
                'N_Countries_Most_Common': 0,
                'Total_Countries': len(df)
            })
            
    return pd.DataFrame(year_summary)


def plot_cdfs(df, label='', **options):
    """
    Plot cumulative distribution functions (CDFs) for columns ending in 'ale'.
    
    Creates CDF plots for all columns in the DataFrame that end with 'ale'
    (typically 'Male' and 'Female' columns). Each CDF is plotted with a label
    combining the column name and the provided label.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing numeric columns to plot as CDFs.
    label : str, optional
        Additional label text to append to each CDF plot label (default: '').
    **options : dict
        Additional keyword arguments for plot customization.
    """
    try:
        from empiricaldist import Cdf
    except ImportError:
        raise ImportError("empiricaldist is required for plot_cdfs. Install with: pip install empiricaldist")
    
    cols = [col for col in df.columns if col.endswith('ale')]
    for col in cols:
        vals = df[col].dropna()
        if vals.count() == 0:
            break
        cdf = Cdf.from_seq(df[col])
        cdf.plot(label=f'{col} {label}', **options)


def plot_distributions(recent, indicator_name=None, all_countries=False, **options):
    """
    Plot CDFs comparing all countries vs OECD countries.
    
    Creates cumulative distribution function plots for both all countries
    and OECD countries subset, allowing comparison of distributions.
    
    Parameters
    ----------
    recent : pandas.DataFrame
        DataFrame indexed by country codes, containing columns ending in 'ale'
        (typically 'Male' and 'Female' columns).
    indicator_name : str, optional
        Name of the indicator to use for the x-axis label. If not provided,
        will attempt to extract from column names.
    **options : dict
        Additional keyword arguments passed to decorate() for plot customization
        (e.g., xlabel, title). The ylabel is automatically set to 'CDF'.
    """
    plot_cdfs(get_oecd(recent), label='OECD')
    if all_countries:
        plot_cdfs(recent, label='All countries')
    
    # Use provided indicator name, or extract from column names if not provided
    if indicator_name is None:
        # Extract indicator name from column names (remove _Male or _Female suffix)
        cols = [col for col in recent.columns if col.endswith('ale')]
        if cols:
            # Get the first column and extract the indicator name
            first_col = cols[0]
            # Remove _Male or _Female suffix to get the indicator name
            indicator_name = '_'.join(first_col.rsplit('_')[:-1]) if '_' in first_col else first_col
        else:
            indicator_name = ''
    
    underride(options, xlabel=indicator_name, ylabel='CDF')
    decorate(**options)


# Map from original value column names to short indicator names
# Used to rename columns before computing gaps so Gap_ and Mid_ columns use short names
column_name_mapping = {
    'CardioDeathRate': 'Cardiovascular',
    'ChronicRespiratoryDeathRate': 'ChronicRespiratory',
    'SuicideRate': 'Suicide',
    'AlcoholDeathRate': 'Alcohol',
    'PoisoningRate': 'Poisoning',
    'RoadTrafficDeathRate': 'RoadTraffic',
    'HomicideRate': 'Homicide',
    'MaternalMortalityRatio': 'MaternalMortality',
    'U5MR': 'Childhood',
    'DiabetesDeathRate': 'Diabetes',
    'DrugDisorderDeathRate': 'DrugDisorder',
    'UnintentionalInjuriesDeathRate': 'UnintentionalInjury',
    'NeoplasmsDeathRate': 'Neoplasms',
    'LiverDiseaseDeathRate': 'LiverDisease',  # Map to 'LiverDisease' for compatibility with model notebooks
    'AlcoholUseDisordersDeathRate': 'Alcohol',  # Map to 'Alcohol' for compatibility with model notebooks
    'SelfHarmDeathRate': 'Suicide',  # Map to 'Suicide' for compatibility with model notebooks
    'InterpersonalViolenceDeathRate': 'Homicide',  # Map to 'Homicide' for compatibility with model notebooks
    'RoadInjuriesDeathRate': 'RoadTraffic',  # Map to 'RoadTraffic' for compatibility with model notebooks
    'MaternalDisordersDeathRate': 'MaternalDisorders',
    'AllCausesUnder5DeathRate': 'Childhood',  # Map to 'Childhood' for compatibility with model notebooks (replacing WHO U5MR)
    'COVID19DeathRate': 'COVID',  # Map to 'COVID' for compatibility with model notebooks
    'ConflictAndTerrorismDeathRate': 'ConflictTerrorism',
}


def load_ihme_indicator(filename_male, filename_female, value_col_name, indicator_code, indicator_name, min_year=2000, max_year=2019, age_filter='All ages'):
    """
    Load IHME indicator data from separate male and female files and convert to WHO-compatible format.
    
    Converts IHME CSV format (Location=country name, Sex="Male"/"Female") to WHO format
    (Country=country code, Sex="Male"/"Female", etc.). Filters to specified year range and age group.
    
    Parameters
    ----------
    filename_male : str
        Path to the IHME CSV file with male data.
    filename_female : str
        Path to the IHME CSV file with female data.
    value_col_name : str
        Name for the value column (e.g., 'DrugDisorderDeathRate', 'DiabetesDeathRate').
    indicator_code : str
        Indicator code for the IHME indicator (e.g., 'IHME_DRUG_DISORDERS', 'IHME_DIABETES_TYPE2').
    indicator_name : str
        Human-readable indicator name (e.g., 'Drug use disorders, death rate per 100,000').
    min_year : int, optional
        Minimum year to include (default: 2000).
    max_year : int, optional
        Maximum year to include (default: 2019).
    age_filter : str, optional
        Age group to filter (default: 'All ages'). Use '<5 years' for under-5 mortality.
        
    Returns
    -------
    df : pandas.DataFrame
        DataFrame in WHO-compatible format with columns: IndicatorCode, IndicatorName,
        Code, CountryCode, Year, Sex, value_col_name, value_col_name_Low, 
        value_col_name_High, Country.
    """
    # Create reverse mapping from country name to code
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    
    # Map IHME country names that differ from WHO names
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States'
    }
    
    def process_ihme_file(filename, sex_value, year_min, year_max, age_val):
        """Helper function to process a single IHME file."""
        df = pd.read_csv(filename)
        
        # Filter to year range (exclude 2020+ for COVID-19 reasons by default)
        df = df.query('Year >= @year_min and Year <= @year_max')
        
        # Filter to specified age group
        if 'Age' in df.columns:
            df = df[df['Age'] == age_val]
        
        # Map IHME country names to WHO country names
        df['Location'] = df['Location'].replace(ihme_country_name_mapping)
        
        # Convert country names to codes
        df['Code'] = df['Location'].map(who_country_to_code)
        
        # Filter out rows where country mapping failed (not in our country list)
        df = df[df['Code'].notna()].copy()
        
        # Set Sex column to the specified value (Male or Female)
        df['Sex'] = sex_value
        
        # Rename and create columns to match WHO format
        df['IndicatorCode'] = indicator_code
        df['IndicatorName'] = indicator_name
        df['CountryCode'] = 'COUNTRY'
        df[value_col_name] = df['Value']
        df[f'{value_col_name}_Low'] = df['Lower bound']
        df[f'{value_col_name}_High'] = df['Upper bound']
        df['Country'] = df['Location']
        
        # Select and reorder columns to match WHO format
        columns_to_keep = [
            'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
            value_col_name, f'{value_col_name}_Low', f'{value_col_name}_High',
            'Country'
        ]
        return df[columns_to_keep].copy()
    
    # Load and process both files
    df_male = process_ihme_file(filename_male, 'Male', min_year, max_year, age_filter)
    df_female = process_ihme_file(filename_female, 'Female', min_year, max_year, age_filter)
    
    # Concatenate male and female data
    df = pd.concat([df_male, df_female], ignore_index=True)
    
    # Sort by country, sex, and year
    df = df.sort_values(['Country', 'Sex', 'Year']).reset_index(drop=True)
    
    return df


def raw_to_temporal_gaps(df, value_col_name, mapping=None, sexes=None):
    """
    Transform raw IHME data (from load_ihme_indicator) to temporal format with Mid_*, Gap_*.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Raw DataFrame from load_ihme_indicator with Code, Year, Sex, value_col_name.
    value_col_name : str
        Name of the value column (e.g., 'AlcoholUseDisordersDeathRate').
    mapping : dict, optional
        Mapping from original to short column names. If None, uses column_name_mapping.
    sexes : list of str, optional
        Sex values to compare (default: ['Male', 'Female']).
        
    Returns
    -------
    df_temporal : pandas.DataFrame
        DataFrame with Code, Year, Mid_*, Gap_* for all years.
    """
    if mapping is None:
        mapping = column_name_mapping
    sexes = sexes or ['Male', 'Female']
    df = df.rename(columns=mapping)
    col = mapping.get(value_col_name, value_col_name)
    return compute_gender_gap(df, col, sexes)


def load_ihme_indicator_temporal(base_filename, value_col_name, indicator_code, indicator_name,
                                 max_year=2023, age_filter='All ages', data_dir='../data'):
    """
    Load IHME indicator data and compute temporal gaps for all years.
    
    Thin wrapper: loads via load_ihme_indicator, then transforms via raw_to_temporal_gaps.
    
    Parameters
    ----------
    base_filename : str
        Base filename without path, sex suffix, or extension (e.g., 'ihme_alcohol_use_disorders_deaths')
    value_col_name : str
        Name of the value column (e.g., 'AlcoholUseDisordersDeathRate')
    indicator_code : str
        Indicator code (e.g., 'IHME_ALCOHOL_USE_DISORDERS')
    indicator_name : str
        Human-readable indicator name
    max_year : int, optional
        Maximum year to include (default: 2023)
    age_filter : str, optional
        Age group to filter (default: 'All ages'). Use '<5 years' for under-5 mortality.
    data_dir : str, optional
        Directory containing IHME CSV files (default: '../data' for notebooks/)
        
    Returns
    -------
    df_temporal : pandas.DataFrame
        DataFrame with Code, Year, Mid_*, Gap_* for all years
    """
    filename_male = f'{data_dir}/{base_filename}_male.csv'
    filename_female = f'{data_dir}/{base_filename}_female.csv'
    df = load_ihme_indicator(
        filename_male, filename_female,
        value_col_name=value_col_name,
        indicator_code=indicator_code,
        indicator_name=indicator_name,
        min_year=2000,
        max_year=max_year,
        age_filter=age_filter
    )
    return raw_to_temporal_gaps(df, value_col_name)


def convert_ihme_hale_to_who_format(df):
    """
    Convert IHME HALE data to WHO-compatible format.

    IHME format: location_name, year, sex_name, val, upper, lower
    WHO format: Code, Year, Sex, HALE_Years, Country (plus optional metadata columns)

    Parameters
    ----------
    df : pd.DataFrame
        IHME HALE raw data (e.g., from IHME-GBD CSV)

    Returns
    -------
    pd.DataFrame
        DataFrame with Code, Year, Sex, HALE_Years, Country and optional metadata
    """
    who_country_to_code = {country: code for code, country in code_to_who_country.items()}
    ihme_country_name_mapping = {
        'Republic of Korea': 'South Korea',
        'United States of America': 'United States',
        'Türkiye': 'Turkey'
    }
    df = df.copy().query('year >= 2000')
    df['location_name'] = df['location_name'].replace(ihme_country_name_mapping)
    df['Code'] = df['location_name'].map(who_country_to_code)
    df = df[df['Code'].notna()].copy()
    df['Sex'] = df['sex_name'].map({'Male': 'Male', 'Female': 'Female', 'Both': 'Both'})
    rename_map = {
        'year': 'Year',
        'val': 'HALE_Years',
        'location_name': 'Country'
    }
    if 'upper' in df.columns:
        rename_map['upper'] = 'HALE_Years_High'
    if 'lower' in df.columns:
        rename_map['lower'] = 'HALE_Years_Low'
    df = df.rename(columns=rename_map)
    df['IndicatorCode'] = 'IHME_HALE'
    df['IndicatorName'] = 'Healthy life expectancy (HALE) at birth (years) - IHME'
    df['CountryCode'] = 'COUNTRY'
    columns_to_keep = [
        'IndicatorCode', 'IndicatorName', 'Code', 'CountryCode', 'Year', 'Sex',
        'HALE_Years', 'HALE_Years_Low', 'HALE_Years_High', 'Country'
    ]
    df = df[[c for c in columns_to_keep if c in df.columns]].copy()
    df = df.sort_values(['Country', 'Sex', 'Year']).reset_index(drop=True)
    return df


def convert_owid_le_to_temporal_format(df, min_year=2000, max_year=2023):
    """
    Convert OWID Life Expectancy data to temporal format for Bayesian model.

    OWID format: Entity, Code, Year, life_expectancy__sex_female__age_0, life_expectancy__sex_male__age_0
    Target format: Code, Year, Sex, LifeExpectancy_Years (long format)

    Parameters
    ----------
    df : pd.DataFrame
        OWID LE data
    min_year : int
        Minimum year to include (default: 2000)
    max_year : int
        Maximum year to include (default: 2023)

    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with Code, Year, Sex, LifeExpectancy_Years
    """
    df = df[(df['Year'] >= min_year) & (df['Year'] <= max_year)].copy()
    df = df[df['Code'].isin(oecd_codes)].copy()

    male_df = df[['Code', 'Year', 'life_expectancy__sex_male__age_0']].copy()
    male_df['Sex'] = 'Male'
    male_df = male_df.rename(columns={'life_expectancy__sex_male__age_0': 'LifeExpectancy_Years'})

    female_df = df[['Code', 'Year', 'life_expectancy__sex_female__age_0']].copy()
    female_df['Sex'] = 'Female'
    female_df = female_df.rename(columns={'life_expectancy__sex_female__age_0': 'LifeExpectancy_Years'})

    df_temporal = pd.concat([male_df, female_df], ignore_index=True)
    df_temporal = df_temporal.sort_values(['Code', 'Sex', 'Year']).reset_index(drop=True)
    return df_temporal