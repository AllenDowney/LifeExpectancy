{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0bcdec88",
   "metadata": {},
   "outputs": [],
   "source": [
    "%load_ext autoreload\n",
    "%autoreload 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f3367092",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "from utils import decorate, underride, configure_plot_style, AIBM_COLORS\n",
    "\n",
    "configure_plot_style()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b4f17fc6",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_and_inventory(filename):\n",
    "    \"\"\"\n",
    "    Load a WHO health indicator CSV file and print inventory information.\n",
    "    \n",
    "    Filters the data to include only records from year 2000 onwards and\n",
    "    country-level data (excludes regional aggregates).\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    filename : str\n",
    "        Path to the CSV file containing WHO health indicator data.\n",
    "        \n",
    "    Returns\n",
    "    -------\n",
    "    df : pandas.DataFrame\n",
    "        Filtered DataFrame containing country-level data from 2000 onwards.\n",
    "    years : numpy.ndarray\n",
    "        Array of unique years present in the filtered dataset.\n",
    "    \"\"\"\n",
    "    df = pd.read_csv(filename).query('Year >= 2000 and CountryCode == \"COUNTRY\"')\n",
    "    print(df.shape)\n",
    "\n",
    "    try:\n",
    "        print(df['IndicatorCode'].unique())\n",
    "        print(df['IndicatorName'].unique())\n",
    "    except KeyError:\n",
    "        pass\n",
    "\n",
    "    sexes = df['Sex'].unique()\n",
    "    print(sexes)\n",
    "    print(df['Comments'].unique())\n",
    "    years = df['Year'].unique()\n",
    "    print(years)\n",
    "    print(df['Country'].unique())\n",
    "    \n",
    "    return df, years"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "161660e1",
   "metadata": {},
   "outputs": [],
   "source": [
    "from functools import reduce\n",
    "\n",
    "def compute_gender_gap(df, value_col, sexes):\n",
    "    \"\"\"\n",
    "    Return a DataFrame with separate columns for each sex and a gap column,\n",
    "    handling cases where one or more sexes are missing.\n",
    "\n",
    "    Parameters\n",
    "    ----------\n",
    "    df : pandas.DataFrame\n",
    "        Must include 'Country', 'Year', 'Sex', and the specified value_col.\n",
    "    value_col : str\n",
    "        Name of the column containing the numeric value to compare between sexes.\n",
    "    sexes : list of str\n",
    "        List of values in the 'Sex' column, e.g. ['SEX_MLE', 'SEX_FMLE'].\n",
    "        The first two entries are used to compute the gap (second - first).\n",
    "\n",
    "    Returns\n",
    "    -------\n",
    "    df_by_sex : pandas.DataFrame\n",
    "        Contains columns for each available sex and a gap column (second - first)\n",
    "        if both sexes are present.\n",
    "    \"\"\"\n",
    "    cols = ['Country', 'Year', value_col]\n",
    "    dfs = []\n",
    "\n",
    "    # Build a renamed DataFrame for each sex, only if it exists\n",
    "    for sex in sexes:\n",
    "        temp = df[df['Sex'] == sex]\n",
    "        if not temp.empty:\n",
    "            temp = temp[cols].copy()\n",
    "            temp = temp.rename(columns={value_col: f\"{value_col}_{sex}\"})\n",
    "            dfs.append(temp)\n",
    "\n",
    "    # If no data at all, return empty DataFrame\n",
    "    if not dfs:\n",
    "        return pd.DataFrame(columns=['Country', 'Year'])\n",
    "\n",
    "    # Merge all available sexes\n",
    "    df_by_sex = reduce(lambda left, right: left.merge(right, on=['Country', 'Year'], how='outer'), dfs)\n",
    "\n",
    "    # Compute the gap only if both sexes are available\n",
    "    if len(sexes) >= 2:\n",
    "        col1 = f\"{value_col}_{sexes[0]}\"\n",
    "        col2 = f\"{value_col}_{sexes[1]}\"\n",
    "        if col1 in df_by_sex.columns and col2 in df_by_sex.columns:\n",
    "            df_by_sex[f\"{value_col}_Gap\"] = df_by_sex[col2] - df_by_sex[col1]\n",
    "\n",
    "    return df_by_sex\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d39830ae",
   "metadata": {},
   "outputs": [],
   "source": [
    "def summarize_gap(df, col, sexes=None):\n",
    "    \"\"\"\n",
    "    Compute gender gap and create summary visualization using most recent data per country.\n",
    "    \n",
    "    Computes gender gaps using compute_gender_gap, then selects the most recent year\n",
    "    available for each country (which may differ by country). Creates a scatter plot\n",
    "    comparing values between sexes (if multiple sexes are provided).\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    df : pandas.DataFrame\n",
    "        DataFrame containing health indicator data with 'Country', 'Year', 'Sex',\n",
    "        and the value column specified by col.\n",
    "    col : str\n",
    "        Name of the column containing the numeric value to compare between sexes.\n",
    "    sexes : list of str\n",
    "        List of sex values to compare (e.g., ['Male', 'Female']).\n",
    "        \n",
    "    Returns\n",
    "    -------\n",
    "    df_gap : pandas.DataFrame\n",
    "        DataFrame with gender gap computed for all years.\n",
    "    df_recent : pandas.DataFrame\n",
    "        DataFrame with the most recent available year for each country, indexed by Country.\n",
    "    \"\"\"\n",
    "    sexes = sexes or ['Male', 'Female']\n",
    "    df_gap = compute_gender_gap(df, col, sexes)\n",
    "    \n",
    "    # Get the most recent year for each country\n",
    "    most_recent_years = df_gap.groupby('Country')['Year'].max().reset_index()\n",
    "    df_recent = df_gap.merge(most_recent_years, on=['Country', 'Year']).set_index('Country').drop(columns='Year')\n",
    "    \n",
    "    if len(sexes) > 1:\n",
    "        cols = [f'{col}_{sex}' for sex in sexes]\n",
    "        high = df_recent[cols].max().max()\n",
    "        domain = [0, high]\n",
    "        scatter_plot(df_recent, cols, domain)\n",
    "        # Use the most common recent year for the title\n",
    "        year_counts = most_recent_years['Year'].value_counts()\n",
    "        most_common_year = year_counts.index[0] if len(year_counts) > 0 else most_recent_years['Year'].max()\n",
    "        decorate(xlabel=f'{col}, Male', \n",
    "                 ylabel=f'{col}, Female', title=f'All Countries, most recent year (mostly {most_common_year:.0f})')\n",
    "    \n",
    "    return df_gap, df_recent"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b8b7d58c",
   "metadata": {},
   "outputs": [],
   "source": [
    "def scatter_plot(df, cols, domain, **options):\n",
    "    \"\"\"\n",
    "    Create a scatter plot comparing two columns with a diagonal reference line.\n",
    "    \n",
    "    Plots the values from two columns against each other, with a diagonal\n",
    "    reference line (y=x) to show equality. Uses a square aspect ratio by default.\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    df : pandas.DataFrame\n",
    "        DataFrame indexed by country, containing the columns to plot.\n",
    "    cols : list of str\n",
    "        List of two column names to plot on x and y axes.\n",
    "    domain : list of float\n",
    "        Two-element list [min, max] defining the plot domain for both axes.\n",
    "    **options : dict\n",
    "        Additional keyword arguments passed to decorate() for plot customization\n",
    "        (e.g., xlabel, ylabel, title).\n",
    "    \"\"\"\n",
    "    plt.plot(df[cols[0]], df[cols[1]], '.', color=AIBM_COLORS['crimson'])\n",
    "    plt.plot(domain, domain, color='gray', alpha=0.5)\n",
    "    \n",
    "    underride(options, aspect='equal')\n",
    "    decorate(**options)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7055fd33",
   "metadata": {},
   "outputs": [],
   "source": [
    "from utils import oecd_codes\n",
    "\n",
    "def get_oecd(df):\n",
    "    \"\"\"\n",
    "    Filter DataFrame to include only OECD member countries.\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    df : pandas.DataFrame\n",
    "        DataFrame indexed by country codes.\n",
    "        \n",
    "    Returns\n",
    "    -------\n",
    "    pandas.DataFrame\n",
    "        Subset of the input DataFrame containing only OECD countries.\n",
    "        \n",
    "    Note\n",
    "    -----\n",
    "    Does not warn if any expected OECD countries are missing from the data.\n",
    "    \"\"\"\n",
    "    # TODO: Warn if any are missing\n",
    "    return df.loc[df.index.intersection(oecd_codes)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6f03f408",
   "metadata": {},
   "outputs": [],
   "source": [
    "from empiricaldist import Cdf\n",
    "\n",
    "def plot_cdfs(df, label='', **options):\n",
    "    \"\"\"\n",
    "    Plot cumulative distribution functions (CDFs) for columns ending in 'ale'.\n",
    "    \n",
    "    Creates CDF plots for all columns in the DataFrame that end with 'ale'\n",
    "    (typically 'Male' and 'Female' columns). Each CDF is plotted with a label\n",
    "    combining the column name and the provided label.\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    df : pandas.DataFrame\n",
    "        DataFrame containing numeric columns to plot as CDFs.\n",
    "    label : str, optional\n",
    "        Additional label text to append to each CDF plot label (default: '').\n",
    "    **options : dict\n",
    "        Additional keyword arguments for plot customization.\n",
    "    \"\"\"\n",
    "    cols = [col for col in df.columns if col.endswith('ale')]\n",
    "    for col in cols:\n",
    "        vals = df[col].dropna()\n",
    "        if vals.count() == 0:\n",
    "            break\n",
    "        cdf = Cdf.from_seq(df[col])\n",
    "        cdf.plot(label=f'{col} {label}', **options)\n",
    "        underride(options)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c3a1716d",
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_distributions(recent, **options):\n",
    "    \"\"\"\n",
    "    Plot CDFs comparing all countries vs OECD countries.\n",
    "    \n",
    "    Creates cumulative distribution function plots for both all countries\n",
    "    and OECD countries subset, allowing comparison of distributions.\n",
    "    \n",
    "    Parameters\n",
    "    ----------\n",
    "    recent : pandas.DataFrame\n",
    "        DataFrame indexed by country codes, containing columns ending in 'ale'\n",
    "        (typically 'Male' and 'Female' columns).\n",
    "    **options : dict\n",
    "        Additional keyword arguments passed to decorate() for plot customization\n",
    "        (e.g., xlabel, title). The ylabel is automatically set to 'CDF'.\n",
    "    \"\"\"\n",
    "    plot_cdfs(recent, label='All countries')\n",
    "    plot_cdfs(get_oecd(recent), label='OECD')\n",
    "    \n",
    "    underride(options, ylabel='CDF')\n",
    "    decorate(**options)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1eced9f2",
   "metadata": {},
   "source": [
    "## WHO HALE data\n",
    "\n",
    "**Healthy Life Expectancy (HALE) at birth** - The average number of years that a person can expect to live in \"full health\" by taking into account years lived in less than full health due to disease and/or injury. This is the **target variable** for the analysis. The gender gap (Female HALE - Male HALE) measures the difference in healthy life expectancy between women and men.\n",
    "\n",
    "**Indicator Code**: WHOSIS_000002  \n",
    "**Relevance**: Direct measure of the outcome we're trying to explain. Gender differences in HALE reflect the cumulative impact of all mortality and morbidity factors that differentially affect men and women.\n",
    "\n",
    "Downloaded using the GHO OData API (who_data.py)\n",
    "\n",
    "https://www.who.int/data/gho/info/gho-odata-api"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "86060e5a",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_hale_data.csv'\n",
    "hale, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "173d083b",
   "metadata": {},
   "outputs": [],
   "source": [
    "d = {'SEX_BTSX': 'Both', 'SEX_FMLE': 'Female', 'SEX_MLE': 'Male', }\n",
    "hale['Sex'] = hale['Sex'].replace(d)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b5896591",
   "metadata": {},
   "outputs": [],
   "source": [
    "hale.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6bed9b64",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'HALE_Years'\n",
    "year = years[-1]\n",
    "hale_gap, hale_recent = summarize_gap(hale, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f65c5d33",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(hale_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9788e789",
   "metadata": {},
   "source": [
    "## Smoking\n",
    "\n",
    "**Age-standardized current tobacco smoking prevalence (%)** - Percentage of population aged 15+ who currently smoke any tobacco product, age-standardized for cross-country comparison.\n",
    "\n",
    "**Indicator Code**: M_Est_smk_curr_std  \n",
    "**Relevance**: Historically, men have had significantly higher smoking rates than women. Smoking is a major contributor to cardiovascular disease, lung cancer, and respiratory diseases. As smoking rates have converged between genders in some countries, the life expectancy gap has narrowed, suggesting smoking is one of the most important modifiable factors contributing to the HALE gender gap."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0de00ca6",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_smoking_data.csv'\n",
    "smoking, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "762a1f42",
   "metadata": {},
   "outputs": [],
   "source": [
    "smoking.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c04e0156",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'SmokingPrevalence'\n",
    "year = years[-1]\n",
    "smoking_gap, smoking_recent = summarize_gap(smoking, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a0525a93",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(smoking_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9ca65cce",
   "metadata": {},
   "source": [
    "## Suicide\n",
    "\n",
    "**Age-standardized suicide rates (per 100,000 population)** - Deaths from intentional self-harm, age-standardized for cross-country comparison.\n",
    "\n",
    "**Indicator Code**: MH_12  \n",
    "**Relevance**: Suicide rates are typically higher in men across most countries, directly contributing to the gender gap in mortality. Suicide reflects mental health and social factors that differentially affect men and women, and is strongly linked to mortality."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "85be09d1",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_suicide_rates.csv'\n",
    "suicide, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1785cc28",
   "metadata": {},
   "outputs": [],
   "source": [
    "suicide.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "490a852c",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'SuicideRate'\n",
    "year = years[-1]\n",
    "suicide_gap, suicide_recent = summarize_gap(suicide, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "39572ac3",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(suicide_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "325eca37",
   "metadata": {},
   "source": [
    "## Alcohol\n",
    "\n",
    "**Alcohol-attributable all-cause deaths per 100,000 (age-standardized)** - Deaths from all causes that are attributable to alcohol consumption, including direct alcohol-related deaths and alcohol-attributable deaths from other causes (e.g., accidents, liver disease).\n",
    "\n",
    "**Indicator Code**: SA_0000001832  \n",
    "**Relevance**: Men typically have higher rates of alcohol consumption and alcohol-related diseases. Alcohol contributes to liver disease, accidents, and various health conditions, directly impacting mortality. Age-standardized rates match HALE methodology for cross-country comparison."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "eff11734",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_alcohol_death_rates.csv'\n",
    "alcohol, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f0f58d0b",
   "metadata": {},
   "outputs": [],
   "source": [
    "alcohol.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c32dc1c1",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'AlcoholDeathRate'\n",
    "year = years[-1]\n",
    "alcohol_gap, alcohol_recent = summarize_gap(alcohol, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c5313093",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(alcohol_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7ff68ae8",
   "metadata": {},
   "source": [
    "## Poison\n",
    "\n",
    "**Mortality rate attributed to unintentional poisoning (per 100,000 population)** - Deaths from accidental poisonings from chemicals, drugs, and other substances.\n",
    "\n",
    "**Indicator Code**: SDGPOISON  \n",
    "**Relevance**: Men often have higher rates of accidental deaths, including poisonings. This reflects occupational hazards and risk-taking behaviors that contribute to the gender gap in mortality. Has excellent temporal coverage (2000-2021) and country coverage (196 countries)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9df3a5d2",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_poisoning_rates.csv'\n",
    "poison, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3f80dabf",
   "metadata": {},
   "outputs": [],
   "source": [
    "poison.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3aab7a83",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'PoisoningRate'\n",
    "year = years[-1]\n",
    "poison_gap, poison_recent = summarize_gap(poison, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "36e3ebba",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(poison_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "02e56bd4",
   "metadata": {},
   "source": [
    "## Traffic\n",
    "\n",
    "**Road traffic crash deaths, age-standardized death rates (15+), per 100,000 population** - Deaths from road traffic accidents, age-standardized for ages 15+.\n",
    "\n",
    "**Indicator Code**: SA_0000001459  \n",
    "**Relevance**: Road traffic deaths are typically 2-4 times higher in men across most countries, making it a major contributor to the gender gap in mortality. Reflects higher exposure to driving (including occupational exposure), occupational hazards, and potentially risk-taking behaviors. Age-standardized rates for ages 15+ match HALE methodology."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a060dc45",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_road_traffic_death_rates.csv'\n",
    "traffic, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e49e7051",
   "metadata": {},
   "outputs": [],
   "source": [
    "traffic.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f784e19b",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'RoadTrafficDeathRate'\n",
    "year = years[-1]\n",
    "traffic_gap, traffic_recent = summarize_gap(traffic, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "363c8cbe",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(traffic_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "28ef8594",
   "metadata": {},
   "source": [
    "## Maternal mortality\n",
    "\n",
    "**Maternal mortality ratio (per 100,000 live births)** - Deaths of women during pregnancy, childbirth, or within 42 days of termination of pregnancy, per 100,000 live births.\n",
    "\n",
    "**Indicator Code**: MDG_0000000026  \n",
    "**Relevance**: Critical for understanding cases where the HALE gender gap is small due to high female mortality, especially in lower-income countries. High maternal mortality can significantly reduce the HALE gender gap by lowering female life expectancy. Inherently female-specific, so only female values are used in analysis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7f14bd45",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_maternal_mortality_ratio.csv'\n",
    "maternal, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "59073fd2",
   "metadata": {},
   "outputs": [],
   "source": [
    "maternal.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "25c29f96",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'MaternalMortalityRatio'\n",
    "year = years[-1]\n",
    "maternal_gap, maternal_recent = summarize_gap(maternal, col, sexes=['Female'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2cc283ce",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(maternal_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e6255574",
   "metadata": {},
   "source": [
    "## Homicide\n",
    "\n",
    "**Estimates of rates of homicides per 100,000 population** - Deaths from intentional homicide, including estimates with confidence intervals.\n",
    "\n",
    "**Indicator Code**: VIOLENCE_HOMICIDERATE  \n",
    "**Relevance**: Homicide rates are typically much higher in men across most countries, making it a major contributor to the gender gap in mortality. Homicide reflects violence, conflict, and social factors that differentially affect men and women. Has excellent temporal coverage (2000-2021) and country coverage (196 countries)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "84cc215d",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_homicide_rates.csv'\n",
    "homicide, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d0c14f13",
   "metadata": {},
   "outputs": [],
   "source": [
    "homicide.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "af246adb",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'HomicideRate'\n",
    "year = years[-1]\n",
    "homicide_gap, homicide_recent = summarize_gap(homicide, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "04335245",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(homicide_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "527a4a84",
   "metadata": {},
   "source": [
    "## Intimate Partner Violence\n",
    "\n",
    "**Proportion of ever-partnered women and girls aged 15-49 years subjected to physical and/or sexual violence by a current or former intimate partner in the previous 12 months (%)** - Prevalence indicator measuring the percentage of women experiencing intimate partner violence.\n",
    "\n",
    "**Indicator Code**: SDGIPV  \n",
    "**Relevance**: Note: This is a **prevalence indicator** (percentage), not a direct death rate. IPV affects women's health indirectly through mental health impacts, injuries, and other health consequences. It may contribute to the gender gap in HALE through its effects on women's physical and mental health, though the relationship is complex and indirect. Inherently female-specific, so only female values are used in analysis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1eb26dee",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_ipv_prevalence.csv'\n",
    "ipv, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c5493b09",
   "metadata": {},
   "outputs": [],
   "source": [
    "ipv.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "58282a44",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'IPVPrevalence'\n",
    "year = years[-1]\n",
    "ipv_gap, ipv_recent = summarize_gap(ipv, col, sexes=['Female'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fb0fce28",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(ipv_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1eeb3d0c",
   "metadata": {},
   "source": [
    "## Under five mortality rate\n",
    "\n",
    "**Under-five mortality rate (probability of dying by age 5 per 1000 live births)** - Deaths of children under age 5 per 1,000 live births, with gender breakdowns.\n",
    "\n",
    "**Indicator Code**: MDG_0000000007  \n",
    "**Relevance**: HALE is calculated from birth, so under-five mortality directly affects HALE calculations. If child mortality differs by gender, it directly contributes to the HALE gender gap. Infant mortality is typically higher in males (biological vulnerability + some behavioral factors). More important in lower-income countries with high child mortality. Note: MDG_0000000007 chosen over u5mr for better data quality when filtered for sex dimension."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7e2cd77c",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_u5mr.csv'\n",
    "u5mr, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ef73b9eb",
   "metadata": {},
   "outputs": [],
   "source": [
    "u5mr.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d6cd4853",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'U5MR'\n",
    "year = years[-1]\n",
    "u5mr_gap, u5mr_recent = summarize_gap(u5mr, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ad6fdcf1",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(u5mr_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "b6115b72",
   "metadata": {},
   "source": [
    "## Cardiovascular Disease\n",
    "\n",
    "**Age-standardized cardiovascular disease death rates (per 100,000)** - Deaths from cardiovascular diseases (heart disease, stroke, etc.), age-standardized for cross-country comparison.\n",
    "\n",
    "**Indicator Code**: Multiple codes tried (WHS2_161, etc.) - see `who_data.py` for implementation details  \n",
    "**Relevance**: Men typically have higher rates of cardiovascular disease and heart attacks, contributing significantly to the gender gap in mortality. Risk factors include smoking, diet, and potentially biological differences. May capture effects of smoking and other risk factors. Age-standardized rates match HALE methodology."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e7dd4208",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_cardiovascular_death_rates.csv'\n",
    "cardio, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ea5cbbc9",
   "metadata": {},
   "outputs": [],
   "source": [
    "cardio.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8619a7ee",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'DeathRate'\n",
    "year = years[-1]\n",
    "cardio_gap, cardio_recent = summarize_gap(cardio, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a25049fc",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(cardio_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "09ee2f6c",
   "metadata": {},
   "source": [
    "## Diabetes\n",
    "\n",
    "**Age-standardized death rates, diabetes mellitus (per 100,000)** - Deaths from diabetes, age-standardized for cross-country comparison.\n",
    "\n",
    "**Indicator Code**: SA_0000001440  \n",
    "**Relevance**: Diabetes is a chronic condition that can contribute to the gender gap in mortality, though the relationship may vary by country and healthcare access. Age-standardized rates match HALE methodology. **Limitation**: Only has data for 2004 (similar to cardiovascular disease indicators), which limits temporal analysis but provides a good cross-sectional snapshot."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ca82971b",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_diabetes_death_rates.csv'\n",
    "diabetes, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a7e3bbac",
   "metadata": {},
   "outputs": [],
   "source": [
    "diabetes.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0935a0a6",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'DiabetesDeathRate'\n",
    "year = years[-1]\n",
    "diabetes_gap, diabetes_recent = summarize_gap(diabetes, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5795d8cc",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(diabetes_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9836bf77",
   "metadata": {},
   "source": [
    "## NCD Mortality (30-70 years)\n",
    "\n",
    "**Probability (%) of dying between age 30 and exact age 70 from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease** - Combined non-communicable disease mortality indicator.\n",
    "\n",
    "**Indicator Code**: NCDMORT3070  \n",
    "**Relevance**: Combines multiple causes of death (cardiovascular disease, cancer, diabetes, chronic respiratory disease), so it's less specific than individual cause indicators. However, it has much better temporal coverage (2000-2021) than diabetes-specific indicators (which only have 2004 data). This makes it useful for model comparison - trading off specificity for temporal coverage. The combined indicator may capture overall NCD mortality patterns that contribute to the HALE gender gap."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2a73ad1e",
   "metadata": {},
   "outputs": [],
   "source": [
    "filename = '../data/who_ncd_mortality_30_70.csv'\n",
    "ncdmort, years = load_and_inventory(filename)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "90542499",
   "metadata": {},
   "outputs": [],
   "source": [
    "ncdmort.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "856f23e5",
   "metadata": {},
   "outputs": [],
   "source": [
    "col = 'NCDMortality30_70'\n",
    "year = years[-1]\n",
    "ncdmort_gap, ncdmort_recent = summarize_gap(ncdmort, col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "68c3bd2b",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_distributions(ncdmort_recent)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "873adbda",
   "metadata": {},
   "source": [
    "## Phase 1: Data Preparation for Regression Analysis\n",
    "\n",
    "### Step 1.2: Prepare Target Variable (HALE Gender Gap)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "69fabe3f",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculate HALE gender gap from existing hale_recent DataFrame\n",
    "hale_recent['HALE_gap'] = hale_recent['HALE_Years_Female'] - hale_recent['HALE_Years_Male']\n",
    "\n",
    "# Filter to OECD countries\n",
    "hale_oecd = get_oecd(hale_recent)\n",
    "\n",
    "# Display summary\n",
    "hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].describe()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f57c7118",
   "metadata": {},
   "source": [
    "### Step 1.4: Merge All Predictors into Single Dataset"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e5ab65ed",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Start with HALE data as base\n",
    "analysis_df = hale_oecd[['HALE_Years_Male', 'HALE_Years_Female', 'HALE_gap']].copy()\n",
    "\n",
    "# Merge all predictor DataFrames (already filtered to OECD in earlier sections)\n",
    "# Note: Exclude gap columns (_Gap) as they are perfectly collinear with male/female columns\n",
    "predictor_dfs = {\n",
    "    'SmokingPrevalence': get_oecd(smoking_recent),\n",
    "    'CardioDeathRate': get_oecd(cardio_recent),  # Cardiovascular\n",
    "    'SuicideRate': get_oecd(suicide_recent),\n",
    "    'AlcoholDeathRate': get_oecd(alcohol_recent),\n",
    "    'PoisoningRate': get_oecd(poison_recent),\n",
    "    'RoadTrafficDeathRate': get_oecd(traffic_recent),\n",
    "    'HomicideRate': get_oecd(homicide_recent),\n",
    "    'MaternalMortalityRatio': get_oecd(maternal_recent),\n",
    "    'U5MR': get_oecd(u5mr_recent),\n",
    "    'DiabetesDeathRate': get_oecd(diabetes_recent),\n",
    "    'NCDMortality30_70': get_oecd(ncdmort_recent),\n",
    "    'IPVPrevalence': get_oecd(ipv_recent),  # Intimate Partner Violence (female-only)\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5e8a3176",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Remove gap columns from each predictor DataFrame (they're collinear with male/female columns)\n",
    "for name, df in predictor_dfs.items():\n",
    "    gap_cols = [col for col in df.columns if col.endswith('_Gap')]\n",
    "    if gap_cols:\n",
    "        predictor_dfs[name] = df.drop(columns=gap_cols)\n",
    "\n",
    "# Check shapes after removing gaps\n",
    "for name, predictor_df in predictor_dfs.items():\n",
    "    print(name, predictor_df.shape)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9ab7a288",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Merge all predictors on index (Country codes)\n",
    "for name, df in predictor_dfs.items():\n",
    "    analysis_df = analysis_df.join(df, how='outer')\n",
    "\n",
    "# Display shape and column names\n",
    "analysis_df.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dc0787a2",
   "metadata": {},
   "outputs": [],
   "source": [
    "analysis_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7e43f97c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create missing data report\n",
    "missing_report = pd.DataFrame({\n",
    "    'Indicator': analysis_df.columns,\n",
    "    'Missing_Count': [analysis_df[col].isna().sum() for col in analysis_df.columns],\n",
    "    'Missing_Pct': [analysis_df[col].isna().sum() / len(analysis_df) * 100 for col in analysis_df.columns],\n",
    "    'Available_Count': [analysis_df[col].notna().sum() for col in analysis_df.columns]\n",
    "}).sort_values('Missing_Count', ascending=False)\n",
    "\n",
    "missing_report"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "106248bc",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Show which countries have complete data for all indicators\n",
    "complete_cases = analysis_df.dropna()\n",
    "complete_cases.shape[0], f\"{complete_cases.shape[0] / len(analysis_df) * 100:.1f}% of countries have complete data\""
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0c9cb96a",
   "metadata": {},
   "source": [
    "### Step 1.5: Create Final Analysis Dataset"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cac13012",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Use complete-case analysis for primary model\n",
    "analysis_complete = analysis_df.dropna()\n",
    "\n",
    "# Document excluded countries\n",
    "excluded_countries = set(analysis_df.index) - set(analysis_complete.index)\n",
    "excluded_countries if excluded_countries else \"No countries excluded - all OECD countries have complete data\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "93f64b38",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Separate target and predictors\n",
    "target = analysis_complete['HALE_gap']\n",
    "predictors = analysis_complete.drop(columns=['HALE_gap', 'HALE_Years_Male', 'HALE_Years_Female'])\n",
    "\n",
    "# Display final dataset info\n",
    "pd.DataFrame({\n",
    "    'Dataset': ['Complete Cases'],\n",
    "    'Countries': [len(analysis_complete)],\n",
    "    'Target_Variable': ['HALE_gap'],\n",
    "    'Number_of_Predictors': [len(predictors.columns)],\n",
    "    'Predictor_Names': [', '.join(predictors.columns)]\n",
    "})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f05637ea",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Summary of Phase 1 completion\n",
    "pd.DataFrame({\n",
    "    'Step': ['1.2: Target Variable', '1.4: Merge', '1.5: Complete Cases'],\n",
    "    'Status': ['Complete', 'Complete', 'Complete'],\n",
    "    'Countries': [len(hale_oecd), len(analysis_df), len(analysis_complete)],\n",
    "    'Variables': [3, len(analysis_df.columns), len(analysis_complete.columns)]\n",
    "})"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1bf0f388",
   "metadata": {},
   "source": [
    "**Note**: Predictor standardization will be done as part of the regression pipeline (e.g., using `StandardScaler` in scikit-learn's pipeline), not as a separate preprocessing step.\n",
    "\n",
    "## Phase 2: Exploratory Data Analysis\n",
    "\n",
    "### Step 2.1: Descriptive Statistics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a2d03999",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Summary statistics for target variable (HALE gap)\n",
    "target.describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a01be734",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Summary statistics for all predictors\n",
    "predictors.describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4641d8c9",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Distribution of HALE gap across OECD countries\n",
    "plt.hist(target, bins=15, color=AIBM_COLORS['crimson'], edgecolor='white')\n",
    "decorate(xlabel='HALE Gap (Female - Male, years)', \n",
    "         ylabel='Number of Countries',\n",
    "         title='Distribution of HALE Gender Gap Across OECD Countries')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7e5e2a49",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Identify potential outliers using IQR method\n",
    "Q1 = target.quantile(0.25)\n",
    "Q3 = target.quantile(0.75)\n",
    "IQR = Q3 - Q1\n",
    "lower_bound = Q1 - 1.5 * IQR\n",
    "upper_bound = Q3 + 1.5 * IQR\n",
    "\n",
    "outliers = target[(target < lower_bound) | (target > upper_bound)]\n",
    "outliers_df = pd.DataFrame({\n",
    "    'Country': outliers.index,\n",
    "    'HALE_Gap': outliers.values\n",
    "}).sort_values('HALE_Gap')\n",
    "\n",
    "outliers_df if not outliers_df.empty else \"No outliers detected using IQR method\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "49b8ea69",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Box plot of HALE gap\n",
    "plt.boxplot(target, vert=True)\n",
    "decorate(ylabel='HALE Gap (Female - Male, years)',\n",
    "         title='HALE Gender Gap Distribution (OECD Countries)')\n",
    "plt.xticks([1], ['HALE Gap'])"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "263ca6f6",
   "metadata": {},
   "source": [
    "### Step 2.2: Correlation Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "152bfed4",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculate correlation matrix of all predictors\n",
    "correlation_matrix = predictors.corr()\n",
    "\n",
    "# Display correlation matrix\n",
    "correlation_matrix"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "890aa0cb",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Visualize correlation matrix as heatmap\n",
    "import seaborn as sns\n",
    "\n",
    "plt.figure(figsize=(12, 10))\n",
    "mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # Mask upper triangle\n",
    "sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', \n",
    "            center=0, square=True, linewidths=0.5, cbar_kws={\"shrink\": 0.8})\n",
    "decorate(title='Correlation Matrix of Predictors (Lower Triangle)')\n",
    "plt.tight_layout()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dcad7ae7",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Identify highly correlated predictor pairs (|correlation| > 0.7)\n",
    "high_corr_pairs = []\n",
    "for i in range(len(correlation_matrix.columns)):\n",
    "    for j in range(i+1, len(correlation_matrix.columns)):\n",
    "        corr_val = correlation_matrix.iloc[i, j]\n",
    "        if abs(corr_val) > 0.7:\n",
    "            high_corr_pairs.append({\n",
    "                'Predictor_1': correlation_matrix.columns[i],\n",
    "                'Predictor_2': correlation_matrix.columns[j],\n",
    "                'Correlation': corr_val\n",
    "            })\n",
    "\n",
    "high_corr_df = pd.DataFrame(high_corr_pairs).sort_values('Correlation', key=abs, ascending=False)\n",
    "high_corr_df if not high_corr_df.empty else \"No highly correlated pairs (|r| > 0.7) found\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b60d01e4",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Summary of correlation analysis\n",
    "pd.DataFrame({\n",
    "    'Analysis': ['Total Predictors', 'High Correlations (|r| > 0.7)', 'Max Correlation', 'Min Correlation'],\n",
    "    'Value': [\n",
    "        len(predictors.columns),\n",
    "        len(high_corr_pairs) if high_corr_pairs else 0,\n",
    "        correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max(),\n",
    "        correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].min()\n",
    "    ]\n",
    "})"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "3009db98",
   "metadata": {},
   "source": [
    "## Phase 3: Model Fitting\n",
    "\n",
    "### Step 3.1: Model Selection Setup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "616d7765",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.preprocessing import StandardScaler\n",
    "from sklearn.pipeline import Pipeline\n",
    "from sklearn.linear_model import Ridge, Lasso, ElasticNet\n",
    "from sklearn.model_selection import GridSearchCV, cross_val_score, KFold\n",
    "from sklearn.metrics import r2_score, mean_squared_error\n",
    "\n",
    "# Prepare data: X (predictors) and y (target)\n",
    "X = predictors.copy()\n",
    "y = target.copy()\n",
    "\n",
    "# Display data shape\n",
    "pd.DataFrame({\n",
    "    'Data': ['Predictors (X)', 'Target (y)'],\n",
    "    'Shape': [X.shape, y.shape],\n",
    "    'Countries': [X.shape[0], y.shape[0]]\n",
    "})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c14aa4f6",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Set up cross-validation (5-fold for small sample size)\n",
    "cv = KFold(n_splits=5, shuffle=True, random_state=42)\n",
    "\n",
    "# Display CV setup\n",
    "f\"Using {cv.n_splits}-fold cross-validation for model selection\""
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8a31bf97",
   "metadata": {},
   "source": [
    "### Step 3.2: Fit Multiple Models"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "39d7bb60",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define parameter grids for each model\n",
    "ridge_params = {'ridge__alpha': np.logspace(-2, 4, 50)}  # Regularization strength\n",
    "lasso_params = {'lasso__alpha': np.logspace(-3, 1, 50)}\n",
    "elastic_net_params = {\n",
    "    'elasticnet__alpha': np.logspace(-3, 1, 20),\n",
    "    'elasticnet__l1_ratio': np.linspace(0.1, 0.9, 9)  # 0=Ridge, 1=Lasso\n",
    "}\n",
    "\n",
    "# Create pipelines with StandardScaler and models\n",
    "ridge_pipeline = Pipeline([\n",
    "    ('scaler', StandardScaler()),\n",
    "    ('ridge', Ridge())\n",
    "])\n",
    "\n",
    "lasso_pipeline = Pipeline([\n",
    "    ('scaler', StandardScaler()),\n",
    "    ('lasso', Lasso(max_iter=10000))\n",
    "])\n",
    "\n",
    "elastic_net_pipeline = Pipeline([\n",
    "    ('scaler', StandardScaler()),\n",
    "    ('elasticnet', ElasticNet(max_iter=10000))\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b7e8f43f",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fit Ridge Regression with cross-validation\n",
    "print(\"Fitting Ridge Regression...\")\n",
    "ridge_grid = GridSearchCV(ridge_pipeline, ridge_params, cv=cv, \n",
    "                          scoring='r2', n_jobs=-1, verbose=1)\n",
    "ridge_grid.fit(X, y)\n",
    "\n",
    "ridge_best_score = ridge_grid.best_score_\n",
    "ridge_best_params = ridge_grid.best_params_\n",
    "ridge_best_model = ridge_grid.best_estimator_\n",
    "\n",
    "pd.DataFrame({\n",
    "    'Model': ['Ridge'],\n",
    "    'Best_CV_R2': [ridge_best_score],\n",
    "    'Best_Alpha': [ridge_best_params['ridge__alpha']]\n",
    "})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6dec797a",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fit Lasso Regression with cross-validation\n",
    "print(\"Fitting Lasso Regression...\")\n",
    "lasso_grid = GridSearchCV(lasso_pipeline, lasso_params, cv=cv,\n",
    "                          scoring='r2', n_jobs=-1, verbose=1)\n",
    "lasso_grid.fit(X, y)\n",
    "\n",
    "lasso_best_score = lasso_grid.best_score_\n",
    "lasso_best_params = lasso_grid.best_params_\n",
    "lasso_best_model = lasso_grid.best_estimator_\n",
    "\n",
    "pd.DataFrame({\n",
    "    'Model': ['Lasso'],\n",
    "    'Best_CV_R2': [lasso_best_score],\n",
    "    'Best_Alpha': [lasso_best_params['lasso__alpha']]\n",
    "})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bec83bcd",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fit Elastic Net with cross-validation\n",
    "print(\"Fitting Elastic Net...\")\n",
    "elastic_net_grid = GridSearchCV(elastic_net_pipeline, elastic_net_params, cv=cv,\n",
    "                                 scoring='r2', n_jobs=-1, verbose=1)\n",
    "elastic_net_grid.fit(X, y)\n",
    "\n",
    "elastic_net_best_score = elastic_net_grid.best_score_\n",
    "elastic_net_best_params = elastic_net_grid.best_params_\n",
    "elastic_net_best_model = elastic_net_grid.best_estimator_\n",
    "\n",
    "pd.DataFrame({\n",
    "    'Model': ['Elastic Net'],\n",
    "    'Best_CV_R2': [elastic_net_best_score],\n",
    "    'Best_Alpha': [elastic_net_best_params['elasticnet__alpha']],\n",
    "    'Best_L1_Ratio': [elastic_net_best_params['elasticnet__l1_ratio']]\n",
    "})"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "cb107262",
   "metadata": {},
   "source": [
    "### Step 3.3: Model Comparison"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f1663a96",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculate RMSE from cross-validation for each model\n",
    "ridge_rmse_scores = np.sqrt(-cross_val_score(ridge_best_model, X, y, cv=cv, scoring='neg_mean_squared_error'))\n",
    "lasso_rmse_scores = np.sqrt(-cross_val_score(lasso_best_model, X, y, cv=cv, scoring='neg_mean_squared_error'))\n",
    "elastic_net_rmse_scores = np.sqrt(-cross_val_score(elastic_net_best_model, X, y, cv=cv, scoring='neg_mean_squared_error'))\n",
    "\n",
    "# Compare cross-validation scores\n",
    "model_comparison = pd.DataFrame({\n",
    "    'Model': ['Ridge', 'Lasso', 'Elastic Net'],\n",
    "    'CV_R2_Score': [ridge_best_score, lasso_best_score, elastic_net_best_score],\n",
    "    'CV_RMSE_Mean': [\n",
    "        ridge_rmse_scores.mean(),\n",
    "        lasso_rmse_scores.mean(),\n",
    "        elastic_net_rmse_scores.mean()\n",
    "    ],\n",
    "    'CV_RMSE_Std': [\n",
    "        ridge_rmse_scores.std(),\n",
    "        lasso_rmse_scores.std(),\n",
    "        elastic_net_rmse_scores.std()\n",
    "    ]\n",
    "})\n",
    "\n",
    "model_comparison.sort_values('CV_R2_Score', ascending=False)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e24346c5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Extract coefficients from each model (on standardized scale)\n",
    "ridge_coefs = pd.DataFrame({\n",
    "    'Predictor': X.columns,\n",
    "    'Ridge_Coefficient': ridge_best_model.named_steps['ridge'].coef_\n",
    "}).sort_values('Ridge_Coefficient', key=abs, ascending=False)\n",
    "\n",
    "lasso_coefs = pd.DataFrame({\n",
    "    'Predictor': X.columns,\n",
    "    'Lasso_Coefficient': lasso_best_model.named_steps['lasso'].coef_\n",
    "}).sort_values('Lasso_Coefficient', key=abs, ascending=False)\n",
    "\n",
    "elastic_net_coefs = pd.DataFrame({\n",
    "    'Predictor': X.columns,\n",
    "    'ElasticNet_Coefficient': elastic_net_best_model.named_steps['elasticnet'].coef_\n",
    "}).sort_values('ElasticNet_Coefficient', key=abs, ascending=False)\n",
    "\n",
    "# Merge coefficient comparisons\n",
    "coef_comparison = ridge_coefs.merge(lasso_coefs, on='Predictor').merge(elastic_net_coefs, on='Predictor')\n",
    "coef_comparison.head(10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "785bc08d",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Count non-zero coefficients (feature selection in Lasso/Elastic Net)\n",
    "feature_selection_summary = pd.DataFrame({\n",
    "    'Model': ['Ridge', 'Lasso', 'Elastic Net'],\n",
    "    'Total_Predictors': [len(X.columns), len(X.columns), len(X.columns)],\n",
    "    'Non_Zero_Coefficients': [\n",
    "        np.sum(ridge_best_model.named_steps['ridge'].coef_ != 0),\n",
    "        np.sum(lasso_best_model.named_steps['lasso'].coef_ != 0),\n",
    "        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ != 0)\n",
    "    ],\n",
    "    'Zero_Coefficients': [\n",
    "        np.sum(ridge_best_model.named_steps['ridge'].coef_ == 0),\n",
    "        np.sum(lasso_best_model.named_steps['lasso'].coef_ == 0),\n",
    "        np.sum(elastic_net_best_model.named_steps['elasticnet'].coef_ == 0)\n",
    "    ]\n",
    "})\n",
    "\n",
    "feature_selection_summary"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1e7d39d5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Select primary model (Ridge for counterfactual analysis, or best performing)\n",
    "# Ridge is preferred for counterfactuals since it keeps all predictors\n",
    "primary_model = ridge_best_model\n",
    "primary_model_name = 'Ridge'\n",
    "\n",
    "# Alternative: Use best performing model\n",
    "# if elastic_net_best_score > ridge_best_score and elastic_net_best_score > lasso_best_score:\n",
    "#     primary_model = elastic_net_best_model\n",
    "#     primary_model_name = 'Elastic Net'\n",
    "# elif lasso_best_score > ridge_best_score:\n",
    "#     primary_model = lasso_best_model\n",
    "#     primary_model_name = 'Lasso'\n",
    "\n",
    "pd.DataFrame({\n",
    "    'Primary_Model': [primary_model_name],\n",
    "    'CV_R2_Score': [ridge_best_score if primary_model_name == 'Ridge' \n",
    "                    else lasso_best_score if primary_model_name == 'Lasso' \n",
    "                    else elastic_net_best_score],\n",
    "    'Reason': ['Keeps all predictors for counterfactual analysis' if primary_model_name == 'Ridge'\n",
    "               else 'Best cross-validation performance']\n",
    "})"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
