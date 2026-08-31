from backend.trajectory.integration.agent_hooks import AgentHooks


class AgentTrajectoryIntegration:
    """
    Safe integration layer between the existing agent
    and the trajectory tracking system.

    Trajectory failures must NEVER stop the bug-fixing agent.
    """

    def __init__(self, benchmark):
        self.enabled = True

        try:
            self.hooks = AgentHooks(benchmark)
        except Exception as error:
            self.enabled = False
            self.hooks = None
            print(
                f"⚠ Trajectory tracking disabled: {error}"
            )

    def _call(self, method, *args, **kwargs):
        if not self.enabled or self.hooks is None:
            return

        try:
            getattr(self.hooks, method)(*args, **kwargs)
        except Exception as error:
            print(
                f"⚠ Trajectory event failed "
                f"({method}): {error}"
            )

    def repository_read(self, result):
        self._call(
            "repository_read",
            result
        )

    def bug_analysis(self, decision, reasoning=None):
        self._call(
            "bug_analysis",
            decision,
            reasoning
        )

    def target_selected(self, file_name):
        self._call(
            "target_selected",
            file_name
        )

    def patch_generated(self, result):
        self._call(
            "patch_generated",
            result
        )

    def patch_validated(self, result):
        self._call(
            "patch_validated",
            result
        )

    def human_approval(self, decision):
        self._call(
            "human_approval",
            decision
        )

    def patch_applied(self, file_name, result):
        self._call(
            "patch_applied",
            file_name,
            result
        )

    def test_result(self, passed, output, runtime=None):
        self._call(
            "test_result",
            passed,
            output,
            runtime
        )

    def failure_classified(
        self,
        failure_type,
        severity,
        reason,
        confidence=None
    ):
        self._call(
            "failure_classified",
            failure_type,
            severity,
            reason,
            confidence
        )

    def recovery_plan(
        self,
        strategy,
        priority,
        retry_allowed,
        max_attempts
    ):
        self._call(
            "recovery_plan",
            strategy,
            priority,
            retry_allowed,
            max_attempts
        )

    def final_result(
        self,
        status,
        confidence=None,
        risk_level=None
    ):
        self._call(
            "final_result",
            status,
            confidence,
            risk_level
        )

    def save(self):
        if not self.enabled or self.hooks is None:
            return None

        try:
            return self.hooks.save()
        except Exception as error:
            print(
                f"⚠ Could not save trajectory: {error}"
            )
            return None