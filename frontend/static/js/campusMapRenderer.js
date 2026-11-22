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
        buildingL: { x: 975, y: 612 },
        buildingM: { x: 612, y: 435 },
        buildingN: { x: 436, y: 260 },
        buildingO: { x: 597, y: 196 },
        buildingP: { x: 450, y: 115 },
        mainParking: { x: 298, y: 766 },
        chilamatesPlaza: { x: 300, y: 292 },
        sportsZone: { x: 918, y: 447 },
        jaguarCenter: { x: 886, y: 623 },
        jaguarGym: { x: 955, y: 726 },
        physiotherapy: { x: 964, y: 677 },
        northGate: { x: 232, y: 74 },
        northeastGate: { x: 645, y: 16 }
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
            badge, badgeClass, badgeX, badgeY, badgeSize = 20,
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
            addBadge(g, badgeX ?? (x + w / 2), badgeY ?? (y + h / 2), badge, badgeClass, badgeSize);
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
    // 2. Layer 1: Campus Perimeter & Internal Vehicle Roads
    // ----------------------------------------------------------------------------
    function renderRoads(layer) {
        // 1A. Secondary walkways & parking driveways (flat pale slate, no lane dashes)
        const connectors = [
            // Driveway into North PON parking (between P and N)
            { d: "M 244 186 L 330 186", w: 13, color: "#cbd5e1" },
            // Driveway into Central CD parking (between Chilamates and A)
            { d: "M 262 366 L 310 366", w: 13, color: "#cbd5e1" },
            // Driveway into Upper & Lower West Parking from West Main Avenue
            { d: "M 218 264 L 252 264", w: 15, color: "#cbd5e1" },
            { d: "M 248 430 L 274 430", w: 15, color: "#cbd5e1" },
            // Driveways from South Main Avenue into upper parking bays & center entry into North/Main-Entrance lot
            { d: "M 634 676 L 634 696", w: 13, color: "#cbd5e1" },
            { d: "M 484 696 L 484 734", w: 16, color: "#cbd5e1" },
            { d: "M 678 696 L 678 742", w: 16, color: "#cbd5e1" },
            // Pedestrian sports concourse between Baseball Stadium and Soccer Field
            { d: "M 708 338 L 1140 338", w: 22, color: "#dce2ec" },
            // Pedestrian corridor cleanly running between Building L/Jaguar Gym and Courts/East Complex
            { d: "M 992 542 L 994 842", w: 10, color: "#e4e9f2" }
        ];

        for (const r of connectors) {
            el("path", { d: r.d, "stroke-width": r.w, stroke: r.color }, layer);
        }

        // 1B. Main Campus Vehicle Road Network (exact loop & access branches from official maps)
        // Drawn in 3 clean layered strokes (curb edge -> asphalt -> subtle center dashes)
        const mainVehiclePaths = [
            // Main Entrance (Entrada Principal) -> SW Corner -> West Avenue -> NW Arch -> Top T-Junction
            "M 298 766 L 298 702 C 294 600, 276 470, 260 340 C 248 245, 236 165, 234 92 C 232 46, 268 24, 385 17 L 645 15",
            // Tercer Acceso (NW gate stub branching west)
            "M 234 74 L 176 74",
            // Camino Segundo Acceso (continuing east from Top T-Junction)
            "M 645 15 L 1120 12",
            // South Internal Ring (Dead-horizontal South Avenue -> SE rounded curve -> Central Spine North -> Top T-Junction)
            "M 298 702 Q 298 696 314 696 L 678 696 Q 706 696 706 668 L 706 430 C 708 345, 678 270, 662 185 L 645 15",
            // SE Branch connecting SE Curve -> Building I Parking Lot -> Jaguar Center Parking
            "M 694 696 Q 710 742 742 744 L 836 744"
        ];

        const roadCurb = el("g", { class: "main-road-curb", fill: "none", stroke: "#9aa8be", "stroke-width": 23, "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        const roadFill = el("g", { class: "main-road-asphalt", fill: "none", stroke: "#bcc6d6", "stroke-width": 19, "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        const roadDash = el("g", { class: "main-road-centerline", fill: "none", stroke: "#ffffff", "stroke-width": 1.3, "stroke-dasharray": "7,6", "stroke-linecap": "round", opacity: 0.72 }, layer);

        for (const d of mainVehiclePaths) {
            el("path", { d }, roadCurb);
            el("path", { d }, roadFill);
            el("path", { d }, roadDash);
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

        // 2.1 Behind Building P (angled north entrance, clean clearance below NW arch road)
        makeLot("parkingLotBehindP", "path", {
            d: "M 344 30 L 420 30 L 522 32 A 6 6 0 0 1 528 38 L 528 76 A 6 6 0 0 1 522 82 L 428 82 L 344 30 Z"
        }, (_, l) => {
            addStallRow(l, 368, 40, 428, 78, 6, 5.5, -9, true);   // SW diagonal stalls
            addStallRow(l, 438, 35, 506, 35, 8, 0, 11, true);     // Top row
            addStallRow(l, 434, 78, 504, 78, 8, 0, -11, true);    // Bottom row
            addStallRow(l, 523, 40, 523, 75, 5, -11, 0, true);    // East column
        });

        // 2.2 West Side of Building P (East of West Main Avenue, above Weather Station)
        makeLot("parkingLotSideP", "rect", { x: 250, y: 96, width: 46, height: 50, rx: 4 }, (_, l) => {
            addStallRow(l, 254, 101, 254, 141, 5, 11, 0, true);
            addStallRow(l, 292, 101, 292, 141, 5, -11, 0, true);
        });

        // 2.3 North Parking (Between Building P, Building O, and Building N)
        makeLot("parkingLotNorthPON", "path", {
            d: "M 294 176 L 330 176 L 330 158 L 538 158 L 538 214 L 330 214 L 330 194 L 294 194 Z"
        }, (_, l) => {
            addStallRow(l, 338, 160, 530, 160, 26, 0, 13);
            addStallRow(l, 338, 212, 530, 212, 26, 0, -13);
        });

        // 2.4 Upper West Parking Lot (North of west tree line, West of West Main Avenue)
        makeLot("parkingLotWestUpper", "path", {
            d: "M 78 202 L 228 202 L 242 328 L 88 328 L 88 310 L 78 202 Z"
        }, (g, l) => {
            // Two full double-sided horizontal bays
            addStallRow(l, 88, 206, 204, 206, 14, 0, 18, true);
            addStallRow(l, 90, 262, 204, 262, 14, 0, -17, true);
            addStallRow(l, 92, 268, 204, 268, 14, 0, 17, true);
            addStallRow(l, 94, 322, 202, 322, 13, 0, -17, true);
            // Right-side moto stalls pocket
            el("rect", { x: 208, y: 294, width: 26, height: 28, rx: 3, fill: "#cfd8e3", stroke: "#ffffff", "stroke-width": 1 }, g);
            addStallRow(l, 210, 298, 232, 298, 4, 0, 9);
            addStallRow(l, 210, 319, 232, 319, 4, 0, -9);
        });

        // 2.5 Lower West Parking Lot (South of west tree line, West of West Main Avenue)
        makeLot("parkingLotWestLower", "path", {
            d: "M 76 364 L 250 364 L 266 504 L 84 494 Z"
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

        // 2.8 East Vertical Roadside Parking Strips (West side of Central Spine Road)
        makeLot("parkingLotEastO", "rect", { x: 626, y: 204, width: 24, height: 64, rx: 4 }, (_, l) => {
            addStallRow(l, 629, 210, 629, 262, 8, 11, 0, true);
        });
        makeLot("parkingLotEastGF", "rect", { x: 664, y: 462, width: 26, height: 110, rx: 4 }, (_, l) => {
            addStallRow(l, 667, 468, 667, 566, 14, 12, 0, true);
        });

        // 2.9 Main South Parking Lot (Upper bay cleanly above the horizontal South Main Avenue)
        makeLot("parkingLotSouthMain", "path", {
            d: "M 314 568 L 500 568 L 500 678 L 318 678 Z"
        }, (g, l) => {
            addStallRow(l, 336, 574, 490, 574, 14, 0, 15, true);
            addStallRow(l, 340, 616, 490, 616, 14, 0, -13, true);
            addStallRow(l, 340, 620, 490, 620, 14, 0, 13);
            addStallRow(l, 342, 660, 492, 660, 14, 0, -13, true);
            // Crisp white horizontal curb along south edge of upper lot
            el("line", { x1: 344, y1: 672, x2: 472, y2: 672, stroke: "#ffffff", "stroke-width": 1.4, "stroke-linecap": "round" }, g);
        });

        // 2.9B North (Compass-North / Main-Entrance) Parking Strip — Dead-Horizontal, Separated from Main Entrance
        makeLot("parkingLotSouthLower", "path", {
            d: "M 342 712 L 692 712 L 692 764 L 682 764 L 682 780 L 560 780 L 560 764 L 542 764 L 542 780 L 414 780 L 414 764 L 372 764 L 376 782 L 348 782 L 342 758 Z"
        }, (g, l) => {
            // Crisp white horizontal planter curb dividers above the two tree blocks (with center driveway opening)
            el("path", { d: "M 356 717 L 468 717", fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round" }, g);
            el("path", { d: "M 502 717 L 630 717", fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round" }, g);
            // Single straight horizontal row of perpendicular parking stalls split into 2 clean bays
            addStallRow(l, 354, 742, 470, 742, 15, 0, 13);
            addStallRow(l, 498, 742, 626, 742, 16, 0, 13);
        });

        // 2.10 South-East Parking Lot (Between E Annexes, F, and Spine Road, with I-shaped median)
        makeLot("parkingLotSouthEF", "path", {
            d: "M 582 596 L 686 596 L 686 666 A 14 14 0 0 1 672 680 L 582 680 Z"
        }, (g, l) => {
            // Center I-shaped raised concrete median island
            el("path", {
                d: "M 616 606 L 652 606 A 2.5 2.5 0 0 1 652 611 L 641 611 L 641 661 L 652 661 A 2.5 2.5 0 0 1 652 666 L 616 666 A 2.5 2.5 0 0 1 616 661 L 627 661 L 627 611 L 616 611 A 2.5 2.5 0 0 1 616 606 Z",
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            // 4 neat columns of stalls (west curb, left of island, right of island, east curb)
            addStallRow(l, 586, 602, 586, 666, 9, 13, 0, true);
            addStallRow(l, 626, 616, 626, 656, 6, -13, 0);
            addStallRow(l, 642, 616, 642, 656, 6, 13, 0);
            addStallRow(l, 682, 602, 682, 666, 9, -13, 0, true);
        });

        // 2.11 & 2.12 Unified Building I + Jaguar Gym / Jaguar Center Parking Lot
        // Single continuous asphalt footprint matching the official close-up geometry & bottom step
        makeLot("parkingLotJaguarGymAndI", "path", {
            d: [
                "M 692 710 L 804 710 L 804 744 L 814 744 L 814 680 L 928 680 Q 934 680 934 686",
                "L 934 700 L 930 700 L 930 750 L 974 750 L 974 772 L 858 772 L 858 786",
                "L 718 786 L 718 766 L 692 766 Z"
            ].join(" ")
        }, (_, l) => {
            // Building I angled parking bay (11 diagonal // stalls with white back curb)
            addStallRow(l, 718, 715, 800, 715, 11, -7, 14, true);
            // Jaguar Gym / Jaguar Center Parking bays (exact stall layout from official map)
            addStallRow(l, 832, 684, 920, 684, 10, 0, 13, true);    // Top row below Jaguar Center
            addStallRow(l, 818, 698, 818, 748, 7, 14, 0, true);     // West column beside Building I sidewalk pier
            addStallRow(l, 926, 704, 926, 748, 7, -14, 0, true);    // East column beside Jaguar Gym
            addStallRow(l, 818, 766, 964, 766, 22, 0, -13, true);   // Bottom straight row extending under Jaguar Gym
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

        // 3C. Outdoor Courts East of Building L: Tennis/Multi-Sport Court + Sand Volleyball Court
        const cts = el("g", { id: "sportsCourts", class: "bldg-shape", "data-node": "buildingL", "data-bldg": "CANCHAS" }, layer);

        // Left Court: Full Tennis / Multi-Sport Court with exact singles/doubles & service lines
        el("rect", { x: 998, y: 568, width: 64, height: 74, fill: "#cbd5e1", stroke: ROOF_BORDER, "stroke-width": 2.2 }, cts);
        el("rect", { x: 1004, y: 573, width: 52, height: 64, fill: "#2563eb", stroke: "#ffffff", "stroke-width": 1.3 }, cts);
        const tl = el("g", { stroke: "#ffffff", "stroke-width": 1.15, fill: "none" }, cts);
        el("line", { x1: 1012, y1: 573, x2: 1012, y2: 637 }, tl); // Left singles sideline
        el("line", { x1: 1048, y1: 573, x2: 1048, y2: 637 }, tl); // Right singles sideline
        el("line", { x1: 1004, y1: 605, x2: 1056, y2: 605 }, tl); // Center net line
        el("line", { x1: 1012, y1: 588, x2: 1048, y2: 588 }, tl); // North service line
        el("line", { x1: 1012, y1: 622, x2: 1048, y2: 622 }, tl); // South service line
        el("line", { x1: 1030, y1: 588, x2: 1030, y2: 622 }, tl); // Center service line

        // Right Court: Sand Volleyball Court (shorter portrait sand box with white court + center net)
        el("rect", { x: 1068, y: 568, width: 48, height: 56, fill: "#e6c88c", stroke: ROOF_BORDER, "stroke-width": 2.2 }, cts);
        el("rect", { x: 1077, y: 576, width: 30, height: 40, fill: "#d9b46e", stroke: "#ffffff", "stroke-width": 1.3 }, cts);
        el("line", { x1: 1077, y1: 596, x2: 1107, y2: 596, stroke: "#ffffff", "stroke-width": 1.3 }, cts);
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
            { x: 534, y: 672, w: 46, h: 12, node: "buildingE", bldg: "E", orientation: "ribV", borderWidth: 2.5 },
            // Edificio H (Laboratorios de Medicina) + small west wing
            { x: 604, y: 354, w: 84, h: 32, node: "buildingH", bldg: "H", badge: "H", badgeClass: "badge-green", badgeX: 646, badgeY: 370, orientation: "h" },
            { x: 576, y: 356, w: 24, h: 20, node: "buildingH", bldg: "H", orientation: "h", borderWidth: 2.5 },
            // Edificio G (Auditorio Central & Derecho)
            { x: 568, y: 488, w: 48, h: 44, node: "buildingG", bldg: "G", badge: "G", badgeClass: "badge-cyan", orientation: "v" },
            // Edificio F (FACEE)
            { x: 568, y: 540, w: 48, h: 48, node: "buildingF", bldg: "F", badge: "F", badgeClass: "badge-magenta", orientation: "v" },
            // Jaguar Gym (vertical hipped-roof geometry matching close-up signage, clickable navigation node)
            { x: 934, y: 704, w: 42, h: 44, node: "jaguarGym", bldg: "JAGUAR GYM", orientation: "v" },
            // Physiotherapy Building / Fisioterapia (hipped roof north of Jaguar Gym, clickable navigation node)
            { x: 944, y: 668, w: 40, h: 22, node: "physiotherapy", bldg: "FISIOTERAPIA", orientation: "v", borderWidth: 2.5 },
            // Edificio L — Two separate twin squares (matching official signage)
            { x: 964, y: 588, w: 22, h: 20, node: "buildingL", bldg: "L", badge: "L", badgeClass: "badge-magenta", badgeSize: 13, orientation: "v", borderWidth: 2.2 },
            { x: 964, y: 616, w: 22, h: 20, node: "buildingL", bldg: "L", badge: "L", badgeClass: "badge-magenta", badgeSize: 13, orientation: "v", borderWidth: 2.2 }
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
            // Edificio I (Rectoria & Biblioteca Central - U-shape, cleanly above its own parking lot)
            {
                node: "buildingI", bldg: "I", badge: "I", badgeClass: "badge-navy", badgeX: 762, badgeY: 652,
                path: "M 748 594 L 798 594 L 798 700 L 728 700 L 728 630 L 752 630 L 752 676 L 774 676 L 774 618 L 748 618 Z",
                facets: [
                    ["748,594 798,594 784,608 762,608", ROOF_LIGHT],
                    ["798,594 798,700 784,686 784,608", ROOF_LIGHT],
                    ["728,630 740,642 740,686 728,700", ROOF_LIGHT],
                    ["728,700 798,700 784,686 740,686", ROOF_DARK]
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
            { x: 254, y: 150, w: 34, h: 28 },      // Estacion Meteorologica
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
            // East / Bottom-Right Sports & Service Complex (exact layout from close-up signage)
            { x: 964, y: 550, w: 24, h: 20, orientation: "v" },   // Public Washrooms (above Building L)
            { x: 962, y: 646, w: 24, h: 16, orientation: "h" },   // Small nameless pavilion (between L & Physiotherapy)
            { x: 1012, y: 652, w: 40, h: 24, orientation: "v" },  // Warehouse (Bodega)
            { x: 1074, y: 630, w: 42, h: 22, orientation: "h" },  // Jaguar Sport Kiosk (main pavilion below sand volleyball)
            { x: 1104, y: 666, w: 26, h: 14, orientation: "h" },  // Jaguar Sport Kiosk (small east booth)
            { x: 1076, y: 684, w: 58, h: 26, orientation: "v" },  // Martial Arts Building (Artes Marciales)
            { x: 1078, y: 720, w: 58, h: 24, orientation: "h" },  // Multipurpose Room (Usos Multiples)
            { x: 1080, y: 792, w: 56, h: 24, orientation: "h" },  // Lunch Area (Comedor)

            // Nameless Modular Complex (stacked corrugated awnings & hipped roofs south of Warehouse)
            { x: 1006, y: 682, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1006, y: 698, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1006, y: 718, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1006, y: 734, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1006, y: 754, w: 52, h: 14, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1008, y: 780, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1008, y: 796, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1008, y: 816, w: 52, h: 14, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1008, y: 832, w: 52, h: 10, orientation: "ribV", borderWidth: 1.5, shadow: false }
        ];

        // Subtle dining patio pad beneath Lunch Area (Comedor)
        el("rect", { x: 1068, y: 782, width: 72, height: 42, rx: 2, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1 }, layer);

        for (const sb of supportBuildings) {
            addRectBuilding(layer, { borderWidth: 2.2, ...sb });
        }

        // Main South Gate (Entrada Principal)
        const gate = el("g", { class: "bldg-shape", "data-node": "mainParking", "data-bldg": "ENTRADA" }, layer);
        el("rect", { x: 278, y: 760, width: 40, height: 18, fill: ROOF_BORDER, stroke: ROOF_BORDER, "stroke-width": 2, filter: "url(#bldgShadow)" }, gate);
    }

    // ----------------------------------------------------------------------------
    // 7. Layer 6: Landscaping (Trees & Bush Rows via Reusable SVG Symbols)
    // ----------------------------------------------------------------------------
    function renderLandscaping(layer) {
        // Large canopy tree rows [x1, y1, x2, y2, count]
        const largeTreeRows = [
            // West parking divider & medians
            [86, 344, 240, 344, 9],
            [148, 398, 218, 398, 5],
            [150, 444, 220, 444, 5],
            // West & east edges of South Main Parking (clean spacing beside West Main Avenue & Building E)
            [316, 580, 326, 678, 7],
            [504, 514, 504, 650, 9],
            // South of Plaza Central
            [396, 562, 486, 562, 5],
            // South parking horizontal tree rows (dead-straight horizontal, matching close-up signage)
            [356, 680, 466, 680, 7],      // Below South Upper Parking (left of E)
            [616, 680, 672, 680, 3],      // Below SE Parking (right of Innovacion)
            [358, 725, 466, 725, 7],      // North/Main-Entrance Lot upper row (left block)
            [504, 725, 628, 725, 8],      // North/Main-Entrance Lot upper row (right block)
            [358, 766, 688, 766, 18],     // Bottom straight perimeter tree line
            // West side of Building I (between Spine Road and Building I)
            [718, 598, 718, 692, 6],
            // Between Building I and Jaguar Center (bottom tree anchors NW corner of Jaguar Gym parking)
            [816, 586, 816, 684, 6],
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

        // Individual accent trees (Plaza Chilamates, near P, F, Main Entrance, Jaguar Gym Lot, East Complex)
        const singleTrees = [
            [304, 248], [368, 152], [338, 560], [358, 560],
            [274, 746], [274, 766],
            [632, 574], [652, 574], [668, 574],
            [866, 704], [882, 720], [916, 696],
            [978, 577], [952, 594], [952, 614], [952, 632], [946, 662], [1132, 756]
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
            [628, 624, 634, 668, 5]
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
            "M 796 706 L 702 706 L 702 588 L 670 530",

            // Sports Concourse -> Meeting Point 3 (Soccer Field)
            "M 754 338 L 876 426",

            // Jaguar Center, L, Gym, Physiotherapy, Warehouse, Nameless Complex & Martial Arts -> Soccer Field
            "M 848 574 L 848 558 L 944 558 L 944 474",
            "M 964 598 L 952 598 L 952 580",
            "M 964 626 L 952 626 L 952 642 L 992 642",
            "M 978 724 L 978 696 L 944 696 L 944 566",
            // East walkway corridor cleanly between Building L/Jaguar Gym and Courts/Nameless Complex (zero court overlap!)
            "M 1004 834 L 994 834 L 994 580 L 950 580",
            "M 1018 676 L 1018 682 L 994 682",
            "M 1068 742 L 1066 742 L 1066 678",
            "M 1140 732 L 1140 656"
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

        // Emergency route junction nodes (green circles along east complex walkways)
        const junctionDots = [
            [994, 642], [994, 676], [1004, 682], [1066, 678], [1140, 656], [994, 766]
        ];
        for (const [cx, cy] of junctionDots) {
            el("circle", { cx, cy, r: 3.2, fill: "#166534", stroke: "#ffffff", "stroke-width": 1 }, layer);
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
