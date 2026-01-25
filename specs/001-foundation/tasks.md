# Tasks: Phase 0 Foundation

**Input**: Design documents from `/specs/001-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution requirement (Test-First for Quality)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Python project initialization and dependency management

- [X] T001 Create project directory structure per plan.md layout
- [X] T002 Create pyproject.toml with Python 3.11+ and dependencies (PyYAML, Pydantic, Click, Jinja2, pytest)
- [X] T003 [P] Create src/__init__.py with package metadata
- [X] T004 [P] Create src/models/__init__.py
- [X] T005 [P] Create src/services/__init__.py
- [X] T006 [P] Create src/cli/__init__.py
- [X] T007 [P] Create src/templates/__init__.py
- [X] T008 [P] Create tests/__init__.py and tests/conftest.py with pytest fixtures
- [X] T009 [P] Create tests/unit/__init__.py
- [X] T010 [P] Create tests/integration/__init__.py
- [X] T011 [P] Create tests/contract/__init__.py

**Checkpoint**: Python project structure ready for implementation

---

## Phase 2: Foundational (Shared Components)

**Purpose**: Core enums and base types that ALL user stories depend on

**CRITICAL**: Must complete before any user story implementation

- [X] T012 [P] Create TechAdoptionCategory enum in src/models/enums.py (innovator, early_adopter, early_majority, late_majority, laggard)
- [X] T013 [P] Create SchwartzValue enum in src/models/enums.py (10 universal values)
- [X] T014 [P] Create VerbosityLevel enum in src/models/enums.py (concise, moderate, detailed)
- [X] T015 [P] Create ExpressivenessLevel enum in src/models/enums.py (reserved, moderate, expressive)
- [X] T016 [P] Create CriticismLevel enum in src/models/enums.py (positive, balanced, critical)
- [X] T017 [P] Create CertaintyLevel enum in src/models/enums.py (certain, questioning, uncertain)
- [X] T018 Create anti-sycophancy instructions template in templates/prompts/anti-sycophancy.md

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Define a New Persona (Priority: P1)

**Goal**: Researchers can create and validate persona definitions with psychological frameworks

**Independent Test**: Create a persona YAML file and validate it against the schema

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [P] [US1] Contract test for persona schema validation in tests/contract/test_persona_schema.py
- [X] T020 [P] [US1] Unit test for BigFive model validation in tests/unit/test_persona_model.py
- [X] T021 [P] [US1] Unit test for Demographics model validation in tests/unit/test_persona_model.py
- [X] T022 [P] [US1] Unit test for SchwartzValues model validation in tests/unit/test_persona_model.py
- [X] T023 [P] [US1] Unit test for PersonaLoader service in tests/unit/test_persona_loader.py

### Implementation for User Story 1

- [X] T024 [P] [US1] Create Occupation Pydantic model in src/models/persona.py
- [X] T025 [P] [US1] Create Demographics Pydantic model in src/models/persona.py
- [X] T026 [P] [US1] Create BigFive Pydantic model with 1-10 range validation in src/models/persona.py
- [X] T027 [P] [US1] Create SchwartzValues Pydantic model with min 2 primary values in src/models/persona.py
- [X] T028 [P] [US1] Create PsychologicalProfile Pydantic model in src/models/persona.py
- [X] T029 [P] [US1] Create Background Pydantic model in src/models/persona.py
- [X] T030 [P] [US1] Create ResponseCalibration Pydantic model in src/models/persona.py
- [X] T031 [P] [US1] Create Metadata Pydantic model in src/models/persona.py
- [X] T032 [US1] Create root Persona Pydantic model with all nested models in src/models/persona.py
- [X] T033 [US1] Implement PersonaLoader.load() to parse YAML files in src/services/persona_loader.py
- [X] T034 [US1] Implement PersonaLoader.validate() to validate against schema in src/services/persona_loader.py
- [X] T035 [US1] Implement error messages with line numbers for invalid YAML in src/services/persona_loader.py
- [X] T036 [US1] Create blank persona template in personas/templates/persona-template.yaml
- [X] T037 [US1] Implement CLI `persona validate` command in src/cli/main.py

**Checkpoint**: User Story 1 complete - personas can be created and validated

---

## Phase 4: User Story 4 - Initialize Project Structure (Priority: P1)

**Goal**: Developers can initialize the project with standard structure and base personas

**Independent Test**: Run init command and verify directories and base personas are created

### Tests for User Story 4

- [X] T038 [P] [US4] Integration test for `init` command in tests/integration/test_cli.py
- [X] T039 [P] [US4] Unit test for directory creation logic in tests/unit/test_init.py

### Implementation for User Story 4

- [X] T040 [P] [US4] Create tech-early-adopter.yaml base persona in personas/definitions/tech-early-adopter.yaml
- [X] T041 [P] [US4] Create skeptical-late-adopter.yaml base persona in personas/definitions/skeptical-late-adopter.yaml
- [X] T042 [P] [US4] Create busy-professional.yaml base persona in personas/definitions/busy-professional.yaml
- [X] T043 [P] [US4] Create privacy-conscious-user.yaml base persona in personas/definitions/privacy-conscious-user.yaml
- [X] T044 [P] [US4] Create power-user.yaml base persona in personas/definitions/power-user.yaml
- [X] T045 [US4] Implement CLI `init` command with directory creation in src/cli/main.py
- [X] T046 [US4] Implement --force flag for init command to overwrite existing files in src/cli/main.py

**Checkpoint**: User Story 4 complete - project initialization works

---

## Phase 5: User Story 2 - Generate Subagent Prompt (Priority: P2)

**Goal**: Transform persona definitions into Claude Code subagent prompts

**Independent Test**: Load a persona and generate a prompt; verify all attributes are included

### Tests for User Story 2

- [X] T047 [P] [US2] Unit test for PromptBuilder service in tests/unit/test_prompt_builder.py
- [X] T048 [P] [US2] Integration test for prompt generation CLI in tests/integration/test_cli.py

### Implementation for User Story 2

- [X] T049 [US2] Create Jinja2 subagent prompt template in src/templates/subagent_prompt.j2
- [X] T050 [US2] Implement identity section in template (name, demographics) in src/templates/subagent_prompt.j2
- [X] T051 [US2] Implement personality section with Big Five behavioral guidance in src/templates/subagent_prompt.j2
- [X] T052 [US2] Implement values section with Schwartz values and conflicts in src/templates/subagent_prompt.j2
- [X] T053 [US2] Implement background section (life stage, experiences, pain points, goals) in src/templates/subagent_prompt.j2
- [X] T054 [US2] Implement response guidelines section (calibration settings) in src/templates/subagent_prompt.j2
- [X] T055 [US2] Include anti-sycophancy instructions from templates/prompts/anti-sycophancy.md
- [X] T056 [US2] Implement PromptBuilder.build() service in src/services/prompt_builder.py
- [X] T057 [US2] Implement CLI `persona prompt` command in src/cli/main.py
- [X] T058 [US2] Add --output flag to save prompt to file in src/cli/main.py
- [X] T059 [US2] Add --template flag for custom templates in src/cli/main.py

**Checkpoint**: User Story 2 complete - prompts can be generated from personas

---

## Phase 6: User Story 3 - Browse Available Personas (Priority: P3)

**Goal**: Researchers can list and view existing personas in the library

**Independent Test**: Run list command and verify all personas are displayed with summaries

### Tests for User Story 3

- [X] T060 [P] [US3] Unit test for PersonaLibrary service in tests/unit/test_persona_library.py
- [X] T061 [P] [US3] Integration test for persona list/show CLI in tests/integration/test_cli.py

### Implementation for User Story 3

- [X] T062 [US3] Implement PersonaLibrary.list_all() to scan persona directory in src/services/persona_library.py
- [X] T063 [US3] Implement PersonaLibrary.get_by_id() to retrieve single persona in src/services/persona_library.py
- [X] T064 [US3] Implement PersonaLibrary.search() for filtering personas in src/services/persona_library.py
- [X] T065 [US3] Handle empty library case with helpful message in src/services/persona_library.py
- [X] T066 [US3] Handle duplicate ID warning in src/services/persona_library.py
- [X] T067 [US3] Implement CLI `persona list` command with table output in src/cli/main.py
- [X] T068 [US3] Add --format flag (table, json, yaml) to list command in src/cli/main.py
- [X] T069 [US3] Implement CLI `persona show` command in src/cli/main.py
- [X] T070 [US3] Add --section flag to show command for filtered output in src/cli/main.py

**Checkpoint**: User Story 3 complete - personas can be browsed and viewed

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [X] T071 [P] Add --verbose and --quiet global options to CLI in src/cli/main.py
- [X] T072 [P] Add --version option to CLI in src/cli/main.py
- [X] T073 [P] Implement consistent error message format across all commands in src/cli/main.py
- [X] T074 [P] Add JSON output support for machine-readable results in src/cli/main.py
- [X] T075 Run all tests and ensure 100% pass rate
- [X] T076 Validate all 5 base personas against schema
- [X] T077 Test quickstart.md scenarios end-to-end
- [X] T078 Code cleanup and docstring additions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Can start after foundational
- **Phase 4 (US4)**: Depends on Phase 2 AND Phase 3 (needs schema validation) - Can run parallel with US2/US3
- **Phase 5 (US2)**: Depends on Phase 2 AND Phase 3 (needs Persona model) - Can run parallel with US4/US3
- **Phase 6 (US3)**: Depends on Phase 2 AND Phase 3 (needs PersonaLoader) - Can run parallel with US4/US2
- **Phase 7 (Polish)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundational
    │
    ▼
Phase 3: US1 (Define Persona) ──────┬───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
Phase 4: US4 (Init)          Phase 5: US2 (Prompt)          Phase 6: US3 (Browse)
    │                               │                               │
    └───────────────────────────────┴───────────────────────────────┘
                                    │
                                    ▼
                            Phase 7: Polish
```

### Within Each User Story

1. Tests MUST be written first and FAIL
2. Models before services
3. Services before CLI commands
4. Core implementation before additional flags

### Parallel Opportunities

**Phase 1 (T003-T011)**: All `__init__.py` files can be created in parallel

**Phase 2 (T012-T017)**: All enums can be created in parallel

**Phase 3 US1 Tests (T019-T023)**: All tests can be written in parallel
**Phase 3 US1 Models (T024-T031)**: All nested Pydantic models can be created in parallel

**Phase 4 US4 Personas (T040-T044)**: All 5 base personas can be created in parallel

**Phase 5, 6 US2/US3**: Can run entirely in parallel with US4 after US1 complete

---

## Parallel Example: User Story 1 Models

```bash
# Launch all nested models for US1 together:
Task: "Create Occupation Pydantic model in src/models/persona.py"
Task: "Create Demographics Pydantic model in src/models/persona.py"
Task: "Create BigFive Pydantic model in src/models/persona.py"
Task: "Create SchwartzValues Pydantic model in src/models/persona.py"
Task: "Create PsychologicalProfile Pydantic model in src/models/persona.py"
Task: "Create Background Pydantic model in src/models/persona.py"
Task: "Create ResponseCalibration Pydantic model in src/models/persona.py"
Task: "Create Metadata Pydantic model in src/models/persona.py"

# Then after all models exist, create root Persona model:
Task: "Create root Persona Pydantic model with all nested models in src/models/persona.py"
```

## Parallel Example: Base Personas

```bash
# Launch all 5 base personas together:
Task: "Create tech-early-adopter.yaml in personas/definitions/"
Task: "Create skeptical-late-adopter.yaml in personas/definitions/"
Task: "Create busy-professional.yaml in personas/definitions/"
Task: "Create privacy-conscious-user.yaml in personas/definitions/"
Task: "Create power-user.yaml in personas/definitions/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational enums
3. Complete Phase 3: User Story 1 (Define Persona)
4. **STOP and VALIDATE**: Test persona validation independently
5. Personas can be created and validated - MVP achieved

### Incremental Delivery

1. Setup + Foundational → Project structure ready
2. Add US1 (Define Persona) → Personas can be validated (MVP!)
3. Add US4 (Init) → Project can be initialized with base personas
4. Add US2 (Prompt) → Prompts can be generated
5. Add US3 (Browse) → Personas can be discovered
6. Polish → Production-ready CLI

### Single Developer Strategy

Follow priority order: US1 → US4 → US2 → US3

### Parallel Team Strategy

After Phase 3 (US1) completes:
- Developer A: US4 (Init with base personas)
- Developer B: US2 (Prompt generation)
- Developer C: US3 (Browse/list)

---

## Notes

- [P] tasks = different files or no dependencies
- [Story] label maps task to specific user story
- US1 must complete before US2, US3, US4 can start (they need the Persona model)
- All 5 base personas follow the same schema and can be created in parallel
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
