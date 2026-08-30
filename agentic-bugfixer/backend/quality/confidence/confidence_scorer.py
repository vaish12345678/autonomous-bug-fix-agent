from dataclasses import dataclass


# ============================================================
# CONFIDENCE RESULT
# ============================================================

@dataclass
class ConfidenceResult:
    score: float
    level: str
    reasons: list[str]


# ============================================================
# CONFIDENCE SCORER
# ============================================================

def calculate_confidence(
    analysis_success: bool,
    syntax_valid: bool,
    patch_applied: bool,
    tests_passed: bool,
    patch_accepted: bool,
    rollback_required: bool = False
) -> ConfidenceResult:
    """
    Calculate confidence in an autonomous bug fix.

    The score is based on independent verification signals.
    """

    score = 0.0
    reasons = []

    # --------------------------------------------------------
    # BUG ANALYSIS
    # --------------------------------------------------------

    if analysis_success:
        score += 20
        reasons.append(
            "Root-cause analysis completed successfully."
        )

    # --------------------------------------------------------
    # SYNTAX VALIDATION
    # --------------------------------------------------------

    if syntax_valid:
        score += 15
        reasons.append(
            "Generated patch passed syntax validation."
        )

    # --------------------------------------------------------
    # PATCH APPLICATION
    # --------------------------------------------------------

    if patch_applied:
        score += 10
        reasons.append(
            "Patch was applied successfully."
        )

    # --------------------------------------------------------
    # TEST VERIFICATION
    # --------------------------------------------------------

    if tests_passed:
        score += 35
        reasons.append(
            "All repository tests passed."
        )

    # --------------------------------------------------------
    # ACCEPTANCE GATE
    # --------------------------------------------------------

    if patch_accepted:
        score += 20
        reasons.append(
            "Patch passed the quality acceptance gate."
        )

    # --------------------------------------------------------
    # ROLLBACK PENALTY
    # --------------------------------------------------------

    if rollback_required:
        score -= 25
        reasons.append(
            "Rollback was required after a failed patch."
        )

    # --------------------------------------------------------
    # BOUND SCORE
    # --------------------------------------------------------

    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )

    # --------------------------------------------------------
    # CONFIDENCE LEVEL
    # --------------------------------------------------------

    if score >= 85:
        level = "VERY HIGH"

    elif score >= 70:
        level = "HIGH"

    elif score >= 50:
        level = "MEDIUM"

    elif score >= 30:
        level = "LOW"

    else:
        level = "VERY LOW"

    return ConfidenceResult(
        score=round(score, 2),
        level=level,
        reasons=reasons
    )


# ============================================================
# DISPLAY
# ============================================================

def print_confidence(result: ConfidenceResult):

    print()
    print("=" * 50)
    print("       PATCH CONFIDENCE SCORE")
    print("=" * 50)

    print()
    print(
        f"Confidence Score : {result.score:.2f}/100"
    )

    print(
        f"Confidence Level : {result.level}"
    )

    print()
    print("Evidence:")

    if result.reasons:

        for reason in result.reasons:
            print(
                f"  ✓ {reason}"
            )

    else:
        print(
            "  No positive verification signals."
        )

    print()
    print("=" * 50)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    result = calculate_confidence(
        analysis_success=True,
        syntax_valid=True,
        patch_applied=True,
        tests_passed=True,
        patch_accepted=True,
        rollback_required=False
    )

    print_confidence(result)