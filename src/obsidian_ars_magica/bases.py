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
properties:
  name:
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
      - name
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
properties:
  name:
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
      - name
      - technique
      - form
      - level
      - range
      - duration
      - target
      - ritual
    sort:
      - column: name
        direction: ASC
  - type: table
    name: "By Arts"
    groupBy:
      property: arts
      direction: ASC
    order:
      - name
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
      - name
      - technique
      - form
      - level
      - range
      - duration
      - target
    sort:
      - column: level
        direction: ASC
"""


def generate_virtues_base() -> str:
    """Generate standalone Obsidian Base content for Virtues (virtues.base)."""
    return """filters:
  and:
    - file.inFolder("virtues")
properties:
  name:
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
      - name
      - cost
      - type
      - properties
    sort:
      - column: name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - name
      - type
      - properties
    sort:
      - column: name
        direction: ASC
"""


def generate_flaws_base() -> str:
    """Generate standalone Obsidian Base content for Flaws (flaws.base)."""
    return """filters:
  and:
    - file.inFolder("flaws")
properties:
  name:
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
      - name
      - cost
      - type
      - properties
    sort:
      - column: name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - name
      - type
      - properties
    sort:
      - column: name
        direction: ASC
"""


def generate_abilities_base() -> str:
    """Generate standalone Obsidian Base content for Abilities (abilities.base)."""
    return """filters:
  and:
    - file.inFolder("abilities")
properties:
  name:
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
      - name
      - type
      - untrained
      - specialties
    sort:
      - column: name
        direction: ASC
  - type: table
    name: "By Type"
    groupBy:
      property: type
      direction: ASC
    order:
      - name
      - untrained
      - specialties
    sort:
      - column: name
        direction: ASC
"""
