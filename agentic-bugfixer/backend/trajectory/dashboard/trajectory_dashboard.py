import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
TRAJECTORY_DIR = BASE_DIR / "evaluation" / "trajectories"


def load_trajectories():
    """Load all recorded trajectory files."""

    if not TRAJECTORY_DIR.exists():
        return []

    trajectories = []

    for path in sorted(TRAJECTORY_DIR.glob("*.json")):
        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
            trajectories.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return trajectories


def display_trajectory(trajectory):
    """Display one complete agent trajectory."""

    print()
    print("=" * 70)
    print("              🤖 AGENT TRAJECTORY")
    print("=" * 70)

    print()
    print(f"Run ID       : {trajectory.get('run_id', 'N/A')}")
    print(f"Benchmark    : {trajectory.get('benchmark', 'N/A')}")
    print(f"Started      : {trajectory.get('started_at', 'N/A')}")
    print(f"Event Count  : {trajectory.get('event_count', 0)}")

    print()
    print("---------- EXECUTION FLOW ----------")

    events = trajectory.get("events", [])

    for event in events:

        step = event.get("step", "?")
        event_type = event.get("event", "UNKNOWN")
        details = event.get("details", {})

        print()
        print(
            f"[{step:02}] {event_type}"
        )

        if not details:
            continue

        for key, value in details.items():

            if value is None:
                continue

            if isinstance(value, str) and len(value) > 300:
                value = value[:300] + "..."

            print(
                f"      {key}: {value}"
            )

    print()
    print("=" * 70)


def display_summary(trajectories):
    """Display high-level trajectory statistics."""

    total_runs = len(trajectories)

    if total_runs == 0:
        print()
        print("No trajectories found.")
        return

    total_events = sum(
        trajectory.get("event_count", 0)
        for trajectory in trajectories
    )

    successful = 0
    failed = 0
    human_checkpoints = 0

    for trajectory in trajectories:

        for event in trajectory.get("events", []):

            event_type = event.get("event")

            if event_type == "FINAL_RESULT":

                status = (
                    event.get("details", {})
                    .get("status", "")
                    .upper()
                )

                if (
                    "VERIFIED" in status
                    or "ACCEPTED" in status
                    or "SUCCESS" in status
                ):
                    successful += 1
                else:
                    failed += 1

            if event_type == "HUMAN_CHECKPOINT":
                human_checkpoints += 1

    print()
    print("=" * 70)
    print("             📊 TRAJECTORY DASHBOARD")
    print("=" * 70)

    print()
    print("---------- SYSTEM SUMMARY ----------")

    print(f"Total Runs          : {total_runs}")
    print(f"Successful Runs     : {successful}")
    print(f"Failed Runs         : {failed}")
    print(f"Total Events        : {total_events}")
    print(f"Human Checkpoints   : {human_checkpoints}")

    if total_runs:
        success_rate = (
            successful / total_runs
        ) * 100

        print(
            f"Trajectory Success  : {success_rate:.2f}%"
        )

    print()
    print("---------- RUNS ----------")

    for index, trajectory in enumerate(
        trajectories,
        start=1,
    ):

        run_id = trajectory.get(
            "run_id",
            "unknown",
        )

        benchmark = trajectory.get(
            "benchmark",
            "unknown",
        )

        event_count = trajectory.get(
            "event_count",
            0,
        )

        print(
            f"{index}. "
            f"{benchmark:<15} "
            f"{run_id:<30} "
            f"{event_count} events"
        )

    print()
    print("=" * 70)


def main():

    trajectories = load_trajectories()

    if not trajectories:

        print()
        print("=" * 70)
        print("             📊 TRAJECTORY DASHBOARD")
        print("=" * 70)
        print()
        print(
            "No trajectory files found."
        )
        print()
        print(
            f"Expected directory:"
        )
        print(
            TRAJECTORY_DIR
        )
        print()
        return

    display_summary(
        trajectories
    )

    print()
    print("---------- LATEST TRAJECTORY ----------")

    display_trajectory(
        trajectories[-1]
    )


if __name__ == "__main__":
    main()