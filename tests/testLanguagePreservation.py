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

import html as html_lib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from backend.app import createApp
from backend.config import Config
from backend.database import initDb


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
        self.assertIn('data-i18n="auth.majors.systems_engineering"', signup_html)
        self.assertIn('data-faculty-key="auth.faculties_full.FIA"', signup_html)

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

    def test_all_dictionary_copies_synced_and_non_empty(self):
        b_eng = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))
        b_spa = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        r_eng = json.loads((PROJECT_ROOT / "languages" / "eng.json").read_text(encoding="utf-8"))
        r_spa = json.loads((PROJECT_ROOT / "languages" / "spa.json").read_text(encoding="utf-8"))

        self.assertEqual(b_eng, r_eng, "languages/eng.json is out of sync with backend/languages/eng.json")
        self.assertEqual(b_spa, r_spa, "languages/spa.json is out of sync with backend/languages/spa.json")

        def collect_leaves(d, prefix=""):
            out = {}
            for k, v in d.items():
                if k.startswith("_"):
                    continue
                full = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    out.update(collect_leaves(v, full))
                else:
                    out[full] = v
            return out

        eng_leaves = collect_leaves(b_eng)
        spa_leaves = collect_leaves(b_spa)
        self.assertEqual(set(eng_leaves.keys()), set(spa_leaves.keys()))
        for k, v in eng_leaves.items():
            if isinstance(v, str):
                self.assertTrue(v.strip(), f"Empty English translation for key {k}")
        for k, v in spa_leaves.items():
            if isinstance(v, str):
                self.assertTrue(v.strip(), f"Empty Spanish translation for key {k}")

    def test_no_missing_i18n_keys_or_legacy_hardcoded_patterns(self):
        eng = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))

        def flatten_keys(d, prefix=""):
            keys = set()
            for k, v in d.items():
                if k.startswith("_"):
                    continue
                full = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    keys |= flatten_keys(v, full)
                else:
                    keys.add(full)
            return keys

        valid_keys = flatten_keys(eng)
        key_patterns = [
            re.compile(r'data-i18n(?:-[a-z-]+)?="([a-zA-Z0-9_.-]+)"'),
            re.compile(r'data-faculty-key="([a-zA-Z0-9_.-]+)"'),
            re.compile(r"""(?:^|[^a-zA-Z0-9_])(?:window\.|global\.|self\.)?(?:t|t_raw|tr|t25d|_t)\(\s*['"]([a-zA-Z0-9_.-]+)['"]"""),
        ]

        missing = []
        forbidden = []
        for root_name in ("frontend", "backend"):
            for dp, _, fns in os.walk(PROJECT_ROOT / root_name):
                if "__pycache__" in dp or "languages" in dp:
                    continue
                for fn in fns:
                    if not fn.endswith((".html", ".js", ".py")):
                        continue
                    fp = Path(dp) / fn
                    rel = fp.relative_to(PROJECT_ROOT).as_posix()
                    text = fp.read_text(encoding="utf-8")
                    lines = text.splitlines()

                    for pat in key_patterns:
                        for m in pat.finditer(text):
                            k = m.group(1)
                            if "." not in k or k.endswith(".") or k == "some.key":
                                continue
                            if k not in valid_keys:
                                line_no = text[:m.start()].count("\n") + 1
                                missing.append((rel, line_no, k))

                    if fn.endswith(".html"):
                        for idx, line in enumerate(lines, 1):
                            if "data-i18n-es=" in line or "data-i18n-en=" in line:
                                forbidden.append((rel, idx, "legacy data-i18n-es/en"))
                            if re.search(r"""\bt\([^)]*default\s*=\s*['"]""", line):
                                forbidden.append((rel, idx, "hardcoded t(..., default='...')"))
                            if re.search(r"\bif\s+es\s+else\b", line):
                                forbidden.append((rel, idx, "hardcoded Jinja if es else"))
                    elif fn.endswith(".py") and "controllers/" in rel:
                        for idx, line in enumerate(lines, 1):
                            if re.search(r"\bdef\s+_?L\b|\bL\(", line):
                                forbidden.append((rel, idx, "legacy L() helper"))

        self.assertEqual(missing, [], f"Missing i18n keys referenced in code: {missing}")
        self.assertEqual(forbidden, [], f"Legacy hardcoded patterns found: {forbidden}")

    def test_every_page_renders_correctly_in_both_spanish_and_english(self):
        spa = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        eng = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))

        def get_val(d, key):
            cur = d
            for part in key.split("."):
                cur = cur[part]
            return cur

        public_key_checks = [
            ("/", "map.directory_title"),
            ("/", "map.plan_route"),
            ("/", "map.buildings.buildingA.name"),
            ("/auth", "auth.login_subtitle"),
            ("/auth/options?mode=signup", "auth.choose_signup"),
            ("/auth/options?mode=signin", "auth.choose_signin"),
            ("/auth/signup?rol=estudiante", "auth.majors.systems_engineering"),
            ("/auth/signup?rol=colaborador", "auth.national_id_label"),
            ("/auth/signup?rol=visitante", "auth.phone_label"),
            ("/auth/signin?rol=estudiante", "auth.student_identifier_label"),
            ("/auth/signin?rol=colaborador", "auth.collaborator_identifier_label"),
            ("/auth/signin?rol=visitante", "auth.visitor_identifier_label"),
            ("/admin/adminsignin", "auth.admin_portal_heading"),
        ]

        def visible_text(raw_html):
            no_script = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw_html, flags=re.S | re.I)
            no_style = re.sub(r"<style\b[^>]*>.*?</style>", " ", no_script, flags=re.S | re.I)
            return html_lib.unescape(re.sub(r"<[^>]+>", " ", no_style))

        # Test all public routes in Spanish and English
        for lang, cur_dict, opp_dict in (("spa", spa, eng), ("eng", eng, spa)):
            self.client.post(f"/api/i18n/set-language/{lang}")
            for route, key in public_key_checks:
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200, f"{route} failed in {lang}")
                html = res.get_data(as_text=True)
                self.assertIn(f'lang="{lang}"', html, f"{route} missing lang='{lang}'")
                vis = visible_text(html)
                expected = get_val(cur_dict, key)
                opposite = get_val(opp_dict, key)
                self.assertIn(expected, vis, f"{route} ({lang}) missing {key}='{expected}'")
                if expected != opposite:
                    self.assertNotIn(opposite, vis, f"{route} ({lang}) leaked opposite {key}='{opposite}'")

        # Test authenticated user catalog route + authenticated admin routes in both languages
        admin_session_user = {
            "Id": 1,
            "FullName": "Admin CAE",
            "UserTypeId": 4,
            "UserTypeName": "Admin",
            "Email": "admin@uamv.edu.ni",
        }
        protected_key_checks = [
            ("/lost-found-object/catalogo", "lost_found.catalog_subtitle"),
            ("/lost-found-object/catalogo", "lost_found.all_categories"),
            ("/admin/dashboard", "admin.dashboard_title"),
            ("/admin/dashboard", "admin.cae_notice_title"),
            ("/admin/items", "lost_found.all_statuses"),
            ("/admin/users", "admin.btn_new_user"),
            ("/admin/users", "admin.btn_create_user"),
        ]

        for lang, cur_dict, opp_dict in (("spa", spa, eng), ("eng", eng, spa)):
            with self.client.session_transaction() as sess:
                sess["user"] = admin_session_user
                sess["idioma"] = lang
                sess["lang"] = lang
            for route, key in protected_key_checks:
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200, f"{route} failed in {lang}")
                html = res.get_data(as_text=True)
                self.assertIn(f'lang="{lang}"', html, f"{route} missing lang='{lang}'")
                vis = visible_text(html)
                expected = get_val(cur_dict, key)
                opposite = get_val(opp_dict, key)
                self.assertIn(expected, vis, f"{route} ({lang}) missing {key}='{expected}'")
                if expected != opposite:
                    self.assertNotIn(opposite, vis, f"{route} ({lang}) leaked opposite {key}='{opposite}'")

    def test_backend_api_endpoints_follow_active_language(self):
        # 1. /api/map/route respects both query lang and session lang
        res_route_es = self.client.post("/api/map/route", json={
            "origin": "mainParking",
            "destination": "buildingA",
            "lang": "spa",
        })
        self.assertEqual(res_route_es.status_code, 200)
        d_es = res_route_es.get_json()
        self.assertTrue(d_es["success"])
        self.assertIn("Edificio A", d_es["destination"])

        res_route_en = self.client.post("/api/map/route", json={
            "origin": "mainParking",
            "destination": "buildingA",
            "lang": "eng",
        })
        self.assertEqual(res_route_en.status_code, 200)
        d_en = res_route_en.get_json()
        self.assertTrue(d_en["success"])
        self.assertIn("Building A", d_en["destination"])

        # 2. /api/admin/stats unauthorized error respects session language
        self.client.post("/api/i18n/set-language/spa")
        res_adm_es = self.client.get("/api/admin/stats")
        self.assertEqual(res_adm_es.status_code, 403)
        self.assertIn("administrador", res_adm_es.get_json()["error"].lower())

        self.client.post("/api/i18n/set-language/eng")
        res_adm_en = self.client.get("/api/admin/stats")
        self.assertEqual(res_adm_en.status_code, 403)
        self.assertIn("administrator", res_adm_en.get_json()["error"].lower())

        # 3. /api/lost-found-object/items missing route 404 respects session language
        with self.client.session_transaction() as sess:
            sess["user"] = {"Id": 1, "FullName": "Test User", "UserTypeId": 1, "Email": "test@uamv.edu.ni"}
            sess["idioma"] = "spa"
            sess["lang"] = "spa"
        res_nf_es = self.client.get("/api/lost-found-object/items/999999")
        self.assertEqual(res_nf_es.status_code, 404)
        self.assertIn("no encontrado", res_nf_es.get_json()["error"].lower())

        with self.client.session_transaction() as sess:
            sess["idioma"] = "eng"
            sess["lang"] = "eng"
        res_nf_en = self.client.get("/api/lost-found-object/items/999999")
        self.assertEqual(res_nf_en.status_code, 404)
        self.assertIn("not found", res_nf_en.get_json()["error"].lower())

    def test_campus_localization_complete_coverage_and_zero_spanish_leaks(self):
        from backend.data.placesCatalog import PLACES_CATALOG
        from backend.data.campusLocalization import (
            PLACE_TRANSLATIONS,
            SUBGRAPH_TRANSLATIONS,
            INDOOR_NODE_TRANSLATIONS,
        )
        from backend.subgraphs import getAllBuildingSubgraphs

        # 1. 100% dictionary coverage of PLACES_CATALOG, all 18 subgraphs, and all indoor nodes
        missing_places = [p["placeId"] for p in PLACES_CATALOG if p["placeId"] not in PLACE_TRANSLATIONS]
        self.assertEqual(missing_places, [], f"Missing PLACE_TRANSLATIONS entries: {missing_places}")

        subgraphs = getAllBuildingSubgraphs()
        missing_subgraphs = [k for k in subgraphs if k not in SUBGRAPH_TRANSLATIONS]
        self.assertEqual(missing_subgraphs, [], f"Missing SUBGRAPH_TRANSLATIONS entries: {missing_subgraphs}")

        missing_indoor = [
            f"{sg_id}:{node.nodeId}"
            for sg_id, sg in subgraphs.items()
            for node in sg.getAllNodes()
            if node.nodeId not in INDOOR_NODE_TRANSLATIONS
        ]
        self.assertEqual(missing_indoor, [], f"Missing INDOOR_NODE_TRANSLATIONS entries: {missing_indoor}")

        # 2. Verify zero Spanish leaks in English API payloads
        spanish_leak_re = re.compile(
            r"\b(Edificio|Aula|Aulas|Piso|Pisos|Planta|Servicios Sanitarios|Baños|Baño|"
            r"Bebedero|Bebederos|Escaleras|Rampa|Contabilidad|Dirección|Facultad|"
            r"Laboratorio|Clínica|Odontología|Biblioteca|Auditorio|Parqueo|Estacionamiento|"
            r"Área de Mesas|Lab Digital|Módulo|Pasillo|Puerta|Salida|Entrada|Junto a|"
            r"Frente a|Hombres|Mujeres|Mixtos|Discapacitados|Colaboradores|Estudiantes|"
            r"Oficina|Sala de|Salón|Cancha|Gimnasio|Comedor|Cafetería|Farmacia|Rectoría)\b",
            re.IGNORECASE,
        )
        english_leak_re = re.compile(
            r"\b(Building|Classroom|Classrooms|Floor|Restrooms|Restroom|Drinking Fountain|"
            r"Water Fountain|Stairs|Ramp|Accounting|Faculty|Laboratory|Dental Clinic|"
            r"Library|Auditorium|Parking|Outdoor Tables|Hallway|Entrance|Exit|Next to|"
            r"Across from|Ground Floor|Second Floor|Third Floor|First Floor|Men's|Women's)\b",
            re.IGNORECASE,
        )

        # /api/map/places?lang=eng
        places_en = self.client.get("/api/map/places?lang=eng").get_json()["places"]
        places_es = self.client.get("/api/map/places?lang=spa").get_json()["places"]
        self.assertEqual(len(places_en), len(places_es))
        self.assertGreaterEqual(len(places_en), len(PLACES_CATALOG))

        en_leaks = []
        for p in places_en:
            for field in ("name", "locationNotes", "buildingName"):
                val = p.get(field) or ""
                if spanish_leak_re.search(val):
                    en_leaks.append(("places", p["placeId"], field, val))

        # /api/map/nodes?lang=eng
        nodes_en = self.client.get("/api/map/nodes?lang=eng").get_json()["nodes"]
        for n in nodes_en:
            if spanish_leak_re.search(n.get("name") or ""):
                en_leaks.append(("nodes", n["nodeId"], "name", n["name"]))

        # /api/map/subgraphs?lang=eng and /api/map/buildings/<id>/locations?lang=eng
        subgraphs_en = self.client.get("/api/map/subgraphs?lang=eng").get_json()["buildings"]
        for sg_item in subgraphs_en:
            for field in ("name", "description"):
                val = sg_item.get(field) or ""
                if spanish_leak_re.search(val):
                    en_leaks.append(("subgraphs", sg_item["macroNodeId"], field, val))
            locs_res = self.client.get(f"/api/map/buildings/{sg_item['macroNodeId']}/locations?lang=eng").get_json()
            self.assertTrue(locs_res["success"])
            if spanish_leak_re.search(locs_res.get("buildingName") or ""):
                en_leaks.append(("locations", sg_item["macroNodeId"], "buildingName", locs_res["buildingName"]))
            for loc in locs_res.get("locations", []):
                if spanish_leak_re.search(loc.get("name") or ""):
                    en_leaks.append(("locations", loc["nodeId"], "name", loc["name"]))

        self.assertEqual(en_leaks, [], f"Spanish text leaked into English map endpoints: {en_leaks[:10]}")

        # /api/map/places?lang=spa must not leak English in locationNotes or names
        es_leaks = []
        for p in places_es:
            for field in ("name", "locationNotes", "buildingName"):
                val = p.get(field) or ""
                if english_leak_re.search(val):
                    es_leaks.append((p["placeId"], field, val))
        self.assertEqual(es_leaks, [], f"English text leaked into Spanish places payload: {es_leaks[:10]}")

        # 3. Full bilingual searchability in both English and Spanish UI modes
        bilingual_queries = [
            ("eng", "Baños", "restroomsMenB1", "Restrooms"),
            ("eng", "bathroom", "restroomsMenB1", "Restrooms"),
            ("eng", "Aula B-210", "classroomB210", "Classroom B210"),
            ("eng", "Classroom B-210", "classroomB210", "Classroom B210"),
            ("eng", "Contabilidad", "accountingOfficeA", "Accounting"),
            ("eng", "Water Fountain", "drinkingFountainB1", "Fountain"),
            ("spa", "Restrooms", "restroomsMenB1", "Sanitarios"),
            ("spa", "Classroom B-210", "classroomB210", "Aula B210"),
            ("spa", "Accounting", "accountingOfficeA", "Contabilidad"),
            ("spa", "Water Fountain", "drinkingFountainB1", "Bebedero"),
        ]
        for lang, q, expected_id, expected_substr in bilingual_queries:
            res = self.client.get("/api/map/places", query_string={"q": q, "lang": lang})
            self.assertEqual(res.status_code, 200)
            results = res.get_json()["places"]
            matched = next((p for p in results if p["placeId"] == expected_id), None)
            self.assertIsNotNone(
                matched,
                f"Bilingual search failed for lang={lang!r} q={q!r}: expected {expected_id}, got {[p['placeId'] for p in results[:6]]}",
            )
            self.assertIn(expected_substr, matched["name"])

    def test_indoor_and_macro_route_navigation_localized_in_english(self):
        spanish_route_re = re.compile(
            r"\b(Edificio|Aula|Piso|Área de Mesas|Lab Digital FIA|Contabilidad|Escaleras|Rampa|Sanitarios)\b",
            re.IGNORECASE,
        )
        scenarios = [
            {"origin": "mainParking", "destination": "Classroom B101", "expect_dest": "Classroom B101"},
            {"origin": "mainParking", "destination": "Accounting & Finance", "expect_dest": "Accounting"},
            {"origin": "areaDeMesas", "destination": "labDigitalFia", "expect_dest": "FIA Digital"},
        ]
        for sc in scenarios:
            res = self.client.post(
                "/api/map/route",
                json={"origin": sc["origin"], "destination": sc["destination"], "lang": "eng"},
            )
            self.assertEqual(res.status_code, 200)
            payload = res.get_json()
            self.assertTrue(payload["success"], f"Route failed for {sc}: {payload}")
            self.assertIn(sc["expect_dest"], payload["destination"])
            self.assertIsNone(spanish_route_re.search(payload["origin"]), f"Spanish in origin: {payload['origin']}")
            self.assertIsNone(spanish_route_re.search(payload["destination"]), f"Spanish in destination: {payload['destination']}")
            for step in payload.get("steps", []):
                instr = step.get("instruction") or ""
                lm = step.get("landmarkName") or ""
                self.assertIsNone(spanish_route_re.search(instr), f"Spanish in step instruction: {instr}")
                self.assertIsNone(spanish_route_re.search(lm), f"Spanish in step landmark: {lm}")

    def test_navigation_html_fields_wired_for_dynamic_i18n_and_clean_in_english(self):
        self.client.post("/api/i18n/set-language/eng")
        html_en = self.client.get("/").get_data(as_text=True)

        required_i18n_attrs = [
            'data-i18n-placeholder="map.where_am_i_placeholder"',
            'data-i18n-placeholder="map.where_to_go_placeholder"',
            'data-i18n-placeholder="map.directory_search_placeholder"',
            'data-i18n-placeholder="map.gps.filter_locations_placeholder"',
            'data-i18n="map.initial_duration"',
            'data-i18n="map.initial_refs"',
            'data-i18n="map.campus_pill"',
            'data-i18n="map.hud25d.default_headline"',
            'data-i18n="map.hud25d.default_instruction"',
            'data-i18n="map.hud25d.default_next_step"',
            'data-i18n="map.hud25d.dock_prompt"',
            'data-i18n="map.hud25d.mode_live"',
            'data-i18n="map.hud25d.gps_label"',
            'data-i18n="map.hud25d.btn_arrived_next"',
            'data-i18n="map.hud25d.tray_simulate"',
            'data-i18n="map.hud25d.speed_label_map"',
            'data-i18n-title="map.toolbar.zoom_in"',
            'data-i18n-title="map.toolbar.zoom_out"',
            'data-i18n-title="map.toolbar.center_map"',
        ]
        for attr in required_i18n_attrs:
            self.assertIn(attr, html_en, f"Missing reactive i18n attribute on /: {attr}")

        # Verify zero Spanish leaks in visible navigation text and attributes on / in English
        no_script = re.sub(r"<script\b[^>]*>.*?</script>", " ", html_en, flags=re.S | re.I)
        no_style = re.sub(r"<style\b[^>]*>.*?</style>", " ", no_script, flags=re.S | re.I)
        visible = html_lib.unescape(re.sub(r"<[^>]+>", " ", no_style))
        attrs_text = " ".join(
            html_lib.unescape(m.group(1))
            for m in re.finditer(r'(?:placeholder|title|aria-label)="([^"]+)"', no_style)
        )
        spanish_nav_re = re.compile(
            r"\b(Edificio|Aula|Aulas|Piso|Pisos|Dónde|Cómo|Buscar|Ruta|Escaleras|Rampa|"
            r"Baños|Bebederos|Sanitarios|Parqueo|Facultades|Comida|Deportes|Laboratorios|"
            r"Calcular|Intercambiar|Ubicación|Destino|Origen|Accesible|Directorio|"
            r"Indicaciones|Área de Mesas|Lab Digital)\b",
            re.IGNORECASE,
        )
        self.assertIsNone(spanish_nav_re.search(visible), f"Spanish visible text on / in EN: {spanish_nav_re.findall(visible)[:10]}")
        self.assertIsNone(spanish_nav_re.search(attrs_text), f"Spanish attribute text on / in EN: {spanish_nav_re.findall(attrs_text)[:10]}")


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

    def test_js_navigation_fields_and_selected_places_retranslate_dynamically(self):
        node_bin = shutil.which("node")
        if not node_bin:
            self.skipTest("Node.js not available in test environment")

        app = createApp()
        client = app.test_client()
        spa_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        eng_dict = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))
        places_spa = client.get("/api/map/places?lang=spa").get_json()["places"]
        places_eng = client.get("/api/map/places?lang=eng").get_json()["places"]
        nodes_spa = client.get("/api/map/nodes?lang=spa").get_json()["nodes"]
        nodes_eng = client.get("/api/map/nodes?lang=eng").get_json()["nodes"]

        test_script = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const spaDict = JSON.parse(process.env.TEST_SPA_DICT);
const engDict = JSON.parse(process.env.TEST_ENG_DICT);
const placesSpa = JSON.parse(process.env.TEST_PLACES_SPA);
const placesEng = JSON.parse(process.env.TEST_PLACES_ENG);
const nodesSpa = JSON.parse(process.env.TEST_NODES_SPA);
const nodesEng = JSON.parse(process.env.TEST_NODES_ENG);

function createEl(tag, attrs = {}) {
    const classSet = new Set((attrs.class || "").split(/\s+/).filter(Boolean));
    const attrMap = new Map(Object.entries(attrs).filter(([k]) => k !== "class" && k !== "children"));
    const el = {
        tagName: tag.toUpperCase(),
        id: attrs.id || "",
        value: attrs.value || "",
        placeholder: attrs.placeholder || "",
        title: attrs.title || "",
        textContent: attrs.textContent || "",
        children: attrs.children || [],
        classList: {
            add(...cls) { cls.forEach(c => classSet.add(c)); },
            remove(...cls) { cls.forEach(c => classSet.delete(c)); },
            contains(c) { return classSet.has(c); },
        },
        getAttribute(k) { return attrMap.has(k) ? attrMap.get(k) : null; },
        setAttribute(k, v) {
            attrMap.set(k, String(v));
            if (k === "placeholder") el.placeholder = String(v);
            if (k === "title") el.title = String(v);
        },
        removeAttribute(k) { attrMap.delete(k); },
        querySelectorAll(sel) {
            const out = [];
            const walk = (n) => {
                for (const ch of (n.children || [])) {
                    if (matches(ch, sel)) out.push(ch);
                    walk(ch);
                }
            };
            walk(el);
            return out;
        },
        querySelector(sel) { return el.querySelectorAll(sel)[0] || null; },
    };
    return el;
}

function matches(el, selector) {
    return selector.split(",").map(s => s.trim()).some((part) => {
        if (part === "title[data-i18n]") return el.tagName === "TITLE" && el.getAttribute("data-i18n") !== null;
        const m = part.match(/^\[([a-z0-9-]+)\]$/i);
        if (m) return el.getAttribute(m[1]) !== null;
        return false;
    });
}

const originLabel = createEl("label", { "data-i18n": "map.where_am_i", textContent: "¿Dónde te encuentras?" });
const originInput = createEl("input", {
    id: "originInput",
    "data-i18n-placeholder": "map.where_am_i_placeholder",
    placeholder: "Usa GPS o selecciona tu ubicación...",
    value: "Aula B204 (Piso 2)",
});
const destLabel = createEl("label", { "data-i18n": "map.where_to_go", textContent: "¿A dónde quieres ir?" });
const destinationInput = createEl("input", {
    id: "destinationInput",
    "data-i18n-placeholder": "map.where_to_go_placeholder",
    placeholder: "Escribe aula, baño, laboratorio, facultad o servicio...",
    value: "Edificio A (Rectoría y Administración)",
});
const dirSearchInput = createEl("input", {
    id: "directorySearchInput",
    "data-i18n-placeholder": "map.directory_search_placeholder",
    placeholder: "Filtrar edificio, aula, oficina o piso...",
});
const gpsFilterInput = createEl("input", {
    id: "gpsLocationFilterInput",
    "data-i18n-placeholder": "map.gps.filter_locations_placeholder",
    placeholder: "Filtrar aula, baño, oficina...",
});
const btnSwap = createEl("button", {
    id: "btnSwapLocations",
    "data-i18n-title": "map.swap",
    title: "Intercambiar ubicaciones",
});
const btnGps = createEl("button", {
    id: "btnGetGps",
    "data-i18n-title": "map.use_gps",
    title: "Usar mi ubicación actual",
});
const btnZoomIn = createEl("button", {
    id: "btnMapZoomIn",
    "data-i18n-title": "map.toolbar.zoom_in",
    "data-i18n-aria-label": "map.toolbar.zoom_in",
    title: "Acercar",
});
const routeDist = createEl("span", { id: "routeDistanceText", "data-i18n": "map.initial_duration", textContent: "~1 min" });
const routeRefs = createEl("span", { id: "routeMinutesText", "data-i18n": "map.initial_refs", textContent: "0 referencias" });
const campusPill = createEl("span", { id: "wazeActiveRoadPill", "data-i18n": "map.campus_pill", textContent: "Campus UAM" });
const tbtDist = createEl("div", { id: "tbtStepDistance", "data-i18n": "map.hud25d.default_headline", textContent: "Sigue recto" });
const tbtInstr = createEl("div", { id: "tbtStepInstruction", "data-i18n": "map.hud25d.default_instruction", textContent: "Inicia tu recorrido hacia el destino." });
const wazeEta = createEl("div", { id: "wazeEtaTime", "data-i18n": "map.campus_pill", textContent: "Campus UAM" });
const wazeMeta = createEl("div", { id: "wazeTripMeta", "data-i18n": "map.hud25d.dock_prompt", textContent: "¿A dónde vas? • Toca para buscar" });

const root = createEl("div", {
    children: [
        originLabel, originInput, destLabel, destinationInput, dirSearchInput,
        gpsFilterInput, btnSwap, btnGps, btnZoomIn, routeDist, routeRefs,
        campusPill, tbtDist, tbtInstr, wazeEta, wazeMeta,
    ],
});
const head = createEl("head", { children: [] });
const winListeners = new Map();

const document = {
    documentElement: { lang: "spa" },
    head,
    title: "JaguarFind",
    querySelectorAll(sel) { return root.querySelectorAll(sel); },
    querySelector(sel) { return root.querySelector(sel); },
    addEventListener() {},
};

const windowObj = {
    document,
    location: { pathname: "/" },
    APP_CONFIG: { currentLang: "spa" },
    APP_TRANSLATIONS: spaDict,
    fetch: async (url) => {
        if (url.includes("/api/i18n/set-language/eng")) {
            return { ok: true, status: 200, async json() { return { success: true, language: "eng", translations: engDict }; } };
        }
        return { ok: true, status: 200, async json() { return { success: true, language: "spa", translations: spaDict }; } };
    },
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

const i18nSrc = fs.readFileSync(path.join(process.cwd(), "frontend/static/js/i18nManager.js"), "utf8");
const ctx = vm.createContext(windowObj);
vm.runInContext(i18nSrc, ctx);

// Mirror navigateMap.html's reactive selected-input retranslation helpers
const navState = {
    allPlaces: placesSpa,
    allNodes: nodesSpa,
    originPlaceId: "classroomB204",
    originNodeId: "buildingB",
    originQuery: "Aula B-204",
    originFloorLevel: 2,
    originShowFloor: true,
    destinationPlaceId: "buildingA",
    destinationNodeId: "buildingA",
    destinationQuery: "Edificio A (Rectoría y Administración)",
};

function resolveLocalizedSelectionTitle(placeId, nodeId, fallbackTitle) {
    if (placeId) {
        const p = navState.allPlaces.find(x => x && x.placeId === placeId);
        if (p && p.name) return p.name;
    }
    const lookup = placeId || nodeId;
    if (lookup) {
        const n = navState.allNodes.find(x => x && x.nodeId === lookup);
        if (n && n.name) return n.name;
        const trVal = windowObj.t(`nodes.${lookup}`);
        if (trVal && trVal !== `nodes.${lookup}`) return trVal;
    }
    return fallbackTitle || "";
}

function formatOriginDisplayValue(baseName, floorLevel, showFloor) {
    const floorWord = windowObj.t("map.floor");
    if (!baseName) return "";
    if (!showFloor || !floorLevel) return baseName;
    if (new RegExp(`\\b${floorWord}\\s+${floorLevel}\\b`, "i").test(baseName)) return baseName;
    return `${baseName} (${floorWord} ${floorLevel})`;
}

function retranslateSelectedNavInputs() {
    if (navState.originPlaceId || navState.originNodeId) {
        const locOrigin = resolveLocalizedSelectionTitle(navState.originPlaceId, navState.originNodeId, navState.originQuery);
        originInput.value = formatOriginDisplayValue(locOrigin, navState.originFloorLevel, navState.originShowFloor);
        navState.originQuery = locOrigin;
    }
    if (navState.destinationPlaceId || navState.destinationNodeId) {
        const locDest = resolveLocalizedSelectionTitle(navState.destinationPlaceId, navState.destinationNodeId, navState.destinationQuery);
        destinationInput.value = locDest;
        navState.destinationQuery = locDest;
    }
}

windowObj.addEventListener("jaguarLanguageChanged", (e) => {
    const isEng = e.detail.lang === "eng";
    navState.allPlaces = isEng ? placesEng : placesSpa;
    navState.allNodes = isEng ? nodesEng : nodesSpa;
    retranslateSelectedNavInputs();
});

(async () => {
    await windowObj.JaguarI18n.setLanguage("eng");

    // 1. All navigation labels, placeholders, titles, aria-labels, and HUD prompts translated to English
    assert.equal(originLabel.textContent, "Where are you?");
    assert.equal(originInput.placeholder, "Use GPS or pick a location...");
    assert.equal(destLabel.textContent, "Where do you want to go?");
    assert.equal(destinationInput.placeholder, "Type a classroom, restroom, lab, faculty, or service...");
    assert.equal(dirSearchInput.placeholder, "Filter building, room, office, or floor...");
    assert.equal(gpsFilterInput.placeholder, "Filter room, restroom, office...");
    assert.equal(btnSwap.getAttribute("title"), "Swap locations");
    assert.equal(btnGps.getAttribute("title"), "Use my current location");
    assert.equal(btnZoomIn.getAttribute("title"), "Zoom In");
    assert.equal(btnZoomIn.getAttribute("aria-label"), "Zoom In");
    assert.equal(routeDist.textContent, "~1 min");
    assert.equal(routeRefs.textContent, "0 landmarks");
    assert.equal(campusPill.textContent, "UAM Campus");
    assert.equal(tbtDist.textContent, "Continue straight");
    assert.equal(tbtInstr.textContent, "Start your route toward the destination.");
    assert.equal(wazeEta.textContent, "UAM Campus");
    assert.equal(wazeMeta.textContent, "Where to? • Tap to search");

    // 2. Selected origin (with GPS floor suffix) & selected destination dynamically re-translated!
    assert.equal(originInput.value, "Classroom B204 (Floor 2)");
    assert.equal(destinationInput.value, "Building A (Student Services & Lost and Found)");

    // 3. Unbound raw free-text draft input is preserved intact on language switch
    navState.originPlaceId = null;
    navState.originNodeId = null;
    originInput.value = "my custom search text";
    await windowObj.JaguarI18n.setLanguage("spa");
    assert.equal(originInput.value, "my custom search text");
    assert.equal(destinationInput.value, "Edificio A (Atención al Estudiante & Objetos Perdidos)");

    console.log("ALL_JS_NAV_I18N_TESTS_PASSED");
})().catch((err) => {
    console.error(err);
    process.exit(1);
});
"""

        env = os.environ.copy()
        env["TEST_SPA_DICT"] = json.dumps(spa_dict)
        env["TEST_ENG_DICT"] = json.dumps(eng_dict)
        env["TEST_PLACES_SPA"] = json.dumps(places_spa)
        env["TEST_PLACES_ENG"] = json.dumps(places_eng)
        env["TEST_NODES_SPA"] = json.dumps(nodes_spa)
        env["TEST_NODES_ENG"] = json.dumps(nodes_eng)

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
            f"JS nav i18n tests failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        self.assertIn("ALL_JS_NAV_I18N_TESTS_PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
