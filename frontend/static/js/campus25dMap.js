/**
 * ================================================================================
 * CAMPUS 2.5D PERSPECTIVE VIEW CONTROLLER (CAMPUS25DMAP.JS)
 * ================================================================================
 * Implements GPU-accelerated 2.5D perspective, tilted camera (pitch 45°/60°),
 * lower-third camera anchoring, and turn-by-turn heading-up navigation.
 *
 * Core Features:
 * 1. 2.5D Perspective Mode: Tilts 2D vector canvas (rotateX) for depth.
 * 2. Lower-Third Camera Anchor: Locks user position at 50% X, 70% Y.
 * 3. Turn-by-Turn Heading-Up: Rotates map (rotateZ) so travel direction faces UP.
 * 4. Step-by-Step Navigation & Simulation Player.
 * 5. Compass Rose orientation synchronization.
 * ================================================================================
 */

(function () {
    "use strict";

    class Campus25dController {
        constructor() {
            // State
            this.is25dActive = false;
            this.pitch = 55; // Default 2.5D pitch in degrees (45° or 60°)
            this.heading = 0; // Rotation around Z axis (in degrees)
            this.isHeadingUp = true;
            this.zoomScale = 1.25;
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.isSimulating = false;
            this.simInterval = null;

            // DOM References
            this.viewport = document.getElementById("campus25dViewport");
            this.stage = document.getElementById("campusMapWrapper");
            this.svg = document.getElementById("officialCampus2dSvg");
            this.horizon = document.getElementById("campusHorizonAtmosphere");
            this.compassRose = document.getElementById("compassRose");

            // 2.5D HUD Elements
            this.btnMode2d = document.getElementById("btnMode2d");
            this.btnMode25d = document.getElementById("btnMode25d");
            this.pitchGroup = document.getElementById("pitchControlGroup");
            this.btnPitch45 = document.getElementById("btnPitch45");
            this.btnPitch60 = document.getElementById("btnPitch60");
            this.headingGroup = document.getElementById("headingControlGroup");
            this.btnToggleHeadingUp = document.getElementById("btnToggleHeadingUp");
            this.iconHeadingMode = document.getElementById("iconHeadingMode");

            // Turn-by-Turn Banner Elements
            this.tbtBanner = document.getElementById("turnByTurnBanner");
            this.tbtStepCounter = document.getElementById("tbtStepCounter");
            this.tbtStepDistance = document.getElementById("tbtStepDistance");
            this.tbtStepInstruction = document.getElementById("tbtStepInstruction");
            this.tbtManeuverIcon = document.getElementById("tbtManeuverIcon");
            this.btnTbtPrev = document.getElementById("btnTbtPrevStep");
            this.btnTbtNext = document.getElementById("btnTbtNextStep");
            this.btnTbtPlay = document.getElementById("btnTbtPlaySimulation");
            this.labelSimPlay = document.getElementById("labelSimPlay");
            this.btnCloseTbt = document.getElementById("btnCloseTbtBanner");

            // Map building coordinates lookup (matches campus2dMap.js)
            this.buildingAnchors = {
                "buildingA": { x: 255, y: 545 },
                "buildingB": { x: 365, y: 585 },
                "buildingC": { x: 395, y: 520 },
                "buildingD": { x: 355, y: 445 },
                "buildingE": { x: 450, y: 635 },
                "buildingF": { x: 510, y: 605 },
                "buildingG": { x: 510, y: 545 },
                "buildingH": { x: 560, y: 460 },
                "buildingI": { x: 645, y: 675 },
                "buildingJ": { x: 300, y: 445 },
                "buildingK": { x: 275, y: 570 },
                "buildingL": { x: 800, y: 585 },
                "buildingM": { x: 565, y: 455 },
                "buildingN": { x: 345, y: 300 },
                "buildingO": { x: 500, y: 245 },
                "buildingP": { x: 355, y: 170 },
                "mainParking": { x: 340, y: 720 },
                "chilamatesPlaza": { x: 240, y: 375 },
                "sportsZone": { x: 725, y: 310 },
                "jaguarCenter": { x: 710, y: 615 },
                "northGate": { x: 400, y: 90 },
                "northeastGate": { x: 740, y: 140 }
            };

            this.init();
        }

        init() {
            if (!this.viewport || !this.stage) {
                // Retry once DOM is fully parsed
                document.addEventListener("DOMContentLoaded", () => this.init());
                return;
            }

            this.bindEvents();
            this.setupUserBeaconLayer();
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

            // Pitch buttons (45° vs 60°)
            if (this.btnPitch45) {
                this.btnPitch45.addEventListener("click", () => this.setPitch(45));
            }
            if (this.btnPitch60) {
                this.btnPitch60.addEventListener("click", () => this.setPitch(60));
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
                    }
                });
            }

            // Turn-by-turn banner controls
            if (this.btnTbtPrev) {
                this.btnTbtPrev.addEventListener("click", () => this.prevStep());
            }
            if (this.btnTbtNext) {
                this.btnTbtNext.addEventListener("click", () => this.nextStep());
            }
            if (this.btnTbtPlay) {
                this.btnTbtPlay.addEventListener("click", () => this.toggleSimulation());
            }
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
                    this.setPitch(this.pitch === 45 ? 60 : 45);
                } else if (e.key.toLowerCase() === "h" && this.is25dActive) {
                    this.isHeadingUp = !this.isHeadingUp;
                    this.updateHeadingControls();
                    this.goToStep(this.currentStepIndex);
                }
            });
        }

        setupUserBeaconLayer() {
            if (!this.svg) return;
            let beaconGroup = document.getElementById("userNavigationBeacon");
            if (!beaconGroup) {
                beaconGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
                beaconGroup.setAttribute("id", "userNavigationBeacon");
                beaconGroup.classList.add("hidden");
                beaconGroup.innerHTML = `
                    <!-- Directional Illumination Cone -->
                    <path id="beaconCone" class="heading-cone" d="M 0 0 L -30 -90 L 30 -90 Z" fill="url(#beaconConeGradient)" />
                    <!-- Outer Pulsing Radar Ring -->
                    <circle id="beaconPulseRing" cx="0" cy="0" r="14" fill="#0284c7" class="beacon-pulse" />
                    <!-- Middle Disc -->
                    <circle cx="0" cy="0" r="10" fill="#0284c7" stroke="#ffffff" stroke-width="2.5" />
                    <!-- Center Core Dot -->
                    <circle cx="0" cy="0" r="4" fill="#ffffff" />
                `;

                // Add gradient definition for the cone
                let defs = this.svg.querySelector("defs");
                if (defs) {
                    const gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
                    gradient.setAttribute("id", "beaconConeGradient");
                    gradient.setAttribute("x1", "0%");
                    gradient.setAttribute("y1", "100%");
                    gradient.setAttribute("x2", "0%");
                    gradient.setAttribute("y2", "0%");
                    gradient.innerHTML = `
                        <stop offset="0%" stop-color="#0284c7" stop-opacity="0.6"/>
                        <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
                    `;
                    defs.appendChild(gradient);
                }

                this.svg.appendChild(beaconGroup);
            }
        }

        /**
         * Toggles between 2D (top-down flat) and 2.5D (perspective tilted) mode
         */
        setMode(enable25d) {
            this.is25dActive = enable25d;

            if (enable25d) {
                this.viewport.classList.add("campus-25d-active");
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

                // If a route exists, center on the current step with heading-up
                if (this.currentRoute) {
                    this.goToStep(this.currentStepIndex);
                } else {
                    // Default bird's-eye oblique view
                    this.pitch = 55;
                    this.heading = 0;
                    this.zoomScale = 1.15;
                    this.centerOnCampusLowerThird();
                }
            } else {
                this.viewport.classList.remove("campus-25d-active");
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
                this.stage.style.transform = "none";
                this.applyTransform();
            }

            this.updateCompass();
        }

        /**
         * Sets camera pitch angle (45° or 60°)
         */
        setPitch(degrees) {
            if (!this.is25dActive) this.setMode(true);
            this.pitch = degrees;

            if (this.btnPitch45 && this.btnPitch60) {
                if (degrees === 45) {
                    this.btnPitch45.classList.add("bg-brand-50", "text-brand-600");
                    this.btnPitch45.classList.remove("text-slate-600");
                    this.btnPitch60.classList.remove("bg-brand-50", "text-brand-600");
                    this.btnPitch60.classList.add("text-slate-600");
                } else {
                    this.btnPitch60.classList.add("bg-brand-50", "text-brand-600");
                    this.btnPitch60.classList.remove("text-slate-600");
                    this.btnPitch45.classList.remove("bg-brand-50", "text-brand-600");
                    this.btnPitch45.classList.add("text-slate-600");
                }
            }

            this.applyTransform();
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

        /**
         * Resolves SVG pixel coordinates (0..1200, 0..850) for a given route coordinate object
         */
        resolveSvgPoint(coord) {
            if (!coord) return { x: 600, y: 425 };
            const known = this.buildingAnchors[coord.nodeId];
            if (known) return { x: known.x, y: known.y };
            return {
                x: Math.round(((coord.xPercent || 50) / 100) * 1200),
                y: Math.round(((coord.yPercent || 50) / 100) * 850)
            };
        }

        /**
         * Calculates walking direction angle (bearing) between two SVG coordinates.
         * Returns rotation needed so vector (p1 -> p2) points straight UP on screen.
         */
        calculateHeadingAngle(p1, p2) {
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            // Screen coordinates have Y positive downwards
            const rad = Math.atan2(dy, dx);
            const deg = rad * (180 / Math.PI);
            // Angle to rotate stage so direction of travel faces upward (-90° screen vector)
            const headingUpRotation = -(deg + 90);
            return headingUpRotation;
        }

        /**
         * Anchors the camera on an SVG coordinate point, placing it in the lower third (50% X, 70% Y)
         */
        anchorToLowerThird(xSvg, ySvg, headingDeg) {
            const vw = this.viewport.clientWidth || 1000;
            const vh = this.viewport.clientHeight || 700;

            // Target anchor location on the screen: 50% X, 70% Y (Lower Third)
            const anchorScreenX = vw * 0.5;
            const anchorScreenY = vh * 0.7;

            // Map SVG coordinates to pixels
            const svgPixelX = (xSvg / 1200) * vw;
            const svgPixelY = (ySvg / 850) * vh;

            const dx = anchorScreenX - svgPixelX;
            const dy = anchorScreenY - svgPixelY;

            this.cameraX = dx;
            this.cameraY = dy;
            this.heading = headingDeg || 0;

            this.applyTransform();
            this.updateCompass();
            this.updateUserBeacon(xSvg, ySvg, headingDeg);
        }

        centerOnCampusLowerThird() {
            // Default center point near Plaza Central / Edificio B (x: 400, y: 500)
            this.anchorToLowerThird(400, 500, 0);
        }

        /**
         * Applies the CSS 3D transformation combining:
         * 1. 3D perspective
         * 2. Tilted camera pitch (rotateX)
         * 3. Heading-up direction (rotateZ)
         * 4. Camera translation & scale
         */
        applyTransform() {
            if (!this.stage) return;

            if (!this.is25dActive) {
                this.stage.style.transform = "";
                return;
            }

            const pitchVal = this.pitch;
            const rotVal = this.isHeadingUp ? this.heading : 0;
            const tx = this.cameraX || 0;
            const ty = this.cameraY || 0;
            const s = this.zoomScale || 1.25;

            // CSS 3D Transform Pipeline
            this.stage.style.transform = `
                perspective(1000px)
                rotateX(${pitchVal}deg)
                rotateZ(${rotVal}deg)
                translate3d(${tx}px, ${ty}px, 0px)
                scale(${s})
            `;
        }

        /**
         * Keeps the Compass Rose synchronized with current map rotation
         */
        updateCompass() {
            if (!this.compassRose) return;
            const compassRot = this.is25dActive && this.isHeadingUp ? -this.heading : 0;
            this.compassRose.style.transform = `rotate(${compassRot}deg)`;
            this.compassRose.style.transition = "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)";
        }

        updateUserBeacon(x, y, headingDeg) {
            const beacon = document.getElementById("userNavigationBeacon");
            const cone = document.getElementById("beaconCone");
            if (!beacon) return;

            beacon.setAttribute("transform", `translate(${x}, ${y})`);
            beacon.classList.remove("hidden");

            if (cone) {
                // Point cone in direction of movement
                cone.setAttribute("transform", `rotate(${-headingDeg})`);
            }
        }

        /**
         * Global Route Calculated Handler
         */
        onRouteCalculated(routeData) {
            this.currentRoute = routeData;
            this.currentStepIndex = 0;

            if (!routeData || !routeData.pathCoordinates || routeData.pathCoordinates.length < 2) return;

            // Automatically switch to 2.5D Perspective Mode for immersive turn-by-turn guidance
            if (!this.is25dActive) {
                this.setMode(true);
            }

            this.showNavigationBanner();
            this.goToStep(0);
        }

        onRouteCleared() {
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.stopSimulation();
            this.hideNavigationBanner();

            const beacon = document.getElementById("userNavigationBeacon");
            if (beacon) beacon.classList.add("hidden");

            if (this.is25dActive) {
                this.heading = 0;
                this.centerOnCampusLowerThird();
            }
        }

        showNavigationBanner() {
            if (this.tbtBanner) {
                this.tbtBanner.classList.remove("hidden");
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
                // At destination, maintain previous segment's bearing
                const prevPt = this.resolveSvgPoint(coords[coords.length - 2]);
                headingDeg = this.calculateHeadingAngle(prevPt, currentPt);
            }

            // Anchor current step in lower third
            this.anchorToLowerThird(currentPt.x, currentPt.y, headingDeg);

            // Update Turn-by-Turn Banner UI
            const instructionText = instructions[stepIndex] || `Avanza hacia ${coords[stepIndex].name || "el punto de ruta"}`;
            this.updateBannerUI(stepIndex, coords.length, instructionText);

            // Update prev/next button states
            if (this.btnTbtPrev) this.btnTbtPrev.disabled = stepIndex === 0;
            if (this.btnTbtNext) this.btnTbtNext.disabled = stepIndex >= coords.length - 1;
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

        updateBannerUI(stepIdx, totalSteps, instruction) {
            if (this.tbtStepCounter) {
                this.tbtStepCounter.textContent = `Paso ${stepIdx + 1} de ${totalSteps}`;
            }
            if (this.tbtStepInstruction) {
                this.tbtStepInstruction.textContent = instruction;
            }

            // Approximate distance for current segment
            if (this.tbtStepDistance && this.currentRoute) {
                const totalMeters = this.currentRoute.totalDistanceMeters || 100;
                const approxStepM = Math.max(15, Math.round(totalMeters / Math.max(1, totalSteps - 1)));
                this.tbtStepDistance.textContent = stepIdx === totalSteps - 1 ? "Destino" : `~${approxStepM} m`;
            }

            // Determine Turn Maneuver Icon
            if (this.tbtManeuverIcon) {
                const lower = instruction.toLowerCase();
                if (stepIdx === totalSteps - 1 || lower.includes("llegado") || lower.includes("destino") || lower.includes("arrived")) {
                    // Destination Flag
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/>`;
                } else if (lower.includes("derecha") || lower.includes("right") || lower.includes("este") || lower.includes("east")) {
                    // Turn Right
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>`;
                } else if (lower.includes("izquierda") || lower.includes("left") || lower.includes("oeste") || lower.includes("west")) {
                    // Turn Left
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>`;
                } else if (lower.includes("escalera") || lower.includes("stairs")) {
                    // Stairs
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19h4v-4h4v-4h4V7h5"/>`;
                } else {
                    // Straight ahead
                    this.tbtManeuverIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19V5m0 0l-5 5m5-5l5 5"/>`;
                }
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
            if (this.labelSimPlay) this.labelSimPlay.textContent = "Pausar";

            // If at end, loop to beginning
            if (this.currentStepIndex >= this.currentRoute.pathCoordinates.length - 1) {
                this.goToStep(0);
            }

            this.simInterval = setInterval(() => {
                if (this.currentStepIndex < this.currentRoute.pathCoordinates.length - 1) {
                    this.nextStep();
                } else {
                    this.stopSimulation();
                }
            }, 2600);
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

    // Export singleton on window
    window.Campus25dController = Campus25dController;
    window.campus25dController = new Campus25dController();

})();
