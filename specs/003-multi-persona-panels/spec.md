# Feature Specification: Multi-Persona Panels

**Feature Branch**: `003-multi-persona-panels`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "Phase 2 Multi-Persona Panels: Execute parallel research with multiple personas, aggregate and analyze responses across panels, and generate research reports"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Panel Research Session (Priority: P1)

A researcher wants to ask a question to an entire panel of synthetic personas simultaneously and receive aggregated results, so that they can gather diverse perspectives on a product concept or feature without running multiple individual sessions.

**Why this priority**: This is the core value proposition of panel research. Without the ability to execute multiple personas in parallel, there's no efficiency gain over running single-persona sessions repeatedly.

**Independent Test**: Can be fully tested by running a single CLI command with a panel name and question, then verifying responses from all panel members are collected and aggregated. Delivers immediate value as a rapid multi-perspective feedback mechanism.

**Acceptance Scenarios**:

1. **Given** a valid pre-built panel name (e.g., "tech-adopters"), **When** the researcher runs `research panel --panel=tech-adopters --question="What do you think of this AI assistant feature?"`, **Then** the system executes research sessions for all personas in that panel and returns aggregated results
2. **Given** a panel with 5 personas, **When** the panel research completes, **Then** the researcher receives individual responses from all 5 personas plus an aggregated summary
3. **Given** a panel research session, **When** completed, **Then** the researcher sees how long the entire panel session took versus estimated sequential time
4. **Given** any panel research session, **When** one persona fails to respond, **Then** the system completes the session with the remaining personas and reports the failure clearly

---

### User Story 2 - View Aggregated Themes and Insights (Priority: P1)

A researcher wants the panel responses automatically analyzed for common themes, consensus points, and divergent opinions, so that they can quickly identify patterns without manually reading and comparing every response.

**Why this priority**: Aggregation is what makes panel research valuable. Raw individual responses without synthesis would require the same manual analysis effort as running separate sessions.

**Independent Test**: Can be tested by running a panel session and verifying the output includes identified themes, sentiment distribution, and consensus/divergence analysis.

**Acceptance Scenarios**:

1. **Given** completed panel responses, **When** aggregation runs, **Then** the system identifies the top 3-5 recurring themes mentioned across responses
2. **Given** panel responses with varying sentiments, **When** aggregated, **Then** the system provides a sentiment distribution showing what percentage were positive, negative, mixed, or neutral
3. **Given** panel responses where personas agree on a concern, **When** aggregated, **Then** this consensus point is highlighted as a strong signal
4. **Given** panel responses where personas have opposing views, **When** aggregated, **Then** the divergence is documented showing which persona types align with which positions

---

### User Story 3 - Use Pre-Built Research Panels (Priority: P2)

A researcher wants access to pre-configured panels designed for specific research purposes, so that they can quickly conduct relevant research without manually selecting personas.

**Why this priority**: Pre-built panels lower the barrier to entry and encode research best practices. However, the core panel execution must work first.

**Independent Test**: Can be tested by listing available panels, selecting one, and verifying it contains the expected persona composition for its stated purpose.

**Acceptance Scenarios**:

1. **Given** the researcher runs `research panel list`, **When** executed, **Then** the system displays available pre-built panels with their names, descriptions, and persona count
2. **Given** the "tech-adopters" panel, **When** used for research, **Then** it includes personas spanning the full technology adoption spectrum (innovators through laggards)
3. **Given** the "skeptics-critics" panel, **When** used for research, **Then** it includes personas with privacy concerns, skeptical attitudes, and critical thinking styles
4. **Given** any pre-built panel, **When** the researcher views its details, **Then** they see the list of included personas and why each was selected for that panel

---

### User Story 4 - Create Custom Panels (Priority: P2)

A researcher wants to create custom panels by selecting specific personas from the library, so that they can target research to their specific product audience or test specific persona combinations.

**Why this priority**: Custom panels enable advanced use cases and researcher autonomy, but pre-built panels serve most initial needs.

**Independent Test**: Can be tested by creating a panel with selected personas, saving it, and running research against it.

**Acceptance Scenarios**:

1. **Given** a list of persona IDs, **When** the researcher runs `research panel create --name="my-panel" --personas="tech-early-adopter,skeptical-late-adopter,busy-professional"`, **Then** a new custom panel is created with those personas
2. **Given** a custom panel name, **When** the researcher uses it for research, **Then** it behaves identically to pre-built panels
3. **Given** an invalid persona ID in the creation list, **When** panel creation is attempted, **Then** the system reports which persona IDs are invalid and suggests corrections
4. **Given** a custom panel, **When** the researcher wants to modify it, **Then** they can add or remove personas from the existing panel

---

### User Story 5 - Generate Research Reports (Priority: P3)

A researcher wants to generate a formatted research report from panel results, so that they can share findings with stakeholders who weren't present during the research session.

**Why this priority**: Reports are valuable for communication but not essential for conducting research. Core functionality must work first.

**Independent Test**: Can be tested by running a panel session and generating a report, then verifying the report contains all essential information in a readable format.

**Acceptance Scenarios**:

1. **Given** completed panel research, **When** the researcher uses `--report report.md`, **Then** a formatted Markdown report is generated
2. **Given** a generated report, **When** opened, **Then** it contains: executive summary, methodology (panel composition, question asked), aggregated findings (themes, sentiment), individual response summaries, and recommendations
3. **Given** panel research with quality metrics, **When** the report is generated, **Then** quality indicators (consistency scores, divergence notes) are included for transparency
4. **Given** multiple panel sessions on the same topic, **When** reports are generated, **Then** each report can be combined or compared for longitudinal analysis

---

### User Story 6 - Export Panel Data (Priority: P3)

A researcher wants to export complete panel session data in a structured format, so that they can perform custom analysis or integrate results with other research tools.

**Why this priority**: Data export enables advanced workflows but is supplementary to core panel functionality.

**Independent Test**: Can be tested by exporting panel data and verifying all individual and aggregated data is present in the export file.

**Acceptance Scenarios**:

1. **Given** completed panel research, **When** the researcher uses `--output data.json`, **Then** the complete session data is exported as JSON
2. **Given** an exported JSON file, **When** inspected, **Then** it contains: panel definition, all individual responses with parsed data, aggregation results, quality metrics, and session metadata
3. **Given** an exported file, **When** imported into a new session, **Then** the researcher can regenerate reports or re-run aggregation analysis

---

### Edge Cases

- What happens when a panel has no available personas (all invalid or missing)?
  - System returns a clear error explaining no valid personas could be loaded and lists the issues encountered
- What happens when all personas in a panel fail to respond?
  - System returns an error indicating complete panel failure with individual failure reasons; no partial aggregation is attempted
- How does the system handle very large panels (>20 personas)?
  - System accepts panels up to 50 personas; execution is batched to manage resource usage; the researcher is warned about longer processing times
- What happens when the researcher requests a non-existent pre-built panel?
  - System returns an error listing available panels and suggests the closest match
- How does the system handle duplicate personas in a custom panel?
  - System warns about duplicates and removes them, keeping only one instance of each persona
- What happens when aggregation cannot identify clear themes (very diverse responses)?
  - System reports high divergence with individual response summaries instead of forcing artificial themes
- How does the system handle panels where personas have conflicting definitions?
  - System proceeds with execution; conflicting perspectives are valuable research data and are highlighted in divergence analysis

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST execute panel research sessions by spawning multiple Claude Code subagents (via Task tool) in parallel for all personas in the panel
- **FR-002**: System MUST aggregate individual responses to identify common themes, sentiment distribution, consensus points, and divergent opinions
- **FR-003**: System MUST provide at least 4 pre-built panels: general-population (10 personas), tech-adopters (5 personas), skeptics-critics (5 personas), and power-users (5 personas)
- **FR-004**: System MUST allow researchers to create custom panels by specifying a list of persona IDs from the persona library
- **FR-005**: System MUST save custom panels for reuse in future research sessions
- **FR-006**: System MUST provide CLI command `research panel --panel=<name> --question="<text>"` for panel research execution
- **FR-007**: System MUST provide CLI command `research panel list` to display available panels with descriptions
- **FR-008**: System MUST provide CLI command `research panel create --name=<name> --personas=<id1,id2,...>` for custom panel creation
- **FR-009**: System MUST handle partial panel failures gracefully, completing research with responding personas and reporting failures
- **FR-010**: System MUST generate structured research reports in Markdown format with executive summary, findings, and individual response summaries
- **FR-011**: System MUST export complete panel session data in JSON format for external analysis
- **FR-012**: System MUST display execution progress during panel research (personas completed, personas remaining)
- **FR-013**: System MUST reuse the SessionRunner, ResponseParser, and QualityMetrics components from Phase 1 for individual persona execution
- **FR-014**: System MUST calculate panel-level quality metrics including overall consistency, theme confidence, and divergence indicators

### Key Entities

- **Research Panel**: A named collection of personas designed for a specific research purpose, containing panel metadata (name, description, purpose) and a list of persona references
- **Panel Session**: A research session involving multiple personas responding to the same question, containing the panel reference, question asked, individual session responses, aggregated results, and panel-level metrics
- **Aggregated Results**: Synthesized findings from multiple responses including identified themes (with frequency counts), sentiment distribution, consensus points (where >60% of personas agree), and divergence analysis (where personas disagree)
- **Research Report**: A formatted document summarizing panel research findings, containing executive summary, methodology description, aggregated findings, individual response highlights, and quality indicators
- **Theme**: A recurring topic or concern identified across multiple responses, with supporting quotes and the personas who mentioned it

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can execute a 5-persona panel research session and receive aggregated results within 60 seconds
- **SC-002**: Panel research with 10 personas completes at least 3x faster than running 10 sequential single-persona sessions
- **SC-003**: 85% of panel research sessions complete successfully with all personas responding
- **SC-004**: Theme identification accurately captures recurring topics (manual review confirms >80% of identified themes are genuinely present in responses)
- **SC-005**: Consensus and divergence analysis correctly identifies agreement/disagreement patterns across personas
- **SC-006**: Generated reports contain all essential sections and can be understood by stakeholders without additional context
- **SC-007**: Exported panel data can be re-imported and regenerated without loss of information
- **SC-008**: Custom panels can be created, saved, and reused across multiple research sessions

## Assumptions

- The Claude Code Task tool supports running multiple subagents in parallel with sufficient throughput for panels up to 10 personas
- Response aggregation and theme identification can be accomplished through structured prompt instructions to Claude, without requiring external NLP libraries
- The 5 base personas from Phase 0 and Phase 1 provide sufficient diversity for the pre-built panels; additional personas may be created as needed during implementation
- Panel execution batching (if needed for large panels) does not significantly impact research quality
- Researchers understand that synthetic panel research provides directional insights but should not replace real user research for critical decisions

## Dependencies

- Phase 0 Foundation: PersonaLoader, PromptBuilder, Persona Library
- Phase 1 Single Persona MVP: SessionRunner, ResponseParser, QualityMetricsCalculator
