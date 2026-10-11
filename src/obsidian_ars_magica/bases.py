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
  file.name:
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
      - file.name
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
  file.name:
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
      - file.name
      - technique
      - form
      - level
      - range
      - duration
      - target
      - ritual
    sort:
      - column: file.name
        direction: ASC
  - type: table
    name: "By Arts"
    groupBy:
      property: arts
      direction: ASC
    order:
      - file.name
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
      - file.name
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
  file.name:
    displayName: Virtue
  cost:
    displayName: Cost
  types:
    displayName: Type
  properties:
    displayName: Properties
views:
  - type: table
    name: "All Virtues"
    order:
      - file.name
      - cost
      - types
      - properties
    sort:
      - column: file.name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - file.name
      - types
      - properties
    sort:
      - column: file.name
        direction: ASC
"""


def generate_flaws_base() -> str:
    """Generate standalone Obsidian Base content for Flaws (flaws.base)."""
    return """filters:
  and:
    - file.inFolder("flaws")
properties:
  file.name:
    displayName: Flaw
  cost:
    displayName: Cost
  types:
    displayName: Type
  properties:
    displayName: Properties
views:
  - type: table
    name: "All Flaws"
    order:
      - file.name
      - cost
      - types
      - properties
    sort:
      - column: file.name
        direction: ASC
  - type: table
    name: "By Cost"
    groupBy:
      property: cost
      direction: ASC
    order:
      - file.name
      - types
      - properties
    sort:
      - column: file.name
        direction: ASC
"""


def generate_abilities_base() -> str:
    """Generate standalone Obsidian Base content for Abilities (abilities.base)."""
    return """filters:
  and:
    - file.inFolder("abilities")
properties:
  file.name:
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
      - file.name
      - type
      - untrained
      - specialties
    sort:
      - column: file.name
        direction: ASC
  - type: table
    name: "By Type"
    groupBy:
      property: type
      direction: ASC
    order:
      - file.name
      - untrained
      - specialties
    sort:
      - column: file.name
        direction: ASC
"""

