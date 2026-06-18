# Datawrapper CSV exports (policy report)

CSV files for collaborators rebuilding figures and tables from **[The Life Expectancy Gender Gap: Evidence and Policy v2](../../report/The%20Life%20Expectancy%20Gender%20Gap_%20Evidence%20and%20Policy%20v2.md)** in Datawrapper.

**Scope:** CSV generation only (no Datawrapper API upload yet). Upload charts manually from these files.

**Regenerate:** from `notebooks/` with conda env `LifeExpectancy`:

```bash
cd notebooks

# Batch 1 — time series (Figures 1–5, 9–10)
jupytext --to ipynb time_series_figs.md --output time_series_figs.ipynb
papermill time_series_figs.ipynb time_series_figs_executed.ipynb -k python3

# Batch 2 — LE coefficients + USA counterfactuals (Figures A1, 6–7; LE tables)
jupytext --to ipynb bayesian_le_figs.md --output bayesian_le_figs.ipynb
papermill bayesian_le_figs.ipynb bayesian_le_figs_executed.ipynb -k python3

jupytext --to ipynb bayes_counter_le.md --output bayes_counter_le.ipynb
papermill bayes_counter_le.ipynb bayes_counter_le_executed.ipynb -k python3 -p COUNTRY_CODE USA

# Batch 3 — road traffic dumbbell + HALE counterfactuals (Figures 8, 11; HALE table)
python extract_factor_changes.py
jupytext --to ipynb road_traffic_dumbbell.md --output road_traffic_dumbbell.ipynb
papermill road_traffic_dumbbell.ipynb road_traffic_dumbbell_executed.ipynb -k python3

jupytext --to ipynb bayes_counter_hale.md --output bayes_counter_hale.ipynb
papermill bayes_counter_hale.ipynb bayes_counter_hale_executed.ipynb -k python3 -p COUNTRY_CODE USA
```

---

## Figures (v2 numbering)

| v2 figure | Short title | CSV file | Status | Source notebook |
|-----------|-------------|----------|--------|-----------------|
| **Figure 1** | Life expectancy gender gap (OECD, 2000–2023) | [`le_gap_timeseries_selected.csv`](le_gap_timeseries_selected.csv) | **available** | [`time_series_figs.md`](../time_series_figs.md) |
| **Figure 2** | Drug use disorders death-rate gap | [`drug_disorders_gap_timeseries_selected.csv`](drug_disorders_gap_timeseries_selected.csv) | **available** | `time_series_figs.md` |
| **Figure 3** | Homicide death-rate gap | [`homicide_gap_timeseries_selected.csv`](homicide_gap_timeseries_selected.csv) | **available** | `time_series_figs.md` |
| **Figure 4** | Suicide death-rate gap | [`suicide_gap_timeseries_selected.csv`](suicide_gap_timeseries_selected.csv) | **available** | `time_series_figs.md` |
| **Figure 5** | Road traffic death-rate gap | [`road_traffic_gap_timeseries_selected.csv`](road_traffic_gap_timeseries_selected.csv) | **available** | `time_series_figs.md` |
| **Figure 6** | U.S. LE counterfactual forest (2023) | [`counterfactual_effects_usa_2023_le.csv`](counterfactual_effects_usa_2023_le.csv) | **available** | [`bayes_counter_le.md`](../bayes_counter_le.md) |
| **Figure 7** | U.S. LE stacked contributions (2000–2023) | [`positive_contributions_stacked_area_usa_le.csv`](positive_contributions_stacked_area_usa_le.csv) | **available** | `bayes_counter_le.md` |
| **Figure 8** | Road traffic dumbbell (Europe) | [`road_traffic_dumbbell_europe.csv`](road_traffic_dumbbell_europe.csv) | **available** | [`road_traffic_dumbbell.md`](../road_traffic_dumbbell.md) (+ [`extract_factor_changes.py`](../extract_factor_changes.py)) |
| **Figure 9** | HALE gender gap (OECD, 2000–2023) | [`hale_gap_timeseries_blog_match.csv`](hale_gap_timeseries_blog_match.csv) | **available** | `time_series_figs.md` |
| **Figure 10** | HALE levels by sex (M/F) | [`hale_levels_male_female_timeseries.csv`](hale_levels_male_female_timeseries.csv) | **available** | `time_series_figs.md` |
| **Figure 11** | U.S. HALE stacked contributions vs predicted/actual | [`positive_contributions_stacked_area_usa_hale.csv`](positive_contributions_stacked_area_usa_hale.csv) | **available** | [`bayes_counter_hale.md`](../bayes_counter_hale.md) |
| **Figure A1** | LE cause coefficients (94% CI) | [`blog2_coefficients_le.csv`](blog2_coefficients_le.csv) | **available** | [`bayesian_le_figs.md`](../bayesian_le_figs.md) |

**Note on Figure A1 vs main text:** v2 puts the LE coefficient chart in **Appendix A (Figure A1)**. [`jb/policy_report.md`](../../jb/policy_report.md) embeds the same PNG (`blog2_coefficients_le.png`) in the modeling section before counterfactuals.

Matching PNGs (for visual check) live under [`jb/figs/`](../../jb/figs/) with the same basename as the CSV (`.png`).

---

## Tables (v2 / policy report)

v2 uses inline markdown tables (no separate “Table N” labels). Names below match section content.

| Report table (v2 location) | CSV file | Status | Source notebook |
|----------------------------|----------|--------|-----------------|
| **U.S. LE counterfactuals (2023)** — counterfactual section table (Cause, Current gap, Target gap, …) | [`counterfactuals_usa_2023_le.csv`](counterfactuals_usa_2023_le.csv) | **available** | `bayes_counter_le.md` (USA run) |
| **HALE vs LE coefficient ranks** — HALE section (Cause, Coefficient, Rank HALE, Rank LE) | [`blog5_hale_coefficient_ranks.csv`](blog5_hale_coefficient_ranks.csv) | **available** | `bayesian_le_figs.md` |
| **U.S. HALE counterfactuals (2023)** — HALE section table | [`counterfactuals_usa_2023_hale.csv`](counterfactuals_usa_2023_hale.csv) | **available** | `bayes_counter_hale.md` (USA run) |
| **Minimum attainable gap by cause (LE)** — appendix table (Cause, Minimum gap, Country, Year) | [`gap_extremes_min_le.csv`](gap_extremes_min_le.csv) | **available** | `bayes_counter_le.md` |

Policy report HTML includes (`jb/tables/policy_*.html`) are copies of the same underlying tables; CSVs mirror the numeric content of those tables.

---

## Column schemas

### Gap time series (Figures 1–5, 9)

Long format: one row per country-year, plus OECD-average rows.

| Column | Description |
|--------|-------------|
| `year` | Calendar year (2000–2023) |
| `code` | ISO3 country code, or `OECD` for the OECD average series |
| `country` | Country name, or `OECD average` |
| `gap` | Plotted gap value (see units below) |
| `highlighted` | `True` if country is labeled/highlighted in the report figure |
| `series` | Label for Datawrapper line grouping (country name or `OECD average`) |

**Units / sign convention**

- **Figure 1, 9 (`LE_gap`, `HALE_gap`):** years, **female minus male** (positive = women live longer).
- **Figures 2–5 (cause death-rate gaps):** deaths per 100,000, **male minus female** (IHME `Gap_*` convention).

**Highlighted countries** (match report figures):

| Figure | `highlighted=True` codes |
|--------|--------------------------|
| 1, 9 | USA, GBR, NOR, FRA, CAN, LTU, JPN |
| 2 | USA, NOR, KOR, LTU, CAN, EST |
| 3 | USA, NOR, COL, LTU, MEX, CRI |
| 4 | USA, NOR, TUR, LTU, CAN, KOR |
| 5 | USA, NLD, DEU, CRI, CAN, LTU, MEX |

All OECD countries are included in each file (`highlighted=False` for background lines).

### HALE levels by sex (Figure 10)

| Column | Description |
|--------|-------------|
| `year` | Calendar year |
| `code` | ISO3 |
| `country` | Country name |
| `sex` | `Male` or `Female` |
| `value` | HALE (years) |
| `highlighted` | `True` for Lithuania (LTU) and Norway (NOR) |

All OECD countries are included; non-highlighted countries correspond to faint background lines in the figure.

### LE coefficients (Figure A1 / main text)

| Column | Description |
|--------|-------------|
| `cause` | Cause label (matches figure y-axis) |
| `coefficient` | Posterior mean (years of LE gap per unit standardized gap) |
| `hdi_lo`, `hdi_hi` | 94% HDI bounds |

### HALE vs LE coefficient ranks (table)

| Column | Description |
|--------|-------------|
| `Cause` | Cause label |
| `Coefficient` | HALE model coefficient (rounded for display) |
| `Rank (HALE)` | Rank by HALE coefficient magnitude |
| `Rank (LE)` | Rank by LE coefficient magnitude |

### USA LE counterfactual forest (Figure 6)

| Column | Description |
|--------|-------------|
| `cause` | Cause label |
| `change_mean` | Posterior mean change in LE gap (years) if cause gap set to minimum |
| `hdi_lo`, `hdi_hi` | 94% HDI bounds |

### USA LE counterfactual table

| Column | Description |
|--------|-------------|
| `Cause` | Cause label |
| `Current gap` | U.S. cause gap in 2023 (deaths per 100k, male minus female) |
| `Target gap` | Minimum observed OECD gap for that cause |
| `Target Country-Year` | Country and year where minimum was observed |
| `Change in LE gap (years)` | Posterior mean change in overall LE gap |

### USA LE stacked contributions (Figure 7)

Long/tidy format for stacked area + total lines.

| Column | Description |
|--------|-------------|
| `year` | Calendar year (2000–2023) |
| `series` | Cause name, or `Predicted Total` / `Actual Total` |
| `series_type` | `contribution` (stacked areas) or `total` (line overlays) |
| `value` | Years of LE gap contribution or total gap |

### Road traffic dumbbell (Figure 8)

European OECD countries, sorted by `change` (most negative first).

| Column | Description |
|--------|-------------|
| `code` | ISO3 country code |
| `country` | Country name |
| `val_2000` | Road-traffic contribution to LE gap in 2000 (years) |
| `val_2023` | Road-traffic contribution to LE gap in 2023 (years) |
| `change` | `val_2023 - val_2000` (negative = contribution fell) |
| `is_largest_decrease` | `True` if road traffic was the largest-decrease factor for that country |
| `is_largest_increase` | `True` if road traffic was the largest-increase factor |
| `substantial` | `True` if \|change\| ≥ 0.2 years |

### USA HALE counterfactual table

Same structure as LE counterfactual table; change column is `Change in HALE gap (years)`.

### USA HALE stacked contributions (Figure 11)

Same long/tidy structure as LE stacked contributions (`year`, `series`, `series_type`, `value`).

### Minimum attainable gap by cause (LE appendix table)

| Column | Description |
|--------|-------------|
| `Cause` | Cause label |
| `Minimum gap` | Minimum observed OECD cause gap (deaths per 100k) |
| `Country` | Country where minimum was observed |
| `Year` | Year of minimum |

---

## Current inventory snapshot

**17 CSV files present** — all v2 figures (1–11, A1) and all in-scope report tables.

Please compare CSVs against the v2 manuscript and `jb/figs/` PNGs before handing off to collaborators.
