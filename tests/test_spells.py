"""Unit and integration tests for Spells extraction, calculation, and export."""

from pathlib import Path

from obsidian_ars_magica.models import SpellEntry
from obsidian_ars_magica.spells import (
    calculate_magnitudes_and_base,
    export_spells,
    extract_spells,
    format_spell_frontmatter,
    format_spell_markdown,
    parse_rdt_line,
    parse_requisites_line,
)

CORE_RULES_PATH = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)


def test_parse_rdt_line_standard():
    r, r_mag, d, d_mag, t, t_mag, ritual = parse_rdt_line("R: Touch, D: Sun, T: Ind")
    assert r == "Touch"
    assert r_mag == 1
    assert d == "Sun"
    assert d_mag == 2
    assert t == "Individual"
    assert t_mag == 0
    assert not ritual


def test_parse_rdt_line_ritual():
    r, r_mag, d, d_mag, t, t_mag, ritual = parse_rdt_line(
        "R: Touch, D: Mom, T: Ind, Ritual<br>"
    )
    assert r == "Touch"
    assert r_mag == 1
    assert d == "Momentary"
    assert d_mag == 0
    assert t == "Individual"
    assert t_mag == 0
    assert ritual is True


def test_parse_rdt_line_arcane_connection_and_boundary():
    r, r_mag, d, d_mag, t, t_mag, ritual = parse_rdt_line(
        "R: Arc, D: Year, T: Bound, Ritual"
    )
    assert r == "Arcane Connection"
    assert r_mag == 4
    assert d == "Year"
    assert d_mag == 4
    assert t == "Boundary"
    assert t_mag == 4
    assert ritual is True


def test_parse_rdt_line_typo_eve_for_eye():
    r, r_mag, d, d_mag, t, t_mag, ritual = parse_rdt_line("R: Eve, D: Mom, T: Ind")
    assert r == "Eye"
    assert r_mag == 1
    assert d == "Momentary"
    assert d_mag == 0
    assert t == "Individual"
    assert t_mag == 0
    assert not ritual


def test_parse_rdt_line_punctuation_anomalies():
    # Missing comma before D: or T:
    r, r_mag, d, d_mag, t, t_mag, ritual = parse_rdt_line(
        "R: Voice, D: Conc T: Ind<br>"
    )
    assert r == "Voice"
    assert r_mag == 2
    assert d == "Concentration"
    assert d_mag == 1
    assert t == "Individual"
    assert t_mag == 0
    assert not ritual



def test_parse_requisites_line():
    tech_reqs, form_reqs = parse_requisites_line("Req: Rego<br>")
    assert tech_reqs == ["Rego"]
    assert form_reqs == []

    tech_reqs2, form_reqs2 = parse_requisites_line("Req: Ignem, Mentem")
    assert tech_reqs2 == []
    assert form_reqs2 == ["Ignem", "Mentem"]

    tech_reqs3, form_reqs3 = parse_requisites_line("Req: Perdo and Terram")
    assert tech_reqs3 == ["Perdo"]
    assert form_reqs3 == ["Terram"]


def test_calculate_magnitudes_and_base_standard():
    body = (
        "Creates a horse, which is normal in every way.\n"
        "(Base 15, +1 Touch, +2 Sun, +1 size)"
    )
    base, add_mag, add_mods, raw_design = calculate_magnitudes_and_base(
        body_text=body,
        level=35,
        range_mag=1,
        duration_mag=2,
        target_mag=0,
    )
    assert base == 15
    assert add_mag == 1
    assert "+1 size" in add_mods
    assert "(Base 15, +1 Touch, +2 Sun, +1 size)" == raw_design


def test_calculate_magnitudes_and_base_negative():
    body = (
        "Reattaches a severed limb.\n"
        "(Base 25, +1 Touch, -1 because the old limb is needed)"
    )
    base, add_mag, add_mods, raw_design = calculate_magnitudes_and_base(
        body_text=body,
        level=25,
        range_mag=1,
        duration_mag=0,
        target_mag=0,
    )
    assert base == 25
    assert add_mag == -1
    assert "-1 because the old limb is needed" in add_mods
    assert "(Base 25, +1 Touch, -1 because the old limb is needed)" in raw_design



def test_spell_entry_model_properties():
    spell = SpellEntry(
        name="Curse of the Ravenous Swarm",
        technique="Creo",
        form="Animal",
        level=50,
        range="Touch",
        duration="Moon",
        target="Group",
        ritual=True,
        technique_requisites=["Rego"],
        base_level=5,
        range_magnitude=1,
        duration_magnitude=3,
        target_magnitude=2,
        additional_magnitudes=3,
    )

    assert spell.filename == "Curse-of-the-Ravenous-Swarm.md"
    assert spell.primary_arts == "CrAn"
    assert spell.arts_shorthand == "CrAn(Re)"
    assert "Curse of the Ravenous Swarm" in spell.aliases
    assert "CrAn 50" in spell.aliases
    assert "CrAn(Re) 50" in spell.aliases
    assert "spell" in spell.tags
    assert "ritual" in spell.tags
    assert "requisite/rego" in spell.tags


def test_format_spell_frontmatter_and_markdown():
    spell = SpellEntry(
        name="Soothe Pains of the Beast",
        technique="Creo",
        form="Animal",
        level=20,
        range="Touch",
        duration="Momentary",
        target="Individual",
        ritual=True,
        base_level=15,
        range_magnitude=1,
        duration_magnitude=0,
        target_magnitude=0,
        additional_magnitudes=0,
        body="The spell cures one Light Wound suffered by the animal.\n\n(Base level 15, +1 Touch)",
    )

    fm = format_spell_frontmatter(spell)
    assert 'name: "Soothe Pains of the Beast"' in fm
    assert "level: 20" in fm
    assert 'range: "Touch"' in fm
    assert "ritual: true" in fm
    assert "total_magnitudes: 1" in fm
    assert 'guideline: "[[Creo-Animal-Guidelines#Level 15]]"' in fm

    md = format_spell_markdown(spell)
    assert "# Soothe Pains of the Beast" in md
    assert "> [!metadata] **CrAn 20** | **Ritual**" in md
    assert "> - **R:** Touch, **D:** Momentary, **T:** Individual" in md
    assert "> - **Base:** 15 | **Total Magnitudes:** +1 (+1 Touch)" in md
    assert "[[Creo-Animal-Guidelines#Level 15|Creo Animal Base 15]]" in md


def test_extract_all_spells_from_core_rules():
    assert CORE_RULES_PATH.exists()
    spells = extract_spells(CORE_RULES_PATH)
    # Exactly 360 spells in Core Rules
    assert len(spells) == 360

    # Verify presence of specific canonical spells
    names = {s.name: s for s in spells}
    assert "Soothe Pains of the Beast" in names
    assert "Curse of the Ravenous Swarm" in names
    assert "Aegis of the Hearth" in names
    assert "The Shadow of Life Renewed" in names
    assert "Bind Wound" in names

    # Verify Aegis of the Hearth
    aegis = names["Aegis of the Hearth"]
    assert aegis.technique == "Rego"
    assert aegis.form == "Vim"
    assert aegis.level == "General"
    assert aegis.range == "Touch"
    assert aegis.duration == "Year"
    assert aegis.target == "Boundary"
    assert aegis.ritual is True


def test_export_spells(tmp_path):
    counts = export_spells(CORE_RULES_PATH, tmp_path)
    assert counts["spells"] == 360

    spells_dir = tmp_path / "spells"
    assert spells_dir.exists()
    assert (spells_dir / "Soothe-Pains-of-the-Beast.md").exists()
    assert (spells_dir / "Aegis-of-the-Hearth.md").exists()

