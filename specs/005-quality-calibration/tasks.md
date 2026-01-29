# Tasks: Quality & Calibration

**Input**: Design documents from `/specs/005-quality-calibration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cli-contracts.md, quickstart.md

**Tests**: Included per constitution requirement ("Quality metrics tests MUST be written before feature implementation").

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new directories, add enumerations, and establish shared configuration for quality & calibration features.

- [X] T001 Create calibration directory structure: `calibration/baselines/` and `calibration/comparisons/` with `.gitkeep` files
- [X] T002 Add QualityStatus, DriftWarningLevel, AlignmentStatus, RecommendationType, and RecommendationPriority enums to `src/models/enums.py`
- [X] T003 [P] Create QualityThresholds model with configurable defaults (consistency 70%, sycophancy 30%, drift 25%, variance 0.6) in `src/models/calibration.py`
- [X] T004 [P] Add quality test fixtures (high_consistency_session, sycophantic_session, drifted_session, calibration_baseline) to `tests/conftest.py`

**Checkpoint**: Directory structure ready, shared enums and thresholds available for all user stories.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core quality models that MUST be complete before ANY user story can be implemented. These are shared entities referenced across multiple stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create TraitAlignment model (trait_name, trait_value, alignment_score, matched_keywords, expected_keywords, weight) in `src/models/quality.py`
- [X] T006 Create ExtendedQualityMetrics model with Phase 1 compatibility fields plus Phase 4 extensions (consistency_details, bias_analysis, variance_report, drift_analysis, quality_status, quality_score) in `src/models/quality.py`
- [X] T007 [P] Write unit tests for QualityThresholds model validation (non-negative, range checks) in `tests/unit/test_quality_models.py`
- [X] T008 [P] Write unit tests for TraitAlignment and ExtendedQualityMetrics models in `tests/unit/test_quality_models.py`
- [X] T009 Extend high-trait and low-trait keyword mappings for all Big Five traits with additional keywords in `src/services/quality_metrics.py` (extending existing `HIGH_TRAIT_KEYWORDS` and `LOW_TRAIT_KEYWORDS`)
- [X] T010 Create Schwartz value keyword mappings (self_direction, security, benevolence, universalism, etc.) in `src/services/quality_metrics.py`

**Checkpoint**: Foundation ready - shared models and keyword mappings available. User story implementation can now begin.

---

## Phase 3: User Story 1 - Assess Persona Response Consistency (Priority: P1) 🎯 MVP

**Goal**: Calculate consistency scores measuring Big Five and Schwartz alignment with per-response breakdown, enabling researchers to validate persona trait fidelity.

**Independent Test**: Run a research session with a known persona, calculate consistency scores, and verify scores reflect actual trait alignment per response.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Write unit tests for ConsistencyScore model (overall_score 0-100, big_five_alignment length 5, per_response_scores validation) in `tests/unit/test_quality_models.py`
- [X] T012 [P] [US1] Write unit tests for ConsistencyChecker.calculate_big_five() with high-openness persona and matching keywords in `tests/unit/test_consistency_checker.py`
- [X] T013 [P] [US1] Write unit tests for ConsistencyChecker.calculate_schwartz() with self_direction and security priorities in `tests/unit/test_consistency_checker.py`
- [X] T014 [P] [US1] Write unit tests for ConsistencyChecker.per_response_breakdown() verifying individual response scores in `tests/unit/test_consistency_checker.py`
- [X] T015 [P] [US1] Write unit tests for weighted scoring (extreme traits weighted higher than neutral) in `tests/unit/test_consistency_checker.py`
- [X] T016 [P] [US1] Write unit tests for consistency threshold warning flags when score < 70% in `tests/unit/test_consistency_checker.py`

### Implementation for User Story 1

- [X] T017 [US1] Create ConsistencyScore model (overall_score, big_five_score, schwartz_score, big_five_alignment, schwartz_alignment, per_response_scores, response_variance, passed_threshold, warning_flags) in `src/models/quality.py`
- [X] T018 [US1] Implement ConsistencyChecker.calculate_big_five() with weighted trait-keyword matching (weight = |trait_value - 5| / 5) in `src/services/consistency_checker.py`
- [X] T019 [US1] Implement ConsistencyChecker.calculate_schwartz() for Schwartz value priority alignment in `src/services/consistency_checker.py`
- [X] T020 [US1] Implement ConsistencyChecker.per_response_breakdown() to score each response individually in `src/services/consistency_checker.py`
- [X] T021 [US1] Implement ConsistencyChecker.calculate() orchestrator combining Big Five (60%) and Schwartz (40%) into overall ConsistencyScore in `src/services/consistency_checker.py`
- [X] T022 [US1] Add threshold checking and warning flag generation for consistency below configurable threshold in `src/services/consistency_checker.py`
- [X] T023 [US1] Verify all US1 tests pass and consistency scoring produces correct results

**Checkpoint**: Consistency scoring works independently. Can calculate per-trait, per-response, and session-level consistency.

---

## Phase 4: User Story 2 - Detect Sycophancy and Positivity Bias (Priority: P1)

**Goal**: Identify unrealistically positive responses through multi-signal detection (phrase patterns, sentiment ratios, clustering, skeptical persona validation).

**Independent Test**: Run sessions with prompts eliciting diverse feedback, measure sycophancy rate, and verify clustering and flagging work correctly.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T024 [P] [US2] Write unit tests for BiasAnalysis, FlaggedResponse, and SentimentClustering models in `tests/unit/test_quality_models.py`
- [X] T025 [P] [US2] Write unit tests for BiasDetector.detect_sycophancy_phrases() with known sycophantic text in `tests/unit/test_bias_detector.py`
- [X] T026 [P] [US2] Write unit tests for BiasDetector.calculate_sentiment_ratio() with positive-skewed responses in `tests/unit/test_bias_detector.py`
- [X] T027 [P] [US2] Write unit tests for BiasDetector.detect_clustering() with identical sentiments from diverse panel in `tests/unit/test_bias_detector.py`
- [X] T028 [P] [US2] Write unit tests for BiasDetector.validate_skeptical_personas() checking that skeptical personas include criticism in `tests/unit/test_bias_detector.py`
- [X] T029 [P] [US2] Write unit tests for sycophancy rate calculation and threshold warnings in `tests/unit/test_bias_detector.py`

### Implementation for User Story 2

- [X] T030 [P] [US2] Create FlaggedResponse model (response_index, response_text, flag_type, flag_reason, confidence) in `src/models/quality.py`
- [X] T031 [P] [US2] Create SentimentClustering model (detected, dominant_sentiment, dominant_percentage, expected_diversity, personas_affected) in `src/models/quality.py`
- [X] T032 [US2] Create BiasAnalysis model (sycophancy_rate, sycophancy_phrases_found, positive_negative_ratio, sentiment_clustering, flagged_responses, passed_threshold, warning_flags) in `src/models/quality.py`
- [X] T033 [US2] Implement BiasDetector.detect_sycophancy_phrases() with extended phrase list (12+ patterns) in `src/services/bias_detector.py`
- [X] T034 [US2] Implement BiasDetector.calculate_sentiment_ratio() with positive/negative keyword counting in `src/services/bias_detector.py`
- [X] T035 [US2] Implement BiasDetector.detect_clustering() checking if >80% of panel has same sentiment in `src/services/bias_detector.py`
- [X] T036 [US2] Implement BiasDetector.validate_skeptical_personas() checking criticism presence for skeptical trait profiles in `src/services/bias_detector.py`
- [X] T037 [US2] Implement BiasDetector.full_analysis() orchestrator combining all signals with weights (phrases 0.25, ratio 0.25, missing_criticism 0.30, clustering 0.20) in `src/services/bias_detector.py`
- [X] T038 [US2] Add response flagging with human-readable explanations for each detected issue in `src/services/bias_detector.py`
- [X] T039 [US2] Verify all US2 tests pass and bias detection correctly identifies sycophantic patterns

**Checkpoint**: Bias detection works independently. Can calculate sycophancy rate, detect clustering, flag specific responses, and validate skeptical personas.

---

## Phase 5: User Story 3 - Monitor Response Variance Across Panels (Priority: P2)

**Goal**: Calculate response variance statistics, compare against expected human baselines, and detect inappropriate clustering in panel sessions.

**Independent Test**: Run the same question across a panel, calculate variance, and verify clustering detection flags homogeneous responses.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T040 [P] [US3] Write unit tests for RatingVariance, SentimentDistribution (percentages sum to ~100), and VarianceReport models in `tests/unit/test_quality_models.py`
- [X] T041 [P] [US3] Write unit tests for VarianceMonitor.calculate_rating_variance() with known rating distributions in `tests/unit/test_variance_monitor.py`
- [X] T042 [P] [US3] Write unit tests for VarianceMonitor.calculate_sentiment_distribution() with mixed panel sentiments in `tests/unit/test_variance_monitor.py`
- [X] T043 [P] [US3] Write unit tests for VarianceMonitor.detect_clustering() with below-threshold variance ratio in `tests/unit/test_variance_monitor.py`
- [X] T044 [P] [US3] Write unit tests for variance stability across multiple sessions (relative difference < 20%) in `tests/unit/test_variance_monitor.py`

### Implementation for User Story 3

- [X] T045 [P] [US3] Create RatingVariance model (question_id, mean, stdev, variance, expected_stdev, variance_ratio, clustering_detected) in `src/models/quality.py`
- [X] T046 [P] [US3] Create SentimentDistribution model (positive, negative, mixed, neutral, diversity_score) in `src/models/quality.py`
- [X] T047 [US3] Create VarianceReport model (rating_variances, overall_rating_variance, sentiment_distribution, clustering_detected, stability_score, passed_threshold, warning_flags) in `src/models/quality.py`
- [X] T048 [US3] Implement VarianceMonitor.calculate_rating_variance() using statistics.stdev with expected human baselines (1-10: 2.5, 1-5: 1.2) in `src/services/variance_monitor.py`
- [X] T049 [US3] Implement VarianceMonitor.calculate_sentiment_distribution() computing positive/negative/mixed/neutral percentages in `src/services/variance_monitor.py`
- [X] T050 [US3] Implement VarianceMonitor.detect_clustering() flagging when variance_ratio < 0.6 or single sentiment > 80% in `src/services/variance_monitor.py`
- [X] T051 [US3] Implement VarianceMonitor.analyze() orchestrator producing full VarianceReport from panel session data in `src/services/variance_monitor.py`
- [X] T052 [US3] Add variance stability tracking for multi-session comparison in `src/services/variance_monitor.py`
- [X] T053 [US3] Verify all US3 tests pass and variance monitoring correctly detects clustering

**Checkpoint**: Variance monitoring works independently. Can calculate rating variance, sentiment distribution, detect clustering, and compare against baselines.

---

## Phase 6: User Story 4 - Detect Character Drift Within Sessions (Priority: P2)

**Goal**: Track persona trait alignment across session segments to detect when personas deviate from their characterization during long sessions.

**Independent Test**: Conduct a long interview session, measure trait alignment at beginning/middle/end, and verify drift detection flags significant deviations.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T054 [P] [US4] Write unit tests for SegmentScore, AffectedTrait, and DriftAnalysis models in `tests/unit/test_quality_models.py`
- [X] T055 [P] [US4] Write unit tests for DriftDetector.segment_session() dividing responses into 3 segments in `tests/unit/test_drift_detector.py`
- [X] T056 [P] [US4] Write unit tests for DriftDetector.calculate_drift_score() with known drifting session in `tests/unit/test_drift_detector.py`
- [X] T057 [P] [US4] Write unit tests for DriftDetector.find_drift_point() identifying segment where drift began in `tests/unit/test_drift_detector.py`
- [X] T058 [P] [US4] Write unit tests for per-trait drift tracking (affected_traits vs stable_traits) in `tests/unit/test_drift_detector.py`
- [X] T059 [P] [US4] Write unit tests for drift threshold warning levels (none < 15%, warning 15-25%, critical > 25%) in `tests/unit/test_drift_detector.py`

### Implementation for User Story 4

- [X] T060 [P] [US4] Create SegmentScore model (segment_index, start_response, end_response, consistency_score, response_count) in `src/models/quality.py`
- [X] T061 [P] [US4] Create AffectedTrait model (trait_name, trait_type, initial_alignment, final_alignment, drift_amount, drift_direction) in `src/models/quality.py`
- [X] T062 [US4] Create DriftAnalysis model (drift_score, drift_detected, segment_scores, drift_point_index, affected_traits, stable_traits, warning_level, warning_flags) in `src/models/quality.py`
- [X] T063 [US4] Implement DriftDetector.segment_session() dividing responses into configurable segments (default 3) in `src/services/drift_detector.py`
- [X] T064 [US4] Implement DriftDetector.calculate_segment_scores() using ConsistencyChecker to score each segment in `src/services/drift_detector.py`
- [X] T065 [US4] Implement DriftDetector.find_drift_point() finding maximum score delta between consecutive segments in `src/services/drift_detector.py`
- [X] T066 [US4] Implement DriftDetector.identify_affected_traits() comparing per-trait alignment between first and last segments in `src/services/drift_detector.py`
- [X] T067 [US4] Implement DriftDetector.analyze() orchestrator producing full DriftAnalysis with warning level classification in `src/services/drift_detector.py`
- [X] T068 [US4] Verify all US4 tests pass and drift detection correctly identifies trait deviations across session segments

**Checkpoint**: Drift detection works independently. Can segment sessions, calculate drift, identify affected traits, and classify warning severity.

---

## Phase 7: User Story 5 - Calibrate Against Real User Baselines (Priority: P3)

**Goal**: Import real user data, compare synthetic response distributions against baselines, and generate persona adjustment recommendations.

**Independent Test**: Import a real user CSV, run synthetic survey with same questions, generate comparison showing overlap percentage and recommendations.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T069 [P] [US5] Write unit tests for NumericDistribution, CategoricalDistribution, QuestionDistribution, CalibrationBaseline models in `tests/unit/test_calibration_models.py`
- [X] T070 [P] [US5] Write unit tests for QuestionComparison, Recommendation, CalibrationComparison models in `tests/unit/test_calibration_models.py`
- [X] T071 [P] [US5] Write unit tests for CalibrationPipeline.import_csv() parsing CSV format into baseline distributions in `tests/unit/test_calibration_pipeline.py`
- [X] T072 [P] [US5] Write unit tests for CalibrationPipeline.import_json() parsing JSON format into baseline distributions in `tests/unit/test_calibration_pipeline.py`
- [X] T073 [P] [US5] Write unit tests for CalibrationPipeline.calculate_overlap() with known distribution pairs in `tests/unit/test_calibration_pipeline.py`
- [X] T074 [P] [US5] Write unit tests for CalibrationPipeline.generate_recommendations() producing adjustment suggestions in `tests/unit/test_calibration_pipeline.py`
- [X] T075 [P] [US5] Write unit tests for CalibrationPipeline.save_baseline() and load_baseline() YAML persistence in `tests/unit/test_calibration_pipeline.py`

### Implementation for User Story 5

- [X] T076 [P] [US5] Create NumericDistribution and CategoricalDistribution models in `src/models/calibration.py`
- [X] T077 [P] [US5] Create QuestionDistribution model with discriminated union for numeric/categorical in `src/models/calibration.py`
- [X] T078 [US5] Create CalibrationBaseline model (id, name, source, sample_size, collection_date, demographic_tags, distributions) in `src/models/calibration.py`
- [X] T079 [P] [US5] Create QuestionComparison and Recommendation models in `src/models/calibration.py`
- [X] T080 [US5] Create CalibrationComparison model (baseline_id, overall_overlap, alignment_status, question_comparisons, recommendations) in `src/models/calibration.py`
- [X] T081 [US5] Implement CalibrationPipeline.import_csv() parsing CSV rows into distributions (compute mean, stdev, histogram for ratings; frequencies for categorical) in `src/services/calibration_pipeline.py`
- [X] T082 [US5] Implement CalibrationPipeline.import_json() parsing JSON array into distributions in `src/services/calibration_pipeline.py`
- [X] T083 [US5] Implement CalibrationPipeline.save_baseline() serializing CalibrationBaseline to YAML in `calibration/baselines/` in `src/services/calibration_pipeline.py`
- [X] T084 [US5] Implement CalibrationPipeline.load_baseline() and list_baselines() reading from `calibration/baselines/` in `src/services/calibration_pipeline.py`
- [X] T085 [US5] Implement CalibrationPipeline.calculate_overlap() using histogram intersection for numeric and frequency overlap for categorical in `src/services/calibration_pipeline.py`
- [X] T086 [US5] Implement CalibrationPipeline.compare() orchestrator producing full CalibrationComparison with per-question results in `src/services/calibration_pipeline.py`
- [X] T087 [US5] Implement CalibrationPipeline.generate_recommendations() analyzing divergence patterns and suggesting persona adjustments in `src/services/calibration_pipeline.py`
- [X] T088 [US5] Implement CalibrationPipeline.delete_baseline() removing baseline YAML file in `src/services/calibration_pipeline.py`
- [X] T089 [US5] Implement `research calibration import` CLI command with --file, --name, --source, --tags, --collection-date options in `src/cli/calibration_commands.py`
- [X] T090 [US5] Implement `research calibration list` CLI command with --format and --tags filtering in `src/cli/calibration_commands.py`
- [X] T091 [US5] Implement `research calibration show` CLI command displaying baseline details with Rich formatting in `src/cli/calibration_commands.py`
- [X] T092 [US5] Implement `research calibration compare` CLI command with --baseline, --session, --recommendations options in `src/cli/calibration_commands.py`
- [X] T093 [US5] Implement `research calibration delete` CLI command with --force confirmation in `src/cli/calibration_commands.py`
- [X] T094 [US5] Register calibration command group under `research` in `src/cli/main.py`
- [X] T095 [US5] Verify all US5 tests pass and calibration pipeline correctly imports, compares, and recommends

**Checkpoint**: Calibration pipeline works independently. Can import baselines, compare distributions, calculate overlap, and generate recommendations.

---

## Phase 8: User Story 6 - View Quality Dashboard (Priority: P3)

**Goal**: Provide CLI-based aggregated quality metrics view with session listings, status filtering, and trend tracking.

**Independent Test**: Run several research sessions, verify dashboard displays correct aggregate metrics and highlights sessions with warnings.

### Tests for User Story 6

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T096 [P] [US6] Write unit tests for SessionSummary, TrendDataPoint, and QualityDashboardMetrics models in `tests/unit/test_quality_models.py`
- [X] T097 [P] [US6] Write unit tests for QualityDashboard.aggregate_metrics() with mixed healthy/warning sessions in `tests/unit/test_quality_dashboard.py`
- [X] T098 [P] [US6] Write unit tests for QualityDashboard.filter_by_status() with healthy/warning/critical filters in `tests/unit/test_quality_dashboard.py`
- [X] T099 [P] [US6] Write unit tests for QualityDashboard.calculate_trends() with time-series data in `tests/unit/test_quality_dashboard.py`

### Implementation for User Story 6

- [X] T100 [P] [US6] Create SessionSummary model (session_id, session_type, quality_status, consistency_score, sycophancy_rate, timestamp) in `src/models/quality.py`
- [X] T101 [P] [US6] Create TrendDataPoint model (date, metric_value, session_count) in `src/models/quality.py`
- [X] T102 [US6] Create QualityDashboardMetrics model (overall_status, sessions_analyzed, avg_consistency_score, avg_sycophancy_rate, recent_sessions, trends) in `src/models/quality.py`
- [X] T103 [US6] Implement QualityDashboard.aggregate_metrics() computing averages from session quality data in `src/services/quality_dashboard.py`
- [X] T104 [US6] Implement QualityDashboard.filter_by_status() filtering sessions by quality status in `src/services/quality_dashboard.py`
- [X] T105 [US6] Implement QualityDashboard.calculate_trends() computing metric trends over time periods in `src/services/quality_dashboard.py`
- [X] T106 [US6] Implement `research quality analyze` CLI command with --session, --format, --output, and threshold options in `src/cli/quality_commands.py`
- [X] T107 [US6] Implement QualityAnalyzer orchestrator combining ConsistencyChecker, BiasDetector, VarianceMonitor, DriftDetector into single analyze() call in `src/services/quality_dashboard.py`
- [X] T108 [US6] Implement `research quality dashboard` CLI command with --limit, --status, --format, --since options and Rich table output in `src/cli/quality_commands.py`
- [X] T109 [US6] Register quality command group under `research` in `src/cli/main.py`
- [X] T110 [US6] Implement Rich formatters for dashboard display (metrics table, session list, trend indicators) in `src/cli/formatters.py`
- [X] T111 [US6] Verify all US6 tests pass and dashboard correctly aggregates and displays quality metrics

**Checkpoint**: Quality dashboard works independently. Can aggregate metrics, filter sessions, display trends, and run quality analysis via CLI.

---

## Phase 9: User Story 7 - Export Quality Reports (Priority: P3)

**Goal**: Generate shareable quality reports in Markdown and JSON formats with calibration comparisons.

**Independent Test**: Generate a quality report and verify it contains all metrics in a formatted, stakeholder-readable document.

### Tests for User Story 7

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T112 [P] [US7] Write unit tests for quality report Jinja2 template rendering with sample metrics data in `tests/unit/test_quality_dashboard.py`
- [X] T113 [P] [US7] Write unit tests for calibration report template rendering with comparison data in `tests/unit/test_calibration_pipeline.py`

### Implementation for User Story 7

- [X] T114 [P] [US7] Create quality report Jinja2 template with executive summary, consistency, bias, variance, drift sections and synthetic data disclaimer in `src/templates/quality_report.j2`
- [X] T115 [P] [US7] Create calibration comparison Jinja2 template with distribution visualizations and recommendation sections in `src/templates/calibration_report.j2`
- [X] T116 [US7] Implement report rendering in QualityDashboard.generate_report() using Jinja2 template for Markdown output in `src/services/quality_dashboard.py`
- [X] T117 [US7] Implement JSON export in QualityDashboard.export_json() serializing ExtendedQualityMetrics with synthetic data disclaimer in `src/services/quality_dashboard.py`
- [X] T118 [US7] Implement `research quality report` CLI command with --session, --since, --until, --output, --format options in `src/cli/quality_commands.py`
- [X] T119 [US7] Verify all US7 tests pass and reports render correctly in both Markdown and JSON formats

**Checkpoint**: Quality reports export correctly. Can generate Markdown and JSON reports for sessions and time periods.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, CLI version update, and final validation.

- [X] T120 [P] Write contract tests for all new CLI commands (quality analyze, dashboard, report; calibration import, list, show, compare, delete) in `tests/contract/test_quality_cli_contract.py`
- [X] T121 Write integration test for full quality workflow (run panel → analyze quality → generate report) in `tests/integration/test_quality_workflow.py`
- [X] T122 Write integration test for full calibration workflow (import baseline → run synthetic survey → compare → recommendations) in `tests/integration/test_quality_workflow.py`
- [X] T123 [P] Add synthetic data disclaimer to all quality report and export outputs
- [X] T124 Update CLI version to 0.4.0 in `src/cli/main.py`
- [X] T125 Run full test suite (`pytest`) and verify all tests pass including new Phase 4 tests
- [X] T126 Run quickstart.md validation - verify all example commands work correctly
- [X] T127 Run `ruff check .` and fix any linting issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 Consistency (Phase 3)**: Depends on Foundational (Phase 2)
- **US2 Bias Detection (Phase 4)**: Depends on Foundational (Phase 2)
- **US3 Variance (Phase 5)**: Depends on Foundational (Phase 2)
- **US4 Drift (Phase 6)**: Depends on Foundational (Phase 2), uses ConsistencyChecker from US1
- **US5 Calibration (Phase 7)**: Depends on Foundational (Phase 2)
- **US6 Dashboard (Phase 8)**: Depends on US1, US2, US3, US4 (aggregates all metrics)
- **US7 Reports (Phase 9)**: Depends on US6 (uses dashboard aggregation)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    │
Phase 2: Foundational
    │
    ├──── US1: Consistency (P1) ──────────────────────┐
    │                                                   │
    ├──── US2: Bias Detection (P1) ────────────────────┤
    │                                                   │
    ├──── US3: Variance (P2) ──────────────────────────┤
    │                                                   │
    ├──── US4: Drift (P2) ─── [needs US1 checker] ────┤
    │                                                   │
    ├──── US5: Calibration (P3) ───────────────────────┤
    │                                                   │
    │                                           US6: Dashboard (P3)
    │                                                   │
    │                                           US7: Reports (P3)
    │                                                   │
    └──────────────────────────────────── Phase 10: Polish
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before CLI commands
- Core implementation before integration
- Story complete (tests pass) before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003, T004 can run in parallel
- **Phase 2**: T007, T008 can run in parallel; T009, T010 can run in parallel
- **US1-US3**: Can start in parallel after Phase 2 (different files, no dependencies)
- **US4**: Can start in parallel with US1 but needs ConsistencyChecker for segment scoring
- **US5**: Can start in parallel with US1-US4 (independent calibration system)
- **Within each US**: All test tasks [P] can run in parallel; model tasks [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for US1 together:
Task: "Unit test for ConsistencyScore model in tests/unit/test_quality_models.py"
Task: "Unit test for calculate_big_five() in tests/unit/test_consistency_checker.py"
Task: "Unit test for calculate_schwartz() in tests/unit/test_consistency_checker.py"
Task: "Unit test for per_response_breakdown() in tests/unit/test_consistency_checker.py"
Task: "Unit test for weighted scoring in tests/unit/test_consistency_checker.py"
Task: "Unit test for threshold warnings in tests/unit/test_consistency_checker.py"

# After tests written, implement in dependency order:
Task: "Create ConsistencyScore model in src/models/quality.py"
# Then:
Task: "Implement calculate_big_five() in src/services/consistency_checker.py"
Task: "Implement calculate_schwartz() in src/services/consistency_checker.py"
# Then:
Task: "Implement calculate() orchestrator in src/services/consistency_checker.py"
```

## Parallel Example: US1 + US2 + US3 + US5 (After Foundational)

```bash
# These can all start in parallel since they work on different files:
Developer A → US1: src/services/consistency_checker.py
Developer B → US2: src/services/bias_detector.py
Developer C → US3: src/services/variance_monitor.py
Developer D → US5: src/services/calibration_pipeline.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Consistency Scoring
4. **STOP and VALIDATE**: Test consistency scoring independently
5. Researchers can now validate persona trait alignment

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Consistency) + US2 (Bias) → Core quality metrics available (MVP!)
3. Add US3 (Variance) + US4 (Drift) → Full quality analysis suite
4. Add US5 (Calibration) → Real user comparison capability
5. Add US6 (Dashboard) + US7 (Reports) → Operational visibility and sharing
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Consistency) → US4 (Drift, needs ConsistencyChecker)
   - Developer B: US2 (Bias) → US6 (Dashboard, after US1-US4)
   - Developer C: US3 (Variance) → US7 (Reports, after US6)
   - Developer D: US5 (Calibration, independent)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires test-first approach for quality metrics
- All exports must include synthetic data disclaimer per constitution
