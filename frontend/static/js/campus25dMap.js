/**
 * ================================================================================
 * CAMPUS25DMAP.JS - WAZE-STYLE 2.5D PERSPECTIVE NAVIGATION ENGINE
 * ================================================================================
 * Transforms the flat 2D UAM campus map into an authentic Waze-style navigation view:
 * 1. Infinite Ground Bleed: Ground color #f3f5f8 and atmospheric fog eliminate horizon seams.
 * 2. Decoupled Upright HTML Overlays: 3D blue navigation puck, building badges, and pins
 *    float flat and upright in screen space—never distorted into trapezoids.
 * 3. Layered 3D Building Extrusions: Zero-blur drop shadows create 6px physical depth walls.
 * 4. Waze Cockpit Framing: Top turn-by-turn banner, bottom trip summary bar (ETA, meters,
 *    re-center, overview), and camera locked at 70% lower-third user anchor.
 * ================================================================================
 */

(function () {
    class Campus25dController {
        constructor() {
            // Waze-Style Navigation State
            this.is25dActive = false;
            this.pitch = 45; // Crisp 45° default (52° selectable via pill)
            this.heading = 0; // Rotation around Z axis (degrees)
            this.isHeadingUp = true;
            this.zoomScale = 2.2; // Mathematical close zoom so canvas edges bleed off-screen
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.isSimulating = false;
            this.simInterval = null;
            this.isOverview = false;
            this.focusedBuildingId = null;
            this.focusedBuildingAnchor = null;
            this.targetZoomScale = undefined;

            // Camera Vector Animation State (camera look-at point in SVG space)
            this.cameraGroup = document.getElementById("mapCameraGroup");
            this.currentUserX = undefined;
            this.currentUserY = undefined;
            this.currentHeading = 0;
            this.targetUserX = 400;
            this.targetUserY = 500;
            this.targetHeading = 0;
            this.tweenAnimId = null;

            // Decoupled User Navigation Arrow State (true user position on map, independent of camera pan/overview)
            this.userSvgX = 400;
            this.userSvgY = 500;
            this.userSvgHeading = 0;
            this.hasUserPosition = false;
            this.isFollowingUser = true;
            this.userAnimId = null;
            this.simAnimId = null;
            this.simLastTimestamp = 0;

            // Active Route Polyline & Continuous Progress State
            this.activeRoutePolyline = [];
            this.totalRoutePx = 0;
            this.totalRouteMeters = 0;
            this.stepSpans = [];
            this.routeProgressDistPx = 0;
            this.routeProgressRatio = 0;
            this.routeUsedGpsOrigin = false;
            this.hasGpsLockOnRoute = false;

            // DOM References
            this.viewport = document.getElementById("campus25dViewport");
            this.stage = document.getElementById("campusMapWrapper");
            this.svg = document.getElementById("officialCampus2dSvg");
            this.horizon = document.getElementById("campusHorizonAtmosphere");
            this.compassRose = document.getElementById("compassRose");
            this.user2dArrowLayer = document.getElementById("user2dArrowLayer");
            this.user2dArrowGroup = document.getElementById("user2dArrowGroup");
            this.user2dArrowRotator = document.getElementById("user2dArrowRotator");

            // Decoupled HTML Overlays Layer
            this.overlayLayer = document.getElementById("campus25dOverlayLayer");
            this.puckContainer = document.getElementById("wazeNavigationPuck");
            this.puckArrow = document.getElementById("wazePuckArrow");
            this.puckCone = document.getElementById("wazePuckCone");
            this.badgesContainer = document.getElementById("wazeBadgesContainer");
            this.wazeOriginPin = document.getElementById("wazeOriginPin");
            this.wazeDestPin = document.getElementById("wazeDestPin");

            // 2.5D HUD Elements
            this.btnMode2d = document.getElementById("btnMode2d");
            this.btnMode25d = document.getElementById("btnMode25d");
            this.pitchGroup = document.getElementById("pitchControlGroup");
            this.btnPitch45 = document.getElementById("btnPitch45");
            this.btnPitch52 = document.getElementById("btnPitch52") || document.getElementById("btnPitch60");
            this.headingGroup = document.getElementById("headingControlGroup");
            this.btnToggleHeadingUp = document.getElementById("btnToggleHeadingUp");
            this.iconHeadingMode = document.getElementById("iconHeadingMode");
            this.liveCompassGroup = document.getElementById("liveCompassControlGroup");
            this.btnLiveCompass = document.getElementById("btnLiveCompass");
            this.liveCompassDot = document.getElementById("liveCompassDot");
            this.labelLiveCompass = document.getElementById("labelLiveCompass");
            this.btnTbtLiveGps = document.getElementById("btnTbtLiveGps");
            this.tbtLiveGpsDot = document.getElementById("tbtLiveGpsDot");
            this.labelTbtLiveGps = document.getElementById("labelTbtLiveGps");
            this.parkingGroup = document.getElementById("parkingControlGroup");
            this.btnToggleParking = document.getElementById("btnToggleParkingHighlight");
            this.isParkingHighlighted = false;

            // Continuous Live GPS + Optional Phone Compass State
            this.isLiveGpsActive = false;
            this.isLiveCompassActive = false;
            this.gpsStatus = "idle"; // "idle" | "searching" | "tracking" | "outside" | "denied" | "unsupported"
            this.gpsWatchId = null;
            this.smoothedCompassDeg = null;
            this.latestCompassDeg = null;
            this.latestGpsCoords = null;
            this.lastGpsAnchor = null;
            this.initialGpsOnRoute = null;
            this._boundOrientationHandler = (ev) => this.handleDeviceOrientation(ev);
            this._compassRafPending = false;
            // Calibrated UAM GPS <-> SVG Affine Parameters + Campus Perimeter (synced with /api/map/calibration)
            this.calibration = {
                lat0: 12.1085,
                lng0: -86.2573,
                mPerDegLat: 111132.0,
                mPerDegLng: 111320.0 * Math.cos((12.1085 * Math.PI) / 180),
                cx0: 529.03,
                cxN: 0.0778,
                cxE: -3.2168,
                cy0: 441.96,
                cyN: 2.5386,
                cyE: -0.0374,
                mapUpTrueBearingDeg: 181.4,
                avgSvgPxPerMeter: 2.88,
                perimeter: [
                    { lat: 12.109617, lng: -86.259097 },
                    { lat: 12.109665, lng: -86.256455 },
                    { lat: 12.108771, lng: -86.255659 },
                    { lat: 12.107598, lng: -86.255665 },
                    { lat: 12.107639, lng: -86.256172 },
                    { lat: 12.107263, lng: -86.256262 },
                    { lat: 12.106934, lng: -86.256302 },
                    { lat: 12.106324, lng: -86.258762 },
                ],
            };

            // Waze Top Banner Elements
            this.tbtBanner = document.getElementById("turnByTurnBanner");
            this.tbtStepCounter = document.getElementById("tbtStepCounter");
            this.tbtStepDistance = document.getElementById("tbtStepDistance");
            this.tbtStepInstruction = document.getElementById("tbtStepInstruction");
            this.tbtOrientationCue = document.getElementById("tbtOrientationCue");
            this.tbtOrientationCueText = document.getElementById("tbtOrientationCueText");
            this.tbtConfirmRow = document.getElementById("tbtConfirmRow");
            this.btnTbtConfirmStep = document.getElementById("btnTbtConfirmStep");
            this.labelTbtConfirmStep = document.getElementById("labelTbtConfirmStep");
            this.tbtNextPreview = document.getElementById("tbtNextPreview");
            this.tbtManeuverIcon = document.getElementById("tbtManeuverIcon");
            this.btnCloseTbt = document.getElementById("btnCloseTbtBanner");

            // Waze Bottom Trip Summary, Floating Dials & Action Tray Elements
            this.wazeBottomBar = document.getElementById("wazeBottomBar");
            this.wazeBottomCenter = document.getElementById("wazeBottomCenter");
            this.wazeEtaTime = document.getElementById("wazeEtaTime");
            this.wazeTripMeta = document.getElementById("wazeTripMeta");
            this.wazeProgressBar = document.getElementById("wazeProgressBar");
            this.wazeActiveRoadPill = document.getElementById("wazeActiveRoadPill");
            this.wazeSpeedDial = document.getElementById("wazeSpeedDial");
            this.wazeDialValue = document.getElementById("wazeDialValue");
            this.wazeDialUnit = document.getElementById("wazeDialUnit");
            this.wazeOrangeFab = document.getElementById("wazeOrangeFab");
            this.wazeOrangeFabIcon = document.getElementById("wazeOrangeFabIcon");
            this.wazeActionTray = document.getElementById("wazeActionTray");
            this.btnWazeSearch = document.getElementById("btnWazeSearch");
            this.btnWazeAudio = document.getElementById("btnWazeAudio");
            this.btnWazeExpandTray = document.getElementById("btnWazeExpandTray");
            this.wazeExpandChevron = document.getElementById("wazeExpandChevron");
            this.btnWazeOpenSteps = document.getElementById("btnWazeOpenSteps");
            this.btnWazeClearRoute = document.getElementById("btnWazeClearRoute");
            this.btnTbtPrevStep = document.getElementById("btnTbtPrevStep");
            this.btnTbtNextStep = document.getElementById("btnTbtNextStep");
            this.btnWazeRecenter = document.getElementById("btnWazeRecenter");
            this.btnWazeOverview = document.getElementById("btnWazeOverview");
            this.btnTbtPlay = document.getElementById("btnTbtPlaySimulation");
            this.labelSimPlay = document.getElementById("labelSimPlay");
            this.isTrayOpen = false;

            // Map building coordinates lookup (single source of truth from campusMapRenderer.js)
            this.buildingAnchors = window.CAMPUS_BUILDING_ANCHORS || {
                "buildingA": { x: 323, y: 435 },
                "buildingB": { x: 444, y: 459 },
                "buildingC": { x: 444, y: 411 },
                "buildingD": { x: 410, y: 316 },
                "buildingE": { x: 534, y: 580 },
                "buildingF": { x: 604, y: 564 },
                "buildingG": { x: 604, y: 510 },
                "buildingH": { x: 652, y: 369 },
                "buildingI": { x: 776, y: 656 },
                "buildingJ": { x: 361, y: 316 },
                "buildingK": { x: 362, y: 526 },
                "buildingL": { x: 989, y: 612 },
                "buildingM": { x: 626, y: 435 },
                "buildingN": { x: 442, y: 260 },
                "buildingO": { x: 611, y: 196 },
                "buildingP": { x: 456, y: 115 },
                "mainParking": { x: 274, y: 766 },
                "chilamatesPlaza": { x: 294, y: 292 },
                "sportsZone": { x: 938, y: 447 },
                "jaguarCenter": { x: 900, y: 623 },
                "jaguarGym": { x: 969, y: 726 },
                "physiotherapy": { x: 978, y: 677 },
                "jaguarJungle": { x: 626, y: 306 },
                "miRanchito": { x: 555, y: 296 },
                "labDigitalFia": { x: 530, y: 328 },
                "areaDeMesas": { x: 532, y: 366 },
                "northGate": { x: 184, y: 74 },
                "northeastGate": { x: 906, y: 14 }
            };

            this.init();
        }

        init() {
            if (!this.viewport || !this.stage) {
                document.addEventListener("DOMContentLoaded", () => this.init());
                return;
            }

            this.bindEvents();
            this.setupInteractions();
            this.initOverlayBadges();

            // Handle window resize dynamically to preserve lower-third user anchor
            window.addEventListener("resize", () => {
                if (this.is25dActive) {
                    this.applyTransform();
                    this.updateOverlays();
                }
            });
        }

        getBuildingData(nodeId) {
            if (window.CAMPUS_BUILDINGS && window.CAMPUS_BUILDINGS[nodeId]) {
                return window.CAMPUS_BUILDINGS[nodeId];
            }
            if (window.campus2dController && window.campus2dController.buildings && window.campus2dController.buildings[nodeId]) {
                return window.campus2dController.buildings[nodeId];
            }
            const letterMap = {
                "buildingA": "A", "buildingB": "B", "buildingC": "C", "buildingD": "D",
                "buildingE": "E", "buildingF": "F", "buildingG": "G", "buildingH": "H",
                "buildingI": "I", "buildingJ": "J", "buildingK": "K", "buildingL": "L",
                "buildingM": "M", "buildingN": "N", "buildingO": "O", "buildingP": "P",
                "sportsZone": "S", "jaguarCenter": "JC", "jaguarGym": "JG", "physiotherapy": "FT"
            };
            const nameMap = {
                "buildingA": "Edificio A", "buildingB": "Edificio B", "buildingC": "Edificio C",
                "buildingD": "Edificio D", "buildingE": "Edificio E", "buildingF": "Edificio F",
                "buildingG": "Edificio G", "buildingH": "Edificio H", "buildingI": "Edificio I",
                "buildingJ": "Edificio J", "buildingK": "Edificio K", "buildingL": "Edificio L",
                "buildingM": "Edificio M", "buildingN": "Edificio N", "buildingO": "Edificio O",
                "buildingP": "Edificio P", "sportsZone": "Campos Deportivos", "jaguarCenter": "Jaguar Center",
                "jaguarGym": "Jaguar Gym", "physiotherapy": "Fisioterapia"
            };
            const colorMap = {
                "buildingA": "#991b1b", "buildingB": "#581c87", "buildingC": "#4c1d95",
                "buildingD": "#15803d", "buildingE": "#0284c7", "buildingF": "#be185d",
                "buildingG": "#0284c7", "buildingH": "#15803d", "buildingI": "#1e3a8a",
                "buildingJ": "#0284c7", "buildingK": "#b45309", "buildingL": "#0284c7",
                "buildingM": "#b45309", "buildingN": "#6b21a8", "buildingO": "#b45309",
                "buildingP": "#be185d", "sportsZone": "#15803d", "jaguarCenter": "#0f766e",
                "jaguarGym": "#0f766e", "physiotherapy": "#0284c7"
            };
            return {
                id: nodeId,
                letter: letterMap[nodeId] || nodeId.charAt(0).toUpperCase(),
                name: nameMap[nodeId] || nodeId,
                badgeBg: colorMap[nodeId] || "#1e3a8a"
            };
        }

        /**
         * Creates decoupled upright HTML badges in the overlay layer
         */
        initOverlayBadges() {
            if (!this.badgesContainer) return;
            this.badgesContainer.innerHTML = "";

            const fragment = document.createDocumentFragment();
            for (const [nodeId, anchor] of Object.entries(this.buildingAnchors)) {
                const bldgData = this.getBuildingData(nodeId);
                const badgeEl = document.createElement("div");
                const isGate = nodeId === "northGate" || nodeId === "northeastGate";
                badgeEl.className = isGate ? "waze-bldg-badge waze-gate-badge" : "waze-bldg-badge";
                badgeEl.id = `wazeBadge_${nodeId}`;
                badgeEl.style.display = "none";

                const badgeBg = bldgData.badgeBg || "#1e3a8a";
                const letter = bldgData.letter || nodeId.replace("building", "").toUpperCase();
                const rawName = bldgData.name || nodeId;
                const cleanName = rawName.includes("•") ? rawName.split("•")[0].trim() : rawName;

                badgeEl.title = cleanName;
                badgeEl.setAttribute("aria-label", cleanName);

                badgeEl.innerHTML = `
                    <span class="waze-bldg-letter" style="background-color: ${badgeBg}">${letter}</span>
                `;

                badgeEl.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.focusBuilding(nodeId, { zoom: 2.85, animate: true });
                });

                fragment.appendChild(badgeEl);
            }
            this.badgesContainer.appendChild(fragment);

            // Populate Origin & Destination pins
            if (this.wazeOriginPin) {
                this.wazeOriginPin.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-emerald-500/30 flex items-center justify-center animate-ping"></div>
                    <div class="absolute inset-0 m-auto w-5 h-5 rounded-full bg-emerald-500 border-2 border-white shadow-lg flex items-center justify-center">
                        <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
                    </div>
                `;
            }

            if (this.wazeDestPin) {
                this.wazeDestPin.innerHTML = `
                    <div class="flex flex-col items-center">
                        <div class="px-2 py-0.5 rounded-md bg-red-600 text-white font-extrabold text-[10px] shadow-md flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/></svg>
                            <span>Meta</span>
                        </div>
                        <div class="w-1 h-3 bg-red-700 shadow-sm"></div>
                        <div class="w-2.5 h-1 rounded-full bg-slate-900/40"></div>
                    </div>
                `;
            }
        }

        bindEvents() {
            // Mode toggle buttons
            if (this.btnMode2d) {
                this.btnMode2d.addEventListener("click", () => this.setMode(false));
            }
            if (this.btnMode25d) {
                this.btnMode25d.addEventListener("click", () => this.setMode(true));
            }
            const btnQuick = document.getElementById("btnToggle25dQuick");
            if (btnQuick) {
                btnQuick.addEventListener("click", () => this.setMode(!this.is25dActive));
            }

            // Pitch buttons (45° vs 52°)
            if (this.btnPitch45) {
                this.btnPitch45.addEventListener("click", () => this.setPitch(45));
            }
            if (this.btnPitch52) {
                this.btnPitch52.addEventListener("click", () => this.setPitch(52));
            }

            // Heading-Up toggle
            if (this.btnToggleHeadingUp) {
                this.btnToggleHeadingUp.addEventListener("click", () => {
                    this.isHeadingUp = !this.isHeadingUp;
                    this.updateHeadingControls();
                    if (this.isFollowingUser && !this.isOverview) {
                        this.currentHeading = this.isHeadingUp ? (this.userSvgHeading || 0) : 0;
                        this.targetHeading = this.currentHeading;
                    }
                    this.applyTransform();
                    this.updateOverlays();
                    this.update2dUserArrow();
                    this.updateCompass(true);
                });
            }

            // Live Phone Compass + Continuous GPS toggles (top pill & TBT banner pill for mobile/desktop)
            if (this.btnLiveCompass) {
                this.btnLiveCompass.addEventListener("click", () => {
                    this.toggleLiveCompassNavigation();
                });
            }
            if (this.btnTbtLiveGps) {
                this.btnTbtLiveGps.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.toggleLiveCompassNavigation();
                });
            }

            // Human Landmark Confirm ("Ya llegué aquí • Siguiente") button
            if (this.btnTbtConfirmStep) {
                this.btnTbtConfirmStep.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.stopSimulation();
                    this.nextStep();
                });
            }

            // Sync calibrated GPS <-> SVG parameters + campus perimeter from backend
            fetch("/api/map/calibration")
                .then(r => r.json())
                .then(d => {
                    if (d && d.success && d.calibration) {
                        this.calibration = Object.assign({}, this.calibration, d.calibration);
                    }
                })
                .catch(() => {});

            // Snap blue puck immediately when user taps "Obtener vía GPS" in sidebar and begin live tracking
            window.addEventListener("jaguarGpsLocationUpdated", (e) => {
                const info = e.detail || {};
                if (typeof info.lat === "number" && typeof info.lng === "number") {
                    this.latestGpsCoords = {
                        lat: info.lat,
                        lng: info.lng,
                        accuracy: info.accuracy || 15,
                        timestamp: Date.now(),
                    };
                }
                if (info.userSvgPosition && typeof info.userSvgPosition.x === "number") {
                    this.userSvgX = info.userSvgPosition.x;
                    this.userSvgY = info.userSvgPosition.y;
                    this.hasUserPosition = true;
                    this.isFollowingUser = true;
                    this.isOverview = false;
                    this.update2dUserArrow();

                    if (this.is25dActive) {
                        this.anchorToLowerThird(this.userSvgX, this.userSvgY, this.userSvgHeading || 0, true);
                    } else if (typeof window.campus2dCenterOnPoint === "function") {
                        window.campus2dCenterOnPoint(this.userSvgX, this.userSvgY);
                    }
                }
                this.startLiveGpsTracking({ auto: true });
            });

            // Parking Lots highlight toggle
            if (this.btnToggleParking) {
                this.btnToggleParking.addEventListener("click", () => {
                    this.toggleParkingHighlight();
                });
            }

            // Waze Re-center button (re-engages user follow mode & anchors camera back to live user arrow)
            if (this.btnWazeRecenter) {
                this.btnWazeRecenter.addEventListener("click", () => {
                    this.recenterOnUser();
                });
            }

            // Waze Overview button (toggles follow mode vs full campus overview while keeping user arrow at true position)
            if (this.btnWazeOverview) {
                this.btnWazeOverview.addEventListener("click", () => {
                    this.isOverview = !this.isOverview;
                    if (this.isOverview) {
                        this.isFollowingUser = false;
                        this.pitch = 35;
                        this.updatePitchControls(this.pitch);
                        this.targetZoomScale = this.getResponsiveZoom(1.15);
                        this.anchorToLowerThird(500, 430, 0, true);
                    } else {
                        this.recenterOnUser();
                    }
                });
            }

            // Step Prev / Next buttons
            if (this.btnTbtPrevStep) {
                this.btnTbtPrevStep.addEventListener("click", () => {
                    this.stopSimulation();
                    this.prevStep();
                });
            }
            if (this.btnTbtNextStep) {
                this.btnTbtNextStep.addEventListener("click", () => {
                    this.stopSimulation();
                    this.nextStep();
                });
            }

            // Simulation player button
            if (this.btnTbtPlay) {
                this.btnTbtPlay.addEventListener("click", () => this.toggleSimulation());
            }

            // Close banner button
            if (this.btnCloseTbt) {
                this.btnCloseTbt.addEventListener("click", () => this.hideNavigationBanner());
            }

            // Unified Waze Bottom Dock & Floating Circular Widgets
            const openPlanner = () => {
                if (window.innerWidth < 1024) {
                    if (typeof window.openMobileBottomSheet === "function") {
                        window.openMobileBottomSheet();
                    }
                } else {
                    if (typeof window.toggleNavigateMapSidebar === "function") {
                        window.toggleNavigateMapSidebar(true);
                    }
                    const tabNav = document.getElementById("sidebarTabNav");
                    if (tabNav) tabNav.click();
                    const destInput = document.getElementById("destinationInput");
                    if (destInput) setTimeout(() => destInput.focus(), 120);
                }
            };

            if (this.btnWazeSearch) {
                this.btnWazeSearch.addEventListener("click", openPlanner);
            }

            if (this.wazeBottomCenter) {
                this.wazeBottomCenter.addEventListener("click", () => {
                    if (this.currentRoute) {
                        this.toggleActionTray();
                    } else {
                        openPlanner();
                    }
                });
            }

            if (this.btnWazeExpandTray) {
                this.btnWazeExpandTray.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.toggleActionTray();
                });
            }

            if (this.btnWazeAudio) {
                this.btnWazeAudio.addEventListener("click", () => {
                    const voiceBtn = document.getElementById("btnVoiceDirections");
                    if (voiceBtn) voiceBtn.click();
                });
            }

            if (this.btnWazeOpenSteps) {
                this.btnWazeOpenSteps.addEventListener("click", () => {
                    this.toggleActionTray(false);
                    if (typeof window.toggleMobileStepsCard === "function") {
                        window.toggleMobileStepsCard();
                    }
                });
            }

            if (this.btnWazeClearRoute) {
                this.btnWazeClearRoute.addEventListener("click", () => {
                    this.toggleActionTray(false);
                    const clearBtn = document.getElementById("btnCloseMobileRoute") || document.getElementById("btnResetNavigation");
                    if (clearBtn) {
                        clearBtn.click();
                    } else {
                        this.onRouteCleared();
                    }
                });
            }

            if (this.wazeSpeedDial) {
                this.wazeSpeedDial.addEventListener("click", () => {
                    this.setMode(!this.is25dActive);
                });
            }

            if (this.wazeOrangeFab) {
                this.wazeOrangeFab.addEventListener("click", () => {
                    if (this.currentRoute) {
                        this.isOverview = false;
                        if (!this.is25dActive) {
                            this.setMode(true, { pitch: 52, zoom: this.getResponsiveZoom(2.4), skipDefaultCenter: true });
                        }
                        this.showNavigationBanner();
                        this.recenterOnUser();
                    } else {
                        openPlanner();
                    }
                });
            }

            // Initialize Waze dial & dock defaults
            this.syncWazeChrome();

            // Global route events from navigateMap.html
            window.addEventListener("jaguarMapRouteCalculated", (e) => {
                this.onRouteCalculated(e.detail);
            });

            window.addEventListener("jaguarMapRouteCleared", () => {
                this.onRouteCleared();
            });

            // Keyboard Shortcuts
            window.addEventListener("keydown", (e) => {
                if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
                if (e.key === "3" || e.key.toLowerCase() === "v") {
                    this.setMode(!this.is25dActive);
                } else if (e.key.toLowerCase() === "p" && this.is25dActive) {
                    this.setPitch(this.pitch === 45 ? 52 : 45);
                } else if (e.key.toLowerCase() === "h" && this.is25dActive) {
                    this.isHeadingUp = !this.isHeadingUp;
                    this.updateHeadingControls();
                    this.goToStep(this.currentStepIndex);
                } else if (e.key.toLowerCase() === "c" && this.is25dActive) {
                    if (this.btnWazeRecenter) this.btnWazeRecenter.click();
                }
            });
        }

        /**
         * Google Maps-style Free 2.5D Gesture Navigation:
         * 1. Left-click/1-finger drag: pan freely with mathematical 1:1 ground tracking under cursor
         * 2. Mouse wheel scroll / 2-finger pinch: smooth zoom in and out
         * 3. Shift/Alt/Right-click drag / 2-finger twist: free 360° heading rotation
         */
        setupInteractions() {
            if (!this.viewport) return;

            let isPointerDown = false;
            let isRotating = false;
            let lastX = 0;
            let lastY = 0;
            let startRotX = 0;
            let startHeading = 0;

            // Touch gesture state
            let isPinching = false;
            let initialDist = 0;
            let initialAngle = 0;
            let initialZoom = 2.2;
            let initialHeading = 0;

            const onPointerDown = (clientX, clientY, isRotateAction, target) => {
                if (!this.is25dActive) return false;
                if (target && (target.closest("button") || target.closest("#bldgPopover") || target.closest(".waze-bldg-badge") || target.closest("#campusCompass") || target.closest("#wazeBottomBar") || target.closest("#wazeActionTray") || target.closest("#turnByTurnBanner"))) {
                    return false;
                }

                if (this.tweenAnimId) {
                    cancelAnimationFrame(this.tweenAnimId);
                    this.tweenAnimId = null;
                }

                if (isRotateAction) {
                    isRotating = true;
                    startRotX = clientX;
                    startHeading = this.currentHeading || 0;
                } else {
                    isPointerDown = true;
                    lastX = clientX;
                    lastY = clientY;
                }

                if (this.stage) this.stage.classList.add("no-transition");
                this.viewport.classList.add("cursor-grabbing");
                return true;
            };

            const onPointerMove = (clientX, clientY) => {
                if (!this.is25dActive) return;

                if (isRotating) {
                    const deltaX = clientX - startRotX;
                    this.isFollowingUser = false;
                    this.currentHeading = (startHeading - deltaX * 0.45) % 360;
                    this.applyTransform();
                    this.updateOverlays();
                    this.updateCompass(false);
                    return;
                }

                if (!isPointerDown) return;

                const deltaX = clientX - lastX;
                const deltaY = clientY - lastY;
                lastX = clientX;
                lastY = clientY;

                if (deltaX === 0 && deltaY === 0) return;

                // User manually panned camera: detach follow mode so user arrow stays at true map location
                this.isFollowingUser = false;

                // Mathematical inverse 2.5D perspective projection
                const vw = this.viewport.clientWidth || 1000;
                const vh = this.viewport.clientHeight || 700;
                const s = Math.min(vw / 1200, vh / 850);
                const zoom = this.zoomScale || 2.2;
                const pitchRad = ((this.pitch || 45) * Math.PI) / 180;
                const cosPitch = Math.cos(pitchRad);

                const deltaRx = deltaX / (zoom * s);
                const deltaRy = deltaY / (zoom * s * cosPitch);

                const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
                const psi = (bearing * Math.PI) / 180;
                const cosPsi = Math.cos(psi);
                const sinPsi = Math.sin(psi);

                const dUserX = -(deltaRx * cosPsi + deltaRy * sinPsi);
                const dUserY = -(-deltaRx * sinPsi + deltaRy * cosPsi);

                if (this.currentUserX === undefined) this.currentUserX = 400;
                if (this.currentUserY === undefined) this.currentUserY = 500;

                this.currentUserX += dUserX;
                this.currentUserY += dUserY;

                this.applyTransform();
                this.updateOverlays();
            };

            const onPointerUp = () => {
                if (!this.is25dActive) return;
                isPointerDown = false;
                isRotating = false;
                if (this.stage) this.stage.classList.remove("no-transition");
                this.viewport.classList.remove("cursor-grabbing");
            };

            // 1. Mouse Drag Handlers
            this.viewport.addEventListener("mousedown", (e) => {
                const isRotate = e.shiftKey || e.altKey || e.button === 2;
                if (onPointerDown(e.clientX, e.clientY, isRotate, e.target)) {
                    if (e.button === 0 || e.button === 2) {
                        e.preventDefault();
                    }
                }
            });

            this.viewport.addEventListener("contextmenu", (e) => {
                if (this.is25dActive) {
                    e.preventDefault();
                }
            });

            window.addEventListener("mousemove", (e) => {
                onPointerMove(e.clientX, e.clientY);
            });

            window.addEventListener("mouseup", () => {
                onPointerUp();
            });

            // 2. Mouse Wheel Zoom (Scroll to zoom smoothly)
            this.viewport.addEventListener("wheel", (e) => {
                if (!this.is25dActive) return;
                e.preventDefault();

                const delta = e.deltaY < 0 ? 0.2 : -0.2;
                this.zoomScale = Math.max(1.1, Math.min(4.0, (this.zoomScale || 2.2) + delta));
                this.applyTransform();
                this.updateOverlays();
            }, { passive: false });

            // 3. Touch Gesture Handlers (Mobile / Tablet: 1 finger pan, 2 fingers pinch & rotate)
            this.viewport.addEventListener("touchstart", (e) => {
                if (!this.is25dActive) return;
                if (e.target.closest("button") || e.target.closest("#bldgPopover") || e.target.closest(".waze-bldg-badge") || e.target.closest("#campusCompass")) {
                    return;
                }

                if (this.tweenAnimId) {
                    cancelAnimationFrame(this.tweenAnimId);
                    this.tweenAnimId = null;
                }

                if (e.touches.length === 1) {
                    isPinching = false;
                    isPointerDown = true;
                    lastX = e.touches[0].clientX;
                    lastY = e.touches[0].clientY;
                    if (this.stage) this.stage.classList.add("no-transition");
                } else if (e.touches.length === 2) {
                    isPointerDown = false;
                    isPinching = true;
                    const t1 = e.touches[0];
                    const t2 = e.touches[1];
                    initialDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
                    initialAngle = Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;
                    initialZoom = this.zoomScale || 2.2;
                    initialHeading = this.currentHeading || 0;
                    if (this.stage) this.stage.classList.add("no-transition");
                }
            }, { passive: false });

            this.viewport.addEventListener("touchmove", (e) => {
                if (!this.is25dActive) return;

                if (isPointerDown && e.touches.length === 1) {
                    e.preventDefault();
                    onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
                } else if (isPinching && e.touches.length === 2) {
                    e.preventDefault();
                    const t1 = e.touches[0];
                    const t2 = e.touches[1];
                    const currentDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
                    const currentAngle = Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;

                    if (initialDist > 0) {
                        const scaleRatio = currentDist / initialDist;
                        this.zoomScale = Math.max(1.1, Math.min(4.0, initialZoom * scaleRatio));
                    }

                    const angleDiff = currentAngle - initialAngle;
                    if (Math.abs(angleDiff) > 3) {
                        this.isFollowingUser = false;
                    }
                    this.currentHeading = (initialHeading - angleDiff) % 360;

                    this.applyTransform();
                    this.updateOverlays();
                    this.updateCompass(false);
                }
            }, { passive: false });

            this.viewport.addEventListener("touchend", (e) => {
                if (!this.is25dActive) return;
                if (e.touches.length === 0) {
                    isPointerDown = false;
                    isPinching = false;
                    if (this.stage) this.stage.classList.remove("no-transition");
                } else if (e.touches.length === 1) {
                    isPinching = false;
                    isPointerDown = true;
                    lastX = e.touches[0].clientX;
                    lastY = e.touches[0].clientY;
                }
            }, { passive: false });
        }

        /**
         * Scales 2.5D zoom proportionally on vertical phone viewports so the campus fills the cockpit richly like Waze
         */
        getResponsiveZoom(baseZoom = 2.2) {
            const vw = this.viewport ? (this.viewport.clientWidth || window.innerWidth) : window.innerWidth;
            const vh = this.viewport ? (this.viewport.clientHeight || window.innerHeight) : window.innerHeight;
            if (vw < 640 && vh > vw) return Math.min(4.5, baseZoom * 1.65);
            if (vw < 1024 && vh > vw) return Math.min(3.8, baseZoom * 1.28);
            return baseZoom;
        }

        getAnchorYRatio() {
            const vw = this.viewport ? (this.viewport.clientWidth || window.innerWidth) : window.innerWidth;
            return vw < 1024 ? 0.66 : 0.70;
        }

        toggleActionTray(forceState) {
            if (!this.wazeActionTray) return;
            this.isTrayOpen = forceState !== undefined ? forceState : !this.isTrayOpen;
            this.wazeActionTray.classList.toggle("hidden", !this.isTrayOpen);
            if (this.viewport) {
                this.viewport.classList.toggle("waze-tray-open", this.isTrayOpen);
            }
            if (this.wazeExpandChevron) {
                this.wazeExpandChevron.style.transform = this.isTrayOpen ? "rotate(180deg)" : "rotate(0deg)";
            }
            if (this.btnWazeExpandTray) {
                this.btnWazeExpandTray.setAttribute("aria-expanded", String(this.isTrayOpen));
            }
        }

        syncWazeChrome() {
            if (this.btnWazeClearRoute) {
                this.btnWazeClearRoute.classList.toggle("hidden", !this.currentRoute);
                this.btnWazeClearRoute.classList.toggle("flex", Boolean(this.currentRoute));
            }
            if (!this.currentRoute) {
                if (this.wazeDialValue) this.wazeDialValue.textContent = this.is25dActive ? "3D" : "2D";
                if (this.wazeDialUnit) this.wazeDialUnit.textContent = this.is25dActive ? "vista" : "mapa";
                if (this.wazeActiveRoadPill) this.wazeActiveRoadPill.classList.add("hidden");
                if (this.wazeOrangeFabIcon) {
                    this.wazeOrangeFabIcon.innerHTML = `<path d="M21.71 11.29l-9-9a1 1 0 00-1.42 0l-9 9a1 1 0 000 1.42l9 9a1 1 0 001.42 0l9-9a1 1 0 000-1.42zM14 14.5V12h-4v3H8v-4a1 1 0 011-1h5V7.5l3.5 3.5-3.5 3.5z"/>`;
                }
            } else if (this.wazeOrangeFabIcon) {
                // Active route: crisp target/recenter icon inside Waze orange FAB
                this.wazeOrangeFabIcon.innerHTML = `<path d="M12 8a4 4 0 100 8 4 4 0 000-8zm8.94 3A8.994 8.994 0 0013 3.06V1h-2v2.06A8.994 8.994 0 003.06 11H1v2h2.06A8.994 8.994 0 0011 20.94V23h2v-2.06A8.994 8.994 0 0020.94 13H23v-2h-2.06zM12 19a7 7 0 110-14 7 7 0 010 14z"/>`;
            }
        }

        /**
         * Toggles between 2D (top-down flat) and 2.5D (perspective tilted) mode
         */
        setMode(enable25d, options = {}) {
            this.is25dActive = enable25d;
            if (!this.cameraGroup) {
                this.cameraGroup = document.getElementById("mapCameraGroup");
            }

            if (enable25d) {
                this.viewport.classList.add("campus-25d-active");
                this.initOverlayBadges();
                if (this.overlayLayer) this.overlayLayer.classList.remove("hidden");
                if (this.wazeBottomBar) this.wazeBottomBar.classList.remove("hidden");

                if (this.btnMode2d) {
                    this.btnMode2d.classList.remove("active", "text-slate-900");
                    this.btnMode2d.classList.add("text-slate-600");
                }
                if (this.btnMode25d) {
                    this.btnMode25d.classList.add("active");
                    this.btnMode25d.classList.remove("text-slate-600");
                }
                if (this.pitchGroup) this.pitchGroup.classList.remove("hidden");
                if (this.headingGroup) this.headingGroup.classList.remove("hidden");
                if (this.liveCompassGroup) this.liveCompassGroup.classList.remove("hidden");
                if (this.parkingGroup) this.parkingGroup.classList.remove("hidden");

                // Clear 2D transform on SVG element so #mapCameraGroup controls the viewport
                if (this.svg) this.svg.style.transform = "none";

                // Waze defaults or caller options
                this.pitch = options.pitch !== undefined ? options.pitch : 48;
                this.zoomScale = options.zoom !== undefined ? options.zoom : this.getResponsiveZoom(2.2);
                this.updatePitchControls(this.pitch);

                if (options.skipDefaultCenter) {
                    this.syncWazeChrome();
                    this.update2dUserArrow();
                    return;
                }

                if (this.currentRoute) {
                    this.showNavigationBanner();
                    if (this.hasUserPosition) {
                        this.isFollowingUser = true;
                        this.isOverview = false;
                        this.anchorToLowerThird(this.userSvgX, this.userSvgY, this.userSvgHeading || 0, false);
                    } else {
                        this.goToStep(this.currentStepIndex);
                    }
                } else if (this.hasUserPosition) {
                    this.isFollowingUser = true;
                    this.showExploreHud();
                    this.anchorToLowerThird(this.userSvgX, this.userSvgY, this.userSvgHeading || 0, false);
                } else {
                    this.heading = 0;
                    this.showExploreHud();
                    this.centerOnCampusLowerThird();
                }
            } else {
                if (this.tweenAnimId) {
                    cancelAnimationFrame(this.tweenAnimId);
                    this.tweenAnimId = null;
                }
                this.viewport.classList.remove("campus-25d-active", "campus-25d-steep", "campus-25d-highlight-parking", "campus-tbt-active");
                this.isParkingHighlighted = false;
                this.updateParkingControl();
                if (this.overlayLayer) this.overlayLayer.classList.add("hidden");
                if (this.tbtBanner) this.tbtBanner.classList.add("hidden");
                // Keep unified Waze bottom dock visible in 2D explore mode too!
                if (this.wazeBottomBar) this.wazeBottomBar.classList.remove("hidden");

                if (this.btnMode2d) {
                    this.btnMode2d.classList.add("active");
                    this.btnMode2d.classList.remove("text-slate-600");
                }
                if (this.btnMode25d) {
                    this.btnMode25d.classList.remove("active");
                    this.btnMode25d.classList.add("text-slate-600");
                }
                if (this.pitchGroup) this.pitchGroup.classList.add("hidden");
                if (this.headingGroup) this.headingGroup.classList.add("hidden");
                if (this.liveCompassGroup) this.liveCompassGroup.classList.add("hidden");
                if (this.parkingGroup) this.parkingGroup.classList.add("hidden");
                // Preserve live GPS tracking across 2D <-> 2.5D mode switches so the 2D user arrow keeps tracking!

                this.pitch = 0;
                this.heading = 0;
                this.zoomScale = 1;
                this.currentUserX = undefined;
                this.currentUserY = undefined;
                this.currentHeading = 0;
                this.focusedBuildingId = null;
                this.focusedBuildingAnchor = null;
                this.stage.style.transform = "";

                if (this.cameraGroup) {
                    this.cameraGroup.removeAttribute("transform");
                }

                if (!this.currentRoute) {
                    if (this.wazeEtaTime) this.wazeEtaTime.textContent = "Campus UAM";
                    if (this.wazeTripMeta) this.wazeTripMeta.textContent = "¿A dónde vas? • Toca para buscar";
                    if (this.wazeProgressBar) this.wazeProgressBar.style.width = "0%";
                }

                if (typeof window.updateCampusCompass === "function") {
                    window.updateCampusCompass(0, true);
                }
                this.update2dUserArrow();
            }

            this.syncWazeChrome();
            this.updateCompass();
            if (typeof window.update25dLostPins === "function") {
                window.update25dLostPins(this);
            }
        }

        /**
         * Updates active styling on the 45° / 52° pitch buttons
         */
        updatePitchControls(degrees) {
            if (!this.btnPitch45 || !this.btnPitch52) return;
            if (degrees <= 48) {
                this.btnPitch45.classList.add("bg-brand-50", "text-brand-600");
                this.btnPitch45.classList.remove("text-slate-600");
                this.btnPitch52.classList.remove("bg-brand-50", "text-brand-600");
                this.btnPitch52.classList.add("text-slate-600");
            } else {
                this.btnPitch52.classList.add("bg-brand-50", "text-brand-600");
                this.btnPitch52.classList.remove("text-slate-600");
                this.btnPitch45.classList.remove("bg-brand-50", "text-brand-600");
                this.btnPitch45.classList.add("text-slate-600");
            }
        }

        /**
         * Toggles high-visibility sky-blue emphasis on all campus parking lots in 2.5D mode
         */
        toggleParkingHighlight() {
            if (!this.is25dActive || !this.viewport) return;
            this.isParkingHighlighted = !this.isParkingHighlighted;
            this.viewport.classList.toggle("campus-25d-highlight-parking", this.isParkingHighlighted);
            this.updateParkingControl();
        }

        updateParkingControl() {
            if (!this.btnToggleParking) return;
            if (this.isParkingHighlighted) {
                this.btnToggleParking.classList.add("bg-sky-50", "text-sky-700");
                this.btnToggleParking.classList.remove("text-slate-600");
            } else {
                this.btnToggleParking.classList.remove("bg-sky-50", "text-sky-700");
                this.btnToggleParking.classList.add("text-slate-600");
            }
        }

        /**
         * Sets camera pitch angle (45° or 52°)
         */
        setPitch(degrees) {
            if (!this.is25dActive) this.setMode(true, { pitch: degrees });
            this.pitch = degrees;
            this.updatePitchControls(degrees);

            this.applyTransform();
            this.updateOverlays();
        }

        updateHeadingControls() {
            if (!this.iconHeadingMode) return;
            if (this.isHeadingUp) {
                this.iconHeadingMode.classList.add("text-brand-600");
                this.iconHeadingMode.classList.remove("text-slate-400");
            } else {
                this.iconHeadingMode.classList.remove("text-brand-600");
                this.iconHeadingMode.classList.add("text-slate-400");
            }
        }

        resolveSvgPoint(coord) {
            if (!coord) return { x: 600, y: 425 };
            if (window.CAMPUS_MICRO_WALKWAYS && coord.nodeId) {
                const microId = window.CAMPUS_MICRO_WALKWAYS.macroToMicro[coord.nodeId];
                const microNode = microId && window.CAMPUS_MICRO_WALKWAYS.nodes[microId];
                if (microNode) return { x: microNode.x, y: microNode.y };
            }
            const known = this.buildingAnchors[coord.nodeId];
            if (known) return { x: known.x, y: known.y };
            return {
                x: Math.round(((coord.xPercent || 50) / 100) * 1200),
                y: Math.round(((coord.yPercent || 50) / 100) * 850)
            };
        }

        calculateHeadingAngle(p1, p2) {
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const rad = Math.atan2(dy, dx);
            const deg = rad * (180 / Math.PI);
            return -(deg + 90);
        }

        /**
         * Locks user position to the lower-third / bottom-center (50% X, 70% Y).
         */
        anchorToLowerThird(xSvg, ySvg, headingDeg, animate = true) {
            this.targetUserX = xSvg;
            this.targetUserY = ySvg;
            this.targetHeading = headingDeg || 0;

            if (!animate || this.currentUserX === undefined) {
                if (this.tweenAnimId) {
                    cancelAnimationFrame(this.tweenAnimId);
                    this.tweenAnimId = null;
                }
                this.currentUserX = this.targetUserX;
                this.currentUserY = this.targetUserY;
                this.currentHeading = this.targetHeading;
                this.applyTransform();
                this.updateOverlays();
                this.updateCompass();
            } else {
                this.startCameraTween();
            }
        }

        startCameraTween(duration = 500) {
            if (this.tweenAnimId) {
                cancelAnimationFrame(this.tweenAnimId);
                this.tweenAnimId = null;
            }

            const startX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const startY = this.currentUserY !== undefined ? this.currentUserY : 500;
            const startH = this.currentHeading || 0;
            const startZ = this.zoomScale || 2.2;

            const targetX = this.targetUserX;
            const targetY = this.targetUserY;
            const targetH = this.targetHeading;
            const targetZ = this.targetZoomScale !== undefined ? this.targetZoomScale : this.zoomScale;

            // Shortest turn interpolation
            let diffH = (targetH - startH) % 360;
            if (diffH < -180) diffH += 360;
            if (diffH > 180) diffH -= 360;

            const startTime = performance.now();

            const step = (now) => {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = 1 - Math.pow(1 - progress, 3); // Smooth cubic ease-out

                this.currentUserX = startX + (targetX - startX) * ease;
                this.currentUserY = startY + (targetY - startY) * ease;
                this.currentHeading = startH + diffH * ease;
                this.zoomScale = startZ + (targetZ - startZ) * ease;

                this.applyTransform();
                this.updateOverlays();
                this.updateCompass(false);

                if (progress < 1) {
                    this.tweenAnimId = requestAnimationFrame(step);
                } else {
                    this.tweenAnimId = null;
                    this.targetZoomScale = undefined;
                }
            };

            this.tweenAnimId = requestAnimationFrame(step);
        }

        /**
         * Switches view to 2.5D mode and zooms specifically into the selected building.
         * @param {string} nodeId - e.g. "buildingA", "buildingB", "buildingP", etc.
         * @param {object} options - { zoom: 2.85, pitch: 48, showPopover: true, animate: true }
         */
        focusBuilding(nodeId, options = {}) {
            if (!nodeId) return;
            const anchor = this.buildingAnchors[nodeId];
            if (!anchor) return;

            const bldgData = this.getBuildingData(nodeId);
            const targetZoom = options.zoom ? this.getResponsiveZoom(options.zoom) : this.getResponsiveZoom(2.65);
            const targetPitch = options.pitch !== undefined ? options.pitch : (this.is25dActive && this.pitch >= 50 ? 52 : 45);

            this.focusedBuildingId = nodeId;
            this.focusedBuildingAnchor = anchor;
            // Detach camera follow so inspecting a building does not teleport the user arrow
            this.isFollowingUser = false;

            const was25d = this.is25dActive;
            if (!this.is25dActive) {
                // Activate 2.5D mode without resetting camera
                this.setMode(true, { skipDefaultCenter: true, pitch: targetPitch, zoom: targetZoom });
            }

            // If transitioning from 2D, seed smooth start position
            if (!was25d || this.currentUserX === undefined) {
                this.currentUserX = 400;
                this.currentUserY = 500;
                this.currentHeading = 0;
                this.zoomScale = 1.6;
            }

            // Set camera targets
            this.targetUserX = anchor.x;
            this.targetUserY = anchor.y;
            this.targetZoomScale = targetZoom;
            this.targetHeading = 0;
            this.pitch = targetPitch;
            this.updatePitchControls(targetPitch);

            // Highlight focused badge in 2.5D overlay
            if (this.badgesContainer) {
                this.badgesContainer.querySelectorAll(".waze-bldg-badge").forEach(badge => {
                    badge.classList.remove("waze-badge-focused");
                });
                const activeBadge = document.getElementById(`wazeBadge_${nodeId}`);
                if (activeBadge) {
                    activeBadge.classList.add("waze-badge-focused");
                }
            }

            // Highlight corresponding directory card
            document.querySelectorAll(".directory-card").forEach(c => {
                if (c.getAttribute("data-bldg") === nodeId) {
                    c.classList.add("ring-2", "ring-brand-500", "bg-brand-50/40");
                    c.scrollIntoView({ behavior: "smooth", block: "nearest" });
                } else {
                    c.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/40");
                }
            });

            // Update 2.5D Top Turn-by-Turn Banner with Building Focus Info
            this.showBuildingFocusBanner(bldgData);

            // Animate camera glide to building
            if (options.animate !== false) {
                this.startCameraTween(550);
            } else {
                this.currentUserX = this.targetUserX;
                this.currentUserY = this.targetUserY;
                this.zoomScale = targetZoom;
                this.applyTransform();
                this.updateOverlays();
                this.updateCompass();
            }

            // Show and position building popover
            if (options.showPopover !== false && typeof window.showBuildingPopover === "function") {
                window.showBuildingPopover(bldgData, anchor);
            }

            // On small devices, close directory sidebar menu so the focused building is immediately visible
            if (window.innerWidth < 1024 && typeof window.toggleNavigateMapSidebar === "function") {
                window.toggleNavigateMapSidebar(false);
            }
        }

        showBuildingFocusBanner(bldgData) {
            if (!this.tbtBanner) return;
            this.tbtBanner.classList.remove("hidden");
            if (this.viewport) this.viewport.classList.add("campus-tbt-active");

            const rawName = bldgData.name || bldgData.id;
            const cleanName = rawName.includes("•") ? rawName.split("•")[0].trim() : rawName;
            const subtitle = rawName.includes("•") ? rawName.split("•")[1].trim() : "Campus UAM";

            if (this.tbtStepCounter) this.tbtStepCounter.textContent = "Vista 2.5D";
            if (this.tbtStepDistance) this.tbtStepDistance.textContent = cleanName;
            if (this.tbtStepInstruction) this.tbtStepInstruction.textContent = subtitle;

            if (this.tbtNextPreview) {
                this.tbtNextPreview.classList.remove("hidden");
                this.tbtNextPreview.textContent = "Toca «Ir aquí» para iniciar navegación JaguarFind";
            }

            if (this.btnTbtConfirmStep && this.btnTbtConfirmStep.parentElement) {
                this.btnTbtConfirmStep.parentElement.classList.add("hidden");
            }

            if (this.wazeActiveRoadPill) {
                this.wazeActiveRoadPill.textContent = cleanName;
                this.wazeActiveRoadPill.classList.remove("hidden");
            }

            this.tbtBanner.onclick = null;
            this.tbtBanner.style.cursor = "default";
            if (this.tbtManeuverIcon) {
                this.tbtManeuverIcon.innerHTML = `
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                `;
            }

            if (this.wazeBottomBar) {
                this.wazeBottomBar.classList.remove("hidden");
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = bldgData.letter || "2.5D";
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = cleanName;
                if (this.wazeProgressBar) this.wazeProgressBar.style.width = "100%";
            }
        }

        centerOnCampusLowerThird() {
            // Default center point near Plaza Central / Edificio B (x: 400, y: 500)
            if (!this.hasUserPosition) {
                this.userSvgX = 400;
                this.userSvgY = 500;
                this.userSvgHeading = 0;
            }
            this.isFollowingUser = true;
            this.isOverview = false;
            this.anchorToLowerThird(this.userSvgX, this.userSvgY, this.userSvgHeading || 0, false);
        }

        recenterOnUser(options = {}) {
            this.isFollowingUser = true;
            this.isOverview = false;
            const animate = options.animate !== false;
            const x = this.hasUserPosition ? this.userSvgX : 400;
            const y = this.hasUserPosition ? this.userSvgY : 500;
            const h = this.hasUserPosition ? (this.userSvgHeading || 0) : 0;

            if (this.is25dActive) {
                this.pitch = this.currentRoute ? 52 : (this.pitch >= 50 ? 52 : 45);
                this.updatePitchControls(this.pitch);
                this.targetZoomScale = this.getResponsiveZoom(this.currentRoute ? 2.42 : 2.2);
                if (!animate) {
                    this.zoomScale = this.targetZoomScale;
                    this.targetZoomScale = undefined;
                }
                this.anchorToLowerThird(x, y, this.isHeadingUp ? h : 0, animate);
            } else if (typeof window.campus2dCenterOnPoint === "function") {
                window.campus2dCenterOnPoint(x, y);
            }
            this.update2dUserArrow();
        }

        update2dUserArrow() {
            if (!this.user2dArrowLayer) {
                this.user2dArrowLayer = document.getElementById("user2dArrowLayer");
                this.user2dArrowGroup = document.getElementById("user2dArrowGroup");
                this.user2dArrowRotator = document.getElementById("user2dArrowRotator");
            }
            if (!this.user2dArrowLayer || !this.user2dArrowGroup) return;

            const shouldShow = Boolean(this.hasUserPosition || this.currentRoute);
            this.user2dArrowLayer.classList.toggle("hidden", !shouldShow);
            if (!shouldShow) return;

            const x = Number.isFinite(this.userSvgX) ? this.userSvgX : 400;
            const y = Number.isFinite(this.userSvgY) ? this.userSvgY : 500;
            const rot = -(this.userSvgHeading || 0);
            this.user2dArrowGroup.setAttribute("transform", `translate(${x.toFixed(1)}, ${y.toFixed(1)})`);
            if (this.user2dArrowRotator) {
                this.user2dArrowRotator.setAttribute("transform", `rotate(${rot.toFixed(1)})`);
            }
        }

        /**
         * Mathematical 3D Screen Projection:
         * Projects an SVG coordinate (0..1200, 0..850) into un-tilted viewport screen pixels.
         * Decouples badges and puck from the tilted SVG plane to eliminate trapezoid stretching.
         */
        projectToScreen(x, y) {
            if (!this.viewport) return null;
            const vw = this.viewport.clientWidth || 1000;
            const vh = this.viewport.clientHeight || 700;

            const s = Math.min(vw / 1200, vh / 850);
            const offX = (vw - 1200 * s) / 2;
            const offY = (vh - 850 * s) / 2;
            const anchorYRatio = this.getAnchorYRatio();
            const anchorX = (vw * 0.50 - offX) / s;
            const anchorY = (vh * anchorYRatio - offY) / s;

            const uX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const uY = this.currentUserY !== undefined ? this.currentUserY : 500;
            const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
            const zoom = this.zoomScale || this.getResponsiveZoom(2.2);
            const pitch = this.pitch || 45;

            // 1. Camera transform in SVG vector space
            const dx = x - uX;
            const dy = y - uY;
            const theta = (bearing * Math.PI) / 180;
            const rx = dx * Math.cos(theta) - dy * Math.sin(theta);
            const ry = dx * Math.sin(theta) + dy * Math.cos(theta);

            const pSvgX = anchorX + rx * zoom;
            const pSvgY = anchorY + ry * zoom;

            // 2. SVG to Viewport mapping
            const x0 = offX + pSvgX * s;
            const y0 = offY + pSvgY * s;

            // 3. 3D perspective projection with responsive lower-third pivot
            const Cx = vw * 0.5;
            const Cy = vh * anchorYRatio;

            const X = x0 - Cx;
            const Y = y0 - Cy;

            const phi = (pitch * Math.PI) / 180;
            const X_prime = X;
            const Y_prime = Y * Math.cos(phi);
            const Z_prime = Y * Math.sin(phi); // negative into screen for Y < 0

            const d = 1300.0;
            const denom = d - Z_prime;
            if (denom <= 60) return null; // Horizon culling

            const k = d / denom;
            const screenX = Cx + X_prime * k;
            const screenY = Cy + Y_prime * k;

            return { x: screenX, y: screenY, k: k };
        }

        /**
         * Updates all decoupled HTML overlay elements (Puck, Badges, Pins)
         */
        updateOverlays() {
            if (!this.is25dActive || !this.overlayLayer) return;

            const vh = this.viewport.clientHeight || 700;
            const vw = this.viewport.clientWidth || 1000;

            // 1. Position Upright Building Badges (aligned with lifted 3D building roofs)
            const flatNodes = new Set(["northGate", "northeastGate", "mainParking", "chilamatesPlaza", "sportsZone", "jaguarJungle", "areaDeMesas"]);
            const roofLift = (this.pitch || 45) >= 50 ? 2.5 : 3.0;
            for (const [nodeId, anchor] of Object.entries(this.buildingAnchors)) {
                const badgeEl = document.getElementById(`wazeBadge_${nodeId}`);
                if (!badgeEl) continue;

                const projY = flatNodes.has(nodeId) ? anchor.y : (anchor.y - roofLift);
                const pos = this.projectToScreen(anchor.x, projY);
                if (pos && pos.y >= 18 && pos.y <= vh - 20 && pos.x >= -60 && pos.x <= vw + 60) {
                    badgeEl.style.display = "inline-flex";
                    badgeEl.style.left = `${pos.x.toFixed(1)}px`;
                    badgeEl.style.top = `${pos.y.toFixed(1)}px`;
                    const scaleFactor = Math.min(1.05, Math.max(0.68, pos.k * 0.95));
                    badgeEl.style.transform = `translate(-50%, -50%) scale(${scaleFactor.toFixed(3)})`;
                    const horizonFade = Math.min(1.0, Math.max(0.0, (pos.y - 14) / 36));
                    badgeEl.style.opacity = horizonFade.toFixed(2);
                } else {
                    badgeEl.style.display = "none";
                }
            }

            // 2. Position & Rotate Decoupled Navigation Puck at True User SVG Coordinates
            if (this.puckContainer) {
                const uPos = this.projectToScreen(this.userSvgX, this.userSvgY);
                if (uPos && uPos.y >= 10 && uPos.y <= vh + 45 && uPos.x >= -60 && uPos.x <= vw + 60) {
                    this.puckContainer.style.display = "flex";
                    this.puckContainer.style.left = `${uPos.x.toFixed(1)}px`;
                    this.puckContainer.style.top = `${uPos.y.toFixed(1)}px`;
                    const puckScale = (this.isFollowingUser && !this.isOverview)
                        ? 1.0
                        : Math.min(1.12, Math.max(0.62, uPos.k * 0.96));
                    this.puckContainer.style.transform = `translate(-50%, -50%) scale(${puckScale.toFixed(3)})`;
                } else {
                    this.puckContainer.style.display = "none";
                }
            }

            if (this.puckArrow) {
                // Relative arrow rotation = cameraBearing - userSvgHeading
                // In Heading-Up follow mode (cameraBearing === userSvgHeading), arrow points straight UP (0°).
                // In Overview, North-Up, or manual pan/rotate, arrow points accurately down the user's walking heading!
                const cameraBearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
                const arrowRot = this.normalizeAngle180(cameraBearing - (this.userSvgHeading || 0));
                this.puckArrow.style.transform = `rotate(${arrowRot.toFixed(2)}deg)`;
                if (this.puckCone) {
                    this.puckCone.style.transform = `rotate(${arrowRot.toFixed(2)}deg)`;
                }
            }

            // 3. Position Destination & Origin Pins (aligned with exact walkway route endpoints)
            const hasPolyline = Array.isArray(this.activeRoutePolyline) && this.activeRoutePolyline.length >= 2;
            const hasMacroCoords = Boolean(this.currentRoute && this.currentRoute.pathCoordinates && this.currentRoute.pathCoordinates.length >= 2);
            if (this.currentRoute && (hasPolyline || hasMacroCoords)) {
                const startPt = hasPolyline
                    ? this.activeRoutePolyline[0]
                    : this.resolveSvgPoint(this.currentRoute.pathCoordinates[0]);
                const endPt = hasPolyline
                    ? this.activeRoutePolyline[this.activeRoutePolyline.length - 1]
                    : this.resolveSvgPoint(this.currentRoute.pathCoordinates[this.currentRoute.pathCoordinates.length - 1]);
                const endPos = this.projectToScreen(endPt.x, endPt.y);

                if (this.wazeDestPin) {
                    if (endPos && endPos.y >= 20 && endPos.y <= vh) {
                        this.wazeDestPin.style.display = "block";
                        this.wazeDestPin.style.left = `${endPos.x.toFixed(1)}px`;
                        this.wazeDestPin.style.top = `${endPos.y.toFixed(1)}px`;
                        this.wazeDestPin.style.transform = `translate(-50%, -100%) scale(${Math.min(1.2, Math.max(0.7, endPos.k)).toFixed(2)})`;
                    } else {
                        this.wazeDestPin.style.display = "none";
                    }
                }

                const startPos = this.projectToScreen(startPt.x, startPt.y);
                if (this.wazeOriginPin) {
                    if (startPos && startPos.y >= 20 && startPos.y <= vh) {
                        this.wazeOriginPin.style.display = "block";
                        this.wazeOriginPin.style.left = `${startPos.x.toFixed(1)}px`;
                        this.wazeOriginPin.style.top = `${startPos.y.toFixed(1)}px`;
                    } else {
                        this.wazeOriginPin.style.display = "none";
                    }
                }
            } else {
                if (this.wazeDestPin) this.wazeDestPin.style.display = "none";
                if (this.wazeOriginPin) this.wazeOriginPin.style.display = "none";
            }

            // 4. Reposition open building popover in real time with 3D camera
            const bldgPopover = document.getElementById("bldgPopover");
            if (bldgPopover && !bldgPopover.classList.contains("hidden") && this.focusedBuildingAnchor) {
                if (vw < 640) {
                    bldgPopover.style.left = "50%";
                    bldgPopover.style.top = "auto";
                    bldgPopover.style.bottom = "80px";
                    bldgPopover.style.transform = "translateX(-50%)";
                } else {
                    const pos = this.projectToScreen(this.focusedBuildingAnchor.x, this.focusedBuildingAnchor.y);
                    if (pos) {
                        const maxLeft = vw - 310;
                        const maxTop = vh - 250;
                        bldgPopover.style.bottom = "auto";
                        bldgPopover.style.transform = "none";
                        bldgPopover.style.left = `${Math.max(12, Math.min(pos.x - 120, maxLeft))}px`;
                        bldgPopover.style.top = `${Math.max(84, Math.min(pos.y - 170, maxTop))}px`;
                    }
                }
            }

            // 5. Position 2.5D Lost & Found Markers
            if (typeof window.update25dLostPins === "function") {
                window.update25dLostPins(this);
            }
        }

        /**
         * Crisp Vector 2.5D Transform Pipeline:
         * 1. rotateX(pitch) strictly on outer wrapper (CSS 3D perspective plane)
         * 2. translate + responsive zoom + rotate strictly inside SVG <g id="mapCameraGroup">
         */
        applyTransform() {
            if (!this.stage) return;
            if (!this.cameraGroup) {
                this.cameraGroup = document.getElementById("mapCameraGroup");
            }

            if (!this.is25dActive) {
                this.stage.style.transform = "";
                if (this.cameraGroup) this.cameraGroup.removeAttribute("transform");
                return;
            }

            const pitch = this.pitch || 45;
            const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
            const zoom = this.zoomScale || this.getResponsiveZoom(2.2);
            const uX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const uY = this.currentUserY !== undefined ? this.currentUserY : 500;

            if (this.viewport) {
                this.viewport.classList.toggle("campus-25d-steep", pitch >= 50);
            }

            const vw = this.viewport ? (this.viewport.clientWidth || 1000) : 1000;
            const vh = this.viewport ? (this.viewport.clientHeight || 700) : 700;
            const s = Math.min(vw / 1200, vh / 850);
            const offX = (vw - 1200 * s) / 2;
            const offY = (vh - 850 * s) / 2;
            const anchorYRatio = this.getAnchorYRatio();
            const anchorX = (vw * 0.50 - offX) / s;
            const anchorY = (vh * anchorYRatio - offY) / s;

            // 1. Tilt STRICTLY via CSS rotateX on the outer stage
            this.stage.style.transform = `rotateX(${pitch}deg)`;

            // 2. Vector pan, zoom & bearing rotation directly inside SVG <g id="mapCameraGroup">
            if (this.cameraGroup) {
                const svgTransform = `translate(${anchorX.toFixed(2)}, ${anchorY.toFixed(2)}) ` +
                                     `scale(${zoom.toFixed(3)}) ` +
                                     `rotate(${bearing.toFixed(2)}) ` +
                                     `translate(${(-uX).toFixed(2)}, ${(-uY).toFixed(2)})`;
                this.cameraGroup.setAttribute("transform", svgTransform);
            }

            // Sync compass with view rotation in real time
            this.updateCompass(false);
        }

        zoomIn() {
            this.zoomScale = Math.min((this.zoomScale || this.getResponsiveZoom(2.2)) + 0.3, 5.2);
            this.applyTransform();
            this.updateOverlays();
        }

        zoomOut() {
            this.zoomScale = Math.max((this.zoomScale || this.getResponsiveZoom(2.2)) - 0.3, 1.15);
            this.applyTransform();
            this.updateOverlays();
        }

        /**
         * Keeps the Compass Rose synchronized with map rotation
         */
        updateCompass(animate = true) {
            const dial = document.getElementById("compassDial");
            const compassRot = this.is25dActive && this.isHeadingUp ? -(this.currentHeading || 0) : 0;
            if (dial) {
                dial.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
                dial.style.transform = `rotate(${compassRot.toFixed(2)}deg)`;
            } else if (typeof window.updateCampusCompass === "function") {
                window.updateCampusCompass(compassRot, animate);
            }
        }

        /**
         * Global Route Calculated Handler
         */
        onRouteCalculated(routeData) {
            this.currentRoute = routeData;
            this.currentStepIndex = 0;

            const hasSteps = Array.isArray(routeData && routeData.steps) && routeData.steps.length > 0;
            const hasPath = Array.isArray(routeData && routeData.pathCoordinates) && routeData.pathCoordinates.length >= 2;
            if (!routeData || (!hasSteps && !hasPath)) {
                return;
            }

            // Restore human landmark confirm button when switching from building focus back to active route
            if (this.btnTbtConfirmStep && this.btnTbtConfirmStep.parentElement) {
                this.btnTbtConfirmStep.parentElement.classList.remove("hidden");
            }

            // Draw exact backend Dijkstra pedestrian walkway polyline
            this.drawRoutePolylines(routeData);

            // Switch to 2.5D Waze-style perspective view (Heading-Up)
            this.isHeadingUp = true;
            this.updateHeadingControls();
            const routeZoom = this.getResponsiveZoom(2.4);
            if (!this.is25dActive) {
                this.setMode(true, { pitch: 52, zoom: routeZoom, skipDefaultCenter: true });
            } else {
                this.pitch = 52;
                this.zoomScale = routeZoom;
            }

            this.showNavigationBanner();
            this.goToStep(0);
        }

        drawRoutePolylines(routeData) {
            if (!routeData) return;
            let resolvedPts = [];
            if (Array.isArray(routeData.walkwayPath) && routeData.walkwayPath.length >= 2) {
                resolvedPts = routeData.walkwayPath.map(pt => ({ x: Math.round(pt.x), y: Math.round(pt.y) }));
            } else if (Array.isArray(routeData.pathCoordinates) && routeData.pathCoordinates.length >= 2) {
                if (typeof window.resolveMicroCampusRoute === "function") {
                    resolvedPts = window.resolveMicroCampusRoute(routeData.pathCoordinates, {
                        accessibleOnly: Boolean(routeData.isAccessibleRoute)
                    });
                }
                if (resolvedPts.length < 2) {
                    resolvedPts = routeData.pathCoordinates.map(coord => this.resolveSvgPoint(coord));
                }
            }
            const points = resolvedPts.map(pt => `${pt.x},${pt.y}`).join(" ");

            const shadow = document.getElementById("route2dShadowPolyline");
            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");
            if (shadow) shadow.setAttribute("points", points);
            if (glow) glow.setAttribute("points", points);
            if (main) main.setAttribute("points", points);
        }

        onRouteCleared() {
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.stopSimulation();
            this.hideNavigationBanner();
            this.toggleActionTray(false);
            if (this.tbtOrientationCue) {
                this.tbtOrientationCue.classList.add("hidden");
            }

            const shadow = document.getElementById("route2dShadowPolyline");
            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");
            if (shadow) shadow.setAttribute("points", "");
            if (glow) glow.setAttribute("points", "");
            if (main) main.setAttribute("points", "");

            this.syncWazeChrome();

            if (this.is25dActive) {
                if (!this.isLiveCompassActive) this.heading = 0;
                this.showExploreHud();
                this.centerOnCampusLowerThird();
            } else {
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = "Campus UAM";
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = "¿A dónde vas? • Toca para buscar";
                if (this.wazeProgressBar) this.wazeProgressBar.style.width = "0%";
            }
        }

        showNavigationBanner() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.remove("hidden");
            }
            if (this.viewport) {
                this.viewport.classList.add("campus-tbt-active");
            }
            if (this.wazeBottomBar) {
                this.wazeBottomBar.classList.remove("hidden");
            }
            this.syncWazeChrome();
        }

        showExploreHud() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.add("hidden");
            }
            if (this.viewport) {
                this.viewport.classList.remove("campus-tbt-active");
            }
            if (this.wazeBottomBar) {
                this.wazeBottomBar.classList.remove("hidden");
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = "Campus UAM";
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = "¿A dónde vas? • Toca para buscar";
                if (this.wazeProgressBar) this.wazeProgressBar.style.width = "0%";
            }
            if (this.wazeActiveRoadPill) {
                this.wazeActiveRoadPill.textContent = "Campus UAM";
                this.wazeActiveRoadPill.classList.remove("hidden");
            }
            this.syncWazeChrome();
        }

        hideNavigationBanner() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.add("hidden");
            }
            if (this.viewport) {
                this.viewport.classList.remove("campus-tbt-active");
            }
            this.stopSimulation();
        }

        // ====================================================================
        // LIVE 2.5D PHONE COMPASS ROTATION + CONTINUOUS GPS TRACKING
        // ====================================================================
        gpsToSvg(lat, lng) {
            const c = this.calibration;
            const mNorth = (lat - c.lat0) * c.mPerDegLat;
            const mEast = (lng - c.lng0) * c.mPerDegLng;
            const x = c.cx0 + c.cxN * mNorth + c.cxE * mEast;
            const y = c.cy0 + c.cyN * mNorth + c.cyE * mEast;
            return {
                x: Math.max(40, Math.min(1160, Math.round(x * 10) / 10)),
                y: Math.max(15, Math.min(835, Math.round(y * 10) / 10)),
            };
        }

        haversineMeters(lat1, lng1, lat2, lng2) {
            const R = 6371000;
            const toRad = (deg) => (deg * Math.PI) / 180;
            const dLat = toRad(lat2 - lat1);
            const dLng = toRad(lng2 - lng1);
            const a = Math.sin(dLat / 2) ** 2 +
                      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        }

        normalizeAngle180(deg) {
            let a = ((deg + 180) % 360 + 360) % 360 - 180;
            return a;
        }

        async toggleLiveCompassNavigation() {
            if (this.isLiveCompassActive) {
                this.stopLiveCompassNavigation();
            } else {
                await this.startLiveCompassNavigation();
            }
        }

        async startLiveCompassNavigation() {
            // Ensure 2.5D mode and Heading-Up are enabled
            if (!this.is25dActive) {
                this.setMode(true, { pitch: 52, zoom: this.getResponsiveZoom(2.4), skipDefaultCenter: true });
            }
            this.isHeadingUp = true;
            this.updateHeadingControls();
            this.stopSimulation();

            // iOS 13+ Safari requires explicit permission inside a user click gesture
            if (typeof DeviceOrientationEvent !== "undefined" && typeof DeviceOrientationEvent.requestPermission === "function") {
                try {
                    const perm = await DeviceOrientationEvent.requestPermission();
                    if (perm !== "granted") {
                        console.warn("Compass permission denied by user.");
                    }
                } catch (err) {
                    console.warn("Compass permission request failed:", err);
                }
            }

            this.isLiveCompassActive = true;
            this.smoothedCompassDeg = null;
            this.updateLiveCompassButtonUI();

            // Prefer absolute orientation (true north) on Android Chrome; fallback to deviceorientation (iOS webkitCompassHeading)
            if ("ondeviceorientationabsolute" in window) {
                window.addEventListener("deviceorientationabsolute", this._boundOrientationHandler, true);
            }
            window.addEventListener("deviceorientation", this._boundOrientationHandler, true);

            // Start continuous high-accuracy GPS tracking
            if (navigator.geolocation) {
                if (this.gpsWatchId !== null) {
                    navigator.geolocation.clearWatch(this.gpsWatchId);
                }
                this.gpsWatchId = navigator.geolocation.watchPosition(
                    (pos) => this.handleLiveGpsPosition(pos),
                    (err) => console.warn("Live GPS watchPosition warning:", err.message),
                    { enableHighAccuracy: true, maximumAge: 2000, timeout: 10000 }
                );
            }
        }

        stopLiveCompassNavigation() {
            this.isLiveCompassActive = false;
            window.removeEventListener("deviceorientationabsolute", this._boundOrientationHandler, true);
            window.removeEventListener("deviceorientation", this._boundOrientationHandler, true);

            if (this.gpsWatchId !== null && navigator.geolocation) {
                navigator.geolocation.clearWatch(this.gpsWatchId);
                this.gpsWatchId = null;
            }
            if (this.tbtOrientationCue) {
                this.tbtOrientationCue.classList.add("hidden");
                this.tbtOrientationCue.classList.remove("flex");
            }
            this.updateLiveCompassButtonUI();
        }

        updateLiveCompassButtonUI() {
            if (!this.btnLiveCompass) return;
            if (this.isLiveCompassActive) {
                this.btnLiveCompass.classList.remove("text-slate-600", "hover:bg-emerald-50");
                this.btnLiveCompass.classList.add("bg-emerald-500", "text-white", "shadow-xs");
                if (this.liveCompassDot) {
                    this.liveCompassDot.className = "w-2 h-2 rounded-full bg-white animate-pulse";
                }
            } else {
                this.btnLiveCompass.classList.remove("bg-emerald-500", "text-white", "shadow-xs");
                this.btnLiveCompass.classList.add("text-slate-600", "hover:bg-emerald-50");
                if (this.liveCompassDot) {
                    this.liveCompassDot.className = "w-2 h-2 rounded-full bg-slate-300";
                }
            }
        }

        handleDeviceOrientation(event) {
            if (!this.isLiveCompassActive || !this.is25dActive || !this.isHeadingUp) return;

            let rawHeading = null;
            if (typeof event.webkitCompassHeading === "number" && !Number.isNaN(event.webkitCompassHeading)) {
                // iOS Safari provides direct clockwise degrees from magnetic north [0..360)
                rawHeading = event.webkitCompassHeading;
            } else if (typeof event.alpha === "number" && !Number.isNaN(event.alpha)) {
                // Android / W3C absolute orientation: alpha is CCW from north
                const screenAngle = (window.screen && window.screen.orientation && window.screen.orientation.angle)
                    || window.orientation || 0;
                rawHeading = (360 - event.alpha + screenAngle) % 360;
            }

            if (rawHeading === null) return;

            // Circular exponential smoothing to keep 2.5D rotation steady without jitter
            if (this.smoothedCompassDeg === null) {
                this.smoothedCompassDeg = rawHeading;
            } else {
                const delta = this.normalizeAngle180(rawHeading - this.smoothedCompassDeg);
                this.smoothedCompassDeg = (this.smoothedCompassDeg + delta * 0.22 + 360) % 360;
            }
            this.latestCompassDeg = this.smoothedCompassDeg;

            if (!this._compassRafPending) {
                this._compassRafPending = true;
                requestAnimationFrame(() => {
                    this._compassRafPending = false;
                    if (!this.isLiveCompassActive || !this.is25dActive) return;

                    // Convert true compass heading to SVG camera rotation (calibrated UAM mapUpTrueBearingDeg = 181.4°)
                    const mapUpBearing = (this.calibration && this.calibration.mapUpTrueBearingDeg) || 181.4;
                    const svgHeading = this.normalizeAngle180(mapUpBearing - this.latestCompassDeg);
                    this.currentHeading = svgHeading;
                    this.targetHeading = svgHeading;
                    this.applyTransform();
                    this.updateOverlays();
                    this.updateCompass(false);
                    this.updateOrientationCue();
                });
            }
        }

        handleLiveGpsPosition(pos) {
            if (!this.isLiveCompassActive || !pos || !pos.coords) return;
            const { latitude, longitude, accuracy, heading } = pos.coords;
            this.latestGpsCoords = { lat: latitude, lng: longitude, accuracy: accuracy || 20 };

            // Ignore extremely noisy indoor readings (> 35m error)
            if (accuracy && accuracy > 35) return;

            const svgPt = this.gpsToSvg(latitude, longitude);
            // If phone has no compass sensor, fall back to GPS movement heading when walking
            if (this.smoothedCompassDeg === null && typeof heading === "number" && !Number.isNaN(heading)) {
                const mapUpBearing = (this.calibration && this.calibration.mapUpTrueBearingDeg) || 181.4;
                this.currentHeading = this.normalizeAngle180(mapUpBearing - heading);
                this.targetHeading = this.currentHeading;
            }

            // Smoothly anchor blue puck to real user GPS position on campus map
            this.currentUserX = svgPt.x;
            this.currentUserY = svgPt.y;
            this.targetUserX = svgPt.x;
            this.targetUserY = svgPt.y;
            this.applyTransform();
            this.updateOverlays();

            // Auto-advance step when user walks within ~10m of current step's target landmark
            const steps = this.getActiveStepsList();
            if (steps.length > 0 && this.currentStepIndex < steps.length - 1) {
                const activeStep = steps[this.currentStepIndex];
                const tLat = activeStep.targetLat || activeStep.lat;
                const tLng = activeStep.targetLng || activeStep.lng;
                if (tLat && tLng) {
                    const distToMilestone = this.haversineMeters(latitude, longitude, tLat, tLng);
                    if (distToMilestone <= 10.5) {
                        this.nextStep({ keepLivePosition: true });
                    }
                }
            }
        }

        updateOrientationCue() {
            if (!this.tbtOrientationCue || !this.tbtOrientationCueText) return;
            const steps = this.getActiveStepsList();
            const step = steps[this.currentStepIndex];
            if (!this.isLiveCompassActive || this.latestCompassDeg === null || !step || typeof step.nextBearingDeg !== "number") {
                this.tbtOrientationCue.classList.add("hidden");
                this.tbtOrientationCue.classList.remove("flex");
                return;
            }

            const diff = this.normalizeAngle180(step.nextBearingDeg - this.latestCompassDeg);
            const absDiff = Math.abs(diff);
            let cueText = "";
            let isAligned = false;

            if (absDiff <= 25) {
                cueText = "¡Bien orientado! Sigue de frente";
                isAligned = true;
            } else if (absDiff >= 145) {
                cueText = "Da media vuelta para seguir el camino";
            } else if (diff > 25 && diff <= 65) {
                cueText = "Gira un poco a tu derecha para alinearte";
            } else if (diff > 65) {
                cueText = "Gira a tu derecha hacia el camino";
            } else if (diff < -25 && diff >= -65) {
                cueText = "Gira un poco a tu izquierda para alinearte";
            } else {
                cueText = "Gira a tu izquierda hacia el camino";
            }

            this.tbtOrientationCueText.textContent = cueText;
            this.tbtOrientationCue.classList.remove("hidden");
            this.tbtOrientationCue.classList.add("flex");
            if (isAligned) {
                this.tbtOrientationCue.className = "flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200/80 rounded-lg px-2 py-0.5 mt-1.5";
            } else {
                this.tbtOrientationCue.className = "flex items-center gap-1.5 text-[11px] font-bold text-amber-800 bg-amber-50 border border-amber-200/80 rounded-lg px-2 py-0.5 mt-1.5";
            }
        }

        // ====================================================================
        // STEP-BY-STEP HUMAN LANDMARK NAVIGATION (SYNCED WITH WALKWAY GRAPH)
        // ====================================================================
        getActiveStepsList() {
            if (!this.currentRoute) return [];
            if (Array.isArray(this.currentRoute.steps) && this.currentRoute.steps.length > 0) {
                return this.currentRoute.steps;
            }
            const coords = this.currentRoute.pathCoordinates || [];
            const instructions = this.currentRoute.stepInstructions || [];
            return coords.map((c, idx) => {
                const pt = this.resolveSvgPoint(c);
                return {
                    index: idx,
                    instruction: instructions[idx] || `Avanza hacia ${c.name || "el siguiente punto"}`,
                    headline: idx === coords.length - 1 ? "Has llegado" : "Sigue recto",
                    maneuver: idx === coords.length - 1 ? "arrive" : "straight",
                    landmark: c.name ? c.name.split("(")[0].trim() : "Campus UAM",
                    x: pt.x,
                    y: pt.y,
                    targetX: pt.x,
                    targetY: pt.y,
                    lat: c.lat,
                    lng: c.lng,
                    buildingId: c.nodeId,
                };
            });
        }

        getManeuverIconPath(maneuver) {
            switch (maneuver) {
                case "arrive":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.4" d="M4 21V5m0 0h11l-2.5 4.5L15 14H4"/>`;
                case "right":
                case "slight_right":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M8 20v-7a5 5 0 015-5h5m0 0l-4-4m4 4l-4 4"/>`;
                case "left":
                case "slight_left":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M16 20v-7a5 5 0 00-5-5H6m0 0l4-4M6 8l4 4"/>`;
                case "uturn":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.8" d="M9 14l-4-4 4-4m-4 4h9a4 4 0 110 8h-3"/>`;
                case "stairs_up":
                case "stairs_down":
                case "stairs":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M3 19h4v-4h4v-4h4V7h5"/>`;
                case "ramp":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M3 18L20 7m0 0h-5m5 0v5"/>`;
                case "crosswalk":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M4 7h16M4 12h16M4 17h16"/>`;
                case "skybridge":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M3 14h18M5 14a7 7 0 0114 0M6 14v5m12-5v5"/>`;
                case "enter":
                case "exit":
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a2 2 0 01-2 2H6a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"/>`;
                default:
                    return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 20V5m0 0l-5 5m5-5l5 5"/>`;
            }
        }

        /**
         * Navigates to a specific human landmark step along the walkway route
         */
        goToStep(stepIndex, options = {}) {
            const steps = this.getActiveStepsList();
            if (!this.currentRoute || steps.length === 0) return;

            if (stepIndex < 0) stepIndex = 0;
            if (stepIndex >= steps.length) stepIndex = steps.length - 1;
            this.currentStepIndex = stepIndex;

            const step = steps[stepIndex];
            const nextStep = stepIndex < steps.length - 1 ? steps[stepIndex + 1] : null;
            const currentPt = { x: step.x || 600, y: step.y || 425 };
            const aimPt = (step.targetX !== undefined && (step.targetX !== step.x || step.targetY !== step.y))
                ? { x: step.targetX, y: step.targetY }
                : (nextStep ? { x: nextStep.x, y: nextStep.y } : currentPt);

            // Compute walkway heading unless real phone compass is driving heading live
            let headingDeg = this.currentHeading || 0;
            if (!this.isLiveCompassActive) {
                if (aimPt.x !== currentPt.x || aimPt.y !== currentPt.y) {
                    headingDeg = this.calculateHeadingAngle(currentPt, aimPt);
                } else if (stepIndex > 0) {
                    const prevS = steps[stepIndex - 1];
                    headingDeg = this.calculateHeadingAngle({ x: prevS.x, y: prevS.y }, currentPt);
                }
            }

            const isFinalStep = stepIndex === steps.length - 1;
            this.pitch = isFinalStep ? 50 : 52;
            this.targetZoomScale = this.getResponsiveZoom(isFinalStep ? 2.75 : 2.42);

            // Highlight active building badge along the route
            if (this.badgesContainer && step.buildingId) {
                this.badgesContainer.querySelectorAll(".waze-bldg-badge").forEach(badge => {
                    badge.classList.toggle("waze-badge-focused", badge.id === `wazeBadge_${step.buildingId}`);
                });
            }

            // Highlight active step in the sidebar directions panel
            document.querySelectorAll("#routeStepsList li").forEach((li, idx) => {
                if (idx === stepIndex) {
                    li.classList.add("ring-2", "ring-brand-500", "bg-brand-50/80");
                } else {
                    li.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/80");
                }
            });

            if (!options.keepLivePosition) {
                this.anchorToLowerThird(currentPt.x, currentPt.y, headingDeg);
            }

            this.updateBannerUI(stepIndex, steps.length, step, nextStep);
            this.updateOrientationCue();
        }

        nextStep(options = {}) {
            if (!this.currentRoute) return;
            const steps = this.getActiveStepsList();
            if (this.currentStepIndex < steps.length - 1) {
                this.goToStep(this.currentStepIndex + 1, options);
            } else {
                this.stopSimulation();
            }
        }

        prevStep() {
            if (!this.currentRoute) return;
            if (this.currentStepIndex > 0) {
                this.goToStep(this.currentStepIndex - 1);
            }
        }

        updateBannerUI(stepIdx, totalSteps, step, nextStep) {
            const isFinal = stepIdx === totalSteps - 1;
            const headline = (step && step.headline) || (isFinal ? "Has llegado" : "Sigue recto");
            const instruction = (step && step.instruction) || "";
            const landmark = (step && step.landmark) || "Campus UAM";

            if (this.tbtStepCounter) {
                this.tbtStepCounter.textContent = `Referencia ${stepIdx + 1} de ${totalSteps}`;
            }
            if (this.tbtStepDistance) {
                this.tbtStepDistance.textContent = headline;
            }
            if (this.tbtStepInstruction) {
                this.tbtStepInstruction.textContent = instruction;
            }
            if (this.wazeActiveRoadPill) {
                this.wazeActiveRoadPill.textContent = landmark;
                this.wazeActiveRoadPill.classList.remove("hidden");
            }

            if (this.tbtNextPreview) {
                if (nextStep && nextStep.headline) {
                    this.tbtNextPreview.textContent = `Luego: ${nextStep.headline} → ${nextStep.landmark || ""}`;
                    this.tbtNextPreview.classList.remove("hidden");
                } else {
                    this.tbtNextPreview.classList.add("hidden");
                }
            }

            if (this.tbtConfirmRow && this.labelTbtConfirmStep) {
                if (isFinal) {
                    this.tbtConfirmRow.classList.add("hidden");
                } else {
                    this.tbtConfirmRow.classList.remove("hidden");
                    this.labelTbtConfirmStep.textContent = nextStep && nextStep.landmark
                        ? `Ya llegué aquí • Ir a ${nextStep.landmark.slice(0, 22)}`
                        : "Ya llegué aquí • Siguiente";
                }
            }

            // Geometric maneuver arrow from backend walkway analysis
            if (this.tbtManeuverIcon) {
                this.tbtManeuverIcon.innerHTML = this.getManeuverIconPath((step && step.maneuver) || "straight");
            }

            // Circular dial: human walking minutes remaining (NOT meters!)
            const totalMinutes = this.currentRoute ? Math.max(1, this.currentRoute.estimatedWalkingMinutes || 1) : 1;
            const remainingRatio = totalSteps > 1 ? Math.max(0, (totalSteps - 1 - stepIdx) / (totalSteps - 1)) : 0;
            const remMinutes = isFinal ? 0 : Math.max(1, Math.ceil(totalMinutes * remainingRatio));

            if (this.wazeDialValue) {
                this.wazeDialValue.textContent = isFinal ? "✓" : `~${remMinutes}`;
            }
            if (this.wazeDialUnit) {
                this.wazeDialUnit.textContent = isFinal ? "fin" : "min";
            }

            // Bottom Dock: Arrival clock + human summary (time + landmarks remaining)
            const now = new Date();
            const arrivalDate = new Date(now.getTime() + remMinutes * 60000);
            const timeStr = arrivalDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });

            if (this.wazeEtaTime) {
                this.wazeEtaTime.textContent = isFinal ? "Llegaste" : timeStr;
            }

            const stepsLeft = Math.max(0, totalSteps - 1 - stepIdx);
            if (this.wazeTripMeta) {
                this.wazeTripMeta.textContent = isFinal
                    ? `${landmark} • Destino alcanzado`
                    : `${this.currentRoute.humanDuration || `~${remMinutes} min`} • ${stepsLeft} ${stepsLeft === 1 ? "referencia" : "referencias"}`;
            }

            if (this.wazeProgressBar) {
                const progressPct = totalSteps > 1 ? Math.round((stepIdx / (totalSteps - 1)) * 100) : 100;
                this.wazeProgressBar.style.width = `${progressPct}%`;
            }

            this.syncWazeChrome();
        }

        toggleSimulation() {
            if (this.isSimulating) {
                this.stopSimulation();
            } else {
                this.startSimulation();
            }
        }

        startSimulation() {
            const steps = this.getActiveStepsList();
            if (!this.currentRoute || steps.length === 0) return;
            if (this.isLiveCompassActive) this.stopLiveCompassNavigation();

            this.isSimulating = true;
            if (this.labelSimPlay) this.labelSimPlay.textContent = "Pausa";

            if (this.currentStepIndex >= steps.length - 1) {
                this.goToStep(0);
            }

            if (this.simInterval) clearInterval(this.simInterval);
            this.simInterval = setInterval(() => {
                const activeSteps = this.getActiveStepsList();
                if (!this.currentRoute || activeSteps.length === 0) {
                    this.stopSimulation();
                    return;
                }

                if (this.currentStepIndex < activeSteps.length - 1) {
                    this.nextStep();
                } else {
                    this.stopSimulation();
                }
            }, 2200);
        }

        stopSimulation() {
            this.isSimulating = false;
            if (this.labelSimPlay) this.labelSimPlay.textContent = "Simular";
            if (this.simInterval) {
                clearInterval(this.simInterval);
                this.simInterval = null;
            }
        }
    }

    // Initialize Global Controller Singleton
    window.campus25dController = new Campus25dController();
})();
