"""Local pathfinding algorithms for RAAHI.

Zero network dependency. Implements:
- Algorithm 1: Dijkstra shortest path (priority queue)
- Algorithm 2: A* with admissible Haversine heuristic
- Algorithm 3: Yen's K-Shortest Simple Paths
- Algorithm 4: Risk-weighted A* (edge_cost = distance * (1 + lambda * normalized_risk))
- Algorithm 5: Alternative-route diversity filtering (shared edge overlap & detour limits)
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Any, Callable

from .geo import distance_km
from .offline_graph import Edge, Node, OfflineRoutingGraph


@dataclass
class PathResult:
    """A computed route path across graph nodes and edges."""
    nodes: list[str]
    edges: list[Edge]
    total_distance_km: float
    total_minutes: float
    geometry: list[list[float]] = field(default_factory=list)  # [[lon, lat], ...]
    cost: float = 0.0

    def edge_ids(self) -> list[str]:
        return [e.id for e in self.edges]

    def segment_ids(self) -> list[str]:
        """Extract canonical segment IDs for risk scoring."""
        sids = []
        for e in self.edges:
            sid = e.tags.get("segment_id") or e.id.replace("_rev", "")
            sids.append(sid)
        return sids


def _reconstruct_path(
    came_from: dict[str, tuple[str | None, Edge | None]],
    start: str,
    target: str,
    graph: OfflineRoutingGraph,
    cost: float
) -> PathResult | None:
    if target not in came_from and target != start:
        return None

    nodes: list[str] = [target]
    edges: list[Edge] = []
    curr = target

    while curr != start:
        prev, edge = came_from.get(curr, (None, None))
        if prev is None or edge is None:
            return None
        edges.append(edge)
        curr = prev
        nodes.append(curr)

    nodes.reverse()
    edges.reverse()

    total_dist = sum(e.length_km for e in edges)
    total_min = sum(e.travel_minutes for e in edges)

    # Build coordinates polyline
    geom: list[list[float]] = []
    for edge in edges:
        if edge.geometry:
            for pt in edge.geometry:
                if not geom or geom[-1] != pt:
                    geom.append(pt)
        else:
            n1 = graph.nodes[edge.start]
            n2 = graph.nodes[edge.end]
            p1 = [n1.lon, n1.lat]
            p2 = [n2.lon, n2.lat]
            if not geom or geom[-1] != p1:
                geom.append(p1)
            geom.append(p2)

    return PathResult(
        nodes=nodes,
        edges=edges,
        total_distance_km=round(total_dist, 3),
        total_minutes=round(total_min, 1),
        geometry=geom,
        cost=round(cost, 4)
    )


def dijkstra(
    graph: OfflineRoutingGraph,
    start: str,
    target: str,
    weight_func: Callable[[Edge], float] | None = None,
    ignored_edges: set[str] | None = None,
    ignored_nodes: set[str] | None = None
) -> PathResult | None:
    """Algorithm 1: Dijkstra shortest path using min-heap priority queue."""
    if start not in graph.nodes or target not in graph.nodes:
        return None
    if start == target:
        n = graph.nodes[start]
        return PathResult(nodes=[start], edges=[], total_distance_km=0.0, total_minutes=0.0, geometry=[[n.lon, n.lat]])

    ignored_edges = ignored_edges or set()
    ignored_nodes = ignored_nodes or set()

    cost_fn = weight_func or (lambda e: e.length_km)

    # Priority queue: (cost, node_id)
    pq: list[tuple[float, str]] = [(0.0, start)]
    dist: dict[str, float] = {start: 0.0}
    came_from: dict[str, tuple[str | None, Edge | None]] = {start: (None, None)}

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        if u == target:
            break

        for edge in graph.get_outgoing(u):
            if edge.id in ignored_edges:
                continue
            v = edge.end
            if v in ignored_nodes and v != target:
                continue

            weight = cost_fn(edge)
            if weight < 0:
                raise ValueError(f"Dijkstra requires non-negative edge weights; got {weight}")

            new_d = d + weight
            if new_d < dist.get(v, math.inf):
                dist[v] = new_d
                came_from[v] = (u, edge)
                heapq.heappush(pq, (new_d, v))

    if target not in dist:
        return None

    return _reconstruct_path(came_from, start, target, graph, dist[target])


def a_star(
    graph: OfflineRoutingGraph,
    start: str,
    target: str,
    weight_func: Callable[[Edge], float] | None = None,
    heuristic_func: Callable[[str, str], float] | None = None,
    ignored_edges: set[str] | None = None,
    ignored_nodes: set[str] | None = None
) -> PathResult | None:
    """Algorithm 2: A* with goal-directed admissible Haversine heuristic."""
    if start not in graph.nodes or target not in graph.nodes:
        return None
    if start == target:
        n = graph.nodes[start]
        return PathResult(nodes=[start], edges=[], total_distance_km=0.0, total_minutes=0.0, geometry=[[n.lon, n.lat]])

    ignored_edges = ignored_edges or set()
    ignored_nodes = ignored_nodes or set()

    cost_fn = weight_func or (lambda e: e.length_km)
    target_node = graph.nodes[target]

    def haversine_h(u: str, tgt: str) -> float:
        un = graph.nodes[u]
        return distance_km(un.lat, un.lon, target_node.lat, target_node.lon)

    h_fn = heuristic_func or haversine_h

    # Priority queue: (f_score, g_score, node_id)
    start_h = h_fn(start, target)
    pq: list[tuple[float, float, str]] = [(start_h, 0.0, start)]
    g_score: dict[str, float] = {start: 0.0}
    came_from: dict[str, tuple[str | None, Edge | None]] = {start: (None, None)}

    while pq:
        f, g, u = heapq.heappop(pq)
        if g > g_score.get(u, math.inf):
            continue
        if u == target:
            break

        for edge in graph.get_outgoing(u):
            if edge.id in ignored_edges:
                continue
            v = edge.end
            if v in ignored_nodes and v != target:
                continue

            weight = cost_fn(edge)
            tentative_g = g + weight
            if tentative_g < g_score.get(v, math.inf):
                g_score[v] = tentative_g
                came_from[v] = (u, edge)
                f_v = tentative_g + h_fn(v, target)
                heapq.heappush(pq, (f_v, tentative_g, v))

    if target not in g_score:
        return None

    return _reconstruct_path(came_from, start, target, graph, g_score[target])


def yens_k_shortest_paths(
    graph: OfflineRoutingGraph,
    start: str,
    target: str,
    K: int = 5,
    weight_func: Callable[[Edge], float] | None = None
) -> list[PathResult]:
    """Algorithm 3: Yen's algorithm for finding top K loopless simple paths."""
    A: list[PathResult] = []
    # Candidate B heap: stores (cost, counter, PathResult)
    B: list[tuple[float, int, PathResult]] = []
    counter = 0

    initial = a_star(graph, start, target, weight_func=weight_func)
    if not initial:
        return []
    A.append(initial)

    for k in range(1, K):
        prev_path = A[k - 1]
        
        # Iterate over spur nodes from index 0 to len(nodes) - 2
        for i in range(len(prev_path.nodes) - 1):
            spur_node = prev_path.nodes[i]
            root_path_nodes = prev_path.nodes[:i + 1]
            root_path_edges = prev_path.edges[:i]

            ignored_edges: set[str] = set()
            for path in A:
                if len(path.nodes) > i and path.nodes[:i + 1] == root_path_nodes:
                    if i < len(path.edges):
                        ignored_edges.add(path.edges[i].id)

            ignored_nodes = set(root_path_nodes[:-1])

            spur_path = dijkstra(
                graph,
                spur_node,
                target,
                weight_func=weight_func,
                ignored_edges=ignored_edges,
                ignored_nodes=ignored_nodes
            )

            if spur_path:
                total_nodes = root_path_nodes[:-1] + spur_path.nodes
                # Ensure simple path (no repeated nodes)
                if len(total_nodes) == len(set(total_nodes)):
                    total_edges = root_path_edges + spur_path.edges
                    total_dist = sum(e.length_km for e in total_edges)
                    total_min = sum(e.travel_minutes for e in total_edges)
                    cost_val = sum((weight_func or (lambda e: e.length_km))(e) for e in total_edges)

                    geom: list[list[float]] = []
                    for e in total_edges:
                        if e.geometry:
                            for pt in e.geometry:
                                if not geom or geom[-1] != pt:
                                    geom.append(pt)
                        else:
                            n1 = graph.nodes[e.start]
                            n2 = graph.nodes[e.end]
                            if not geom or geom[-1] != [n1.lon, n1.lat]:
                                geom.append([n1.lon, n1.lat])
                            geom.append([n2.lon, n2.lat])

                    candidate = PathResult(
                        nodes=total_nodes,
                        edges=total_edges,
                        total_distance_km=round(total_dist, 3),
                        total_minutes=round(total_min, 1),
                        geometry=geom,
                        cost=round(cost_val, 4)
                    )

                    # Check if already in A or B
                    if not any(p.nodes == candidate.nodes for p in A):
                        if not any(item[2].nodes == candidate.nodes for item in B):
                            counter += 1
                            heapq.heappush(B, (candidate.cost, counter, candidate))

        if not B:
            break

        _, _, best_candidate = heapq.heappop(B)
        A.append(best_candidate)

    return A


def risk_weighted_a_star(
    graph: OfflineRoutingGraph,
    start: str,
    target: str,
    lambda_risk: float,
    risk_lookup: dict[str, float]
) -> PathResult | None:
    """Algorithm 4: Risk-weighted A* optimization.

    edge_cost = distance_km * (1.0 + lambda_risk * (normalized_risk))
    where normalized_risk = risk_score / 100.0.
    Since edge_cost >= distance_km >= haversine, the Haversine heuristic is admissible.
    """
    def risk_cost(edge: Edge) -> float:
        sid = edge.tags.get("segment_id") or edge.id.replace("_rev", "")
        risk = risk_lookup.get(sid, 50.0)  # Neutral 50 if unassessed
        norm_risk = max(0.0, min(100.0, risk)) / 100.0
        return edge.length_km * (1.0 + max(0.0, lambda_risk) * norm_risk)

    return a_star(graph, start, target, weight_func=risk_cost)


def calculate_route_overlap(path_a: PathResult, path_b: PathResult) -> float:
    """Algorithm 5: Calculate shared edge length overlap ratio between two paths."""
    edges_a = {e.id.replace("_rev", ""): e.length_km for e in path_a.edges}
    edges_b = {e.id.replace("_rev", ""): e.length_km for e in path_b.edges}

    shared_km = sum(edges_a[eid] for eid in edges_a if eid in edges_b)
    len_a = path_a.total_distance_km or 1.0
    len_b = path_b.total_distance_km or 1.0
    min_len = min(len_a, len_b)

    return shared_km / min_len if min_len > 0 else 1.0


def filter_diverse_routes(
    candidates: list[PathResult],
    max_overlap_ratio: float = 0.75,
    max_detour_ratio: float = 1.60
) -> list[PathResult]:
    """Algorithm 5: Filter candidate routes to ensure topological diversity and practical limits."""
    if not candidates:
        return []

    # Sort candidates by cost/distance
    candidates = sorted(candidates, key=lambda p: (p.total_distance_km, p.cost))
    shortest_dist = candidates[0].total_distance_km or 0.1

    accepted: list[PathResult] = [candidates[0]]

    for cand in candidates[1:]:
        # Filter excessive detour
        if cand.total_distance_km > shortest_dist * max_detour_ratio:
            continue

        # Filter excessive overlap with all already accepted routes
        overlap_too_high = False
        for acc in accepted:
            overlap = calculate_route_overlap(cand, acc)
            if overlap >= max_overlap_ratio:
                overlap_too_high = True
                break

        if not overlap_too_high:
            accepted.append(cand)

    return accepted


def generate_candidate_routes(
    graph: OfflineRoutingGraph,
    start_node: str,
    target_node: str,
    risk_lookup: dict[str, float] | None = None,
    k_alternatives: int = 5
) -> list[PathResult]:
    """Multi-strategy route candidate generator.

    Combines:
    1. Shortest distance (A* / Dijkstra)
    2. Fastest travel (travel_minutes)
    3. Risk-weighted A* (with varying lambda risk aversion: 0.8, 1.5, 2.5)
    4. Yen's K-Shortest Simple Paths
    Then deduplicates and filters for meaningful alternative diversity.
    """
    raw_candidates: list[PathResult] = []
    risk_map = risk_lookup or {}

    # 1. Shortest distance
    shortest = a_star(graph, start_node, target_node, weight_func=lambda e: e.length_km)
    if shortest:
        raw_candidates.append(shortest)

    # 2. Fastest travel
    fastest = a_star(graph, start_node, target_node, weight_func=lambda e: e.travel_minutes)
    if fastest:
        raw_candidates.append(fastest)

    # 3. Risk-weighted A* with multiple aversion levels
    for lam in (0.8, 1.5, 2.5):
        rw = risk_weighted_a_star(graph, start_node, target_node, lambda_risk=lam, risk_lookup=risk_map)
        if rw:
            raw_candidates.append(rw)

    # 4. Yen's K-shortest paths
    yen_paths = yens_k_shortest_paths(graph, start_node, target_node, K=k_alternatives, weight_func=lambda e: e.length_km)
    raw_candidates.extend(yen_paths)

    # Deduplicate strictly identical node sequences
    unique_candidates: list[PathResult] = []
    seen_node_seqs: set[tuple[str, ...]] = set()

    for p in raw_candidates:
        seq = tuple(p.nodes)
        if seq not in seen_node_seqs:
            seen_node_seqs.add(seq)
            unique_candidates.append(p)

    # Filter for diverse alternatives
    diverse = filter_diverse_routes(unique_candidates, max_overlap_ratio=0.85, max_detour_ratio=1.60)
    if len(diverse) < 2 and len(unique_candidates) >= 2:
        diverse = filter_diverse_routes(unique_candidates, max_overlap_ratio=0.92, max_detour_ratio=1.60)
    if not diverse and unique_candidates:
        diverse = [unique_candidates[0]]
    return diverse[:k_alternatives]
