#!/usr/bin/env python
"""
Read country_summary_le.json and print a summary table.

Run from notebooks/: python summarize_countries.py
"""

import json
from pathlib import Path

SUMMARY_PATH = Path('tables/country_summary_le.json')


def main():
    if not SUMMARY_PATH.exists():
        print(f"File not found: {SUMMARY_PATH}")
        return

    with open(SUMMARY_PATH) as f:
        summary = json.load(f)

    # Build table rows sorted by current_gap descending
    rows = []
    for code, data in summary.items():
        rows.append({
            'Country': data['country_name'],
            'Code': code,
            'Current gap': data['current_gap'],
            'Top factor': data['top_factor_label'],
            'Top effect (yr)': data['top_effect'],
            'Total gap-reducing': data['total_gap_reducing'],
            '% of gap': data['pct_of_gap'],
        })
    rows.sort(key=lambda r: r['Current gap'], reverse=True)

    # Print markdown table
    print("| Country | Current gap | Top factor | Top effect (yr) | Total gap-reducing | % of gap |")
    print("|---------|------------|------------|-----------------|--------------------|----------|")
    for r in rows:
        print(f"| {r['Country']} | {r['Current gap']:.2f} | {r['Top factor']} | {r['Top effect (yr)']:.2f} | "
              f"{r['Total gap-reducing']:.2f} | {r['% of gap']:.1f}% |")

    # Also write HTML
    html_path = Path('tables/country_summary_le.html')
    with open(html_path, 'w') as f:
        f.write("<table>\n")
        f.write("  <thead><tr><th>Country</th><th>Current gap</th><th>Top factor</th>"
                "<th>Top effect (yr)</th><th>Total gap-reducing</th><th>% of gap</th></tr></thead>\n")
        f.write("  <tbody>\n")
        for r in rows:
            f.write(f"    <tr><td>{r['Country']}</td><td>{r['Current gap']:.2f}</td>"
                    f"<td>{r['Top factor']}</td><td>{r['Top effect (yr)']:.2f}</td>"
                    f"<td>{r['Total gap-reducing']:.2f}</td><td>{r['% of gap']:.1f}%</td></tr>\n")
        f.write("  </tbody>\n</table>\n")
    print(f"\nWrote {html_path}")


if __name__ == '__main__':
    main()
