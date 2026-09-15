import asyncio
import unittest

from mcp_probe_plugin import ProbeConfig, ToolsListProbePlugin, probe_tools_list


TOOL = {
    "name": "search",
    "description": "Search stored memories.",
    "inputSchema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
        "additionalProperties": False,
    },
}


class FakeModel:
    def __init__(self, *, arguments=None, verdict="consistent", quote="No memories"):
        self.arguments = {"query": "blue"} if arguments is None else arguments
        self.verdict = verdict
        self.quote = quote
        self.calls = []

    async def complete(self, system, payload):
        self.calls.append(payload)
        if "result_json" not in payload:
            return {"arguments": self.arguments, "purpose": "search memory"}
        return {"verdict": self.verdict, "reason": "observed result", "evidence_quote": self.quote}


async def ok_call(name, arguments):
    return {"content": [{"type": "text", "text": "No memories found"}], "isError": False}


class CoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_consistent_result_admits_observed(self):
        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=ok_call,
            planner=FakeModel(),
            fixture={},
        )
        self.assertEqual(result["decision"], "admit_observed")
        self.assertEqual(result["records"][0]["evidence_location"], "$serialized")

    async def test_nested_json_string_evidence_uses_leaf_pointer(self):
        async def nested(*args):
            return {
                "content": [{"type": "text", "text": '[{"name":"main"}]'}],
                "isError": False,
            }

        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=nested,
            planner=FakeModel(quote='[{"name":"main"}'),
            fixture={},
        )
        self.assertEqual(result["records"][0]["evidence_location"], "/content/0/text")

    async def test_distinct_planner_and_judge(self):
        planner, judge = FakeModel(), FakeModel()
        await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=ok_call,
            planner=planner,
            judge=judge,
            fixture={},
        )
        self.assertEqual(len(planner.calls), 1)
        self.assertEqual(len(judge.calls), 1)

    async def test_invalid_arguments_never_execute(self):
        called = False

        async def forbidden(*args):
            nonlocal called
            called = True

        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=forbidden,
            planner=FakeModel(arguments={"query": 7}),
            fixture={},
        )
        self.assertFalse(called)
        self.assertEqual(result["records"][0]["failure_code"], "ARGUMENT_SCHEMA_INVALID")

    async def test_policy_denies_before_execution(self):
        called = False

        async def forbidden(*args):
            nonlocal called
            called = True

        def deny(*args):
            raise PermissionError("outside authority")

        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=forbidden,
            planner=FakeModel(),
            fixture={},
            call_policy=deny,
        )
        self.assertFalse(called)
        self.assertEqual(result["records"][0]["stage"], "policy")
        self.assertEqual(result["records"][0]["failure_code"], "POLICY_DENIED")

    async def test_missing_evidence_is_unknown(self):
        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=ok_call,
            planner=FakeModel(quote="not observed"),
            fixture={},
        )
        self.assertEqual(result["counts"]["unknown"], 1)
        self.assertEqual(result["records"][0]["failure_code"], "EVIDENCE_NOT_FOUND")

    async def test_large_result_has_structured_failure(self):
        async def large(*args):
            return {"content": [{"type": "text", "text": "x" * 100}]}

        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=large,
            planner=FakeModel(),
            fixture={},
            config=ProbeConfig(max_result_chars=10),
        )
        self.assertEqual(result["records"][0]["failure_code"], "RESULT_TOO_LARGE")

    async def test_timeout_is_unknown(self):
        async def slow(*args):
            await asyncio.sleep(1)

        result = await probe_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=slow,
            planner=FakeModel(),
            fixture={},
            config=ProbeConfig(timeout_seconds=0.01),
        )
        self.assertEqual(result["records"][0]["failure_code"], "EXECUTION_TIMEOUT")

    async def test_plugin_wrapper(self):
        plugin = ToolsListProbePlugin(planner=FakeModel())
        result = await plugin.on_tools_list(
            server_id="fixture",
            tools=[TOOL],
            probe_executor=ok_call,
            fixture={},
        )
        plugin.require_admit_observed(result)


if __name__ == "__main__":
    unittest.main()
