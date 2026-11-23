/**
 * lostFoundMapLayer.js
 * ================================================================================
 * SLEEK VECTOR & 2.5D LOST & FOUND ALERT PINS LAYER FOR JAGUARMAPS
 * ================================================================================
 * Renders high-fidelity, proportionate vector markers on campus nodes where items
 * have been reported lost or held in custody. Features:
 * - Pure SVG vector geometry conforming with official campus map aesthetics
 * - Full 2.5D perspective decoupling via HTML overlays in #wazeLostPinsContainer
 * - Zero unanchored pulse animations (no rogue blue circles on canvas)
 * - Dynamic badge counter with crisp vector styling
 * - Detailed popover card on click with catalog & report integration
 * - Camera focus integration in 2.5D mode
 */

(function() {
    let activePinsData = [];
    let layerVisible = true;
    let selectedPin = null;

    const layerGroup = document.getElementById("lostFoundMapPinsLayer");
    const container25d = document.getElementById("wazeLostPinsContainer");
    const toggleBtn = document.getElementById("btnToggleLostObjectsLayer");
    const badgeCounter = document.getElementById("mapLostPinsBadgeCount");
    const popover = document.getElementById("lostFoundPinPopover");
    const btnClosePopover = document.getElementById("btnCloseLostPinPopover");
    const btnFocus25d = document.getElementById("btnFocus25dPin");
    const pinNodeName = document.getElementById("lostPinNodeName");
    const pinCountSub = document.getElementById("lostPinCountSubtitle");
    const pinItemsList = document.getElementById("lostPinItemsList");
    const btnViewCatalog = document.getElementById("btnViewInCatalog");
    const btnReportHere = document.getElementById("btnReportHere");

    function getSvgCoordinates(pin) {
        if (pin.xPercent != null && pin.yPercent != null) {
            return {
                x: Math.round((pin.xPercent / 100) * 1200),
                y: Math.round((pin.yPercent / 100) * 850)
            };
        }
        return { x: 600, y: 425 };
    }

    async function fetchAndRenderPins() {
        try {
            const res = await fetch("/api/lost-found-object/map-pins");
            const data = await res.json();

            if (!data.success || !data.pins) {
                if (layerGroup) layerGroup.innerHTML = "";
                if (container25d) container25d.innerHTML = "";
                return;
            }

            activePinsData = data.pins;
            const totalCount = data.totalActiveItems || 0;

            if (badgeCounter) {
                badgeCounter.textContent = totalCount;
                badgeCounter.classList.toggle("hidden", totalCount === 0);
            }

            renderPins();
            checkUrlFocusTarget();
        } catch (err) {
            console.error("Failed to load lost & found map pins", err);
        }
    }

    function checkUrlFocusTarget() {
        const params = new URLSearchParams(window.location.search);
        const focusNode = params.get("focus");
        const modeParam = params.get("mode");

        if (focusNode || modeParam === "25d") {
            setTimeout(() => {
                if (window.campus25dController) {
                    if (modeParam === "25d" && !window.campus25dController.is25dActive) {
                        window.campus25dController.setMode(true);
                    }
                    if (focusNode && typeof window.campus25dController.focusBuilding === "function") {
                        window.campus25dController.focusBuilding(focusNode, { zoom: 2.85, animate: true });
                        const matchPin = activePinsData.find(p => p.locationNodeId && p.locationNodeId.toLowerCase() === focusNode.toLowerCase());
                        if (matchPin) {
                            showPinPopover(matchPin);
                        }
                    }
                }
            }, 350);
        }
    }

    function renderPins() {
        const is25dActive = window.campus25dController && window.campus25dController.is25dActive;

        // 1. Render 2D SVG Pins
        if (layerGroup) {
            layerGroup.innerHTML = "";
            layerGroup.style.display = (!is25dActive && layerVisible) ? "block" : "none";

            if (layerVisible && activePinsData.length > 0) {
                activePinsData.forEach(pin => {
                    const coords = getSvgCoordinates(pin);
                    const x = coords.x;
                    const y = coords.y;

                    // Master Pin Group
                    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                    g.setAttribute("class", "waze-lost-pin cursor-pointer");
                    g.setAttribute("data-node-id", pin.locationNodeId);
                    g.style.cursor = "pointer";

                    // Soft Ground Contact Shadow (static, proportional, zero CSS scaling)
                    const shadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
                    shadow.setAttribute("cx", x);
                    shadow.setAttribute("cy", y + 1);
                    shadow.setAttribute("rx", "11");
                    shadow.setAttribute("ry", "4.5");
                    shadow.setAttribute("fill", "#0f172a");
                    shadow.setAttribute("opacity", "0.26");

                    // Upright 3D Pin Beacon
                    const beaconGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
                    beaconGroup.setAttribute("class", "billboard-pin");

                    // Pin Stalk pointing to ground contact
                    const stalk = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    stalk.setAttribute("x1", x);
                    stalk.setAttribute("y1", y);
                    stalk.setAttribute("x2", x);
                    stalk.setAttribute("y2", y - 13);
                    stalk.setAttribute("stroke", "#1e293b");
                    stalk.setAttribute("stroke-width", "2");
                    stalk.setAttribute("stroke-linecap", "round");

                    // Outer Badge Circle (Clean white card with brand teal accent ring)
                    const badgeBg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                    const badgeCenterY = y - 24;
                    badgeBg.setAttribute("cx", x);
                    badgeBg.setAttribute("cy", badgeCenterY);
                    badgeBg.setAttribute("r", "11.5");
                    badgeBg.setAttribute("fill", "#ffffff");
                    badgeBg.setAttribute("stroke", "#2f99a8");
                    badgeBg.setAttribute("stroke-width", "2.2");
                    badgeBg.setAttribute("filter", "url(#bldgShadow)");

                    // Inner soft tint circle
                    const badgeInner = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                    badgeInner.setAttribute("cx", x);
                    badgeInner.setAttribute("cy", badgeCenterY);
                    badgeInner.setAttribute("r", "9.5");
                    badgeInner.setAttribute("fill", "#f0fdfa");

                    // Crisp Vector Package Icon (pure SVG, no emojis)
                    const iconGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
                    iconGroup.setAttribute("transform", `translate(${x - 6.5}, ${badgeCenterY - 6.5})`);
                    iconGroup.innerHTML = `
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#185057" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" fill="#5dafbb" fill-opacity="0.35"/>
                            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                            <line x1="12" y1="22.08" x2="12" y2="12"/>
                        </svg>
                    `;

                    beaconGroup.appendChild(stalk);
                    beaconGroup.appendChild(badgeBg);
                    beaconGroup.appendChild(badgeInner);
                    beaconGroup.appendChild(iconGroup);

                    // Counter Badge Pill (if 1 or more items)
                    const countX = x + 8.5;
                    const countY = badgeCenterY - 8.5;

                    const badgeCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                    badgeCircle.setAttribute("cx", countX);
                    badgeCircle.setAttribute("cy", countY);
                    badgeCircle.setAttribute("r", "5.8");
                    badgeCircle.setAttribute("fill", "#f59e0b");
                    badgeCircle.setAttribute("stroke", "#ffffff");
                    badgeCircle.setAttribute("stroke-width", "1.2");

                    const badgeText = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    badgeText.setAttribute("x", countX);
                    badgeText.setAttribute("y", countY + 2.2);
                    badgeText.setAttribute("text-anchor", "middle");
                    badgeText.setAttribute("fill", "#ffffff");
                    badgeText.setAttribute("font-size", "7");
                    badgeText.setAttribute("font-weight", "900");
                    badgeText.setAttribute("font-family", "system-ui, sans-serif");
                    badgeText.textContent = pin.itemsCount || 1;

                    beaconGroup.appendChild(badgeCircle);
                    beaconGroup.appendChild(badgeText);

                    g.appendChild(shadow);
                    g.appendChild(beaconGroup);

                    // Click Handler
                    g.addEventListener("click", function(e) {
                        e.stopPropagation();
                        showPinPopover(pin, x, y);
                    });

                    layerGroup.appendChild(g);
                });
            }
        }

        // 2. Render 2.5D Decoupled HTML Markers
        if (container25d) {
            container25d.innerHTML = "";
            container25d.style.display = (is25dActive && layerVisible) ? "block" : "none";

            if (layerVisible && activePinsData.length > 0) {
                activePinsData.forEach(pin => {
                    const marker = document.createElement("div");
                    marker.id = `wazeLostPin_${pin.locationNodeId}`;
                    marker.className = "waze-lost-pin-25d absolute pointer-events-auto cursor-pointer transition-transform hover:scale-115";
                    marker.style.display = "none";
                    marker.setAttribute("data-node-id", pin.locationNodeId);
                    marker.title = `${pin.itemsCount} objeto(s) reportado(s) en ${pin.locationName || pin.locationNodeId}`;

                    marker.innerHTML = `
                        <div class="relative flex flex-col items-center">
                            <div class="w-8 h-8 rounded-full bg-white border-2 border-[#2f99a8] shadow-lg shadow-black/25 flex items-center justify-center relative bg-gradient-to-b from-white to-slate-50">
                                <svg class="w-4 h-4 text-brand-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                                </svg>
                                <span class="absolute -top-1.5 -right-1.5 min-w-[17px] h-4 px-1 rounded-full bg-amber-500 border-2 border-white text-white text-[9px] font-black flex items-center justify-center leading-none shadow-xs">
                                    ${pin.itemsCount || 1}
                                </span>
                            </div>
                            <div class="w-0.5 h-2.5 bg-slate-800"></div>
                            <div class="w-3 h-1 rounded-full bg-slate-900/40"></div>
                        </div>
                    `;

                    marker.addEventListener("click", (e) => {
                        e.stopPropagation();
                        if (window.campus25dController && typeof window.campus25dController.focusBuilding === "function") {
                            window.campus25dController.focusBuilding(pin.locationNodeId, { zoom: 2.85, animate: true });
                        }
                        showPinPopover(pin);
                    });

                    container25d.appendChild(marker);
                });
            }
        }

        // Trigger position update for 2.5D markers if 2.5D is active
        if (window.campus25dController && typeof window.update25dLostPins === "function") {
            window.update25dLostPins(window.campus25dController);
        }
    }

    window.update25dLostPins = function(controller) {
        if (!controller || !container25d) return;

        const is25d = controller.is25dActive;
        container25d.style.display = (is25d && layerVisible) ? "block" : "none";
        if (layerGroup) {
            layerGroup.style.display = (!is25d && layerVisible) ? "block" : "none";
        }

        if (!is25d || !layerVisible) return;

        const vh = controller.viewport ? controller.viewport.clientHeight : 700;
        const vw = controller.viewport ? controller.viewport.clientWidth : 1000;
        const roofLift = (controller.pitch || 45) >= 50 ? 5.5 : 6.0;

        activePinsData.forEach(pin => {
            const el = document.getElementById(`wazeLostPin_${pin.locationNodeId}`);
            if (!el) return;

            let anchorX = 600, anchorY = 425;
            if (controller.buildingAnchors && controller.buildingAnchors[pin.locationNodeId]) {
                anchorX = controller.buildingAnchors[pin.locationNodeId].x;
                anchorY = controller.buildingAnchors[pin.locationNodeId].y;
            } else if (pin.xPercent != null && pin.yPercent != null) {
                anchorX = Math.round((pin.xPercent / 100) * 1200);
                anchorY = Math.round((pin.yPercent / 100) * 850);
            }

            const projY = anchorY - roofLift;
            const pos = controller.projectToScreen(anchorX, projY);

            if (pos && pos.y >= 16 && pos.y <= vh - 20 && pos.x >= -40 && pos.x <= vw + 40) {
                el.style.display = "block";
                el.style.left = `${pos.x.toFixed(1)}px`;
                el.style.top = `${pos.y.toFixed(1)}px`;
                const scaleFactor = Math.min(1.15, Math.max(0.72, pos.k * 0.98));
                el.style.transform = `translate(-50%, -100%) scale(${scaleFactor.toFixed(3)})`;
                const horizonFade = Math.min(1.0, Math.max(0.0, (pos.y - 12) / 36));
                el.style.opacity = horizonFade.toFixed(2);
            } else {
                el.style.display = "none";
            }
        });

        // Reposition popover if pin is currently selected
        if (selectedPin && popover && !popover.classList.contains("hidden")) {
            let anchorX = 600, anchorY = 425;
            if (controller.buildingAnchors && controller.buildingAnchors[selectedPin.locationNodeId]) {
                anchorX = controller.buildingAnchors[selectedPin.locationNodeId].x;
                anchorY = controller.buildingAnchors[selectedPin.locationNodeId].y;
            }
            const pos = controller.projectToScreen(anchorX, anchorY - roofLift);
            if (pos) {
                const maxLeft = Math.max(12, vw - 340);
                const maxTop = Math.max(80, vh - 260);
                if (vw < 640) {
                    popover.style.left = "50%";
                    popover.style.top = "auto";
                    popover.style.bottom = "80px";
                    popover.style.transform = "translateX(-50%)";
                } else {
                    popover.style.bottom = "auto";
                    popover.style.transform = "none";
                    popover.style.left = `${Math.max(12, Math.min(pos.x - 140, maxLeft))}px`;
                    popover.style.top = `${Math.max(80, Math.min(pos.y - 210, maxTop))}px`;
                }
            }
        }
    };

    function showPinPopover(pin, svgX, svgY) {
        selectedPin = pin;
        if (!popover) return;

        pinNodeName.textContent = pin.locationName || pin.locationNodeId;
        pinCountSub.textContent = `${pin.itemsCount} objeto${pin.itemsCount === 1 ? '' : 's'} extraviado${pin.itemsCount === 1 ? '' : 's'} o en custodia`;

        pinItemsList.innerHTML = "";
        pin.items.forEach(item => {
            const itemRow = document.createElement("div");
            itemRow.className = "p-2 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-2";

            const isCustody = item.lostObjectStateId === 2;
            const stateColor = isCustody ? 'bg-sky-50 text-sky-700 border-sky-200' : 'bg-amber-50 text-amber-800 border-amber-200';

            itemRow.innerHTML = `
                <div class="min-w-0 flex items-center gap-2">
                    <span class="w-6 h-6 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 shrink-0">
                        <svg class="w-3.5 h-3.5 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                    </span>
                    <div class="min-w-0">
                        <span class="font-bold text-slate-800 text-xs block truncate leading-tight">${item.itemName}</span>
                        <span class="text-[10px] text-slate-400">${item.dateTimeReported ? item.dateTimeReported.split(' ')[0] : ''}</span>
                    </div>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold shrink-0 border ${stateColor}">
                    ${item.stateName || 'Reportado'}
                </span>
            `;
            pinItemsList.appendChild(itemRow);
        });

        if (btnViewCatalog) {
            btnViewCatalog.href = `/lost-found-object/catalogo?q=${encodeURIComponent(pin.locationNodeId)}`;
        }

        if (btnFocus25d) {
            btnFocus25d.onclick = function() {
                if (window.campus25dController && typeof window.campus25dController.focusBuilding === "function") {
                    window.campus25dController.focusBuilding(pin.locationNodeId, { zoom: 2.85, animate: true });
                }
            };
        }

        if (btnReportHere) {
            btnReportHere.onclick = function() {
                popover.classList.add("hidden");
                if (typeof window.openReportObjectDialog === "function") {
                    window.openReportObjectDialog(pin.locationNodeId);
                }
            };
        }

        popover.classList.remove("hidden");

        const is25d = window.campus25dController && window.campus25dController.is25dActive;
        if (!is25d) {
            popover.style.top = "80px";
            popover.style.left = "50%";
            popover.style.transform = "translateX(-50%)";
        } else if (window.campus25dController) {
            window.update25dLostPins(window.campus25dController);
        }
    }

    if (btnClosePopover) {
        btnClosePopover.addEventListener("click", () => {
            if (popover) popover.classList.add("hidden");
            selectedPin = null;
        });
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            layerVisible = !layerVisible;
            toggleBtn.setAttribute("aria-pressed", layerVisible ? "true" : "false");
            toggleBtn.classList.toggle("bg-amber-100", layerVisible);
            toggleBtn.classList.toggle("text-amber-800", layerVisible);
            toggleBtn.classList.toggle("bg-slate-50", !layerVisible);
            toggleBtn.classList.toggle("text-slate-400", !layerVisible);
            renderPins();
            if (!layerVisible && popover) popover.classList.add("hidden");
        });
    }

    window.addEventListener("lostObjectReported", fetchAndRenderPins);

    document.addEventListener("DOMContentLoaded", fetchAndRenderPins);
    if (document.readyState === "complete" || document.readyState === "interactive") {
        fetchAndRenderPins();
    }
})();
