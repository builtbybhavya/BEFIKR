"""Offline road network graph and spatial indexing for RAAHI.

Zero network dependency. Converts and represents road topology G = (V, E)
with nodes, edges, spatial snapping, and OSM extraction.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from .geo import distance_km


@dataclass
class Node:
    id: str
    lat: float
    lon: float
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    start: str
    end: str
    length_km: float
    road_type: str = "residential"
    name: str = ""
    one_way: bool = False
    speed_kmh: float = 4.5  # Typical walking speed
    geometry: list[list[float]] = field(default_factory=list)  # [[lon, lat], ...] GeoJSON order
    tags: dict[str, str] = field(default_factory=dict)

    @property
    def travel_minutes(self) -> float:
        speed = self.speed_kmh if self.speed_kmh > 0 else 4.5
        return (self.length_km / speed) * 60.0


class SpatialGridIndex:
    """Fast, local, zero-dependency 2D spatial grid index for coordinate snapping."""

    def __init__(self, cell_size_deg: float = 0.01):
        self.cell_size = cell_size_deg
        self.grid: dict[tuple[int, int], list[Node]] = {}
        self.nodes: dict[str, Node] = {}

    def _cell(self, lat: float, lon: float) -> tuple[int, int]:
        return int(math.floor(lat / self.cell_size)), int(math.floor(lon / self.cell_size))

    def insert(self, node: Node) -> None:
        self.nodes[node.id] = node
        cell = self._cell(node.lat, node.lon)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(node)

    def nearest_node(self, lat: float, lon: float, max_distance_km: float = 5.0) -> tuple[Node | None, float]:
        """Find the nearest traversable node within max_distance_km."""
        cell_x, cell_y = self._cell(lat, lon)
        search_radius = max(1, int(math.ceil(max_distance_km / (self.cell_size * 111.0))))
        
        best_node: Node | None = None
        best_dist = math.inf

        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                candidates = self.grid.get((cell_x + dx, cell_y + dy), [])
                for node in candidates:
                    d = distance_km(lat, lon, node.lat, node.lon)
                    if d < best_dist:
                        best_dist = d
                        best_node = node

        if best_dist <= max_distance_km:
            return best_node, round(best_dist, 4)
        return None, math.inf


class OfflineRoutingGraph:
    """Traversable road network graph G = (V, E) operating 100% offline."""

    def __init__(self, name: str = "offline_graph"):
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.adjacency: dict[str, list[Edge]] = {}
        self.reverse_adjacency: dict[str, list[Edge]] = {}
        self.spatial_index = SpatialGridIndex()

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node
        if node.id not in self.adjacency:
            self.adjacency[node.id] = []
        if node.id not in self.reverse_adjacency:
            self.reverse_adjacency[node.id] = []
        self.spatial_index.insert(node)

    def add_edge(self, edge: Edge, bidirectional: bool = False) -> None:
        if edge.start not in self.nodes or edge.end not in self.nodes:
            raise ValueError(f"Cannot add edge {edge.id}: start ({edge.start}) or end ({edge.end}) node missing.")

        self.edges[edge.id] = edge
        self.adjacency[edge.start].append(edge)
        self.reverse_adjacency[edge.end].append(edge)

        if bidirectional and not edge.one_way:
            rev_id = f"{edge.id}_rev"
            rev_geom = list(reversed(edge.geometry)) if edge.geometry else []
            rev_edge = Edge(
                id=rev_id,
                start=edge.end,
                end=edge.start,
                length_km=edge.length_km,
                road_type=edge.road_type,
                name=edge.name,
                one_way=False,
                speed_kmh=edge.speed_kmh,
                geometry=rev_geom,
                tags=edge.tags.copy()
            )
            self.edges[rev_id] = rev_edge
            self.adjacency[edge.end].append(rev_edge)
            self.reverse_adjacency[edge.start].append(rev_edge)

    def get_outgoing(self, node_id: str) -> list[Edge]:
        return self.adjacency.get(node_id, [])

    def snap(self, lat: float, lon: float, max_distance_km: float = 3.0) -> tuple[Node | None, float]:
        """Snap a coordinate pair to the nearest traversable graph node."""
        return self.spatial_index.nearest_node(lat, lon, max_distance_km=max_distance_km)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "nodes": [asdict(n) for n in self.nodes.values()],
            "edges": [asdict(e) for e in self.edges.values()]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OfflineRoutingGraph:
        graph = cls(name=data.get("name", "offline_graph"))
        for nd in data.get("nodes", []):
            graph.add_node(Node(**nd))
        for ed in data.get("edges", []):
            graph.add_edge(Edge(**ed), bidirectional=False)
        return graph

    def save_json(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, separators=(",", ":"))

    @classmethod
    def load_json(cls, path: str) -> OfflineRoutingGraph:
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


def build_delhi_synthetic_topology() -> OfflineRoutingGraph:
    """Build a traversable connected graph for Mode A (Synthetic Demonstration).

    Converts the 100 synthetic segments (RSEG0001 - RSEG0100) into an interconnected
    grid corridor network around Rohini demo coordinates with cross-connecting edges,
    allowing Dijkstra, A*, Yen's, and risk-weighted pathfinding across multiple viable routes.
    """
    fixtures_dir = os.getenv("BEFIKR_FIXTURES_DIR", os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "fixtures"
    ))
    csv_path = os.path.join(fixtures_dir, "raahi_synthetic", "road_network.csv")

    graph = OfflineRoutingGraph(name="delhi_synthetic_demo_graph")
    import csv

    if not os.path.exists(csv_path):
        return graph

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Add all base nodes and segments
    for row in rows:
        fn = row["from_node"]
        tn = row["to_node"]
        s_lat, s_lon = float(row["start_lat"]), float(row["start_lon"])
        e_lat, e_lon = float(row["end_lat"]), float(row["end_lon"])

        if fn not in graph.nodes:
            graph.add_node(Node(id=fn, lat=s_lat, lon=s_lon, tags={"area": row.get("area", "")}))
        if tn not in graph.nodes:
            graph.add_node(Node(id=tn, lat=e_lat, lon=e_lon, tags={"area": row.get("area", "")}))

        length = float(row.get("length_km", 0.5))
        if length <= 0:
            length = max(0.05, distance_km(s_lat, s_lon, e_lat, e_lon))

        seg_id = row["segment_id"]
        geom = [[s_lon, s_lat], [e_lon, e_lat]]

        edge = Edge(
            id=seg_id,
            start=fn,
            end=tn,
            length_km=round(length, 3),
            road_type=row.get("road_type", "secondary"),
            name=row.get("road_name", seg_id),
            one_way=False,
            geometry=geom,
            tags={"segment_id": seg_id, "area": row.get("area", "")}
        )
        graph.add_edge(edge, bidirectional=True)

    # Cross-connect neighboring demo nodes to create realistic alternative corridors
    # Connect every node with nearby nodes in Euclidean distance to form a traversable mesh
    node_list = list(graph.nodes.values())
    for i, n1 in enumerate(node_list):
        for j in range(i + 1, min(i + 12, len(node_list))):
            n2 = node_list[j]
            d = distance_km(n1.lat, n1.lon, n2.lat, n2.lon)
            if 0.05 <= d <= 1.5:
                # Add cross street connector
                conn_id = f"CONN_{n1.id}_{n2.id}"
                if conn_id not in graph.edges:
                    graph.add_edge(Edge(
                        id=conn_id,
                        start=n1.id,
                        end=n2.id,
                        length_km=round(d, 3),
                        road_type="residential",
                        name=f"Connector {n1.id}-{n2.id}",
                        one_way=False,
                        geometry=[[n1.lon, n1.lat], [n2.lon, n2.lat]],
                        tags={"synthetic_connector": "true"}
                    ), bidirectional=True)

    return graph


def build_delhi_real_osm_corridors() -> OfflineRoutingGraph:
    """Build a genuine, geometrically valid offline road graph for Mode B.

    Covers central Delhi pedestrian and arterial corridors (Connaught Place,
    Barakhamba, Janpath, Kasturba Gandhi Marg, Sansad Marg, Rajiv Chowk,
    Mandi House, India Gate, etc.) with verified coordinates and intersections.
    Strictly unassessed / GREY by default.
    """
    graph = OfflineRoutingGraph(name="delhi_central_osm_corridors")

    # Real Central Delhi Landmark Intersections
    real_nodes = [
        # Connaught Place Inner Circle & Radials
        Node("CP_BLOCK_A", 28.6329, 77.2195, {"name": "Connaught Place Inner Circle A"}),
        Node("CP_BLOCK_B", 28.6335, 77.2210, {"name": "Connaught Place Inner Circle B"}),
        Node("CP_BLOCK_C", 28.6325, 77.2225, {"name": "Connaught Place Inner Circle C"}),
        Node("CP_BLOCK_D", 28.6310, 77.2220, {"name": "Connaught Place Inner Circle D"}),
        Node("CP_BLOCK_E", 28.6300, 77.2205, {"name": "Connaught Place Inner Circle E"}),
        Node("CP_BLOCK_F", 28.6312, 77.2180, {"name": "Connaught Place Inner Circle F"}),
        Node("CP_RAJIV_CHOWK", 28.6328, 77.2197, {"name": "Rajiv Chowk Central Park"}),

        # Connaught Place Outer Circle
        Node("CP_OUTER_CONNAUGHT_CIRCUS_N", 28.6350, 77.2190, {"name": "Connaught Circus North"}),
        Node("CP_OUTER_CONNAUGHT_CIRCUS_E", 28.6330, 77.2245, {"name": "Connaught Circus East / Barakhamba Rd"}),
        Node("CP_OUTER_CONNAUGHT_CIRCUS_S", 28.6290, 77.2200, {"name": "Connaught Circus South / Janpath"}),
        Node("CP_OUTER_CONNAUGHT_CIRCUS_W", 28.6315, 77.2155, {"name": "Connaught Circus West"}),

        # Radial Avenues to South & East
        Node("JANPATH_TOLSTOY", 28.6255, 77.2185, {"name": "Janpath & Tolstoy Marg"}),
        Node("JANPATH_WINDSOR", 28.6210, 77.2175, {"name": "Windsor Place Roundabout"}),
        Node("KG_MARG_TOLSTOY", 28.6265, 77.2230, {"name": "Kasturba Gandhi Marg & Tolstoy Marg"}),
        Node("KG_MARG_FEROZSHAH", 28.6215, 77.2240, {"name": "KG Marg & Ferozeshah Rd Roundabout"}),
        Node("BARAKHAMBA_TOLSTOY", 28.6280, 77.2260, {"name": "Barakhamba Rd & Tolstoy Marg"}),
        Node("MANDI_HOUSE", 28.6258, 77.2345, {"name": "Mandi House Roundabout"}),
        Node("FEROZSHAH_MANDI", 28.6225, 77.2300, {"name": "Ferozeshah Rd & Copernicus Marg"}),

        # India Gate Hexagon
        Node("INDIA_GATE_C_HEXAGON_N", 28.6160, 77.2290, {"name": "India Gate C-Hexagon North / Kasturba Gandhi Exit"}),
        Node("INDIA_GATE_C_HEXAGON_NW", 28.6150, 77.2260, {"name": "India Gate C-Hexagon Ashoka Rd"}),
        Node("INDIA_GATE_CENTRAL", 28.6129, 77.2295, {"name": "India Gate War Memorial"}),
        Node("INDIA_GATE_C_HEXAGON_E", 28.6120, 77.2335, {"name": "India Gate C-Hexagon Purana Qila Rd"}),
        Node("INDIA_GATE_C_HEXAGON_S", 28.6095, 77.2300, {"name": "India Gate C-Hexagon Shershah Rd"}),
        Node("INDIA_GATE_C_HEXAGON_W", 28.6125, 77.2250, {"name": "India Gate C-Hexagon Kartavya Path West"}),
        Node("KARTAVYA_PATH_MAN_SINGH", 28.6128, 77.2200, {"name": "Kartavya Path & Man Singh Road Crossing"}),
        Node("KARTAVYA_PATH_JANPATH", 28.6130, 77.2170, {"name": "Kartavya Path & Janpath Crossing"}),
        Node("NATIONAL_MUSEUM", 28.6115, 77.2190, {"name": "National Museum Gate"}),

        # Central to North Delhi (Kashmere Gate) Arterial
        Node("NEW_DELHI_RLY", 28.6430, 77.2200, {"name": "New Delhi Railway Station / Ajmeri Gate"}),
        Node("CHAWRI_BAZAR", 28.6500, 77.2270, {"name": "Chawri Bazar / Hauz Qazi"}),
        Node("CHANDNI_CHOWK", 28.6570, 77.2300, {"name": "Chandni Chowk / Red Fort Rd"}),
        Node("ISBT_KASHMERE_GATE", 28.6680, 77.2290, {"name": "ISBT Kashmere Gate / Ring Road"}),

        # North-West Arterial Corridor (Ring Road / GT Karnal / Outer Ring Road to Rohini)
        Node("CIVIL_LINES", 28.6780, 77.2220, {"name": "Civil Lines / Rajpur Road"}),
        Node("MALL_ROAD", 28.6900, 77.2130, {"name": "Mall Road Crossing / Vishwavidyalaya"}),
        Node("MODEL_TOWN", 28.7020, 77.1930, {"name": "Model Town / Ring Road Junction"}),
        Node("AZADPUR_CHOWK", 28.7070, 77.1780, {"name": "Azadpur Chowk / GT Karnal Road"}),
        Node("SHALIMAR_BAGH", 28.7120, 77.1560, {"name": "Shalimar Bagh / Outer Ring Road"}),
        Node("PITAMPURA_METRO", 28.7030, 77.1350, {"name": "Pitampura Metro / Madhuban Road"}),
        Node("MADHUBAN_CHOWK", 28.7070, 77.1255, {"name": "Madhuban Chowk / Outer Ring Road"}),
        Node("ROHINI_SEC_3", 28.7020, 77.1180, {"name": "Rohini Sector 3 / Naharpur"}),
        Node("ROHINI_SEC_7", 28.7110, 77.1210, {"name": "Rohini Sector 7 / Sai Baba Chowk"}),
        Node("ROHINI_EAST", 28.7130, 77.1190, {"name": "Rohini East Metro Station"}),
        Node("ROHINI_WEST", 28.7170, 77.1130, {"name": "Rohini West Metro Station"}),
        Node("ROHINI_SEC_11", 28.7250, 77.1150, {"name": "Rohini Sector 11 Main Market"}),
        Node("ROHINI_SEC_16", 28.7280, 77.0900, {"name": "Rohini Sector 16 Crossing"}),
        Node("ROHINI_SEC_17", 28.7300, 77.0780, {"name": "Rohini Sector 17 Market"}),
        Node("ROHINI_SEC_22", 28.7280, 77.0540, {"name": "Rohini Sector 22 Residential"}),
        Node("ROHINI_SEC_23", 28.7325, 77.0572, {"name": "Rohini Sector 23 Hub"}),
        Node("ROHINI_SEC_24", 28.7350, 77.0520, {"name": "Rohini Sector 24 Hub"}),
    ]

    for n in real_nodes:
        graph.add_node(n)

    def add_corridor(e_id: str, u: str, v: str, rtype: str, name: str, oneway: bool = False):
        n1 = graph.nodes[u]
        n2 = graph.nodes[v]
        d = round(distance_km(n1.lat, n1.lon, n2.lat, n2.lon), 3)
        edge = Edge(
            id=e_id,
            start=u,
            end=v,
            length_km=d,
            road_type=rtype,
            name=name,
            one_way=oneway,
            geometry=[[n1.lon, n1.lat], [n2.lon, n2.lat]],
            tags={"osm_highway": rtype, "mode": "real_unassessed"}
        )
        graph.add_edge(edge, bidirectional=not oneway)

    # Connect CP Inner Ring
    add_corridor("CP_IN_AB", "CP_BLOCK_A", "CP_BLOCK_B", "pedestrian", "CP Inner Circle A-B")
    add_corridor("CP_IN_BC", "CP_BLOCK_B", "CP_BLOCK_C", "pedestrian", "CP Inner Circle B-C")
    add_corridor("CP_IN_CD", "CP_BLOCK_C", "CP_BLOCK_D", "pedestrian", "CP Inner Circle C-D")
    add_corridor("CP_IN_DE", "CP_BLOCK_D", "CP_BLOCK_E", "pedestrian", "CP Inner Circle D-E")
    add_corridor("CP_IN_EF", "CP_BLOCK_E", "CP_BLOCK_F", "pedestrian", "CP Inner Circle E-F")
    add_corridor("CP_IN_FA", "CP_BLOCK_F", "CP_BLOCK_A", "pedestrian", "CP Inner Circle F-A")

    # Connect Rajiv Chowk Park Walkways
    add_corridor("CP_RC_A", "CP_RAJIV_CHOWK", "CP_BLOCK_A", "footway", "Central Park Path North")
    add_corridor("CP_RC_C", "CP_RAJIV_CHOWK", "CP_BLOCK_C", "footway", "Central Park Path East")
    add_corridor("CP_RC_E", "CP_RAJIV_CHOWK", "CP_BLOCK_E", "footway", "Central Park Path South")
    add_corridor("CP_RC_F", "CP_RAJIV_CHOWK", "CP_BLOCK_F", "footway", "Central Park Path West")

    # Radials to Outer Circus
    add_corridor("CP_RAD_N", "CP_BLOCK_A", "CP_OUTER_CONNAUGHT_CIRCUS_N", "secondary", "radial to North Circus")
    add_corridor("CP_RAD_E", "CP_BLOCK_C", "CP_OUTER_CONNAUGHT_CIRCUS_E", "secondary", "radial to Barakhamba Circus")
    add_corridor("CP_RAD_S", "CP_BLOCK_E", "CP_OUTER_CONNAUGHT_CIRCUS_S", "secondary", "radial to Janpath Circus")
    add_corridor("CP_RAD_W", "CP_BLOCK_F", "CP_OUTER_CONNAUGHT_CIRCUS_W", "secondary", "radial to West Circus")

    # Connect Outer Circus
    add_corridor("CP_OUT_NE", "CP_OUTER_CONNAUGHT_CIRCUS_N", "CP_OUTER_CONNAUGHT_CIRCUS_E", "primary", "Connaught Circus Eastbound")
    add_corridor("CP_OUT_ES", "CP_OUTER_CONNAUGHT_CIRCUS_E", "CP_OUTER_CONNAUGHT_CIRCUS_S", "primary", "Connaught Circus Southbound")
    add_corridor("CP_OUT_SW", "CP_OUTER_CONNAUGHT_CIRCUS_S", "CP_OUTER_CONNAUGHT_CIRCUS_W", "primary", "Connaught Circus Westbound")
    add_corridor("CP_OUT_WN", "CP_OUTER_CONNAUGHT_CIRCUS_W", "CP_OUTER_CONNAUGHT_CIRCUS_N", "primary", "Connaught Circus Northbound")

    # North-South Corridors to India Gate
    # Route Option 1: Via Janpath
    add_corridor("JANPATH_1", "CP_OUTER_CONNAUGHT_CIRCUS_S", "JANPATH_TOLSTOY", "primary", "Janpath North")
    add_corridor("JANPATH_2", "JANPATH_TOLSTOY", "JANPATH_WINDSOR", "primary", "Janpath Central")
    add_corridor("JANPATH_3", "JANPATH_WINDSOR", "KARTAVYA_PATH_JANPATH", "primary", "Janpath South")

    # Route Option 2: Via Kasturba Gandhi Marg
    add_corridor("KG_1", "CP_OUTER_CONNAUGHT_CIRCUS_E", "KG_MARG_TOLSTOY", "primary", "KG Marg North")
    add_corridor("KG_2", "KG_MARG_TOLSTOY", "KG_MARG_FEROZSHAH", "primary", "KG Marg Central")
    add_corridor("KG_3", "KG_MARG_FEROZSHAH", "INDIA_GATE_C_HEXAGON_N", "primary", "KG Marg South to C-Hexagon")

    # Route Option 3: Via Barakhamba Rd & Mandi House & Copernicus Marg
    add_corridor("BK_1", "CP_OUTER_CONNAUGHT_CIRCUS_E", "BARAKHAMBA_TOLSTOY", "primary", "Barakhamba Road North")
    add_corridor("BK_2", "BARAKHAMBA_TOLSTOY", "MANDI_HOUSE", "primary", "Barakhamba Road South")
    add_corridor("COP_1", "MANDI_HOUSE", "FEROZSHAH_MANDI", "secondary", "Copernicus Marg")
    add_corridor("COP_2", "FEROZSHAH_MANDI", "INDIA_GATE_C_HEXAGON_N", "secondary", "Copernicus Marg to C-Hexagon")

    # Cross Streets (Tolstoy Marg and Ferozeshah Road)
    add_corridor("TOLSTOY_1", "JANPATH_TOLSTOY", "KG_MARG_TOLSTOY", "secondary", "Tolstoy Marg West-Center")
    add_corridor("TOLSTOY_2", "KG_MARG_TOLSTOY", "BARAKHAMBA_TOLSTOY", "secondary", "Tolstoy Marg Center-East")
    add_corridor("FEROZ_1", "JANPATH_WINDSOR", "KG_MARG_FEROZSHAH", "secondary", "Ferozeshah Road West")
    add_corridor("FEROZ_2", "KG_MARG_FEROZSHAH", "FEROZSHAH_MANDI", "secondary", "Ferozeshah Road East")

    # India Gate Perimeter & Kartavya Path Walkways
    add_corridor("IG_HEX_N_NW", "INDIA_GATE_C_HEXAGON_N", "INDIA_GATE_C_HEXAGON_NW", "primary", "C-Hexagon NW")
    add_corridor("IG_HEX_NW_W", "INDIA_GATE_C_HEXAGON_NW", "INDIA_GATE_C_HEXAGON_W", "primary", "C-Hexagon W")
    add_corridor("IG_HEX_W_S", "INDIA_GATE_C_HEXAGON_W", "INDIA_GATE_C_HEXAGON_S", "primary", "C-Hexagon SW")
    add_corridor("IG_HEX_S_E", "INDIA_GATE_C_HEXAGON_S", "INDIA_GATE_C_HEXAGON_E", "primary", "C-Hexagon SE")
    add_corridor("IG_HEX_E_N", "INDIA_GATE_C_HEXAGON_E", "INDIA_GATE_C_HEXAGON_N", "primary", "C-Hexagon NE")

    add_corridor("IG_PLAZA_W", "INDIA_GATE_C_HEXAGON_W", "INDIA_GATE_CENTRAL", "pedestrian", "War Memorial West Approach")
    add_corridor("IG_PLAZA_N", "INDIA_GATE_C_HEXAGON_N", "INDIA_GATE_CENTRAL", "pedestrian", "War Memorial North Approach")
    add_corridor("IG_PLAZA_E", "INDIA_GATE_C_HEXAGON_E", "INDIA_GATE_CENTRAL", "pedestrian", "War Memorial East Approach")
    add_corridor("IG_PLAZA_S", "INDIA_GATE_C_HEXAGON_S", "INDIA_GATE_CENTRAL", "pedestrian", "War Memorial South Approach")

    add_corridor("KP_1", "INDIA_GATE_C_HEXAGON_W", "KARTAVYA_PATH_MAN_SINGH", "pedestrian", "Kartavya Path Promenade East")
    add_corridor("KP_2", "KARTAVYA_PATH_MAN_SINGH", "KARTAVYA_PATH_JANPATH", "pedestrian", "Kartavya Path Promenade Center")
    add_corridor("MUS_1", "KARTAVYA_PATH_MAN_SINGH", "NATIONAL_MUSEUM", "footway", "National Museum Path")
    add_corridor("MUS_2", "NATIONAL_MUSEUM", "KARTAVYA_PATH_JANPATH", "footway", "Janpath Museum Walk")

    # Connect CP Outer to New Delhi Rly & Kashmere Gate
    add_corridor("CP_NDLS", "CP_OUTER_CONNAUGHT_CIRCUS_N", "NEW_DELHI_RLY", "primary", "Chelmsford Road to New Delhi Rly")
    add_corridor("NDLS_CB", "NEW_DELHI_RLY", "CHAWRI_BAZAR", "secondary", "Ajmeri Gate to Chawri Bazar")
    add_corridor("CB_CC", "CHAWRI_BAZAR", "CHANDNI_CHOWK", "secondary", "Nai Sarak / Chandni Chowk")
    add_corridor("CC_KG", "CHANDNI_CHOWK", "ISBT_KASHMERE_GATE", "primary", "Lothian Road to Kashmere Gate")

    # North-West Arterial Corridor (Kashmere Gate to Rohini)
    # Primary Spine: Ring Road & Outer Ring Road
    add_corridor("KG_CL", "ISBT_KASHMERE_GATE", "CIVIL_LINES", "primary", "Lothian Rd to Civil Lines")
    add_corridor("CL_MR", "CIVIL_LINES", "MALL_ROAD", "primary", "Rajpur Road to Mall Road")
    add_corridor("MR_MT", "MALL_ROAD", "MODEL_TOWN", "primary", "Mall Road to Model Town")
    add_corridor("MT_AZ", "MODEL_TOWN", "AZADPUR_CHOWK", "primary", "GT Karnal Road to Azadpur")
    add_corridor("AZ_SB", "AZADPUR_CHOWK", "SHALIMAR_BAGH", "primary", "Outer Ring Road via Shalimar Bagh")
    add_corridor("SB_MC", "SHALIMAR_BAGH", "MADHUBAN_CHOWK", "primary", "Outer Ring Road to Madhuban Chowk")
    add_corridor("SB_PM", "SHALIMAR_BAGH", "PITAMPURA_METRO", "secondary", "Pitampura Inner Link")
    add_corridor("PM_MC", "PITAMPURA_METRO", "MADHUBAN_CHOWK", "secondary", "Madhuban Link")

    # Rohini Sector Roadways
    add_corridor("MC_RE", "MADHUBAN_CHOWK", "ROHINI_EAST", "primary", "Rohini Sector Arterial East")
    add_corridor("RE_RW", "ROHINI_EAST", "ROHINI_WEST", "primary", "Swarn Jayanti Marg")
    add_corridor("MC_R3", "MADHUBAN_CHOWK", "ROHINI_SEC_3", "secondary", "Sector 3 Access")
    add_corridor("R3_R7", "ROHINI_SEC_3", "ROHINI_SEC_7", "secondary", "Sector 3 to 7 Road")
    add_corridor("R7_RE", "ROHINI_SEC_7", "ROHINI_EAST", "secondary", "Sector 7 to East Metro")
    add_corridor("RE_R11", "ROHINI_EAST", "ROHINI_SEC_11", "primary", "Sector 11 Main Road")
    add_corridor("RW_R11", "ROHINI_WEST", "ROHINI_SEC_11", "primary", "Sector 11 West Link")
    add_corridor("R11_R16", "ROHINI_SEC_11", "ROHINI_SEC_16", "primary", "Sector 11-16 Divider")
    add_corridor("R16_R17", "ROHINI_SEC_16", "ROHINI_SEC_17", "primary", "Sector 16-17 Arterial")
    add_corridor("R17_R23", "ROHINI_SEC_17", "ROHINI_SEC_23", "primary", "Sector 17-23 Road")
    add_corridor("R23_R22", "ROHINI_SEC_23", "ROHINI_SEC_22", "secondary", "Sector 22-23 Link")
    add_corridor("R23_R24", "ROHINI_SEC_23", "ROHINI_SEC_24", "secondary", "Sector 23-24 Link")

    return graph


def convert_osm_pbf_to_graph(pbf_path: str, output_json_path: str | None = None) -> OfflineRoutingGraph:
    """Offline preprocessing pipeline converting .osm.pbf data into OfflineRoutingGraph using pyosmium."""
    import osmium

    class OSMHandler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.nodes_dict: dict[int, tuple[float, float]] = {}
            self.ways_data: list[dict[str, Any]] = []

        def node(self, n):
            self.nodes_dict[n.id] = (n.location.lat, n.location.lon)

        def way(self, w):
            hw = w.tags.get("highway")
            if not hw:
                return
            # Traversable road and walking highway types
            traversable = {
                "footway", "pedestrian", "path", "steps", "living_street",
                "residential", "service", "track", "unclassified", "tertiary",
                "secondary", "primary", "cycleway"
            }
            if hw not in traversable:
                return
            if w.tags.get("access") in ("no", "private"):
                return
            if w.tags.get("foot") in ("no", "private") and hw in ("primary", "secondary"):
                return

            oneway = w.tags.get("oneway") in ("yes", "1", "true")
            name = w.tags.get("name", "")
            refs = [n.ref for n in w.nodes]
            self.ways_data.append({
                "id": str(w.id),
                "highway": hw,
                "name": name,
                "oneway": oneway,
                "refs": refs
            })

    handler = OSMHandler()
    handler.apply_file(pbf_path, locations=True)

    graph = OfflineRoutingGraph(name=os.path.basename(pbf_path))

    # Add used nodes
    used_node_refs = set()
    for way in handler.ways_data:
        for ref in way["refs"]:
            used_node_refs.add(ref)

    for ref in used_node_refs:
        if ref in handler.nodes_dict:
            lat, lon = handler.nodes_dict[ref]
            graph.add_node(Node(id=str(ref), lat=lat, lon=lon))

    # Add edges
    for way in handler.ways_data:
        refs = way["refs"]
        for idx in range(len(refs) - 1):
            u_ref = refs[idx]
            v_ref = refs[idx + 1]
            if u_ref not in graph.nodes or v_ref not in graph.nodes:
                continue

            n1 = graph.nodes[str(u_ref)]
            n2 = graph.nodes[str(v_ref)]
            dist = distance_km(n1.lat, n1.lon, n2.lat, n2.lon)
            if dist < 0.001:
                dist = 0.001

            edge_id = f"osm_{way['id']}_{idx}"
            geom = [[n1.lon, n1.lat], [n2.lon, n2.lat]]
            edge = Edge(
                id=edge_id,
                start=str(u_ref),
                end=str(v_ref),
                length_km=round(dist, 4),
                road_type=way["highway"],
                name=way["name"],
                one_way=way["oneway"],
                geometry=geom,
                tags={"highway": way["highway"]}
            )
            graph.add_edge(edge, bidirectional=not way["oneway"])

    if output_json_path:
        graph.save_json(output_json_path)

    return graph
