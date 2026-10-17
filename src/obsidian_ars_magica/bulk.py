# SPDX-License-Identifier: MIT
"""Bulk extraction pipeline for obsidian-ars-magica."""

from collections.abc import Callable
from pathlib import Path

from obsidian_ars_magica.abilities import export_abilities
from obsidian_ars_magica.guidelines import export_guidelines
from obsidian_ars_magica.spells import export_spells
from obsidian_ars_magica.virtues_flaws import export_virtues_and_flaws


def export_all(
    source_path: Path | str,
    output_dir: Path | str,
    progress_callback: Callable[[str, dict[str, int]], None] | None = None,
) -> dict[str, int]:
    """Parse core rules and export all content in sequence.

    Runs extraction for Virtues & Flaws, Abilities, Spells, and Spell Guidelines.

    Args:
        source_path: Path to the Ars Magica core rules markdown file.
        output_dir: Root directory where note subfolders will be created.
        progress_callback: Optional callback invoked after each stage with
            (stage_name, stage_counts).

    Returns:
        Dict containing counts for each category and 'total'.
    """
    source = Path(source_path)
    target_root = Path(output_dir)

    target_root.mkdir(parents=True, exist_ok=True)

    # 1. Virtues and Flaws (Chapter 4)
    vf_counts = export_virtues_and_flaws(source, target_root)
    if progress_callback:
        progress_callback("virtues_flaws", vf_counts)

    # 2. Abilities (Chapter 5)
    ab_counts = export_abilities(source, target_root)
    if progress_callback:
        progress_callback("abilities", ab_counts)

    # 3. Spells (Chapter 9)
    sp_counts = export_spells(source, target_root)
    if progress_callback:
        progress_callback("spells", sp_counts)

    # 4. Spell Guidelines (Chapter 9)
    gl_counts = export_guidelines(source, target_root)
    if progress_callback:
        progress_callback("guidelines", gl_counts)

    total = (
        vf_counts["virtues"]
        + vf_counts["flaws"]
        + ab_counts["abilities"]
        + sp_counts["spells"]
        + gl_counts["guidelines"]
    )

    return {
        "virtues": vf_counts["virtues"],
        "flaws": vf_counts["flaws"],
        "abilities": ab_counts["abilities"],
        "spells": sp_counts["spells"],
        "guidelines": gl_counts["guidelines"],
        "total": total,
    }


__all__ = ["export_all"]
