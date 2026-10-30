#!/usr/bin/env python3
"""
Render Model **4c** only (structural latents | Risk | Cause-specific death rates | LE gap).

Run from ``notebooks/`` with the LifeExpectancy env::

    cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && python render_model4c.py

Writes ``figs/dag_presentation_model4c.png`` and ``figs/dag_presentation_model4c_slides.png``
(same as the full ``presentation_dags`` notebook).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from presentation_dag_layout import render_model4_png
from presentation_dag_style import (
    ELLIPSIS_LABEL,
    LABEL_ALCOHOL,
    LABEL_LE,
    LABEL_SMOKING,
    LATENT_SPECS,
    NODE_FONT_SIZE_PTS,
    make_node,
)
from utils import gap_predictor_columns, gap_predictor_display_label

INCLUDE_COVID_DATA = True
CUTOFF_YEAR = 2023 if INCLUDE_COVID_DATA else 2019
COUNTRIES_TO_EXCLUDE = ["TUR"]
_GAP_EXCLUDE_LE_MODEL1 = frozenset({"Gap_MaternalDisorders", "Gap_ConflictTerrorism"})


def draw_model4c(predictor_cols: list[str], filename: str | Path) -> Path:
    return render_model4_png(
        predictor_cols,
        filename,
        make_node=make_node,
        gap_predictor_display_label=gap_predictor_display_label,
        ellipsis_label=ELLIPSIS_LABEL,
        label_smoking=LABEL_SMOKING,
        label_alcohol=LABEL_ALCOHOL,
        label_le=LABEL_LE,
        node_fontsize=NODE_FONT_SIZE_PTS,
        variant="4c",
        latent_specs=LATENT_SPECS,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render presentation DAG Model 4c only.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figs/dag_presentation_model4c.png"),
        help="Primary PNG path (slides copy uses <stem>_slides.png).",
    )
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    panel_path = here / "interim" / "panel_le.h5"
    panel_le = pd.read_hdf(panel_path, key="panel")
    if COUNTRIES_TO_EXCLUDE:
        panel_le = panel_le[~panel_le["country"].isin(COUNTRIES_TO_EXCLUDE)].copy()
    panel_le = panel_le[
        (panel_le["Year"] >= 2000) & (panel_le["Year"] <= CUTOFF_YEAR)
    ].copy()
    panel_le = panel_le.dropna(subset=["LE_gap"]).copy()

    _all_gap = gap_predictor_columns(panel_le)
    predictor_cols = sorted(
        (c for c in _all_gap if c not in _GAP_EXCLUDE_LE_MODEL1),
        key=str.lower,
    )

    out = args.output
    if not out.is_absolute():
        out = here / out
    out.parent.mkdir(parents=True, exist_ok=True)

    written = draw_model4c(predictor_cols, str(out))
    slides = written.with_name(f"{written.stem}_slides{written.suffix}")
    print(f"Wrote {written}")
    if slides.is_file():
        print(f"Wrote {slides}")


if __name__ == "__main__":
    main()
