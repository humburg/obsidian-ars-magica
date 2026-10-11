# obsidian-ars-magica

Python tooling for extracting, formatting, and enhancing *Ars Magica 5th Edition Definitive Edition* Open License content for use in [Obsidian](https://obsidian.md/) markdown vaults.

> [!NOTE]
> **AI Assistance**: This codebase was developed and generated with the help of an AI assistant.

---

## Overview

The `obsidian-ars-magica` package parses reviewed markdown rules from the Ars Magica Open License repository and splits core game systems into modular, atomic Obsidian notes.

Each generated note is augmented with:
- **YAML Frontmatter**: Standardized metadata (names, categories, types, costs, tags, aliases) optimized for Obsidian Properties and search.
- **Wikilinks & Anchors**: Spells link directly to their corresponding Spell Guideline base levels (e.g., `[[Creo-Ignem-Guidelines#Level 5|Creo Ignem Base 5]]`).
- **Obsidian Callouts**: Rich visual summaries formatted with metadata callouts (`> [!metadata]`).
- **Block IDs**: Spell Guideline level bullet points include stable block IDs (e.g., `^crig-5-1`) for precise referencing.
- **Obsidian Bases Integration**: Standalone `.base` database files (`spells.base`, `virtues.base`, `flaws.base`, `abilities.base`) and embedded Bases table views (` ```base `) in Guideline notes for native, interactive querying in Obsidian (requires Obsidian v1.9+ core Bases plugin).

---

## Features & Tools

The CLI provides dedicated extraction tools for individual systems as well as a bulk extractor to generate the complete vault in one command:

| Command | Source Content | Target Output Folder | Key Generated Features |
| :--- | :--- | :--- | :--- |
| `extract-all` (alias: `all`) | Chapters 4, 6, 9 | `output/` (all subfolders & `.base` files) | Runs all four extractors in sequence, generating Virtues, Flaws, Abilities, Spells, Guidelines, and standalone Base databases in a single pass with consolidated progress reporting. |
| `extract-virtues-flaws` | Chapter 4: Virtues & Flaws | `output/virtues/`<br>`output/flaws/`<br>`output/virtues.base`<br>`output/flaws.base` | Categorized as Virtue or Flaw; parses costs (Minor/Major/Free), types (Hermetic, General, Social Status, etc.), and custom properties; generates standalone `virtues.base` and `flaws.base` databases. |
| `extract-abilities` | Chapter 6: Abilities | `output/abilities/`<br>`output/abilities.base` | Parses ability types (General, Academic, Arcane, Martial, Supernatural), specialties list, and untrained flags; generates standalone `abilities.base` database. |
| `extract-spells` | Chapter 9: Spells | `output/spells/`<br>`output/spells.base` | Parses Arts, requisites, Range, Duration, Target, Ritual flag, base level, magnitude breakdown (+R/+D/+T modifiers), and direct guideline anchor link; generates standalone `spells.base` database. |
| `extract-guidelines` | Chapter 9: Spells | `output/guidelines/` | Generates 50 Technique + Form guideline notes with level headings, block IDs on individual bullets, and embedded Obsidian Bases query tables. |

---

## Prerequisites & Installation

### Requirements
- **Python**: Requires Python **3.15** or higher (`>=3.15`). Tested with Python 3.15.
- **Git Submodule**: The upstream rules text is maintained in the `Ars-Magica-Open-License` git submodule.

### Setup

1. **Clone the repository and initialize submodules**:
   ```bash
   git clone https://github.com/your-username/obsidian-ars-magica.git
   cd obsidian-ars-magica
   git submodule update --init --recursive
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install the package in editable mode**:
   ```bash
   # Standard installation
   pip install -e .

   # Or with development dependencies (pytest, ruff):
   pip install -e ".[dev]"
   ```

---

## Usage & CLI Reference

Commands can be invoked using the installed console script (`obsidian-ars-magica`) or via Python module execution (`python -m obsidian_ars_magica.cli`).

### Global Flags

All commands accept the following optional arguments:
- `--source <path>`: Path to the core rules markdown file (default: `Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md`).
- `--output <path>`: Target root directory for generated notes (default: `output`). Can be pointed directly to an existing Obsidian vault directory.

```
usage: obsidian-ars-magica [-h] {extract-virtues-flaws,extract-abilities,extract-spells,extract-guidelines,extract-all} ...
```

---

### Individual Commands

#### 1. Extract Virtues and Flaws (`extract-virtues-flaws`)
Extracts all Virtues and Flaws from Chapter 4 into separate files in `virtues/` and `flaws/`, and generates standalone `virtues.base` and `flaws.base` databases.

```bash
obsidian-ars-magica extract-virtues-flaws
```
*Custom output example:*
```bash
obsidian-ars-magica extract-virtues-flaws --output "C:/MyVault/ArsMagica"
```

#### 2. Extract Abilities (`extract-abilities`)
Extracts all character abilities from Chapter 6 into separate files in `abilities/`, and generates a standalone `abilities.base` database.

```bash
obsidian-ars-magica extract-abilities
```
*Custom output example:*
```bash
obsidian-ars-magica extract-abilities --output "C:/MyVault/ArsMagica"
```

#### 3. Extract Spells (`extract-spells`)
Extracts all Hermetic spells from Chapter 9 into separate files in `spells/`, and generates a standalone `spells.base` database. Computes magnitude calculations, canonical R/D/T parameters, requisites, and cross-links to guideline notes.

```bash
obsidian-ars-magica extract-spells
```
*Custom output example:*
```bash
obsidian-ars-magica extract-spells --output "C:/MyVault/ArsMagica"
```

#### 4. Extract Spell Guidelines (`extract-guidelines`)
Extracts all 50 Hermetic Technique + Form guideline sections (5 Techniques &times; 10 Forms) into individual notes under `guidelines/`. Each note contains level subsections with block IDs and an embedded Obsidian Bases query table.

```bash
obsidian-ars-magica extract-guidelines
```
*Custom output example:*
```bash
obsidian-ars-magica extract-guidelines --output "C:/MyVault/ArsMagica"
```

---

### Bulk Extraction (`extract-all` / `all`)

To run all extraction tools in sequence and generate a complete vault in one go, use `extract-all` (or the short alias `all`):

```bash
obsidian-ars-magica extract-all
```

*Custom output example:*
```bash
obsidian-ars-magica extract-all --output "C:/MyVault/ArsMagica"
```

*Using shorthand alias:*
```bash
obsidian-ars-magica all --output "C:/MyVault/ArsMagica"
```

This sequentially executes Virtues & Flaws, Abilities, Spells, and Spell Guidelines, streaming step progress and displaying a total note count upon completion.

*(Alternative: You can also run individual commands in a custom shell loop if desired)*
- **PowerShell (Windows)**:
  ```powershell
  @("extract-virtues-flaws", "extract-abilities", "extract-spells", "extract-guidelines") | ForEach-Object {
      obsidian-ars-magica $_ --output "output"
  }
  ```
- **Bash (Linux / macOS)**:
  ```bash
  for cmd in extract-virtues-flaws extract-abilities extract-spells extract-guidelines; do
      obsidian-ars-magica "$cmd" --output "output"
  done
  ```

---

## Output Vault Structure

When all tools are run with `--output output`, the resulting folder structure is:

```
output/
├── abilities/
│   ├── Animal-Handling.md
│   ├── Chirurgy.md
│   └── ...
├── flaws/
│   ├── Blatant-Gift.md
│   ├── Enemies.md
│   └── ...
├── guidelines/
│   ├── Creo-Animal-Guidelines.md
│   ├── Creo-Ignem-Guidelines.md
│   └── ... (50 Technique-Form notes)
├── spells/
│   ├── Ball-of-Abysmal-Flame.md
│   ├── Circular-Ward-Against-Demons.md
│   └── ...
└── virtues/
    ├── Affinity-with-Art.md
    ├── The-Gift.md
    └── ...
```

---

## Note Examples

### Spell Note Example (`spells/Ball-of-Abysmal-Flame.md`)

````markdown
---
name: "Ball of Abysmal Flame"
category: "Spell"
technique: "Creo"
form: "Ignem"
arts: "CrIg"
level: 35
technique_requisites: []
form_requisites: []
range: "Voice"
duration: "Momentary"
target: "Individual"
ritual: false
base_level: 25
range_magnitude: 2
duration_magnitude: 0
target_magnitude: 0
additional_magnitudes: 0
total_magnitudes: 2
guideline: "[[Creo-Ignem-Guidelines#Level 25]]"
aliases:
  - "Ball of Abysmal Flame"
  - "CrIg 35"
tags:
  - "spell"
  - "creo"
  - "ignem"
  - "crig"
---

# Ball of Abysmal Flame

> [!metadata] **CrIg 35**
> - **R:** Voice, **D:** Mom, **T:** Ind
> - **Base:** 25 | **Total Magnitudes:** +2 (+2 Voice)
> - **Guideline:** [[Creo-Ignem-Guidelines#Level 25|Creo Ignem Base 25]]

A ball of fire shoots from your hand to strike a target up to Voice range away, inflicting +30 damage.
````

### Guideline Note Example (`guidelines/Creo-Ignem-Guidelines.md`)

````markdown
---
name: "Creo Ignem Guidelines"
category: "Spell Guidelines"
technique: "Creo"
form: "Ignem"
arts: "CrIg"
aliases:
  - "Creo Ignem Guidelines"
  - "CrIg Guidelines"
tags:
  - "spell-guidelines"
  - "creo"
  - "ignem"
  - "crig"
---

# Creo Ignem Guidelines

### Level 5
- Create a fire that inflicts +5 damage. ^crig-5-1

### Level 10
- Create a fire that inflicts +10 damage. ^crig-10-1

...

---

## Known Spells

```base
filters:
  and:
    - file.inFolder("spells")
    - 'technique == "Creo"'
    - 'form == "Ignem"'
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
```
````

---

## Python API Usage

All core extraction and formatting functionality can be used programmatically in custom Python scripts:

```python
from pathlib import Path
from obsidian_ars_magica import (
    export_abilities,
    export_guidelines,
    export_spells,
    export_virtues_and_flaws,
)

source_path = Path("Ars-Magica-Open-License/reviewed/Ars Magica - Definitive Edition (Core Rules).md")
output_dir = Path("output")

# Export all categories
export_virtues_and_flaws(source_path, output_dir)
export_abilities(source_path, output_dir)
export_spells(source_path, output_dir)
export_guidelines(source_path, output_dir)
```

Lower-level functions (such as `extract_spells`, `extract_guidelines`, `format_spell_markdown`, and `parse_qualifiers`) are also exported from `obsidian_ars_magica`.

---

## Development & Testing

Run automated tests and linting using the project virtual environment:

```powershell
# Run the pytest test suite
.venv\Scripts\pytest

# Run linter checks
.venv\Scripts\ruff check src tests
```

On Linux or macOS:
```bash
pytest
ruff check src tests
```

---

## License & Attribution

- **Tooling Code**: Licensed under the [MIT License](LICENSE). Source code files include the `# SPDX-License-Identifier: MIT` identifier.
- **Rules Content**: *Ars Magica 5th Edition Definitive Edition* text is provided by Trident, Inc. d/b/a Atlas Games under the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/) license (see the [Ars Magica Open License](https://www.atlas-games.com/arsmagica/openars)).
- **Submodule Protection**: Do not modify files in the `Ars-Magica-Open-License/` directory directly, as it tracks the upstream open license repository.
