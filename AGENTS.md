# Agent Instructions & Guidelines - obsidian-ars-magica

## 1. Project Context & Boundaries
- **Project Purpose**: Python tooling to process and enhance markdown files located in `Ars-Magica-Open-License/reviewed` for use with Obsidian.
- **Submodule Protection**: NEVER modify, delete, or overwrite any files inside `Ars-Magica-Open-License/` (it is an upstream git submodule).
- **Read Permissions**: No user permission is required to read files or directories within the project directory (including `Ars-Magica-Open-License/`). Read freely as needed.
- **Test Permissions**: No user permission is required to run unit tests or linting. Run these freely as needed.
- **Output Separation**: All processed, converted, or generated markdown files must be written to a separate designated directory in this project (e.g., `output/` or user-specified target directory).

## 2. Communication & Disambiguation
- **Be Concise**: Keep explanations, answers, and summaries direct, relevant, and free of fluff.
- **Disambiguation Protocol**:
  1. If an instruction is unclear or has multiple interpretations, first infer the intended meaning from repository context and past interactions.
  2. If confident in the inference: explicitly state the inferred interpretation and ask to confirm understanding before taking major actions.
  3. If still unsure: immediately ask for clarification with targeted questions.

## 3. Python Development Standards
- **Code Organization**: Organize code into cohesive modules and functions following standard Python best practices (e.g., `src/<package_name>/`). Maintain single responsibility per function/module.
- **Reuse Before Rewriting**: Leverage existing standard library modules, installed third-party libraries, and internal project utilities before writing custom implementations.
- **Dependency Management & Permission**: If an external or third-party package not currently installed in the local environment provides functionality relevant to the task, request permission from the user before installing it.
- **Readability & Comments**: Write human-readable code. Add clear comments explaining non-trivial logic, domain rules, and design choices.

## 4. Testing & Regression Workflow (Pytest)
- **Framework**: All automated tests must use `pytest` and reside in `tests/`.
- **New Code Coverage**: When writing new functions or modules, always accompany them with unit tests verifying correctness, edge cases, and expected failures.
- **Bug Fix & Regression Protocol**:
  1. When addressing a bug or unwanted behavior, check whether the scenario is already covered by an existing test.
  2. If a test already covered the scenario but passed, fix the test assertions/setup so it accurately detects the flaw.
  3. If no test covers the scenario, create a new unit test reproducing the bug.
  4. Verify that the test FAILS against the existing/unpatched code.
  5. Apply the fix and verify that the test PASSES against the updated code.

