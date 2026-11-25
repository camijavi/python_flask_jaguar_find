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
from .i18n import t, normalize_language


def formatHumanWalkingTime(totalDistanceMeters: float, lang: str = "spa") -> str:
    """Converts Dijkstra metric weight sum into human-readable walking duration."""
    activeLang = normalize_language(lang)
    if totalDistanceMeters <= 0:
        return t("navigation.time_already_here", lang=activeLang)
    if totalDistanceMeters < 45.0:
        return t("navigation.time_very_close", lang=activeLang)
    mins = max(1, math.ceil(totalDistanceMeters / 72.0))
    return t("navigation.time_walking_min", lang=activeLang, minutes=mins)


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
    conj = t("navigation.conjunction_and", lang=normalize_language(lang))
    return f"{picked[0]}{conj}{picked[1]}"


def _headlineForManeuver(maneuver: str, lang: str) -> str:
    activeLang = normalize_language(lang)
    validKeys = {
        "start", "straight", "slight_right", "right", "slight_left", "left",
        "uturn", "crosswalk", "skybridge", "stairs_up", "stairs_down",
        "stairs", "ramp", "enter", "exit", "arrive",
        "indoor_location", "access_notice",
    }
    key = maneuver if maneuver in validKeys else "straight"
    return t(f"navigation.headlines.{key}", lang=activeLang)


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
    activeLang = normalize_language(lang)
    if len(nodes) < 2:
        n0 = nodes[0]
        arrText = t("navigation.steps.already_at_place", lang=activeLang, dest=destDisplayName)
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
        arrText = t("navigation.arrived_at_destination", lang=activeLang, destNode=destDisplayName)
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
    activeLang = normalize_language(lang)
    passTail = t("navigation.steps.pass_clause", lang=activeLang, passed=passedClause) if passedClause else ""
    viaTail = t("navigation.steps.via_indoor", lang=activeLang) if env == "indoor" else ""

    if maneuver == "skybridge":
        return t("navigation.steps.skybridge", lang=activeLang, target=targetLabel)
    if maneuver == "crosswalk":
        return t("navigation.steps.crosswalk", lang=activeLang, target=targetLabel)
    if maneuver == "stairs":
        return t("navigation.steps.stairs", lang=activeLang, target=targetLabel)
    if maneuver == "ramp":
        return t("navigation.steps.ramp", lang=activeLang, pass_tail=passTail, target=targetLabel)
    if maneuver == "enter":
        if turnAnchor:
            return t("navigation.steps.enter_anchor", lang=activeLang, anchor=turnAnchor, pass_tail=passTail, target=targetLabel)
        return t("navigation.steps.enter_generic", lang=activeLang, pass_tail=passTail, target=targetLabel)
    if maneuver == "exit":
        if turnAnchor:
            return t("navigation.steps.exit_anchor", lang=activeLang, anchor=turnAnchor, pass_tail=passTail, target=targetLabel)
        return t("navigation.steps.exit_generic", lang=activeLang, pass_tail=passTail, target=targetLabel)

    if isFirst:
        originRef = originName or t("navigation.steps.starting_point_default", lang=activeLang)
        key = "navigation.steps.first_indoor" if env == "indoor" else "navigation.steps.first_outdoor"
        return t(key, lang=activeLang, origin=originRef, pass_tail=passTail, target=targetLabel)

    anchorPrefix = t("navigation.steps.anchor_prefix", lang=activeLang, anchor=turnAnchor) if turnAnchor else ""
    maneuverKeyMap = {
        "right": "navigation.steps.turn_right",
        "slight_right": "navigation.steps.turn_slight_right",
        "left": "navigation.steps.turn_left",
        "slight_left": "navigation.steps.turn_slight_left",
        "uturn": "navigation.steps.turn_uturn",
    }
    stepKey = maneuverKeyMap.get(maneuver, "navigation.steps.continue_straight")
    return t(stepKey, lang=activeLang, anchor_prefix=anchorPrefix, via_tail=viaTail, pass_tail=passTail, target=targetLabel)


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

    activeLang = normalize_language(lang)
    buildingDisplay = t(f"nodes.{subgraph.macroNodeId}", lang=activeLang, default=subgraph.name)

    if len(nodes) == 1:
        n0 = nodes[0]
        sx, sy = _nodeSvg(n0)
        if mode == "enter_destination":
            txt = t(
                "navigation.steps.indoor_enter_at_door",
                lang=activeLang,
                building=buildingDisplay,
                room=n0.getName(activeLang),
                floor=n0.floorLevel,
            )
            return [{
                "index": 0,
                "instruction": txt,
                "headline": _headlineForManeuver("arrive", activeLang),
                "maneuver": "arrive",
                "landmark": _shortPlaceName(n0.getName(activeLang)),
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
        txt = t(
            "navigation.steps.indoor_already_here",
            lang=activeLang,
            room=n0.getName(activeLang),
            floor=n0.floorLevel,
        )
        return [{
            "index": 0,
            "instruction": txt,
            "headline": _headlineForManeuver("arrive", activeLang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(n0.getName(activeLang)),
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
            stepKey = "navigation.steps.indoor_stairs_up" if isUp else "navigation.steps.indoor_stairs_down"
            txt = t(stepKey, lang=activeLang, building=buildingDisplay, floor=toFloor)
            steps.append({
                "index": len(steps),
                "instruction": txt,
                "headline": _headlineForManeuver(maneuver, activeLang),
                "maneuver": maneuver,
                "landmark": t("navigation.floor_label", lang=activeLang, floor=toFloor),
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
        interNames = [_shortPlaceName(n.getName(activeLang)) for n in segNodes[1:-1]]
        # Check if this corridor uses an accessible ramp
        usesRamp = any("rampa" in n.name.lower() or "ramp" in n.nodeId.lower() for n in segNodes)
        isExitRun = (mode == "exit_origin" and segIdx == len(segments) - 1)
        isEntryRun = (mode == "enter_destination" and segIdx == 0)

        if isExitRun:
            maneuver = "exit"
            txt = t(
                "navigation.steps.indoor_exit_run",
                lang=activeLang,
                building=buildingDisplay,
                floor=floor,
                start=startN.getName(activeLang),
                end=endN.getName(activeLang),
            )
        elif usesRamp:
            maneuver = "ramp"
            txt = t(
                "navigation.steps.indoor_ramp",
                lang=activeLang,
                building=buildingDisplay,
                floor=floor,
                end=endN.getName(activeLang),
            )
        else:
            maneuver = "enter" if isEntryRun else "straight"
            if len(interNames) == 0:
                if isEntryRun:
                    txt = t(
                        "navigation.steps.indoor_entry_direct",
                        lang=activeLang,
                        building=buildingDisplay,
                        floor=floor,
                        start=startN.getName(activeLang),
                        end=endN.getName(activeLang),
                    )
                else:
                    txt = t(
                        "navigation.steps.indoor_floor_direct",
                        lang=activeLang,
                        floor=floor,
                        end=endN.getName(activeLang),
                    )
            elif len(interNames) <= 2:
                joined = _formatPassedList(interNames, activeLang)
                txt = t(
                    "navigation.steps.indoor_hallway_pass",
                    lang=activeLang,
                    floor=floor,
                    passed=joined,
                    end=endN.getName(activeLang),
                )
            else:
                txt = t(
                    "navigation.steps.indoor_hallway_range",
                    lang=activeLang,
                    floor=floor,
                    first=interNames[0],
                    last=interNames[-1],
                    end=endN.getName(activeLang),
                )

        steps.append({
            "index": len(steps),
            "instruction": txt,
            "headline": _headlineForManeuver(maneuver, activeLang),
            "maneuver": maneuver,
            "landmark": _shortPlaceName(endN.getName(activeLang)),
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
        arrText = t(
            "navigation.steps.indoor_arrived",
            lang=activeLang,
            room=finalN.getName(activeLang),
            floor=finalN.floorLevel,
        )
        steps.append({
            "index": len(steps),
            "instruction": arrText,
            "headline": _headlineForManeuver("arrive", activeLang),
            "maneuver": "arrive",
            "landmark": _shortPlaceName(finalN.getName(activeLang)),
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
        notice = finalN.getAccessNotice(activeLang)
        if notice:
            steps.append({
                "index": len(steps),
                "instruction": t("navigation.access_notice", lang=activeLang, notice=notice),
                "headline": _headlineForManeuver("access_notice", activeLang),
                "maneuver": "arrive",
                "landmark": _shortPlaceName(finalN.getName(activeLang)),
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
