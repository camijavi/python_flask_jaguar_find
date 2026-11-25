"""
testRoomSearch.py
================================================================================
Comprehensive automated verification suite for Campus Room & Facility Search:
1. Data source completeness cross-checked directly against `buildings.txt`
   (all 95 room codes + key offices/labs/auditoriums/facilities)
2. Canonical catalog unification across backend/data, data/, and backend/graph
3. Exact matches (e.g. "B210") and partial matches (e.g. "B2", "B20", "210",
   "C3", "H1", "H2", "M3", "P3") without dropping valid entries or polluting
   results with unrelated rooms from building range titles
4. Case-insensitivity, leading/trailing/internal whitespace handling,
   hyphen/underscore separator tolerance, and accent/diacritic insensitivity
5. End-to-end routing and building node detail resolution for newly indexed
   rooms (B210, B206-B209, C305, H103-H207, M202-M304, P307-P308)
6. Client-side JavaScript unit tests (via Node.js) against
   `frontend/static/js/campusSearchHelper.js` using the live API payload
================================================================================
"""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from backend.app import createApp
from backend.data import placesCatalog as canonicalCatalog
from backend.graph import placesCatalog as graphCatalog
from data import placesCatalog as rootCatalog
from backend.services.placeSearchService import (
    buildIndexedPlaces,
    canonicalizeSearchText,
    extractRoomCodes,
    searchPlaces,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _extractAllRoomCodesFromBuildingsTxt():
    txt = (PROJECT_ROOT / "buildings.txt").read_text(encoding="utf-8")
    rawCodes = re.findall(r"\b([A-Za-z]\s*-?\s*\d{3})\b", txt)
    unique = []
    seen = set()
    for code in rawCodes:
        norm = re.sub(r"[\s-]+", "", code).upper()
        if norm not in seen:
            seen.add(norm)
            unique.append(norm)
    return unique


class TestRoomSearchBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = createApp()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_single_canonical_places_catalog_across_all_import_paths(self):
        self.assertIs(canonicalCatalog.PLACES_CATALOG, rootCatalog.PLACES_CATALOG)
        self.assertIs(canonicalCatalog.PLACES_CATALOG, graphCatalog.PLACES_CATALOG)

    def test_every_room_code_in_buildings_txt_is_searchable_and_ranked_first(self):
        roomCodes = _extractAllRoomCodesFromBuildingsTxt()
        self.assertGreaterEqual(len(roomCodes), 90)

        missing = []
        wrongRank = []
        polluted = []

        for code in roomCodes:
            res = self.client.get(f"/api/map/places?q={code}&lang=spa")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data["success"])
            places = data["places"]

            if not places:
                missing.append(code)
                continue

            topCodes = extractRoomCodes(places[0]["name"]) | set(places[0].get("roomCodes", []))
            if code.lower() not in topCodes:
                wrongRank.append((code, places[0]["name"]))

            # Ensure no unrelated rooms pollute an exact room-code query
            for p in places:
                pCodes = extractRoomCodes(p["name"]) | set(p.get("roomCodes", []))
                if code.lower() not in pCodes and code.lower() not in canonicalizeSearchText(
                    " ".join([p["name"], p["placeId"], *p.get("keywords", [])])
                ):
                    polluted.append((code, p["name"]))

        self.assertEqual(missing, [], f"Room codes from buildings.txt returned 0 results: {missing}")
        self.assertEqual(wrongRank, [], f"Room codes not ranked #1: {wrongRank}")
        self.assertEqual(polluted, [], f"Unrelated rooms polluted exact room search: {polluted}")

    def test_b210_exact_case_whitespace_and_separator_variants(self):
        variants = [
            "B210",
            "b210",
            "B-210",
            "b-210",
            "B 210",
            "b 210",
            "  B210  ",
            "  b   210  ",
            "\tB-210\n",
            "B_210",
            "Aula B210",
            "aula b-210",
            "AULA B 210",
            "Edificio B 210",
            "classroomB210",
        ]
        for query in variants:
            res = self.client.get("/api/map/places", query_string={"q": query, "lang": "spa"})
            self.assertEqual(res.status_code, 200)
            payload = res.get_json()
            places = payload["places"]
            self.assertGreaterEqual(len(places), 1, f"Query {query!r} returned no results")
            self.assertEqual(
                places[0]["placeId"],
                "classroomB210",
                f"Query {query!r} expected classroomB210 at #1, got {[p['placeId'] for p in places[:5]]}",
            )
            self.assertEqual(places[0]["name"], "Aula B210")
            self.assertEqual(places[0]["parentBuildingId"], "buildingB")
            self.assertEqual(places[0]["floorLevel"], 2)

        # Exact code 'B210' must NOT return unrelated rooms like B101 or stairs
        exactPlaces = self.client.get("/api/map/places?q=B210&lang=spa").get_json()["places"]
        self.assertEqual([p["placeId"] for p in exactPlaces], ["classroomB210"])

    def test_partial_matches_return_every_matching_room_without_dropping_entries(self):
        # "B2" -> ALL 10 Building B Floor 2 classrooms B-201..B-210 in natural order
        resB2 = self.client.get("/api/map/places?q=B2&lang=spa").get_json()["places"]
        idsB2 = [p["placeId"] for p in resB2]
        expectedB2 = [f"classroomB{n}" for n in range(201, 211)]
        self.assertEqual(idsB2[:10], expectedB2)

        # "B20" -> ALL 9 rooms B-201..B-209
        resB20 = self.client.get("/api/map/places?q=B20&lang=spa").get_json()["places"]
        idsB20 = [p["placeId"] for p in resB20]
        self.assertEqual(idsB20[:9], [f"classroomB{n}" for n in range(201, 210)])

        # "B1" -> ALL 9 Building B Floor 1 classrooms B-101..B-109
        resB1 = self.client.get("/api/map/places?q=B1&lang=spa").get_json()["places"]
        idsB1 = [p["placeId"] for p in resB1]
        for n in range(101, 110):
            self.assertIn(f"classroomB{n}", idsB1)

        # "C3" -> ALL 10 Building C Floor 3 rooms (C301-C305, C306, C307-C310)
        resC3 = self.client.get("/api/map/places?q=C3&lang=spa").get_json()["places"]
        codesC3 = set()
        for p in resC3:
            codesC3 |= set(p.get("roomCodes", []))
        for n in range(301, 311):
            self.assertIn(f"c{n}", codesC3)

        # "H1" & "H2" -> ALL Building H labs H101-H107 and H201-H207
        resH1 = self.client.get("/api/map/places?q=H1&lang=spa").get_json()["places"]
        idsH1 = {p["placeId"] for p in resH1}
        for n in range(101, 108):
            self.assertIn(f"medicalLabH{n}", idsH1)

        resH2 = self.client.get("/api/map/places?q=H2&lang=spa").get_json()["places"]
        idsH2 = {p["placeId"] for p in resH2}
        for n in range(201, 208):
            self.assertIn(f"medicalLabH{n}", idsH2)

        # "M3" -> ALL Building M Floor 3 classrooms M301-M304
        resM3 = self.client.get("/api/map/places?q=M3&lang=spa").get_json()["places"]
        idsM3 = [p["placeId"] for p in resM3]
        self.assertEqual(idsM3[:4], ["classroomM301", "classroomM302", "classroomM303", "classroomM304"])

        # "P3" -> ALL Building P Floor 3 rooms P301-P308
        resP3 = self.client.get("/api/map/places?q=P3&lang=spa").get_json()["places"]
        codesP3 = set()
        for p in resP3:
            codesP3 |= set(p.get("roomCodes", []))
        for n in range(301, 309):
            self.assertIn(f"p{n}", codesP3)

        # Numeric partial "210" -> BOTH B-210 and C-210
        res210 = self.client.get("/api/map/places?q=210&lang=spa").get_json()["places"]
        ids210 = {p["placeId"] for p in res210}
        self.assertIn("classroomB210", ids210)
        self.assertIn("classroomC210", ids210)

    def test_accent_insensitivity_and_non_collision_word_boundaries(self):
        # Accent-insensitive queries
        for q, expectedSub in [
            ("computacion", "Computación"),
            ("COMPUTACIÓN", "Computación"),
            ("odontologia", "Odontología"),
            ("ruben dario", "Rubén Darío"),
            ("copernico", "Copérnico"),
            ("musica", "Música"),
            ("banos", "Sanitarios"),
            ("ciclograma", "Ciclograma"),
            ("meteorologia", "Meteorología"),
            ("mediacion", "Mediación"),
            ("comedor de colaboradores", "Colaboradores"),
        ]:
            places = self.client.get("/api/map/places", query_string={"q": q, "lang": "spa"}).get_json()["places"]
            self.assertTrue(
                any(expectedSub.lower() in p["name"].lower() for p in places),
                f"Expected match containing {expectedSub!r} for query {q!r}, got {[p['name'] for p in places[:5]]}",
            )

        # Ensure "A1" does NOT falsely collapse "Planta 1" into "planta1"
        placesA1 = self.client.get("/api/map/places?q=A1&lang=spa").get_json()["places"]
        for p in placesA1:
            self.assertNotEqual(p["parentBuildingId"], "buildingP")

        # Empty / whitespace-only query returns full catalog
        allPlaces = self.client.get("/api/map/places?lang=spa").get_json()["places"]
        wsPlaces = self.client.get("/api/map/places", query_string={"q": "   \t  ", "lang": "spa"}).get_json()["places"]
        self.assertEqual(len(allPlaces), len(wsPlaces))

        # Combined category + floor + query filter
        filteredB2 = self.client.get("/api/map/places?q=B2&floor=2&category=classroom&lang=spa").get_json()["places"]
        self.assertEqual([p["placeId"] for p in filteredB2], [f"classroomB{n}" for n in range(201, 211)])

        filteredB = self.client.get("/api/map/places?q=B&floor=2&category=classroom&lang=spa").get_json()["places"]
        self.assertEqual([p["placeId"] for p in filteredB[:10]], [f"classroomB{n}" for n in range(201, 211)])

    def test_routing_and_building_detail_for_newly_indexed_rooms(self):
        for dest in ["B210", "classroomB210", "  b 210  ", "B206", "C305", "P308", "M304", "H207"]:
            res = self.client.post(
                "/api/map/route",
                json={"origin": "mainParking", "destination": dest, "lang": "spa"},
            )
            self.assertEqual(res.status_code, 200, f"Routing to {dest!r} failed: {res.get_data(as_text=True)}")
            payload = res.get_json()
            self.assertTrue(payload["success"], f"Route unsuccessful for {dest!r}: {payload}")
            self.assertGreaterEqual(len(payload["steps"]), 2)

        # Building B detail endpoint includes all B101-B109 and B201-B210
        detailB = self.client.get("/api/map/nodes/buildingB?lang=spa").get_json()
        self.assertTrue(detailB["success"])
        bPlaceIds = {p["placeId"] for p in detailB["subPlaces"]}
        for n in list(range(101, 110)) + list(range(201, 211)):
            self.assertIn(f"classroomB{n}", bPlaceIds)

    def test_map_html_wires_campus_search_helper_and_directory_cards(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("campusSearchHelper.js", html)
        self.assertIn("JaguarCampusSearch.searchCampus", html)
        self.assertNotIn("results.slice(0, 8)", html)
        for bldg in ("buildingB", "buildingL", "buildingM", "buildingP", "jaguarCenter"):
            self.assertIn(f'data-bldg="{bldg}"', html)


class TestRoomSearchClientJS(unittest.TestCase):
    """Runs deterministic Node.js tests against frontend/static/js/campusSearchHelper.js."""

    def test_frontend_search_helper_with_live_api_dataset(self):
        nodeBin = shutil.which("node")
        if not nodeBin:
            self.skipTest("Node.js not available in test environment")

        app = createApp()
        client = app.test_client()
        places = client.get("/api/map/places?lang=spa").get_json()["places"]
        nodes = client.get("/api/map/nodes?lang=spa").get_json()["nodes"]
        b2Locations = client.get("/api/map/buildings/buildingB/locations?floor=2&lang=spa").get_json()["locations"]

        jsTest = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const places = JSON.parse(process.env.TEST_PLACES);
const nodes = JSON.parse(process.env.TEST_NODES);
const b2Locations = JSON.parse(process.env.TEST_B2_LOCATIONS);

const sandbox = { window: {}, globalThis: {} };
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

const helperSrc = fs.readFileSync(
    path.join(process.cwd(), "frontend/static/js/campusSearchHelper.js"),
    "utf8"
);
vm.runInContext(helperSrc, sandbox);
const S = sandbox.JaguarCampusSearch;
assert.ok(S, "JaguarCampusSearch must be exported globally");

// 1. Exact query "B210" & case/whitespace/hyphen variants
for (const q of ["B210", "b210", "B-210", "B 210", "  b   210  ", "aula b 210", "AULA B-210"]) {
    const matches = S.searchCampus(q, "", places, nodes);
    assert.ok(matches.length >= 1, `Expected match for ${JSON.stringify(q)}`);
    assert.equal(matches[0].id, "classroomB210", `Expected classroomB210 first for ${JSON.stringify(q)}, got ${matches[0].id}`);
    assert.equal(matches[0].title, "Aula B210");
}

// Exact B210 does not return unrelated B101/stairs
const exactB210 = S.searchCampus("B210", "", places, nodes).filter(m => m.type === "place");
assert.deepEqual(Array.from(exactB210, m => m.id), ["classroomB210"]);

// 2. Partial query "B2" returns ALL 10 Floor-2 classrooms (no 8-item truncation!)
const matchesB2 = S.searchCampus("B2", "", places, nodes).filter(m => m.type === "place");
const b2Ids = Array.from(matchesB2, m => m.id);
assert.ok(b2Ids.length >= 10, `Expected >= 10 matches for 'B2', got ${b2Ids.length}`);
for (let n = 201; n <= 210; n++) {
    assert.ok(b2Ids.includes(`classroomB${n}`), `Missing classroomB${n} from 'B2' partial search`);
}
assert.deepEqual(
    Array.from(b2Ids.slice(0, 10)),
    Array.from({ length: 10 }, (_, i) => `classroomB${201 + i}`),
    "B201-B210 must be ranked first in natural numerical order"
);

// 3. Partial query "C3" returns ALL 10 rooms including C305 and C310 (no truncation!)
const matchesC3 = S.searchCampus("C3", "", places, nodes).filter(m => m.type === "place");
assert.ok(matchesC3.length >= 10, `Expected >= 10 matches for 'C3', got ${matchesC3.length}`);
assert.ok(matchesC3.some(m => m.id === "classroomC305"), "Missing classroomC305");
assert.ok(matchesC3.some(m => m.id === "classroomC310"), "Missing classroomC310");

// 4. Numeric partial "210" returns both Aula B-210 and Aula C-210
const matches210 = S.searchCampus("210", "", places, nodes).map(m => m.id);
assert.ok(matches210.includes("classroomB210"));
assert.ok(matches210.includes("classroomC210"));

// 5. Diacritic & case insensitivity
const compMatches = S.searchCampus("computacion", "", places, nodes);
assert.ok(compMatches.some(m => m.id === "computerLabC201"));

// 6. GPS manual floor filter matches individual room node ("Aula B210") on "B210" / "b 210" / "b-210"
for (const q of ["B210", "b210", "B 210", "b-210"]) {
    const filtered = S.filterLocationsList(b2Locations, q);
    assert.ok(
        filtered.some(loc => loc.nodeId === "b_room_210"),
        `GPS floor filter failed for ${JSON.stringify(q)}`
    );
}

// 7. Building Directory card matching expands room ranges & matches indexed building rooms
const cardBText = "B Edificio B • Aulas & Farmacia 2 Pisos Piso 1: Módulo Comercial 1 (Farmacia), Aulas B101 - B109. Piso 2: Aulas B201 - B210.";
for (const q of ["B210", "b-210", "B 207", "b206", "  B  103  "]) {
    assert.equal(
        S.matchesDirectoryCard(cardBText, "buildingB", q, places),
        true,
        `Building B directory card should match ${JSON.stringify(q)}`
    );
}
assert.equal(S.matchesDirectoryCard(cardBText, "buildingB", "C310", places), false);

console.log("JS_ROOM_SEARCH_TESTS_OK");
"""
        proc = subprocess.run(
            [nodeBin, "-e", jsTest],
            cwd=str(PROJECT_ROOT),
            env={
                **dict(subprocess.os.environ),
                "TEST_PLACES": json.dumps(places),
                "TEST_NODES": json.dumps(nodes),
                "TEST_B2_LOCATIONS": json.dumps(b2Locations),
            },
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"Node.js search tests failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        self.assertIn("JS_ROOM_SEARCH_TESTS_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
