"""Make data/panel_le.csv, the input for the notebooks in this folder.

The panel is derived from IHME data, which IHME's terms don't allow us to
redistribute, so it is not in the repository. To make it, run
notebooks/process.md (see the main README), then, from this folder:

    python make_panel.py

It selects the countries and columns the January version of the model used:
37 OECD countries (Turkey excluded) and 12 causes of death.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
SOURCE = HERE / '../../notebooks/interim/panel_le.h5'
CAUSES = ['Alcohol', 'Suicide', 'Homicide', 'RoadTraffic', 'Cardiovascular', 'Diabetes',
          'Neoplasms', 'ChronicRespiratory', 'LiverDisease', 'UnintentionalInjury',
          'DrugDisorder', 'COVID']


def main():
    panel = pd.read_hdf(SOURCE)
    panel = panel[panel['country'] != 'TUR']
    columns = ['country', 'Year', 'LE_gap'] + [f'{p}_{c}' for c in CAUSES for p in ('Mid', 'Gap')]
    (HERE / 'data').mkdir(exist_ok=True)
    out = HERE / 'data' / 'panel_le.csv'
    panel[columns].to_csv(out, index=False)
    print(f'Wrote {out} ({len(panel)} rows, {panel["country"].nunique()} countries)')


if __name__ == '__main__':
    main()
