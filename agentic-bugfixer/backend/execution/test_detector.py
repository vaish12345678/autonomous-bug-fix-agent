import json
import shutil
from pathlib import Path


# ============================================================
# INTELLIGENT TEST COMMAND DETECTOR
# ============================================================

SUPPORTED_TEST_COMMANDS = {
    "pytest": ["pytest", "-q"],
    "unittest": ["python", "-m", "unittest"],
    "npm": ["npm", "test"],
    "maven": ["mvn", "test"],
    "gradle": ["gradle", "test"],
}


# ============================================================
# PROJECT DETECTION
# ============================================================

def detect_project_type(repo_path: str) -> str:
    """
    Detect the repository's primary project type using
    project configuration files and source files.
    """

    root = Path(repo_path).resolve()

    if not root.is_dir():
        raise FileNotFoundError(
            f"Repository not found: {repo_path}"
        )

    # Python
    python_markers = [
        "pyproject.toml",
        "pytest.ini",
        "setup.py",
        "requirements.txt",
        "Pipfile",
    ]

    if any(
        (root / marker).exists()
        for marker in python_markers
    ):
        return "python"

    if list(root.rglob("*.py")):
        return "python"

    # Node.js
    if (root / "package.json").exists():
        return "node"

    if list(root.rglob("*.js")) or list(
        root.rglob("*.ts")
    ):
        return "node"

    # Maven
    if (root / "pom.xml").exists():
        return "maven"

    # Gradle
    if (
        (root / "build.gradle").exists()
        or (root / "build.gradle.kts").exists()
    ):
        return "gradle"

    # Java fallback
    if list(root.rglob("*.java")):
        return "java"

    return "unknown"


# ============================================================
# PYTHON TEST FRAMEWORK DETECTION
# ============================================================

def detect_python_framework(
    repo_path: str,
) -> str | None:
    """
    Detect the available Python test framework.
    """

    root = Path(repo_path).resolve()

    if shutil.which("pytest"):
        pytest_files = list(
            root.rglob("test_*.py")
        )

        if pytest_files:
            return "pytest"

    unittest_files = list(
        root.rglob("test_*.py")
    )

    if unittest_files:
        return "unittest"

    return None


# ============================================================
# NODE TEST COMMAND DETECTION
# ============================================================

def detect_node_test_command(
    repo_path: str,
) -> list[str] | None:
    """
    Inspect package.json and determine the project's
    configured test command.
    """

    root = Path(repo_path).resolve()

    package_file = root / "package.json"

    if not package_file.is_file():
        return None

    try:
        package_data = json.loads(
            package_file.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None

    scripts = package_data.get(
        "scripts",
        {},
    )

    test_script = scripts.get("test")

    if test_script:
        return [
            "npm",
            "test",
        ]

    return None


# ============================================================
# TEST COMMAND DETECTION
# ============================================================

def detect_test_command(
    repo_path: str,
) -> dict:
    """
    Automatically determine the most appropriate test
    command for the repository.

    No benchmark-specific knowledge is used.
    """

    project_type = detect_project_type(
        repo_path
    )

    root = Path(repo_path).resolve()

    command = None
    framework = None
    reason = None

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    if project_type == "python":

        framework = detect_python_framework(
            repo_path
        )

        if framework == "pytest":

            command = SUPPORTED_TEST_COMMANDS[
                "pytest"
            ]

            reason = (
                "pytest test files detected."
            )

        elif framework == "unittest":

            command = SUPPORTED_TEST_COMMANDS[
                "unittest"
            ]

            reason = (
                "Python unittest-compatible "
                "test files detected."
            )

    # --------------------------------------------------------
    # NODE
    # --------------------------------------------------------

    elif project_type == "node":

        command = detect_node_test_command(
            repo_path
        )

        if command:

            framework = "npm"

            reason = (
                "package.json contains a test script."
            )

    # --------------------------------------------------------
    # MAVEN
    # --------------------------------------------------------

    elif project_type == "maven":

        if shutil.which("mvn"):

            command = SUPPORTED_TEST_COMMANDS[
                "maven"
            ]

            framework = "maven"

            reason = (
                "pom.xml detected and Maven "
                "is available."
            )

    # --------------------------------------------------------
    # GRADLE
    # --------------------------------------------------------

    elif project_type == "gradle":

        if shutil.which("gradle"):

            command = SUPPORTED_TEST_COMMANDS[
                "gradle"
            ]

            framework = "gradle"

            reason = (
                "Gradle build configuration detected."
            )

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    if command is None:

        return {
            "detected": False,
            "project_type": project_type,
            "framework": framework,
            "command": None,
            "reason": (
                "No supported test framework "
                "was detected."
            ),
        }

    return {
        "detected": True,
        "project_type": project_type,
        "framework": framework,
        "command": command,
        "reason": reason,
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def main():

    import sys

    if len(sys.argv) > 1:

        repository = sys.argv[1]

    else:

        repository = (
            Path(__file__).resolve()
            .parents[2]
            / "benchmarks"
            / "bug_01"
            / "repo"
        )

    print(
        "\n" + "=" * 60
    )

    print(
        "       🧠 INTELLIGENT TEST DETECTION"
    )

    print(
        "=" * 60
    )

    print(
        f"\nRepository:"
    )

    print(
        repository
    )

    result = detect_test_command(
        str(repository)
    )

    print(
        "\n========== DETECTION RESULT ==========\n"
    )

    print(
        f"Project Type : "
        f"{result['project_type']}"
    )

    print(
        f"Framework    : "
        f"{result['framework'] or 'NONE'}"
    )

    if result["command"]:

        print(
            "Test Command : "
            + " ".join(
                result["command"]
            )
        )

    else:

        print(
            "Test Command : NONE"
        )

    print(
        f"Detected     : "
        f"{'YES' if result['detected'] else 'NO'}"
    )

    print(
        f"Reason       : "
        f"{result['reason']}"
    )

    print(
        "\n" + "=" * 60
    )


if __name__ == "__main__":
    main()