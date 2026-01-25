<!--
  SYNC IMPACT REPORT
  ==================
  Version change: 1.0.0 → 1.1.0 (MINOR)

  Modified Principles:
  - I. Subagent-First Architecture: Language strengthened (is → MUST be)
  - II. Persona Integrity: Language strengthened (are defined → MUST be defined)
  - III. Honest Limitations: Language strengthened (state → MUST state)
  - IV. Quality Through Calibration: Language strengthened (improves → MUST improve)
  - V. Parallel Execution: Language strengthened (maximizes → MUST maximize)
  - Response Quality Gates: Clarified warning/review actions

  Added Sections:
  - Governance > Amendment Procedure
  - Governance > Versioning Policy
  - Governance > Compliance Review

  Removed Sections: None

  Templates Requiring Updates:
  - .specify/templates/plan-template.md: ✅ No update needed (generic constitution reference)
  - .specify/templates/spec-template.md: ✅ No update needed
  - .specify/templates/tasks-template.md: ✅ No update needed

  Follow-up TODOs: None
-->

# Synthetic User Research Platform Constitution

## Core Principles

### I. Subagent-First Architecture

Every research capability MUST be executed through Claude Code subagents. The orchestration layer coordinates subagents but MUST delegate all persona simulation to independent Task tool invocations. Each persona MUST run in isolation with its own context to ensure behavioral independence.

### II. Persona Integrity

Personas MUST be defined declaratively in YAML with psychological frameworks (Big Five, Schwartz values). Persona definitions MUST be versioned and immutable within a research session. Responses MUST demonstrably align with defined traits - consistency is measurable and enforced.

### III. Honest Limitations

Synthetic research has known biases (sycophancy, variance reduction, WEIRD bias). All outputs MUST explicitly state these limitations. The system MUST recommend real user validation for high-stakes decisions. Synthetic data MUST NOT be presented as equivalent to human research.

### IV. Quality Through Calibration

Research quality MUST improve through systematic calibration against real user baselines. Quality metrics (consistency, sycophancy rate, variance) MUST be tracked for every session. Personas MUST be refined based on calibration data on a 60-90 day cycle.

### V. Parallel Execution

Panel research MUST maximize efficiency through parallel subagent execution. Independent persona responses MUST be gathered concurrently. Aggregation and analysis MUST occur after all responses complete.

## Technical Standards

### Persona Definition Requirements

- All personas MUST include Big Five personality scores (1-10 scale)
- At least two Schwartz value priorities MUST be specified
- Technology adoption category is REQUIRED for product testing
- Anti-sycophancy calibration instructions are REQUIRED

### Response Quality Gates

- Consistency score MUST exceed 90% to include in final analysis
- Sessions with >30% sycophancy rate MUST trigger a warning notification to the operator and flag the session for manual review
- Variance significantly below human baseline MUST pause session for calibration review before proceeding

### Data Handling

- Real user PII MUST NOT appear in persona definitions
- Research sessions MUST be logged with full reproducibility
- Export formats MUST clearly label data as synthetically generated

## Development Workflow

### Test-First for Quality

Quality metrics tests MUST be written before feature implementation. Persona consistency validation MUST be automated. Integration tests MUST verify subagent coordination.

### Progressive Enhancement

Each phase MUST build on a stable foundation. MVP MUST validate core approach before expanding. New features MUST include quality metric coverage.

## Governance

This constitution guides all development decisions for the Synthetic User Research Platform.

### Amendment Procedure

1. **Proposal**: Any contributor MAY propose an amendment by documenting the rationale and impact
2. **Review**: Amendments MUST be reviewed for impact on existing capabilities
3. **Approval**: Changes to Core Principles require explicit project lead approval
4. **Documentation**: All amendments MUST update the version number and Last Amended date

### Versioning Policy

This constitution follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Backward-incompatible changes - removal or fundamental redefinition of principles
- **MINOR**: Backward-compatible additions - new principles, sections, or materially expanded guidance
- **PATCH**: Backward-compatible fixes - clarifications, wording improvements, typo corrections

### Compliance Review

- Constitution compliance SHOULD be verified at the start of each feature implementation (via plan.md Constitution Check)
- Violations MUST be documented in the plan's Complexity Tracking table with justification
- Quarterly review of constitution effectiveness is RECOMMENDED

**Version**: 1.1.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-01-24
