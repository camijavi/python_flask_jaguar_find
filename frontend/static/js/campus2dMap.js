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
    // 2. Official Campus Building Metadata & Directory Details
    // ----------------------------------------------------------------------------
    const CAMPUS_BUILDINGS = {
        "buildingA": {
            id: "buildingA",
            letter: "A",
            name: "Edificio A • Atención al Estudiante",
            badgeClass: "badge-purple",
            badgeBg: "#6b21a8",
            anchor: { x: 252, y: 459 },
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
            badgeBg: "#6b21a8",
            anchor: { x: 390, y: 490 },
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
            anchor: { x: 390, y: 427 },
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
            anchor: { x: 351, y: 335 },
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
            anchor: { x: 458, y: 620 },
            floors: [
                { floor: "Piso 1", rooms: "Clínica Médica & Atención al Adolescente, SS Hombres / Mujeres, Centro de Diagnóstico, Decanatura de Medicina, Oficinas de Médicos Especialistas." }
            ]
        },
        "buildingF": {
            id: "buildingF",
            letter: "F",
            name: "Edificio F • FACEE (Ciencias Económicas)",
            badgeClass: "badge-magenta",
            badgeBg: "#be185d",
            anchor: { x: 517, y: 628 },
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
            anchor: { x: 517, y: 558 },
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
            anchor: { x: 572, y: 383 },
            floors: [
                { floor: "Piso 1", rooms: "SS Hombres / Mujeres, Laboratorios Multidisciplinarios H101-H103, Coordinación de Laboratorios, Oficina de Sustancias Químicas, Laboratorios H105-H107." },
                { floor: "Piso 2", rooms: "Laboratorio de Anatomía H201-H207, Quirófano de Práctica, Depósito de Reactivos." }
            ]
        },
        "buildingI": {
            id: "buildingI",
            letter: "I",
            name: "Edificio I • Rectoría & Biblioteca Central",
            badgeClass: "badge-navy",
            badgeBg: "#1e3a8a",
            anchor: { x: 635, y: 715 },
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
            anchor: { x: 297, y: 332 },
            floors: [
                { floor: "Piso 1", rooms: "Laboratorio de Simulación y Práctica Preclínica Odontológica J101-J102, Depósito de Instrumental, SS Hombres / Mujeres." }
            ]
        },
        "buildingK": {
            id: "buildingK",
            letter: "K",
            name: "Edificio K • Cafetería Central & Terrazas",
            badgeClass: "badge-amber",
            badgeBg: "#b45309",
            anchor: { x: 285, y: 582 },
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
            anchor: { x: 842, y: 502 },
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
            anchor: { x: 567, y: 460 },
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
            anchor: { x: 350, y: 262 },
            floors: [
                { floor: "Piso 1", rooms: "Recepción de Pacientes, Módulo de Triaje, Clínicas Odontológicas Integrales, Quirófano Ambulatorio, Central de Esterilización." }
            ]
        },
        "buildingO": {
            id: "buildingO",
            letter: "O",
            name: "Edificio O • Facultad de Ingeniería (FIA)",
            badgeClass: "badge-amber",
            badgeBg: "#b45309",
            anchor: { x: 510, y: 200 },
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
            badgeBg: "#881337",
            anchor: { x: 360, y: 104 },
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
            anchor: { x: 340, y: 800 },
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
            anchor: { x: 225, y: 332 },
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
            anchor: { x: 762, y: 357 },
            floors: [
                { floor: "Campo Abierto", rooms: "Estadio Oficial de Béisbol con Diamante de Tierra, Cancha de Fútbol Reglamentaria de Grama, Pista y Acceso a Camerinos." }
            ]
        },
        "jaguarCenter": {
            id: "jaguarCenter",
            letter: "JC",
            name: "Jaguar Center (Gimnasio & Complejo Deportivo)",
            badgeClass: "badge-amber",
            badgeBg: "#b45309",
            anchor: { x: 735, y: 510 },
            floors: [
                { floor: "Piso 1", rooms: "Gimnasio Universitario Jaguar Gym, Canchas Techadas de Baloncesto / Voleibol, Graderías Principales, Área de Fisioterapia." }
            ]
        },
        "northGate": {
            id: "northGate",
            letter: "ACC",
            name: "Acceso Norte (Copérnico / FIA)",
            badgeClass: "badge-navy",
            badgeBg: "#64748b",
            anchor: { x: 340, y: 60 },
            floors: [
                { floor: "Acceso", rooms: "Caseta de Vigilancia Norte, Acceso Vehicular Segundo Camino hacia Edificios P y O." }
            ]
        },
        "northeastGate": {
            id: "northeastGate",
            letter: "ACC",
            name: "Acceso Noreste (Deportes)",
            badgeClass: "badge-navy",
            badgeBg: "#64748b",
            anchor: { x: 720, y: 60 },
            floors: [
                { floor: "Acceso", rooms: "Portón de Ingreso a Complejo Deportivo y Parqueo de Deportes." }
            ]
        }
    };

    let activeSelectedBuilding = null;

    // ----------------------------------------------------------------------------
    // 3. Pan, Zoom & Real Responsive Compass Canvas Controller
    // ----------------------------------------------------------------------------
    let scale = 1;
    let translateX = 0;
    let translateY = 0;
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

    // Expose global helper so 2.5D perspective and route animations can also sync the compass
    window.updateCampusCompass = updateCompass;

    function applyTransform(animate = false) {
        if (window.campus25dController && window.campus25dController.is25dActive) {
            svg.style.transform = "none";
            const c25d = window.campus25dController;
            const headingDeg = c25d.isHeadingUp ? -(c25d.currentHeading || 0) : 0;
            updateCompass(headingDeg, animate);
            return;
        }

        svg.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
        svg.style.transformOrigin = "600px 425px";
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
            scale = Math.min(scale + 0.25, 2.8);
            applyTransform(true);
        });
    }

    if (btnZoomOut) {
        btnZoomOut.addEventListener("click", () => {
            if (window.campus25dController && window.campus25dController.is25dActive) {
                window.campus25dController.zoomOut();
                return;
            }
            scale = Math.max(scale - 0.25, 0.75);
            applyTransform(true);
        });
    }

    if (btnResetView) {
        btnResetView.addEventListener("click", () => {
            if (window.campus25dController && window.campus25dController.is25dActive) {
                window.campus25dController.zoomScale = 2.2;
                window.campus25dController.heading = 0;
                window.campus25dController.currentHeading = 0;
                window.campus25dController.centerOnCampusLowerThird();
                window.campus25dController.updateCompass(true);
                return;
            }
            scale = 1;
            translateX = 0;
            translateY = 0;
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
                    window.campus25dController.heading = -angleDeg;
                    window.campus25dController.currentHeading = -angleDeg;
                    window.campus25dController.applyTransform();
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
        if (e.target.closest("#bldgPopover") || e.target.closest("button") || e.target.closest("#campusCompass")) return;

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
        if (e.target.closest("#bldgPopover") || e.target.closest("button") || e.target.closest("#campusCompass")) return;

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
                scale = Math.max(0.75, Math.min(initialPinchScale * (currentDist / initialPinchDist), 2.8));
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
                <div class="border-b border-slate-100 pb-1 last:border-0">
                    <span class="font-bold text-slate-800">${f.floor}:</span>
                    <span class="text-slate-600">${f.rooms}</span>
                </div>
            `).join("");

            if (bldgData.id === "buildingP") {
                popoverFacilities.innerHTML += `
                    <div class="mt-2.5 pt-2 border-t border-slate-100">
                        <button type="button" onclick="if(typeof window.openBuildingPIsometricModal==='function') window.openBuildingPIsometricModal();" class="w-full py-1.5 px-2 bg-pink-800 hover:bg-pink-900 text-white rounded-lg font-bold text-[11px] shadow-sm flex items-center justify-center gap-1.5 transition-colors">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                            <span>Ver Vista Isométrica 3D</span>
                        </button>
                    </div>
                `;
            }
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

        const maxLeft = wRect.width - 290;
        const maxTop = wRect.height - 220;

        bldgPopover.style.left = `${Math.max(12, Math.min(clientX - 100, maxLeft))}px`;
        bldgPopover.style.top = `${Math.max(12, Math.min(clientY - 170, maxTop))}px`;
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
            const originInput = document.getElementById("originInput");
            if (originInput) {
                originInput.value = activeSelectedBuilding.name;
                originInput.dispatchEvent(new Event("input"));
            }
            if (window.innerWidth < 1024 && typeof window.openMobileBottomSheet === "function") {
                window.openMobileBottomSheet();
            } else if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
            }
            bldgPopover.classList.add("hidden");
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
            if (window.innerWidth < 1024 && typeof window.openMobileBottomSheet === "function") {
                window.openMobileBottomSheet();
            } else if (typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(true);
            }
            bldgPopover.classList.add("hidden");
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

        // Resolve exact points on the 1200x850 official SVG canvas
        const points = route.pathCoordinates.map(coord => {
            const known = CAMPUS_BUILDINGS[coord.nodeId];
            if (known && known.anchor) {
                return `${known.anchor.x},${known.anchor.y}`;
            }
            // Fallback percentage to 1200x850
            const x = Math.round(((coord.xPercent || 50) / 100) * 1200);
            const y = Math.round(((coord.yPercent || 50) / 100) * 850);
            return `${x},${y}`;
        }).join(" ");

        if (routeShadowPolyline) routeShadowPolyline.setAttribute("points", points);
        if (routePolyline) routePolyline.setAttribute("points", points);
        if (routeGlowPolyline) routeGlowPolyline.setAttribute("points", points);

        // Draw Origin Pin (Ground Shadow + Upright 3D Billboard Pin)
        const startCoord = route.pathCoordinates[0];
        const startKnown = CAMPUS_BUILDINGS[startCoord.nodeId];
        const startX = startKnown ? startKnown.anchor.x : Math.round(((startCoord.xPercent || 50) / 100) * 1200);
        const startY = startKnown ? startKnown.anchor.y : Math.round(((startCoord.yPercent || 50) / 100) * 850);

        if (originPinGroup) {
            originPinGroup.innerHTML = `
                <!-- Ground Contact Shadow -->
                <ellipse cx="${startX}" cy="${startY + 2}" rx="13" ry="6" fill="#0f172a" opacity="0.4" />
                <circle cx="${startX}" cy="${startY}" r="14" fill="#10b981" opacity="0.25" class="animate-ping" />
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
        const endCoord = route.pathCoordinates[route.pathCoordinates.length - 1];
        const endKnown = CAMPUS_BUILDINGS[endCoord.nodeId];
        const endX = endKnown ? endKnown.anchor.x : Math.round(((endCoord.xPercent || 50) / 100) * 1200);
        const endY = endKnown ? endKnown.anchor.y : Math.round(((endCoord.yPercent || 50) / 100) * 850);

        if (destPinGroup) {
            destPinGroup.innerHTML = `
                <!-- Ground Contact Shadow -->
                <ellipse cx="${endX}" cy="${endY + 2}" rx="14" ry="7" fill="#0f172a" opacity="0.45" />
                <circle cx="${endX}" cy="${endY}" r="16" fill="#ef4444" opacity="0.25" class="animate-ping" />
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
