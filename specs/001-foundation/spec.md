# Feature Specification: Phase 0 Foundation

**Feature Branch**: `001-foundation`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "Phase 0 Foundation: Establish project structure, define persona schema, create base personas and prompt templates"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define a New Persona (Priority: P1)

A researcher wants to define a synthetic user persona with specific psychological traits, demographics, and behavioral patterns so that the persona can be used in future research sessions.

**Why this priority**: Persona definitions are the fundamental building block of the entire platform. Without well-structured personas, no research can be conducted. This establishes the core data model that all subsequent phases depend on.

**Independent Test**: Can be fully tested by creating a persona YAML file and validating it against the schema. Delivers immediate value as a reusable research asset.

**Acceptance Scenarios**:

1. **Given** a blank persona template, **When** the researcher fills in demographics (age, occupation, location), **Then** the system validates the demographics section is complete
2. **Given** a persona template, **When** the researcher specifies Big Five personality scores (1-10 for each trait), **Then** the system validates all five traits are within valid range
3. **Given** a persona template, **When** the researcher specifies fewer than two Schwartz values, **Then** the system rejects the persona as incomplete
4. **Given** a complete persona definition, **When** the researcher saves the file, **Then** the system confirms the persona is valid and ready for use

---

### User Story 2 - Generate Subagent Prompt from Persona (Priority: P2)

A researcher wants to transform a persona definition into a Claude Code subagent prompt so that the persona can be instantiated for research sessions.

**Why this priority**: Prompt generation is the bridge between static persona definitions and active research. Without this capability, personas remain unused data files.

**Independent Test**: Can be tested by loading a persona and generating a prompt. The output prompt can be reviewed for completeness and persona fidelity.

**Acceptance Scenarios**:

1. **Given** a valid persona YAML file, **When** the prompt template engine processes it, **Then** a complete subagent prompt is generated containing all persona attributes
2. **Given** a persona with specific Big Five traits, **When** the prompt is generated, **Then** the prompt includes behavioral guidance aligned with those traits
3. **Given** a persona definition, **When** the prompt is generated, **Then** the prompt includes anti-sycophancy instructions to encourage realistic responses
4. **Given** a persona with defined values and pain points, **When** the prompt is generated, **Then** these elements appear in the background section of the prompt

---

### User Story 3 - Browse Available Personas (Priority: P3)

A researcher wants to list and view existing personas in the library so that they can select appropriate personas for their research needs.

**Why this priority**: Discoverability of existing personas enables reuse and helps researchers understand what's available before creating new ones.

**Independent Test**: Can be tested by running the list command and verifying all personas in the library are displayed with summary information.

**Acceptance Scenarios**:

1. **Given** multiple personas exist in the library, **When** the researcher requests a list, **Then** all personas are displayed with their names and brief descriptions
2. **Given** a persona ID or name, **When** the researcher requests details, **Then** the full persona definition is displayed
3. **Given** an empty persona library, **When** the researcher requests a list, **Then** a helpful message indicates no personas exist yet

---

### User Story 4 - Initialize Project Structure (Priority: P1)

A developer wants to set up the initial project directory structure and configuration so that the team has a consistent foundation for development.

**Why this priority**: Project scaffolding is a prerequisite for all development work. Without proper structure, team coordination becomes difficult.

**Independent Test**: Can be tested by running the initialization and verifying all expected directories and configuration files are created.

**Acceptance Scenarios**:

1. **Given** a new project directory, **When** the developer runs initialization, **Then** the standard directory structure is created (src/, personas/, templates/, tests/)
2. **Given** initialization completes, **When** the developer inspects the output, **Then** base configuration files are present and properly formatted
3. **Given** the project is initialized, **When** the developer adds a new persona file to the personas/ directory, **Then** the file is recognized by the system

---

### Edge Cases

- What happens when a persona YAML file contains invalid syntax?
  - System provides clear error message indicating the line and nature of the syntax error
- What happens when a persona is missing required fields (e.g., Big Five traits)?
  - System lists all missing required fields and rejects the persona until complete
- How does the system handle persona files with duplicate IDs?
  - System warns about the duplicate and uses the most recently modified file
- What happens when Big Five scores are outside the 1-10 range?
  - System rejects the persona with a clear message about valid ranges
- How does the system handle non-UTF8 characters in persona names or descriptions?
  - System accepts UTF-8 characters to support international names and content

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a YAML schema for defining personas with required fields: id, name, demographics, psychological_profile, background, and response_calibration
- **FR-002**: System MUST validate persona definitions against the schema before accepting them
- **FR-003**: Personas MUST include Big Five personality scores (openness, conscientiousness, extraversion, agreeableness, neuroticism) on a 1-10 integer scale
- **FR-004**: Personas MUST specify at least two Schwartz value priorities from the ten universal values
- **FR-005**: Personas MUST include a technology adoption category (innovator, early_adopter, early_majority, late_majority, laggard)
- **FR-006**: System MUST generate subagent prompts from persona definitions using a template engine
- **FR-007**: Generated prompts MUST include anti-sycophancy instructions to encourage realistic and critical responses
- **FR-008**: System MUST provide five pre-built archetypal personas covering diverse user types
- **FR-009**: System MUST allow listing all available personas with summary information
- **FR-010**: System MUST allow viewing the full definition of any persona
- **FR-011**: System MUST create a standard directory structure with folders for source code, personas, templates, and tests
- **FR-012**: System MUST provide a basic CLI entry point for persona-related commands

### Key Entities

- **Persona**: A synthetic user profile containing demographics (age, gender, location, occupation), psychological profile (Big Five traits, Schwartz values, tech adoption), background narrative (life stage, experiences, pain points, goals), and response calibration settings (verbosity, emotional expressiveness, criticism tendency)
- **Persona Library**: A collection of persona definition files organized in a standard directory structure, supporting versioning and retrieval
- **Prompt Template**: A structured template that transforms persona attributes into a complete subagent prompt with identity, personality, background, and response guidelines sections
- **Anti-Sycophancy Instructions**: Embedded prompt content that directs the subagent to avoid unrealistic positivity and express genuine criticism when warranted

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can create a complete persona definition in under 15 minutes using the provided schema and templates
- **SC-002**: 100% of valid persona definitions successfully generate corresponding subagent prompts without manual intervention
- **SC-003**: All five base personas pass schema validation and include all required psychological framework elements
- **SC-004**: Researchers can list and view persona details within 3 seconds of issuing the command
- **SC-005**: New team members can understand the project structure and locate relevant files within 10 minutes of onboarding
- **SC-006**: Generated prompts include all defined persona attributes with zero data loss during transformation

## Assumptions

- YAML is an appropriate format for persona definitions (human-readable, widely supported)
- Big Five and Schwartz frameworks are sufficient for initial persona modeling (can be extended later)
- Five archetypal personas provide adequate coverage for initial testing and validation
- The CLI will be the primary interface for Phase 0 (web interface deferred to later phases)
- Persona versioning within sessions is immutable (as per constitution) but files can be updated between sessions
