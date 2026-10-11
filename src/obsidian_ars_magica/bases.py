# SPDX-License-Identifier: MIT
"""Obsidian Bases definitions and generators for Ars Magica content."""


def format_guideline_bases_block(technique: str, form: str) -> str:
    """Format an embedded Obsidian Bases code block querying spells for this Technique and Form."""
    return f"""```base
filters:
  and:
    - file.inFolder("spells")
    - 'technique == "{technique}"'
    - 'form == "{form}"'
formulas:
  name: 'file.asLink(note.name)'
properties:
  formula.name:
    displayName: Spell
  level:
    displayName: Level
  range:
    displayName: R
  duration:
    displayName: D
  target:
    displayName: T
  ritual:
    displayName: Ritual
views:
  - type: table
    name: "Known Spells"
    order:
      - formula.name
      - level
      - range
      - duration
      - target
      - ritual
    sort:
      - column: level
        direction: ASC
```"""


def generate_spells_base() -> str:
    """Generate standalone Obsidian Base content for Spells (spells.base)."""
    return """filters:
  and:
    - file.inFolder("spells")
formulas:
  name: 'file.asLink(note.name)'
properties:
  formula.name:
    displayName: Spell
  technique:
    displayName: Technique
  form:
    displayName: Form
  level:
    displayName: Level
  range:
    displayName: R
  duration:
    displayName: D
  target:
    displayName: T
  ritual:
    displayName: Ritual
  base_level:
    displayName: Base
  total_magnitudes:
    displayName: Magnitudes
views:
  - type: table
    name: "All Spells"
    order:
      - formula.name
      - technique
      - form
      - level
      - range
      - duration
      - target
      - ritual
    sort:
      - column: formula.name
        direction: ASC
  - type: table
    name: "By Arts"
    groupBy:
      property: arts
      direction: ASC
    order:
      - formula.name
      - level
      - range
      - duration
      - target
      - ritual
    sort:
      - column: level
        direction: ASC
  - type: table
    name: "Ritual Spells"
    filters:
      and:
        - 'ritual == true'
    order:
      - formula.name
      - technique
      - form
      - level
      - range
      - duration
      - target
    sort:
      - column: formula.name
        direction: ASC
"""


def generate_virtues_base() -> str:
    """Generate standalone Obsidian Base content for Virtues (virtues.base)."""
    return """filters:
  and:
    - file.inFolder("virtues")
formulas:
  name: 'file.asLink(note.name)'
properties:
  formula.name:
    displayName: Virtue
  cost:
    displayName: Cost
  type:
    displayName: Type
  properties:
    displayName: Properties
views:
  - type: table
    name: "All Virtues"
    order:
      - formula.name
      - cost
      - type
      - properties
    sort:
      - column: formula.name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - formula.name
      - type
      - properties
    sort:
      - column: formula.name
        direction: ASC
"""


def generate_flaws_base() -> str:
    """Generate standalone Obsidian Base content for Flaws (flaws.base)."""
    return """filters:
  and:
    - file.inFolder("flaws")
formulas:
  name: 'file.asLink(note.name)'
properties:
  formula.name:
    displayName: Flaw
  cost:
    displayName: Cost
  type:
    displayName: Type
  properties:
    displayName: Properties
views:
  - type: table
    name: "All Flaws"
    order:
      - formula.name
      - cost
      - type
      - properties
    sort:
      - column: formula.name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - formula.name
      - type
      - properties
    sort:
      - column: formula.name
        direction: ASC
"""


def generate_abilities_base() -> str:
    """Generate standalone Obsidian Base content for Abilities (abilities.base)."""
    return """filters:
  and:
    - file.inFolder("abilities")
formulas:
  name: 'file.asLink(note.name)'
properties:
  formula.name:
    displayName: Ability
  type:
    displayName: Type
  untrained:
    displayName: Untrained
  specialties:
    displayName: Specialties
views:
  - type: table
    name: "All Abilities"
    order:
      - formula.name
      - type
      - untrained
      - specialties
    sort:
      - column: formula.name
        direction: ASC
  - type: table
    name: "By Type"
    groupBy:
      property: type
      direction: ASC
    order:
      - formula.name
      - untrained
      - specialties
    sort:
      - column: formula.name
        direction: ASC
"""
