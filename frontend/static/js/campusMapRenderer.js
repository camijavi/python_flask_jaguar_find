/**
 * ================================================================================
 * CAMPUSMAPRENDERER.JS - DECLARATIVE 2D UAM CAMPUS MAP VECTOR RENDERER
 * ================================================================================
 * Renders the official UAM campus layout onto #officialCampus2dSvg (1200 x 850)
 * using compact, reusable SVG helpers to avoid repetitive markup:
 *  - Roads & perimeter access avenues
 *  - Parking lots with procedurally stamped stalls & islands
 *  - Sports facilities (Baseball Stadium, Soccer Field, Courts, Grandstands)
 *  - Plazas & courtyards (Plaza Central Ruben Dario, Plaza Chilamates, B-C patio)
 *  - Architectural hip-roofed buildings (A-P + campus annexes & sports buildings)
 *  - Landscaping trees & bush rows via reusable SVG <use> symbols
 *  - Dedicated Emergency Evacuation Layer (green safe zones & dashed routes)
 */

(function () {
    const SVG_NS = "http://www.w3.org/2000/svg";

    // Official flat architectural roof palette
    const ROOF_BASE = "#1da495";
    const ROOF_LIGHT = "#48b2a9";
    const ROOF_DARK = "#1f8383";
    const ROOF_BORDER = "#253452";

    // Single source of truth for building & landmark anchors (1200 x 850 SVG coords)
    window.CAMPUS_BUILDING_ANCHORS = {
        buildingA: { x: 323, y: 435 },
        buildingB: { x: 444, y: 459 },
        buildingC: { x: 444, y: 411 },
        buildingD: { x: 404, y: 316 },
        buildingE: { x: 534, y: 580 },
        buildingF: { x: 592, y: 564 },
        buildingG: { x: 592, y: 510 },
        buildingH: { x: 646, y: 370 },
        buildingI: { x: 762, y: 656 },
        buildingJ: { x: 357, y: 316 },
        buildingK: { x: 362, y: 526 },
        buildingL: { x: 982, y: 626 },
        buildingM: { x: 612, y: 435 },
        buildingN: { x: 436, y: 260 },
        buildingO: { x: 597, y: 196 },
        buildingP: { x: 450, y: 115 },
        mainParking: { x: 318, y: 765 },
        chilamatesPlaza: { x: 300, y: 292 },
        sportsZone: { x: 918, y: 447 },
        jaguarCenter: { x: 886, y: 623 },
        northGate: { x: 245, y: 72 },
        northeastGate: { x: 645, y: 18 }
    };

    // ----------------------------------------------------------------------------
    // 1. Minimal SVG DOM & Geometry Helpers
    // ----------------------------------------------------------------------------
    function el(tag, attrs = {}, parent = null) {
        const node = document.createElementNS(SVG_NS, tag);
        for (const [k, v] of Object.entries(attrs)) {
            if (v !== undefined && v !== null) node.setAttribute(k, String(v));
        }
        if (parent) parent.appendChild(node);
        return node;
    }

    /** Adds a badge box + single-letter label inside a building group */
    function addBadge(parent, cx, cy, letter, badgeClass, size = 20) {
        const g = el("g", { class: "billboard-badge" }, parent);
        el("rect", {
            x: cx - size / 2,
            y: cy - size / 2,
            width: size,
            height: size,
            class: badgeClass
        }, g);
        const txt = el("text", { x: cx, y: cy, class: "badge-text" }, g);
        txt.textContent = letter;
    }

    /**
     * Renders a rectangular architectural building with hipped roof facets.
     * orientation: "h" (horizontal ridge), "v" (vertical ridge), or "ribH"/"ribV" (corrugated roof).
     */
    function addRectBuilding(parent, cfg) {
        const {
            x, y, w, h,
            node, bldg,
            badge, badgeClass, badgeX, badgeY,
            orientation = (w >= h ? "h" : "v"),
            borderWidth = 3,
            shadow = true
        } = cfg;

        const g = el("g", {
            class: node || bldg ? "bldg-shape" : undefined,
            "data-node": node,
            "data-bldg": bldg,
            filter: shadow ? "url(#bldgShadow)" : undefined
        }, parent);

        if (orientation === "ribH" || orientation === "ribV") {
            el("rect", { x, y, width: w, height: h, fill: "#62b8b0" }, g);
            if (orientation === "ribH") {
                el("rect", { x, y, width: w / 2, height: h, fill: "#74c4bc" }, g);
                for (let ry = y + 4; ry < y + h - 1; ry += 4) {
                    el("line", { x1: x, y1: ry, x2: x + w, y2: ry, stroke: ROOF_DARK, "stroke-width": 0.9, opacity: 0.35 }, g);
                }
            } else {
                el("rect", { x, y, width: w, height: h / 2, fill: "#74c4bc" }, g);
                for (let rx = x + 5; rx < x + w - 1; rx += 5) {
                    el("line", { x1: rx, y1: y, x2: rx, y2: y + h, stroke: ROOF_DARK, "stroke-width": 0.9, opacity: 0.35 }, g);
                }
            }
        } else {
            // Base teal fill
            el("rect", { x, y, width: w, height: h, fill: ROOF_BASE }, g);
            const inset = Math.min(w, h) * 0.42;

            if (orientation === "h") {
                // Top lit slope + left & right hip triangles
                el("polygon", { points: `${x},${y} ${x + w},${y} ${x + w - inset},${y + h / 2} ${x + inset},${y + h / 2}`, fill: ROOF_LIGHT }, g);
                el("polygon", { points: `${x},${y} ${x},${y + h} ${x + inset},${y + h / 2}`, fill: ROOF_DARK }, g);
                el("polygon", { points: `${x + w},${y} ${x + w},${y + h} ${x + w - inset},${y + h / 2}`, fill: ROOF_DARK }, g);
            } else {
                // Left lit slope + top & bottom hip triangles
                el("polygon", { points: `${x},${y} ${x + w / 2},${y + inset} ${x + w / 2},${y + h - inset} ${x},${y + h}`, fill: ROOF_LIGHT }, g);
                el("polygon", { points: `${x},${y} ${x + w},${y} ${x + w / 2},${y + inset}`, fill: ROOF_DARK }, g);
                el("polygon", { points: `${x},${y + h} ${x + w},${y + h} ${x + w / 2},${y + h - inset}`, fill: ROOF_DARK }, g);
            }
        }

        // Crisp navy architectural outline
        el("rect", {
            x, y, width: w, height: h,
            fill: "none", stroke: ROOF_BORDER, "stroke-width": borderWidth, "stroke-linejoin": "miter"
        }, g);

        if (badge) {
            addBadge(g, badgeX ?? (x + w / 2), badgeY ?? (y + h / 2), badge, badgeClass);
        }
        return g;
    }

    /** Renders a custom-footprint building (L, U, dogleg, cruciform) with facet polygons */
    function addCustomBuilding(parent, cfg) {
        const {
            path, facets = [],
            node, bldg,
            badge, badgeClass, badgeX, badgeY,
            borderWidth = 3,
            shadow = true
        } = cfg;

        const g = el("g", {
            class: node || bldg ? "bldg-shape" : undefined,
            "data-node": node,
            "data-bldg": bldg,
            filter: shadow ? "url(#bldgShadow)" : undefined
        }, parent);

        el("path", { d: path, fill: ROOF_BASE }, g);
        for (const [points, fill] of facets) {
            el("polygon", { points, fill }, g);
        }
        el("path", { d: path, fill: "none", stroke: ROOF_BORDER, "stroke-width": borderWidth, "stroke-linejoin": "miter" }, g);

        if (badge) {
            addBadge(g, badgeX, badgeY, badge, badgeClass);
        }
        return g;
    }

    /**
     * Stamps a uniform row of parking stall dividers between (x1, y1) and (x2, y2).
     * dx, dy specify the divider line vector pointing out from the baseline.
     */
    function addStallRow(parent, x1, y1, x2, y2, count, dx, dy, drawBackLine = false) {
        if (drawBackLine) {
            el("line", { x1, y1, x2, y2 }, parent);
        }
        for (let i = 0; i <= count; i++) {
            const t = count === 0 ? 0 : i / count;
            const px = x1 + (x2 - x1) * t;
            const py = y1 + (y2 - y1) * t;
            el("line", {
                x1: px.toFixed(1),
                y1: py.toFixed(1),
                x2: (px + dx).toFixed(1),
                y2: (py + dy).toFixed(1)
            }, parent);
        }
    }

    /** Stamps a line of reusable tree or bush symbols from (x1, y1) to (x2, y2) */
    function addTreeRow(parent, x1, y1, x2, y2, count, symbol = "#treeLarge") {
        for (let i = 0; i < count; i++) {
            const t = count <= 1 ? 0.5 : i / (count - 1);
            el("use", {
                href: symbol,
                x: (x1 + (x2 - x1) * t).toFixed(1),
                y: (y1 + (y2 - y1) * t).toFixed(1)
            }, parent);
        }
    }

    // ----------------------------------------------------------------------------
    // 2. Layer 1: Campus Perimeter & Internal Roads
    // ----------------------------------------------------------------------------
    function renderRoads(layer) {
        const roads = [
            // Top perimeter avenue (Camino Segundo Acceso) curving into Tercer Acceso
            { d: "M -2000 18 L 320 18 L 245 72 L 175 72", w: 20 },
            { d: "M 320 18 L 3000 18", w: 20 },
            // West campus access road (Tercer Acceso -> West Parking -> Entrada Principal)
            { d: "M 245 72 L 265 200 L 265 460 L 298 765", w: 22 },
            // North-South central spine road (East of P, O, H, M, G, F, I)
            { d: "M 645 18 L 658 240 L 692 355 L 696 555 L 806 600 L 808 776", w: 20 },
            // South main avenue (Entrada Principal across south boundary to east complex)
            { d: "M -2000 764 L 305 764 L 820 792 L 3000 792", w: 24 },
            // Internal connector: West road -> North PON parking & P-O corridor
            { d: "M 265 188 L 558 188", w: 14 },
            // Internal connector: West road -> Central CD parking
            { d: "M 265 366 L 560 366", w: 14 },
            // Internal connector: Spine road -> between F and SE Parking -> South Parking
            { d: "M 696 588 L 560 588 L 560 710", w: 12 },
            // East sports concourse between Baseball Stadium and Soccer Field
            { d: "M 692 338 L 1140 338", w: 22, color: "#dce2ec" },
            // East corridor between Jaguar Center/Soccer and L/Courts/East buildings
            { d: "M 988 538 L 998 840", w: 14, color: "#dce2ec" }
        ];

        for (const r of roads) {
            el("path", {
                d: r.d,
                "stroke-width": r.w,
                stroke: r.color || "#c8cfde"
            }, layer);
        }
    }

    // ----------------------------------------------------------------------------
    // 3. Layer 2: Parking Lots (All 11 Official Campus Lots)
    // ----------------------------------------------------------------------------
    function renderParking(layer) {
        function makeLot(id, shapeTag, shapeAttrs, buildStalls) {
            const g = el("g", { id, class: "parking-lot" }, layer);
            el(shapeTag, {
                ...shapeAttrs,
                class: "parking-asphalt",
                fill: "#dfe5ec",
                stroke: "#cbd5e1",
                "stroke-width": 1.5,
                "stroke-linejoin": "round"
            }, g);
            const lines = el("g", {
                class: "parking-lines",
                stroke: "#ffffff",
                "stroke-width": 1.2,
                "stroke-linecap": "round"
            }, g);
            if (buildStalls) buildStalls(g, lines);
            return g;
        }

        // 2.1 Behind Building P (angled north entrance)
        makeLot("parkingLotBehindP", "path", {
            d: "M 342 22 L 420 22 L 522 25 A 6 6 0 0 1 528 31 L 528 70 A 6 6 0 0 1 522 76 L 428 76 L 342 22 Z"
        }, (_, l) => {
            addStallRow(l, 366, 33, 428, 72, 6, 5.5, -9, true);   // SW diagonal stalls
            addStallRow(l, 438, 28, 506, 28, 8, 0, 11, true);     // Top row
            addStallRow(l, 434, 72, 504, 72, 8, 0, -11, true);    // Bottom row
            addStallRow(l, 523, 33, 523, 69, 5, -11, 0, true);    // East column
        });

        // 2.2 West Side of Building P (above Weather Station)
        makeLot("parkingLotSideP", "rect", { x: 236, y: 96, width: 52, height: 52, rx: 4 }, (_, l) => {
            addStallRow(l, 240, 101, 240, 143, 5, 13, 0, true);
            addStallRow(l, 284, 101, 284, 143, 5, -13, 0, true);
        });

        // 2.3 North Parking (Between Building P, Building O, and Building N)
        makeLot("parkingLotNorthPON", "path", {
            d: "M 294 176 L 330 176 L 330 158 L 538 158 L 538 214 L 330 214 L 330 194 L 294 194 Z"
        }, (_, l) => {
            addStallRow(l, 338, 160, 530, 160, 26, 0, 13);
            addStallRow(l, 338, 212, 530, 212, 26, 0, -13);
        });

        // 2.4 Upper West Parking Lot (North of west tree line, east of Acopio)
        makeLot("parkingLotWestUpper", "path", {
            d: "M 78 202 L 254 202 L 254 328 L 88 328 L 88 310 L 78 202 Z"
        }, (g, l) => {
            // Two full double-sided horizontal bays
            addStallRow(l, 88, 206, 214, 206, 15, 0, 18, true);
            addStallRow(l, 90, 262, 214, 262, 15, 0, -17, true);
            addStallRow(l, 92, 268, 214, 268, 15, 0, 17, true);
            addStallRow(l, 94, 322, 212, 322, 14, 0, -17, true);
            // Right-side moto stalls pocket
            el("rect", { x: 222, y: 294, width: 28, height: 28, rx: 3, fill: "#cfd8e3", stroke: "#ffffff", "stroke-width": 1 }, g);
            addStallRow(l, 224, 298, 248, 298, 5, 0, 9);
            addStallRow(l, 224, 319, 248, 319, 5, 0, -9);
        });

        // 2.5 Lower West Parking Lot (South of west tree line, west of A & K)
        makeLot("parkingLotWestLower", "path", {
            d: "M 76 364 L 268 364 L 268 504 L 84 494 Z"
        }, (_, l) => {
            // Top stalls above upper tree median (y=398)
            addStallRow(l, 88, 368, 224, 368, 16, 0, 16, true);
            // Center stalls neatly between the two tree medians (y=398 & y=444)
            addStallRow(l, 90, 412, 224, 412, 16, 0, 10, true);
            addStallRow(l, 90, 432, 224, 432, 16, 0, -10, true);
            // Bottom stalls below lower tree median (y=444)
            addStallRow(l, 94, 488, 224, 488, 16, 0, -18, true);
        });

        // 2.6 Central Parking Lot (Between N/J/D and Building C, ending at x=496 before bush median)
        makeLot("parkingLotCentralCD", "path", {
            d: "M 304 366 L 322 344 L 496 344 L 496 395 L 304 395 Z"
        }, (g, l) => {
            el("rect", { x: 304, y: 391, width: 192, height: 4, fill: "#cbd5e1" }, g);
            addStallRow(l, 330, 346, 486, 346, 13, -10, 14);  // Angled top stalls
            addStallRow(l, 318, 391, 490, 391, 15, 0, -14);   // Perpendicular bottom stalls
        });

        // Pedestrian Zebra Crosswalk between Plaza Chilamates & Building A
        const cw = el("g", { id: "pedestrianChilamatesToA" }, layer);
        el("rect", { x: 280, y: 344, width: 22, height: 54, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1.2 }, cw);
        for (let y = 350; y <= 392; y += 7) {
            el("line", { x1: 283, y1: y, x2: 299, y2: y, stroke: "#ffffff", "stroke-width": 3 }, cw);
        }

        // 2.7 North-East Sports Parking (North of Baseball Stadium)
        makeLot("parkingLotNorthSports", "rect", { x: 744, y: 42, width: 128, height: 52, rx: 6 }, (_, l) => {
            addStallRow(l, 754, 46, 862, 46, 12, 0, 14, true);
            addStallRow(l, 754, 90, 862, 90, 12, 0, -14, true);
        });

        // 2.8 East Vertical Roadside Parking Strips (East of O & East of G/F)
        makeLot("parkingLotEastO", "rect", { x: 632, y: 204, width: 28, height: 68, rx: 4 }, (_, l) => {
            addStallRow(l, 635, 210, 635, 266, 8, 12, 0, true);
        });
        makeLot("parkingLotEastGF", "rect", { x: 668, y: 462, width: 28, height: 112, rx: 4 }, (_, l) => {
            addStallRow(l, 671, 468, 671, 568, 14, 13, 0, true);
        });

        // 2.9 Main South Parking Lot (Large Lot South of Plaza Central & K + South Striping)
        makeLot("parkingLotSouthMain", "path", {
            d: "M 310 568 L 502 568 L 516 686 L 758 708 L 756 764 L 326 738 Z"
        }, (_, l) => {
            // Upper main bay perimeter + center aisle stalls (clear of tree rows at y=672, 708, 744)
            addStallRow(l, 336, 574, 490, 574, 14, 0, 15, true);
            addStallRow(l, 340, 614, 492, 620, 14, 0, -13, true);
            addStallRow(l, 340, 618, 492, 624, 14, 0, 13);
            addStallRow(l, 342, 658, 494, 664, 14, 0, -13, true);
            // Lower long bays tucked cleanly between the 3 horizontal tree dividers
            addStallRow(l, 384, 686, 502, 696, 12, 0, 12, true);
            addStallRow(l, 380, 722, 738, 754, 32, 0, 12, true);
        });

        // 2.10 South-East Parking Lot (Between E Annexes, F, and I, with I-shaped median)
        makeLot("parkingLotSouthEF", "path", {
            d: "M 582 598 L 686 598 L 686 678 A 14 14 0 0 1 672 692 L 582 692 Z"
        }, (g, l) => {
            // Center I-shaped raised concrete median island
            el("path", {
                d: "M 616 610 L 652 610 A 2.5 2.5 0 0 1 652 615 L 641 615 L 641 671 L 652 671 A 2.5 2.5 0 0 1 652 676 L 616 676 A 2.5 2.5 0 0 1 616 671 L 627 671 L 627 615 L 616 615 A 2.5 2.5 0 0 1 616 610 Z",
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            // 4 neat columns of stalls (west curb, left of island, right of island, east curb)
            addStallRow(l, 586, 604, 586, 676, 10, 13, 0, true);
            addStallRow(l, 626, 620, 626, 666, 7, -13, 0);
            addStallRow(l, 642, 620, 642, 666, 7, 13, 0);
            addStallRow(l, 682, 604, 682, 676, 10, -13, 0, true);
        });

        // 2.11 Jaguar Center South Parking Lot (Between Building I, Jaguar Center & Jaguar Gym)
        makeLot("parkingLotJaguarCenter", "path", {
            d: "M 818 682 L 924 682 L 924 760 L 976 764 L 976 786 L 818 776 Z"
        }, (_, l) => {
            addStallRow(l, 824, 686, 918, 686, 11, 0, 15, true);
            addStallRow(l, 824, 722, 918, 722, 11, 0, -13, true);
            addStallRow(l, 838, 742, 918, 742, 9, 0, 13, true);
            addStallRow(l, 824, 774, 968, 782, 16, 0, -11, true);
        });
    }

    // ----------------------------------------------------------------------------
    // 4. Layer 3: Sports Facilities (Baseball, Soccer, Courts, Grandstands)
    // ----------------------------------------------------------------------------
    function renderSports(layer) {
        // 3A. Estadio de Beisbol (Diamond in upper-right corner facing SW, matching official map)
        const bb = el("g", { id: "baseballStadium", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "BÉISBOL" }, layer);
        el("path", {
            d: "M 692 108 L 1076 108 L 1076 312 L 728 312 Q 696 308 692 270 Z",
            fill: "#22c55e", stroke: ROOF_BORDER, "stroke-width": 2.5
        }, bb);
        // Outfield warning track arc
        el("path", {
            d: "M 738 118 L 1054 118 L 1054 294 L 748 294 A 185 185 0 0 1 738 118 Z",
            fill: "#16a34a", opacity: 0.45
        }, bb);
        // Upper-right infield dirt box & rotated diamond
        el("polygon", {
            points: "930,124 1026,124 1026,220 930,220",
            fill: "#c28854", stroke: "#ffffff", "stroke-width": 1.6
        }, bb);
        el("polygon", { points: "978,136 1014,172 978,208 942,172", fill: "#16a34a", stroke: "#ffffff", "stroke-width": 1.6 }, bb);
        // Foul lines sweeping SW across outfield
        el("line", { x1: 1014, y1: 136, x2: 736, y2: 136, stroke: "#ffffff", "stroke-width": 1.4, opacity: 0.85 }, bb);
        el("line", { x1: 1014, y1: 136, x2: 1014, y2: 300, stroke: "#ffffff", "stroke-width": 1.4, opacity: 0.85 }, bb);
        // Pitcher's mound & bases
        el("line", { x1: 1014, y1: 136, x2: 978, y2: 172, stroke: "#ffffff", "stroke-width": 1.5, opacity: 0.7 }, bb);
        el("circle", { cx: 978, cy: 172, r: 5, fill: "#c28854", stroke: "#ffffff", "stroke-width": 1.4 }, bb);
        for (const [bx, by] of [[1014, 136], [978, 136], [942, 172], [978, 208]]) {
            el("rect", { x: bx - 2.5, y: by - 2.5, width: 5, height: 5, fill: "#ffffff", transform: `rotate(45 ${bx} ${by})` }, bb);
        }

        // 3B. Cancha de Futbol (Wide proportional soccer pitch)
        const sc = el("g", { id: "soccerField", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "FÚTBOL" }, layer);
        el("rect", { x: 744, y: 372, width: 348, height: 150, fill: "#15803d", stroke: ROOF_BORDER, "stroke-width": 2.5 }, sc);
        const lines = el("g", { stroke: "#ffffff", "stroke-width": 1.8, fill: "none" }, sc);
        el("rect", { x: 756, y: 382, width: 324, height: 130 }, lines);
        el("line", { x1: 918, y1: 382, x2: 918, y2: 512 }, lines);
        el("circle", { cx: 918, cy: 447, r: 24 }, lines);
        el("circle", { cx: 918, cy: 447, r: 2.2, fill: "#ffffff" }, lines);
        // Left & right penalty boxes
        el("rect", { x: 756, y: 412, width: 38, height: 70 }, lines);
        el("rect", { x: 756, y: 427, width: 16, height: 40 }, lines);
        el("rect", { x: 1042, y: 412, width: 38, height: 70 }, lines);
        el("rect", { x: 1064, y: 427, width: 16, height: 40 }, lines);

        // 3C. Outdoor Courts (Canchas) & Grandstands (Graderias) East of Building L
        const cts = el("g", { id: "sportsCourts", class: "bldg-shape", "data-node": "buildingL", "data-bldg": "CANCHAS" }, layer);
        // Two side-by-side blue courts
        for (const cx of [1028, 1088]) {
            el("rect", { x: cx, y: 586, width: 52, height: 54, fill: "#2563eb", stroke: ROOF_BORDER, "stroke-width": 2.5 }, cts);
            el("rect", { x: cx + 5, y: 591, width: 42, height: 44, fill: "none", stroke: "#ffffff", "stroke-width": 1.2 }, cts);
            el("line", { x1: cx + 5, y1: 613, x2: cx + 47, y2: 613, stroke: "#ffffff", "stroke-width": 1.2 }, cts);
            el("circle", { cx: cx + 26, cy: 613, r: 6, fill: "none", stroke: "#ffffff", "stroke-width": 1.1 }, cts);
        }
        // Grandstands (Graderias) along north & west edges of courts
        const gr = el("g", { id: "grandstands" }, layer);
        el("rect", { x: 1018, y: 562, width: 72, height: 18, fill: "#94a3b8", stroke: ROOF_BORDER, "stroke-width": 1.8 }, gr);
        for (let gy = 567; gy <= 576; gy += 4.5) {
            el("line", { x1: 1020, y1: gy, x2: 1088, y2: gy, stroke: "#e2e8f0", "stroke-width": 1 }, gr);
        }
        el("rect", { x: 1012, y: 586, width: 11, height: 54, fill: "#94a3b8", stroke: ROOF_BORDER, "stroke-width": 1.5 }, gr);
    }

    // ----------------------------------------------------------------------------
    // 5. Layer 4: Plazas & Courtyards
    // ----------------------------------------------------------------------------
    function renderPlazas(layer) {
        // 4A. Plaza Chilamates (Paved courtyard west of J)
        const ch = el("g", { class: "bldg-shape", "data-node": "chilamatesPlaza", "data-bldg": "CHILAMATES" }, layer);
        el("rect", { x: 274, y: 242, width: 54, height: 98, rx: 3, fill: "#e2e8f0", stroke: "#94a3b8", "stroke-width": 1.5 }, ch);
        el("circle", { cx: 304, cy: 288, r: 16, fill: "#10b981", opacity: 0.45 }, ch);

        // 4B. Central Courtyard & Fountains between Building C and Building B
        const cc = el("g", { id: "centralColonnade" }, layer);
        el("rect", { x: 334, y: 422, width: 230, height: 26, fill: "#dfe5ec" }, cc);
        el("line", { x1: 334, y1: 435, x2: 564, y2: 435, stroke: "#64748b", "stroke-width": 5 }, cc);
        el("line", { x1: 334, y1: 435, x2: 564, y2: 435, stroke: "#94a3b8", "stroke-width": 1.4 }, cc);
        for (const fx of [380, 504]) {
            el("circle", { cx: fx, cy: 435, r: 7, fill: "#64748b" }, cc);
            el("circle", { cx: fx, cy: 435, r: 4.5, fill: "#94a3b8", stroke: "#cbd5e1", "stroke-width": 0.9 }, cc);
            el("circle", { cx: fx, cy: 435, r: 1.8, fill: "#ffffff" }, cc);
        }

        // 4C. Plaza Central Ruben Dario (Terrace between K, B, and E)
        const pc = el("g", { id: "plazaCentralRubenDario", "pointer-events": "none" }, layer);
        // West apron beside K
        el("rect", { x: 306, y: 498, width: 28, height: 58, rx: 2, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1.2 }, pc);
        // Tiled patio north of K
        el("rect", { x: 338, y: 474, width: 40, height: 24, fill: "#e2e8f0", stroke: "#cbd5e1", "stroke-width": 1 }, pc);
        // Main hatched terrace polygon
        const terracePts = "378,476 474,476 502,504 502,562 338,562 338,554 398,554 398,534 378,504";
        el("polygon", { points: terracePts, fill: "#e2e8f0", stroke: "#94a3b8", "stroke-width": 1.4, "stroke-linejoin": "round" }, pc);
        el("polygon", { points: terracePts, fill: "url(#plazaDiagonalHatch)" }, pc);
        // Curved/diagonal terrace steps toward Building E
        for (let i = 0; i < 4; i++) {
            el("line", { x1: 474 + i * 4, y1: 476, x2: 502 + i * 4, y2: 504, stroke: "#94a3b8", "stroke-width": 1.1 }, pc);
        }
        // Mini UAM water pool between K and Central Plaza
        const pool = el("g", { id: "uamMiniPool", transform: "rotate(-36, 405, 492)" }, pc);
        el("rect", { x: 386, y: 484, width: 38, height: 15, rx: 2, fill: "#94a3b8", stroke: "#475569", "stroke-width": 0.9 }, pool);
        el("rect", { x: 388, y: 486, width: 34, height: 11, rx: 1, fill: "#38bdf8", stroke: "#0284c7", "stroke-width": 0.9 }, pool);
        el("line", { x1: 391, y1: 489, x2: 419, y2: 489, stroke: "#ffffff", "stroke-width": 0.8, opacity: 0.75 }, pool);
    }

    // ----------------------------------------------------------------------------
    // 6. Layer 5: All Official Campus Buildings (A-P + Campus Support Buildings)
    // ----------------------------------------------------------------------------
    function renderBuildings(layer) {
        // --- Rectangular Main Buildings (A, B, C, E, F, G, H, J, P, Jaguar Center, Jaguar Gym) ---
        const rectBuildings = [
            // Edificio P (Copernico)
            { x: 344, y: 94, w: 218, h: 42, node: "buildingP", bldg: "P", badge: "P", badgeClass: "badge-maroon", badgeX: 486, badgeY: 115, orientation: "h" },
            // Edificio J (Laboratorios Odontologia)
            { x: 338, y: 300, w: 38, h: 32, node: "buildingJ", bldg: "J", badge: "J", badgeClass: "badge-cyan", orientation: "h" },
            // Edificio A (West Bar)
            { x: 310, y: 400, w: 26, h: 70, node: "buildingA", bldg: "A", badge: "A", badgeClass: "badge-maroon", orientation: "v" },
            // Edificio C (North Classroom Bar)
            { x: 336, y: 400, w: 228, h: 22, node: "buildingC", bldg: "C", badge: "C", badgeClass: "badge-purple", badgeX: 444, badgeY: 402, orientation: "h" },
            // Connector Roof between C and B
            { x: 432, y: 422, w: 24, h: 26, bldg: "TECHO_BC", orientation: "v", borderWidth: 2.5 },
            // Edificio B (South Classroom Bar)
            { x: 336, y: 448, w: 228, h: 22, node: "buildingB", bldg: "B", badge: "B", badgeClass: "badge-purple", badgeX: 444, badgeY: 458, orientation: "h" },
            // 2nd-floor bridge between B and E
            { x: 526, y: 470, w: 8, h: 30, bldg: "PUENTE_BE", orientation: "v", borderWidth: 2 },
            // Edificio E (Facultad de Medicina) + Vida Estudiantil & Innovacion Annexes
            { x: 520, y: 500, w: 28, h: 156, node: "buildingE", bldg: "E", badge: "E", badgeClass: "badge-navy", badgeX: 534, badgeY: 604, orientation: "v" },
            { x: 554, y: 626, w: 24, h: 46, node: "buildingE", bldg: "E", orientation: "ribH", borderWidth: 2.5 },
            { x: 538, y: 682, w: 54, h: 13, node: "buildingE", bldg: "E", orientation: "ribV", borderWidth: 2.5 },
            // Edificio H (Laboratorios de Medicina) + small west wing
            { x: 604, y: 354, w: 84, h: 32, node: "buildingH", bldg: "H", badge: "H", badgeClass: "badge-green", badgeX: 646, badgeY: 370, orientation: "h" },
            { x: 576, y: 356, w: 24, h: 20, node: "buildingH", bldg: "H", orientation: "h", borderWidth: 2.5 },
            // Edificio G (Auditorio Central & Derecho)
            { x: 568, y: 488, w: 48, h: 44, node: "buildingG", bldg: "G", badge: "G", badgeClass: "badge-cyan", orientation: "v" },
            // Edificio F (FACEE)
            { x: 568, y: 540, w: 48, h: 48, node: "buildingF", bldg: "F", badge: "F", badgeClass: "badge-magenta", orientation: "v" },
            // Jaguar Gym
            { x: 932, y: 712, w: 48, h: 42, node: "jaguarCenter", bldg: "JAGUAR GYM", orientation: "h" }
        ];

        for (const cfg of rectBuildings) {
            addRectBuilding(layer, cfg);
        }

        // Observatorio Dome attached to West end of Building P
        const obs = el("g", { class: "bldg-shape", "data-node": "buildingP", "data-bldg": "P", filter: "url(#bldgShadow)" }, layer);
        el("rect", { x: 302, y: 94, width: 42, height: 42, fill: "#cbd5e1", stroke: ROOF_BORDER, "stroke-width": 3 }, obs);
        el("circle", { cx: 323, cy: 115, r: 15, fill: ROOF_BASE, stroke: ROOF_BORDER, "stroke-width": 2.2 }, obs);
        el("path", { d: "M 312 106 A 14 14 0 0 1 334 106 L 323 115 Z", fill: ROOF_LIGHT }, obs);
        el("line", { x1: 323, y1: 100, x2: 323, y2: 116, stroke: "#ffffff", "stroke-width": 1.6, opacity: 0.7 }, obs);

        // Jaguar Center Arena (with Official UAM Jaguar Emblem)
        const jc = addRectBuilding(layer, {
            x: 834, y: 576, w: 104, h: 94,
            node: "jaguarCenter", bldg: "JAGUAR CENTER", orientation: "h"
        });
        const logoUrl = layer.closest("svg")?.dataset.jaguarLogo || "/static/img/jaguarCenterLogo.png";
        el("image", {
            href: logoUrl, x: 851, y: 589, width: 70, height: 68,
            preserveAspectRatio: "xMidYMid meet", "pointer-events": "none"
        }, jc);

        // --- Custom-Footprint Buildings (O, N, D, M, K, I, L) ---
        const customBuildings = [
            // Edificio O (Ingenieria & FIA)
            {
                node: "buildingO", bldg: "O", badge: "O", badgeClass: "badge-amber", badgeX: 597, badgeY: 186,
                path: "M 572 154 L 622 154 L 622 242 L 592 242 L 592 228 L 572 228 L 572 216 L 558 216 L 558 174 L 572 174 Z",
                facets: [
                    ["622,154 598,172 598,220 622,242", ROOF_LIGHT],
                    ["572,154 622,154 598,172", ROOF_DARK],
                    ["558,174 558,216 572,195", ROOF_DARK],
                    ["558,174 572,174 572,195", ROOF_LIGHT]
                ]
            },
            // Edificio N (Clinicas Medicas Odontologicas - Inverted L)
            {
                node: "buildingN", bldg: "N", badge: "N", badgeClass: "badge-magenta", badgeX: 386, badgeY: 256,
                path: "M 364 230 L 510 230 L 510 340 L 464 340 L 464 276 L 364 276 Z",
                facets: [
                    ["364,230 510,230 487,253 364,253", ROOF_LIGHT],
                    ["510,230 510,340 487,318 487,253", ROOF_LIGHT],
                    ["364,230 364,276 386,253", ROOF_DARK],
                    ["464,340 510,340 487,318", ROOF_DARK]
                ]
            },
            // Edificio D (Odontologia Digital)
            {
                node: "buildingD", bldg: "D", badge: "D", badgeClass: "badge-green", badgeX: 404, badgeY: 314,
                path: "M 384 300 L 424 300 L 424 328 L 417 328 L 417 338 L 391 338 L 391 328 L 384 328 Z",
                facets: [
                    ["384,300 424,300 424,315 384,315", ROOF_LIGHT],
                    ["384,300 384,328 399,314", ROOF_DARK]
                ]
            },
            // Edificio M (Postgrados - Cruciform)
            {
                node: "buildingM", bldg: "M", badge: "M", badgeClass: "badge-teal", badgeX: 612, badgeY: 432,
                path: "M 592 404 L 636 404 L 636 466 L 592 466 L 592 452 L 578 452 L 578 418 L 592 418 Z",
                facets: [
                    ["614,415 636,404 636,466 614,454", ROOF_LIGHT],
                    ["578,418 578,452 592,435", ROOF_DARK],
                    ["592,404 636,404 614,415", ROOF_DARK],
                    ["592,466 636,466 614,454", ROOF_DARK]
                ]
            },
            // Edificio K (Cafeteria Central - Dogleg)
            {
                node: "buildingK", bldg: "K", badge: "K", badgeClass: "badge-amber", badgeX: 358, badgeY: 518,
                path: "M 338 498 L 376 498 L 376 506 L 398 534 L 398 556 L 378 556 L 378 540 L 374 540 L 374 556 L 338 556 Z",
                facets: [
                    ["338,498 358,510 358,542 338,556", ROOF_LIGHT],
                    ["376,506 398,534 398,556 388,546 388,534 376,520", ROOF_LIGHT],
                    ["338,498 376,498 358,510", ROOF_DARK],
                    ["338,556 374,556 358,542", ROOF_DARK]
                ]
            },
            // Edificio I (Rectoria & Biblioteca Central - U-shape)
            {
                node: "buildingI", bldg: "I", badge: "I", badgeClass: "badge-navy", badgeX: 762, badgeY: 656,
                path: "M 748 598 L 798 598 L 798 704 L 728 704 L 728 634 L 752 634 L 752 680 L 774 680 L 774 622 L 748 622 Z",
                facets: [
                    ["748,598 798,598 784,612 762,612", ROOF_LIGHT],
                    ["798,598 798,704 784,690 784,612", ROOF_LIGHT],
                    ["728,634 740,646 740,690 728,704", ROOF_LIGHT],
                    ["728,704 798,704 784,690 740,690", ROOF_DARK]
                ]
            },
            // Edificio L (Cultura & Complejo Deportivo)
            {
                node: "buildingL", bldg: "L", badge: "L", badgeClass: "badge-cyan", badgeX: 982, badgeY: 622,
                path: "M 964 590 L 996 590 L 996 668 L 972 668 L 972 618 L 964 618 Z",
                facets: [
                    ["964,590 996,590 984,606 964,606", ROOF_LIGHT],
                    ["996,590 996,668 984,656 984,606", ROOF_LIGHT],
                    ["972,668 996,668 984,656", ROOF_DARK]
                ]
            }
        ];

        for (const cfg of customBuildings) {
            addCustomBuilding(layer, cfg);
        }

        // --- Secondary Campus Pavilions, Kiosks, Restrooms & East Complex Buildings ---
        // (All clean architectural teal hipped roofs, no cluttered physical-sign text)
        const supportBuildings = [
            // West & North-Central pavilions
            { x: 60, y: 288, w: 30, h: 20 },       // Acopio
            { x: 244, y: 150, w: 34, h: 28 },      // Estacion Meteorologica
            { x: 284, y: 318, w: 18, h: 17 },      // Kiosko Plaza Chilamates
            { x: 528, y: 248, w: 16, h: 15 },      // Small annex 1 below O
            { x: 548, y: 248, w: 16, h: 15 },      // Small annex 2 below O
            { x: 528, y: 282, w: 30, h: 28 },      // Ranchon
            { x: 522, y: 322, w: 11, h: 15 },      // Lab Digital FIA
            { x: 224, y: 512, w: 20, h: 13 },      // Ranpro booth
            // Sports North & Mid Concourse pavilions
            { x: 902, y: 50, w: 36, h: 30 },       // Kiosko NE
            { x: 978, y: 46, w: 38, h: 30 },       // Sanitarios NE
            { x: 774, y: 325, w: 30, h: 28 },      // Kiosko Mid
            { x: 844, y: 325, w: 30, h: 28 },      // Sanitarios Mid
            { x: 944, y: 320, w: 42, h: 31 },      // Oficina de Deportes
            // East / Bottom-Right Complex
            { x: 974, y: 548, w: 28, h: 24 },      // Sanitarios Publicos
            { x: 954, y: 676, w: 32, h: 22 },      // Fisioterapia
            { x: 1018, y: 664, w: 40, h: 30 },     // Bodega / Warehouse
            { x: 1086, y: 656, w: 48, h: 22 },     // Kiosko Jaguar Sport
            { x: 1030, y: 714, w: 36, h: 28 },     // Artes Marciales (West)
            { x: 1084, y: 714, w: 56, h: 28 },     // Artes Marciales (East)
            { x: 1024, y: 754, w: 44, h: 36 },     // Usos Multiples (West)
            { x: 1082, y: 754, w: 60, h: 28 },     // Usos Multiples (East)
            { x: 1014, y: 812, w: 46, h: 24 },     // Comedor (West)
            { x: 1082, y: 812, w: 56, h: 24 }      // Comedor (East)
        ];

        for (const sb of supportBuildings) {
            addRectBuilding(layer, { ...sb, borderWidth: 2.2 });
        }

        // Container Area (Area de Contenedores - bottom east utility pad)
        const cont = el("g", { id: "containerArea" }, layer);
        el("rect", { x: 914, y: 804, width: 28, height: 18, fill: "#94a3b8", stroke: ROOF_BORDER, "stroke-width": 1.8 }, cont);
        el("line", { x1: 928, y1: 804, x2: 928, y2: 822, stroke: ROOF_BORDER, "stroke-width": 1.2 }, cont);

        // Main South Gate (Entrada Principal)
        const gate = el("g", { class: "bldg-shape", "data-node": "mainParking", "data-bldg": "ENTRADA" }, layer);
        el("rect", { x: 292, y: 754, width: 52, height: 22, fill: ROOF_BORDER, stroke: ROOF_BORDER, "stroke-width": 2, filter: "url(#bldgShadow)" }, gate);
    }

    // ----------------------------------------------------------------------------
    // 7. Layer 6: Landscaping (Trees & Bush Rows via Reusable SVG Symbols)
    // ----------------------------------------------------------------------------
    function renderLandscaping(layer) {
        // Large canopy tree rows [x1, y1, x2, y2, count]
        const largeTreeRows = [
            // West parking divider & medians
            [86, 344, 244, 344, 9],
            [148, 398, 218, 398, 5],
            [150, 444, 220, 444, 5],
            // West & east edges of South Main Parking (clean spacing beside Building E)
            [316, 580, 334, 718, 9],
            [504, 514, 504, 650, 9],
            // South of Plaza Central
            [396, 562, 486, 562, 5],
            // South parking horizontal rows (3 iconic tree dividers)
            [390, 672, 498, 682, 6],
            [386, 706, 516, 718, 7],
            [562, 708, 686, 720, 7],
            [380, 744, 744, 774, 19],
            // East of SE Parking / West of Building I
            [698, 596, 712, 702, 8],
            // Between Building I and Jaguar Center
            [818, 582, 824, 686, 7],
            // West edge of Baseball Stadium
            [706, 134, 712, 286, 9],
            // South edge of Baseball Stadium
            [818, 304, 1044, 304, 4],
            // West edge of Soccer Field
            [732, 358, 744, 530, 10],
            // South edge of Soccer Field
            [764, 538, 926, 538, 9],
            [974, 538, 1094, 538, 7]
        ];

        for (const [x1, y1, x2, y2, count] of largeTreeRows) {
            addTreeRow(layer, x1, y1, x2, y2, count, "#treeLarge");
        }

        // Individual accent trees (Plaza Chilamates, near P, F, Jaguar Gym, East)
        const singleTrees = [
            [304, 248], [368, 152], [338, 560], [358, 560],
            [632, 574], [652, 574], [668, 574],
            [826, 732], [856, 732], [896, 732], [954, 704], [1138, 796]
        ];
        for (const [x, y] of singleTrees) {
            el("use", { href: "#treeLarge", x, y }, layer);
        }

        // Small manicured bush / hedge rows [x1, y1, x2, y2, count]
        const bushRows = [
            // Plaza Chilamates west hedge
            [266, 250, 266, 308, 8],
            // West side of Building N
            [340, 246, 340, 286, 5],
            // East side of Central Parking (west of H)
            [506, 346, 514, 386, 6],
            [520, 346, 526, 386, 6],
            // Below H & East of M
            [592, 394, 626, 394, 5],
            [676, 434, 676, 464, 5],
            // Inside C-B Courtyard (west & east of central bridge)
            [344, 427, 424, 427, 7],
            [464, 427, 554, 427, 8],
            [344, 443, 424, 443, 7],
            [464, 443, 554, 443, 8],
            // South perimeter of Building B
            [346, 474, 438, 474, 9],
            [458, 474, 514, 474, 6],
            // Around Building F & SE Parking
            [628, 624, 634, 668, 5],
            // Around Building L & Jaguar Center east corridor
            [952, 588, 952, 656, 7]
        ];

        for (const [x1, y1, x2, y2, count] of bushRows) {
            addTreeRow(layer, x1, y1, x2, y2, count, "#treeSmall");
        }
    }

    // ----------------------------------------------------------------------------
    // 8. Layer 7: Emergency Layer (Safe Areas, Meeting Points & Evacuation Routes)
    // ----------------------------------------------------------------------------
    function renderEmergencyLayer(layer) {
        const evacuationPaths = [
            // Building P & N -> Meeting Point 2 (East of O, routed around O's north edge) & N assembly
            "M 325 140 L 325 202 L 422 202 L 422 224",
            "M 562 138 L 628 144 L 646 184",
            "M 624 182 L 640 194",
            "M 622 238 L 656 238 L 656 218",
            "M 336 296 L 336 220 L 422 220",
            "M 512 292 L 526 292 L 526 216",

            // Buildings A, B, C, K, E -> Meeting Point 4 (Plaza Central Ruben Dario)
            "M 352 472 L 352 494 L 426 508",
            "M 448 472 L 448 492",
            "M 504 472 L 468 500",
            "M 400 524 L 426 518",
            "M 518 522 L 470 518",

            // Buildings H, M, G, F, E, I -> Meeting Point 5 (East Spine Road)
            "M 688 380 L 692 468 L 668 504",
            "M 638 446 L 654 498",
            "M 566 468 L 628 468 L 648 504",
            "M 618 514 L 640 516",
            "M 618 560 L 646 530",
            "M 664 646 L 664 584 L 658 532",
            "M 748 606 L 720 578 L 668 528",
            "M 796 712 L 702 712 L 702 588 L 670 530",

            // Sports Concourse -> Meeting Point 3 (Soccer Field)
            "M 754 338 L 876 426",

            // Jaguar Center, L, Gym, Courts, East Complex -> Meeting Point 3 (Soccer Field)
            "M 848 574 L 848 558 L 938 558 L 938 474",
            "M 962 612 L 948 612 L 948 558 L 938 558",
            "M 996 732 L 996 678 L 948 678 L 948 568",
            "M 1068 818 L 1068 696 L 996 696 L 996 678",
            "M 1054 644 L 1054 580 L 1006 580 L 950 558"
        ];

        // Crisp white halo underneath so green dashed routes stay legible on dark grass & light roads
        const casingGroup = el("g", {
            fill: "none",
            stroke: "#ffffff",
            "stroke-width": 4,
            "stroke-dasharray": "5,4",
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            opacity: 0.85
        }, layer);

        // 7A. Green Dashed Evacuation Routes with Directional Arrowheads
        const routesGroup = el("g", {
            id: "emergencyRoutesGroup",
            fill: "none",
            stroke: "#15803d",
            "stroke-width": 2.2,
            "stroke-dasharray": "5,4",
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
        }, layer);

        for (const d of evacuationPaths) {
            el("path", { d }, casingGroup);
            el("path", { d, "marker-end": "url(#evacArrow)" }, routesGroup);
        }

        // 7B. Safe Area / Meeting Point Green Circles with Checkmarks
        const pointsGroup = el("g", { id: "emergencySafePointsGroup" }, layer);
        const safePoints = [
            { cx: 866, cy: 194, r: 18 },   // Baseball Stadium Outfield
            { cx: 656, cy: 200, r: 11 },   // East of Building O
            { cx: 904, cy: 446, r: 21 },   // Soccer Field Center
            { cx: 448, cy: 514, r: 18 },   // Plaza Central Ruben Dario
            { cx: 656, cy: 516, r: 11 }    // Spine Road East of G/F
        ];

        for (const pt of safePoints) {
            const g = el("g", { class: "safe-point-marker" }, pointsGroup);
            // Soft outer safe-zone halo ring
            el("circle", {
                cx: pt.cx, cy: pt.cy, r: pt.r + 4,
                fill: "#22c55e", opacity: 0.22
            }, g);
            // Solid dark-green circle badge
            el("circle", {
                cx: pt.cx, cy: pt.cy, r: pt.r,
                fill: "#166534", stroke: "#ffffff", "stroke-width": 2.2
            }, g);
            // Crisp white checkmark scaled to radius
            const s = pt.r * 0.45;
            el("path", {
                d: `M ${pt.cx - s} ${pt.cy + s * 0.05} L ${pt.cx - s * 0.2} ${pt.cy + s * 0.8} L ${pt.cx + s * 1.1} ${pt.cy - s * 0.7}`,
                fill: "none", stroke: "#ffffff", "stroke-width": Math.max(2, pt.r * 0.16),
                "stroke-linecap": "round", "stroke-linejoin": "round"
            }, g);
        }
    }

    // ----------------------------------------------------------------------------
    // 9. Bootstrap Renderer & Emergency Layer Toggle
    // ----------------------------------------------------------------------------
    function renderCampusMap() {
        const svg = document.getElementById("officialCampus2dSvg");
        if (!svg || svg.dataset.rendered === "true") return;
        svg.dataset.rendered = "true";

        const layers = {
            roads: document.getElementById("roadsLayer"),
            parking: document.getElementById("parkingLayer"),
            sports: document.getElementById("sportsComplexLayer"),
            plazas: document.getElementById("plazasLayer"),
            buildings: document.getElementById("buildingsLayer"),
            landscaping: document.getElementById("landscapingLayer"),
            emergency: document.getElementById("emergencyEvacuationLayer")
        };

        if (layers.roads) renderRoads(layers.roads);
        if (layers.parking) renderParking(layers.parking);
        if (layers.sports) renderSports(layers.sports);
        if (layers.plazas) renderPlazas(layers.plazas);
        if (layers.buildings) renderBuildings(layers.buildings);
        if (layers.landscaping) renderLandscaping(layers.landscaping);
        if (layers.emergency) renderEmergencyLayer(layers.emergency);

        // Wire toolbar toggle button for the Emergency Evacuation Layer
        const btnEmergency = document.getElementById("btnToggleEmergencyLayer");
        if (btnEmergency && layers.emergency) {
            btnEmergency.addEventListener("click", () => {
                const isHidden = layers.emergency.classList.toggle("hidden");
                btnEmergency.classList.toggle("bg-emerald-100", !isHidden);
                btnEmergency.classList.toggle("text-emerald-800", !isHidden);
                btnEmergency.classList.toggle("bg-slate-100", isHidden);
                btnEmergency.classList.toggle("text-slate-500", isHidden);
                btnEmergency.setAttribute("aria-pressed", String(!isHidden));
            });
        }
    }

    // Run immediately when loaded after the SVG markup (so campus2dMap.js sees all .bldg-shape nodes)
    if (document.getElementById("officialCampus2dSvg")) {
        renderCampusMap();
    } else {
        document.addEventListener("DOMContentLoaded", renderCampusMap);
    }
})();
