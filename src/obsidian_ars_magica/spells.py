"""Extractor and formatter for Ars Magica Spells and Spell Guidelines."""

import re
from pathlib import Path

from obsidian_ars_magica.models import (
    GuidelineLevelEntry,
    GuidelineSection,
    SpellEntry,
)

TECHNIQUES: list[str] = ["Creo", "Intellego", "Muto", "Perdo", "Rego"]
FORMS: list[str] = [
    "Animal",
    "Aquam",
    "Auram",
    "Corpus",
    "Herbam",
    "Ignem",
    "Imaginem",
    "Mentem",
    "Terram",
    "Vim",
]

RANGE_CANONICAL: dict[str, tuple[str, int]] = {
    "per": ("Personal", 0),
    "personal": ("Personal", 0),
    "touch": ("Touch", 1),
    "eye": ("Eye", 1),
    "eve": ("Eye", 1),  # OCR / print typo in core rules
    "voice": ("Voice", 2),
    "sight": ("Sight", 3),
    "arc": ("Arcane Connection", 4),
    "arcane connection": ("Arcane Connection", 4),
    "special": ("Special", 0),
}

DURATION_CANONICAL: dict[str, tuple[str, int]] = {
    "mom": ("Momentary", 0),
    "momentary": ("Momentary", 0),
    "conc": ("Concentration", 1),
    "concentration": ("Concentration", 1),
    "diam": ("Diameter", 1),
    "diameter": ("Diameter", 1),
    "sun": ("Sun", 2),
    "ring": ("Ring", 2),
    "moon": ("Moon", 3),
    "year": ("Year", 4),
    "sun & year": ("Sun & Year", 4),
    "special": ("Special", 0),
    "spec": ("Special", 0),
}

TARGET_CANONICAL: dict[str, tuple[str, int]] = {
    "ind": ("Individual", 0),
    "individual": ("Individual", 0),
    "circle": ("Circle", 0),
    "taste": ("Taste", 0),
    "part": ("Part", 1),
    "touch": ("Touch", 1),
    "group": ("Group", 2),
    "room": ("Room", 2),
    "smell": ("Smell", 2),
    "struct": ("Structure", 3),
    "str": ("Structure", 3),
    "structure": ("Structure", 3),
    "hear": ("Hearing", 3),
    "hearing": ("Hearing", 3),
    "bound": ("Boundary", 4),
    "boundary": ("Boundary", 4),
    "vision": ("Vision", 4),
    "special": ("Special", 0),
}


def yaml_quote(value: str) -> str:
    """Safely quote a string for YAML frontmatter."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def clean_ocr_errors(text: str) -> str:
    """Normalize known OCR typos in Ars Magica spell texts.

    Specifically:
    - Normalizes 'Eve' (OCR error for 'Eye' Range) to 'Eye'.
    - Normalizes missing spaces in signed numbers and keywords (e.g. '+1Touch' -> '+1 Touch').
    """
    cleaned = re.sub(r"\bEve\b", "Eye", text)
    cleaned = re.sub(
        r"([+-]\d+)(Touch|Eye|Voice|Sight|Arc|Mom|Conc|Diam|Sun|Ring|Moon|Year|Ind|Part|Group|Room|Struct|Bound)\b",
        r"\1 \2",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


def parse_rdt_line(
    raw_rdt_line: str,
) -> tuple[str, int, str, int, str, int, bool]:
    """Parse Range, Duration, Target, and Ritual status from RDT text.

    Returns:
        (range_name, range_mag, duration_name, duration_mag, target_name, target_mag, is_ritual)
    """
    cleaned = clean_ocr_errors(raw_rdt_line)
    cleaned = re.sub(r"<\s*br\s*/?\s*>", "", cleaned).strip().rstrip(".")
    # Standardize delimiters before D: and T:
    cleaned = re.sub(r"[\s\.,;]+D:\s*", ", D: ", cleaned)
    cleaned = re.sub(r"[\s\.,;]+T:\s*", ", T: ", cleaned)


    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    r_val, d_val, t_val = "", "", ""
    is_ritual = False

    for part in parts:
        lower_p = part.lower()
        if lower_p.startswith("r:"):
            r_val = part[2:].strip().rstrip(".")
        elif lower_p.startswith("d:"):
            d_val = part[2:].strip().rstrip(".")
        elif lower_p.startswith("t:"):
            t_val = part[2:].strip().rstrip(".")
        elif "ritual" in lower_p:
            is_ritual = True

    r_norm, r_mag = RANGE_CANONICAL.get(r_val.lower(), (r_val or "Personal", 0))
    d_norm, d_mag = DURATION_CANONICAL.get(d_val.lower(), (d_val or "Momentary", 0))
    t_norm, t_mag = TARGET_CANONICAL.get(t_val.lower(), (t_val or "Individual", 0))

    return r_norm, r_mag, d_norm, d_mag, t_norm, t_mag, is_ritual


def parse_requisites_line(
    raw_req_line: str,
) -> tuple[list[str], list[str]]:
    """Parse technique and form requisites from a 'Req: ...' line.

    Returns:
        (technique_requisites, form_requisites)
    """
    cleaned = re.sub(r"<\s*br\s*/?\s*>", "", raw_req_line).strip()
    val = re.sub(r"^Req\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip().rstrip(".")
    parts = [p.strip() for p in re.split(r"[,/]|(?:\s+and\s+)", val) if p.strip()]

    tech_set = {t.lower(): t for t in TECHNIQUES}
    form_set = {f.lower(): f for f in FORMS}

    tech_reqs: list[str] = []
    form_reqs: list[str] = []

    for item in parts:
        lower = item.lower()
        if lower in tech_set:
            tech_reqs.append(tech_set[lower])
        elif lower in form_set:
            form_reqs.append(form_set[lower])

    return tech_reqs, form_reqs


def calculate_magnitudes_and_base(
    body_text: str,
    level: int | str,
    range_mag: int,
    duration_mag: int,
    target_mag: int,
) -> tuple[int | str, int, list[str], str]:
    """Extract base level, additional magnitudes, and modifiers from body text.

    Returns:
        (base_level, additional_magnitudes, additional_modifiers, raw_design_string)
    """
    body_text = clean_ocr_errors(body_text)

    # 1. Search for parenthetical design at end of description
    calc_match = re.findall(
        r"\((?:Base|Base level|Base effect|Base spell|As ward|Special spell|Unique spell|Mercurian Ritual)[^)]*\)",
        body_text,
        flags=re.IGNORECASE,
    )
    raw_design = calc_match[-1] if calc_match else ""

    # 2. Extract base level
    base_level: int | str
    base_num_match = re.search(r"Base:?\s*(?:level)?\s*(\d+)", body_text, flags=re.IGNORECASE)
    if base_num_match:
        base_level = int(base_num_match.group(1))
    elif level == "General" or "general" in raw_design.lower():
        base_level = "General"
    elif "mercurian ritual" in raw_design.lower():
        base_level = "Mercurian Ritual"
    elif "special spell" in raw_design.lower():
        base_level = "Special"
    elif "unique spell" in raw_design.lower():
        base_level = "Unique"
    else:
        base_level = 0

    # 3. Calculate additional magnitudes
    add_mag = 0
    known_mag = range_mag + duration_mag + target_mag

    if isinstance(level, int) and isinstance(base_level, int):
        if base_level < 5:
            if level <= 5:
                total_mags = level - base_level
            else:
                total_mags = (5 - base_level) + (level - 5) // 5
        else:
            total_mags = (level - base_level) // 5
        add_mag = total_mags - known_mag

    # 4. Extract modifier notes if raw_design exists
    add_modifiers: list[str] = []
    if raw_design:
        # Match tokens like +1 size, +2 size, -1 because..., +1 extra effect...
        mod_matches = re.findall(r"([+-]\d+\s+[^,\)]+)", raw_design)
        for m in mod_matches:
            cleaned_m = m.strip()
            # Exclude standard R/D/T keywords
            lower_m = cleaned_m.lower()
            if not any(
                k in lower_m
                for k in [
                    "touch",
                    "eye",
                    "eve",
                    "voice",
                    "sight",
                    "arc",
                    "mom",
                    "conc",
                    "diam",
                    "sun",
                    "ring",
                    "moon",
                    "year",
                    "ind",
                    "part",
                    "group",
                    "room",
                    "struct",
                    "bound",
                ]
            ):
                add_modifiers.append(cleaned_m)


    return base_level, add_mag, add_modifiers, raw_design


def extract_spells(source_path: Path | str) -> list[SpellEntry]:
    """Parse Ars Magica core rules markdown and extract all Spells."""
    source = Path(source_path)
    lines = source.read_text(encoding="utf-8").splitlines()

    # Locate Chapter 9: Spells
    ch9_start = 0
    ch10_start = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "# Chapter 9: Spells":
            ch9_start = idx
        elif line.strip() == "# Chapter 10: Long Term Events":
            ch10_start = idx
            break

    spell_records: list[dict] = []
    current_technique: str = ""
    current_form: str = ""
    current_level: int | str = 0

    for idx in range(ch9_start, ch10_start):
        line = lines[idx]
        if line.startswith("### ") and line.endswith(" Spells"):
            tefo = line[4:-7].strip().split()
            if len(tefo) >= 2:
                current_technique = tefo[0]
                current_form = tefo[1]
        elif line.startswith("#### "):
            lvl_text = line[5:].strip()
            if lvl_text.upper() == "GENERAL":
                current_level = "General"
            else:
                num_m = re.search(r"\d+", lvl_text)
                current_level = int(num_m.group(0)) if num_m else 0
        elif line.startswith("##### "):
            spell_name = line[6:].strip()
            spell_records.append(
                {
                    "start_line": idx,
                    "name": spell_name,
                    "technique": current_technique,
                    "form": current_form,
                    "level": current_level,
                }
            )

    spells: list[SpellEntry] = []

    for i, rec in enumerate(spell_records):
        start_line = rec["start_line"]
        next_start = (
            spell_records[i + 1]["start_line"]
            if i + 1 < len(spell_records)
            else ch10_start
        )

        entry_lines: list[str] = []
        for l in lines[start_line + 1 : next_start]:
            if l.startswith(("### ", "## ", "#### ")):
                break
            entry_lines.append(l)


        # First non-empty line is RDT
        non_empty_indices = [
            j for j, l in enumerate(entry_lines) if l.strip()
        ]
        if not non_empty_indices:
            continue

        rdt_line_idx = non_empty_indices[0]
        raw_rdt = clean_ocr_errors(entry_lines[rdt_line_idx].strip())
        r_name, r_mag, d_name, d_mag, t_name, t_mag, is_ritual = parse_rdt_line(
            raw_rdt
        )

        # Check for Req: line
        tech_reqs: list[str] = []
        form_reqs: list[str] = []
        body_start_idx = rdt_line_idx + 1

        if len(non_empty_indices) > 1:
            second_idx = non_empty_indices[1]
            candidate_req = entry_lines[second_idx].strip()
            if candidate_req.lower().startswith("req:") or candidate_req.lower().startswith("req :"):
                tech_reqs, form_reqs = parse_requisites_line(candidate_req)
                body_start_idx = second_idx + 1

        raw_body = clean_ocr_errors("\n".join(entry_lines[body_start_idx:]).strip())


        base_level, add_mag, add_mods, raw_design = calculate_magnitudes_and_base(
            raw_body,
            rec["level"],
            r_mag,
            d_mag,
            t_mag,
        )

        spell = SpellEntry(
            name=rec["name"],
            technique=rec["technique"],
            form=rec["form"],
            level=rec["level"],
            range=r_name,
            duration=d_name,
            target=t_name,
            ritual=is_ritual,
            technique_requisites=tech_reqs,
            form_requisites=form_reqs,
            base_level=base_level,
            range_magnitude=r_mag,
            duration_magnitude=d_mag,
            target_magnitude=t_mag,
            additional_magnitudes=add_mag,
            additional_modifiers=add_mods,
            raw_rdt=raw_rdt,
            raw_design=raw_design,
            body=raw_body,
            source_line=start_line + 1,
        )
        spells.append(spell)

    return spells


def extract_guidelines(source_path: Path | str) -> list[GuidelineSection]:
    """Parse Ars Magica core rules markdown and extract all 50 Spell Guideline sections."""
    source = Path(source_path)
    lines = source.read_text(encoding="utf-8").splitlines()

    ch9_start = 0
    ch10_start = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "# Chapter 9: Spells":
            ch9_start = idx
        elif line.strip() == "# Chapter 10: Long Term Events":
            ch10_start = idx
            break

    guidelines: list[GuidelineSection] = []

    for form in FORMS:
        for tech in TECHNIQUES:
            heading = f"### {tech} {form} Guidelines"
            # find heading line
            heading_idx = -1
            for idx in range(ch9_start, ch10_start):
                if lines[idx].strip() == heading:
                    heading_idx = idx
                    break

            if heading_idx == -1:
                continue

            # find section end (next "### ... Spells")
            end_idx = heading_idx + 1
            while end_idx < ch10_start:
                if (
                    lines[end_idx].startswith("### ")
                    and lines[end_idx].endswith(" Spells")
                ):
                    break
                end_idx += 1

            sec_lines = lines[heading_idx + 1 : end_idx]

            # Separate intro text and table
            intro_lines: list[str] = []
            table_lines: list[str] = []
            in_table = False

            for l in sec_lines:
                stripped = l.strip()
                if stripped.startswith("|"):
                    in_table = True
                    table_lines.append(stripped)
                elif in_table:
                    # After table has finished
                    continue
                else:
                    intro_lines.append(l)

            intro_body = "\n".join(intro_lines).strip()

            # Parse table rows into GuidelineLevelEntry
            levels_dict: dict[int | str, list[str]] = {}

            for tl in table_lines:
                parts = [p.strip() for p in tl.split("|")[1:-1]]
                if len(parts) >= 2 and not all(c == "-" for c in parts[0]):
                    lvl_col = parts[0]
                    desc_col = parts[1]
                    if lvl_col.lower() == "level" or lvl_col.startswith("Additional"):
                        continue

                    # Level could be int or "General"
                    level_key: int | str
                    if lvl_col.isdigit():
                        level_key = int(lvl_col)
                    elif lvl_col.lower() == "general":
                        level_key = "General"
                    else:
                        level_key = lvl_col

                    # Desc may contain multiple bullets separated by <br>
                    raw_bullets = [
                        b.strip() for b in desc_col.split("<br>") if b.strip()
                    ]
                    clean_bullets: list[str] = []
                    for b in raw_bullets:
                        # Strip leading bullet symbols (•, -, *)
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


def format_spell_frontmatter(spell: SpellEntry) -> str:
    """Format YAML frontmatter for a Spell note."""
    lines = [
        "---",
        f"name: {yaml_quote(spell.name)}",
        f"category: {yaml_quote(spell.category)}",
        f"technique: {yaml_quote(spell.technique)}",
        f"form: {yaml_quote(spell.form)}",
        f"arts: {yaml_quote(spell.primary_arts)}",
        f"level: {spell.level if isinstance(spell.level, int) else yaml_quote(str(spell.level))}",
    ]

    # Requisites
    if spell.technique_requisites:
        lines.append("technique_requisites:")
        for t in spell.technique_requisites:
            lines.append(f"  - {yaml_quote(t)}")
    else:
        lines.append("technique_requisites: []")

    if spell.form_requisites:
        lines.append("form_requisites:")
        for f in spell.form_requisites:
            lines.append(f"  - {yaml_quote(f)}")
    else:
        lines.append("form_requisites: []")

    # Parameters
    lines.append(f"range: {yaml_quote(spell.range)}")
    lines.append(f"duration: {yaml_quote(spell.duration)}")
    lines.append(f"target: {yaml_quote(spell.target)}")
    lines.append(f"ritual: {'true' if spell.ritual else 'false'}")

    # Design breakdown
    lines.append(
        f"base_level: {spell.base_level if isinstance(spell.base_level, int) else yaml_quote(str(spell.base_level))}"
    )
    lines.append(f"range_magnitude: {spell.range_magnitude}")
    lines.append(f"duration_magnitude: {spell.duration_magnitude}")
    lines.append(f"target_magnitude: {spell.target_magnitude}")
    lines.append(f"additional_magnitudes: {spell.additional_magnitudes}")

    total_mags = (
        spell.range_magnitude
        + spell.duration_magnitude
        + spell.target_magnitude
        + spell.additional_magnitudes
    )
    lines.append(f"total_magnitudes: {total_mags}")

    # Guideline link
    if isinstance(spell.base_level, int) and spell.base_level > 0:
        lines.append(
            f'guideline: {yaml_quote(f"[[{spell.technique}-{spell.form}-Guidelines#Level {spell.base_level}]]")}'
        )
    elif spell.base_level == "General":
        lines.append(
            f'guideline: {yaml_quote(f"[[{spell.technique}-{spell.form}-Guidelines#Level General]]")}'
        )
    else:
        lines.append(
            f'guideline: {yaml_quote(f"[[{spell.technique}-{spell.form}-Guidelines]]")}'
        )

    # Aliases
    lines.append("aliases:")
    for a in spell.aliases:
        lines.append(f"  - {yaml_quote(a)}")

    # Tags
    lines.append("tags:")
    for t in spell.tags:
        lines.append(f"  - {yaml_quote(t)}")

    lines.append("---")
    return "\n".join(lines)


def format_spell_markdown(spell: SpellEntry) -> str:
    """Format full markdown document for a Spell."""
    fm = format_spell_frontmatter(spell)

    # Header and Callout block
    level_disp = "Gen" if spell.level == "General" else str(spell.level)
    ritual_badge = " | **Ritual**" if spell.ritual else ""

    # Requisites line
    reqs_list = spell.technique_requisites + spell.form_requisites
    req_line = f"\n> - **Req:** {', '.join(reqs_list)}" if reqs_list else ""

    # Guideline anchor link
    if isinstance(spell.base_level, int) and spell.base_level > 0:
        guideline_display = f"[[{spell.technique}-{spell.form}-Guidelines#Level {spell.base_level}|{spell.technique} {spell.form} Base {spell.base_level}]]"
    elif spell.base_level == "General":
        guideline_display = f"[[{spell.technique}-{spell.form}-Guidelines#Level General|{spell.technique} {spell.form} Base General]]"
    else:
        guideline_display = f"[[{spell.technique}-{spell.form}-Guidelines|{spell.technique} {spell.form} Guidelines]]"

    total_mags = (
        spell.range_magnitude
        + spell.duration_magnitude
        + spell.target_magnitude
        + spell.additional_magnitudes
    )

    mag_breakdown = f"+{total_mags}" if total_mags >= 0 else str(total_mags)
    breakdown_parts = []
    if spell.range_magnitude:
        breakdown_parts.append(f"+{spell.range_magnitude} {spell.range}")
    if spell.duration_magnitude:
        breakdown_parts.append(f"+{spell.duration_magnitude} {spell.duration}")
    if spell.target_magnitude:
        breakdown_parts.append(f"+{spell.target_magnitude} {spell.target}")
    breakdown_parts.extend(spell.additional_modifiers)

    breakdown_str = f" ({', '.join(breakdown_parts)})" if breakdown_parts else ""


    callout = (
        f"> [!metadata] **{spell.arts_shorthand} {level_disp}**{ritual_badge}\n"
        f"> - **R:** {spell.range}, **D:** {spell.duration}, **T:** {spell.target}{req_line}\n"
        f"> - **Base:** {spell.base_level} | **Total Magnitudes:** {mag_breakdown}{breakdown_str}\n"
        f"> - **Guideline:** {guideline_display}"
    )

    body = spell.body.strip()

    return f"{fm}\n\n# {spell.name}\n\n{callout}\n\n{body}\n"


def format_guideline_frontmatter(section: GuidelineSection) -> str:
    """Format YAML frontmatter for a Guideline note."""
    lines = [
        "---",
        f"name: {yaml_quote(f'{section.technique} {section.form} Guidelines')}",
        f"category: {yaml_quote(section.category)}",
        f"technique: {yaml_quote(section.technique)}",
        f"form: {yaml_quote(section.form)}",
        f"arts: {yaml_quote(section.primary_arts)}",
        "aliases:",
    ]
    for a in section.aliases:
        lines.append(f"  - {yaml_quote(a)}")

    lines.append("tags:")
    for t in section.tags:
        lines.append(f"  - {yaml_quote(t)}")

    lines.append("---")
    return "\n".join(lines)


def format_guideline_markdown(section: GuidelineSection) -> str:
    """Format full markdown document for a Technique + Form Guideline note."""
    fm = format_guideline_frontmatter(section)
    art_sh = section.primary_arts.lower()

    lines = [fm, f"\n# {section.technique} {section.form} Guidelines\n"]

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

    # Dataview query section
    lines.append("---")
    lines.append("\n## Known Spells\n")
    lines.append("```dataview")
    lines.append('TABLE level as "Level", range as "R", duration as "D", target as "T", ritual as "Ritual"')
    lines.append('FROM "spells"')
    lines.append(f'WHERE technique = "{section.technique}" AND form = "{section.form}"')
    lines.append("SORT level ASC")
    lines.append("```\n")

    return "\n".join(lines)


def export_spells(
    source_path: Path | str,
    output_dir: Path | str,
) -> dict[str, int]:
    """Parse core rules and export individual Spell notes to output_dir/spells."""
    source = Path(source_path)
    target_root = Path(output_dir)

    spells_dir = target_root / "spells"
    spells_dir.mkdir(parents=True, exist_ok=True)

    spells = extract_spells(source)

    for spell in spells:
        file_path = spells_dir / spell.filename
        content = format_spell_markdown(spell)
        file_path.write_text(content, encoding="utf-8")

    return {"spells": len(spells)}


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
