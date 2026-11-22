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
        buildingD: { x: 410, y: 316 },
        buildingE: { x: 534, y: 580 },
        buildingF: { x: 604, y: 564 },
        buildingG: { x: 604, y: 510 },
        buildingH: { x: 652, y: 369 },
        buildingI: { x: 776, y: 656 },
        buildingJ: { x: 361, y: 316 },
        buildingK: { x: 362, y: 526 },
        buildingL: { x: 989, y: 612 },
        buildingM: { x: 626, y: 435 },
        buildingN: { x: 442, y: 260 },
        buildingO: { x: 611, y: 196 },
        buildingP: { x: 456, y: 115 },
        mainParking: { x: 274, y: 766 },
        chilamatesPlaza: { x: 294, y: 292 },
        sportsZone: { x: 938, y: 447 },
        jaguarCenter: { x: 900, y: 623 },
        jaguarGym: { x: 969, y: 726 },
        physiotherapy: { x: 978, y: 677 },
        northGate: { x: 218, y: 74 },
        northeastGate: { x: 659, y: 16 }
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
        // 1A. Secondary walkways & pedestrian concourses (flat pale slate, no lane dashes)
        const connectors = [
            // North Sports Parking entry apron connecting down from Camino Segundo Acceso
            { d: "M 822 16 L 822 46", w: 24, color: "#dfe5ec" },
            // Pedestrian sports concourse between Baseball Stadium and Soccer Field
            { d: "M 722 338 L 1154 338", w: 22, color: "#dce2ec" },
            // Pedestrian corridor cleanly running between Building L/Jaguar Gym and Courts/East Complex
            { d: "M 1006 542 L 1008 842", w: 10, color: "#e4e9f2" }
        ];

        for (const r of connectors) {
            el("path", { d: r.d, "stroke-width": r.w, stroke: r.color }, layer);
        }

        // 1B. Main Campus Vehicle Road Network
        // Wide boulevard from Entrada Principal (south) up to Tercer Acceso (north-west)
        const westAvenuePath = "M 274 762 L 274 702 C 270 595, 256 465, 240 340 C 228 242, 220 164, 218 92";
        // Smooth tapered transition around Tercer Acceso into the northern perimeter arch
        const northArchPath = "M 218 92 L 218 74 C 218 42, 258 22, 376 17 L 659 15";
        const tercerAccesoPath = "M 218 74 L 156 74";
        const otherMainPaths = [
            // Camino Segundo Acceso (continuing east from Top T-Junction)
            "M 659 15 L 1140 12",
            // South Internal Ring (Dead-horizontal South Avenue -> SE rounded curve -> Central Spine North -> Top T-Junction)
            "M 274 702 Q 274 696 292 696 L 692 696 Q 720 696 720 668 L 720 430 C 722 345, 692 270, 676 185 L 659 15",
            // SE Branch connecting SE Curve -> Building I Parking Lot -> Jaguar Center Parking
            "M 708 696 Q 724 742 756 744 L 850 744"
        ];

        // Smooth tapered collar joining the 36px West Avenue cleanly into the 24px North Arch at Tercer Acceso (no round-cap bump)
        const nwTaperCurb = "M 198 92 C 198 72, 200 54, 212 40 L 228 50 C 232 62, 236 76, 238 92 Z";
        const nwTaperFill = "M 200 92 C 200 72, 202 55, 214 42 L 226 51 C 230 63, 234 77, 236 92 Z";

        // Smooth concave-filleted driveway aprons opening the road curb cleanly into every adjacent parking lot & drop-off bay
        const flaredAprons = [
            // Upper West Parking seamless curved mouth off West Avenue
            "M 202 202 Q 214 202 214 192 L 222 192 L 234 340 L 224 340 Q 222 330 212 330 L 198 330 L 194 202 Z",
            // Lower West Parking seamless curved mouth off West Avenue
            "M 216 360 Q 228 360 227 350 L 236 350 L 254 514 L 245 514 Q 243 504 233 504 L 216 504 L 206 360 Z",
            // Side P Parking seamless open throat above Weather Station
            "M 224 96 L 252 96 L 252 146 L 226 146 Z",
            // North PON Parking seamless flared throat below Weather Station
            "M 228 179 Q 238 179 237 170 L 240 179 L 254 179 L 254 214 L 244 214 Q 234 214 234 224 L 226 218 Z",
            // Behind Building P Parking open NW throat off North Arch
            "M 344 16 L 434 15 L 434 30 L 344 28 Z",
            // Central Parking & Crosswalk wide driveway throat between Plaza Chilamates and Building A drop-off
            "M 244 344 L 332 344 L 332 394 L 252 394 Z",
            // Building A curved drive-through drop-off bay seamless connection to West Avenue
            "M 250 388 L 304 394 L 304 476 L 258 486 Z",
            // South Main Parking left & right driveway connections to South Avenue
            "M 332 676 L 358 676 Q 358 686 366 686 L 366 696 L 324 696 L 324 686 Q 332 686 332 676 Z",
            "M 472 676 L 498 676 Q 498 686 506 686 L 506 696 L 464 696 L 464 686 Q 472 686 472 676 Z",
            // South Lower Parking & SE Parking driveway connections to South Avenue
            "M 466 696 L 502 696 L 502 706 Q 494 706 494 716 L 474 716 Q 474 706 466 706 Z",
            "M 636 678 L 656 678 Q 656 686 664 686 L 664 696 L 628 696 L 628 686 Q 636 686 636 678 Z",
            "M 674 696 L 710 696 L 710 706 Q 702 706 702 720 L 682 720 Q 682 706 674 706 Z"
        ];

        // Pass 1: Continuous outer road & driveway curb casing (#9aa8be)
        const roadCurb = el("g", { class: "main-road-curb", fill: "none", stroke: "#9aa8be", "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        el("path", { d: westAvenuePath, "stroke-width": 40, "stroke-linecap": "butt" }, roadCurb);
        el("path", { d: northArchPath, "stroke-width": 28 }, roadCurb);
        el("path", { d: tercerAccesoPath, "stroke-width": 26 }, roadCurb);
        el("path", { d: nwTaperCurb, fill: "#9aa8be", stroke: "none" }, roadCurb);
        for (const d of otherMainPaths) {
            el("path", { d, "stroke-width": 24 }, roadCurb);
        }
        // Subtle curb border around flared driveway throats (broken cleanly inside by Pass 2 asphalt fill)
        for (const d of flaredAprons) {
            el("path", { d, fill: "#9aa8be", stroke: "#9aa8be", "stroke-width": 3, "stroke-linejoin": "round" }, roadCurb);
        }

        // Pass 2: Seamless road & driveway asphalt fill (#bcc6d6) — automatically opens every intersection & parking mouth
        const roadFill = el("g", { class: "main-road-asphalt", fill: "none", stroke: "#bcc6d6", "stroke-linecap": "round", "stroke-linejoin": "round" }, layer);
        el("path", { d: westAvenuePath, "stroke-width": 36, "stroke-linecap": "butt" }, roadFill);
        el("path", { d: northArchPath, "stroke-width": 24 }, roadFill);
        el("path", { d: tercerAccesoPath, "stroke-width": 22 }, roadFill);
        el("path", { d: nwTaperFill, fill: "#bcc6d6", stroke: "none" }, roadFill);
        for (const d of otherMainPaths) {
            el("path", { d, "stroke-width": 20 }, roadFill);
        }
        for (const d of flaredAprons) {
            el("path", { d, fill: "#bcc6d6", stroke: "none" }, roadFill);
        }

        // Smooth paved shoulder & curved drop-off entry blending Building A's front bay + Bus Lay-By seamlessly into West Avenue
        const layBy = el("g", { id: "mainEntranceLayBy" }, layer);
        // Continuous paved shoulder along east side of West Avenue from Building A drop-off down to Main Entrance
        el("path", {
            d: "M 262 476 L 296 476 L 318 686 L 284 686 Z",
            fill: "#bcc6d6"
        }, layBy);
        // Darker asphalt pull-out bus/passenger lay-by bay cleanly beside the wider through-lane
        el("path", {
            d: "M 307 570 L 296 570 Q 289 570 290 579 L 298 675 Q 299 684 308 684 L 318 684 Z",
            fill: "#9faec4"
        }, layBy);
        // Crisp white pull-out bay border + vertical curb line continuing straight north to Building A's drop-off exit
        el("path", {
            d: "M 294 475 L 307 570 L 296 570 Q 289 570 290 579 L 298 675 Q 299 684 308 684 L 318 684 L 307 570",
            fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round", "stroke-linejoin": "round"
        }, layBy);

        // Pass 3: Crisp white dashed road centerlines (drawn above asphalt & aprons so lanes read clearly)
        const roadDash = el("g", { class: "main-road-centerline", fill: "none", stroke: "#ffffff", "stroke-width": 1.35, "stroke-dasharray": "7,6", "stroke-linecap": "round", opacity: 0.78 }, layer);
        el("path", { d: westAvenuePath }, roadDash);
        el("path", { d: northArchPath }, roadDash);
        el("path", { d: tercerAccesoPath }, roadDash);
        for (const d of otherMainPaths) {
            el("path", { d }, roadDash);
        }

        // Tercer Acceso divided gatehouse island + crosswalk stripes
        el("rect", { x: 166, y: 71, width: 22, height: 6, rx: 3, fill: "#e2e8f0", stroke: "#ffffff", "stroke-width": 1.2 }, layer);
        el("rect", { x: 154, y: 61, width: 7, height: 26, rx: 1, fill: ROOF_BASE, stroke: ROOF_BORDER, "stroke-width": 1.4 }, layer);
        el("line", { x1: 163, y1: 64, x2: 163, y2: 71, stroke: "#ffffff", "stroke-width": 1.4, "stroke-dasharray": "2,2" }, layer);
        el("line", { x1: 163, y1: 77, x2: 163, y2: 84, stroke: "#ffffff", "stroke-width": 1.4, "stroke-dasharray": "2,2" }, layer);
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

        // 2.1 Behind Building P (seamless open throat off NW arch road, aligned with shifted P)
        makeLot("parkingLotBehindP", "path", {
            d: "M 346 20 L 430 18 L 538 24 A 6 6 0 0 1 544 30 L 544 74 A 6 6 0 0 1 538 80 L 440 80 L 346 24 Z"
        }, (_, l) => {
            addStallRow(l, 374, 34, 440, 76, 8, 5, -9, true);      // SW diagonal stalls
            addStallRow(l, 450, 29, 520, 29, 9, 0, 11, true);     // Top row
            addStallRow(l, 446, 76, 518, 76, 9, 0, -11, true);    // Bottom row
            addStallRow(l, 539, 35, 539, 72, 6, -11, 0, true);    // East column
        });

        // 2.2 West Side of Building P (opens cleanly off wider West Avenue above Weather Station)
        makeLot("parkingLotSideP", "path", {
            d: "M 238 96 L 288 96 A 4 4 0 0 1 292 100 L 292 160 A 4 4 0 0 1 288 164 L 246 164 L 246 146 L 238 146 Z"
        }, (_, l) => {
            addStallRow(l, 248, 101, 248, 144, 5, 11, 0, true);   // Left column above Weather Station
            addStallRow(l, 288, 101, 288, 159, 7, -11, 0, true);  // Right column running beside Weather Station
        });

        // 2.3 North Parking (Between P & N — seamless apron meeting wider West Avenue + 3 south curb tabs & NW tree notch)
        makeLot("parkingLotNorthPON", "path", {
            d: "M 240 179 L 324 179 L 324 164 L 354 164 L 354 158 L 546 158 L 546 214 L 536 214 L 536 221 L 528 221 L 528 214 L 420 214 L 420 221 L 412 221 L 412 214 L 340 214 L 340 221 L 332 221 L 332 214 L 244 214 Z"
        }, (_, l) => {
            addStallRow(l, 336, 160, 540, 160, 26, 0, 14);
            addStallRow(l, 336, 212, 540, 212, 26, 0, -14);
        });

        // 2.4 Upper West Parking Lot (Seamless flared east mouth joining wider West Avenue, 4 structured stall rows)
        makeLot("parkingLotWestUpper", "path", {
            d: "M 56 202 L 207 202 L 220 330 L 62 330 L 62 304 L 56 202 Z"
        }, (_, l) => {
            addStallRow(l, 66, 206, 190, 206, 15, 0, 14, true);    // Top perimeter row
            addStallRow(l, 66, 244, 188, 244, 15, 0, -13, true);   // Upper center island (north)
            addStallRow(l, 66, 246, 188, 246, 15, 0, 13);          // Upper center island (south)
            addStallRow(l, 68, 288, 186, 288, 14, 0, -13, true);   // Lower center island (north)
            addStallRow(l, 68, 290, 186, 290, 14, 0, 13);          // Lower center island (south)
            addStallRow(l, 70, 326, 186, 326, 14, 0, -13, true);   // Bottom perimeter row
        });

        // 2.5 Lower West Parking Lot (Solar-panel strip, T-cap medians, dark corner pad & seamless connection to wider West Avenue)
        makeLot("parkingLotWestLower", "path", {
            d: "M 54 360 L 224 360 L 241 504 L 62 504 L 62 496 L 54 496 Z"
        }, (g, l) => {
            // Far-west Solar Panel Canopy strip along left perimeter
            el("rect", { x: 42, y: 366, width: 12, height: 124, fill: "#cbd5e1", stroke: "#94a3b8", "stroke-width": 1.1 }, g);
            for (let sy = 372; sy < 488; sy += 6) {
                el("line", { x1: 42, y1: sy, x2: 54, y2: sy, stroke: "#ffffff", "stroke-width": 0.9 }, g);
            }

            // Far-west vertical perimeter stalls along solar-panel edge
            addStallRow(l, 56, 372, 56, 488, 12, 11, 0);

            // Top & bottom perimeter stall rows
            addStallRow(l, 70, 363, 204, 363, 15, 0, 13);
            addStallRow(l, 70, 500, 190, 500, 14, 0, -13);

            // Upper T-capped median island (y=398) + perpendicular stalls above & below
            el("path", {
                d: "M 78 391 A 4 4 0 0 0 74 395 L 74 401 A 4 4 0 0 0 78 405 M 74 398 L 198 398 M 194 391 A 4 4 0 0 1 198 395 L 198 401 A 4 4 0 0 1 194 405",
                fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round"
            }, g);
            addStallRow(l, 80, 396, 192, 396, 13, 0, -12);
            addStallRow(l, 80, 400, 192, 400, 13, 0, 12);
            // Small entrance traffic bollard island
            el("rect", { x: 212, y: 393, width: 4, height: 12, rx: 1.5, fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1 }, g);

            // Lower median island (y=446) leading into rounded dark corner planter/service pad
            el("path", {
                d: "M 78 439 A 4 4 0 0 0 74 443 L 74 449 A 4 4 0 0 0 78 453 M 74 446 L 188 446",
                fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round"
            }, g);
            el("rect", {
                x: 188, y: 432, width: 32, height: 32, rx: 5,
                fill: "#aeb9ca", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            addStallRow(l, 80, 444, 184, 444, 12, 0, -12);
            addStallRow(l, 80, 448, 184, 448, 12, 0, 12);
            // Small stalls below the dark corner pad
            addStallRow(l, 192, 466, 214, 466, 3, 0, 11);
        });

        // 2.6 Central Parking Lot (Starts cleanly east of the moved crosswalk at x=329, ends at x=514 aligned with N & C dormer)
        makeLot("parkingLotCentralCD", "path", {
            d: "M 329 368 L 356 346 L 514 344 L 514 395 L 329 395 Z"
        }, (g, l) => {
            el("rect", { x: 329, y: 391, width: 185, height: 4, fill: "#cbd5e1" }, g);
            // Architectural double retaining curb & center stair landing along north edge (between D & N leg)
            el("path", { d: "M 335 366 L 358 349 L 444 345 L 454 341 L 466 345 L 514 344", fill: "none", stroke: "#64748b", "stroke-width": 1.2 }, g);
            el("rect", { x: 448, y: 336, width: 16, height: 11, fill: "#cbd5e1", stroke: "#64748b", "stroke-width": 1 }, g);
            addStallRow(l, 358, 350, 498, 349, 13, 7, 12);    // Angled top stalls slanting down-right
            addStallRow(l, 354, 391, 508, 391, 14, 0, -14);   // Perpendicular bottom stalls (starting above C's left dormer)
        });

        // Pedestrian Zebra Crosswalk — positioned at real compass-west location connecting Plaza Chilamates SW edge directly to Building A
        const cw = el("g", { id: "pedestrianChilamatesToA" }, layer);
        el("rect", { x: 310, y: 344, width: 19, height: 54, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1.2 }, cw);
        for (let y = 350; y <= 392; y += 7) {
            el("line", { x1: 313, y1: y, x2: 326, y2: y, stroke: "#ffffff", "stroke-width": 3 }, cw);
        }

        // 2.7 North-East Sports Parking (North of Baseball Stadium, shifted +14px with east campus)
        makeLot("parkingLotNorthSports", "rect", { x: 758, y: 42, width: 128, height: 52, rx: 6 }, (_, l) => {
            addStallRow(l, 768, 46, 876, 46, 12, 0, 14, true);
            addStallRow(l, 768, 90, 876, 90, 12, 0, -14, true);
        });

        // 2.8 East & Central-Spine Parking Lots (Shifted +14px cleanly alongside spine road)
        makeLot("parkingLotEastO", "path", {
            d: "M 678 138 L 696 138 L 708 274 L 690 274 Z"
        }, (_, l) => {
            addStallRow(l, 693, 144, 705, 268, 14, -13, 0, true);
        });
        // Parking Lot on Right (Compass-West) Side of Buildings G & F (shifted +12px)
        makeLot("parkingLotWestGF", "path", {
            d: "M 630 486 L 686 476 L 708 476 L 708 562 L 692 578 L 630 578 Z"
        }, (g, l) => {
            addStallRow(l, 636, 490, 636, 530, 5, 11, 0);
            addStallRow(l, 636, 542, 636, 574, 5, 11, 0);
            el("rect", {
                x: 682, y: 496, width: 7, height: 58, rx: 3.5,
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            addStallRow(l, 695, 480, 695, 554, 12, 12, 0);
        });
        makeLot("parkingLotSoccerEast", "path", {
            d: "M 730 398 L 749 398 L 749 536 L 730 536 Z"
        }, (_, l) => {
            addStallRow(l, 732, 402, 732, 532, 20, 15, 0);
        });

        // 2.9 Main South Parking Lot (Upper bay cleanly east of the pull-out lay-by & 12-tree line)
        makeLot("parkingLotSouthMain", "path", {
            d: "M 326 568 L 500 568 L 500 680 L 330 680 Z"
        }, (g, l) => {
            addStallRow(l, 344, 574, 490, 574, 13, 0, 15, true);
            addStallRow(l, 346, 616, 490, 616, 13, 0, -13, true);
            addStallRow(l, 346, 620, 490, 620, 13, 0, 13);
            addStallRow(l, 348, 660, 492, 660, 13, 0, -13, true);
            el("line", { x1: 360, y1: 673, x2: 472, y2: 673, stroke: "#ffffff", "stroke-width": 1.4, "stroke-linecap": "round" }, g);
            el("path", { d: "M 334 666 Q 341 678 355 674", fill: "none", stroke: "#1da495", "stroke-width": 2, "stroke-linecap": "round" }, g);
        });

        // 2.9B North (Compass-North / Main-Entrance) Parking Strip — extended cleanly to meet shifted Building I lot at x=706
        makeLot("parkingLotSouthLower", "path", {
            d: "M 342 712 L 706 712 L 706 764 L 694 764 L 694 780 L 566 780 L 566 764 L 546 764 L 546 780 L 414 780 L 414 764 L 372 764 L 376 782 L 348 782 L 342 758 Z"
        }, (g, l) => {
            el("path", { d: "M 356 717 L 468 717", fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round" }, g);
            el("path", { d: "M 502 717 L 642 717", fill: "none", stroke: "#ffffff", "stroke-width": 1.6, "stroke-linecap": "round" }, g);
            addStallRow(l, 354, 742, 470, 742, 15, 0, 13);
            addStallRow(l, 498, 742, 638, 742, 17, 0, 13);
        });

        // 2.10 South-East Parking Lot (Shifted +12px cleanly with G/F & Spine Road)
        makeLot("parkingLotSouthEF", "path", {
            d: "M 594 602 L 698 602 L 698 668 A 14 14 0 0 1 684 682 L 594 682 Z"
        }, (g, l) => {
            el("path", {
                d: "M 628 611 L 664 611 A 2.5 2.5 0 0 1 664 616 L 653 616 L 653 663 L 664 663 A 2.5 2.5 0 0 1 664 668 L 628 668 A 2.5 2.5 0 0 1 628 663 L 639 663 L 639 616 L 628 616 A 2.5 2.5 0 0 1 628 611 Z",
                fill: "#b4c0cf", stroke: "#ffffff", "stroke-width": 1.3, class: "parking-island"
            }, g);
            addStallRow(l, 598, 608, 598, 668, 9, 13, 0, true);
            addStallRow(l, 638, 621, 638, 658, 6, -13, 0);
            addStallRow(l, 654, 621, 654, 658, 6, 13, 0);
            addStallRow(l, 694, 608, 694, 668, 9, -13, 0, true);
        });

        // 2.11 & 2.12 Unified Building I + Jaguar Gym / Jaguar Center Parking Lot (Shifted +14px with east campus)
        makeLot("parkingLotJaguarGymAndI", "path", {
            d: [
                "M 706 710 L 818 710 L 818 744 L 828 744 L 828 680 L 942 680 Q 948 680 948 686",
                "L 948 700 L 944 700 L 944 750 L 988 750 L 988 772 L 872 772 L 872 786",
                "L 732 786 L 732 766 L 706 766 Z"
            ].join(" ")
        }, (_, l) => {
            addStallRow(l, 732, 715, 814, 715, 11, -7, 14, true);
            addStallRow(l, 846, 684, 934, 684, 10, 0, 13, true);
            addStallRow(l, 832, 698, 832, 748, 7, 14, 0, true);
            addStallRow(l, 940, 704, 940, 748, 7, -14, 0, true);
            addStallRow(l, 832, 766, 978, 766, 22, 0, -13, true);
        });
    }

    // ----------------------------------------------------------------------------
    // 4. Layer 3: Sports Facilities (Baseball, Soccer, Tennis & Sand Volleyball — shifted +14px with east campus)
    // ----------------------------------------------------------------------------
    function renderSports(layer) {
        const eastSports = el("g", { transform: "translate(14, 0)" }, layer);
        // 3A. Estadio de Beisbol (Exact official sign geometry: concave-corner infield, pitcher lane, dugouts & fan backstop)
        const bb = el("g", { id: "baseballStadium", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "BÉISBOL" }, eastSports);
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
        const sc = el("g", { id: "soccerField", class: "bldg-shape", "data-node": "sportsZone", "data-bldg": "FÚTBOL" }, eastSports);
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
        const cts = el("g", { id: "sportsCourts", class: "bldg-shape", "data-node": "buildingL", "data-bldg": "CANCHAS" }, eastSports);

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
        // 4A. Plaza Chilamates (Paved plaza west of J/N with slanted edge parallel to wider West Avenue)
        const ch = el("g", { class: "bldg-shape", "data-node": "chilamatesPlaza", "data-bldg": "CHILAMATES" }, layer);
        el("path", {
            d: "M 248 226 L 329 226 L 329 344 L 260 344 Z",
            fill: "#e2e8f0", stroke: "#cbd5e1", "stroke-width": 1.3, "stroke-linejoin": "round"
        }, ch);
        // Iconic large Chilamate specimen canopy & smaller north companion canopy
        el("circle", { cx: 299, cy: 287, r: 15.5, fill: "#3b5e54", stroke: "#28423b", "stroke-width": 1.1 }, ch);
        el("circle", { cx: 295, cy: 283, r: 6.5, fill: "#527d70", opacity: 0.7 }, ch);
        el("circle", { cx: 298, cy: 251, r: 8.5, fill: "#3b5e54", stroke: "#28423b", "stroke-width": 0.9 }, ch);
        el("circle", { cx: 296, cy: 249, r: 3.5, fill: "#527d70", opacity: 0.7 }, ch);

        // 4A-2. Building A Drive-Through Drop-Off Bay & Curved Entrance Steps (Seamlessly connected to West Avenue)
        const frontA = el("g", { id: "buildingAFrontPlaza", "pointer-events": "none" }, layer);
        // Smooth open-mouth U-shaped drive-through drop-off lane curving seamlessly out of & back into West Avenue
        el("path", {
            d: "M 258 389 Q 282 390 292 400 L 310 400 L 310 470 L 294 470 Q 286 480 268 482 L 270 469 Q 282 468 282 458 L 279 412 Q 278 402 260 401 Z",
            fill: "#e2e8f0", stroke: "none"
        }, frontA);
        // Subtle outer curb guide lines only along top & bottom edges (leaving both road mouths 100% open)
        el("path", {
            d: "M 262 390 Q 282 391 292 400 L 310 400 M 310 470 L 294 470 Q 286 479 272 481",
            fill: "none", stroke: "#94a3b8", "stroke-width": 1.2, "stroke-linecap": "round"
        }, frontA);
        // Flared outer median island separating West Avenue through-lane from the Building A drop-off bay
        el("path", {
            d: "M 266 402 Q 274 404 275 412 L 279 458 Q 280 466 273 469 L 269 464 Q 273 462 272 456 L 269 414 Q 268 408 263 406 Z",
            fill: "#8f9eb3", stroke: "#ffffff", "stroke-width": 1.1, "stroke-linejoin": "round"
        }, frontA);
        // Inner rounded pedestrian entrance platform flush with Building A's front wall
        el("path", {
            d: "M 310 400 L 297 400 Q 288 400 288 409 L 288 461 Q 288 470 297 470 L 310 470 Z",
            fill: "#e8edf3", stroke: "#94a3b8", "stroke-width": 1.2
        }, frontA);
        // Inner dark-slate curved planter curbs framing Building A's entrance doors
        el("path", {
            d: "M 309 403 L 296 403 Q 290 403 290 409 L 290 417 L 297 417 L 297 409 L 309 409 Z",
            fill: "#94a3b8", stroke: "#475569", "stroke-width": 0.9
        }, frontA);
        el("path", {
            d: "M 309 467 L 296 467 Q 290 467 290 461 L 290 453 L 297 453 L 297 461 L 309 461 Z",
            fill: "#94a3b8", stroke: "#475569", "stroke-width": 0.9
        }, frontA);
        // Twin dark bracket curbs flanking the curved entrance stairs
        el("path", { d: "M 292 416 L 299 416 L 299 422", fill: "none", stroke: "#334155", "stroke-width": 1.5, "stroke-linecap": "round" }, frontA);
        el("path", { d: "M 292 454 L 299 454 L 299 448", fill: "none", stroke: "#334155", "stroke-width": 1.5, "stroke-linecap": "round" }, frontA);
        // Concentric curved entry steps leading into Building A's main doorway
        el("path", { d: "M 307 422 Q 297 435 307 448", fill: "none", stroke: "#64748b", "stroke-width": 1.35 }, frontA);
        el("path", { d: "M 310 426 Q 302 435 310 444", fill: "none", stroke: "#64748b", "stroke-width": 1.15 }, frontA);

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

        // 4D. Architectural Paved Courtyard Pads (Building M patio, E-to-G/F terrace, Building I apron — shifted with east campus)
        const pads = el("g", { id: "campusTerracePads", "pointer-events": "none" }, layer);
        el("rect", { x: 584, y: 400, width: 72, height: 72, rx: 2, fill: "#cbd5e1", opacity: 0.6 }, pads);  // Behind M
        el("rect", { x: 548, y: 488, width: 32, height: 92, rx: 2, fill: "#cbd5e1", opacity: 0.65 }, pads); // Between E & G/F
        el("rect", { x: 752, y: 584, width: 68, height: 118, rx: 2, fill: "#cbd5e1", opacity: 0.55 }, pads); // Around Building I
    }

    // ----------------------------------------------------------------------------
    // 6. Layer 5: All Official Campus Buildings (A-P + Campus Support Buildings)
    // ----------------------------------------------------------------------------
    function renderBuildings(layer) {
        // --- Rectangular Main Buildings (A, B, C, E, H, J, P, Jaguar Gym, Physiotherapy, Twin L) ---
        const rectBuildings = [
            // Edificio P (Copernico — shifted +6px with N/J/D)
            { x: 350, y: 94, w: 218, h: 42, node: "buildingP", bldg: "P", badge: "P", badgeClass: "badge-maroon", badgeX: 492, badgeY: 115, orientation: "h" },
            // Edificio J (Laboratorios Odontologia — cleanly right of the moved crosswalk)
            { x: 342, y: 300, w: 38, h: 32, node: "buildingJ", bldg: "J", badge: "J", badgeClass: "badge-cyan", orientation: "h" },
            // Edificio A (West Bar — directly beneath the moved crosswalk)
            { x: 310, y: 400, w: 26, h: 70, node: "buildingA", bldg: "A", badge: "A", badgeClass: "badge-maroon", orientation: "v" },
            // Edificio C (North Classroom Bar)
            { x: 336, y: 400, w: 228, h: 22, node: "buildingC", bldg: "C", badge: "C", badgeClass: "badge-purple", badgeX: 444, badgeY: 402, orientation: "h" },
            // Connector Roof between C and B
            { x: 432, y: 422, w: 24, h: 26, bldg: "TECHO_BC", orientation: "v", borderWidth: 2.5 },
            // Edificio B (South Classroom Bar)
            { x: 336, y: 448, w: 228, h: 22, node: "buildingB", bldg: "B", badge: "B", badgeClass: "badge-purple", badgeX: 444, badgeY: 458, orientation: "h" },
            // 2nd-floor bridge between B and E
            { x: 526, y: 470, w: 8, h: 30, bldg: "PUENTE_BE", orientation: "v", borderWidth: 2 },
            // Edificio E (Facultad de Medicina) + Vida Estudiantil & Direccion de Innovacion
            { x: 520, y: 500, w: 28, h: 156, node: "buildingE", bldg: "E", badge: "E", badgeClass: "badge-navy", badgeX: 534, badgeY: 604, orientation: "v" },
            { x: 560, y: 622, w: 22, h: 48, node: "buildingE", bldg: "E", orientation: "v", borderWidth: 2.5 },
            { x: 538, y: 676, w: 54, h: 14, node: "buildingE", bldg: "E", orientation: "h", borderWidth: 2.5 },
            // Edificio H (Laboratorios de Medicina — shifted +14px with east spine) + flush west porch + lab annex
            { x: 610, y: 354, w: 84, h: 30, node: "buildingH", bldg: "H", badge: "H", badgeClass: "badge-green", badgeX: 652, badgeY: 369, orientation: "h" },
            { x: 598, y: 358, w: 12, h: 20, node: "buildingH", bldg: "H", orientation: "h", borderWidth: 2.2 },
            { x: 570, y: 352, w: 20, h: 26, node: "buildingH", bldg: "H", orientation: "v", borderWidth: 2.3 },
            // Jaguar Gym (shifted +14px with east campus)
            { x: 948, y: 704, w: 42, h: 44, node: "jaguarGym", bldg: "JAGUAR GYM", orientation: "v" },
            // Physiotherapy Building / Fisioterapia (shifted +14px with east campus)
            { x: 958, y: 668, w: 40, h: 22, node: "physiotherapy", bldg: "FISIOTERAPIA", orientation: "v", borderWidth: 2.5 },
            // Edificio L — Two separate twin squares (shifted +14px with east campus)
            { x: 978, y: 588, w: 22, h: 20, node: "buildingL", bldg: "L", badge: "L", badgeClass: "badge-magenta", badgeSize: 13, orientation: "v", borderWidth: 2.2 },
            { x: 978, y: 616, w: 22, h: 20, node: "buildingL", bldg: "L", badge: "L", badgeClass: "badge-magenta", badgeSize: 13, orientation: "v", borderWidth: 2.2 }
        ];

        for (const cfg of rectBuildings) {
            addRectBuilding(layer, cfg);
        }

        // Twin protruding north roof dormers on Building C (matching Photo 7 & 10)
        for (const dx of [354, 514]) {
            addRectBuilding(layer, { x: dx, y: 392, w: 24, h: 9, node: "buildingC", bldg: "C", orientation: "v", borderWidth: 2.2, shadow: false });
        }

        // Observatorio Dome attached to West end of Building P (shifted +6px with P)
        const obs = el("g", { class: "bldg-shape", "data-node": "buildingP", "data-bldg": "P", filter: "url(#bldgShadow)" }, layer);
        el("rect", { x: 308, y: 94, width: 42, height: 42, fill: "#cbd5e1", stroke: ROOF_BORDER, "stroke-width": 3 }, obs);
        el("rect", { x: 312, y: 98, width: 34, height: 34, fill: "#e2e8f0", stroke: "#94a3b8", "stroke-width": 1 }, obs);
        el("circle", { cx: 329, cy: 115, r: 14, fill: ROOF_BASE, stroke: "#ffffff", "stroke-width": 1.6 }, obs);
        el("path", { d: "M 329 115 L 317 122 A 14 14 0 0 0 337 127 Z", fill: "#cbd5e1", stroke: "#ffffff", "stroke-width": 1.1 }, obs);

        // Jaguar Center Arena (shifted +14px with east campus)
        const jc = addRectBuilding(layer, {
            x: 848, y: 576, w: 104, h: 94,
            node: "jaguarCenter", bldg: "JAGUAR CENTER", orientation: "h"
        });
        const logoUrl = layer.closest("svg")?.dataset.jaguarLogo || "/static/img/jaguarCenterLogo.png";
        el("image", {
            href: logoUrl, x: 865, y: 589, width: 70, height: 68,
            preserveAspectRatio: "xMidYMid meet", "pointer-events": "none"
        }, jc);

        // --- Custom-Footprint Buildings (O, N, D, M, G, F, Banpro, K, I) ---
        const customBuildings = [
            // Edificio O (Ingenieria & FIA — shifted +14px with east spine)
            {
                node: "buildingO", bldg: "O", badge: "O", badgeClass: "badge-amber", badgeX: 611, badgeY: 184,
                path: "M 586 152 L 636 152 L 636 258 L 610 258 L 610 238 L 586 238 L 586 224 L 570 224 L 570 174 L 586 174 Z",
                facets: [
                    ["636,152 611,172 611,214 636,238", ROOF_LIGHT],
                    ["586,152 636,152 611,172", ROOF_DARK],
                    ["586,238 636,238 611,214", ROOF_DARK],
                    ["570,174 570,224 586,199", ROOF_DARK],
                    ["570,174 586,174 586,199", ROOF_LIGHT],
                    ["610,258 636,258 623,246", ROOF_DARK]
                ]
            },
            // Edificio N (Clinicas Medicas Odontologicas — shifted +6px so right wall aligns with Central Parking & C dormer)
            {
                node: "buildingN", bldg: "N", badge: "N", badgeClass: "badge-magenta", badgeX: 392, badgeY: 256,
                path: "M 370 230 L 516 230 L 516 340 L 470 340 L 470 276 L 370 276 Z",
                facets: [
                    ["370,230 516,230 493,253 370,253", ROOF_LIGHT],
                    ["516,230 516,340 493,318 493,253", ROOF_LIGHT],
                    ["370,230 370,276 392,253", ROOF_DARK],
                    ["470,340 516,340 493,318", ROOF_DARK]
                ]
            },
            // Edificio D (Odontologia Digital — shifted +6px with J & N)
            {
                node: "buildingD", bldg: "D", badge: "D", badgeClass: "badge-green", badgeX: 406, badgeY: 314,
                path: "M 390 300 L 434 300 L 434 326 L 424 326 L 424 336 L 390 336 Z",
                facets: [
                    ["390,300 434,300 422,314 390,314", ROOF_LIGHT],
                    ["434,300 434,326 422,314", ROOF_DARK],
                    ["390,336 424,336 407,324", ROOF_DARK]
                ]
            },
            // Edificio M (Postgrados — shifted +14px with H & east spine)
            {
                node: "buildingM", bldg: "M", badge: "M", badgeClass: "badge-teal", badgeX: 626, badgeY: 432,
                path: "M 606 404 L 644 404 L 644 410 L 654 410 L 654 432 L 644 432 L 644 468 L 606 468 L 606 452 L 590 452 L 590 424 L 606 424 Z",
                facets: [
                    ["626,416 644,404 644,468 626,454", ROOF_LIGHT],
                    ["590,424 590,452 606,438", ROOF_DARK],
                    ["606,404 644,404 626,416", ROOF_DARK],
                    ["606,468 644,468 626,454", ROOF_DARK],
                    ["644,410 654,410 654,432 644,432", ROOF_LIGHT]
                ]
            },
            // Edificio G (Auditorio Central & Derecho — shifted +12px cleanly east of E courtyard)
            {
                node: "buildingG", bldg: "G", badge: "G", badgeClass: "badge-navy", badgeX: 603, badgeY: 509,
                path: "M 580 486 L 626 486 L 626 495 L 634 495 L 634 515 L 626 515 L 626 532 L 580 532 Z",
                facets: [
                    ["580,486 603,500 603,518 580,532", ROOF_LIGHT],
                    ["580,486 626,486 603,500", ROOF_DARK],
                    ["580,532 626,532 603,518", ROOF_DARK],
                    ["626,495 634,495 634,515 626,515", ROOF_LIGHT]
                ]
            },
            // Edificio F (FACEE — shifted +12px with G)
            {
                node: "buildingF", bldg: "F", badge: "F", badgeClass: "badge-magenta", badgeX: 603, badgeY: 566,
                path: "M 580 540 L 626 540 L 626 550 L 633 550 L 633 561 L 626 561 L 626 570 L 634 570 L 634 585 L 626 585 L 626 592 L 580 592 Z",
                facets: [
                    ["580,540 603,554 603,578 580,592", ROOF_LIGHT],
                    ["580,540 626,540 603,554", ROOF_DARK],
                    ["580,592 626,592 603,578", ROOF_DARK],
                    ["626,550 633,550 633,561 626,561", ROOF_LIGHT],
                    ["626,570 634,570 634,585 626,585", ROOF_LIGHT]
                ]
            },
            // Banpro / Bank (distinct L-shaped teal building flush against Lower West Parking & wider West Avenue)
            {
                path: "M 200 502 L 230 502 L 230 534 L 212 534 L 212 518 L 200 518 Z",
                borderWidth: 2.2,
                facets: [
                    ["200,502 230,502 221,510 200,510", ROOF_LIGHT],
                    ["230,502 230,534 221,526 221,510", ROOF_LIGHT],
                    ["212,534 230,534 221,526", ROOF_DARK]
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
            // Edificio I (Rectoria & Biblioteca Central — shifted +14px with east campus)
            {
                node: "buildingI", bldg: "I", badge: "I", badgeClass: "badge-navy", badgeX: 776, badgeY: 652,
                path: "M 762 594 L 812 594 L 812 700 L 742 700 L 742 630 L 766 630 L 766 676 L 788 676 L 788 618 L 762 618 Z",
                facets: [
                    ["762,594 812,594 798,608 776,608", ROOF_LIGHT],
                    ["812,594 812,700 798,686 798,608", ROOF_LIGHT],
                    ["742,630 754,642 754,686 742,700", ROOF_LIGHT],
                    ["742,700 812,700 798,686 754,686", ROOF_DARK]
                ]
            }
        ];

        for (const cfg of customBuildings) {
            addCustomBuilding(layer, cfg);
        }

        // --- Secondary Campus Pavilions, Kiosks, Restrooms & East Complex Buildings ---
        const supportBuildings = [
            // West & North-Central pavilions
            { x: 38, y: 278, w: 30, h: 20, orientation: "v" },  // Acopio
            { x: 248, y: 148, w: 34, h: 26 },                  // Estacion Meteorologica
            { x: 282, y: 320, w: 18, h: 18, orientation: "h" }, // Kiosko Plaza Chilamates
            { x: 536, y: 246, w: 16, h: 15 },                  // Small annex 1 below O
            { x: 556, y: 246, w: 16, h: 15 },                  // Small annex 2 below O
            { x: 540, y: 282, w: 30, h: 28 },                  // Ranchon (+12px)
            { x: 534, y: 322, w: 11, h: 15 },                  // Lab Digital FIA (+12px)
            // Sports North & Mid Concourse pavilions (+14px with east campus)
            { x: 916, y: 50, w: 36, h: 30 },                   // Kiosko NE
            { x: 992, y: 46, w: 38, h: 30 },                   // Sanitarios NE
            { x: 784, y: 325, w: 30, h: 28 },                  // Kiosko Mid
            { x: 852, y: 325, w: 30, h: 28 },                  // Sanitarios Mid
            { x: 964, y: 320, w: 42, h: 31 },                  // Oficina de Deportes
            // East / Bottom-Right Sports & Service Complex (+14px with east campus)
            { x: 978, y: 550, w: 24, h: 20, orientation: "v" },  // Public Washrooms
            { x: 976, y: 646, w: 24, h: 16, orientation: "h" },  // Small nameless pavilion
            { x: 1026, y: 652, w: 40, h: 24, orientation: "v" }, // Warehouse (Bodega)
            { x: 1088, y: 630, w: 42, h: 22, orientation: "h" }, // Jaguar Sport Kiosk (main)
            { x: 1118, y: 666, w: 26, h: 14, orientation: "h" }, // Jaguar Sport Kiosk (east booth)
            { x: 1090, y: 684, w: 58, h: 26, orientation: "v" }, // Martial Arts Building
            { x: 1092, y: 720, w: 58, h: 24, orientation: "h" }, // Multipurpose Room
            { x: 1094, y: 792, w: 56, h: 24, orientation: "h" }, // Lunch Area (Comedor)
            // Nameless Modular Complex (+14px with east campus)
            { x: 1020, y: 682, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1020, y: 698, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1020, y: 718, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1020, y: 734, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1020, y: 754, w: 52, h: 14, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1022, y: 780, w: 52, h: 16, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1022, y: 796, w: 52, h: 20, orientation: "h", borderWidth: 2 },
            { x: 1022, y: 816, w: 52, h: 14, orientation: "ribV", borderWidth: 1.5, shadow: false },
            { x: 1022, y: 832, w: 52, h: 10, orientation: "ribV", borderWidth: 1.5, shadow: false }
        ];

        // Subtle dining patio pad beneath Lunch Area (Comedor, shifted +14px)
        el("rect", { x: 1082, y: 782, width: 72, height: 42, rx: 2, fill: "#dfe5ec", stroke: "#cbd5e1", "stroke-width": 1 }, layer);

        for (const sb of supportBuildings) {
            addRectBuilding(layer, { borderWidth: 2.2, ...sb });
        }

        // Main South Gate (Entrada Principal — centered on wider West Avenue)
        const gate = el("g", { class: "bldg-shape", "data-node": "mainParking", "data-bldg": "ENTRADA" }, layer);
        el("rect", { x: 248, y: 760, width: 52, height: 18, fill: ROOF_BORDER, stroke: ROOF_BORDER, "stroke-width": 2, filter: "url(#bldgShadow)" }, gate);
    }

    // ----------------------------------------------------------------------------
    // 7. Layer 6: Landscaping (Trees & Bush Rows via Reusable SVG Symbols)
    // ----------------------------------------------------------------------------
    function renderLandscaping(layer) {
        // Large canopy tree rows [x1, y1, x2, y2, count]
        const largeTreeRows = [
            // West parking divider (8 trees) & Lower West Parking median trees (3 on upper median, 4 on lower median)
            [64, 344, 204, 344, 8],
            [138, 398, 182, 398, 3],
            [136, 446, 196, 446, 4],
            // Continuous 12-tree line hugging Building K & Main Entrance pull-out lay-by (6 beside K + 6 beside lay-by)
            [308, 486, 316, 562, 6],
            [318, 578, 326, 674, 6],
            // East edge of South Main Parking (10 continuous trees along Building E west side, Photo 12 & 13)
            [506, 504, 512, 656, 10],
            // South of Plaza Central (matching exact tree positions below K & Plaza Central)
            [398, 562, 486, 562, 5],
            // Double staggered tree rows separating G/F Parking from South-East Parking (shifted +12px)
            [640, 581, 684, 581, 4],
            [632, 593, 694, 593, 5],
            // South parking horizontal tree rows (dead-straight horizontal, matching close-up signage)
            [356, 680, 466, 680, 7],      // Below South Upper Parking (left of E)
            [630, 680, 682, 680, 3],      // Below SE Parking (right of Innovacion, +12px)
            [358, 725, 466, 725, 7],      // North/Main-Entrance Lot upper row (left block)
            [504, 725, 640, 725, 9],      // North/Main-Entrance Lot upper row (right block)
            [358, 766, 700, 766, 19],     // Bottom straight perimeter tree line
            // Double tree column flanking Central Spine Road & West side of Building I
            [704, 606, 704, 666, 5],
            [732, 598, 734, 694, 7],
            // Between Building I and Jaguar Center (bottom tree anchors NW corner of Jaguar Gym parking, +14px)
            [830, 586, 830, 684, 6],
            // Baseball Stadium: 7 west trees cleanly inside western curve + 3 south concourse trees (+14px)
            [722, 128, 730, 276, 7],
            [806, 308, 970, 308, 3],
            // Left (compass-east) edge of Soccer Field — dead-straight vertical line of 10 trees beside parking buffer (+14px)
            [761, 376, 761, 524, 10],
            // South edge of Soccer Field — clean 90-degree corner turn from vertical tree line (+14px)
            [772, 534, 940, 534, 10],
            [988, 534, 1108, 534, 7]
        ];

        for (const [x1, y1, x2, y2, count] of largeTreeRows) {
            addTreeRow(layer, x1, y1, x2, y2, count, "#treeLarge");
        }

        // Individual accent trees (near P, Plaza Chilamates perimeter, below J, K/Plaza Central, Banpro, Main Entrance, G/F, Jaguar Gym Lot, East Complex)
        const singleTrees = [
            [362, 150], [262, 314], [344, 345], [354, 562],
            [202, 528], [244, 746], [244, 766],
            [700, 585],
            [880, 704], [896, 720], [930, 696],
            [992, 577], [966, 594], [966, 614], [966, 632], [960, 662], [1146, 756]
        ];
        for (const [x, y] of singleTrees) {
            el("use", { href: "#treeLarge", x, y }, layer);
        }

        // Small manicured bush / hedge rows [x1, y1, x2, y2, count]
        const bushRows = [
            // Plaza Chilamates west hedge (10 neat small bushes)
            [268, 244, 268, 298, 10],
            // West side of Building N (9 neat small bushes aligned between corridor & shifted N)
            [356, 242, 356, 290, 9],
            // East side of Central Parking (double 6-bush column + 2 diagonal accents aligned below N & above C right dormer)
            [520, 346, 528, 386, 6],
            [531, 346, 539, 386, 6],
            [547, 354, 551, 364, 2],
            // Below H (5 bushes) & double vertical 6+6 bush column east of M (+14px)
            [608, 393, 642, 393, 5],
            [680, 434, 680, 464, 6],
            [687, 434, 687, 464, 6],
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
        // Tiny 3-bush cluster tucked cleanly above NW corner of shifted Building J
        for (const [bx, by] of [[342, 290], [349, 290], [342, 296]]) {
            el("use", { href: "#treeSmall", x: bx, y: by }, layer);
        }
    }

    // ----------------------------------------------------------------------------
    // 8. Layer 7: Emergency Layer (Safe Areas, Meeting Points & Evacuation Routes)
    // ----------------------------------------------------------------------------
    function renderEmergencyLayer(layer) {
        const evacuationPaths = [
            // Zone North (P, Observatorio, N, J, D, Ranchon, O -> North PON Lot & Meeting Point 2 east of O)
            "M 329 140 L 331 186 L 436 186",
            "M 331 186 L 336 335 L 386 335 L 386 340 L 414 340",
            "M 404 256 L 492 256 L 494 336",
            "M 442 226 L 442 198",
            "M 538 294 L 526 294 L 526 222 L 534 222 L 534 198",
            "M 574 148 L 574 184 L 474 186",
            "M 638 200 L 670 200",

            // Zone Central (A, B, C, K, E -> Meeting Point 4 in Plaza Central Ruben Dario)
            "M 352 472 L 352 484 L 440 484 L 444 494",
            "M 448 472 L 452 492",
            "M 516 472 L 470 500",
            "M 400 524 L 426 518",
            "M 518 522 L 470 518",
            "M 534 654 L 534 670 L 494 670 L 494 540 L 470 526",

            // Zone East-Center (H, M, G, F, Vida Estudiantil, SE Parking, I -> Meeting Point 5)
            "M 694 370 L 700 468 L 676 504",
            "M 644 438 L 670 438 L 676 498",
            "M 568 468 L 638 468 L 656 504",
            "M 634 508 L 646 516",
            "M 634 560 L 652 532",
            "M 570 618 L 570 600 L 663 600 L 663 536",
            "M 776 640 L 776 628 L 754 628 L 732 576 L 680 532",
            "M 810 706 L 716 706 L 716 588 L 678 534",

            // Sports Concourse -> Meeting Point 3 (Soccer Field, +14px)
            "M 768 344 L 890 426",

            // Jaguar Center, L, Gym, Physiotherapy, Warehouse, Nameless Complex & Martial Arts -> Soccer Field (+14px)
            "M 866 574 L 866 560 L 958 560 L 958 474",
            "M 912 574 L 912 560",
            "M 978 598 L 966 598 L 966 580",
            "M 978 626 L 966 626 L 966 642 L 1006 642",
            "M 992 724 L 992 696 L 958 696 L 958 566",
            "M 1018 834 L 1008 834 L 1008 580 L 964 580",
            "M 1032 676 L 1032 682 L 1008 682",
            "M 1072 646 L 1080 742",
            "M 1082 742 L 1080 742 L 1080 678",
            "M 1154 732 L 1154 656"
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

        // Emergency route junction nodes (green circles along east complex walkways, +14px)
        const junctionDots = [
            [1008, 642], [1008, 676], [1018, 682], [1072, 646], [1080, 678], [1154, 656], [1008, 766]
        ];
        for (const [cx, cy] of junctionDots) {
            el("circle", { cx, cy, r: 3.2, fill: "#166534", stroke: "#ffffff", "stroke-width": 1 }, layer);
        }

        // 7B. Safe Area / Meeting Point Green Circles with Checkmarks
        const pointsGroup = el("g", { id: "emergencySafePointsGroup" }, layer);
        const safePoints = [
            { cx: 880, cy: 194, r: 18 },   // Baseball Stadium Outfield
            { cx: 686, cy: 200, r: 10.5 }, // East of Building O (on roadside parking bay)
            { cx: 918, cy: 446, r: 21 },   // Soccer Field Center
            { cx: 448, cy: 514, r: 18 },   // Plaza Central Ruben Dario
            { cx: 663, cy: 518, r: 10.5 }  // G/F Parking Aisle (West of Pill Median)
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
