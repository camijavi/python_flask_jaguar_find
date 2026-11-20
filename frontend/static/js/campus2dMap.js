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
    const originPinGroup = document.getElementById("origin2dPin");
    const destPinGroup = document.getElementById("destination2dPin");

    const btnZoomIn = document.getElementById("btnMapZoomIn");
    const btnZoomOut = document.getElementById("btnMapZoomOut");
    const btnResetView = document.getElementById("btnMapResetView");

    const dirSearchInput = document.getElementById("directorySearchInput");
    const dirList = document.getElementById("directoryList");
    const dirCountBadge = document.getElementById("directoryCountBadge");

    // ----------------------------------------------------------------------------
    // 2. Official Campus Building Metadata & Directory Details (1024 x 764 Canvas)
    // ----------------------------------------------------------------------------
    const CAMPUS_BUILDINGS = {
        "buildingA": {
            id: "buildingA",
            letter: "A",
            name: "Edificio A • Atención al Estudiante",
            badgeClass: "badge-maroon",
            badgeBg: "#b91c1c",
            anchor: { x: 270, y: 490 },
            floors: [
                { floor: "Piso 1", rooms: "Contabilidad, CAE (Centro de Atención al Estudiante), Admisiones, Registro Académico, Cartera y Cobro, Finanzas, Cajeros Automáticos." },
                { floor: "Piso 2", rooms: "Dirección Administrativa, Logística Académica, TIC (Tecnología de la Información), Mercadeo y Publicidad, Gestión del Talento y RRHH." },
                { floor: "Piso 3", rooms: "Dirección de Producción Audiovisual (DPA), Set de Grabación Ciclograma, Estudio de Sonido, Oficinas Auxiliares DPA, Control Máster, Set de Radio." }
            ]
        },
        "buildingB": {
            id: "buildingB",
            letter: "B",
            name: "Edificio B • Aulas & Farmacia",
            badgeClass: "badge-purple",
            badgeBg: "#7e22ce",
            anchor: { x: 375, y: 512 },
            floors: [
                { floor: "Piso 1", rooms: "Módulo Comercial 1, Aulas B101 - B109, SS Hombres / Mujeres, Jaguar Shop." },
                { floor: "Piso 2", rooms: "Aulas B201 - B210." }
            ]
        },
        "buildingC": {
            id: "buildingC",
            letter: "C",
            name: "Edificio C • Cómputo & Caja UAM",
            badgeClass: "badge-navy",
            badgeBg: "#1e3a8a",
            anchor: { x: 375, y: 465 },
            floors: [
                { floor: "Piso 1", rooms: "Área de Lavado Uso Común, Auditorio C101, Aulas C102-C104, Caja UAM / Tesorería, Aula C106, Lab MAC C107, Lab Cómputo Acad-Erasmus, Auditorio C109." },
                { floor: "Piso 2", rooms: "Laboratorios de Computación C201-C205, Laboratorio MAC C203, SS Hombres / Mujeres, Aulas C209-C211." },
                { floor: "Piso 3", rooms: "Aulas C301-C305, Coordinación de Compras, Aulas C307-C310." }
            ]
        },
        "buildingD": {
            id: "buildingD",
            letter: "D",
            name: "Edificio D • Odontología Digital",
            badgeClass: "badge-green",
            badgeBg: "#15803d",
            anchor: { x: 340, y: 355 },
            floors: [
                { floor: "Piso 1", rooms: "Aula D102, Laboratorio de Odontología Digital CAM-CAM, Oficina de Servicio al Cliente, Sala de Reunión." }
            ]
        },
        "buildingE": {
            id: "buildingE",
            letter: "E",
            name: "Edificio E • Facultad de Medicina",
            badgeClass: "badge-navy",
            badgeBg: "#1e3a8a",
            anchor: { x: 450, y: 660 },
            floors: [
                { floor: "Piso 1", rooms: "Clínica Médica & Atención al Adolescente, SS Hombres / Mujeres, Centro de Diagnóstico, Decanatura de Medicina, Oficinas de Médicos Especialistas." }
            ]
        },
        "buildingF": {
            id: "buildingF",
            letter: "F",
            name: "Edificio F • FACEE (Ciencias Económicas)",
            badgeClass: "badge-maroon",
            badgeBg: "#b91c1c",
            anchor: { x: 500, y: 662 },
            floors: [
                { floor: "Piso 1", rooms: "Salón de Profesores FACEE, Dirección de Postgrado y Formación Continua, Decanatura FACEE, Aulas F101-F104." }
            ]
        },
        "buildingG": {
            id: "buildingG",
            letter: "G",
            name: "Edificio G • Derecho & Auditorio",
            badgeClass: "badge-cyan",
            badgeBg: "#0284c7",
            anchor: { x: 500, y: 585 },
            floors: [
                { floor: "Piso 1", rooms: "Decanatura FCJ, Centro de Mediación, Language Center, UAM College, Dirección de Relaciones Internacionales." },
                { floor: "Piso 2", rooms: "Auditorio Central Rubén Darío, Sala de Juicios Orales Simulados." }
            ]
        },
        "buildingH": {
            id: "buildingH",
            letter: "H",
            name: "Edificio H • Laboratorios de Medicina",
            badgeClass: "badge-green",
            badgeBg: "#15803d",
            anchor: { x: 538, y: 415 },
            floors: [
                { floor: "Piso 1", rooms: "SS Hombres / Mujeres, Laboratorios Multidisciplinarios H101-H103, Coordinación de Laboratorios, Oficina de Sustancias Químicas, Laboratorios H105-H107." },
                { floor: "Piso 2", rooms: "Laboratorio de Anatomía H201-H207, Quirófano de Práctica, Depósito de Reactivos." }
            ]
        },
        "buildingI": {
            id: "buildingI",
            letter: "I",
            name: "Edificio I • Rectoría & Biblioteca Central",
            badgeClass: "badge-purple",
            badgeBg: "#7e22ce",
            anchor: { x: 642, y: 595 },
            floors: [
                { floor: "Piso 1", rooms: "SS Hombres / Mujeres, Vicepresidencia, Sala de Reunión de Consejo, Dirección Académica, Rectoría, Gerencia General, Secretaría General, Biblioteca Central UAM, Dirección de RR.PP." }
            ]
        },
        "buildingJ": {
            id: "buildingJ",
            letter: "J",
            name: "Edificio J • Laboratorios Odontología",
            badgeClass: "badge-cyan",
            badgeBg: "#0284c7",
            anchor: { x: 295, y: 355 },
            floors: [
                { floor: "Piso 1", rooms: "Laboratorio de Simulación y Práctica Preclínica Odontológica J101-J102, Depósito de Instrumental, SS Hombres / Mujeres." }
            ]
        },
        "buildingK": {
            id: "buildingK",
            letter: "K",
            name: "Edificio K • Cafetería Central & Terrazas",
            badgeClass: "badge-teal",
            badgeBg: "#0f766e",
            anchor: { x: 305, y: 615 },
            floors: [
                { floor: "Piso 1", rooms: "Comedor Estudiantil Central, Kioscos Gourmet, Terrazas Techadas, Cajeros Automáticos Banpro / BAC." }
            ]
        },
        "buildingL": {
            id: "buildingL",
            letter: "L",
            name: "Edificio L • Cultura & Graderías",
            badgeClass: "badge-cyan",
            badgeBg: "#0284c7",
            anchor: { x: 818, y: 500 },
            floors: [
                { floor: "Piso 1", rooms: "Sala de Ensayo Musical y Danza, Auditorio Jaguar, Acceso a Graderías del Complejo Deportivo, Oficinas de Deportes." }
            ]
        },
        "buildingM": {
            id: "buildingM",
            letter: "M",
            name: "Edificio M • Aulas & Postgrados",
            badgeClass: "badge-teal",
            badgeBg: "#0f766e",
            anchor: { x: 515, y: 490 },
            floors: [
                { floor: "Piso 1", rooms: "Aulas de Grado M101 - M108, Coordinación de Maestrías y Especialidades." },
                { floor: "Piso 2", rooms: "Aulas Ejecutivas M201 - M208, Sala de Coworking para Investigadores." }
            ]
        },
        "buildingN": {
            id: "buildingN",
            letter: "N",
            name: "Edificio N • Clínicas Odontológicas",
            badgeClass: "badge-magenta",
            badgeBg: "#be185d",
            anchor: { x: 368, y: 305 },
            floors: [
                { floor: "Piso 1", rooms: "Recepción de Pacientes, Módulo de Triaje, Clínicas Odontológicas Integrales, Quirófano Ambulatorio, Central de Esterilización." }
            ]
        },
        "buildingO": {
            id: "buildingO",
            letter: "O",
            name: "Edificio O • Facultad de Ingeniería (FIA)",
            badgeClass: "badge-amber",
            badgeBg: "#d97706",
            anchor: { x: 508, y: 200 },
            floors: [
                { floor: "Piso 1", rooms: "Decanatura FIA, Laboratorio de Resistencia de Materiales y Suelos, Taller de Maquetería y Diseño Arquitectónico." },
                { floor: "Piso 2", rooms: "Aulas de Ingeniería O201 - O208, Salas de Cómputo CAD / BIM." }
            ]
        },
        "buildingP": {
            id: "buildingP",
            letter: "P",
            name: "Edificio P • Copérnico & Observatorio",
            badgeClass: "badge-maroon",
            badgeBg: "#b91c1c",
            anchor: { x: 370, y: 105 },
            floors: [
                { floor: "Piso 1", rooms: "Aulas P101 - P106, Observatorio Meteorológico UAM, Laboratorio de Física Experimental y Astronomía." }
            ]
        },
        "mainParking": {
            id: "mainParking",
            letter: "P",
            name: "Entrada Principal & Parqueo Sur",
            badgeClass: "badge-navy",
            badgeBg: "#0f172a",
            anchor: { x: 350, y: 595 },
            floors: [
                { floor: "Exterior", rooms: "Caseta de Seguridad Sur, Bahías de Parqueo Estudiantil y Docente, Rampa Peatonal Principal hacia Edificio K." }
            ]
        },
        "chilamatesPlaza": {
            id: "chilamatesPlaza",
            letter: "CH",
            name: "Plaza Chilamates (Kioskos & Fast Food)",
            badgeClass: "badge-green",
            badgeBg: "#15803d",
            anchor: { x: 235, y: 360 },
            floors: [
                { floor: "Plaza", rooms: "Kioskos de Comida Rápida, Puntos de Café, Mesas al Aire Libre, Espacio de Recreación Estudiantil." }
            ]
        },
        "sportsZone": {
            id: "sportsZone",
            letter: "DEP",
            name: "Canchas Deportivas (Béisbol & Fútbol)",
            badgeClass: "badge-green",
            badgeBg: "#15803d",
            anchor: { x: 760, y: 385 },
            floors: [
                { floor: "Campo Abierto", rooms: "Estadio Oficial de Béisbol con Diamante de Tierra, Cancha de Fútbol Reglamentaria de Grama, Pista y Acceso a Camerinos." }
            ]
        },
        "jaguarCenter": {
            id: "jaguarCenter",
            letter: "JC",
            name: "Jaguar Center (Gimnasio & Complejo Deportivo)",
            badgeClass: "badge-amber",
            badgeBg: "#d97706",
            anchor: { x: 740, y: 558 },
            floors: [
                { floor: "Piso 1", rooms: "Gimnasio Universitario Jaguar Gym, Canchas Techadas de Baloncesto / Voleibol, Graderías Principales, Área de Fisioterapia." }
            ]
        },
        "northGate": {
            id: "northGate",
            letter: "ACC",
            name: "Tercer Acceso / Acceso Norte (Copérnico)",
            badgeClass: "badge-cyan",
            badgeBg: "#0284c7",
            anchor: { x: 170, y: 50 },
            floors: [
                { floor: "Acceso", rooms: "Caseta de Vigilancia Norte, Acceso Vehicular hacia Edificios P y O." }
            ]
        },
        "northeastGate": {
            id: "northeastGate",
            letter: "ACC",
            name: "Acceso Noreste (Deportes)",
            badgeClass: "badge-navy",
            badgeBg: "#64748b",
            anchor: { x: 700, y: 45 },
            floors: [
                { floor: "Acceso", rooms: "Portón de Ingreso a Complejo Deportivo y Parqueo de Deportes." }
            ]
        }
    };

    let activeSelectedBuilding = null;

    // ----------------------------------------------------------------------------
    // 3. Pan & Zoom Canvas Controller
    // ----------------------------------------------------------------------------
    let scale = 1;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;

    function applyTransform() {
        svg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    if (btnZoomIn) {
        btnZoomIn.addEventListener("click", () => {
            scale = Math.min(scale + 0.25, 2.5);
            applyTransform();
        });
    }

    if (btnZoomOut) {
        btnZoomOut.addEventListener("click", () => {
            scale = Math.max(scale - 0.25, 0.75);
            applyTransform();
        });
    }

    if (btnResetView) {
        btnResetView.addEventListener("click", () => {
            scale = 1;
            translateX = 0;
            translateY = 0;
            applyTransform();
        });
    }

    // Mouse wheel zoom
    wrapper.addEventListener("wheel", (e) => {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.15 : -0.15;
        scale = Math.max(0.75, Math.min(scale + delta, 2.8));
        applyTransform();
    }, { passive: false });

    // Drag-to-pan handlers
    wrapper.addEventListener("mousedown", (e) => {
        if (e.target.closest("#bldgPopover") || e.target.closest("button")) return;
        isDragging = true;
        dragStartX = e.clientX - translateX;
        dragStartY = e.clientY - translateY;
        wrapper.classList.add("cursor-grabbing");
    });

    window.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        translateX = e.clientX - dragStartX;
        translateY = e.clientY - dragStartY;
        applyTransform();
    });

    window.addEventListener("mouseup", () => {
        if (isDragging) {
            isDragging = false;
            wrapper.classList.remove("cursor-grabbing");
        }
    });

    // Touch support for mobile pan
    let touchStartX = 0;
    let touchStartY = 0;
    wrapper.addEventListener("touchstart", (e) => {
        if (e.touches.length === 1 && !e.target.closest("#bldgPopover")) {
            isDragging = true;
            touchStartX = e.touches[0].clientX - translateX;
            touchStartY = e.touches[0].clientY - translateY;
        }
    }, { passive: true });

    wrapper.addEventListener("touchmove", (e) => {
        if (isDragging && e.touches.length === 1) {
            translateX = e.touches[0].clientX - touchStartX;
            translateY = e.touches[0].clientY - touchStartY;
            applyTransform();
        }
    }, { passive: true });

    wrapper.addEventListener("touchend", () => {
        isDragging = false;
    });

    // ----------------------------------------------------------------------------
    // 4. Interactive Popover & Building Highlight Logic
    // ----------------------------------------------------------------------------
    function showBuildingPopover(bldgData, anchorCoords) {
        activeSelectedBuilding = bldgData;
        if (!bldgPopover) return;

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
                <div class="border-b border-slate-100 pb-1.5 last:border-0">
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
                c.scrollIntoView({ behavior: "smooth", block: "nearest" });
            } else {
                c.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/40");
            }
        });

        // Position popover relative to SVG bounding box (1024 x 764 canvas)
        const rect = svg.getBoundingClientRect();
        const clientX = (anchorCoords.x / 1024) * rect.width;
        const clientY = (anchorCoords.y / 764) * rect.height;

        const maxLeft = rect.width - 310;
        const maxTop = rect.height - 230;

        bldgPopover.style.left = `${Math.max(12, Math.min(clientX - 100, maxLeft))}px`;
        bldgPopover.style.top = `${Math.max(12, Math.min(clientY - 160, maxTop))}px`;
        bldgPopover.classList.remove("hidden");
    }

    if (btnClosePopover) {
        btnClosePopover.addEventListener("click", () => {
            bldgPopover.classList.add("hidden");
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
            const originInput = document.getElementById("originInput");
            if (originInput) {
                originInput.value = activeSelectedBuilding.name;
                originInput.dispatchEvent(new Event("input"));
            }
            bldgPopover.classList.add("hidden");
            if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
            }
        });
    }

    if (btnSetDest) {
        btnSetDest.addEventListener("click", () => {
            if (!activeSelectedBuilding) return;
            const destInput = document.getElementById("destinationInput");
            if (destInput) {
                destInput.value = activeSelectedBuilding.name;
                destInput.dispatchEvent(new Event("input"));
            }
            bldgPopover.classList.add("hidden");
            if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
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
                showBuildingPopover(bldgData, bldgData.anchor);
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
                // Focus / Pan smoothly toward building
                const centerTargetX = (512 - bldgData.anchor.x) * 0.45;
                const centerTargetY = (382 - bldgData.anchor.y) * 0.45;
                translateX = centerTargetX;
                translateY = centerTargetY;
                scale = 1.35;
                applyTransform();

                showBuildingPopover(bldgData, bldgData.anchor);
            }
        });
    });

    if (dirSearchInput) {
        dirSearchInput.addEventListener("input", () => {
            const q = dirSearchInput.value.toLowerCase().trim();
            const cards = document.querySelectorAll(".directory-card");
            let visibleCount = 0;

            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (!q || text.includes(q)) {
                    card.style.display = "block";
                    visibleCount++;
                } else {
                    card.style.display = "none";
                }
            });

            if (dirCountBadge) {
                dirCountBadge.textContent = `${visibleCount} Edificios`;
            }
        });
    }

    // ----------------------------------------------------------------------------
    // 6. Global Dijkstra Route Visualization
    // ----------------------------------------------------------------------------
    window.addEventListener("jaguarMapRouteCalculated", function (e) {
        const route = e.detail;
        if (!route || !route.pathCoordinates || route.pathCoordinates.length < 2) return;

        // Resolve exact points on the 1024x764 official SVG canvas
        const points = route.pathCoordinates.map(coord => {
            const known = CAMPUS_BUILDINGS[coord.nodeId];
            if (known && known.anchor) {
                return `${known.anchor.x},${known.anchor.y}`;
            }
            // Fallback percentage to 1024x764
            const x = Math.round(((coord.xPercent || 50) / 100) * 1024);
            const y = Math.round(((coord.yPercent || 50) / 100) * 764);
            return `${x},${y}`;
        }).join(" ");

        if (routePolyline) routePolyline.setAttribute("points", points);
        if (routeGlowPolyline) routeGlowPolyline.setAttribute("points", points);

        // Draw Origin Pin (Green Ring Beacon Wave & Pulse)
        const startCoord = route.pathCoordinates[0];
        const startKnown = CAMPUS_BUILDINGS[startCoord.nodeId];
        const startX = startKnown ? startKnown.anchor.x : Math.round(((startCoord.xPercent || 50) / 100) * 1024);
        const startY = startKnown ? startKnown.anchor.y : Math.round(((startCoord.yPercent || 50) / 100) * 764);

        if (originPinGroup) {
            originPinGroup.innerHTML = `
                <circle cx="${startX}" cy="${startY}" r="18" fill="#10b981" opacity="0.35" class="beacon-origin-wave" />
                <circle cx="${startX}" cy="${startY}" r="9" fill="#10b981" stroke="#ffffff" stroke-width="2.5" filter="url(#bldgShadow)" />
                <circle cx="${startX}" cy="${startY}" r="3.5" fill="#ffffff" />
            `;
            originPinGroup.classList.remove("hidden");
        }

        // Draw Destination Pin (Clean SVG Flag Pin with Drop Wave)
        const endCoord = route.pathCoordinates[route.pathCoordinates.length - 1];
        const endKnown = CAMPUS_BUILDINGS[endCoord.nodeId];
        const endX = endKnown ? endKnown.anchor.x : Math.round(((endCoord.xPercent || 50) / 100) * 1024);
        const endY = endKnown ? endKnown.anchor.y : Math.round(((endCoord.yPercent || 50) / 100) * 764);

        if (destPinGroup) {
            destPinGroup.innerHTML = `
                <circle cx="${endX}" cy="${endY}" r="18" fill="#ef4444" opacity="0.3" class="beacon-origin-wave" />
                <circle cx="${endX}" cy="${endY}" r="9" fill="#ef4444" stroke="#ffffff" stroke-width="2.5" filter="url(#bldgShadow)" />
                <g class="flag-destination-drop">
                    <path d="M ${endX - 3} ${endY - 28} v 16 M ${endX - 3} ${endY - 28} l 13 6 l -13 6 z" fill="#ef4444" stroke="#ffffff" stroke-width="1.8" stroke-linejoin="round" filter="url(#pinShadow)"/>
                </g>
            `;
            destPinGroup.classList.remove("hidden");
        }

        // Automatically center canvas between origin and destination
        const midX = (startX + endX) / 2;
        const midY = (startY + endY) / 2;
        translateX = (512 - midX) * 0.5;
        translateY = (382 - midY) * 0.5;
        scale = 1.15;
        applyTransform();
    });

    window.addEventListener("jaguarMapRouteCleared", function () {
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
