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

# Presentation DAGs (pydot): Models 1, 1b, 1c, 2, 4, 4a, 4b, 4c

Stable **left-to-right** DAGs for slides and writeups, using **`gap_predictor_display_label()`** from **`utils`** for cause labels.

**Graphical grammar**

| Role | Meaning | Style |
|------|---------|--------|
| **Random factors** | Country, year (context / FE) | Gray filled **box** |
| **Measured predictors** | Observed cause gaps (`Gap_*`) | White filled **ellipse**, solid border |
| **Ellipsis** | Omitted gaps in **truncated** figures | Plain **text** only (`shape=none`; no fill, no border; no arrows to `LE_gap`) |
| **Latent factors** | Unmeasured drivers (Model 2) | Light fill **ellipse**, **dashed** border |
| **Outcome** | `LE_gap` | Blue filled **ellipse** |

**Outputs:** Full **and** truncated (first **2** + **…** + last **2** cause gaps) variants:

- Full: `dag_presentation_model1.png`, `…_model1b.png`, `…_model1c.png`
- Truncated: same names with **`_trunc`** before **`.png`** (e.g. `dag_presentation_model1_trunc.png`)
- Model **2** (single measured block): `dag_presentation_model2.png` only
- Model **4** (unmeasured smoking / alcohol → same full cause list as **4a** / **4b**, no **…**): `dag_presentation_model4.png`
- Model **4a** — left column **Risk behavior** → Smoking, Alcohol, and ``MODEL4_RISK_DIRECT_GAPS`` (road traffic, homicide, suicide, injury, drug disorders, child mortality when those gaps are in the panel), then the usual Model 4 middle and gap column: `dag_presentation_model4a.png`
- Model **4b** — Policy, Economics, Health care, and Demography in the first column; **Risk behavior** between that column and Smoking/Alcohol; each latent → **Smoking**, **Alcohol**, and the measured cause gaps (not **LE**); other LE-model gaps are drawn by name (no **…**): `dag_presentation_model4b.png`
- Model **4c** — Same latent columns as **4b** without Smoking/Alcohol: structural latents | **Risk behavior** | **Cause-specific death rates** (single measured node, like Model 2) | **LE gap**; structural → **Risk behavior**; each latent → measured block → **LE**; four evenly spaced columns: `dag_presentation_model4c.png`

The **same** drawing code runs with `truncate=False` or `True` so layouts stay aligned (Models 1–1c).

**Requires:** `pydot` and Graphviz **`dot`** on `PATH` (Models 1–1c, 2). **Model 4** uses fixed node positions rendered with **`neato -n2`** — ensure **`neato`** is on `PATH` as well. Primary Model 4-family PNGs use Graphviz’s default bitmap **dpi** (typically **96** unless you pass ``png_dpi`` to ``render_model4_png``). **4b** also writes ``dag_presentation_model4b_slides.png`` at **72** dpi by default for Google Slides (``slides_png_dpi`` / ``write_slides_png``).

If **`conda run`** hangs, use the env interpreter directly or run in Jupyter with the **LifeExpectancy** kernel.

**Model 4c only** (skip the full notebook):

```
cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && python render_model4c.py
```

**Run headlessly (all DAG figures):**

```
cd ~/LifeExpectancy/notebooks && conda activate LifeExpectancy && \
  jupytext --to ipynb presentation_dags.md --output presentation_dags.ipynb && \
  papermill presentation_dags.ipynb presentation_dags_executed.ipynb
```

Outputs: `figs/dag_presentation_model1.png`, `figs/dag_presentation_model1_trunc.png`, `figs/dag_presentation_model1b.png`, `figs/dag_presentation_model1b_trunc.png`, `figs/dag_presentation_model1c.png`, `figs/dag_presentation_model1c_trunc.png`, `figs/dag_presentation_model2.png`, `figs/dag_presentation_model4.png`, `figs/dag_presentation_model4a.png`, `figs/dag_presentation_model4b.png`, **`figs/dag_presentation_model4b_slides.png`**, **`figs/dag_presentation_model4c.png`**, **`figs/dag_presentation_model4c_slides.png`**.

```python
import pathlib

import pandas as pd
import pydot

from utils import gap_predictor_columns, gap_predictor_display_label

from presentation_dag_layout import (
    MODEL4_DISPLAY_ORDER,
    MODEL4_RISK_DIRECT_GAPS,
    MODEL4_SMOKING_GAPS,
    MODEL4_ALCOHOL_GAPS,
    model4_full_gap_sequence,
    render_model4_png,
)
from presentation_dag_style import (
    ELLIPSIS_FONT_SIZE_PTS,
    ELLIPSIS_LABEL,
    LABEL_ALCOHOL,
    LABEL_LE,
    LABEL_SMOKING,
    LATENT_SPECS,
    NODE_FONT_SIZE_PTS,
    make_node,
)

# Match causal_model.md LE panel slice + exclusions
INCLUDE_COVID_DATA = True
CUTOFF_YEAR = 2023 if INCLUDE_COVID_DATA else 2019
COUNTRIES_TO_EXCLUDE = ["TUR"]
_GAP_EXCLUDE_LE_MODEL1 = frozenset({"Gap_MaternalDisorders", "Gap_ConflictTerrorism"})

OUT_DIR = pathlib.Path("figs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Outcome / context nodes (presentation strings)
LABEL_COUNTRY = "Country"
LABEL_YEAR = "Year"
TRUNC_HEAD = 2
TRUNC_TAIL = 2

# Model 2: composite measured block (avoids 5×13 crossing edges)
LABEL_MEASURED_GAPS = "Cause-specific gaps"

# Model 4: unmeasured smoking / alcohol → measured cause gaps (IHME column names).
# Gap sets and display order live in ``presentation_dag_layout`` (fixed ``neato -n2`` layout).
# ``LABEL_*``, ``LATENT_SPECS``, ``make_node``, typography: ``presentation_dag_style``
```

```python
panel_le = pd.read_hdf("interim/panel_le.h5", key="panel")
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
predictor_cols
```

## Shared helpers

```python
def base_graph():
    g = pydot.Dot(graph_type="digraph", rankdir="LR")
    # Sans-serif; NODE_FONT_SIZE_PTS from config cell
    g.set_node_defaults(
        fontname="Helvetica",
        fontsize=str(NODE_FONT_SIZE_PTS),
    )
    g.set_edge_defaults(
        arrowsize="0.7",
        fontname="Helvetica",
        fontsize=str(NODE_FONT_SIZE_PTS),
    )
    g.set_ranksep("1.0")
    g.set_nodesep("0.45")
    g.set_splines("spline")
    g.set_outputorder("edgesfirst")
    # Helps separate rank=same groups when multiple layers feed the same sink
    g.set("newrank", "true")
    # Prefer node order matching definition / invisible chains (gap column stack)
    g.set("ordering", "out")
    return g


def add_same_rank(graph, nodes):
    """Force nodes onto one rank (same row when rankdir=LR)."""
    sg = pydot.Subgraph()
    sg.set_rank("same")
    for n in nodes:
        sg.add_node(n)
    graph.add_subgraph(sg)


def polish_edges(graph):
    for e in graph.get_edges():
        if (e.get_style() or "") == "invis":
            continue
        e.set_penwidth("1")


def apply_gap_stack_sortv(gap_nodes_in_display_order):
    """
    Set ``sortv`` on each gap node to 0, 1, … so ``dot`` keeps this order within
    the rank (used together with the invisible chain).
    """
    for i, n in enumerate(gap_nodes_in_display_order):
        n.set_sortv(str(i))


def chain_invisible_gap_order(graph, gap_nodes_in_display_order):
    """
    With ``rankdir=LR``, gap nodes sit in one rank (a vertical stack). Invisible
    edges with high weight enforce top-to-bottom order. Latent→gap edges in
    Model 4 use ``constraint=false`` so they do not override this order.
    """
    nodes = list(gap_nodes_in_display_order)
    if len(nodes) < 2:
        return
    for i in range(len(nodes) - 1):
        graph.add_edge(
            pydot.Edge(
                nodes[i],
                nodes[i + 1],
                style="invis",
                weight="1000",
            )
        )


def gap_column_sequence(
    predictor_cols,
    truncate=False,
    head=TRUNC_HEAD,
    tail=TRUNC_TAIL,
):
    """
    Return a sequence of column names, or None for an ellipsis placeholder.

    When ``truncate`` is True and there are more than ``head + tail`` predictors,
    the sequence is ``[:head] + [None] + [-tail:]``. Otherwise returns the full list.
    """
    cols = list(predictor_cols)
    n = len(cols)
    if not truncate or n <= head + tail:
        return cols
    return cols[:head] + [None] + cols[-tail:]


def pin_ellipsis_to_le_layer(graph, gap_nodes_all, le_node):
    """
    ``…`` has no *visible* arrow to ``LE_gap``; add an invisible edge so Graphviz
    keeps it in the same layer as other gap→LE parents (otherwise it floats to the wrong rank).
    """
    for n in gap_nodes_all:
        if n.get_name() == "z_gap_ellipsis":
            graph.add_edge(
                pydot.Edge(
                    n,
                    le_node,
                    style="invis",
                    weight="100",
                )
            )
            break


def add_gap_column_nodes(graph, sequence):
    """
    Add measured / ellipsis nodes for one middle column. Returns
    ``(all_nodes, real_gap_nodes)`` — only ``real_gap_nodes`` get visible edges to ``LE_gap``
    or from ``country`` (1c). Call ``pin_ellipsis_to_le_layer`` when ``…`` is present.
    """
    all_nodes = []
    real_nodes = []
    for col in sequence:
        if col is None:
            n = make_node(
                "z_gap_ellipsis",
                "ellipsis",
                label=ELLIPSIS_LABEL,
            )
            graph.add_node(n)
            all_nodes.append(n)
        else:
            n = make_node(
                col,
                "measured",
                label=gap_predictor_display_label(col),
            )
            graph.add_node(n)
            all_nodes.append(n)
            real_nodes.append(n)
    return all_nodes, real_nodes


def draw_model1(predictor_cols, filename, truncate=False):
    g = base_graph()
    seq = gap_column_sequence(predictor_cols, truncate=truncate)

    country = make_node("country", "random_factor", label=LABEL_COUNTRY)
    le = make_node("LE_gap", "outcome", label=LABEL_LE)

    g.add_node(country)
    g.add_node(le)

    gaps, gaps_real = add_gap_column_nodes(g, seq)
    apply_gap_stack_sortv(gaps)

    for node in gaps_real:
        g.add_edge(pydot.Edge(node, le))
    pin_ellipsis_to_le_layer(g, gaps, le)
    g.add_edge(pydot.Edge(country, le))

    add_same_rank(g, [country])
    add_same_rank(g, gaps)
    chain_invisible_gap_order(g, gaps)
    add_same_rank(g, [le])

    polish_edges(g)
    g.write_png(filename)
    return filename


def draw_model1b(predictor_cols, filename, truncate=False):
    """Country + year share the top rank; all Gap_* sit on the rank below (not interleaved)."""
    g = base_graph()
    seq = gap_column_sequence(predictor_cols, truncate=truncate)

    country = make_node("country", "random_factor", label=LABEL_COUNTRY)
    year = make_node("year", "random_factor", label=LABEL_YEAR)
    le = make_node("LE_gap", "outcome", label=LABEL_LE)

    g.add_node(country)
    g.add_node(year)
    g.add_node(le)

    gaps, gaps_real = add_gap_column_nodes(g, seq)
    apply_gap_stack_sortv(gaps)

    for node in gaps_real:
        g.add_edge(pydot.Edge(node, le))
    pin_ellipsis_to_le_layer(g, gaps, le)
    g.add_edge(pydot.Edge(country, le))
    g.add_edge(pydot.Edge(year, le))
    g.add_edge(
        pydot.Edge(
            country,
            year,
            style="invis",
            weight="100",
        )
    )

    add_same_rank(g, [country, year])
    add_same_rank(g, gaps)
    chain_invisible_gap_order(g, gaps)
    add_same_rank(g, [le])

    polish_edges(g)
    g.write_png(filename)
    return filename


def draw_model1c(predictor_cols, filename, truncate=False):
    g = base_graph()
    seq = gap_column_sequence(predictor_cols, truncate=truncate)

    country = make_node("country", "random_factor", label=LABEL_COUNTRY)
    le = make_node("LE_gap", "outcome", label=LABEL_LE)

    g.add_node(country)
    g.add_node(le)

    gaps, gaps_real = add_gap_column_nodes(g, seq)
    apply_gap_stack_sortv(gaps)

    for node in gaps_real:
        g.add_edge(pydot.Edge(country, node))
        g.add_edge(pydot.Edge(node, le))
    pin_ellipsis_to_le_layer(g, gaps, le)
    g.add_edge(pydot.Edge(country, le))

    add_same_rank(g, [country])
    add_same_rank(g, gaps)
    chain_invisible_gap_order(g, gaps)
    add_same_rank(g, [le])

    polish_edges(g)
    g.write_png(filename)
    return filename


def draw_model4(predictor_cols, filename):
    """
    Smoking and alcohol → measured ``Gap_*`` → ``LE_gap``. Cause column matches
    ``model4_full_gap_sequence`` (schematic stack, drug disorders / child mortality
    when applicable, then every other union-excluded cause)—no **…**. Layout and
    PNG export in ``presentation_dag_layout`` (fixed ``pos`` + ``neato -n2``).
    """
    render_model4_png(
        predictor_cols,
        filename,
        make_node=make_node,
        gap_predictor_display_label=gap_predictor_display_label,
        ellipsis_label=ELLIPSIS_LABEL,
        label_smoking=LABEL_SMOKING,
        label_alcohol=LABEL_ALCOHOL,
        label_le=LABEL_LE,
        node_fontsize=NODE_FONT_SIZE_PTS,
    )
    return filename


def draw_model4a(predictor_cols, filename, use_ellipsis=False):
    """
    **Risk behavior** (left column) → Smoking, Alcohol, and each ``Gap_*`` in
    ``MODEL4_RISK_DIRECT_GAPS`` that is drawn. Gap column: ``model4a_gap_sequence``
    (default: same full listing as Model **4**); set ``use_ellipsis=True`` to use
    **…** for other union-excluded causes.
    """
    render_model4_png(
        predictor_cols,
        filename,
        make_node=make_node,
        gap_predictor_display_label=gap_predictor_display_label,
        ellipsis_label=ELLIPSIS_LABEL,
        label_smoking=LABEL_SMOKING,
        label_alcohol=LABEL_ALCOHOL,
        label_le=LABEL_LE,
        node_fontsize=NODE_FONT_SIZE_PTS,
        variant="4a",
        model4a_ellipsis=use_ellipsis,
    )
    return filename


def draw_model4b(predictor_cols, filename):
    """
    Full ``LATENT_SPECS`` in the left column: each latent → **Smoking**, **Alcohol**,
    and every measured cause gap in the figure; gap order ``model4_full_gap_sequence``
    (same as Models **4** / **4a**).
    """
    render_model4_png(
        predictor_cols,
        filename,
        make_node=make_node,
        gap_predictor_display_label=gap_predictor_display_label,
        ellipsis_label=ELLIPSIS_LABEL,
        label_smoking=LABEL_SMOKING,
        label_alcohol=LABEL_ALCOHOL,
        label_le=LABEL_LE,
        node_fontsize=NODE_FONT_SIZE_PTS,
        variant="4b",
        latent_specs=LATENT_SPECS,
    )
    return filename


def draw_model4c(predictor_cols, filename):
    """
    **4c** — Structural latents | **Risk behavior** | **Cause-specific death rates**
    (one ``measured_block``) | **LE gap** (no Smoking/Alcohol, no per-cause ellipses).
    Structural → **Risk behavior**; each latent → measured block → **LE**.
    """
    render_model4_png(
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
    return filename


def draw_model2(filename):
    """
    Latent factors → measured cause gaps → LE_gap; country/year as random factors
    affecting latents and the outcome (and measured gaps via context).
    """
    g = base_graph()

    country = make_node("country", "random_factor", label=LABEL_COUNTRY)
    year = make_node("year", "random_factor", label=LABEL_YEAR)
    measured = make_node("measured_gaps", "measured_block", label=LABEL_MEASURED_GAPS)
    le = make_node("LE_gap", "outcome", label=LABEL_LE)

    latents = []
    for node_id, lab in LATENT_SPECS:
        latents.append(make_node(node_id, "latent", label=lab))

    for n in [country, year, measured, le, *latents]:
        g.add_node(n)

    for L in latents:
        g.add_edge(pydot.Edge(L, measured))
        g.add_edge(pydot.Edge(country, L))
        g.add_edge(pydot.Edge(year, L))

    g.add_edge(pydot.Edge(measured, le))
    g.add_edge(pydot.Edge(country, le))
    g.add_edge(pydot.Edge(year, le))
    g.add_edge(pydot.Edge(country, measured))
    g.add_edge(pydot.Edge(year, measured))

    g.add_edge(
        pydot.Edge(
            country,
            year,
            style="invis",
            weight="100",
        )
    )

    add_same_rank(g, [country, year])
    add_same_rank(g, latents)
    add_same_rank(g, [measured])
    add_same_rank(g, [le])

    polish_edges(g)
    g.write_png(filename)
    return filename
```

## Render

```python
written = []
for trunc, suffix in ((False, ""), (True, "_trunc")):
    draw_model1(predictor_cols, str(OUT_DIR / f"dag_presentation_model1{suffix}.png"), truncate=trunc)
    draw_model1b(predictor_cols, str(OUT_DIR / f"dag_presentation_model1b{suffix}.png"), truncate=trunc)
    draw_model1c(predictor_cols, str(OUT_DIR / f"dag_presentation_model1c{suffix}.png"), truncate=trunc)

p2 = OUT_DIR / "dag_presentation_model2.png"
draw_model2(str(p2))

p4 = OUT_DIR / "dag_presentation_model4.png"
draw_model4(predictor_cols, str(p4))

p4a = OUT_DIR / "dag_presentation_model4a.png"
draw_model4a(predictor_cols, str(p4a))

p4b = OUT_DIR / "dag_presentation_model4b.png"
draw_model4b(predictor_cols, str(p4b))

p4c = OUT_DIR / "dag_presentation_model4c.png"
draw_model4c(predictor_cols, str(p4c))

for path in sorted(OUT_DIR.glob("dag_presentation_model*.png")):
    written.append(path.resolve())
print("Wrote:\n", "\n ".join(str(p) for p in written))
```

Labels for measured gaps come from **`GAP_PREDICTOR_DISPLAY_LABELS`** via **`gap_predictor_display_label`**. Example:

```python
{col: gap_predictor_display_label(col) for col in predictor_cols}
```

**Model 2** uses one **measured** summary node so the figure stays readable; latent → individual `Gap_*` edges would be **5×13** and are omitted by design.

**Model 4** is a **schematic**: **Smoking** and **Alcohol** drive the same gap subsets as before (`MODEL4_*_GAPS` in `presentation_dag_layout`). The gap column lists **every** cause included in Models **4a** / **4b** for the panel (`model4_full_gap_sequence`): schematic order from **`MODEL4_DISPLAY_ORDER`**, then **drug disorders** and **child mortality** when they apply, then any other union-excluded `Gap_*` sorted alphabetically—**no** **…**. Slide-style labels via `MODEL4_GAP_PRESENTATION_LABELS`.

**Model 4a** adds a left column with **Risk behavior** only, with the same gap column as Model **4** by default (`model4a_gap_sequence` with `ellipsis=False`). Pass **`use_ellipsis=True`** to **`draw_model4a`** to collapse remaining union-excluded causes to **…** (older behavior). Arrows: Risk → **Smoking**, **Alcohol**, and each drawn gap in **`MODEL4_RISK_DIRECT_GAPS`**.

**Model 4b** places Policy, Economics, Health care, and Demography in the **first** column, **Risk behavior** between that block and Smoking/Alcohol, then the usual gap and **LE** columns on a wider canvas. **Each** latent has arrows to **Smoking**, **Alcohol**, and **each measured cause gap** (no direct latent → **LE**). Vertical spacing between stacked causes is **~10%** tighter than Models 4 / 4a; a **72** dpi ``*_slides.png`` sibling is written next to the full **4b** PNG for Slides.

**Model 4c** removes the Smoking/Alcohol column and lists **one** measured node in the third column (**Cause-specific death rates**, same role as Model 2’s block): structural latents | **Risk behavior** | that block | **LE gap**. Arrows: structural → **Risk behavior**; each latent → block → **LE**. Column centers are evenly spaced (wider canvas than earlier **4c** drafts). ``label_cause_column`` overrides the block label if set. Also writes ``dag_presentation_model4c_slides.png`` at **72** dpi.
