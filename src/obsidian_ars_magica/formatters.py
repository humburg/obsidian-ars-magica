# SPDX-License-Identifier: MIT
"""Formatting utilities for Obsidian notes and YAML frontmatter."""

import re
from typing import Any


def yaml_quote(value: str) -> str:
    """Safely quote a string for YAML frontmatter."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def sanitize_filename(name: str) -> str:
    """Sanitize a name to a valid note filename with hyphens."""
    clean = re.sub(r"[^\w]+", "-", name, flags=re.UNICODE).strip("-")
    return f"{clean}.md"


def dump_frontmatter(metadata: dict[str, Any]) -> str:
    """Serialize a dictionary into standard Obsidian YAML frontmatter block.

    Args:
        metadata: Key-value mapping of frontmatter fields.

    Returns:
        String starting and ending with '---' lines.
    """
    lines = ["---"]

    for key, value in metadata.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        elif isinstance(value, str):
            lines.append(f"{key}: {yaml_quote(value)}")
        elif isinstance(value, (list, tuple)):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, str):
                        lines.append(f"  - {yaml_quote(item)}")
                    elif isinstance(item, bool):
                        lines.append(f"  - {'true' if item else 'false'}")
                    else:
                        lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {yaml_quote(str(value))}")

    lines.append("---")
    return "\n".join(lines)

