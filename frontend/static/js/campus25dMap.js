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
    function t25d(key, params) {
        if (typeof window.t === "function") {
            return window.t(key, undefined, params);
        }
        return key;
    }

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
            const colorMap = {
                "buildingA": "#991b1b", "buildingB": "#581c87", "buildingC": "#4c1d95",
                "buildingD": "#15803d", "buildingE": "#0284c7", "buildingF": "#be185d",
                "buildingG": "#0284c7", "buildingH": "#15803d", "buildingI": "#1e3a8a",
                "buildingJ": "#0284c7", "buildingK": "#b45309", "buildingL": "#0284c7",
                "buildingM": "#b45309", "buildingN": "#6b21a8", "buildingO": "#b45309",
                "buildingP": "#be185d", "sportsZone": "#15803d", "jaguarCenter": "#0f766e",
                "jaguarGym": "#0f766e", "physiotherapy": "#0284c7"
            };
            const gatePinKey = (nodeId === "northGate" || nodeId === "northeastGate")
                ? `map.buildings.${nodeId}.pin_code`
                : null;
            return {
                id: nodeId,
                letter: gatePinKey ? t25d(gatePinKey) : (letterMap[nodeId] || nodeId.charAt(0).toUpperCase()),
                name: t25d(`nodes.${nodeId}`),
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
                            <span data-dest-pin-label>${t25d("map.hud25d.dest_pin_label")}</span>
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
                        altitude: typeof info.altitude === "number" ? info.altitude : null,
                        altitudeAccuracy: typeof info.altitudeAccuracy === "number" ? info.altitudeAccuracy : null,
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

            // Re-translate dynamic 2.5D HUD, badges, and status pills on live language change
            window.addEventListener("jaguarLanguageChanged", () => {
                if (this.is25dActive) {
                    this.initOverlayBadges();
                    this.updateOverlays();
                } else if (this.wazeDestPin) {
                    const destSpan = this.wazeDestPin.querySelector("[data-dest-pin-label]");
                    if (destSpan) destSpan.textContent = t25d("map.hud25d.dest_pin_label");
                }
                this.syncWazeChrome();
                this.updateLiveCompassButtonUI();
                if (this.labelSimPlay) {
                    this.labelSimPlay.textContent = this.isSimulating
                        ? t25d("map.hud25d.tray_pause")
                        : t25d("map.hud25d.tray_simulate");
                }
                if (this.currentRoute) {
                    this.applyActiveStepUI(this.currentStepIndex);
                    this.updateRouteProgressVisuals(this.routeProgressDistPx || 0);
                } else if (this.focusedBuildingId && this.is25dActive) {
                    this.showBuildingFocusBanner(this.getBuildingData(this.focusedBuildingId));
                } else if (this.is25dActive) {
                    this.showExploreHud();
                } else {
                    if (this.wazeEtaTime) this.wazeEtaTime.textContent = t25d("map.campus_pill");
                    if (this.wazeTripMeta) this.wazeTripMeta.textContent = t25d("map.hud25d.dock_prompt");
                }
            });

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
            const openPlanner = ({ toggleOnMobile = false } = {}) => {
                if (window.innerWidth < 1024) {
                    if (toggleOnMobile && typeof window.toggleMobileNavigation === "function") {
                        window.toggleMobileNavigation();
                    } else if (typeof window.openMobileBottomSheet === "function") {
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
                this.btnWazeSearch.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.btnWazeSearch.blur();
                    openPlanner();
                });
            }

            if (this.wazeBottomCenter) {
                this.wazeBottomCenter.addEventListener("click", (e) => {
                    e.stopPropagation();
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
                    this.btnWazeExpandTray.blur();
                    this.toggleActionTray();
                });
            }

            if (this.btnWazeAudio) {
                this.btnWazeAudio.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.btnWazeAudio.blur();
                    const voiceBtn = document.getElementById("btnVoiceDirections");
                    if (voiceBtn) voiceBtn.click();
                });
            }

            if (this.btnWazeOpenSteps) {
                this.btnWazeOpenSteps.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.btnWazeOpenSteps.blur();
                    this.toggleActionTray(false);
                    if (typeof window.toggleMobileStepsCard === "function") {
                        window.toggleMobileStepsCard();
                    }
                });
            }

            if (this.btnWazeClearRoute) {
                this.btnWazeClearRoute.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.btnWazeClearRoute.blur();
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
                this.wazeSpeedDial.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.wazeSpeedDial.blur();
                    this.setMode(!this.is25dActive);
                });
            }

            if (this.wazeOrangeFab) {
                this.wazeOrangeFab.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.wazeOrangeFab.blur();
                    if (this.currentRoute) {
                        this.isOverview = false;
                        if (!this.is25dActive) {
                            this.setMode(true, { pitch: 52, zoom: this.getResponsiveZoom(2.4), skipDefaultCenter: true });
                        }
                        this.showNavigationBanner();
                        this.recenterOnUser();
                    } else {
                        openPlanner({ toggleOnMobile: true });
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
                    if (this.isFollowingUser && !this.isOverview) {
                        this.currentHeading = this.isHeadingUp ? (this.userSvgHeading || 0) : 0;
                        this.targetHeading = this.currentHeading;
                    }
                    this.applyTransform();
                    this.updateOverlays();
                    this.update2dUserArrow();
                    this.updateCompass(true);
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

            const isInteractiveUiTarget = (target) => {
                if (!target || typeof target.closest !== "function") return false;
                return Boolean(
                    target.closest("button") ||
                    target.closest("a") ||
                    target.closest("input") ||
                    target.closest("#bldgPopover") ||
                    target.closest("#lostFoundPinPopover") ||
                    target.closest(".waze-bldg-badge") ||
                    target.closest("#campusCompass") ||
                    target.closest("#campus25dModeControls") ||
                    target.closest("#mapRightToolbar") ||
                    target.closest("#wazeBottomBar") ||
                    target.closest("#wazeActionTray") ||
                    target.closest("#turnByTurnBanner") ||
                    target.closest("#navigateMapComponent") ||
                    target.closest("#routeResultsCard")
                );
            };

            const onPointerDown = (clientX, clientY, isRotateAction, target) => {
                if (!this.is25dActive) return false;
                if (isInteractiveUiTarget(target)) {
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
                if (isInteractiveUiTarget(e.target)) {
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

            const resetTouchState = (e) => {
                if (!this.is25dActive) return;
                if (!e.touches || e.touches.length === 0) {
                    isPointerDown = false;
                    isPinching = false;
                    if (this.stage) this.stage.classList.remove("no-transition");
                    this.viewport.classList.remove("cursor-grabbing");
                } else if (e.touches.length === 1) {
                    isPinching = false;
                    isPointerDown = true;
                    lastX = e.touches[0].clientX;
                    lastY = e.touches[0].clientY;
                }
            };

            this.viewport.addEventListener("touchend", resetTouchState, { passive: true });
            this.viewport.addEventListener("touchcancel", () => {
                isPointerDown = false;
                isPinching = false;
                if (this.stage) this.stage.classList.remove("no-transition");
                this.viewport.classList.remove("cursor-grabbing");
            }, { passive: true });
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
            if (this.viewport) {
                this.viewport.classList.toggle("campus-route-active", Boolean(this.currentRoute));
            }
            if (this.btnWazeClearRoute) {
                this.btnWazeClearRoute.classList.toggle("hidden", !this.currentRoute);
                this.btnWazeClearRoute.classList.toggle("flex", Boolean(this.currentRoute));
            }
            if (!this.currentRoute) {
                if (this.wazeDialValue) this.wazeDialValue.textContent = this.is25dActive ? "3D" : "2D";
                if (this.wazeDialUnit) this.wazeDialUnit.textContent = this.is25dActive ? t25d("map.hud25d.speed_label_view") : t25d("map.hud25d.speed_label_map");
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
                    if (this.wazeEtaTime) this.wazeEtaTime.textContent = t25d("map.campus_pill");
                    if (this.wazeTripMeta) this.wazeTripMeta.textContent = t25d("map.hud25d.dock_prompt");
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
                    if (c.offsetParent !== null) {
                        c.scrollIntoView({ behavior: "smooth", block: "nearest" });
                    }
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
            const subtitle = rawName.includes("•") ? rawName.split("•")[1].trim() : t25d("map.campus_pill");

            if (this.tbtStepCounter) this.tbtStepCounter.textContent = t25d("map.hud25d.dock_focus_subtitle");
            if (this.tbtStepDistance) this.tbtStepDistance.textContent = cleanName;
            if (this.tbtStepInstruction) this.tbtStepInstruction.textContent = subtitle;

            if (this.tbtNextPreview) {
                this.tbtNextPreview.classList.remove("hidden");
                this.tbtNextPreview.textContent = t25d("map.hud25d.dock_focus_hint");
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
            this.stopSimulation();
            this.cancelUserAnimation();

            this.currentRoute = routeData;
            this.currentStepIndex = 0;
            this.routeUsedGpsOrigin = Boolean(routeData && routeData.usedGpsOrigin);
            this.hasGpsLockOnRoute = false;
            this.initialGpsOnRoute = null;
            this.routeProgressDistPx = 0;
            this.routeProgressRatio = 0;

            const hasSteps = Array.isArray(routeData && routeData.steps) && routeData.steps.length > 0;
            const hasPath = Array.isArray(routeData && routeData.pathCoordinates) && routeData.pathCoordinates.length >= 1;
            if (!routeData || (!hasSteps && !hasPath)) {
                return;
            }

            // Restore human landmark confirm button when switching from building focus back to active route
            if (this.btnTbtConfirmStep && this.btnTbtConfirmStep.parentElement) {
                this.btnTbtConfirmStep.parentElement.classList.remove("hidden");
            }

            // Build dense walkway polyline + step progress spans and draw route polylines
            this.buildActiveRouteIndex(routeData);
            this.drawRoutePolylines(routeData);

            // Seed user navigation arrow cleanly at route start pointing along first walkway segment
            const startSample = this.samplePolylineAtDistance(0);
            if (startSample) {
                this.userSvgX = startSample.x;
                this.userSvgY = startSample.y;
                this.userSvgHeading = startSample.headingDeg;
                this.hasUserPosition = true;
            }

            // Switch to 2.5D Waze-style perspective view (Heading-Up, following user arrow)
            this.isHeadingUp = true;
            this.isFollowingUser = true;
            this.isOverview = false;
            this.updateHeadingControls();
            const routeZoom = this.getResponsiveZoom(2.4);
            if (!this.is25dActive) {
                this.setMode(true, { pitch: 52, zoom: routeZoom, skipDefaultCenter: true });
            } else {
                this.pitch = 52;
                this.zoomScale = routeZoom;
            }

            this.showNavigationBanner();
            this.goToStep(0, { instant: true });
            this.update2dUserArrow();

            // Automatically start continuous live GPS tracking so the user arrow follows real walking progress!
            this.startLiveGpsTracking({ auto: true });

            // If we already hold a fresh on-campus GPS reading (< 15s old), apply it immediately
            if (this.latestGpsCoords && (Date.now() - (this.latestGpsCoords.timestamp || 0)) < 15000) {
                this.handleLiveGpsPosition({
                    coords: {
                        latitude: this.latestGpsCoords.lat,
                        longitude: this.latestGpsCoords.lng,
                        accuracy: this.latestGpsCoords.accuracy,
                        heading: null,
                        speed: null,
                    },
                });
            }
        }

        // ====================================================================
        // ROUTE POLYLINE INDEXING, SAMPLING & PROGRESS VISUALS
        // ====================================================================
        buildActiveRouteIndex(routeData) {
            this.activeRoutePolyline = [];
            this.totalRoutePx = 0;
            this.totalRouteMeters = 0;
            this.stepSpans = [];

            if (!routeData) return;

            let rawPts = [];
            if (Array.isArray(routeData.walkwayPath) && routeData.walkwayPath.length >= 2) {
                rawPts = routeData.walkwayPath.map(pt => ({
                    nodeId: pt.nodeId || null,
                    name: pt.name || "",
                    buildingId: pt.buildingId || null,
                    x: Number(pt.x),
                    y: Number(pt.y),
                    lat: typeof pt.lat === "number" ? pt.lat : null,
                    lng: typeof pt.lng === "number" ? pt.lng : null,
                }));
            } else if (Array.isArray(routeData.pathCoordinates) && routeData.pathCoordinates.length >= 2) {
                if (typeof window.resolveMicroCampusRoute === "function") {
                    const microPts = window.resolveMicroCampusRoute(routeData.pathCoordinates, {
                        accessibleOnly: Boolean(routeData.isAccessibleRoute)
                    });
                    if (Array.isArray(microPts) && microPts.length >= 2) {
                        rawPts = microPts.map(pt => ({
                            nodeId: pt.nodeId || null,
                            name: pt.name || "",
                            buildingId: null,
                            x: Number(pt.x),
                            y: Number(pt.y),
                            lat: null,
                            lng: null,
                        }));
                    }
                }
                if (rawPts.length < 2) {
                    rawPts = routeData.pathCoordinates.map(coord => {
                        const pt = this.resolveSvgPoint(coord);
                        return {
                            nodeId: coord.nodeId || null,
                            name: coord.name || "",
                            buildingId: coord.nodeId || null,
                            x: pt.x,
                            y: pt.y,
                            lat: typeof coord.lat === "number" ? coord.lat : null,
                            lng: typeof coord.lng === "number" ? coord.lng : null,
                        };
                    });
                }
            } else if (Array.isArray(routeData.pathCoordinates) && routeData.pathCoordinates.length === 1) {
                const c0 = routeData.pathCoordinates[0];
                const pt = this.resolveSvgPoint(c0);
                rawPts = [{
                    nodeId: c0.nodeId || null,
                    name: c0.name || "",
                    buildingId: c0.nodeId || null,
                    x: pt.x,
                    y: pt.y,
                    lat: typeof c0.lat === "number" ? c0.lat : null,
                    lng: typeof c0.lng === "number" ? c0.lng : null,
                }];
            }

            if (rawPts.length === 0) return;

            const pxPerMeter = (this.calibration && this.calibration.avgSvgPxPerMeter) || 2.88;
            let cumPx = 0;
            let cumMeters = 0;
            const polyline = [];

            for (let i = 0; i < rawPts.length; i++) {
                const p = rawPts[i];
                let lat = p.lat;
                let lng = p.lng;
                if (lat === null || lng === null) {
                    const inv = this.svgToGps(p.x, p.y);
                    lat = inv.lat;
                    lng = inv.lng;
                }
                if (polyline.length > 0) {
                    const prev = polyline[polyline.length - 1];
                    const segPx = Math.hypot(p.x - prev.x, p.y - prev.y);
                    // Skip exact duplicate consecutive vertices
                    if (segPx < 0.05 && i < rawPts.length - 1) {
                        continue;
                    }
                    const segM = (prev.lat !== null && lat !== null)
                        ? this.haversineMeters(prev.lat, prev.lng, lat, lng)
                        : (segPx / pxPerMeter);
                    cumPx += segPx;
                    cumMeters += Math.max(segPx / pxPerMeter * 0.25, segM);
                }
                polyline.push({
                    nodeId: p.nodeId,
                    name: p.name,
                    buildingId: p.buildingId,
                    x: p.x,
                    y: p.y,
                    lat: lat,
                    lng: lng,
                    cumDistPx: cumPx,
                    cumDistMeters: cumMeters,
                });
            }

            this.activeRoutePolyline = polyline;
            this.totalRoutePx = cumPx;
            this.totalRouteMeters = (routeData.totalDistanceMeters && routeData.totalDistanceMeters > 0)
                ? routeData.totalDistanceMeters
                : cumMeters;

            // Map every step in getActiveStepsList() to its [startDistPx, endDistPx] span along polyline
            const steps = this.getActiveStepsList();
            let cursorIdx = 0;
            const findNearestVertex = (tx, ty, fromIdx) => {
                if (typeof tx !== "number" || typeof ty !== "number") return fromIdx;
                let bestIdx = fromIdx;
                let bestDist = Infinity;
                for (let j = fromIdx; j < polyline.length; j++) {
                    const d = Math.hypot(polyline[j].x - tx, polyline[j].y - ty);
                    if (d < bestDist) {
                        bestDist = d;
                        bestIdx = j;
                    }
                }
                return bestIdx;
            };

            this.stepSpans = steps.map((step, idx) => {
                const isFinal = idx === steps.length - 1;
                if (polyline.length === 1) {
                    return { stepIndex: idx, startDistPx: 0, endDistPx: 0, startVertexIdx: 0, endVertexIdx: 0 };
                }
                if (isFinal) {
                    const lastIdx = polyline.length - 1;
                    return {
                        stepIndex: idx,
                        startDistPx: polyline[lastIdx].cumDistPx,
                        endDistPx: polyline[lastIdx].cumDistPx,
                        startVertexIdx: lastIdx,
                        endVertexIdx: lastIdx,
                    };
                }

                let startV = cursorIdx;
                let endV = cursorIdx;
                const nodeIds = Array.isArray(step.nodeIds) ? step.nodeIds : [];

                if (nodeIds.length > 0) {
                    const firstId = nodeIds[0];
                    const lastId = nodeIds[nodeIds.length - 1];
                    let foundStart = -1;
                    for (let j = cursorIdx; j < polyline.length; j++) {
                        if (polyline[j].nodeId === firstId) {
                            foundStart = j;
                            break;
                        }
                    }
                    startV = foundStart >= 0 ? foundStart : findNearestVertex(step.x, step.y, cursorIdx);

                    let foundEnd = -1;
                    for (let j = startV; j < polyline.length; j++) {
                        if (polyline[j].nodeId === lastId) {
                            foundEnd = j;
                            break;
                        }
                    }
                    endV = foundEnd >= 0
                        ? foundEnd
                        : findNearestVertex(
                            step.targetX !== undefined ? step.targetX : step.x,
                            step.targetY !== undefined ? step.targetY : step.y,
                            startV
                        );
                } else {
                    startV = findNearestVertex(step.x, step.y, cursorIdx);
                    endV = findNearestVertex(
                        step.targetX !== undefined ? step.targetX : step.x,
                        step.targetY !== undefined ? step.targetY : step.y,
                        startV
                    );
                }

                if (endV < startV) endV = startV;
                cursorIdx = endV;

                return {
                    stepIndex: idx,
                    startDistPx: polyline[startV].cumDistPx,
                    endDistPx: polyline[endV].cumDistPx,
                    startVertexIdx: startV,
                    endVertexIdx: endV,
                };
            });
        }

        samplePolylineAtDistance(distPx) {
            const poly = this.activeRoutePolyline;
            if (!poly || poly.length === 0) return null;
            if (poly.length === 1 || this.totalRoutePx <= 0.01) {
                const p0 = poly[0];
                return {
                    x: p0.x,
                    y: p0.y,
                    lat: p0.lat,
                    lng: p0.lng,
                    segIdx: 0,
                    t: 0,
                    headingDeg: this.userSvgHeading || 0,
                    trueBearingDeg: null,
                    distPx: 0,
                    progressRatio: 1,
                };
            }

            const clamped = Math.max(0, Math.min(this.totalRoutePx, distPx));
            let segIdx = 0;
            for (let i = 0; i < poly.length - 1; i++) {
                if (clamped <= poly[i + 1].cumDistPx || i === poly.length - 2) {
                    segIdx = i;
                    break;
                }
            }

            const p1 = poly[segIdx];
            const p2 = poly[segIdx + 1];
            const segLen = Math.max(0.001, p2.cumDistPx - p1.cumDistPx);
            const t = Math.max(0, Math.min(1, (clamped - p1.cumDistPx) / segLen));

            const x = p1.x + (p2.x - p1.x) * t;
            const y = p1.y + (p2.y - p1.y) * t;
            const lat = p1.lat + (p2.lat - p1.lat) * t;
            const lng = p1.lng + (p2.lng - p1.lng) * t;

            // Use a slight lookahead so ultra-short doorway segments don't cause heading flicker
            let aim = p2;
            if (Math.hypot(p2.x - x, p2.y - y) < 8 && segIdx + 2 < poly.length) {
                aim = poly[segIdx + 2];
            } else if (Math.hypot(p2.x - p1.x, p2.y - p1.y) < 1 && segIdx > 0) {
                aim = p1;
            }
            const headingDeg = (Math.hypot(aim.x - x, aim.y - y) >= 0.5)
                ? this.calculateHeadingAngle({ x, y }, aim)
                : this.calculateHeadingAngle(p1, p2);
            const trueBearingDeg = (lat !== null && aim.lat !== null && Math.hypot(aim.x - x, aim.y - y) >= 0.5)
                ? this.calculateCompassBearing(lat, lng, aim.lat, aim.lng)
                : null;

            return {
                x,
                y,
                lat,
                lng,
                segIdx,
                t,
                headingDeg,
                trueBearingDeg,
                distPx: clamped,
                progressRatio: clamped / this.totalRoutePx,
            };
        }

        projectGpsToRoute(lat, lng) {
            const poly = this.activeRoutePolyline;
            if (!poly || poly.length < 2) return null;

            const mPerDegLat = (this.calibration && this.calibration.mPerDegLat) || 111132.0;
            const mPerDegLng = 111320.0 * Math.cos((lat * Math.PI) / 180);

            let best = null;
            let bestScore = Infinity;

            for (let i = 0; i < poly.length - 1; i++) {
                const a = poly[i];
                const b = poly[i + 1];
                if (a.lat === null || a.lng === null || b.lat === null || b.lng === null) continue;

                const ax = (a.lng - lng) * mPerDegLng;
                const ay = (a.lat - lat) * mPerDegLat;
                const bx = (b.lng - lng) * mPerDegLng;
                const by = (b.lat - lat) * mPerDegLat;

                const dx = bx - ax;
                const dy = by - ay;
                const segLenSq = dx * dx + dy * dy;

                let t = 0;
                if (segLenSq > 1e-6) {
                    // Closest point to origin (user GPS at (0, 0)): t = -dot(a, d) / |d|^2
                    t = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / segLenSq));
                }

                const projEast = ax + dx * t;
                const projNorth = ay + dy * t;
                const perpMeters = Math.hypot(projEast, projNorth);

                const candDistPx = a.cumDistPx + (b.cumDistPx - a.cumDistPx) * t;
                // Asymmetric forward-progress continuity bias (like Waze/Google Maps HMM matching):
                // gently favors advancing forward along the route and resists GPS jitter pulling backward,
                // while still allowing genuine backtracking if the user walks >15m back.
                let continuityPenalty = 0;
                if (this.hasGpsLockOnRoute) {
                    const deltaPx = candDistPx - this.routeProgressDistPx;
                    if (deltaPx >= 0) {
                        continuityPenalty = Math.min(4.0, deltaPx * 0.004);
                    } else {
                        continuityPenalty = Math.min(14.0, Math.abs(deltaPx) * 0.06);
                    }
                }
                const score = perpMeters + continuityPenalty;

                if (score < bestScore) {
                    bestScore = score;
                    const x = a.x + (b.x - a.x) * t;
                    const y = a.y + (b.y - a.y) * t;
                    const snapLat = a.lat + (b.lat - a.lat) * t;
                    const snapLng = a.lng + (b.lng - a.lng) * t;

                    let aim = b;
                    if (Math.hypot(b.x - x, b.y - y) < 8 && i + 2 < poly.length) {
                        aim = poly[i + 2];
                    }
                    const headingDeg = (Math.hypot(aim.x - x, aim.y - y) >= 0.5)
                        ? this.calculateHeadingAngle({ x, y }, aim)
                        : this.calculateHeadingAngle(a, b);
                    const trueBearingDeg = (aim.lat !== null)
                        ? this.calculateCompassBearing(snapLat, snapLng, aim.lat, aim.lng)
                        : null;

                    best = {
                        x,
                        y,
                        lat: snapLat,
                        lng: snapLng,
                        perpMeters,
                        cumDistPx: candDistPx,
                        segIdx: i,
                        t,
                        headingDeg,
                        trueBearingDeg,
                        progressRatio: this.totalRoutePx > 0 ? candDistPx / this.totalRoutePx : 1,
                    };
                }
            }

            return best;
        }

        drawRoutePolylines(routeData) {
            if (!routeData) return;
            if (!this.activeRoutePolyline || this.activeRoutePolyline.length === 0) {
                this.buildActiveRouteIndex(routeData);
            }
            this.updateRouteProgressVisuals(this.routeProgressDistPx || 0, { updateMetrics: false });
        }

        updateRouteProgressVisuals(distPx, options = {}) {
            const poly = this.activeRoutePolyline;
            const traveledEl = document.getElementById("route2dTraveledPolyline");
            const shadow = document.getElementById("route2dShadowPolyline");
            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");

            if (!poly || poly.length < 2) {
                const fallbackPts = poly && poly.length === 1
                    ? `${Math.round(poly[0].x)},${Math.round(poly[0].y)} ${Math.round(poly[0].x)},${Math.round(poly[0].y)}`
                    : "";
                if (traveledEl) traveledEl.setAttribute("points", "");
                if (shadow) shadow.setAttribute("points", fallbackPts);
                if (glow) glow.setAttribute("points", fallbackPts);
                if (main) main.setAttribute("points", fallbackPts);
                return;
            }

            const clamped = Math.max(0, Math.min(this.totalRoutePx, distPx || 0));
            this.routeProgressDistPx = clamped;
            this.routeProgressRatio = this.totalRoutePx > 0 ? (clamped / this.totalRoutePx) : 1;

            const showSplit = options.showSplit !== false && clamped > 1.5;
            if (!showSplit) {
                const fullPoints = poly.map(pt => `${Math.round(pt.x)},${Math.round(pt.y)}`).join(" ");
                if (traveledEl) traveledEl.setAttribute("points", "");
                if (shadow) shadow.setAttribute("points", fullPoints);
                if (glow) glow.setAttribute("points", fullPoints);
                if (main) main.setAttribute("points", fullPoints);
            } else {
                const sample = this.samplePolylineAtDistance(clamped);
                const curStr = `${sample.x.toFixed(1)},${sample.y.toFixed(1)}`;
                const traveledPts = [];
                for (let i = 0; i <= sample.segIdx; i++) {
                    traveledPts.push(`${poly[i].x.toFixed(1)},${poly[i].y.toFixed(1)}`);
                }
                traveledPts.push(curStr);

                const remainingPts = [curStr];
                for (let i = sample.segIdx + 1; i < poly.length; i++) {
                    remainingPts.push(`${poly[i].x.toFixed(1)},${poly[i].y.toFixed(1)}`);
                }

                if (traveledEl) traveledEl.setAttribute("points", traveledPts.join(" "));
                const remStr = remainingPts.length >= 2 ? remainingPts.join(" ") : "";
                if (shadow) shadow.setAttribute("points", remStr);
                if (glow) glow.setAttribute("points", remStr);
                if (main) main.setAttribute("points", remStr);
            }

            // Live ETA, dial, and progress bar sync
            if (options.updateMetrics !== false && this.currentRoute) {
                const steps = this.getActiveStepsList();
                const isFinal = this.routeProgressRatio >= 0.985 || (steps.length > 0 && this.currentStepIndex >= steps.length - 1);
                const totalMinutes = Math.max(1, this.currentRoute.estimatedWalkingMinutes || 1);
                const remRatio = Math.max(0, 1 - this.routeProgressRatio);
                const remMinutes = isFinal ? 0 : Math.max(1, Math.ceil(totalMinutes * remRatio));

                if (this.wazeProgressBar) {
                    const pct = isFinal ? 100 : Math.round(this.routeProgressRatio * 100);
                    this.wazeProgressBar.style.width = `${pct}%`;
                }
                if (this.wazeDialValue) {
                    this.wazeDialValue.textContent = isFinal ? "✓" : `~${remMinutes}`;
                }
                if (this.wazeDialUnit) {
                    this.wazeDialUnit.textContent = isFinal ? t25d("map.hud25d.end_short") : t25d("map.hud25d.unit_min");
                }
                if (this.wazeEtaTime) {
                    if (isFinal) {
                        this.wazeEtaTime.textContent = t25d("map.hud25d.arrived_short");
                    } else {
                        const arrivalDate = new Date(Date.now() + remMinutes * 60000);
                        this.wazeEtaTime.textContent = arrivalDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
                    }
                }
                if (this.wazeTripMeta && steps.length > 0) {
                    const step = steps[this.currentStepIndex] || steps[steps.length - 1];
                    const landmark = (step && step.landmark) || t25d("map.campus_pill");
                    const stepsLeft = Math.max(0, steps.length - 1 - this.currentStepIndex);
                    const refLabel = t25d(stepsLeft === 1 ? "map.reference_singular" : "map.reference_plural");
                    this.wazeTripMeta.textContent = isFinal
                        ? `${landmark} • ${t25d("map.hud25d.arrived_destination")}`
                        : `~${remMinutes} ${t25d("map.hud25d.unit_min")} • ${stepsLeft} ${refLabel}`;
                }
            }
        }

        // ====================================================================
        // DECOUPLED USER POSE ANIMATION (GLIDES ARROW + OPTIONAL CAMERA FOLLOW)
        // ====================================================================
        cancelUserAnimation() {
            if (this.userAnimId) {
                cancelAnimationFrame(this.userAnimId);
                this.userAnimId = null;
            }
        }

        setUserPose(x, y, headingDeg, options = {}) {
            this.userSvgX = x;
            this.userSvgY = y;
            if (typeof headingDeg === "number" && Number.isFinite(headingDeg)) {
                this.userSvgHeading = headingDeg;
            }
            this.hasUserPosition = true;

            const shouldFollowCamera = options.syncCamera !== false && this.isFollowingUser && !this.isOverview;
            if (shouldFollowCamera && this.is25dActive) {
                this.currentUserX = x;
                this.currentUserY = y;
                this.targetUserX = x;
                this.targetUserY = y;
                if (this.isHeadingUp) {
                    this.currentHeading = this.userSvgHeading;
                    this.targetHeading = this.userSvgHeading;
                }
                this.applyTransform();
            }

            if (this.is25dActive) {
                this.updateOverlays();
            }
            this.update2dUserArrow();
        }

        animateUserTo(targetX, targetY, targetHeadingDeg, options = {}) {
            this.cancelUserAnimation();
            const duration = options.duration !== undefined ? options.duration : 450;
            const followCamera = options.syncCamera !== false && this.isFollowingUser && !this.isOverview;

            if (followCamera && this.tweenAnimId) {
                cancelAnimationFrame(this.tweenAnimId);
                this.tweenAnimId = null;
            }

            if (duration <= 0 || !this.hasUserPosition) {
                this.setUserPose(targetX, targetY, targetHeadingDeg, { syncCamera: followCamera });
                return;
            }

            const startX = this.userSvgX;
            const startY = this.userSvgY;
            const startH = this.userSvgHeading || 0;
            const destH = typeof targetHeadingDeg === "number" ? targetHeadingDeg : startH;
            const diffH = this.normalizeAngle180(destH - startH);

            const startCamX = this.currentUserX !== undefined ? this.currentUserX : startX;
            const startCamY = this.currentUserY !== undefined ? this.currentUserY : startY;
            const startCamH = this.currentHeading || 0;
            const diffCamH = this.normalizeAngle180(destH - startCamH);

            const startTime = performance.now();
            const frame = (now) => {
                const progress = Math.min(1, (now - startTime) / duration);
                const ease = 1 - Math.pow(1 - progress, 3);

                const curX = startX + (targetX - startX) * ease;
                const curY = startY + (targetY - startY) * ease;
                const curH = startH + diffH * ease;

                this.userSvgX = curX;
                this.userSvgY = curY;
                this.userSvgHeading = curH;
                this.hasUserPosition = true;

                if (this.isFollowingUser && !this.isOverview && this.is25dActive) {
                    this.currentUserX = startCamX + (targetX - startCamX) * ease;
                    this.currentUserY = startCamY + (targetY - startCamY) * ease;
                    this.targetUserX = targetX;
                    this.targetUserY = targetY;
                    if (this.isHeadingUp) {
                        this.currentHeading = startCamH + diffCamH * ease;
                        this.targetHeading = destH;
                    }
                    this.applyTransform();
                }

                if (this.is25dActive) {
                    this.updateOverlays();
                }
                this.update2dUserArrow();

                if (progress < 1) {
                    this.userAnimId = requestAnimationFrame(frame);
                } else {
                    this.userAnimId = null;
                }
            };

            this.userAnimId = requestAnimationFrame(frame);
        }

        animateAlongRoute(fromDistPx, toDistPx, options = {}) {
            this.cancelUserAnimation();
            if (this.tweenAnimId && this.isFollowingUser && !this.isOverview) {
                cancelAnimationFrame(this.tweenAnimId);
                this.tweenAnimId = null;
            }

            const deltaPx = Math.abs(toDistPx - fromDistPx);
            const duration = options.duration !== undefined
                ? options.duration
                : Math.min(950, Math.max(420, deltaPx * 3.2));

            if (duration <= 0 || deltaPx < 0.5 || this.activeRoutePolyline.length < 2) {
                const s = this.samplePolylineAtDistance(toDistPx);
                if (s) {
                    const heading = (this.isLiveCompassActive && this.latestCompassDeg !== null)
                        ? this.userSvgHeading
                        : s.headingDeg;
                    this.setUserPose(s.x, s.y, heading);
                    this.updateRouteProgressVisuals(toDistPx);
                }
                return;
            }

            const startZ = this.zoomScale || this.getResponsiveZoom(2.4);
            const targetZ = this.targetZoomScale !== undefined ? this.targetZoomScale : startZ;
            const startTime = performance.now();

            const frame = (now) => {
                const progress = Math.min(1, (now - startTime) / duration);
                // Smooth ease-in-out along the walkway path
                const ease = progress < 0.5
                    ? 2 * progress * progress
                    : 1 - Math.pow(-2 * progress + 2, 2) / 2;

                const curDist = fromDistPx + (toDistPx - fromDistPx) * ease;
                const sample = this.samplePolylineAtDistance(curDist);
                if (sample) {
                    const desiredH = (this.isLiveCompassActive && this.latestCompassDeg !== null)
                        ? this.userSvgHeading
                        : sample.headingDeg;
                    const diffH = this.normalizeAngle180(desiredH - (this.userSvgHeading || 0));
                    const smoothH = (this.userSvgHeading || 0) + diffH * 0.25;

                    if (this.isFollowingUser && !this.isOverview && this.is25dActive) {
                        this.zoomScale = startZ + (targetZ - startZ) * ease;
                    }
                    this.setUserPose(sample.x, sample.y, smoothH);
                    this.updateRouteProgressVisuals(curDist);
                }

                if (progress < 1) {
                    this.userAnimId = requestAnimationFrame(frame);
                } else {
                    this.userAnimId = null;
                    this.targetZoomScale = undefined;
                    const finalSample = this.samplePolylineAtDistance(toDistPx);
                    if (finalSample) {
                        const finalH = (this.isLiveCompassActive && this.latestCompassDeg !== null)
                            ? this.userSvgHeading
                            : finalSample.headingDeg;
                        this.setUserPose(finalSample.x, finalSample.y, finalH);
                        this.updateRouteProgressVisuals(toDistPx);
                    }
                }
            };

            this.userAnimId = requestAnimationFrame(frame);
        }

        onRouteCleared() {
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.activeRoutePolyline = [];
            this.totalRoutePx = 0;
            this.totalRouteMeters = 0;
            this.stepSpans = [];
            this.routeProgressDistPx = 0;
            this.routeProgressRatio = 0;
            this.routeUsedGpsOrigin = false;
            this.hasGpsLockOnRoute = false;
            this.initialGpsOnRoute = null;

            this.stopSimulation();
            this.cancelUserAnimation();
            this.hideNavigationBanner();
            this.toggleActionTray(false);
            if (this.tbtOrientationCue) {
                this.tbtOrientationCue.classList.add("hidden");
            }

            const traveledEl = document.getElementById("route2dTraveledPolyline");
            const shadow = document.getElementById("route2dShadowPolyline");
            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");
            if (traveledEl) traveledEl.setAttribute("points", "");
            if (shadow) shadow.setAttribute("points", "");
            if (glow) glow.setAttribute("points", "");
            if (main) main.setAttribute("points", "");

            // If user did not explicitly activate live compass mode, stop automatic route GPS watcher
            if (!this.isLiveCompassActive) {
                this.stopLiveGpsTracking();
                this.hasUserPosition = false;
            }

            this.syncWazeChrome();
            this.update2dUserArrow();

            if (this.is25dActive) {
                if (!this.isLiveCompassActive) this.heading = 0;
                this.showExploreHud();
                this.centerOnCampusLowerThird();
            } else {
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = t25d("map.campus_pill");
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = t25d("map.hud25d.dock_prompt");
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
            this.updateLiveCompassButtonUI();
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
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = t25d("map.campus_pill");
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = t25d("map.hud25d.dock_prompt");
                if (this.wazeProgressBar) this.wazeProgressBar.style.width = "0%";
            }
            if (this.wazeActiveRoadPill) {
                this.wazeActiveRoadPill.textContent = t25d("map.campus_pill");
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
        // LIVE GPS ROUTE-MATCHING + OPTIONAL PHONE COMPASS ROTATION
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

        svgToGps(x, y) {
            const c = this.calibration;
            const dx = x - c.cx0;
            const dy = y - c.cy0;
            const det = c.cxN * c.cyE - c.cxE * c.cyN;
            if (Math.abs(det) < 1e-9) return { lat: c.lat0, lng: c.lng0 };
            const mNorth = (dx * c.cyE - c.cxE * dy) / det;
            const mEast = (c.cxN * dy - dx * c.cyN) / det;
            return {
                lat: c.lat0 + mNorth / c.mPerDegLat,
                lng: c.lng0 + mEast / c.mPerDegLng,
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

        calculateCompassBearing(lat1, lng1, lat2, lng2) {
            const toRad = (deg) => (deg * Math.PI) / 180;
            const phi1 = toRad(lat1);
            const phi2 = toRad(lat2);
            const dLng = toRad(lng2 - lng1);
            const y = Math.sin(dLng) * Math.cos(phi2);
            const x = Math.cos(phi1) * Math.sin(phi2) - Math.sin(phi1) * Math.cos(phi2) * Math.cos(dLng);
            return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
        }

        pointToSegmentDistanceMeters(lat, lng, lat1, lng1, lat2, lng2) {
            const latMid = (((lat1 + lat2) / 2) * Math.PI) / 180;
            const mPerDegLat = 111132.954 - 559.822 * Math.cos(2 * latMid);
            const mPerDegLng = 111412.84 * Math.cos(latMid);

            const px = (lng - lng1) * mPerDegLng;
            const py = (lat - lat1) * mPerDegLat;
            const dx = (lng2 - lng1) * mPerDegLng;
            const dy = (lat2 - lat1) * mPerDegLat;
            const segLenSq = dx * dx + dy * dy;
            if (segLenSq === 0) return Math.hypot(px, py);

            const t = Math.max(0, Math.min(1, (px * dx + py * dy) / segLenSq));
            return Math.hypot(px - t * dx, py - t * dy);
        }

        isPointInPolygon(lat, lng, polygon) {
            const n = polygon.length;
            let inside = false;
            let p1 = polygon[0];
            for (let i = 1; i <= n; i++) {
                const p2 = polygon[i % n];
                if (Math.min(p1.lat, p2.lat) < lat && lat <= Math.max(p1.lat, p2.lat)) {
                    if (p1.lat !== p2.lat) {
                        const xinters = ((lat - p1.lat) * (p2.lng - p1.lng)) / (p2.lat - p1.lat) + p1.lng;
                        if (lng <= xinters) {
                            inside = !inside;
                        }
                    }
                }
                p1 = p2;
            }
            return inside;
        }

        isWithinCampusPerimeter(lat, lng, bufferMeters = 40) {
            const polygon = (this.calibration && Array.isArray(this.calibration.perimeter) && this.calibration.perimeter.length >= 3)
                ? this.calibration.perimeter
                : null;
            if (!polygon) return true;
            if (this.isPointInPolygon(lat, lng, polygon)) return true;
            if (bufferMeters > 0) {
                for (let i = 0; i < polygon.length; i++) {
                    const p1 = polygon[i];
                    const p2 = polygon[(i + 1) % polygon.length];
                    if (this.pointToSegmentDistanceMeters(lat, lng, p1.lat, p1.lng, p2.lat, p2.lng) <= bufferMeters) {
                        return true;
                    }
                }
            }
            return false;
        }

        normalizeAngle180(deg) {
            let a = ((deg + 180) % 360 + 360) % 360 - 180;
            return a;
        }

        startLiveGpsTracking(options = {}) {
            if (!navigator.geolocation) {
                this.gpsStatus = "unsupported";
                this.updateLiveCompassButtonUI();
                return;
            }

            this.isLiveGpsActive = true;
            if (this.gpsWatchId !== null) {
                this.updateLiveCompassButtonUI();
                return;
            }

            this.gpsStatus = "searching";
            this.updateLiveCompassButtonUI();

            this.gpsWatchId = navigator.geolocation.watchPosition(
                (pos) => this.handleLiveGpsPosition(pos),
                (err) => {
                    console.warn("Live GPS watchPosition warning:", err && err.message);
                    if (err && err.code === 1) {
                        this.gpsStatus = "denied";
                        this.isLiveGpsActive = false;
                        if (this.gpsWatchId !== null) {
                            navigator.geolocation.clearWatch(this.gpsWatchId);
                            this.gpsWatchId = null;
                        }
                    }
                    this.updateLiveCompassButtonUI();
                },
                { enableHighAccuracy: true, maximumAge: 1500, timeout: 15000 }
            );
        }

        stopLiveGpsTracking() {
            this.isLiveGpsActive = false;
            this.gpsStatus = "idle";
            if (this.gpsWatchId !== null && navigator.geolocation) {
                navigator.geolocation.clearWatch(this.gpsWatchId);
                this.gpsWatchId = null;
            }
            this.updateLiveCompassButtonUI();
        }

        async toggleLiveCompassNavigation() {
            if (this.isLiveCompassActive) {
                this.stopLiveCompassNavigation({ keepGps: Boolean(this.currentRoute) });
            } else {
                await this.startLiveCompassNavigation();
            }
        }

        async startLiveCompassNavigation() {
            this.stopSimulation();
            this.isFollowingUser = true;
            this.isOverview = false;

            if (this.is25dActive) {
                this.isHeadingUp = true;
                this.updateHeadingControls();
            }

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

            // Ensure continuous high-accuracy GPS tracking is running & re-center on user
            this.startLiveGpsTracking({ auto: false });
            if (this.hasUserPosition) {
                this.recenterOnUser();
            }
        }

        stopLiveCompassNavigation(options = {}) {
            this.isLiveCompassActive = false;
            window.removeEventListener("deviceorientationabsolute", this._boundOrientationHandler, true);
            window.removeEventListener("deviceorientation", this._boundOrientationHandler, true);

            if (!options.keepGps) {
                this.stopLiveGpsTracking();
            }
            if (this.tbtOrientationCue) {
                this.tbtOrientationCue.classList.add("hidden");
                this.tbtOrientationCue.classList.remove("flex");
            }
            this.updateLiveCompassButtonUI();
        }

        updateLiveCompassButtonUI() {
            // 1. Top-left 2.5D mode pill button
            if (this.btnLiveCompass) {
                if (this.isLiveCompassActive) {
                    this.btnLiveCompass.classList.remove("text-slate-600", "hover:bg-emerald-50", "bg-sky-50", "text-sky-700");
                    this.btnLiveCompass.classList.add("bg-emerald-500", "text-white", "shadow-xs");
                    if (this.liveCompassDot) this.liveCompassDot.className = "w-2 h-2 rounded-full bg-white animate-pulse";
                    if (this.labelLiveCompass) this.labelLiveCompass.textContent = t25d("map.hud25d.live_badge");
                } else if (this.isLiveGpsActive && this.gpsStatus === "tracking") {
                    this.btnLiveCompass.classList.remove("bg-emerald-500", "text-white", "shadow-xs", "text-slate-600");
                    this.btnLiveCompass.classList.add("bg-sky-50", "text-sky-700", "hover:bg-emerald-50");
                    if (this.liveCompassDot) this.liveCompassDot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
                    if (this.labelLiveCompass) this.labelLiveCompass.textContent = t25d("map.hud25d.gps_label");
                } else {
                    this.btnLiveCompass.classList.remove("bg-emerald-500", "text-white", "shadow-xs", "bg-sky-50", "text-sky-700");
                    this.btnLiveCompass.classList.add("text-slate-600", "hover:bg-emerald-50");
                    if (this.liveCompassDot) {
                        this.liveCompassDot.className = this.gpsStatus === "searching"
                            ? "w-2 h-2 rounded-full bg-amber-400 animate-pulse"
                            : "w-2 h-2 rounded-full bg-slate-300";
                    }
                    if (this.labelLiveCompass) this.labelLiveCompass.textContent = t25d("map.hud25d.live_badge");
                }
            }

            // 2. Always-visible TBT banner live GPS / Compass pill (accessible on mobile < 1024px & desktop!)
            if (this.btnTbtLiveGps) {
                if (this.isLiveCompassActive) {
                    this.btnTbtLiveGps.className = "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500 text-white border border-emerald-600 shadow-2xs transition-colors cursor-pointer";
                    if (this.tbtLiveGpsDot) this.tbtLiveGpsDot.className = "w-1.5 h-1.5 rounded-full bg-white animate-pulse";
                    if (this.labelTbtLiveGps) this.labelTbtLiveGps.textContent = t25d("map.hud25d.live_badge");
                } else if (this.isLiveGpsActive && this.gpsStatus === "tracking") {
                    this.btnTbtLiveGps.className = "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 transition-colors cursor-pointer";
                    if (this.tbtLiveGpsDot) this.tbtLiveGpsDot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse";
                    if (this.labelTbtLiveGps) this.labelTbtLiveGps.textContent = t25d("map.hud25d.gps_active");
                } else if (this.isLiveGpsActive && this.gpsStatus === "searching") {
                    this.btnTbtLiveGps.className = "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-sky-50 hover:bg-emerald-50 text-sky-700 border border-sky-200 transition-colors cursor-pointer";
                    if (this.tbtLiveGpsDot) this.tbtLiveGpsDot.className = "w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse";
                    if (this.labelTbtLiveGps) this.labelTbtLiveGps.textContent = t25d("map.hud25d.gps_searching");
                } else {
                    this.btnTbtLiveGps.className = "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 border border-slate-200 transition-colors cursor-pointer";
                    if (this.tbtLiveGpsDot) this.tbtLiveGpsDot.className = "w-1.5 h-1.5 rounded-full bg-slate-400";
                    if (this.labelTbtLiveGps) this.labelTbtLiveGps.textContent = t25d("map.hud25d.live_badge");
                }
            }
        }

        handleDeviceOrientation(event) {
            if (!this.isLiveCompassActive) return;

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

            // Circular exponential smoothing to keep rotation steady without jitter
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
                    if (!this.isLiveCompassActive) return;

                    // Convert true compass heading to SVG heading (calibrated UAM mapUpTrueBearingDeg = 181.4°)
                    const mapUpBearing = (this.calibration && this.calibration.mapUpTrueBearingDeg) || 181.4;
                    const svgHeading = this.normalizeAngle180(mapUpBearing - this.latestCompassDeg);
                    this.userSvgHeading = svgHeading;

                    if (this.is25dActive) {
                        if (this.isHeadingUp && this.isFollowingUser && !this.isOverview) {
                            this.currentHeading = svgHeading;
                            this.targetHeading = svgHeading;
                            this.applyTransform();
                        }
                        this.updateOverlays();
                        this.updateCompass(false);
                    }
                    this.update2dUserArrow();
                    this.updateOrientationCue();
                });
            }
        }

        handleLiveGpsPosition(pos) {
            if (!this.isLiveGpsActive && !this.isLiveCompassActive) return;
            if (!pos || !pos.coords) return;

            const { latitude, longitude, accuracy, altitude, altitudeAccuracy, heading, speed } = pos.coords;
            if (typeof latitude !== "number" || typeof longitude !== "number" || Number.isNaN(latitude) || Number.isNaN(longitude)) {
                return;
            }

            this.latestGpsCoords = {
                lat: latitude,
                lng: longitude,
                accuracy: typeof accuracy === "number" ? accuracy : 20,
                altitude: typeof altitude === "number" && !Number.isNaN(altitude) ? altitude : null,
                altitudeAccuracy: typeof altitudeAccuracy === "number" && !Number.isNaN(altitudeAccuracy) ? altitudeAccuracy : null,
                timestamp: Date.now(),
            };

            // Reject severely coarse IP / cell-tower fixes (> 85m)
            if (typeof accuracy === "number" && accuracy > 85) return;

            // Validate campus perimeter so off-campus users are never snapped onto the SVG canvas border
            if (!this.isWithinCampusPerimeter(latitude, longitude, 40)) {
                this.gpsStatus = "outside";
                this.updateLiveCompassButtonUI();
                return;
            }

            this.gpsStatus = "tracking";
            this.updateLiveCompassButtonUI();

            // Do not fight an active route simulation preview
            if (this.isSimulating) return;

            const mapUpBearing = (this.calibration && this.calibration.mapUpTrueBearingDeg) || 181.4;
            const rawSvgPt = this.gpsToSvg(latitude, longitude);

            // Track physical walking displacement between GPS anchors for bearing fallback & remote-preview detection
            if (!this.initialGpsOnRoute) {
                this.initialGpsOnRoute = { lat: latitude, lng: longitude };
            }
            const movedSinceStart = this.haversineMeters(
                this.initialGpsOnRoute.lat, this.initialGpsOnRoute.lng,
                latitude, longitude
            );

            let movementSvgHeading = null;
            if (this.lastGpsAnchor) {
                const movedMeters = this.haversineMeters(
                    this.lastGpsAnchor.lat, this.lastGpsAnchor.lng,
                    latitude, longitude
                );
                if (movedMeters >= 2.2) {
                    const moveBearing = this.calculateCompassBearing(
                        this.lastGpsAnchor.lat, this.lastGpsAnchor.lng,
                        latitude, longitude
                    );
                    movementSvgHeading = this.normalizeAngle180(mapUpBearing - moveBearing);
                    this.lastGpsAnchor = { lat: latitude, lng: longitude, x: rawSvgPt.x, y: rawSvgPt.y, timestamp: Date.now() };
                }
            } else {
                this.lastGpsAnchor = { lat: latitude, lng: longitude, x: rawSvgPt.x, y: rawSvgPt.y, timestamp: Date.now() };
            }

            // CASE A: Active Route Navigation -> GPS-space map matching directly onto walkwayPath!
            if (this.currentRoute && this.activeRoutePolyline && this.activeRoutePolyline.length >= 2) {
                const match = this.projectGpsToRoute(latitude, longitude);
                if (!match) return;

                // Activate live tracking onto this route when user:
                // - used GPS as origin, OR explicitly toggled "En vivo", OR is already locked,
                // - OR is within 65m of the route corridor, OR physically started walking (>= 3.5m) on campus!
                const shouldTrackRoute = Boolean(
                    this.isLiveCompassActive ||
                    this.routeUsedGpsOrigin ||
                    this.hasGpsLockOnRoute ||
                    match.perpMeters <= 65 ||
                    movedSinceStart >= 3.5
                );
                if (!shouldTrackRoute) return;
                this.hasGpsLockOnRoute = true;

                // Dynamic snap corridor accounts for GPS accuracy near buildings (16m..30m)
                const snapRadiusMeters = Math.min(30, Math.max(16, (accuracy || 12) * 1.45));
                const isSnappedToRoute = match.perpMeters <= snapRadiusMeters;

                const targetX = isSnappedToRoute ? match.x : rawSvgPt.x;
                const targetY = isSnappedToRoute ? match.y : rawSvgPt.y;

                // Heading priority cascade so the arrow ALWAYS points the direction the user walks:
                // 1. Live phone magnetometer compass (if active)
                // 2. GPS hardware course heading (when moving)
                // 3. Route segment forward tangent (when snapped to route) / computed GPS walking vector
                let targetHeading = this.userSvgHeading || 0;
                const hasValidGpsHeading = typeof heading === "number" && !Number.isNaN(heading) && heading >= 0 &&
                    (speed === null || speed === undefined || Number.isNaN(speed) || speed >= 0.4);

                if (this.isLiveCompassActive && this.smoothedCompassDeg !== null) {
                    targetHeading = this.normalizeAngle180(mapUpBearing - this.smoothedCompassDeg);
                } else if (isSnappedToRoute) {
                    // When walking along the route without compass, align smoothly along the walkway toward destination
                    // (unless GPS explicitly shows user walking backward along the corridor)
                    if (movementSvgHeading !== null) {
                        const diffToRoute = Math.abs(this.normalizeAngle180(movementSvgHeading - match.headingDeg));
                        targetHeading = diffToRoute <= 95 ? match.headingDeg : movementSvgHeading;
                    } else if (hasValidGpsHeading) {
                        const gpsH = this.normalizeAngle180(mapUpBearing - heading);
                        const diffToRoute = Math.abs(this.normalizeAngle180(gpsH - match.headingDeg));
                        targetHeading = diffToRoute <= 95 ? match.headingDeg : gpsH;
                    } else {
                        targetHeading = match.headingDeg;
                    }
                } else if (hasValidGpsHeading) {
                    targetHeading = this.normalizeAngle180(mapUpBearing - heading);
                } else if (movementSvgHeading !== null) {
                    targetHeading = movementSvgHeading;
                } else {
                    // Off-route and stationary: point toward the nearest point on the route
                    targetHeading = this.calculateHeadingAngle({ x: rawSvgPt.x, y: rawSvgPt.y }, { x: match.x, y: match.y });
                }

                // Update traveled/remaining route line & progress metrics
                this.updateRouteProgressVisuals(match.cumDistPx, { showSplit: isSnappedToRoute });

                // Smoothly animate user arrow (and camera if following) to live position
                this.animateUserTo(targetX, targetY, targetHeading, { duration: 480 });

                // Dynamically sync turn-by-turn step from continuous progress & milestone proximity
                this.syncStepFromProgress(latitude, longitude, match);
                this.updateOrientationCue();
                return;
            }

            // CASE B: Explore Mode (no active route) -> live blue user arrow glides across campus
            let exploreHeading = this.userSvgHeading || 0;
            if (this.isLiveCompassActive && this.smoothedCompassDeg !== null) {
                exploreHeading = this.normalizeAngle180(mapUpBearing - this.smoothedCompassDeg);
            } else if (typeof heading === "number" && !Number.isNaN(heading) && heading >= 0 && (speed === null || speed === undefined || speed >= 0.4)) {
                exploreHeading = this.normalizeAngle180(mapUpBearing - heading);
            } else if (movementSvgHeading !== null) {
                exploreHeading = movementSvgHeading;
            }

            this.animateUserTo(rawSvgPt.x, rawSvgPt.y, exploreHeading, { duration: 480 });
        }

        syncStepFromProgress(lat, lng, match) {
            const steps = this.getActiveStepsList();
            if (!steps || steps.length === 0) return;

            let targetStepIdx = this.currentStepIndex;
            const lastIdx = steps.length - 1;

            // 1. Check arrival at outdoor route endpoint / final destination
            // If destination has an indoor entry leg (e.g. room on 2nd floor), advance to the first indoor
            // destination step when arriving at the building door rather than skipping indoor directions.
            let outdoorArrivalStepIdx = lastIdx;
            if (steps[lastIdx] && steps[lastIdx].isIndoor && Array.isArray(this.stepSpans) && this.stepSpans.length === steps.length) {
                for (let k = lastIdx; k >= 0; k--) {
                    if (steps[k].isIndoor && this.stepSpans[k].startDistPx >= this.totalRoutePx - 2) {
                        outdoorArrivalStepIdx = k;
                    } else {
                        break;
                    }
                }
            }

            const finalStep = steps[lastIdx];
            const destLat = (this.activeRoutePolyline.length > 0 ? this.activeRoutePolyline[this.activeRoutePolyline.length - 1].lat : null) ||
                (finalStep && (finalStep.targetLat || finalStep.lat));
            const destLng = (this.activeRoutePolyline.length > 0 ? this.activeRoutePolyline[this.activeRoutePolyline.length - 1].lng : null) ||
                (finalStep && (finalStep.targetLng || finalStep.lng));

            if ((destLat && destLng && this.haversineMeters(lat, lng, destLat, destLng) <= 11.0) ||
                (match && match.progressRatio >= 0.96 && match.perpMeters <= 18)) {
                targetStepIdx = Math.max(this.currentStepIndex, outdoorArrivalStepIdx);
            } else if (match && Array.isArray(this.stepSpans) && this.stepSpans.length === steps.length) {
                // 2. Match current polyline distance to step spans (prefer active outdoor spans when moving)
                const distPx = match.cumDistPx;
                for (let i = 0; i < lastIdx; i++) {
                    const span = this.stepSpans[i];
                    const spanLen = span.endDistPx - span.startDistPx;
                    // Skip completed zero-length origin indoor steps once user has moved along outdoor walkway
                    if (spanLen <= 1 && span.endDistPx <= 1 && distPx > 14) {
                        continue;
                    }
                    // Advance slightly early (~16px ≈ 5.5m) before reaching corner so turn instruction previews smoothly
                    const triggerEnd = spanLen > 24 ? (span.endDistPx - 14) : span.endDistPx;
                    if (distPx <= triggerEnd) {
                        targetStepIdx = i;
                        break;
                    }
                    targetStepIdx = Math.min(lastIdx, i + 1);
                }
            }

            // 3. Fallback GPS proximity check ONLY when polyline spans are unavailable
            if (targetStepIdx < lastIdx && (!Array.isArray(this.stepSpans) || this.stepSpans.length !== steps.length)) {
                const s = steps[targetStepIdx];
                const tLat = s && (s.targetLat || s.lat);
                const tLng = s && (s.targetLng || s.lng);
                if (tLat && tLng && this.haversineMeters(lat, lng, tLat, tLng) <= 8.0) {
                    targetStepIdx = targetStepIdx + 1;
                }
            }

            if (targetStepIdx !== this.currentStepIndex) {
                this.currentStepIndex = targetStepIdx;
                this.applyActiveStepUI(targetStepIdx);
            }
        }

        applyActiveStepUI(stepIndex) {
            const steps = this.getActiveStepsList();
            if (!this.currentRoute || steps.length === 0) return;
            const idx = Math.max(0, Math.min(steps.length - 1, stepIndex));
            const step = steps[idx];
            const nextStep = idx < steps.length - 1 ? steps[idx + 1] : null;

            // Highlight active building badge along the route
            if (this.badgesContainer && step.buildingId) {
                this.badgesContainer.querySelectorAll(".waze-bldg-badge").forEach(badge => {
                    badge.classList.toggle("waze-badge-focused", badge.id === `wazeBadge_${step.buildingId}`);
                });
            }

            // Highlight active step in the sidebar directions panel
            document.querySelectorAll("#routeStepsList li").forEach((li, i) => {
                if (i === idx) {
                    li.classList.add("ring-2", "ring-brand-500", "bg-brand-50/80");
                    li.scrollIntoView({ behavior: "smooth", block: "nearest" });
                } else {
                    li.classList.remove("ring-2", "ring-brand-500", "bg-brand-50/80");
                }
            });

            this.updateBannerUI(idx, steps.length, step, nextStep);
            this.updateOrientationCue();
        }

        updateOrientationCue() {
            if (!this.tbtOrientationCue || !this.tbtOrientationCueText) return;
            const steps = this.getActiveStepsList();
            const step = steps[this.currentStepIndex];

            // Prefer live true bearing of the exact route segment user is walking on
            let targetBearing = null;
            if (this.activeRoutePolyline && this.activeRoutePolyline.length >= 2) {
                const sample = this.samplePolylineAtDistance(this.routeProgressDistPx || 0);
                if (sample && typeof sample.trueBearingDeg === "number") {
                    targetBearing = sample.trueBearingDeg;
                }
            }
            if (targetBearing === null && step && typeof step.nextBearingDeg === "number") {
                targetBearing = step.nextBearingDeg;
            }

            if (!this.isLiveCompassActive || this.latestCompassDeg === null || targetBearing === null || (step && step.maneuver === "arrive")) {
                this.tbtOrientationCue.classList.add("hidden");
                this.tbtOrientationCue.classList.remove("flex");
                return;
            }

            const diff = this.normalizeAngle180(targetBearing - this.latestCompassDeg);
            const absDiff = Math.abs(diff);
            let cueText = "";
            let isAligned = false;

            if (absDiff <= 25) {
                cueText = t25d("map.hud25d.cue_aligned");
                isAligned = true;
            } else if (absDiff >= 145) {
                cueText = t25d("map.hud25d.cue_turn_around");
            } else if (diff > 25 && diff <= 65) {
                cueText = t25d("map.hud25d.cue_slight_right");
            } else if (diff > 65) {
                cueText = t25d("map.hud25d.cue_turn_right");
            } else if (diff < -25 && diff >= -65) {
                cueText = t25d("map.hud25d.cue_slight_left");
            } else {
                cueText = t25d("map.hud25d.cue_turn_left");
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
                    instruction: instructions[idx] || t25d("map.hud25d.step_fallback_advance", { name: c.name || t25d("map.hud25d.next_point_default") }),
                    headline: idx === coords.length - 1 ? t25d("map.hud25d.arrived_headline") : t25d("map.hud25d.default_headline"),
                    maneuver: idx === coords.length - 1 ? "arrive" : "straight",
                    landmark: c.name ? c.name.split("(")[0].trim() : t25d("map.campus_pill"),
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
         * Navigates to a specific human landmark step along the walkway route,
         * smoothly gliding the user arrow along actual walkway segments!
         */
        goToStep(stepIndex, options = {}) {
            const steps = this.getActiveStepsList();
            if (!this.currentRoute || steps.length === 0) return;

            if (stepIndex < 0) stepIndex = 0;
            if (stepIndex >= steps.length) stepIndex = steps.length - 1;
            this.currentStepIndex = stepIndex;

            const step = steps[stepIndex];
            const nextStep = stepIndex < steps.length - 1 ? steps[stepIndex + 1] : null;
            const isFinalStep = stepIndex === steps.length - 1;

            this.pitch = isFinalStep ? 50 : 52;
            this.targetZoomScale = this.getResponsiveZoom(isFinalStep ? 2.75 : 2.42);
            this.isFollowingUser = true;
            this.isOverview = false;

            if (!options.keepLivePosition) {
                const span = this.stepSpans && this.stepSpans[stepIndex];
                if (span && this.activeRoutePolyline && this.activeRoutePolyline.length >= 2 && this.totalRoutePx > 1) {
                    const targetDistPx = span.startDistPx;
                    if (options.instant) {
                        const sample = this.samplePolylineAtDistance(targetDistPx);
                        if (sample) {
                            this.zoomScale = this.targetZoomScale;
                            this.targetZoomScale = undefined;
                            const heading = (this.isLiveCompassActive && this.latestCompassDeg !== null)
                                ? this.userSvgHeading
                                : sample.headingDeg;
                            this.setUserPose(sample.x, sample.y, heading);
                            this.updateRouteProgressVisuals(targetDistPx);
                        }
                    } else {
                        this.animateAlongRoute(this.routeProgressDistPx || 0, targetDistPx);
                    }
                } else {
                    const currentPt = { x: step.x || 600, y: step.y || 425 };
                    const aimPt = (step.targetX !== undefined && (step.targetX !== step.x || step.targetY !== step.y))
                        ? { x: step.targetX, y: step.targetY }
                        : (nextStep ? { x: nextStep.x, y: nextStep.y } : currentPt);

                    let headingDeg = this.userSvgHeading || 0;
                    if (!this.isLiveCompassActive) {
                        if (aimPt.x !== currentPt.x || aimPt.y !== currentPt.y) {
                            headingDeg = this.calculateHeadingAngle(currentPt, aimPt);
                        } else if (stepIndex > 0) {
                            const prevS = steps[stepIndex - 1];
                            headingDeg = this.calculateHeadingAngle({ x: prevS.x, y: prevS.y }, currentPt);
                        }
                    }
                    this.animateUserTo(currentPt.x, currentPt.y, headingDeg, { duration: options.instant ? 0 : 480 });
                }
            }

            this.applyActiveStepUI(stepIndex);
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
            const headline = (step && step.headline) || (isFinal ? t25d("map.hud25d.arrived_headline") : t25d("map.hud25d.default_headline"));
            const instruction = (step && step.instruction) || "";
            const landmark = (step && step.landmark) || t25d("map.campus_pill");

            if (this.tbtStepCounter) {
                this.tbtStepCounter.textContent = t25d("map.hud25d.step_counter", { current: stepIdx + 1, total: totalSteps });
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
                    const nextSummary = nextStep.landmark ? `${nextStep.headline} → ${nextStep.landmark}` : nextStep.headline;
                    this.tbtNextPreview.textContent = t25d("map.hud25d.next_prefix", { text: nextSummary });
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
                        ? t25d("map.hud25d.btn_arrived_next_to", { landmark: nextStep.landmark.slice(0, 22) })
                        : t25d("map.hud25d.btn_arrived_next");
                }
            }

            // Geometric maneuver arrow from backend walkway analysis
            if (this.tbtManeuverIcon) {
                this.tbtManeuverIcon.innerHTML = this.getManeuverIconPath((step && step.maneuver) || "straight");
            }

            // Circular dial & progress bar: use continuous polyline ratio if available, else step ratio
            const totalMinutes = this.currentRoute ? Math.max(1, this.currentRoute.estimatedWalkingMinutes || 1) : 1;
            const progressRatio = (this.totalRoutePx > 1)
                ? (isFinal ? 1 : Math.max(0, Math.min(1, this.routeProgressRatio)))
                : (totalSteps > 1 ? stepIdx / (totalSteps - 1) : 1);
            const remainingRatio = Math.max(0, 1 - progressRatio);
            const remMinutes = isFinal ? 0 : Math.max(1, Math.ceil(totalMinutes * remainingRatio));

            if (this.wazeDialValue) {
                this.wazeDialValue.textContent = isFinal ? "✓" : `~${remMinutes}`;
            }
            if (this.wazeDialUnit) {
                this.wazeDialUnit.textContent = isFinal ? t25d("map.hud25d.end_short") : t25d("map.hud25d.unit_min");
            }

            // Bottom Dock: Arrival clock + human summary (time + landmarks remaining)
            const now = new Date();
            const arrivalDate = new Date(now.getTime() + remMinutes * 60000);
            const timeStr = arrivalDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });

            if (this.wazeEtaTime) {
                this.wazeEtaTime.textContent = isFinal ? t25d("map.hud25d.arrived_short") : timeStr;
            }

            const stepsLeft = Math.max(0, totalSteps - 1 - stepIdx);
            if (this.wazeTripMeta) {
                const refLabel = t25d(stepsLeft === 1 ? "map.reference_singular" : "map.reference_plural");
                const unitMin = t25d("map.hud25d.unit_min");
                this.wazeTripMeta.textContent = isFinal
                    ? `${landmark} • ${t25d("map.hud25d.arrived_destination")}`
                    : `${this.currentRoute.humanDuration || `~${remMinutes} ${unitMin}`} • ${stepsLeft} ${refLabel}`;
            }

            if (this.wazeProgressBar) {
                const progressPct = isFinal ? 100 : Math.round(progressRatio * 100);
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
            if (this.isLiveCompassActive) this.stopLiveCompassNavigation({ keepGps: true });
            this.cancelUserAnimation();

            this.isSimulating = true;
            this.isFollowingUser = true;
            this.isOverview = false;
            if (this.labelSimPlay) this.labelSimPlay.textContent = t25d("map.hud25d.tray_pause");

            // Indoor-only single-point route fallback (step interval)
            if (!this.activeRoutePolyline || this.activeRoutePolyline.length < 2 || this.totalRoutePx <= 1) {
                if (this.currentStepIndex >= steps.length - 1) {
                    this.goToStep(0, { instant: true });
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
                }, 2000);
                return;
            }

            // Smooth continuous walkway walking simulation along every segment & turn!
            if (this.routeProgressDistPx >= this.totalRoutePx - 2 || this.currentStepIndex >= steps.length - 1) {
                this.routeProgressDistPx = 0;
                this.routeProgressRatio = 0;
                this.currentStepIndex = 0;
                this.applyActiveStepUI(0);
            }

            const speedPxPerSec = Math.max(48, Math.min(95, this.totalRoutePx / 9.5));
            this.simLastTimestamp = performance.now();

            const tick = (now) => {
                if (!this.isSimulating || !this.currentRoute) {
                    this.simAnimId = null;
                    return;
                }

                const dtSec = Math.min(0.1, Math.max(0.001, (now - this.simLastTimestamp) / 1000));
                this.simLastTimestamp = now;

                const nextDist = Math.min(this.totalRoutePx, (this.routeProgressDistPx || 0) + speedPxPerSec * dtSec);
                const sample = this.samplePolylineAtDistance(nextDist);
                if (sample) {
                    const diffH = this.normalizeAngle180(sample.headingDeg - (this.userSvgHeading || 0));
                    const smoothH = (this.userSvgHeading || 0) + diffH * Math.min(1, dtSec * 8.5);

                    this.setUserPose(sample.x, sample.y, smoothH);
                    this.updateRouteProgressVisuals(nextDist);

                    // Sync step banner cleanly as the simulated walker crosses each landmark
                    const activeSteps = this.getActiveStepsList();
                    const lastStepIdx = activeSteps.length - 1;
                    let matchedStep = this.currentStepIndex;
                    if (nextDist >= this.totalRoutePx - 1) {
                        matchedStep = lastStepIdx;
                    } else if (Array.isArray(this.stepSpans) && this.stepSpans.length === activeSteps.length) {
                        for (let i = 0; i < lastStepIdx; i++) {
                            const span = this.stepSpans[i];
                            const spanLen = span.endDistPx - span.startDistPx;
                            if (spanLen <= 1 && span.endDistPx <= 1 && nextDist > 8) continue;
                            if (nextDist <= span.endDistPx - 6) {
                                matchedStep = i;
                                break;
                            }
                            matchedStep = Math.min(lastStepIdx, i + 1);
                        }
                    }
                    if (matchedStep !== this.currentStepIndex) {
                        this.currentStepIndex = matchedStep;
                        this.applyActiveStepUI(matchedStep);
                    }
                }

                if (nextDist >= this.totalRoutePx - 0.5) {
                    this.stopSimulation();
                    return;
                }
                this.simAnimId = requestAnimationFrame(tick);
            };

            this.simAnimId = requestAnimationFrame(tick);
        }

        stopSimulation() {
            this.isSimulating = false;
            if (this.labelSimPlay) this.labelSimPlay.textContent = t25d("map.hud25d.tray_simulate");
            if (this.simInterval) {
                clearInterval(this.simInterval);
                this.simInterval = null;
            }
            if (this.simAnimId) {
                cancelAnimationFrame(this.simAnimId);
                this.simAnimId = null;
            }
        }
    }

    // Initialize Global Controller Singleton
    window.campus25dController = new Campus25dController();
})();
