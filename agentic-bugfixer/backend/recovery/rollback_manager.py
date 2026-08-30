import json
import shutil
from datetime import datetime
from pathlib import Path


# ============================================================
# PATCH RECOVERY / ROLLBACK MANAGER
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RECOVERY_DIR = (
    BASE_DIR
    / "evaluation"
    / "recovery"
)


# ============================================================
# CREATE RECOVERY SNAPSHOT
# ============================================================

def create_snapshot(
    repository: str,
    target_file: str,
) -> Path:
    """
    Create a snapshot of the target file before modification.

    The snapshot is stored outside the repository so the
    recovery mechanism does not modify project source files.
    """

    repository_path = Path(
        repository
    ).resolve()

    source_path = (
        repository_path
        / target_file
    ).resolve()

    if repository_path not in source_path.parents:
        raise ValueError(
            "Target file is outside repository."
        )

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Target file does not exist: {target_file}"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    snapshot_dir = (
        RECOVERY_DIR
        / timestamp
    )

    snapshot_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot_path = (
        snapshot_dir
        / Path(target_file).name
    )

    shutil.copy2(
        source_path,
        snapshot_path,
    )

    metadata = {
        "repository": str(repository_path),
        "target_file": target_file,
        "snapshot": str(snapshot_path),
        "created_at": datetime.now().isoformat(),
    }

    metadata_path = (
        snapshot_dir
        / "metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )

    return snapshot_path


# ============================================================
# RESTORE SNAPSHOT
# ============================================================

def restore_snapshot(
    repository: str,
    target_file: str,
    snapshot_path: str,
) -> bool:
    """
    Restore the target file from a previously created snapshot.
    """

    repository_path = Path(
        repository
    ).resolve()

    target_path = (
        repository_path
        / target_file
    ).resolve()

    snapshot = Path(
        snapshot_path
    ).resolve()

    if repository_path not in target_path.parents:
        raise ValueError(
            "Target file is outside repository."
        )

    if not snapshot.is_file():
        raise FileNotFoundError(
            f"Snapshot does not exist: {snapshot}"
        )

    target_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        snapshot,
        target_path,
    )

    return True


# ============================================================
# VERIFY RESTORATION
# ============================================================

def verify_restoration(
    repository: str,
    target_file: str,
    snapshot_path: str,
) -> bool:
    """
    Verify that the restored target file exactly matches
    the recovery snapshot.
    """

    repository_path = Path(
        repository
    ).resolve()

    target_path = (
        repository_path
        / target_file
    ).resolve()

    snapshot = Path(
        snapshot_path
    ).resolve()

    if not target_path.is_file():
        return False

    if not snapshot.is_file():
        return False

    return (
        target_path.read_bytes()
        == snapshot.read_bytes()
    )


# ============================================================
# REMOVE SNAPSHOT
# ============================================================

def remove_snapshot(
    snapshot_path: str,
) -> None:
    """
    Remove a recovery snapshot after it is no longer needed.
    """

    snapshot = Path(
        snapshot_path
    ).resolve()

    if not snapshot.exists():
        return

    snapshot_dir = snapshot.parent

    if snapshot_dir.exists():
        shutil.rmtree(
            snapshot_dir
        )


# ============================================================
# RECOVERY WORKFLOW
# ============================================================

def rollback_patch(
    repository: str,
    target_file: str,
    snapshot_path: str,
) -> bool:
    """
    Complete rollback workflow.

    1. Restore original source.
    2. Verify restoration.
    3. Report the result.
    """

    print(
        "\n========== PATCH RECOVERY ==========\n"
    )

    print(
        f"Target File : {target_file}"
    )

    print(
        "Restoring original source..."
    )

    restore_snapshot(
        repository,
        target_file,
        snapshot_path,
    )

    verified = verify_restoration(
        repository,
        target_file,
        snapshot_path,
    )

    if verified:

        print(
            "✓ Original source restored."
        )

        print(
            "✓ Restoration verified."
        )

        print(
            "\n🛡 PATCH SAFELY ROLLED BACK"
        )

        return True

    print(
        "❌ Restoration verification failed."
    )

    return False


# ============================================================
# STANDALONE DEMO
# ============================================================

def main():

    print(
        "\n" + "=" * 60
    )

    print(
        "       🛡 PATCH ROLLBACK MANAGER"
    )

    print(
        "=" * 60
    )

    demo_repo = (
        BASE_DIR
        / "benchmarks"
        / "bug_01"
        / "repo"
    )

    target_file = "calculator.py"

    print(
        "\n========== CREATING SNAPSHOT ==========\n"
    )

    snapshot = create_snapshot(
        str(demo_repo),
        target_file,
    )

    print(
        f"✓ Snapshot created:"
    )

    print(snapshot)

    print(
        "\n========== VERIFYING SNAPSHOT ==========\n"
    )

    if snapshot.is_file():

        print(
            "✓ Snapshot exists."
        )

    else:

        print(
            "❌ Snapshot creation failed."
        )

        return

    print(
        "\n========== RECOVERY READY ==========\n"
    )

    print(
        "The original source is safely backed up."
    )

    print(
        "A failed patch can now be restored using:"
    )

    print(
        "rollback_patch(...)"
    )

    print(
        "\n" + "=" * 60
    )


if __name__ == "__main__":
    main()