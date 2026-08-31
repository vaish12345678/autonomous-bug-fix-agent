import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
TRAJECTORY_DIR = BASE_DIR / "evaluation" / "trajectories"


class AgentTrajectory:
    """
    Records the real execution trajectory of the autonomous
    bug-fixing agent.
    """

    def __init__(self, benchmark="unknown"):
        self.benchmark = benchmark
        self.run_id = (
            "run_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

        self.started_at = (
            datetime.now().isoformat()
        )

        self.events = []

        self.record(
            "RUN_STARTED",
            {
                "benchmark": benchmark
            }
        )

    def record(self, event, details=None):
        """Record one execution event."""

        self.events.append(
            {
                "step": len(self.events) + 1,
                "event": event,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
        )

    def record_ai_decision(
        self,
        stage,
        decision,
        reasoning=None
    ):
        """Record an AI decision."""

        details = {
            "stage": stage,
            "decision": decision
        }

        if reasoning:
            details["reasoning"] = reasoning

        self.record(
            "AI_DECISION",
            details
        )

    def record_action(
        self,
        action,
        tool=None,
        result=None
    ):
        """Record an agent action."""

        details = {
            "action": action
        }

        if tool:
            details["tool"] = tool

        if result:
            details["result"] = result

        self.record(
            "ACTION",
            details
        )

    def record_test_result(
        self,
        passed,
        output="",
        runtime=None
    ):
        """Record test execution."""

        details = {
            "passed": passed,
            "output": output
        }

        if runtime is not None:
            details["runtime"] = runtime

        self.record(
            "TEST_RESULT",
            details
        )

    def record_failure(
        self,
        failure_type,
        severity,
        reason,
        confidence=None
    ):
        """Record a classified failure."""

        details = {
            "type": failure_type,
            "severity": severity,
            "reason": reason
        }

        if confidence is not None:
            details["confidence"] = confidence

        self.record(
            "FAILURE_CLASSIFICATION",
            details
        )

    def record_recovery(
        self,
        strategy,
        priority,
        retry_allowed,
        max_attempts
    ):
        """Record recovery planning."""

        self.record(
            "RECOVERY_PLAN",
            {
                "strategy": strategy,
                "priority": priority,
                "retry_allowed": retry_allowed,
                "max_attempts": max_attempts
            }
        )

    def record_human_checkpoint(
        self,
        decision
    ):
        """Record human approval."""

        self.record(
            "HUMAN_CHECKPOINT",
            {
                "decision": decision
            }
        )

    def record_final_result(
        self,
        status,
        confidence=None,
        risk_level=None
    ):
        """Record final agent decision."""

        details = {
            "status": status
        }

        if confidence is not None:
            details["confidence"] = confidence

        if risk_level is not None:
            details["risk_level"] = risk_level

        self.record(
            "FINAL_RESULT",
            details
        )

    def save(self):
        """Save trajectory to JSON."""

        TRAJECTORY_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        trajectory = {
            "run_id": self.run_id,
            "benchmark": self.benchmark,
            "started_at": self.started_at,
            "event_count": len(self.events),
            "events": self.events
        }

        output_path = (
            TRAJECTORY_DIR
            / f"{self.run_id}.json"
        )

        output_path.write_text(
            json.dumps(
                trajectory,
                indent=4
            ),
            encoding="utf-8"
        )

        return output_path


def demo():
    """
    Demonstrate the trajectory integration layer.
    """

    trajectory = AgentTrajectory(
        benchmark="demo"
    )

    trajectory.record_action(
        action="Read repository",
        tool="read_repository",
        result="Repository loaded."
    )

    trajectory.record_ai_decision(
        stage="BUG_ANALYSIS",
        decision="calculator.py is the target file.",
        reasoning="Repository inspection identified the defective operation."
    )

    trajectory.record_action(
        action="Generate patch",
        tool="AI patch generator",
        result="Patch generated."
    )

    trajectory.record_action(
        action="Validate patch",
        tool="syntax validator",
        result="Syntax validation passed."
    )

    trajectory.record_human_checkpoint(
        "APPROVED"
    )

    trajectory.record_action(
        action="Apply patch",
        tool="patcher",
        result="Patch applied successfully."
    )

    trajectory.record_test_result(
        passed=True,
        output="2 passed in 0.02s",
        runtime=1.89
    )

    trajectory.record_final_result(
        status="VERIFIED_AND_ACCEPTED",
        confidence=100.0,
        risk_level="LOW"
    )

    path = trajectory.save()

    print()
    print("=" * 60)
    print("       🤖 TRAJECTORY INTEGRATION DEMO")
    print("=" * 60)
    print()
    print(f"Run ID       : {trajectory.run_id}")
    print(f"Events       : {len(trajectory.events)}")
    print()
    print(f"✓ Trajectory saved:")
    print(path)
    print()
    print("=" * 60)


if __name__ == "__main__":
    demo()