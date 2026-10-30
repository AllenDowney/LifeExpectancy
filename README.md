# The Gender Gap in Life Expectancy

In most countries women live longer than men, but the size of the gap varies a lot between countries and has changed over time, which suggests it is not inevitable. This repository has the data processing, models, and figures behind an analysis of the gap across OECD countries: which causes of death account for it, and how much of it could be closed by reducing those deaths.

By [Allen Downey](https://allendowney.com).

## Published work

- **Policy paper:** [Is it inevitable that men die younger than women? Looking at evidence and policy solutions](https://aibm.org/research/is-it-inevitable-that-men-die-younger-than-women-looking-at-evidence-and-policy-solutions/), American Institute for Boys and Men, July 2026.
- **Blog series** on [Probably Overthinking It](https://allendowney.substack.com/):
  1. [The Gender Gap in Life Expectancy](https://allendowney.substack.com/p/the-gender-gap-in-life-expectancy) (February 2026)
  2. [What Drives the Life Expectancy Gender Gap?](https://allendowney.substack.com/p/what-drives-the-life-expectancy-gender) (March 2026)
  3. [How Much of the Life Expectancy Gap Could We Close?](https://allendowney.substack.com/p/how-much-of-the-life-expectancy-gap) (March 2026)
  4. [International Patterns in the Life Expectancy Gap](https://allendowney.substack.com/p/international-patterns-in-the-life) (March 2026)
  5. [Healthy Life Expectancy and the Gender Gap](https://allendowney.substack.com/p/healthy-life-expectancy-and-the-gender) (May 2026)

The technical reports are on the project site, **<https://allendowney.github.io/LifeExpectancy/>**: the model, validation experiments, the causal assumptions, and the data inventory.

## The analysis in brief

The outcome is the gap between female and male life expectancy (LE), and in a second model the gap in health-adjusted life expectancy (HALE), for each OECD country and year from 2000 to 2023. The predictors are the differences between male and female death rates from specific causes: road traffic, suicide, homicide, drug and alcohol use disorders, liver disease, cancer, cardiovascular and chronic respiratory disease, and others.

The main model is a Bayesian hierarchical panel model, written in [PyMC](https://www.pymc.io/), with an intercept for each country. Counterfactual analyses then ask how the gap in a given country would change if the gap for one cause were reduced.

## What is where

| Path | Contents |
|------|----------|
| [`notebooks/`](notebooks/) | The analysis, as [jupytext](https://jupytext.readthedocs.io/) markdown notebooks (`.md`), with helper modules (`utils.py`, `fig_utils.py`, `counterfactual_utils.py`) |
| [`notebooks/datawrapper/`](notebooks/datawrapper/) | The data behind each figure and table in the policy paper, one CSV each, with an [inventory](notebooks/datawrapper/README.md) |
| [`jb/`](jb/) | Source for the project site ([MyST](https://mystmd.org/) / Jupyter Book 2) |
| [`examples/python-to-r/`](examples/python-to-r/) | The same model in PyMC and in R with brms, and a comparison of the two |

## Data

- **Cause-specific death rates and HALE:** [IHME Global Burden of Disease 2023](https://www.healthdata.org/research-analysis/gbd), downloaded by sex for OECD countries from IHME's [GBD Compare](https://vizhub.healthdata.org/gbd-compare/) tool. The [Data Inventory](https://allendowney.github.io/LifeExpectancy/data-inventory/) lists each indicator and the settings used.
- **Life expectancy by sex:** [Our World in Data](https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex), downloaded by [`notebooks/download_owid_le.py`](notebooks/download_owid_le.py).
- **WHO Global Health Observatory:** used to check the results against a second source ([`notebooks/who_data.py`](notebooks/who_data.py)).

IHME's terms don't allow redistributing their data, so it is not included; download it from IHME. Results derived from it carry IHME's required notice:

> Source: Institute for Health Metrics and Evaluation. Used with permission. All rights reserved.

The raw data goes in `data/`, which is not in the repository. Notebooks write intermediate files, model traces, figures, and tables to `notebooks/interim/`, `nc/`, `figs/`, and `tables/`, which are not tracked either.

## Running the analysis

Create the environment with [mamba](https://mamba.readthedocs.io/) (it includes Python, R, and Stan, and registers an R kernel for Jupyter):

```bash
make env
conda activate LifeExpectancy
```

To run a notebook, convert it to `.ipynb` and execute it from the `notebooks/` directory:

```bash
cd notebooks
jupytext --to ipynb process.md
papermill process.ipynb process_executed.ipynb
```

Run the notebooks in this order:

1. [`process.md`](notebooks/process.md) builds the country-year panels for LE and HALE (`interim/panel_le.h5`, `interim/panel_hale.h5`).
2. [`bayesian_model.md`](notebooks/bayesian_model.md) fits the LE and HALE models and saves the posterior draws in `nc/`. Later runs reuse them; pass `-p FORCE_RUN True` to papermill to sample again.
3. [`bayes_counter_le.md`](notebooks/bayes_counter_le.md) and [`bayes_counter_hale.md`](notebooks/bayes_counter_hale.md) run the counterfactuals for one country (`-p COUNTRY_CODE USA`).
4. Figures: [`time_series_figs.md`](notebooks/time_series_figs.md) and [`bayesian_le_figs.md`](notebooks/bayesian_le_figs.md); for the road-traffic figure, run [`extract_factor_changes.py`](notebooks/extract_factor_changes.py) and then [`road_traffic_dumbbell.md`](notebooks/road_traffic_dumbbell.md).
5. Causal assumptions: [`causal_model.md`](notebooks/causal_model.md) and [`presentation_dags.md`](notebooks/presentation_dags.md).

The other notebooks are exploratory: time series ([`time_series.md`](notebooks/time_series.md)), a cancer drilldown ([`neoplasms.md`](notebooks/neoplasms.md)), the comparison of WHO and IHME data ([`who_data.md`](notebooks/who_data.md)), and the Elastic Net models that came before the Bayesian one ([`model_le.md`](notebooks/model_le.md), [`model_hale.md`](notebooks/model_hale.md)).

## Python to R example

[`examples/python-to-r/`](examples/python-to-r/) has an early version of the model written twice, in PyMC and in R with brms, and a notebook that shows the two posteriors agree.

## How to cite

For the findings, cite the policy paper:

> Downey, Allen B. 2026. "Is It Inevitable That Men Die Younger Than Women? Looking at Evidence and Policy Solutions." American Institute for Boys and Men. https://aibm.org/research/is-it-inevitable-that-men-die-younger-than-women-looking-at-evidence-and-policy-solutions/

For the code and data, cite this repository at the version used for the paper (tag [`published-2026`](https://github.com/AllenDowney/LifeExpectancy/tree/published-2026)):

> Downey, Allen B. 2026. *The Gender Gap in Life Expectancy* (code and data). https://github.com/AllenDowney/LifeExpectancy

## License

The code is under the [MIT License](LICENSE). The text, including the site pages and reports, is under [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
