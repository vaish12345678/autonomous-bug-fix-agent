import json
from datetime import datetime
from pathlib import Path


# ============================================================
# HUMAN APPROVAL GATE
# ============================================================

APPROVAL_DIR = (
    Path(__file__).resolve().parents[2]
    / "evaluation"
    / "approvals"
)


# ============================================================
# BUILD APPROVAL REQUEST
# ============================================================

def create_approval_request(
    benchmark: str,
    issue: str,
    target_file: str,
    root_cause: str,
    correction: str,
    risk_level: str,
    risk_score: int,
    confidence: float,
    diff: str,
) -> dict:
    """
    Create a structured human approval request.

    This module does not decide whether a patch is correct.
    It presents the evidence collected by the agent and lets
    the human make the final approval decision.
    """

    return {
        "benchmark": benchmark,
        "issue": issue,
        "target_file": target_file,
        "root_cause": root_cause,
        "correction": correction,
        "risk": {
            "level": risk_level,
            "score": risk_score,
        },
        "confidence": confidence,
        "diff": diff,
        "created_at": datetime.now().isoformat(),
        "approved": None,
        "approval_reason": None,
    }


# ============================================================
# DISPLAY APPROVAL REQUEST
# ============================================================

def display_approval_request(
    request: dict,
) -> None:
    """
    Display the proposed patch and supporting evidence.
    """

    print("\n" + "=" * 65)
    print("             👤 HUMAN PATCH APPROVAL")
    print("=" * 65)

    print("\n---------- BENCHMARK ----------")
    print(
        f"Benchmark       : "
        f"{request['benchmark']}"
    )

    print("\n---------- ISSUE ----------")
    print(request["issue"])

    print("\n---------- TARGET ----------")
    print(
        f"Target File     : "
        f"{request['target_file']}"
    )

    print("\n---------- ROOT CAUSE ----------")
    print(request["root_cause"])

    print("\n---------- CORRECTION ----------")
    print(request["correction"])

    print("\n---------- RISK ----------")
    print(
        f"Risk Level      : "
        f"{request['risk']['level']}"
    )

    print(
        f"Risk Score      : "
        f"{request['risk']['score']}/100"
    )

    print("\n---------- CONFIDENCE ----------")
    print(
        f"Confidence      : "
        f"{request['confidence']:.2f}/100"
    )

    print("\n---------- PROPOSED DIFF ----------")

    diff = request.get("diff", "")

    if diff:
        print(diff)
    else:
        print("No diff available.")

    print("\n" + "-" * 65)
    print("The AI has proposed this patch.")
    print("Review the evidence before approving it.")
    print("-" * 65)


# ============================================================
# ASK HUMAN FOR APPROVAL
# ============================================================

def request_human_approval(
    request: dict,
) -> dict:
    """
    Ask the human whether the proposed patch should proceed.

    The patch is NOT modified or applied by this module.
    """

    display_approval_request(request)

    while True:

        choice = input(
            "\nApprove this patch? "
            "[y]es / [n]o: "
        ).strip().lower()

        if choice in {"y", "yes"}:

            request["approved"] = True
            request["approval_reason"] = (
                "Human approved the proposed patch."
            )

            print(
                "\n✅ PATCH APPROVED BY HUMAN"
            )

            return request

        if choice in {"n", "no"}:

            request["approved"] = False
            request["approval_reason"] = (
                "Human rejected the proposed patch."
            )

            print(
                "\n❌ PATCH REJECTED BY HUMAN"
            )

            return request

        print(
            "Invalid choice. Enter 'y' or 'n'."
        )


# ============================================================
# SAVE APPROVAL DECISION
# ============================================================

def save_approval_decision(
    request: dict,
) -> Path:
    """
    Persist the human approval decision for auditing.
    """

    APPROVAL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    benchmark = request.get(
        "benchmark",
        "unknown",
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    output_path = (
        APPROVAL_DIR
        / f"{benchmark}_{timestamp}.json"
    )

    output_path.write_text(
        json.dumps(
            request,
            indent=4,
        ),
        encoding="utf-8",
    )

    return output_path


# ============================================================
# COMPLETE APPROVAL FLOW
# ============================================================

def run_approval_gate(
    benchmark: str,
    issue: str,
    target_file: str,
    root_cause: str,
    correction: str,
    risk_level: str,
    risk_score: int,
    confidence: float,
    diff: str,
) -> bool:
    """
    Execute the complete human approval workflow.

    Returns:
        True  -> human approved
        False -> human rejected
    """

    request = create_approval_request(
        benchmark=benchmark,
        issue=issue,
        target_file=target_file,
        root_cause=root_cause,
        correction=correction,
        risk_level=risk_level,
        risk_score=risk_score,
        confidence=confidence,
        diff=diff,
    )

    request = request_human_approval(
        request
    )

    output_path = save_approval_decision(
        request
    )

    print(
        f"\n✓ Approval decision saved to:"
    )

    print(output_path)

    print(
        "\n" + "=" * 65
    )

    if request["approved"]:
        print(
            "🚀 DECISION: PROCEED WITH PATCH"
        )
    else:
        print(
            "🛑 DECISION: BLOCK PATCH"
        )

    print(
        "=" * 65
    )

    return bool(
        request["approved"]
    )


# ============================================================
# STANDALONE DEMO
# ============================================================

def main():
    """
    Demonstrate the human approval gate independently.
    """

    print(
        "\n" + "=" * 65
    )

    print(
        "        👤 HUMAN APPROVAL GATE DEMO"
    )

    print(
        "=" * 65
    )

    approved = run_approval_gate(
        benchmark="demo",
        issue=(
            "divide() returns an incorrect result."
        ),
        target_file="calculator.py",
        root_cause=(
            "The implementation performs "
            "the wrong arithmetic operation."
        ),
        correction=(
            "Replace multiplication with division."
        ),
        risk_level="LOW",
        risk_score=0,
        confidence=100.0,
        diff=(
            "- return a * b\n"
            "+ return a / b"
        ),
    )

    print(
        f"\nFinal approval result: "
        f"{approved}"
    )


if __name__ == "__main__":
    main()