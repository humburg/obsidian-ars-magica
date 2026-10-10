"""Extractor and formatter for Ars Magica Virtues and Flaws."""

import re
from pathlib import Path
from typing import Any

from obsidian_ars_magica.models import VirtueFlawEntry

KNOWN_COSTS = [
    "minor or major",
    "major or minor",
    "free",
    "minor",
    "major",
]

KNOWN_TYPES = [
    "general",
    "hermetic",
    "social status",
    "supernatural",
    "personality",
    "story",
    "mythic companion",
    "special",
]


def yaml_quote(value: str) -> str:
    """Safely quote a string for YAML frontmatter."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def parse_qualifiers(raw_line: str) -> dict[str, Any]:
    """Parse the italic qualifier line following a Virtue or Flaw heading.

    Example inputs:
        '*Minor, General*<br>'
        '*Major, Hermetic*<br>'
        '*Minor, General, Tainted*<br>'
        '*Free, Social Status, animals only*<br>'
        '*General, Minor*<br>'
        '*Minor, Social Status, Supernatural*<br>'

    Returns a dict with keys: 'cost', 'types', 'properties', 'raw'.
    """
    clean = re.sub(r"<\s*br\s*/?\s*>", "", raw_line).strip()
    if clean.startswith("*") and clean.endswith("*"):
        clean = clean[1:-1].strip()

    tokens = [tok.strip() for tok in clean.split(",") if tok.strip()]

    cost: str = ""
    types: list[str] = []
    properties: list[str] = []

    for token in tokens:
        low = token.lower()

        # Check if token is a cost
        if not cost and low in KNOWN_COSTS:
            # Capitalize standard format
            if low == "free":
                cost = "Free"
            elif low == "minor":
                cost = "Minor"
            elif low == "major":
                cost = "Major"
            elif low == "minor or major":
                cost = "Minor or Major"
            elif low == "major or minor":
                cost = "Major or Minor"
            continue

        # Check if token is a known type or compound type expression (e.g. 'General and Hermetic')
        if low in KNOWN_TYPES or any(f" {sep} " in low for sep in ["and", "or"]):
            # Preserve title-cased components
            types.append(token)
        else:
            # Otherwise it's a qualifier property, like 'Tainted' or 'animals only'
            properties.append(token)

    return {
        "cost": cost,
        "types": types,
        "properties": properties,
        "raw": raw_line.strip(),
    }


def format_frontmatter(entry: VirtueFlawEntry) -> str:
    """Format the YAML frontmatter for an entry."""
    lines = [
        "---",
        f"name: {yaml_quote(entry.name)}",
        f"category: {yaml_quote(entry.category)}",
        f"cost: {yaml_quote(entry.cost)}",
    ]

    # Types list
    if entry.types:
        lines.append("type:")
        for t in entry.types:
            lines.append(f"  - {yaml_quote(t)}")
    else:
        lines.append("type: []")

    # Properties list
    if entry.properties:
        lines.append("properties:")
        for p in entry.properties:
            lines.append(f"  - {yaml_quote(p)}")
    else:
        lines.append("properties: []")

    # Aliases list
    if entry.aliases:
        lines.append("aliases:")
        for alias in entry.aliases:
            lines.append(f"  - {yaml_quote(alias)}")
    else:
        lines.append("aliases: []")

    # Tags list
    if entry.tags:
        lines.append("tags:")
        for tag in entry.tags:
            lines.append(f"  - {yaml_quote(tag)}")
    else:
        lines.append("tags: []")

    lines.append("---")
    return "\n".join(lines)


def format_entry_markdown(entry: VirtueFlawEntry) -> str:
    """Format full markdown document with frontmatter, H1 heading, and body."""
    frontmatter = format_frontmatter(entry)
    body_text = entry.body.strip()
    return f"{frontmatter}\n\n# {entry.name}\n\n{body_text}\n"


def _parse_section_entries(
    lines: list[str],
    start_line_idx: int,
    end_line_idx: int,
    category: str,
) -> list[VirtueFlawEntry]:
    """Parse Level 4 entries within a given line range."""
    entries: list[VirtueFlawEntry] = []
    i = start_line_idx

    while i < end_line_idx:
        line = lines[i]
        if line.startswith("#### "):
            entry_name = line[5:].strip()
            source_line = i + 1

            # The immediately following line contains the italic qualifiers
            qualifier_line = lines[i + 1].strip() if i + 1 < end_line_idx else ""
            parsed = parse_qualifiers(qualifier_line)

            # Find start of body
            k = i + 2
            while k < end_line_idx and not lines[k].strip():
                k += 1

            # Find end of body (next #### heading, ## section heading, or end marker)
            next_entry = k
            while next_entry < end_line_idx:
                next_line = lines[next_entry]
                if next_line.startswith(("#### ", "## ")):
                    break
                if next_line.startswith("---") and (
                    next_entry + 1 < end_line_idx and lines[next_entry + 1].startswith(">")
                ):
                    # Section end marker before Chapter 5
                    break
                next_entry += 1

            body_lines = lines[k:next_entry]
            body_text = "".join(body_lines).strip()

            entry = VirtueFlawEntry(
                name=entry_name,
                category=category,
                cost=parsed["cost"],
                types=parsed["types"],
                properties=parsed["properties"],
                raw_qualifiers=parsed["raw"],
                body=body_text,
                source_line=source_line,
            )
            entries.append(entry)
            i = next_entry
        else:
            i += 1

    return entries


def extract_virtues_and_flaws(
    file_path: Path | str,
) -> tuple[list[VirtueFlawEntry], list[VirtueFlawEntry]]:
    """Extract all Virtues and Flaws from the core rules markdown file.

    Returns:
        tuple (virtues, flaws)
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    virtues_start: int | None = None
    list_of_flaws_idx: int | None = None
    flaws_start: int | None = None
    chapter_5_idx: int | None = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## Virtues" and virtues_start is None:
            virtues_start = idx
        elif stripped == "## List of Flaws" and list_of_flaws_idx is None:
            list_of_flaws_idx = idx
        elif stripped == "## Flaws" and flaws_start is None:
            flaws_start = idx
        elif stripped.startswith("# Chapter 5:") and chapter_5_idx is None:
            chapter_5_idx = idx

    if (
        virtues_start is None
        or list_of_flaws_idx is None
        or flaws_start is None
        or chapter_5_idx is None
    ):
        raise ValueError(
            f"Could not locate required section boundaries in {file_path}. "
            f"Found: Virtues={virtues_start}, ListOfFlaws={list_of_flaws_idx}, "
            f"Flaws={flaws_start}, Chapter5={chapter_5_idx}"
        )

    virtues = _parse_section_entries(lines, virtues_start, list_of_flaws_idx, "Virtue")
    flaws = _parse_section_entries(lines, flaws_start, chapter_5_idx, "Flaw")

    return virtues, flaws


def export_virtues_and_flaws(
    source_path: Path | str,
    output_dir: Path | str,
) -> dict[str, int]:
    """Parse core rules and export individual Virtue and Flaw notes."""
    source = Path(source_path)
    target_root = Path(output_dir)

    virtues_dir = target_root / "virtues"
    flaws_dir = target_root / "flaws"

    virtues_dir.mkdir(parents=True, exist_ok=True)
    flaws_dir.mkdir(parents=True, exist_ok=True)

    virtues, flaws = extract_virtues_and_flaws(source)

    for v in virtues:
        file_path = virtues_dir / v.filename
        content = format_entry_markdown(v)
        file_path.write_text(content, encoding="utf-8")

    for f in flaws:
        file_path = flaws_dir / f.filename
        content = format_entry_markdown(f)
        file_path.write_text(content, encoding="utf-8")

    return {
        "virtues": len(virtues),
        "flaws": len(flaws),
    }
