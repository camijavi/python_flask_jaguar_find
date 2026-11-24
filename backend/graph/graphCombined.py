"""
graphCombined.py
================================================================================
CENTRAL DATA STRUCTURE: WEIGHTED, DIRECTED, NON-COMPLETE GRAPH G = (V, E, W)
================================================================================
Core graph template recommended for the JaguarFind & JaguarMaps UAM project.
Every graph in the application (Macro Campus Graph, Pedestrian Walkway Graph,
and all 18 Indoor Building Subgraphs) inherits directly from Vertex and Graph
defined in this module.

Formal Graph Properties:
  - Directed (E subset of V x V): Every edge has an explicit origin -> destination.
    Bidirectional paths are modeled as two opposite directed edges (u -> v, v -> u).
  - Weighted (W: E -> R+): Every directed edge stores a strictly positive weight.
  - Non-Complete (|E| << |V|(|V| - 1)): Sparse adjacency list per vertex (neigh),
    without self-loops or duplicate parallel edges.
================================================================================
"""

from __future__ import annotations

from typing import Optional, Union


class Vertex:
    """
    Base vertex in a weighted, directed, non-complete graph.
    Stores its unique identifier and its weighted outgoing adjacency list `neigh`.
    """

    def __init__(self, vertexId: str):
        self.nodeId: str = str(vertexId)
        self.neigh: list[tuple[Vertex, float]] = []

    @property
    def city(self) -> str:
        """Alias preserved for compatibility with the base reference template."""
        return self.nodeId

    @city.setter
    def city(self, value: str) -> None:
        self.nodeId = str(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.nodeId!r})"


class Graph:
    """
    Central weighted, directed, non-complete graph G = (V, E, W).
    Maintains an ordered list of vertices (`self.vertices`) and an internal
    case-insensitive index for O(1) lookup via `search()`.
    """

    def __init__(self):
        self.vertices: list[Vertex] = []
        self._vertexIndex: dict[str, Vertex] = {}

    def search(self, target: Union[str, Vertex]) -> Optional[Vertex]:
        """Finds a vertex by ID (case-insensitive) or Vertex instance."""
        if isinstance(target, Vertex):
            key = target.nodeId.lower()
        else:
            key = str(target).lower()

        cached = self._vertexIndex.get(key)
        if cached is not None:
            return cached

        # Safe fallback in case `self.vertices` was mutated directly
        for vertex in self.vertices:
            if vertex.nodeId.lower() == key:
                self._vertexIndex[key] = vertex
                return vertex
        return None

    def addVertex(self, vertexOrId: Union[str, Vertex]) -> Vertex:
        """
        Adds a vertex (string ID or Vertex/subclass instance) if not already
        present, and returns the registered Vertex instance.
        """
        existing = self.search(vertexOrId)
        if existing is not None:
            return existing

        vertex = vertexOrId if isinstance(vertexOrId, Vertex) else Vertex(str(vertexOrId))
        self.vertices.append(vertex)
        self._vertexIndex[vertex.nodeId.lower()] = vertex
        return vertex

    def insertVertex(self, vertexOrId: Union[str, Vertex]) -> bool:
        """Inserts a new vertex; returns False if it already exists."""
        if self.search(vertexOrId) is not None:
            return False
        self.addVertex(vertexOrId)
        return True

    def addEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
        weight: float,
    ) -> bool:
        """
        Adds a directed weighted edge (origin -> destination, weight > 0).
        Rejects missing vertices, self-loops, non-positive weights, and duplicates.
        """
        v_origin = self.search(origin)
        v_destination = self.search(destination)
        if v_origin is None or v_destination is None:
            return False

        # Simple weighted directed graph invariants: no self-loops, w > 0, no duplicates
        if v_origin is v_destination:
            return False

        numericWeight = float(weight)
        if numericWeight <= 0:
            return False

        if any(neighbor is v_destination for neighbor, _ in v_origin.neigh):
            return False

        v_origin.neigh.append((v_destination, numericWeight))
        return True

    def link(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
        weight: float,
    ) -> bool:
        """Alias for addEdge()."""
        return self.addEdge(origin, destination, weight)

    def addBidirectionalEdge(
        self,
        vertexA: Union[str, Vertex],
        vertexB: Union[str, Vertex],
        weight: float,
    ) -> bool:
        """Adds symmetric directed edges (A -> B) and (B -> A) with the same weight."""
        fwd = self.addEdge(vertexA, vertexB, weight)
        bwd = self.addEdge(vertexB, vertexA, weight)
        return fwd and bwd

    def deleteEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
    ) -> bool:
        """Deletes the directed edge (origin -> destination) if it exists."""
        v_origin = self.search(origin)
        v_destination = self.search(destination)
        if v_origin is None or v_destination is None:
            return False

        for index, (neighbor, _) in enumerate(v_origin.neigh):
            if neighbor is v_destination:
                del v_origin.neigh[index]
                return True
        return False

    def hasEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
    ) -> bool:
        """Returns True if a directed edge (origin -> destination) exists."""
        return self.getEdgeWeight(origin, destination) is not None

    def getEdgeWeight(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
    ) -> Optional[float]:
        """Returns the positive weight of (origin -> destination), or None."""
        v_origin = self.search(origin)
        v_destination = self.search(destination)
        if v_origin is None or v_destination is None:
            return None
        for neighbor, weight in v_origin.neigh:
            if neighbor is v_destination:
                return weight
        return None

    def getNeighbors(
        self,
        origin: Union[str, Vertex],
    ) -> list[tuple[Vertex, float]]:
        """Returns the outgoing weighted adjacency list for a vertex."""
        v_origin = self.search(origin)
        return list(v_origin.neigh) if v_origin is not None else []

    def vertexCount(self) -> int:
        return len(self.vertices)

    def edgeCount(self) -> int:
        return sum(len(vertex.neigh) for vertex in self.vertices)

    def density(self) -> float:
        """Returns directed graph density |E| / (|V| * (|V| - 1))."""
        v = self.vertexCount()
        if v <= 1:
            return 0.0
        return self.edgeCount() / (v * (v - 1))

    def isComplete(self) -> bool:
        """Returns True only if every ordered pair (u, v), u != v, has an edge."""
        v = self.vertexCount()
        if v <= 1:
            return False
        return self.edgeCount() >= v * (v - 1)

    def getGraphSummary(self) -> dict:
        """Returns formal graph-theory metrics proving directed, weighted, non-complete status."""
        v = self.vertexCount()
        e = self.edgeCount()
        maxEdges = v * (v - 1) if v > 1 else 0
        return {
            "vertexCount": v,
            "directedEdgeCount": e,
            "maxPossibleDirectedEdges": maxEdges,
            "density": round(self.density(), 5),
            "isDirected": True,
            "isWeighted": True,
            "isComplete": self.isComplete(),
        }

    def display(self) -> None:
        if not self.vertices:
            print("El grafo está vacío.")
            return

        print("--- Estructura del Grafo ---")
        for vertex in self.vertices:
            connections = [
                f"{neighbor.nodeId} (peso: {weight})"
                for neighbor, weight in vertex.neigh
            ]
            print(f"{vertex.nodeId:<16} -> {connections}")
        print("----------------------------")

    def printMatrix(self) -> None:
        print("\t" + "\t".join(vertex.nodeId for vertex in self.vertices))
        for origin in self.vertices:
            weights = {
                neighbor: weight for neighbor, weight in origin.neigh
            }
            row = [
                str(weights[dest]) if dest in weights else "-"
                for dest in self.vertices
            ]
            print(f"{origin.nodeId}\t" + "\t".join(row))


if __name__ == "__main__":
    # Standalone demonstration of the base directed, non-complete, weighted graph
    graph = Graph()
    sampleLocations = [
        "mainParking", "buildingK", "buildingA", "buildingB",
        "buildingC", "buildingD", "buildingN", "buildingO", "buildingP",
    ]

    for loc in sampleLocations:
        graph.insertVertex(loc)

    graph.link("mainParking", "buildingK", 65.0)
    graph.link("buildingK", "buildingA", 45.0)
    graph.addEdge("buildingA", "buildingB", 35.0)
    graph.addEdge("buildingA", "buildingC", 30.0)
    graph.addEdge("buildingC", "buildingD", 40.0)
    graph.addEdge("buildingD", "buildingN", 35.0)
    graph.addEdge("buildingN", "buildingO", 55.0)
    graph.addEdge("buildingO", "buildingP", 45.0)

    graph.display()
    graph.printMatrix()
    print("Resumen formal:", graph.getGraphSummary())
