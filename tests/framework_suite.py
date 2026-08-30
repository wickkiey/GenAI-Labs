"""
Shared test suite for all Phase 7 frameworks.

This harness takes a callable run(question) -> Answer and runs standardized tests.
"""

from __future__ import annotations

from typing import Callable

from common.config import settings

# Import the Answer model and test questions
try:
    from spec import Answer, TEST_QUESTIONS
except ImportError:
    from 06_frameworks.spec import Answer, TEST_QUESTIONS


def run_framework_tests(
    run_agent: Callable[[str], Answer],
    framework_name: str,
    verbose: bool = False,
) -> dict[str, any]:
    """
    Run standardized tests on a framework implementation.
    
    Args:
        run_agent: Callable that takes a question and returns Answer
        framework_name: Name of the framework for reporting
        verbose: Print detailed output
    
    Returns:
        Dict with test results
    """
    results = {
        "framework": framework_name,
        "total_tests": len(TEST_QUESTIONS),
        "passed": 0,
        "failed": 0,
        "errors": [],
        "questions": [],
    }

    for i, question in enumerate(TEST_QUESTIONS, 1):
        test_result = {
            "question": question,
            "passed": False,
            "error": None,
        }

        try:
            answer = run_agent(question)
            
            # Validate Answer structure
            assert isinstance(answer, Answer), f"Expected Answer, got {type(answer)}"
            assert answer.value, "Answer value is empty"
            assert answer.reasoning, "Answer reasoning is empty"
            assert isinstance(answer.tools_used, list), "tools_used should be a list"
            assert answer.confidence in ["high", "medium", "low"], "Invalid confidence"
            
            test_result["passed"] = True
            results["passed"] += 1
            
            if verbose:
                print(f"✓ Question {i}: {question[:50]}...")
                print(f"  Answer: {answer.value[:100]}...")
                print(f"  Tools: {answer.tools_used}, Confidence: {answer.confidence}")

        except Exception as e:
            test_result["error"] = str(e)
            results["failed"] += 1
            results["errors"].append(f"Q{i}: {str(e)}")
            
            if verbose:
                print(f"✗ Question {i}: {question[:50]}...")
                print(f"  Error: {e}")

        results["questions"].append(test_result)

    return results


def print_results(results: dict) -> None:
    """Print test results in a nice format."""
    print(f"\n{'='*60}")
    print(f"Framework: {results['framework']}")
    print(f"Results: {results['passed']}/{results['total_tests']} passed")
    print(f"{'='*60}")
    
    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    print()


if __name__ == "__main__":
    print("Framework test suite loaded.")
    print("Use: run_framework_tests(run_agent_func, 'framework_name')")
