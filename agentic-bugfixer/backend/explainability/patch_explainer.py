import difflib
import json
import sys
from datetime import datetime
from pathlib import Path


# ============================================================
# PATCH EXPLAINABILITY ENGINE
# ============================================================

def _safe_text(value):
    """
    Convert runtime values into safe displayable text.
    """

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# CODE CHANGE EXTRACTION
# ============================================================

def extract_code_changes(
    original_code: str,
    patched_code: str
) -> dict:
    """
    Compare original and patched source code.

    This function is completely generic and does not know
    anything about benchmarks, filenames, or bug types.
    """

    original_lines = _safe_text(
        original_code
    ).splitlines()

    patched_lines = _safe_text(
        patched_code
    ).splitlines()

    diff = list(
        difflib.unified_diff(
            original_lines,
            patched_lines,
            fromfile="original",
            tofile="patched",
            lineterm=""
        )
    )

    additions = []
    removals = []

    for line in diff:

        if line.startswith("+++"):
            continue

        if line.startswith("---"):
            continue

        if line.startswith("@@"):
            continue

        if line.startswith("+"):
            additions.append(
                line[1:]
            )

        elif line.startswith("-"):
            removals.append(
                line[1:]
            )

    return {
        "additions": additions,
        "removals": removals,
        "diff": diff,
        "lines_added": len(additions),
        "lines_removed": len(removals)
    }


# ============================================================
# TEST RESULT INTERPRETATION
# ============================================================

def determine_validation_status(
    test_result=None,
    regression_result=None,
    acceptance_result=None
) -> dict:
    """
    Convert validation results into a generic explanation.
    """

    validation = {}

    if isinstance(test_result, dict):
        validation["tests"] = (
            "PASS"
            if test_result.get("passed") is True
            else "FAIL"
        )

    elif test_result is not None:
        validation["tests"] = (
            "PASS"
            if bool(test_result)
            else "FAIL"
        )

    else:
        validation["tests"] = "NOT PROVIDED"

    if isinstance(regression_result, dict):

        regression_passed = (
            regression_result.get("passed")
            if "passed" in regression_result
            else regression_result.get("safe")
        )

        validation["regression"] = (
            "PASS"
            if regression_passed is True
            else "FAIL"
        )

    elif regression_result is not None:

        validation["regression"] = (
            "PASS"
            if bool(regression_result)
            else "FAIL"
        )

    else:
        validation["regression"] = "NOT PROVIDED"

    if isinstance(acceptance_result, dict):

        accepted = (
            acceptance_result.get("accepted")
            if "accepted" in acceptance_result
            else acceptance_result.get("passed")
        )

        validation["acceptance"] = (
            "ACCEPTED"
            if accepted is True
            else "REJECTED"
        )

    elif acceptance_result is not None:

        validation["acceptance"] = (
            "ACCEPTED"
            if bool(acceptance_result)
            else "REJECTED"
        )

    else:
        validation["acceptance"] = "NOT PROVIDED"

    return validation


# ============================================================
# PATCH EXPLANATION
# ============================================================

def explain_patch(
    issue: str,
    root_cause: str,
    correction: str,
    target_file: str,
    original_code: str,
    patched_code: str,
    test_result=None,
    regression_result=None,
    acceptance_result=None,
    risk_result=None,
    confidence_result=None
) -> dict:
    """
    Build a complete, generic explanation of a source-code patch.

    No benchmark-specific information is used.
    """

    changes = extract_code_changes(
        original_code,
        patched_code
    )

    validation = determine_validation_status(
        test_result,
        regression_result,
        acceptance_result
    )

    if isinstance(risk_result, dict):

        risk_level = risk_result.get(
            "risk_level",
            risk_result.get(
                "level",
                "UNKNOWN"
            )
        )

        risk_score = risk_result.get(
            "risk_score",
            risk_result.get(
                "score",
                None
            )
        )

    else:

        risk_level = "NOT PROVIDED"
        risk_score = None

    if isinstance(confidence_result, dict):

        confidence_score = confidence_result.get(
            "confidence_score",
            confidence_result.get(
                "score",
                None
            )
        )

        confidence_level = confidence_result.get(
            "confidence_level",
            confidence_result.get(
                "level",
                "UNKNOWN"
            )
        )

    else:

        confidence_score = None
        confidence_level = "NOT PROVIDED"

    if (
        validation.get("tests") == "PASS"
        and validation.get("regression") == "PASS"
        and validation.get("acceptance") == "ACCEPTED"
    ):
        final_decision = "PATCH VERIFIED AND ACCEPTED"

    elif validation.get("tests") == "FAIL":
        final_decision = "PATCH FAILED VALIDATION"

    elif validation.get("acceptance") == "REJECTED":
        final_decision = "PATCH REJECTED"

    else:
        final_decision = "PATCH REQUIRES FURTHER VALIDATION"

    return {
        "timestamp": datetime.now().isoformat(),
        "target_file": _safe_text(target_file),
        "issue": _safe_text(issue),
        "root_cause": _safe_text(root_cause),
        "correction": _safe_text(correction),

        "changes": {
            "lines_added": changes["lines_added"],
            "lines_removed": changes["lines_removed"],
            "additions": changes["additions"],
            "removals": changes["removals"]
        },

        "validation": validation,

        "risk": {
            "level": risk_level,
            "score": risk_score
        },

        "confidence": {
            "score": confidence_score,
            "level": confidence_level
        },

        "final_decision": final_decision
    }


# ============================================================
# TERMINAL REPORT
# ============================================================

def print_explanation(result: dict) -> None:

    changes = result["changes"]
    validation = result["validation"]
    risk = result["risk"]
    confidence = result["confidence"]

    print()
    print("=" * 65)
    print("              🔍 PATCH EXPLAINABILITY")
    print("=" * 65)

    print()
    print("========== WHY WAS THIS FILE CHANGED? ==========")
    print()
    print(
        f"Target File : {result['target_file']}"
    )

    print()
    print("========== REPORTED ISSUE ==========")
    print()
    print(
        result["issue"]
    )

    print()
    print("========== ROOT CAUSE ==========")
    print()
    print(
        result["root_cause"]
    )

    print()
    print("========== CORRECTION ==========")
    print()
    print(
        result["correction"]
    )

    print()
    print("========== CODE CHANGES ==========")
    print()

    print(
        f"Lines Added   : {changes['lines_added']}"
    )

    print(
        f"Lines Removed : {changes['lines_removed']}"
    )

    if changes["removals"]:

        print()
        print("Removed:")

        for line in changes["removals"]:
            print(
                f"  - {line}"
            )

    if changes["additions"]:

        print()
        print("Added:")

        for line in changes["additions"]:
            print(
                f"  + {line}"
            )

    print()
    print("========== VALIDATION ==========")
    print()

    print(
        f"Syntax      : NOT PROVIDED"
    )

    print(
        f"Tests       : {validation['tests']}"
    )

    print(
        f"Regression  : {validation['regression']}"
    )

    print(
        f"Acceptance  : {validation['acceptance']}"
    )

    print()
    print("========== SAFETY ==========")
    print()

    print(
        f"Risk Level  : {risk['level']}"
    )

    if risk["score"] is not None:

        print(
            f"Risk Score  : {risk['score']}/100"
        )

    print()
    print("========== CONFIDENCE ==========")
    print()

    if confidence["score"] is not None:

        print(
            f"Confidence  : {confidence['score']}/100"
        )

    else:

        print(
            "Confidence  : NOT PROVIDED"
        )

    print(
        f"Level       : {confidence['level']}"
    )

    print()
    print("========== FINAL DECISION ==========")
    print()

    if result["final_decision"] == (
        "PATCH VERIFIED AND ACCEPTED"
    ):

        print(
            "🎉 " + result["final_decision"]
        )

    else:

        print(
            "⚠ " + result["final_decision"]
        )

    print()
    print("=" * 65)


# ============================================================
# SAVE REPORT
# ============================================================

def save_explanation(
    result: dict,
    output_directory: str = "evaluation/explanations"
) -> Path:
    """
    Save the explanation as JSON.
    """

    directory = Path(
        output_directory
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"patch_explanation_{timestamp}.json"
    )

    output_path = directory / filename

    output_path.write_text(
        json.dumps(
            result,
            indent=4
        ),
        encoding="utf-8"
    )

    return output_path


# ============================================================
# DEMO
# ============================================================

def demo():

    original_code = """def calculate(a, b):
    return a * b
"""

    patched_code = """def calculate(a, b):
    return a / b
"""

    result = explain_patch(
        issue="The calculation returns an incorrect result.",
        root_cause=(
            "The implementation uses the wrong arithmetic operation."
        ),
        correction=(
            "Use division instead of multiplication."
        ),
        target_file="example.py",
        original_code=original_code,
        patched_code=patched_code,
        test_result={
            "passed": True
        },
        regression_result={
            "passed": True
        },
        acceptance_result={
            "accepted": True
        },
        risk_result={
            "risk_level": "LOW",
            "risk_score": 0
        },
        confidence_result={
            "confidence_score": 100,
            "confidence_level": "VERY HIGH"
        }
    )

    print_explanation(
        result
    )

    output = save_explanation(
        result
    )

    print()
    print(
        f"✓ Explanation saved to:\n{output}"
    )


# ============================================================
# COMMAND LINE
# ============================================================

def main():

    demo()


if __name__ == "__main__":
    main()