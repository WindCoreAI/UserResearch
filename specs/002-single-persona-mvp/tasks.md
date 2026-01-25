# Tasks: Single Persona MVP

**Input**: Design documents from `/specs/002-single-persona-mvp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included per Constitution "Test-First for Quality" requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependency and extend existing project structure

- [X] T001 Add Rich dependency to pyproject.toml for formatted CLI output
- [X] T002 [P] Create src/models/question.py with QuestionType enum stub
- [X] T003 [P] Create src/models/session.py with SessionStatus enum stub
- [X] T004 [P] Create src/services/session_runner.py module stub
- [X] T005 [P] Create src/services/response_parser.py module stub
- [X] T006 [P] Create src/services/quality_metrics.py module stub
- [X] T007 [P] Create src/cli/formatters.py module stub
- [X] T008 [P] Create src/templates/research_prompt.j2 template stub
- [X] T009 Update src/models/__init__.py to export new models
- [X] T010 Update src/services/__init__.py to export new services

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and enums that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [X] T011 [P] Create tests/unit/test_question_model.py with QuestionType enum tests
- [X] T012 [P] Create tests/unit/test_session_model.py with SessionStatus, Sentiment enum tests

### Implementation for Foundation

- [X] T013 [P] Implement QuestionType enum (OPEN_ENDED, RATING, MULTIPLE_CHOICE) in src/models/question.py
- [X] T014 [P] Implement Sentiment enum (POSITIVE, NEGATIVE, MIXED, NEUTRAL) in src/models/session.py
- [X] T015 [P] Implement SessionStatus enum (PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT) in src/models/session.py
- [X] T016 Implement ResearchQuestion Pydantic model in src/models/question.py with text, type, options, scale validation
- [X] T017 Create research_prompt.j2 Jinja2 template with structured response format instructions in src/templates/research_prompt.j2

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Run Single Persona Research Session (Priority: P1) 🎯 MVP

**Goal**: Execute a research session by spawning a Claude Code subagent with persona prompt and question, capturing the raw response

**Independent Test**: Run `research-cli research single --persona tech-early-adopter --question "Test question"` and verify response is returned with persona characteristics

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US1] Create tests/contract/test_session_schema.py with ResearchSession JSON export schema validation
- [X] T019 [P] [US1] Create tests/integration/test_session_runner.py with mock subagent execution test

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement ResearchSession Pydantic model in src/models/session.py with id, persona_id, persona_name, question, status, started_at, completed_at, metadata fields
- [X] T021 [P] [US1] Implement SessionResponse Pydantic model (basic - raw_text, response_time_ms only) in src/models/session.py
- [X] T022 [US1] Implement SessionRunner class in src/services/session_runner.py with build_prompt() method integrating PromptBuilder and research_prompt.j2
- [X] T023 [US1] Implement SessionRunner.execute() method to create Task tool invocation specification in src/services/session_runner.py
- [X] T024 [US1] Add research command group to src/cli/main.py with Click
- [X] T025 [US1] Implement `research single` subcommand in src/cli/main.py with --persona and --question required arguments
- [X] T026 [US1] Implement basic Rich output formatting for session header and raw response in src/cli/formatters.py
- [X] T027 [US1] Add error handling for persona not found with suggestion list in src/cli/main.py
- [X] T028 [US1] Add error handling for empty question in src/cli/main.py
- [X] T029 [US1] Add timeout handling with --timeout flag (default 30s) in src/cli/main.py

**Checkpoint**: User Story 1 complete - can execute basic research sessions with raw response output

---

## Phase 4: User Story 2 - Parse Structured Response Data (Priority: P2)

**Goal**: Extract sentiment, concerns, suggestions, and key quotes from raw persona responses into structured ParsedResponse

**Independent Test**: Run research session and verify output includes parsed sections (sentiment, concerns, suggestions, overall_impression)

### Tests for User Story 2

- [X] T030 [P] [US2] Create tests/unit/test_response_parser.py with section extraction tests for labeled response format
- [X] T031 [P] [US2] Add fallback parsing tests for unstructured responses in tests/unit/test_response_parser.py

### Implementation for User Story 2

- [X] T032 [P] [US2] Implement ParsedResponse Pydantic model in src/models/session.py with sentiment, overall_impression, concerns, suggestions, key_quotes fields
- [X] T033 [US2] Implement ResponseParser class in src/services/response_parser.py with parse_labeled_sections() method
- [X] T034 [US2] Implement ResponseParser.parse_sentiment() method with sentiment enum mapping in src/services/response_parser.py
- [X] T035 [US2] Implement ResponseParser.extract_concerns() method in src/services/response_parser.py
- [X] T036 [US2] Implement ResponseParser.extract_suggestions() method in src/services/response_parser.py
- [X] T037 [US2] Implement fallback parsing for unstructured responses in src/services/response_parser.py
- [X] T038 [US2] Update SessionResponse model to include parsed field in src/models/session.py
- [X] T039 [US2] Integrate ResponseParser into SessionRunner.execute() in src/services/session_runner.py
- [X] T040 [US2] Add parsed response Rich formatting (sentiment, concerns, suggestions tables) in src/cli/formatters.py
- [X] T041 [US2] Add --format json flag to output complete session as JSON in src/cli/main.py

**Checkpoint**: User Story 2 complete - sessions include structured parsed data

---

## Phase 5: User Story 3 - Validate Response Quality (Priority: P2)

**Goal**: Calculate consistency score and sycophancy indicators to validate response quality against persona traits

**Independent Test**: Run research session and verify quality metrics (consistency score, sycophancy warning, passed_gates) appear in output

### Tests for User Story 3

- [X] T042 [P] [US3] Create tests/unit/test_quality_metrics.py with consistency score calculation tests
- [X] T043 [P] [US3] Add sycophancy detection tests in tests/unit/test_quality_metrics.py

### Implementation for User Story 3

- [X] T044 [P] [US3] Implement QualityMetrics Pydantic model in src/models/session.py with consistency_score, sycophancy_indicators, warnings, passed_gates, matched_traits, missing_traits fields
- [X] T045 [US3] Implement QualityMetricsCalculator class in src/services/quality_metrics.py with trait-keyword mappings per research.md
- [X] T046 [US3] Implement calculate_consistency_score() method comparing response keywords to Big Five trait expectations in src/services/quality_metrics.py
- [X] T047 [US3] Implement detect_sycophancy() method checking positive:negative ratio and sycophancy phrases in src/services/quality_metrics.py
- [X] T048 [US3] Implement check_quality_gates() method with 70% consistency threshold and 4:1 sycophancy ratio in src/services/quality_metrics.py
- [X] T049 [US3] Update SessionResponse model to include quality field in src/models/session.py
- [X] T050 [US3] Integrate QualityMetricsCalculator into SessionRunner in src/services/session_runner.py
- [X] T051 [US3] Add quality metrics Rich formatting (score table, warnings) in src/cli/formatters.py
- [X] T052 [US3] Add --no-quality flag to skip quality calculation in src/cli/main.py
- [X] T053 [US3] Implement exit code 2 for quality warnings in src/cli/main.py
- [X] T054 [US3] Add synthetic data limitations disclaimer to output in src/cli/formatters.py

**Checkpoint**: User Story 3 complete - sessions include quality validation

---

## Phase 6: User Story 4 - Handle Multiple Question Formats (Priority: P3)

**Goal**: Support rating scale (1-10) and multiple choice questions in addition to open-ended

**Independent Test**: Run `research single --type rating --scale 1-10` and `--type choice --options "A,B,C"` and verify appropriate response formats

### Tests for User Story 4

- [X] T055 [P] [US4] Add rating question validation tests in tests/unit/test_question_model.py
- [X] T056 [P] [US4] Add multiple choice question validation tests in tests/unit/test_question_model.py

### Implementation for User Story 4

- [X] T057 [US4] Extend ResearchQuestion model validation for RATING type (scale_min, scale_max) in src/models/question.py
- [X] T058 [US4] Extend ResearchQuestion model validation for MULTIPLE_CHOICE type (options required, 2-10 items) in src/models/question.py
- [X] T059 [US4] Update research_prompt.j2 with conditional sections for rating and choice question instructions in src/templates/research_prompt.j2
- [X] T060 [US4] Update ParsedResponse model to include rating and selected_option fields in src/models/session.py
- [X] T061 [US4] Update ResponseParser to extract rating value and selected_option in src/services/response_parser.py
- [X] T062 [US4] Add --type flag (open, rating, choice) to research single command in src/cli/main.py
- [X] T063 [US4] Add --scale flag for rating questions (default 1-10) in src/cli/main.py
- [X] T064 [US4] Add --options flag for choice questions (comma-separated) in src/cli/main.py
- [X] T065 [US4] Update formatters to display rating/selected_option appropriately in src/cli/formatters.py

**Checkpoint**: User Story 4 complete - supports all three question types

---

## Phase 7: User Story 5 - Export Session Transcript (Priority: P3)

**Goal**: Allow researchers to save complete session data to JSON file for archival

**Independent Test**: Run `research single --output ./session.json` and verify complete session JSON is written to file

### Tests for User Story 5

- [X] T066 [P] [US5] Add session JSON export/import roundtrip test in tests/contract/test_session_schema.py

### Implementation for User Story 5

- [X] T067 [US5] Implement ResearchSession.to_json() method with complete export format per data-model.md in src/models/session.py
- [X] T068 [US5] Add --output flag to research single command in src/cli/main.py
- [X] T069 [US5] Implement session export logic with timestamp-based filename suggestion in src/cli/main.py
- [X] T070 [US5] Add metadata fields (platform_version, limitations disclaimer) to export in src/models/session.py

**Checkpoint**: User Story 5 complete - sessions can be exported to JSON files

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, edge cases, and refinements

- [X] T071 Add question length validation (max 2000 chars) with truncation warning in src/services/session_runner.py
- [X] T072 Add `ask` shorthand command alias per CLI contract in src/cli/main.py
- [X] T073 Implement fuzzy matching for persona not found suggestions using difflib in src/cli/main.py
- [X] T074 [P] Add verbose flag (--verbose) to show raw response in output in src/cli/main.py
- [X] T075 [P] Update pyproject.toml version to 0.2.0
- [X] T076 Run all tests and verify 100% pass rate
- [X] T077 Validate quickstart.md commands work end-to-end
- [X] T078 Code cleanup and docstring completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P2 → P3 → P3)
  - US2 and US3 can run in parallel after US1 (both P2)
  - US4 and US5 can run in parallel after US2/US3 (both P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories - **MVP SCOPE**
- **US2 (P2)**: Builds on US1 SessionResponse model
- **US3 (P2)**: Builds on US1 SessionRunner, can parallel with US2
- **US4 (P3)**: Extends US1 question types, US2 parsing
- **US5 (P3)**: Extends US1 session model, can parallel with US4

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models before services
3. Services before CLI integration
4. Core implementation before edge cases
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004, T005, T006, T007, T008 can all run in parallel
```

**Phase 2 (Foundational)**:
```
T011, T012 (tests) can run in parallel
T013, T014, T015 (enums) can run in parallel
```

**User Story 1**:
```
T018, T019 (tests) can run in parallel
T020, T021 (models) can run in parallel
```

**User Story 2 & 3 (both P2)** can run in parallel after US1:
```
Team A: US2 (T030-T041)
Team B: US3 (T042-T054)
```

**User Story 4 & 5 (both P3)** can run in parallel after US2/US3:
```
Team A: US4 (T055-T065)
Team B: US5 (T066-T070)
```

---

## Parallel Example: User Story 1

```bash
# Launch tests for User Story 1 together:
Task: "Create tests/contract/test_session_schema.py with ResearchSession JSON export schema validation"
Task: "Create tests/integration/test_session_runner.py with mock subagent execution test"

# Launch models for User Story 1 together:
Task: "Implement ResearchSession Pydantic model in src/models/session.py"
Task: "Implement SessionResponse Pydantic model (basic) in src/models/session.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test `research-cli research single` end-to-end
5. Deploy/demo - researchers can now run basic research sessions

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → Demo (MVP! Basic research sessions work)
3. Add US2 → Test → Demo (Parsed responses)
4. Add US3 → Test → Demo (Quality metrics)
5. Add US4 → Test → Demo (Rating/choice questions)
6. Add US5 → Test → Demo (Export to file)
7. Polish → Final release 0.2.0

### Suggested MVP Scope

**Minimum viable: Complete through Phase 3 (User Story 1)**
- Researchers can execute basic open-ended research sessions
- Raw response captured and displayed
- Basic error handling
- This validates the core subagent architecture

---

## Task Summary

| Phase | Story | Task Count | Parallelizable |
|-------|-------|------------|----------------|
| Phase 1: Setup | - | 10 | 8 |
| Phase 2: Foundational | - | 7 | 5 |
| Phase 3: US1 | P1 | 12 | 4 |
| Phase 4: US2 | P2 | 12 | 2 |
| Phase 5: US3 | P2 | 13 | 2 |
| Phase 6: US4 | P3 | 11 | 2 |
| Phase 7: US5 | P3 | 5 | 1 |
| Phase 8: Polish | - | 8 | 2 |
| **Total** | | **78** | **26** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Exit code 2 indicates warnings (quality issues) per CLI contract
