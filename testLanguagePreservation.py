"""
testLanguagePreservation.py
================================================================================
Automated test suite verifying:
1. Reactive non-reloading language switching API & translation dictionaries
2. Server-rendered auth, navigation, and catalog templates include reactive
   data-lang-switch, data-i18n*, and formDraftManager / i18nManager hooks
3. Session language synchronization across backend auth endpoints after
   reactive POST /api/i18n/set-language/<lang> calls
4. Client-side JS unit tests (via Node.js) for i18nManager.js and
   formDraftManager.js:
   - Clicking ES/EN prevents full page reload, updates DOM & title in place,
     preserves all input values (including password in memory), and excludes
     passwords from sessionStorage
   - Scoped sessionStorage draft persistence & automatic rehydration for auth
     and navigation forms
   - Clearing stored draft data once a form is successfully submitted or reset
   - Out-of-order async language switch race protection
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


class TestLanguagePreservationBackend(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.original_db_path = Config.DATABASE_PATH
        Config.DATABASE_PATH = self.temp_db_path
        initDb(dbPath=self.temp_db_path, seedSampleData=True)

        self.app = createApp(Config)
        self.app.config["TESTING"] = True
        self.app.config["DB_PATH"] = self.temp_db_path
        self.client = self.app.test_client()

    def tearDown(self):
        Config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_translation_dictionaries_are_symmetrical(self):
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
        self.assertIn("auth.sign_up_heading", spa_keys)
        self.assertIn("auth.validation.cedula_invalid", spa_keys)
        self.assertIn("map.where_am_i", spa_keys)
        self.assertIn("nav.map", spa_keys)

    def test_api_set_language_updates_session_and_returns_translations(self):
        res_spa = self.client.post("/api/i18n/set-language/spa")
        self.assertEqual(res_spa.status_code, 200)
        data_spa = res_spa.get_json()
        self.assertTrue(data_spa["success"])
        self.assertEqual(data_spa["language"], "spa")
        self.assertIn("translations", data_spa)
        self.assertEqual(data_spa["translations"]["auth"]["sign_up_heading"], "Crear una cuenta")
        self.assertEqual(data_spa["translations"]["map"]["where_am_i"], "¿Dónde te encuentras?")

        with self.client.session_transaction() as sess:
            self.assertEqual(sess["idioma"], "spa")
            self.assertEqual(sess["lang"], "spa")

        # Switching to English updates session & returns English dictionary
        res_eng = self.client.post("/api/i18n/set-language/eng")
        self.assertEqual(res_eng.status_code, 200)
        data_eng = res_eng.get_json()
        self.assertTrue(data_eng["success"])
        self.assertEqual(data_eng["language"], "eng")
        self.assertEqual(data_eng["translations"]["auth"]["sign_up_heading"], "Create account")
        self.assertEqual(data_eng["translations"]["map"]["where_am_i"], "Where are you?")

        # Accepts ISO shorthand "es"
        res_es = self.client.post("/api/i18n/set-language/es")
        self.assertEqual(res_es.status_code, 200)
        self.assertEqual(res_es.get_json()["language"], "spa")

    def test_backend_auth_error_messages_follow_reactive_session_language(self):
        # Switch to Spanish via API (no page reload)
        self.client.post("/api/i18n/set-language/spa")
        res_es = self.client.post("/api/auth/login", json={
            "identifier": "",
            "password": "",
            "userTypeId": 1,
        })
        self.assertEqual(res_es.status_code, 400)
        self.assertIn("identificación", res_es.get_json()["error"].lower())

        # Switch to English via API (no page reload)
        self.client.post("/api/i18n/set-language/eng")
        res_en = self.client.post("/api/auth/login", json={
            "identifier": "",
            "password": "",
            "userTypeId": 1,
        })
        self.assertEqual(res_en.status_code, 400)
        self.assertIn("identifier", res_en.get_json()["error"].lower())

    def test_fallback_set_language_route_prevents_open_redirect(self):
        res_safe = self.client.get("/set-language/spa?next=/auth/signup?rol=estudiante")
        self.assertEqual(res_safe.status_code, 302)
        self.assertTrue(res_safe.headers["Location"].endswith("/auth/signup?rol=estudiante"))

        res_evil = self.client.get("/set-language/eng?next=//evil.example/phish")
        self.assertEqual(res_evil.status_code, 302)
        self.assertNotIn("evil.example", res_evil.headers["Location"])

    def test_auth_and_map_pages_wire_reactive_i18n_and_draft_persistence(self):
        routes = [
            "/",
            "/auth",
            "/auth/options?mode=signup",
            "/auth/options?mode=signin",
            "/auth/signup?rol=estudiante",
            "/auth/signup?rol=colaborador",
            "/auth/signup?rol=visitante",
            "/auth/signin?rol=estudiante",
            "/auth/signin?rol=colaborador",
            "/auth/signin?rol=visitante",
            "/admin/adminsignin",
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed")
            html = res.get_data(as_text=True)
            self.assertIn("formDraftManager.js", html, f"Missing formDraftManager.js on {route}")
            self.assertIn("i18nManager.js", html, f"Missing i18nManager.js on {route}")
            self.assertIn('data-lang-switch="spa"', html, f"Missing ES reactive toggle on {route}")
            self.assertIn('data-lang-switch="eng"', html, f"Missing EN reactive toggle on {route}")

        # Verify specific draft registration and submit-clear hooks exist in rendered pages
        signup_html = self.client.get("/auth/signup?rol=estudiante").get_data(as_text=True)
        self.assertIn("JaguarFormDrafts.registerForm", signup_html)
        self.assertIn("draftHandle.clear()", signup_html)
        self.assertIn('data-i18n="auth.sign_up_heading"', signup_html)
        self.assertIn('data-i18n="auth.faculties.FIA"', signup_html)

        signin_html = self.client.get("/auth/signin?rol=colaborador").get_data(as_text=True)
        self.assertIn("JaguarFormDrafts.registerForm", signin_html)
        self.assertIn("draftHandle.clear()", signin_html)
        self.assertIn('data-i18n="auth.collaborator_identifier_label"', signin_html)

        admin_signin_html = self.client.get("/admin/adminsignin").get_data(as_text=True)
        self.assertIn("JaguarFormDrafts.registerForm", admin_signin_html)
        self.assertIn("draftHandle.clear()", admin_signin_html)

        map_html = self.client.get("/").get_data(as_text=True)
        self.assertIn('JaguarFormDrafts.registerCustom("mapNavigation"', map_html)
        self.assertIn("clearNavDraft()", map_html)
        self.assertIn('data-i18n="map.where_am_i"', map_html)
        self.assertIn('data-i18n-placeholder="map.where_to_go_placeholder"', map_html)


class TestClientSideI18nAndFormDraftsJS(unittest.TestCase):
    """Runs deterministic Node.js unit tests against formDraftManager.js and i18nManager.js."""

    def test_js_reactive_switcher_and_session_draft_lifecycle(self):
        node_bin = shutil.which("node")
        if not node_bin:
            self.skipTest("Node.js not available in test environment")

        spa_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        eng_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))

        test_script = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const spaDict = JSON.parse(process.env.TEST_SPA_DICT);
const engDict = JSON.parse(process.env.TEST_ENG_DICT);

function createMockStorage() {
    const store = new Map();
    return {
        get length() { return store.size; },
        key(i) { return Array.from(store.keys())[i] ?? null; },
        getItem(k) { return store.has(k) ? store.get(k) : null; },
        setItem(k, v) { store.set(String(k), String(v)); },
        removeItem(k) { store.delete(k); },
        clear() { store.clear(); },
        _dump() { return Object.fromEntries(store.entries()); },
    };
}

function createElement(tag, attrs = {}) {
    const listeners = new Map();
    const classSet = new Set((attrs.class || "").split(/\s+/).filter(Boolean));
    const attrMap = new Map(Object.entries(attrs).filter(([k]) => k !== "class" && k !== "options" && k !== "children"));
    const el = {
        tagName: tag.toUpperCase(),
        id: attrs.id || "",
        name: attrs.name || "",
        type: attrs.type || (tag === "input" ? "text" : ""),
        value: attrs.value || "",
        checked: Boolean(attrs.checked),
        defaultChecked: Boolean(attrs.checked),
        placeholder: attrs.placeholder || "",
        textContent: attrs.textContent || "",
        options: attrs.options || [],
        children: attrs.children || [],
        dataset: {},
        classList: {
            add(...cls) { cls.forEach(c => classSet.add(c)); },
            remove(...cls) { cls.forEach(c => classSet.delete(c)); },
            contains(c) { return classSet.has(c); },
        },
        getAttribute(k) { return attrMap.has(k) ? attrMap.get(k) : null; },
        setAttribute(k, v) {
            attrMap.set(k, String(v));
            if (k === "placeholder") el.placeholder = String(v);
        },
        removeAttribute(k) { attrMap.delete(k); },
        addEventListener(evt, fn) {
            if (!listeners.has(evt)) listeners.set(evt, []);
            listeners.get(evt).push(fn);
        },
        removeEventListener(evt, fn) {
            const arr = listeners.get(evt) || [];
            listeners.set(evt, arr.filter(x => x !== fn));
        },
        dispatchEvent(evt) {
            (listeners.get(evt.type) || []).forEach(fn => fn.call(el, evt));
        },
        closest(selector) {
            if (selector === "[data-lang-switch]" && attrMap.has("data-lang-switch")) return el;
            return null;
        },
        querySelectorAll(selector) {
            const out = [];
            const walk = (node) => {
                for (const ch of (node.children || [])) {
                    if (matchesSelector(ch, selector)) out.push(ch);
                    walk(ch);
                }
            };
            walk(el);
            return out;
        },
        querySelector(selector) {
            return el.querySelectorAll(selector)[0] || null;
        },
    };
    return el;
}

function matchesSelector(el, selector) {
    return selector.split(",").map(s => s.trim()).some((part) => {
        if (part === "input" || part === "select" || part === "textarea") {
            return el.tagName === part.toUpperCase();
        }
        if (part === "title[data-i18n]") {
            return el.tagName === "TITLE" && el.getAttribute("data-i18n") !== null;
        }
        if (part === "title[data-i18n-es][data-i18n-en]") {
            return el.tagName === "TITLE" && el.getAttribute("data-i18n-es") !== null && el.getAttribute("data-i18n-en") !== null;
        }
        if (part === "[data-i18n-es][data-i18n-en]") {
            return el.getAttribute("data-i18n-es") !== null && el.getAttribute("data-i18n-en") !== null;
        }
        const m = part.match(/^\[([a-z0-9-]+)\]$/i);
        if (m) return el.getAttribute(m[1]) !== null;
        return false;
    });
}

function createSandbox(sharedStorage, fetchImpl) {
    const titleEl = createElement("title", { "data-i18n": "auth.sign_up_page_title", textContent: "Crear una cuenta · JaguarFind" });
    const head = createElement("head", { children: [titleEl] });

    const heading = createElement("h1", { "data-i18n": "auth.sign_up_heading", textContent: "Crear una cuenta" });
    const nameLabel = createElement("label", { "data-i18n": "auth.full_name_label", textContent: "Nombre completo" });
    const nameInput = createElement("input", { id: "nombre", name: "nombre", type: "text", "data-i18n-placeholder": "auth.full_name_placeholder", placeholder: "Juan Pérez" });
    const emailInput = createElement("input", { id: "correo", name: "correo", type: "email" });
    const passInput = createElement("input", { id: "password", name: "password", type: "password" });
    const cifInput = createElement("input", { id: "cif", name: "cif", type: "text", "data-i18n-placeholder": "auth.cif_placeholder", placeholder: "8 dígitos" });
    const optFIA = createElement("option", { value: "FIA", "data-i18n": "auth.faculties.FIA", textContent: "Ingeniería y Arquitectura" });
    optFIA.defaultSelected = true;
    const optFCM = createElement("option", { value: "FCM", "data-i18n": "auth.faculties.FCM", textContent: "Ciencias Médicas" });
    const facultySelect = createElement("select", { id: "facultad", name: "facultad", value: "FIA", options: [optFIA, optFCM], children: [optFIA, optFCM] });

    const form = createElement("form", {
        id: "signUpForm",
        children: [heading, nameLabel, nameInput, emailInput, passInput, cifInput, facultySelect],
    });

    const esLink = createElement("a", {
        "data-lang-switch": "spa",
        "data-i18n-title": "nav.switch_to_es",
        class: "bg-white text-slate-900 shadow-xs",
        textContent: "ES",
    });
    const enLink = createElement("a", {
        "data-lang-switch": "eng",
        "data-i18n-title": "nav.switch_to_en",
        class: "text-slate-500 hover:text-slate-800",
        textContent: "EN",
    });

    const docRoot = createElement("div", { children: [form, esLink, enLink] });
    const docListeners = new Map();
    const winListeners = new Map();

    const document = {
        documentElement: { lang: "spa" },
        head,
        title: titleEl.textContent,
        getElementById(id) {
            const all = [form, nameInput, emailInput, passInput, cifInput, facultySelect];
            return all.find(el => el.id === id) || null;
        },
        querySelectorAll(sel) { return docRoot.querySelectorAll(sel); },
        querySelector(sel) { return docRoot.querySelector(sel); },
        addEventListener(evt, fn) {
            if (!docListeners.has(evt)) docListeners.set(evt, []);
            docListeners.get(evt).push(fn);
        },
        dispatchClick(target) {
            let prevented = false;
            const evt = {
                type: "click",
                target,
                button: 0,
                preventDefault() { prevented = true; },
            };
            (docListeners.get("click") || []).forEach(fn => fn(evt));
            return prevented;
        },
    };

    const windowObj = {
        document,
        sessionStorage: sharedStorage,
        location: { pathname: "/auth/signup" },
        APP_CONFIG: { currentLang: "spa" },
        APP_TRANSLATIONS: spaDict,
        fetch: fetchImpl,
        console,
        CustomEvent: function(type, init) { this.type = type; this.detail = init && init.detail; },
        addEventListener(evt, fn) {
            if (!winListeners.has(evt)) winListeners.set(evt, []);
            winListeners.get(evt).push(fn);
        },
        dispatchEvent(evt) {
            (winListeners.get(evt.type) || []).forEach(fn => fn(evt));
        },
    };
    windowObj.window = windowObj;
    windowObj.globalThis = windowObj;

    const draftSrc = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/formDraftManager.js"), "utf8");
    const i18nSrc = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/i18nManager.js"), "utf8");
    const ctx = vm.createContext(windowObj);
    vm.runInContext(draftSrc, ctx);
    vm.runInContext(i18nSrc, ctx);

    return {
        window: windowObj,
        document,
        els: { form, heading, nameLabel, nameInput, emailInput, passInput, cifInput, facultySelect, optFIA, optFCM, esLink, enLink },
    };
}

(async () => {
    const sharedStorage = createMockStorage();
    const fetchCalls = [];
    const mockFetch = async (url, opts) => {
        fetchCalls.push({ url, opts });
        const isSpa = url.includes("/spa");
        return {
            ok: true,
            status: 200,
            async json() {
                return {
                    success: true,
                    language: isSpa ? "spa" : "eng",
                    translations: isSpa ? spaDict : engDict,
                };
            },
        };
    };

    // 1. Register auth form and type user inputs (including password)
    const sb1 = createSandbox(sharedStorage, mockFetch);
    const handle1 = sb1.window.JaguarFormDrafts.registerForm(sb1.els.form, { draftKey: "signUp:estudiante" });

    sb1.els.nameInput.value = "Camila Morales";
    sb1.els.emailInput.value = "camila@uamv.edu.ni";
    sb1.els.passInput.value = "SuperSecret123";
    sb1.els.cifInput.value = "22014567";
    sb1.els.facultySelect.value = "FCM";
    sb1.els.form.dispatchEvent({ type: "input" });

    // Verify password is NEVER persisted in sessionStorage
    const savedBeforeSwitch = sb1.window.JaguarFormDrafts.getDraft("signUp:estudiante");
    assert.equal(savedBeforeSwitch.fields.nombre, "Camila Morales");
    assert.equal(savedBeforeSwitch.fields.correo, "camila@uamv.edu.ni");
    assert.equal(savedBeforeSwitch.fields.cif, "22014567");
    assert.equal(savedBeforeSwitch.fields.facultad, "FCM");
    assert.equal(Object.prototype.hasOwnProperty.call(savedBeforeSwitch.fields, "password"), false);

    // 2. Click EN language toggle -> must prevent default (no reload), update DOM reactively, keep ALL inputs incl. password
    let langEventDetail = null;
    sb1.window.addEventListener("jaguarLanguageChanged", (e) => { langEventDetail = e.detail; });

    const defaultPrevented = sb1.document.dispatchClick(sb1.els.enLink);
    assert.equal(defaultPrevented, true, "Language toggle click must prevent full page reload");

    // Wait for async fetch microtasks
    await new Promise(r => setTimeout(r, 15));

    assert.equal(fetchCalls.length, 1);
    assert.equal(fetchCalls[0].url, "/api/i18n/set-language/eng");
    assert.equal(sb1.window.APP_CONFIG.currentLang, "eng");
    assert.equal(sb1.document.documentElement.lang, "eng");
    assert.equal(sb1.document.title, "Create account · JaguarFind");
    assert.equal(sb1.els.heading.textContent, "Create account");
    assert.equal(sb1.els.nameLabel.textContent, "Full name");
    assert.equal(sb1.els.nameInput.placeholder, "John Doe");
    assert.equal(sb1.els.cifInput.placeholder, "8 digits");
    assert.equal(sb1.els.optFIA.textContent, "Engineering & Architecture");
    assert.equal(sb1.els.optFCM.textContent, "Medical Sciences");
    assert.equal(sb1.els.enLink.classList.contains("bg-white"), true);
    assert.equal(sb1.els.esLink.classList.contains("bg-white"), false);
    assert.equal(langEventDetail.lang, "eng");
    assert.equal(langEventDetail.previousLang, "spa");

    // ALL typed values (including password!) remain intact without reload
    assert.equal(sb1.els.nameInput.value, "Camila Morales");
    assert.equal(sb1.els.emailInput.value, "camila@uamv.edu.ni");
    assert.equal(sb1.els.passInput.value, "SuperSecret123");
    assert.equal(sb1.els.cifInput.value, "22014567");
    assert.equal(sb1.els.facultySelect.value, "FCM");

    // 3. Simulate full page reload -> fresh DOM rehydrates non-password draft automatically
    const sb2 = createSandbox(sharedStorage, mockFetch);
    const handle2 = sb2.window.JaguarFormDrafts.registerForm(sb2.els.form, { draftKey: "signUp:estudiante" });
    assert.equal(sb2.els.nameInput.value, "Camila Morales");
    assert.equal(sb2.els.emailInput.value, "camila@uamv.edu.ni");
    assert.equal(sb2.els.cifInput.value, "22014567");
    assert.equal(sb2.els.facultySelect.value, "FCM");
    assert.equal(sb2.els.passInput.value, ""); // password never stored in sessionStorage

    // Different role scope does not bleed drafts
    const sbOtherRole = createSandbox(sharedStorage, mockFetch);
    sbOtherRole.window.JaguarFormDrafts.registerForm(sbOtherRole.els.form, { draftKey: "signUp:visitante" });
    assert.equal(sbOtherRole.els.nameInput.value, "");

    // 4. Successful submission clears stored draft data
    handle2.clear();
    assert.equal(sb2.window.JaguarFormDrafts.hasDraft("signUp:estudiante"), false);

    // Subsequent reload starts completely clean
    const sb3 = createSandbox(sharedStorage, mockFetch);
    sb3.window.JaguarFormDrafts.registerForm(sb3.els.form, { draftKey: "signUp:estudiante" });
    assert.equal(sb3.els.nameInput.value, "");
    assert.equal(sb3.els.emailInput.value, "");
    assert.equal(sb3.els.cifInput.value, "");
    assert.equal(sb3.els.facultySelect.value, "FIA");

    // 5. Custom navigation draft persistence, rehydration & clear-on-submit/reset
    let navState = { originValue: "", destinationValue: "", accessibleOnly: false };
    const navHandle = sb3.window.JaguarFormDrafts.registerCustom("mapNavigation", {
        read: () => (navState.originValue || navState.destinationValue || navState.accessibleOnly) ? { ...navState } : null,
        restore: (d) => { navState = { ...d }; },
    });
    navState = { originValue: "Edificio A", destinationValue: "Edificio O", accessibleOnly: true };
    navHandle.save();
    assert.equal(sb3.window.JaguarFormDrafts.hasDraft("mapNavigation"), true);

    let rehydratedNav = null;
    const sb4 = createSandbox(sharedStorage, mockFetch);
    const navHandle2 = sb4.window.JaguarFormDrafts.registerCustom("mapNavigation", {
        read: () => rehydratedNav,
        restore: (d) => { rehydratedNav = d; },
    });
    assert.equal(rehydratedNav.originValue, "Edificio A");
    assert.equal(rehydratedNav.destinationValue, "Edificio O");
    assert.equal(rehydratedNav.accessibleOnly, true);

    navHandle2.clear();
    assert.equal(sb4.window.JaguarFormDrafts.hasDraft("mapNavigation"), false);

    // 6. Race-condition test: slower first request must not overwrite faster latest language switch
    let resolveSlowEng;
    const raceFetch = (url) => new Promise((resolve) => {
        if (url.includes("/eng")) {
            resolveSlowEng = () => resolve({
                ok: true,
                status: 200,
                async json() { return { success: true, language: "eng", translations: engDict }; },
            });
        } else {
            resolve({
                ok: true,
                status: 200,
                async json() { return { success: true, language: "spa", translations: spaDict }; },
            });
        }
    });
    const sbRace = createSandbox(createMockStorage(), raceFetch);
    const p1 = sbRace.window.JaguarI18n.setLanguage("eng");
    const p2 = sbRace.window.JaguarI18n.setLanguage("spa", { force: true });
    await p2;
    resolveSlowEng();
    const r1 = await p1;
    assert.equal(r1.stale, true);
    assert.equal(sbRace.window.APP_CONFIG.currentLang, "spa");
    assert.equal(sbRace.els.heading.textContent, "Crear una cuenta");

    console.log("ALL_JS_I18N_AND_DRAFT_TESTS_PASSED");
})().catch((err) => {
    console.error(err);
    process.exit(1);
});
"""

        env = os.environ.copy()
        env["TEST_SPA_DICT"] = json.dumps(spa_dict)
        env["TEST_ENG_DICT"] = json.dumps(eng_dict)

        proc = subprocess.run(
            [node_bin, "-e", test_script],
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
        self.assertIn("ALL_JS_I18N_AND_DRAFT_TESTS_PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
