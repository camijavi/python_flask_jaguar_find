"""
testMapToCatalogNavigation.py
================================================================================
Automated test suite verifying:
1. Backend API filtering by `building` (and `location` alias), localized
   building names, item detail endpoint, and map pins payload
2. Web routes `/lost-found-object/catalogo`, `/catalog`,
   `/lost-found-object/catalogo/<item_id>`, `/catalog/<item_id>`, `/admin/items`,
   and query-preserving auth redirect
3. Translation dictionary symmetry between `spa.json` and `eng.json`
4. Client-side JS behavior (via Node.js) for:
   - `lostFoundMapLayer.js`: item-level detail action buttons next to each item
     in the map popup (`?item=<id>`), building-filtered "View in Catalog" link
     (`?building=<building_id>`), XSS escaping, and live i18n re-rendering
   - `catalogScreen.js`: reading `?building=` and `?item=` (and route item IDs)
     on load, applying/clearing the building filter cleanly, auto-opening the
     item detail modal (even when filtered to another building), handling missing
     items gracefully, URL synchronization, and Escape/Close modal dismissal
================================================================================
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from backend.app import createApp
from backend.config import Config
from backend.database import initDb, createLostObjectReport


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestMapToCatalogBackend(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.original_db_path = Config.DATABASE_PATH
        Config.DATABASE_PATH = self.temp_db_path
        initDb(dbPath=self.temp_db_path, seedSampleData=True)

        # Add a second active item in buildingB so Building B has multiple items
        self.extra_item_id = createLostObjectReport(
            itemName="Audífonos Sony WH-1000XM5",
            location="buildingB",
            description="Audífonos negros con estuche gris olvidados en aula B-204.",
            category="electronics",
            userId=2,
            lostObjectStateId=1,
            secretDetail="Iniciales CM grabadas en la diadema interior.",
            dbPath=self.temp_db_path,
        )

        self.app = createApp(Config)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        Config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def _login_as_student(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "Id": 2,
                "UserTypeId": 1,
                "UserTypeName": "Student",
                "FullName": "Camila Navarro",
                "Email": "camila.navarro@uamv.edu.ni",
            }
            sess["idioma"] = "spa"
            sess["lang"] = "spa"

    def _login_as_admin(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "Id": 1,
                "UserTypeId": 4,
                "UserTypeName": "Admin",
                "FullName": "Administrador CAE Edificio A",
                "Email": "admin@uamv.edu.ni",
            }
            sess["idioma"] = "spa"
            sess["lang"] = "spa"

    def test_translation_dictionaries_remain_symmetrical(self):
        spa = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        eng = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))

        def flatten(d, prefix=""):
            keys = set()
            for k, v in d.items():
                if k.startswith("_"):
                    continue
                full = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    keys |= flatten(v, full)
                else:
                    keys.add(full)
            return keys

        self.assertEqual(flatten(spa), flatten(eng))
        self.assertIn("lost_found.view_details", flatten(spa))
        self.assertIn("lost_found.clear_building_filter", flatten(spa))
        self.assertIn("lost_found.filtered_by_building", flatten(spa))

    def test_api_items_filter_by_building_and_case_insensitivity(self):
        res_all = self.client.get("/api/lost-found-object/items")
        self.assertEqual(res_all.status_code, 200)
        data_all = res_all.get_json()
        self.assertTrue(data_all["success"])
        self.assertEqual(data_all["count"], 4)

        res_b = self.client.get("/api/lost-found-object/items?building=buildingB")
        self.assertEqual(res_b.status_code, 200)
        data_b = res_b.get_json()
        self.assertTrue(data_b["success"])
        self.assertEqual(data_b["building"], "buildingB")
        self.assertEqual(data_b["count"], 2)
        for item in data_b["items"]:
            self.assertEqual(item["Location"], "buildingB")
            self.assertTrue(item.get("locationName"))

        # Case-insensitive building match
        res_b_upper = self.client.get("/api/lost-found-object/items?building=BUILDINGB")
        self.assertEqual(res_b_upper.status_code, 200)
        self.assertEqual(res_b_upper.get_json()["count"], 2)

        # Backwards-compatible `location` alias
        res_k = self.client.get("/api/lost-found-object/items?location=buildingK")
        self.assertEqual(res_k.status_code, 200)
        data_k = res_k.get_json()
        self.assertEqual(data_k["count"], 1)
        self.assertEqual(data_k["items"][0]["Location"], "buildingK")

        # Empty building result
        res_empty = self.client.get("/api/lost-found-object/items?building=buildingP")
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(res_empty.get_json()["count"], 0)

    def test_api_item_detail_and_secret_masking(self):
        # Unauthenticated viewer does not see SecretDetail
        res = self.client.get("/api/lost-found-object/items/1")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["item"]["Id"], 1)
        self.assertEqual(payload["item"]["Location"], "buildingB")
        self.assertTrue(payload["item"]["hasSecretDetail"])
        self.assertIsNone(payload["item"]["SecretDetail"])
        self.assertTrue(payload["item"].get("locationName"))

        # Admin sees SecretDetail
        self._login_as_admin()
        res_admin = self.client.get("/api/lost-found-object/items/1")
        self.assertEqual(res_admin.status_code, 200)
        self.assertIsNotNone(res_admin.get_json()["item"]["SecretDetail"])

        # Missing item returns 404
        res_missing = self.client.get("/api/lost-found-object/items/99999")
        self.assertEqual(res_missing.status_code, 404)
        self.assertFalse(res_missing.get_json()["success"])

    def test_map_pins_include_item_ids_and_localized_building_name(self):
        self._login_as_student()
        res = self.client.get("/api/lost-found-object/map-pins")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        pins_by_node = {p["locationNodeId"]: p for p in data["pins"]}
        self.assertIn("buildingB", pins_by_node)
        pin_b = pins_by_node["buildingB"]
        self.assertEqual(pin_b["itemsCount"], 2)
        self.assertIn("Edificio B", pin_b["locationName"])
        item_ids = {it["id"] for it in pin_b["items"]}
        self.assertIn(1, item_ids)
        self.assertIn(self.extra_item_id, item_ids)
        for it in pin_b["items"]:
            self.assertNotIn("photoUrl", it)

    def test_catalog_and_item_routes_and_auth_redirect_preserves_query(self):
        # Unauthenticated redirect preserves ?building=...&item=...
        res_redir = self.client.get("/lost-found-object/catalogo?building=buildingB&item=1")
        self.assertEqual(res_redir.status_code, 302)
        loc = res_redir.headers["Location"]
        self.assertTrue(loc.startswith("/auth?next="))
        self.assertIn("/lost-found-object/catalogo?building=buildingB&item=1", unquote(loc))

        # Authenticated routes render cleanly
        self._login_as_student()
        for path, expected_initial_id in [
            ("/lost-found-object/catalogo", 'data-initial-item-id=""'),
            ("/lost-found-object/catalogo?building=buildingB", 'data-initial-item-id=""'),
            ("/catalog?building=buildingB&item=1", 'data-initial-item-id=""'),
            ("/lost-found-object/catalogo/1", 'data-initial-item-id="1"'),
            ("/catalog/2", 'data-initial-item-id="2"'),
        ]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Route {path} failed")
            html = res.get_data(as_text=True)
            self.assertIn('id="filterBuilding"', html)
            self.assertIn('id="activeBuildingFilterBanner"', html)
            self.assertIn('id="btnClearBuildingFilter"', html)
            self.assertIn('id="itemDetailModal"', html)
            self.assertIn("catalogScreen.js", html)
            self.assertIn(expected_initial_id, html)

        # Map page renders popover with building catalog link when authenticated
        map_res = self.client.get("/")
        self.assertEqual(map_res.status_code, 200)
        map_html = map_res.get_data(as_text=True)
        self.assertIn('id="btnViewInCatalog"', map_html)
        self.assertIn('id="btnBldgViewCatalog"', map_html)
        self.assertIn("lostFoundMapLayer.js", map_html)

        # Admin items management page still renders cleanly
        self._login_as_admin()
        admin_res = self.client.get("/admin/items")
        self.assertEqual(admin_res.status_code, 200)
        admin_html = admin_res.get_data(as_text=True)
        self.assertIn('id="catalogAppRoot"', admin_html)
        self.assertIn('id="itemDetailModal"', admin_html)


class TestMapAndCatalogClientJS(unittest.TestCase):
    """Runs deterministic Node.js tests against lostFoundMapLayer.js and catalogScreen.js."""

    def test_map_popover_and_catalog_query_params_js(self):
        node_bin = shutil.which("node")
        if not node_bin:
            self.skipTest("Node.js not available in test environment")

        spa_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        eng_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))

        js_test = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const spaDict = JSON.parse(process.env.TEST_SPA_DICT);
const engDict = JSON.parse(process.env.TEST_ENG_DICT);

function resolveDict(dict, keyPath) {
    let curr = dict;
    for (const k of String(keyPath).split(".")) {
        if (curr && typeof curr === "object" && Object.prototype.hasOwnProperty.call(curr, k)) {
            curr = curr[k];
        } else {
            return null;
        }
    }
    return typeof curr === "string" ? curr : null;
}

function makeTranslator(langRef, dictRef) {
    return function t(key, fallback, params) {
        const found = resolveDict(dictRef.current, key);
        let text = found !== null ? found : (fallback !== undefined ? fallback : key);
        if (params && typeof text === "string") {
            for (const [k, v] of Object.entries(params)) {
                text = text.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
            }
        }
        return text;
    };
}

function createEl(tag, attrs = {}) {
    const listeners = new Map();
    const classSet = new Set((attrs.class || "").split(/\s+/).filter(Boolean));
    const attrMap = new Map(Object.entries(attrs).filter(([k]) => !["class", "options", "children", "textContent"].includes(k)));
    const el = {
        tagName: tag.toUpperCase(),
        id: attrs.id || "",
        value: attrs.value || "",
        href: attrs.href || "",
        src: attrs.src || "",
        alt: attrs.alt || "",
        title: attrs.title || "",
        disabled: false,
        style: {},
        textContent: attrs.textContent || "",
        _innerHTML: "",
        get innerHTML() { return this._innerHTML; },
        set innerHTML(v) {
            this._innerHTML = String(v);
            if (v === "") this.children = [];
        },
        children: attrs.children ? [...attrs.children] : [],
        options: attrs.options ? [...attrs.options] : [],
        className: attrs.class || "",
        classList: {
            add(...cls) { cls.forEach(c => classSet.add(c)); },
            remove(...cls) { cls.forEach(c => classSet.delete(c)); },
            contains(c) { return classSet.has(c); },
            toggle(c, force) {
                const add = force === undefined ? !classSet.has(c) : Boolean(force);
                if (add) classSet.add(c); else classSet.delete(c);
                return add;
            },
        },
        appendChild(child) {
            this.children.push(child);
            if (this.tagName === "SELECT" && child.tagName === "OPTION") {
                this.options.push(child);
            }
            return child;
        },
        getAttribute(k) { return attrMap.has(k) ? attrMap.get(k) : null; },
        setAttribute(k, v) {
            attrMap.set(k, String(v));
            if (k === "class") {
                classSet.clear();
                String(v).split(/\s+/).filter(Boolean).forEach(c => classSet.add(c));
            }
        },
        addEventListener(evt, fn) {
            if (!listeners.has(evt)) listeners.set(evt, []);
            listeners.get(evt).push(fn);
        },
        dispatchEvent(evt) {
            const eventObj = Object.assign({ preventDefault() {}, stopPropagation() {}, target: el }, evt);
            (listeners.get(eventObj.type) || []).forEach(fn => fn.call(el, eventObj));
        },
        focus() {},
        closest() { return null; },
    };
    return el;
}

// =========================================================================
// PART 1: Test lostFoundMapLayer.js popup links & item-level detail buttons
// =========================================================================
(async () => {
    const langRef = { current: "spa" };
    const dictRef = { current: spaDict };
    const winListeners = new Map();

    const els = {
        lostFoundMapPinsLayer: createEl("g", { id: "lostFoundMapPinsLayer" }),
        wazeLostPinsContainer: createEl("div", { id: "wazeLostPinsContainer" }),
        btnToggleLostObjectsLayer: createEl("button", { id: "btnToggleLostObjectsLayer" }),
        mapLostPinsBadgeCount: createEl("span", { id: "mapLostPinsBadgeCount", class: "hidden" }),
        lostFoundPinPopover: createEl("div", { id: "lostFoundPinPopover", class: "hidden" }),
        btnCloseLostPinPopover: createEl("button", { id: "btnCloseLostPinPopover" }),
        btnFocus25dPin: createEl("button", { id: "btnFocus25dPin" }),
        lostPinNodeName: createEl("span", { id: "lostPinNodeName" }),
        lostPinCountSubtitle: createEl("span", { id: "lostPinCountSubtitle" }),
        lostPinItemsList: createEl("div", { id: "lostPinItemsList" }),
        btnViewInCatalog: createEl("a", { id: "btnViewInCatalog", href: "/lost-found-object/catalogo" }),
        btnReportHere: createEl("button", { id: "btnReportHere" }),
        bldgPopover: createEl("div", { id: "bldgPopover" }),
    };

    const mockPinsResponse = {
        success: true,
        totalPins: 1,
        totalActiveItems: 2,
        pins: [{
            locationNodeId: "buildingB",
            locationName: "Edificio B (Aulas B101-B106 & Farmacia)",
            xPercent: 37.0,
            yPercent: 54.0,
            itemsCount: 2,
            items: [
                { id: 1, itemName: "Calculadora <script>alert(1)</script>", lostObjectStateId: 2, stateName: "In Custody", dateTimeReported: "2026-11-24 10:00:00" },
                { id: 7, itemName: "Audífonos Sony", lostObjectStateId: 1, stateName: "Reported", dateTimeReported: "2026-11-24 12:30:00" },
            ],
        }],
    };

    const documentObj = {
        readyState: "complete",
        getElementById: (id) => els[id] || null,
        createElement: (tag) => createEl(tag),
        createElementNS: (_ns, tag) => createEl(tag),
        addEventListener() {},
    };

    const winMap = {
        document: documentObj,
        location: { search: "" },
        URLSearchParams,
        APP_CONFIG: { currentLang: "spa" },
        APP_TRANSLATIONS: spaDict,
        JaguarI18n: { isSpanish: () => langRef.current === "spa" },
        t: makeTranslator(langRef, dictRef),
        fetch: async () => ({ ok: true, json: async () => mockPinsResponse }),
        addEventListener(evt, fn) {
            if (!winListeners.has(evt)) winListeners.set(evt, []);
            winListeners.get(evt).push(fn);
        },
        dispatchEvent(evt) {
            (winListeners.get(evt.type) || []).forEach(fn => fn(evt));
        },
        setTimeout,
        clearTimeout,
        console,
    };
    winMap.window = winMap;
    winMap.globalThis = winMap;

    const mapSrc = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/lostFoundMapLayer.js"), "utf8");
    vm.runInContext(mapSrc, vm.createContext(winMap));
    await new Promise(r => setTimeout(r, 20));

    // Open popover for buildingB
    winMap.JaguarLostFoundMap.showPinPopover(mockPinsResponse.pins[0]);

    assert.equal(els.lostFoundPinPopover.classList.contains("hidden"), false, "Popover must open");
    assert.equal(els.bldgPopover.classList.contains("hidden"), true, "Building popover must close");
    assert.equal(
        els.btnViewInCatalog.href,
        "/lost-found-object/catalogo?building=buildingB",
        "View in Catalog button must pre-filter by building=<building_id>"
    );
    assert.equal(els.lostPinItemsList.children.length, 2, "Must render 2 item rows");

    const row1Html = els.lostPinItemsList.children[0].innerHTML;
    const row2Html = els.lostPinItemsList.children[1].innerHTML;
    assert.ok(row1Html.includes('href="/lost-found-object/catalogo?item=1"'), "Item 1 must have direct ?item=1 detail action link");
    assert.ok(row1Html.includes("data-item-detail-link"), "Item 1 link must have data-item-detail-link");
    assert.ok(row1Html.includes("Ver detalle"), "Item 1 button must show Spanish label");
    assert.ok(!row1Html.includes("<script>"), "Item name must be HTML-escaped");
    assert.ok(row2Html.includes('href="/lost-found-object/catalogo?item=7"'), "Item 2 must have direct ?item=7 detail action link");

    // Live language switch updates popover labels
    langRef.current = "eng";
    dictRef.current = engDict;
    winMap.dispatchEvent({ type: "jaguarLanguageChanged" });
    assert.equal(els.btnViewInCatalog.textContent, "View in Catalog");
    assert.ok(els.lostPinItemsList.children[0].innerHTML.includes("View details"));

    // =========================================================================
    // PART 2: Test catalogScreen.js URL params, building filter, clear & modal
    // =========================================================================
    const sampleItems = [
        { Id: 1, ItemName: "Calculadora Casio", Category: "electronics", Location: "buildingB", locationName: "Edificio B", Description: "Calculadora científica completa", LostObjectStateId: 2, StateName: "In Custody", DateTimeReported: "2026-11-24 10:00:00", hasSecretDetail: true, SecretDetail: null, PhotoUrl: null, ReporterName: "Camila Navarro" },
        { Id: 2, ItemName: "Termo Yeti Azul", Category: "personalItems", Location: "buildingK", locationName: "Edificio K", Description: "Termo azul marino 26oz", LostObjectStateId: 1, StateName: "Reported", DateTimeReported: "2026-11-24 11:00:00", hasSecretDetail: true, SecretDetail: null, PhotoUrl: null, ReporterName: "Carlos Mendoza" },
        { Id: 3, ItemName: "Carnet UAM", Category: "documents", Location: "buildingA", locationName: "Edificio A", Description: "Carnet estudiantil", LostObjectStateId: 3, StateName: "Claimed", DateTimeReported: "2026-11-23 09:00:00", DateTimeResolved: "2026-11-24 08:00:00", hasSecretDetail: false, SecretDetail: null, PhotoUrl: null, ReporterName: "Camila Navarro" },
    ];

    function createCatalogSandbox({ pathname = "/lost-found-object/catalogo", search = "", initialItemId = "", isAdmin = false } = {}) {
        const cLangRef = { current: "spa" };
        const cDictRef = { current: spaDict };
        const fetchCalls = [];
        const historyLog = [];
        const winL = new Map();
        const docL = new Map();

        const bldgOpts = [
            createEl("option", { value: "", textContent: "Todos los edificios" }),
            createEl("option", { value: "buildingA", textContent: "Edificio A (Atención al Estudiante)" }),
            createEl("option", { value: "buildingB", textContent: "Edificio B (Aulas B101-B106 & Farmacia)" }),
            createEl("option", { value: "buildingK", textContent: "Edificio K (Cafetería Central & Terrazas)" }),
        ];

        const cEls = {
            catalogAppRoot: createEl("div", {
                id: "catalogAppRoot",
                "data-is-admin": isAdmin ? "true" : "false",
                "data-initial-item-id": initialItemId,
                "data-user-name": "Camila Navarro",
                "data-user-contact": "camila@uamv.edu.ni",
            }),
            catalogGrid: createEl("div", { id: "catalogGrid", class: "hidden" }),
            catalogLoading: createEl("div", { id: "catalogLoading" }),
            catalogEmpty: createEl("div", { id: "catalogEmpty", class: "hidden" }),
            btnClearFiltersEmpty: createEl("button", { id: "btnClearFiltersEmpty", class: "hidden" }),
            catalogItemsCount: createEl("span", { id: "catalogItemsCount" }),
            catalogSearchInput: createEl("input", { id: "catalogSearchInput", value: "" }),
            filterBuilding: createEl("select", { id: "filterBuilding", value: "", options: bldgOpts, children: bldgOpts }),
            filterCategory: createEl("select", { id: "filterCategory", value: "" }),
            filterState: createEl("select", { id: "filterState", value: "" }),
            btnRefreshCatalog: createEl("button", { id: "btnRefreshCatalog" }),
            btnOpenReportDialog: createEl("button", { id: "btnOpenReportDialog" }),
            activeBuildingFilterBanner: createEl("div", { id: "activeBuildingFilterBanner", class: "hidden" }),
            activeBuildingFilterLabel: createEl("span", { id: "activeBuildingFilterLabel" }),
            btnClearBuildingFilter: createEl("button", { id: "btnClearBuildingFilter" }),
            itemDetailModal: createEl("div", { id: "itemDetailModal", class: "hidden" }),
            btnCloseItemDetailModal: createEl("button", { id: "btnCloseItemDetailModal" }),
            btnCloseItemDetailError: createEl("button", { id: "btnCloseItemDetailError" }),
            itemDetailLoading: createEl("div", { id: "itemDetailLoading", class: "hidden" }),
            itemDetailError: createEl("div", { id: "itemDetailError", class: "hidden" }),
            itemDetailContent: createEl("div", { id: "itemDetailContent", class: "hidden" }),
            detailItemPhoto: createEl("img", { id: "detailItemPhoto", class: "hidden" }),
            detailItemNoPhoto: createEl("div", { id: "detailItemNoPhoto" }),
            detailStateBadge: createEl("div", { id: "detailStateBadge" }),
            detailCategoryBadge: createEl("span", { id: "detailCategoryBadge" }),
            detailTicketId: createEl("span", { id: "detailTicketId" }),
            detailItemTitle: createEl("h2", { id: "detailItemTitle" }),
            btnDetailFilterBuilding: createEl("button", { id: "btnDetailFilterBuilding" }),
            detailItemLocation: createEl("span", { id: "detailItemLocation" }),
            detailItemDescription: createEl("p", { id: "detailItemDescription" }),
            detailItemDate: createEl("span", { id: "detailItemDate" }),
            detailItemReporterWrap: createEl("div", { id: "detailItemReporterWrap", class: "hidden" }),
            detailItemReporter: createEl("span", { id: "detailItemReporter" }),
            detailItemResolvedWrap: createEl("div", { id: "detailItemResolvedWrap", class: "hidden" }),
            detailItemResolvedDate: createEl("span", { id: "detailItemResolvedDate" }),
            detailCustodyBox: createEl("div", { id: "detailCustodyBox" }),
            detailCustodyText: createEl("span", { id: "detailCustodyText" }),
            detailSecretBox: createEl("div", { id: "detailSecretBox", class: "hidden" }),
            detailSecretText: createEl("p", { id: "detailSecretText" }),
            btnDetailViewOnMap: createEl("a", { id: "btnDetailViewOnMap" }),
            btnDetailMoreInBuilding: createEl("button", { id: "btnDetailMoreInBuilding" }),
            btnDetailCopyLink: createEl("button", { id: "btnDetailCopyLink" }),
            detailCopyLinkLabel: createEl("span", { id: "detailCopyLinkLabel" }),
            btnToggleClaimForm: createEl("button", { id: "btnToggleClaimForm" }),
            detailClaimSection: createEl("div", { id: "detailClaimSection", class: "hidden" }),
            detailClaimForm: createEl("form", { id: "detailClaimForm" }),
            claimantNameInput: createEl("input", { id: "claimantNameInput" }),
            claimantContactInput: createEl("input", { id: "claimantContactInput" }),
            claimSecretInput: createEl("input", { id: "claimSecretInput" }),
            btnCancelClaimForm: createEl("button", { id: "btnCancelClaimForm" }),
            btnSubmitClaimForm: createEl("button", { id: "btnSubmitClaimForm" }),
            detailClaimAlert: createEl("div", { id: "detailClaimAlert", class: "hidden" }),
        };

        const bodyEl = createEl("body");
        const doc = {
            readyState: "complete",
            body: bodyEl,
            getElementById: (id) => cEls[id] || null,
            createElement: (tag) => createEl(tag),
            addEventListener(evt, fn) {
                if (!docL.has(evt)) docL.set(evt, []);
                docL.get(evt).push(fn);
            },
            dispatchEvent(evt) {
                (docL.get(evt.type) || []).forEach(fn => fn(evt));
            },
        };

        const locObj = { pathname, search, origin: "http://localhost:5000" };
        const historyObj = {
            replaceState(state, _title, url) {
                historyLog.push({ method: "replaceState", url });
                const u = new URL(url, "http://localhost:5000");
                locObj.pathname = u.pathname;
                locObj.search = u.search;
            },
            pushState(state, _title, url) {
                historyLog.push({ method: "pushState", url });
                const u = new URL(url, "http://localhost:5000");
                locObj.pathname = u.pathname;
                locObj.search = u.search;
            },
        };

        const mockFetch = async (url) => {
            fetchCalls.push(url);
            const u = new URL(url, "http://localhost:5000");
            const itemMatch = u.pathname.match(/^\/api\/lost-found-object\/items\/(\d+)$/);
            if (itemMatch) {
                const id = parseInt(itemMatch[1], 10);
                const found = sampleItems.find(it => it.Id === id);
                if (!found) {
                    return { ok: false, status: 404, json: async () => ({ success: false, error: "Not found" }) };
                }
                return { ok: true, status: 200, json: async () => ({ success: true, item: found }) };
            }
            if (u.pathname === "/api/lost-found-object/items") {
                const b = (u.searchParams.get("building") || "").toLowerCase();
                const items = b ? sampleItems.filter(it => it.Location.toLowerCase() === b) : sampleItems;
                return { ok: true, status: 200, json: async () => ({ success: true, count: items.length, items }) };
            }
            return { ok: false, status: 404, json: async () => ({ success: false }) };
        };

        const win = {
            document: doc,
            location: locObj,
            history: historyObj,
            URLSearchParams,
            APP_CONFIG: { currentLang: "spa" },
            APP_TRANSLATIONS: spaDict,
            JaguarI18n: { isSpanish: () => cLangRef.current === "spa" },
            t: makeTranslator(cLangRef, cDictRef),
            fetch: mockFetch,
            addEventListener(evt, fn) {
                if (!winL.has(evt)) winL.set(evt, []);
                winL.get(evt).push(fn);
            },
            dispatchEvent(evt) {
                (winL.get(evt.type) || []).forEach(fn => fn(evt));
            },
            setTimeout,
            clearTimeout,
            console,
        };
        win.window = win;
        win.globalThis = win;

        const catalogSrc = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/catalogScreen.js"), "utf8");
        vm.runInContext(catalogSrc, vm.createContext(win));

        return { win, doc, cEls, fetchCalls, historyLog, locObj, cLangRef, cDictRef };
    }

    // Scenario A: ?building=buildingB pre-filters catalog and lets user clear it
    const sbBuilding = createCatalogSandbox({ search: "?building=buildingB" });
    await new Promise(r => setTimeout(r, 20));

    assert.equal(sbBuilding.cEls.filterBuilding.value, "buildingB", "Building dropdown must select buildingB");
    assert.equal(sbBuilding.cEls.activeBuildingFilterBanner.classList.contains("hidden"), false, "Active building banner must be visible");
    assert.ok(sbBuilding.cEls.activeBuildingFilterLabel.textContent.includes("Edificio B"), "Banner must show localized building name");
    assert.ok(sbBuilding.fetchCalls.includes("/api/lost-found-object/items?building=buildingB"), "Must fetch filtered API");
    assert.equal(sbBuilding.cEls.catalogGrid.children.length, 1, "Must render only Building B's item");
    assert.equal(sbBuilding.cEls.itemDetailModal.classList.contains("hidden"), true, "Modal stays closed when no ?item param");

    // Click clear building filter -> restores full catalog and clears URL query param
    sbBuilding.cEls.btnClearBuildingFilter.dispatchEvent({ type: "click" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(sbBuilding.cEls.filterBuilding.value, "", "Building filter cleared");
    assert.equal(sbBuilding.cEls.activeBuildingFilterBanner.classList.contains("hidden"), true, "Banner hidden after clear");
    assert.equal(sbBuilding.locObj.search, "", "URL query cleared");
    assert.equal(sbBuilding.cEls.catalogGrid.children.length, 3, "All 3 items rendered after clearing filter");

    // Scenario B: ?item=1 auto-opens item detail modal on load; Escape closes it & removes ?item
    const sbItem = createCatalogSandbox({ search: "?item=1" });
    await new Promise(r => setTimeout(r, 20));

    assert.equal(sbItem.cEls.itemDetailModal.classList.contains("hidden"), false, "Detail modal must auto-open for ?item=1");
    assert.equal(sbItem.cEls.itemDetailContent.classList.contains("hidden"), false, "Detail content visible");
    assert.equal(sbItem.cEls.detailItemTitle.textContent, "Calculadora Casio");
    assert.equal(sbItem.cEls.detailItemDescription.textContent, "Calculadora científica completa");
    assert.equal(sbItem.cEls.detailTicketId.textContent, "#1");
    assert.equal(sbItem.cEls.btnDetailViewOnMap.href, "/mapa?focus=buildingB&mode=25d");

    // Escape closes modal and removes ?item from URL
    sbItem.doc.dispatchEvent({ type: "keydown", key: "Escape" });
    assert.equal(sbItem.cEls.itemDetailModal.classList.contains("hidden"), true, "Escape closes detail modal");
    assert.equal(sbItem.locObj.search, "", "?item removed from URL after close");

    // Scenario C: Combined ?building=buildingK&item=1 filters catalog by buildingK AND opens item #1 (from buildingB!)
    const sbCombo = createCatalogSandbox({ search: "?building=buildingK&item=1" });
    await new Promise(r => setTimeout(r, 20));

    assert.equal(sbCombo.cEls.filterBuilding.value, "buildingK");
    assert.equal(sbCombo.cEls.catalogGrid.children.length, 1, "Background grid shows Building K");
    assert.equal(sbCombo.cEls.itemDetailModal.classList.contains("hidden"), false, "Item #1 modal opens even across buildings");
    assert.equal(sbCombo.cEls.detailItemTitle.textContent, "Calculadora Casio");

    // Closing modal preserves ?building=buildingK while stripping ?item=1
    sbCombo.cEls.btnCloseItemDetailModal.dispatchEvent({ type: "click" });
    assert.equal(sbCombo.cEls.itemDetailModal.classList.contains("hidden"), true);
    assert.equal(sbCombo.locObj.search, "?building=buildingK");

    // Scenario D: Dedicated path route /catalog/2 via data-initial-item-id="2"
    const sbRoute = createCatalogSandbox({ pathname: "/catalog/2", initialItemId: "2" });
    await new Promise(r => setTimeout(r, 20));

    assert.equal(sbRoute.cEls.itemDetailModal.classList.contains("hidden"), false);
    assert.equal(sbRoute.cEls.detailItemTitle.textContent, "Termo Yeti Azul");

    // Clicking "More from this building" filters catalog to buildingK and closes modal
    sbRoute.cEls.btnDetailMoreInBuilding.dispatchEvent({ type: "click" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(sbRoute.cEls.itemDetailModal.classList.contains("hidden"), true);
    assert.equal(sbRoute.cEls.filterBuilding.value, "buildingK");
    assert.equal(sbRoute.locObj.pathname, "/catalog");
    assert.equal(sbRoute.locObj.search, "?building=buildingK");

    // Scenario E: Non-existent ?item=9999 displays graceful not-found state
    const sbMissing = createCatalogSandbox({ search: "?item=9999" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(sbMissing.cEls.itemDetailModal.classList.contains("hidden"), false);
    assert.equal(sbMissing.cEls.itemDetailError.classList.contains("hidden"), false, "Not-found error view must display");
    assert.equal(sbMissing.cEls.itemDetailContent.classList.contains("hidden"), true);

    console.log("ALL_MAP_AND_CATALOG_JS_TESTS_PASSED");
})().catch((err) => {
    console.error(err);
    process.exit(1);
});
"""

        env = os.environ.copy()
        env["TEST_SPA_DICT"] = json.dumps(spa_dict)
        env["TEST_ENG_DICT"] = json.dumps(eng_dict)

        proc = subprocess.run(
            [node_bin, "-e", js_test],
            cwd=str(PROJECT_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"JS tests failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        self.assertIn("ALL_MAP_AND_CATALOG_JS_TESTS_PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
