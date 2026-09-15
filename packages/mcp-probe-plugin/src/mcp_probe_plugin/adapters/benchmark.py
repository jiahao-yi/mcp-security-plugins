from __future__ import annotations

from typing import Any

from ..core import CallPolicy, ProbeExecutor
from ..plugin import ToolsListProbePlugin


async def probe_benchmark_server(
    plugin: ToolsListProbePlugin,
    *,
    server_id: str,
    tool_metadata: list[Any],
    call_tool: ProbeExecutor,
    trusted_fixture: dict[str, Any],
    call_policy: CallPolicy | None = None,
    execution_boundary: dict[str, Any] | str = "benchmark-provided",
) -> dict[str, Any]:
    """Adapter for benchmarks that already expose metadata and call_tool."""
    return await plugin.on_tools_list(
        server_id=server_id,
        tools=tool_metadata,
        probe_executor=call_tool,
        fixture=trusted_fixture,
        call_policy=call_policy,
        execution_boundary=execution_boundary,
    )

