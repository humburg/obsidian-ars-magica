"""Command-line interface for obsidian-ars-magica tooling."""

import argparse
import sys
from pathlib import Path

from obsidian_ars_magica.abilities import export_abilities
from obsidian_ars_magica.virtues_flaws import export_virtues_and_flaws

DEFAULT_SOURCE = Path(
    "Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md"
)
DEFAULT_OUTPUT = Path("output")


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="obsidian-ars-magica",
        description="Tools for converting and enhancing Ars Magica Open License markdown for Obsidian.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: extract-virtues-flaws
    vf_parser = subparsers.add_parser(
        "extract-virtues-flaws",
        help="Extract Virtues and Flaws into separate notes with YAML frontmatter.",
    )
    vf_parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source core rules markdown file (default: {DEFAULT_SOURCE})",
    )
    vf_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Target output directory (default: {DEFAULT_OUTPUT})",
    )

    # Subcommand: extract-abilities
    ab_parser = subparsers.add_parser(
        "extract-abilities",
        help="Extract Abilities into separate notes with YAML frontmatter.",
    )
    ab_parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source core rules markdown file (default: {DEFAULT_SOURCE})",
    )
    ab_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Target output directory (default: {DEFAULT_OUTPUT})",
    )

    args = parser.parse_args(argv)

    if args.command == "extract-virtues-flaws":
        source_path = args.source
        output_dir = args.output

        if not source_path.exists():
            print(f"Error: Source file does not exist: {source_path}", file=sys.stderr)
            return 1

        print(f"Reading source: {source_path}")
        print(f"Exporting to:   {output_dir}")

        counts = export_virtues_and_flaws(source_path, output_dir)

        print(f"Successfully extracted {counts['virtues']} Virtues to {output_dir / 'virtues'}")
        print(f"Successfully extracted {counts['flaws']} Flaws to {output_dir / 'flaws'}")
        return 0

    if args.command == "extract-abilities":
        source_path = args.source
        output_dir = args.output

        if not source_path.exists():
            print(f"Error: Source file does not exist: {source_path}", file=sys.stderr)
            return 1

        print(f"Reading source: {source_path}")
        print(f"Exporting to:   {output_dir}")

        counts = export_abilities(source_path, output_dir)

        print(f"Successfully extracted {counts['abilities']} Abilities to {output_dir / 'abilities'}")
        return 0


    return 0


if __name__ == "__main__":
    sys.exit(main())
