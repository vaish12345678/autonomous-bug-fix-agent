import subprocess
from pathlib import Path


def validate_target_file(repo_path: str, file_name: str) -> Path:
    """
    Validate that the target file exists inside the repository
    and is not a test file.
    """

    root = Path(repo_path).resolve()
    target = (root / file_name).resolve()

    if root not in target.parents:
        raise ValueError(
            "Target file is outside repository."
        )

    if not target.is_file():
        raise FileNotFoundError(
            f"Target file does not exist: {file_name}"
        )

    filename = target.name.lower()

    if filename.startswith("test_"):
        raise ValueError(
            "Agent is not allowed to modify test files."
        )

    if filename.endswith("_test.py"):
        raise ValueError(
            "Agent is not allowed to modify test files."
        )

    if filename == "conftest.py":
        raise ValueError(
            "Agent is not allowed to modify test configuration."
        )

    return target


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


def get_diff(repo_path: str) -> str:
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