# SPDX-License-Identifier: MIT
"""Unit tests for formatters utility module."""

from obsidian_ars_magica.formatters import dump_frontmatter, sanitize_filename, yaml_quote


def test_yaml_quote_escaping():
    assert yaml_quote("Simple") == '"Simple"'
    assert yaml_quote('With "quotes"') == r'"With \"quotes\""'
    assert yaml_quote(r"With \backslashes") == r'"With \\backslashes"'


def test_sanitize_filename():
    assert sanitize_filename("Animal Handling") == "Animal-Handling.md"
    assert sanitize_filename("(Area) Lore") == "Area-Lore.md"
    assert sanitize_filename("Theology: Christian") == "Theology-Christian.md"
    assert sanitize_filename("Ball of Abysmal Flame") == "Ball-of-Abysmal-Flame.md"


def test_dump_frontmatter_types():
    data = {
        "title": "Sample Note",
        "level": 25,
        "ritual": True,
        "empty_list": [],
        "tags": ["spell", "creo", "ignem"],
        "none_val": None,
    }
    fm = dump_frontmatter(data)
    assert fm.startswith("---\n")
    assert fm.endswith("---")
    assert 'title: "Sample Note"' in fm
    assert "level: 25" in fm
    assert "ritual: true" in fm
    assert "empty_list: []" in fm
    assert "tags:\n  - \"spell\"\n  - \"creo\"\n  - \"ignem\"" in fm
    assert "none_val:" in fm

