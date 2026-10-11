# SPDX-License-Identifier: MIT
"""Unit and integration tests for Abilities extraction and export."""

from pathlib import Path

import pytest

from obsidian_ars_magica.abilities import (
    export_abilities,
    extract_abilities,
    format_ability_frontmatter,
    format_ability_markdown,
    split_specialties,
)
from obsidian_ars_magica.models import AbilityEntry

CORE_RULES_PATH = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)


def test_split_specialties_standard():
    res = split_specialties("falconry, specific animals. (General)")
    assert res == ["falconry", "specific animals"]


def test_split_specialties_with_parentheses():
    raw = (
        "searching for a particular kind of thing (water, gold, etc.), "
        "searching in a particular kind of place. (Supernatural)"
    )
    res = split_specialties(raw)
    assert res == [
        "searching for a particular kind of thing (water, gold, etc.)",
        "searching in a particular kind of place",
    ]


def test_split_specialties_with_html_br_and_colons():
    raw = "<br>*Specialties:* cauterization, diagnosis, binding wounds, setting bones."
    res = split_specialties(raw)
    assert res == ["cauterization", "diagnosis", "binding wounds", "setting bones"]


def test_split_specialties_empty():
    assert split_specialties("") == []
    assert split_specialties("   ") == []


def test_ability_model_filename():
    e1 = AbilityEntry(name="Animal Handling", ability_type="General")
    assert e1.filename == "Animal-Handling.md"

    e2 = AbilityEntry(name="(Area) Lore", ability_type="General")
    assert e2.filename == "Area-Lore.md"

    e3 = AbilityEntry(name="Theology: Christian", ability_type="Academic")
    assert e3.filename == "Theology-Christian.md"

    e4 = AbilityEntry(name="Craft (Type)", ability_type="General")
    assert e4.filename == "Craft-Type.md"


def test_ability_model_tags_and_aliases():
    e1 = AbilityEntry(name="Animal Handling", ability_type="General")
    assert e1.tags == ["ability", "general"]
    assert e1.aliases == ["Animal Handling"]

    e2 = AbilityEntry(name="Chirurgy", ability_type="General")
    assert e2.tags == ["ability", "general"]
    assert e2.aliases == ["Chirurgy", "Chirurgy (kie-RUHR-gee)"]


def test_format_ability_frontmatter():
    entry = AbilityEntry(
        name="Animal Handling",
        ability_type="General",
        specialties=["falconry", "specific animals"],
        untrained=True,
    )
    fm = format_ability_frontmatter(entry)
    assert fm.startswith("---\n")
    assert 'name: "Animal Handling"' in fm
    assert 'category: "Ability"' in fm
    assert 'type: "General"' in fm
    assert "specialties:\n  - \"falconry\"\n  - \"specific animals\"" in fm
    assert "untrained: true" in fm
    assert fm.endswith("---")


def test_format_ability_markdown():
    entry = AbilityEntry(
        name="Animal Handling",
        ability_type="General",
        specialties=["falconry", "specific animals"],
        untrained=True,
        body="Care and use of animals, including raising, tending, grooming, and healing them.\n\n*Specialties:* falconry, specific animals. (General)",
    )
    md = format_ability_markdown(entry)

    assert md.startswith("---\n")
    assert 'name: "Animal Handling"' in md
    assert 'category: "Ability"' in md
    assert 'type: "General"' in md
    assert "specialties:\n  - \"falconry\"\n  - \"specific animals\"" in md
    assert "untrained: true" in md
    assert "aliases:\n  - \"Animal Handling\"" in md
    assert "tags:\n  - \"ability\"\n  - \"general\"" in md
    assert "\n# Animal Handling\n\n" in md
    assert "*Specialties:* falconry, specific animals. (General)" in md


def test_extract_abilities_synthetic(tmp_path: Path):
    sample_content = r"""# Chapter 5: Abilities

## Abilities by Type

#### General Abilities

[Animal Handling](#animal-handling)<br>
[(Area) Lore\*](#area-lore)<br>

#### Supernatural Abilities

[Hex\*](#hex)<br>

## Ability List

#### Animal Handling
Care and use of animals.<br>
*Specialties:* falconry, specific animals. (General)

#### (Area) Lore\*
Knowledge of one particular region.<br>
*Specialties:* geography, history. (General)

#### Hex\*
The character has the power to bring about injury.

#### Hex Delay Modifiers

| Delay | Modifier |
| ----- | -------- |
| day   | -6       |

Specialties: duration, effect. (Supernatural)

#### Hex Effects

| Ease Factor | Severity |
| ----------- | -------- |
| 6+          | Minor    |

# Chapter 6: Covenants
"""
    doc_path = tmp_path / "sample_abilities.md"
    doc_path.write_text(sample_content, encoding="utf-8")

    abilities = extract_abilities(doc_path)

    assert len(abilities) == 3

    # Check Animal Handling
    a1 = abilities[0]
    assert a1.name == "Animal Handling"
    assert a1.ability_type == "General"
    assert a1.untrained is True
    assert a1.specialties == ["falconry", "specific animals"]
    assert "Care and use of animals." in a1.body

    # Check (Area) Lore
    a2 = abilities[1]
    assert a2.name == "(Area) Lore"
    assert a2.ability_type == "General"
    assert a2.untrained is False
    assert a2.specialties == ["geography", "history"]

    # Check Hex (ensuring Hex Delay Modifiers and Hex Effects are absorbed into body)
    a3 = abilities[2]
    assert a3.name == "Hex"
    assert a3.ability_type == "Supernatural"
    assert a3.untrained is False
    assert a3.specialties == ["duration", "effect"]
    assert "#### Hex Delay Modifiers" in a3.body
    assert "#### Hex Effects" in a3.body
    assert "| day   | -6       |" in a3.body


@pytest.mark.skipif(not CORE_RULES_PATH.exists(), reason="Core rules file not found")
def test_extract_abilities_core_rules():
    abilities = extract_abilities(CORE_RULES_PATH)

    # Exactly 78 abilities
    assert len(abilities) == 78

    # Unique filenames
    filenames = [a.filename for a in abilities]
    assert len(filenames) == len(set(filenames))

    # Type counts match canonical categories
    type_counts: dict[str, int] = {}
    for a in abilities:
        type_counts[a.ability_type] = type_counts.get(a.ability_type, 0) + 1
        assert a.name
        assert a.ability_type
        assert len(a.body) > 20, f"Ability body too short: {a.name}"

    assert type_counts["General"] == 29
    assert type_counts["Academic"] == 12
    assert type_counts["Arcane"] == 12
    assert type_counts["Martial"] == 4
    assert type_counts["Supernatural"] == 21

    # Check specific complex abilities
    by_name = {a.name: a for a in abilities}

    hex_ability = by_name["Hex"]
    assert hex_ability.untrained is False
    assert "#### Hex Delay Modifiers" in hex_ability.body
    assert "#### Hex Effects" in hex_ability.body
    assert len(hex_ability.specialties) >= 3

    art_of_memory = by_name["Art of Memory"]
    assert art_of_memory.untrained is False
    assert "#### Memorization Ease Factors" in art_of_memory.body

    corpse_magic = by_name["Corpse Magic"]
    assert corpse_magic.untrained is False
    assert "#### Corpse Magic Ease Factor Outcome" in corpse_magic.body
    assert "kings" in corpse_magic.specialties

    chirurgy = by_name["Chirurgy"]
    assert chirurgy.untrained is False
    assert "cauterization" in chirurgy.specialties
    assert "Chirurgy (kie-RUHR-gee)" in chirurgy.aliases

    animal_handling = by_name["Animal Handling"]
    assert animal_handling.untrained is True


@pytest.mark.skipif(not CORE_RULES_PATH.exists(), reason="Core rules file not found")
def test_export_abilities(tmp_path: Path):
    counts = export_abilities(CORE_RULES_PATH, tmp_path)

    assert counts["abilities"] == 78

    abilities_dir = tmp_path / "abilities"
    files = list(abilities_dir.glob("*.md"))
    assert len(files) == 78

    # Check sample file
    sample = abilities_dir / "Animal-Handling.md"
    assert sample.exists()
    content = sample.read_text(encoding="utf-8")
    assert 'name: "Animal Handling"' in content
    assert 'type: "General"' in content
    assert "untrained: true" in content
    assert "# Animal Handling" in content
    assert "*Specialties:* falconry, specific animals. (General)" in content
