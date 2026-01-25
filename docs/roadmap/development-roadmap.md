# Development Roadmap

## Overview

This roadmap outlines the phased development of the Synthetic User Research Platform, prioritizing a working MVP with Claude Code subagents before expanding to more sophisticated capabilities.

## Current Status

| Phase | Status | Completion Date |
|-------|--------|-----------------|
| Phase 0: Foundation | ✅ Complete | 2026-01-25 |
| Phase 1: Single Persona MVP | 🔲 Not Started | - |
| Phase 2: Multi-Persona Panels | 🔲 Not Started | - |
| Phase 3: Research Methods | 🔲 Not Started | - |
| Phase 4: Quality & Calibration | 🔲 Not Started | - |
| Phase 5: Advanced Features | 🔲 Not Started | - |

---

## Phase 0: Foundation ✅ COMPLETE

**Completed**: 2026-01-25 | **Branch**: `001-foundation`

### Objectives
- [x] Establish project structure
- [x] Define core data models
- [x] Create initial persona templates

### Deliverables

| Deliverable | Description | Status |
|-------------|-------------|--------|
| Project scaffolding | Directory structure, dependencies, configs | ✅ |
| Persona schema | YAML schema with Pydantic validation | ✅ |
| Base personas (5) | Initial set of diverse test personas | ✅ |
| Prompt templates | Jinja2 subagent prompt generation | ✅ |
| CLI commands | `persona validate/list/show/prompt`, `init` | ✅ |

### Implementation Summary

**Core Components:**
- `src/models/enums.py` - TechAdoptionCategory, SchwartzValue, calibration enums
- `src/models/persona.py` - Full Pydantic schema with Big Five, Schwartz values
- `src/services/persona_loader.py` - YAML loading with validation
- `src/services/persona_library.py` - List, search, retrieve personas
- `src/services/prompt_builder.py` - Jinja2 template-based prompt generation
- `src/cli/main.py` - Click CLI with 6 commands

**Base Personas Created:**
| ID | Name | Tech Adoption | Age |
|----|------|---------------|-----|
| tech-early-adopter | Alex Chen | early_adopter | 32 |
| skeptical-late-adopter | Margaret Wilson | late_majority | 58 |
| busy-professional | David Park | early_majority | 42 |
| privacy-conscious-user | Sarah Martinez | late_majority | 35 |
| power-user | Jamie Thompson | innovator | 27 |

**Test Coverage:**
- 73 tests passing (unit, integration, contract)
- Schema validation with helpful error messages
- CLI integration tests with Click CliRunner

### Usage

```bash
# Install
pip install -e ".[dev]"

# List personas
research-cli persona list

# Validate a persona
research-cli persona validate personas/definitions/tech-early-adopter.yaml

# Generate subagent prompt
research-cli persona prompt tech-early-adopter -o prompt.md

# Show persona details
research-cli persona show tech-early-adopter --section psychological
```

---

## Phase 1: Single Persona MVP 🔲 NEXT

**Prerequisites**: Phase 0 Complete ✅
**Branch**: `002-single-persona-mvp` (planned)

### Objectives
- [ ] Execute single persona research sessions
- [ ] Validate subagent approach with Claude Code Task tool
- [ ] Establish response quality baseline

### Deliverables

| Deliverable | Description | Status |
|-------------|-------------|--------|
| PersonaLoader | ✅ *Completed in Phase 0* | ✅ |
| PromptBuilder | ✅ *Completed in Phase 0* | ✅ |
| SingleSessionRunner | Execute one persona interview | 🔲 |
| ResponseParser | Extract structured data from responses | 🔲 |
| Research CLI | `research --persona=X --question="Y"` | 🔲 |

### Implementation Architecture

```
┌────────────────┐     ┌───────────────┐     ┌─────────────────┐
│ CLI Command    │────▶│ PersonaLoader │────▶│ PromptBuilder   │
└────────────────┘     └───────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌────────────────┐     ┌───────────────┐     ┌─────────────────┐
│ Response Output│◀────│ResponseParser │◀────│ Task(subagent)  │
└────────────────┘     └───────────────┘     └─────────────────┘
```

### Key Validation Criteria
- [ ] Persona responses align with defined traits
- [ ] Responses vary meaningfully across different personas
- [ ] Anti-sycophancy instructions produce critical feedback
- [ ] Responses maintain character consistency

## Phase 2: Multi-Persona Panels

### Objectives
- Execute parallel research with multiple personas
- Aggregate and analyze responses across panels
- Generate research reports

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| PanelManager | Create/manage persona panels |
| ParallelExecutor | Run multiple subagents concurrently |
| ResponseAggregator | Combine responses, identify themes |
| ReportGenerator | Create structured research reports |
| Panel CLI | `research --panel=X --topic="Y"` |

### Implementation Architecture

```
┌────────────────┐
│ Research       │
│ Request        │
└───────┬────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│                   PanelManager                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Persona 1│ │Persona 2│ │Persona 3│ │Persona N│ │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │
└───────┼──────────┼──────────┼──────────┼────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
┌───────────────────────────────────────────────────┐
│           ParallelExecutor (Task tools)           │
│    [Subagent]  [Subagent]  [Subagent]  [Subagent] │
└───────────────────────────────────────────────────┘
        │          │          │          │
        └──────────┴──────────┴──────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│              ResponseAggregator                   │
│  • Theme extraction                               │
│  • Consensus/divergence analysis                  │
│  • Quantitative summaries                         │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│              ReportGenerator                      │
│  • Markdown reports                               │
│  • JSON data export                               │
│  • Executive summaries                            │
└───────────────────────────────────────────────────┘
```

### Pre-Built Panels

| Panel Name | Composition | Use Case |
|------------|-------------|----------|
| `general-population` | Demographically diverse, 10 personas | General product testing |
| `tech-adopters` | Full adoption spectrum, 5 personas | Tech product testing |
| `skeptics-critics` | Privacy-conscious, skeptical, 5 personas | Stress testing |
| `power-users` | High-engagement, expert, 5 personas | Advanced feature testing |

## Phase 3: Research Methods

### Objectives
- Support different research methodologies
- Implement survey, interview, and focus group modes
- Add structured research protocols

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| SurveyEngine | Structured survey with rating scales |
| InterviewEngine | Deep-dive conversational interviews |
| FocusGroupEngine | Multi-persona discussions |
| ProtocolTemplates | Reusable research protocols |
| Method CLI | `survey`, `interview`, `focus-group` commands |

### Research Method Specifications

#### Survey Mode
```yaml
survey:
  title: "Feature Concept Test"
  questions:
    - type: rating
      question: "How likely are you to use this feature?"
      scale: 1-10

    - type: multiple_choice
      question: "What is your primary concern?"
      options: [Privacy, Complexity, Cost, None]

    - type: open_ended
      question: "What would make this feature more valuable?"
```

#### Interview Mode
```yaml
interview:
  topic: "Onboarding Experience"
  guide:
    - section: "Background"
      questions:
        - "Tell me about similar products you've tried"
        - "What was your first impression?"

    - section: "Experience"
      questions:
        - "Walk me through your first session"
        - "What was confusing or unclear?"

    - section: "Recommendations"
      questions:
        - "What would you change?"
```

#### Focus Group Mode
```yaml
focus_group:
  topic: "Pricing Model Feedback"
  size: 6
  composition:
    - type: "price-sensitive"
      count: 2
    - type: "value-focused"
      count: 2
    - type: "feature-focused"
      count: 2
  discussion_guide:
    - "Initial reactions to proposed pricing"
    - "Value perception at each tier"
    - "Comparison to alternatives"
```

## Phase 4: Quality & Calibration

### Objectives
- Implement quality metrics and monitoring
- Build calibration pipeline against real data
- Add consistency validation

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| ConsistencyChecker | Validate persona trait alignment |
| BiasDetector | Identify sycophancy and clustering |
| VarianceMonitor | Track response distribution |
| CalibrationPipeline | Compare against real user baselines |
| Quality Dashboard | Metrics visualization |

### Quality Metrics Implementation

```python
class QualityMetrics:
    def consistency_score(self, persona, responses) -> float:
        """How well responses align with persona traits"""

    def sycophancy_rate(self, responses) -> float:
        """Percentage of unrealistically positive responses"""

    def variance_score(self, panel_responses) -> float:
        """Standard deviation compared to expected human variance"""

    def character_drift(self, persona, session_responses) -> float:
        """Deviation from initial persona over conversation"""
```

### Calibration Workflow

```
┌────────────────────┐
│ Real User Data     │
│ (baseline corpus)  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐     ┌────────────────────┐
│ Run Same Questions │────▶│ Synthetic Responses│
│ on Synthetic Panel │     │                    │
└────────────────────┘     └─────────┬──────────┘
                                     │
          ┌──────────────────────────┘
          │
          ▼
┌────────────────────┐
│ Compare & Analyze  │
│ • Response dist.   │
│ • Theme overlap    │
│ • Sentiment parity │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐     ┌────────────────────┐
│ Identify Gaps      │────▶│ Refine Personas    │
└────────────────────┘     └────────────────────┘
```

## Phase 5: Advanced Features

### Objectives
- Add sophisticated capabilities
- Support complex research scenarios
- Enable integration with external tools

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| MemorySystem | Long-term persona memory |
| PrototypeTesting | Test product mockups |
| A/B Research | Compare feature variants |
| APIEndpoints | External integration |
| WebInterface | Optional web UI |

### Memory Architecture

```
storage/
├── personas/
│   └── definitions/
├── memories/
│   └── {persona-id}/
│       ├── interactions.jsonl    # All past interactions
│       ├── insights.json         # Derived insights
│       └── preferences.json      # Learned preferences
└── sessions/
    └── {session-id}/
        ├── transcript.json
        └── analysis.json
```

### A/B Research Pattern

```
A/B Research Session:
├── Variant A: [Feature description A]
├── Variant B: [Feature description B]
├── Panel: [Same personas see both]
└── Output:
    ├── Preference split
    ├── Reasoning analysis
    └── Recommendation
```

## Milestone Summary

| Milestone | Key Outcome | Success Criteria | Status |
|-----------|-------------|------------------|--------|
| Phase 0 | Foundation complete | 5 personas, schema defined, CLI working | ✅ Complete |
| Phase 1 | Single persona works | Consistent, quality responses | 🔲 Next |
| Phase 2 | Panel research works | Parallel execution, aggregation | 🔲 Planned |
| Phase 3 | Multiple methods | Survey, interview, focus group | 🔲 Planned |
| Phase 4 | Quality assured | Calibration pipeline running | 🔲 Planned |
| Phase 5 | Production ready | Memory, integrations, scale | 🔲 Planned |

## Technical Dependencies

### Core Dependencies
- Claude Code CLI (subagent execution)
- Python 3.11+ (orchestration logic)
- PyYAML (configuration parsing)
- Rich (CLI formatting)

### Optional Dependencies
- SQLite/Redis (persistence layer)
- FastAPI (API endpoints - Phase 5)
- React (web UI - Phase 5)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Subagent consistency | Extensive prompt engineering, testing |
| Cost at scale | Model routing (Haiku for simple queries) |
| Response quality | Calibration pipeline, real user validation |
| Character drift | Session boundaries, prompt reinforcement |

## Success Metrics

| Metric | Target |
|--------|--------|
| Persona consistency | >90% trait alignment |
| Response quality | <30% sycophancy rate |
| Research throughput | 10 personas in <2 minutes |
| User satisfaction | >4/5 usefulness rating |

---

**Version**: 1.1.0 | **Created**: 2026-01-24 | **Updated**: 2026-01-25

### Changelog

- **1.1.0** (2026-01-25): Phase 0 Foundation completed - 78 tasks, 73 tests, 5 base personas
- **1.0.0** (2026-01-24): Initial roadmap created
