# Python to R: the same Bayesian model in PyMC and brms

This folder shows one model written twice, once in Python with [PyMC](https://www.pymc.io/) and once in R with [brms](https://paul-buerkner.github.io/brms/), and checks that the two give the same answer. It comes from an early version of this project (January 2026), when we translated the Python analysis into R.

The model is a Bayesian hierarchical panel model of the gender gap in life expectancy across 37 OECD countries. The predictors are the gaps between male and female death rates from each cause: road traffic, suicide, alcohol, cancer, and so on. In brms notation:

```
LE_gap_centered ~ Gap_Alcohol + Gap_Suicide + ... + (1 | country)
```

Predictors are standardized, the outcome is centered, and each country has its own intercept. Both versions use the same priors: Normal(0, 1) for the coefficients, Normal(0, 5) for the intercept, and half-Normal(1) for the country and residual standard deviations.

The published analysis uses a later version of this model. See the main [README](../../README.md).

## Notebooks

| Notebook | What it does |
|----------|--------------|
| [`bayesian_model_py.ipynb`](bayesian_model_py.ipynb) | Fits the model with PyMC (sampled with nutpie) and saves the posterior samples |
| [`bayesian_model_r.ipynb`](bayesian_model_r.ipynb) | Fits the same model with brms (Stan) and saves the posterior samples |
| [`compare_pymc_brms.ipynb`](compare_pymc_brms.ipynb) | Compares the two posteriors: coefficients, country intercepts, and hyperparameters |

The notebooks are saved with their outputs, so you can read them on GitHub without running anything.

## Result

The two fits agree to within Monte Carlo error. The posterior means of the coefficients differ by less than 0.002 (on the standardized scale), and the country intercepts correlate at r = 0.99999.

## Running them

- The input is `data/panel_le.csv`: one row per country and year (888 rows), with the life expectancy gap and the cause-specific gaps. It is derived from IHME data, which IHME's terms don't allow us to redistribute, so it is not in the repository. To make it, run [`notebooks/process.md`](../../notebooks/process.md) (see the main [README](../../README.md)), then `python make_panel.py` in this folder. With the February 2026 data, this reproduces the input the saved outputs were made with.
- `utils.py` and `utils.R` are symbolic links to the helper modules in [`notebooks/`](../../notebooks/). On Windows, where git may check out a link as a small text file, copy those two files here instead.
- The environment in the repo's [`environment.yml`](../../environment.yml) includes Python, R, brms, and CmdStan, plus a Jupyter kernel for R. Run `make env` at the top of the repo, then `conda activate LifeExpectancy`.
- Run the two model notebooks first, then the comparison. Results are written to `output/` and logs to `logs/` (both ignored by git).

Source: Institute for Health Metrics and Evaluation. Used with permission. All rights reserved.
