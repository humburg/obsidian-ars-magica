# SPDX-License-Identifier: MIT
"""Unit and integration tests for the command-line interface."""

import runpy
import sys
from pathlib import Path

import pytest

from obsidian_ars_magica.cli import DEFAULT_OUTPUT, DEFAULT_SOURCE, main


def test_cli_help(capsys: pytest.CaptureFixture[str]):
    """Verify that --help displays prog name and subcommands."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "obsidian-ars-magica" in captured.out
    assert "extract-virtues-flaws" in captured.out
    assert "extract-abilities" in captured.out
    assert "extract-spells" in captured.out
    assert "extract-guidelines" in captured.out
    assert "extract-all" in captured.out


def test_cli_subcommand_help(capsys: pytest.CaptureFixture[str]):
    """Verify that extract-virtues-flaws --help displays options."""
    with pytest.raises(SystemExit) as exc_info:
        main(["extract-virtues-flaws", "--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "--source" in captured.out
    assert "--output" in captured.out


def test_cli_no_args(capsys: pytest.CaptureFixture[str]):
    """Verify that invoking CLI without subcommands exits with error code 2."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2

    captured = capsys.readouterr()
    assert "usage:" in captured.err.lower()


def test_cli_invalid_subcommand(capsys: pytest.CaptureFixture[str]):
    """Verify that invoking an unknown subcommand exits with error code 2."""
    with pytest.raises(SystemExit) as exc_info:
        main(["unknown-subcommand"])
    assert exc_info.value.code == 2

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err.lower()


def test_cli_source_not_found(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verify that missing source file reports error on stderr and returns 1."""
    nonexistent = tmp_path / "does_not_exist.md"
    exit_code = main(["extract-virtues-flaws", "--source", str(nonexistent)])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert f"Error: Source file does not exist: {nonexistent}" in captured.err


def test_cli_extract_virtues_flaws_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify successful execution with custom arguments and mocked exporter."""
    source_file = tmp_path / "rules.md"
    source_file.write_text("# Dummy rules", encoding="utf-8")
    output_dir = tmp_path / "custom_output"

    mock_counts = {"virtues": 12, "flaws": 8}
    calls = []

    def fake_export(src: Path, out: Path):
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr("obsidian_ars_magica.cli.export_virtues_and_flaws", fake_export)

    exit_code = main([
        "extract-virtues-flaws",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (source_file, output_dir)

    captured = capsys.readouterr()
    assert f"Reading source: {source_file}" in captured.out
    assert f"Exporting to:   {output_dir}" in captured.out
    assert f"Successfully extracted 12 Virtues to {output_dir / 'virtues'}" in captured.out
    assert f"Successfully extracted 8 Flaws to {output_dir / 'flaws'}" in captured.out


def test_cli_extract_virtues_flaws_defaults(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify that extract-virtues-flaws uses default paths when flags are omitted."""
    # Mock Path.exists so default path does not fail if not present in test env
    monkeypatch.setattr(Path, "exists", lambda self: True)

    mock_counts = {"virtues": 100, "flaws": 50}
    calls = []

    def fake_export(src: Path, out: Path):
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr("obsidian_ars_magica.cli.export_virtues_and_flaws", fake_export)

    exit_code = main(["extract-virtues-flaws"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (DEFAULT_SOURCE, DEFAULT_OUTPUT)

    captured = capsys.readouterr()
    assert f"Reading source: {DEFAULT_SOURCE}" in captured.out
    assert f"Exporting to:   {DEFAULT_OUTPUT}" in captured.out


def test_cli_argv_none_uses_sys_argv(monkeypatch: pytest.MonkeyPatch):
    """Verify that main(None) consumes arguments from sys.argv."""
    monkeypatch.setattr(sys, "argv", ["obsidian-ars-magica", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main(None)
    assert exc_info.value.code == 0


def test_cli_module_main_execution(monkeypatch: pytest.MonkeyPatch):
    """Verify that running obsidian_ars_magica.cli as __main__ invokes sys.exit(main())."""
    import obsidian_ars_magica.cli as cli_module

    cli_path = Path(cli_module.__file__).resolve()
    monkeypatch.setattr(sys, "argv", ["obsidian-ars-magica", "--help"])
    monkeypatch.delitem(sys.modules, "obsidian_ars_magica.cli", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(cli_path), run_name="__main__")
    assert exc_info.value.code == 0


def test_cli_extract_virtues_flaws_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """End-to-end integration test of extract-virtues-flaws CLI on synthetic markdown."""
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(
        """# Chapter 4: Virtues and Flaws

## List of Virtues
[Sample Virtue](#sample-virtue)

## Virtues

#### Sample Virtue
*Minor, General*<br>
A sample virtue.

## List of Flaws
[Sample Flaw](#sample-flaw)

## Flaws

#### Sample Flaw
*Major, Hermetic*<br>
A sample flaw.

# Chapter 5: Abilities
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-virtues-flaws",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0

    virtue_file = output_dir / "virtues" / "Sample-Virtue.md"
    flaw_file = output_dir / "flaws" / "Sample-Flaw.md"
    assert virtue_file.exists()
    assert flaw_file.exists()

    captured = capsys.readouterr()
    assert "Successfully extracted 1 Virtues" in captured.out
    assert "Successfully extracted 1 Flaws" in captured.out


def test_cli_extract_abilities_help(capsys: pytest.CaptureFixture[str]):
    """Verify that extract-abilities --help displays options."""
    with pytest.raises(SystemExit) as exc_info:
        main(["extract-abilities", "--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "--source" in captured.out
    assert "--output" in captured.out


def test_cli_extract_abilities_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify successful extract-abilities with custom arguments and mocked exporter."""
    source_file = tmp_path / "rules.md"
    source_file.write_text("# Dummy rules", encoding="utf-8")
    output_dir = tmp_path / "custom_output"

    mock_counts = {"abilities": 42}
    calls = []

    def fake_export(src: Path, out: Path):
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr("obsidian_ars_magica.cli.export_abilities", fake_export)

    exit_code = main([
        "extract-abilities",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (source_file, output_dir)

    captured = capsys.readouterr()
    assert f"Reading source: {source_file}" in captured.out
    assert f"Exporting to:   {output_dir}" in captured.out
    assert f"Successfully extracted 42 Abilities to {output_dir / 'abilities'}" in captured.out


def test_cli_extract_abilities_defaults(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify that extract-abilities uses default paths when flags are omitted."""
    monkeypatch.setattr(Path, "exists", lambda self: True)

    mock_counts = {"abilities": 78}
    calls = []

    def fake_export(src: Path, out: Path):
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr("obsidian_ars_magica.cli.export_abilities", fake_export)

    exit_code = main(["extract-abilities"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (DEFAULT_SOURCE, DEFAULT_OUTPUT)

    captured = capsys.readouterr()
    assert f"Reading source: {DEFAULT_SOURCE}" in captured.out
    assert f"Exporting to:   {DEFAULT_OUTPUT}" in captured.out
    assert f"Successfully extracted 78 Abilities to {DEFAULT_OUTPUT / 'abilities'}" in captured.out


def test_cli_extract_abilities_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """End-to-end integration test of extract-abilities CLI on synthetic markdown."""
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(
        """# Chapter 5: Abilities

## Abilities by Type

#### General Abilities

[Animal Handling](#animal-handling)<br>

## Ability List

#### Animal Handling
Care and use of animals.<br>
*Specialties:* falconry, specific animals. (General)

# Chapter 6: Covenants
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-abilities",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0

    ability_file = output_dir / "abilities" / "Animal-Handling.md"
    assert ability_file.exists()
    content = ability_file.read_text(encoding="utf-8")
    assert 'name: "Animal Handling"' in content
    assert 'type: "General"' in content
    assert "untrained: true" in content

    captured = capsys.readouterr()
    assert "Successfully extracted 1 Abilities" in captured.out


def test_cli_extract_spells_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "mock_core_rules.md"
    source_file.write_text(
        """# Chapter 9: Spells

## Animal Spells

### Creo Animal Guidelines

| Level | Creo Animal Guideline |
| ----- | --------------------- |
| 15 | • Heal a Light Wound |

### Creo Animal Spells

#### LEVEL 20

##### Soothe Pains of the Beast
R: Touch, D: Mom, T: Ind, Ritual<br>
The spell cures one Light Wound suffered by the animal.<br>
(Base level 15, +1 Touch)

# Chapter 10: Long Term Events
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-spells",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    spell_file = output_dir / "spells" / "Soothe-Pains-of-the-Beast.md"
    assert spell_file.exists()
    content = spell_file.read_text(encoding="utf-8")
    assert 'name: "Soothe Pains of the Beast"' in content
    assert "ritual: true" in content
    assert "> [!metadata] **CrAn 20** | **Ritual**" in content

    captured = capsys.readouterr()
    assert "Successfully extracted 1 Spells" in captured.out


def test_cli_extract_guidelines_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "mock_core_rules.md"
    source_file.write_text(
        """# Chapter 9: Spells

## Animal Spells

### Creo Animal Guidelines

Rules for Creo Animal.

| Level | Creo Animal Guideline |
| ----- | --------------------- |
| 1 | • Give an animal a +1 bonus |
| 5 | • Create an insect |

### Creo Animal Spells

# Chapter 10: Long Term Events
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-guidelines",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    gl_file = output_dir / "guidelines" / "Creo-Animal-Guidelines.md"
    assert gl_file.exists()
    content = gl_file.read_text(encoding="utf-8")
    assert 'name: "Creo Animal Guidelines"' in content
    assert "### Level 1" in content
    assert "- Give an animal a +1 bonus ^cran-1-1" in content

    captured = capsys.readouterr()
    assert "Successfully extracted 1 Guideline sections" in captured.out


def test_cli_extract_all_help(capsys: pytest.CaptureFixture[str]):
    """Verify that extract-all --help displays options and description."""
    with pytest.raises(SystemExit) as exc_info:
        main(["extract-all", "--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "--source" in captured.out
    assert "--output" in captured.out


def test_cli_extract_all_source_not_found(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verify missing source file exits with code 1 for extract-all."""
    nonexistent = tmp_path / "missing.md"
    exit_code = main(["extract-all", "--source", str(nonexistent)])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert f"Error: Source file does not exist: {nonexistent}" in captured.err


def test_cli_extract_all_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify successful extract-all CLI execution with progress and summary output."""
    source_file = tmp_path / "rules.md"
    source_file.write_text("# Rules", encoding="utf-8")
    output_dir = tmp_path / "custom_out"

    mock_result = {
        "virtues": 10,
        "flaws": 15,
        "abilities": 25,
        "spells": 50,
        "guidelines": 5,
        "total": 105,
    }

    def fake_export_all(src: Path, out: Path, progress_callback=None):
        if progress_callback:
            progress_callback("virtues_flaws", {"virtues": 10, "flaws": 15})
            progress_callback("abilities", {"abilities": 25})
            progress_callback("spells", {"spells": 50})
            progress_callback("guidelines", {"guidelines": 5})
        return mock_result

    monkeypatch.setattr("obsidian_ars_magica.cli.export_all", fake_export_all)

    exit_code = main([
        "extract-all",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert f"Reading source: {source_file}" in captured.out
    assert f"Exporting to:   {output_dir}" in captured.out
    assert f"Successfully extracted 10 Virtues to {output_dir / 'virtues'}" in captured.out
    assert f"Successfully extracted 15 Flaws to {output_dir / 'flaws'}" in captured.out
    assert f"Successfully extracted 25 Abilities to {output_dir / 'abilities'}" in captured.out
    assert f"Successfully extracted 50 Spells to {output_dir / 'spells'}" in captured.out
    assert f"Successfully extracted 5 Guideline sections to {output_dir / 'guidelines'}" in captured.out
    assert "Bulk extraction complete: 105 total notes generated." in captured.out


def test_cli_extract_all_defaults(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify that extract-all defaults to DEFAULT_SOURCE and DEFAULT_OUTPUT."""
    monkeypatch.setattr(Path, "exists", lambda self: True)

    calls = []

    def fake_export_all(src: Path, out: Path, progress_callback=None):
        calls.append((src, out))
        return {
            "virtues": 0,
            "flaws": 0,
            "abilities": 0,
            "spells": 0,
            "guidelines": 0,
            "total": 0,
        }

    monkeypatch.setattr("obsidian_ars_magica.cli.export_all", fake_export_all)

    exit_code = main(["extract-all"])
    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (DEFAULT_SOURCE, DEFAULT_OUTPUT)

    captured = capsys.readouterr()
    assert f"Reading source: {DEFAULT_SOURCE}" in captured.out
    assert f"Exporting to:   {DEFAULT_OUTPUT}" in captured.out


def test_cli_extract_all_alias(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify that 'all' alias works identically to 'extract-all'."""
    monkeypatch.setattr(Path, "exists", lambda self: True)

    calls = []

    def fake_export_all(src: Path, out: Path, progress_callback=None):
        calls.append((src, out))
        return {
            "virtues": 1,
            "flaws": 1,
            "abilities": 1,
            "spells": 1,
            "guidelines": 1,
            "total": 5,
        }

    monkeypatch.setattr("obsidian_ars_magica.cli.export_all", fake_export_all)

    exit_code = main(["all"])
    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (DEFAULT_SOURCE, DEFAULT_OUTPUT)


def test_cli_extract_all_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """End-to-end integration test of extract-all CLI on synthetic markdown."""
    source_file = tmp_path / "mock_core_rules.md"
    source_file.write_text(
        """# Chapter 4: Virtues and Flaws

## List of Virtues
[Sample Virtue](#sample-virtue)

## Virtues

#### Sample Virtue
*Minor, General*<br>
A sample virtue.

## List of Flaws
[Sample Flaw](#sample-flaw)

## Flaws

#### Sample Flaw
*Major, Hermetic*<br>
A sample flaw.

# Chapter 5: Abilities

## Abilities by Type

#### General Abilities
[Athletics](#athletics)<br>

## Ability List

#### Athletics
Running and jumping.<br>
*Specialties:* running. (General)

# Chapter 6: Covenants

# Chapter 9: Spells

## Animal Spells

### Creo Animal Guidelines

Rules for Creo Animal.

| Level | Creo Animal Guideline |
| ----- | --------------------- |
| 5 | • Create an insect |

### Creo Animal Spells

#### LEVEL 10

##### Beast of Outlandish Size
R: Touch, D: Sun, T: Ind<br>
Increases animal size.<br>
(Base 5, +1 Touch, +2 Sun)

# Chapter 10: Long Term Events
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-all",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0

    assert (output_dir / "virtues" / "Sample-Virtue.md").exists()
    assert (output_dir / "flaws" / "Sample-Flaw.md").exists()
    assert (output_dir / "abilities" / "Athletics.md").exists()
    assert (output_dir / "spells" / "Beast-of-Outlandish-Size.md").exists()
    assert (output_dir / "guidelines" / "Creo-Animal-Guidelines.md").exists()

    captured = capsys.readouterr()
    assert "Bulk extraction complete: 5 total notes generated." in captured.out



