from __future__ import annotations

import re
from typing import Any


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def render_template(template: str, values: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = values.get(key, match.group(0))
        return "" if value is None else str(value)

    return _PLACEHOLDER_RE.sub(replace, template)

