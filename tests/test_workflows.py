# SPDX-License-Identifier: MIT
"""Tests verifying GitHub Actions workflow configurations."""

from pathlib import Path


def test_release_workflow_file_exists():
    """Verify that the release workflow file exists in .github/workflows/."""
    workflow_path = Path(".github/workflows/release.yaml")
    assert workflow_path.is_file(), "Expected .github/workflows/release.yaml to exist"


def test_release_workflow_triggers_and_permissions():
    """Verify release.yaml triggers on published releases and has write permissions."""
    content = Path(".github/workflows/release.yaml").read_text(encoding="utf-8")

    # Verify release trigger and activity type
    assert "release:" in content
    assert "types: [published]" in content
    assert "workflow_dispatch:" in content

    # Verify permissions for release asset upload
    assert "permissions:" in content
    assert "contents: write" in content


def test_release_workflow_steps_configuration():
    """Verify key workflow steps: checkout with submodules, extract-all, zip, and gh upload."""
    content = Path(".github/workflows/release.yaml").read_text(encoding="utf-8")

    # Checkout submodules
    assert "actions/checkout@v4" in content
    assert "submodules: true" in content

    # Python setup
    assert "actions/setup-python@v5" in content
    assert 'python-version: "3.15"' in content

    # Execution of extract-all
    assert "obsidian-ars-magica extract-all --output output" in content

    # Licensing inclusion
    assert "output/LICENSE.md" in content

    # Dual archive packaging (versioned and static)
    assert 'ARCHIVE_VERSIONED="obsidian-ars-magica-notes-${TAG}.zip"' in content
    assert 'ARCHIVE_STATIC="obsidian-ars-magica-notes.zip"' in content

    # GitHub CLI upload
    assert "gh release upload" in content
    assert "--clobber" in content

    # Workflow artifact upload
    assert "actions/upload-artifact@v4" in content

