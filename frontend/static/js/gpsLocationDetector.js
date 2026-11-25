/**
 * ================================================================================
 * GPSLOCATIONDETECTOR.JS - BROWSER GEOLOCATION API, PERMISSIONS & CAMPUS MATCHER
 * ================================================================================
 * Provides unified browser Geolocation API access for JaguarFind & JaguarMaps:
 *  - Secure-context and browser support verification
 *  - Permissions API inspection (`granted` | `prompt` | `denied` | `unknown`)
 *    plus live permission change notifications
 *  - Two-stage GPS acquisition: high-accuracy GPS fix with automatic indoor
 *    Wi-Fi / network positioning retry on signal loss or timeout
 *  - Full sensor forwarding (`latitude`, `longitude`, `accuracy`, `altitude`,
 *    `altitudeAccuracy`) plus optional indoor beacon/floor hints
 *  - Structured error states (`PERMISSION_DENIED`, `POSITION_UNAVAILABLE`,
 *    `TIMEOUT`, `UNSUPPORTED`, `INSECURE_CONTEXT`, `OUTSIDE_CAMPUS`, `NETWORK_ERROR`)
 *  - Building-level manual fallback fetcher (`/api/map/buildings/<id>/locations`)
 * ================================================================================
 */

(function (global) {
    "use strict";

    const ERROR_CODES = Object.freeze({
        UNSUPPORTED: "UNSUPPORTED",
        INSECURE_CONTEXT: "INSECURE_CONTEXT",
        PERMISSION_DENIED: "PERMISSION_DENIED",
        POSITION_UNAVAILABLE: "POSITION_UNAVAILABLE",
        TIMEOUT: "TIMEOUT",
        OUTSIDE_CAMPUS: "OUTSIDE_CAMPUS",
        NETWORK_ERROR: "NETWORK_ERROR",
    });

    function getCurrentLang() {
        if (global.JaguarI18n && typeof global.JaguarI18n.getLang === "function") {
            return global.JaguarI18n.getLang();
        }
        if (global.APP_CONFIG && global.APP_CONFIG.currentLang) {
            return String(global.APP_CONFIG.currentLang).toLowerCase().startsWith("sp") ? "spa" : "eng";
        }
        return "eng";
    }

    function tr(keyPath, paramsOrUnused, _unusedEng, legacyParams) {
        const params = (paramsOrUnused && typeof paramsOrUnused === "object") ? paramsOrUnused : legacyParams;
        if (typeof global.t === "function") {
            return global.t(keyPath, undefined, params);
        }
        return keyPath;
    }

    function escapeHtml(text) {
        return String(text == null ? "" : text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function shortBuildingLabel(name) {
        return String(name || "").split("(")[0].trim();
    }

    function getErrorCopy(code) {
        switch (code) {
            case ERROR_CODES.PERMISSION_DENIED:
                return {
                    code,
                    retryable: true,
                    tone: "rose",
                    title: tr("map.gps.err_permission_denied_title"),
                    description: tr("map.gps.err_permission_denied_desc"),
                };
            case ERROR_CODES.POSITION_UNAVAILABLE:
                return {
                    code,
                    retryable: true,
                    tone: "amber",
                    title: tr("map.gps.err_unavailable_title"),
                    description: tr("map.gps.err_unavailable_desc"),
                };
            case ERROR_CODES.TIMEOUT:
                return {
                    code,
                    retryable: true,
                    tone: "amber",
                    title: tr("map.gps.err_timeout_title"),
                    description: tr("map.gps.err_timeout_desc"),
                };
            case ERROR_CODES.INSECURE_CONTEXT:
                return {
                    code,
                    retryable: false,
                    tone: "amber",
                    title: tr("map.gps.err_insecure_title"),
                    description: tr("map.gps.err_insecure_desc"),
                };
            case ERROR_CODES.UNSUPPORTED:
                return {
                    code,
                    retryable: false,
                    tone: "slate",
                    title: tr("map.gps.err_unsupported_title"),
                    description: tr("map.gps.err_unsupported_desc"),
                };
            case ERROR_CODES.OUTSIDE_CAMPUS:
                return {
                    code,
                    retryable: true,
                    tone: "amber",
                    title: tr("map.gps.outside_campus_title"),
                    description: tr("map.gps.outside_campus_desc"),
                };
            default:
                return {
                    code: ERROR_CODES.NETWORK_ERROR,
                    retryable: true,
                    tone: "rose",
                    title: tr("map.gps.err_network_title"),
                    description: tr("map.gps.err_network_desc"),
                };
        }
    }

    function checkSupport() {
        const hostname = (global.location && global.location.hostname) || "";
        const isLocalhost = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "[::1]";
        if (typeof global.isSecureContext === "boolean" && !global.isSecureContext && !isLocalhost) {
            return { supported: false, error: getErrorCopy(ERROR_CODES.INSECURE_CONTEXT) };
        }
        if (typeof navigator === "undefined" || !navigator.geolocation) {
            return { supported: false, error: getErrorCopy(ERROR_CODES.UNSUPPORTED) };
        }
        return { supported: true, error: null };
    }

    let _permissionStatusObj = null;
    const _permissionListeners = new Set();

    async function queryPermissionState() {
        if (typeof navigator === "undefined" || !navigator.permissions || typeof navigator.permissions.query !== "function") {
            return "unknown";
        }
        try {
            const status = await navigator.permissions.query({ name: "geolocation" });
            if (!_permissionStatusObj) {
                _permissionStatusObj = status;
                status.onchange = function () {
                    _permissionListeners.forEach((cb) => {
                        try {
                            cb(status.state);
                        } catch (_) {}
                    });
                };
            }
            return status.state || "unknown"; // "granted" | "prompt" | "denied"
        } catch (_) {
            return "unknown";
        }
    }

    function onPermissionChange(callback) {
        if (typeof callback === "function") {
            _permissionListeners.add(callback);
            queryPermissionState().then((state) => {
                try {
                    callback(state);
                } catch (_) {}
            });
        }
        return () => _permissionListeners.delete(callback);
    }

    function _mapGeolocationPositionError(err) {
        if (!err) return getErrorCopy(ERROR_CODES.POSITION_UNAVAILABLE);
        if (err.code === 1) return getErrorCopy(ERROR_CODES.PERMISSION_DENIED);
        if (err.code === 2) return getErrorCopy(ERROR_CODES.POSITION_UNAVAILABLE);
        if (err.code === 3) return getErrorCopy(ERROR_CODES.TIMEOUT);
        return getErrorCopy(ERROR_CODES.POSITION_UNAVAILABLE);
    }

    function _extractCoords(pos) {
        const c = (pos && pos.coords) || {};
        const validNum = (v) => (typeof v === "number" && !Number.isNaN(v) && Number.isFinite(v) ? v : null);
        return {
            latitude: validNum(c.latitude),
            longitude: validNum(c.longitude),
            accuracy: validNum(c.accuracy),
            altitude: validNum(c.altitude),
            altitudeAccuracy: validNum(c.altitudeAccuracy),
            heading: validNum(c.heading),
            speed: validNum(c.speed),
            timestamp: (pos && pos.timestamp) || Date.now(),
        };
    }

    function _getCurrentPositionOnce(geoOptions) {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve(_extractCoords(pos)),
                (err) => reject(err),
                geoOptions
            );
        });
    }

    /**
     * Reads optional indoor beacon metadata from explicit options, URL query
     * parameters (?beacon=UAM-P-F2&beaconFloor=2), or window.JAGUAR_ACTIVE_BEACON.
     */
    function getAmbientBeaconHint(options) {
        const opts = options || {};
        let beaconId = opts.beaconId || null;
        let beaconFloor = opts.beaconFloor != null ? opts.beaconFloor : null;

        if (!beaconId && global.JAGUAR_ACTIVE_BEACON) {
            if (typeof global.JAGUAR_ACTIVE_BEACON === "string") {
                beaconId = global.JAGUAR_ACTIVE_BEACON;
            } else if (typeof global.JAGUAR_ACTIVE_BEACON === "object") {
                beaconId = global.JAGUAR_ACTIVE_BEACON.beaconId || null;
                if (beaconFloor == null && global.JAGUAR_ACTIVE_BEACON.floorLevel != null) {
                    beaconFloor = global.JAGUAR_ACTIVE_BEACON.floorLevel;
                }
            }
        }

        if (!beaconId && global.location && global.location.search) {
            try {
                const params = new URLSearchParams(global.location.search);
                beaconId = params.get("beacon") || params.get("beaconId") || null;
                const bf = params.get("beaconFloor");
                if (beaconFloor == null && bf !== null && bf !== "") {
                    const parsed = parseInt(bf, 10);
                    if (!Number.isNaN(parsed)) beaconFloor = parsed;
                }
            } catch (_) {}
        }

        return { beaconId, beaconFloor };
    }

    /**
     * Acquires browser GPS coordinates with Permissions API pre-check and
     * automatic indoor Wi-Fi / network retry when high-accuracy GPS times out.
     */
    async function acquireRawPosition(options) {
        const opts = options || {};
        const onStatusChange = typeof opts.onStatusChange === "function" ? opts.onStatusChange : () => {};

        const support = checkSupport();
        if (!support.supported) {
            return { ok: false, error: support.error, permissionState: "unsupported" };
        }

        const permissionState = await queryPermissionState();
        if (permissionState === "denied") {
            return {
                ok: false,
                error: getErrorCopy(ERROR_CODES.PERMISSION_DENIED),
                permissionState: "denied",
            };
        }

        if (permissionState === "prompt") {
            onStatusChange("requesting_permission");
        } else {
            onStatusChange("locating");
        }

        try {
            const coords = await _getCurrentPositionOnce({
                enableHighAccuracy: true,
                timeout: opts.highAccuracyTimeoutMs || 9000,
                maximumAge: opts.forceFresh ? 0 : (opts.maximumAgeMs || 10000),
            });
            return { ok: true, coords, permissionState: "granted" };
        } catch (err) {
            // Never retry when user explicitly denied permission
            if (err && err.code === 1) {
                return {
                    ok: false,
                    error: getErrorCopy(ERROR_CODES.PERMISSION_DENIED),
                    permissionState: "denied",
                };
            }

            // Indoor fallback: retry once using Wi-Fi / network geolocation
            if (err && (err.code === 2 || err.code === 3) && opts.allowNetworkFallback !== false) {
                onStatusChange("retrying_network");
                try {
                    const fallbackCoords = await _getCurrentPositionOnce({
                        enableHighAccuracy: false,
                        timeout: opts.fallbackTimeoutMs || 8000,
                        maximumAge: 30000,
                    });
                    return { ok: true, coords: fallbackCoords, usedNetworkFallback: true, permissionState: "granted" };
                } catch (err2) {
                    return {
                        ok: false,
                        error: _mapGeolocationPositionError(err2),
                        permissionState: err2 && err2.code === 1 ? "denied" : permissionState,
                    };
                }
            }

            return {
                ok: false,
                error: _mapGeolocationPositionError(err),
                permissionState,
            };
        }
    }

    /**
     * Sends acquired WGS84 coordinates (plus optional accuracy, altitude, floor,
     * and beacon metadata) to /api/map/nearest-gps for building boundary & floor matching.
     */
    async function matchCoordinates(coords, options) {
        const opts = options || {};
        const lang = opts.lang || getCurrentLang();
        const endpoint = (global.APP_CONFIG && global.APP_CONFIG.endpoints && global.APP_CONFIG.endpoints.nearestGps)
            || "/api/map/nearest-gps";

        const qs = new URLSearchParams();
        qs.set("lat", String(coords.latitude));
        qs.set("lng", String(coords.longitude));
        qs.set("lang", lang);

        if (typeof coords.accuracy === "number" && !Number.isNaN(coords.accuracy)) {
            qs.set("accuracy", coords.accuracy.toFixed(1));
        }
        if (typeof coords.altitude === "number" && !Number.isNaN(coords.altitude)) {
            qs.set("altitude", coords.altitude.toFixed(2));
        }
        if (typeof coords.altitudeAccuracy === "number" && !Number.isNaN(coords.altitudeAccuracy)) {
            qs.set("altitudeAccuracy", coords.altitudeAccuracy.toFixed(2));
        }
        if (opts.floorHint != null && opts.floorHint !== "") {
            qs.set("floor", String(opts.floorHint));
        }

        const beacon = getAmbientBeaconHint(opts);
        if (beacon.beaconId) qs.set("beaconId", String(beacon.beaconId));
        if (beacon.beaconFloor != null) qs.set("beaconFloor", String(beacon.beaconFloor));

        try {
            const res = await fetch(`${endpoint}?${qs.toString()}`);
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }
            const data = await res.json();
            const nearest = (data && data.nearest) ? data.nearest : null;
            const isOutside = Boolean(
                (data && data.outsideCampus === true) ||
                (nearest && nearest.isWithinCampus === false)
            );

            if (isOutside) {
                return {
                    ok: false,
                    outsideCampus: true,
                    error: getErrorCopy(ERROR_CODES.OUTSIDE_CAMPUS),
                    coords,
                    response: data,
                    nearest,
                    campusEntrances: (data && data.campusEntrances) || [],
                };
            }

            if (data && data.success && nearest) {
                return {
                    ok: true,
                    outsideCampus: false,
                    error: null,
                    coords,
                    response: data,
                    nearest,
                };
            }

            return {
                ok: false,
                outsideCampus: false,
                error: getErrorCopy(ERROR_CODES.NETWORK_ERROR),
                coords,
                response: data,
                nearest,
            };
        } catch (err) {
            return {
                ok: false,
                outsideCampus: false,
                error: getErrorCopy(ERROR_CODES.NETWORK_ERROR),
                coords,
                rawError: err,
            };
        }
    }

    /**
     * Fetches ALL available location options for a given building grouped by floor
     * (used when switching buildings manually in the fallback picker).
     */
    async function fetchBuildingLocations(buildingId, options) {
        const opts = options || {};
        const lang = opts.lang || getCurrentLang();
        const qs = new URLSearchParams();
        qs.set("lang", lang);
        if (opts.floor != null && opts.floor !== "") {
            qs.set("floor", String(opts.floor));
        }
        if (opts.coords && typeof opts.coords.latitude === "number" && typeof opts.coords.longitude === "number") {
            qs.set("lat", String(opts.coords.latitude));
            qs.set("lng", String(opts.coords.longitude));
        }

        const res = await fetch(`/api/map/buildings/${encodeURIComponent(buildingId)}/locations?${qs.toString()}`);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        return await res.json();
    }

    /**
     * End-to-end GPS detection: checks support & permissions, acquires raw
     * browser coordinates (with optional fresh live cache reuse), and resolves
     * building boundary, floor, confidence, and manual fallback options.
     */
    async function detectCampusLocation(options) {
        const opts = options || {};
        const onStatusChange = typeof opts.onStatusChange === "function" ? opts.onStatusChange : () => {};

        // Optionally reuse a very fresh (< 15s) GPS reading already tracked by the live map controller
        const live = !opts.forceFresh && opts.reuseFreshLive && global.campus25dController && global.campus25dController.latestGpsCoords;
        if (live && typeof live.lat === "number" && typeof live.lng === "number" && (Date.now() - (live.timestamp || 0)) < 15000) {
            onStatusChange("locating");
            return await matchCoordinates(
                {
                    latitude: live.lat,
                    longitude: live.lng,
                    accuracy: live.accuracy || null,
                    altitude: live.altitude != null ? live.altitude : null,
                    altitudeAccuracy: live.altitudeAccuracy != null ? live.altitudeAccuracy : null,
                    timestamp: live.timestamp || Date.now(),
                },
                opts
            );
        }

        const acquired = await acquireRawPosition(opts);
        if (!acquired.ok) {
            return {
                ok: false,
                outsideCampus: false,
                error: acquired.error,
                permissionState: acquired.permissionState,
                coords: null,
                nearest: null,
            };
        }

        const matched = await matchCoordinates(acquired.coords, opts);
        matched.permissionState = acquired.permissionState;
        matched.usedNetworkFallback = Boolean(acquired.usedNetworkFallback);
        return matched;
    }

    global.JaguarGpsDetector = Object.freeze({
        ERROR_CODES,
        getCurrentLang,
        tr,
        escapeHtml,
        shortBuildingLabel,
        getErrorCopy,
        checkSupport,
        queryPermissionState,
        onPermissionChange,
        getAmbientBeaconHint,
        acquireRawPosition,
        matchCoordinates,
        fetchBuildingLocations,
        detectCampusLocation,
    });
})(window);
