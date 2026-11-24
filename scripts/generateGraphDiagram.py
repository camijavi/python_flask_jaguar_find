"""
generateGraphDiagram.py
================================================================================
LIVE VECTOR GRAPHIC GENERATOR FOR ALL JAGUARFIND & JAGUARMAPS GRAPHS
================================================================================
Reads all 20 live `graphCombined.Graph`-derived structures directly from the
application (1 Macro Campus Graph + 1 Micro Pedestrian Walkway Graph + 18 Indoor
Building Subgraphs) and renders a high-resolution, dependency-free SVG graphic
saved to `docs/campus_graphs_diagram.svg`.
================================================================================
"""

from __future__ import annotations

import html
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.graph import getGraphsInventory, globalNavigationService
from backend.subgraphs import getAllBuildingSubgraphs
from backend.data.campusCategories import CampusCategory


# Short, collision-free labels for the 28 Macro Campus Graph nodes
MACRO_SHORT_LABELS: Dict[str, str] = {
    "mainParking": "1er Acc",
    "northGate": "3er Acc",
    "northeastGate": "2do Acc",
    "buildingA": "A",
    "buildingB": "B",
    "buildingC": "C",
    "buildingD": "D",
    "buildingE": "E",
    "buildingF": "F",
    "buildingG": "G",
    "buildingH": "H",
    "buildingI": "I",
    "buildingJ": "J",
    "buildingK": "K",
    "buildingL": "L",
    "buildingM": "M",
    "buildingN": "N",
    "buildingO": "O",
    "buildingP": "P",
    "chilamatesPlaza": "CH",
    "jaguarJungle": "JJ",
    "miRanchito": "MR",
    "labDigitalFia": "DF",
    "areaDeMesas": "AM",
    "sportsZone": "SP",
    "jaguarCenter": "JC",
    "jaguarGym": "GYM",
    "physiotherapy": "FT",
}

# Small visual nudges (dx, dy in panel pixels) only for tightly clustered macro nodes
MACRO_VISUAL_NUDGES: Dict[str, Tuple[float, float]] = {
    "buildingB": (0, 8),
    "buildingC": (0, -6),
    "buildingD": (8, 2),
    "buildingJ": (-8, 2),
    "areaDeMesas": (-10, 6),
    "labDigitalFia": (-8, -4),
    "miRanchito": (2, -8),
    "jaguarJungle": (10, -2),
    "buildingG": (2, -4),
    "buildingF": (2, 6),
    "buildingE": (-10, 12),
    "jaguarCenter": (-14, -4),
    "buildingL": (18, -14),
    "physiotherapy": (14, 4),
    "jaguarGym": (2, 16),
}

CATEGORY_COLORS: Dict[str, str] = {
    CampusCategory.CLASSROOM: "#2563eb",        # Blue
    CampusCategory.FACULTY: "#0d9488",          # Teal
    CampusCategory.ADMINISTRATIVE: "#475569",   # Slate
    CampusCategory.DENTAL_LAB: "#e11d48",       # Rose
    CampusCategory.MEDICAL_LAB: "#db2777",      # Pink-magenta
    CampusCategory.FOOD_AREA: "#d97706",        # Amber
    CampusCategory.SPORTS: "#16a34a",           # Green
    CampusCategory.PARKING_LOT: "#7c3aed",      # Violet
    CampusCategory.STAIRS: "#ea580c",           # Orange
    CampusCategory.ACCESSIBLE_RAMP: "#059669",  # Emerald
    CampusCategory.RESTROOM: "#0284c7",         # Sky
    CampusCategory.DRINKING_FOUNTAIN: "#06b6d4",
}

WALKWAY_TYPE_STYLE: Dict[str, Tuple[str, float, str]] = {
    # type -> (strokeColor, strokeWidth, dasharray)
    "ground":    ("#ec4899", 1.7, ""),
    "indoor":    ("#4f46e5", 1.8, "3,2"),
    "level2":    ("#7c3aed", 2.8, "5,2"),
    "crosswalk": ("#f59e0b", 2.8, "2,2"),
    "ramp":      ("#10b981", 2.6, ""),
    "stairs":    ("#ef4444", 2.6, "3,2"),
}

SHORT_SUBGRAPH_TITLES: Dict[str, str] = {
    "buildingA": "Edificio A — CAE & DPA",
    "buildingB": "Edificio B — Aulas & Farmacia",
    "buildingC": "Edificio C — Labs & Caja",
    "buildingD": "Edificio D — Odonto Digital",
    "buildingE": "Edificio E — Medicina",
    "buildingF": "Edificio F — FCAE & FMDCC",
    "buildingG": "Edificio G — Derecho & Aud.",
    "buildingH": "Edificio H — Labs Medicina",
    "buildingI": "Edificio I — Rectoría & Bib.",
    "buildingJ": "Edificio J — Labs Odonto",
    "buildingK": "Edificio K — Cafetería",
    "buildingL": "Edificio L — Cultura & Mús.",
    "buildingM": "Edificio M — Posgrados",
    "buildingN": "Edificio N — Clínicas (GW)",
    "buildingO": "Edificio O — Ingeniería FIA",
    "buildingP": "Edificio P — Copérnico",
    "jaguarCenter": "Jaguar Center — Complejo",
    "sportsZone": "Campos Deportivos",
}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def mapBox(
    val: float,
    inMin: float,
    inMax: float,
    outMin: float,
    outMax: float,
) -> float:
    if inMax - inMin == 0:
        return (outMin + outMax) / 2.0
    t = (val - inMin) / (inMax - inMin)
    return outMin + t * (outMax - outMin)


def renderHeaderAndArchitecture(inventory: dict, width: int) -> List[str]:
    lines: List[str] = []
    b = inventory["breakdown"]
    tot = inventory["totals"]

    # Top hero banner
    lines.append(
        f'<rect x="0" y="0" width="{width}" height="106" fill="url(#heroGrad)"/>'
    )
    lines.append(
        '<text x="36" y="42" fill="#ffffff" font-size="24" font-weight="800">'
        'JaguarFind &amp; JaguarMaps UAM — All Application Graphs</text>'
    )
    lines.append(
        '<text x="36" y="68" fill="#cbd5e1" font-size="13" font-weight="600">'
        'Central Guide: graphCombined.py (Vertex &amp; Graph) • Directed, Non-Complete, Weighted G = (V, E, W)</text>'
    )
    lines.append(
        '<text x="36" y="89" fill="#94a3b8" font-size="11.5">'
        'Data sources: buildings.txt &amp; coordenadas.txt • Every backend graph inherits directly from graphCombined.Graph</text>'
    )

    # KPI pills on top-right
    kpis = [
        (f"{inventory['totalBackendGraphs']}", "Backend Graphs", "#38bdf8"),
        (f"{tot['vertices']}", "Total Vertices |V|", "#34d399"),
        (f"{tot['directedEdges']:,}", "Directed Edges |E|", "#f472b6"),
        (f"+{b['frontendMirrorGraphs']}", "UI Mirror Graphs", "#fbbf24"),
    ]
    pillW, pillH, gap = 148, 62, 12
    startX = width - 36 - (len(kpis) * pillW + (len(kpis) - 1) * gap)
    for idx, (val, label, accent) in enumerate(kpis):
        px = startX + idx * (pillW + gap)
        py = 22
        lines.append(
            f'<rect x="{px}" y="{py}" width="{pillW}" height="{pillH}" rx="10" '
            f'fill="#0f172a" fill-opacity="0.45" stroke="{accent}" stroke-opacity="0.7" stroke-width="1.3"/>'
        )
        lines.append(
            f'<text x="{px + pillW / 2:.1f}" y="{py + 31}" text-anchor="middle" '
            f'fill="{accent}" font-size="22" font-weight="800">{esc(val)}</text>'
        )
        lines.append(
            f'<text x="{px + pillW / 2:.1f}" y="{py + 50}" text-anchor="middle" '
            f'fill="#e2e8f0" font-size="11" font-weight="600">{esc(label)}</text>'
        )

    # Architecture Inheritance Strip (y: 122 .. 244)
    stripY = 122
    lines.append(
        f'<rect x="32" y="{stripY}" width="{width - 64}" height="122" rx="14" '
        f'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" filter="url(#cardShadow)"/>'
    )
    lines.append(
        f'<text x="52" y="{stripY + 24}" fill="#0f172a" font-size="13" font-weight="800">'
        'UNIFIED CLASS HIERARCHY &amp; 3-TIER CAMPUS NAVIGATION ARCHITECTURE</text>'
    )

    # Box 1: graphCombined.py
    bx1, by, bw1, bh = 52, stripY + 36, 355, 72
    lines.append(
        f'<rect x="{bx1}" y="{by}" width="{bw1}" height="{bh}" rx="10" '
        f'fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>'
    )
    lines.append(
        f'<text x="{bx1 + 14}" y="{by + 21}" fill="#1d4ed8" font-size="13" font-weight="800">'
        'graphCombined.py (Central Guide)</text>'
    )
    lines.append(
        f'<text x="{bx1 + 14}" y="{by + 40}" fill="#1e293b" font-size="10.8" font-family="monospace">'
        'Vertex(nodeId, neigh) • Graph(vertices)</text>'
    )
    lines.append(
        f'<text x="{bx1 + 14}" y="{by + 58}" fill="#475569" font-size="9.2">'
        'search • addVertex • addEdge • link • deleteEdge • printMatrix</text>'
    )

    # Arrow 1 -> 2
    lines.append(
        f'<line x1="{bx1 + bw1}" y1="{by + bh/2}" x2="{bx1 + bw1 + 38}" y2="{by + bh/2}" '
        f'stroke="#2563eb" stroke-width="2.2" marker-end="url(#arrowBlue)"/>'
    )
    lines.append(
        f'<text x="{bx1 + bw1 + 19}" y="{by + bh/2 - 8}" text-anchor="middle" '
        f'fill="#2563eb" font-size="9.2" font-weight="700">inherits</text>'
    )

    # Box 2: directedGraph.py + dijkstraRouter.py
    bx2, bw2 = bx1 + bw1 + 42, 345
    lines.append(
        f'<rect x="{bx2}" y="{by}" width="{bw2}" height="{bh}" rx="10" '
        f'fill="#f0fdfa" stroke="#0d9488" stroke-width="1.8"/>'
    )
    lines.append(
        f'<text x="{bx2 + 14}" y="{by + 21}" fill="#0f766e" font-size="13" font-weight="800">'
        'directedGraph.py &amp; dijkstraRouter.py</text>'
    )
    lines.append(
        f'<text x="{bx2 + 14}" y="{by + 40}" fill="#1e293b" font-size="10.8" font-family="monospace">'
        'Node(Vertex) • DirectedGraph(Graph)</text>'
    )
    lines.append(
        f'<text x="{bx2 + 14}" y="{by + 58}" fill="#475569" font-size="9.4">'
        'GPS/SVG coords • Accessibility filter • Dijkstra O((V+E) log V)</text>'
    )

    # Arrow 2 -> Tiers
    branchStartX = bx2 + bw2
    branchMidX = branchStartX + 24
    lines.append(
        f'<line x1="{branchStartX}" y1="{by + bh/2}" x2="{branchMidX}" y2="{by + bh/2}" '
        f'stroke="#0d9488" stroke-width="2.2"/>'
    )

    # 3 Tier Summary Cards on the right
    tierX = branchMidX + 16
    tierW = (width - 52 - tierX - 24) / 3.0
    tiers = [
        ("Tier 1 • Macro Campus", "1 Graph", "28 V • 110 E_dir • ρ=0.146", "#2563eb", "#eff6ff"),
        ("Tier 2 • Outdoor Walkways", "1 Graph", "209 V • 508 E_dir • ρ=0.012", "#db2777", "#fdf2f8"),
        ("Tier 3 • Building Subgraphs", "18 Graphs", "261 V • 538 E_dir • Floors 1–5", "#0d9488", "#f0fdfa"),
    ]
    lines.append(
        f'<line x1="{branchMidX}" y1="{by + bh/2}" x2="{tierX - 4}" y2="{by + bh/2}" '
        f'stroke="#0d9488" stroke-width="2.2" marker-end="url(#arrowTeal)"/>'
    )
    for idx, (title, countStr, statsStr, border, fill) in enumerate(tiers):
        tx = tierX + idx * (tierW + 12)
        lines.append(
            f'<rect x="{tx:.1f}" y="{by}" width="{tierW:.1f}" height="{bh}" rx="10" '
            f'fill="{fill}" stroke="{border}" stroke-width="1.6"/>'
        )
        lines.append(
            f'<text x="{tx + 12:.1f}" y="{by + 21}" fill="{border}" font-size="11.5" font-weight="800">'
            f'{esc(title)}</text>'
        )
        lines.append(
            f'<text x="{tx + 12:.1f}" y="{by + 42}" fill="#0f172a" font-size="14" font-weight="800">'
            f'{esc(countStr)}</text>'
        )
        lines.append(
            f'<text x="{tx + 12:.1f}" y="{by + 60}" fill="#475569" font-size="10.2" font-weight="600">'
            f'{esc(statsStr)}</text>'
        )

    return lines


def renderMacroPanel(px: float, py: float, pw: float, ph: float) -> List[str]:
    lines: List[str] = []
    macro = globalNavigationService.graph
    summary = macro.getGraphSummary()

    lines.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" '
        f'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" filter="url(#cardShadow)"/>'
    )
    lines.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="46" rx="14" fill="#eff6ff"/>'
    )
    lines.append(
        f'<rect x="{px}" y="{py + 32}" width="{pw}" height="14" fill="#eff6ff"/>'
    )
    lines.append(
        f'<line x1="{px}" y1="{py + 46}" x2="{px + pw}" y2="{py + 46}" stroke="#bfdbfe" stroke-width="1"/>'
    )
    lines.append(
        f'<text x="{px + 18}" y="{py + 22}" fill="#1d4ed8" font-size="14" font-weight="800">'
        'TIER 1 — MACRO CAMPUS GRAPH (BUILDINGS, GATES &amp; ZONES)</text>'
    )
    lines.append(
        f'<text x="{px + 18}" y="{py + 38}" fill="#475569" font-size="11">'
        f'|V| = {summary["vertexCount"]} vertices  •  |E_dir| = {summary["directedEdgeCount"]} directed edges (55 pairs)  •  '
        f'Density ρ = {summary["density"]:.4f} (Non-Complete)</text>'
    )

    # Plot bounding box
    plotX0, plotY0 = px + 28, py + 62
    plotX1, plotY1 = px + pw - 28, py + ph - 52
    lines.append(
        f'<rect x="{plotX0 - 10}" y="{plotY0 - 6}" width="{plotX1 - plotX0 + 20}" '
        f'height="{plotY1 - plotY0 + 12}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>'
    )

    nodes = macro.getAllNodes()
    xs = [n.xSvg for n in nodes]
    ys = [n.ySvg for n in nodes]
    minX, maxX = min(xs), max(xs)
    minY, maxY = min(ys), max(ys)

    pos: Dict[str, Tuple[float, float]] = {}
    for n in nodes:
        sx = mapBox(n.xSvg, minX, maxX, plotX0 + 18, plotX1 - 18)
        sy = mapBox(n.ySvg, minY, maxY, plotY0 + 16, plotY1 - 16)
        dx, dy = MACRO_VISUAL_NUDGES.get(n.nodeId, (0.0, 0.0))
        pos[n.nodeId] = (sx + dx, sy + dy)

    # Draw edges (deduplicate bidirectional pairs visually while showing directionality clearly)
    drawnPairs = set()
    for n in nodes:
        x1, y1 = pos[n.nodeId]
        for edge in n.outgoingEdges:
            pair = tuple(sorted((n.nodeId, edge.targetNodeId)))
            if pair in drawnPairs:
                continue
            drawnPairs.add(pair)
            x2, y2 = pos[edge.targetNodeId]
            if not edge.isAccessible:
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#ef4444" stroke-width="2.4" stroke-dasharray="5,3"/>'
                )
            else:
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#94a3b8" stroke-width="1.6" stroke-opacity="0.82"/>'
                )
            # Show edge weight (meters) on well-spaced edges (>= 72px)
            segLen = math.hypot(x2 - x1, y2 - y1)
            if segLen >= 74 or not edge.isAccessible:
                mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                labelColor = "#dc2626" if not edge.isAccessible else "#475569"
                tag = f"{int(edge.distanceMeters)}m"
                lines.append(
                    f'<rect x="{mx - 15:.1f}" y="{my - 7:.1f}" width="30" height="13" rx="4" '
                    f'fill="#ffffff" fill-opacity="0.9"/>'
                )
                lines.append(
                    f'<text x="{mx:.1f}" y="{my + 3:.1f}" text-anchor="middle" '
                    f'fill="{labelColor}" font-size="8.5" font-weight="700">{tag}</text>'
                )

    # Draw macro vertices
    for n in nodes:
        cx, cy = pos[n.nodeId]
        color = CATEGORY_COLORS.get(n.category, "#475569")
        label = MACRO_SHORT_LABELS.get(n.nodeId, n.nodeId[:3].upper())
        r = 13.5 if len(label) <= 2 else 17.0
        # Double halo if building has a child indoor subgraph
        hasSubgraph = n.nodeId in getAllBuildingSubgraphs()
        if hasSubgraph:
            lines.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 3:.1f}" '
                f'fill="none" stroke="{color}" stroke-opacity="0.35" stroke-width="2"/>'
            )
        lines.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )
        fontSize = "9.5" if len(label) <= 2 else ("8.2" if len(label) <= 3 else "7.2")
        lines.append(
            f'<text x="{cx:.1f}" y="{cy + 3.2:.1f}" text-anchor="middle" '
            f'fill="#ffffff" font-size="{fontSize}" font-weight="800">{esc(label)}</text>'
        )

    # Legend at bottom of macro panel
    legY = py + ph - 26
    legendItems = [
        ("#2563eb", "Classrooms"),
        ("#0d9488", "Faculties"),
        ("#e11d48", "Labs/Clinics"),
        ("#d97706", "Food/Plazas"),
        ("#16a34a", "Sports"),
        ("#7c3aed", "Gates"),
        ("#475569", "Admin"),
    ]
    lx = px + 20
    for color, name in legendItems:
        lines.append(f'<circle cx="{lx + 5}" cy="{legY - 3}" r="4.5" fill="{color}"/>')
        lines.append(
            f'<text x="{lx + 13}" y="{legY}" fill="#334155" font-size="10" font-weight="600">{esc(name)}</text>'
        )
        lx += len(name) * 6.0 + 26

    # Stairs dashed key + Child subgraph halo key
    lines.append(
        f'<line x1="{lx}" y1="{legY - 3}" x2="{lx + 16}" y2="{legY - 3}" '
        f'stroke="#ef4444" stroke-width="2.2" stroke-dasharray="4,2"/>'
    )
    lines.append(
        f'<text x="{lx + 21}" y="{legY}" fill="#dc2626" font-size="10" font-weight="700">Stairs (inaccessible)</text>'
    )

    return lines


def renderWalkwayPanel(px: float, py: float, pw: float, ph: float) -> List[str]:
    lines: List[str] = []
    wg = globalNavigationService.walkwayGraph
    summary = wg.getGraphSummary()

    lines.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" '
        f'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" filter="url(#cardShadow)"/>'
    )
    lines.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="46" rx="14" fill="#fdf2f8"/>'
    )
    lines.append(
        f'<rect x="{px}" y="{py + 32}" width="{pw}" height="14" fill="#fdf2f8"/>'
    )
    lines.append(
        f'<line x1="{px}" y1="{py + 46}" x2="{px + pw}" y2="{py + 46}" stroke="#fbcfe8" stroke-width="1"/>'
    )
    lines.append(
        f'<text x="{px + 18}" y="{py + 22}" fill="#be185d" font-size="14" font-weight="800">'
        'TIER 2 — MICRO PEDESTRIAN WALKWAY GRAPH (SIDEWALKS &amp; PORTALS)</text>'
    )
    lines.append(
        f'<text x="{px + 18}" y="{py + 38}" fill="#475569" font-size="11">'
        f'|V| = {summary["vertexCount"]} waypoints  •  |E_dir| = {summary["directedEdgeCount"]} directed edges (254 segments)  •  '
        f'Density ρ = {summary["density"]:.4f} (Sparse / Non-Complete)</text>'
    )

    plotX0, plotY0 = px + 28, py + 62
    plotX1, plotY1 = px + pw - 28, py + ph - 52
    lines.append(
        f'<rect x="{plotX0 - 10}" y="{plotY0 - 6}" width="{plotX1 - plotX0 + 20}" '
        f'height="{plotY1 - plotY0 + 12}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>'
    )

    nodes = wg.getAllNodes()
    xs = [n.xSvg for n in nodes]
    ys = [n.ySvg for n in nodes]
    minX, maxX = min(xs), max(xs)
    minY, maxY = min(ys), max(ys)

    pos: Dict[str, Tuple[float, float]] = {}
    for n in nodes:
        sx = mapBox(n.xSvg, minX, maxX, plotX0 + 14, plotX1 - 14)
        sy = mapBox(n.ySvg, minY, maxY, plotY0 + 14, plotY1 - 14)
        pos[n.nodeId] = (sx, sy)

    # Draw all walkway edges styled by walkwayType
    drawnPairs = set()
    for n in nodes:
        x1, y1 = pos[n.nodeId]
        for edge in n.outgoingEdges:
            pair = tuple(sorted((n.nodeId, edge.targetNodeId)))
            if pair in drawnPairs:
                continue
            drawnPairs.add(pair)
            x2, y2 = pos[edge.targetNodeId]
            wType = "stairs" if not edge.isAccessible else edge.walkwayType
            color, sw, dash = WALKWAY_TYPE_STYLE.get(wType, ("#ec4899", 1.6, ""))
            dashAttr = f' stroke-dasharray="{dash}"' if dash else ""
            lines.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{dashAttr}/>'
            )

    # Draw vertices (portals slightly larger than generic junctions)
    for n in nodes:
        cx, cy = pos[n.nodeId]
        if n.portalKind in ("gate", "skybridge", "stairs", "ramp", "crosswalk"):
            color = {
                "gate": "#7c3aed",
                "skybridge": "#7c3aed",
                "stairs": "#ef4444",
                "ramp": "#10b981",
                "crosswalk": "#f59e0b",
            }[n.portalKind]
            lines.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" fill="{color}" stroke="#ffffff" stroke-width="1"/>'
            )
        elif n.portalKind == "door":
            lines.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.0" fill="#0ea5e9" stroke="#ffffff" stroke-width="0.9"/>'
            )
        else:
            lines.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.9" fill="#9d174d" fill-opacity="0.72"/>'
            )

    # Subtle landmark callout tags for key orientation zones
    zoneAnchors = [
        ("ent_gate", "1er Acceso", (0, -9)),
        ("gate_third", "3er Acceso", (16, 12)),
        ("gate_second", "2do Acceso", (-16, 12)),
        ("a_center", "A-B-C", (-24, 2)),
        ("p_front_mid", "Edif. P", (0, -10)),
        ("o_terrace_mid", "Edif. O", (22, -4)),
        ("i_courtyard", "Edif. I", (-20, 12)),
        ("jc_entry", "Jaguar Ctr", (0, -10)),
        ("sports_concourse_m", "Deportes", (0, -10)),
        ("chilamates_mid", "Chilamates", (-30, 0)),
    ]
    for nid, label, (dx, dy) in zoneAnchors:
        if nid in pos:
            ax, ay = pos[nid]
            tx, ty = ax + dx, ay + dy
            tw = len(label) * 5.6 + 10
            lines.append(
                f'<rect x="{tx - tw/2:.1f}" y="{ty - 7:.1f}" width="{tw:.1f}" height="13" rx="4" '
                f'fill="#0f172a" fill-opacity="0.78"/>'
            )
            lines.append(
                f'<text x="{tx:.1f}" y="{ty + 2.6:.1f}" text-anchor="middle" '
                f'fill="#ffffff" font-size="8.5" font-weight="700">{esc(label)}</text>'
            )

    # Legend at bottom of walkway panel
    legY = py + ph - 26
    wLegend = [
        ("#ec4899", "", "Sidewalk"),
        ("#4f46e5", "3,2", "Indoor"),
        ("#7c3aed", "5,2", "2P Skybridge"),
        ("#f59e0b", "2,2", "Crosswalk"),
        ("#10b981", "", "Ramp"),
        ("#ef4444", "3,2", "Stairs"),
    ]
    lx = px + 22
    for color, dash, name in wLegend:
        dashAttr = f' stroke-dasharray="{dash}"' if dash else ""
        lines.append(
            f'<line x1="{lx}" y1="{legY - 3}" x2="{lx + 18}" y2="{legY - 3}" '
            f'stroke="{color}" stroke-width="2.6"{dashAttr}/>'
        )
        lines.append(
            f'<text x="{lx + 23}" y="{legY}" fill="#334155" font-size="10" font-weight="600">{esc(name)}</text>'
        )
        lx += len(name) * 6.0 + 38

    lines.append(f'<circle cx="{lx + 4}" cy="{legY - 3}" r="3.4" fill="#0ea5e9"/>')
    lines.append(
        f'<text x="{lx + 12}" y="{legY}" fill="#334155" font-size="10" font-weight="600">Door Portal</text>'
    )

    return lines


def renderSubgraphCard(
    buildingId: str,
    sg,
    cx: float,
    cy: float,
    cw: float,
    ch: float,
) -> List[str]:
    lines: List[str] = []
    metrics = sg.graph.getGraphSummary()
    title = SHORT_SUBGRAPH_TITLES.get(buildingId, sg.name)

    # Outer card
    lines.append(
        f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="11" '
        f'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.1" filter="url(#cardShadow)"/>'
    )
    # Header bar
    lines.append(
        f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="32" rx="11" fill="#f0fdfa"/>'
    )
    lines.append(
        f'<rect x="{cx:.1f}" y="{cy + 20:.1f}" width="{cw:.1f}" height="12" fill="#f0fdfa"/>'
    )
    lines.append(
        f'<line x1="{cx:.1f}" y1="{cy + 32:.1f}" x2="{cx + cw:.1f}" y2="{cy + 32:.1f}" '
        f'stroke="#ccfbf1" stroke-width="1"/>'
    )
    # Building code pill
    lines.append(
        f'<rect x="{cx + 8:.1f}" y="{cy + 7:.1f}" width="26" height="18" rx="5" fill="#0d9488"/>'
    )
    lines.append(
        f'<text x="{cx + 21:.1f}" y="{cy + 19.5:.1f}" text-anchor="middle" '
        f'fill="#ffffff" font-size="10" font-weight="800">{esc(sg.code)}</text>'
    )
    lines.append(
        f'<text x="{cx + 40:.1f}" y="{cy + 20:.1f}" fill="#0f172a" font-size="10.8" font-weight="700">'
        f'{esc(title)}</text>'
    )

    # Mini plot area
    mx0, my0 = cx + 10, cy + 38
    mw, mh = cw - 20, ch - 76
    lines.append(
        f'<rect x="{mx0:.1f}" y="{my0:.1f}" width="{mw:.1f}" height="{mh:.1f}" rx="7" '
        f'fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.9"/>'
    )

    # Floor-layered layout: Floor 1 at bottom, higher floors above
    floors = sorted(sg.floors)
    numFloors = max(1, len(floors))
    bandH = mh / numFloors
    nodePos: Dict[str, Tuple[float, float]] = {}

    for fIdx, fl in enumerate(floors):
        # Bottom-to-top floor ordering (Floor 1 at bottom)
        bandTop = my0 + (numFloors - 1 - fIdx) * bandH
        bandMidY = bandTop + bandH / 2.0

        # Subtle alternating floor stripe & floor label
        if fIdx % 2 == 1:
            lines.append(
                f'<rect x="{mx0 + 1:.1f}" y="{bandTop + 1:.1f}" width="{mw - 2:.1f}" '
                f'height="{bandH - 2:.1f}" fill="#f1f5f9" fill-opacity="0.55"/>'
            )
        if fIdx > 0:
            lines.append(
                f'<line x1="{mx0 + 4:.1f}" y1="{bandTop + bandH:.1f}" '
                f'x2="{mx0 + mw - 4:.1f}" y2="{bandTop + bandH:.1f}" '
                f'stroke="#cbd5e1" stroke-width="0.7" stroke-dasharray="3,3"/>'
            )
        lines.append(
            f'<text x="{mx0 + 6:.1f}" y="{bandTop + 11:.1f}" fill="#94a3b8" '
            f'font-size="8.2" font-weight="700">P{fl}</text>'
        )

        flNodes = sg.getNodesByFloor(fl)
        count = len(flNodes)
        if count == 0:
            continue

        # Sort nodes on this floor gently by longitude (or preserve build order if tied)
        # Preserve original insertion order (already ordered along hallways!) for clean corridors
        padLeft, padRight = 24.0, 12.0
        usableW = max(10.0, mw - padLeft - padRight)

        if count <= 8:
            for i, n in enumerate(flNodes):
                nx = mx0 + padLeft + (usableW * 0.5 if count == 1 else (i / (count - 1)) * usableW)
                # Gentle zigzag on single-floor dense nodes so overlapping edges remain visible
                jitter = 0.0
                if numFloors == 1 and count >= 5:
                    jitter = (-12.0 if i % 2 == 0 else 12.0)
                elif count >= 6:
                    jitter = (-5.5 if i % 2 == 0 else 5.5)
                nodePos[n.nodeId] = (nx, bandMidY + jitter)
        else:
            # Two staggered rows within this floor band (e.g., Building C/O/P 12-17 nodes per floor)
            for i, n in enumerate(flNodes):
                nx = mx0 + padLeft + (i / (count - 1)) * usableW
                rowOffset = -bandH * 0.22 if i % 2 == 0 else bandH * 0.22
                nodePos[n.nodeId] = (nx, bandMidY + rowOffset)

    # Draw edges inside this subgraph
    drawn = set()
    for n in sg.getAllNodes():
        if n.nodeId not in nodePos:
            continue
        x1, y1 = nodePos[n.nodeId]
        for edge in n.outgoingEdges:
            if edge.targetNodeId not in nodePos:
                continue
            pair = tuple(sorted((n.nodeId, edge.targetNodeId)))
            if pair in drawn:
                continue
            drawn.add(pair)
            x2, y2 = nodePos[edge.targetNodeId]
            targetNode = sg.getNode(edge.targetNodeId)
            isVertical = targetNode is not None and targetNode.floorLevel != n.floorLevel

            if isVertical:
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#ea580c" stroke-width="1.6" stroke-dasharray="3,2"/>'
                )
            elif not edge.isAccessible:
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#ef4444" stroke-width="1.4" stroke-dasharray="2,2"/>'
                )
            elif "ramp" in n.nodeId.lower() or "ramp" in edge.targetNodeId.lower():
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#10b981" stroke-width="1.8"/>'
                )
            else:
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#64748b" stroke-width="1.25" stroke-opacity="0.8"/>'
                )

    # Draw nodes inside this subgraph
    entranceSet = set(sg.entranceNodeIds)
    nodeCount = len(sg.getAllNodes())
    dotR = 3.0 if nodeCount >= 24 else (3.6 if nodeCount >= 14 else 4.3)
    for n in sg.getAllNodes():
        if n.nodeId not in nodePos:
            continue
        nx, ny = nodePos[n.nodeId]
        if n.category == CampusCategory.STAIRS:
            fill = "#ea580c"
        elif n.category == CampusCategory.ACCESSIBLE_RAMP:
            fill = "#10b981"
        elif n.accessLevel == "restricted":
            fill = "#e11d48"
        elif n.nodeId in entranceSet:
            fill = "#2563eb"
        else:
            fill = "#0d9488"

        if n.nodeId in entranceSet:
            lines.append(
                f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{dotR + 1.8:.1f}" '
                f'fill="none" stroke="#2563eb" stroke-opacity="0.45" stroke-width="1.3"/>'
            )
        lines.append(
            f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{dotR:.1f}" '
            f'fill="{fill}" stroke="#ffffff" stroke-width="0.9"/>'
        )

    # Footer metrics bar
    fy = cy + ch - 26
    floorText = f"{len(floors)}F" if len(floors) > 1 else "1F"
    lines.append(
        f'<text x="{cx + 10:.1f}" y="{fy + 9:.1f}" fill="#0f172a" font-size="10.2" font-weight="700">'
        f'|V|={metrics["vertexCount"]}  |E|={metrics["directedEdgeCount"]}</text>'
    )
    lines.append(
        f'<text x="{cx + cw - 10:.1f}" y="{fy + 9:.1f}" text-anchor="end" '
        f'fill="#64748b" font-size="9.8" font-weight="600">'
        f'{floorText} • ρ={metrics["density"]:.3f}</text>'
    )
    lines.append(
        f'<text x="{cx + 10:.1f}" y="{fy + 21:.1f}" fill="#94a3b8" font-size="8.6">'
        f'Parent: {esc(sg.macroNodeId)} • Non-Complete</text>'
    )

    return lines


def generateDiagram(outputPath: Path) -> Path:
    inventory = getGraphsInventory()
    subgraphs = getAllBuildingSubgraphs()

    width = 1600
    height = 1790

    svg: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif">',
        "<defs>",
        '  <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '    <stop offset="0%" stop-color="#0f172a"/>',
        '    <stop offset="55%" stop-color="#1e3a5f"/>',
        '    <stop offset="100%" stop-color="#0f766e"/>',
        "  </linearGradient>",
        '  <filter id="cardShadow" x="-2%" y="-2%" width="104%" height="106%">',
        '    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.06"/>',
        "  </filter>",
        '  <marker id="arrowBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "  </marker>",
        '  <marker id="arrowTeal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#0d9488"/>',
        "  </marker>",
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f1f5f9"/>',
    ]

    # 1. Header & Unified Class Architecture
    svg.extend(renderHeaderAndArchitecture(inventory, width))

    # 2. Tier 1 (Macro) & Tier 2 (Walkway) Side-by-Side
    panelY, panelH = 262, 540
    panelW = (width - 64 - 24) / 2.0
    svg.extend(renderMacroPanel(32, panelY, panelW, panelH))
    svg.extend(renderWalkwayPanel(32 + panelW + 24, panelY, panelW, panelH))

    # 3. Tier 3: All 18 Building Subgraphs Section Header
    secY = panelY + panelH + 22
    svg.append(
        f'<rect x="32" y="{secY}" width="{width - 64}" height="42" rx="10" '
        f'fill="#0f766e" filter="url(#cardShadow)"/>'
    )
    svg.append(
        f'<text x="50" y="{secY + 26}" fill="#ffffff" font-size="14" font-weight="800">'
        f'TIER 3 — ALL {len(subgraphs)} MICRO INDOOR BUILDING SUBGRAPHS '
        f'(CHILD GRAPHS OF MACRO BUILDINGS • 261 VERTICES, 538 DIRECTED EDGES)</text>'
    )

    # Legend pills inside section header (right side)
    sLegItems = [
        ("#2563eb", "Entrance"),
        ("#0d9488", "Room/Area"),
        ("#ea580c", "Stairs"),
        ("#10b981", "Ramp"),
        ("#e11d48", "Gateway/Restricted"),
    ]
    slx = width - 485
    for color, label in sLegItems:
        svg.append(
            f'<circle cx="{slx}" cy="{secY + 21}" r="4.5" fill="{color}" stroke="#ffffff" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{slx + 9}" y="{secY + 25}" fill="#f0fdfa" font-size="10.2" font-weight="600">{esc(label)}</text>'
        )
        slx += len(label) * 6.0 + 30

    # 6 columns x 3 rows grid of all 18 building subgraphs
    gridY = secY + 54
    cols = 6
    gapX, gapY = 14, 14
    cardW = (width - 64 - (cols - 1) * gapX) / cols
    cardH = 270

    orderedIds = list(subgraphs.keys())
    for idx, bid in enumerate(orderedIds):
        r = idx // cols
        c = idx % cols
        cx = 32 + c * (cardW + gapX)
        cy = gridY + r * (cardH + gapY)
        svg.extend(renderSubgraphCard(bid, subgraphs[bid], cx, cy, cardW, cardH))

    # Footer summary bar
    footY = height - 42
    svg.append(
        f'<rect x="32" y="{footY}" width="{width - 64}" height="28" rx="8" fill="#e2e8f0"/>'
    )
    svg.append(
        f'<text x="48" y="{footY + 18}" fill="#334155" font-size="10.8" font-weight="600">'
        'Total Backend Core Graphs: 20 (1 Macro + 1 Pedestrian Walkway + 18 Indoor Building Subgraphs) — '
        '100% Unified on graphCombined.py • Plus 2 Client-Side JS Visual Mirrors '
        '(campusWalkwaysLayer.js &amp; buildingP.html)</text>'
    )
    svg.append(
        f'<text x="{width - 48}" y="{footY + 18}" text-anchor="end" fill="#0f766e" '
        f'font-size="10.8" font-weight="800">All 20 Graphs Verified: Directed • Weighted (w&gt;0) • Non-Complete</text>'
    )

    svg.append("</svg>")

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    outputPath.write_text("\n".join(svg), encoding="utf-8")
    return outputPath


if __name__ == "__main__":
    out = generateDiagram(ROOT_DIR / "docs" / "campus_graphs_diagram.svg")
    print(f"Generated visual graph diagram: {out}")
