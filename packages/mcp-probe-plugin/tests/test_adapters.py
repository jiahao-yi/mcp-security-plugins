import unittest
from types import SimpleNamespace

from mcp_probe_plugin.adapters import collect_mcp_tools


class FakeSession:
    def __init__(self):
        self.calls = 0

    async def list_tools(self, cursor=None):
        self.calls += 1
        if self.calls == 1:
            return SimpleNamespace(tools=[{"name": "a"}], nextCursor="next")
        return SimpleNamespace(tools=[{"name": "b"}], nextCursor=None)


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_collects_paginated_tools(self):
        tools = await collect_mcp_tools(FakeSession())
        self.assertEqual([tool["name"] for tool in tools], ["a", "b"])


if __name__ == "__main__":
    unittest.main()

