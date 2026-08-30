"""
Phase 7 Test: Framework comparison

Run the same spec task across all 6 frameworks and compare results.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from tests.framework_suite import run_framework_tests, print_results


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_pydantic_ai():
    """Test PydanticAI implementation."""
    try:
        from06_frameworks.pydantic_ai.06_the_spec_task import run_agent
        results = run_framework_tests(run_agent, "PydanticAI")
        print_results(results)
        assert results["passed"] >= 8, f"PydanticAI: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("pydantic-ai not installed")


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_langchain():
    """Test LangChain implementation."""
    try:
        from 06_frameworks.langchain.06_the_spec_task import run_agent
        results = run_framework_tests(run_agent, "LangChain")
        print_results(results)
        assert results["passed"] >= 8, f"LangChain: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("langchain not installed")


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_langgraph():
    """Test LangGraph implementation."""
    try:
        from 06_frameworks.langgraph.10_the_spec_task import run_agent
        results = run_framework_tests(run_agent, "LangGraph")
        print_results(results)
        assert results["passed"] >= 8, f"LangGraph: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("langgraph not installed")


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_strands():
    """Test Strands implementation."""
    try:
        from 06_frameworks.strands.01_agent import run_agent
        results = run_framework_tests(run_agent, "Strands")
        print_results(results)
        assert results["passed"] >= 8, f"Strands: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("strands-agents not installed")


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_crewai():
    """Test CrewAI implementation."""
    try:
        from 06_frameworks.crewai.01_agent import run_agent
        results = run_framework_tests(run_agent, "CrewAI")
        print_results(results)
        assert results["passed"] >= 8, f"CrewAI: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("crewai not installed")


@pytest.mark.skipif(True, reason="Requires framework dependencies - run manually")
def test_autogen():
    """Test AutoGen implementation."""
    try:
        from 06_frameworks.autogen.01_agent import run_agent
        results = run_framework_tests(run_agent, "AutoGen")
        print_results(results)
        assert results["passed"] >= 8, f"AutoGen: {results['passed']}/10 passed"
    except ImportError:
        pytest.skip("autogen-agentchat not installed")


if __name__ == "__main__":
    # Manual test runner
    print("Phase 7 Framework Tests")
    print("=" * 60)
    print("\nTo test individual frameworks:")
    print("  python -m pytest tests/test_phase7.py::test_pydantic_ai -v")
    print("\nOr run framework scripts directly:")
    print("  python 06_frameworks/pydantic_ai/06_the_spec_task.py")
    print("  python 06_frameworks/langchain/06_the_spec_task.py")
    print("  python 06_frameworks/langgraph/10_the_spec_task.py")
