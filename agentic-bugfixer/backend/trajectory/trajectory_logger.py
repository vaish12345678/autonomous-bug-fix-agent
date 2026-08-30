import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TRAJECTORY_DIR = BASE_DIR / "evaluation" / "trajectories"


class TrajectoryLogger:
    """
    Records the complete decision and execution trajectory
    of an autonomous bug-fixing run.

    The logger is intentionally passive:
    it records events supplied by the agent and does not
    invent or modify execution results.
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        benchmark: Optional[str] = None,
    ):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        self.run_id = run_id or f"run_{timestamp}"
        self.benchmark = benchmark
        self.started_at = datetime.now().isoformat()

        self.events: List[Dict[str, Any]] = []

        self.record(
            "RUN_STARTED",
            {
                "benchmark": benchmark,
            },
        )

    # ============================================================
    # RECORD EVENT
    # ============================================================

    def record(
        self,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record one event in the agent trajectory.
        """

        event = {
            "step": len(self.events) + 1,
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details or {},
        }

        self.events.append(event)

        return event

    # ============================================================
    # AI DECISION
    # ============================================================

    def record_ai_decision(
        self,
        stage: str,
        decision: str,
        reasoning: Optional[str] = None,
    ):
        """
        Record an AI-driven decision.

        This stores the reasoning supplied by the caller;
        it does not generate fake reasoning.
        """

        return self.record(
            "AI_DECISION",
            {
                "stage": stage,
                "decision": decision,
                "reasoning": reasoning,
            },
        )

    # ============================================================
    # TOOL / ACTION
    # ============================================================

    def record_action(
        self,
        action: str,
        tool: Optional[str] = None,
        result: Optional[str] = None,
    ):
        """
        Record an action performed by the agent.
        """

        return self.record(
            "ACTION",
            {
                "action": action,
                "tool": tool,
                "result": result,
            },
        )

    # ============================================================
    # TEST RESULT
    # ============================================================

    def record_test_result(
        self,
        passed: bool,
        output: str,
        runtime: Optional[float] = None,
    ):
        """
        Record an actual test execution result.
        """

        return self.record(
            "TEST_RESULT",
            {
                "passed": passed,
                "output": output,
                "runtime": runtime,
            },
        )

    # ============================================================
    # FAILURE
    # ============================================================

    def record_failure(
        self,
        failure_type: str,
        severity: str,
        reason: str,
        confidence: Optional[float] = None,
    ):
        """
        Record failure classification.
        """

        return self.record(
            "FAILURE_CLASSIFIED",
            {
                "type": failure_type,
                "severity": severity,
                "reason": reason,
                "confidence": confidence,
            },
        )

    # ============================================================
    # RECOVERY
    # ============================================================

    def record_recovery(
        self,
        strategy: str,
        priority: str,
        retry_allowed: bool,
        max_attempts: int,
    ):
        """
        Record the recovery strategy selected
        after a failed attempt.
        """

        return self.record(
            "RECOVERY_PLAN",
            {
                "strategy": strategy,
                "priority": priority,
                "retry_allowed": retry_allowed,
                "max_attempts": max_attempts,
            },
        )

    # ============================================================
    # HUMAN CHECKPOINT
    # ============================================================

    def record_human_checkpoint(
        self,
        decision: str,
        reviewer: Optional[str] = None,
    ):
        """
        Record a human approval/rejection checkpoint.
        """

        return self.record(
            "HUMAN_CHECKPOINT",
            {
                "decision": decision,
                "reviewer": reviewer,
            },
        )

    # ============================================================
    # FINAL RESULT
    # ============================================================

    def record_final_result(
        self,
        status: str,
        confidence: Optional[float] = None,
        risk_level: Optional[str] = None,
    ):
        """
        Record the final agent decision.
        """

        return self.record(
            "FINAL_RESULT",
            {
                "status": status,
                "confidence": confidence,
                "risk_level": risk_level,
            },
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(self) -> Dict[str, Any]:
        """
        Generate a compact trajectory summary.
        """

        return {
            "run_id": self.run_id,
            "benchmark": self.benchmark,
            "started_at": self.started_at,
            "event_count": len(self.events),
            "events": self.events,
        }

    # ============================================================
    # SAVE
    # ============================================================

    def save(self) -> Path:
        """
        Persist trajectory as JSON.
        """

        TRAJECTORY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            TRAJECTORY_DIR
            / f"{self.run_id}.json"
        )

        output_path.write_text(
            json.dumps(
                self.summary(),
                indent=4,
            ),
            encoding="utf-8",
        )

        return output_path


# ================================================================
# DEMO
# ================================================================

def main():
    print()
    print("=" * 60)
    print("       🤖 AGENT TRAJECTORY LOGGER")
    print("=" * 60)

    logger = TrajectoryLogger(
        benchmark="demo"
    )

    logger.record_ai_decision(
        stage="BUG_ANALYSIS",
        decision="calculator.py is the target source file.",
        reasoning="Repository inspection identified the incorrect arithmetic operation.",
    )

    logger.record_action(
        action="Read target source file",
        tool="read_file",
        result="Source file loaded successfully.",
    )

    logger.record_ai_decision(
        stage="PATCH_GENERATION",
        decision="Replace multiplication with division.",
    )

    logger.record_action(
        action="Generate patch",
        tool="AI patch generator",
        result="Patch generated.",
    )

    logger.record_action(
        action="Validate patch syntax",
        tool="syntax validator",
        result="Syntax validation passed.",
    )

    logger.record_human_checkpoint(
        decision="APPROVED"
    )

    logger.record_action(
        action="Apply patch",
        tool="patcher",
        result="Patch applied successfully.",
    )

    logger.record_test_result(
        passed=True,
        output="2 passed in 0.02s",
        runtime=1.89,
    )

    logger.record_final_result(
        status="VERIFIED_AND_ACCEPTED",
        confidence=100.0,
        risk_level="LOW",
    )

    output_path = logger.save()

    print()
    print("========== TRAJECTORY ==========")

    for event in logger.events:
        print(
            f"{event['step']:02d}. "
            f"{event['event']}"
        )

    print()
    print("✓ Trajectory saved:")
    print(output_path)
    print("=" * 60)


if __name__ == "__main__":
    main()