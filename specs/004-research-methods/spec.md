# Feature Specification: Research Methods

**Feature Branch**: `004-research-methods`
**Created**: 2026-01-26
**Status**: Draft
**Input**: User description: "Phase 3: Research Methods - Support different research methodologies including survey, interview, and focus group modes with structured research protocols"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute Structured Survey Research (Priority: P1)

As a researcher, I want to run structured surveys with multiple question types so that I can collect quantifiable feedback from synthetic personas in a standardized format.

**Why this priority**: Surveys are the most common research method and provide quantifiable data. They build directly on the existing single-question capability from Phase 1/2, making them the lowest-risk starting point.

**Independent Test**: Can be fully tested by creating a survey definition with mixed question types and running it against a single persona, then verifying all responses are collected and match expected formats.

**Acceptance Scenarios**:

1. **Given** a researcher has a survey definition with rating, multiple choice, and open-ended questions, **When** they execute the survey against a persona, **Then** the system collects responses for each question in the appropriate format (numeric for ratings, selection for multiple choice, text for open-ended).

2. **Given** a researcher runs a survey with a rating scale (1-10), **When** the persona responds, **Then** the system validates the response is within the defined scale bounds.

3. **Given** a researcher runs a survey with multiple choice options, **When** the persona responds, **Then** the system validates the selection matches one of the provided options.

4. **Given** a survey is executed, **When** all questions have been answered, **Then** the system generates a structured result containing all question-response pairs with metadata (persona ID, timestamp, question type).

---

### User Story 2 - Execute Multi-Persona Survey Panels (Priority: P1)

As a researcher, I want to run the same survey across multiple personas so that I can aggregate quantitative insights and identify patterns across different user segments.

**Why this priority**: Extends Survey capability to leverage existing panel infrastructure, providing statistically meaningful sample sizes essential for survey research validity.

**Independent Test**: Can be tested by running a survey against a pre-defined panel and verifying aggregated statistics (mean, distribution) are calculated correctly.

**Acceptance Scenarios**:

1. **Given** a researcher has a survey and a panel of 5 personas, **When** they execute the panel survey, **Then** the system runs the survey for each persona and aggregates results.

2. **Given** a panel survey completes, **When** viewing results, **Then** the system displays per-persona responses and aggregate statistics (for ratings: mean, median, distribution; for multiple choice: selection frequency).

3. **Given** a panel survey with rating questions, **When** results are generated, **Then** the system identifies any significant divergence between persona segments (e.g., early adopters vs late majority).

---

### User Story 3 - Conduct In-Depth Interviews (Priority: P2)

As a researcher, I want to conduct structured interviews with follow-up questions so that I can explore topics in depth and uncover nuanced insights that surveys cannot capture.

**Why this priority**: Interviews provide rich qualitative data. They require more complex conversation management than surveys but deliver deeper insights for product decisions.

**Independent Test**: Can be tested by executing an interview guide with a single persona and verifying the conversation flows through all sections with contextual follow-ups.

**Acceptance Scenarios**:

1. **Given** a researcher has an interview guide with multiple sections, **When** they start an interview, **Then** the system guides the conversation through each section in order.

2. **Given** an interview is in progress, **When** a persona provides a response, **Then** the system may generate contextual follow-up questions based on the response content before moving to the next planned question.

3. **Given** an interview guide specifies probing questions, **When** a persona's response is brief or unclear, **Then** the system uses appropriate probes to encourage elaboration.

4. **Given** an interview completes, **When** viewing results, **Then** the system provides a full transcript organized by section with timestamps and identified themes.

---

### User Story 4 - Run Focus Group Discussions (Priority: P3)

As a researcher, I want to facilitate focus group discussions where multiple personas interact with each other so that I can observe group dynamics and how opinions evolve through discussion.

**Why this priority**: Focus groups are the most complex method, requiring multi-persona interaction simulation. While valuable for certain research questions, they depend on mature single-persona capabilities.

**Independent Test**: Can be tested by initiating a focus group on a topic and verifying multiple personas contribute responses that reference or build upon each other's statements.

**Acceptance Scenarios**:

1. **Given** a researcher defines a focus group with 4-6 personas and discussion topics, **When** they run the focus group, **Then** the system simulates a moderated discussion where personas respond to topics and to each other.

2. **Given** a focus group discussion is in progress, **When** one persona expresses an opinion, **Then** other personas may agree, disagree, or build upon that opinion based on their defined traits.

3. **Given** a focus group completes, **When** viewing results, **Then** the system provides a discussion transcript showing the flow of conversation, points of agreement, and points of contention.

4. **Given** a focus group discussion, **When** analyzing results, **Then** the system identifies opinion shifts (personas who changed their stance during discussion) and consensus points.

---

### User Story 5 - Create and Manage Research Protocols (Priority: P2)

As a researcher, I want to define reusable research protocols so that I can standardize my research approaches and easily repeat studies with different panels.

**Why this priority**: Protocols enable research reproducibility and efficiency. Supporting protocol templates early allows all three methods to benefit from standardized definitions.

**Independent Test**: Can be tested by creating a protocol definition, saving it, and successfully loading and executing it in a new session.

**Acceptance Scenarios**:

1. **Given** a researcher defines a survey protocol, **When** they save it, **Then** the protocol is stored and can be retrieved by name or ID.

2. **Given** a saved interview protocol exists, **When** a researcher loads it, **Then** they can execute it without re-defining all questions and sections.

3. **Given** multiple protocols exist, **When** a researcher lists protocols, **Then** they see all available protocols organized by type (survey, interview, focus-group).

4. **Given** a protocol is in use, **When** a researcher wants to modify it, **Then** they can create a versioned copy without affecting the original.

---

### User Story 6 - Export Research Results (Priority: P2)

As a researcher, I want to export research results in multiple formats so that I can analyze them in external tools or share with stakeholders.

**Why this priority**: Data portability is essential for integrating synthetic research into existing workflows and enabling advanced analysis.

**Independent Test**: Can be tested by running any research method and exporting results, then verifying the export contains all expected data in valid format.

**Acceptance Scenarios**:

1. **Given** a completed survey, **When** the researcher exports results, **Then** the system produces structured output containing all questions, responses, and aggregate statistics.

2. **Given** a completed interview, **When** the researcher exports results, **Then** the system produces a transcript with metadata and identified themes.

3. **Given** a completed focus group, **When** the researcher exports results, **Then** the system produces a discussion log with participant attributions and interaction analysis.

---

### Edge Cases

- What happens when a persona provides an out-of-range rating value? System should re-prompt or use the closest valid value with a warning.
- How does the system handle a persona that refuses to answer a question? System should record "declined to answer" and continue with remaining questions.
- What happens if a focus group persona becomes unresponsive mid-discussion? System should continue with remaining participants and note the dropout.
- How does the system handle survey questions with no valid response mapping? System should fallback to open-ended capture with a type mismatch warning.
- What happens when an interview follow-up chain exceeds reasonable depth? System should cap follow-up depth (default: 3 levels) and move to next planned question.
- How does the system handle conflicting persona traits in focus group dynamics? System should prioritize primary traits (psychological profile) over secondary characteristics.

## Requirements *(mandatory)*

### Functional Requirements

#### Survey Engine

- **FR-001**: System MUST support three question types: rating (numeric scale), multiple choice (single selection), and open-ended (free text).
- **FR-002**: System MUST validate rating responses fall within the defined scale bounds (e.g., 1-10, 1-5).
- **FR-003**: System MUST validate multiple choice responses match one of the provided options.
- **FR-004**: System MUST execute surveys against single personas using the existing SessionRunner infrastructure.
- **FR-005**: System MUST execute surveys against panels using the existing PanelExecutor infrastructure.
- **FR-006**: System MUST calculate aggregate statistics for rating questions (mean, median, standard deviation, distribution).
- **FR-007**: System MUST calculate selection frequencies for multiple choice questions.
- **FR-008**: System MUST preserve question order during survey execution.

#### Interview Engine

- **FR-009**: System MUST support interview guides organized into named sections with ordered questions.
- **FR-010**: System MUST execute interview questions in section order, completing all questions in a section before advancing.
- **FR-011**: System MUST support optional probing questions that activate when responses are brief (under a configurable threshold).
- **FR-012**: System MUST generate contextual follow-up questions based on response content when interview guide permits.
- **FR-013**: System MUST limit follow-up question depth to a configurable maximum (default: 3).
- **FR-014**: System MUST produce interview transcripts organized by section with timestamps.

#### Focus Group Engine

- **FR-015**: System MUST support focus group definitions specifying 4-6 participating personas.
- **FR-016**: System MUST simulate turn-taking discussion where personas respond to topics and to each other's statements.
- **FR-017**: System MUST ensure each persona maintains trait consistency throughout the discussion.
- **FR-018**: System MUST detect and record agreement/disagreement patterns between personas.
- **FR-019**: System MUST track opinion evolution when personas modify their stance during discussion.
- **FR-020**: System MUST support moderator prompts to guide discussion toward specific topics.

#### Protocol Management

- **FR-021**: System MUST support YAML-based protocol definitions for all three research methods.
- **FR-022**: System MUST validate protocol definitions against method-specific schemas.
- **FR-023**: System MUST persist protocols in the protocols directory with unique identifiers.
- **FR-024**: System MUST support listing all available protocols filtered by method type.
- **FR-025**: System MUST support protocol versioning to preserve original definitions when modifications are made.

#### CLI Commands

- **FR-026**: System MUST provide `research survey run` command to execute survey protocols.
- **FR-027**: System MUST provide `research survey create` command to define new surveys interactively or from YAML.
- **FR-028**: System MUST provide `research interview run` command to execute interview protocols.
- **FR-029**: System MUST provide `research interview create` command to define new interview guides.
- **FR-030**: System MUST provide `research focus-group run` command to execute focus group sessions.
- **FR-031**: System MUST provide `research focus-group create` command to define new focus group configurations.
- **FR-032**: System MUST provide `research protocol list/show/delete` commands for protocol management.

#### Output & Export

- **FR-033**: System MUST support JSON export format for all research methods.
- **FR-034**: System MUST support Markdown report generation for all research methods.
- **FR-035**: System MUST include research method metadata in all exports (method type, protocol version, execution timestamp).

### Key Entities

- **Survey**: A structured questionnaire containing ordered questions with defined types (rating, multiple_choice, open_ended), scales, and options. Produces quantifiable responses suitable for statistical analysis.

- **InterviewGuide**: A research instrument organizing questions into thematic sections with optional probing questions and follow-up rules. Guides in-depth qualitative exploration.

- **FocusGroup**: A research configuration defining participating personas, discussion topics, and moderation rules. Simulates group interaction dynamics.

- **ResearchProtocol**: A reusable, versioned definition of any research method (survey, interview, or focus group) that can be stored, retrieved, and executed repeatedly.

- **SurveyResponse**: Captures a persona's answer to a single survey question, including the raw response, validated value, and response metadata.

- **InterviewTranscript**: A chronological record of an interview session containing all questions asked, responses given, and follow-up exchanges organized by section.

- **DiscussionLog**: A record of focus group interaction capturing each statement, the speaking persona, responses from other personas, and detected agreement/disagreement patterns.

## Assumptions

- Existing Phase 1/2 infrastructure (PersonaLoader, SessionRunner, PanelExecutor, ResponseParser, ResponseAggregator) will be reused and extended rather than replaced.
- Research protocols will be stored as YAML files in a `protocols/` directory structure, consistent with existing persona and panel storage patterns.
- Focus group simulations will use a turn-based approach rather than true real-time parallel interaction, as this simplifies implementation while still capturing group dynamics.
- Interview follow-up questions will be generated using the same LLM infrastructure as persona responses, maintaining consistency with the subagent approach.
- Default response length thresholds for probe activation will be 50 characters, adjustable via protocol configuration.
- Focus group size is limited to 4-6 personas to maintain readable discussion transcripts and manageable computational requirements.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can define and execute a 10-question survey across a 5-persona panel in under 5 minutes.
- **SC-002**: Survey aggregate statistics (mean, distribution) are calculated accurately with less than 1% variance from manual calculation.
- **SC-003**: Interview sessions produce coherent transcripts where follow-up questions demonstrably relate to the preceding response at least 80% of the time.
- **SC-004**: Focus group discussions produce at least 3 distinct interaction patterns (agreement, disagreement, building-on) per 10-turn session.
- **SC-005**: 90% of saved research protocols can be successfully loaded and executed without modification.
- **SC-006**: All three research methods (survey, interview, focus-group) produce valid exports that can be parsed by standard tools.
- **SC-007**: Persona trait consistency scores remain above 70% threshold across all research methods (consistent with Phase 1/2 quality standards).
- **SC-008**: Researchers report the new methods address at least 80% of common research scenarios in user feedback.
