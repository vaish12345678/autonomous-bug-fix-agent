import re


# ============================================================
# FAILURE CLASSIFICATION
# ============================================================

FAILURE_PATTERNS = [
    {
        "type": "SYNTAX_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"SyntaxError",
            r"IndentationError",
            r"TabError",
        ],
        "reason": (
            "The test execution encountered invalid "
            "source-code syntax."
        ),
    },
    {
        "type": "IMPORT_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"ModuleNotFoundError",
            r"ImportError",
        ],
        "reason": (
            "A required module or dependency could "
            "not be imported."
        ),
    },
    {
        "type": "ASSERTION_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"AssertionError",
            r"assert .*==",
            r"assert .*!=",
            r"assert .*<",
            r"assert .*>",
        ],
        "reason": (
            "A test assertion failed because the "
            "actual behavior differs from the expected behavior."
        ),
    },
    {
        "type": "TYPE_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"TypeError",
        ],
        "reason": (
            "The program performed an operation using "
            "an incompatible type."
        ),
    },
    {
        "type": "NAME_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"NameError",
        ],
        "reason": (
            "The program referenced a name that is "
            "not defined."
        ),
    },
    {
        "type": "ATTRIBUTE_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"AttributeError",
        ],
        "reason": (
            "The program attempted to access an "
            "attribute that does not exist."
        ),
    },
    {
        "type": "KEY_ERROR",
        "severity": "MEDIUM",
        "patterns": [
            r"KeyError",
        ],
        "reason": (
            "The program attempted to access a "
            "missing dictionary key."
        ),
    },
    {
        "type": "INDEX_ERROR",
        "severity": "MEDIUM",
        "patterns": [
            r"IndexError",
        ],
        "reason": (
            "The program attempted to access an "
            "invalid sequence index."
        ),
    },
    {
        "type": "TIMEOUT",
        "severity": "CRITICAL",
        "patterns": [
            r"timed out",
            r"TimeoutExpired",
            r"TIMEOUT",
        ],
        "reason": (
            "Test execution exceeded the allowed "
            "time limit."
        ),
    },
    {
        "type": "COMMAND_ERROR",
        "severity": "HIGH",
        "patterns": [
            r"command not found",
            r"not recognized as an internal or external command",
            r"COMMAND_NOT_FOUND",
        ],
        "reason": (
            "The detected test command could not "
            "be executed."
        ),
    },
]


# ============================================================
# CLASSIFY FAILURE
# ============================================================

def classify_failure(
    test_output: str,
) -> dict:
    """
    Classify a test failure using the execution output.

    This function does not know anything about individual
    benchmarks or expected solutions.
    """

    if not test_output:
        return {
            "type": "UNKNOWN",
            "severity": "MEDIUM",
            "reason": "No test output was available.",
            "matched_pattern": None,
            "confidence": 0.0,
        }

    output = str(test_output)

    for failure in FAILURE_PATTERNS:

        for pattern in failure["patterns"]:

            match = re.search(
                pattern,
                output,
                flags=re.IGNORECASE,
            )

            if match:

                return {
                    "type": failure["type"],
                    "severity": failure["severity"],
                    "reason": failure["reason"],
                    "matched_pattern": match.group(0),
                    "confidence": 1.0,
                }

    # --------------------------------------------------------
    # Generic test failure detection
    # --------------------------------------------------------

    generic_patterns = [
        r"\bFAILED\b",
        r"\bfailed\b",
        r"FAILURES",
        r"tests failed",
    ]

    for pattern in generic_patterns:

        match = re.search(
            pattern,
            output,
            flags=re.IGNORECASE,
        )

        if match:

            return {
                "type": "TEST_FAILURE",
                "severity": "HIGH",
                "reason": (
                    "The test suite reported a failure, "
                    "but the specific failure type could "
                    "not be determined."
                ),
                "matched_pattern": match.group(0),
                "confidence": 0.7,
            }

    return {
        "type": "UNKNOWN",
        "severity": "MEDIUM",
        "reason": (
            "The test execution failed, but no known "
            "failure pattern was detected."
        ),
        "matched_pattern": None,
        "confidence": 0.3,
    }


# ============================================================
# DISPLAY FAILURE
# ============================================================

def print_failure_analysis(
    result: dict,
) -> None:

    print(
        "\n========== FAILURE ANALYSIS ==========\n"
    )

    print(
        f"Failure Type : {result['type']}"
    )

    print(
        f"Severity     : {result['severity']}"
    )

    print(
        f"Confidence   : "
        f"{result['confidence'] * 100:.1f}%"
    )

    print(
        f"Reason       : {result['reason']}"
    )

    if result["matched_pattern"]:

        print(
            f"Matched     : "
            f"{result['matched_pattern']}"
        )

    print(
        "\n" + "=" * 44
    )


# ============================================================
# STANDALONE DEMO
# ============================================================

def main():

    print(
        "\n" + "=" * 50
    )

    print(
        "       🧠 FAILURE CLASSIFIER"
    )

    print(
        "=" * 50
    )

    samples = [
        (
            "Assertion example",
            """
            FAILED test_calculator.py
            AssertionError: assert 20 == 5
            """,
        ),
        (
            "Syntax example",
            """
            SyntaxError: invalid syntax
            """,
        ),
        (
            "Import example",
            """
            ModuleNotFoundError:
            No module named 'example'
            """,
        ),
        (
            "Type example",
            """
            TypeError: unsupported operand type
            """,
        ),
        (
            "Timeout example",
            """
            Tests timed out.
            """,
        ),
    ]

    for name, output in samples:

        print(
            f"\n---------- {name} ----------"
        )

        result = classify_failure(
            output
        )

        print_failure_analysis(
            result
        )


if __name__ == "__main__":
    main()