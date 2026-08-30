import subprocess
import sys
from pathlib import Path


# ============================================================
# GIT COMMAND HELPER
# ============================================================

def run_git(repo_path: str, *args: str) -> str:
    """
    Execute a Git command inside the repository.
    """

    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or f"Git command failed: git {' '.join(args)}"
        )

    return result.stdout.strip()


# ============================================================
# GIT STATUS
# ============================================================

def get_git_status(repo_path: str) -> dict:
    """
    Read repository changes using porcelain Git status.
    """

    output = run_git(
        repo_path,
        "status",
        "--porcelain"
    )

    modified = []
    added = []
    deleted = []
    renamed = []
    untracked = []

    for line in output.splitlines():

        if not line:
            continue

        status = line[:2]
        file_path = line[3:].strip()

        if status.startswith("??"):
            untracked.append(file_path)

        elif "R" in status:
            renamed.append(file_path)

        elif "D" in status:
            deleted.append(file_path)

        elif "A" in status:
            added.append(file_path)

        elif "M" in status:
            modified.append(file_path)

    return {
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "renamed": renamed,
        "untracked": untracked
    }


# ============================================================
# DIFF STATISTICS
# ============================================================

def get_diff_stats(repo_path: str) -> dict:
    """
    Calculate added and removed lines.
    """

    output = run_git(
        repo_path,
        "diff",
        "--numstat"
    )

    added_lines = 0
    removed_lines = 0
    files_changed = 0

    for line in output.splitlines():

        if not line:
            continue

        parts = line.split("\t")

        if len(parts) < 3:
            continue

        try:
            added = int(parts[0])
            removed = int(parts[1])
        except ValueError:
            continue

        added_lines += added
        removed_lines += removed
        files_changed += 1

    return {
        "files_changed": files_changed,
        "added_lines": added_lines,
        "removed_lines": removed_lines
    }


# ============================================================
# UNEXPECTED CHANGE DETECTION
# ============================================================

def detect_unexpected_changes(
    repo_path: str,
    expected_file: str
) -> dict:
    """
    Verify that only the expected target file was modified.
    """

    status = get_git_status(repo_path)

    expected_path = Path(expected_file).as_posix()

    changed_files = []

    for category in (
        "modified",
        "added",
        "deleted",
        "renamed",
        "untracked"
    ):
        changed_files.extend(
            status[category]
        )

    normalized_files = [
        Path(file).as_posix()
        for file in changed_files
    ]

    unexpected = [
        file
        for file in normalized_files
        if file != expected_path
    ]

    return {
        "expected_file": expected_path,
        "changed_files": normalized_files,
        "unexpected_files": unexpected,
        "safe": len(unexpected) == 0
    }


# ============================================================
# CHANGE TRACKING
# ============================================================

def analyze_git_changes(
    repo_path: str,
    expected_file: str
) -> dict:
    """
    Perform complete Git-aware change analysis.
    """

    repository = Path(repo_path).resolve()

    if not repository.is_dir():
        raise FileNotFoundError(
            f"Repository not found: {repo_path}"
        )

    status = get_git_status(
        str(repository)
    )

    stats = get_diff_stats(
        str(repository)
    )

    safety = detect_unexpected_changes(
        str(repository),
        expected_file
    )

    total_changes = (
        len(status["modified"])
        + len(status["added"])
        + len(status["deleted"])
        + len(status["renamed"])
        + len(status["untracked"])
    )

    return {
        "repository": str(repository),
        "expected_file": expected_file,
        "status": status,
        "diff": stats,
        "safety": safety,
        "total_changed_files": total_changes,
        "commit_safe": safety["safe"]
    }


# ============================================================
# TERMINAL REPORT
# ============================================================

def print_report(result: dict) -> None:

    status = result["status"]
    diff = result["diff"]
    safety = result["safety"]

    print()
    print("=" * 60)
    print("       🔍 GIT-AWARE CHANGE TRACKING")
    print("=" * 60)

    print()
    print("========== REPOSITORY STATUS ==========")
    print()

    print(
        f"Modified files : {len(status['modified'])}"
    )

    print(
        f"Added files    : {len(status['added'])}"
    )

    print(
        f"Deleted files  : {len(status['deleted'])}"
    )

    print(
        f"Renamed files  : {len(status['renamed'])}"
    )

    print(
        f"Untracked files: {len(status['untracked'])}"
    )

    print()
    print("========== TARGET FILE ==========")
    print()

    print(
        f"Expected file : {result['expected_file']}"
    )

    print()
    print("========== DIFF STATISTICS ==========")
    print()

    print(
        f"Files changed : {diff['files_changed']}"
    )

    print(
        f"Lines added   : {diff['added_lines']}"
    )

    print(
        f"Lines removed : {diff['removed_lines']}"
    )

    print()
    print("========== CHANGE SAFETY ==========")
    print()

    if safety["safe"]:

        print(
            "✓ Only the expected target file was changed."
        )

        print()
        print(
            "✓ COMMIT SAFE"
        )

    else:

        print(
            "⚠ UNEXPECTED FILE CHANGES DETECTED"
        )

        print()

        print("Unexpected files:")

        for file in safety["unexpected_files"]:
            print(
                f"  - {file}"
            )

        print()
        print(
            "❌ COMMIT BLOCKED"
        )

    print()
    print("=" * 60)


# ============================================================
# COMMAND LINE
# ============================================================

def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python -m backend.git.change_tracker "
            "<repo_path> <expected_file>"
        )

        sys.exit(1)

    repo_path = sys.argv[1]
    expected_file = sys.argv[2]

    try:

        result = analyze_git_changes(
            repo_path,
            expected_file
        )

        print_report(result)

    except Exception as error:

        print()
        print(
            f"❌ Git change tracking failed: {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()