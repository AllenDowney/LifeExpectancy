# Post 3: Counterfactuals — How Much of the Gap Could We Close?

## Purpose

Present the counterfactual analysis that estimates how much of the life expectancy gap could feasibly be closed by reducing gender gaps in specific causes of death. Use country-specific analysis to show that prioritization depends on where a country stands relative to best attainable levels — not just on global importance.

---

## Logical Flow

### 1. Bridge from Importance (Blog 2)

- **Recap**: In the previous article we estimated coefficients (effect size) and importance (coefficient × standard deviation). Importance shows which factors contribute most to *overall* variation in the life expectancy gap across countries and time.
- **Limitation**: The most important factor globally may not be the most important for a particular country. For example, drug disorders have low importance overall because the gap is small in most OECD countries — but in the United States and Canada, drug disorders have a much larger effect on the life expectancy gap.
- **This article**: We ask a different question — *for a given country*, which causes of death offer the largest opportunity to close the gap? To answer that, we need **country-specific counterfactuals**.

### 2. The Counterfactual Question and Methodology

- **Question**: What would happen to a country's life expectancy gap if we reduced each cause-specific gender gap to the best level achieved by any OECD country in the dataset?
- **"Best attainable"**: For each cause, we find the minimum gap observed across all 37 countries and 24 years. If Iceland achieved a small road traffic gap, we assume it's possible for others.

Table: Minimum gap by cause across OECD countries (country and year where each minimum occurs).

```{include} tables/gap_extremes_min_blog_le.html
```

- **Conservative approach**: We adjust only the *gap* (male–female difference in death rates), not overall death rates. We're not assuming countries can achieve Iceland's overall traffic safety — only that they could achieve Iceland's *gender parity* in traffic deaths.
- **Prediction**: Using the Bayesian model from Blog 2, we predict how the life expectancy gap would change if each predictor were adjusted to its best attainable value (holding others constant). Results include 94% credible intervals.

### 3. United States (Primary Case Study)

- **Why the US**: Promised in Blog 2; also OECD-average gap (~5 years) with distinctive drivers (opioid epidemic, homicide, road traffic).
- **Current gap** (2023): ~5.4 years predicted

Table: Counterfactual impacts for USA 2023 (sorted by magnitude).

```{include} tables/counterfactuals_usa_2023_le_blog.html
```

Figure: Counterfactual effects by cause, USA 2023 (gap-closing vs gap-widening, 94% credible intervals).

```{figure} figs/counterfactual_effects_usa_2023_le_bayesian.png
:width: 80%

Counterfactual effects: hypothetical change in life expectancy gap for each cause-specific death rate, USA (2023), 94% credible intervals.
```

Figure: Positive contributions to the life expectancy gap over time, USA (2000–2023).

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:width: 80%

Stacked positive contributions to the life expectancy gap, USA (2000–2023).
```

### 4. High-Gap Countries (Lithuania, Latvia, Estonia)

Figure: Country intercepts (random effects) from the hierarchical model—each country’s baseline gap when predictors are at their mean, 94% credible intervals.

```{figure} figs/country_intercepts_le_intercepts.png
:width: 80%

Country intercepts (random effects): deviation from grand mean, 94% credible intervals.
```

- **Context**: In 2023 these Baltic countries had the largest gaps in the OECD (>8 years). Blog 1: "A ferry from Tallinn to Stockholm travels 240 miles and closes the gender gap from 8.1 years in Estonia to 3.7 years in Sweden."
- **Question**: Which causes drive their large gaps? Which offer the largest opportunities to close them?
- **Expected pattern**: Suicide and road traffic have been major drivers; Lithuania's road traffic gap improved sharply post-EU accession. Counterfactuals will quantify remaining potential.
- **Narrative**: Compare one or two Baltic countries (e.g., Lithuania as primary). Show which factors are "low-hanging fruit" vs already improved.

### 5. Low-Gap Country (Netherlands or Norway)

- **Context**: Netherlands, Norway, Luxembourg, New Zealand all had gaps <3.5 years in 2023. Blog 1 established that near-zero gaps are achievable.
- **Question**: What (if anything) could close the remaining gap? Or — what drove these countries to achieve small gaps?
- **Expected pattern**: Smaller counterfactual impacts overall; some factors may show gap-widening effects (competing risks) if eliminating remaining small gaps would paradoxically widen the LE gap.
- **Narrative**: Use one low-gap country to show that the model applies across the spectrum — and that even "best" countries may have room for improvement in specific causes.

### 6. Synthesis and Policy Implications

- **Country-specific prioritization**: The counterfactual ranking differs by country. Road traffic may be top everywhere it's poor; drug disorders matter most where the epidemic hit; suicide matters where rates are high.
- **Feasibility**: Evidence from other countries that it's achievable. Clear causal pathways.
- **Competing risks**: Cardiovascular, diabetes, lung disease — eliminating these gaps could widen the LE gap. Interpretation: these affect overall mortality but have complex relationships with gender gaps; not a reason to ignore them for health policy, but a nuance for gap-focused interventions.
- **Key message**: A substantial portion of the gender gap could be closed through targeted interventions. The roadmap is country-specific.

---

## Key Message

A substantial portion of the gender gap in life expectancy could be closed through targeted interventions. Country-specific counterfactual analysis shows that prioritization depends on how far each country is from best attainable levels — not just on global importance. Road traffic safety offers the largest single impact in the United States; drug disorders and suicide are also critical. High-gap countries like Lithuania have different drivers and opportunities; low-gap countries like the Netherlands show that near-zero gaps are achievable.

---

## Completed Since Last Update

- [x] **Factor change analysis (2000 vs 2023)**: For each country, compute which factor's contribution increased or decreased the most between 2000 and 2023. Per-country logic in `bayes_counter_le.md`; each papermill run updates `tables/contribution_changes_2000_2023_le.json` and regenerates the HTML table.
- [x] **Collated contribution changes by region**: `jb/contribution_changes_2000_2023.md` with tables organized by region for all 37 countries.
- [x] **Road traffic European analysis**: `extract_factor_changes.py` extracts Road Traffic contribution change (2000→2023) for 26 European countries from positive_contributions HTML; outputs CSV (`tables/road_traffic_gap_change_europe.csv`) and markdown (`jb/road_traffic_gap_change_europe.md`).
- [x] **Road traffic dumbbell plot**: `notebooks/road_traffic_dumbbell.md` reads the CSV and creates horizontal dumbbell plot (square = 2000, left-pointing triangle = 2023, gray connecting lines, AIBM style). Output: `figs/road_traffic_dumbbell_europe.png`.
- [x] **Blog integration**: Replaced the road traffic table in `blog3_counterfactual.md` with the dumbbell figure in the "Success Story: Road Traffic in Europe" section.

---

## Tasks Before Draft

- [ ] Run counterfactuals for Lithuania (and/or Latvia) — extend `bayes_counter_le` or add cells
- [ ] Run counterfactuals for Netherlands (and/or Norway)
- [ ] Generate comparison figure/table if using multiple countries
- [ ] Update numeric results to match latest model (13 predictors including Childhood)
- [ ] Verify `tables/counterfactuals_usa_2023_le_bayesian.html` reflects current run
