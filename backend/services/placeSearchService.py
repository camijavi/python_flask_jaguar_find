"""
placeSearchService.py
================================================================================
UNIFIED CAMPUS PLACE INDEXING, NORMALIZATION & SEARCH SERVICE
================================================================================
Provides deterministic, complete, pollution-free indexing and search across
PLACES_CATALOG and all 18 indoor building subgraphs (buildings.txt +
coordenadas.txt).

Key guarantees:
  - Case-insensitive, accent/diacritic-insensitive matching
  - Whitespace-tolerant and separator-tolerant room code matching
    ("B210", "b210", "B-210", "B 210", "  b   210  " all resolve identically)
  - Zero keyword pollution from parent building room-range titles
  - Zero duplicate room entries when catalog + subgraph overlap
  - Complete result sets (exact and partial matches) ranked by relevance with
    natural alphanumeric ordering (never dropping valid matches)
================================================================================
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.data.campusCategories import CampusCategory
from backend.data.placesCatalog import PLACES_CATALOG
from backend.data.campusLocalization import (
    getLocalizedPlaceName,
    getLocalizedPlaceNotes,
    getPlaceBilingualNames,
)
from backend.graph.navigationService import globalNavigationService
from backend.i18n import t, normalize_language
from backend.subgraphs import getAllBuildingSubgraphs

_CAMEL_BOUNDARY_RE = re.compile(r"([a-z0-9])([A-Z])")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_ROOM_PREFIX_SPACE_RE = re.compile(r"\b([a-z])\s+(\d)")
_ROOM_CODE_RE = re.compile(r"\b([a-z])\s*[-_]?\s*(\d{3}[a-z]?)\b")
_EXACT_ROOM_CODE_RE = re.compile(r"^[a-z]\d{3}[a-z]?$")
_NATURAL_CHUNK_RE = re.compile(r"(\d+)")

_ROOM_LIKE_CATEGORIES = {
    CampusCategory.CLASSROOM,
    CampusCategory.MEDICAL_LAB,
    CampusCategory.DENTAL_LAB,
    CampusCategory.AUDITORIUM,
}


def stripAccents(text: str) -> str:
    """Decomposes Unicode text and removes combining diacritical marks."""
    decomposed = unicodedata.normalize("NFD", str(text or ""))
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalizeText(text: str) -> str:
    """Case- and accent-insensitive normalization with collapsed whitespace."""
    cleaned = stripAccents(text).strip().lower()
    return " ".join(cleaned.split())


def canonicalizeSearchText(text: str) -> str:
    """
    Normalizes text for room/facility search:
      - Splits camelCase boundaries (e.g. 'classroomB210' -> 'classroom B210')
      - Strips accents and lowercases
      - Replaces punctuation/hyphens/underscores with single spaces
      - Collapses standalone single-letter + space + digits ('b 210' -> 'b210',
        'b 2' -> 'b2') while keeping normal word boundaries intact
        ('planta 1' stays 'planta 1', never 'planta1')
    """
    raw = str(text or "")
    spaced = _CAMEL_BOUNDARY_RE.sub(r"\1 \2", raw)
    stripped = stripAccents(spaced).lower()
    alnumSpaced = _NON_ALNUM_RE.sub(" ", stripped).strip()
    return _ROOM_PREFIX_SPACE_RE.sub(r"\1\2", alnumSpaced)


def compactSearchText(text: str) -> str:
    """Removes all non-alphanumeric characters after accent stripping."""
    return _NON_ALNUM_RE.sub("", stripAccents(text).lower())


def extractRoomCodes(text: str) -> Set[str]:
    """Extracts canonical room codes (e.g. 'b210', 'c108', 'p306b') from text."""
    spaced = _CAMEL_BOUNDARY_RE.sub(r"\1 \2", str(text or ""))
    stripped = stripAccents(spaced).lower()
    return {f"{m.group(1)}{m.group(2)}" for m in _ROOM_CODE_RE.finditer(stripped)}


def naturalSortKey(text: str) -> Tuple[Any, ...]:
    """Natural sort key so B201, B202, ..., B209, B210 sort numerically."""
    canon = canonicalizeSearchText(text)
    parts: List[Any] = []
    for chunk in _NATURAL_CHUNK_RE.split(canon):
        if chunk.isdigit():
            parts.append((0, int(chunk)))
        else:
            parts.append((1, chunk))
    return tuple(parts)


def shortBuildingLabel(localizedName: str) -> str:
    """
    Returns the clean short building label without parenthetical room ranges
    (e.g. 'Edificio B (Aulas B101-B210 & Farmacia)' -> 'Edificio B') so room
    ranges never pollute individual room keywords or location notes.
    """
    base = str(localizedName or "").split("(")[0].strip()
    return base or str(localizedName or "").strip()


def _expandRoomCodeKeywords(codes: Set[str]) -> List[str]:
    expanded: List[str] = []
    for code in sorted(codes):
        letter, rest = code[0], code[1:]
        expanded.extend([code, f"{letter}-{rest}", f"{letter} {rest}"])
    return expanded


def _dedupeKeywords(keywords: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for kw in keywords:
        val = str(kw or "").strip()
        if not val:
            continue
        norm = normalizeText(val)
        if norm not in seen:
            seen.add(norm)
            out.append(val)
    return out


def buildIndexedPlaces(lang: str = "spa") -> List[Dict[str, Any]]:
    """
    Builds the complete, deduplicated list of campus places combining
    PLACES_CATALOG and all 18 indoor building subgraphs with localized
    names & location notes while preserving full bilingual searchability.
    """
    activeLang = normalize_language(lang)
    macroGraph = globalNavigationService.graph
    subgraphs = getAllBuildingSubgraphs()

    def _getShortBuilding(buildingId: str, targetLang: str = activeLang, fallback: str = "") -> str:
        macroNode = macroGraph.getNode(buildingId)
        if macroNode:
            return shortBuildingLabel(macroNode.getName(targetLang))
        return shortBuildingLabel(fallback or buildingId)

    combinedPlaces: List[Dict[str, Any]] = []
    seenNameKeys: Set[Tuple[str, str]] = set()
    catalogRoomCodesByBuilding: Dict[str, Set[str]] = {}

    # 1. Index every entry from PLACES_CATALOG (canonical individual rooms & POIs)
    for rawPlace in PLACES_CATALOG:
        place = dict(rawPlace)
        parentId = place.get("parentBuildingId", "")
        parentNorm = normalizeText(parentId)
        shortBldg = _getShortBuilding(parentId, activeLang)
        shortBldgSpa = _getShortBuilding(parentId, "spa")
        shortBldgEng = _getShortBuilding(parentId, "eng")

        localizedName = getLocalizedPlaceName(rawPlace, activeLang)
        localizedNotes = getLocalizedPlaceNotes(rawPlace, activeLang)
        bilingualNames = getPlaceBilingualNames(rawPlace)

        place["name"] = localizedName
        place["locationNotes"] = localizedNotes

        ownCodes = extractRoomCodes(localizedName) | extractRoomCodes(rawPlace.get("name", "")) | extractRoomCodes(place.get("placeId", ""))
        for kw in place.get("keywords", []):
            ownCodes |= extractRoomCodes(kw)

        keywords = list(place.get("keywords", []))
        keywords.extend(bilingualNames)
        keywords.extend(_expandRoomCodeKeywords(ownCodes))
        for bLabel in (shortBldg, shortBldgSpa, shortBldgEng):
            if bLabel:
                keywords.append(bLabel)
        place["keywords"] = _dedupeKeywords(keywords)
        place["buildingName"] = shortBldg
        place["roomCodes"] = sorted(ownCodes)

        combinedPlaces.append(place)
        for nameVariant in bilingualNames:
            seenNameKeys.add((parentNorm, canonicalizeSearchText(nameVariant)))
        if ownCodes:
            catalogRoomCodesByBuilding.setdefault(parentNorm, set()).update(ownCodes)

    # 2. Index supplementary indoor nodes from all 18 building subgraphs
    for _, sg in subgraphs.items():
        parentId = sg.macroNodeId
        parentNorm = normalizeText(parentId)
        shortBldg = _getShortBuilding(parentId, activeLang, fallback=sg.getName(activeLang))
        shortBldgSpa = _getShortBuilding(parentId, "spa", fallback=sg.getName("spa"))
        shortBldgEng = _getShortBuilding(parentId, "eng", fallback=sg.getName("eng"))

        aliasesByNodeId: Dict[str, List[str]] = {}
        for alias, targetNodeId in sg.roomAliases.items():
            aliasesByNodeId.setdefault(targetNodeId, []).append(alias)

        coveredCodes = catalogRoomCodesByBuilding.get(parentNorm, set())

        for node in sg.getAllNodes():
            localizedName = node.getName(activeLang)
            spaName = node.getName("spa")
            engName = node.getName("eng")
            candidateNameKeys = [
                (parentNorm, canonicalizeSearchText(variant))
                for variant in (localizedName, spaName, engName)
                if variant
            ]
            if any(nk in seenNameKeys for nk in candidateNameKeys):
                continue

            nodeAliases = aliasesByNodeId.get(node.nodeId, [])
            nodeCodes = extractRoomCodes(localizedName) | extractRoomCodes(spaName) | extractRoomCodes(node.nodeId)
            for alias in nodeAliases:
                nodeCodes |= extractRoomCodes(alias)

            # Avoid duplicate entries for combined/mirrored room nodes when ALL
            # of their rooms are already individually represented in PLACES_CATALOG
            # (e.g. 'Aulas B209 y B210' when both 'Aula B209' and 'Aula B210'
            # are already indexed individually in buildingB).
            if (
                nodeCodes
                and node.category in _ROOM_LIKE_CATEGORIES
                and nodeCodes.issubset(coveredCodes)
            ):
                continue

            for nk in candidateNameKeys:
                seenNameKeys.add(nk)

            nodeKeywords = [node.nodeId, spaName, engName]
            nodeKeywords.extend(nodeAliases)
            nodeKeywords.extend(_expandRoomCodeKeywords(nodeCodes))
            for bLabel in (shortBldg, shortBldgSpa, shortBldgEng):
                if bLabel:
                    nodeKeywords.append(bLabel)

            combinedPlaces.append({
                "placeId": node.nodeId,
                "name": localizedName,
                "category": node.category,
                "parentBuildingId": parentId,
                "buildingName": shortBldg,
                "floorLevel": node.floorLevel,
                "isAccessible": node.category != CampusCategory.STAIRS,
                "latitude": node.latitude,
                "longitude": node.longitude,
                "locationNotes": t(
                    "api.map_floor_note",
                    lang=activeLang,
                    floor=node.floorLevel,
                    building=shortBldg,
                ),
                "keywords": _dedupeKeywords(nodeKeywords),
                "roomCodes": sorted(nodeCodes),
            })

    return combinedPlaces


def _scorePlaceMatch(
    place: Dict[str, Any],
    qCanon: str,
    qCompact: str,
    qTokens: List[str],
) -> Optional[int]:
    """
    Returns a relevance tier (lower is better, 0 = exact match) if `place`
    matches the query, or None if it does not match.
    """
    nameRaw = place.get("name", "")
    placeIdRaw = place.get("placeId", "")
    notesRaw = place.get("locationNotes", "")
    buildingRaw = place.get("buildingName", "")
    keywordsRaw = place.get("keywords", []) or []

    nameCanon = canonicalizeSearchText(nameRaw)
    placeIdCanon = canonicalizeSearchText(placeIdRaw)
    notesCanon = canonicalizeSearchText(notesRaw)
    buildingCanon = canonicalizeSearchText(buildingRaw)
    keywordsCanon = [canonicalizeSearchText(kw) for kw in keywordsRaw]

    roomCodes: Set[str] = set(place.get("roomCodes") or [])
    if not roomCodes:
        roomCodes = extractRoomCodes(nameRaw) | extractRoomCodes(placeIdRaw)
        for kw in keywordsRaw:
            roomCodes |= extractRoomCodes(kw)

    # Tier 0: Exact room code, exact name, or exact placeId match
    if qCanon in roomCodes or qCanon == nameCanon or qCanon == placeIdCanon:
        return 0
    if qCompact and qCompact in roomCodes:
        return 0

    # Tier 1: Room code prefix match (e.g. 'b2' -> b201..b210, 'b20' -> b201..b209)
    if any(code.startswith(qCanon) for code in roomCodes):
        return 1

    # Tier 2: Name starts with query or any token in name starts with query
    nameWords = nameCanon.split()
    if nameCanon.startswith(qCanon) or any(w.startswith(qCanon) for w in nameWords):
        return 2

    # Tier 3: Substring match inside name (or alpha-only compact match for >=4 chars like 'camcam')
    allowCompact = len(qCompact) >= 4 and qCompact.isalpha()
    if qCanon in nameCanon:
        return 3
    if allowCompact and qCompact in compactSearchText(nameRaw):
        return 3

    # Tier 4: Exact or prefix match in keywords or placeId
    if any(
        kw == qCanon or kw.startswith(qCanon) or any(w.startswith(qCanon) for w in kw.split())
        for kw in keywordsCanon
        if kw
    ):
        return 4
    if placeIdCanon and (placeIdCanon.startswith(qCanon) or any(w.startswith(qCanon) for w in placeIdCanon.split())):
        return 4

    # Tier 5: Substring match in keywords or placeId
    if any(qCanon in kw for kw in keywordsCanon if kw):
        return 5
    if qCanon in placeIdCanon:
        return 5
    if allowCompact and (
        qCompact in compactSearchText(placeIdRaw)
        or any(qCompact in compactSearchText(kw) for kw in keywordsRaw)
    ):
        return 5

    # Tier 6: Multi-token AND match across combined fields (e.g. 'aula b 210', 'edificio b 210', 'piso 2 b')
    if len(qTokens) >= 2:
        floorNum = place.get("floorLevel")
        floorText = f"piso {floorNum} floor {floorNum}" if floorNum is not None else ""
        combinedCanon = " ".join(
            part for part in [nameCanon, placeIdCanon, buildingCanon, notesCanon, floorText, *keywordsCanon] if part
        )
        combinedCompact = compactSearchText(combinedCanon)
        allMatched = True
        for tok in qTokens:
            tokCompact = compactSearchText(tok)
            if tok in combinedCanon or any(code.startswith(tok) for code in roomCodes):
                continue
            if len(tokCompact) >= 4 and tokCompact.isalpha() and tokCompact in combinedCompact:
                continue
            allMatched = False
            break
        if allMatched:
            return 6

    # Tier 7: Location notes or short building name match
    # Skip incidental neighbor mentions in locationNotes (e.g. "next to C-103")
    # when the user explicitly queried an exact room code.
    if not _EXACT_ROOM_CODE_RE.fullmatch(qCanon):
        if qCanon in notesCanon or (buildingCanon and qCanon in buildingCanon):
            return 7

    return None


def searchPlaces(
    places: List[Dict[str, Any]],
    query: str = "",
    category: Optional[str] = None,
    floor: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Filters and ranks places with case-insensitive, accent-insensitive,
    whitespace- and hyphen-tolerant matching. Returns EVERY matching place
    without dropping valid entries.
    """
    categoryNorm = normalizeText(category) if category else ""
    floorInt: Optional[int] = None
    if floor is not None and str(floor).strip() != "":
        try:
            floorInt = int(floor)
        except (ValueError, TypeError):
            floorInt = None

    qCanon = canonicalizeSearchText(query or "")
    qCompact = compactSearchText(query or "")
    qTokens = [tok for tok in qCanon.split() if tok]

    scored: List[Tuple[int, Tuple[Any, ...], Dict[str, Any]]] = []
    for place in places:
        if categoryNorm and normalizeText(place.get("category", "")) != categoryNorm:
            continue
        if floorInt is not None and place.get("floorLevel") != floorInt:
            continue

        if not qCanon:
            scored.append((0, naturalSortKey(place.get("name", "")), place))
            continue

        score = _scorePlaceMatch(place, qCanon, qCompact, qTokens)
        if score is not None:
            scored.append((score, naturalSortKey(place.get("name", "")), place))

    if qCanon:
        scored.sort(key=lambda item: (item[0], item[1]))

    return [item[2] for item in scored]
