# SPDX-License-Identifier: MIT
"""Unit and integration tests for the command-line interface."""

import runpy
import sys
from pathlib import Path
from typing import Any

import pytest

from obsidian_ars_magica.cli import DEFAULT_OUTPUT, DEFAULT_SOURCE, main

SUBCOMMANDS = [
    "extract-virtues-flaws",
    "extract-abilities",
    "extract-spells",
    "extract-guidelines",
    "extract-all",
    "all",
]

MOCKED_SUBCOMMANDS = [
    (
        "extract-virtues-flaws",
        "obsidian_ars_magica.cli.export_virtues_and_flaws",
        {"virtues": 12, "flaws": 8},
        ["12 Virtues", "8 Flaws", "virtues.base", "flaws.base"],
    ),
    (
        "extract-abilities",
        "obsidian_ars_magica.cli.export_abilities",
        {"abilities": 42},
        ["42 Abilities", "abilities.base"],
    ),
    (
        "extract-spells",
        "obsidian_ars_magica.cli.export_spells",
        {"spells": 35},
        ["35 Spells", "spells.base"],
    ),
    (
        "extract-guidelines",
        "obsidian_ars_magica.cli.export_guidelines",
        {"guidelines": 50},
        ["50 Guideline sections"],
    ),
]


def test_cli_help(capsys: pytest.CaptureFixture[str]):
    """Verify that --help displays prog name and all subcommands."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "obsidian-ars-magica" in captured.out
    for sub in ["extract-virtues-flaws", "extract-abilities", "extract-spells", "extract-guidelines", "extract-all"]:
        assert sub in captured.out


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_cli_subcommand_help(subcommand: str, capsys: pytest.CaptureFixture[str]):
    """Verify that every subcommand --help displays source and output options."""
    with pytest.raises(SystemExit) as exc_info:
        main([subcommand, "--help"])
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


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_cli_source_not_found(subcommand: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verify that missing source file reports error on stderr and returns 1 across all subcommands."""
    nonexistent = tmp_path / "does_not_exist.md"
    exit_code = main([subcommand, "--source", str(nonexistent)])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert f"Error: Source file does not exist: {nonexistent}" in captured.err


@pytest.mark.parametrize("subcommand,mock_target,mock_counts,expected_snippets", MOCKED_SUBCOMMANDS)
def test_cli_subcommand_success(
    subcommand: str,
    mock_target: str,
    mock_counts: dict[str, int],
    expected_snippets: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    """Verify successful execution with custom arguments across subcommands."""
    source_file = tmp_path / "rules.md"
    source_file.write_text("# Dummy rules", encoding="utf-8")
    output_dir = tmp_path / "custom_output"

    calls: list[tuple[Path, Path]] = []

    def fake_export(src: Path, out: Path) -> dict[str, int]:
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr(mock_target, fake_export)

    exit_code = main([
        subcommand,
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
    for snippet in expected_snippets:
        assert snippet in captured.out


@pytest.mark.parametrize("subcommand,mock_target,mock_counts,expected_snippets", MOCKED_SUBCOMMANDS)
def test_cli_subcommand_defaults(
    subcommand: str,
    mock_target: str,
    mock_counts: dict[str, int],
    expected_snippets: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    """Verify that subcommands use default paths when flags are omitted."""
    monkeypatch.setattr(Path, "exists", lambda self: True)

    calls: list[tuple[Path, Path]] = []

    def fake_export(src: Path, out: Path) -> dict[str, int]:
        calls.append((src, out))
        return mock_counts

    monkeypatch.setattr(mock_target, fake_export)

    exit_code = main([subcommand])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0] == (DEFAULT_SOURCE, DEFAULT_OUTPUT)

    captured = capsys.readouterr()
    assert f"Reading source: {DEFAULT_SOURCE}" in captured.out
    assert f"Exporting to:   {DEFAULT_OUTPUT}" in captured.out
    for snippet in expected_snippets:
        assert snippet in captured.out


def test_cli_extract_all_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Verify extract-all CLI execution with progress callback and summary output."""
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

    def fake_export_all(src: Path, out: Path, progress_callback: Any = None) -> dict[str, int]:
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
    assert f"Generated Base databases: {output_dir / 'virtues.base'}, {output_dir / 'flaws.base'}" in captured.out
    assert f"Generated Base database:  {output_dir / 'abilities.base'}" in captured.out
    assert f"Generated Base database:  {output_dir / 'spells.base'}" in captured.out
    assert "Bulk extraction complete: 105 total notes generated." in captured.out


@pytest.mark.parametrize("subcommand", ["extract-all", "all"])
def test_cli_extract_all_defaults(
    subcommand: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    """Verify that extract-all and alias 'all' default to DEFAULT_SOURCE and DEFAULT_OUTPUT."""
    monkeypatch.setattr(Path, "exists", lambda self: True)

    calls: list[tuple[Path, Path]] = []

    def fake_export_all(src: Path, out: Path, progress_callback: Any = None) -> dict[str, int]:
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

    exit_code = main([subcommand])
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


SYNTHETIC_RULES = """# Chapter 4: Virtues and Flaws

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
| 15 | • Heal a Light Wound |

### Creo Animal Spells

#### LEVEL 20

##### Soothe Pains of the Beast
R: Touch, D: Mom, T: Ind, Ritual<br>
The spell cures one Light Wound suffered by the animal.<br>
(Base level 15, +1 Touch)

# Chapter 10: Long Term Events
"""


def test_cli_extract_virtues_flaws_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(SYNTHETIC_RULES, encoding="utf-8")
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-virtues-flaws",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "virtues" / "Sample-Virtue.md").exists()
    assert (output_dir / "flaws" / "Sample-Flaw.md").exists()
    assert (output_dir / "virtues.base").exists()
    assert (output_dir / "flaws.base").exists()


def test_cli_extract_abilities_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(SYNTHETIC_RULES, encoding="utf-8")
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-abilities",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "abilities" / "Athletics.md").exists()
    assert (output_dir / "abilities.base").exists()


def test_cli_extract_spells_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(SYNTHETIC_RULES, encoding="utf-8")
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-spells",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "spells" / "Soothe-Pains-of-the-Beast.md").exists()
    assert (output_dir / "spells.base").exists()


def test_cli_extract_guidelines_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(SYNTHETIC_RULES, encoding="utf-8")
    output_dir = tmp_path / "obsidian_vault"

    exit_code = main([
        "extract-guidelines",
        "--source",
        str(source_file),
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "guidelines" / "Creo-Animal-Guidelines.md").exists()


def test_cli_extract_all_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source_file = tmp_path / "sample_rules.md"
    source_file.write_text(SYNTHETIC_RULES, encoding="utf-8")
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
    assert (output_dir / "spells" / "Soothe-Pains-of-the-Beast.md").exists()
    assert (output_dir / "guidelines" / "Creo-Animal-Guidelines.md").exists()

    captured = capsys.readouterr()
    assert "Bulk extraction complete: 5 total notes generated." in captured.out
