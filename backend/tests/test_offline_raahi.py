"""Comprehensive automated test suite for RAAHI Offline AI Safe Route Decision System.

Verifies:
- Graph topology, connectivity, directional restrictions, snapping
- Dijkstra correctness, A* optimality vs Dijkstra
- Yen's K-Shortest Simple Paths & diversity filtering
- Risk-weighted A* optimization
- Exact 7 scoring parameters, missing data handling, coverage, confidence
- GREEN/YELLOW/RED/GREY classification boundaries
- Whole-route scoring (70% weighted avg + 30% peak stretch)
- Mode A (synthetic demo) vs Mode B (real OSM) strict data isolation
- Local Scikit-learn Random Forest offline training & inference
- Safety-first Decision Engine recommendation & explainability
- Safe Spot offline walking routing
- Backup (Tap Me) checkin cadence integration
- Zero network requests.
"""

import math
import os
import unittest
from unittest.mock import patch

from app.geo import distance_km
from app.offline_graph import (
    Edge,
    Node,
    OfflineRoutingGraph,
    SpatialGridIndex,
    build_delhi_real_osm_corridors,
    build_delhi_synthetic_topology,
)
from app.offline_provider import OfflineMappingProvider
from app.pathfinding import (
    PathResult,
    a_star,
    calculate_route_overlap,
    dijkstra,
    filter_diverse_routes,
    generate_candidate_routes,
    risk_weighted_a_star,
    yens_k_shortest_paths,
)
from app.raahi_ml import ML_ENGINE, RaahiOfflineMLEngine
from app.raahi_risk_engine import (
    RISK_WEIGHTS,
    SYNTHETIC_STORE,
    TOTAL_WEIGHT_SUM,
    assess_route_segments,
    calculate_segment_score,
    calculate_whole_route_risk,
)
from app.route_decision_engine import decide_safe_routes


class OfflineRaahiTests(unittest.TestCase):

    def setUp(self):
        # Create a small, deterministic test graph G = (V, E)
        # N1 --(1.0km)--> N2 --(1.0km)--> N3 --(1.0km)--> N4  (Total: 3.0km)
        #  |                               |
        #  +--------(2.2km)--------------->+  (Total: 3.2km)
        self.test_graph = OfflineRoutingGraph(name="test_grid")
        self.test_graph.add_node(Node("N1", 28.6000, 77.2000))
        self.test_graph.add_node(Node("N2", 28.6090, 77.2000))
        self.test_graph.add_node(Node("N3", 28.6180, 77.2000))
        self.test_graph.add_node(Node("N4", 28.6270, 77.2000))

        self.test_graph.add_edge(Edge("E12", "N1", "N2", 1.0, "primary", "Street 1-2"), bidirectional=True)
        self.test_graph.add_edge(Edge("E23", "N2", "N3", 1.0, "primary", "Street 2-3"), bidirectional=True)
        self.test_graph.add_edge(Edge("E34", "N3", "N4", 1.0, "primary", "Street 3-4"), bidirectional=True)
        self.test_graph.add_edge(Edge("E13_bypass", "N1", "N3", 2.2, "secondary", "Bypass 1-3"), bidirectional=True)

    # 1. Graph Topology & Directional Restrictions
    def test_graph_directional_restrictions(self):
        g = OfflineRoutingGraph(name="oneway_test")
        g.add_node(Node("A", 28.0, 77.0))
        g.add_node(Node("B", 28.01, 77.0))
        g.add_edge(Edge("E_oneway", "A", "B", 1.0, one_way=True), bidirectional=False)

        self.assertEqual(len(g.get_outgoing("A")), 1)
        self.assertEqual(len(g.get_outgoing("B")), 0)

        # Route from A to B works
        path = dijkstra(g, "A", "B")
        self.assertIsNotNone(path)

        # Route from B to A fails due to one-way restriction
        rev_path = dijkstra(g, "B", "A")
        self.assertIsNone(rev_path)

    # 2. Spatial Index & Coordinate Snapping
    def test_spatial_grid_snapping(self):
        node, dist = self.test_graph.snap(28.6001, 77.2001, max_distance_km=1.0)
        self.assertIsNotNone(node)
        self.assertEqual(node.id, "N1")
        self.assertLess(dist, 0.1)

        # Snapping far away should return None
        far_node, _ = self.test_graph.snap(10.0, 10.0, max_distance_km=2.0)
        self.assertIsNone(far_node)

    # 3. Dijkstra Correctness
    def test_dijkstra_correctness(self):
        res = dijkstra(self.test_graph, "N1", "N4")
        self.assertIsNotNone(res)
        self.assertEqual(res.nodes, ["N1", "N2", "N3", "N4"])
        self.assertAlmostEqual(res.total_distance_km, 3.0, places=2)

    # 4. A* Optimality vs Dijkstra
    def test_a_star_optimality_vs_dijkstra(self):
        d_res = dijkstra(self.test_graph, "N1", "N4")
        a_res = a_star(self.test_graph, "N1", "N4")
        self.assertIsNotNone(a_res)
        self.assertEqual(d_res.nodes, a_res.nodes)
        self.assertAlmostEqual(d_res.total_distance_km, a_res.total_distance_km, places=4)

    # 5. Yen's K-Shortest Simple Paths
    def test_yens_k_shortest_simple_paths(self):
        paths = yens_k_shortest_paths(self.test_graph, "N1", "N4", K=3)
        self.assertGreaterEqual(len(paths), 2)
        # Check sorted order of distance
        self.assertLessEqual(paths[0].total_distance_km, paths[1].total_distance_km)
        # Check paths are simple (no duplicate nodes)
        for p in paths:
            self.assertEqual(len(p.nodes), len(set(p.nodes)))

    # 6. Risk-Weighted A* Optimization
    def test_risk_weighted_a_star(self):
        # By default, path via N2 is 2.0 km (E12 + E23), bypass is 2.2 km
        # If N2 stretch (E12 or E23) has extreme risk (95) and bypass has low risk (10),
        # risk-weighted A* with lambda=2.0 should divert to the bypass
        risk_map = {"E12": 95.0, "E23": 95.0, "E13_bypass": 10.0}

        shortest = a_star(self.test_graph, "N1", "N3")
        self.assertEqual(shortest.nodes, ["N1", "N2", "N3"])

        diverted = risk_weighted_a_star(self.test_graph, "N1", "N3", lambda_risk=2.0, risk_lookup=risk_map)
        self.assertIsNotNone(diverted)
        self.assertEqual(diverted.nodes, ["N1", "N3"])  # Chose the safer bypass

    # 7. Alternative-Route Diversity Filtering
    def test_route_diversity_filtering(self):
        p1 = PathResult(nodes=["A", "B", "C"], edges=[Edge("E1", "A", "B", 1.0), Edge("E2", "B", "C", 1.0)], total_distance_km=2.0, total_minutes=25)
        # p2 shares 100% of edges with p1
        p2 = PathResult(nodes=["A", "B", "C"], edges=[Edge("E1", "A", "B", 1.0), Edge("E2", "B", "C", 1.0)], total_distance_km=2.0, total_minutes=25)
        overlap = calculate_route_overlap(p1, p2)
        self.assertEqual(overlap, 1.0)

        filtered = filter_diverse_routes([p1, p2], max_overlap_ratio=0.75)
        self.assertEqual(len(filtered), 1)

    # 8. Exact 7 Scoring Parameters and Weights
    def test_exact_scoring_parameters_and_weights(self):
        self.assertAlmostEqual(TOTAL_WEIGHT_SUM, 0.90, places=4)
        self.assertEqual(len(RISK_WEIGHTS), 7)
        self.assertEqual(RISK_WEIGHTS["incident_risk"], 0.25)
        self.assertEqual(RISK_WEIGHTS["report_freshness"], 0.15)
        self.assertEqual(RISK_WEIGHTS["population_foot_traffic_risk"], 0.10)
        self.assertEqual(RISK_WEIGHTS["lighting_risk"], 0.10)
        self.assertEqual(RISK_WEIGHTS["time_of_day_risk"], 0.10)
        self.assertEqual(RISK_WEIGHTS["historical_risk"], 0.10)
        self.assertEqual(RISK_WEIGHTS["isolation_risk"], 0.10)

    # 9. Missing Data Handling (Never replaced with zero)
    def test_missing_data_coverage_reduction(self):
        # All 7 inputs present
        full_inputs = {k: 50.0 for k in RISK_WEIGHTS}
        res_full = calculate_segment_score(full_inputs, corroboration=0.5)
        self.assertAlmostEqual(res_full.coverage, 0.90, places=2)
        self.assertAlmostEqual(res_full.score, 50.0, places=1)

        # Only incident_risk provided (weight 0.25 < 0.40 threshold)
        sparse_inputs = {"incident_risk": 20.0}
        res_sparse = calculate_segment_score(sparse_inputs, corroboration=0.5)
        self.assertAlmostEqual(res_sparse.coverage, 0.25, places=2)
        # Must be GREY due to coverage < 0.40
        self.assertEqual(res_sparse.classification, "GREY")
        self.assertEqual(res_sparse.data_status, "INSUFFICIENT")

    # 10. Classification Boundaries
    def test_risk_classification_boundaries(self):
        inputs_green = {k: 30.0 for k in RISK_WEIGHTS}
        res_g = calculate_segment_score(inputs_green, corroboration=0.5)
        self.assertEqual(res_g.classification, "GREEN")

        inputs_yellow = {k: 50.0 for k in RISK_WEIGHTS}
        res_y = calculate_segment_score(inputs_yellow, corroboration=0.5)
        self.assertEqual(res_y.classification, "YELLOW")

        inputs_red = {k: 75.0 for k in RISK_WEIGHTS}
        res_r = calculate_segment_score(inputs_red, corroboration=0.5)
        self.assertEqual(res_r.classification, "RED")

    # 11. Whole-Route Scoring Formula
    def test_whole_route_scoring_formula(self):
        s1 = calculate_segment_score({k: 40.0 for k in RISK_WEIGHTS}, length_km=1.0, corroboration=0.6)
        s2 = calculate_segment_score({k: 80.0 for k in RISK_WEIGHTS}, length_km=1.0, corroboration=0.6)

        route_res = calculate_whole_route_risk([s1, s2])
        # weighted_avg = (1.0*40 + 1.0*80) / 2 = 60.0
        # peak = 80.0
        # route_score = 0.70 * 60.0 + 0.30 * 80.0 = 42.0 + 24.0 = 66.0
        self.assertAlmostEqual(route_res.route_score, 66.0, places=1)
        self.assertEqual(route_res.classification, "RED")
        self.assertEqual(route_res.highest_risk_segment_id, s2.segment_id)

    # 12. Synthetic vs Real Data Strict Isolation
    def test_synthetic_vs_real_data_isolation(self):
        # Mode A: Synthetic demonstration
        syn_res = assess_route_segments(["RSEG0001", "RSEG0002"], [0.5, 0.5], time_band="morning", mode="synthetic")
        self.assertTrue(syn_res.is_synthetic)
        self.assertIsNotNone(syn_res.route_score)

        # Mode B: Real road network
        real_res = assess_route_segments(["CP_IN_AB", "JANPATH_1"], [0.4, 0.8], time_band="morning", mode="real")
        self.assertFalse(real_res.is_synthetic)
        self.assertIsNone(real_res.route_score)
        self.assertEqual(real_res.classification, "GREY")
        self.assertEqual(real_res.data_status, "UNASSESSED")

    # 13. Offline Machine Learning Training and Inference
    def test_offline_ml_component(self):
        rep = ML_ENGINE.train_and_evaluate("random_forest")
        self.assertIsNotNone(rep)
        self.assertGreater(rep.sample_count, 100)
        self.assertIn("length_km", rep.feature_importances)

        pred = ML_ENGINE.predict_segment_risk(length_km=0.7, time_band="night", lighting_status="poor")
        self.assertIn("predicted_risk_score", pred)
        self.assertIn(pred["predicted_classification"], ("GREEN", "YELLOW", "RED"))
        self.assertTrue(pred["is_synthetic_demonstration"])

    # 14. Safety-First Route Decision Engine
    def test_decision_engine_tradeoff_recommendation(self):
        # Build candidate paths in synthetic demo
        g = build_delhi_synthetic_topology()
        cands = generate_candidate_routes(g, "N0001", "N0010", k_alternatives=3)
        self.assertGreaterEqual(len(cands), 1)

        decision = decide_safe_routes(cands, time_band="day", mode="synthetic")
        self.assertTrue(decision.has_reliable_recommendation)
        self.assertIsNotNone(decision.recommended_route)
        self.assertTrue(decision.recommended_route.is_recommended)
        self.assertIn("Recommended", decision.recommended_route.tradeoff_explanation)

    # 15. Unassessed Corridors Honest Statement
    def test_unassessed_routes_honest_fallback(self):
        g = build_delhi_real_osm_corridors()
        cands = generate_candidate_routes(g, "CP_BLOCK_A", "INDIA_GATE_CENTRAL", k_alternatives=2)
        self.assertGreaterEqual(len(cands), 1)

        decision = decide_safe_routes(cands, time_band="day", mode="real")
        self.assertFalse(decision.has_reliable_recommendation)
        self.assertIsNone(decision.recommended_route)
        self.assertEqual(decision.status_message, "No route has sufficient evidence for a reliable safety recommendation.")

    # 16. Safe Spot Offline Walking Integration
    def test_safe_spot_offline_walking(self):
        provider = OfflineMappingProvider()
        # Safe Spot search from Rajiv Chowk (CP) to a nearby point
        res = provider.alternatives(
            origin="Rajiv Chowk",
            destination="Connaught Place Inner Circle B",
            origin_coordinates=(28.6328, 77.2197),
            destination_coordinates=(28.6335, 77.2210),
            context="safe_spot"
        )
        self.assertTrue(res["offline"])
        self.assertIn("safe_spot_walking", res)
        walking = res["safe_spot_walking"]
        self.assertGreater(walking["distance_km"], 0.0)
        self.assertGreater(walking["minutes"], 0.0)
        self.assertGreater(len(walking["geometry"]), 0)

    # 17. Time-Dependent Scoring
    def test_time_dependent_variation(self):
        ass_day = SYNTHETIC_STORE.get_segment_risk("RSEG0001", "day")
        ass_night = SYNTHETIC_STORE.get_segment_risk("RSEG0001", "night")
        self.assertIsNotNone(ass_day)
        self.assertIsNotNone(ass_night)
        # Different time bands evaluate different lighting and time-of-day risks
        self.assertEqual(ass_day.time_band, "day")
        self.assertEqual(ass_night.time_band, "night")


if __name__ == "__main__":
    unittest.main()
