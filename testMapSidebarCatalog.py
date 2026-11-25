"""
testMapSidebarCatalog.py
================================================================================
Automated test suite verifying the Map Sidebar Lost & Found Objects Catalog tab
and Item Detail Dialog:
1. Map routes (/, /map, /mapa) render a responsive sidebar switcher, with the
   catalog tab and panel available only to authenticated users, plus the shared
   detail dialog (#itemDetailModal) and mapSidebarCatalog.js (admin-only controls
   are gated to UserTypeId == 4)
2. Bilingual dictionary symmetry and presence of new sidebar catalog keys
3. Client-side JS behavior (via Node.js) for mapSidebarCatalog.js:
   - Fetches and renders catalog cards with XSS escaping & safe PhotoUrl checks
   - Selecting a card (click or keyboard Enter) opens #itemDetailModal with
     authoritative item details, custody info, and secret verification notice
   - Dismissing via Close button, backdrop click, or Escape key
   - Filtering by search, category, custody status, and building + reset
   - Focusing an item's location on the live map (including auto-closing mobile
     sidebar drawer when viewport < 1024px)
   - Submitting an inline claim request from the detail dialog
   - Reactive refresh on lostObjectReported and live ES/EN re-rendering on
     jaguarLanguageChanged
   - Graceful error & retry handling
================================================================================
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from backend.app import createApp
from backend.config import Config
from backend.database import initDb


PROJECT_ROOT = Path(__file__).resolve().parent


class TestMapSidebarCatalogBackend(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.original_db_path = Config.DATABASE_PATH
        Config.DATABASE_PATH = self.temp_db_path
        initDb(dbPath=self.temp_db_path, seedSampleData=True)

        self.app = createApp(Config)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        Config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def _login_as(self, user_type_id=1, full_name="Camila Navarro", email="camila@uamv.edu.ni"):
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "Id": 2 if user_type_id != 4 else 1,
                "UserTypeId": user_type_id,
                "UserTypeName": "Admin" if user_type_id == 4 else "Student",
                "FullName": full_name,
                "Email": email,
            }
            sess["idioma"] = "spa"
            sess["lang"] = "spa"

    def test_sidebar_catalog_translations_symmetrical(self):
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

        spa_keys = flatten(spa)
        eng_keys = flatten(eng)
        self.assertEqual(spa_keys, eng_keys)
        for required_key in [
            "map.tabs.lost_found",
            "lost_found.sidebar_catalog_title",
            "lost_found.sidebar_search_placeholder",
            "lost_found.sidebar_open_full_catalog",
            "lost_found.sidebar_locate_on_map",
            "lost_found.sidebar_load_error",
            "lost_found.sidebar_retry",
            "lost_found.sidebar_refresh",
            "lost_found.sidebar_items_short_singular",
            "lost_found.sidebar_items_short_plural",
        ]:
            self.assertIn(required_key, spa_keys)

    def test_map_screen_renders_sidebar_catalog_tab_and_detail_dialog(self):
        # Unauthenticated visitors do not see the lost & found catalog in the sidebar.
        for route in ("/", "/map", "/mapa"):
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('id="sidebarSwitcher"', html)
            self.assertIn('id="sidebarTabNav"', html)
            self.assertIn('id="sidebarTabDir"', html)
            self.assertNotIn('id="sidebarTabCatalog"', html)
            self.assertNotIn('id="sidebarPanelCatalog"', html)
            self.assertNotIn('id="sidebarLostFoundComponent"', html)
            self.assertNotIn('id="sidebarCatalogList"', html)
            self.assertIn('id="itemDetailModal"', html)
            self.assertIn("mapSidebarCatalog.js", html)
            # Non-admin must NOT receive admin state modal
            self.assertNotIn('id="adminStateModal"', html)
            self.assertNotIn('id="btnDetailAdminEditState"', html)

        # Authenticated student still does not get admin modal
        self._login_as(user_type_id=1)
        res_student = self.client.get("/mapa")
        self.assertEqual(res_student.status_code, 200)
        student_html = res_student.get_data(as_text=True)
        self.assertIn('data-is-admin="false"', student_html)
        self.assertIn('data-user-name="Camila Navarro"', student_html)
        self.assertIn('id="sidebarTabCatalog"', student_html)
        self.assertIn('id="sidebarPanelCatalog"', student_html)
        self.assertIn('id="sidebarLostFoundComponent"', student_html)
        self.assertNotIn('id="adminStateModal"', student_html)

        # Authenticated admin gets admin state modal & button
        self._login_as(user_type_id=4, full_name="Administrador CAE", email="admin@uamv.edu.ni")
        res_admin = self.client.get("/mapa")
        self.assertEqual(res_admin.status_code, 200)
        admin_html = res_admin.get_data(as_text=True)
        self.assertIn('data-is-admin="true"', admin_html)
        self.assertIn('id="adminStateModal"', admin_html)
        self.assertIn('id="btnDetailAdminEditState"', admin_html)


class TestMapSidebarCatalogClientJS(unittest.TestCase):
    """Runs deterministic Node.js tests against mapSidebarCatalog.js."""

    def test_sidebar_catalog_cards_and_detail_dialog_js(self):
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

function makeTranslator(dictRef) {
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
        focused: false,
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
            child.parentNode = this;
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
            const eventObj = Object.assign({
                preventDefault() { this.defaultPrevented = true; },
                stopPropagation() {},
                target: el,
                defaultPrevented: false,
            }, evt);
            (listeners.get(eventObj.type) || []).forEach(fn => fn.call(el, eventObj));
            return eventObj;
        },
        focus() { this.focused = true; },
        closest(selector) {
            const m = selector.match(/^\[([a-z0-9-]+)\]$/i);
            if (m) {
                let curr = this;
                while (curr) {
                    if (curr.getAttribute && curr.getAttribute(m[1]) !== null) return curr;
                    curr = curr.parentNode || null;
                }
            }
            return null;
        },
        querySelectorAll(selector) {
            const m = selector.match(/^\[([a-z0-9-]+)\]$/i);
            if (!m) return [];
            const out = [];
            const walk = (node) => {
                for (const ch of (node.children || [])) {
                    if (ch.getAttribute && ch.getAttribute(m[1]) !== null) out.push(ch);
                    walk(ch);
                }
            };
            walk(this);
            return out;
        },
    };
    return el;
}

(async () => {
    const sampleItems = [
        {
            Id: 1,
            ItemName: "Calculadora <script>alert(1)</script>",
            Category: "electronics",
            Location: "buildingB",
            locationName: "Edificio B",
            Description: "Calculadora científica negra con tapa",
            LostObjectStateId: 2,
            StateName: "In Custody",
            DateTimeReported: "2026-11-24 10:00:00",
            hasSecretDetail: true,
            SecretDetail: null,
            PhotoUrl: "javascript:alert(1)",
            ReporterName: "Camila Navarro",
        },
        {
            Id: 2,
            ItemName: "Termo Yeti Azul",
            Category: "personalItems",
            Location: "buildingK",
            locationName: "Edificio K",
            Description: "Termo azul marino 26oz encontrado en terraza",
            LostObjectStateId: 1,
            StateName: "Reported",
            DateTimeReported: "2026-11-24 11:30:00",
            hasSecretDetail: false,
            SecretDetail: null,
            PhotoUrl: "https://example.com/yeti.jpg",
            ReporterName: "Carlos Mendoza",
        },
    ];

    const langRef = { current: "spa" };
    const dictRef = { current: spaDict };
    const fetchCalls = [];
    const focusedBuildings = [];
    const sidebarToggles = [];
    const activeTabs = [];
    const winL = new Map();
    const docL = new Map();
    let forceListFailure = false;

    const bldgOpts = [
        createEl("option", { value: "", textContent: "Todos los edificios" }),
        createEl("option", { value: "buildingB", textContent: "Edificio B (Aulas B101-B106 & Farmacia)" }),
        createEl("option", { value: "buildingK", textContent: "Edificio K (Cafetería Central & Terrazas)" }),
    ];

    const els = {
        sidebarLostFoundComponent: createEl("div", {
            id: "sidebarLostFoundComponent",
            "data-is-admin": "false",
            "data-user-name": "Camila Navarro",
            "data-user-contact": "camila@uamv.edu.ni",
        }),
        sidebarCatalogList: createEl("div", { id: "sidebarCatalogList", class: "hidden" }),
        sidebarCatalogCountBadge: createEl("span", { id: "sidebarCatalogCountBadge" }),
        sidebarTabCatalogBadge: createEl("span", { id: "sidebarTabCatalogBadge", class: "hidden" }),
        sidebarCatalogSearchInput: createEl("input", { id: "sidebarCatalogSearchInput", value: "" }),
        btnSidebarClearSearch: createEl("button", { id: "btnSidebarClearSearch", class: "hidden" }),
        sidebarCatalogCategory: createEl("select", { id: "sidebarCatalogCategory", value: "" }),
        sidebarCatalogState: createEl("select", { id: "sidebarCatalogState", value: "" }),
        sidebarCatalogBuilding: createEl("select", { id: "sidebarCatalogBuilding", value: "", options: bldgOpts, children: bldgOpts }),
        btnSidebarCatalogRefresh: createEl("button", { id: "btnSidebarCatalogRefresh" }),
        sidebarCatalogRefreshIcon: createEl("svg", { id: "sidebarCatalogRefreshIcon" }),
        btnSidebarReportObject: createEl("button", { id: "btnSidebarReportObject" }),
        btnCloseCatalogSidebar: createEl("button", { id: "btnCloseCatalogSidebar" }),
        sidebarCatalogActiveFilterBar: createEl("div", { id: "sidebarCatalogActiveFilterBar", class: "hidden" }),
        sidebarCatalogActiveFilterLabel: createEl("span", { id: "sidebarCatalogActiveFilterLabel" }),
        btnSidebarClearFilters: createEl("button", { id: "btnSidebarClearFilters" }),
        btnSidebarClearFiltersEmpty: createEl("button", { id: "btnSidebarClearFiltersEmpty", class: "hidden" }),
        btnSidebarCatalogRetry: createEl("button", { id: "btnSidebarCatalogRetry" }),
        sidebarCatalogLoading: createEl("div", { id: "sidebarCatalogLoading" }),
        sidebarCatalogError: createEl("div", { id: "sidebarCatalogError", class: "hidden" }),
        sidebarCatalogEmpty: createEl("div", { id: "sidebarCatalogEmpty", class: "hidden" }),
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

    const doc = {
        readyState: "complete",
        getElementById: (id) => els[id] || null,
        createElement: (tag) => createEl(tag),
        addEventListener(evt, fn) {
            if (!docL.has(evt)) docL.set(evt, []);
            docL.get(evt).push(fn);
        },
        dispatchEvent(evt) {
            (docL.get(evt.type) || []).forEach(fn => fn(evt));
        },
    };

    const mockFetch = async (url, init = {}) => {
        fetchCalls.push({ url, method: init.method || "GET", body: init.body || null });
        const u = new URL(url, "http://localhost:5000");

        if (u.pathname.match(/^\/api\/lost-found-object\/items\/(\d+)\/claim$/)) {
            return {
                ok: true,
                status: 200,
                json: async () => ({ success: true, message: "Claim registered at CAE Building A." }),
            };
        }
        const itemMatch = u.pathname.match(/^\/api\/lost-found-object\/items\/(\d+)$/);
        if (itemMatch) {
            const id = parseInt(itemMatch[1], 10);
            const found = sampleItems.find(it => it.Id === id);
            if (!found) return { ok: false, status: 404, json: async () => ({ success: false }) };
            return { ok: true, status: 200, json: async () => ({ success: true, item: found }) };
        }
        if (u.pathname === "/api/lost-found-object/items") {
            if (forceListFailure) {
                return { ok: false, status: 500, json: async () => ({ success: false }) };
            }
            const b = (u.searchParams.get("building") || "").toLowerCase();
            const cat = (u.searchParams.get("category") || "").toLowerCase();
            const st = u.searchParams.get("stateId") || "";
            let items = sampleItems;
            if (b) items = items.filter(it => it.Location.toLowerCase() === b);
            if (cat) items = items.filter(it => it.Category.toLowerCase() === cat);
            if (st) items = items.filter(it => String(it.LostObjectStateId) === st);
            return { ok: true, status: 200, json: async () => ({ success: true, count: items.length, items }) };
        }
        return { ok: false, status: 404, json: async () => ({ success: false }) };
    };

    const win = {
        document: doc,
        innerWidth: 390, // Simulate mobile viewport to verify responsive drawer auto-close
        location: { origin: "http://localhost:5000" },
        URLSearchParams,
        APP_CONFIG: { currentLang: "spa" },
        APP_TRANSLATIONS: spaDict,
        JaguarI18n: { isSpanish: () => langRef.current === "spa" },
        t: makeTranslator(dictRef),
        fetch: mockFetch,
        campus25dController: {
            focusBuilding: (nodeId, opts) => focusedBuildings.push({ nodeId, opts }),
        },
        toggleNavigateMapSidebar: (open) => sidebarToggles.push(open),
        setSidebarActiveTab: (tab) => activeTabs.push(tab),
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

    const src = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/mapSidebarCatalog.js"), "utf8");
    vm.runInContext(src, vm.createContext(win));
    await new Promise(r => setTimeout(r, 25));

    // 1. Initial load renders 2 cards, updates count & tab badges, escapes XSS & sanitizes javascript: PhotoUrl
    assert.equal(els.sidebarCatalogList.children.length, 2, "Must render 2 sidebar catalog cards");
    assert.equal(els.sidebarCatalogCountBadge.textContent, "2 objetos");
    assert.equal(els.sidebarTabCatalogBadge.textContent, "2");
    assert.equal(els.sidebarTabCatalogBadge.classList.contains("hidden"), false);

    const card1 = els.sidebarCatalogList.children[0];
    const card2 = els.sidebarCatalogList.children[1];
    assert.ok(!card1.innerHTML.includes("<script>"), "Card title must be HTML-escaped");
    assert.ok(!card1.innerHTML.includes("javascript:alert"), "Unsafe PhotoUrl must be stripped");
    assert.ok(card2.innerHTML.includes("https://example.com/yeti.jpg"), "Safe HTTPS PhotoUrl must render");

    // 2. Clicking card #1 opens the Item Detail Dialog and fetches authoritative details
    els.sidebarCatalogList.dispatchEvent({ type: "click", target: card1 });
    await new Promise(r => setTimeout(r, 25));

    assert.equal(els.itemDetailModal.classList.contains("hidden"), false, "Detail dialog must open on card click");
    assert.equal(els.itemDetailContent.classList.contains("hidden"), false, "Detail content must be visible");
    assert.equal(els.detailTicketId.textContent, "#1");
    assert.equal(els.detailItemTitle.textContent, "Calculadora <script>alert(1)</script>");
    assert.equal(els.detailItemPhoto.classList.contains("hidden"), true, "Unsafe photo URL must stay hidden in dialog");
    assert.equal(els.detailSecretBox.classList.contains("hidden"), false, "Anti-fraud secret notice must show");
    assert.equal(card1.classList.contains("ring-2"), true, "Selected card must be highlighted");
    assert.ok(fetchCalls.some(c => c.url === "/api/lost-found-object/items/1"), "Must fetch /api/lost-found-object/items/1");

    // 3. Inline claim submission works inside dialog
    els.btnToggleClaimForm.dispatchEvent({ type: "click" });
    assert.equal(els.detailClaimSection.classList.contains("hidden"), false, "Claim section must toggle open");
    els.detailClaimForm.dispatchEvent({ type: "submit" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(els.detailClaimAlert.classList.contains("hidden"), false, "Claim alert must display");
    assert.ok(els.detailClaimAlert.textContent.includes("Claim registered"));

    // 4. Reactive language switch updates open dialog and sidebar cards to English
    langRef.current = "eng";
    dictRef.current = engDict;
    win.dispatchEvent({ type: "jaguarLanguageChanged" });
    assert.equal(els.sidebarCatalogCountBadge.textContent, "2 items");
    assert.ok(els.detailCustodyText.textContent.includes("Building A"), "Dialog custody banner must switch to English");
    assert.ok(els.sidebarCatalogList.children[0].innerHTML.includes("View details"));

    // 5. Clicking "View on 2.5D Map" closes dialog, focuses buildingB, and closes mobile sidebar (< 1024px)
    const mapClickEvt = els.btnDetailViewOnMap.dispatchEvent({ type: "click" });
    assert.equal(mapClickEvt.defaultPrevented, true, "Map focus inside map screen must not trigger full page navigation");
    assert.equal(els.itemDetailModal.classList.contains("hidden"), true, "Dialog must close after map focus");
    assert.equal(focusedBuildings.length, 1);
    assert.equal(focusedBuildings[0].nodeId, "buildingB");
    assert.equal(sidebarToggles[sidebarToggles.length - 1], false, "Mobile sidebar must close on map focus");

    // 6. Keyboard Enter on card #2 opens dialog with photo, and Escape dismisses it
    els.sidebarCatalogList.dispatchEvent({ type: "keydown", key: "Enter", target: card2 });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(els.itemDetailModal.classList.contains("hidden"), false, "Enter key must open detail dialog");
    assert.equal(els.detailTicketId.textContent, "#2");
    assert.equal(els.detailItemPhoto.classList.contains("hidden"), false, "Valid photo must display in dialog");
    assert.equal(els.detailItemPhoto.src, "https://example.com/yeti.jpg");

    // Click "More from this building" filters sidebar to buildingK
    els.btnDetailMoreInBuilding.dispatchEvent({ type: "click" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(els.itemDetailModal.classList.contains("hidden"), true);
    assert.equal(els.sidebarCatalogBuilding.value, "buildingK");
    assert.equal(els.sidebarCatalogList.children.length, 1, "Only buildingK item should show");
    assert.equal(els.sidebarCatalogActiveFilterBar.classList.contains("hidden"), false, "Active filter bar must show");
    assert.equal(activeTabs[activeTabs.length - 1], "catalog");

    // Clear filters restores all 2 items
    els.btnSidebarClearFilters.dispatchEvent({ type: "click" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(els.sidebarCatalogBuilding.value, "");
    assert.equal(els.sidebarCatalogList.children.length, 2);
    assert.equal(els.sidebarCatalogActiveFilterBar.classList.contains("hidden"), true);

    // 7. Escape key closes open detail dialog
    await win.JaguarMapSidebarCatalog.openItemDetailModal(1);
    assert.equal(els.itemDetailModal.classList.contains("hidden"), false);
    doc.dispatchEvent({ type: "keydown", key: "Escape" });
    assert.equal(els.itemDetailModal.classList.contains("hidden"), true, "Escape key must close detail dialog");

    // 8. Error state & retry recovery
    forceListFailure = true;
    await win.JaguarMapSidebarCatalog.loadCatalog();
    assert.equal(els.sidebarCatalogError.classList.contains("hidden"), false, "Error state must show on failed fetch");
    forceListFailure = false;
    els.btnSidebarCatalogRetry.dispatchEvent({ type: "click" });
    await new Promise(r => setTimeout(r, 20));
    assert.equal(els.sidebarCatalogError.classList.contains("hidden"), true, "Retry must clear error state");
    assert.equal(els.sidebarCatalogList.children.length, 2, "Retry must reload items");

    console.log("ALL_MAP_SIDEBAR_CATALOG_JS_TESTS_PASSED");
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
        self.assertIn("ALL_MAP_SIDEBAR_CATALOG_JS_TESTS_PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
