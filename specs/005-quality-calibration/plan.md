# Implementation Plan: Quality & Calibration

**Branch**: `005-quality-calibration` | **Date**: 2026-01-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-quality-calibration/spec.md`

## Summary

Phase 4 implements comprehensive quality metrics and calibration capabilities for the Synthetic User Research Platform. Building on the existing QualityMetricsCalculator (Phase 1) and PanelQualityMetrics (Phase 2), this phase adds:

1. **Enhanced Consistency Checking** - Extended Big Five and Schwartz value alignment scoring with per-response breakdown
2. **Advanced Bias Detection** - Sycophancy rate calculation, sentiment clustering detection, and skeptical persona validation
3. **Variance Monitoring** - Panel diversity measurement, clustering detection, and baseline comparison
4. **Character Drift Detection** - Session-level trait stability tracking for interviews and focus groups
5. **Calibration Pipeline** - Import real user baselines, compare distributions, generate adjustment recommendations
6. **Quality Dashboard & Reports** - CLI-based metrics aggregation and export

## Technical Context

**Language/Version**: Python 3.11+ (continuation from Phase 0-3)
**Primary Dependencies**: PyYAML>=6.0, Pydantic>=2.0, Click>=8.0, Jinja2>=3.0, Rich>=13.0, asyncio (stdlib), statistics (stdlib)
**Storage**: YAML files for calibration baselines (`calibration/`), JSON for session exports
**Testing**: pytest>=7.0, pytest-cov>=4.0, pytest-asyncio>=0.23.0
**Target Platform**: CLI application (macOS/Linux/Windows)
**Project Type**: Single project (existing structure)
**Performance Goals**: Quality analysis completes within 10 seconds for 5-persona, 10-question panel sessions
**Constraints**: No new external dependencies; use stdlib statistics module
**Scale/Scope**: Support analysis of sessions with up to 50 responses; calibration baselines up to 1000 records

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Subagent-First Architecture | Quality analysis MUST work with subagent-generated responses | ✅ Pass | Analyzes existing SessionResponse objects from subagent execution |
| II. Persona Integrity | Quality metrics MUST validate trait alignment | ✅ Pass | Core feature: consistency scoring validates Big Five and Schwartz alignment |
| III. Honest Limitations | Outputs MUST state synthetic data limitations | ✅ Pass | Quality reports include synthetic data disclaimers |
| IV. Quality Through Calibration | Calibration MUST improve through real baselines | ✅ Pass | Core feature: CalibrationPipeline compares against real user data |
| V. Parallel Execution | Panel analysis MUST support parallel metrics calculation | ✅ Pass | Builds on existing async PanelExecutor patterns |

### Technical Standards Compliance

| Standard | Requirement | Status | Notes |
|----------|-------------|--------|-------|
| Persona Definition | Big Five (1-10), Schwartz values, tech adoption | ✅ Pass | Uses existing persona schema for consistency validation |
| Response Quality Gates | Consistency >90%, Sycophancy <30%, Variance baseline | ✅ Pass | Implements configurable thresholds per spec |
| Data Handling | No PII, full reproducibility, labeled exports | ✅ Pass | Calibration baselines anonymized; exports labeled synthetic |

### Development Workflow Compliance

| Workflow | Requirement | Status | Notes |
|----------|-------------|--------|-------|
| Test-First | Quality tests before implementation | ✅ Pass | Contract and unit tests for all new services |
| Progressive Enhancement | Build on stable foundation | ✅ Pass | Extends Phase 1 QualityMetricsCalculator |
| Quality Metric Coverage | New features include quality metrics | ✅ Pass | All quality services have their own quality gates |

## Project Structure

### Documentation (this feature)

```text
specs/005-quality-calibration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-contracts.md # CLI interface contract
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── quality.py              # NEW: QualityMetrics, ConsistencyScore, BiasAnalysis, VarianceReport, DriftAnalysis
│   ├── calibration.py          # NEW: CalibrationBaseline, CalibrationComparison, QualityThresholds
│   ├── enums.py                # EXTEND: QualityStatus enum
│   └── [existing models]
├── services/
│   ├── quality_metrics.py      # EXTEND: Enhanced consistency, bias detection, drift
│   ├── consistency_checker.py  # NEW: ConsistencyChecker service
│   ├── bias_detector.py        # NEW: BiasDetector service
│   ├── variance_monitor.py     # NEW: VarianceMonitor service
│   ├── drift_detector.py       # NEW: DriftDetector service
│   ├── calibration_pipeline.py # NEW: CalibrationPipeline service
│   ├── quality_dashboard.py    # NEW: QualityDashboard aggregation service
│   └── [existing services]
├── cli/
│   ├── quality_commands.py     # NEW: research quality analyze/dashboard/report
│   ├── calibration_commands.py # NEW: research calibration import/compare/list
│   └── [existing commands]
└── templates/
    ├── quality_report.j2       # NEW: Quality report template
    └── calibration_report.j2   # NEW: Calibration comparison template

tests/
├── unit/
│   ├── test_quality_models.py        # NEW
│   ├── test_calibration_models.py    # NEW
│   ├── test_consistency_checker.py   # NEW
│   ├── test_bias_detector.py         # NEW
│   ├── test_variance_monitor.py      # NEW
│   ├── test_drift_detector.py        # NEW
│   ├── test_calibration_pipeline.py  # NEW
│   └── test_quality_dashboard.py     # NEW
├── integration/
│   └── test_quality_workflow.py      # NEW
└── contract/
    └── test_quality_cli_contract.py  # NEW

calibration/                    # NEW: Calibration baseline storage
├── baselines/
│   └── [baseline-id].yaml      # Imported real user data
└── comparisons/
    └── [comparison-id].json    # Comparison results
```

**Structure Decision**: Continues single-project structure established in Phase 0-3. New services follow existing patterns with dedicated modules per responsibility. Calibration data stored in new `calibration/` directory alongside existing `personas/` and `protocols/` directories.

## Complexity Tracking

> No constitution violations requiring justification. All implementations follow established patterns.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
