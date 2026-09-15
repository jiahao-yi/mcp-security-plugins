from __future__ import annotations

import json
from typing import Any


def json_text(value: Any) -> str:
    """Return the canonical serialization used for hashing and evidence checks."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def evidence_location(value: Any, quote: str, pointer: str = "") -> str | None:
    """Locate a verbatim quote in a parsed JSON string leaf."""
    if isinstance(value, str):
        return pointer or "/" if quote in value else None
    if isinstance(value, dict):
        for key, child in value.items():
            token = str(key).replace("~", "~0").replace("/", "~1")
            found = evidence_location(child, quote, f"{pointer}/{token}")
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = evidence_location(child, quote, f"{pointer}/{index}")
            if found is not None:
                return found
    return None


def verify_evidence(result: Any, serialized: str, quote: str) -> str | None:
    """Return a deterministic location for observed evidence."""
    if not quote:
        return None
    if quote in serialized:
        return "$serialized"
    return evidence_location(result, quote)

