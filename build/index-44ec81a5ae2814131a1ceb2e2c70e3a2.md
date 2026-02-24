# Gender Gaps in Life Expectancy

## About This Project

In most countries, women live longer than men. This difference is often assumed to be natural and inevitable. However, the gap varies substantially between countries and has changed over time, which suggests that it might not be entirely natural, or if it is, it can be mitigated.

This project explores differences in life expectancy and health-adjusted life expectancy (HALE) between countries, in order to identify the factors that contribute to the observed gender gaps and to understand what it would take to close those gaps by improving health outcomes for both men and women.

## Contents

- [Technical Report](tech_report.md) - Analysis of the gender gap in life expectancy and HALE, including methodology, results, and counterfactual analysis.

- [Data Inventory](data_inventory.md) - Data sources and metadata.

- [Neoplasms Drilldown Analysis](neoplasms_report.md) - Granular analysis of the cancer mortality gender gap, including specific cancer types and risk factor attribution (Behavioral, Metabolic, Environmental).

- [Exploratory Data Analysis](eda_report.md) - Summary of exploratory data analysis of gender gaps in HALE and Life Expectancy, including target variables, predictors, summary statistics, and relationships between variables.

- [Validation Experiments](validation.md) - Model validation comparing WHO and IHME indicators to ensure results remain stable across data sources.

- [Time Series Analysis](time_series_report.md) - Trends in health indicators and gender gaps (2000-2019), visualizing how HALE, Life Expectancy, and cause-specific mortality indicators have evolved over time.

- [Temporal Analysis](temporal.md) - Evolution of health patterns and gender gaps over time (2000-2019). Runs predictive models at five-year intervals (2000, 2005, 2010, 2015, 2019) and compares results to examine how indicator importance and intervention opportunities have changed.

- [Bayesian Panel Data Model](bayesian_model_report.md) - Bayesian hierarchical panel model analyzing HALE and Life Expectancy gender gaps using both temporal variation (2000-2019) and cross-country variation simultaneously. Provides posterior distributions for all parameters and enables temporal counterfactual analysis.

## Methodology

We use Elastic Net regression to model the gender gap in life expectancy and HALE as a function of cause-specific mortality indicators. This approach handles the high correlation among predictors and identifies which patterns of mortality are most strongly associated with the life expectancy gap.

The analysis focuses on OECD countries (38 countries) using the most recent available data from 2000-2019, excluding 2020 and later years to avoid distortions from the COVID-19 pandemic.

We validate our results by comparing models using WHO indicators with models using IHME indicators, ensuring that conclusions remain stable across data sources. See the [Validation Experiments](validation.md) for details.

## Data Sources

- **WHO Global Health Observatory (GHO) API**: Provides HALE, life expectancy, and various cause-specific mortality indicators
- **IHME Global Burden of Disease**: Provides additional cause-specific mortality indicators with better temporal coverage

## Key Findings

The analysis identifies several key factors that contribute to the gender gap in life expectancy and HALE:

**For Life Expectancy:**
- Alcohol-attributable deaths are the most important predictor of the gender gap
- Neoplasms (cancer) death rates are the second most important factor
- Cardiovascular disease, chronic respiratory disease, and other cause-specific mortality patterns also contribute

**For HALE (Healthy Life Expectancy):**
- Neoplasms (cancer) is the most important factor, with both overall rates and gender gaps contributing
- Alcohol-attributable deaths are the second most important factor
- Chronic respiratory disease, unintentional injuries, and other cause-specific mortality patterns also contribute

For detailed findings and counterfactual analysis, see the [Technical Report](tech_report.md).

