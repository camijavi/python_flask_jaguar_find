/**
 * lostFoundMapLayer.js
 * ================================================================================
 * WAZE-STYLE LOST & FOUND ALERT PINS LAYER FOR JAGUARMAPS
 * ================================================================================
 * Renders interactive Waze-style alert markers on campus nodes where items have
 * been reported lost or are held in custody. Features animated pulsing ripples,
 * item count badges, and detailed popover cards with catalog shortcuts.
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

    // Coordinate mapping helper from node metadata to 1200 x 850 SVG space
    function getSvgCoordinates(pin) {
        if (pin.xPercent != null && pin.yPercent != null) {
            return {
                x: Math.round((pin.xPercent / 100) * 1200),
                y: Math.round((pin.yPercent / 100) * 850)
            };
        }
        // Fallback: estimate from building coordinates
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

            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("class", "waze-lost-pin cursor-pointer transition-transform hover:scale-110");
            g.setAttribute("data-node-id", pin.locationNodeId);
            g.style.cursor = "pointer";

            // 1. Animated radar pulse ring (like Waze police/hazard alerts)
            const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            pulse.setAttribute("cx", x);
            pulse.setAttribute("cy", y - 18);
            pulse.setAttribute("r", "22");
            pulse.setAttribute("fill", "#f59e0b");
            pulse.setAttribute("opacity", "0.28");
            pulse.setAttribute("class", "animate-ping pointer-events-none");

            // 2. Drop shadow filter reference or soft base shadow
            const baseShadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
            baseShadow.setAttribute("cx", x);
            baseShadow.setAttribute("cy", y + 2);
            baseShadow.setAttribute("rx", "10");
            baseShadow.setAttribute("ry", "4");
            baseShadow.setAttribute("fill", "#0f172a");
            baseShadow.setAttribute("opacity", "0.22");

            // 3. Waze pin body path (round top + pointer tip downwards)
            const pinBody = document.createElementNS("http://www.w3.org/2000/svg", "path");
            // Symmetrical balloon/marker tip centered at (x, y)
            const d = `M ${x} ${y} 
                       C ${x - 6} ${y - 8}, ${x - 17} ${y - 14}, ${x - 17} ${y - 25} 
                       A 17 17 0 1 1 ${x + 17} ${y - 25} 
                       C ${x + 17} ${y - 14}, ${x + 6} ${y - 8}, ${x} ${y} Z`;
            pinBody.setAttribute("d", d);
            pinBody.setAttribute("fill", "#ffffff");
            pinBody.setAttribute("stroke", "#ea580c"); // Institutional bright amber-orange
            pinBody.setAttribute("stroke-width", "2.8");
            pinBody.setAttribute("filter", "url(#bldgShadow)");

            // 4. Inner package icon or badge
            const innerIcon = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            innerIcon.setAttribute("cx", x);
            innerIcon.setAttribute("cy", y - 25);
            innerIcon.setAttribute("r", "11");
            innerIcon.setAttribute("fill", "#fff7ed");

            // Text emoji or count
            const textIcon = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textIcon.setAttribute("x", x);
            textIcon.setAttribute("y", y - 21);
            textIcon.setAttribute("text-anchor", "middle");
            textIcon.setAttribute("font-size", "11");
            textIcon.setAttribute("font-family", "sans-serif");
            textIcon.textContent = "📦";

            // 5. Floating alert badge counter (top-right of pin)
            const countBadge = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            countBadge.setAttribute("cx", x + 12);
            countBadge.setAttribute("cy", y - 36);
            countBadge.setAttribute("r", "7.5");
            countBadge.setAttribute("fill", "#dc2626"); // Red notification badge
            countBadge.setAttribute("stroke", "#ffffff");
            countBadge.setAttribute("stroke-width", "1.5");

            const countText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            countText.setAttribute("x", x + 12);
            countText.setAttribute("y", y - 33);
            countText.setAttribute("text-anchor", "middle");
            countText.setAttribute("fill", "#ffffff");
            countText.setAttribute("font-size", "8.5");
            countText.setAttribute("font-weight", "900");
            countText.setAttribute("font-family", "sans-serif");
            countText.textContent = pin.itemsCount || 1;

            g.appendChild(pulse);
            g.appendChild(baseShadow);
            g.appendChild(pinBody);
            g.appendChild(innerIcon);
            g.appendChild(textIcon);
            g.appendChild(countBadge);
            g.appendChild(countText);

            // Interaction
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

            const stateColor = item.lostObjectStateId === 2 ? 'bg-sky-50 text-sky-700' : 'bg-amber-50 text-amber-700';

            itemRow.innerHTML = `
                <div class="min-w-0">
                    <span class="font-bold text-slate-800 text-xs block truncate leading-tight">${item.itemName}</span>
                    <span class="text-[10px] text-slate-400">${item.dateTimeReported ? item.dateTimeReported.split(' ')[0] : ''}</span>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold shrink-0 ${stateColor}">
                    ${item.stateName || 'Reportado'}
                </span>
            `;
            pinItemsList.appendChild(itemRow);
        });

        // Set catalog link
        if (btnViewCatalog) {
            btnViewCatalog.href = `/lost-found-object/catalogo?q=${encodeURIComponent(pin.locationNodeId)}`;
        }

        // Set report here button action
        if (btnReportHere) {
            btnReportHere.onclick = function() {
                popover.classList.add("hidden");
                if (typeof window.openReportObjectDialog === "function") {
                    window.openReportObjectDialog(pin.locationNodeId);
                }
            };
        }

        // Position popover near center/screen
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

    // Toggle button handler
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

    // Refresh on custom events
    window.addEventListener("lostObjectReported", fetchAndRenderPins);

    // Initial load
    document.addEventListener("DOMContentLoaded", fetchAndRenderPins);
    // Also trigger if already loaded
    if (document.readyState === "complete" || document.readyState === "interactive") {
        fetchAndRenderPins();
    }
})();
