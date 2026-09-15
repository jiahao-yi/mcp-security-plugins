from __future__ import annotations

import json
from typing import Any

from .errors import ModelResponseError
from .evidence import json_text


class OpenAICompatibleLLM:
    """Bounded JSON adapter for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        max_tokens: int = 700,
        request_extra_body: dict[str, Any] | None = None,
    ) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=30, max_retries=0)
        self.model = model
        self.max_tokens = max_tokens
        self.request_extra_body = request_extra_body
        self.calls = 0
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0}

    async def complete(self, system: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        request_overrides = (
            {"extra_body": self.request_extra_body} if self.request_extra_body else {}
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json_text(payload)},
            ],
            **request_overrides,
        )
        if response.usage:
            for key in self.usage:
                self.usage[key] += getattr(response.usage, key, 0) or 0
        if response.choices[0].finish_reason != "stop":
            raise ModelResponseError("MODEL_INCOMPLETE")
        try:
            value = json.loads(response.choices[0].message.content or "")
        except json.JSONDecodeError as exc:
            raise ModelResponseError("MODEL_JSON_INVALID") from exc
        if not isinstance(value, dict):
            raise ModelResponseError("MODEL_SHAPE_INVALID")
        return value

    async def close(self) -> None:
        await self.client.close()

