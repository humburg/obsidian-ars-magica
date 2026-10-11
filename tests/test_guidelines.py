# SPDX-License-Identifier: MIT
"""Unit and integration tests for Spell Guidelines extraction, formatting, and export."""

from pathlib import Path

from obsidian_ars_magica.models import GuidelineLevelEntry, GuidelineSection
from obsidian_ars_magica.spells import (
    export_guidelines,
    extract_guidelines,
    format_guideline_frontmatter,
    format_guideline_markdown,
)

CORE_RULES_PATH = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)


def test_guideline_model_properties():
    sec = GuidelineSection(
        technique="Creo",
        form="Animal",
        intro_body="Most Animal spells cannot be used with Personal range.",
        guidelines_by_level=[
            GuidelineLevelEntry(level=1, bullets=["Give an animal a +1 bonus to Recovery rolls"]),
            GuidelineLevelEntry(level=5, bullets=["Create an animal product", "Create an insect"]),
        ],
    )

    assert sec.primary_arts == "CrAn"
    assert sec.filename == "Creo-Animal-Guidelines.md"
    assert "Creo Animal Guidelines" in sec.aliases
    assert "CrAn Guidelines" in sec.aliases
    assert "spell-guidelines" in sec.tags
    assert "creo" in sec.tags
    assert "animal" in sec.tags
    assert "cran" in sec.tags


def test_format_guideline_markdown():
    sec = GuidelineSection(
        technique="Creo",
        form="Animal",
        intro_body="Introductory rules text.",
        guidelines_by_level=[
            GuidelineLevelEntry(level=1, bullets=["Give an animal a +1 bonus to Recovery rolls"]),
            GuidelineLevelEntry(level=5, bullets=["Create an insect or similar bug"]),
        ],
    )

    fm = format_guideline_frontmatter(sec)
    assert 'name: "Creo Animal Guidelines"' in fm
    assert 'category: "Spell Guidelines"' in fm

    md = format_guideline_markdown(sec)
    assert 'name: "Creo Animal Guidelines"' in md
    assert 'arts: "CrAn"' in md

    assert "# Creo Animal Guidelines" in md
    assert "Introductory rules text." in md
    assert "### Level 1" in md
    assert "- Give an animal a +1 bonus to Recovery rolls ^cran-1-1" in md
    assert "### Level 5" in md
    assert "- Create an insect or similar bug ^cran-5-1" in md
    assert "## Known Spells" in md
    assert "```base" in md
    assert 'file.inFolder("spells")' in md
    assert "'technique == \"Creo\"'" in md
    assert "formulas:\n  name: 'file.asLink(note.name)'" in md
    assert "formula.name:\n    displayName: Spell" in md
    assert "file.name" not in md
    assert "```dataview" not in md


def test_extract_all_guidelines_from_core_rules():
    assert CORE_RULES_PATH.exists()
    guidelines = extract_guidelines(CORE_RULES_PATH)
    # Exactly 50 Technique + Form pairs
    assert len(guidelines) == 50

    # Verify all 5 Techniques and 10 Forms are represented
    seen_arts = {g.primary_arts for g in guidelines}
    assert len(seen_arts) == 50

    # Spot check Creo Animal
    cr_an = next(g for g in guidelines if g.primary_arts == "CrAn")
    assert cr_an.technique == "Creo"
    assert cr_an.form == "Animal"
    assert len(cr_an.guidelines_by_level) > 0
    # Spot check Rego Vim
    re_vi = next(g for g in guidelines if g.primary_arts == "ReVi")
    assert re_vi.technique == "Rego"
    assert re_vi.form == "Vim"
    assert any(entry.level == "General" for entry in re_vi.guidelines_by_level)


def test_export_guidelines(tmp_path):
    counts = export_guidelines(CORE_RULES_PATH, tmp_path)
    assert counts["guidelines"] == 50

    guidelines_dir = tmp_path / "guidelines"
    assert guidelines_dir.exists()
    assert (guidelines_dir / "Creo-Animal-Guidelines.md").exists()
    assert (guidelines_dir / "Rego-Vim-Guidelines.md").exists()
    assert len(list(guidelines_dir.glob("*.md"))) == 50

    # Ensure standalone guidelines.base is not created per design
    assert not (tmp_path / "guidelines.base").exists()

