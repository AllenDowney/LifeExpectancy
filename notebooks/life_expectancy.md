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

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import decorate, configure_plot_style, AIBM_COLORS

configure_plot_style()
```

## Our World In Data

https://ourworldindata.org/why-do-women-live-longer-than-men

```python
import requests

filename = '../life-expectancy-of-women-vs-life-expectancy-of-men.csv'
```

```python
owid = pd.read_csv(filename)
owid.columns = ['Entity', 'Code', 'Year',
       'life_expectancy_female',
       'life_expectancy_male',
       'population',
       'region', 'time', 'time.1']
owid.index = owid['Code']
```

```python
owid.head()
```

```python
from utils import save_indicators
save_indicators(df_oecd, 'life_expectancy')
```

```python
from utils import plot_indicators, add_title

plot_indicators(df_oecd)
plt.xlabel('Healthy Life Expectancy (years)')
add_title("Women Live Longer In Most OECD Countries",
          "Healthy Life Expectancy", y=1.01)
```

```python
df_oecd['diff'] = df_oecd['female'] - df_oecd['male']
df_oecd.sort_values(by='diff').tail()
```

```python
plot_indicators(df_oecd.sort_values(by='diff', ascending=False), sort=False)
plt.xlabel('Healthy Life Expectancy (years)')
add_title("Women Live Longer In Most OECD Countries",
          "Healthy Life Expectancy", y=1.01)
```

```python
df_oecd.query("country == 'South Korea'")
```

```python
df_oecd.query("country == 'United States'")
```

```python
df_oecd.query("country == 'Lithuania'")
```

```python
df_oecd.query("country == 'Netherlands'")
```

```python
codes = ['NLD', 'LTU', 'USA']
cols = ['country', 'male', 'female', 'ratio', 'score', 'revised_score']
df_oecd.loc[codes, cols].round(3)
```

```python
from utils import save_revised_scores
save_revised_scores(df_oecd, 'life_expectancy')
```

```python
from utils import add_title, add_subtext, add_logo

plot_revised_scores(df_oecd)

add_title("Untruncated Life Expectancy Looks Totally Different",
    "Health life expectancy ratios compared to parity", y=1.02
)
decorate(xlabel='Healthy Life Expectancy Ratio')
add_subtext("Source: WEF, WHO", y=-0.05)
logo = add_logo(location=(1.0, -0.05))
```

```python
import seaborn as sns

options = dict(cut=0, bw_adjust=0.7)

sns.kdeplot(wef['score'], label='WEF truncated scores', **options)
sns.kdeplot(wef['revised_score'], label='Revised symmetric scores', **options)

decorate(xlabel='Gender equality score')

add_title("The Distribution of Scores Is Different",
          "Healthy life expectancy")
add_subtext("Source: World Economic Forum", y=-0.25)
logo = add_logo(location=(1.0, -0.25))
None
```

```python

```

```python

```

```python

```
