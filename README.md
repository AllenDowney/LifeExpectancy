# Life Expectancy Gender Gap Analysis

Exploring causes of gender differences in life expectancy across OECD countries.

## Overview

This project analyzes the gender gap in life expectancy using data from WHO and IHME. It identifies which mortality factors (cardiovascular disease, alcohol, suicide, etc.) explain the most variation in the life expectancy gap between men and women.

The analysis uses PyMC (Python) for Bayesian hierarchical panel modeling.

A [Quarto website](https://allendowney.github.io/LifeExpectancy/) provides a concise summary of the methodology, results, and findings.

## Repository Structure

```
LifeExpectancy/
├── environment.yml      # Conda environment (Python + R + Stan)
├── Makefile             # Setup and build commands
├── data/                # Raw data files (WHO and IHME)
│   ├── who_*.csv        # WHO health indicators
│   ├── ihme_*.csv       # IHME cause-of-death data
│   └── *.h5             # Processed data files
├── notebooks/           # Analysis notebooks and outputs
│   ├── *.ipynb, *.md   # Jupyter notebooks (in .ipynb and .md formats)
│   ├── utils.py         # Helper functions (Python)
│   ├── utils.R          # Helper functions (R)
│   ├── counterfactual_utils.py  # Counterfactual analysis utilities
│   ├── download_data.py # Data download scripts
│   ├── who_data.py      # WHO data access utilities
│   ├── interim/         # Interim data (metadata, panel datasets)
│   ├── nc/              # NetCDF trace files (model outputs)
│   ├── figs/            # Figure outputs
│   ├── tables/          # Table outputs (HTML, CSV)
│   └── logs/            # Execution logs
├── jb/                  # Jupyter Book (figs and tables for reports)
└── quarto/              # Quarto website source
    ├── _quarto.yml      # Site configuration
    ├── index.qmd        # Landing page
    ├── tech_report.qmd  # Technical report
    └── Makefile         # Build and deploy commands
```

## Setup

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)
- [Mamba](https://mamba.readthedocs.io/) (optional but recommended for faster installs)

Install mamba if you don't have it:
```bash
conda install -n base -c conda-forge mamba
```

### Create Environment

```bash
make env
```

This creates a conda environment with:
- Python 3.11 + pandas, PyMC, nutpie, arviz, etc.
- R 4.3 + brms, tidyverse, cmdstan
- Jupyter with both Python and R kernels
- Quarto for website generation

### Activate and Run

```bash
conda activate LifeExpectancy
jupyter lab
```

## Data Pipeline

### Main Analysis Pipeline

Run the notebooks in order:

1. **`process.ipynb`** — Load raw data, compute gender gaps, filter to OECD countries, save to HDF5/CSV
2. **`bayesian_model.ipynb`** — Fit Bayesian hierarchical panel model using PyMC

### Additional Analyses
- **`bayes_counter_hale.ipynb`** — Counterfactual analysis for HALE gap
- **`bayes_counter_le.ipynb`** — Counterfactual analysis for Life Expectancy gap
- **`time_series.ipynb`** — Time series analysis of gaps and predictors
- **`neoplasms.ipynb`** — Cancer-specific analysis
- **`model_hale.ipynb`**, **`model_le.ipynb`** — Additional modeling approaches

### Output Organization

Notebooks write outputs to subdirectories within `notebooks/`:
- **`interim/`** — Intermediate data files (metadata, panel datasets) generated during processing
- **`nc/`** — NetCDF trace files from Bayesian model fits
- **`figs/`** — All figure outputs (PNG)
- **`tables/`** — All table outputs (HTML, CSV)
- **`logs/`** — Execution logs

Data files are read from `../data/` (relative to notebooks directory).

## Data Sources

- **WHO Global Health Observatory**: Life expectancy, HALE, mortality indicators
  - https://www.who.int/data/gho
- **IHME Global Burden of Disease 2023**: Cause-specific mortality by sex
  - https://vizhub.healthdata.org/gbd-results/


## License

MIT License - see [LICENSE](LICENSE)
