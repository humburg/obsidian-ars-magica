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

    # Node 24 runner configuration
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in content

    # Checkout submodules (Node 24)
    assert "actions/checkout@v5" in content
    assert "submodules: true" in content

    # Python setup (Node 24)
    assert "actions/setup-python@v7" in content
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

    # Workflow artifact upload (Node 24)
    assert "actions/upload-artifact@v6" in content


def test_ci_workflow_targets_node24():
    """Verify CI workflow targets Node.js 24 and uses updated action versions."""
    content = Path(".github/workflows/ci.yaml").read_text(encoding="utf-8")

    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in content
    assert "actions/checkout@v5" in content
    assert "actions/setup-python@v7" in content
    assert "actions/upload-artifact@v6" in content


