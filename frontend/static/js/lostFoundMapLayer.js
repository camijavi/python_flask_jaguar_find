/**
 * lostFoundMapLayer.js
 * ================================================================================
 * SLEEK VECTOR LOST & FOUND ALERT PINS LAYER FOR JAGUARMAPS
 * ================================================================================
 * Renders high-fidelity, proportionate vector markers on campus nodes where items
 * have been reported lost or held in custody. Features:
 * - Pure SVG vector geometry conforming with official campus map aesthetics
 * - Full 2.5D tilt & rotation compatibility via 'billboard-pin' class
 * - Soft breathing radar ring indicator
 * - Dynamic badge counter with crisp vector styling
 * - Detailed popover card on click with catalog & report integration
 */

(function() {
    let activePinsData = [];
    let layerVisible = true;
    let selectedPin = null;

    const layerGroup = document.getElementById("lostFoundMapPinsLayer");
    const toggleBtn = document.getElementById("btnToggleLostObjectsLayer");
    const badgeCounter = document.getElementById("mapLostPinsBadgeCount");
    const popover = document.getElementById("lostFoundPinPopover");
    const btnClosePopover = document.getElementById("btnCloseLostPinPopover");
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
        if (!layerGroup) return;

        try {
            const res = await fetch("/api/lost-found-object/map-pins");
            const data = await res.json();

            if (!data.success || !data.pins) {
                layerGroup.innerHTML = "";
                return;
            }

            activePinsData = data.pins;
            const totalCount = data.totalActiveItems || 0;

            if (badgeCounter) {
                badgeCounter.textContent = totalCount;
                badgeCounter.classList.toggle("hidden", totalCount === 0);
            }

            renderPins();
        } catch (err) {
            console.error("Failed to load lost & found map pins", err);
        }
    }

    function renderPins() {
        if (!layerGroup) return;
        layerGroup.innerHTML = "";
        layerGroup.style.display = layerVisible ? "block" : "none";

        if (!layerVisible || activePinsData.length === 0) return;

        activePinsData.forEach(pin => {
            const coords = getSvgCoordinates(pin);
            const x = coords.x;
            const y = coords.y;

            // Master Pin Group with billboard-pin class for 2.5D camera alignment
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("class", "waze-lost-pin cursor-pointer");
            g.setAttribute("data-node-id", pin.locationNodeId);
            g.style.cursor = "pointer";

            // 1. Soft Ground Contact Shadow (exact proportions of campus nodes)
            const shadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
            shadow.setAttribute("cx", x);
            shadow.setAttribute("cy", y + 1);
            shadow.setAttribute("rx", "11");
            shadow.setAttribute("ry", "4.5");
            shadow.setAttribute("fill", "#0f172a");
            shadow.setAttribute("opacity", "0.26");

            // 2. Subtle translucent pulse ring (non-intrusive)
            const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            pulse.setAttribute("cx", x);
            pulse.setAttribute("cy", y);
            pulse.setAttribute("r", "13");
            pulse.setAttribute("fill", "#2f99a8");
            pulse.setAttribute("opacity", "0.22");
            pulse.setAttribute("class", "animate-ping pointer-events-none");

            // 3. Upright 3D Pin Beacon (Billboarding group)
            const beaconGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
            beaconGroup.setAttribute("class", "billboard-pin");

            // Pin Needle / Stalk pointing to ground contact
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

            // Crisp Vector Package Icon (Isometric pure SVG paths, no emoji!)
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
            g.appendChild(pulse);
            g.appendChild(beaconGroup);

            // Click Handler
            g.addEventListener("click", function(e) {
                e.stopPropagation();
                showPinPopover(pin, x, y);
            });

            layerGroup.appendChild(g);
        });
    }

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

        if (btnReportHere) {
            btnReportHere.onclick = function() {
                popover.classList.add("hidden");
                if (typeof window.openReportObjectDialog === "function") {
                    window.openReportObjectDialog(pin.locationNodeId);
                }
            };
        }

        popover.classList.remove("hidden");
        popover.style.top = "80px";
        popover.style.left = "50%";
        popover.style.transform = "translateX(-50%)";
    }

    if (btnClosePopover) {
        btnClosePopover.addEventListener("click", () => {
            if (popover) popover.classList.add("hidden");
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
