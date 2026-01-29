# Feature Specification: Quality & Calibration

**Feature Branch**: `005-quality-calibration`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Phase 4: Quality & Calibration - Implement quality metrics and monitoring, build calibration pipeline against real data, and add consistency validation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assess Persona Response Consistency (Priority: P1)

As a researcher, I want to measure how well synthetic persona responses align with their defined personality traits so that I can trust the validity of my research findings and identify when personas are not behaving authentically.

**Why this priority**: Consistency is the foundation of synthetic research validity. Without reliable trait alignment, all research outputs become questionable. This must be validated before any other quality metrics.

**Independent Test**: Can be fully tested by running a research session with a known persona, calculating consistency scores against trait definitions, and verifying scores reflect actual alignment.

**Acceptance Scenarios**:

1. **Given** a completed research session with a persona, **When** I request consistency analysis, **Then** the system calculates a consistency score (0-100%) showing how well responses align with the persona's Big Five traits and Schwartz values.

2. **Given** a persona with high conscientiousness, **When** they respond to questions about work habits, **Then** their responses should demonstrate organized, thorough, and detail-oriented language patterns that match the trait.

3. **Given** a consistency score below the configured threshold (default: 70%), **When** viewing results, **Then** the system flags the session with a quality warning indicating which traits showed misalignment.

4. **Given** multiple research sessions with the same persona, **When** comparing consistency scores across sessions, **Then** scores should remain within 15% variance to indicate stable persona behavior.

---

### User Story 2 - Detect Sycophancy and Positivity Bias (Priority: P1)

As a researcher, I want to identify when synthetic personas are exhibiting sycophantic behavior (unrealistically agreeable or positive responses) so that I can distinguish genuine feedback from AI-typical agreeableness patterns.

**Why this priority**: Sycophancy is a known failure mode of AI systems and directly undermines research validity. Detecting it early prevents researchers from acting on misleading positive signals.

**Independent Test**: Can be tested by running sessions with prompts designed to elicit both positive and negative feedback, then measuring the ratio and identifying unrealistic positivity patterns.

**Acceptance Scenarios**:

1. **Given** a completed panel research session, **When** I request bias analysis, **Then** the system calculates a sycophancy rate showing the percentage of responses that are unrealistically positive or agreeable.

2. **Given** a panel where all personas express identical positive sentiment despite having diverse traits (including skeptical personas), **When** analyzing results, **Then** the system flags this as potential sycophancy clustering.

3. **Given** a sycophancy rate above the configured threshold (default: 30%), **When** viewing results, **Then** the system displays a warning and highlights specific responses that triggered the detection.

4. **Given** a skeptical-late-adopter persona, **When** they respond to a feature concept, **Then** their response should include at least one concern or criticism consistent with their skeptical trait profile.

---

### User Story 3 - Monitor Response Variance Across Panels (Priority: P2)

As a researcher, I want to track response variance across panel sessions so that I can verify synthetic panels produce appropriately diverse opinions rather than clustering around similar viewpoints.

**Why this priority**: Variance monitoring ensures panels deliver the diversity they promise. Without it, researchers may believe they have broad feedback when actually receiving homogeneous responses.

**Independent Test**: Can be tested by running the same question across multiple panels and calculating variance statistics, comparing against expected human variance baselines.

**Acceptance Scenarios**:

1. **Given** a completed panel session with 5 diverse personas, **When** I request variance analysis, **Then** the system calculates the standard deviation of sentiment and key response dimensions across the panel.

2. **Given** a panel with intentionally diverse personas (early adopter to late majority), **When** variance is below expected thresholds, **Then** the system flags potential clustering and identifies which responses are unexpectedly similar.

3. **Given** rating scale questions, **When** analyzing variance, **Then** the system compares the synthetic panel's rating distribution against expected human population variance for that question type.

4. **Given** multiple sessions with the same panel, **When** comparing variance, **Then** variance should remain consistent (within 20% relative difference) indicating stable panel diversity.

---

### User Story 4 - Detect Character Drift Within Sessions (Priority: P2)

As a researcher, I want to identify when a persona's responses drift away from their initial characterization during a research session so that I can ensure personas maintain consistent identity throughout longer engagements.

**Why this priority**: Character drift undermines the reliability of multi-turn interactions like interviews and focus groups. Detecting drift ensures the persona at the end of a session still represents the same user segment.

**Independent Test**: Can be tested by conducting a long interview session and measuring trait alignment at different points in the transcript, flagging significant deviations.

**Acceptance Scenarios**:

1. **Given** a completed interview session with 20+ exchanges, **When** I request drift analysis, **Then** the system calculates drift scores showing how persona trait alignment changed from beginning to end.

2. **Given** a persona who starts with strong privacy concerns, **When** their later responses show decreased privacy awareness, **Then** the system flags this as character drift with specific examples.

3. **Given** a drift score above the configured threshold (default: 25%), **When** viewing results, **Then** the system identifies the approximate point where drift began and which traits were affected.

4. **Given** a focus group discussion, **When** analyzing individual participant consistency, **Then** each persona's drift is tracked independently throughout the discussion.

---

### User Story 5 - Calibrate Against Real User Baselines (Priority: P3)

As a researcher, I want to compare synthetic panel responses against real user research data so that I can calibrate personas to better match actual human response patterns and validate the synthetic approach.

**Why this priority**: Calibration against real data is the ultimate validation of synthetic research. While valuable, it requires external data and is therefore a later priority after internal quality metrics are established.

**Independent Test**: Can be tested by importing a real user survey dataset, running the same questions on a synthetic panel, and generating a comparison report showing alignment.

**Acceptance Scenarios**:

1. **Given** I have real user survey data in a supported format, **When** I import it as a calibration baseline, **Then** the system stores the baseline with metadata (source, sample size, collection date).

2. **Given** a stored calibration baseline, **When** I run the same questions on a synthetic panel, **Then** the system automatically generates a comparison showing response distribution overlap.

3. **Given** synthetic responses significantly diverge from real baselines (overlap below 60%), **When** viewing calibration results, **Then** the system identifies specific questions and persona types that need adjustment.

4. **Given** calibration results, **When** I request recommendations, **Then** the system suggests specific persona trait adjustments to improve alignment with real user patterns.

---

### User Story 6 - View Quality Dashboard (Priority: P3)

As a researcher, I want to view a consolidated quality dashboard showing all metrics across my research sessions so that I can quickly assess the overall health of my synthetic research and identify areas needing attention.

**Why this priority**: A dashboard provides operational visibility but depends on all underlying metrics being implemented first. It's a usability enhancement rather than core functionality.

**Independent Test**: Can be tested by running several research sessions and verifying the dashboard correctly aggregates and displays all quality metrics with appropriate visualizations.

**Acceptance Scenarios**:

1. **Given** I have completed multiple research sessions, **When** I access the quality dashboard, **Then** I see aggregated metrics including average consistency, sycophancy rate, variance scores, and drift metrics.

2. **Given** the quality dashboard, **When** viewing recent sessions, **Then** sessions with quality warnings are visually distinguished (highlighted or badged) for easy identification.

3. **Given** quality metrics over time, **When** viewing the dashboard, **Then** I can see trend lines showing whether quality is improving, stable, or degrading.

4. **Given** the dashboard, **When** I click on a specific metric, **Then** I can drill down to see which sessions contributed to that metric and their individual scores.

---

### User Story 7 - Export Quality Reports (Priority: P3)

As a researcher, I want to export quality analysis reports so that I can share validation evidence with stakeholders and document research quality for compliance purposes.

**Why this priority**: Exporting supports transparency and stakeholder communication but is secondary to calculating and displaying the metrics themselves.

**Independent Test**: Can be tested by generating a quality report and verifying it contains all metrics in a well-formatted, shareable document.

**Acceptance Scenarios**:

1. **Given** a completed research session with quality analysis, **When** I export a quality report, **Then** the system generates a document containing all calculated metrics with explanations.

2. **Given** a quality export in Markdown format, **When** I share it with stakeholders, **Then** the document includes visualizations (tables, summaries) that are understandable without technical background.

3. **Given** a calibration comparison, **When** I export results, **Then** the export includes both synthetic and baseline data with side-by-side comparisons.

---

### Edge Cases

- What happens when a session has too few responses for meaningful variance calculation? System should require minimum 3 responses and display "insufficient data" warning for smaller samples.
- How does the system handle personas with intentionally contradictory traits (e.g., high openness but high traditionalism)? System should flag trait conflicts during persona validation rather than during quality analysis.
- What happens when calibration baseline data has missing values? System should calculate partial metrics for available data and note which comparisons were skipped.
- How does the system handle extremely short responses that lack sufficient content for trait analysis? System should require minimum 20 characters and flag shorter responses as "unable to analyze."
- What happens when all personas in a panel legitimately agree (e.g., universal usability issue)? System should distinguish genuine consensus (supported by reasoning) from sycophantic clustering (identical sentiment without substantive justification).
- How does the system handle real user baseline data from different demographic populations? System should support multiple baselines with demographic tags and compare synthetic panels against appropriately matched baselines.

## Requirements *(mandatory)*

### Functional Requirements

#### Consistency Checking

- **FR-001**: System MUST calculate consistency scores (0-100%) measuring alignment between persona responses and defined Big Five personality traits.
- **FR-002**: System MUST calculate consistency scores for Schwartz value alignment in addition to Big Five traits.
- **FR-003**: System MUST support configurable consistency threshold (default: 70%) for flagging quality warnings.
- **FR-004**: System MUST identify which specific traits show misalignment when consistency falls below threshold.
- **FR-005**: System MUST provide per-response trait alignment breakdown, not just session-level scores.

#### Bias Detection

- **FR-006**: System MUST calculate sycophancy rate as the percentage of unrealistically positive or agreeable responses.
- **FR-007**: System MUST detect sentiment clustering when diverse personas produce unexpectedly similar sentiment patterns.
- **FR-008**: System MUST support configurable sycophancy threshold (default: 30%) for flagging warnings.
- **FR-009**: System MUST flag specific responses that triggered sycophancy detection with explanations.
- **FR-010**: System MUST validate that skeptical personas include critical or cautionary content in their responses.

#### Variance Monitoring

- **FR-011**: System MUST calculate response variance (standard deviation) across panel sessions.
- **FR-012**: System MUST compare synthetic variance against expected human population variance baselines.
- **FR-013**: System MUST detect and flag response clustering when variance is below expected thresholds.
- **FR-014**: System MUST track variance stability across multiple sessions with the same panel.
- **FR-015**: System MUST support variance analysis for both quantitative (ratings) and qualitative (sentiment, themes) responses.

#### Character Drift Detection

- **FR-016**: System MUST calculate drift scores showing trait alignment change from session beginning to end.
- **FR-017**: System MUST identify the approximate point in a session where significant drift began.
- **FR-018**: System MUST support configurable drift threshold (default: 25%) for flagging warnings.
- **FR-019**: System MUST track individual persona drift independently in multi-persona sessions (focus groups).
- **FR-020**: System MUST identify which specific traits were affected by drift.

#### Calibration Pipeline

- **FR-021**: System MUST support importing real user survey data in CSV and JSON formats as calibration baselines.
- **FR-022**: System MUST store calibration baselines with metadata (source, sample size, collection date, demographic tags).
- **FR-023**: System MUST compare synthetic response distributions against stored baselines.
- **FR-024**: System MUST calculate distribution overlap percentage between synthetic and real responses.
- **FR-025**: System MUST generate recommendations for persona trait adjustments based on calibration gaps.
- **FR-026**: System MUST support multiple calibration baselines for different demographic populations.

#### Quality Dashboard

- **FR-027**: System MUST provide CLI commands for viewing quality metrics across sessions.
- **FR-028**: System MUST aggregate quality metrics (consistency, sycophancy, variance, drift) at session, panel, and persona levels.
- **FR-029**: System MUST visually distinguish sessions with quality warnings in listings.
- **FR-030**: System MUST support filtering sessions by quality status (healthy, warning, critical).
- **FR-031**: System MUST calculate trend metrics showing quality changes over time.

#### CLI Commands

- **FR-032**: System MUST provide `research quality analyze` command to run quality analysis on a session.
- **FR-033**: System MUST provide `research quality dashboard` command to view aggregated metrics.
- **FR-034**: System MUST provide `research quality report` command to generate quality reports.
- **FR-035**: System MUST provide `research calibration import` command to import baseline data.
- **FR-036**: System MUST provide `research calibration compare` command to compare synthetic vs real data.
- **FR-037**: System MUST provide `research calibration list` command to view stored baselines.

#### Output & Export

- **FR-038**: System MUST support Markdown export format for quality reports.
- **FR-039**: System MUST support JSON export format for quality metrics data.
- **FR-040**: System MUST include quality metadata in all research session exports.

### Key Entities

- **QualityMetrics**: A comprehensive assessment of research session quality containing consistency scores, sycophancy rate, variance measurements, and drift scores with associated thresholds and warnings.

- **ConsistencyScore**: Measures alignment between a persona's responses and their defined traits (Big Five, Schwartz values), with per-trait breakdown and overall percentage.

- **BiasAnalysis**: Assessment of response bias patterns including sycophancy rate, sentiment clustering indicators, and flagged responses with explanations.

- **VarianceReport**: Statistical analysis of response diversity across a panel including standard deviation, expected vs actual variance, and clustering detection.

- **DriftAnalysis**: Measurement of persona characterization stability over a session including drift score, drift point identification, and affected traits.

- **CalibrationBaseline**: Stored real user research data with metadata used for comparison including source, sample demographics, response distributions, and collection date.

- **CalibrationComparison**: Analysis comparing synthetic panel responses against real baselines including distribution overlap, divergence points, and adjustment recommendations.

- **QualityThresholds**: Configurable limits for quality warnings including consistency minimum (70%), sycophancy maximum (30%), variance minimum, and drift maximum (25%).

## Assumptions

- Quality analysis will integrate with existing research methods (single, panel, survey, interview, focus group) by analyzing completed session data.
- Trait-keyword mapping for consistency checking will extend the existing Big Five keyword matching from Phase 1 to be more comprehensive.
- Sycophancy detection will use a combination of sentiment analysis and reasoning pattern detection rather than simple positive word counting.
- Character drift will be measured by comparing trait alignment at different windows of the session (beginning, middle, end) rather than per-response.
- Calibration baseline imports will support standard research data formats (CSV with headers, JSON arrays) without requiring custom transformations.
- The quality dashboard will be CLI-based using Rich formatting, consistent with existing UI patterns (web UI is Phase 5).
- Default thresholds are based on industry quality standards and initial testing; they should be adjustable per-project.
- Real user baseline data will be provided by the researcher from their own studies; the system does not include pre-packaged baselines.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Consistency scores correlate with human evaluation of persona authenticity at least 80% of the time when validated against manual review.
- **SC-002**: Sycophancy detection identifies at least 85% of artificially positive responses when tested against known sycophantic examples.
- **SC-003**: Variance monitoring correctly flags clustering in panels where responses should differ but do not, with less than 10% false positive rate.
- **SC-004**: Character drift detection identifies drift in long sessions (20+ exchanges) that human reviewers confirm at least 75% of the time.
- **SC-005**: Calibration comparisons produce actionable insights that improve synthetic-real alignment by at least 15% when recommendations are applied.
- **SC-006**: Quality analysis completes within 10 seconds for a 5-persona panel session with 10 questions each.
- **SC-007**: Researchers report quality metrics increase their confidence in synthetic research findings by at least 50% in user feedback.
- **SC-008**: All quality reports are understandable to non-technical stakeholders without additional explanation.
