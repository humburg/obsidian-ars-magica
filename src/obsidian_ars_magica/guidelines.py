# SPDX-License-Identifier: MIT
"""Extractor and formatter for Ars Magica Spell Guidelines."""

import re
from pathlib import Path

from obsidian_ars_magica.bases import format_guideline_bases_block
from obsidian_ars_magica.formatters import dump_frontmatter
from obsidian_ars_magica.models import (
    FORMS,
    TECHNIQUES,
    GuidelineLevelEntry,
    GuidelineSection,
)


def parse_guidelines(text: str) -> list[GuidelineSection]:
    """Parse Ars Magica core rules markdown text and extract all 50 Spell Guideline sections."""
    lines = text.splitlines()

    ch9_start = 0
    ch10_start = len(lines)
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "# Chapter 9: Spells":
            ch9_start = idx
        elif stripped == "# Chapter 10: Long Term Events":
            ch10_start = idx
            break

    guidelines: list[GuidelineSection] = []

    for form in FORMS:
        for tech in TECHNIQUES:
            heading = f"### {tech} {form} Guidelines"
            heading_idx = -1
            for idx in range(ch9_start, ch10_start):
                if lines[idx].strip() == heading:
                    heading_idx = idx
                    break

            if heading_idx == -1:
                continue

            end_idx = heading_idx + 1
            while end_idx < ch10_start:
                if (
                    lines[end_idx].startswith("### ")
                    and lines[end_idx].endswith(" Spells")
                ):
                    break
                end_idx += 1

            sec_lines = lines[heading_idx + 1 : end_idx]

            intro_lines: list[str] = []
            table_lines: list[str] = []
            in_table = False

            for l in sec_lines:
                stripped = l.strip()
                if stripped.startswith("|"):
                    in_table = True
                    table_lines.append(stripped)
                elif in_table:
                    continue
                else:
                    intro_lines.append(l)

            intro_body = "\n".join(intro_lines).strip()

            levels_dict: dict[int | str, list[str]] = {}

            for tl in table_lines:
                parts = [p.strip() for p in tl.split("|")[1:-1]]
                if len(parts) >= 2 and not all(c == "-" for c in parts[0]):
                    lvl_col = parts[0]
                    desc_col = parts[1]
                    if lvl_col.lower() == "level" or lvl_col.startswith("Additional"):
                        continue

                    level_key: int | str
                    if lvl_col.isdigit():
                        level_key = int(lvl_col)
                    elif lvl_col.lower() == "general":
                        level_key = "General"
                    else:
                        level_key = lvl_col

                    raw_bullets = [
                        b.strip() for b in desc_col.split("<br>") if b.strip()
                    ]
                    clean_bullets: list[str] = []
                    for b in raw_bullets:
                        cb = re.sub(r"^[•\-\*]\s*", "", b).strip()
                        if cb:
                            clean_bullets.append(cb)

                    if level_key not in levels_dict:
                        levels_dict[level_key] = []
                    levels_dict[level_key].extend(clean_bullets)

            level_entries = [
                GuidelineLevelEntry(level=k, bullets=v)
                for k, v in levels_dict.items()
            ]

            sec = GuidelineSection(
                technique=tech,
                form=form,
                intro_body=intro_body,
                guidelines_by_level=level_entries,
                source_line=heading_idx + 1,
            )
            guidelines.append(sec)

    return guidelines


def extract_guidelines(source_path: Path | str) -> list[GuidelineSection]:
    """Parse Ars Magica core rules markdown file and extract all 50 Spell Guideline sections."""
    source = Path(source_path)
    content = source.read_text(encoding="utf-8")
    return parse_guidelines(content)


def format_guideline_frontmatter(section: GuidelineSection) -> str:
    """Format YAML frontmatter for a Guideline note."""
    return dump_frontmatter({
        "name": section.name,
        "category": section.category,
        "technique": section.technique,
        "form": section.form,
        "arts": section.primary_arts,
        "aliases": section.aliases,
        "tags": section.tags,
    })


def format_guideline_markdown(section: GuidelineSection) -> str:
    """Format full markdown document for a Technique + Form Guideline note."""
    fm = format_guideline_frontmatter(section)
    art_sh = section.primary_arts.lower()

    lines = [fm, f"\n# {section.name}\n"]

    if section.intro_body:
        lines.append(section.intro_body)
        lines.append("")

    for lvl_entry in section.guidelines_by_level:
        lvl_str = str(lvl_entry.level)
        lines.append(f"### Level {lvl_str}")
        for idx, bullet in enumerate(lvl_entry.bullets, start=1):
            block_id = f"^{art_sh}-{lvl_str.lower()}-{idx}"
            lines.append(f"- {bullet} {block_id}")
        lines.append("")

    # Obsidian Bases view section
    lines.append("---")
    lines.append("\n## Known Spells\n")
    lines.append(format_guideline_bases_block(section.technique, section.form))
    lines.append("")

    return "\n".join(lines)


def export_guidelines(
    source_path: Path | str,
    output_dir: Path | str,
) -> dict[str, int]:
    """Parse core rules and export 50 Technique+Form Guideline notes to output_dir/guidelines."""
    source = Path(source_path)
    target_root = Path(output_dir)

    guidelines_dir = target_root / "guidelines"
    guidelines_dir.mkdir(parents=True, exist_ok=True)

    guidelines = extract_guidelines(source)

    for g in guidelines:
        file_path = guidelines_dir / g.filename
        content = format_guideline_markdown(g)
        file_path.write_text(content, encoding="utf-8")

    return {"guidelines": len(guidelines)}

