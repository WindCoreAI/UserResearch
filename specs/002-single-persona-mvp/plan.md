# Implementation Plan: Single Persona MVP

**Branch**: `002-single-persona-mvp` | **Date**: 2026-01-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-single-persona-mvp/spec.md`

## Summary

Execute single persona research sessions using Claude Code subagents via the Task tool. This phase builds on the Phase 0 foundation (PersonaLoader, PromptBuilder, personas) to enable researchers to ask questions to synthetic personas and receive structured, quality-validated responses through a CLI interface.

## Technical Context

**Language/Version**: Python 3.11+ (continuation from Phase 0)
**Primary Dependencies**: PyYAML, Pydantic, Click, Jinja2 (Phase 0), Rich (new - for formatted output)
**Storage**: File-based JSON for session transcripts (optional export)
**Testing**: pytest with pytest-cov
**Target Platform**: macOS/Linux CLI (cross-platform Python)
**Project Type**: Single project (CLI tool extension)
**Performance Goals**: Research session response < 30 seconds, session parsing < 1 second
**Constraints**: Depends on Claude Code Task tool for subagent execution; operates within Claude Code environment only
**Scale/Scope**: Single persona per session, 5 question types, quality metrics baseline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Phase 1 Compliance | Status |
|-----------|-------------|-------------------|--------|
| I. Subagent-First | Research via Claude Code subagents | SingleSessionRunner spawns Task tool subagent for persona simulation | PASS |
| II. Persona Integrity | YAML with Big Five, Schwartz; versioned; immutable in session | Uses Phase 0 PersonaLoader; persona locked for session duration | PASS |
| III. Honest Limitations | Outputs state biases; recommend validation | Session output includes limitations disclaimer; metrics flag sycophancy | PASS |
| IV. Quality Through Calibration | Track quality metrics per session | Consistency score, sycophancy rate tracked; exported with session | PASS |
| V. Parallel Execution | Concurrent execution for panels | N/A - Phase 1 is single persona only (sequential by design) | PASS |
| Response Quality Gates | >90% consistency; <30% sycophancy warning | FR-007 flags <70% consistency; FR-013 measures sycophancy | PASS |
| Test-First | Tests before implementation | pytest structure extends Phase 0; quality metric tests written first | PASS |
| Progressive Enhancement | Build on stable Phase 0 | Extends PersonaLoader, PromptBuilder, CLI; no Phase 0 modifications | PASS |

**Gate Status**: PASSED - No violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/002-single-persona-mvp/
├── plan.md              # This file
├── research.md          # Phase 0 output - technical decisions
├── data-model.md        # Phase 1 output - session/response models
├── quickstart.md        # Phase 1 output - usage guide
├── contracts/           # Phase 1 output - CLI interface contracts
│   └── cli-interface.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── persona.py           # (Phase 0) Pydantic models for persona schema
│   ├── enums.py             # (Phase 0) Tech adoption, Schwartz values enums
│   ├── session.py           # (NEW) Research session models
│   └── question.py          # (NEW) Question type models
├── services/
│   ├── __init__.py
│   ├── persona_loader.py    # (Phase 0) Load/validate persona YAML files
│   ├── prompt_builder.py    # (Phase 0) Transform persona to subagent prompt
│   ├── persona_library.py   # (Phase 0) List, search, retrieve personas
│   ├── session_runner.py    # (NEW) Execute single persona sessions
│   ├── response_parser.py   # (NEW) Parse subagent responses into structured data
│   └── quality_metrics.py   # (NEW) Calculate consistency, sycophancy scores
├── cli/
│   ├── __init__.py
│   ├── main.py              # (Phase 0) Click CLI entry point - extended
│   └── formatters.py        # (NEW) Rich output formatters for sessions
└── templates/
    ├── __init__.py
    ├── subagent_prompt.j2   # (Phase 0) Jinja2 template for prompt generation
    └── research_prompt.j2   # (NEW) Template for research question injection

tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_persona_model.py    # (Phase 0)
│   ├── test_persona_loader.py   # (Phase 0)
│   ├── test_prompt_builder.py   # (Phase 0)
│   ├── test_session_model.py    # (NEW) Session model validation
│   ├── test_question_model.py   # (NEW) Question type validation
│   ├── test_response_parser.py  # (NEW) Response parsing tests
│   └── test_quality_metrics.py  # (NEW) Quality calculation tests
├── integration/
│   ├── __init__.py
│   ├── test_cli.py              # (Phase 0) - extended
│   └── test_session_runner.py   # (NEW) End-to-end session tests
└── contract/
    ├── __init__.py
    ├── test_persona_schema.py   # (Phase 0)
    └── test_session_schema.py   # (NEW) Session output schema tests
```

**Structure Decision**: Extends Phase 0 single project structure. New models in `models/`, new services in `services/`, CLI commands added to existing `main.py`. Maintains clear separation between Phase 0 foundation and Phase 1 research execution.

## Complexity Tracking

> No violations - table not required.
