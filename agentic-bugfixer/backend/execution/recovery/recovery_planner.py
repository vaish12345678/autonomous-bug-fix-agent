"""
Intelligent Recovery Planner

Converts classified test failures into a generic recovery strategy.

This module does NOT know benchmark names or specific bugs.
"""

from typing import Dict


RECOVERY_RULES = {
    "ASSERTION_ERROR": {
        "strategy": "REANALYZE_AND_REPAIR",
        "priority": "HIGH",
        "action": (
            "Re-evaluate the root cause, inspect the failing test output, "
            "generate a corrected patch, validate it, and rerun tests."
        ),
        "retry_allowed": True,
        "max_attempts": 3,
    },
    "SYNTAX_ERROR": {
        "strategy": "SYNTAX_REPAIR",
        "priority": "CRITICAL",
        "action": (
            "Inspect the syntax failure, correct the generated source, "
            "validate syntax again, and rerun tests."
        ),
        "retry_allowed": True,
        "max_attempts": 3,
    },
    "IMPORT_ERROR": {
        "strategy": "DEPENDENCY_REPAIR",
        "priority": "HIGH",
        "action": (
            "Inspect the import failure and repository structure, "
            "correct the implementation or import usage, then rerun tests."
        ),
        "retry_allowed": True,
        "max_attempts": 3,
    },
    "TIMEOUT": {
        "strategy": "TIMEOUT_REVIEW",
        "priority": "CRITICAL",
        "action": (
            "Inspect the execution timeout, identify the operation causing "
            "excessive runtime, apply a safe correction, and rerun tests."
        ),
        "retry_allowed": True,
        "max_attempts": 2,
    },
    "TEST_COLLECTION_ERROR": {
        "strategy": "TEST_ENVIRONMENT_REVIEW",
        "priority": "HIGH",
        "action": (
            "Inspect test discovery and environment errors before attempting "
            "another repair."
        ),
        "retry_allowed": True,
        "max_attempts": 2,
    },
    "RUNTIME_ERROR": {
        "strategy": "RUNTIME_REPAIR",
        "priority": "HIGH",
        "action": (
            "Inspect the runtime traceback, identify the failing operation, "
            "generate a corrected patch, validate it, and rerun tests."
        ),
        "retry_allowed": True,
        "max_attempts": 3,
    },
}


def plan_recovery(failure: Dict) -> Dict:
    """
    Create a recovery plan from a classified failure.

    The planner is generic and relies only on failure metadata.
    """

    if not isinstance(failure, dict):
        raise TypeError("failure must be a dictionary.")

    failure_type = str(
        failure.get("type", "UNKNOWN")
    ).upper()

    severity = str(
        failure.get("severity", "MEDIUM")
    ).upper()

    confidence = float(
        failure.get("confidence", 0.0)
    )

    rule = RECOVERY_RULES.get(
        failure_type,
        {
            "strategy": "GENERAL_REANALYSIS",
            "priority": severity,
            "action": (
                "Re-analyze the failure, inspect the available evidence, "
                "generate a safe correction, validate it, and rerun tests."
            ),
            "retry_allowed": True,
            "max_attempts": 2,
        },
    )

    return {
        "failure_type": failure_type,
        "severity": severity,
        "failure_confidence": confidence,
        "strategy": rule["strategy"],
        "priority": rule["priority"],
        "action": rule["action"],
        "retry_allowed": rule["retry_allowed"],
        "max_attempts": rule["max_attempts"],
    }


def print_recovery_plan(plan: Dict) -> None:
    """
    Display a recovery plan in a human-readable format.
    """

    print("\n" + "=" * 50)
    print("       🔄 RECOVERY PLAN")
    print("=" * 50)

    print(f"\nFailure Type       : {plan['failure_type']}")
    print(f"Severity           : {plan['severity']}")
    print(
        f"Failure Confidence: "
        f"{plan['failure_confidence']:.2f}"
    )

    print(f"\nStrategy           : {plan['strategy']}")
    print(f"Priority           : {plan['priority']}")
    print(f"Retry Allowed      : {plan['retry_allowed']}")
    print(f"Max Attempts       : {plan['max_attempts']}")

    print("\nAction:")
    print(f"  {plan['action']}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    from backend.execution.failure.failure_classifier import (
        classify_failure
    )

    sample_output = (
        "FAILED test_calculator.py::test_divide "
        "- assert 20 == 5"
    )

    failure = classify_failure(sample_output)

    plan = plan_recovery(failure)

    print_recovery_plan(plan)