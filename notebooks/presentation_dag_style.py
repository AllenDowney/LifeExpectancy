"""
Shared Graphviz node styles and ``make_node`` for presentation DAGs.

Used by ``presentation_dags.md`` and ``render_model4c.py`` so Model **4c** can be
regenerated without running the full notebook.
"""

from __future__ import annotations

import pydot

NODE_FONT_SIZE_PTS = 22
ELLIPSIS_FONT_SIZE_PTS = NODE_FONT_SIZE_PTS * 2
ELLIPSIS_LABEL = "\u2026"

# Model 2 / 4b / 4c latent factor labels (conceptual)
LATENT_SPECS = [
    ("latent_policy", "Policy"),
    ("latent_economics", "Economics"),
    ("latent_healthcare", "Health care"),
    ("latent_demography", "Demography"),
    ("latent_risk", "Risk behavior"),
]

LABEL_SMOKING = "Smoking"
LABEL_ALCOHOL = "Alcohol"
LABEL_LE = "LE gap"


def make_node(name: str, role: str, label: str | None = None) -> pydot.Node:
    """
    Roles:
      random_factor — country / year (gray box)
      measured      — observed Gap_* (white ellipse)
      ellipsis      — “…” placeholder: plain text only (no box; no edges to LE)
      latent        — unmeasured factor (dashed ellipse, warm fill)
      measured_block— single summary node for measured gaps (Model 2 / 4c)
      outcome       — LE_gap (blue ellipse)
      column_title  — optional light rounded box
    """
    styles = {
        "random_factor": dict(
            shape="box",
            style="filled",
            fillcolor="#d8d8d8",
            color="#555555",
        ),
        "measured": dict(
            shape="ellipse",
            style="filled",
            fillcolor="#ffffff",
            color="#333333",
        ),
        "ellipsis": dict(
            shape="none",
            margin="0.06,0.04",
            fontcolor="#444444",
        ),
        "latent": dict(
            shape="ellipse",
            style="filled,dashed",
            fillcolor="#f5e6c8",
            color="#8b6914",
        ),
        "measured_block": dict(
            shape="ellipse",
            style="filled",
            fillcolor="#ffffff",
            color="#333333",
            penwidth="1.2",
        ),
        "outcome": dict(
            shape="ellipse",
            style="filled",
            fillcolor="#cce5ff",
            color="#1a5fb4",
        ),
        "column_title": dict(
            shape="box",
            style="rounded,filled",
            fillcolor="#eeeeee",
            color="#888888",
            fontsize="18",
        ),
    }
    kw = dict(styles[role])
    if label is not None:
        kw["label"] = label
    if role == "ellipsis":
        kw["fontsize"] = str(ELLIPSIS_FONT_SIZE_PTS)
    return pydot.Node(name, **kw)
