# Implementation Plan: Multi-Persona Panels

**Branch**: `003-multi-persona-panels` | **Date**: 2026-01-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-multi-persona-panels/spec.md`

## Summary

Execute parallel multi-persona research sessions using Claude Code subagents via the Task tool. This phase builds on Phase 0 (PersonaLoader, PromptBuilder) and Phase 1 (SessionRunner, ResponseParser, QualityMetrics) to enable researchers to query entire panels of synthetic personas simultaneously, with automatic response aggregation, theme extraction, and research report generation through an extended CLI interface.

## Technical Context

**Language/Version**: Python 3.11+ (continuation from Phase 0/1)
**Primary Dependencies**: PyYAML, Pydantic, Click, Jinja2 (Phase 0/1), Rich (Phase 1), asyncio (new - for parallel execution)
**Storage**: YAML files for panel definitions, JSON for session export (consistent with Phase 1)
**Testing**: pytest with pytest-cov, pytest-asyncio (new)
**Target Platform**: macOS/Linux CLI (cross-platform Python)
**Project Type**: Single project (CLI tool extension)
**Performance Goals**: 5-persona panel < 60 seconds; 10-persona panel achieves 3x speedup vs sequential
**Constraints**: Depends on Claude Code Task tool for subagent execution; operates within Claude Code environment only
**Scale/Scope**: Panels of 2-50 personas, 4 pre-built panels, custom panel support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Phase 2 Compliance | Status |
|-----------|-------------|-------------------|--------|
| I. Subagent-First | Research via Claude Code subagents | PanelExecutor spawns multiple Task tool subagents in parallel; aggregator also uses Task tool | PASS |
| II. Persona Integrity | YAML with Big Five, Schwartz; versioned; immutable in session | Uses Phase 0 PersonaLoader; personas locked for panel session duration | PASS |
| III. Honest Limitations | Outputs state biases; recommend validation | All panel outputs include synthetic data disclaimer; report includes limitations section | PASS |
| IV. Quality Through Calibration | Track quality metrics per session | Panel-level quality metrics (avg consistency, theme confidence, divergence); extends Phase 1 metrics | PASS |
| V. Parallel Execution | Concurrent execution for panels | asyncio-based parallel execution of all personas; aggregation after all responses complete | PASS |
| Response Quality Gates | >90% consistency; <30% sycophancy warning | Panel gates: avg consistency >70%, completion rate >80%; warnings propagated from individual sessions | PASS |
| Test-First | Tests before implementation | pytest-asyncio for concurrent tests; aggregation tests written first | PASS |
| Progressive Enhancement | Build on stable Phase 0/1 | Extends SessionRunner, ResponseParser, QualityMetrics; no Phase 0/1 modifications | PASS |

**Gate Status**: PASSED - No violations requiring justification

**Post-Design Re-Check**: All principles remain satisfied after Phase 1 design artifacts completed.

## Project Structure

### Documentation (this feature)

```text
specs/003-multi-persona-panels/
├── plan.md              # This file
├── research.md          # Phase 0 output - technical decisions
├── data-model.md        # Phase 1 output - panel/aggregation models
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
│   ├── session.py           # (Phase 1) Research session models
│   ├── question.py          # (Phase 1) Question type models
│   ├── panel.py             # (NEW) Panel definition models
│   └── aggregation.py       # (NEW) Aggregated results models
├── services/
│   ├── __init__.py
│   ├── persona_loader.py    # (Phase 0) Load/validate persona YAML files
│   ├── prompt_builder.py    # (Phase 0) Transform persona to subagent prompt
│   ├── persona_library.py   # (Phase 0) List, search, retrieve personas
│   ├── session_runner.py    # (Phase 1) Execute single persona sessions
│   ├── response_parser.py   # (Phase 1) Parse subagent responses
│   ├── quality_metrics.py   # (Phase 1) Calculate quality scores - extended
│   ├── panel_loader.py      # (NEW) Load/validate panel YAML files
│   ├── panel_executor.py    # (NEW) Parallel panel execution
│   ├── response_aggregator.py # (NEW) Aggregate and analyze responses
│   └── report_generator.py  # (NEW) Generate Markdown reports
├── cli/
│   ├── __init__.py
│   ├── main.py              # (Phase 0/1) Click CLI entry point - extended
│   ├── formatters.py        # (Phase 1) Rich output formatters - extended
│   └── panel_commands.py    # (NEW) Panel subcommands
└── templates/
    ├── __init__.py
    ├── subagent_prompt.j2   # (Phase 0) Jinja2 template for prompt generation
    ├── research_prompt.j2   # (Phase 1) Template for research question injection
    ├── aggregation_prompt.j2 # (NEW) Template for aggregation subagent
    └── panel_report.j2      # (NEW) Template for Markdown reports

panels/
├── definitions/             # (NEW) Pre-built panel definitions
│   ├── tech-adopters.yaml
│   ├── skeptics-critics.yaml
│   ├── power-users.yaml
│   └── general-population.yaml
└── custom/                  # (NEW) User-created panels

tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_persona_model.py     # (Phase 0)
│   ├── test_persona_loader.py    # (Phase 0)
│   ├── test_prompt_builder.py    # (Phase 0)
│   ├── test_session_model.py     # (Phase 1)
│   ├── test_question_model.py    # (Phase 1)
│   ├── test_response_parser.py   # (Phase 1)
│   ├── test_quality_metrics.py   # (Phase 1) - extended
│   ├── test_panel_model.py       # (NEW) Panel model validation
│   ├── test_aggregation_model.py # (NEW) Aggregation model validation
│   ├── test_panel_loader.py      # (NEW) Panel loader tests
│   ├── test_response_aggregator.py # (NEW) Aggregation logic tests
│   └── test_report_generator.py  # (NEW) Report generation tests
├── integration/
│   ├── __init__.py
│   ├── test_cli.py               # (Phase 0/1) - extended
│   ├── test_session_runner.py    # (Phase 1)
│   └── test_panel_executor.py    # (NEW) End-to-end panel tests
└── contract/
    ├── __init__.py
    ├── test_persona_schema.py    # (Phase 0)
    ├── test_session_schema.py    # (Phase 1)
    └── test_panel_schema.py      # (NEW) Panel/aggregation schema tests
```

**Structure Decision**: Extends Phase 0/1 single project structure. New models in `models/`, new services in `services/`, panel CLI commands in separate module for clarity. New `panels/` directory at root for panel definitions (parallel to `personas/`). Maintains clear separation between foundation, single-session, and panel functionality.

## Complexity Tracking

> No violations - table not required.
