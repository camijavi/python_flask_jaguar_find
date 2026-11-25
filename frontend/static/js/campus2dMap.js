/**
 * ================================================================================
 * CAMPUS2DMAP.JS - OFFICIAL UAM 2D VECTOR CAMPUS MAP & DIRECTORY CONTROLLER
 * ================================================================================
 * Controls the interactive 2D architectural campus map replicating the official
 * UAM signage:
 * - Architectural building footprints (A-P) with official floor directory
 * - Real sports zone (Baseball Stadium, Soccer Field, Jaguar Center & Gym)
 * - Walkways, tree rows, compass rose, and animated Dijkstra pedestrian paths
 * - Interactive building inspection popover with origin/destination dispatch
 * - Smooth drag panning, mouse wheel zoom, reset controls, and directory sync
 * - Strictly pure JavaScript, clean SVG iconography, zero emojis
 * ================================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------------------------------
    // 1. DOM Elements
    // ----------------------------------------------------------------------------
    const wrapper = document.getElementById("campusMapWrapper");
    const svg = document.getElementById("officialCampus2dSvg");
    if (!wrapper || !svg) return;

    const bldgPopover = document.getElementById("bldgPopover");
    const popoverBadge = document.getElementById("popoverBadge");
    const popoverName = document.getElementById("popoverName");
    const popoverFacilities = document.getElementById("popoverFacilities");
    const btnClosePopover = document.getElementById("btnCloseBldgPopover");
    const btnSetOrigin = document.getElementById("btnSetBldgOrigin");
    const btnSetDest = document.getElementById("btnSetBldgDestination");

    const routePolyline = document.getElementById("route2dPolyline");
    const routeGlowPolyline = document.getElementById("route2dGlowPolyline");
    const routeShadowPolyline = document.getElementById("route2dShadowPolyline");
    const routeTraveledPolyline = document.getElementById("route2dTraveledPolyline");
    const originPinGroup = document.getElementById("origin2dPin");
    const destPinGroup = document.getElementById("destination2dPin");

    const btnZoomIn = document.getElementById("btnMapZoomIn");
    const btnZoomOut = document.getElementById("btnMapZoomOut");
    const btnResetView = document.getElementById("btnMapResetView");
    const compassWidget = document.getElementById("campusCompass");

    const dirSearchInput = document.getElementById("directorySearchInput");
    const dirList = document.getElementById("directoryList");
    const dirCountBadge = document.getElementById("directoryCountBadge");

    // ----------------------------------------------------------------------------
    // 2. Official Campus Building Metadata & Localized Directory Accessors
    // ----------------------------------------------------------------------------
    function resolveBuildingFloors(id, floorKeys) {
        return floorKeys.map((fk) => ({
            floor: typeof window.t === "function" ? window.t(`map.buildings.${id}.floors.${fk}.label`) : "",
            rooms: typeof window.t === "function" ? window.t(`map.buildings.${id}.floors.${fk}.rooms`) : ""
        }));
    }

    function createLocalizedBuilding(spec) {
        const entry = {
            id: spec.id,
            badgeClass: spec.badgeClass,
            badgeBg: spec.badgeBg,
            anchor: spec.anchor,
            floorKeys: spec.floorKeys
        };
        Object.defineProperty(entry, "letter", {
            enumerable: true,
            get() {
                if (spec.pinCodeKey && typeof window.t === "function") {
                    return window.t(spec.pinCodeKey);
                }
                return spec.letter;
            }
        });
        Object.defineProperty(entry, "name", {
            enumerable: true,
            get() {
                return typeof window.t === "function" ? window.t(`map.buildings.${spec.id}.name`) : spec.id;
            }
        });
        Object.defineProperty(entry, "floors", {
            enumerable: true,
            get() {
                return resolveBuildingFloors(spec.id, spec.floorKeys);
            }
        });
        return entry;
    }

    const CAMPUS_BUILDING_SPECS = [
        { id: "buildingA",       letter: "A",   badgeClass: "badge-maroon",  badgeBg: "#991b1b", anchor: { x: 250, y: 455 }, floorKeys: ["f1", "f2", "f3"] },
        { id: "buildingB",       letter: "B",   badgeClass: "badge-purple",  badgeBg: "#581c87", anchor: { x: 384, y: 500 }, floorKeys: ["f1", "f2"] },
        { id: "buildingC",       letter: "C",   badgeClass: "badge-purple",  badgeBg: "#4c1d95", anchor: { x: 384, y: 410 }, floorKeys: ["f1", "f2", "f3"] },
        { id: "buildingD",       letter: "D",   badgeClass: "badge-green",   badgeBg: "#15803d", anchor: { x: 351, y: 290 }, floorKeys: ["f1"] },
        { id: "buildingE",       letter: "E",   badgeClass: "badge-navy",    badgeBg: "#1e3a8a", anchor: { x: 458, y: 653 }, floorKeys: ["f1", "f2"] },
        { id: "buildingF",       letter: "F",   badgeClass: "badge-magenta", badgeBg: "#be185d", anchor: { x: 545, y: 646 }, floorKeys: ["f1"] },
        { id: "buildingG",       letter: "G",   badgeClass: "badge-cyan",    badgeBg: "#0284c7", anchor: { x: 545, y: 590 }, floorKeys: ["f1", "f2"] },
        { id: "buildingH",       letter: "H",   badgeClass: "badge-green",   badgeBg: "#15803d", anchor: { x: 602, y: 383 }, floorKeys: ["f1", "f2"] },
        { id: "buildingI",       letter: "I",   badgeClass: "badge-navy",    badgeBg: "#1e3a8a", anchor: { x: 653, y: 724 }, floorKeys: ["f1"] },
        { id: "buildingJ",       letter: "J",   badgeClass: "badge-cyan",    badgeBg: "#0284c7", anchor: { x: 297, y: 287 }, floorKeys: ["f1"] },
        { id: "buildingK",       letter: "K",   badgeClass: "badge-amber",   badgeBg: "#b45309", anchor: { x: 293, y: 598 }, floorKeys: ["f1", "f2"] },
        { id: "buildingL",       letter: "L",   badgeClass: "badge-cyan",    badgeBg: "#0284c7", anchor: { x: 842, y: 502 }, floorKeys: ["f1"] },
        { id: "buildingM",       letter: "M",   badgeClass: "badge-teal",    badgeBg: "#0f766e", anchor: { x: 597, y: 460 }, floorKeys: ["f1", "f2", "f3"] },
        { id: "buildingN",       letter: "N",   badgeClass: "badge-magenta", badgeBg: "#be185d", anchor: { x: 350, y: 217 }, floorKeys: ["f1", "f2"] },
        { id: "buildingO",       letter: "O",   badgeClass: "badge-amber",   badgeBg: "#b45309", anchor: { x: 510, y: 200 }, floorKeys: ["f1", "f2"] },
        { id: "buildingP",       letter: "P",   badgeClass: "badge-maroon",  badgeBg: "#881337", anchor: { x: 360, y: 104 }, floorKeys: ["f1", "f2", "f3", "f4", "f5"] },
        { id: "mainParking",     letter: "P",   badgeClass: "badge-navy",    badgeBg: "#0f172a", anchor: { x: 274, y: 766 }, floorKeys: ["f1"] },
        { id: "chilamatesPlaza", letter: "CH",  badgeClass: "badge-green",   badgeBg: "#15803d", anchor: { x: 225, y: 287 }, floorKeys: ["f1"] },
        { id: "sportsZone",      letter: "DEP", badgeClass: "badge-green",   badgeBg: "#15803d", anchor: { x: 762, y: 357 }, floorKeys: ["f1"] },
        { id: "jaguarCenter",    letter: "JC",  badgeClass: "badge-amber",   badgeBg: "#b45309", anchor: { x: 886, y: 623 }, floorKeys: ["f1"] },
        { id: "jaguarGym",       letter: "JG",  badgeClass: "badge-teal",    badgeBg: "#0f766e", anchor: { x: 955, y: 726 }, floorKeys: ["f1"] },
        { id: "physiotherapy",   letter: "FT",  badgeClass: "badge-cyan",    badgeBg: "#0284c7", anchor: { x: 964, y: 677 }, floorKeys: ["f1"] },
        { id: "jaguarJungle",    letter: "JJ",  badgeClass: "badge-green",   badgeBg: "#15803d", anchor: { x: 626, y: 306 }, floorKeys: ["f1"] },
        { id: "miRanchito",      letter: "MR",  badgeClass: "badge-amber",   badgeBg: "#b45309", anchor: { x: 555, y: 296 }, floorKeys: ["f1"] },
        { id: "labDigitalFia",   letter: "FIA", badgeClass: "badge-teal",    badgeBg: "#0f766e", anchor: { x: 530, y: 328 }, floorKeys: ["f1"] },
        { id: "areaDeMesas",     letter: "AM",  badgeClass: "badge-navy",    badgeBg: "#1e3a8a", anchor: { x: 532, y: 366 }, floorKeys: ["f1"] },
        { id: "northGate",       letter: "3",   pinCodeKey: "map.buildings.northGate.pin_code",     badgeClass: "badge-navy", badgeBg: "#475569", anchor: { x: 184, y: 74 }, floorKeys: ["f1"] },
        { id: "northeastGate",   letter: "2",   pinCodeKey: "map.buildings.northeastGate.pin_code", badgeClass: "badge-navy", badgeBg: "#0f766e", anchor: { x: 906, y: 14 }, floorKeys: ["f1"] }
    ];

    const CAMPUS_BUILDINGS = {};
    for (const spec of CAMPUS_BUILDING_SPECS) {
        CAMPUS_BUILDINGS[spec.id] = createLocalizedBuilding(spec);
    }

    // Sync anchors from single source of truth in campusMapRenderer.js
    if (window.CAMPUS_BUILDING_ANCHORS) {
        for (const [key, anchor] of Object.entries(window.CAMPUS_BUILDING_ANCHORS)) {
            if (CAMPUS_BUILDINGS[key]) CAMPUS_BUILDINGS[key].anchor = anchor;
        }
    }

    let activeSelectedBuilding = null;

    // ----------------------------------------------------------------------------
    // 3. Pan, Zoom & Real Responsive Compass Canvas Controller
    // ----------------------------------------------------------------------------
    function getDefault2dScale() {
        const w = wrapper.clientWidth || window.innerWidth;
        const h = wrapper.clientHeight || window.innerHeight;
        // On portrait mobile phones, zoom slightly in so the horizontal campus fills the screen readably
        if (w < 640 && h > w) return 1.75;
        if (w < 1024 && h > w) return 1.3;
        return 1;
    }

    let scale = getDefault2dScale();
    let translateX = (wrapper.clientWidth || window.innerWidth) < 640 ? 18 : 0;
    let translateY = (wrapper.clientWidth || window.innerWidth) < 640 ? -12 : 0;
    let rotation = 0; // View rotation angle in degrees (0° = South Up)
    let isDragging = false;
    let isRotating = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let rotateStartX = 0;
    let rotateStartAngle = 0;

    // Multi-touch gestures (Pinch-to-zoom & Twist-to-rotate)
    let isPinching = false;
    let initialPinchDist = 0;
    let initialPinchAngle = 0;
    let initialPinchScale = 1;
    let initialPinchRotation = 0;

    /**
     * Synchronizes compass needle & dial with current map orientation.
     * Functions like a real physical magnetic compass: always keeps orientation
     * pointing towards the map's South reference axis as user rotates view.
     */
    function updateCompass(deg, animate = false) {
        const dial = document.getElementById("compassDial");
        if (dial) {
            dial.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
            dial.style.transform = `rotate(${deg.toFixed(2)}deg)`;
        } else if (compassWidget) {
            const svgRose = compassWidget.querySelector("#compassRose");
            if (svgRose) {
                svgRose.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
                svgRose.style.transform = `rotate(${deg.toFixed(2)}deg)`;
            }
        }
    }

    // Expose global helper so 2.5D perspective and route animations can also sync the compass & 2D centering
    window.updateCampusCompass = updateCompass;
    window.campus2dCenterOnPoint = function (xSvg, ySvg, targetScale) {
        if (window.campus25dController && window.campus25dController.is25dActive) return;
        const w = wrapper.clientWidth || 1000;
        const h = wrapper.clientHeight || 700;
        const s = Math.min(w / 1200, h / 850);
        if (typeof targetScale === "number") {
            scale = Math.max(0.75, Math.min(targetScale, 3.8));
        } else if (scale < 1.35) {
            scale = Math.max(getDefault2dScale(), 1.45);
        }
        translateX = (600 - xSvg) * s * scale;
        translateY = (425 - ySvg) * s * scale;
        applyTransform(true);
    };

    function applyTransform(animate = false) {
        if (window.campus25dController && window.campus25dController.is25dActive) {
            svg.style.transform = "none";
            const c25d = window.campus25dController;
            const headingDeg = c25d.isHeadingUp ? -(c25d.currentHeading || 0) : 0;
            updateCompass(headingDeg, animate);
            return;
        }

        svg.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
        svg.style.transformOrigin = "50% 50%";
        svg.style.transform = `translate(${translateX.toFixed(2)}px, ${translateY.toFixed(2)}px) scale(${scale.toFixed(3)}) rotate(${rotation.toFixed(2)}deg)`;
        
        // Compass rotates with the 2D view to remain locked onto map direction
        updateCompass(rotation, animate);
    }

    if (btnZoomIn) {
        btnZoomIn.addEventListener("click", () => {
            if (window.campus25dController && window.campus25dController.is25dActive) {
                window.campus25dController.zoomIn();
                return;
            }
            scale = Math.min(scale + 0.3, 3.8);
            applyTransform(true);
        });
    }

    if (btnZoomOut) {
        btnZoomOut.addEventListener("click", () => {
            if (window.campus25dController && window.campus25dController.is25dActive) {
                window.campus25dController.zoomOut();
                return;
            }
            scale = Math.max(scale - 0.3, 0.75);
            applyTransform(true);
        });
    }

    if (btnResetView) {
        btnResetView.addEventListener("click", () => {
            if (window.campus25dController && window.campus25dController.is25dActive) {
                if (typeof window.campus25dController.recenterOnUser === "function" &&
                    (window.campus25dController.currentRoute || window.campus25dController.hasUserPosition)) {
                    window.campus25dController.recenterOnUser();
                } else {
                    window.campus25dController.zoomScale = window.campus25dController.getResponsiveZoom(2.2);
                    window.campus25dController.heading = 0;
                    window.campus25dController.currentHeading = 0;
                    window.campus25dController.centerOnCampusLowerThird();
                    window.campus25dController.updateCompass(true);
                }
                return;
            }
            if (window.campus25dController && window.campus25dController.hasUserPosition) {
                window.campus2dCenterOnPoint(
                    window.campus25dController.userSvgX,
                    window.campus25dController.userSvgY
                );
                return;
            }
            scale = getDefault2dScale();
            translateX = (wrapper.clientWidth || window.innerWidth) < 640 ? 18 : 0;
            translateY = (wrapper.clientWidth || window.innerWidth) < 640 ? -12 : 0;
            rotation = 0;
            applyTransform(true);
        });
    }

    // Interactive Compass Widget:
    // - Click: Smoothly re-aligns view to default 0° (South-Up official orientation)
    // - Drag: Allows dialing / twisting the compass directly to rotate the map
    if (compassWidget) {
        let isCompassDragging = false;
        let compassCenter = { x: 0, y: 0 };
        let hasCompassMoved = false;

        compassWidget.addEventListener("pointerdown", (e) => {
            e.stopPropagation();
            const rect = compassWidget.getBoundingClientRect();
            compassCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
            isCompassDragging = true;
            hasCompassMoved = false;
            try { compassWidget.setPointerCapture(e.pointerId); } catch (_) {}
        });

        compassWidget.addEventListener("pointermove", (e) => {
            if (!isCompassDragging) return;
            const dx = e.clientX - compassCenter.x;
            const dy = e.clientY - compassCenter.y;
            if (Math.hypot(dx, dy) > 6) {
                hasCompassMoved = true;
                // Compute angle relative to top (South = 0°)
                let angleDeg = Math.atan2(dy, dx) * 180 / Math.PI + 90;
                while (angleDeg < 0) angleDeg += 360;
                while (angleDeg >= 360) angleDeg -= 360;

                if (window.campus25dController && window.campus25dController.is25dActive) {
                    window.campus25dController.isFollowingUser = false;
                    window.campus25dController.heading = -angleDeg;
                    window.campus25dController.currentHeading = -angleDeg;
                    window.campus25dController.applyTransform();
                    window.campus25dController.updateOverlays();
                    window.campus25dController.updateCompass(false);
                } else {
                    rotation = angleDeg;
                    applyTransform(false);
                }
            }
        });

        const handleCompassPointerUp = (e) => {
            if (!isCompassDragging) return;
            isCompassDragging = false;
            try { compassWidget.releasePointerCapture(e.pointerId); } catch (_) {}

            if (!hasCompassMoved) {
                // User simply clicked the compass: smoothly reorient & center
                if (window.campus25dController && window.campus25dController.is25dActive) {
                    window.campus25dController.heading = 0;
                    window.campus25dController.currentHeading = 0;
                    window.campus25dController.applyTransform();
                    window.campus25dController.updateOverlays();
                    window.campus25dController.updateCompass(true);
                } else {
                    if (Math.abs(rotation) > 0.5) {
                        rotation = 0;
                        applyTransform(true);
                    } else {
                        scale = 1;
                        translateX = 0;
                        translateY = 0;
                        rotation = 0;
                        applyTransform(true);
                    }
                }
            }
        };

        compassWidget.addEventListener("pointerup", handleCompassPointerUp);
        compassWidget.addEventListener("pointercancel", handleCompassPointerUp);
    }

    // Mouse wheel zoom
    wrapper.addEventListener("wheel", (e) => {
        if (window.campus25dController && window.campus25dController.is25dActive) return;
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.15 : -0.15;
        scale = Math.max(0.75, Math.min(scale + delta, 2.8));
        applyTransform(false);
    }, { passive: false });

    // Desktop Mouse Drag handlers: Pan (left drag) and Rotate (Shift/Alt/Right drag)
    wrapper.addEventListener("mousedown", (e) => {
        if (window.campus25dController && window.campus25dController.is25dActive) return;
        if (e.target.closest("#bldgPopover") || e.target.closest("#lostFoundPinPopover") || e.target.closest("button") || e.target.closest("a") || e.target.closest("#campusCompass")) return;

        if (e.shiftKey || e.altKey || e.button === 2) {
            // View rotation mode
            isRotating = true;
            rotateStartX = e.clientX;
            rotateStartAngle = rotation;
            wrapper.classList.add("cursor-grabbing");
        } else if (e.button === 0) {
            // View pan mode
            isDragging = true;
            dragStartX = e.clientX - translateX;
            dragStartY = e.clientY - translateY;
            wrapper.classList.add("cursor-grabbing");
        }
    });

    wrapper.addEventListener("contextmenu", (e) => {
        if (isRotating || e.shiftKey || e.altKey) {
            e.preventDefault();
        }
    });

    window.addEventListener("mousemove", (e) => {
        if (isRotating) {
            const deltaX = e.clientX - rotateStartX;
            rotation = (rotateStartAngle + deltaX * 0.45) % 360;
            applyTransform(false);
        } else if (isDragging) {
            translateX = e.clientX - dragStartX;
            translateY = e.clientY - dragStartY;
            applyTransform(false);
        }
    });

    window.addEventListener("mouseup", () => {
        if (isDragging || isRotating) {
            isDragging = false;
            isRotating = false;
            wrapper.classList.remove("cursor-grabbing");
        }
    });

    // Touch support for Mobile / Tablet (1 finger Pan, 2 fingers Pinch-Zoom + Twist-Rotate)
    let touchStartX = 0;
    let touchStartY = 0;

    wrapper.addEventListener("touchstart", (e) => {
        if (window.campus25dController && window.campus25dController.is25dActive) return;
        if (e.target.closest("#bldgPopover") || e.target.closest("#lostFoundPinPopover") || e.target.closest("button") || e.target.closest("a") || e.target.closest("#campusCompass")) return;

        if (e.touches.length === 1) {
            isDragging = true;
            isPinching = false;
            touchStartX = e.touches[0].clientX - translateX;
            touchStartY = e.touches[0].clientY - translateY;
        } else if (e.touches.length === 2) {
            isDragging = false;
            isPinching = true;
            const t1 = e.touches[0];
            const t2 = e.touches[1];
            initialPinchDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
            initialPinchAngle = Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;
            initialPinchScale = scale;
            initialPinchRotation = rotation;
        }
    }, { passive: true });

    wrapper.addEventListener("touchmove", (e) => {
        if (isDragging && e.touches.length === 1) {
            translateX = e.touches[0].clientX - touchStartX;
            translateY = e.touches[0].clientY - touchStartY;
            applyTransform(false);
        } else if (isPinching && e.touches.length === 2) {
            const t1 = e.touches[0];
            const t2 = e.touches[1];
            const currentDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
            const currentAngle = Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;

            if (initialPinchDist > 0) {
                scale = Math.max(0.75, Math.min(initialPinchScale * (currentDist / initialPinchDist), 3.8));
            }
            const angleDiff = currentAngle - initialPinchAngle;
            rotation = (initialPinchRotation + angleDiff) % 360;
            applyTransform(false);
        }
    }, { passive: true });

    wrapper.addEventListener("touchend", (e) => {
        if (e.touches.length === 0) {
            isDragging = false;
            isPinching = false;
        } else if (e.touches.length === 1) {
            // One finger lifted, smoothly transition back to panning
            isPinching = false;
            isDragging = true;
            touchStartX = e.touches[0].clientX - translateX;
            touchStartY = e.touches[0].clientY - translateY;
        }
    }, { passive: true });

    wrapper.addEventListener("touchcancel", () => {
        isDragging = false;
        isPinching = false;
    }, { passive: true });

    // ----------------------------------------------------------------------------
    // 4. Interactive Popover & Building Highlight Logic
    // ----------------------------------------------------------------------------
    function showBuildingPopover(bldgData, anchorCoords) {
        activeSelectedBuilding = bldgData;
        if (!bldgPopover) return;

        // Dismiss the Lost & Found popover so both cards never overlap
        const lostPopover = document.getElementById("lostFoundPinPopover");
        if (lostPopover) {
            lostPopover.classList.add("hidden");
        }

        // Update building-scoped catalog link when user is authenticated
        const btnBldgCatalog = document.getElementById("btnBldgViewCatalog");
        if (btnBldgCatalog && bldgData && bldgData.id) {
            btnBldgCatalog.href = `/lost-found-object/catalogo?building=${encodeURIComponent(bldgData.id)}`;
        }

        // Populate popover
        if (popoverBadge) {
            popoverBadge.textContent = bldgData.letter || "•";
            popoverBadge.style.backgroundColor = bldgData.badgeBg || "#0284c7";
        }
        if (popoverName) {
            popoverName.textContent = bldgData.name;
        }
        if (popoverFacilities) {
            popoverFacilities.innerHTML = bldgData.floors.map(f => `
                <div class="border-b border-slate-100 pb-1 last:border-0">
                    <span class="font-bold text-slate-800">${f.floor}:</span>
                    <span class="text-slate-600">${f.rooms}</span>
                </div>
            `).join("");
        }

        // Highlight shape in SVG
        document.querySelectorAll(".bldg-shape").forEach(el => el.classList.remove("active-bldg"));
        const bldgEl = document.querySelector(`.bldg-shape[data-node="${bldgData.id}"]`);
        if (bldgEl) {
            bldgEl.classList.add("active-bldg");
        }

        // Highlight matching directory card
        document.querySelectorAll(".directory-card").forEach(c => {
            if (c.getAttribute("data-bldg") === bldgData.id) {
                c.classList.add("ring-2", "ring-brand-500", "bg-brand-50/40");
                if (c.offsetParent !== null) {
                    c.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            } else {
                c.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/40");
            }
        });

        // Position popover relative to wrapper container
        const wRect = wrapper.getBoundingClientRect();
        let clientX, clientY;

        if (window.campus25dController && window.campus25dController.is25dActive) {
            const projected = window.campus25dController.projectToScreen(anchorCoords.x, anchorCoords.y);
            if (projected) {
                clientX = projected.x;
                clientY = projected.y;
            }
        }

        if (clientX === undefined) {
            if (bldgEl) {
                const bRect = bldgEl.getBoundingClientRect();
                clientX = bRect.left - wRect.left + (bRect.width / 2);
                clientY = bRect.top - wRect.top;
            } else {
                const rect = svg.getBoundingClientRect();
                clientX = (anchorCoords.x / 1200) * rect.width;
                clientY = (anchorCoords.y / 850) * rect.height;
            }
        }

        if (wRect.width < 640) {
            // On mobile phones, anchor building popover cleanly centered above the Waze bottom dock
            bldgPopover.style.left = "50%";
            bldgPopover.style.top = "auto";
            bldgPopover.style.bottom = "80px";
            bldgPopover.style.transform = "translateX(-50%)";
        } else {
            const maxLeft = wRect.width - 310;
            const maxTop = wRect.height - 250;
            bldgPopover.style.bottom = "auto";
            bldgPopover.style.transform = "none";
            bldgPopover.style.left = `${Math.max(12, Math.min(clientX - 120, maxLeft))}px`;
            bldgPopover.style.top = `${Math.max(84, Math.min(clientY - 170, maxTop))}px`;
        }
        bldgPopover.classList.remove("hidden");
    }

    // Expose globally for decoupled 2.5D HTML overlays
    window.showBuildingPopover = showBuildingPopover;
    window.CAMPUS_BUILDINGS = CAMPUS_BUILDINGS;

    if (btnClosePopover) {
        btnClosePopover.addEventListener("click", () => {
            bldgPopover.classList.add("hidden");
            if (window.campus25dController) {
                window.campus25dController.focusedBuildingAnchor = null;
                window.campus25dController.focusedBuildingId = null;
                if (window.campus25dController.badgesContainer) {
                    window.campus25dController.badgesContainer.querySelectorAll(".waze-bldg-badge").forEach(b => {
                        b.classList.remove("waze-badge-focused");
                    });
                }
            }
            document.querySelectorAll(".bldg-shape").forEach(el => el.classList.remove("active-bldg"));
            document.querySelectorAll(".directory-card").forEach(c => {
                c.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/40");
            });
        });
    }

    // Set Origin / Destination buttons in popover
    if (btnSetOrigin) {
        btnSetOrigin.addEventListener("click", () => {
            if (!activeSelectedBuilding) return;
            const nodeId = activeSelectedBuilding.id || activeSelectedBuilding.nodeId;
            if (typeof window.setJaguarNavigationOrigin === "function" && nodeId) {
                window.setJaguarNavigationOrigin(nodeId, activeSelectedBuilding.name);
            } else {
                const originInput = document.getElementById("originInput");
                if (originInput) {
                    originInput.value = activeSelectedBuilding.name;
                    originInput.dispatchEvent(new Event("input"));
                }
            }
            if (window.innerWidth < 1024 && typeof window.openMobileBottomSheet === "function") {
                window.openMobileBottomSheet();
            } else if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
                if (typeof window.setSidebarActiveTab === "function") {
                    window.setSidebarActiveTab("nav");
                }
            }
            bldgPopover.classList.add("hidden");
        });
    }

    if (btnSetDest) {
        btnSetDest.addEventListener("click", () => {
            if (!activeSelectedBuilding) return;
            const nodeId = activeSelectedBuilding.id || activeSelectedBuilding.nodeId;
            if (typeof window.setJaguarNavigationDestination === "function" && nodeId) {
                window.setJaguarNavigationDestination(nodeId, activeSelectedBuilding.name);
            } else {
                const destInput = document.getElementById("destinationInput");
                if (destInput) {
                    destInput.value = activeSelectedBuilding.name;
                    destInput.dispatchEvent(new Event("input"));
                }
            }
            if (window.innerWidth < 1024 && typeof window.openMobileBottomSheet === "function") {
                window.openMobileBottomSheet();
            } else if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
                if (typeof window.setSidebarActiveTab === "function") {
                    window.setSidebarActiveTab("nav");
                }
            }
            bldgPopover.classList.add("hidden");
        });
    }

    const btnBldgReport = document.getElementById("btnBldgReportLost");
    if (btnBldgReport) {
        btnBldgReport.addEventListener("click", () => {
            if (!activeSelectedBuilding) return;
            const nodeId = activeSelectedBuilding.id || activeSelectedBuilding.nodeId;
            bldgPopover.classList.add("hidden");
            if (typeof window.openReportObjectDialog === "function") {
                window.openReportObjectDialog(nodeId);
            }
        });
    }

    // Attach click listeners to all SVG building shapes
    document.querySelectorAll(".bldg-shape").forEach(el => {
        el.addEventListener("click", (e) => {
            e.stopPropagation();
            const nodeId = el.getAttribute("data-node");
            const bldgData = CAMPUS_BUILDINGS[nodeId];
            if (bldgData) {
                // When clicking on a building, switch view to 2.5D and zoom specifically into that building
                if (window.campus25dController && typeof window.campus25dController.focusBuilding === "function") {
                    window.campus25dController.focusBuilding(nodeId, { zoom: 2.85, animate: true });
                } else {
                    showBuildingPopover(bldgData, bldgData.anchor);
                }

                // On small devices, close directory sidebar menu so the focused building is immediately visible
                if (window.innerWidth < 1024 && typeof window.toggleNavigateMapSidebar === "function") {
                    window.toggleNavigateMapSidebar(false);
                }
            }
        });
    });

    // ----------------------------------------------------------------------------
    // 5. Official Building Directory Interaction & Live Search
    // ----------------------------------------------------------------------------
    document.querySelectorAll(".directory-card").forEach(card => {
        card.addEventListener("click", () => {
            const nodeId = card.getAttribute("data-bldg");
            const bldgData = CAMPUS_BUILDINGS[nodeId];
            if (bldgData) {
                // When clicking on a building card, switch view to 2.5D and zoom specifically into that building
                if (window.campus25dController && typeof window.campus25dController.focusBuilding === "function") {
                    window.campus25dController.focusBuilding(nodeId, { zoom: 2.85, animate: true });
                } else {
                    const centerTargetX = (600 - bldgData.anchor.x) * 0.4;
                    const centerTargetY = (425 - bldgData.anchor.y) * 0.4;
                    translateX = centerTargetX;
                    translateY = centerTargetY;
                    scale = 1.35;
                    applyTransform();
                    showBuildingPopover(bldgData, bldgData.anchor);
                }

                // On small devices, close directory sidebar menu so the focused building is immediately visible
                if (window.innerWidth < 1024 && typeof window.toggleNavigateMapSidebar === "function") {
                    window.toggleNavigateMapSidebar(false);
                }
            }
        });
    });

    function updateDirectoryCountBadge(visibleCount) {
        if (!dirCountBadge) return;
        const count = Number.isFinite(visibleCount)
            ? visibleCount
            : parseInt(dirCountBadge.dataset.visibleCount || String(document.querySelectorAll(".directory-card").length), 10);
        dirCountBadge.dataset.visibleCount = String(count);
        if (typeof window.t === "function") {
            const key = count === 1 ? "map.buildings_count_singular" : "map.buildings_count_plural";
            dirCountBadge.textContent = window.t(key, undefined, { count });
        }
    }

    function filterDirectoryCards() {
        if (!dirSearchInput) return;
        const rawQuery = dirSearchInput.value || "";
        const q = rawQuery.toLowerCase().trim();
        const cards = document.querySelectorAll(".directory-card");
        const indexedPlaces = Array.isArray(window.jaguarCampusPlaces) ? window.jaguarCampusPlaces : [];
        let visibleCount = 0;

        cards.forEach(card => {
            const text = card.textContent || "";
            const bldgId = card.getAttribute("data-bldg") || "";
            const matched = (window.JaguarCampusSearch && typeof window.JaguarCampusSearch.matchesDirectoryCard === "function")
                ? window.JaguarCampusSearch.matchesDirectoryCard(text, bldgId, rawQuery, indexedPlaces)
                : (!q || text.toLowerCase().includes(q));
            if (matched) {
                card.style.display = "block";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        updateDirectoryCountBadge(visibleCount);
    }

    if (dirSearchInput) {
        dirSearchInput.addEventListener("input", filterDirectoryCards);
    }

    window.addEventListener("jaguarCatalogLoaded", function () {
        if (dirSearchInput && dirSearchInput.value.trim()) {
            filterDirectoryCards();
        }
    });

    window.addEventListener("jaguarLanguageChanged", function () {
        if (dirSearchInput && dirSearchInput.value.trim()) {
            filterDirectoryCards();
        } else {
            updateDirectoryCountBadge();
        }
        if (activeSelectedBuilding && bldgPopover && !bldgPopover.classList.contains("hidden")) {
            const freshData = CAMPUS_BUILDINGS[activeSelectedBuilding.id] || activeSelectedBuilding;
            showBuildingPopover(freshData, freshData.anchor || activeSelectedBuilding.anchor);
        }
    });

    // ----------------------------------------------------------------------------
    // 6. Global Dijkstra Route Visualization (Sidewalk-Hugging Micro-Walkway Routing)
    // ----------------------------------------------------------------------------
    window.addEventListener("jaguarMapRouteCalculated", function (e) {
        const route = e.detail;
        if (!route) return;

        // 1. Prefer backend Dijkstra real pedestrian walkwayPath (single source of truth synced with instructions!)
        let resolvedPts = [];
        if (Array.isArray(route.walkwayPath) && route.walkwayPath.length >= 2) {
            resolvedPts = route.walkwayPath.map(pt => ({ x: Math.round(pt.x), y: Math.round(pt.y) }));
        } else if (route.pathCoordinates && route.pathCoordinates.length >= 2) {
            // Fallback to client micro-router if walkwayPath absent
            if (typeof window.resolveMicroCampusRoute === "function") {
                resolvedPts = window.resolveMicroCampusRoute(route.pathCoordinates, {
                    accessibleOnly: Boolean(route.isAccessibleRoute)
                });
            }
            if (resolvedPts.length < 2 && !route.isAccessibleRoute) {
                resolvedPts = route.pathCoordinates.map(coord => {
                    const known = CAMPUS_BUILDINGS[coord.nodeId];
                    if (known && known.anchor) return { x: known.anchor.x, y: known.anchor.y };
                    return {
                        x: Math.round(((coord.xPercent || 50) / 100) * 1200),
                        y: Math.round(((coord.yPercent || 50) / 100) * 850)
                    };
                });
            }
        } else if (route.pathCoordinates && route.pathCoordinates.length === 1) {
            // Indoor-only single-building route
            const c0 = route.pathCoordinates[0];
            const known = CAMPUS_BUILDINGS[c0.nodeId];
            const pt = (known && known.anchor) ? known.anchor : { x: Math.round(c0.x || 600), y: Math.round(c0.y || 425) };
            resolvedPts = [pt, pt];
        } else {
            return;
        }

        if (route.isAccessibleRoute && resolvedPts.length < 2) return;
        const points = resolvedPts.map(pt => `${pt.x},${pt.y}`).join(" ");

        const managedBy25d = Boolean(
            window.campus25dController &&
            Array.isArray(window.campus25dController.activeRoutePolyline) &&
            window.campus25dController.activeRoutePolyline.length >= 2
        );
        if (!managedBy25d) {
            if (routeTraveledPolyline) routeTraveledPolyline.setAttribute("points", "");
            if (routeShadowPolyline) routeShadowPolyline.setAttribute("points", points);
            if (routePolyline) routePolyline.setAttribute("points", points);
            if (routeGlowPolyline) routeGlowPolyline.setAttribute("points", points);
        }

        // Draw Origin Pin (Ground Shadow + Upright 3D Billboard Pin)
        const startX = resolvedPts[0].x;
        const startY = resolvedPts[0].y;

        if (originPinGroup) {
            originPinGroup.innerHTML = `
                <!-- Ground Contact Shadow -->
                <ellipse cx="${startX}" cy="${startY + 2}" rx="13" ry="6" fill="#0f172a" opacity="0.4" />
                <circle cx="${startX}" cy="${startY}" r="12" fill="#10b981" opacity="0.22" />
                <!-- Upright 3D Origin Beacon (Billboarding) -->
                <g class="billboard-pin">
                    <line x1="${startX}" y1="${startY}" x2="${startX}" y2="${startY - 18}" stroke="#065f46" stroke-width="2.5" stroke-linecap="round"/>
                    <circle cx="${startX}" cy="${startY - 18}" r="9" fill="#10b981" stroke="#ffffff" stroke-width="2.5" filter="url(#bldgShadow)" />
                    <circle cx="${startX}" cy="${startY - 18}" r="3" fill="#ffffff" />
                </g>
            `;
            originPinGroup.classList.remove("hidden");
        }

        // Draw Destination Pin (Ground Shadow + Upright 3D Billboard Flag)
        const endPt = resolvedPts[resolvedPts.length - 1];
        const endX = endPt.x;
        const endY = endPt.y;

        if (destPinGroup) {
            destPinGroup.innerHTML = `
                <!-- Ground Contact Shadow -->
                <ellipse cx="${endX}" cy="${endY + 2}" rx="14" ry="7" fill="#0f172a" opacity="0.45" />
                <circle cx="${endX}" cy="${endY}" r="14" fill="#ef4444" opacity="0.22" />
                <!-- Upright 3D Destination Pin (Billboarding) -->
                <g class="billboard-pin">
                    <line x1="${endX}" y1="${endY}" x2="${endX}" y2="${endY - 24}" stroke="#1e293b" stroke-width="2.5" stroke-linecap="round"/>
                    <circle cx="${endX}" cy="${endY - 24}" r="11" fill="#ef4444" stroke="#ffffff" stroke-width="2.5" filter="url(#bldgShadow)"/>
                    <circle cx="${endX}" cy="${endY - 24}" r="4" fill="#ffffff"/>
                </g>
            `;
            destPinGroup.classList.remove("hidden");
        }

        // Automatically center canvas between origin and destination (in 2D mode)
        if (!window.campus25dController || !window.campus25dController.is25dActive) {
            const midX = (startX + endX) / 2;
            const midY = (startY + endY) / 2;
            translateX = (600 - midX) * 0.5;
            translateY = (425 - midY) * 0.5;
            scale = 1.15;
            applyTransform();
        }
    });

    window.addEventListener("jaguarMapRouteCleared", function () {
        if (routeTraveledPolyline) routeTraveledPolyline.setAttribute("points", "");
        if (routeShadowPolyline) routeShadowPolyline.setAttribute("points", "");
        if (routePolyline) routePolyline.setAttribute("points", "");
        if (routeGlowPolyline) routeGlowPolyline.setAttribute("points", "");
        if (originPinGroup) originPinGroup.classList.add("hidden");
        if (destPinGroup) destPinGroup.classList.add("hidden");
        if (bldgPopover) bldgPopover.classList.add("hidden");
        document.querySelectorAll(".bldg-shape").forEach(el => el.classList.remove("active-bldg"));
    });

    // Initial scale apply
    applyTransform();
});
