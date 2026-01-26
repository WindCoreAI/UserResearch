# Tasks: Multi-Persona Panels

**Input**: Design documents from `/specs/003-multi-persona-panels/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md, research.md, quickstart.md

**Tests**: Included per Constitution Test-First principle ("Quality metrics tests MUST be written before feature implementation")

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- Panel definitions: `panels/definitions/` (pre-built), `panels/custom/` (user-created)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for panel support

- [X] T001 Create panels/ directory structure with definitions/ and custom/ subdirectories
- [X] T002 [P] Add pytest-asyncio to dev dependencies in pyproject.toml
- [X] T003 [P] Update tests/conftest.py with asyncio fixtures for panel testing

**Checkpoint**: Directory structure ready for panel definitions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and services that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase

- [X] T004 [P] Create unit tests for ResearchPanel model validation in tests/unit/test_panel_model.py
- [X] T005 [P] Create unit tests for aggregation models (Theme, AggregatedResults, PanelQualityMetrics) in tests/unit/test_aggregation_model.py
- [X] T006 [P] Create unit tests for PanelLoader service in tests/unit/test_panel_loader.py
- [X] T007 [P] Create contract tests for panel schema validation in tests/contract/test_panel_schema.py

### Implementation for Foundational Phase

- [X] T008 [P] Create ResearchPanel and PanelSessionStatus models in src/models/panel.py
- [X] T009 [P] Create aggregation models (Theme, QuoteReference, SentimentDistribution, ConsensusPoint, DivergencePoint, Position, AggregatedResults, PanelQualityMetrics) in src/models/aggregation.py
- [X] T010 Create PanelSession model in src/models/panel.py (depends on T008, T009)
- [X] T011 Update src/models/__init__.py to export new panel and aggregation models
- [X] T012 Create PanelLoader service with load_panel() and validate_panel() in src/services/panel_loader.py
- [X] T013 Create aggregation prompt template in src/templates/aggregation_prompt.j2

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Stories 1+2 - Core Panel Research (Priority: P1) 🎯 MVP

**Goal**: Execute panel research sessions with parallel persona querying and automatic response aggregation with themes, sentiment distribution, consensus/divergence analysis

**Independent Test**: Run `research panel run --panel=tech-adopters --question="Test question"` and verify all personas respond with aggregated themes, sentiment distribution, and consensus/divergence points displayed

### Tests for User Stories 1+2

- [X] T014 [P] [US1+2] Create unit tests for PanelExecutor service in tests/unit/test_panel_executor.py
- [X] T015 [P] [US1+2] Create unit tests for ResponseAggregator service in tests/unit/test_response_aggregator.py
- [ ] T016 [P] [US1+2] Create integration tests for panel execution flow in tests/integration/test_panel_executor.py
- [X] T017 [P] [US1+2] Create contract tests for CLI panel run output format in tests/contract/test_panel_schema.py

### Implementation for User Stories 1+2

- [X] T018 [US1+2] Create PanelExecutor service with async parallel execution in src/services/panel_executor.py
- [X] T019 [US1+2] Implement execute_panel() method using asyncio.gather() for concurrent persona sessions
- [X] T020 [US1+2] Add progress callback support to PanelExecutor for real-time status updates
- [X] T021 [US1+2] Implement partial failure handling in PanelExecutor (continue with successful responses)
- [X] T022 [US1+2] Create ResponseAggregator service in src/services/response_aggregator.py
- [X] T023 [US1+2] Implement aggregate_responses() method using Claude Task tool for theme extraction
- [X] T024 [US1+2] Implement sentiment distribution calculation in ResponseAggregator
- [X] T025 [US1+2] Implement consensus point detection (>60% agreement threshold) in ResponseAggregator
- [X] T026 [US1+2] Implement divergence point detection in ResponseAggregator
- [X] T027 [US1+2] Extend QualityMetrics to calculate panel-level metrics in src/services/quality_metrics.py
- [X] T028 [US1+2] Create panel formatters for Rich output in src/cli/formatters.py
- [X] T029 [US1+2] Implement panel header formatter (panel name, question, persona count)
- [X] T030 [US1+2] Implement executive summary formatter
- [X] T031 [US1+2] Implement themes list formatter with percentages and quotes
- [X] T032 [US1+2] Implement sentiment distribution formatter
- [X] T033 [US1+2] Implement consensus points formatter
- [X] T034 [US1+2] Implement divergence points formatter with positions
- [X] T035 [US1+2] Implement quality metrics panel formatter
- [X] T036 [US1+2] Implement individual responses summary formatter
- [X] T037 [US1+2] Implement progress display with Rich Progress in src/cli/formatters.py
- [X] T038 [US1+2] Create panel_commands.py Click command group in src/cli/panel_commands.py
- [X] T039 [US1+2] Implement `research panel run` command with --panel and --question arguments
- [X] T040 [US1+2] Add --format flag (text/json) to panel run command
- [X] T041 [US1+2] Add --timeout flag for per-persona timeout configuration
- [X] T042 [US1+2] Add --quiet flag to suppress progress display
- [X] T043 [US1+2] Register panel command group in src/cli/main.py
- [X] T044 [US1+2] Add synthetic data disclaimer to panel output (per Constitution Principle III)

**Checkpoint**: Core panel research with aggregation is fully functional. User Stories 1 and 2 can be tested independently with `research panel run` command.

---

## Phase 4: User Story 3 - Pre-Built Research Panels (Priority: P2)

**Goal**: Provide 4 pre-built panels (tech-adopters, skeptics-critics, power-users, general-population) with list and show commands

**Independent Test**: Run `research panel list` to see all pre-built panels, then `research panel show tech-adopters` to view panel details with persona composition

### Tests for User Story 3

- [ ] T045 [P] [US3] Create integration tests for panel list command in tests/integration/test_cli.py
- [ ] T046 [P] [US3] Create integration tests for panel show command in tests/integration/test_cli.py

### Implementation for User Story 3

- [ ] T047 [P] [US3] Create tech-adopters.yaml panel definition in panels/definitions/tech-adopters.yaml
- [ ] T048 [P] [US3] Create skeptics-critics.yaml panel definition in panels/definitions/skeptics-critics.yaml
- [ ] T049 [P] [US3] Create power-users.yaml panel definition in panels/definitions/power-users.yaml
- [ ] T050 [P] [US3] Create general-population.yaml panel definition in panels/definitions/general-population.yaml
- [ ] T051 [US3] Implement PanelLibrary service for listing and retrieving panels in src/services/panel_loader.py
- [ ] T052 [US3] Add list_panels() method returning all available panels (pre-built + custom)
- [ ] T053 [US3] Add get_panel_details() method for panel show command
- [ ] T054 [US3] Implement panel list formatter in src/cli/formatters.py
- [ ] T055 [US3] Implement panel show/details formatter in src/cli/formatters.py
- [ ] T056 [US3] Implement `research panel list` command with --type filter in src/cli/panel_commands.py
- [ ] T057 [US3] Implement `research panel show <panel-id>` command in src/cli/panel_commands.py

**Checkpoint**: Pre-built panels are available and can be listed, viewed, and used for research. User Story 3 independently testable.

---

## Phase 5: User Story 4 - Custom Panels (Priority: P2)

**Goal**: Allow researchers to create and manage custom panels with selected personas

**Independent Test**: Run `research panel create --name=test-panel --personas=tech-early-adopter,skeptical-late-adopter` then verify panel is saved and can be used with `research panel run`

### Tests for User Story 4

- [ ] T058 [P] [US4] Create integration tests for panel create command in tests/integration/test_cli.py
- [ ] T059 [P] [US4] Create integration tests for panel delete command in tests/integration/test_cli.py

### Implementation for User Story 4

- [ ] T060 [US4] Implement create_custom_panel() in PanelLoader service in src/services/panel_loader.py
- [ ] T061 [US4] Add persona ID validation in create_custom_panel() (check against PersonaLibrary)
- [ ] T062 [US4] Add duplicate persona detection and removal in create_custom_panel()
- [ ] T063 [US4] Add pre-built panel name conflict detection in create_custom_panel()
- [ ] T064 [US4] Implement save_panel_to_yaml() for persisting custom panels to panels/custom/
- [ ] T065 [US4] Implement delete_custom_panel() in PanelLoader service
- [ ] T066 [US4] Add pre-built panel deletion protection in delete_custom_panel()
- [ ] T067 [US4] Implement `research panel create` command with --name, --personas, --description in src/cli/panel_commands.py
- [ ] T068 [US4] Implement `research panel delete <panel-id>` command with --force flag in src/cli/panel_commands.py
- [ ] T069 [US4] Add confirmation prompt for panel deletion (skip with --force)

**Checkpoint**: Custom panels can be created, saved, used for research, and deleted. User Story 4 independently testable.

---

## Phase 6: User Story 5 - Research Reports (Priority: P3)

**Goal**: Generate formatted Markdown research reports from panel results for stakeholder communication

**Independent Test**: Run `research panel run --panel=tech-adopters --question="Test" --report=report.md` and verify Markdown file contains executive summary, methodology, findings, and individual responses

### Tests for User Story 5

- [ ] T070 [P] [US5] Create unit tests for ReportGenerator service in tests/unit/test_report_generator.py
- [ ] T071 [P] [US5] Create integration tests for --report flag in tests/integration/test_cli.py

### Implementation for User Story 5

- [ ] T072 [US5] Create ReportGenerator service in src/services/report_generator.py
- [ ] T073 [US5] Implement generate_report() method taking PanelSession and returning Markdown string
- [ ] T074 [US5] Create panel_report.j2 Jinja2 template in src/templates/panel_report.j2
- [ ] T075 [US5] Add executive summary section to report template
- [ ] T076 [US5] Add methodology section (panel composition, question, timestamp) to report template
- [ ] T077 [US5] Add aggregated findings section (themes, sentiment, consensus/divergence) to report template
- [ ] T078 [US5] Add individual response summaries section to report template
- [ ] T079 [US5] Add quality assessment section with metrics and warnings to report template
- [ ] T080 [US5] Add synthetic data limitations disclaimer to report template
- [ ] T081 [US5] Add --report flag to `research panel run` command in src/cli/panel_commands.py
- [ ] T082 [US5] Implement report file writing with error handling

**Checkpoint**: Research reports can be generated in Markdown format. User Story 5 independently testable.

---

## Phase 7: User Story 6 - Export Panel Data (Priority: P3)

**Goal**: Export complete panel session data as JSON for external analysis and integration

**Independent Test**: Run `research panel run --panel=tech-adopters --question="Test" --output=data.json` and verify JSON file contains panel, question, all individual responses, aggregation, and quality metrics

### Tests for User Story 6

- [ ] T083 [P] [US6] Create unit tests for JSON export methods in tests/unit/test_panel_model.py
- [ ] T084 [P] [US6] Create integration tests for --output flag in tests/integration/test_cli.py

### Implementation for User Story 6

- [ ] T085 [US6] Add to_dict() method to ResearchPanel model in src/models/panel.py
- [ ] T086 [US6] Add to_dict() method to PanelSession model in src/models/panel.py
- [ ] T087 [US6] Add to_dict() method to AggregatedResults model in src/models/aggregation.py
- [ ] T088 [US6] Add to_dict() method to PanelQualityMetrics model in src/models/aggregation.py
- [ ] T089 [US6] Implement export_session_to_json() function in src/services/panel_executor.py
- [ ] T090 [US6] Add metadata fields (platform_version, speedup_factor, limitations) to export
- [ ] T091 [US6] Add --output flag to `research panel run` command in src/cli/panel_commands.py
- [ ] T092 [US6] Implement JSON file writing with pretty printing

**Checkpoint**: Panel data can be exported to JSON format. User Story 6 independently testable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T093 [P] Add comprehensive error handling for all panel operations in src/cli/panel_commands.py
- [ ] T094 [P] Add error messages per CLI contract (PANEL_NOT_FOUND, PERSONA_NOT_FOUND, etc.)
- [ ] T095 [P] Implement exit codes per CLI contract (0=success, 1=error, 2=warning)
- [ ] T096 Update src/services/__init__.py to export new panel services
- [ ] T097 Update src/cli/__init__.py to export panel commands
- [ ] T098 [P] Run all tests and ensure 100% of new tests pass
- [ ] T099 Run quickstart.md validation - verify all example commands work
- [ ] T100 Code cleanup and docstring additions for new modules

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories 1+2 (Phase 3)**: Depends on Foundational - MVP delivery
- **User Story 3 (Phase 4)**: Depends on Foundational - can run in parallel with US1+2
- **User Story 4 (Phase 5)**: Depends on Foundational - can run in parallel with US1+2, US3
- **User Story 5 (Phase 6)**: Depends on US1+2 (needs PanelSession for reports)
- **User Story 6 (Phase 7)**: Depends on US1+2 (needs PanelSession for export)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS ALL)
    ↓
    ├── Phase 3: US1+2 Core Panel Research (P1) 🎯 MVP
    │       ↓
    │       ├── Phase 6: US5 Reports (P3)
    │       └── Phase 7: US6 Export (P3)
    │
    ├── Phase 4: US3 Pre-Built Panels (P2)
    │
    └── Phase 5: US4 Custom Panels (P2)
```

- **User Stories 1+2 (P1)**: Foundational complete - Core MVP
- **User Story 3 (P2)**: Foundational complete - Can parallel with US1+2
- **User Story 4 (P2)**: Foundational complete - Can parallel with US1+2, US3
- **User Story 5 (P3)**: US1+2 complete (needs panel session data for reports)
- **User Story 6 (P3)**: US1+2 complete (needs panel session data for export)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before CLI commands
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tests (T004-T007) can run in parallel
- Foundational model creation (T008, T009) can run in parallel
- Once Foundational phase completes:
  - US3 and US4 can run in parallel with US1+2 (but US1+2 is higher priority)
  - US5 and US6 can run in parallel after US1+2 completes
- All tests for a user story marked [P] can run in parallel
- Pre-built panel definitions (T047-T050) can all run in parallel

---

## Parallel Example: User Stories 1+2 (MVP)

```bash
# Launch all tests for User Stories 1+2 together:
Task: "Create unit tests for PanelExecutor service in tests/unit/test_panel_executor.py"
Task: "Create unit tests for ResponseAggregator service in tests/unit/test_response_aggregator.py"
Task: "Create integration tests for panel execution flow in tests/integration/test_panel_executor.py"
Task: "Create contract tests for CLI panel run output format in tests/contract/test_panel_schema.py"
```

## Parallel Example: Pre-Built Panels (US3)

```bash
# Launch all panel definitions together:
Task: "Create tech-adopters.yaml panel definition in panels/definitions/tech-adopters.yaml"
Task: "Create skeptics-critics.yaml panel definition in panels/definitions/skeptics-critics.yaml"
Task: "Create power-users.yaml panel definition in panels/definitions/power-users.yaml"
Task: "Create general-population.yaml panel definition in panels/definitions/general-population.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1+2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Stories 1+2 (Core Panel Research)
4. **STOP and VALIDATE**: Run `research panel run` with a test panel
5. Deploy/demo if ready - researchers can now run panel research!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Stories 1+2 → Test independently → **MVP Ready!**
3. Add User Story 3 (Pre-Built Panels) → Researchers have curated panels
4. Add User Story 4 (Custom Panels) → Researchers have full flexibility
5. Add User Story 5 (Reports) → Stakeholder communication enabled
6. Add User Story 6 (Export) → External tool integration enabled
7. Polish → Production quality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Stories 1+2 (MVP - highest priority)
   - Developer B: User Story 3 (Pre-Built Panels)
   - Developer C: User Story 4 (Custom Panels)
3. After US1+2 completes:
   - Developer B: User Story 5 (Reports)
   - Developer C: User Story 6 (Export)
4. All developers: Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [US1+2] = User Stories 1 and 2 combined (tightly coupled P1 stories)
- [US3], [US4], [US5], [US6] = Individual user story labels
- Tests follow Constitution Test-First principle
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Panel definitions in Phase 4 require existing personas from Phase 0/1
