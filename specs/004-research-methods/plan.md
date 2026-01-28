# Implementation Plan: Research Methods

**Branch**: `004-research-methods` | **Date**: 2026-01-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-research-methods/spec.md`

## Summary

Extend the Synthetic User Research Platform to support three distinct research methodologies: **Survey** (structured questionnaires with quantitative aggregation), **Interview** (in-depth conversations with follow-up capability), and **Focus Group** (multi-persona interactive discussions). Each method builds on the existing SessionRunner and PanelExecutor infrastructure, adding method-specific execution engines, response parsing, and report generation. Research protocols will be stored as versioned YAML definitions, consistent with existing persona and panel patterns.

## Technical Context

**Language/Version**: Python 3.11+ (continuation from Phase 0/1/2)
**Primary Dependencies**: PyYAML, Pydantic>=2.0, Click>=8.0, Jinja2>=3.0, Rich>=13.0, asyncio (existing), statistics (stdlib)
**Storage**: YAML files for protocol definitions (`protocols/`), JSON for session exports
**Testing**: pytest>=7.0, pytest-asyncio>=0.23.0, pytest-cov>=4.0
**Target Platform**: CLI (cross-platform: Linux, macOS, Windows)
**Project Type**: Single project (extends existing `src/` structure)
**Performance Goals**: Execute 10-question survey across 5-persona panel in under 5 minutes (SC-001)
**Constraints**: Maintain 70%+ persona consistency scores (SC-007), follow-up relevance ≥80% (SC-003)
**Scale/Scope**: 3 research methods, 35 functional requirements, 8 new CLI commands, ~15 new source files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| I. Subagent-First Architecture | All research execution through Claude Code subagents | ✅ PASS | Reuses existing SessionRunner/PanelExecutor which delegate to Task tool |
| II. Persona Integrity | Personas defined declaratively, immutable within session | ✅ PASS | Extends existing PersonaLoader; no modifications to persona schema |
| III. Honest Limitations | Outputs explicitly state synthetic data limitations | ✅ PASS | Existing disclaimer pattern in formatters.py; will extend to new methods |
| IV. Quality Through Calibration | Quality metrics tracked for every session | ✅ PASS | Extends QualityMetricsCalculator; trait consistency applies to all methods |
| V. Parallel Execution | Panel research maximizes efficiency through parallel execution | ✅ PASS | Survey panels reuse PanelExecutor; focus groups use turn-based simulation |
| Response Quality Gates | Consistency >90%, sycophancy warning at >30% | ✅ PASS | Existing gates in quality_metrics.py apply to all methods |
| Data Handling | No real PII, full reproducibility, labeled exports | ✅ PASS | Existing patterns; exports include method_type in metadata |

**Gate Result**: PASS - All constitution requirements satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/004-research-methods/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── survey.py            # NEW: Survey, SurveyQuestion, SurveyResponse
│   ├── interview.py         # NEW: InterviewGuide, InterviewSection, InterviewTranscript
│   ├── focus_group.py       # NEW: FocusGroup, DiscussionTurn, DiscussionLog
│   ├── protocol.py          # NEW: ResearchProtocol base and variants
│   ├── persona.py           # EXISTING: No changes
│   ├── session.py           # EXISTING: Minor extension for method type
│   ├── panel.py             # EXISTING: No changes
│   ├── question.py          # EXISTING: No changes
│   ├── aggregation.py       # EXISTING: Extend for survey statistics
│   └── enums.py             # EXISTING: Add ResearchMethodType enum
├── services/
│   ├── survey_engine.py     # NEW: SurveyEngine execution
│   ├── interview_engine.py  # NEW: InterviewEngine with follow-ups
│   ├── focus_group_engine.py # NEW: FocusGroupEngine with turn-taking
│   ├── protocol_loader.py   # NEW: Load/validate/save protocols
│   ├── survey_aggregator.py # NEW: Statistical aggregation for surveys
│   ├── session_runner.py    # EXISTING: No changes (reused)
│   ├── panel_executor.py    # EXISTING: No changes (reused)
│   ├── response_parser.py   # EXISTING: Extend for method-specific parsing
│   ├── quality_metrics.py   # EXISTING: No changes (reused)
│   └── report_generator.py  # EXISTING: Extend for method-specific reports
├── cli/
│   ├── survey_commands.py   # NEW: survey run/create
│   ├── interview_commands.py # NEW: interview run/create
│   ├── focus_group_commands.py # NEW: focus-group run/create
│   ├── protocol_commands.py # NEW: protocol list/show/delete
│   ├── main.py              # EXISTING: Register new command groups
│   ├── panel_commands.py    # EXISTING: No changes
│   └── formatters.py        # EXISTING: Extend for method-specific output
└── templates/
    ├── survey_prompt.j2     # NEW: Survey execution prompt
    ├── interview_prompt.j2  # NEW: Interview section prompt
    ├── focus_group_prompt.j2 # NEW: Focus group moderation prompt
    ├── survey_report.j2     # NEW: Survey results report
    ├── interview_report.j2  # NEW: Interview transcript report
    ├── focus_group_report.j2 # NEW: Focus group discussion report
    ├── research_prompt.j2   # EXISTING: No changes
    └── panel_report.j2      # EXISTING: No changes

protocols/
├── surveys/             # NEW: Survey protocol definitions
│   └── sample-survey.yaml
├── interviews/          # NEW: Interview guide definitions
│   └── sample-interview.yaml
└── focus-groups/        # NEW: Focus group definitions
    └── sample-focus-group.yaml

tests/
├── unit/
│   ├── test_survey_model.py      # NEW
│   ├── test_interview_model.py   # NEW
│   ├── test_focus_group_model.py # NEW
│   ├── test_protocol_model.py    # NEW
│   ├── test_survey_engine.py     # NEW
│   ├── test_interview_engine.py  # NEW
│   ├── test_focus_group_engine.py # NEW
│   ├── test_protocol_loader.py   # NEW
│   └── test_survey_aggregator.py # NEW
├── integration/
│   ├── test_survey_cli.py        # NEW
│   ├── test_interview_cli.py     # NEW
│   └── test_focus_group_cli.py   # NEW
└── contract/
    └── test_protocol_schema.py   # NEW
```

**Structure Decision**: Single project extending existing `src/` structure. New models, services, CLI commands, and templates follow established patterns from Phase 1/2. Protocol storage mirrors existing `personas/` and `panels/` directory organization.

## Complexity Tracking

> No constitution violations identified. This section remains empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | - | - |

---

## Constitution Check (Post-Phase 1 Design)

*Re-evaluation after completing Phase 0 research and Phase 1 design artifacts.*

| Principle | Requirement | Status | Evidence from Design |
|-----------|-------------|--------|---------------------|
| I. Subagent-First Architecture | All research execution through Claude Code subagents | ✅ PASS | SurveyEngine, InterviewEngine, FocusGroupEngine all use SessionRunner which delegates to Task tool (research.md §1-3) |
| II. Persona Integrity | Personas defined declaratively, immutable within session | ✅ PASS | No persona model changes; protocols reference persona_ids only (data-model.md §4-5) |
| III. Honest Limitations | Outputs explicitly state synthetic data limitations | ✅ PASS | CLI contracts specify disclaimer in text output; JSON includes "synthetic" metadata (contracts/cli-contracts.md §7) |
| IV. Quality Through Calibration | Quality metrics tracked for every session | ✅ PASS | All result models include quality_metrics field; extends existing QualityMetricsCalculator (data-model.md §2-4) |
| V. Parallel Execution | Panel research maximizes efficiency through parallel execution | ✅ PASS | Survey panel execution reuses PanelExecutor with asyncio (research.md §1); focus groups use sequential turn-based approach as designed |
| Response Quality Gates | Consistency >90%, sycophancy warning at >30% | ✅ PASS | Existing gates apply to all methods; method-specific quality extensions documented (research.md §8) |
| Data Handling | No real PII, full reproducibility, labeled exports | ✅ PASS | Protocol versioning enables reproducibility; JSON exports include method_type (contracts/cli-contracts.md §5) |

**Post-Design Gate Result**: ✅ PASS - All constitution requirements remain satisfied after Phase 1 design.

---

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Implementation Plan | `specs/004-research-methods/plan.md` | ✅ Complete |
| Research Findings | `specs/004-research-methods/research.md` | ✅ Complete |
| Data Model | `specs/004-research-methods/data-model.md` | ✅ Complete |
| CLI Contracts | `specs/004-research-methods/contracts/cli-contracts.md` | ✅ Complete |
| Quickstart Guide | `specs/004-research-methods/quickstart.md` | ✅ Complete |

---

## Next Steps

Run `/speckit.tasks` to generate the implementation task list in `specs/004-research-methods/tasks.md`.
