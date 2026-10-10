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
