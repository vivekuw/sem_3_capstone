"""Comprehensive tests for Phase 2: Neo4j Knowledge Graph schema, topology seed, and query helpers."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from knowledge_graph.queries import KnowledgeGraphQueries
from causal_reasoning.graph_proximity import PlantGraphTopology


def test_cypher_seed_files_exist_and_contain_required_schema():
    """Verify that Cypher scripts contain the exact requested ontology."""
    kg_dir = Path(__file__).resolve().parent.parent / "knowledge_graph"
    schema_path = kg_dir / "schema.cypher"
    seed_path = kg_dir / "seed_tep_topology.cypher"

    assert schema_path.exists(), "schema.cypher must exist"
    assert seed_path.exists(), "seed_tep_topology.cypher must exist"

    schema_content = schema_path.read_text(encoding="utf-8")
    assert "CONSTRAINT" in schema_content
    assert "Unit" in schema_content
    assert "Sensor" in schema_content
    assert "FailureMode" in schema_content

    seed_content = seed_path.read_text(encoding="utf-8")
    # Verify core relationships specified by user
    assert ":FEEDS" in seed_content
    assert ":MEASURES" in seed_content
    assert ":SUSCEPTIBLE_TO" in seed_content
    assert ":TYPICALLY_CAUSES" in seed_content
    # Verify key plant units
    assert "UNIT_REACTOR" in seed_content
    assert "UNIT_CONDENSER" in seed_content
    assert "UNIT_SEPARATOR" in seed_content
    assert "UNIT_COMPRESSOR" in seed_content
    assert "UNIT_STRIPPER" in seed_content


def test_plant_graph_topology_hops():
    """Verify shortest path hop calculations between plant equipment."""
    topology = PlantGraphTopology()
    # Feed to Reactor is 1 hop
    assert topology.get_unit_hop_distance("UNIT_FEED", "UNIT_REACTOR") == 1
    # Feed to Condenser is 2 hops (Feed -> Reactor -> Condenser)
    assert topology.get_unit_hop_distance("UNIT_FEED", "UNIT_CONDENSER") == 2
    # Separator to Compressor is 1 hop
    assert topology.get_unit_hop_distance("UNIT_SEPARATOR", "UNIT_COMPRESSOR") == 1


def test_kg_queries_unit_for_sensor():
    """Test get_unit_for_sensor query helper with mocked driver."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    mock_record = {
        "id": "UNIT_REACTOR",
        "name": "Chemical Reactor",
        "description": "Continuous stirred-tank reactor",
    }
    mock_session.run.return_value.single.return_value = mock_record

    queries = KnowledgeGraphQueries(mock_driver)
    unit = queries.get_unit_for_sensor("XMEAS_9")
    assert unit is not None
    assert unit["id"] == "UNIT_REACTOR"
    assert unit["name"] == "Chemical Reactor"


def test_kg_queries_candidate_failure_modes():
    """Test get_candidate_failure_modes query helper."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    mock_record = {
        "failure_id": "IDV_4",
        "code": "IDV(4)",
        "name": "Reactor Cooling Water Inlet Temp Step Increase",
        "category": "Cooling Disturbance",
        "severity": "High",
        "description": "Excursion",
        "matching_sensors": ["XMEAS_9", "XMEAS_21"],
        "unit_id": "UNIT_REACTOR",
        "unit_name": "Chemical Reactor",
    }
    mock_session.run.return_value = [mock_record]

    queries = KnowledgeGraphQueries(mock_driver)
    results = queries.get_candidate_failure_modes(["XMEAS_9", "XMEAS_21"])
    assert len(results) == 1
    assert results[0]["code"] == "IDV(4)"
    assert "XMEAS_9" in results[0]["matching_sensors"]


def test_kg_queries_upstream_and_cascading():
    """Test get_upstream_units and get_cascading_failure_chain helpers."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    # Upstream mock
    mock_session.run.return_value = [
        {"id": "UNIT_FEED", "name": "Feed Delivery System", "hop_distance": 1},
        {"id": "UNIT_COMPRESSOR", "name": "Recycle Compressor", "hop_distance": 1},
    ]

    queries = KnowledgeGraphQueries(mock_driver)
    upstream = queries.get_upstream_units("UNIT_REACTOR")
    assert len(upstream) == 2
    assert upstream[0]["id"] == "UNIT_FEED"
