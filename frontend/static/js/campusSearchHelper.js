/**
 * ================================================================================
 * CAMPUSSEARCHHELPER.JS - CANONICAL ROOM & FACILITY SEARCH ENGINE (FRONTEND)
 * ================================================================================
 * Mirrors backend/services/placeSearchService.py for instant, deterministic,
 * zero-drop search across classrooms, laboratories, offices, buildings, and
 * the UAM Building Directory:
 *  - Case-insensitive & Unicode accent/diacritic-insensitive matching
 *  - Whitespace-tolerant & separator-tolerant room code matching
 *    ("B210", "b210", "B-210", "B 210", "  b   210  " all match identically)
 *  - Multi-token AND search ("aula b 210", "edificio b 210", "piso 2 b")
 *  - Relevance tier ranking with natural numeric ordering (B-201 .. B-210)
 *  - ZERO arbitrary result truncation when searching (never drops valid matches)
 *  - Directory room-range expansion ("B201 - B210", "P-301 a P-308", etc.)
 * ================================================================================
 */
(function (global) {
    "use strict";

    function stripAccents(text) {
        return String(text == null ? "" : text)
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function normalizeText(text) {
        return stripAccents(text).trim().toLowerCase().replace(/\s+/g, " ");
    }

    /**
     * Canonicalizes text for room & facility search:
     *  - Splits camelCase boundaries ("classroomB210" -> "classroom B210")
     *  - Strips accents and lowercases
     *  - Replaces punctuation/hyphens/underscores with single spaces
     *  - Collapses standalone single-letter + space + digit ("b 210" -> "b210",
     *    "b 2" -> "b2") while preserving normal word boundaries ("planta 1")
     */
    function canonicalizeSearchText(text) {
        const spaced = String(text == null ? "" : text).replace(/([a-z0-9])([A-Z])/g, "$1 $2");
        const alnum = stripAccents(spaced)
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, " ")
            .trim();
        return alnum.replace(/\b([a-z])\s+(\d)/g, "$1$2");
    }

    function compactSearchText(text) {
        return stripAccents(text).toLowerCase().replace(/[^a-z0-9]+/g, "");
    }

    function extractRoomCodes(text) {
        const spaced = String(text == null ? "" : text).replace(/([a-z0-9])([A-Z])/g, "$1 $2");
        const stripped = stripAccents(spaced).toLowerCase();
        const codes = new Set();
        const re = /\b([a-z])\s*[-_]?\s*(\d{3}[a-z]?)\b/g;
        let m;
        while ((m = re.exec(stripped)) !== null) {
            codes.add(m[1] + m[2]);
        }
        return codes;
    }

    /**
     * Expands room range patterns such as "B201 - B210", "P-101 a P-108",
     * "P-301 to P-308", "C307-C310" into explicit room codes so directory
     * searches like "B207" or "P307" match their parent building card.
     */
    function expandRoomRanges(text) {
        const stripped = stripAccents(String(text == null ? "" : text)).toLowerCase();
        const expanded = [];
        const rangeRe = /\b([a-z])\s*-?\s*(\d{3})\s*(?:-|–|—|\ba\b|\bto\b)\s*([a-z])?\s*-?\s*(\d{3})\b/g;
        let m;
        while ((m = rangeRe.exec(stripped)) !== null) {
            const letterStart = m[1];
            const numStart = parseInt(m[2], 10);
            const letterEnd = m[3] || letterStart;
            const numEnd = parseInt(m[4], 10);
            if (letterStart === letterEnd && numEnd >= numStart && (numEnd - numStart) <= 50) {
                for (let n = numStart; n <= numEnd; n++) {
                    expanded.push(letterStart + String(n));
                }
            }
        }
        return expanded.join(" ");
    }

    function naturalCompare(a, b) {
        const ca = canonicalizeSearchText(a);
        const cb = canonicalizeSearchText(b);
        const pa = ca.split(/(\d+)/);
        const pb = cb.split(/(\d+)/);
        const len = Math.max(pa.length, pb.length);
        for (let i = 0; i < len; i++) {
            const xa = pa[i] === undefined ? "" : pa[i];
            const xb = pb[i] === undefined ? "" : pb[i];
            if (xa === xb) continue;
            const da = /^\d+$/.test(xa);
            const db = /^\d+$/.test(xb);
            if (da && db) {
                const diff = parseInt(xa, 10) - parseInt(xb, 10);
                if (diff !== 0) return diff;
            } else {
                if (xa < xb) return -1;
                if (xa > xb) return 1;
            }
        }
        return 0;
    }

    function getPlaceRoomCodes(place) {
        const codes = new Set();
        if (Array.isArray(place.roomCodes)) {
            for (const c of place.roomCodes) {
                if (c) codes.add(String(c).toLowerCase());
            }
        }
        if (codes.size === 0) {
            for (const c of extractRoomCodes(place.name)) codes.add(c);
            for (const c of extractRoomCodes(place.placeId)) codes.add(c);
            if (Array.isArray(place.keywords)) {
                for (const kw of place.keywords) {
                    for (const c of extractRoomCodes(kw)) codes.add(c);
                }
            }
        }
        return codes;
    }

    function scorePlaceMatch(place, qCanon, qCompact, qTokens) {
        const nameRaw = place.name || "";
        const placeIdRaw = place.placeId || "";
        const notesRaw = place.locationNotes || "";
        const buildingRaw = place.buildingName || "";
        const keywordsRaw = Array.isArray(place.keywords) ? place.keywords : [];

        const nameCanon = canonicalizeSearchText(nameRaw);
        const placeIdCanon = canonicalizeSearchText(placeIdRaw);
        const notesCanon = canonicalizeSearchText(notesRaw);
        const buildingCanon = canonicalizeSearchText(buildingRaw);
        const keywordsCanon = keywordsRaw.map(canonicalizeSearchText).filter(Boolean);
        const roomCodes = getPlaceRoomCodes(place);

        // Tier 0: Exact room code, exact name, or exact placeId match
        if (roomCodes.has(qCanon) || (qCompact && roomCodes.has(qCompact)) || qCanon === nameCanon || qCanon === placeIdCanon) {
            return 0;
        }

        // Tier 1: Room code prefix match (e.g. "B2" -> B201..B210, "B20" -> B201..B209)
        for (const code of roomCodes) {
            if (code.startsWith(qCanon)) return 1;
        }

        // Tier 2: Name prefix or word-prefix match
        const nameWords = nameCanon ? nameCanon.split(" ") : [];
        if (nameCanon.startsWith(qCanon) || nameWords.some((w) => w.startsWith(qCanon))) {
            return 2;
        }

        // Tier 3: Substring match in name (or alpha-only compact match for >=4 chars like "camcam")
        const allowCompact = qCompact.length >= 4 && /^[a-z]+$/.test(qCompact);
        if (nameCanon.includes(qCanon)) return 3;
        if (allowCompact && compactSearchText(nameRaw).includes(qCompact)) return 3;

        // Tier 4: Keyword or placeId exact / word-prefix match
        if (keywordsCanon.some((kw) => kw === qCanon || kw.startsWith(qCanon) || kw.split(" ").some((w) => w.startsWith(qCanon)))) {
            return 4;
        }
        if (placeIdCanon && (placeIdCanon.startsWith(qCanon) || placeIdCanon.split(" ").some((w) => w.startsWith(qCanon)))) {
            return 4;
        }

        // Tier 5: Substring match in keywords or placeId
        if (keywordsCanon.some((kw) => kw.includes(qCanon))) return 5;
        if (placeIdCanon.includes(qCanon)) return 5;
        if (allowCompact) {
            if (compactSearchText(placeIdRaw).includes(qCompact)) return 5;
            if (keywordsRaw.some((kw) => compactSearchText(kw).includes(qCompact))) return 5;
        }

        // Tier 6: Multi-token AND match across combined fields
        if (qTokens.length >= 2) {
            const floorText = place.floorLevel != null ? `piso ${place.floorLevel} floor ${place.floorLevel}` : "";
            const combinedCanon = [nameCanon, placeIdCanon, buildingCanon, notesCanon, floorText]
                .concat(keywordsCanon)
                .filter(Boolean)
                .join(" ");
            const combinedCompact = compactSearchText(combinedCanon);
            const allMatched = qTokens.every((tok) => {
                if (combinedCanon.includes(tok)) return true;
                for (const code of roomCodes) {
                    if (code.startsWith(tok)) return true;
                }
                const tokCompact = compactSearchText(tok);
                return tokCompact.length >= 4 && /^[a-z]+$/.test(tokCompact) && combinedCompact.includes(tokCompact);
            });
            if (allMatched) return 6;
        }

        // Tier 7: Location notes or building name match (skip incidental neighbor notes for exact room codes)
        if (!/^[a-z]\d{3}[a-z]?$/.test(qCanon)) {
            if (notesCanon.includes(qCanon) || (buildingCanon && buildingCanon.includes(qCanon))) {
                return 7;
            }
        }

        return null;
    }

    function scoreNodeMatch(node, qCanon, qCompact, qTokens) {
        const nameRaw = node.name || "";
        const nodeIdRaw = node.nodeId || "";
        const shortRaw = nameRaw.split("(")[0].trim();

        const nameCanon = canonicalizeSearchText(nameRaw);
        const shortCanon = canonicalizeSearchText(shortRaw);
        const nodeIdCanon = canonicalizeSearchText(nodeIdRaw);

        if (qCanon === shortCanon || qCanon === nameCanon || qCanon === nodeIdCanon) return 0;
        if (shortCanon.startsWith(qCanon) || shortCanon.split(" ").some((w) => w.startsWith(qCanon))) return 2;
        if (nodeIdCanon.startsWith(qCanon)) return 3;
        if (shortCanon.includes(qCanon) || nameCanon.includes(qCanon) || nodeIdCanon.includes(qCanon)) return 5;
        if (qCompact.length >= 4 && (compactSearchText(nameRaw).includes(qCompact) || compactSearchText(nodeIdRaw).includes(qCompact))) {
            return 5;
        }
        if (qTokens.length >= 2) {
            const combined = `${nameCanon} ${nodeIdCanon}`;
            if (qTokens.every((tok) => combined.includes(tok))) return 6;
        }
        return null;
    }

    /**
     * Searches both places (classrooms, labs, offices, facilities) and macro
     * building nodes. Never truncates matches when a query or category filter
     * is provided, ensuring exact and partial queries return EVERY valid room.
     */
    function searchCampus(queryText, categoryFilter, allPlaces, allNodes, helpers) {
        const opts = helpers || {};
        const catFilterNorm = normalizeText(categoryFilter || "");
        const qCanon = canonicalizeSearchText(queryText || "");
        const qCompact = compactSearchText(queryText || "");
        const qTokens = qCanon ? qCanon.split(" ").filter(Boolean) : [];
        const hasQuery = qCanon.length > 0;

        const floorWord = typeof opts.floorWord === "string" ? opts.floorWord : "Floor";
        const bldgSubtitle = typeof opts.bldgSubtitle === "string" ? opts.bldgSubtitle : "Main building";
        const resolveParentLabel = typeof opts.resolveParentLabel === "function"
            ? opts.resolveParentLabel
            : (id, place) => (place && place.buildingName) || id || "";
        const getCategorySvg = typeof opts.getCategorySvg === "function" ? opts.getCategorySvg : () => "";
        const buildingIconSvg = opts.buildingIconSvg || "";

        const scored = [];

        // 1. Sub-places (classrooms, labs, auditoriums, offices, fountains, restrooms)
        for (const place of (allPlaces || [])) {
            if (catFilterNorm && normalizeText(place.category || "") !== catFilterNorm) continue;

            let score = 0;
            if (hasQuery) {
                score = scorePlaceMatch(place, qCanon, qCompact, qTokens);
                if (score === null) continue;
            }

            const parentLabel = resolveParentLabel(place.parentBuildingId, place);
            scored.push({
                score,
                typeOrder: 0,
                item: {
                    type: "place",
                    id: place.placeId,
                    targetNodeId: place.parentBuildingId,
                    title: place.name,
                    subtitle: `${parentLabel} • ${floorWord} ${place.floorLevel}${place.locationNotes ? ` • ${place.locationNotes}` : ""}`,
                    category: place.category,
                    iconSvg: getCategorySvg(place.category),
                },
            });
        }

        // 2. Macro nodes (buildings, gates, parking) when no sub-place category filter is active
        if (!catFilterNorm) {
            for (const node of (allNodes || [])) {
                let score = 0;
                if (hasQuery) {
                    score = scoreNodeMatch(node, qCanon, qCompact, qTokens);
                    if (score === null) continue;
                }

                scored.push({
                    score,
                    typeOrder: hasQuery ? 1 : -1,
                    item: {
                        type: "node",
                        id: node.nodeId,
                        targetNodeId: node.nodeId,
                        title: node.name,
                        subtitle: `${bldgSubtitle} (${floorWord} ${node.floorLevel})`,
                        category: node.category,
                        iconSvg: buildingIconSvg,
                    },
                });
            }
        }

        if (hasQuery) {
            scored.sort((a, b) => {
                if (a.score !== b.score) return a.score - b.score;
                if (a.typeOrder !== b.typeOrder) return a.typeOrder - b.typeOrder;
                return naturalCompare(a.item.title, b.item.title);
            });
            return scored.map((entry) => entry.item);
        }

        if (catFilterNorm) {
            scored.sort((a, b) => naturalCompare(a.item.title, b.item.title));
            return scored.map((entry) => entry.item);
        }

        // Empty query & no category filter: show macro buildings first, then catalog entries
        scored.sort((a, b) => {
            if (a.typeOrder !== b.typeOrder) return a.typeOrder - b.typeOrder;
            return naturalCompare(a.item.title, b.item.title);
        });
        return scored.map((entry) => entry.item);
    }

    /**
     * Filters building indoor location lists (e.g. GPS manual floor picker)
     * with accent-, case-, hyphen-, and whitespace-tolerant matching.
     */
    function filterLocationsList(rawList, filterText) {
        const list = Array.isArray(rawList) ? rawList : [];
        const qCanon = canonicalizeSearchText(filterText || "");
        if (!qCanon) return list;
        const qCompact = compactSearchText(filterText || "");
        const qTokens = qCanon.split(" ").filter(Boolean);

        return list.filter((loc) => {
            const nameCanon = canonicalizeSearchText(loc.name || "");
            const catCanon = canonicalizeSearchText(loc.category || "");
            const idCanon = canonicalizeSearchText(loc.nodeId || loc.placeId || "");
            const codes = extractRoomCodes(loc.name || "");
            if (codes.has(qCanon) || Array.from(codes).some((c) => c.startsWith(qCanon))) return true;
            if (nameCanon.includes(qCanon) || catCanon.includes(qCanon) || idCanon.includes(qCanon)) return true;
            if (qCompact.length >= 4 && compactSearchText(loc.name || "").includes(qCompact)) return true;
            if (qTokens.length >= 2) {
                const combined = `${nameCanon} ${catCanon} ${idCanon}`;
                return qTokens.every((tok) => combined.includes(tok));
            }
            return false;
        });
    }

    /**
     * Determines whether a Building Directory card matches a user query by
     * checking both the card's text (including expanded room ranges such as
     * "B201 - B210") and all indexed places belonging to that building.
     */
    function matchesDirectoryCard(cardText, buildingId, queryText, allPlaces) {
        const qCanon = canonicalizeSearchText(queryText || "");
        if (!qCanon) return true;
        const qCompact = compactSearchText(queryText || "");
        const qTokens = qCanon.split(" ").filter(Boolean);

        const expandedRanges = expandRoomRanges(cardText);
        const cardCanon = `${canonicalizeSearchText(cardText)} ${expandedRanges}`.trim();
        const cardCodes = extractRoomCodes(`${cardText} ${expandedRanges}`);

        if (cardCodes.has(qCanon) || Array.from(cardCodes).some((c) => c.startsWith(qCanon))) {
            return true;
        }
        if (cardCanon.includes(qCanon)) return true;
        if (qCompact.length >= 4 && compactSearchText(cardText).includes(qCompact)) return true;
        if (qTokens.length >= 2 && qTokens.every((tok) => cardCanon.includes(tok))) return true;

        // Also match against indexed places belonging to this building
        const bIdNorm = normalizeText(buildingId || "");
        if (bIdNorm && Array.isArray(allPlaces) && allPlaces.length > 0) {
            for (const place of allPlaces) {
                if (normalizeText(place.parentBuildingId || "") !== bIdNorm) continue;
                if (scorePlaceMatch(place, qCanon, qCompact, qTokens) !== null) {
                    return true;
                }
            }
        }

        return false;
    }

    global.JaguarCampusSearch = Object.freeze({
        stripAccents,
        normalizeText,
        canonicalizeSearchText,
        compactSearchText,
        extractRoomCodes,
        expandRoomRanges,
        naturalCompare,
        scorePlaceMatch,
        scoreNodeMatch,
        searchCampus,
        filterLocationsList,
        matchesDirectoryCard,
    });
})(typeof window !== "undefined" ? window : globalThis);
