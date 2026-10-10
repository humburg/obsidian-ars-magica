"""Unit and integration tests for Virtues and Flaws extraction."""

from pathlib import Path

import pytest

from obsidian_ars_magica.models import VirtueFlawEntry
from obsidian_ars_magica.virtues_flaws import (
    export_virtues_and_flaws,
    extract_virtues_and_flaws,
    format_entry_markdown,
    parse_qualifiers,
)

CORE_RULES_PATH = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)


def test_parse_qualifiers_standard():
    res1 = parse_qualifiers("*Minor, General*<br>")
    assert res1["cost"] == "Minor"
    assert res1["types"] == ["General"]
    assert res1["properties"] == []

    res2 = parse_qualifiers("*Major, Hermetic*<br>")
    assert res2["cost"] == "Major"
    assert res2["types"] == ["Hermetic"]
    assert res2["properties"] == []

    res3 = parse_qualifiers("*Free, Social Status*<br>")
    assert res3["cost"] == "Free"
    assert res3["types"] == ["Social Status"]
    assert res3["properties"] == []


def test_parse_qualifiers_inverted_order():
    # In 'Prestigious Student', the text is '*General, Minor*<br>'
    res = parse_qualifiers("*General, Minor*<br>")
    assert res["cost"] == "Minor"
    assert res["types"] == ["General"]
    assert res["properties"] == []


def test_parse_qualifiers_dual_cost():
    res1 = parse_qualifiers("*Major or Minor, Personality*<br>")
    assert res1["cost"] == "Major or Minor"
    assert res1["types"] == ["Personality"]
    assert res1["properties"] == []

    res2 = parse_qualifiers("*Minor or Major, Hermetic*<br>")
    assert res2["cost"] == "Minor or Major"
    assert res2["types"] == ["Hermetic"]
    assert res2["properties"] == []


def test_parse_qualifiers_compound_and_multiple_types():
    res1 = parse_qualifiers("*Minor, General and Hermetic*<br>")
    assert res1["cost"] == "Minor"
    assert res1["types"] == ["General and Hermetic"]
    assert res1["properties"] == []

    # 'Sufi' has multiple types separated by comma
    res2 = parse_qualifiers("*Minor, Social Status, Supernatural*<br>")
    assert res2["cost"] == "Minor"
    assert res2["types"] == ["Social Status", "Supernatural"]
    assert res2["properties"] == []


def test_parse_qualifiers_with_properties():
    res1 = parse_qualifiers("*Minor, General, Tainted*<br>")
    assert res1["cost"] == "Minor"
    assert res1["types"] == ["General"]
    assert res1["properties"] == ["Tainted"]

    res2 = parse_qualifiers("*Free, Social Status, animals only*<br>")
    assert res2["cost"] == "Free"
    assert res2["types"] == ["Social Status"]
    assert res2["properties"] == ["animals only"]


def test_model_filename_sanitization():
    e1 = VirtueFlawEntry(
        name="Major Magical Focus",
        category="Virtue",
        cost="Major",
    )
    assert e1.filename == "Major-Magical-Focus.md"

    e2 = VirtueFlawEntry(
        name="Gentleman/woman",
        category="Virtue",
        cost="Minor",
    )
    assert e2.filename == "Gentleman-woman.md"

    e3 = VirtueFlawEntry(
        name="(Land) Regio Network",
        category="Virtue",
        cost="Minor",
    )
    assert e3.filename == "Land-Regio-Network.md"

    e4 = VirtueFlawEntry(
        name="'Alim",
        category="Virtue",
        cost="Minor",
    )
    assert e4.filename == "Alim.md"

    e5 = VirtueFlawEntry(
        name="Horrifying Appearance – Snake Legs",
        category="Flaw",
        cost="Major",
    )
    assert e5.filename == "Horrifying-Appearance-Snake-Legs.md"


def test_model_tags():
    e = VirtueFlawEntry(
        name="Mentored by Demons",
        category="Virtue",
        cost="Minor",
        types=["General"],
        properties=["Tainted"],
    )
    assert e.tags == ["virtue", "general", "minor", "tainted"]

    e_compound = VirtueFlawEntry(
        name="Sufi",
        category="Virtue",
        cost="Minor",
        types=["Social Status", "Supernatural"],
        properties=[],
    )
    assert e_compound.tags == ["virtue", "social-status", "supernatural", "minor"]


def test_format_entry_markdown():
    entry = VirtueFlawEntry(
        name="Mentored by Demons",
        category="Virtue",
        cost="Minor",
        types=["General"],
        properties=["Tainted"],
        body="You were taught by demons.\n\nBe careful.",
    )
    md = format_entry_markdown(entry)

    assert md.startswith("---\n")
    assert 'name: "Mentored by Demons"' in md
    assert 'category: "Virtue"' in md
    assert 'cost: "Minor"' in md
    assert 'type:\n  - "General"' in md
    assert 'properties:\n  - "Tainted"' in md
    assert 'aliases:\n  - "Mentored by Demons"' in md
    assert "tags:\n  - \"virtue\"\n  - \"general\"\n  - \"minor\"\n  - \"tainted\"" in md
    assert "\n# Mentored by Demons\n\n" in md
    assert md.endswith("You were taught by demons.\n\nBe careful.\n")


def test_extract_virtues_and_flaws_synthetic(tmp_path: Path):
    sample_content = """# Chapter 4: Virtues and Flaws

## List of Virtues
[Sample Virtue](#sample-virtue)

## Virtues

#### Sample Virtue
*Minor, General*<br>
This is the description of sample virtue.

It spans two paragraphs.

#### Second Virtue
*Major, Hermetic, Tainted*<br>
Another virtue description.

## List of Flaws
[Sample Flaw](#sample-flaw)

## Flaws

#### Sample Flaw
*Major, Story*<br>
A terrible flaw.

# Chapter 5: Abilities
Abilities section begins.
"""
    doc_path = tmp_path / "sample.md"
    doc_path.write_text(sample_content, encoding="utf-8")

    virtues, flaws = extract_virtues_and_flaws(doc_path)

    assert len(virtues) == 2
    assert virtues[0].name == "Sample Virtue"
    assert virtues[0].cost == "Minor"
    assert virtues[0].types == ["General"]
    assert "This is the description of sample virtue." in virtues[0].body
    assert virtues[0].filename == "Sample-Virtue.md"

    assert virtues[1].name == "Second Virtue"
    assert virtues[1].cost == "Major"
    assert virtues[1].types == ["Hermetic"]
    assert virtues[1].properties == ["Tainted"]

    assert len(flaws) == 1
    assert flaws[0].name == "Sample Flaw"
    assert flaws[0].cost == "Major"
    assert flaws[0].types == ["Story"]


@pytest.mark.skipif(not CORE_RULES_PATH.exists(), reason="Core rules file not found")
def test_extract_virtues_and_flaws_core_rules():
    virtues, flaws = extract_virtues_and_flaws(CORE_RULES_PATH)

    assert len(virtues) == 318
    assert len(flaws) == 308

    # Verify no empty bodies
    for v in virtues:
        assert v.name
        assert v.cost
        assert v.types
        assert len(v.body) > 20, f"Virtue body too short: {v.name}"

    for f in flaws:
        assert f.name
        assert f.cost
        assert f.types
        assert len(f.body) > 20, f"Flaw body too short: {f.name}"

    # Verify 0 filename collisions within each category
    v_filenames = [v.filename for v in virtues]
    assert len(v_filenames) == len(set(v_filenames))

    f_filenames = [f.filename for f in flaws]
    assert len(f_filenames) == len(set(f_filenames))


@pytest.mark.skipif(not CORE_RULES_PATH.exists(), reason="Core rules file not found")
def test_export_virtues_and_flaws(tmp_path: Path):
    counts = export_virtues_and_flaws(CORE_RULES_PATH, tmp_path)

    assert counts["virtues"] == 318
    assert counts["flaws"] == 308

    virtues_dir = tmp_path / "virtues"
    flaws_dir = tmp_path / "flaws"

    assert len(list(virtues_dir.glob("*.md"))) == 318
    assert len(list(flaws_dir.glob("*.md"))) == 308

    sample_virtue = virtues_dir / "Major-Magical-Focus.md"
    assert sample_virtue.exists()
    content = sample_virtue.read_text(encoding="utf-8")
    assert 'name: "Major Magical Focus"' in content
    assert "# Major Magical Focus" in content
    assert "> #### Sample Major Magical Foci" in content
