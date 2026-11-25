/**
 * apiContracts.js
 * =============================================================================
 * DATA CONTRACTS & TYPE SPECIFICATIONS FOR FRONTEND DEVELOPERS
 * =============================================================================
 * Defines client-side enums, endpoint routes, and object structures for
 * JaguarFind (Lost & Found Object) and JaguarMaps.
 */

// =============================================================================
// 1. ENUMS & CONSTANTS
// =============================================================================

function translateContractKey(key) {
    if (typeof window !== "undefined" && typeof window.t === "function") {
        return window.t(key);
    }
    return key;
}

const USER_TYPE_LABEL_KEYS = Object.freeze({
    1: "auth.role_student",
    2: "auth.role_collaborator",
    3: "auth.role_visitor_short",
    4: "auth.role_admin"
});

const LOST_OBJECT_STATE_LABEL_KEYS = Object.freeze({
    1: "lost_found.state_reported",
    2: "lost_found.state_custody",
    3: "lost_found.state_claimed"
});

export const UserType = Object.freeze({
    STUDENT: 1,
    COLLABORATOR: 2,
    VISITOR: 3,
    ADMIN: 4,

    labelKeys: USER_TYPE_LABEL_KEYS,
    getLabel: (id) => translateContractKey(USER_TYPE_LABEL_KEYS[id] || "common.unknown"),
    get labels() {
        return {
            1: translateContractKey(USER_TYPE_LABEL_KEYS[1]),
            2: translateContractKey(USER_TYPE_LABEL_KEYS[2]),
            3: translateContractKey(USER_TYPE_LABEL_KEYS[3]),
            4: translateContractKey(USER_TYPE_LABEL_KEYS[4])
        };
    }
});

export const LostObjectState = Object.freeze({
    REPORTED: 1,    // Reported on campus or online
    IN_CUSTODY: 2,  // Safely stored at Building A (CAE)
    CLAIMED: 3,     // Returned to rightful owner

    labelKeys: LOST_OBJECT_STATE_LABEL_KEYS,
    getLabel: (id) => translateContractKey(LOST_OBJECT_STATE_LABEL_KEYS[id] || "common.unknown"),
    get labels() {
        return {
            1: translateContractKey(LOST_OBJECT_STATE_LABEL_KEYS[1]),
            2: translateContractKey(LOST_OBJECT_STATE_LABEL_KEYS[2]),
            3: translateContractKey(LOST_OBJECT_STATE_LABEL_KEYS[3])
        };
    },

    badgeColors: {
        1: "amber",
        2: "blue",
        3: "emerald"
    }
});

// =============================================================================
// 2. ENDPOINT URL REGISTRY (Using /lost-found-object)
// =============================================================================

export const API_ENDPOINTS = Object.freeze({
    // Auth & Identity
    AUTH_LOGIN: "/api/auth/login",
    AUTH_SIGNUP: "/api/auth/signup",
    AUTH_LOGOUT: "/api/auth/logout",
    AUTH_ME: "/api/auth/me",

    // JaguarMaps & Dijkstra
    MAP_NODES: "/api/map/nodes",
    MAP_NODE_DETAIL: (nodeId) => `/api/map/nodes/${nodeId}`,
    MAP_CATEGORIES: "/api/map/categories",
    MAP_PLACES: "/api/map/places",
    MAP_ROUTE: "/api/map/route",
    MAP_NEAREST_GPS: "/api/map/nearest-gps",
    MAP_BOUNDARIES: "/api/map/boundaries",
    MAP_BUILDING_LOCATIONS: (buildingId) => `/api/map/buildings/${buildingId}/locations`,

    // JaguarFind (Lost & Found Object)
    LOST_FOUND_ITEMS: "/api/lost-found-object/items",
    LOST_FOUND_ITEM_DETAIL: (id) => `/api/lost-found-object/items/${id}`,
    LOST_FOUND_REPORT: "/api/lost-found-object/items",
    LOST_FOUND_CLAIM: (id) => `/api/lost-found-object/items/${id}/claim`,
    LOST_FOUND_MAP_PINS: "/api/lost-found-object/map-pins",

    // Admin Custody Panel
    ADMIN_STATS: "/api/admin/stats",
    ADMIN_UPDATE_STATE: (id) => `/api/admin/items/${id}/state`,
    ADMIN_USERS: "/api/admin/users",

    // System & i18n
    SET_LANGUAGE: (lang) => `/api/i18n/set-language/${lang}`,
    TRANSLATIONS: (lang) => `/api/i18n/translations/${lang}`
});

// =============================================================================
// 3. JSDOC TYPE DEFINITIONS (For IDE Autocomplete & Linting)
// =============================================================================

/**
 * @typedef {Object} User
 * @property {number} id
 * @property {number} userTypeId - 1: Student, 2: Collaborator, 3: Visitor, 4: Admin
 * @property {string} roleName
 * @property {string} fullName
 * @property {string|null} [userName] - Username handle (e.g. 'camila.navarro')
 * @property {string|null} [username] - Alias for userName
 * @property {string|null} [cif] - Mandatory for students (8 digits)
 * @property {string|null} [govermentId] - Mandatory for collaborators/visitors
 * @property {string|null} [phoneNumber] - Mandatory for visitors
 * @property {string|null} [email] - Mandatory for admin
 * @property {string} [createdAt]
 * @property {boolean} isActive
 */

/**
 * @typedef {Object} LostObjectReport
 * @property {number} id
 * @property {string} itemName - e.g. "Calculadora Casio fx-991"
 * @property {string} category - 'electronics', 'documents', 'personalItems', etc.
 * @property {string} location - Campus node ID, e.g. "buildingB"
 * @property {string} description - Public description
 * @property {number} lostObjectStateId - 1: Reported, 2: In Custody, 3: Claimed
 * @property {string} stateName - Spanish label
 * @property {string} badgeColor - 'amber' | 'blue' | 'emerald'
 * @property {string|null} [secretDetail] - Hidden from public; only visible to Admin
 * @property {boolean} hasSecretDetail
 * @property {boolean} hasSignature
 * @property {string|null} [photoUrl]
 * @property {number|null} [userId]
 * @property {string|null} [reporterName]
 * @property {string} dateTimeReported
 * @property {string|null} [dateTimeResolved]
 */

/**
 * @typedef {Object} CampusNode
 * @property {string} nodeId - e.g. "buildingA", "mainParking"
 * @property {string} name - e.g. "Edificio A (Atención al Estudiante)"
 * @property {string} category - Category ID
 * @property {number} xPercent - SVG/Image X position (0.0 to 100.0%)
 * @property {number} yPercent - SVG/Image Y position (0.0 to 100.0%)
 * @property {number} lat - Real GPS latitude
 * @property {number} lng - Real GPS longitude
 * @property {number} floorLevel
 * @property {string} accessLevel - "public" | "restricted" | "facultyOnly"
 * @property {string|null} [accessNotice]
 * @property {boolean} isOutdoorAccessPoint
 */

/**
 * @typedef {Object} RouteResult
 * @property {boolean} success
 * @property {string} origin - Display name of start
 * @property {string} destination - Display name of target
 * @property {string} category
 * @property {number} floorLevel
 * @property {string[]} pathNodeIds - Ordered list of node IDs along path
 * @property {Array<{nodeId: string, name: string, xPercent: number, yPercent: number, lat: number, lng: number}>} pathCoordinates
 * @property {number} totalDistanceMeters
 * @property {number} estimatedWalkingMinutes
 * @property {string[]} stepInstructions - Turn-by-turn guidance strings
 * @property {boolean} isAccessibleRoute - True if stairs were bypassed
 * @property {string|null} [error]
 */

/**
 * @typedef {Object} CategoryMetadata
 * @property {string} category - Category identifier
 * @property {string} labelSpanish
 * @property {string} labelEnglish
 * @property {string} icon - FontAwesome / Lucide icon name
 * @property {string} badgeColor - Color name
 */
