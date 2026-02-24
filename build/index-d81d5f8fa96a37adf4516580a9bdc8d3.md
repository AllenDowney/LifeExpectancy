# Gender Gaps in Life Expectancy

## About This Project

In most countries, women live longer than men. This difference is often assumed to be natural and inevitable. However, the gap varies substantially between countries and has changed over time, which suggests that it might not be entirely natural, or if it is, it can be mitigated.

This project explores differences in life expectancy and health-adjusted life expectancy (HALE) between countries, in order to identify the factors that contribute to the observed gender gaps and to understand what it would take to close those gaps by improving health outcomes for both men and women.

## Contents

- [Bayesian Panel Data Model (2023, IHME HALE)](bayesian_model_report_2023.md) - **Primary analysis**: Bayesian hierarchical panel model analyzing HALE and Life Expectancy gender gaps using both temporal variation (2000-2023 for HALE, 2000-2021 for LE) and cross-country variation simultaneously. Uses IHME HALE data for methodological consistency with predictor indicators. Provides posterior distributions for all parameters with uncertainty quantification and enables temporal counterfactual analysis.
- [Bayesian Panel Data Model (2021, WHO HALE)](bayesian_model_report_2021.md) - **Legacy analysis**: Previous version using WHO HALE data (2000-2021). Retained for comparison and historical reference.

- [Technical Report](tech_report.md) - Exploratory analysis using Elastic Net regression, developed as part of the model development process. Includes methodology, results, and counterfactual analysis using cross-sectional models.

- [Data Inventory](data_inventory.md) - Data sources and metadata.

- [Neoplasms Drilldown Analysis](neoplasms_report.md) - Granular analysis of the cancer mortality gender gap, including specific cancer types and risk factor attribution (Behavioral, Metabolic, Environmental).

- [Exploratory Data Analysis](eda_report.md) - Summary of exploratory data analysis of gender gaps in HALE and Life Expectancy, including target variables, predictors, summary statistics, and relationships between variables.

- [Validation Experiments](validation.md) - Model validation comparing WHO and IHME indicators to ensure results remain stable across data sources.

- [Time Series Analysis](time_series_report.md) - Trends in health indicators and gender gaps (2000-2019), visualizing how HALE, Life Expectancy, and cause-specific mortality indicators have evolved over time.

- [Temporal Analysis](temporal.md) - Evolution of health patterns and gender gaps over time (2000-2019). Runs predictive models at five-year intervals (2000, 2005, 2010, 2015, 2019) and compares results to examine how indicator importance and intervention opportunities have changed.

## Methodology

Our primary analysis uses a **Bayesian hierarchical panel model** to analyze the gender gap in life expectancy and HALE. This approach leverages both temporal variation (2000-2023 for HALE using IHME data, 2000-2021 for Life Expectancy using WHO data) and cross-country variation simultaneously, providing several advantages:

- **Uncertainty quantification**: All parameter estimates include posterior distributions with credible intervals
- **Country-specific effects**: Accounts for unobserved country-level heterogeneity through random intercepts
- **Robust inference**: Handles correlation among predictors while quantifying uncertainty in all estimates

The analysis focuses on OECD countries (37 countries excluding Turkey) using IHME HALE data from 2000-2023 and WHO Life Expectancy data from 2000-2021. This extended temporal range includes the full COVID-19 pandemic period (2020-2023) to understand its impact on gender gaps in health outcomes, including the post-acute recovery phase.

During the development process, we also explored Elastic Net regression models (see the [Technical Report](tech_report.md)) to identify key predictors and validate our approach. These cross-sectional models helped inform the Bayesian panel model specification and provided initial insights into which cause-specific mortality indicators are most strongly associated with the gender gap.

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

For detailed findings, counterfactual analysis, and uncertainty quantification, see the [Bayesian Panel Data Model (2023)](bayesian_model_report_2023.md) report. For comparison with the previous WHO HALE-based analysis, see the [2021 Legacy Report](bayesian_model_report_2021.md). For exploratory analysis using Elastic Net regression, see the [Technical Report](tech_report.md).

