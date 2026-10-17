# SPDX-License-Identifier: MIT
"""Extractor and formatter for Ars Magica Abilities."""

import re
from pathlib import Path

from obsidian_ars_magica.bases import generate_abilities_base
from obsidian_ars_magica.formatters import dump_frontmatter, yaml_quote
from obsidian_ars_magica.models import AbilityEntry


def split_specialties(raw_specialties_text: str) -> list[str]:
    """Split comma-separated specialties, preserving commas nested within parentheses.

    Example inputs:
        'falconry, specific animals' -> ['falconry', 'specific animals']
        'searching for a particular kind of thing (water, gold, etc.), searching in a particular kind of place'
            -> ['searching for a particular kind of thing (water, gold, etc.)', 'searching in a particular kind of place']
    """
    clean = re.sub(r"<\s*br\s*/?\s*>", "", raw_specialties_text).strip()
    # Strip any leading Specialties / Specialities label if present
    clean = re.sub(
        r"^\*?Speciali?t(?:ies|y)\*?:?\*?\s*", "", clean, flags=re.IGNORECASE
    ).strip()
    # Strip any trailing (Type) designation such as (General), (Academic), etc.
    clean = re.sub(
        r"\s*\((?:General|Academic|Arcane|Martial|Supernatural)\)\.?\s*$",
        "",
        clean,
        flags=re.IGNORECASE,
    ).strip()
    clean = clean.rstrip(".").lstrip(":").strip()

    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for char in clean:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)

        if char == "," and depth == 0:
            item = "".join(current).strip()
            if item:
                parts.append(item)
            current = []
        else:
            current.append(char)

    last_item = "".join(current).strip()
    if last_item:
        parts.append(last_item)

    return parts


def format_ability_frontmatter(entry: AbilityEntry) -> str:
    """Format YAML frontmatter for an Ability note."""
    return dump_frontmatter({
        "name": entry.name,
        "category": entry.category,
        "type": entry.ability_type,
        "specialties": entry.specialties,
        "untrained": entry.untrained,
        "aliases": entry.aliases,
        "tags": entry.tags,
    })


def format_ability_markdown(entry: AbilityEntry) -> str:
    """Format full markdown document with frontmatter, H1 heading, and body."""
    frontmatter = format_ability_frontmatter(entry)
    body_text = entry.body.strip()
    return f"{frontmatter}\n\n# {entry.name}\n\n{body_text}\n"


def _clean_heading_name(raw_heading: str) -> tuple[str, bool]:
    """Extract clean ability name and whether it had an asterisk indicating trained-only."""
    has_star = "*" in raw_heading or r"\*" in raw_heading
    cleaned = raw_heading.replace(r"\*", "").replace("*", "").strip()
    return cleaned, has_star


def parse_abilities(text: str, source_label: str = "source") -> list[AbilityEntry]:
    """Parse all Abilities from markdown rules text."""
    lines = text.splitlines(keepends=True)

    abt_idx: int | None = None
    al_idx: int | None = None
    end_idx: int | None = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## Abilities by Type" and abt_idx is None:
            abt_idx = idx
        elif stripped == "## Ability List" and al_idx is None:
            al_idx = idx
        elif stripped.startswith("# Chapter 6:") and end_idx is None:
            end_idx = idx

    if al_idx is None:
        raise ValueError(
            f"Could not locate '## Ability List' section in {source_label}."
        )

    if end_idx is None:
        end_idx = len(lines)

    # 1. Parse '## Abilities by Type' to build canonical ability metadata if present
    canonical_metadata: dict[str, dict[str, str | bool]] = {}
    if abt_idx is not None and abt_idx < al_idx:
        abt_content = "".join(lines[abt_idx:al_idx])
        type_sections = re.findall(
            r"#### (.*?) Abilities\n(.*?)(?=(?:####|\Z))", abt_content, re.DOTALL
        )
        for ability_type, section_content in type_sections:
            links = re.findall(r"\[(.*?)\]\(#(.*?)\)", section_content)
            for raw_link_name, anchor in links:
                clean_name, has_star = _clean_heading_name(raw_link_name)
                canonical_metadata[clean_name] = {
                    "type": ability_type,
                    "anchor": anchor,
                    "has_star": has_star,
                }

    # 2. Identify ability headings in ## Ability List
    known_subheadings = {"hex delay modifiers", "hex effects"}

    ability_headings: list[tuple[int, str, str, str, bool]] = []
    # tuple: (line_index, raw_heading, clean_name, ability_type, has_star)

    i = al_idx + 1
    while i < end_idx:
        line = lines[i]
        if line.startswith("#### "):
            raw_heading = line[5:].strip()
            clean_name, has_star = _clean_heading_name(raw_heading)
            # Normalize possible pronunciation guide in heading, e.g. Chirurgy (kie-RUHR-gee)
            base_name = re.sub(r"\s*\(.*?\)", "", clean_name).strip()

            matched_name: str | None = None
            ability_type: str = "General"

            if clean_name.lower() in known_subheadings:
                i += 1
                continue

            if canonical_metadata:
                if clean_name in canonical_metadata:
                    matched_name = clean_name
                    ability_type = str(canonical_metadata[clean_name]["type"])
                    has_star = has_star or bool(canonical_metadata[clean_name]["has_star"])
                elif base_name in canonical_metadata:
                    matched_name = base_name
                    ability_type = str(canonical_metadata[base_name]["type"])
                    has_star = has_star or bool(canonical_metadata[base_name]["has_star"])
            else:
                # Synthetic document without canonical 'Abilities by Type' list
                matched_name = base_name if base_name else clean_name

            if matched_name:
                ability_headings.append((i, raw_heading, matched_name, ability_type, has_star))
        i += 1

    # 3. Parse entries and specialties
    entries: list[AbilityEntry] = []

    for h_idx, (start_line_i, raw_heading, name, ability_type, has_star) in enumerate(
        ability_headings
    ):
        end_line_i = (
            ability_headings[h_idx + 1][0]
            if h_idx + 1 < len(ability_headings)
            else end_idx
        )

        entry_lines = lines[start_line_i + 1 : end_line_i]
        raw_body = "".join(entry_lines).strip()
        source_line = start_line_i + 1

        # Extract specialties list from the body text
        specialties: list[str] = []

        # Check line-based specialties format: e.g. '*Specialties:* ...' or '*Specialities:* ...'
        spec_match = re.search(
            r"(?:\n|^)(?:<\s*br\s*/?\s*>\s*)?\*?Speciali?t(?:ies|y)\*?:?\*?\s*(.*?)(?=\n|$)",
            raw_body,
            re.IGNORECASE,
        )
        if spec_match:
            raw_spec_text = spec_match.group(1).strip()
            specialties = split_specialties(raw_spec_text)
        else:
            # Check inline format (e.g. Hex ending with 'Specialties: ... (Supernatural)')
            inline_match = re.search(
                r"Speciali?t(?:ies|y):?\s*(.*?)\s*\((?:General|Academic|Arcane|Martial|Supernatural)\)\.?",
                raw_body,
                re.IGNORECASE,
            )
            if inline_match:
                specialties = split_specialties(inline_match.group(1).strip())

        # An ability without an asterisk can be used untrained (Score 0)
        can_be_used_untrained = not has_star

        entry = AbilityEntry(
            name=name,
            ability_type=ability_type,
            specialties=specialties,
            untrained=can_be_used_untrained,
            category="Ability",
            body=raw_body,
            source_line=source_line,
        )
        entries.append(entry)

    return entries


def extract_abilities(
    file_path: Path | str,
) -> list[AbilityEntry]:
    """Extract all Abilities from the core rules markdown file."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    return parse_abilities(content, source_label=str(file_path))


def export_abilities(
    source_path: Path | str,
    output_dir: Path | str,
) -> dict[str, int]:
    """Parse core rules and export individual Ability notes."""
    source = Path(source_path)
    target_root = Path(output_dir)

    abilities_dir = target_root / "abilities"
    abilities_dir.mkdir(parents=True, exist_ok=True)

    abilities = extract_abilities(source)

    for a in abilities:
        file_path = abilities_dir / a.filename
        content = format_ability_markdown(a)
        file_path.write_text(content, encoding="utf-8")

    # Generate standalone abilities.base database file
    abilities_base_path = target_root / "abilities.base"
    abilities_base_path.write_text(generate_abilities_base(), encoding="utf-8")

    return {
        "abilities": len(abilities),
    }


__all__ = [
    "export_abilities",
    "extract_abilities",
    "format_ability_frontmatter",
    "format_ability_markdown",
    "parse_abilities",
    "split_specialties",
    "yaml_quote",
]
