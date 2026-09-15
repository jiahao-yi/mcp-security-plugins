from __future__ import annotations


class ProbeError(Exception):
    """Base error whose code is safe to persist in a probe report."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class ModelResponseError(ProbeError):
    """A provider returned an incomplete or structurally invalid model response."""


class ProbeAdmissionError(RuntimeError):
    """Raised when a caller requires a conclusive admission decision."""

    def __init__(self, decision: str):
        super().__init__(f"MCP probe decision does not permit admission: {decision}")
        self.decision = decision

