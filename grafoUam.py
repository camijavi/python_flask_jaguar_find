"""
grafoUam.py
================================================================================
TDA GRAFO PONDERADO, DIRIGIDO Y NO COMPLETO DEL CAMPUS UAM
Implementación en Python puro con Algoritmo de Dijkstra, Cola de Prioridad (heapq),
Filtro de Accesibilidad ♿, Fórmula de Haversine y Resolución Inteligente de Destinos.
Nomenclatura interna en inglés y camelCase.
================================================================================
"""

import heapq
import math
from typing import Dict, List, Tuple, Optional, Any
from data.campusCategories import CampusCategory, CATEGORY_METADATA
from data.placesCatalog import PLACES_CATALOG

# ==============================================================================
# 1. CORE DATA STRUCTURES: DIRECTED EDGE & NODE
# ==============================================================================

class DirectedEdge:
    """
    Represents a directed pedestrian path segment (u -> v) with a positive metric weight (meters).
    """
    def __init__(
        self,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = ""
    ):
        self.targetNodeId = targetNodeId
        self.distanceMeters = distanceMeters
        self.isAccessible = isAccessible
        self.stepInstruction = stepInstruction

    def toDict(self) -> dict:
        return {
            "targetNodeId": self.targetNodeId,
            "distanceMeters": self.distanceMeters,
            "isAccessible": self.isAccessible,
            "stepInstruction": self.stepInstruction
        }


class Node:
    """
    Represents a physical building entrance, pedestrian gate, or junction on the UAM campus.
    """
    def __init__(
        self,
        nodeId: str,
        name: str,
        category: str,
        xPercent: float,
        yPercent: float,
        latitude: float,
        longitude: float,
        floorLevel: int = 1,
        accessLevel: str = "public",        # "public", "restricted", "facultyOnly"
        accessNotice: Optional[str] = None, # Notice displayed upon arrival (e.g. biosecurity)
        isOutdoorAccessPoint: bool = True
    ):
        self.nodeId = nodeId
        self.name = name
        self.category = category
        self.xPercent = xPercent
        self.yPercent = yPercent
        self.latitude = latitude
        self.longitude = longitude
        self.floorLevel = floorLevel
        self.accessLevel = accessLevel
        self.accessNotice = accessNotice
        self.isOutdoorAccessPoint = isOutdoorAccessPoint
        self.outgoingEdges: List[DirectedEdge] = []

    def addOutgoingEdge(self, edge: DirectedEdge) -> None:
        self.outgoingEdges.append(edge)

    def toDict(self) -> dict:
        return {
            "nodeId": self.nodeId,
            "name": self.name,
            "category": self.category,
            "xPercent": self.xPercent,
            "yPercent": self.yPercent,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "floorLevel": self.floorLevel,
            "accessLevel": self.accessLevel,
            "accessNotice": self.accessNotice,
            "isOutdoorAccessPoint": self.isOutdoorAccessPoint
        }


# ==============================================================================
# 2. DIRECTED GRAPH CONTAINER (ADJACENCY LIST)
# ==============================================================================

class DirectedGraph:
    """
    Weighted, Directed, Non-Complete Graph G = (V, E, W) representing the UAM Campus.
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def addNode(self, node: Node) -> None:
        if node.nodeId not in self.nodes:
            self.nodes[node.nodeId] = node

    def addDirectedEdge(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = ""
    ) -> None:
        """Adds a single directed edge from source to target (u -> v)."""
        if sourceNodeId in self.nodes and targetNodeId in self.nodes:
            edge = DirectedEdge(targetNodeId, distanceMeters, isAccessible, stepInstruction)
            self.nodes[sourceNodeId].addOutgoingEdge(edge)

    def addBidirectionalWalkway(
        self,
        nodeAId: str,
        nodeBId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        forwardInstruction: str = "",
        backwardInstruction: str = ""
    ) -> None:
        """
        Creates two opposite directed edges (u -> v) and (v -> u)
        to model a bidirectional pedestrian sidewalk with equal physical weight.
        """
        self.addDirectedEdge(nodeAId, nodeBId, distanceMeters, isAccessible, forwardInstruction)
        self.addDirectedEdge(nodeBId, nodeAId, distanceMeters, isAccessible, backwardInstruction)

    def getNode(self, nodeId: str) -> Optional[Node]:
        return self.nodes.get(nodeId)

    def getAllNodes(self) -> List[Node]:
        return list(self.nodes.values())


# ==============================================================================
# 3. DIJKSTRA ROUTER WITH MIN-HEAP & STEP-BY-STEP GENERATION
# ==============================================================================

class DijkstraRouter:
    def __init__(self, graph: DirectedGraph, averageWalkingSpeedMpm: float = 72.0):
        self.graph = graph
        self.walkingSpeed = averageWalkingSpeedMpm # 1.2 m/s = 72 meters per minute

    def findShortestPath(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        accessibleOnly: bool = False
    ) -> Tuple[List[str], float, int, List[str]]:
        """
        Calculates optimal route using Dijkstra's Algorithm with a binary min-heap (heapq).
        Complexity: O((V + E) log V).
        Returns: (pathNodeIds, totalDistanceMeters, estimatedMinutes, stepDirections)
        """
        if sourceNodeId not in self.graph.nodes or targetNodeId not in self.graph.nodes:
            return [], float("inf"), 0, []

        shortestDistances: Dict[str, float] = {nodeId: float("inf") for nodeId in self.graph.nodes}
        previousNodes: Dict[str, Optional[str]] = {nodeId: None for nodeId in self.graph.nodes}
        edgeInstructions: Dict[Tuple[str, str], str] = {}

        shortestDistances[sourceNodeId] = 0.0
        priorityQueue = [(0.0, sourceNodeId)]

        while priorityQueue:
            currentDistance, currentNodeId = heapq.heappop(priorityQueue)

            if currentDistance > shortestDistances[currentNodeId]:
                continue

            if currentNodeId == targetNodeId:
                break

            currentNode = self.graph.nodes[currentNodeId]
            for edge in currentNode.outgoingEdges:
                if accessibleOnly and not edge.isAccessible:
                    continue

                newDistance = currentDistance + edge.distanceMeters
                targetId = edge.targetNodeId

                if newDistance < shortestDistances[targetId]:
                    shortestDistances[targetId] = newDistance
                    previousNodes[targetId] = currentNodeId
                    edgeInstructions[(currentNodeId, targetId)] = edge.stepInstruction
                    heapq.heappush(priorityQueue, (newDistance, targetId))

        # Reconstruct path from target to source
        path: List[str] = []
        currId = targetNodeId
        while currId is not None:
            path.insert(0, currId)
            currId = previousNodes[currId]

        if not path or path[0] != sourceNodeId:
            return [], float("inf"), 0, []

        totalDistance = shortestDistances[targetNodeId]
        estimatedMinutes = math.ceil(totalDistance / self.walkingSpeed)
        stepDirections = self._buildStepDirections(path, edgeInstructions)

        return path, round(totalDistance, 1), estimatedMinutes, stepDirections

    def _buildStepDirections(self, path: List[str], edgeInstructions: Dict[Tuple[str, str], str]) -> List[str]:
        if len(path) < 2:
            return ["Ya estás en tu destino."]

        directions: List[str] = []
        startNodeName = self.graph.nodes[path[0]].name
        directions.append(f"Inicia tu recorrido en {startNodeName}.")

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            instruction = edgeInstructions.get((u, v))
            if instruction:
                directions.append(instruction)
            else:
                targetName = self.graph.nodes[v].name
                directions.append(f"Camina hacia {targetName}.")

        destNode = self.graph.nodes[path[-1]]
        directions.append(f"Has llegado a tu destino: {destNode.name}.")
        if destNode.accessNotice:
            directions.append(f"Aviso de acceso: {destNode.accessNotice}")

        return directions


# ==============================================================================
# 4. GEOLOCATION UTILITIES (HAVERSINE & SMART SEARCH RESOLUTION)
# ==============================================================================

class CampusGeoUtils:
    EARTH_RADIUS_METERS = 6371000

    @staticmethod
    def calculateHaversineDistance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return CampusGeoUtils.EARTH_RADIUS_METERS * c

    @staticmethod
    def findNearestNodeByGps(graph: DirectedGraph, userLat: float, userLng: float) -> Tuple[Optional[str], float]:
        nearestNodeId = None
        minDistance = float("inf")

        for nodeId, node in graph.nodes.items():
            if not node.isOutdoorAccessPoint:
                continue
            distance = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
            if distance < minDistance:
                minDistance = distance
                nearestNodeId = nodeId

        return nearestNodeId, round(minDistance, 1)


# ==============================================================================
# 5. UAM CAMPUS GRAPH FACTORY & TOPOLOGY BUILDER
# ==============================================================================

def buildUamCampusGraph() -> DirectedGraph:
    """
    Constructs the official weighted, directed, and non-complete graph of UAM campus.
    Coordinates correspond to official campus map and entrance waypoints.
    """
    g = DirectedGraph()

    # 1. Main Buildings, Gates & Public Nodes (Macro Graph)
    g.addNode(Node("mainParking", "Parqueo Principal & Caseta Sur", CampusCategory.PARKING_LOT, 35.0, 85.0, 12.12350, -86.27080))
    g.addNode(Node("buildingK", "Edificio K (Cafetería Central & Terrazas)", CampusCategory.FOOD_AREA, 29.0, 66.0, 12.12415, -86.27125))
    g.addNode(Node("chilamatesPlaza", "Plaza Chilamates (Kioskos & Fast Point)", CampusCategory.FOOD_AREA, 24.0, 48.0, 12.12510, -86.27180))
    g.addNode(Node("buildingA", "Edificio A (Atención al Estudiante & Objetos Perdidos)", CampusCategory.ADMINISTRATIVE, 28.0, 58.0, 12.12450, -86.27120))
    g.addNode(Node("buildingB", "Edificio B (Aulas B101-B106 & Farmacia)", CampusCategory.CLASSROOM, 34.0, 58.0, 12.12465, -86.27095))
    g.addNode(Node("buildingC", "Edificio C (Laboratorios de Cómputo & Caja UAM)", CampusCategory.CLASSROOM, 34.0, 53.0, 12.12495, -86.27090))
    g.addNode(Node("buildingD", "Edificio D (Odontología Digital CAM-CAM)", CampusCategory.DENTAL_LAB, 31.0, 44.0, 12.12530, -86.27105))
    g.addNode(Node("buildingJ", "Edificio J (Laboratorios de Odontología)", CampusCategory.DENTAL_LAB, 29.0, 44.0, 12.12535, -86.27125, accessLevel="restricted"))
    g.addNode(Node("buildingN", "Edificio N (Clínicas Odontológicas - Recepción)", CampusCategory.DENTAL_LAB, 33.0, 40.0, 12.12560, -86.27100, accessLevel="restricted",
                   accessNotice="Recepción de Clínicas. El ingreso a áreas clínicas y quirófanos requiere uniforme estéril y autorización docente."))
    g.addNode(Node("buildingO", "Edificio O (Facultad de Ingeniería y Arquitectura - FIA)", CampusCategory.FACULTY, 43.0, 32.0, 12.12600, -86.27040))
    g.addNode(Node("buildingP", "Edificio P (Aulas & Observatorio Copérnico)", CampusCategory.CLASSROOM, 33.0, 27.0, 12.12640, -86.27110))
    g.addNode(Node("buildingM", "Edificio M (Aulas & Posgrados)", CampusCategory.CLASSROOM, 45.0, 55.0, 12.12485, -86.27020))
    g.addNode(Node("buildingG", "Edificio G (Facultad de Derecho & Auditorio Central)", CampusCategory.FACULTY, 44.0, 62.0, 12.12470, -86.27010))
    g.addNode(Node("buildingF", "Edificio F (Facultad de Ciencias Administrativas)", CampusCategory.FACULTY, 44.0, 68.0, 12.12445, -86.27015))
    g.addNode(Node("buildingE", "Edificio E (Facultad de Medicina & Clínicas Médicas)", CampusCategory.FACULTY, 41.0, 72.0, 12.12430, -86.27030))
    g.addNode(Node("buildingI", "Edificio I (Rectoría & Biblioteca Central)", CampusCategory.ADMINISTRATIVE, 55.0, 76.0, 12.12390, -86.26930))
    g.addNode(Node("buildingH", "Edificio H (Laboratorios de Medicina)", CampusCategory.MEDICAL_LAB, 46.0, 50.0, 12.12505, -86.27005, accessLevel="restricted"))
    g.addNode(Node("sportsZone", "Campos Deportivos (Estadio de Béisbol & Cancha Fútbol)", CampusCategory.SPORTS, 64.0, 45.0, 12.12550, -86.26870))
    g.addNode(Node("jaguarCenter", "Complejo Jaguar Center (Gimnasio & Polideportivo)", CampusCategory.SPORTS, 64.0, 72.0, 12.12425, -86.26880))
    g.addNode(Node("buildingL", "Edificio L (Cultura & Música)", CampusCategory.CLASSROOM, 69.0, 72.0, 12.12420, -86.26830))
    g.addNode(Node("northeastGate", "Caseta Noreste (Acceso Deportivo)", CampusCategory.PARKING_LOT, 62.0, 38.0, 12.12600, -86.26840))
    g.addNode(Node("northGate", "Caseta Norte (Acceso Copérnico / FIA)", CampusCategory.PARKING_LOT, 36.0, 22.0, 12.12670, -86.27070))

    # 2. Walkways / Edges with Physical Distance in Meters and Accessibility (♿)
    # Walkways are bidirectional, modeled as symmetric pairs of directed edges (u -> v) and (v -> u)
    g.addBidirectionalWalkway("mainParking", "buildingK", 65.0, isAccessible=True,
                             forwardInstruction="Camina 65m al norte hacia la Cafetería Central (Edificio K).",
                             backwardInstruction="Camina 65m al sur hacia el Parqueo Principal.")

    g.addBidirectionalWalkway("buildingK", "buildingA", 45.0, isAccessible=True,
                             forwardInstruction="Avanza 45m al noreste hacia el Edificio A (Atención al Estudiante).",
                             backwardInstruction="Avanza 45m al suroeste hacia el Edificio K.")

    g.addBidirectionalWalkway("buildingK", "chilamatesPlaza", 50.0, isAccessible=True,
                             forwardInstruction="Camina 50m al noroeste hacia Plaza Chilamates.",
                             backwardInstruction="Camina 50m al sureste hacia el Edificio K.")

    g.addBidirectionalWalkway("buildingA", "buildingB", 35.0, isAccessible=True,
                             forwardInstruction="Cruza el pasillo central 35m al este hacia el Edificio B.",
                             backwardInstruction="Cruza 35m al oeste hacia el Edificio A.")

    g.addBidirectionalWalkway("buildingB", "buildingC", 30.0, isAccessible=True,
                             forwardInstruction="Avanza 30m al norte hacia el Edificio C (Caja / Cómputo).",
                             backwardInstruction="Camina 30m al sur hacia el Edificio B.")

    g.addBidirectionalWalkway("buildingC", "buildingD", 40.0, isAccessible=True,
                             forwardInstruction="Camina 40m al norte hacia el Edificio D.",
                             backwardInstruction="Camina 40m al sur hacia el Edificio C.")

    g.addBidirectionalWalkway("buildingD", "buildingJ", 20.0, isAccessible=True,
                             forwardInstruction="Camina 20m al oeste hacia el Edificio J.",
                             backwardInstruction="Camina 20m al este hacia el Edificio D.")

    g.addBidirectionalWalkway("buildingD", "buildingN", 35.0, isAccessible=True,
                             forwardInstruction="Camina 35m al norte hacia las Clínicas Odontológicas (Edificio N).",
                             backwardInstruction="Camina 35m al sur hacia el Edificio D.")

    # Note: Path from Building N to P has stairs; marked isAccessible = False
    g.addBidirectionalWalkway("buildingN", "buildingP", 60.0, isAccessible=False,
                             forwardInstruction="Sube las gradas y avanza 60m al norte hacia el Edificio P (Copérnico).",
                             backwardInstruction="Baja las gradas 60m al sur hacia el Edificio N.")

    g.addBidirectionalWalkway("buildingP", "buildingO", 45.0, isAccessible=True,
                             forwardInstruction="Camina 45m al este hacia el Edificio O (Ingeniería y Arquitectura).",
                             backwardInstruction="Camina 45m al oeste hacia el Edificio P.")

    g.addBidirectionalWalkway("buildingO", "buildingN", 55.0, isAccessible=True,
                             forwardInstruction="Desciende por la rampa 55m al suroeste hacia el Edificio N.",
                             backwardInstruction="Sube por la rampa 55m al noreste hacia el Edificio O.")

    g.addBidirectionalWalkway("buildingP", "northGate", 40.0, isAccessible=True,
                             forwardInstruction="Camina 40m al norte hacia el Portón Copérnico (Caseta Norte).",
                             backwardInstruction="Ingresa por el Portón Norte 40m al sur hacia el Edificio P.")

    g.addBidirectionalWalkway("buildingB", "buildingM", 40.0, isAccessible=True,
                             forwardInstruction="Avanza 40m al este hacia el Edificio M.",
                             backwardInstruction="Avanza 40m al oeste hacia el Edificio B.")

    g.addBidirectionalWalkway("buildingM", "buildingG", 35.0, isAccessible=True,
                             forwardInstruction="Camina 35m al sur hacia el Edificio G (Auditorio Central / Derecho).",
                             backwardInstruction="Camina 35m al norte hacia el Edificio M.")

    g.addBidirectionalWalkway("buildingG", "buildingF", 30.0, isAccessible=True,
                             forwardInstruction="Avanza 30m al sur hacia el Edificio F (Administración).",
                             backwardInstruction="Camina 30m al norte hacia el Edificio G.")

    g.addBidirectionalWalkway("buildingF", "buildingE", 25.0, isAccessible=True,
                             forwardInstruction="Camina 25m al sur hacia el Edificio E (Medicina).",
                             backwardInstruction="Camina 25m al norte hacia el Edificio F.")

    g.addBidirectionalWalkway("buildingE", "buildingI", 60.0, isAccessible=True,
                             forwardInstruction="Avanza 60m al sureste hacia Rectoría y Biblioteca Central (Edificio I).",
                             backwardInstruction="Camina 60m al noroeste hacia el Edificio E.")

    g.addBidirectionalWalkway("buildingI", "jaguarCenter", 70.0, isAccessible=True,
                             forwardInstruction="Cruza el andén 70m al este hacia el Complejo Jaguar Center.",
                             backwardInstruction="Camina 70m al oeste hacia la Biblioteca Central (Edificio I).")

    g.addBidirectionalWalkway("jaguarCenter", "buildingL", 30.0, isAccessible=True,
                             forwardInstruction="Camina 30m al este hacia el Edificio L (Cultura y Música).",
                             backwardInstruction="Camina 30m al oeste hacia Jaguar Center.")

    g.addBidirectionalWalkway("jaguarCenter", "sportsZone", 80.0, isAccessible=True,
                             forwardInstruction="Avanza 80m al norte hacia los Campos Deportivos.",
                             backwardInstruction="Camina 80m al sur hacia Jaguar Center.")

    g.addBidirectionalWalkway("sportsZone", "northeastGate", 45.0, isAccessible=True,
                             forwardInstruction="Camina 45m al este hacia la Caseta Noreste de Deportes.",
                             backwardInstruction="Ingresa por la Caseta Noreste 45m al oeste hacia los campos deportivos.")

    g.addBidirectionalWalkway("buildingC", "buildingH", 40.0, isAccessible=True,
                             forwardInstruction="Camina 40m al este hacia los Laboratorios de Medicina (Edificio H).",
                             backwardInstruction="Camina 40m al oeste hacia el Edificio C.")

    g.addBidirectionalWalkway("buildingM", "buildingH", 35.0, isAccessible=True,
                             forwardInstruction="Camina 35m al noreste hacia el Edificio H.",
                             backwardInstruction="Camina 35m al suroeste hacia el Edificio M.")

    return g


# ==============================================================================
# 6. HIGH-LEVEL NAVIGATION & QUERY RESOLUTION SERVICE
# ==============================================================================

class NavigationService:
    def __init__(self):
        self.graph = buildUamCampusGraph()
        self.router = DijkstraRouter(self.graph)

    def resolveQueryToDestination(self, queryText: str) -> Optional[dict]:
        """
        Resolves free-form text or placeId to a destination payload containing:
        - targetNodeId (Macro node for Dijkstra)
        - placeDetails (Sub-room info, floor, notes, category)
        """
        if not queryText:
            return None

        cleaned = queryText.strip().lower()

        # 1. Direct match with a macro nodeId (e.g. "buildingA", "mainParking")
        if cleaned in self.graph.nodes:
            node = self.graph.nodes[cleaned]
            return {
                "targetNodeId": node.nodeId,
                "displayName": node.name,
                "category": node.category,
                "floorLevel": node.floorLevel,
                "locationNotes": "Edificio principal.",
                "isSubPlace": False
            }

        # 2. Check placesCatalog for exact placeId or keywords
        for place in PLACES_CATALOG:
            if place["placeId"].lower() == cleaned or place["name"].lower() == cleaned:
                return {
                    "targetNodeId": place["parentBuildingId"],
                    "displayName": place["name"],
                    "category": place["category"],
                    "floorLevel": place["floorLevel"],
                    "locationNotes": place["locationNotes"],
                    "isSubPlace": True
                }
            for kw in place["keywords"]:
                if kw in cleaned:
                    return {
                        "targetNodeId": place["parentBuildingId"],
                        "displayName": place["name"],
                        "category": place["category"],
                        "floorLevel": place["floorLevel"],
                        "locationNotes": place["locationNotes"],
                        "isSubPlace": True
                    }

        # 3. Fallback to building search by letter (e.g. "edificio b", "building b")
        for nodeId, node in self.graph.nodes.items():
            if nodeId.lower() in cleaned or node.name.lower() in cleaned:
                return {
                    "targetNodeId": nodeId,
                    "displayName": node.name,
                    "category": node.category,
                    "floorLevel": node.floorLevel,
                    "locationNotes": "Edificio principal.",
                    "isSubPlace": False
                }

        return None

    def calculateRoute(
        self,
        originQuery: str,
        destinationQuery: str,
        accessibleOnly: bool = False
    ) -> dict:
        """
        Calculates pedestrian route from origin to destination.
        Handles both macro-buildings and internal sub-rooms seamlessly.
        """
        originDest = self.resolveQueryToDestination(originQuery)
        targetDest = self.resolveQueryToDestination(destinationQuery)

        if not originDest:
            return {"success": False, "error": f"Origen no encontrado: '{originQuery}'"}
        if not targetDest:
            return {"success": False, "error": f"Destino no encontrado: '{destinationQuery}'"}

        sourceNodeId = originDest["targetNodeId"]
        targetNodeId = targetDest["targetNodeId"]

        # Run Dijkstra
        pathNodes, distanceMeters, estimatedMinutes, instructions = self.router.findShortestPath(
            sourceNodeId, targetNodeId, accessibleOnly
        )

        if not pathNodes:
            return {
                "success": False,
                "error": "No existe una ruta peatonal transitable entre ambos puntos con las restricciones solicitadas."
            }

        # If destination is an internal sub-room (e.g. B-103 or water fountain), append final micro-instruction
        if targetDest["isSubPlace"]:
            instructions.append(
                f"Ubicación en el edificio: {targetDest['displayName']} (Piso {targetDest['floorLevel']}) - {targetDest['locationNotes']}"
            )

        # Collect SVG coordinates for polyline drawing
        pathCoordinates = [
            {
                "nodeId": nId,
                "name": self.graph.nodes[nId].name,
                "xPercent": self.graph.nodes[nId].xPercent,
                "yPercent": self.graph.nodes[nId].yPercent,
                "lat": self.graph.nodes[nId].latitude,
                "lng": self.graph.nodes[nId].longitude
            }
            for nId in pathNodes
        ]

        return {
            "success": True,
            "origin": originDest["displayName"],
            "destination": targetDest["displayName"],
            "category": targetDest["category"],
            "floorLevel": targetDest["floorLevel"],
            "pathNodeIds": pathNodes,
            "pathCoordinates": pathCoordinates,
            "totalDistanceMeters": distanceMeters,
            "estimatedWalkingMinutes": estimatedMinutes,
            "stepInstructions": instructions,
            "isAccessibleRoute": accessibleOnly
        }

    def getPlacesByCategory(self, category: str) -> List[dict]:
        """Returns all points of interest belonging to a category."""
        return [p for p in PLACES_CATALOG if p["category"] == category]

    def findNearestGpsNode(self, userLat: float, userLng: float) -> dict:
        """Finds nearest macro node to given GPS coordinates."""
        nearestId, distMeters = CampusGeoUtils.findNearestNodeByGps(self.graph, userLat, userLng)
        node = self.graph.getNode(nearestId) if nearestId else None
        return {
            "nearestNodeId": nearestId,
            "nodeName": node.name if node else None,
            "distanceMeters": distMeters
        }


# Singleton instance for quick import
globalNavigationService = NavigationService()
