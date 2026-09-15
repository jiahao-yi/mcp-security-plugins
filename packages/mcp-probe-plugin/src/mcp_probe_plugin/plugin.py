from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import CallPolicy, JsonLLM, ProbeConfig, ProbeExecutor, probe_tools_list
from .errors import ProbeAdmissionError


@dataclass
class ToolsListProbePlugin:
    """Reusable layer-one hook for MCP hosts."""

    planner: JsonLLM
    judge: JsonLLM | None = None
    config: ProbeConfig = field(default_factory=ProbeConfig)

    async def on_tools_list(
        self,
        *,
        server_id: str,
        tools: list[Any],
        probe_executor: ProbeExecutor,
        fixture: dict[str, Any],
        call_policy: CallPolicy | None = None,
        execution_boundary: dict[str, Any] | str = "caller-provided",
    ) -> dict[str, Any]:
        return await probe_tools_list(
            server_id=server_id,
            tools=tools,
            probe_executor=probe_executor,
            planner=self.planner,
            judge=self.judge,
            fixture=fixture,
            call_policy=call_policy,
            execution_boundary=execution_boundary,
            config=self.config,
        )

    @staticmethod
    def require_admit_observed(report: dict[str, Any]) -> None:
        if report.get("decision") != "admit_observed":
            raise ProbeAdmissionError(str(report.get("decision")))

