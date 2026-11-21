/**
 * buildingPIsometric.js
 * ==============================================================================
 * Interactive 2.5D Isometric Multi-Floor Viewer & Indoor Router for Building P.
 * Features:
 *   - Smooth entrance animation on clicking Building P
 *   - UAM architectural specs: White walls, gray skirting line, dual gray doors
 *   - Central dividing wall for men's & women's restrooms
 *   - Level isolation switcher (Floor 1, 2, 3 or All)
 *   - Indoor Dijkstra turn-by-turn route visualizer
 * ==============================================================================
 */

(function () {
    "use strict";

    // SVG node coordinates on the 1150x780 canvas
    const ISO_NODE_POSITIONS = {
        // --- FLOOR 1 ---
        "p_ramp_parking": { x: 100, y: 550, floor: 1 },
        "p_stairs_f1_west": { x: 162, y: 550, floor: 1 },
        "p_restrooms_f1": { x: 238, y: 550, floor: 1 },
        "p_room_108": { x: 289, y: 536, floor: 1 },
        "p_room_107": { x: 362, y: 536, floor: 1 },
        "p_room_106": { x: 435, y: 536, floor: 1 },
        "p_room_105": { x: 508, y: 536, floor: 1 },
        "p_room_104": { x: 581, y: 536, floor: 1 },
        "p_room_103": { x: 654, y: 536, floor: 1 },
        "p_room_102": { x: 727, y: 536, floor: 1 },
        "p_room_101": { x: 800, y: 536, floor: 1 },
        "p_fountain_f1": { x: 877, y: 547, floor: 1 },
        "p_stairs_f1_east": { x: 920, y: 550, floor: 1 },
        "p_stairs_f1_ext_left": { x: 975, y: 550, floor: 1 },

        // --- FLOOR 2 ---
        "p_stairs_f2_west": { x: 162, y: 365, floor: 2 },
        "p_restrooms_f2": { x: 238, y: 365, floor: 2 },
        "p_room_208": { x: 289, y: 350, floor: 2 },
        "p_room_207": { x: 362, y: 350, floor: 2 },
        "p_room_206": { x: 435, y: 350, floor: 2 },
        "p_room_205": { x: 508, y: 350, floor: 2 },
        "p_room_204": { x: 581, y: 350, floor: 2 },
        "p_room_203": { x: 654, y: 350, floor: 2 },
        "p_room_202": { x: 727, y: 350, floor: 2 },
        "p_room_201": { x: 800, y: 350, floor: 2 },
        "p_fountain_f2_east": { x: 877, y: 362, floor: 2 },
        "p_stairs_f2_east": { x: 920, y: 365, floor: 2 },

        // --- FLOOR 3 ---
        "p_restrooms_f3": { x: 238, y: 175, floor: 3 },
        "p_room_306": { x: 291, y: 160, floor: 3 },
        "p_room_305": { x: 389, y: 160, floor: 3 },
        "p_room_304": { x: 487, y: 160, floor: 3 },
        "p_room_303": { x: 585, y: 160, floor: 3 },
        "p_room_302": { x: 683, y: 160, floor: 3 },
        "p_room_301": { x: 781, y: 160, floor: 3 },
        "p_fountain_f3": { x: 881, y: 172, floor: 3 },
        "p_stairs_f3_east": { x: 920, y: 175, floor: 3 },
    };

    let modalEl = null;
    let roomDrawerEl = null;
    let currentSelectedNodeId = null;

    function init() {
        modalEl = document.getElementById("bldgPIsometricModal");
        roomDrawerEl = document.getElementById("isoRoomDrawer");
        if (!modalEl) return;

        bindEvents();
    }

    function bindEvents() {
        // Close modal buttons
        const btnClose = document.getElementById("btnCloseIsoModal");
        if (btnClose) {
            btnClose.addEventListener("click", closeBuildingPIsometricModal);
        }

        // Click outside modal card to close
        modalEl.addEventListener("click", (e) => {
            if (e.target === modalEl) {
                closeBuildingPIsometricModal();
            }
        });

        // ESC key to close
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && modalEl && modalEl.classList.contains("bldg-modal-open")) {
                closeBuildingPIsometricModal();
            }
        });

        // Floor selector pills
        const floorBtns = modalEl.querySelectorAll(".floor-pill-btn");
        floorBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                floorBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const floor = btn.getAttribute("data-floor");
                setFloorFilter(floor);
            });
        });

        // Interactive room clicks
        const hotspots = modalEl.querySelectorAll(".room-interactive-hotspot");
        hotspots.forEach(el => {
            el.addEventListener("click", (e) => {
                e.stopPropagation();
                const roomId = el.getAttribute("data-room-id");
                const roomName = el.getAttribute("data-name");
                showRoomDrawer(roomId, roomName);
            });
        });

        // Drawer buttons
        const btnDrawerClose = document.getElementById("btnDrawerClose");
        if (btnDrawerClose) {
            btnDrawerClose.addEventListener("click", hideRoomDrawer);
        }

        const btnDrawerRoute = document.getElementById("btnDrawerRouteHere");
        if (btnDrawerRoute) {
            btnDrawerRoute.addEventListener("click", () => {
                if (!currentSelectedNodeId) return;
                const originSel = document.getElementById("isoOriginSelect");
                const originId = originSel ? originSel.value : "p_ramp_parking";
                drawIsometricRoute(originId, currentSelectedNodeId);
                hideRoomDrawer();
            });
        }

        // Indoor Route Simulation button
        const btnCalcRoute = document.getElementById("btnIsoCalculateRoute");
        if (btnCalcRoute) {
            btnCalcRoute.addEventListener("click", () => {
                const originSel = document.getElementById("isoOriginSelect");
                const destSel = document.getElementById("isoDestSelect");
                if (originSel && destSel) {
                    drawIsometricRoute(originSel.value, destSel.value);
                }
            });
        }
    }

    /**
     * Opens the Building P Isometric View with smooth cinematic animation.
     */
    function openBuildingPIsometricModal(focusRoomId = null) {
        if (!modalEl) modalEl = document.getElementById("bldgPIsometricModal");
        if (!modalEl) return;

        // Reset floor filters to All Floors view
        setFloorFilter("all");
        const allBtn = modalEl.querySelector('.floor-pill-btn[data-floor="all"]');
        if (allBtn) {
            modalEl.querySelectorAll(".floor-pill-btn").forEach(b => b.classList.remove("active"));
            allBtn.classList.add("active");
        }

        // Clear previous route
        clearRoute();

        // Reveal modal and trigger CSS animation
        modalEl.classList.remove("hidden");
        // Force reflow for smooth transition
        void modalEl.offsetWidth;
        modalEl.classList.add("bldg-modal-open");

        // If a specific room is requested, focus and highlight it
        if (focusRoomId) {
            setTimeout(() => {
                highlightRoom(focusRoomId);
            }, 400);
        }
    }

    /**
     * Closes the modal with smooth transition.
     */
    function closeBuildingPIsometricModal() {
        if (!modalEl) return;
        modalEl.classList.remove("bldg-modal-open");
        hideRoomDrawer();
        setTimeout(() => {
            modalEl.classList.add("hidden");
        }, 350);
    }

    /**
     * Isolates a specific floor level (1, 2, 3) or restores full axonometric stacked view (all).
     */
    function setFloorFilter(floor) {
        const tiers = {
            1: document.getElementById("floorTier1"),
            2: document.getElementById("floorTier2"),
            3: document.getElementById("floorTier3"),
        };

        if (floor === "all") {
            Object.values(tiers).forEach(t => {
                if (t) {
                    t.classList.remove("floor-dimmed", "floor-isolated");
                }
            });
        } else {
            const target = parseInt(floor, 10);
            Object.entries(tiers).forEach(([k, t]) => {
                if (!t) return;
                if (parseInt(k, 10) === target) {
                    t.classList.remove("floor-dimmed");
                    t.classList.add("floor-isolated");
                } else {
                    t.classList.remove("floor-isolated");
                    t.classList.add("floor-dimmed");
                }
            });
        }
    }

    /**
     * Highlights a door or target room.
     */
    function highlightRoom(nodeId) {
        // Remove existing highlights
        modalEl.querySelectorAll(".uam-door-highlight").forEach(el => el.classList.remove("uam-door-highlight"));

        // Highlight matching door element
        const doorEl = document.getElementById(`door_${nodeId}`);
        if (doorEl) {
            doorEl.classList.add("uam-door-highlight");
        }

        const hotspot = modalEl.querySelector(`.room-interactive-hotspot[data-room-id="${nodeId}"]`);
        if (hotspot) {
            const name = hotspot.getAttribute("data-name");
            showRoomDrawer(nodeId, name);
        }
    }

    /**
     * Displays the room detail card drawer.
     */
    function showRoomDrawer(nodeId, name) {
        currentSelectedNodeId = nodeId;
        if (!roomDrawerEl) roomDrawerEl = document.getElementById("isoRoomDrawer");
        if (!roomDrawerEl) return;

        const nameEl = document.getElementById("drawerRoomName");
        const subEl = document.getElementById("drawerRoomSub");
        const iconEl = document.getElementById("drawerRoomIcon");

        if (nameEl) nameEl.textContent = name || nodeId;

        const nodeMeta = ISO_NODE_POSITIONS[nodeId];
        const floorText = nodeMeta ? `Piso ${nodeMeta.floor}` : "Edificio P";

        if (subEl) {
            if (nodeId.includes("restroom")) {
                subEl.textContent = `${floorText} • Pared Divisoria Central • Servicios Higiénicos Hombres & Mujeres`;
                if (iconEl) iconEl.innerHTML = `<span class="text-xs font-bold">WC</span>`;
            } else if (nodeId.includes("fountain")) {
                subEl.textContent = `${floorText} • Bebedero de Agua Filtrada`;
                if (iconEl) iconEl.innerHTML = `<svg class="w-5 h-5 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>`;
            } else if (nodeId.includes("stairs")) {
                subEl.textContent = `${floorText} • Caja de Escaleras y Tránsito Vertical`;
                if (iconEl) iconEl.innerHTML = `<span class="text-xs font-bold">ESC</span>`;
            } else if (nodeId.includes("ramp")) {
                subEl.textContent = `${floorText} • Acceso Accesible hacia Estacionamiento y Edificio O`;
                if (iconEl) iconEl.innerHTML = `<svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="4" r="2"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 19l4-2 3 3 5-1-1-5-4 1-1-4h4"></path></svg>`;
            } else {
                subEl.textContent = `${floorText} • 2 Puertas Grises (Documentada: Izquierda) • Aulas UAM`;
                if (iconEl) iconEl.innerHTML = `<span class="text-xs font-bold">P</span>`;
            }
        }

        roomDrawerEl.classList.add("drawer-open");
    }

    function hideRoomDrawer() {
        if (roomDrawerEl) roomDrawerEl.classList.remove("drawer-open");
        currentSelectedNodeId = null;
    }

    /**
     * Calculates and renders an animated indoor route polyline on the 3D cutaway.
     */
    async function drawIsometricRoute(originId, destId) {
        clearRoute();
        try {
            const res = await fetch(`/api/map/buildings/buildingP/route?origin=${originId}&destination=${destId}&lang=spa`);
            const data = await res.json();

            if (!data.success || !data.pathNodeIds || data.pathNodeIds.length === 0) {
                alert(data.error || "No se pudo calcular la ruta interna.");
                return;
            }

            const pathNodeIds = data.pathNodeIds;
            const points = [];

            pathNodeIds.forEach(nid => {
                const pos = ISO_NODE_POSITIONS[nid];
                if (pos) {
                    points.push(pos);
                }
            });

            if (points.length < 2) return;

            // Build SVG path data string
            let d = `M ${points[0].x} ${points[0].y}`;
            for (let i = 1; i < points.length; i++) {
                const prev = points[i - 1];
                const curr = points[i];

                // If crossing floors via stairs, add a vertical connection step
                if (prev.floor !== curr.floor) {
                    d += ` L ${curr.x} ${curr.y}`;
                } else {
                    d += ` L ${curr.x} ${curr.y}`;
                }
            }

            const pathEl = document.getElementById("isoRoutePath");
            if (pathEl) {
                pathEl.setAttribute("d", d);
                pathEl.classList.remove("hidden");
            }

            // Pin at destination door
            const targetPin = document.getElementById("isoTargetPin");
            const targetPinText = document.getElementById("isoTargetPinText");
            const lastPt = points[points.length - 1];

            if (targetPin && lastPt) {
                targetPin.setAttribute("transform", `translate(${lastPt.x - 37}, ${lastPt.y - 30})`);
                targetPin.classList.remove("hidden");
                if (targetPinText) {
                    const label = destId.replace("p_room_", "P-").replace("p_", "").toUpperCase();
                    targetPinText.textContent = `DEST: ${label}`;
                }
            }

            // Highlight target door
            highlightRoom(destId);

        } catch (err) {
            console.error("Error drawing isometric route:", err);
        }
    }

    function clearRoute() {
        const pathEl = document.getElementById("isoRoutePath");
        if (pathEl) {
            pathEl.setAttribute("d", "");
            pathEl.classList.add("hidden");
        }
        const targetPin = document.getElementById("isoTargetPin");
        if (targetPin) {
            targetPin.classList.add("hidden");
        }
        if (modalEl) {
            modalEl.querySelectorAll(".uam-door-highlight").forEach(el => el.classList.remove("uam-door-highlight"));
        }
    }

    // Expose globally so map and popovers can launch Building P isometric view
    window.openBuildingPIsometricModal = openBuildingPIsometricModal;
    window.closeBuildingPIsometricModal = closeBuildingPIsometricModal;
    window.drawIsometricRoute = drawIsometricRoute;

    // Auto-initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();
