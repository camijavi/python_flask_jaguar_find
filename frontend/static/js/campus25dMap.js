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
            this.pitch = 48; // Gentle 48° pitch, authentic Waze perspective
            this.heading = 0; // Rotation around Z axis (degrees)
            this.isHeadingUp = true;
            this.zoomScale = 2.2; // Mathematical close zoom so canvas edges bleed off-screen
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.isSimulating = false;
            this.simInterval = null;
            this.isOverview = false;

            // Camera Vector Animation State
            this.cameraGroup = document.getElementById("mapCameraGroup");
            this.currentUserX = undefined;
            this.currentUserY = undefined;
            this.currentHeading = 0;
            this.targetUserX = 400;
            this.targetUserY = 500;
            this.targetHeading = 0;
            this.tweenAnimId = null;

            // DOM References
            this.viewport = document.getElementById("campus25dViewport");
            this.stage = document.getElementById("campusMapWrapper");
            this.svg = document.getElementById("officialCampus2dSvg");
            this.horizon = document.getElementById("campusHorizonAtmosphere");
            this.compassRose = document.getElementById("compassRose");

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

            // Waze Top Banner Elements
            this.tbtBanner = document.getElementById("turnByTurnBanner");
            this.tbtStepCounter = document.getElementById("tbtStepCounter");
            this.tbtStepDistance = document.getElementById("tbtStepDistance");
            this.tbtStepInstruction = document.getElementById("tbtStepInstruction");
            this.tbtNextPreview = document.getElementById("tbtNextPreview");
            this.tbtManeuverIcon = document.getElementById("tbtManeuverIcon");
            this.btnCloseTbt = document.getElementById("btnCloseTbtBanner");

            // Waze Bottom Trip Summary Elements
            this.wazeBottomBar = document.getElementById("wazeBottomBar");
            this.wazeEtaTime = document.getElementById("wazeEtaTime");
            this.wazeTripMeta = document.getElementById("wazeTripMeta");
            this.wazeProgressBar = document.getElementById("wazeProgressBar");
            this.btnWazeRecenter = document.getElementById("btnWazeRecenter");
            this.btnWazeOverview = document.getElementById("btnWazeOverview");
            this.btnTbtPlay = document.getElementById("btnTbtPlaySimulation");
            this.labelSimPlay = document.getElementById("labelSimPlay");

            // Map building coordinates lookup (matches campus2dMap.js)
            this.buildingAnchors = {
                "buildingA": { x: 252, y: 459 },
                "buildingB": { x: 390, y: 490 },
                "buildingC": { x: 390, y: 427 },
                "buildingD": { x: 351, y: 335 },
                "buildingE": { x: 458, y: 620 },
                "buildingF": { x: 517, y: 628 },
                "buildingG": { x: 517, y: 558 },
                "buildingH": { x: 572, y: 383 },
                "buildingI": { x: 635, y: 715 },
                "buildingJ": { x: 297, y: 332 },
                "buildingK": { x: 285, y: 582 },
                "buildingL": { x: 842, y: 502 },
                "buildingM": { x: 567, y: 460 },
                "buildingN": { x: 350, y: 262 },
                "buildingO": { x: 510, y: 200 },
                "buildingP": { x: 360, y: 104 },
                "mainParking": { x: 340, y: 800 },
                "chilamatesPlaza": { x: 225, y: 332 },
                "sportsZone": { x: 762, y: 357 },
                "jaguarCenter": { x: 735, y: 510 },
                "northGate": { x: 340, y: 60 },
                "northeastGate": { x: 720, y: 60 }
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
                "sportsZone": "S", "jaguarCenter": "JC"
            };
            const nameMap = {
                "buildingA": "Edificio A", "buildingB": "Edificio B", "buildingC": "Edificio C",
                "buildingD": "Edificio D", "buildingE": "Edificio E", "buildingF": "Edificio F",
                "buildingG": "Edificio G", "buildingH": "Edificio H", "buildingI": "Edificio I",
                "buildingJ": "Edificio J", "buildingK": "Edificio K", "buildingL": "Edificio L",
                "buildingM": "Edificio M", "buildingN": "Edificio N", "buildingO": "Edificio O",
                "buildingP": "Edificio P", "sportsZone": "Campos Deportivos", "jaguarCenter": "Jaguar Center"
            };
            const colorMap = {
                "buildingA": "#6b21a8", "buildingB": "#1e3a8a", "buildingC": "#1e3a8a",
                "buildingD": "#15803d", "buildingE": "#0284c7", "buildingF": "#be185d",
                "buildingG": "#0284c7", "buildingH": "#15803d", "buildingI": "#1e3a8a",
                "buildingJ": "#0284c7", "buildingK": "#b45309", "buildingL": "#0284c7",
                "buildingM": "#b45309", "buildingN": "#6b21a8", "buildingO": "#b45309",
                "buildingP": "#be185d", "sportsZone": "#15803d", "jaguarCenter": "#0f766e"
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
                badgeEl.className = "waze-bldg-badge";
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
                    if (nodeId === "buildingP" && typeof window.openBuildingPIsometricModal === "function") {
                        window.openBuildingPIsometricModal();
                    } else if (typeof window.showBuildingPopover === "function") {
                        window.showBuildingPopover(bldgData, anchor);
                    }
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
                    if (this.currentRoute) {
                        this.goToStep(this.currentStepIndex);
                    } else {
                        this.heading = 0;
                        this.applyTransform();
                        this.updateOverlays();
                        this.updateCompass(true);
                    }
                });
            }

            // Waze Re-center button (anchors camera back to user lower third)
            if (this.btnWazeRecenter) {
                this.btnWazeRecenter.addEventListener("click", () => {
                    this.isOverview = false;
                    this.pitch = 48;
                    this.zoomScale = 2.2;
                    if (this.currentRoute) {
                        this.goToStep(this.currentStepIndex);
                    } else {
                        this.centerOnCampusLowerThird();
                    }
                });
            }

            // Waze Overview button (toggles follow mode vs full campus overview)
            if (this.btnWazeOverview) {
                this.btnWazeOverview.addEventListener("click", () => {
                    this.isOverview = !this.isOverview;
                    if (this.isOverview) {
                        this.pitch = 35;
                        this.zoomScale = 1.15;
                        this.anchorToLowerThird(500, 430, 0, true);
                    } else {
                        this.pitch = 48;
                        this.zoomScale = 2.2;
                        if (this.currentRoute) {
                            this.goToStep(this.currentStepIndex);
                        } else {
                            this.centerOnCampusLowerThird();
                        }
                    }
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
                if (target && (target.closest("button") || target.closest("#bldgPopover") || target.closest(".waze-bldg-badge") || target.closest("#campusCompass"))) {
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

                // Mathematical inverse 2.5D perspective projection
                const vw = this.viewport.clientWidth || 1000;
                const vh = this.viewport.clientHeight || 700;
                const s = Math.min(vw / 1200, vh / 850);
                const zoom = this.zoomScale || 2.2;
                const pitchRad = ((this.pitch || 48) * Math.PI) / 180;
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
         * Toggles between 2D (top-down flat) and 2.5D (perspective tilted) mode
         */
        setMode(enable25d) {
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

                // Clear 2D transform on SVG element so #mapCameraGroup controls the viewport
                if (this.svg) this.svg.style.transform = "none";

                // Waze defaults
                this.pitch = 48; // Gentle 48° pitch
                this.zoomScale = 2.2; // Close zoom calculated mathematically inside SVG

                if (this.currentRoute) {
                    this.showNavigationBanner();
                    this.goToStep(this.currentStepIndex);
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
                this.viewport.classList.remove("campus-25d-active");
                if (this.overlayLayer) this.overlayLayer.classList.add("hidden");
                if (this.wazeBottomBar) this.wazeBottomBar.classList.add("hidden");
                if (this.tbtBanner) this.tbtBanner.classList.add("hidden");

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

                this.pitch = 0;
                this.heading = 0;
                this.zoomScale = 1;
                this.currentUserX = undefined;
                this.currentUserY = undefined;
                this.currentHeading = 0;
                this.stage.style.transform = "";

                if (this.cameraGroup) {
                    this.cameraGroup.removeAttribute("transform");
                }

                if (typeof window.updateCampusCompass === "function") {
                    window.updateCampusCompass(0, true);
                }
            }

            this.updateCompass();
        }

        /**
         * Sets camera pitch angle (45° or 52°)
         */
        setPitch(degrees) {
            if (!this.is25dActive) this.setMode(true);
            this.pitch = degrees;

            if (this.btnPitch45 && this.btnPitch52) {
                if (degrees === 45) {
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

        startCameraTween() {
            if (this.tweenAnimId) {
                cancelAnimationFrame(this.tweenAnimId);
                this.tweenAnimId = null;
            }

            const startX = this.currentUserX;
            const startY = this.currentUserY;
            const startH = this.currentHeading;
            const targetX = this.targetUserX;
            const targetY = this.targetUserY;
            const targetH = this.targetHeading;

            // Shortest turn interpolation
            let diffH = (targetH - startH) % 360;
            if (diffH < -180) diffH += 360;
            if (diffH > 180) diffH -= 360;

            const startTime = performance.now();
            const duration = 400; // ms

            const step = (now) => {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = 1 - Math.pow(1 - progress, 3); // Smooth cubic ease-out

                this.currentUserX = startX + (targetX - startX) * ease;
                this.currentUserY = startY + (targetY - startY) * ease;
                this.currentHeading = startH + diffH * ease;

                this.applyTransform();
                this.updateOverlays();
                this.updateCompass(false);

                if (progress < 1) {
                    this.tweenAnimId = requestAnimationFrame(step);
                } else {
                    this.tweenAnimId = null;
                }
            };

            this.tweenAnimId = requestAnimationFrame(step);
        }

        centerOnCampusLowerThird() {
            // Default center point near Plaza Central / Edificio B (x: 400, y: 500)
            this.anchorToLowerThird(400, 500, 0, false);
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
            const anchorX = (vw * 0.50 - offX) / s;
            const anchorY = (vh * 0.70 - offY) / s;

            const uX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const uY = this.currentUserY !== undefined ? this.currentUserY : 500;
            const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
            const zoom = this.zoomScale || 2.2;
            const pitch = this.pitch || 48;

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

            // 3. 3D perspective projection with pivot at (vw*0.5, vh*0.70)
            const Cx = vw * 0.5;
            const Cy = vh * 0.70;

            const X = x0 - Cx;
            const Y = y0 - Cy;

            const phi = (pitch * Math.PI) / 180;
            const X_prime = X;
            const Y_prime = Y * Math.cos(phi);
            const Z_prime = Y * Math.sin(phi); // negative into screen for Y < 0

            const d = 1000.0;
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

            // 1. Position Upright Building Badges
            for (const [nodeId, anchor] of Object.entries(this.buildingAnchors)) {
                const badgeEl = document.getElementById(`wazeBadge_${nodeId}`);
                if (!badgeEl) continue;

                const pos = this.projectToScreen(anchor.x, anchor.y);
                if (pos && pos.y >= 30 && pos.y <= vh - 20 && pos.x >= -60 && pos.x <= vw + 60) {
                    badgeEl.style.display = "inline-flex";
                    badgeEl.style.left = `${pos.x.toFixed(1)}px`;
                    badgeEl.style.top = `${pos.y.toFixed(1)}px`;
                    const scaleFactor = Math.min(1.05, Math.max(0.68, pos.k * 0.95));
                    badgeEl.style.transform = `translate(-50%, -50%) scale(${scaleFactor.toFixed(3)})`;
                    const horizonFade = Math.min(1.0, Math.max(0.0, (pos.y - 25) / 50));
                    badgeEl.style.opacity = horizonFade.toFixed(2);
                } else {
                    badgeEl.style.display = "none";
                }
            }

            // 2. Rotate Navigation Puck Arrow
            if (this.puckArrow) {
                // In Heading-Up mode, arrow points straight UP (0°). In North-Up, arrow points along bearing.
                const arrowRot = this.isHeadingUp ? 0 : -(this.currentHeading || 0);
                this.puckArrow.style.transform = `rotate(${arrowRot.toFixed(2)}deg)`;
                if (this.puckCone) {
                    this.puckCone.style.transform = `rotate(${arrowRot.toFixed(2)}deg)`;
                }
            }

            // 3. Position Destination & Origin Pins
            if (this.currentRoute && this.currentRoute.pathCoordinates && this.currentRoute.pathCoordinates.length >= 2) {
                const coords = this.currentRoute.pathCoordinates;
                const endPt = this.resolveSvgPoint(coords[coords.length - 1]);
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

                const startPt = this.resolveSvgPoint(coords[0]);
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
        }

        /**
         * Crisp Vector 2.5D Transform Pipeline:
         * 1. rotateX(pitch) strictly on outer wrapper (CSS 3D perspective plane)
         * 2. translate + scale(2.2) + rotate strictly inside SVG <g id="mapCameraGroup">
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

            const pitch = this.pitch || 48;
            const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
            const zoom = this.zoomScale || 2.2;
            const uX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const uY = this.currentUserY !== undefined ? this.currentUserY : 500;

            const vw = this.viewport ? (this.viewport.clientWidth || 1000) : 1000;
            const vh = this.viewport ? (this.viewport.clientHeight || 700) : 700;
            const s = Math.min(vw / 1200, vh / 850);
            const offX = (vw - 1200 * s) / 2;
            const offY = (vh - 850 * s) / 2;
            const anchorX = (vw * 0.50 - offX) / s;
            const anchorY = (vh * 0.70 - offY) / s;

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
            this.zoomScale = Math.min((this.zoomScale || 2.2) + 0.25, 3.5);
            this.applyTransform();
            this.updateOverlays();
        }

        zoomOut() {
            this.zoomScale = Math.max((this.zoomScale || 2.2) - 0.25, 1.15);
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

            if (!routeData || !routeData.pathCoordinates || routeData.pathCoordinates.length < 2) return;

            // Ensure route polyline points are populated in SVG
            this.drawRoutePolylines(routeData);

            // Automatically switch to Waze-style 2.5D navigation view
            if (!this.is25dActive) {
                this.setMode(true);
            }

            this.showNavigationBanner();
            this.goToStep(0);
        }

        drawRoutePolylines(routeData) {
            if (!routeData || !routeData.pathCoordinates) return;
            const points = routeData.pathCoordinates.map(coord => {
                const pt = this.resolveSvgPoint(coord);
                return `${pt.x},${pt.y}`;
            }).join(" ");

            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");
            if (glow) glow.setAttribute("points", points);
            if (main) main.setAttribute("points", points);
        }

        onRouteCleared() {
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.stopSimulation();
            this.hideNavigationBanner();

            const glow = document.getElementById("route2dGlowPolyline");
            const main = document.getElementById("route2dPolyline");
            if (glow) glow.setAttribute("points", "");
            if (main) main.setAttribute("points", "");

            if (this.is25dActive) {
                this.heading = 0;
                this.showExploreHud();
                this.centerOnCampusLowerThird();
            }
        }

        showNavigationBanner() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.remove("hidden");
            }
            if (this.wazeBottomBar) {
                this.wazeBottomBar.classList.remove("hidden");
            }
        }

        showExploreHud() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.remove("hidden");
                if (this.tbtStepCounter) this.tbtStepCounter.textContent = "Modo 2.5D";
                if (this.tbtStepDistance) this.tbtStepDistance.textContent = "Waze";
                if (this.tbtStepInstruction) this.tbtStepInstruction.textContent = "Explorando Campus UAM • Rumbo al frente";
                if (this.tbtNextPreview) this.tbtNextPreview.classList.add("hidden");
                if (this.tbtManeuverIcon) {
                    this.tbtManeuverIcon.innerHTML = `<polygon points="12 2 19 21 12 17 5 21 12 2" stroke-width="2" stroke-linejoin="round"/>`;
                }
            }
            if (this.wazeBottomBar) {
                this.wazeBottomBar.classList.remove("hidden");
                if (this.wazeEtaTime) this.wazeEtaTime.textContent = "Campus UAM";
                if (this.wazeTripMeta) this.wazeTripMeta.textContent = "Selecciona un edificio para trazar ruta";
                if (this.wazeProgressBar) this.wazeProgressBar.style.width = "0%";
            }
        }

        hideNavigationBanner() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.add("hidden");
            }
            this.stopSimulation();
        }

        /**
         * Navigates to a specific step along the route
         */
        goToStep(stepIndex) {
            if (!this.currentRoute || !this.currentRoute.pathCoordinates) return;
            const coords = this.currentRoute.pathCoordinates;
            const instructions = this.currentRoute.stepInstructions || [];

            if (stepIndex < 0) stepIndex = 0;
            if (stepIndex >= coords.length) stepIndex = coords.length - 1;
            this.currentStepIndex = stepIndex;

            const currentPt = this.resolveSvgPoint(coords[stepIndex]);
            const nextPt = stepIndex < coords.length - 1
                ? this.resolveSvgPoint(coords[stepIndex + 1])
                : (coords.length > 1 ? this.resolveSvgPoint(coords[stepIndex - 1]) : currentPt);

            // Compute segment bearing
            let headingDeg = 0;
            if (stepIndex < coords.length - 1) {
                headingDeg = this.calculateHeadingAngle(currentPt, nextPt);
            } else if (coords.length > 1) {
                const prevPt = this.resolveSvgPoint(coords[coords.length - 2]);
                headingDeg = this.calculateHeadingAngle(prevPt, currentPt);
            }

            // Anchor current step in lower third (70% down)
            this.anchorToLowerThird(currentPt.x, currentPt.y, headingDeg);

            // Update Turn-by-Turn Banner & Bottom Trip Summary
            const instructionText = instructions[stepIndex] || `Avanza hacia ${coords[stepIndex].name || "el punto de ruta"}`;
            const nextInstruction = stepIndex < instructions.length - 1 ? instructions[stepIndex + 1] : null;
            this.updateBannerUI(stepIndex, coords.length, instructionText, nextInstruction);
        }

        nextStep() {
            if (!this.currentRoute) return;
            if (this.currentStepIndex < this.currentRoute.pathCoordinates.length - 1) {
                this.goToStep(this.currentStepIndex + 1);
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

        updateBannerUI(stepIdx, totalSteps, instruction, nextInstruction) {
            if (this.tbtStepCounter) {
                this.tbtStepCounter.textContent = `Paso ${stepIdx + 1} de ${totalSteps}`;
            }
            if (this.tbtStepInstruction) {
                this.tbtStepInstruction.textContent = instruction;
            }

            const totalMeters = this.currentRoute ? (this.currentRoute.totalDistanceMeters || 140) : 140;
            const stepsRemaining = Math.max(0, totalSteps - 1 - stepIdx);
            const remainingMeters = Math.round((stepsRemaining / Math.max(1, totalSteps - 1)) * totalMeters);

            if (this.tbtStepDistance) {
                const approxStepM = Math.max(15, Math.round(totalMeters / Math.max(1, totalSteps - 1)));
                this.tbtStepDistance.textContent = stepIdx === totalSteps - 1 ? "Meta" : `${approxStepM} m`;
            }

            if (this.tbtNextPreview) {
                if (nextInstruction) {
                    this.tbtNextPreview.textContent = `Luego: ${nextInstruction.replace(/^(\d+\.\s*)/, '').slice(0, 42)}...`;
                    this.tbtNextPreview.classList.remove("hidden");
                } else {
                    this.tbtNextPreview.classList.add("hidden");
                }
            }

            // Determine Turn Maneuver Icon
            if (this.tbtManeuverIcon) {
                const lower = instruction.toLowerCase();
                if (stepIdx === totalSteps - 1 || lower.includes("llegado") || lower.includes("destino") || lower.includes("arrived")) {
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/>`;
                } else if (lower.includes("derecha") || lower.includes("right") || lower.includes("este") || lower.includes("east")) {
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>`;
                } else if (lower.includes("izquierda") || lower.includes("left") || lower.includes("oeste") || lower.includes("west")) {
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>`;
                } else if (lower.includes("escalera") || lower.includes("stairs")) {
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19h4v-4h4v-4h4V7h5"/>`;
                } else {
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19V5m0 0l-5 5m5-5l5 5"/>`;
                }
            }

            // Update Waze Bottom Trip Summary Bar
            if (this.wazeEtaTime) {
                const estMinutes = Math.max(1, Math.ceil(remainingMeters / 50));
                this.wazeEtaTime.textContent = stepIdx === totalSteps - 1 ? "Llegaste" : `${estMinutes} min`;
            }

            if (this.wazeTripMeta) {
                const now = new Date();
                const arrivalDate = new Date(now.getTime() + Math.max(1, Math.ceil(remainingMeters / 50)) * 60000);
                const timeStr = arrivalDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                this.wazeTripMeta.textContent = `${remainingMeters} m • Llegada aprox. ${timeStr}`;
            }

            if (this.wazeProgressBar) {
                const progressPct = totalSteps > 1 ? Math.round((stepIdx / (totalSteps - 1)) * 100) : 100;
                this.wazeProgressBar.style.width = `${progressPct}%`;
            }
        }

        toggleSimulation() {
            if (this.isSimulating) {
                this.stopSimulation();
            } else {
                this.startSimulation();
            }
        }

        startSimulation() {
            if (!this.currentRoute) return;
            this.isSimulating = true;
            if (this.labelSimPlay) this.labelSimPlay.textContent = "Pausa";

            if (this.currentStepIndex >= this.currentRoute.pathCoordinates.length - 1) {
                this.goToStep(0);
            }

            if (this.simInterval) clearInterval(this.simInterval);
            this.simInterval = setInterval(() => {
                if (!this.currentRoute) {
                    this.stopSimulation();
                    return;
                }

                if (this.currentStepIndex < this.currentRoute.pathCoordinates.length - 1) {
                    this.nextStep();
                } else {
                    this.stopSimulation();
                }
            }, 3000);
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
