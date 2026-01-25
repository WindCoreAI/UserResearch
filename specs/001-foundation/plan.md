# Implementation Plan: Phase 0 Foundation

**Branch**: `001-foundation` | **Date**: 2026-01-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-foundation/spec.md`

## Summary

Establish the foundational infrastructure for the Synthetic User Research Platform: define the YAML schema for persona definitions using psychological frameworks (Big Five, Schwartz values), create five archetypal base personas, build a prompt template engine to transform personas into Claude Code subagent prompts, and provide a basic CLI for persona management.

## Technical Context

**Language/Version**: Python 3.11+ (wide YAML support, rich CLI libraries, rapid prototyping)
**Primary Dependencies**: PyYAML (parsing), Pydantic (schema validation), Click (CLI), Jinja2 (templating)
**Storage**: File-based YAML (personas/), no database required for Phase 0
**Testing**: pytest with pytest-cov for coverage
**Target Platform**: macOS/Linux CLI (cross-platform Python)
**Project Type**: Single project (CLI tool with library)
**Performance Goals**: CLI response < 3 seconds, persona validation < 100ms
**Constraints**: No external API calls required for Phase 0 (prompt generation is local)
**Scale/Scope**: 5 base personas, ~10 CLI commands, foundation for future phases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Phase 0 Compliance | Status |
|-----------|-------------|-------------------|--------|
| I. Subagent-First | Research capabilities via subagents | N/A - Phase 0 is infrastructure only | PASS |
| II. Persona Integrity | YAML with Big Five, Schwartz values; versioned; immutable in session | Schema enforces Big Five + Schwartz; file-based versioning | PASS |
| III. Honest Limitations | Outputs state biases; recommend real user validation | N/A - no research outputs in Phase 0 | PASS |
| IV. Quality Through Calibration | Track quality metrics; 60-90 day refinement | N/A - metrics come in Phase 4 | PASS |
| V. Parallel Execution | Concurrent subagent execution | N/A - single persona in Phase 0 | PASS |
| Persona Requirements | Big Five (1-10), 2+ Schwartz values, tech adoption, anti-sycophancy | Schema enforces all requirements | PASS |
| Test-First | Tests before implementation; automated validation | pytest structure ready; schema validation automated | PASS |
| Progressive Enhancement | Build on stable foundation | Phase 0 is the foundation itself | PASS |

**Gate Status**: PASSED - No violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── persona.py           # Pydantic models for persona schema
│   └── enums.py             # Tech adoption, Schwartz values enums
├── services/
│   ├── __init__.py
│   ├── persona_loader.py    # Load/validate persona YAML files
│   ├── prompt_builder.py    # Transform persona to subagent prompt
│   └── persona_library.py   # List, search, retrieve personas
├── cli/
│   ├── __init__.py
│   └── main.py              # Click CLI entry point
└── templates/
    ├── __init__.py
    └── subagent_prompt.j2   # Jinja2 template for prompt generation

personas/
├── definitions/
│   ├── tech-early-adopter.yaml
│   ├── skeptical-late-adopter.yaml
│   ├── busy-professional.yaml
│   ├── privacy-conscious-user.yaml
│   └── power-user.yaml
└── templates/
    └── persona-template.yaml    # Blank template for new personas

templates/
└── prompts/
    └── anti-sycophancy.md       # Reusable anti-sycophancy instructions

tests/
├── __init__.py
├── conftest.py                  # pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_persona_model.py   # Pydantic model validation
│   ├── test_persona_loader.py  # YAML loading tests
│   └── test_prompt_builder.py  # Prompt generation tests
├── integration/
│   ├── __init__.py
│   └── test_cli.py             # CLI command tests
└── contract/
    ├── __init__.py
    └── test_persona_schema.py  # Schema contract tests
```

**Structure Decision**: Single project structure with clear separation between models, services, and CLI. The `personas/` directory at root level provides easy access for researchers to browse and edit persona files directly.

## Complexity Tracking

> No violations - table not required.
