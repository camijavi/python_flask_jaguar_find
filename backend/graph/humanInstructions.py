"""
humanInstructions.py
================================================================================
HUMAN-CENTRIC LANDMARK & RELATIVE-TURN INSTRUCTION GENERATOR (ES / EN)
================================================================================
Translates optimal paths found by Dijkstra on our Weighted, Directed,
Non-Complete Graphs (outdoor pedestrian walkway graph + 18 indoor building
subgraphs) into natural, realistic pedestrian instructions:
  - ZERO metric step counts ("camina 40m") — distances stay purely as internal
    graph edge weights W(e) for Dijkstra & total walking-time estimation.
  - ZERO compass cardinal directions ("al noreste", "al suroeste").
  - Geometric relative turns computed from consecutive path vectors (A -> B -> C):
    straight, slight_left, left, slight_right, right, uturn.
  - Automatic chunking / collapsing of consecutive straight segments and
    multi-floor staircases into concise, landmark-anchored human directions.
  - Full awareness of real pedestrian walkways, doors (PORTALS), crosswalks,
    ramps, stairs, and 2nd-floor covered skybridges.
================================================================================
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from .directedGraph import DirectedGraph, DirectedEdge, Node
from .geoUtils import CampusGeoUtils


def formatHumanWalkingTime(totalDistanceMeters: float, lang: str = "spa") -> str:
    """Converts Dijkstra metric weight sum into human-readable walking duration."""
    if totalDistanceMeters <= 0:
        return "Ya estás aquí" if lang == "spa" else "You are already here"
    if totalDistanceMeters < 45.0:
        return "Muy cerca (menos de 1 min)" if lang == "spa" else "Very close (< 1 min)"
    mins = max(1, math.ceil(totalDistanceMeters / 72.0))
    if lang == "spa":
        return f"~{mins} min caminando"
    return f"~{mins} min walk"


def _computeRelativeTurn(
    pPrev: Tuple[float, float],
    pCurr: Tuple[float, float],
    pNext: Tuple[float, float],
) -> Tuple[str, float]:
    """
    Computes walker-relative turn classification in SVG space (+x right, +y down).
    Returns (maneuverKey, signedAngleDeg).
    Positive angle = clockwise = RIGHT turn; Negative angle = counter-clockwise = LEFT turn.
    """
    ux, uy = pCurr[0] - pPrev[0], pCurr[1] - pPrev[1]
    vx, vy = pNext[0] - pCurr[0], pNext[1] - pCurr[1]
    lenU = math.hypot(ux, uy)
    lenV = math.hypot(vx, vy)
    if lenU < 1.0 or lenV < 1.0:
        return "straight", 0.0

    cross = ux * vy - uy * vx
    dot = ux * vx + uy * vy
    angleDeg = math.degrees(math.atan2(cross, dot))

    absA = abs(angleDeg)
    if absA < 28.0:
        return "straight", angleDeg
    if absA > 142.0:
        return "uturn", angleDeg
    if angleDeg >= 56.0:
        return "right", angleDeg
    if angleDeg >= 28.0:
        return "slight_right", angleDeg
    if angleDeg <= -56.0:
        return "left", angleDeg
    return "slight_left", angleDeg


def _getLookbackPoint(nodes: List[Node], idx: int, minDistPx: float = 14.0) -> Tuple[float, float]:
    curr = nodes[idx]
    for j in range(idx - 1, -1, -1):
        cand = nodes[j]
        if math.hypot(curr.xSvg - cand.xSvg, curr.ySvg - cand.ySvg) >= minDistPx:
            return (cand.xSvg, cand.ySvg)
    prev = nodes[max(0, idx - 1)]
    return (prev.xSvg, prev.ySvg)


def _getLookaheadPoint(nodes: List[Node], idx: int, minDistPx: float = 14.0) -> Tuple[float, float]:
    curr = nodes[idx]
    for j in range(idx + 1, len(nodes)):
        cand = nodes[j]
        if math.hypot(cand.xSvg - curr.xSvg, cand.ySvg - curr.ySvg) >= minDistPx:
            return (cand.xSvg, cand.ySvg)
    nxt = nodes[min(len(nodes) - 1, idx + 1)]
    return (nxt.xSvg, nxt.ySvg)


def _cleanLandmarkLabel(node: Node, lang: str) -> Optional[str]:
    if lang == "spa" and node.landmarkNameSpa:
        return node.landmarkNameSpa
    if lang == "eng" and node.landmarkNameEng:
        return node.landmarkNameEng
    return None


def _shortPlaceName(label: str) -> str:
    if not label:
        return ""
    # Strip redundant leading articles for compact badges/headlines
    cleaned = label.strip()
    for prefix in ("el ", "la ", "los ", "las ", "the "):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    if "(" in cleaned and len(cleaned) > 34:
        cleaned = cleaned.split("(")[0].strip()
    return cleaned[:1].upper() + cleaned[1:] if cleaned else cleaned


def _formatPassedList(landmarks: List[str], lang: str) -> str:
    unique: List[str] = []
    seen = set()
    for lm in landmarks:
        key = _shortPlaceName(lm).lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(lm)
    if not unique:
        return ""
    picked = unique[:2]
    if len(picked) == 1:
        return picked[0]
    conj = " y " if lang == "spa" else " and "
    return f"{picked[0]}{conj}{picked[1]}"


def _headlineForManeuver(maneuver: str, lang: str) -> str:
    spa = {
        "start": "Inicia el recorrido",
        "straight": "Sigue recto",
        "slight_right": "Mantente a la derecha",
        "right": "Gira a la derecha",
        "slight_left": "Mantente a la izquierda",
        "left": "Gira a la izquierda",
        "uturn": "Da media vuelta",
        "crosswalk": "Cruza el paso peatonal",
        "skybridge": "Puente del 2.º piso",
        "stairs_up": "Sube las gradas",
        "stairs_down": "Baja las gradas",
        "stairs": "Usa las gradas",
        "ramp": "Toma la rampa accesible",
        "enter": "Entra al edificio",
        "exit": "Sal al exterior",
        "arrive": "Has llegado",
    }
    eng = {
        "start": "Start route",
        "straight": "Continue straight",
        "slight_right": "Keep right",
        "right": "Turn right",
        "slight_left": "Keep left",
        "left": "Turn left",
        "uturn": "Turn around",
        "crosswalk": "Cross the crosswalk",
        "skybridge": "2nd-floor skybridge",
        "stairs_up": "Go up the stairs",
        "stairs_down": "Go down the stairs",
        "stairs": "Use the stairs",
        "ramp": "Take the accessible ramp",
        "enter": "Enter building",
        "exit": "Exit outside",
        "arrive": "You arrived",
    }
    table = spa if lang == "spa" else eng
    return table.get(maneuver, table["straight"])


def _polishSentence(text: str, lang: str) -> str:
    """Fixes capitalization, Spanish contractions ('a el' -> 'al', 'de el' -> 'del'), and spacing."""
    cleaned = " ".join(text.split())
    if lang == "spa":
        cleaned = cleaned.replace(" a el ", " al ").replace(" A el ", " Al ")
        cleaned = cleaned.replace(" hacia el la ", " hacia la ").replace(" hacia el el ", " hacia el ")
        cleaned = cleaned.replace(" de el ", " del ")
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


def _chunkLengthPx(nodes: List[Node], startIdx: int, endIdx: int) -> float:
    total = 0.0
    for k in range(startIdx, endIdx):
        total += math.hypot(nodes[k + 1].xSvg - nodes[k].xSvg, nodes[k + 1].ySvg - nodes[k].ySvg)
    return total


def buildHumanWalkwaySteps(
    walkwayGraph: DirectedGraph,
    pathNodeIds: List[str],
    edgeMap: Dict[Tuple[str, str], DirectedEdge],
    originDisplayName: str,
    destDisplayName: str,
    lang: str = "spa",
    includeStartStep: bool = True,
    includeArrivalStep: bool = True,
) -> List[Dict[str, Any]]:
    """
    Converts a micro-level pedestrian walkway Dijkstra path into concise,
    landmark-anchored, relative-turn human steps with ZERO meters and ZERO cardinals.
    """
    if not pathNodeIds:
        return []

    nodes = [walkwayGraph.nodes[nid] for nid in pathNodeIds if nid in walkwayGraph.nodes]
    if len(nodes) < 2:
        n0 = nodes[0]
        arrText = (
            f"Ya te encuentras en {destDisplayName}."
            if lang == "spa"
            else f"You are already at {destDisplayName}."
        )
        return [{
            "index": 0,
            "instruction": arrText,
            "headline": _headlineForManeuver("arrive", lang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(destDisplayName),
            "passedLandmarks": [],
            "environment": "ground",
            "floorLevel": n0.floorLevel,
            "x": n0.xSvg,
            "y": n0.ySvg,
            "lat": n0.latitude,
            "lng": n0.longitude,
            "nextBearingDeg": None,
            "buildingId": n0.buildingId,
            "isIndoor": False,
            "nodeIds": [n0.nodeId],
        }]

    # 1. Inspect every edge along the walkway path
    edgeTypes: List[str] = []
    edgeAccessible: List[bool] = []
    for i in range(len(nodes) - 1):
        e = edgeMap.get((nodes[i].nodeId, nodes[i + 1].nodeId))
        wType = e.walkwayType if e else "ground"
        edgeTypes.append(wType)
        edgeAccessible.append(e.isAccessible if e else True)

    # Initial maneuver reflects special starting transitions (skybridge, crosswalk, ramp, stairs)
    firstEnv = edgeTypes[0]
    if firstEnv == "level2":
        initialTrigger = "skybridge"
    elif firstEnv == "crosswalk":
        initialTrigger = "crosswalk"
    elif firstEnv == "stairs" or not edgeAccessible[0]:
        initialTrigger = "stairs"
    elif firstEnv == "ramp":
        initialTrigger = "ramp"
    else:
        initialTrigger = "start" if includeStartStep else "straight"

    # 2. Identify chunk break indices (real walker events: turn, door, crosswalk, skybridge, stairs, ramp)
    chunks: List[Dict[str, Any]] = []
    chunkStart = 0
    chunkTrigger = initialTrigger
    chunkEnv = firstEnv

    for i in range(1, len(nodes) - 1):
        prevEnv = edgeTypes[i - 1]
        nextEnv = edgeTypes[i]
        currNode = nodes[i]

        pPrev = _getLookbackPoint(nodes, i, minDistPx=18.0)
        pCurr = (currNode.xSvg, currNode.ySvg)
        pNext = _getLookaheadPoint(nodes, i, minDistPx=18.0)
        turnManeuver, _ = _computeRelativeTurn(pPrev, pCurr, pNext)

        shouldBreak = False
        nextTrigger = turnManeuver
        curLenPx = _chunkLengthPx(nodes, chunkStart, i)
        remLenPx = _chunkLengthPx(nodes, i, len(nodes) - 1)

        # Special physical transitions ALWAYS break cleanly into a dedicated human step
        if nextEnv != prevEnv:
            if nextEnv == "level2":
                shouldBreak = True
                nextTrigger = "skybridge"
            elif nextEnv == "stairs" or not edgeAccessible[i]:
                shouldBreak = True
                nextTrigger = "stairs"
            elif nextEnv == "ramp":
                shouldBreak = True
                nextTrigger = "ramp"
            elif nextEnv == "crosswalk":
                shouldBreak = True
                nextTrigger = "crosswalk"
            elif prevEnv == "ground" and nextEnv == "indoor":
                shouldBreak = True
                nextTrigger = "enter"
            elif prevEnv == "indoor" and nextEnv == "ground":
                shouldBreak = True
                nextTrigger = "exit"
            elif prevEnv in ("level2", "stairs", "ramp", "crosswalk"):
                shouldBreak = True
                nextTrigger = turnManeuver if turnManeuver != "straight" else "straight"
        elif turnManeuver in ("left", "right", "uturn"):
            # Only emit a separate turn if it's a real corner (not a tiny doorway offset < 28px)
            if curLenPx >= 30.0 and remLenPx >= 26.0:
                shouldBreak = True
                nextTrigger = turnManeuver
        elif turnManeuver in ("slight_left", "slight_right") and _cleanLandmarkLabel(currNode, lang):
            if curLenPx >= 55.0 and remLenPx >= 32.0:
                shouldBreak = True
                nextTrigger = turnManeuver

        if shouldBreak:
            chunks.append({
                "startIdx": chunkStart,
                "endIdx": i,
                "maneuver": chunkTrigger,
                "environment": chunkEnv,
            })
            chunkStart = i
            chunkTrigger = nextTrigger
            chunkEnv = nextEnv

    # Final chunk up to the destination walkway node
    chunks.append({
        "startIdx": chunkStart,
        "endIdx": len(nodes) - 1,
        "maneuver": chunkTrigger,
        "environment": chunkEnv,
    })

    # 2b. Absorb ultra-short transition stubs (< 18px) right before a major event
    #     (e.g. a 5px doorway step right before crosswalk_bot -> crosswalk_top)
    cleanedChunks: List[Dict[str, Any]] = []
    for ch in chunks:
        if cleanedChunks:
            prev = cleanedChunks[-1]
            prevLen = _chunkLengthPx(nodes, prev["startIdx"], prev["endIdx"])
            if prevLen < 18.0 and prev["maneuver"] in ("exit", "straight", "slight_left", "slight_right") and ch["maneuver"] in ("crosswalk", "skybridge", "stairs", "ramp"):
                ch["startIdx"] = prev["startIdx"]
                cleanedChunks[-1] = ch
                continue
            if prevLen < 18.0 and ch["maneuver"] == "enter" and prev["maneuver"] in ("left", "right", "slight_left", "slight_right"):
                ch["startIdx"] = prev["startIdx"]
                cleanedChunks[-1] = ch
                continue
        cleanedChunks.append(ch)
    chunks = cleanedChunks

    # 3. Convert each chunk into natural, human-sounding bilingual text
    steps: List[Dict[str, Any]] = []

    for cIdx, ch in enumerate(chunks):
        sIdx = ch["startIdx"]
        eIdx = ch["endIdx"]
        maneuver = ch["maneuver"]
        env = ch["environment"]
        startNode = nodes[sIdx]
        endNode = nodes[eIdx]
        segNodes = nodes[sIdx : eIdx + 1]

        # Collect passed visual landmarks strictly inside this chunk (excluding junctions & start/end)
        passed: List[str] = []
        endLabel = _cleanLandmarkLabel(endNode, lang)
        startLabel = _cleanLandmarkLabel(startNode, lang)

        # For the final chunk, anchor destination to destDisplayName when available
        isLastChunk = (cIdx == len(chunks) - 1)
        targetLabel = destDisplayName if (isLastChunk and destDisplayName) else (endLabel or endNode.getName(lang))
        if not targetLabel or targetLabel == endNode.nodeId or endNode.portalKind == "junction":
            # Look slightly forward for the nearest recognizable named landmark
            for lookIdx in range(eIdx, len(nodes)):
                if nodes[lookIdx].portalKind == "junction":
                    continue
                candLabel = _cleanLandmarkLabel(nodes[lookIdx], lang)
                if candLabel:
                    targetLabel = candLabel
                    break
            else:
                targetLabel = destDisplayName

        targetShortLower = _shortPlaceName(targetLabel).lower()
        startShortLower = _shortPlaceName(startLabel or originDisplayName).lower()
        for midNode in segNodes[1:-1]:
            if midNode.portalKind == "junction":
                continue
            midLabel = _cleanLandmarkLabel(midNode, lang)
            if not midLabel:
                continue
            midShort = _shortPlaceName(midLabel).lower()
            if midShort and midShort not in (targetShortLower, startShortLower):
                if not any(midShort in _shortPlaceName(p).lower() for p in passed):
                    passed.append(midLabel)

        passedClause = _formatPassedList(passed, lang)
        turnAnchor = startLabel if (startLabel and startNode.portalKind != "junction") else None

        # Compute true compass bearing at start of this chunk for live compass guidance
        lookAheadNode = nodes[min(eIdx, sIdx + 1)]
        if sIdx + 1 < eIdx and math.hypot(lookAheadNode.xSvg - startNode.xSvg, lookAheadNode.ySvg - startNode.ySvg) < 10.0:
            lookAheadNode = nodes[min(eIdx, sIdx + 2)]
        bearingDeg = round(
            CampusGeoUtils.calculateCompassBearing(
                startNode.latitude, startNode.longitude,
                lookAheadNode.latitude, lookAheadNode.longitude
            ),
            1,
        )

        # Build natural phrasing per maneuver & physical environment
        instruction = _polishSentence(
            _composeWalkwaySentence(
                maneuver=maneuver,
                env=env,
                originName=originDisplayName if cIdx == 0 else (turnAnchor or ""),
                turnAnchor=turnAnchor,
                targetLabel=targetLabel,
                passedClause=passedClause,
                isFirst=(cIdx == 0),
                lang=lang,
            ),
            lang=lang,
        )

        steps.append({
            "index": len(steps),
            "instruction": instruction,
            "headline": _headlineForManeuver(maneuver, lang),
            "maneuver": maneuver,
            "landmark": _shortPlaceName(targetLabel),
            "passedLandmarks": [_shortPlaceName(p) for p in passed[:2]],
            "environment": env,
            "floorLevel": 2 if env == "level2" else 1,
            "x": startNode.xSvg,
            "y": startNode.ySvg,
            "targetX": endNode.xSvg,
            "targetY": endNode.ySvg,
            "lat": startNode.latitude,
            "lng": startNode.longitude,
            "targetLat": endNode.latitude,
            "targetLng": endNode.longitude,
            "nextBearingDeg": bearingDeg,
            "buildingId": endNode.buildingId or startNode.buildingId,
            "isIndoor": env == "indoor",
            "nodeIds": [n.nodeId for n in segNodes],
        })

    if includeArrivalStep:
        finalNode = nodes[-1]
        arrText = (
            f"Has llegado a tu destino: {destDisplayName}."
            if lang == "spa"
            else f"You have arrived at your destination: {destDisplayName}."
        )
        steps.append({
            "index": len(steps),
            "instruction": arrText,
            "headline": _headlineForManeuver("arrive", lang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(destDisplayName),
            "passedLandmarks": [],
            "environment": edgeTypes[-1] if edgeTypes else "ground",
            "floorLevel": finalNode.floorLevel,
            "x": finalNode.xSvg,
            "y": finalNode.ySvg,
            "targetX": finalNode.xSvg,
            "targetY": finalNode.ySvg,
            "lat": finalNode.latitude,
            "lng": finalNode.longitude,
            "targetLat": finalNode.latitude,
            "targetLng": finalNode.longitude,
            "nextBearingDeg": None,
            "buildingId": finalNode.buildingId,
            "isIndoor": False,
            "nodeIds": [finalNode.nodeId],
        })

    return steps


def _composeWalkwaySentence(
    maneuver: str,
    env: str,
    originName: str,
    turnAnchor: Optional[str],
    targetLabel: str,
    passedClause: str,
    isFirst: bool,
    lang: str,
) -> str:
    if lang == "spa":
        passTail = f", pasando {passedClause}," if passedClause else ""
        viaTail = " por el pasillo interior" if env == "indoor" else ""

        if maneuver == "skybridge":
            return f"Sube y cruza el puente techado del 2.º piso hacia {targetLabel}."
        if maneuver == "crosswalk":
            return f"Cruza el paso peatonal (cebra) hacia {targetLabel}."
        if maneuver == "stairs":
            return f"Usa las gradas y avanza hacia {targetLabel}."
        if maneuver == "ramp":
            return f"Toma la rampa accesible{passTail} hacia {targetLabel}."
        if maneuver == "enter":
            if turnAnchor:
                return f"Entra por {turnAnchor} y avanza por el pasillo{passTail} hacia {targetLabel}."
            return f"Entra al edificio y sigue por el pasillo{passTail} hacia {targetLabel}."
        if maneuver == "exit":
            if turnAnchor:
                return f"Sal por {turnAnchor} y dirígete{passTail} hacia {targetLabel}."
            return f"Sal al camino exterior{passTail} hacia {targetLabel}."

        if isFirst:
            originRef = originName or "tu punto de partida"
            if env == "indoor":
                return f"Desde {originRef}, avanza por el pasillo{passTail} hacia {targetLabel}."
            return f"Desde {originRef}, avanza por el camino peatonal{passTail} hacia {targetLabel}."

        anchorPrefix = f"Al llegar a {turnAnchor}, " if turnAnchor else ""
        if maneuver == "right":
            return f"{anchorPrefix}gira a la derecha{viaTail}{passTail} hacia {targetLabel}."
        if maneuver == "slight_right":
            return f"{anchorPrefix}mantente ligeramente a la derecha{viaTail}{passTail} hacia {targetLabel}."
        if maneuver == "left":
            return f"{anchorPrefix}gira a la izquierda{viaTail}{passTail} hacia {targetLabel}."
        if maneuver == "slight_left":
            return f"{anchorPrefix}mantente ligeramente a la izquierda{viaTail}{passTail} hacia {targetLabel}."
        if maneuver == "uturn":
            return f"{anchorPrefix}da media vuelta y dirígete{passTail} hacia {targetLabel}."
        return f"{anchorPrefix}sigue recto{viaTail}{passTail} hacia {targetLabel}."

    # English phrasing
    passTail = f", passing {passedClause}," if passedClause else ""
    viaTail = " through the indoor corridor" if env == "indoor" else ""

    if maneuver == "skybridge":
        return f"Cross the 2nd-floor covered skybridge toward {targetLabel}."
    if maneuver == "crosswalk":
        return f"Cross the pedestrian crosswalk toward {targetLabel}."
    if maneuver == "stairs":
        return f"Take the stairs and continue toward {targetLabel}."
    if maneuver == "ramp":
        return f"Follow the accessible ramp{passTail} toward {targetLabel}."
    if maneuver == "enter":
        if turnAnchor:
            return f"Enter through {turnAnchor} and follow the corridor{passTail} toward {targetLabel}."
        return f"Enter the building and follow the hallway{passTail} toward {targetLabel}."
    if maneuver == "exit":
        if turnAnchor:
            return f"Exit through {turnAnchor} and head{passTail} toward {targetLabel}."
        return f"Exit onto the outdoor walkway{passTail} toward {targetLabel}."

    if isFirst:
        originRef = originName or "your starting point"
        if env == "indoor":
            return f"From {originRef}, follow the corridor{passTail} toward {targetLabel}."
        return f"From {originRef}, follow the pedestrian walkway{passTail} toward {targetLabel}."

    anchorPrefix = f"At {turnAnchor}, " if turnAnchor else ""
    if maneuver == "right":
        return f"{anchorPrefix}turn right{viaTail}{passTail} toward {targetLabel}."
    if maneuver == "slight_right":
        return f"{anchorPrefix}keep slightly right{viaTail}{passTail} toward {targetLabel}."
    if maneuver == "left":
        return f"{anchorPrefix}turn left{viaTail}{passTail} toward {targetLabel}."
    if maneuver == "slight_left":
        return f"{anchorPrefix}keep slightly left{viaTail}{passTail} toward {targetLabel}."
    if maneuver == "uturn":
        return f"{anchorPrefix}turn around and head{passTail} toward {targetLabel}."
    return f"{anchorPrefix}continue straight{viaTail}{passTail} toward {targetLabel}."


def buildHumanIndoorSteps(
    subgraph,
    pathNodeIds: List[str],
    lang: str = "spa",
    mode: str = "standalone",  # "standalone" | "exit_origin" | "enter_destination"
    buildingAnchorSvg: Optional[Tuple[float, float]] = None,
) -> List[Dict[str, Any]]:
    """
    Converts an indoor BuildingSubgraph Dijkstra path into grouped, human-friendly
    floor & hallway instructions with ZERO meters and ZERO cardinal directions.
    Collapses multi-floor staircases and consecutive corridor rooms automatically.
    """
    if not pathNodeIds:
        return []

    nodes = [subgraph.graph.nodes[nid] for nid in pathNodeIds if nid in subgraph.graph.nodes]
    if not nodes:
        return []

    def _nodeSvg(n: Node) -> Tuple[float, float]:
        if buildingAnchorSvg:
            return buildingAnchorSvg
        if n.latitude and n.longitude:
            return CampusGeoUtils.gpsToSvg(n.latitude, n.longitude)
        return (n.xSvg, n.ySvg)

    if len(nodes) == 1:
        n0 = nodes[0]
        sx, sy = _nodeSvg(n0)
        if mode == "enter_destination":
            txt = (
                f"Al ingresar a {subgraph.name}, encontrarás {n0.name} justo en el acceso (Piso {n0.floorLevel})."
                if lang == "spa"
                else f"Upon entering {subgraph.name}, you will find {n0.name} right by the entrance (Floor {n0.floorLevel})."
            )
            return [{
                "index": 0,
                "instruction": txt,
                "headline": _headlineForManeuver("arrive", lang),
                "maneuver": "arrive",
                "landmark": _shortPlaceName(n0.name),
                "passedLandmarks": [],
                "environment": "indoor",
                "floorLevel": n0.floorLevel,
                "x": sx, "y": sy,
                "lat": n0.latitude, "lng": n0.longitude,
                "nextBearingDeg": None,
                "buildingId": subgraph.macroNodeId,
                "isIndoor": True,
                "nodeIds": [n0.nodeId],
            }]
        if mode == "exit_origin":
            return []
        txt = (
            f"Ya te encuentras en {n0.name} (Piso {n0.floorLevel})."
            if lang == "spa"
            else f"You are already at {n0.name} (Floor {n0.floorLevel})."
        )
        return [{
            "index": 0,
            "instruction": txt,
            "headline": _headlineForManeuver("arrive", lang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(n0.name),
            "passedLandmarks": [],
            "environment": "indoor",
            "floorLevel": n0.floorLevel,
            "x": sx, "y": sy,
            "lat": n0.latitude, "lng": n0.longitude,
            "nextBearingDeg": None,
            "buildingId": subgraph.macroNodeId,
            "isIndoor": True,
            "nodeIds": [n0.nodeId],
        }]

    # Group consecutive edges into horizontal runs (same floor) and vertical climbs/descents
    segments: List[Dict[str, Any]] = []
    i = 0
    while i < len(nodes) - 1:
        u = nodes[i]
        v = nodes[i + 1]
        if u.floorLevel != v.floorLevel:
            # Collapse multi-floor vertical staircase into ONE step!
            direction = "up" if v.floorLevel > u.floorLevel else "down"
            vStart = i
            while i < len(nodes) - 1 and (
                (direction == "up" and nodes[i + 1].floorLevel > nodes[i].floorLevel)
                or (direction == "down" and nodes[i + 1].floorLevel < nodes[i].floorLevel)
            ):
                i += 1
            segments.append({
                "kind": f"stairs_{direction}",
                "nodes": nodes[vStart : i + 1],
                "fromFloor": nodes[vStart].floorLevel,
                "toFloor": nodes[i].floorLevel,
            })
        else:
            # Horizontal run on the same floor
            hStart = i
            floor = u.floorLevel
            while i < len(nodes) - 1 and nodes[i + 1].floorLevel == floor:
                i += 1
            segments.append({
                "kind": "corridor",
                "nodes": nodes[hStart : i + 1],
                "floor": floor,
            })

    steps: List[Dict[str, Any]] = []
    for segIdx, seg in enumerate(segments):
        segNodes = seg["nodes"]
        startN = segNodes[0]
        endN = segNodes[-1]
        sx, sy = _nodeSvg(startN)
        ex, ey = _nodeSvg(endN)

        if seg["kind"] in ("stairs_up", "stairs_down"):
            isUp = seg["kind"] == "stairs_up"
            maneuver = "stairs_up" if isUp else "stairs_down"
            toFloor = seg["toFloor"]
            if lang == "spa":
                verb = "Sube" if isUp else "Baja"
                txt = f"{verb} por las escaleras de {subgraph.name} hasta el Piso {toFloor}."
            else:
                verb = "Go up" if isUp else "Go down"
                txt = f"{verb} the stairs in {subgraph.name} to Floor {toFloor}."
            steps.append({
                "index": len(steps),
                "instruction": txt,
                "headline": _headlineForManeuver(maneuver, lang),
                "maneuver": maneuver,
                "landmark": f"Piso {toFloor}" if lang == "spa" else f"Floor {toFloor}",
                "passedLandmarks": [],
                "environment": "stairs",
                "floorLevel": toFloor,
                "x": sx, "y": sy,
                "targetX": ex, "targetY": ey,
                "lat": startN.latitude, "lng": startN.longitude,
                "nextBearingDeg": None,
                "buildingId": subgraph.macroNodeId,
                "isIndoor": True,
                "nodeIds": [n.nodeId for n in segNodes],
            })
            continue

        # Horizontal corridor run on floor
        floor = seg["floor"]
        interNames = [_shortPlaceName(n.name) for n in segNodes[1:-1]]
        # Check if this corridor uses an accessible ramp
        usesRamp = any("rampa" in n.name.lower() or "ramp" in n.nodeId.lower() for n in segNodes)
        isExitRun = (mode == "exit_origin" and segIdx == len(segments) - 1)
        isEntryRun = (mode == "enter_destination" and segIdx == 0)

        if isExitRun:
            maneuver = "exit"
            if lang == "spa":
                txt = f"En {subgraph.name} (Piso {floor}), avanza desde {startN.name} hacia la salida ({endN.name})."
            else:
                txt = f"Inside {subgraph.name} (Floor {floor}), head from {startN.name} toward the exit ({endN.name})."
        elif usesRamp:
            maneuver = "ramp"
            if lang == "spa":
                txt = f"Usa la rampa accesible en {subgraph.name} (Piso {floor}) hacia {endN.name}."
            else:
                txt = f"Use the accessible ramp in {subgraph.name} (Floor {floor}) toward {endN.name}."
        else:
            maneuver = "enter" if isEntryRun else "straight"
            if len(interNames) == 0:
                if lang == "spa":
                    if isEntryRun:
                        txt = f"Dentro de {subgraph.name} (Piso {floor}), dirígete desde {startN.name} hacia {endN.name}."
                    else:
                        txt = f"En el Piso {floor}, dirígete hacia {endN.name}."
                else:
                    if isEntryRun:
                        txt = f"Inside {subgraph.name} (Floor {floor}), head from {startN.name} toward {endN.name}."
                    else:
                        txt = f"On Floor {floor}, head toward {endN.name}."
            elif len(interNames) <= 2:
                joined = _formatPassedList(interNames, lang)
                if lang == "spa":
                    txt = f"Avanza por el pasillo del Piso {floor} pasando {joined} hasta llegar a {endN.name}."
                else:
                    txt = f"Follow the Floor {floor} hallway passing {joined} until you reach {endN.name}."
            else:
                firstPass = interNames[0]
                lastPass = interNames[-1]
                if lang == "spa":
                    txt = f"Recorre el pasillo del Piso {floor} pasando desde {firstPass} hasta {lastPass} para llegar a {endN.name}."
                else:
                    txt = f"Follow the Floor {floor} hallway past {firstPass} through {lastPass} to reach {endN.name}."

        steps.append({
            "index": len(steps),
            "instruction": txt,
            "headline": _headlineForManeuver(maneuver, lang),
            "maneuver": maneuver,
            "landmark": _shortPlaceName(endN.name),
            "passedLandmarks": interNames[:2],
            "environment": "ramp" if usesRamp else "indoor",
            "floorLevel": floor,
            "x": sx, "y": sy,
            "targetX": ex, "targetY": ey,
            "lat": startN.latitude, "lng": startN.longitude,
            "nextBearingDeg": None,
            "buildingId": subgraph.macroNodeId,
            "isIndoor": True,
            "nodeIds": [n.nodeId for n in segNodes],
        })

    # Arrival step for standalone or enter_destination
    if mode in ("standalone", "enter_destination"):
        finalN = nodes[-1]
        fx, fy = _nodeSvg(finalN)
        arrText = (
            f"Has llegado a {finalN.name} (Piso {finalN.floorLevel})."
            if lang == "spa"
            else f"You have arrived at {finalN.name} (Floor {finalN.floorLevel})."
        )
        steps.append({
            "index": len(steps),
            "instruction": arrText,
            "headline": _headlineForManeuver("arrive", lang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(finalN.name),
            "passedLandmarks": [],
            "environment": "indoor",
            "floorLevel": finalN.floorLevel,
            "x": fx, "y": fy,
            "targetX": fx, "targetY": fy,
            "lat": finalN.latitude, "lng": finalN.longitude,
            "nextBearingDeg": None,
            "buildingId": subgraph.macroNodeId,
            "isIndoor": True,
            "nodeIds": [finalN.nodeId],
        })

        # Append Gateway Pattern biosecurity / restricted notice if present
        notice = finalN.getAccessNotice(lang)
        if notice:
            steps.append({
                "index": len(steps),
                "instruction": f"Aviso de acceso: {notice}" if lang == "spa" else f"Access notice: {notice}",
                "headline": "Aviso de acceso" if lang == "spa" else "Access notice",
                "maneuver": "arrive",
                "landmark": _shortPlaceName(finalN.name),
                "passedLandmarks": [],
                "environment": "indoor",
                "floorLevel": finalN.floorLevel,
                "x": fx, "y": fy,
                "targetX": fx, "targetY": fy,
                "lat": finalN.latitude, "lng": finalN.longitude,
                "nextBearingDeg": None,
                "buildingId": subgraph.macroNodeId,
                "isIndoor": True,
                "nodeIds": [finalN.nodeId],
            })

    return steps
