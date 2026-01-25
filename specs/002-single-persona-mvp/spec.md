# Feature Specification: Single Persona MVP

**Feature Branch**: `002-single-persona-mvp`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "Phase 1 Single Persona MVP: Execute single persona research sessions using Claude Code subagents, validate the subagent approach with the Task tool, and establish response quality baseline"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Single Persona Research Session (Priority: P1)

A researcher wants to ask a question to a specific synthetic persona and receive a response that reflects that persona's unique psychological profile, demographics, and values, so that they can gather preliminary user feedback on a product concept or feature idea.

**Why this priority**: This is the core value proposition of the entire platform. Without the ability to execute a single persona research session, no research can be conducted. This validates the fundamental subagent approach and proves the architecture works.

**Independent Test**: Can be fully tested by running a single CLI command with a persona ID and question, then verifying the response demonstrates persona characteristics. Delivers immediate value as a rapid feedback mechanism.

**Acceptance Scenarios**:

1. **Given** a valid persona ID from the library, **When** the researcher runs `research --persona=tech-early-adopter --question="What do you think of this daily reflection feature?"`, **Then** the system returns a response that reflects the persona's psychological traits and background
2. **Given** a persona with high openness and early adopter status, **When** asked about a new AI feature, **Then** the response demonstrates curiosity and willingness to try new things consistent with those traits
3. **Given** a persona with high neuroticism and skeptical values, **When** asked about data-sharing features, **Then** the response expresses concerns and hesitation aligned with that psychological profile
4. **Given** a valid persona and question, **When** the session completes, **Then** the researcher receives both the raw response and metadata about the session (persona used, timestamp, question asked)

---

### User Story 2 - Parse Structured Response Data (Priority: P2)

A researcher wants the persona's response to be parsed into structured sections (sentiment, key concerns, suggestions, overall rating) so that they can quickly analyze and compare responses across different research sessions.

**Why this priority**: Structured data extraction transforms raw text into actionable insights. Without parsing, researchers must manually analyze each response, limiting scalability.

**Independent Test**: Can be tested by running a research session and verifying the output contains structured sections with appropriate content extracted from the raw response.

**Acceptance Scenarios**:

1. **Given** a completed research session, **When** the response is processed, **Then** the system extracts sentiment (positive, negative, mixed, neutral) from the response
2. **Given** a persona response that mentions concerns, **When** parsed, **Then** the key concerns are identified and listed separately
3. **Given** a persona response with suggestions, **When** parsed, **Then** the suggestions are extracted into a discrete list
4. **Given** a response, **When** the researcher requests structured output format, **Then** the system returns JSON with fields: sentiment, concerns, suggestions, key_quotes, overall_impression

---

### User Story 3 - Validate Response Quality (Priority: P2)

A researcher wants to verify that the persona's response is consistent with the defined persona traits so that they can trust the research results are valid representations of that user type.

**Why this priority**: Quality validation is essential for research credibility. If responses don't align with persona definitions, the research value is compromised.

**Independent Test**: Can be tested by comparing response characteristics against persona trait definitions and calculating a consistency score.

**Acceptance Scenarios**:

1. **Given** a completed session with a high-openness persona, **When** the response is validated, **Then** the system confirms the response demonstrates openness characteristics (curiosity, new ideas)
2. **Given** a response from a skeptical persona, **When** validated, **Then** the system verifies critical or cautious language is present
3. **Given** any completed session, **When** quality validation runs, **Then** a consistency score (0-100%) is calculated comparing response traits to persona definition
4. **Given** a response that deviates significantly from persona traits, **When** validated, **Then** the system flags the response with a warning about potential character drift

---

### User Story 4 - Handle Multiple Question Formats (Priority: P3)

A researcher wants to ask questions in various formats (open-ended, rating scale, multiple choice) so that they can conduct different types of research inquiries with the same persona.

**Why this priority**: Flexibility in question types expands research capabilities, but the core open-ended question flow must work first.

**Independent Test**: Can be tested by submitting different question types and verifying appropriate response formats for each.

**Acceptance Scenarios**:

1. **Given** an open-ended question like "What do you think of this feature?", **When** submitted, **Then** the persona provides a narrative response with opinions and reasoning
2. **Given** a rating question like "Rate this feature 1-10", **When** submitted, **Then** the persona provides a numeric rating with justification
3. **Given** a multiple choice question with options A, B, C, **When** submitted, **Then** the persona selects an option and explains their choice based on their values and preferences

---

### User Story 5 - Export Session Transcript (Priority: P3)

A researcher wants to save the complete session transcript to a file so that they can archive research sessions for later review, sharing, or compliance purposes.

**Why this priority**: Persistence is important for research traceability but not essential for the MVP core functionality.

**Independent Test**: Can be tested by running a session with an export flag and verifying a file is created with complete session data.

**Acceptance Scenarios**:

1. **Given** a completed research session, **When** the researcher uses `--output transcript.json`, **Then** the full session is saved to the specified file
2. **Given** an exported transcript, **When** opened, **Then** it contains: persona ID, persona name, question asked, raw response, parsed data, quality metrics, and timestamp
3. **Given** multiple sessions, **When** exported to the same directory, **Then** each file has a unique name based on persona and timestamp

---

### Edge Cases

- What happens when the specified persona ID does not exist in the library?
  - System returns a clear error message listing available personas and suggesting the closest match
- What happens when the question is empty or contains only whitespace?
  - System rejects the request with an error indicating a question is required
- How does the system handle extremely long questions (>2000 characters)?
  - System accepts questions up to 2000 characters; longer questions are truncated with a warning
- What happens when the subagent fails to respond within the timeout period?
  - System returns an error with timeout details and suggests retrying; partial responses are discarded
- How does the system handle special characters or unicode in questions?
  - System accepts UTF-8 encoded questions including international characters and emoji
- What happens when the persona response is unexpectedly short or empty?
  - System flags the response as potentially incomplete and includes a warning in the output
- How does the system handle questions that might elicit harmful or inappropriate content?
  - System relies on Claude's built-in safety measures; responses are passed through as-is with standard safeguards

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST execute research sessions by spawning a Claude Code subagent via the Task tool with the persona's generated prompt
- **FR-002**: System MUST load the specified persona from the persona library using the PersonaLoader from Phase 0
- **FR-003**: System MUST generate a complete subagent prompt using the PromptBuilder from Phase 0
- **FR-004**: System MUST pass the researcher's question to the subagent and capture the complete response
- **FR-005**: System MUST parse the raw response into structured fields: sentiment, concerns, suggestions, key_quotes, overall_impression
- **FR-006**: System MUST calculate a consistency score comparing response characteristics to persona trait definitions
- **FR-007**: System MUST flag responses where consistency score falls below 70% as potentially inconsistent
- **FR-008**: System MUST support open-ended question format for initial research inquiries
- **FR-009**: System MUST support rating scale questions (1-10) with justification
- **FR-010**: System MUST support multiple choice questions with option selection and explanation
- **FR-011**: System MUST provide CLI command `research --persona=<id> --question="<text>"` for single-session execution
- **FR-012**: System MUST provide `--output <filepath>` flag to export session transcripts
- **FR-013**: System MUST include anti-sycophancy effectiveness in quality metrics, measuring presence of critical or nuanced feedback
- **FR-014**: System MUST display session results in human-readable format by default, with `--format json` option for structured output
- **FR-015**: System MUST include session metadata (timestamp, persona ID, question, response time) in all outputs

### Key Entities

- **Research Session**: A single interaction between a researcher and a synthetic persona, containing the persona reference, question asked, raw response, parsed response, quality metrics, and session metadata (timestamp, duration)
- **Session Response**: The output from a persona subagent, including raw text and structured data (sentiment, concerns, suggestions, key quotes)
- **Quality Metrics**: Measurements of response validity including consistency score (0-100%), sycophancy indicators (boolean flags for excessive positivity), and character alignment assessment
- **Research Question**: The input query from the researcher, with metadata about question type (open-ended, rating, multiple-choice) and any constraints

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can execute a complete single-persona research session and receive a response within 30 seconds
- **SC-002**: 90% of research sessions complete successfully without errors or timeouts
- **SC-003**: Responses from the same persona to similar questions demonstrate consistent personality traits (>85% trait alignment when tested across 10 sessions)
- **SC-004**: Different personas produce meaningfully different responses to the same question (measurable variance in sentiment and concerns)
- **SC-005**: Anti-sycophancy measures result in at least 40% of responses containing critical feedback, concerns, or suggestions for improvement
- **SC-006**: Researchers can understand the complete session output (persona, question, response, metrics) within 30 seconds of completion
- **SC-007**: Parsed response data accurately reflects the content of raw responses (manual review confirms >90% accuracy on key extraction)
- **SC-008**: Session transcripts can be exported and re-imported without data loss

## Assumptions

- Claude Code Task tool provides reliable subagent execution with consistent response quality
- The PromptBuilder from Phase 0 generates prompts that effectively convey persona characteristics to the subagent
- Response parsing can be accomplished through structured prompt instructions requesting specific output format, without requiring external NLP tools
- 30-second timeout is sufficient for single-session responses; complex questions may occasionally require longer
- Consistency scoring can be implemented through keyword and pattern matching against persona trait definitions
- The five base personas from Phase 0 provide sufficient diversity to validate the approach before expanding the library
