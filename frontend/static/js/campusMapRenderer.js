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
        buildingH: { x: 637, y: 369 },
        buildingI: { x: 762, y: 656 },
        buildingJ: { x: 357, y: 316 },
        buildingK: { x: 362, y: 526 },
        buildingL: { x: 975, y: 612 },
        buildingM: { x: 612, y: 435 },
        buildingN: { x: 436, y: 260 },
        buildingO: { x: 597, y: 196 },
        buildingP: { x: 450, y: 115 },
        mainParking: { x: 282, y: 766 },
        chilamatesPlaza: { x: 300, y: 292 },
        sportsZone: { x: 924, y: 447 },
        jaguarCenter: { x: 886, y: 623 },
        jaguarGym: { x: 955, y: 726 },
        physiotherapy: { x: 964, y: 677 },
        northGate: { x: 224, y: 74 },
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
            // Wide seamless asphalt throat connecting West Main Avenue into Central CD Parking
            { d: "M 252 366 L 312 366", w: 28, color: "#dfe5ec" },
            // Wide seamless asphalt throat connecting West Main Avenue into Upper & Lower West Parking
            { d: "M 226 266 L 246 266", w: 120, color: "#dfe5ec" },
            { d: "M 236 432 L 260 432", w: 132, color: "#dfe5ec" },
            // North Sports Parking entry apron connecting down from Camino Segundo Acceso
            { d: "M 808 16 L 808 46", w: 24, color: "#dfe5ec" },
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

        // 1B. Main Campus Vehicle Road Network (balanced uniform boulevard width, zero corner step)
        const westMainPath = "M 282 766 L 282 702 C 278 600, 264 470, 248 340 C 236 245, 226 165, 224 92 C 222 46, 260 24, 380 17 L 645 15";
        const otherMainPaths = [
            // Tercer Acceso (NW gate stub branching west)
            "M 224 74 L 164 74",
            // Camino Segundo Acceso (continuing east from Top T-Junction)
            "M 645 15 L 1120 12",
            // South Internal Ring (Dead-horizontal South Avenue -> SE rounded curve -> Central Spine North -> Top T-Junction)
            "M 282 702 Q 282 696 298 696 L 678 696 Q 706 696 706 668 L 706 430 C 708 345, 678 270, 662 185 L 645 15",
            // SE Branch connecting SE Curve -> Building I Parking Lot -> Jaguar Center Parking
            "M 694 696 Q 710 742 742 744 L 836 744"
        ];

        const roadCurb = el("g", { class: "main-road-curb", fill: "none", stroke: "#9aa8be", "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        const roadFill = el("g", { class: "main-road-asphalt", fill: "none", stroke: "#bcc6d6", "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        const roadDash = el("g", { class: "main-road-centerline", fill: "none", stroke: "#ffffff", "stroke-width": 1.3, "stroke-dasharray": "7,6", "stroke-linecap": "round", opacity: 0.72 }, layer);

        // Balanced Main Vehicle Loop (West boulevard slightly fuller 24px asphalt, rest 20px asphalt)
        el("path", { d: westMainPath, "stroke-width": 28 }, roadCurb);
        el("path", { d: westMainPath, "stroke-width": 24 }, roadFill);
        el("path", { d: westMainPath }, roadDash);

        for (const d of otherMainPaths) {
            el("path", { d, "stroke-width": 24 }, roadCurb);
            el("path", { d, "stroke-width": 20 }, roadFill);
            el("path", { d }, roadDash);
        }

        // Tercer Acceso divided gatehouse island + crosswalk stripes (matching Photo 1 & 9)
        el("rect", { x: 174, y: 71, width: 22, height: 6, rx: 3, fill: "#e2e8f0", stroke: "#ffffff", "stroke-width": 1.2 }, layer);
        el("rect", { x: 162, y: 61, width: 7, height: 26, rx: 1, fill: ROOF_BASE, stroke: ROOF_BORDER, "stroke-width": 1.4 }, layer);
        el("line", { x1: 171, y1: 64, x2: 171, y2: 71, stroke: "#ffffff", "stroke-width": 1.4, "stroke-dasharray": "2,2" }, layer);
        el("line", { x1: 171, y1: 77, x2: 171, y2: 84, stroke: "#ffffff", "stroke-width": 1.4, "stroke-dasharray": "2,2" }, layer);

        // 1C. Designated Bus / Passenger Pull-Out Bay (Lay-By) Beside the East Curb of West Main Avenue
        const layBy = el("g", { id: "mainEntranceLayBy" }, layer);
        // Paved shoulder joining the east edge of West Main Avenue cleanly to the lay-by & 12-tree curb
        el("path", {
            d: "M 282 480 L 298 480 L 318 688 L 292 688 Z",
            fill: "#bcc6d6"
        }, layBy);
        // Darker asphalt lay-by bay pocket cleanly beside the through-lane (zero overlap with road centerline)
        el("path", {
            d: "M 307 572 L 298 572 Q 292 572 292 580 L 300 675 Q 301 684 309 684 L 318 684 Z",
            fill: "#9faec4"
        }, layBy);
        // Crisp white pull-out bay border + vertical curb line continuing straight north past Building K
        el("path", {
            d: "M 297 480 L 307 572 L 298 572 Q 292 572 292 580 L 300 675 Q 301 684 309 684 L 318 684 L 307 572",
            fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round", "stroke-linejoin": "round"
        }, layBy);
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

        // 2.1 Behind Building P (seamless open throat off NW arch road, matching Photo 1)
        makeLot("parkingLotBehindP", "path", {
            d: "M 340 20 L 424 18 L 532 24 A 6 6 0 0 1 538 30 L 538 74 A 6 6 0 0 1 532 80 L 434 80 L 340 24 Z"
        }, (_, l) => {
            addStallRow(l, 368, 34, 434, 76, 8, 5, -9, true);      // SW diagonal stalls
            addStallRow(l, 444, 29, 514, 29, 9, 0, 11, true);     // Top row
            addStallRow(l, 440, 76, 512, 76, 9, 0, -11, true);    // Bottom row
            addStallRow(l, 533, 35, 533, 72, 6, -11, 0, true);    // East column
        });

        // 2.2 West Side of Building P (extends down behind Weather Station on its east column, matching Photo 1 & 9)
        makeLot("parkingLotSideP", "rect", { x: 244, y: 96, width: 48, height: 68, rx: 4 }, (_, l) => {
            addStallRow(l, 248, 101, 248, 144, 5, 11, 0, true);   // Left column above Weather Station
            addStallRow(l, 288, 101, 288, 159, 7, -11, 0, true);  // Right column running beside Weather Station
        });

        // 2.3 North Parking (Between P & N — full apron to West Main Avenue + 3 south curb tabs & NW tree notch, Photo 4 & 5)
        makeLot("parkingLotNorthPON", "path", {
            d: "M 244 179 L 318 179 L 318 164 L 348 164 L 348 158 L 538 158 L 538 214 L 528 214 L 528 221 L 520 221 L 520 214 L 414 214 L 414 221 L 406 221 L 406 214 L 334 214 L 334 221 L 326 221 L 326 214 L 248 214 Z"
        }, (_, l) => {
            addStallRow(l, 330, 160, 532, 160, 26, 0, 14);
            addStallRow(l, 330, 212, 532, 212, 26, 0, -14);
        });

        // 2.4 Upper West Parking Lot (Seamless connection to West Main Avenue, 4 structured stall rows)
        makeLot("parkingLotWestUpper", "path", {
            d: "M 66 202 L 228 202 L 236 330 L 72 330 L 72 304 L 66 202 Z"
        }, (_, l) => {
            addStallRow(l, 76, 206, 200, 206, 15, 0, 14, true);    // Top perimeter row
            addStallRow(l, 76, 244, 198, 244, 15, 0, -13, true);   // Upper center island (north)
            addStallRow(l, 76, 246, 198, 246, 15, 0, 13);          // Upper center island (south)
            addStallRow(l, 78, 288, 196, 288, 14, 0, -13, true);   // Lower center island (north)
            addStallRow(l, 78, 290, 196, 290, 14, 0, 13);          // Lower center island (south)
            addStallRow(l, 80, 326, 196, 326, 14, 0, -13, true);   // Bottom perimeter row
        });

        // 2.5 Lower West Parking Lot (Exact close-up layout: solar-panel strip, T-cap medians, dark corner pad & seamless road entry)
        makeLot("parkingLotWestLower", "path", {
            d: "M 64 360 L 244 360 L 254 504 L 72 504 L 72 496 L 64 496 Z"
        }, (g, l) => {
            // Far-west Solar Panel Canopy strip along left perimeter
            el("rect", { x: 52, y: 366, width: 12, height: 124, fill: "#cbd5e1", stroke: "#94a3b8", "stroke-width": 1.1 }, g);
            for (let sy = 372; sy < 488; sy += 6) {
                el("line", { x1: 52, y1: sy, x2: 64, y2: sy, stroke: "#ffffff", "stroke-width": 0.9 }, g);
            }

            // Far-west vertical perimeter stalls along solar-panel edge (matching Photo 10 & 11)
            addStallRow(l, 66, 372, 66, 488, 12, 11, 0);

            // Top & bottom perimeter stall rows
            addStallRow(l, 80, 363, 214, 363, 15, 0, 13);
            addStallRow(l, 80, 500, 200, 500, 14, 0, -13);

            // Upper T-capped median island (y=398) + perpendicular stalls above & below
            el("path", {
                d: "M 88 391 A 4 4 0 0 0 84 395 L 84 401 A 4 4 0 0 0 88 405 M 84 398 L 208 398 M 204 391 A 4 4 0 0 1 208 395 L 208 401 A 4 4 0 0 1 204 405",
                fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round"
            }, g);
            addStallRow(l, 90, 396, 202, 396, 13, 0, -12);
            addStallRow(l, 90, 400, 202, 400, 13, 0, 12);
            // Small entrance traffic bollard island
            el("rect", { x: 222, y: 393, width: 4, height: 12, rx: 1.5, fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1 }, g);

            // Lower median island (y=446) leading into rounded dark corner planter/service pad
            el("path", {
                d: "M 88 439 A 4 4 0 0 0 84 443 L 84 449 A 4 4 0 0 0 88 453 M 84 446 L 198 446",
                fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round"
            }, g);
            el("rect", {
                x: 198, y: 432, width: 32, height: 32, rx: 5,
                fill: "#aeb9ca", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            addStallRow(l, 90, 444, 194, 444, 12, 0, -12);
            addStallRow(l, 90, 448, 194, 448, 12, 0, 12);
            // Small stalls below the dark corner pad
            addStallRow(l, 202, 466, 224, 466, 3, 0, 11);
        });

        // 2.6 Central Parking Lot (Between N/J/D and Building C — with north double curb & center stair landing, Photo 6 & 7)
        makeLot("parkingLotCentralCD", "path", {
            d: "M 304 366 L 322 344 L 496 344 L 496 395 L 304 395 Z"
        }, (g, l) => {
            el("rect", { x: 304, y: 391, width: 192, height: 4, fill: "#cbd5e1" }, g);
            // Architectural double retaining curb & center stair landing along north edge (Photo 6 & 7)
            el("path", { d: "M 314 362 L 326 348 L 434 345 L 444 341 L 456 345 L 496 344", fill: "none", stroke: "#64748b", "stroke-width": 1.2 }, g);
            el("rect", { x: 438, y: 336, width: 16, height: 11, fill: "#cbd5e1", stroke: "#64748b", "stroke-width": 1 }, g);
            addStallRow(l, 330, 349, 486, 349, 13, -9, 13);   // Angled top stalls
            addStallRow(l, 318, 391, 490, 391, 15, 0, -14);   // Perpendicular bottom stalls
        });

        // Pedestrian Zebra Crosswalk between Plaza Chilamates & Building A Front Plaza
        const cw = el("g", { id: "pedestrianChilamatesToA" }, layer);
        el("rect", { x: 280, y: 344, width: 22, height: 50, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1.2 }, cw);
        for (let y = 350; y <= 388; y += 7) {
            el("line", { x1: 283, y1: y, x2: 299, y2: y, stroke: "#ffffff", "stroke-width": 3 }, cw);
        }

        // 2.7 North-East Sports Parking (North of Baseball Stadium)
        makeLot("parkingLotNorthSports", "rect", { x: 744, y: 42, width: 128, height: 52, rx: 6 }, (_, l) => {
            addStallRow(l, 754, 46, 862, 46, 12, 0, 14, true);
            addStallRow(l, 754, 90, 862, 90, 12, 0, -14, true);
        });

        // 2.8 East & Central-Spine Parking Lots (Full-length roadside bay east of Spine Road beside O, G/F lot, Soccer lot)
        makeLot("parkingLotEastO", "path", {
            d: "M 664 138 L 682 138 L 694 274 L 676 274 Z"
        }, (_, l) => {
            // 14 crisp horizontal perpendicular stalls flush along the east curb of the Spine Road (zero road overlap)
            addStallRow(l, 679, 144, 691, 268, 14, -13, 0, true);
        });
        // Parking Lot on Right (Compass-West) Side of Buildings G & F (with pill median island & dual stall columns)
        makeLot("parkingLotWestGF", "path", {
            d: "M 618 486 L 672 476 L 694 476 L 694 562 L 678 578 L 618 578 Z"
        }, (g, l) => {
            // Left column perpendicular stalls along Building G & Building F
            addStallRow(l, 624, 490, 624, 530, 5, 11, 0);
            addStallRow(l, 624, 542, 624, 574, 5, 11, 0);
            // Vertical pill-shaped raised concrete median island (east of Meeting Point 5)
            el("rect", {
                x: 668, y: 496, width: 7, height: 58, rx: 3.5,
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            // Right column perpendicular stalls along Central Spine Road
            addStallRow(l, 681, 480, 681, 554, 12, 12, 0);
        });
        makeLot("parkingLotSoccerEast", "path", {
            d: "M 716 398 L 735 398 L 735 536 L 716 536 Z"
        }, (_, l) => {
            // 20 crisp perpendicular stalls running along the left (compass-east) side of the Soccer Field
            addStallRow(l, 718, 402, 718, 532, 20, 15, 0);
        });

        // 2.9 Main South Parking Lot (Upper bay cleanly east of the pull-out lay-by & 12-tree line)
        makeLot("parkingLotSouthMain", "path", {
            d: "M 326 568 L 500 568 L 500 680 L 330 680 Z"
        }, (g, l) => {
            addStallRow(l, 344, 574, 490, 574, 13, 0, 15, true);
            addStallRow(l, 346, 616, 490, 616, 13, 0, -13, true);
            addStallRow(l, 346, 620, 490, 620, 13, 0, 13);
            addStallRow(l, 348, 660, 492, 660, 13, 0, -13, true);
            // Crisp white horizontal curb along south edge of upper lot
            el("line", { x1: 360, y1: 673, x2: 472, y2: 673, stroke: "#ffffff", "stroke-width": 1.4, "stroke-linecap": "round" }, g);
            // Curved teal UAM sign-wall accent at the SW corner beside the pull-out bay
            el("path", { d: "M 334 666 Q 341 678 355 674", fill: "none", stroke: "#1da495", "stroke-width": 2, "stroke-linecap": "round" }, g);
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

        // 2.10 South-East Parking Lot (Between E Annexes, F double-tree row, and Spine Road, with I-shaped median)
        makeLot("parkingLotSouthEF", "path", {
            d: "M 582 602 L 686 602 L 686 668 A 14 14 0 0 1 672 682 L 582 682 Z"
        }, (g, l) => {
            // Center I-shaped raised concrete median island
            el("path", {
                d: "M 616 611 L 652 611 A 2.5 2.5 0 0 1 652 616 L 641 616 L 641 663 L 652 663 A 2.5 2.5 0 0 1 652 668 L 616 668 A 2.5 2.5 0 0 1 616 663 L 627 663 L 627 616 L 616 616 A 2.5 2.5 0 0 1 616 611 Z",
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            // 4 neat columns of stalls (west curb, left of island, right of island, east curb)
            addStallRow(l, 586, 608, 586, 668, 9, 13, 0, true);
            addStallRow(l, 626, 621, 626, 658, 6, -13, 0);
            addStallRow(l, 642, 621, 642, 658, 6, 13, 0);
            addStallRow(l, 682, 608, 682, 668, 9, -13, 0, true);
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
        // 3A. Estadio de Beisbol (Exact official sign geometry: concave-corner infield, pitcher lane, dugouts & fan backstop)
        const bb = el("g", { id: "baseballStadium", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "BÉISBOL" }, layer);
        // Outer stadium parcel with smooth SW curve following the spine road
        el("path", {
            d: "M 696 108 L 1076 108 L 1076 312 L 734 312 Q 702 308 696 272 Z",
            fill: "#22c55e", stroke: ROOF_BORDER, "stroke-width": 2.4
        }, bb);
        // Deep outfield grass arc
        el("path", {
            d: "M 744 120 L 1058 120 L 1058 298 L 758 298 A 192 192 0 0 1 744 120 Z",
            fill: "#16a34a", opacity: 0.42
        }, bb);
        // Official upper-right clay infield square with concave base cutouts (Photos 2, 3, 15)
        el("path", {
            d: "M 936 128 L 1020 128 A 10 10 0 0 0 1030 138 L 1030 212 A 10 10 0 0 0 1020 222 L 942 222 A 10 10 0 0 0 932 212 L 932 138 A 10 10 0 0 0 936 128 Z",
            fill: "#b87a4b", stroke: "#ffffff", "stroke-width": 1.4
        }, bb);
        // Outer square boundary frame around infield cutouts
        el("rect", { x: 932, y: 128, width: 98, height: 94, fill: "none", stroke: "#ffffff", "stroke-width": 1, opacity: 0.7 }, bb);
        // White pitcher's lane from home plate (upper-right) to central mound circle
        el("line", { x1: 1025, y1: 133, x2: 981, y2: 175, stroke: "#ffffff", "stroke-width": 4.2, "stroke-linecap": "round" }, bb);
        el("circle", { cx: 981, cy: 175, r: 7.5, fill: "#ffffff", stroke: "#b87a4b", "stroke-width": 1.2 }, bb);
        // Parallel dugout & foul wall architectural lines (top & right edges)
        const dg = el("g", { fill: "none", stroke: "#ffffff", "stroke-width": 1.1, opacity: 0.85 }, bb);
        el("line", { x1: 874, y1: 122, x2: 1034, y2: 122 }, dg);
        el("line", { x1: 896, y1: 116, x2: 1022, y2: 116 }, dg);
        el("line", { x1: 1036, y1: 130, x2: 1036, y2: 264 }, dg);
        el("line", { x1: 1043, y1: 140, x2: 1043, y2: 252 }, dg);
        // Curved segmented backstop grandstand fan wrapping upper-right home plate corner (clean margin inside border)
        for (const r of [9, 13, 17]) {
            el("path", { d: `M ${1024 - r * 0.45} ${132 - r * 0.85} A ${r} ${r} 0 0 1 ${1030 + r * 0.85} ${137 + r * 0.45}`, fill: "none", stroke: "#ffffff", "stroke-width": 1, opacity: 0.85 }, bb);
        }

        // 3B. Cancha de Futbol (Wide proportional soccer pitch with penalty D-arcs & corner arcs, Photo 15)
        const sc = el("g", { id: "soccerField", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "FÚTBOL" }, layer);
        el("rect", { x: 757, y: 372, width: 335, height: 150, fill: "#15803d", stroke: ROOF_BORDER, "stroke-width": 2.5 }, sc);
        const lines = el("g", { stroke: "#ffffff", "stroke-width": 1.8, fill: "none" }, sc);
        el("rect", { x: 768, y: 382, width: 313, height: 130 }, lines);
        el("line", { x1: 924.5, y1: 382, x2: 924.5, y2: 512 }, lines);
        el("circle", { cx: 924.5, cy: 447, r: 24 }, lines);
        el("circle", { cx: 924.5, cy: 447, r: 2.2, fill: "#ffffff" }, lines);
        // Left & right penalty boxes + goal boxes + penalty D-arcs (matching Photo 15)
        el("rect", { x: 768, y: 412, width: 38, height: 70 }, lines);
        el("rect", { x: 768, y: 427, width: 16, height: 40 }, lines);
        el("path", { d: "M 806 431 A 19 19 0 0 1 806 463" }, lines);
        el("rect", { x: 1043, y: 412, width: 38, height: 70 }, lines);
        el("rect", { x: 1065, y: 427, width: 16, height: 40 }, lines);
        el("path", { d: "M 1043 431 A 19 19 0 0 0 1043 463" }, lines);
        // Corner quarter-arcs
        el("path", { d: "M 768 389 A 7 7 0 0 0 775 382 M 1074 382 A 7 7 0 0 0 1081 389 M 1081 505 A 7 7 0 0 0 1074 512 M 775 512 A 7 7 0 0 0 768 505", "stroke-width": 1.2 }, lines);

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
        // 4A. Plaza Chilamates (Paved plaza west of J/N with iconic giant Chilamate tree & corner Kiosk)
        const ch = el("g", { class: "bldg-shape", "data-node": "chilamatesPlaza", "data-bldg": "CHILAMATES" }, layer);
        el("path", {
            d: "M 256 226 L 330 226 L 330 330 L 314 344 L 256 344 Z",
            fill: "#e2e8f0", stroke: "#cbd5e1", "stroke-width": 1.3, "stroke-linejoin": "round"
        }, ch);
        // Iconic large Chilamate specimen canopy & smaller north companion canopy
        el("circle", { cx: 299, cy: 287, r: 15.5, fill: "#3b5e54", stroke: "#28423b", "stroke-width": 1.1 }, ch);
        el("circle", { cx: 295, cy: 283, r: 6.5, fill: "#527d70", opacity: 0.7 }, ch);
        el("circle", { cx: 298, cy: 251, r: 8.5, fill: "#3b5e54", stroke: "#28423b", "stroke-width": 0.9 }, ch);
        el("circle", { cx: 296, cy: 249, r: 3.5, fill: "#527d70", opacity: 0.7 }, ch);

        // 4A-2. Front Entrance Plaza & Curved Steps in Front (Left / Compass-East Side) of Building A
        const frontA = el("g", { id: "buildingAFrontPlaza", "pointer-events": "none" }, layer);
        // Outer rounded drop-off / pedestrian terrace apron wrapping the front of Building A
        el("path", {
            d: "M 310 394 L 290 394 Q 277 394 277 410 L 277 460 Q 277 476 290 476 L 310 476 Z",
            fill: "#e2e8f0", stroke: "#94a3b8", "stroke-width": 1.4
        }, frontA);
        // Inner architectural dark-slate curved planter frames (top & bottom L-brackets)
        el("path", {
            d: "M 308 400 L 290 400 Q 282 400 282 408 L 282 418 L 292 418 L 292 408 L 308 408 Z",
            fill: "#94a3b8", stroke: "#475569", "stroke-width": 1
        }, frontA);
        el("path", {
            d: "M 308 470 L 290 470 Q 282 470 282 462 L 282 452 L 292 452 L 292 462 L 308 462 Z",
            fill: "#94a3b8", stroke: "#475569", "stroke-width": 1
        }, frontA);
        // Subtle twin bracket accent curbs flanking the front stairs
        el("path", { d: "M 288 416 L 296 416 L 296 422", fill: "none", stroke: "#334155", "stroke-width": 1.6, "stroke-linecap": "round" }, frontA);
        el("path", { d: "M 288 454 L 296 454 L 296 448", fill: "none", stroke: "#334155", "stroke-width": 1.6, "stroke-linecap": "round" }, frontA);
        // Concentric curved entry steps leading into Building A's main doorway
        el("path", { d: "M 306 422 Q 294 435 306 448", fill: "none", stroke: "#64748b", "stroke-width": 1.4 }, frontA);
        el("path", { d: "M 309 426 Q 299 435 309 444", fill: "none", stroke: "#64748b", "stroke-width": 1.2 }, frontA);

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
        // Clean grey apron west of Building K (restored to original neutral terrace style)
        el("rect", { id: "greenAreaWestK", x: 314, y: 498, width: 22, height: 58, rx: 2, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1.2 }, pc);
        // Covered skylight walkway connecting Building B down to Building K
        el("rect", { x: 342, y: 470, width: 9, height: 28, fill: "#bae6fd", stroke: "#38bdf8", "stroke-width": 0.9, opacity: 0.85 }, pc);
        for (let wy = 475; wy < 496; wy += 5) {
            el("line", { x1: 342, y1: wy, x2: 351, y2: wy, stroke: "#ffffff", "stroke-width": 0.8 }, pc);
        }
        // Tiled patio north of K
        el("rect", { x: 351, y: 474, width: 27, height: 24, fill: "#e2e8f0", stroke: "#cbd5e1", "stroke-width": 1 }, pc);
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
        // 4C-end: restore pool line right before 4D terrace pads
        el("line", { x1: 391, y1: 489, x2: 419, y2: 489, stroke: "#ffffff", "stroke-width": 0.8, opacity: 0.75 }, pool);

        // 4D. Architectural Paved Courtyard Pads (Building M patio, E-to-G/F terrace, Building I apron — Photos 7, 13, 14)
        const pads = el("g", { id: "campusTerracePads", "pointer-events": "none" }, layer);
        el("rect", { x: 570, y: 400, width: 72, height: 72, rx: 2, fill: "#cbd5e1", opacity: 0.6 }, pads);  // Behind M
        el("rect", { x: 546, y: 488, width: 22, height: 92, rx: 2, fill: "#cbd5e1", opacity: 0.65 }, pads); // Between E & G/F
        el("rect", { x: 738, y: 584, width: 68, height: 118, rx: 2, fill: "#cbd5e1", opacity: 0.55 }, pads); // Around Building I
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
            // Edificio E (Facultad de Medicina) + Vida Estudiantil & Direccion de Innovacion (crisp hipped roofs, Photo 13)
            { x: 520, y: 500, w: 28, h: 156, node: "buildingE", bldg: "E", badge: "E", badgeClass: "badge-navy", badgeX: 534, badgeY: 604, orientation: "v" },
            { x: 554, y: 622, w: 22, h: 48, node: "buildingE", bldg: "E", orientation: "v", borderWidth: 2.5 },
            { x: 532, y: 676, w: 54, h: 14, node: "buildingE", bldg: "E", orientation: "h", borderWidth: 2.5 },
            // Edificio H (Laboratorios de Medicina — main bar + flush west porch + separate lab annex, Photo 7 & 8)
            { x: 596, y: 354, w: 84, h: 30, node: "buildingH", bldg: "H", badge: "H", badgeClass: "badge-green", badgeX: 638, badgeY: 369, orientation: "h" },
            { x: 584, y: 358, w: 12, h: 20, node: "buildingH", bldg: "H", orientation: "h", borderWidth: 2.2 },
            { x: 556, y: 352, w: 20, h: 26, node: "buildingH", bldg: "H", orientation: "v", borderWidth: 2.3 },
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

        // Twin protruding north roof dormers on Building C (matching Photo 7 & 10)
        for (const dx of [354, 514]) {
            addRectBuilding(layer, { x: dx, y: 392, w: 24, h: 9, node: "buildingC", bldg: "C", orientation: "v", borderWidth: 2.2, shadow: false });
        }

        // Observatorio Dome attached to West end of Building P (iconic pie-wedge telescope dome, Photo 1 & 5)
        const obs = el("g", { class: "bldg-shape", "data-node": "buildingP", "data-bldg": "P", filter: "url(#bldgShadow)" }, layer);
        el("rect", { x: 302, y: 94, width: 42, height: 42, fill: "#cbd5e1", stroke: ROOF_BORDER, "stroke-width": 3 }, obs);
        el("rect", { x: 306, y: 98, width: 34, height: 34, fill: "#e2e8f0", stroke: "#94a3b8", "stroke-width": 1 }, obs);
        // Full teal circle + bottom-left light-grey pie-wedge cutout matching official Copernicus Observatory graphic
        el("circle", { cx: 323, cy: 115, r: 14, fill: ROOF_BASE, stroke: "#ffffff", "stroke-width": 1.6 }, obs);
        el("path", { d: "M 323 115 L 311 122 A 14 14 0 0 0 331 127 Z", fill: "#cbd5e1", stroke: "#ffffff", "stroke-width": 1.1 }, obs);

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
            // Edificio O (Ingenieria & FIA — main block + west wing + bottom-right hipped annex, Photo 8)
            {
                node: "buildingO", bldg: "O", badge: "O", badgeClass: "badge-amber", badgeX: 597, badgeY: 184,
                path: "M 572 152 L 622 152 L 622 258 L 596 258 L 596 238 L 572 238 L 572 224 L 556 224 L 556 174 L 572 174 Z",
                facets: [
                    ["622,152 597,172 597,214 622,238", ROOF_LIGHT],
                    ["572,152 622,152 597,172", ROOF_DARK],
                    ["572,238 622,238 597,214", ROOF_DARK],
                    ["556,174 556,224 572,199", ROOF_DARK],
                    ["556,174 572,174 572,199", ROOF_LIGHT],
                    ["596,258 622,258 609,246", ROOF_DARK]
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
            // Edificio D (Odontologia Digital — exact bottom-right cutout notch, Photo 6)
            {
                node: "buildingD", bldg: "D", badge: "D", badgeClass: "badge-green", badgeX: 400, badgeY: 314,
                path: "M 384 300 L 428 300 L 428 326 L 418 326 L 418 336 L 384 336 Z",
                facets: [
                    ["384,300 428,300 416,314 384,314", ROOF_LIGHT],
                    ["428,300 428,326 416,314", ROOF_DARK],
                    ["384,336 418,336 401,324", ROOF_DARK]
                ]
            },
            // Edificio M (Postgrados — asymmetric main spine + west wing + upper-right wing, Photo 7)
            {
                node: "buildingM", bldg: "M", badge: "M", badgeClass: "badge-teal", badgeX: 612, badgeY: 432,
                path: "M 592 404 L 630 404 L 630 410 L 640 410 L 640 432 L 630 432 L 630 468 L 592 468 L 592 452 L 576 452 L 576 424 L 592 424 Z",
                facets: [
                    ["612,416 630,404 630,468 612,454", ROOF_LIGHT],
                    ["576,424 576,452 592,438", ROOF_DARK],
                    ["592,404 630,404 612,416", ROOF_DARK],
                    ["592,468 630,468 612,454", ROOF_DARK],
                    ["630,410 640,410 640,432 630,432", ROOF_LIGHT]
                ]
            },
            // Edificio G (Auditorio Central & Derecho — main hipped block + upper-right side annex)
            {
                node: "buildingG", bldg: "G", badge: "G", badgeClass: "badge-navy", badgeX: 591, badgeY: 509,
                path: "M 568 486 L 614 486 L 614 495 L 622 495 L 622 515 L 614 515 L 614 532 L 568 532 Z",
                facets: [
                    ["568,486 591,500 591,518 568,532", ROOF_LIGHT],
                    ["568,486 614,486 591,500", ROOF_DARK],
                    ["568,532 614,532 591,518", ROOF_DARK],
                    ["614,495 622,495 622,515 614,515", ROOF_LIGHT]
                ]
            },
            // Edificio F (FACEE — taller hipped block + twin right-side annex notches)
            {
                node: "buildingF", bldg: "F", badge: "F", badgeClass: "badge-magenta", badgeX: 591, badgeY: 566,
                path: "M 568 540 L 614 540 L 614 550 L 621 550 L 621 561 L 614 561 L 614 570 L 622 570 L 622 585 L 614 585 L 614 592 L 568 592 Z",
                facets: [
                    ["568,540 591,554 591,578 568,592", ROOF_LIGHT],
                    ["568,540 614,540 591,554", ROOF_DARK],
                    ["568,592 614,592 591,578", ROOF_DARK],
                    ["614,550 621,550 621,561 614,561", ROOF_LIGHT],
                    ["614,570 622,570 622,585 614,585", ROOF_LIGHT]
                ]
            },
            // Banpro / Bank (distinct L-shaped teal building flush against Lower West Parking & West Main Avenue)
            {
                path: "M 206 502 L 236 502 L 236 534 L 218 534 L 218 518 L 206 518 Z",
                borderWidth: 2.2,
                facets: [
                    ["206,502 236,502 227,510 206,510", ROOF_LIGHT],
                    ["236,502 236,534 227,526 227,510", ROOF_LIGHT],
                    ["218,534 236,534 227,526", ROOF_DARK]
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
            // West & North-Central pavilions (aligned with reshaped West Parking & Plaza Chilamates)
            { x: 48, y: 278, w: 30, h: 20, orientation: "v" },  // Acopio
            { x: 246, y: 148, w: 34, h: 26 },                  // Estacion Meteorologica (cleanly above N parking apron)
            { x: 282, y: 320, w: 18, h: 18, orientation: "h" }, // Kiosko Plaza Chilamates (aligned below giant tree)
            { x: 528, y: 248, w: 16, h: 15 },                  // Small annex 1 below O
            { x: 548, y: 248, w: 16, h: 15 },                  // Small annex 2 below O
            { x: 528, y: 282, w: 30, h: 28 },                  // Ranchon
            { x: 522, y: 322, w: 11, h: 15 },                  // Lab Digital FIA
            // Sports North & Mid Concourse pavilions (locked to official overlay coordinates)
            { x: 902, y: 50, w: 36, h: 30 },       // Kiosko NE
            { x: 978, y: 46, w: 38, h: 30 },       // Sanitarios NE
            { x: 770, y: 325, w: 30, h: 28 },      // Kiosko Mid
            { x: 838, y: 325, w: 30, h: 28 },      // Sanitarios Mid
            { x: 950, y: 320, w: 42, h: 31 },      // Oficina de Deportes
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

        // Main South Gate (Entrada Principal — centered on shifted wider West Main Avenue)
        const gate = el("g", { class: "bldg-shape", "data-node": "mainParking", "data-bldg": "ENTRADA" }, layer);
        el("rect", { x: 260, y: 760, width: 44, height: 18, fill: ROOF_BORDER, stroke: ROOF_BORDER, "stroke-width": 2, filter: "url(#bldgShadow)" }, gate);
    }

    // ----------------------------------------------------------------------------
    // 7. Layer 6: Landscaping (Trees & Bush Rows via Reusable SVG Symbols)
    // ----------------------------------------------------------------------------
    function renderLandscaping(layer) {
        // Large canopy tree rows [x1, y1, x2, y2, count]
        const largeTreeRows = [
            // West parking divider (8 trees) & Lower West Parking median trees (3 on upper median, 4 on lower median)
            [74, 344, 218, 344, 8],
            [148, 398, 192, 398, 3],
            [146, 446, 206, 446, 4],
            // Continuous 12-tree line hugging Building K & Main Entrance pull-out lay-by (6 beside K + 6 beside lay-by)
            [308, 486, 316, 562, 6],
            [318, 578, 326, 674, 6],
            // East edge of South Main Parking (10 continuous trees along Building E west side, Photo 12 & 13)
            [506, 504, 512, 656, 10],
            // South of Plaza Central (matching exact tree positions below K & Plaza Central)
            [398, 562, 486, 562, 5],
            // Double staggered tree rows separating G/F Parking from South-East Parking (Photo 12 & 13)
            [628, 581, 672, 581, 4],
            [620, 593, 682, 593, 5],
            // South parking horizontal tree rows (dead-straight horizontal, matching close-up signage)
            [356, 680, 466, 680, 7],      // Below South Upper Parking (left of E)
            [618, 680, 670, 680, 3],      // Below SE Parking (right of Innovacion)
            [358, 725, 466, 725, 7],      // North/Main-Entrance Lot upper row (left block)
            [504, 725, 628, 725, 8],      // North/Main-Entrance Lot upper row (right block)
            [358, 766, 688, 766, 18],     // Bottom straight perimeter tree line
            // Double tree column flanking Central Spine Road & West side of Building I (Photo 12 & 14)
            [692, 606, 692, 666, 5],
            [716, 598, 720, 694, 7],
            // Between Building I and Jaguar Center (bottom tree anchors NW corner of Jaguar Gym parking)
            [816, 586, 816, 684, 6],
            // Baseball Stadium: 7 west trees cleanly inside western curve + 3 south concourse trees (Photo 2 & 15)
            [708, 128, 716, 276, 7],
            [792, 308, 956, 308, 3],
            // Left (compass-east) edge of Soccer Field — dead-straight vertical line of 10 trees beside parking buffer
            [747, 376, 747, 524, 10],
            // South edge of Soccer Field — clean 90-degree corner turn from vertical tree line
            [758, 534, 926, 534, 10],
            [974, 534, 1094, 534, 7]
        ];

        for (const [x1, y1, x2, y2, count] of largeTreeRows) {
            addTreeRow(layer, x1, y1, x2, y2, count, "#treeLarge");
        }

        // Individual accent trees (near P, Plaza Chilamates perimeter, K/Plaza Central, Banpro, Main Entrance, G/F, Jaguar Gym Lot, East Complex)
        const singleTrees = [
            [356, 152], [260, 314], [334, 338], [354, 562],
            [208, 528], [256, 746], [256, 766],
            [688, 585],
            [866, 704], [882, 720], [916, 696],
            [978, 577], [952, 594], [952, 614], [952, 632], [946, 662], [1132, 756]
        ];
        for (const [x, y] of singleTrees) {
            el("use", { href: "#treeLarge", x, y }, layer);
        }

        // Small manicured bush / hedge rows [x1, y1, x2, y2, count]
        const bushRows = [
            // Plaza Chilamates west hedge (10 neat small bushes)
            [268, 244, 268, 298, 10],
            // West side of Building N (9 neat small bushes)
            [346, 242, 346, 290, 9],
            // East side of Central Parking (double 6-bush column + 2 diagonal accents, Photo 7 & 8)
            [506, 346, 514, 386, 6],
            [518, 346, 526, 386, 6],
            [534, 354, 538, 364, 2],
            // Below H (5 bushes) & double vertical 6+6 bush column east of M (Photo 7)
            [594, 393, 628, 393, 5],
            [666, 434, 666, 464, 6],
            [673, 434, 673, 464, 6],
            // Inside C-B Courtyard (west & east of central bridge)
            [344, 427, 424, 427, 7],
            [464, 427, 554, 427, 8],
            [344, 443, 424, 443, 7],
            [464, 443, 554, 443, 8],
            // South perimeter of Building B (3 distinct bush groups: west 9, middle 7, east of bridge 3 — Photo 7 & 12)
            [344, 474, 426, 474, 9],
            [456, 474, 514, 474, 7],
            [538, 474, 558, 474, 3]
        ];

        for (const [x1, y1, x2, y2, count] of bushRows) {
            addTreeRow(layer, x1, y1, x2, y2, count, "#treeSmall");
        }
        // Tiny 3-bush cluster tucked at NW corner of Building J (Photo 6)
        for (const [bx, by] of [[335, 295], [342, 295], [335, 302]]) {
            el("use", { href: "#treeSmall", x: bx, y: by }, layer);
        }
    }

    // ----------------------------------------------------------------------------
    // 8. Layer 7: Emergency Layer (Safe Areas, Meeting Points & Evacuation Routes)
    // ----------------------------------------------------------------------------
    function renderEmergencyLayer(layer) {
        const evacuationPaths = [
            // Zone North (P, Observatorio, N, J, D, Ranchon, O -> North PON Lot & Meeting Point 2 east of O — Photos 1, 4, 5, 8)
            "M 320 140 L 322 186 L 430 186",
            "M 326 186 L 332 336 L 382 336 L 382 342 L 408 342",
            "M 398 256 L 484 256 L 488 336",
            "M 436 226 L 436 198",
            "M 526 294 L 516 294 L 516 222 L 528 222 L 528 198",
            "M 560 148 L 560 184 L 468 186",
            "M 624 200 L 656 200",

            // Zone Central (A, B, C, K, E -> Meeting Point 4 in Plaza Central Ruben Dario — Photos 7, 10, 12)
            "M 352 472 L 352 484 L 440 484 L 444 494",
            "M 448 472 L 452 492",
            "M 516 472 L 470 500",
            "M 400 524 L 426 518",
            "M 518 522 L 470 518",
            "M 534 654 L 534 670 L 494 670 L 494 540 L 470 526",

            // Zone East-Center (H, M, G, F, Vida Estudiantil, SE Parking, I -> Meeting Point 5 — Photos 7, 12, 13)
            "M 680 370 L 686 468 L 664 504",
            "M 630 438 L 656 438 L 664 498",
            "M 568 468 L 626 468 L 644 504",
            "M 622 508 L 634 516",
            "M 622 560 L 640 532",
            "M 560 618 L 560 600 L 651 600 L 651 536",
            "M 762 640 L 762 628 L 740 628 L 718 576 L 668 532",
            "M 796 706 L 702 706 L 702 588 L 666 534",

            // Sports Concourse -> Meeting Point 3 (Soccer Field — Photo 15)
            "M 754 344 L 876 426",

            // Jaguar Center, L, Gym, Physiotherapy, Warehouse, Nameless Complex & Martial Arts -> Soccer Field (Photo 14)
            "M 852 574 L 852 560 L 944 560 L 944 474",
            "M 898 574 L 898 560",
            "M 964 598 L 952 598 L 952 580",
            "M 964 626 L 952 626 L 952 642 L 992 642",
            "M 978 724 L 978 696 L 944 696 L 944 566",
            "M 1004 834 L 994 834 L 994 580 L 950 580",
            "M 1018 676 L 1018 682 L 994 682",
            "M 1058 646 L 1066 742",
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
            [994, 642], [994, 676], [1004, 682], [1058, 646], [1066, 678], [1140, 656], [994, 766]
        ];
        for (const [cx, cy] of junctionDots) {
            el("circle", { cx, cy, r: 3.2, fill: "#166534", stroke: "#ffffff", "stroke-width": 1 }, layer);
        }

        // 7B. Safe Area / Meeting Point Green Circles with Checkmarks
        const pointsGroup = el("g", { id: "emergencySafePointsGroup" }, layer);
        const safePoints = [
            { cx: 866, cy: 194, r: 18 },   // Baseball Stadium Outfield
            { cx: 672, cy: 200, r: 10.5 }, // East of Building O (on roadside parking bay)
            { cx: 904, cy: 446, r: 21 },   // Soccer Field Center
            { cx: 448, cy: 514, r: 18 },   // Plaza Central Ruben Dario
            { cx: 651, cy: 518, r: 10.5 }  // G/F Parking Aisle (West of Pill Median)
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
