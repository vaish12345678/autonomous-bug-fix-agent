from dataclasses import dataclass

from backend.quality.patch_analyzer import (
    PatchAnalysis,
    analyze_patch,
)


@dataclass
class GateDecision:
    accepted: bool
    reason: str
    risk_level: str
    risk_score: int


# ============================================================
# ACCEPTANCE POLICY
# ============================================================

MAX_ACCEPTABLE_RISK = 40


# ============================================================
# EVALUATE PATCH
# ============================================================

def evaluate_patch(
    original_code: str,
    patched_code: str
) -> GateDecision:

    """
    Decide whether a generated patch is safe enough
    to continue through the autonomous repair pipeline.

    This function does not modify any files.
    """

    analysis: PatchAnalysis = analyze_patch(
        original_code,
        patched_code
    )

    # --------------------------------------------------------
    # CRITICAL RISK
    # --------------------------------------------------------

    if analysis.risk_level == "CRITICAL":

        return GateDecision(
            accepted=False,
            reason=(
                "Patch rejected because it contains "
                "critical-risk changes."
            ),
            risk_level=analysis.risk_level,
            risk_score=analysis.score
        )

    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if analysis.risk_level == "HIGH":

        return GateDecision(
            accepted=False,
            reason=(
                "Patch rejected because the detected "
                "risk is too high."
            ),
            risk_level=analysis.risk_level,
            risk_score=analysis.score
        )

    # --------------------------------------------------------
    # SCORE LIMIT
    # --------------------------------------------------------

    if analysis.score > MAX_ACCEPTABLE_RISK:

        return GateDecision(
            accepted=False,
            reason=(
                f"Patch risk score "
                f"{analysis.score}/100 exceeds "
                f"the maximum accepted risk of "
                f"{MAX_ACCEPTABLE_RISK}."
            ),
            risk_level=analysis.risk_level,
            risk_score=analysis.score
        )

    # --------------------------------------------------------
    # ACCEPT
    # --------------------------------------------------------

    return GateDecision(
        accepted=True,
        reason=(
            "Patch passed the quality and risk "
            "acceptance gate."
        ),
        risk_level=analysis.risk_level,
        risk_score=analysis.score
    )


# ============================================================
# PRINT DECISION
# ============================================================

def print_gate_decision(
    decision: GateDecision
):

    print(
        "\n========== PATCH ACCEPTANCE GATE ==========\n"
    )

    if decision.accepted:

        print(
            "✅ PATCH ACCEPTED"
        )

    else:

        print(
            "❌ PATCH REJECTED"
        )

    print(
        f"Risk Level : {decision.risk_level}"
    )

    print(
        f"Risk Score : {decision.risk_score}/100"
    )

    print(
        f"Reason     : {decision.reason}"
    )

    print(
        "\n============================================"
    )


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    original = """
def add(a, b):
    return a + b
"""

    safe_patch = """
def add(a, b):
    return a - b
"""

    decision = evaluate_patch(
        original,
        safe_patch
    )

    print_gate_decision(
        decision
    )