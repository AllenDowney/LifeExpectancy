---
description: "The same Bayesian hierarchical model written in Python with PyMC and in R with brms, and a comparison showing that the two posteriors agree."
title: "Python to R: The Same Bayesian Model in PyMC and brms"
---

Early in this project, we wrote the model twice, once in Python with [PyMC](https://www.pymc.io/) and once in R with [brms](https://paul-buerkner.github.io/brms/), and checked that the two give the same answer. The notebooks are in [`examples/python-to-r/`](https://github.com/AllenDowney/LifeExpectancy/tree/main/examples/python-to-r) in the repository. They are saved with their outputs, so you can read them on GitHub without running anything.

## The model

This is an early version (January 2026) of the model in the [Bayesian Panel Data Model](bayesian_model_report_2023.md) report. The outcome is the gap between female and male life expectancy for 37 OECD countries and each year. The predictors are the differences between male and female death rates from specific causes. Predictors are standardized, the outcome is centered, and each country has its own intercept. In brms notation:

```
LE_gap_centered ~ Gap_Alcohol + Gap_Suicide + ... + (1 | country)
```

Both versions use the same priors: Normal(0, 1) for the coefficients, Normal(0, 5) for the intercept, and half-Normal(1) for the country and residual standard deviations.

## The notebooks

- [`bayesian_model_py.ipynb`](https://github.com/AllenDowney/LifeExpectancy/blob/main/examples/python-to-r/bayesian_model_py.ipynb) fits the model with PyMC, sampled with nutpie.
- [`bayesian_model_r.ipynb`](https://github.com/AllenDowney/LifeExpectancy/blob/main/examples/python-to-r/bayesian_model_r.ipynb) fits the same model with brms, which uses Stan.
- [`compare_pymc_brms.ipynb`](https://github.com/AllenDowney/LifeExpectancy/blob/main/examples/python-to-r/compare_pymc_brms.ipynb) compares the two posteriors.

## The result

The two fits agree to within Monte Carlo error. The posterior means of the coefficients differ by less than 0.002 on the standardized scale, and the country intercepts correlate at r = 0.99999.

To run the notebooks yourself, see the [README](https://github.com/AllenDowney/LifeExpectancy/tree/main/examples/python-to-r) in that folder.
