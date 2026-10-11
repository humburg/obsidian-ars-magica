# SPDX-License-Identifier: MIT
"""Unit tests for Obsidian Bases configuration generators."""

from obsidian_ars_magica.bases import (
    format_guideline_bases_block,
    generate_abilities_base,
    generate_flaws_base,
    generate_spells_base,
    generate_virtues_base,
)


def test_format_guideline_bases_block():
    block = format_guideline_bases_block("Creo", "Ignem")
    assert block.startswith("```base\n")
    assert block.endswith("```")

    # Filters
    assert 'file.inFolder("spells")' in block
    assert "'technique == \"Creo\"'" in block
    assert "'form == \"Ignem\"'" in block

    # Properties & First column category name
    assert "file.name:\n    displayName: Spell" in block
    assert "level:\n    displayName: Level" in block
    assert "range:\n    displayName: R" in block
    assert "duration:\n    displayName: D" in block
    assert "target:\n    displayName: T" in block
    assert "ritual:\n    displayName: Ritual" in block

    # Views
    assert 'name: "Known Spells"' in block
    assert "type: table" in block
    assert "- file.name" in block
    assert "column: level" in block
    assert "direction: ASC" in block


def test_generate_spells_base():
    content = generate_spells_base()
    assert 'file.inFolder("spells")' in content

    # First column category name
    assert "file.name:\n    displayName: Spell" in content
    assert "technique:\n    displayName: Technique" in content
    assert "form:\n    displayName: Form" in content
    assert "level:\n    displayName: Level" in content

    # Views
    assert 'name: "All Spells"' in content
    assert 'name: "By Arts"' in content
    assert 'name: "Ritual Spells"' in content
    assert "groupBy:\n      property: arts" in content
    assert "'ritual == true'" in content


def test_generate_virtues_base():
    content = generate_virtues_base()
    assert 'file.inFolder("virtues")' in content
    assert "file.name:\n    displayName: Virtue" in content
    assert "cost:\n    displayName: Cost" in content
    assert 'name: "All Virtues"' in content
    assert 'name: "By Cost"' in content
    assert "groupBy:\n      property: cost" in content


def test_generate_flaws_base():
    content = generate_flaws_base()
    assert 'file.inFolder("flaws")' in content
    assert "file.name:\n    displayName: Flaw" in content
    assert "cost:\n    displayName: Cost" in content
    assert 'name: "All Flaws"' in content
    assert 'name: "By Cost"' in content
    assert "groupBy:\n      property: cost" in content


def test_generate_abilities_base():
    content = generate_abilities_base()
    assert 'file.inFolder("abilities")' in content
    assert "file.name:\n    displayName: Ability" in content
    assert "type:\n    displayName: Type" in content
    assert "untrained:\n    displayName: Untrained" in content
    assert "specialties:\n    displayName: Specialties" in content
    assert 'name: "All Abilities"' in content
    assert 'name: "By Type"' in content
    assert "groupBy:\n      property: type" in content

