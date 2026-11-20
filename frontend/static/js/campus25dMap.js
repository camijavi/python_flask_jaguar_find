/**
 * ================================================================================
 * CAMPUS 2.5D PERSPECTIVE VIEW CONTROLLER (CAMPUS25DMAP.JS)
 * ================================================================================
 * Implements GPU-accelerated Waze-like 2.5D perspective navigation view:
 * 1. Gentle camera pitch (45°–52°, default 48°) to avoid excessive compression.
 * 2. Close zoom (scale 2.2) so map edges bleed off-screen (no "flying carpet").
 * 3. Lower-Third camera anchor: Locks user position at 50% X, 72% Y.
 * 4. Billboarding: Labels, building badges, and destination pins counter-rotate
 *    and un-squash so they remain upright, readable, and face the camera.
 * 5. Elevated 3D navigation elements (puck with ground shadow & raised chevron,
 *    route line extrusion, standing 3D flag pins).
 * ================================================================================
 */

(function () {
    "use strict";

    class Campus25dController {
        constructor() {
            // Waze-Style Navigation Defaults
            this.is25dActive = false;
            this.pitch = 48; // Gentle tilt (48°), avoids vertical squashing
            this.heading = 0; // Rotation around Z axis (degrees)
            this.isHeadingUp = true;
            this.zoomScale = 2.2; // Zoomed in mathematically so canvas edges bleed completely off-screen
            this.currentRoute = null;
            this.currentStepIndex = 0;
            this.isSimulating = false;
            this.simInterval = null;

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

            // 2.5D HUD Elements
            this.btnMode2d = document.getElementById("btnMode2d");
            this.btnMode25d = document.getElementById("btnMode25d");
            this.pitchGroup = document.getElementById("pitchControlGroup");
            this.btnPitch45 = document.getElementById("btnPitch45");
            this.btnPitch52 = document.getElementById("btnPitch52") || document.getElementById("btnPitch60");
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
            this.setupUserBeaconLayer();

            // Handle window resize dynamically to preserve lower-third user anchor
            window.addEventListener("resize", () => {
                if (this.is25dActive) {
                    if (this.currentRoute) {
                        this.goToStep(this.currentStepIndex);
                    } else {
                        this.centerOnCampusLowerThird();
                    }
                }
            });
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
                    this.setPitch(this.pitch === 45 ? 52 : 45);
                } else if (e.key.toLowerCase() === "h" && this.is25dActive) {
                    this.isHeadingUp = !this.isHeadingUp;
                    this.updateHeadingControls();
                    this.goToStep(this.currentStepIndex);
                }
            });
        }

        /**
         * Elevated 3D Navigation Puck (Waze-Style)
         * - Ground contact shadow ellipse
         * - Pulsing radar accuracy ring
         * - Forward illumination cone
         * - Raised puck disk with drop shadow and sharp forward navigation chevron
         */
        setupUserBeaconLayer() {
            if (!this.svg) return;
            let beaconGroup = document.getElementById("userNavigationBeacon");
            if (!beaconGroup) {
                beaconGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
                beaconGroup.setAttribute("id", "userNavigationBeacon");
                beaconGroup.classList.add("hidden");
                beaconGroup.innerHTML = `
                    <!-- 1. Ground Contact Shadow (Soft dark ellipse on asphalt) -->
                    <ellipse cx="0" cy="4" rx="18" ry="9" fill="#0f172a" opacity="0.4" />
                    <!-- 2. Radar Accuracy Pulse Ring on Ground -->
                    <circle cx="0" cy="0" r="14" fill="#0284c7" opacity="0.3" class="beacon-pulse" />
                    <!-- 3. Forward Directional Illumination Beam -->
                    <path id="beaconCone" class="heading-cone" d="M 0 0 L -30 -90 L 30 -90 Z" fill="url(#beaconConeGradient)" />
                    <!-- 4. Elevated 3D Navigation Puck (Counter-tilted & Raised above Ground) -->
                    <g id="puckElevatedBody" class="billboard-puck">
                        <!-- Drop Shadow under raised puck disk -->
                        <circle cx="0" cy="-2" r="13" fill="#0369a1" opacity="0.35" filter="url(#bldgShadow)" />
                        <!-- Beveled Outer White Rim -->
                        <circle cx="0" cy="-5" r="13" fill="#ffffff" filter="url(#bldgShadow)" />
                        <!-- Core Brand Blue Disk -->
                        <circle cx="0" cy="-5" r="10.5" fill="#0284c7" />
                        <!-- Forward Direction Navigation Chevron (White Arrow) -->
                        <path d="M 0 -11 L 5 -2 L 0 -4 L -5 -2 Z" fill="#ffffff" />
                    </g>
                `;

                // Add gradient definition for the forward beam
                let defs = this.svg.querySelector("defs");
                if (defs) {
                    const gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
                    gradient.setAttribute("id", "beaconConeGradient");
                    gradient.setAttribute("x1", "0%");
                    gradient.setAttribute("y1", "100%");
                    gradient.setAttribute("x2", "0%");
                    gradient.setAttribute("y2", "0%");
                    gradient.innerHTML = `
                        <stop offset="0%" stop-color="#0284c7" stop-opacity="0.55"/>
                        <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
                    `;
                    defs.appendChild(gradient);
                }

                const target = document.getElementById("mapCameraGroup") || this.svg;
                target.appendChild(beaconGroup);
            }
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
                    this.goToStep(this.currentStepIndex);
                } else {
                    this.heading = 0;
                    this.centerOnCampusLowerThird();
                }
            } else {
                if (this.tweenAnimId) {
                    cancelAnimationFrame(this.tweenAnimId);
                    this.tweenAnimId = null;
                }
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
                this.currentUserX = undefined;
                this.currentUserY = undefined;
                this.currentHeading = 0;
                this.stage.style.transform = "";

                if (this.cameraGroup) {
                    this.cameraGroup.removeAttribute("transform");
                }

                // Reset SVG custom properties
                if (this.viewport) {
                    this.viewport.style.removeProperty("--bearing");
                    this.viewport.style.removeProperty("--counter-bearing");
                    this.viewport.style.removeProperty("--pitch");
                    this.viewport.style.removeProperty("--counter-pitch-scale");
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
            const rad = Math.atan2(dy, dx);
            const deg = rad * (180 / Math.PI);
            // Rotate stage so direction of travel faces upward (-90° in standard screen coords)
            return -(deg + 90);
        }

        /**
         * Locks user position to the lower-third / bottom-center (50% X, 72% Y).
         * Uses vector camera group transformation so shapes re-render mathematically.
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
                this.updateCompass();
                this.updateUserBeacon(this.currentUserX, this.currentUserY, this.currentHeading);
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
                // Smooth cubic ease-out
                const ease = 1 - Math.pow(1 - progress, 3);

                this.currentUserX = startX + (targetX - startX) * ease;
                this.currentUserY = startY + (targetY - startY) * ease;
                this.currentHeading = startH + diffH * ease;

                this.applyTransform();
                this.updateCompass();
                this.updateUserBeacon(this.currentUserX, this.currentUserY, this.currentHeading);

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
         * Crisp Vector 2.5D Transform Pipeline:
         * 1. rotateX(pitch) strictly on outer wrapper (CSS 3D perspective plane)
         * 2. translate + scale(2.2) + rotate strictly inside SVG <g id="mapCameraGroup">
         *    -> Vector math renders without GPU texture downsampling or blurriness
         */
        applyTransform() {
            if (!this.stage) return;
            if (!this.cameraGroup) {
                this.cameraGroup = document.getElementById("mapCameraGroup");
            }

            if (!this.is25dActive) {
                this.stage.style.transform = "";
                if (this.cameraGroup) this.cameraGroup.removeAttribute("transform");
                if (this.viewport) {
                    this.viewport.style.removeProperty("--bearing");
                    this.viewport.style.removeProperty("--counter-bearing");
                    this.viewport.style.removeProperty("--pitch");
                    this.viewport.style.removeProperty("--counter-pitch-scale");
                }
                return;
            }

            const pitch = this.pitch || 48; // Gentle tilt (45°–52°)
            const bearing = this.isHeadingUp ? (this.currentHeading || 0) : 0;
            const zoom = this.zoomScale || 2.2; // Waze-style close zoom in SVG vector space
            const uX = this.currentUserX !== undefined ? this.currentUserX : 400;
            const uY = this.currentUserY !== undefined ? this.currentUserY : 500;

            // Viewport dimensions for lower-third anchor
            const vw = this.viewport.clientWidth || 1000;
            const vh = this.viewport.clientHeight || 700;
            const svgAspect = 1200 / 850;
            const containerAspect = vw / vh;

            let anchorX = 600;
            let anchorY = 612; // 850 * 0.72 = 612 (Lower Third of 1200x850 SVG)

            if (containerAspect < svgAspect) {
                // Narrow / mobile portrait screen: vertical letterbox mapping
                const visibleHeightSvg = 1200 / containerAspect;
                anchorY = 425 + visibleHeightSvg * 0.22;
            }

            // Set CSS custom properties on viewport for billboarding labels & badges
            if (this.viewport) {
                this.viewport.style.setProperty("--bearing", `${bearing.toFixed(2)}deg`);
                this.viewport.style.setProperty("--counter-bearing", `${(-bearing).toFixed(2)}deg`);
                this.viewport.style.setProperty("--pitch", `${pitch}deg`);
                const pitchRad = (pitch * Math.PI) / 180;
                // Un-squash factor = 1 / cos(pitch)
                const counterPitchScale = (1 / Math.cos(pitchRad)).toFixed(3);
                this.viewport.style.setProperty("--counter-pitch-scale", counterPitchScale);
            }

            // 1. Tilt STRICTLY via CSS rotateX on the outer stage (no scale, no translate!)
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
        }

        zoomOut() {
            this.zoomScale = Math.max((this.zoomScale || 2.2) - 0.25, 1.5);
            this.applyTransform();
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
            } else {
                if (!this.compassRose) {
                    this.compassRose = document.getElementById("compassRose");
                }
                if (this.compassRose) {
                    this.compassRose.style.transition = animate ? "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
                    this.compassRose.style.transform = `rotate(${compassRot.toFixed(2)}deg)`;
                }
            }
        }

        /**
         * Positions user navigation puck and aligns the directional cone
         */
        updateUserBeacon(x, y, headingDeg) {
            const beacon = document.getElementById("userNavigationBeacon");
            const cone = document.getElementById("beaconCone");
            if (!beacon) return;

            beacon.setAttribute("transform", `translate(${x.toFixed(2)}, ${y.toFixed(2)})`);
            beacon.classList.remove("hidden");

            const beaconRot = this.isHeadingUp ? -headingDeg : 0;
            if (cone) {
                cone.setAttribute("transform", `rotate(${beaconRot.toFixed(2)})`);
            }
        }

        /**
         * Global Route Calculated Handler
         */
        onRouteCalculated(routeData) {
            this.currentRoute = routeData;
            this.currentStepIndex = 0;

            if (!routeData || !routeData.pathCoordinates || routeData.pathCoordinates.length < 2) return;

            // Automatically switch to Waze-style 2.5D navigation view
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

            if (this.tbtStepDistance && this.currentRoute) {
                const totalMeters = this.currentRoute.totalDistanceMeters || 100;
                const approxStepM = Math.max(15, Math.round(totalMeters / Math.max(1, totalSteps - 1)));
                this.tbtStepDistance.textContent = stepIdx === totalSteps - 1 ? "Destino" : `~${approxStepM} m`;
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
