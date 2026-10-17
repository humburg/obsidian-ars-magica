# SPDX-License-Identifier: MIT
"""Package initialization for obsidian_ars_magica."""

from obsidian_ars_magica.abilities import (
    export_abilities,
    extract_abilities,
    format_ability_frontmatter,
    format_ability_markdown,
    parse_abilities,
    split_specialties,
)
from obsidian_ars_magica.bases import (
    format_guideline_bases_block,
    generate_abilities_base,
    generate_flaws_base,
    generate_spells_base,
    generate_virtues_base,
)
from obsidian_ars_magica.bulk import export_all
from obsidian_ars_magica.formatters import dump_frontmatter, sanitize_filename, yaml_quote
from obsidian_ars_magica.guidelines import (
    export_guidelines,
    extract_guidelines,
    format_guideline_frontmatter,
    format_guideline_markdown,
    parse_guidelines,
)
from obsidian_ars_magica.models import (
    FORMS,
    TECH_ABBREV,
    TECHNIQUES,
    AbilityEntry,
    BaseNoteEntry,
    GuidelineLevelEntry,
    GuidelineSection,
    SpellEntry,
    VirtueFlawEntry,
)
from obsidian_ars_magica.spells import (
    calculate_magnitudes_and_base,
    export_spells,
    extract_spells,
    format_spell_frontmatter,
    format_spell_markdown,
    parse_rdt_line,
    parse_requisites_line,
    parse_spells,
    spell_level_to_magnitude,
)
from obsidian_ars_magica.virtues_flaws import (
    export_virtues_and_flaws,
    extract_virtues_and_flaws,
    format_entry_markdown,
    format_frontmatter,
    parse_qualifiers,
    parse_virtues_and_flaws,
)

__version__ = "0.1.0"

__all__ = [
    "FORMS",
    "TECHNIQUES",
    "TECH_ABBREV",
    "AbilityEntry",
    "BaseNoteEntry",
    "GuidelineLevelEntry",
    "GuidelineSection",
    "SpellEntry",
    "VirtueFlawEntry",
    "calculate_magnitudes_and_base",
    "dump_frontmatter",
    "export_abilities",
    "export_all",
    "export_guidelines",
    "export_spells",
    "export_virtues_and_flaws",
    "extract_abilities",
    "extract_guidelines",
    "extract_spells",
    "extract_virtues_and_flaws",
    "format_ability_frontmatter",
    "format_ability_markdown",
    "format_entry_markdown",
    "format_frontmatter",
    "format_guideline_bases_block",
    "format_guideline_frontmatter",
    "format_guideline_markdown",
    "format_spell_frontmatter",
    "format_spell_markdown",
    "generate_abilities_base",
    "generate_flaws_base",
    "generate_spells_base",
    "generate_virtues_base",
    "parse_abilities",
    "parse_guidelines",
    "parse_qualifiers",
    "parse_rdt_line",
    "parse_requisites_line",
    "parse_spells",
    "parse_virtues_and_flaws",
    "sanitize_filename",
    "spell_level_to_magnitude",
    "split_specialties",
    "yaml_quote",
]
