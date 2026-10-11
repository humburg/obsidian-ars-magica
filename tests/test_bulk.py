# SPDX-License-Identifier: MIT
"""Unit and integration tests for bulk extraction."""

from pathlib import Path

import pytest

from obsidian_ars_magica.bulk import export_all


def test_export_all_aggregates_counts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify export_all delegates to all 4 exporters and computes total."""
    source_file = tmp_path / "mock_rules.md"
    source_file.write_text("# Mock rules", encoding="utf-8")
    output_dir = tmp_path / "out"

    calls = []

    def mock_vf(src: Path, out: Path) -> dict[str, int]:
        calls.append(("vf", src, out))
        return {"virtues": 10, "flaws": 5}

    def mock_ab(src: Path, out: Path) -> dict[str, int]:
        calls.append(("ab", src, out))
        return {"abilities": 20}

    def mock_sp(src: Path, out: Path) -> dict[str, int]:
        calls.append(("sp", src, out))
        return {"spells": 30}

    def mock_gl(src: Path, out: Path) -> dict[str, int]:
        calls.append(("gl", src, out))
        return {"guidelines": 40}

    monkeypatch.setattr("obsidian_ars_magica.bulk.export_virtues_and_flaws", mock_vf)
    monkeypatch.setattr("obsidian_ars_magica.bulk.export_abilities", mock_ab)
    monkeypatch.setattr("obsidian_ars_magica.bulk.export_spells", mock_sp)
    monkeypatch.setattr("obsidian_ars_magica.bulk.export_guidelines", mock_gl)

    result = export_all(source_file, output_dir)

    assert result == {
        "virtues": 10,
        "flaws": 5,
        "abilities": 20,
        "spells": 30,
        "guidelines": 40,
        "total": 105,
    }

    assert len(calls) == 4
    assert calls[0] == ("vf", source_file, output_dir)
    assert calls[1] == ("ab", source_file, output_dir)
    assert calls[2] == ("sp", source_file, output_dir)
    assert calls[3] == ("gl", source_file, output_dir)
    assert output_dir.exists()


def test_export_all_progress_callback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify progress_callback receives notifications for all stages."""
    source_file = tmp_path / "mock_rules.md"
    source_file.write_text("# Mock rules", encoding="utf-8")
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "obsidian_ars_magica.bulk.export_virtues_and_flaws",
        lambda src, out: {"virtues": 1, "flaws": 2},
    )
    monkeypatch.setattr(
        "obsidian_ars_magica.bulk.export_abilities",
        lambda src, out: {"abilities": 3},
    )
    monkeypatch.setattr(
        "obsidian_ars_magica.bulk.export_spells",
        lambda src, out: {"spells": 4},
    )
    monkeypatch.setattr(
        "obsidian_ars_magica.bulk.export_guidelines",
        lambda src, out: {"guidelines": 5},
    )

    stage_events = []

    def on_progress(stage: str, counts: dict[str, int]) -> None:
        stage_events.append((stage, counts))

    result = export_all(str(source_file), str(output_dir), progress_callback=on_progress)

    assert result["total"] == 15
    assert len(stage_events) == 4
    assert stage_events[0] == ("virtues_flaws", {"virtues": 1, "flaws": 2})
    assert stage_events[1] == ("abilities", {"abilities": 3})
    assert stage_events[2] == ("spells", {"spells": 4})
    assert stage_events[3] == ("guidelines", {"guidelines": 5})


SYNTHETIC_CORE_RULES = """# Chapter 4: Virtues and Flaws

## List of Virtues
[Affinity with Art](#affinity-with-art)

## Virtues

#### Affinity with Art
*Minor, Hermetic*<br>
Study totals with that Art are increased.

## List of Flaws
[Afflicted Tongue](#afflicted-tongue)

## Flaws

#### Afflicted Tongue
*Minor, Personality*<br>
You have difficulty speaking.

# Chapter 5: Abilities

## Abilities by Type

#### General Abilities

[Athletics](#athletics)<br>

## Ability List

#### Athletics
Running, jumping, and climbing.<br>
*Specialties:* running, jumping. (General)

# Chapter 6: Covenants

# Chapter 9: Spells

## Animal Spells

### Creo Animal Guidelines

Guidelines for Creo Animal.

| Level | Creo Animal Guideline |
| ----- | --------------------- |
| 5 | • Create a tiny insect |

### Creo Animal Spells

#### LEVEL 10

##### Beast of Outlandish Size
R: Touch, D: Sun, T: Ind<br>
Increases the size of a beast.<br>
(Base 5, +1 Touch, +2 Sun)

# Chapter 10: Long Term Events
"""


def test_export_all_synthetic_end_to_end(tmp_path: Path):
    """End-to-end integration test extracting all content from a synthetic core rules file."""
    source_file = tmp_path / "synthetic_rules.md"
    source_file.write_text(SYNTHETIC_CORE_RULES, encoding="utf-8")
    output_dir = tmp_path / "vault"

    counts = export_all(source_file, output_dir)

    assert counts["virtues"] == 1
    assert counts["flaws"] == 1
    assert counts["abilities"] == 1
    assert counts["spells"] == 1
    assert counts["guidelines"] == 1
    assert counts["total"] == 5

    # Check generated files in each subfolder
    assert (output_dir / "virtues" / "Affinity-with-Art.md").exists()
    assert (output_dir / "flaws" / "Afflicted-Tongue.md").exists()
    assert (output_dir / "abilities" / "Athletics.md").exists()
    assert (output_dir / "spells" / "Beast-of-Outlandish-Size.md").exists()
    assert (output_dir / "guidelines" / "Creo-Animal-Guidelines.md").exists()

    # Check generated standalone .base files
    assert (output_dir / "spells.base").exists()
    assert (output_dir / "virtues.base").exists()
    assert (output_dir / "flaws.base").exists()
    assert (output_dir / "abilities.base").exists()
    assert not (output_dir / "guidelines.base").exists()

