from backend.trajectory.integration.agent_trajectory import AgentTrajectory


class AgentHooks:
    """
    Adapter between the autonomous bug-fixing agent
    and the trajectory recording system.
    """

    def __init__(self, benchmark):
        self.trajectory = AgentTrajectory(
            benchmark=benchmark
        )

    def repository_read(self, result=None):
        self.trajectory.record_action(
            action="Read repository",
            tool="read_repository",
            result=result
        )

    def bug_analysis(self, decision, reasoning=None):
        self.trajectory.record_ai_decision(
            stage="BUG_ANALYSIS",
            decision=decision,
            reasoning=reasoning
        )

    def target_selected(self, file_name):
        self.trajectory.record(
            "TARGET_SELECTED",
            {
                "file": file_name
            }
        )

    def patch_generated(self, result=None):
        self.trajectory.record_action(
            action="Generate patch",
            tool="AI patch generator",
            result=result
        )

    def patch_validated(self, result=None):
        self.trajectory.record_action(
            action="Validate patch",
            tool="patch validator",
            result=result
        )

    def patch_applied(self, file_name, result=None):
        self.trajectory.record_action(
            action="Apply patch",
            tool="patcher",
            result=result
        )

        self.trajectory.record(
            "TARGET_MODIFIED",
            {
                "file": file_name
            }
        )

    def test_result(self, passed, output, runtime=None):
        self.trajectory.record_test_result(
            passed=passed,
            output=output,
            runtime=runtime
        )

    def failure_classified(
        self,
        failure_type,
        severity,
        reason,
        confidence=None
    ):
        self.trajectory.record_failure(
            failure_type=failure_type,
            severity=severity,
            reason=reason,
            confidence=confidence
        )

    def recovery_plan(
        self,
        strategy,
        priority,
        retry_allowed,
        max_attempts
    ):
        self.trajectory.record_recovery(
            strategy=strategy,
            priority=priority,
            retry_allowed=retry_allowed,
            max_attempts=max_attempts
        )

    def human_approval(self, decision):
        self.trajectory.record_human_checkpoint(
            decision
        )

    def final_result(
        self,
        status,
        confidence=None,
        risk_level=None
    ):
        self.trajectory.record_final_result(
            status=status,
            confidence=confidence,
            risk_level=risk_level
        )

    def save(self):
        return self.trajectory.save()