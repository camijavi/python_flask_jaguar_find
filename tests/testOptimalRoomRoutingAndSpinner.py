"""
testOptimalRoomRoutingAndSpinner.py
================================================================================
Verifies:
1. Joint indoor+outdoor door-to-door route optimization respecting UAM's
   left-to-right classroom numbering (101/201/301 east/left -> 108/109/208/209
   west/right) so routes like B208->P208, B209->P208, B109->P108, and C209->P208
   use the fast right/west corridor instead of detouring via Building A / left side.
2. Zero indoor-exit <-> outdoor-portal cross-building teleportation.
3. Wheelchair accessibility preservation and upper-floor stairs-only guard.
4. Route calculation spinning wheel UI (button spinner + map overlay) and
   bilingual i18n keys across backend/languages and languages/.
================================================================================
"""

import json
import os
import re
import tempfile
import unittest
from pathlib import Path

from backend.app import createApp
from backend.config import Config
from backend.database import initDb
from backend.graph.geoUtils import CampusGeoUtils
from backend.graph.navigationService import globalNavigationService
from backend.graph.pedestrianWalkwayGraph import globalPedestrianWalkwayGraph
from backend.subgraphs import getBuildingSubgraph


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestOptimalRoomRouting(unittest.TestCase):
    def _assertNoCrossBuildingTeleport(self, route: dict, maxHandoffMeters: float = 25.0):
        walkwayIds = route.get("walkwayNodeIds") or []
        self.assertGreaterEqual(len(walkwayIds), 2)

        originIndoor = route.get("originIndoorPathIds") or []
        if originIndoor:
            sgOrigin = getBuildingSubgraph(route["originNodeId"])
            exitNode = sgOrigin.graph.nodes[originIndoor[-1]]
            startPortal = globalPedestrianWalkwayGraph.nodes[walkwayIds[0]]
            handoff = CampusGeoUtils.calculateHaversineDistance(
                exitNode.latitude, exitNode.longitude, startPortal.latitude, startPortal.longitude
            )
            self.assertLessEqual(
                handoff,
                maxHandoffMeters,
                f"Origin indoor exit {originIndoor[-1]} teleported {handoff:.1f}m to portal {walkwayIds[0]}",
            )

        destIndoor = route.get("destinationIndoorPathIds") or []
        if destIndoor:
            sgDest = getBuildingSubgraph(route["destinationNodeId"])
            entryNode = sgDest.graph.nodes[destIndoor[0]]
            endPortal = globalPedestrianWalkwayGraph.nodes[walkwayIds[-1]]
            handoff = CampusGeoUtils.calculateHaversineDistance(
                entryNode.latitude, entryNode.longitude, endPortal.latitude, endPortal.longitude
            )
            self.assertLessEqual(
                handoff,
                maxHandoffMeters,
                f"Destination portal {walkwayIds[-1]} teleported {handoff:.1f}m to indoor entry {destIndoor[0]}",
            )

    def test_west_side_rooms_B_and_C_to_P_use_west_corridor(self):
        westCases = [
            ("B208", "P208", "b_bridge_top", "p_front_east", "p_stairs_f1_west"),
            ("B209", "P208", "b_bridge_top", "p_front_east", "p_stairs_f1_west"),
            ("B109", "P108", "b_bridge_top", "p_front_east", "p_stairs_f1_west"),
            ("C209", "P208", "c_west_exit", "p_front_east", "p_stairs_f1_west"),
            ("C109", "P108", "c_west_exit", "p_front_east", "p_stairs_f1_west"),
        ]
        forbiddenMetric = re.compile(r"\b\d+\s*(m|mts|metros|meters)\b", re.IGNORECASE)
        forbiddenCardinal = re.compile(
            r"\b(al norte|al sur|al este|al oeste|al noreste|al noroeste|al sureste|al suroeste|"
            r"northeast|northwest|southeast|southwest)\b",
            re.IGNORECASE,
        )

        for orig, dest, expectedStartPortal, expectedEndPortal, expectedDestEntry in westCases:
            for lang in ("eng", "spa"):
                route = globalNavigationService.calculateRoute(orig, dest, accessibleOnly=False, lang=lang)
                self.assertTrue(route["success"], f"Route failed for {orig}->{dest} ({lang}): {route}")
                walkwayIds = route["walkwayNodeIds"]
                self.assertEqual(walkwayIds[0], expectedStartPortal, f"{orig}->{dest} should exit at {expectedStartPortal}")
                self.assertEqual(walkwayIds[-1], expectedEndPortal, f"{orig}->{dest} should enter P at {expectedEndPortal}")
                self.assertNotIn("p_front_west", walkwayIds, f"{orig}->{dest} should not detour to left/east Building P portal")
                self.assertNotIn("a_center", walkwayIds, f"{orig}->{dest} should not detour through Building A")
                self.assertEqual(route["destinationIndoorPathIds"][0], expectedDestEntry)
                self.assertEqual(route["recommendedIndoorEntrance"], "F1-ENT-O")
                self._assertNoCrossBuildingTeleport(route)
                for step in route["stepInstructions"]:
                    self.assertFalse(forbiddenMetric.search(step), f"Metric distance leaked: {step}")
                    self.assertFalse(forbiddenCardinal.search(step), f"Cardinal direction leaked: {step}")
                    self.assertNotIn("passing the ramp", step.lower(), f"Redundant ramp phrasing: {step}")
                    self.assertNotIn("pasando la rampa", step.lower(), f"Redundant ramp phrasing: {step}")

    def test_reverse_west_side_route_P_to_B_avoids_skybridge_misdirection(self):
        for orig, dest in [("P208", "B208"), ("P208", "B209")]:
            for lang in ("eng", "spa"):
                route = globalNavigationService.calculateRoute(orig, dest, accessibleOnly=False, lang=lang)
                self.assertTrue(route["success"], f"Route failed for {orig}->{dest} ({lang}): {route}")
                walkwayIds = route["walkwayNodeIds"]
                self.assertEqual(walkwayIds[0], "p_front_east")
                self.assertEqual(walkwayIds[-1], "b_bridge_top")
                self.assertEqual(route["destinationIndoorPathIds"][0], "b_stairs_f1")
                self._assertNoCrossBuildingTeleport(route)
                for step in route["stepInstructions"]:
                    self.assertNotIn("skybridge", step.lower(), f"Misleading skybridge reference: {step}")
                    self.assertNotIn("puente techado", step.lower(), f"Misleading skybridge reference: {step}")

    def test_west_side_route_is_strictly_shorter_than_east_side_detour(self):
        sgB = getBuildingSubgraph("buildingB")
        sgP = getBuildingSubgraph("buildingP")
        _, outdoorEast, _, _ = globalNavigationService.walkwayRouter.findShortestPathWithEdges(
            "b_east_entry", "p_front_west", accessibleOnly=False
        )

        for bRoom, pRoom in [("B208", "P208"), ("B209", "P208"), ("B109", "P108")]:
            route = globalNavigationService.calculateRoute(bRoom, pRoom, accessibleOnly=False, lang="eng")
            self.assertTrue(route["success"])

            bNodeId = sgB.resolveRoomQuery(bRoom)
            pNodeId = sgP.resolveRoomQuery(pRoom)
            _, indoorBToEast, _, _ = sgB.router.findShortestPathWithEdges(bNodeId, "b_room_101")
            _, indoorPEastToRoom, _, _ = sgP.router.findShortestPathWithEdges("p_stairs_f1_east", pNodeId)
            eastDetourTotal = indoorBToEast + outdoorEast + indoorPEastToRoom

            self.assertLess(
                route["totalDistanceMeters"],
                eastDetourTotal - 40.0,
                f"{bRoom}->{pRoom} ({route['totalDistanceMeters']}m) should beat east detour ({eastDetourTotal:.1f}m)",
            )

    def test_east_side_rooms_B_and_C_to_P_use_east_corridor(self):
        eastCases = [
            ("B101", "P101", "b_east_entry", "p_front_west", "p_stairs_f1_east"),
            ("B201", "P201", "b_east_entry", "p_front_west", "p_stairs_f1_east"),
            ("C101", "P101", "c_east_entry", "p_front_west", "p_stairs_f1_east"),
            ("C201", "P201", "c_east_entry", "p_front_west", "p_stairs_f1_east"),
        ]
        for orig, dest, expectedStartPortal, expectedEndPortal, expectedDestEntry in eastCases:
            route = globalNavigationService.calculateRoute(orig, dest, accessibleOnly=False, lang="eng")
            self.assertTrue(route["success"], f"Route failed for {orig}->{dest}: {route}")
            walkwayIds = route["walkwayNodeIds"]
            self.assertEqual(walkwayIds[0], expectedStartPortal)
            self.assertEqual(walkwayIds[-1], expectedEndPortal)
            self.assertEqual(route["destinationIndoorPathIds"][0], expectedDestEntry)
            self.assertEqual(route["recommendedIndoorEntrance"], "F1-ENT-W")
            self._assertNoCrossBuildingTeleport(route)

    def test_cross_side_routes_pick_aligned_optimal_portals(self):
        # B209 (west/right F2) -> P201 (east/left F2): walking B F1 to b_east_entry -> p_front_west is shorter
        b209ToP201 = globalNavigationService.calculateRoute("B209", "P201", accessibleOnly=False, lang="eng")
        self.assertTrue(b209ToP201["success"])
        self.assertEqual(b209ToP201["walkwayNodeIds"][0], "b_east_entry")
        self.assertEqual(b209ToP201["walkwayNodeIds"][-1], "p_front_west")
        self._assertNoCrossBuildingTeleport(b209ToP201)

        # B201 (east/left F2, descends at west stairs) -> P208 (west/right F2): exit b_bridge_top -> p_front_east
        b201ToP208 = globalNavigationService.calculateRoute("B201", "P208", accessibleOnly=False, lang="eng")
        self.assertTrue(b201ToP208["success"])
        self.assertEqual(b201ToP208["walkwayNodeIds"][0], "b_bridge_top")
        self.assertEqual(b201ToP208["walkwayNodeIds"][-1], "p_front_east")
        self._assertNoCrossBuildingTeleport(b201ToP208)

    def test_accessible_room_routing_and_upper_floor_guard(self):
        # Floor 1 west-to-west wheelchair accessible route succeeds without stairs
        accFloor1 = globalNavigationService.calculateRoute("B109", "P108", accessibleOnly=True, lang="eng")
        self.assertTrue(accFloor1["success"], f"Expected accessible Floor 1 route: {accFloor1}")
        self.assertEqual(accFloor1["walkwayNodeIds"][0], "b_bridge_top")
        self.assertEqual(accFloor1["walkwayNodeIds"][-1], "p_front_east")
        self.assertEqual(accFloor1["recommendedIndoorEntrance"], "F1-ENT-E")
        self._assertNoCrossBuildingTeleport(accFloor1)

        # Floor 2 destination with stairs-only access cleanly reports accessibility limitation
        accFloor2 = globalNavigationService.calculateRoute("B109", "P208", accessibleOnly=True, lang="eng")
        self.assertFalse(accFloor2["success"])
        self.assertIn("Floor 2", accFloor2["error"])


class TestRouteApiAndSpinnerUi(unittest.TestCase):
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

    def test_api_map_route_returns_optimal_west_side_route(self):
        res = self.client.post(
            "/api/map/route",
            json={
                "origin": "Classroom B208",
                "destination": "Classroom P208",
                "accessibleOnly": False,
                "lang": "eng",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["walkwayNodeIds"][0], "b_bridge_top")
        self.assertEqual(data["walkwayNodeIds"][-1], "p_front_east")
        self.assertEqual(data["destinationIndoorPathIds"][0], "p_stairs_f1_west")

    def test_calculating_route_i18n_synced_across_all_dictionaries(self):
        engBackend = json.loads((PROJECT_ROOT / "backend" / "languages" / "eng.json").read_text(encoding="utf-8"))
        spaBackend = json.loads((PROJECT_ROOT / "backend" / "languages" / "spa.json").read_text(encoding="utf-8"))
        engRoot = json.loads((PROJECT_ROOT / "languages" / "eng.json").read_text(encoding="utf-8"))
        spaRoot = json.loads((PROJECT_ROOT / "languages" / "spa.json").read_text(encoding="utf-8"))

        self.assertEqual(engBackend, engRoot)
        self.assertEqual(spaBackend, spaRoot)
        self.assertEqual(engBackend["map"]["calculating_route"], "Calculating route...")
        self.assertEqual(spaBackend["map"]["calculating_route"], "Calculando ruta...")

    def test_map_pages_render_route_calculation_spinner_elements(self):
        for routePath in ("/", "/map", "/mapa"):
            res = self.client.get(routePath)
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('id="btnCalculateRouteSpinner"', html)
            self.assertIn('id="btnCalculateRouteIcon"', html)
            self.assertIn('id="btnCalculateRouteLabel"', html)
            self.assertIn('id="routeCalculatingOverlay"', html)
            self.assertIn('id="routeCalculatingOverlayText"', html)
            self.assertIn("map.calculating_route", html)
            self.assertIn("setRouteCalculatingUi", html)
            self.assertIn("animate-spin", html)


if __name__ == "__main__":
    unittest.main()
