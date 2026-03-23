#!/usr/bin/env python3
"""
Extract leading factors (top factor + any >= half its size) from counterfactual HTML tables.
Outputs a JSON file and prints a markdown document for review.
"""
import json
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit("pip install beautifulsoup4")

# Map HTML indicator names to human-readable labels
INDICATOR_LABELS = {
    'Neoplasms': 'Cancer',
    'Cardiovascular': 'Cardiovascular',
    'Homicide': 'Homicide',
    'Suicide': 'Suicide',
    'ChronicRespiratory': 'Lung Disease',
    'RoadTraffic': 'Road Traffic',
    'LiverDisease': 'Liver Disease',
    'UnintentionalInjury': 'Injury',
    'COVID': 'COVID-19',
    'Childhood': 'Childhood',
    'Alcohol': 'Alcohol',
    'Diabetes': 'Diabetes',
    'DrugDisorder': 'Drug Disorders',
}


def label(indicator: str) -> str:
    return INDICATOR_LABELS.get(indicator, indicator.replace('_', ' '))


def parse_change(cell_text: str) -> float | None:
    """Extract mean from '−0.806 [−0.904, −0.712]' or '-0.806 [-0.904, -0.712]'."""
    # Handle minus signs (unicode and ASCII)
    text = cell_text.strip().replace('−', '-')
    match = re.match(r'^(-?\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return None


def extract_gap_closing_factors(html_path: Path) -> list[dict]:
    """Parse HTML table and return gap-closing factors (negative change) with effect in years."""
    soup = BeautifulSoup(html_path.read_text(), 'html.parser')
    rows = soup.find_all('tr')[1:]  # skip header
    factors = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 5:
            continue
        indicator = cells[0].get_text(strip=True)
        change_text = cells[4].get_text(strip=True)
        effect = parse_change(change_text)
        if effect is not None and effect < 0:
            factors.append({
                'indicator': indicator,
                'label': label(indicator),
                'effect': effect,
            })
    return sorted(factors, key=lambda x: x['effect'])  # most negative first


def leading_factors(factors: list[dict], threshold_frac: float = 0.5) -> list[dict]:
    """Top factor + any with |effect| >= threshold_frac * |top_effect|."""
    if not factors:
        return []
    top_effect = factors[0]['effect']
    threshold = abs(top_effect) * threshold_frac
    return [f for f in factors if abs(f['effect']) >= threshold]


# Regional grouping (OECD-style)
REGIONS = {
    'North America': ['USA', 'CAN'],
    'Latin America': ['CHL', 'COL', 'CRI', 'MEX'],
    'Northern Europe': ['DNK', 'FIN', 'ISL', 'NOR', 'SWE'],
    'Baltic': ['EST', 'LVA', 'LTU'],
    'Western Europe': ['AUT', 'BEL', 'CHE', 'DEU', 'FRA', 'GBR', 'IRL', 'ITA', 'LUX', 'NLD', 'PRT', 'ESP'],
    'Eastern Europe': ['CZE', 'HUN', 'POL', 'SVK', 'SVN'],
    'Southern Europe': ['GRC'],
    'Oceania': ['AUS', 'NZL'],
    'East Asia': ['JPN', 'KOR'],
    'Other': ['ISR'],
}


def main():
    tables_dir = Path('tables')
    summary_path = Path('tables/country_summary_le.json')
    with open(summary_path) as f:
        summary = json.load(f)

    all_countries = {}
    for country_code, info in summary.items():
        html_name = f'counterfactuals_{country_code.lower()}_2023_le_bayesian.html'
        html_path = tables_dir / html_name
        if not html_path.exists():
            continue
        factors = extract_gap_closing_factors(html_path)
        leading = leading_factors(factors)
        all_countries[country_code] = {
            'country_name': info['country_name'],
            'current_gap': info['current_gap'],
            'top_factor': info['top_factor_label'],
            'leading': [(f['label'], f['effect']) for f in leading],
        }

    # Save for later use
    out_path = Path('tables/leading_factors_by_country.json')
    out_data = {c: {**v, 'leading': [(l, float(e)) for l, e in v['leading']]} for c, v in all_countries.items()}
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2)
    print(f"Saved: {out_path}\n")

    # Build markdown document
    lines = [
        "# Leading Factors by Country and Region",
        "",
        "Leading factors = top factor + any other with effect ≥ half the top effect.",
        "",
    ]
    for region_name, codes in REGIONS.items():
        present = [c for c in codes if c in all_countries]
        if not present:
            continue
        lines.append(f"## {region_name}")
        lines.append("")
        lines.append("| Country | Current gap | Leading factors (effect in years) |")
        lines.append("|---------|-------------|------------------------------------|")
        for code in sorted(present, key=lambda c: -all_countries[c]['current_gap']):
            info = all_countries[code]
            leads = ', '.join(f"{l} ({e:.2f})" for l, e in info['leading'])
            lines.append(f"| {info['country_name']} | {info['current_gap']:.2f} | {leads} |")
        lines.append("")

    md_path = Path(__file__).parent.parent / 'jb' / 'leading_factors_by_region.md'
    md_path.write_text('\n'.join(lines))
    print(f"Saved: {md_path}\n")

    for line in lines:
        print(line)


if __name__ == '__main__':
    main()
