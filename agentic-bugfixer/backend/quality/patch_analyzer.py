import ast
from dataclasses import dataclass
from typing import List


@dataclass
class PatchAnalysis:
    risk_level: str
    score: int
    warnings: List[str]
    changes: List[str]


def _parse_python(code: str):
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _count_nodes(tree) -> int:
    if tree is None:
        return 0

    return sum(1 for _ in ast.walk(tree))


def _find_dangerous_calls(tree) -> List[str]:
    warnings = []

    if tree is None:
        return warnings

    dangerous_functions = {
        "eval",
        "exec",
        "__import__",
    }

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in dangerous_functions:

                    warnings.append(
                        f"Dangerous function used: "
                        f"{node.func.id}"
                    )

    return warnings


def _find_file_operations(tree) -> List[str]:
    warnings = []

    if tree is None:
        return warnings

    file_operations = {
        "open",
        "remove",
        "unlink",
        "rmdir",
    }

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in file_operations:

                    warnings.append(
                        f"File operation detected: "
                        f"{node.func.id}"
                    )

    return warnings


def _compare_functions(
    old_tree,
    new_tree
) -> List[str]:

    changes = []

    if old_tree is None or new_tree is None:
        return changes

    old_functions = {
        node.name
        for node in ast.walk(old_tree)
        if isinstance(node, ast.FunctionDef)
    }

    new_functions = {
        node.name
        for node in ast.walk(new_tree)
        if isinstance(node, ast.FunctionDef)
    }

    for function_name in sorted(
        new_functions - old_functions
    ):
        changes.append(
            f"Function added: {function_name}"
        )

    for function_name in sorted(
        old_functions - new_functions
    ):
        changes.append(
            f"Function removed: {function_name}"
        )

    return changes


def analyze_patch(
    original_code: str,
    patched_code: str
) -> PatchAnalysis:

    """
    Analyze a generated Python patch and estimate
    its structural and operational risk.

    This module does not modify files.
    """

    warnings = []
    changes = []

    old_tree = _parse_python(
        original_code
    )

    new_tree = _parse_python(
        patched_code
    )

    # --------------------------------------------------------
    # Syntax safety
    # --------------------------------------------------------

    if new_tree is None:

        return PatchAnalysis(
            risk_level="CRITICAL",
            score=100,
            warnings=[
                "Patched code contains invalid "
                "Python syntax."
            ],
            changes=[]
        )

    # --------------------------------------------------------
    # Structural analysis
    # --------------------------------------------------------

    old_node_count = _count_nodes(
        old_tree
    )

    new_node_count = _count_nodes(
        new_tree
    )

    changes.extend(
        _compare_functions(
            old_tree,
            new_tree
        )
    )

    # --------------------------------------------------------
    # Dangerous operations
    # --------------------------------------------------------

    warnings.extend(
        _find_dangerous_calls(
            new_tree
        )
    )

    warnings.extend(
        _find_file_operations(
            new_tree
        )
    )

    score = 0

    # --------------------------------------------------------
    # Structural change score
    # --------------------------------------------------------

    if old_node_count > 0:

        difference = abs(
            new_node_count -
            old_node_count
        )

        change_ratio = (
            difference /
            old_node_count
        )

        if change_ratio > 0.50:

            score += 40

            warnings.append(
                "Large structural change detected."
            )

        elif change_ratio > 0.25:

            score += 20

            warnings.append(
                "Moderate structural change detected."
            )

    # --------------------------------------------------------
    # Dangerous function score
    # --------------------------------------------------------

    for warning in warnings:

        if warning.startswith(
            "Dangerous function"
        ):

            score += 30

        elif warning.startswith(
            "File operation"
        ):

            score += 10

    # --------------------------------------------------------
    # Added functions
    # --------------------------------------------------------

    added_functions = [
        change
        for change in changes
        if change.startswith(
            "Function added:"
        )
    ]

    score += min(
        len(added_functions) * 5,
        20
    )

    score = min(
        score,
        100
    )

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    if score >= 70:

        risk_level = "CRITICAL"

    elif score >= 40:

        risk_level = "HIGH"

    elif score >= 20:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    return PatchAnalysis(
        risk_level=risk_level,
        score=score,
        warnings=warnings,
        changes=changes
    )


def print_patch_analysis(
    analysis: PatchAnalysis
):

    print(
        "\n========== PATCH QUALITY ANALYSIS ==========\n"
    )

    print(
        f"Risk Level : {analysis.risk_level}"
    )

    print(
        f"Risk Score : {analysis.score}/100"
    )

    if analysis.changes:

        print(
            "\nStructural Changes:"
        )

        for change in analysis.changes:

            print(
                f"  • {change}"
            )

    if analysis.warnings:

        print(
            "\nWarnings:"
        )

        for warning in analysis.warnings:

            print(
                f"  ⚠ {warning}"
            )

    else:

        print(
            "\n✓ No suspicious operations detected."
        )

    print(
        "\n============================================"
    )


if __name__ == "__main__":

    original = """
def add(a, b):
    return a + b
"""

    patched = """
def add(a, b):
    return a - b
"""

    result = analyze_patch(
        original,
        patched
    )

    print_patch_analysis(
        result
    )