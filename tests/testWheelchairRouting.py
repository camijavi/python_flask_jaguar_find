import re
import unittest
from pathlib import Path

from backend.graph.directedGraph import DirectedGraph, Node
from backend.graph.dijkstraRouter import DijkstraRouter
from backend.graph.pedestrianWalkwayGraph import (
    INACCESSIBLE_WALKWAY_SEGMENTS,
    RECOMMENDED_WALKWAY_SEGMENTS,
    WALKWAY_SEGMENTS_SPEC,
    buildPedestrianWalkwayGraph,
)


class TestWheelchairRouting(unittest.TestCase):
    def makeNode(self, nodeId):
        return Node(nodeId, nodeId, "waypoint", 0, 0, 0, 0)

    def test_accessible_route_prefers_recommended_edges_but_reports_real_distance(self):
        graph = DirectedGraph()
        for nodeId in ("start", "recommended", "blocked", "destination"):
            graph.addNode(self.makeNode(nodeId))

        graph.addBidirectionalWalkway(
            "start", "destination", 10, accessibilityZone="neutral"
        )
        graph.addBidirectionalWalkway(
            "start", "recommended", 6, accessibilityZone="recommended",
            routingCostFactor=0.8,
        )
        graph.addBidirectionalWalkway(
            "recommended", "destination", 6, accessibilityZone="recommended",
            routingCostFactor=0.8,
        )
        graph.addBidirectionalWalkway(
            "start", "blocked", 0.5, isAccessible=False,
            accessibilityZone="inaccessible",
        )
        graph.addBidirectionalWalkway(
            "blocked", "destination", 0.5, isAccessible=False,
            accessibilityZone="inaccessible",
        )

        path, distance, _, _ = DijkstraRouter(graph).findShortestPathWithEdges(
            "start", "destination", accessibleOnly=True
        )

        self.assertEqual(path, ["start", "recommended", "destination"])
        self.assertEqual(distance, 12)

    def test_accessible_route_does_not_use_inaccessible_only_connection(self):
        graph = DirectedGraph()
        graph.addNode(self.makeNode("start"))
        graph.addNode(self.makeNode("destination"))
        graph.addBidirectionalWalkway(
            "start", "destination", 2, isAccessible=False,
            accessibilityZone="inaccessible",
        )

        path, _, _, _ = DijkstraRouter(graph).findShortestPathWithEdges(
            "start", "destination", accessibleOnly=True
        )

        self.assertEqual(path, [])

    def test_reference_zones_are_applied_to_the_campus_walkway_graph(self):
        graph = buildPedestrianWalkwayGraph()
        edges = [
            edge
            for node in graph.getAllNodes()
            for edge in node.outgoingEdges
        ]

        self.assertTrue(any(edge.accessibilityZone == "recommended" for edge in edges))
        self.assertTrue(any(edge.accessibilityZone == "neutral" for edge in edges))
        self.assertTrue(
            all(
                edge.isAccessible
                for edge in edges
                if edge.accessibilityZone == "recommended"
            )
        )
        self.assertTrue(
            all(
                not edge.isAccessible
                for edge in edges
                if edge.accessibilityZone == "inaccessible"
            )
        )
        walkwaySegments = {
            frozenset((source, target))
            for source, target, _, _ in WALKWAY_SEGMENTS_SPEC
        }
        self.assertTrue(RECOMMENDED_WALKWAY_SEGMENTS <= walkwaySegments)
        self.assertTrue(INACCESSIBLE_WALKWAY_SEGMENTS <= walkwaySegments)

    def test_browser_and_backend_recommended_segments_stay_in_sync(self):
        projectRoot = Path(__file__).resolve().parents[1]
        source = (projectRoot / "frontend/static/js/campusWalkwaysLayer.js").read_text(
            encoding="utf-8"
        )
        block = re.search(
            r"const RECOMMENDED_SEGMENT_KEYS = new Set\(\[(.*?)\]\.map",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(block)
        browserSegments = {
            frozenset(pair)
            for pair in re.findall(r'\["([^"]+)", "([^"]+)"\]', block.group(1))
        }

        self.assertEqual(browserSegments, RECOMMENDED_WALKWAY_SEGMENTS)

        blockedBlock = re.search(
            r"const INACCESSIBLE_SEGMENT_KEYS = new Set\(\[(.*?)\]\.map",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(blockedBlock)
        browserBlockedSegments = {
            frozenset(pair)
            for pair in re.findall(r'\["([^"]+)", "([^"]+)"\]', blockedBlock.group(1))
        }
        self.assertEqual(browserBlockedSegments, INACCESSIBLE_WALKWAY_SEGMENTS)


if __name__ == "__main__":
    unittest.main()
