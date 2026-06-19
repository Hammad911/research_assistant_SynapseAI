"""Smoke tests.

These check that the graph compiles and that the routing functions send work to
the right next agent. They run without any network access or API keys.
"""

from app.graph import build_graph, route_after_research, route_after_validation


def test_graph_compiles():
    graph = build_graph()
    assert graph is not None


def test_high_confidence_routes_to_synthesis():
    state = {"confidence_score": 8}
    assert route_after_research(state) == "synthesis"


def test_low_confidence_routes_to_validator():
    state = {"confidence_score": 2}
    assert route_after_research(state) == "validator"


def test_sufficient_validation_routes_to_synthesis():
    state = {"validation_result": "sufficient", "attempts": 1}
    assert route_after_validation(state) == "synthesis"


def test_insufficient_validation_loops_back_to_research():
    state = {"validation_result": "insufficient", "attempts": 1}
    assert route_after_validation(state) == "research"


def test_boundary_confidence_routes_to_synthesis():
    from app.config import settings
    state = {"confidence_score": settings.confidence_threshold}
    assert route_after_research(state) == "synthesis"
