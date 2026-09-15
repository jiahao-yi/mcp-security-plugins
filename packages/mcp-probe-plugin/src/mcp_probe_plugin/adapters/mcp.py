from __future__ import annotations

from typing import Any

from ..core import CallPolicy
from ..plugin import ToolsListProbePlugin


async def collect_mcp_tools(session: Any, *, max_pages: int = 100) -> list[Any]:
    """Collect a paginated MCP tools/list response without binding to an SDK version."""
    tools: list[Any] = []
    cursor = None
    seen: set[str] = set()
    for _ in range(max_pages):
        page = await session.list_tools(cursor=cursor)
        tools.extend(page.tools)
        cursor = getattr(page, "nextCursor", None)
        if not cursor:
            return tools
        if cursor in seen:
            raise RuntimeError("Repeated tools/list cursor")
        seen.add(cursor)
    raise RuntimeError("tools/list page limit exceeded")


async def probe_mcp_session(
    plugin: ToolsListProbePlugin,
    *,
    session: Any,
    server_id: str,
    trusted_fixture: dict[str, Any],
    call_policy: CallPolicy | None = None,
    execution_boundary: dict[str, Any] | str = "caller-provided MCP session",
) -> dict[str, Any]:
    """Probe an initialized MCP ClientSession or compatible object."""
    tools = await collect_mcp_tools(session)

    async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
        return await session.call_tool(name, arguments)

    return await plugin.on_tools_list(
        server_id=server_id,
        tools=tools,
        probe_executor=call_tool,
        fixture=trusted_fixture,
        call_policy=call_policy,
        execution_boundary=execution_boundary,
    )

