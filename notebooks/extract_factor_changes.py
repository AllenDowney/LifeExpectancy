#!/usr/bin/env python3
"""
Extract contribution change (2000 vs 2023) for a specified cause from positive_contributions
HTML tables. Outputs CSV and markdown.

Usage:
  python extract_factor_changes.py                         # default: RoadTraffic, europe
  python extract_factor_changes.py --cause Suicide --scope all
  python extract_factor_changes.py --cause DrugDisorder --scope all
"""
import argparse
import csv
import json
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit("pip install beautifulsoup4")

EUROPEAN_COUNTRIES = [
    'AUT', 'BEL', 'CHE', 'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA',
    'GBR', 'GRC', 'HUN', 'IRL', 'ISL', 'ITA', 'LUX', 'LTU', 'LVA', 'NLD',
    'NOR', 'POL', 'PRT', 'SVK', 'SVN', 'SWE',
]

# Map HTML column names to labels used in contribution_changes JSON
COLUMN_TO_LABEL = {
    'RoadTraffic': 'Road Traffic',
    'Suicide': 'Suicide',
    'DrugDisorder': 'Drug Disorders',
    'Neoplasms': 'Cancer',
    'Homicide': 'Homicide',
    'ChronicRespiratory': 'Lung Disease',
    'LiverDisease': 'Liver Disease',
    'UnintentionalInjury': 'Injury',
    'Childhood': 'Childhood',
    'Alcohol': 'Alcohol',
    'Cardiovascular': 'Cardiovascular',
    'Diabetes': 'Diabetes',
}


def extract_factor_change(
    html_path: Path,
    factor_col: str,
    year_start: int = 2000,
    year_end: int = 2023,
) -> dict | None:
    """
    Parse positive_contributions HTML and return factor values for start/end years.
    Returns {'val_2000': float, 'val_2023': float, 'change': float} or None if not found.
    """
    soup = BeautifulSoup(html_path.read_text(), 'html.parser')
    table = soup.find('table')
    if not table:
        return None

    thead = table.find('thead')
    if not thead:
        return None
    headers = [th.get_text(strip=True) for th in thead.find_all('th')]
    if factor_col not in headers:
        return None
    col_idx = headers.index(factor_col)

    tbody = table.find('tbody')
    if not tbody:
        return None
    rows = tbody.find_all('tr')
    if len(rows) < 24:
        return None

    def parse_val(cell) -> float | None:
        text = cell.get_text(strip=True)
        try:
            return float(text)
        except ValueError:
            return None

    row_start = year_start - 2000
    row_end = year_end - 2000
    if row_end >= len(rows):
        row_end = len(rows) - 1

    cells_start = rows[row_start].find_all('td')
    cells_end = rows[row_end].find_all('td')
    if col_idx >= len(cells_start) or col_idx >= len(cells_end):
        return None

    val_start = parse_val(cells_start[col_idx])
    val_end = parse_val(cells_end[col_idx])
    if val_start is None or val_end is None:
        return None

    return {
        'val_2000': val_start,
        'val_2023': val_end,
        'change': val_end - val_start,
    }


def get_country_code_from_path(path: Path) -> str:
    """Extract country code from positive_contributions_XXX_le_over_time.html"""
    m = re.search(r'positive_contributions_([a-z]{3})_le_over_time', path.name)
    return m.group(1).upper() if m else ''


def get_cause_slug(cause: str) -> str:
    """Convert column name to slug for filenames (e.g. RoadTraffic -> road_traffic)."""
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', cause).lower()


def main():
    parser = argparse.ArgumentParser(description='Extract contribution change for a cause (2000 vs 2023)')
    parser.add_argument('--cause', default='RoadTraffic',
                        help='Column name in contributions table (e.g. RoadTraffic, Suicide, DrugDisorder)')
    parser.add_argument('--scope', choices=['europe', 'all'], default='europe',
                        help='europe: European OECD countries only; all: all countries with data')
    parser.add_argument('--substantial-threshold', type=float, default=0.2,
                        help='|change| >= this (years) is "substantial"; used for scope=all markdown sections')
    args = parser.parse_args()

    tables_dir = Path(__file__).parent / 'tables'
    changes_path = tables_dir / 'contribution_changes_2000_2023_le.json'
    with open(changes_path) as f:
        changes_data = json.load(f)

    cause_slug = get_cause_slug(args.cause)
    label = COLUMN_TO_LABEL.get(args.cause, args.cause.replace('_', ' '))

    if args.scope == 'europe':
        country_codes = EUROPEAN_COUNTRIES
        html_paths = [(tables_dir / f'positive_contributions_{c.lower()}_le_over_time.html', c)
                      for c in country_codes]
    else:
        html_files = sorted(tables_dir.glob('positive_contributions_*_le_over_time.html'))
        html_paths = [(p, get_country_code_from_path(p)) for p in html_files]

    results = []
    for html_path, code in html_paths:
        if not html_path.exists() or not code:
            continue
        out = extract_factor_change(html_path, args.cause)
        if out is None:
            continue
        country_name = changes_data.get(code, {}).get('Country', code)
        rec = changes_data.get(code, {})
        is_largest_decrease = rec.get('Largest decrease') == label
        is_largest_increase = rec.get('Largest increase') == label
        change = out['change']
        substantial = abs(change) >= args.substantial_threshold

        results.append({
            'code': code,
            'country': country_name,
            'val_2000': out['val_2000'],
            'val_2023': out['val_2023'],
            'change': change,
            'is_largest_decrease': is_largest_decrease,
            'is_largest_increase': is_largest_increase,
            'substantial': substantial,
        })

    results.sort(key=lambda x: x['change'])

    out_suffix = 'europe' if args.scope == 'europe' else 'all'
    csv_path = tables_dir / f'{cause_slug}_gap_change_{out_suffix}.csv'
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['code', 'country', 'val_2000', 'val_2023', 'change',
                    'is_largest_decrease', 'is_largest_increase', 'substantial'])
        for r in results:
            w.writerow([r['code'], r['country'], r['val_2000'], r['val_2023'], r['change'],
                        r['is_largest_decrease'], r['is_largest_increase'], r['substantial']])
    print(f"Saved: {csv_path}")

    md_path = Path(__file__).parent.parent / 'jb' / f'{cause_slug}_gap_change_{out_suffix}.md'

    if args.scope == 'all':
        substantial_increase = [r for r in results if r['substantial'] and r['change'] > 0]
        substantial_decrease = [r for r in results if r['substantial'] and r['change'] < 0]

        lines = [
            f"# Change in Life Expectancy Gender Gap Due to {label} (2000–2023)",
            "",
            f"For each country, the change in the {label.lower()}-contribution to the life expectancy",
            "gender gap between 2000 and 2023. Positive = now explains more of the gap;",
            "negative = now explains less.",
            "",
            f"**Substantial change** = |change| ≥ {args.substantial_threshold} years.",
            "",
            "## Substantial Increases",
            "",
            "| Country | 2000 (yr) | 2023 (yr) | Change (yr) |",
            "|---------|----------|----------|-------------|",
        ]
        for r in reversed(substantial_increase):
            lines.append(f"| {r['country']} | {r['val_2000']:.3f} | {r['val_2023']:.3f} | {r['change']:+.3f} |")
        if not substantial_increase:
            lines.append("| *(none)* | | | |")

        lines.extend([
            "",
            "## Substantial Decreases",
            "",
            "| Country | 2000 (yr) | 2023 (yr) | Change (yr) |",
            "|---------|----------|----------|-------------|",
        ])
        for r in substantial_decrease:
            lines.append(f"| {r['country']} | {r['val_2000']:.3f} | {r['val_2023']:.3f} | {r['change']:+.3f} |")
        if not substantial_decrease:
            lines.append("| *(none)* | | | |")

        lines.extend([
            "",
            "## All Countries (sorted by change)",
            "",
            "| Country | 2000 (yr) | 2023 (yr) | Change (yr) | Substantial? |",
            "|---------|----------|----------|-------------|--------------|",
        ])
        for r in results:
            flag = "†" if r['substantial'] else ""
            lines.append(f"| {r['country']} | {r['val_2000']:.3f} | {r['val_2023']:.3f} | {r['change']:+.3f} | {flag} |")
    else:
        lines = [
            f"# Change in Life Expectancy Gender Gap Due to {label} (2000–2023)",
            "",
            f"For each European country, the change in the {label.lower()}-contribution between 2000 and 2023.",
            "Negative = now explains less of the gap; positive = now explains more.",
            "",
            f"**†** = {label} was the factor with the *largest* decrease in contribution.",
            "",
            "| Country | 2000 (yr) | 2023 (yr) | Change (yr) | Largest? |",
            "|---------|----------|----------|-------------|----------|",
        ]
        for r in results:
            flag = "†" if r['is_largest_decrease'] else ""
            lines.append(
                f"| {r['country']} | {r['val_2000']:.3f} | {r['val_2023']:.3f} | {r['change']:+.3f} | {flag} |"
            )

    lines.append("")
    md_path.write_text("\n".join(lines))
    print(f"Saved: {md_path}")

    n_largest = sum(1 for r in results if r['is_largest_decrease'])
    if args.scope == 'all':
        n_inc = sum(1 for r in results if r['substantial'] and r['change'] > 0)
        n_dec = sum(1 for r in results if r['substantial'] and r['change'] < 0)
        print(f"\n{len(results)} countries. Substantial increases: {n_inc}, substantial decreases: {n_dec}")
    else:
        print(f"\n{len(results)} European countries. {label} was largest decrease in {n_largest} of them.")


if __name__ == '__main__':
    main()
