# Tasks: Research Methods

**Input**: Design documents from `/specs/004-research-methods/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included based on the project's existing test-first approach (Phase 0/1/2 established 239 tests).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project Type**: Single project extending existing `src/` structure
- **Models**: `src/models/`
- **Services**: `src/services/`
- **CLI**: `src/cli/`
- **Templates**: `src/templates/`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`
- **Protocols**: `protocols/surveys/`, `protocols/interviews/`, `protocols/focus-groups/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for new research methods

- [X] T001 Create protocol directory structure: `protocols/surveys/`, `protocols/interviews/`, `protocols/focus-groups/`
- [X] T002 [P] Add ResearchMethodType enum to src/models/enums.py (SURVEY, INTERVIEW, FOCUS_GROUP)
- [X] T003 [P] Add SurveyQuestionType enum to src/models/enums.py (RATING, MULTIPLE_CHOICE, OPEN_ENDED)
- [X] T004 [P] Add InterviewProbeType enum to src/models/enums.py (ELABORATION, CLARIFICATION, EXAMPLE, FEELING)
- [X] T005 [P] Add DiscussionInteractionType enum to src/models/enums.py (AGREEMENT, DISAGREEMENT, BUILDING_ON, QUESTION, NEW_POINT)

---

## Phase 2: Foundational - Protocol Management (Blocking Prerequisites)

**Purpose**: Protocol infrastructure that ALL research methods depend on (corresponds to User Story 5)

**⚠️ CRITICAL**: No research method can be executed until protocols can be loaded and validated

### Tests for Protocol Foundation

- [X] T006 [P] Unit test for ResearchProtocol model in tests/unit/test_protocol_model.py
- [X] T007 [P] Unit test for ProtocolLoader service in tests/unit/test_protocol_loader.py
- [X] T008 [P] Contract test for protocol schema validation in tests/contract/test_protocol_schema.py

### Implementation for Protocol Foundation

- [X] T009 [P] Create ResearchProtocol base model in src/models/protocol.py (id, version, type, name, description, created_at, tags)
- [X] T010 [P] Create SurveyProtocol variant in src/models/protocol.py (extends ResearchProtocol)
- [X] T011 [P] Create InterviewProtocol variant in src/models/protocol.py (extends ResearchProtocol)
- [X] T012 [P] Create FocusGroupProtocol variant in src/models/protocol.py (extends ResearchProtocol)
- [X] T013 Implement ProtocolLoader service in src/services/protocol_loader.py (load_by_id, list_protocols, save_protocol, delete_protocol)
- [X] T014 Implement protocol type discrimination and schema validation in src/services/protocol_loader.py
- [X] T015 Implement protocol versioning (copy-on-write) in src/services/protocol_loader.py
- [X] T016 [P] Create protocol CLI commands in src/cli/protocol_commands.py (list, show, delete)
- [X] T017 Register protocol command group in src/cli/main.py
- [X] T018 [P] Create sample-survey.yaml protocol in protocols/surveys/
- [X] T019 [P] Create sample-interview.yaml protocol in protocols/interviews/
- [X] T020 [P] Create sample-focus-group.yaml protocol in protocols/focus-groups/

**Checkpoint**: Protocol infrastructure ready - research method implementation can begin

---

## Phase 3: User Story 1 - Execute Structured Survey Research (Priority: P1) 🎯 MVP

**Goal**: Run structured surveys with rating, multiple choice, and open-ended questions against a single persona

**Independent Test**: Create a survey with 3 question types, execute against tech-early-adopter, verify all responses collected with correct format validation

### Tests for User Story 1

- [X] T021 [P] [US1] Unit test for Survey model in tests/unit/test_survey_model.py
- [X] T022 [P] [US1] Unit test for SurveyQuestion model with type validation in tests/unit/test_survey_model.py
- [X] T023 [P] [US1] Unit test for SurveyResponse model in tests/unit/test_survey_model.py
- [X] T024 [P] [US1] Unit test for SurveyEngine service in tests/unit/test_survey_engine.py
- [ ] T025 [P] [US1] Integration test for survey CLI in tests/integration/test_survey_cli.py

### Implementation for User Story 1

- [X] T026 [P] [US1] Create SurveyQuestion model in src/models/survey.py (id, text, type, scale_min/max, options, required)
- [X] T027 [P] [US1] Create Survey model in src/models/survey.py (id, version, name, questions list with unique IDs)
- [X] T028 [P] [US1] Create SurveyResponse model in src/models/survey.py (question_id, type, raw_response, parsed values)
- [X] T029 [P] [US1] Create SurveyResult model in src/models/survey.py (survey_id, persona_id, responses, timing, quality_metrics)
- [X] T030 [US1] Implement SurveyEngine.execute_survey() in src/services/survey_engine.py (sequential question execution)
- [X] T031 [US1] Implement rating validation with re-prompt strategy in src/services/survey_engine.py
- [X] T032 [US1] Implement multiple choice validation in src/services/survey_engine.py
- [ ] T033 [US1] Extend ResponseParser for survey-specific parsing in src/services/response_parser.py
- [X] T034 [P] [US1] Create survey_prompt.j2 template in src/templates/ (question rendering with type-specific formats)
- [X] T035 [P] [US1] Create survey_report.j2 template in src/templates/ (single persona results)
- [X] T036 [US1] Create survey CLI commands in src/cli/survey_commands.py (run --persona, create)
- [ ] T037 [US1] Extend formatters.py for survey output in src/cli/formatters.py
- [X] T038 [US1] Register survey command group in src/cli/main.py

**Checkpoint**: Single persona survey fully functional - can execute `research survey run -p sample-survey --persona tech-early-adopter`

---

## Phase 4: User Story 2 - Execute Multi-Persona Survey Panels (Priority: P1)

**Goal**: Run surveys across panels with statistical aggregation (mean, median, distribution for ratings; frequency for multiple choice)

**Independent Test**: Execute sample-survey against tech-adopters panel, verify aggregate statistics match manual calculation within 1% variance

### Tests for User Story 2

- [X] T039 [P] [US2] Unit test for RatingStatistics model in tests/unit/test_survey_model.py
- [X] T040 [P] [US2] Unit test for MultipleChoiceStatistics model in tests/unit/test_survey_model.py
- [X] T041 [P] [US2] Unit test for SurveyAggregation model in tests/unit/test_survey_model.py
- [ ] T042 [P] [US2] Unit test for SurveyAggregator service in tests/unit/test_survey_aggregator.py
- [ ] T043 [P] [US2] Integration test for panel survey in tests/integration/test_survey_cli.py

### Implementation for User Story 2

- [X] T044 [P] [US2] Create RatingStatistics model in src/models/survey.py (mean, median, stdev, distribution)
- [X] T045 [P] [US2] Create MultipleChoiceStatistics model in src/models/survey.py (selection_counts, percentages)
- [X] T046 [P] [US2] Create SurveyAggregation model in src/models/survey.py (rating_statistics, mc_statistics, themes)
- [ ] T047 [US2] Implement SurveyAggregator.aggregate_ratings() in src/services/survey_aggregator.py (using statistics module)
- [ ] T048 [US2] Implement SurveyAggregator.aggregate_multiple_choice() in src/services/survey_aggregator.py
- [ ] T049 [US2] Implement SurveyAggregator.aggregate_open_ended() in src/services/survey_aggregator.py (reuse Theme extraction)
- [ ] T050 [US2] Implement SurveyEngine.execute_panel_survey() in src/services/survey_engine.py (reuse PanelExecutor)
- [ ] T051 [US2] Implement segment divergence detection in src/services/survey_aggregator.py
- [ ] T052 [US2] Update survey_report.j2 for panel results with aggregate statistics in src/templates/
- [ ] T053 [US2] Add --panel option to survey run command in src/cli/survey_commands.py
- [ ] T054 [US2] Implement JSON export for survey results in src/cli/survey_commands.py (--output flag)

**Checkpoint**: Panel survey fully functional with aggregation - can execute `research survey run -p sample-survey --panel tech-adopters -r report.md`

---

## Phase 5: User Story 3 - Conduct In-Depth Interviews (Priority: P2)

**Goal**: Execute structured interviews with sections, follow-up questions, and probing based on response length

**Independent Test**: Execute sample-interview guide with tech-early-adopter, verify conversation flows through all sections with at least one follow-up generated

### Tests for User Story 3

- [ ] T055 [P] [US3] Unit test for InterviewQuestion model in tests/unit/test_interview_model.py
- [ ] T056 [P] [US3] Unit test for InterviewSection model in tests/unit/test_interview_model.py
- [ ] T057 [P] [US3] Unit test for InterviewGuide model in tests/unit/test_interview_model.py
- [ ] T058 [P] [US3] Unit test for InterviewTranscript model in tests/unit/test_interview_model.py
- [ ] T059 [P] [US3] Unit test for InterviewEngine service in tests/unit/test_interview_engine.py
- [ ] T060 [P] [US3] Integration test for interview CLI in tests/integration/test_interview_cli.py

### Implementation for User Story 3

- [X] T061 [P] [US3] Create InterviewProbe model in src/models/interview.py (type, trigger, question_template)
- [X] T062 [P] [US3] Create InterviewQuestion model in src/models/interview.py (id, text, probes, allow_followups, max_depth)
- [X] T063 [P] [US3] Create InterviewSection model in src/models/interview.py (id, name, questions, transition_prompt)
- [X] T064 [P] [US3] Create InterviewGuide model in src/models/interview.py (id, version, sections, min_response_length)
- [X] T065 [P] [US3] Create InterviewExchange model in src/models/interview.py (question, response, followups, timestamp)
- [X] T066 [P] [US3] Create SectionTranscript model in src/models/interview.py (section_id, exchanges, timing)
- [X] T067 [P] [US3] Create InterviewTranscript model in src/models/interview.py (guide_id, persona_id, sections, themes)
- [X] T068 [US3] Implement InterviewEngine.conduct_interview() in src/services/interview_engine.py (section-based flow)
- [X] T069 [US3] Implement InterviewEngine._execute_section() in src/services/interview_engine.py
- [X] T070 [US3] Implement InterviewEngine.should_probe() logic in src/services/interview_engine.py (response length check)
- [X] T071 [US3] Implement follow-up question generation in src/services/interview_engine.py (with depth limiting)
- [ ] T072 [US3] Implement followup relevance scoring in src/services/interview_engine.py
- [ ] T073 [US3] Extend ResponseParser for interview-specific parsing in src/services/response_parser.py
- [X] T074 [P] [US3] Create interview_prompt.j2 template in src/templates/ (section context, follow-up rules)
- [X] T075 [P] [US3] Create interview_report.j2 template in src/templates/ (transcript organized by section)
- [X] T076 [US3] Create interview CLI commands in src/cli/interview_commands.py (run, create)
- [ ] T077 [US3] Extend formatters.py for interview output in src/cli/formatters.py
- [X] T078 [US3] Register interview command group in src/cli/main.py

**Checkpoint**: Interview fully functional - can execute `research interview run -g sample-interview -p tech-early-adopter -r transcript.md`

---

## Phase 6: User Story 4 - Run Focus Group Discussions (Priority: P3)

**Goal**: Simulate turn-based discussions where personas respond to topics and reference each other's statements

**Independent Test**: Run pricing-feedback focus group, verify at least 3 interaction types (agreement, disagreement, building-on) occur across turns

### Tests for User Story 4

- [ ] T079 [P] [US4] Unit test for FocusGroup model in tests/unit/test_focus_group_model.py
- [ ] T080 [P] [US4] Unit test for DiscussionTurn model in tests/unit/test_focus_group_model.py
- [ ] T081 [P] [US4] Unit test for DiscussionLog model in tests/unit/test_focus_group_model.py
- [ ] T082 [P] [US4] Unit test for FocusGroupEngine service in tests/unit/test_focus_group_engine.py
- [ ] T083 [P] [US4] Integration test for focus-group CLI in tests/integration/test_focus_group_cli.py

### Implementation for User Story 4

- [X] T084 [P] [US4] Create FocusGroupConfig model in src/models/focus_group.py (max_rounds, turns_per_round, config options)
- [X] T085 [P] [US4] Create FocusGroup model in src/models/focus_group.py (id, version, persona_ids 4-6, topics, config)
- [X] T086 [P] [US4] Create DiscussionReference model in src/models/focus_group.py (referenced_persona_id, turn_index, type)
- [X] T087 [P] [US4] Create DiscussionTurn model in src/models/focus_group.py (turn_index, persona_id, statement, references)
- [X] T088 [P] [US4] Create OpinionShift model in src/models/focus_group.py (persona_id, from_turn, to_turn, positions)
- [X] T089 [P] [US4] Create DiscussionLog model in src/models/focus_group.py (group_id, topic, turns, consensus, shifts)
- [X] T090 [US4] Implement FocusGroupEngine.run_discussion() in src/services/focus_group_engine.py (turn-based simulation)
- [X] T091 [US4] Implement FocusGroupEngine._build_turn_prompt() in src/services/focus_group_engine.py (include context)
- [X] T092 [US4] Implement FocusGroupEngine._extract_references() in src/services/focus_group_engine.py
- [ ] T093 [US4] Implement opinion shift detection in src/services/focus_group_engine.py
- [ ] T094 [US4] Implement consensus/divergence detection in src/services/focus_group_engine.py (reuse aggregation patterns)
- [ ] T095 [US4] Extend ResponseParser for focus group parsing in src/services/response_parser.py
- [X] T096 [P] [US4] Create focus_group_prompt.j2 template in src/templates/ (discussion context, reference instructions)
- [X] T097 [P] [US4] Create focus_group_report.j2 template in src/templates/ (turns, consensus, divergence, shifts)
- [X] T098 [US4] Create focus-group CLI commands in src/cli/focus_group_commands.py (run, create)
- [ ] T099 [US4] Extend formatters.py for focus group output in src/cli/formatters.py
- [X] T100 [US4] Register focus-group command group in src/cli/main.py

**Checkpoint**: Focus group fully functional - can execute `research focus-group run -c sample-focus-group -t "Pricing feedback" -r discussion.md`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T101 [P] Add method-specific quality metrics extensions in src/services/quality_metrics.py
- [ ] T102 [P] Extend report_generator.py with method routing in src/services/report_generator.py
- [ ] T103 [P] Add synthetic data disclaimer to all new method outputs in src/cli/formatters.py
- [ ] T104 Run full test suite and verify all 13 new test files pass
- [ ] T105 Validate quickstart.md scenarios work end-to-end
- [ ] T106 Update CLI version to 0.3.0 in src/cli/main.py

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    └── Phase 2: Foundational (Protocol Management) - BLOCKS ALL
            ├── Phase 3: US1 - Single Survey (P1) 🎯 MVP
            │       └── Phase 4: US2 - Panel Survey (P1)
            ├── Phase 5: US3 - Interview (P2)
            └── Phase 6: US4 - Focus Group (P3)
                    └── Phase 7: Polish
```

### User Story Dependencies

| Story | Priority | Depends On | Can Parallel With |
|-------|----------|------------|-------------------|
| US1 (Single Survey) | P1 | Phase 2 only | US3, US4 |
| US2 (Panel Survey) | P1 | US1 | US3, US4 |
| US3 (Interview) | P2 | Phase 2 only | US1, US4 |
| US4 (Focus Group) | P3 | Phase 2 only | US1, US3 |
| US5 (Protocols) | P2 | Phase 1 only | - (in Phase 2) |
| US6 (Export) | P2 | Integrated into each story | - |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models before services
3. Services before CLI
4. Templates can parallel with services
5. CLI integration last

### Parallel Opportunities

**Phase 1 (all parallel)**:
- T002, T003, T004, T005 (all enum additions)

**Phase 2 (models parallel, then services)**:
- T006, T007, T008 (tests parallel)
- T009, T010, T011, T012 (protocol models parallel)
- T018, T019, T020 (sample protocols parallel)

**Phase 3 (tests first, then implementation)**:
- T021-T025 (all tests parallel)
- T026-T029 (survey models parallel)
- T034, T035 (templates parallel with service)

**Cross-story parallel** (after Phase 2):
- US1, US3, US4 can all start simultaneously if team capacity allows

---

## Parallel Example: Phase 3 (User Story 1)

```bash
# Launch all tests together (should fail initially):
Task: "Unit test for Survey model in tests/unit/test_survey_model.py"
Task: "Unit test for SurveyQuestion model in tests/unit/test_survey_model.py"
Task: "Unit test for SurveyResponse model in tests/unit/test_survey_model.py"
Task: "Unit test for SurveyEngine service in tests/unit/test_survey_engine.py"
Task: "Integration test for survey CLI in tests/integration/test_survey_cli.py"

# Launch all models together:
Task: "Create SurveyQuestion model in src/models/survey.py"
Task: "Create Survey model in src/models/survey.py"
Task: "Create SurveyResponse model in src/models/survey.py"
Task: "Create SurveyResult model in src/models/survey.py"

# Launch templates in parallel with services:
Task: "Create survey_prompt.j2 template in src/templates/"
Task: "Create survey_report.j2 template in src/templates/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T020)
3. Complete Phase 3: User Story 1 (T021-T038)
4. **STOP and VALIDATE**: `research survey run -p sample-survey --persona tech-early-adopter`
5. Deploy/demo single persona survey capability

### Incremental Delivery

| Milestone | Stories Included | CLI Capability |
|-----------|-----------------|----------------|
| MVP | US1 | `research survey run --persona` |
| Survey Complete | US1 + US2 | `research survey run --panel` with aggregation |
| Interview Added | US1 + US2 + US3 | `research interview run` |
| All Methods | US1-US4 | Full research methods suite |

### Parallel Team Strategy

With 3 developers after Phase 2:
- **Developer A**: US1 → US2 (Survey path)
- **Developer B**: US3 (Interview)
- **Developer C**: US4 (Focus Group)

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total Tasks** | 106 |
| Setup | 5 |
| Foundational (US5) | 15 |
| US1 (Single Survey) | 18 |
| US2 (Panel Survey) | 16 |
| US3 (Interview) | 24 |
| US4 (Focus Group) | 22 |
| Polish | 6 |
| **Parallel Opportunities** | 58 tasks marked [P] |
| **Test Tasks** | 21 |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [USx] label maps task to specific user story
- Export (US6) is integrated into each method's CLI implementation
- Protocol management (US5) is in Phase 2 as foundation
- Each checkpoint enables independent validation
- Commit after each task or logical group
- Run `pytest tests/` after each phase completion
