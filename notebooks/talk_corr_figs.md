---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.20.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Talk figures: predictor correlation scatters (AIBM)

Small notebook aligned with `process.md`: **one OECD country per point** — for each cause, the most recent year ≤ `cutoff_year` (`summarize_gap`), then an **inner join** across alcohol, childhood (under-five), homicide, and road traffic.

Point colors by relationship type (**AIBM**): **rate–gap** (Mid vs Gap) → green; **gap–gap** → purple; **level–level** (Mid vs Mid) → orange.

Outputs in `figs/`:

- `talk_corr_gap_level_alcohol.png`, `talk_corr_gap_level_homicide.png`, `talk_corr_gap_level_roadtraffic.png` — Mid vs gap (one plot per cause)
- `talk_corr_level_level_childhood_homicide.png` — Mid childhood vs Mid homicide
- `talk_corr_gap_gap_childhood_road.png` — Gap childhood vs Gap road traffic

```python
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt

from utils import (
    configure_plot_style,
    load_ihme_indicator,
    raw_to_temporal_gaps,
    column_name_mapping,
    summarize_gap,
    get_oecd,
)
from fig_utils import plot_correlation_scatter_aibm

configure_plot_style()

# Match process.md descriptive / correlation tables (pre-COVID cross-section)
cutoff_year = 2019
```

```python
def _load_ihme(name, base, value_col, code, desc, age_filter='All ages'):
    raw = load_ihme_indicator(
        f'../data/{base}_male.csv', f'../data/{base}_female.csv',
        value_col_name=value_col, indicator_code=code, indicator_name=desc,
        max_year=2023, age_filter=age_filter,
    )
    renamed = raw.rename(columns=column_name_mapping)
    temporal = raw_to_temporal_gaps(raw, value_col)
    return renamed, temporal


alcohol_use_disorders_ihme, _ = _load_ihme(
    'alcohol', 'ihme_alcohol_use_disorders_deaths', 'AlcoholUseDisordersDeathRate',
    'IHME_ALCOHOL_USE_DISORDERS', 'Alcohol use disorders',
)
interpersonal_violence_ihme, _ = _load_ihme(
    'interpersonal_violence', 'ihme_interpersonal_violence_deaths',
    'InterpersonalViolenceDeathRate',
    'IHME_INTERPERSONAL_VIOLENCE', 'Interpersonal violence (homicide)',
)
road_injuries_ihme, _ = _load_ihme(
    'road_injuries', 'ihme_road_injuries_deaths', 'RoadInjuriesDeathRate',
    'IHME_ROAD_INJURIES', 'Road injuries',
)
all_causes_under5_ihme, _ = _load_ihme(
    'all_causes_under5', 'ihme_all_causes_under5_deaths', 'AllCausesUnder5DeathRate',
    'IHME_ALL_CAUSES_UNDER5', 'All-cause deaths under 5 years', age_filter='<5 years',
)
```

```python
gap_alcohol = summarize_gap(alcohol_use_disorders_ihme, 'Alcohol', cutoff_year=cutoff_year)
plt.close('all')
gap_childhood = summarize_gap(all_causes_under5_ihme, 'Childhood', cutoff_year=cutoff_year)
plt.close('all')
gap_homicide = summarize_gap(interpersonal_violence_ihme, 'Homicide', cutoff_year=cutoff_year)
plt.close('all')
gap_road = summarize_gap(road_injuries_ihme, 'RoadTraffic', cutoff_year=cutoff_year)
plt.close('all')

m = (
    get_oecd(gap_alcohol)[['Mid_Alcohol', 'Gap_Alcohol']]
    .join(get_oecd(gap_childhood)[['Mid_Childhood', 'Gap_Childhood']], how='inner')
    .join(get_oecd(gap_homicide)[['Mid_Homicide', 'Gap_Homicide']], how='inner')
    .join(get_oecd(gap_road)[['Mid_RoadTraffic', 'Gap_RoadTraffic']], how='inner')
)
m.shape
```

```python
rate_unit = 'Death rate (per 100,000)'
gap_unit = 'Gender gap in rate (male − female, per 100,000)'
src = 'Source: IHME Global Burden of Disease, OECD countries; most recent year ≤ 2019 per country.'
```

```python
fig, ax = plot_correlation_scatter_aibm(
    m,
    'Mid_Alcohol',
    'Gap_Alcohol',
    title='Alcohol use disorders: level vs gender gap',
    subtitle=f'OECD, one country per point ({cutoff_year} cross-section)',
    xlabel=f'Overall death rate — {rate_unit}',
    ylabel=f'Gap — {gap_unit}',
    subtext=src,
    trend_line=True,
    logo=True,
    correlation_kind='rate_gap',
)
plt.savefig('figs/talk_corr_gap_level_alcohol.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
fig, ax = plot_correlation_scatter_aibm(
    m,
    'Mid_Homicide',
    'Gap_Homicide',
    title='Homicide: level vs gender gap',
    subtitle=f'OECD, one country per point ({cutoff_year} cross-section)',
    xlabel=f'Overall death rate (interpersonal violence) — {rate_unit}',
    ylabel=f'Gap — {gap_unit}',
    subtext=src,
    trend_line=True,
    logo=True,
    correlation_kind='rate_gap',
)
plt.savefig('figs/talk_corr_gap_level_homicide.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
fig, ax = plot_correlation_scatter_aibm(
    m,
    'Mid_RoadTraffic',
    'Gap_RoadTraffic',
    title='Road injuries: level vs gender gap',
    subtitle=f'OECD, one country per point ({cutoff_year} cross-section)',
    xlabel=f'Overall death rate (road injuries) — {rate_unit}',
    ylabel=f'Gap — {gap_unit}',
    subtext=src,
    trend_line=True,
    logo=True,
    correlation_kind='rate_gap',
)
plt.savefig('figs/talk_corr_gap_level_roadtraffic.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
fig, ax = plot_correlation_scatter_aibm(
    m,
    'Mid_Childhood',
    'Mid_Homicide',
    title='Childhood vs homicide mortality (overall rates)',
    subtitle=f'OECD, one country per point ({cutoff_year} cross-section)',
    xlabel=f'Under-five all-cause — {rate_unit}',
    ylabel=f'Interpersonal violence (homicide) — {rate_unit}',
    subtext=src,
    trend_line=True,
    logo=True,
    correlation_kind='level_level',
)
plt.savefig('figs/talk_corr_level_level_childhood_homicide.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
fig, ax = plot_correlation_scatter_aibm(
    m,
    'Gap_Childhood',
    'Gap_RoadTraffic',
    title='Gender gap: under-five mortality vs road injuries',
    subtitle=f'OECD, one country per point ({cutoff_year} cross-section)',
    xlabel=f'Under-five — {gap_unit}',
    ylabel=f'Road injuries — {gap_unit}',
    subtext=src,
    trend_line=True,
    logo=True,
    correlation_kind='gap_gap',
)
plt.savefig('figs/talk_corr_gap_gap_childhood_road.png', dpi=150, bbox_inches='tight')
plt.show()
```
