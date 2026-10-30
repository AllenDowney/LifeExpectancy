---
description: "Technical reports behind an analysis of the gender gap in life expectancy in OECD countries: a Bayesian panel model, counterfactuals, data, and code."
title: "The Gender Gap in Life Expectancy: Technical Reports"
thumbnail: figs/le_gap_timeseries_selected.png
---

## About This Project

In most countries, women live longer than men. This difference is often assumed to be natural and inevitable. However, the gap varies substantially between countries and has changed over time, which suggests that it might not be entirely natural, or if it is, it can be mitigated.

This project explores differences in life expectancy and health-adjusted life expectancy (HALE) between countries, in order to identify the factors that contribute to the observed gender gaps and to understand what it would take to close those gaps by improving health outcomes for both men and women.

This site has the technical details behind the published work. The code and data are on [GitHub](https://github.com/AllenDowney/LifeExpectancy).

## Published work

- **Policy paper:** [Is it inevitable that men die younger than women? Looking at evidence and policy solutions](https://aibm.org/research/is-it-inevitable-that-men-die-younger-than-women-looking-at-evidence-and-policy-solutions/), American Institute for Boys and Men, July 2026.
- **Blog series** on [Probably Overthinking It](https://allendowney.substack.com/), February to May 2026, also on this site:
  1. [The Gender Gap in Life Expectancy](blog1_time_series.md)
  2. [What Drives the Life Expectancy Gender Gap?](blog2_model.md)
  3. [How Much of the Life Expectancy Gap Could We Close?](blog3_counterfactual.md)
  4. [International Patterns in the Life Expectancy Gap](blog4_international.md)
  5. [Healthy Life Expectancy and the Gender Gap](blog5_hale.md)

## Contents

- [Executive Summary](summary.md): **start here** for the motivation, methods, key findings, and policy implications.
- [Policy paper](https://aibm.org/research/is-it-inevitable-that-men-die-younger-than-women-looking-at-evidence-and-policy-solutions/) (AIBM): the evidence and policy recommendations, as published.

**Methods and results**

- [Bayesian Panel Data Model](bayesian_model_report_2023.md): the **primary analysis**, a Bayesian hierarchical panel model of the LE and HALE gender gaps in OECD countries, 2000–2023, using IHME HALE and OWID life expectancy data.
- [Validation Experiments](validation.md): checks that the conclusions hold when WHO indicators are replaced with IHME indicators.
- [Data Inventory](data_inventory.md): data sources, indicators, and download settings.
- [Python to R](python_to_r.md): an early version of the model written in both PyMC and R (brms), with a comparison showing the two agree.

**Archive: working notes**

These reports document earlier stages of the analysis. They are kept for reference; the results above supersede them.

- [Bayesian Panel Data Model, 2000–2021](bayesian_model_report_2021.md): the previous version, using WHO HALE data.
- [Exploratory Data Analysis](eda_report.md): the outcomes and predictors, summary statistics, and relationships between variables.
- [Time Series Analysis](time_series_report.md): trends in the gaps and in cause-specific death rates.
- [Temporal Analysis](temporal.md): cross-sectional models at five-year intervals, to see how the important factors changed.
- [Elastic Net Models](tech_report.md): the cross-sectional regression models that preceded the Bayesian model.
- [Causal Assumptions (working note)](causal_results.md): minimal causal diagrams (DAGs) for the model, fixed-effects regressions that implement them, and a comparison with the Bayesian estimates.
- [Cancer Drilldown](neoplasms_report.md): the gender gap in cancer mortality by cancer type and risk factor.

## Methodology

Our primary analysis uses a **Bayesian hierarchical panel model** to analyze the gender gap in life expectancy and HALE. This approach leverages both temporal variation (2000-2023 for both outcomes) and cross-country variation simultaneously, providing several advantages:

- **Uncertainty quantification**: All parameter estimates include posterior distributions with credible intervals
- **Country-specific effects**: Accounts for unobserved country-level heterogeneity through random intercepts
- **Robust inference**: Handles correlation among predictors while quantifying uncertainty in all estimates

The analysis focuses on OECD countries (37 countries excluding Turkey) using IHME HALE data (2000-2023) and OWID Life Expectancy data (2000-2023). This extended temporal range includes the full COVID-19 pandemic period (2020-2023) to understand its impact on gender gaps in health outcomes, including the post-acute recovery phase.

During the development process, we also explored Elastic Net regression models (see the [Technical Report](tech_report.md)) to identify key predictors and validate our approach. These cross-sectional models helped inform the Bayesian panel model specification and provided initial insights into which cause-specific mortality indicators are most strongly associated with the gender gap.

We validate our results by comparing models using WHO indicators with models using IHME indicators, ensuring that conclusions remain stable across data sources. See the [Validation Experiments](validation.md) for details.

## Data Sources

- **IHME Global Burden of Disease 2023**: HALE and cause-specific death rates by sex, 2000–2023
- **Our World in Data**: life expectancy by sex, 2000–2023, combining the Human Mortality Database and UN World Population Prospects
- **WHO Global Health Observatory**: an earlier source for HALE, life expectancy, and death rates (2000–2021), used in the [Validation Experiments](validation.md)

## Key Findings

The analysis identifies several key factors that contribute to the gender gap in life expectancy and HALE:

**Primary Drivers (External Causes):**
- **Road traffic accidents**: The single strongest predictor—countries where men die in traffic accidents at much higher rates have substantially larger longevity gaps
- **Suicide**: The second or third strongest factor across both HALE and Life Expectancy
- **Homicide**: A substantial contributor, especially for total lifespan
- **Drug disorders**: Major factor, particularly important in countries experiencing opioid epidemics

**Chronic Disease Contributors:**
- **Chronic respiratory disease**: Significant contributor, possibly reflecting smoking-related differences
- **Cancer (neoplasms)**: Moderate contributor to both HALE and Life Expectancy gaps
- **Cardiovascular disease & diabetes**: Show "competing risk" effects—act as protective factors because they primarily affect people who survive to older ages

**United States Example:**
If the USA could achieve best-in-class levels for key factors, the Life Expectancy gap could be reduced by approximately **2.5 years** through improvements in:
- Road traffic safety (-0.83 years)
- Drug overdose prevention (-0.77 years)
- Suicide prevention (-0.52 years)
- Violence reduction (-0.29 years)

For detailed findings, counterfactual analysis, and uncertainty quantification, see the [Executive Summary](summary.md) or the full [Bayesian Panel Data Model (2023)](bayesian_model_report_2023.md) report. For comparison with the previous WHO HALE-based analysis, see the [2021 Legacy Report](bayesian_model_report_2021.md). For exploratory analysis using Elastic Net regression, see the [Technical Report](tech_report.md).

## License

The text of this site is under [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/); the [code](https://github.com/AllenDowney/LifeExpectancy) is under the MIT License.
