# SPDX-License-Identifier: MIT
"""Command-line interface for obsidian-ars-magica tooling."""

import argparse
import sys
from pathlib import Path

from obsidian_ars_magica.abilities import export_abilities
from obsidian_ars_magica.bulk import export_all
from obsidian_ars_magica.guidelines import export_guidelines
from obsidian_ars_magica.spells import export_spells
from obsidian_ars_magica.virtues_flaws import export_virtues_and_flaws

DEFAULT_SOURCE = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)
DEFAULT_OUTPUT = Path("output")


def _build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser with common options."""
    parser = argparse.ArgumentParser(
        prog="obsidian-ars-magica",
        description="Tools for converting and enhancing Ars Magica Open License markdown for Obsidian.",
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source core rules markdown file (default: {DEFAULT_SOURCE})",
    )
    common_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Target output directory (default: {DEFAULT_OUTPUT})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "extract-virtues-flaws",
        parents=[common_parser],
        help="Extract Virtues and Flaws into separate notes and generate virtues.base and flaws.base.",
    )

    subparsers.add_parser(
        "extract-abilities",
        parents=[common_parser],
        help="Extract Abilities into separate notes and generate abilities.base.",
    )

    subparsers.add_parser(
        "extract-spells",
        parents=[common_parser],
        help="Extract Spells into separate notes and generate spells.base.",
    )

    subparsers.add_parser(
        "extract-guidelines",
        parents=[common_parser],
        help="Extract Spell Guidelines into 50 Technique+Form notes with embedded Bases views.",
    )

    subparsers.add_parser(
        "extract-all",
        aliases=["all"],
        parents=[common_parser],
        help="Run all extraction tools in one go to generate a complete Obsidian vault.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    source_path: Path = args.source
    output_dir: Path = args.output

    if not source_path.exists():
        print(f"Error: Source file does not exist: {source_path}", file=sys.stderr)
        return 1

    print(f"Reading source: {source_path}")
    print(f"Exporting to:   {output_dir}")

    if args.command == "extract-virtues-flaws":
        counts = export_virtues_and_flaws(source_path, output_dir)
        print(f"Successfully extracted {counts['virtues']} Virtues to {output_dir / 'virtues'}")
        print(f"Successfully extracted {counts['flaws']} Flaws to {output_dir / 'flaws'}")
        print(f"Generated Base databases: {output_dir / 'virtues.base'}, {output_dir / 'flaws.base'}")
        return 0

    if args.command == "extract-abilities":
        counts = export_abilities(source_path, output_dir)
        print(f"Successfully extracted {counts['abilities']} Abilities to {output_dir / 'abilities'}")
        print(f"Generated Base database:  {output_dir / 'abilities.base'}")
        return 0

    if args.command == "extract-spells":
        counts = export_spells(source_path, output_dir)
        print(f"Successfully extracted {counts['spells']} Spells to {output_dir / 'spells'}")
        print(f"Generated Base database:  {output_dir / 'spells.base'}")
        return 0

    if args.command == "extract-guidelines":
        counts = export_guidelines(source_path, output_dir)
        print(f"Successfully extracted {counts['guidelines']} Guideline sections to {output_dir / 'guidelines'}")
        return 0

    if args.command in ("extract-all", "all"):
        def progress(stage: str, counts: dict[str, int]) -> None:
            if stage == "virtues_flaws":
                print(f"Successfully extracted {counts['virtues']} Virtues to {output_dir / 'virtues'}")
                print(f"Successfully extracted {counts['flaws']} Flaws to {output_dir / 'flaws'}")
                print(f"Generated Base databases: {output_dir / 'virtues.base'}, {output_dir / 'flaws.base'}")
            elif stage == "abilities":
                print(f"Successfully extracted {counts['abilities']} Abilities to {output_dir / 'abilities'}")
                print(f"Generated Base database:  {output_dir / 'abilities.base'}")
            elif stage == "spells":
                print(f"Successfully extracted {counts['spells']} Spells to {output_dir / 'spells'}")
                print(f"Generated Base database:  {output_dir / 'spells.base'}")
            elif stage == "guidelines":
                print(f"Successfully extracted {counts['guidelines']} Guideline sections to {output_dir / 'guidelines'}")

        counts = export_all(source_path, output_dir, progress_callback=progress)
        print(f"Bulk extraction complete: {counts['total']} total notes generated.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
