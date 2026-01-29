# Life Expectancy Gender Gap Analysis

Exploring causes of gender differences in life expectancy across OECD countries.

## Overview

This project analyzes the gender gap in life expectancy using data from WHO and IHME. It identifies which mortality factors (cardiovascular disease, alcohol, suicide, etc.) explain the most variation in the life expectancy gap between men and women.

The analysis uses:
- **PyMC (Python)**: Bayesian hierarchical panel model implementation
- **brms (R/Stan)**: Bayesian hierarchical panel model implementation
- **Model comparison**: Validation that both implementations produce identical results

A [Quarto website](https://allendowney.github.io/LifeExpectancy/) provides a concise summary of the methodology, results, and findings.

## Repository Structure

```
LifeExpectancy/
├── environment.yml      # Conda environment (Python + R + Stan)
├── Makefile             # Setup and build commands
├── data/                # WHO and IHME data files
│   ├── who_*.csv        # WHO health indicators
│   ├── ihme_*.csv       # IHME cause-of-death data
│   └── *.h5             # Processed data (HDF5)
├── notebooks/
│   ├── utils.py         # Helper functions (Python)
│   ├── utils.R          # Helper functions (R)
│   ├── process.ipynb    # Data preparation and processing
│   ├── bayesian_model_py.ipynb  # PyMC implementation
│   ├── bayesian_model_r.Rmd     # brms implementation
│   └── compare_pymc_brms.ipynb  # Model comparison
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

Run the notebooks in order:

1. **`process.ipynb`** — Load raw data, compute gender gaps, filter to OECD countries, save to HDF5/CSV
2. **`bayesian_model_py.ipynb`** — Fit Bayesian hierarchical panel model using PyMC
3. **`bayesian_model_r.Rmd`** — Fit Bayesian hierarchical panel model using brms
4. **`compare_pymc_brms.ipynb`** — Compare results between PyMC and brms implementations

## Data Sources

- **WHO Global Health Observatory**: Life expectancy, HALE, mortality indicators
  - https://www.who.int/data/gho
- **IHME Global Burden of Disease 2023**: Cause-specific mortality by sex
  - https://vizhub.healthdata.org/gbd-results/


## License

MIT License - see [LICENSE](LICENSE)
