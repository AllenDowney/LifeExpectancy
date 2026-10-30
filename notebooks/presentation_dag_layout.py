"""
Fixed-position layout and ``neato -n2`` rendering for presentation DAG Model 4 family.

Models 1–1c and 2 continue to use ``dot`` via pydot in ``presentation_dags``; Model 4
uses explicit ``pos`` attributes (points) and Graphviz ``neato -n2`` so the gap stack
order stays stable without rank/same hacks.

Variants **4a** / **4b** add latent factors before Smoking / Alcohol:
**4a** — **Risk behavior** only (left column), with arrows to Smoking, Alcohol, and
``MODEL4_RISK_DIRECT_GAPS`` (including drug disorders and child mortality when shown);
**4b** — Policy, Economics, Health care, and Demography in
the first column, **Risk behavior** between that column and Smoking/Alcohol, then gaps
and LE on a wider canvas.

**4c** — Simplified **4b**: structural latents | **Risk behavior** | one **measured**
node (**Cause-specific death rates**) | **LE gap** — no Smoking/Alcohol column and
no per-cause nodes. Structural latents → **Risk behavior**; each latent → measured
block; block → **LE**. Four columns use uniform horizontal spacing.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Literal, Sequence

import pydot

MODEL4_SMOKING_GAPS = (
    "Gap_Neoplasms",
    "Gap_ChronicRespiratory",
    "Gap_Cardiovascular",
)
MODEL4_ALCOHOL_GAPS = (
    "Gap_LiverDisease",
    "Gap_Neoplasms",
    "Gap_RoadTraffic",
    "Gap_Homicide",
    "Gap_Suicide",
    "Gap_UnintentionalInjury",
)
MODEL4_DISPLAY_ORDER = (
    "Gap_Cardiovascular",
    "Gap_ChronicRespiratory",
    "Gap_Neoplasms",
    "Gap_LiverDisease",
    "Gap_RoadTraffic",
    "Gap_Homicide",
    "Gap_Suicide",
    "Gap_UnintentionalInjury",
)

# Gaps that receive a direct edge from **Risk behavior** in **4a** via
# ``_edges_risk_behavior`` (and the same targets whenever those nodes exist). Not used
# for **4b**, where every latent already points at every measured gap.
MODEL4_RISK_DIRECT_GAPS = (
    "Gap_RoadTraffic",
    "Gap_Homicide",
    "Gap_Suicide",
    "Gap_UnintentionalInjury",
    "Gap_DrugDisorder",
    "Gap_Childhood",
)

# In **4a**, drawn after the schematic stack (when in ``predictor_cols``), before **…**.
MODEL4A_EXTRA_GAP_ORDER = (
    "Gap_DrugDisorder",
    "Gap_Childhood",
)

# Slide-style labels for Model 4 nodes (same strings as ``fig_utils.PREDICTOR_LABELS``).
MODEL4_GAP_PRESENTATION_LABELS = {
    "Gap_Cardiovascular": "Cardiovascular",
    "Gap_ChronicRespiratory": "Lung Disease",
    "Gap_Neoplasms": "Cancer",
    "Gap_RoadTraffic": "Road Traffic",
    "Gap_Homicide": "Homicide",
    "Gap_Suicide": "Suicide",
    "Gap_UnintentionalInjury": "Injury",
    "Gap_LiverDisease": "Liver Disease",
    "Gap_DrugDisorder": "Drug disorders",
    "Gap_Childhood": "Child mortality",
}

# Graphviz points (neato -n2 honors these; y increases upward)
# Model 4 (no left column): smoking/alcohol | gaps | LE
_X4_SA = 0.0
_X4_GAPS = 275.0
_X4_LE = 650.0

# Model 4a: drivers | smoking/alcohol | gaps | LE
_XEXT_LEFT = 0.0
_XEXT_SA = 275.0
_XEXT_GAPS = 550.0
_XEXT_LE = 925.0

# Model 4b: four latents | risk behavior | smoking/alcohol | gaps | LE (wide canvas)
_X4B_LEFT = 0.0
_X4B_RISK = 255.0
_X4B_SA = 510.0
_X4B_GAPS = 810.0
_X4B_LE = 1240.0

# Model 4c: four columns evenly spaced (equal Δx); Δ ≈ 1.25× prior mean inter-column gap
_X4C_COL_STEP = 375.0
_X4C_LEFT = 0.0
_X4C_RISK = _X4C_COL_STEP
_X4C_GAPS = 2.0 * _X4C_COL_STEP
_X4C_LE = 3.0 * _X4C_COL_STEP

_Y_CENTER = 420.0
_GAP_Y_SPACING = 92.0
_LATENT_DY = 116.0
# Vertical spacing for structural latents in the left column (4b)
_LATENT_LEFT_COL_SPACING = 76.0
# Tighter vertical stacking in 4b (many causes / Google Slides)
_4B_VERTICAL_TIGHTEN = 0.9

# PNG rasterization: if ``None``, ``neato`` uses Graphviz’s default ``dpi`` (typically 96).
SLIDE_FRIENDLY_PNG_DPI = 72.0


def model4_gap_sequence(
    predictor_cols: Sequence[str],
    *,
    rest_as: Literal["ellipsis", "list"] = "ellipsis",
) -> list[str | None]:
    """
    Named gaps in ``MODEL4_DISPLAY_ORDER`` (subset of predictors). If other measured
    gaps remain in the LE model (not in the smoking ∪ alcohol schematic union):

    - ``rest_as="ellipsis"`` (default): append ``None`` (ellipsis placeholder).
    - ``rest_as="list"``: append those ``Gap_*`` columns, sorted case-insensitively
      (used for **4b** so every remaining cause is drawn).
    """
    union = set(MODEL4_SMOKING_GAPS) | set(MODEL4_ALCOHOL_GAPS)
    seq = [c for c in MODEL4_DISPLAY_ORDER if c in predictor_cols]
    rest = [c for c in predictor_cols if c not in union]
    if not rest:
        return seq
    if rest_as == "ellipsis":
        return [*seq, None]
    return [*seq, *sorted(rest, key=str.lower)]


def model4_full_gap_sequence(predictor_cols: Sequence[str]) -> list[str]:
    """
    Full gap column for Model **4** (and **4a** without ellipsis): same ordering as **4a**
    (schematic stack, then drug disorders and child mortality when they belong in
    ``rest``), then every other ``Gap_*`` in ``rest`` sorted case-insensitively. No
    placeholder nodes.
    """
    union = set(MODEL4_SMOKING_GAPS) | set(MODEL4_ALCOHOL_GAPS)
    pred = set(predictor_cols)
    seq = [c for c in MODEL4_DISPLAY_ORDER if c in pred]
    rest = [c for c in predictor_cols if c not in union]
    extras = [c for c in MODEL4A_EXTRA_GAP_ORDER if c in pred and c in rest]
    rest_other = [c for c in rest if c not in extras]
    out: list[str] = [*seq]
    seen = set(seq)
    for c in extras:
        if c not in seen:
            out.append(c)
            seen.add(c)
    for c in sorted(rest_other, key=str.lower):
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out


def model4a_gap_sequence(
    predictor_cols: Sequence[str],
    *,
    ellipsis: bool = False,
) -> list[str | None]:
    """
    Column order for **4a**. If ``ellipsis`` is **False** (default), same nodes as
    ``model4_full_gap_sequence``. If **True**, append **…** when ``rest_other`` is
    non-empty (other union-excluded causes not drawn by name).
    """
    if not ellipsis:
        return model4_full_gap_sequence(predictor_cols)
    union = set(MODEL4_SMOKING_GAPS) | set(MODEL4_ALCOHOL_GAPS)
    pred = set(predictor_cols)
    seq = [c for c in MODEL4_DISPLAY_ORDER if c in pred]
    rest = [c for c in predictor_cols if c not in union]
    extras = [c for c in MODEL4A_EXTRA_GAP_ORDER if c in pred and c in rest]
    rest_other = [c for c in rest if c not in extras]
    out: list[str | None] = [*seq]
    seen = set(seq)
    for c in extras:
        if c not in seen:
            out.append(c)
            seen.add(c)
    if rest_other:
        out.append(None)
    return out


def model4_measured_label(
    col: str,
    fallback: Callable[[str], str],
) -> str:
    """Presentation label for a Model 4 ``Gap_*`` column; ``fallback`` for unknown names."""
    if col in MODEL4_GAP_PRESENTATION_LABELS:
        return MODEL4_GAP_PRESENTATION_LABELS[col]
    return fallback(col)


def _stack_y_positions(n: int, y_center: float, spacing: float) -> list[float]:
    if n <= 0:
        return []
    half = (n - 1) / 2 * spacing
    return [y_center + half - i * spacing for i in range(n)]


def set_fixed_pos(node: pydot.Node, x: float, y: float) -> None:
    node.set_pos(f"{x},{y}!")


def _base_graph_neato(node_fontsize: int) -> pydot.Dot:
    g = pydot.Dot(graph_type="digraph")
    g.set("overlap", "false")
    g.set_margin("0.15")
    g.set_node_defaults(
        fontname="Helvetica",
        fontsize=str(node_fontsize),
    )
    g.set_edge_defaults(
        arrowsize="0.7",
        fontname="Helvetica",
        fontsize=str(node_fontsize),
    )
    g.set_splines("spline")
    return g


def _polish_edges(graph: pydot.Dot) -> None:
    for e in graph.get_edges():
        if (e.get_style() or "") == "invis":
            continue
        e.set_penwidth("1")


def write_png_neato_n2(
    graph: pydot.Dot,
    path: str | Path,
    dpi: float | None = None,
) -> None:
    """
    Write ``graph`` to PNG using ``neato -n2`` (fixed positions, no re-layout).

    ``dpi`` is passed as ``-Gdpi=…`` to Graphviz. If omitted, the library default
    applies (commonly **96** dpi for PNG bitmap output—same effective size in points,
    pixel dimensions scale with dpi).
    """
    path = Path(path)
    cmd = ["neato", "-n2"]
    if dpi is not None:
        cmd.append(f"-Gdpi={float(dpi)}")
    cmd.extend(["-Tpng", "-o", str(path)])
    subprocess.run(
        cmd,
        input=graph.to_string(),
        text=True,
        check=True,
        capture_output=True,
    )


def _add_model4_column_nodes(
    graph: pydot.Dot,
    sequence: Sequence[str | None],
    make_node: Callable[..., pydot.Node],
    gap_predictor_display_label: Callable[[str], str],
    ellipsis_label: str,
) -> tuple[list[pydot.Node], list[pydot.Node]]:
    all_nodes: list[pydot.Node] = []
    real_nodes: list[pydot.Node] = []
    for col in sequence:
        if col is None:
            n = make_node("z_gap_ellipsis", "ellipsis", label=ellipsis_label)
            graph.add_node(n)
            all_nodes.append(n)
        else:
            lab = model4_measured_label(col, gap_predictor_display_label)
            n = make_node(col, "measured", label=lab)
            graph.add_node(n)
            all_nodes.append(n)
            real_nodes.append(n)
    return all_nodes, real_nodes


def _pin_ellipsis_to_le_layer(
    graph: pydot.Dot,
    gap_nodes_all: Sequence[pydot.Node],
    le_node: pydot.Node,
) -> None:
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


def _edges_smoking_alcohol_gaps(
    g: pydot.Dot,
    smoking: pydot.Node,
    alcohol: pydot.Node,
    name_to_node: dict[str, pydot.Node],
) -> None:
    for col in MODEL4_SMOKING_GAPS:
        if col in name_to_node:
            g.add_edge(pydot.Edge(smoking, name_to_node[col]))
    for col in MODEL4_ALCOHOL_GAPS:
        if col in name_to_node:
            g.add_edge(pydot.Edge(alcohol, name_to_node[col]))


def _edges_risk_behavior(
    g: pydot.Dot,
    risk: pydot.Node,
    smoking: pydot.Node,
    alcohol: pydot.Node,
    name_to_node: dict[str, pydot.Node],
) -> None:
    """
    **4a:** Risk → Smoking, Alcohol, and each drawn gap in ``MODEL4_RISK_DIRECT_GAPS``
    (road traffic, homicide, suicide, injury, drug disorders, child mortality).
    """
    g.add_edge(pydot.Edge(risk, smoking))
    g.add_edge(pydot.Edge(risk, alcohol))
    for col in MODEL4_RISK_DIRECT_GAPS:
        if col in name_to_node:
            g.add_edge(pydot.Edge(risk, name_to_node[col]))


def _edges_latents_to_smoking_alcohol_and_gaps(
    g: pydot.Dot,
    left_nodes: dict[str, pydot.Node],
    latent_specs: Sequence[tuple[str, str]],
    smoking: pydot.Node,
    alcohol: pydot.Node,
    name_to_node: dict[str, pydot.Node],
) -> None:
    """Each left-column latent → Smoking, Alcohol, and each measured cause gap."""
    for node_id, _lab in latent_specs:
        L = left_nodes[node_id]
        g.add_edge(pydot.Edge(L, smoking))
        g.add_edge(pydot.Edge(L, alcohol))
        for _col, gap_node in name_to_node.items():
            g.add_edge(pydot.Edge(L, gap_node))


def _edges_structural_to_risk(
    g: pydot.Dot,
    left_nodes: dict[str, pydot.Node],
    non_risk_specs: Sequence[tuple[str, str]],
    risk_node: pydot.Node,
) -> None:
    """Policy, Economics, Health care, Demography → Risk behavior (**4c**)."""
    for node_id, _lab in non_risk_specs:
        g.add_edge(pydot.Edge(left_nodes[node_id], risk_node))


def _edges_latents_to_measured_block(
    g: pydot.Dot,
    left_nodes: dict[str, pydot.Node],
    latent_specs: Sequence[tuple[str, str]],
    measured_block: pydot.Node,
) -> None:
    """Each latent (structural + risk) → single measured block (**4c**)."""
    for node_id, _lab in latent_specs:
        L = left_nodes[node_id]
        g.add_edge(pydot.Edge(L, measured_block))


def render_model4_png(
    predictor_cols: Sequence[str],
    out_path: str | Path,
    *,
    make_node: Callable[..., pydot.Node],
    gap_predictor_display_label: Callable[[str], str],
    ellipsis_label: str,
    label_smoking: str,
    label_alcohol: str,
    label_le: str,
    node_fontsize: int = 22,
    variant: Literal["4", "4a", "4b", "4c"] = "4",
    latent_specs: Sequence[tuple[str, str]] | None = None,
    png_dpi: float | None = None,
    write_slides_png: bool = True,
    slides_png_dpi: float = 72.0,
    model4a_ellipsis: bool = False,
    label_cause_column: str | None = None,
) -> Path:
    """
    Build Model 4 (or **4a** / **4b** / **4c**) with fixed node positions and ``neato -n2 -Tpng``.

    **4** — Smoking / Alcohol | gaps | LE; gap column matches **4a**’s causes
    (``model4_full_gap_sequence``) with every union-excluded cause listed—no **…**.

    **4a** — Risk behavior | Smoking / Alcohol | gaps | LE; Risk → Smoking, Alcohol,
    and ``MODEL4_RISK_DIRECT_GAPS``. Gap column: ``model4a_gap_sequence``; pass
    ``model4a_ellipsis=True`` to collapse remaining union-excluded causes to **…**.

    **4b** — Structural latents (Policy, …, Demography) in the first column; **Risk
    behavior** sits between that column and Smoking/Alcohol. Each latent → **Smoking**,
    **Alcohol**, and each measured cause gap (no latent → **LE**). Same gap ordering as
    Models **4** / **4a** (``model4_full_gap_sequence``). Requires ``latent_specs``
    including ``latent_risk``.

    **4c** — Structural latents | **Risk behavior** | **Cause-specific death rates**
    (one ``measured_block`` node) | **LE gap** (no Smoking/Alcohol, no per-cause
    ellipses). Structural → **Risk behavior**; each latent → measured block; block →
    **LE**. ``label_cause_column`` sets the block label (default **"Cause-specific death
    rates"** when ``None``). Column centers are evenly spaced (see ``_X4C_COL_STEP``).

    ``png_dpi`` sets ``-Gdpi`` for the primary PNG (default: Graphviz default, usually
    ~96). For **4b** and **4c**, ``write_slides_png`` (default **True**) also writes
    ``<stem>_slides.png`` at ``slides_png_dpi`` (default **72**) for a lighter bitmap
    (e.g. Google Slides). Set ``write_slides_png=False`` to skip the copy.

    Requires ``neato`` on ``PATH`` (Graphviz).
    """
    out_path = Path(out_path)
    if variant in ("4b", "4c") and (latent_specs is None or len(latent_specs) < 2):
        raise ValueError(
            "variant='4b' or '4c' requires latent_specs (e.g. LATENT_SPECS)."
        )

    if variant == "4c":
        seq: list[str | None] = []
    elif variant == "4":
        seq = model4_full_gap_sequence(predictor_cols)
    elif variant == "4a":
        seq = model4a_gap_sequence(predictor_cols, ellipsis=model4a_ellipsis)
    else:
        seq = model4_full_gap_sequence(predictor_cols)
    g = _base_graph_neato(node_fontsize)
    if variant == "4b":
        g.set_margin("0.45")
        g.set("pad", "0.85")
    elif variant == "4c":
        g.set_margin("0.42")
        g.set("pad", "0.88")

    smoking = alcohol = None  # type: ignore[assignment]
    if variant != "4c":
        smoking = make_node("latent_smoking", "latent", label=label_smoking)
        alcohol = make_node("latent_alcohol", "latent", label=label_alcohol)
        g.add_node(smoking)
        g.add_node(alcohol)
    le = make_node("LE_gap", "outcome", label=label_le)

    g.add_node(le)

    cause_node_4c: pydot.Node | None = None
    if variant == "4c":
        block_label = (
            label_cause_column
            if label_cause_column is not None
            else "Cause-specific gaps"
        )
        cause_node_4c = make_node(
            "measured_cause_rates", "measured_block", label=block_label
        )
        g.add_node(cause_node_4c)
        gaps: list = []
        gaps_real = []
    else:
        gaps, gaps_real = _add_model4_column_nodes(
            g, seq, make_node, gap_predictor_display_label, ellipsis_label
        )
    name_to_node = {n.get_name(): n for n in gaps_real}

    if variant == "4":
        x_sa, x_g, x_le = _X4_SA, _X4_GAPS, _X4_LE
        ys = _stack_y_positions(len(gaps), _Y_CENTER, _GAP_Y_SPACING)
        for node, y in zip(gaps, ys, strict=True):
            set_fixed_pos(node, x_g, y)

        set_fixed_pos(smoking, x_sa, _Y_CENTER + _LATENT_DY / 2)
        set_fixed_pos(alcohol, x_sa, _Y_CENTER - _LATENT_DY / 2)
        set_fixed_pos(le, x_le, _Y_CENTER)

        _edges_smoking_alcohol_gaps(g, smoking, alcohol, name_to_node)

    elif variant == "4a":
        x_left, x_sa, x_g, x_le = _XEXT_LEFT, _XEXT_SA, _XEXT_GAPS, _XEXT_LE
        risk = make_node("latent_risk", "latent", label="Risk behavior")
        g.add_node(risk)
        set_fixed_pos(risk, x_left, _Y_CENTER)

        ys = _stack_y_positions(len(gaps), _Y_CENTER, _GAP_Y_SPACING)
        for node, y in zip(gaps, ys, strict=True):
            set_fixed_pos(node, x_g, y)

        set_fixed_pos(smoking, x_sa, _Y_CENTER + _LATENT_DY / 2)
        set_fixed_pos(alcohol, x_sa, _Y_CENTER - _LATENT_DY / 2)
        set_fixed_pos(le, x_le, _Y_CENTER)

        _edges_risk_behavior(g, risk, smoking, alcohol, name_to_node)
        _edges_smoking_alcohol_gaps(g, smoking, alcohol, name_to_node)

    elif variant == "4b":
        assert latent_specs is not None
        assert smoking is not None and alcohol is not None
        non_risk_specs = [(nid, lab) for nid, lab in latent_specs if nid != "latent_risk"]
        risk_spec = next(
            ((nid, lab) for nid, lab in latent_specs if nid == "latent_risk"),
            None,
        )
        if risk_spec is None:
            raise ValueError(
                "variant='4b' requires ('latent_risk', ...) in latent_specs."
            )

        x_left, x_risk, x_sa, x_g, x_le = (
            _X4B_LEFT,
            _X4B_RISK,
            _X4B_SA,
            _X4B_GAPS,
            _X4B_LE,
        )

        left_nodes: dict[str, pydot.Node] = {}
        for node_id, lab in latent_specs:
            n = make_node(node_id, "latent", label=lab)
            g.add_node(n)
            left_nodes[node_id] = n

        ys_left = _stack_y_positions(
            len(non_risk_specs),
            _Y_CENTER,
            _LATENT_LEFT_COL_SPACING * _4B_VERTICAL_TIGHTEN,
        )
        for (node_id, _lab), y in zip(non_risk_specs, ys_left, strict=True):
            set_fixed_pos(left_nodes[node_id], x_left, y)

        risk_id, _risk_lab = risk_spec
        set_fixed_pos(left_nodes[risk_id], x_risk, _Y_CENTER)

        gap_spacing = _GAP_Y_SPACING * _4B_VERTICAL_TIGHTEN
        n_gap = len(gaps)
        if n_gap > 14:
            gap_spacing = max(
                52.0 * _4B_VERTICAL_TIGHTEN,
                min(_GAP_Y_SPACING * _4B_VERTICAL_TIGHTEN, 760.0 / max(n_gap - 1, 1)),
            )

        ys = _stack_y_positions(n_gap, _Y_CENTER, gap_spacing)
        for node, y in zip(gaps, ys, strict=True):
            set_fixed_pos(node, x_g, y)

        set_fixed_pos(smoking, x_sa, _Y_CENTER + _LATENT_DY / 2)
        set_fixed_pos(alcohol, x_sa, _Y_CENTER - _LATENT_DY / 2)
        set_fixed_pos(le, x_le, _Y_CENTER)

        _edges_latents_to_smoking_alcohol_and_gaps(
            g, left_nodes, latent_specs, smoking, alcohol, name_to_node
        )
        _edges_smoking_alcohol_gaps(g, smoking, alcohol, name_to_node)

    else:  # 4c
        assert latent_specs is not None
        assert cause_node_4c is not None
        non_risk_specs = [(nid, lab) for nid, lab in latent_specs if nid != "latent_risk"]
        risk_spec = next(
            ((nid, lab) for nid, lab in latent_specs if nid == "latent_risk"),
            None,
        )
        if risk_spec is None:
            raise ValueError(
                "variant='4c' requires ('latent_risk', ...) in latent_specs."
            )

        x_left, x_risk, x_g, x_le = (
            _X4C_LEFT,
            _X4C_RISK,
            _X4C_GAPS,
            _X4C_LE,
        )

        left_nodes = {}
        for node_id, lab in latent_specs:
            n = make_node(node_id, "latent", label=lab)
            g.add_node(n)
            left_nodes[node_id] = n

        ys_left = _stack_y_positions(
            len(non_risk_specs),
            _Y_CENTER,
            _LATENT_LEFT_COL_SPACING * _4B_VERTICAL_TIGHTEN,
        )
        for (node_id, _lab), y in zip(non_risk_specs, ys_left, strict=True):
            set_fixed_pos(left_nodes[node_id], x_left, y)

        risk_id, _risk_lab = risk_spec
        set_fixed_pos(left_nodes[risk_id], x_risk, _Y_CENTER)

        set_fixed_pos(cause_node_4c, x_g, _Y_CENTER)
        set_fixed_pos(le, x_le, _Y_CENTER)

        _edges_structural_to_risk(g, left_nodes, non_risk_specs, left_nodes[risk_id])
        _edges_latents_to_measured_block(
            g, left_nodes, latent_specs, cause_node_4c
        )

    if variant == "4c":
        assert cause_node_4c is not None
        g.add_edge(pydot.Edge(cause_node_4c, le))
    else:
        for node in gaps_real:
            g.add_edge(pydot.Edge(node, le))
        _pin_ellipsis_to_le_layer(g, gaps, le)

    if variant != "4c":
        assert smoking is not None and alcohol is not None
        g.add_edge(
            pydot.Edge(
                smoking,
                alcohol,
                style="invis",
                weight="100",
            )
        )

    _polish_edges(g)
    write_png_neato_n2(g, out_path, dpi=png_dpi)
    if variant in ("4b", "4c") and write_slides_png:
        slides_path = out_path.with_name(f"{out_path.stem}_slides{out_path.suffix}")
        write_png_neato_n2(g, slides_path, dpi=slides_png_dpi)
    return out_path
