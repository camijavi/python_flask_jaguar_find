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
    // 2. Official Campus Building Metadata & Directory Details
    // ----------------------------------------------------------------------------
    const CAMPUS_BUILDINGS = {
        "buildingA": {
            id: "buildingA",
            letter: "A",
            name: "Edificio A • Atención al Estudiante",
            badgeClass: "badge-maroon",
            badgeBg: "#991b1b",
            anchor: { x: 250, y: 455 },
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
            badgeBg: "#581c87",
            anchor: { x: 384, y: 500 },
            floors: [
                { floor: "Piso 1", rooms: "Módulo Comercial 1, Aulas B101 - B109, SS Hombres / Mujeres, Jaguar Shop." },
                { floor: "Piso 2", rooms: "Aulas B201 - B210." }
            ]
        },
        "buildingC": {
            id: "buildingC",
            letter: "C",
            name: "Edificio C • Cómputo & Caja UAM",
            badgeClass: "badge-purple",
            badgeBg: "#4c1d95",
            anchor: { x: 384, y: 410 },
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
            anchor: { x: 351, y: 290 },
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
            anchor: { x: 458, y: 653 },
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
            anchor: { x: 545, y: 646 },
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
            anchor: { x: 545, y: 590 },
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
            anchor: { x: 602, y: 383 },
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
            anchor: { x: 653, y: 724 },
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
            anchor: { x: 297, y: 287 },
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
            anchor: { x: 293, y: 598 },
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
            anchor: { x: 597, y: 460 },
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
            anchor: { x: 350, y: 217 },
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
            anchor: { x: 274, y: 766 },
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
            anchor: { x: 225, y: 287 },
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
            name: "Jaguar Center (Complejo Deportivo)",
            badgeClass: "badge-amber",
            badgeBg: "#b45309",
            anchor: { x: 886, y: 623 },
            floors: [
                { floor: "Piso 1", rooms: "Canchas Techadas de Baloncesto / Voleibol, Graderías Principales, Acceso al Complejo Deportivo." }
            ]
        },
        "jaguarGym": {
            id: "jaguarGym",
            letter: "JG",
            name: "Jaguar Gym • Gimnasio Universitario",
            badgeClass: "badge-teal",
            badgeBg: "#0f766e",
            anchor: { x: 955, y: 726 },
            floors: [
                { floor: "Piso 1", rooms: "Área de Pesas, Máquinas Cardiovasculares, Entrenamiento Funcional y Vestidores." }
            ]
        },
        "physiotherapy": {
            id: "physiotherapy",
            letter: "FT",
            name: "Fisioterapia • Clínica de Rehabilitación",
            badgeClass: "badge-cyan",
            badgeBg: "#0284c7",
            anchor: { x: 964, y: 677 },
            floors: [
                { floor: "Piso 1", rooms: "Clínica de Fisioterapia, Rehabilitación Física y Deportiva, Atención a Estudiantes y Atletas." }
            ]
        },
        "jaguarJungle": {
            id: "jaguarJungle",
            letter: "JJ",
            name: "Jaguar Jungle • Jardín & Conexión Central",
            badgeClass: "badge-green",
            badgeBg: "#15803d",
            anchor: { x: 626, y: 306 },
            floors: [
                { floor: "Área Verde & Senderos", rooms: "Zona recreativa natural con senderos peatonales que conectan Edificio O, Mi Ranchito, Lab Digital FIA, Edificio H y la Avenida Principal Interna." }
            ]
        },
        "miRanchito": {
            id: "miRanchito",
            letter: "MR",
            name: "Mi Ranchito • Ranchón Universitario",
            badgeClass: "badge-amber",
            badgeBg: "#b45309",
            anchor: { x: 555, y: 296 },
            floors: [
                { floor: "Pabellón Exterior", rooms: "Ranchón de descanso, cafetería y punto de encuentro estudiantil entre Edificio N, Edificio O y Jaguar Jungle." }
            ]
        },
        "labDigitalFia": {
            id: "labDigitalFia",
            letter: "FIA",
            name: "Lab Digital FIA • Laboratorio Digital",
            badgeClass: "badge-teal",
            badgeBg: "#0f766e",
            anchor: { x: 530, y: 328 },
            floors: [
                { floor: "Piso 1", rooms: "Laboratorio Digital de la Facultad de Ingeniería y Arquitectura (FIA), junto al Edificio N, Mi Ranchito y Área de Mesas." }
            ]
        },
        "areaDeMesas": {
            id: "areaDeMesas",
            letter: "AM",
            name: "Área de Mesas • Terraza de Estudio",
            badgeClass: "badge-navy",
            badgeBg: "#1e3a8a",
            anchor: { x: 532, y: 366 },
            floors: [
                { floor: "Terraza Exterior", rooms: "Mesas techadas y sombreadas para estudio, trabajo grupal y almuerzo entre Lab Digital FIA, Parqueo Central y Edificio C." }
            ]
        },
        "northGate": {
            id: "northGate",
            letter: "3°",
            name: "Tercer Acceso • Third Access (Copérnico)",
            badgeClass: "badge-navy",
            badgeBg: "#475569",
            anchor: { x: 184, y: 74 },
            floors: [
                { floor: "Acceso Vehicular y Peatonal", rooms: "Tercer Acceso (Caseta Oeste junto a Estación Meteorológica y Edificio P - Copérnico). Conecta directamente con la Avenida Principal Oeste y Parqueos Oeste." }
            ]
        },
        "northeastGate": {
            id: "northeastGate",
            letter: "2°",
            name: "Segundo Acceso • Camino Estadio Jaguar",
            badgeClass: "badge-navy",
            badgeBg: "#0f766e",
            anchor: { x: 906, y: 14 },
            floors: [
                { floor: "Acceso Vehicular y Peatonal", rooms: "Camino Segundo Acceso (Vía Estadio de Béisbol Jaguar). Conecta directamente con el Complejo Deportivo, Parqueo Norte Deportes, Edificio O y vía perimetral norte." }
            ]
        }
    };

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
            const originInput = document.getElementById("originInput");
            if (originInput) {
                originInput.value = activeSelectedBuilding.name;
                originInput.dispatchEvent(new Event("input"));
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
            const destInput = document.getElementById("destinationInput");
            if (destInput) {
                destInput.value = activeSelectedBuilding.name;
                destInput.dispatchEvent(new Event("input"));
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
            if (resolvedPts.length < 2) {
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
