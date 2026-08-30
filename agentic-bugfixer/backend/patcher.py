import subprocess
from pathlib import Path


# ============================================================
# TARGET FILE VALIDATION
# ============================================================

def validate_target_file(
    repo_path: str,
    file_name: str
) -> Path:
    """
    Validate that the target file exists inside the repository
    and is not a test file.
    """

    root = Path(repo_path).resolve()
    target = (root / file_name).resolve()

    # Prevent path traversal
    if root not in target.parents:
        raise ValueError(
            "Target file is outside repository."
        )

    # Target must exist
    if not target.is_file():
        raise FileNotFoundError(
            f"Target file does not exist: {file_name}"
        )

    filename = target.name.lower()

    # Never modify test files
    if filename.startswith("test_"):
        raise ValueError(
            "Agent is not allowed to modify test files."
        )

    if filename.endswith("_test.py"):
        raise ValueError(
            "Agent is not allowed to modify test files."
        )

    # Never modify pytest configuration
    if filename == "conftest.py":
        raise ValueError(
            "Agent is not allowed to modify test configuration."
        )

    return target


# ============================================================
# BACKUP
# ============================================================

def create_backup(
    repo_path: str,
    file_name: str
) -> Path:
    """
    Create a backup before modifying a source file.
    """

    target = validate_target_file(
        repo_path,
        file_name
    )

    backup = target.with_suffix(
        target.suffix + ".bak"
    )

    backup.write_text(
        target.read_text(
            encoding="utf-8"
        ),
        encoding="utf-8"
    )

    return backup


# ============================================================
# APPLY FIX
# ============================================================

def apply_fix(
    repo_path: str,
    file_name: str,
    fixed_code: str
) -> None:
    """
    Apply AI-generated source code to the target file.
    """

    if not fixed_code.strip():
        raise ValueError(
            "Cannot apply an empty fix."
        )

    target = validate_target_file(
        repo_path,
        file_name
    )

    target.write_text(
        fixed_code.rstrip() + "\n",
        encoding="utf-8"
    )


# ============================================================
# RESTORE BACKUP
# ============================================================

def restore_backup(
    repo_path: str,
    file_name: str
) -> None:
    """
    Restore the original source file from its backup.
    """

    target = validate_target_file(
        repo_path,
        file_name
    )

    backup = target.with_suffix(
        target.suffix + ".bak"
    )

    if not backup.is_file():
        raise FileNotFoundError(
            f"Backup not found: {backup}"
        )

    target.write_text(
        backup.read_text(
            encoding="utf-8"
        ),
        encoding="utf-8"
    )

    backup.unlink()


# ============================================================
# REMOVE BACKUP
# ============================================================

def remove_backup(
    repo_path: str,
    file_name: str
) -> None:
    """
    Remove the backup after a verified successful fix.
    """

    target = validate_target_file(
        repo_path,
        file_name
    )

    backup = target.with_suffix(
        target.suffix + ".bak"
    )

    if backup.exists():
        backup.unlink()


# ============================================================
# GIT DIFF
# ============================================================

def get_diff(
    repo_path: str
) -> str:
    """
    Return the current git diff for the repository.
    """

    result = subprocess.run(
        [
            "git",
            "diff"
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
        )

    return result.stdout.strip()


# ============================================================
# GET CHANGED FILES
# ============================================================

def get_changed_files(
    repo_path: str
) -> list[str]:
    """
    Return files currently modified according to git.
    """

    result = subprocess.run(
        [
            "git",
            "status",
            "--short"
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
        )

    changed_files = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        # Git status format:
        #
        # XY filename
        #
        # Example:
        # M  calculator.py
        #
        # The first two characters are status flags.

        if len(line) < 4:
            continue

        file_name = line[3:].strip()

        # Handle renamed files:
        #
        # old.py -> new.py
        #
        if " -> " in file_name:
            file_name = file_name.split(
                " -> "
            )[-1]

        # Remove surrounding quotes if Git
        # returns a quoted path.
        file_name = file_name.strip('"')

        changed_files.append(
            file_name
        )

    return changed_files


# ============================================================
# CHANGED FILE SAFETY VALIDATION
# ============================================================

def validate_changed_files(
    repo_path: str,
    allowed_file: str
) -> None:
    """
    Ensure the agent has modified only the intended
    source file.

    Backup files are allowed because they are created
    intentionally by the agent.
    """

    changed_files = get_changed_files(
        repo_path
    )

    allowed_path = Path(
        allowed_file
    ).as_posix()

    unexpected_files = []

    for file_name in changed_files:

        normalized_path = Path(
            file_name
        ).as_posix()

        # Intended target file
        if normalized_path == allowed_path:
            continue

        # Agent-created backup
        if normalized_path == (
            allowed_path + ".bak"
        ):
            continue

        unexpected_files.append(
            file_name
        )

    if unexpected_files:

        raise RuntimeError(
            "Unexpected files modified by agent: "
            + ", ".join(
                unexpected_files
            )
        )


# ============================================================
# PYTHON SYNTAX VALIDATION
# ============================================================

def validate_python_syntax(
    code: str
) -> None:
    """
    Validate Python source code before applying it.

    Raises SyntaxError when the generated code is invalid.
    """

    if not code.strip():
        raise ValueError(
            "Cannot validate empty Python code."
        )

    compile(
        code,
        "<agent_generated_code>",
        "exec"
    )