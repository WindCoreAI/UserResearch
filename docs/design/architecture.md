# Synthetic User Research Platform Architecture

## Overview

This document defines the architecture for a synthetic user research platform that leverages Claude Code subagents to simulate diverse user personas. The system enables rapid, scalable user research by orchestrating multiple AI agents that embody different psychological profiles, demographics, and behavioral patterns.

## Core Architecture Principles

### 1. Subagent-Centric Design

The platform is built around Claude Code's multi-agent capabilities, where each synthetic user is represented by a specialized subagent with:

- **Persistent persona context**: Maintained across research sessions
- **Behavioral consistency**: Enforced through psychological frameworks
- **Independent reasoning**: Each agent processes questions through their unique worldview

### 2. Layered Persona Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Orchestrator                     │
│              (Coordinates research sessions)                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Persona Manager                           │
│         (Creates, stores, retrieves persona configs)         │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Persona A   │   │   Persona B   │   │   Persona C   │
│  (Subagent)   │   │  (Subagent)   │   │  (Subagent)   │
│               │   │               │   │               │
│ Demographics  │   │ Demographics  │   │ Demographics  │
│ Personality   │   │ Personality   │   │ Personality   │
│ Values        │   │ Values        │   │ Values        │
│ Context       │   │ Context       │   │ Context       │
└───────────────┘   └───────────────┘   └───────────────┘
```

## System Components

### 1. Research Orchestrator

The central coordinator that:

- Receives research requests (surveys, interviews, focus groups)
- Selects appropriate personas based on research criteria
- Spawns and manages subagents in parallel
- Aggregates and analyzes responses
- Generates research reports

**Implementation**: Claude Code Task tool with `subagent_type=general-purpose`

### 2. Persona Manager

Responsible for:

- Storing persona definitions in structured format (YAML/JSON)
- Versioning persona configurations
- Providing persona retrieval APIs
- Ensuring persona diversity and coverage

**Storage Structure**:
```
personas/
├── definitions/
│   ├── innovator-tech-professional.yaml
│   ├── skeptical-late-adopter.yaml
│   └── spiritual-seeker.yaml
├── templates/
│   ├── base-persona.yaml
│   └── psychological-traits.yaml
└── panels/
    ├── general-population.yaml
    └── tech-early-adopters.yaml
```

### 3. Persona Subagents

Each persona is instantiated as a Claude Code subagent with:

**Context Components**:
1. **System Prompt**: Core persona identity and behavioral guidelines
2. **Psychological Profile**: Big Five traits, Schwartz values
3. **Demographic Context**: Age, occupation, location, life stage
4. **Domain Knowledge**: Relevant experience and expertise
5. **Response Calibration**: Anti-sycophancy instructions, variance guidelines

### 4. Response Analyzer

Post-processing component that:

- Extracts key themes across responses
- Identifies consensus and divergence patterns
- Detects potential bias or unrealistic clustering
- Generates quantitative and qualitative summaries

## Data Flow

```
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│   Research   │────▶│  Orchestrator │────▶│ Persona Manager │
│   Request    │     │               │     │                 │
└──────────────┘     └───────┬───────┘     └────────┬────────┘
                             │                      │
                             │  Spawn Subagents     │ Load Configs
                             ▼                      ▼
                    ┌────────────────────────────────────────┐
                    │          Parallel Execution            │
                    │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐   │
                    │  │ P1  │  │ P2  │  │ P3  │  │ Pn  │   │
                    │  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘   │
                    └─────┼───────┼───────┼───────┼────────┘
                          │       │       │       │
                          ▼       ▼       ▼       ▼
                    ┌────────────────────────────────────────┐
                    │         Response Aggregation           │
                    └──────────────────┬─────────────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────────────────┐
                    │           Research Report              │
                    └────────────────────────────────────────┘
```

## Subagent Implementation Strategy

### Using Claude Code Task Tool

Each persona is executed via the Task tool with specific configuration:

```python
# Pseudocode for orchestrator logic
def run_interview(persona_config, questions):
    return Task(
        subagent_type="general-purpose",
        prompt=f"""
        You are {persona_config.name}, embodying the following characteristics:

        ## Demographics
        {persona_config.demographics}

        ## Psychological Profile
        - Big Five: {persona_config.big_five}
        - Values: {persona_config.values}

        ## Background
        {persona_config.background}

        ## Response Guidelines
        - Stay in character throughout
        - Express genuine uncertainty and mixed feelings
        - Avoid unrealistic positivity
        - Draw from your defined experiences

        ## Interview Questions
        {questions}

        Respond as this persona would, maintaining consistency
        with your psychological profile and life experiences.
        """,
        model="sonnet"  # or "haiku" for cost efficiency
    )
```

### Parallel Execution Pattern

For panel research with multiple personas:

```python
# Execute multiple personas in parallel
def run_panel_research(panel_personas, research_protocol):
    tasks = []
    for persona in panel_personas:
        tasks.append(Task(
            subagent_type="general-purpose",
            prompt=build_persona_prompt(persona, research_protocol),
            run_in_background=True
        ))

    # Aggregate results
    results = [TaskOutput(task_id=t.id) for t in tasks]
    return analyze_responses(results)
```

## Memory and Consistency Architecture

### Short-Term Memory (Session)
- Conversation context within a single research session
- Maintained automatically by subagent

### Long-Term Memory (Persona)
- Stored persona definitions
- Previous research participation history
- Learned preferences and refined characteristics

### Implementation
```
storage/
├── personas/           # Persona definitions
├── sessions/           # Research session logs
├── memories/           # Persona-specific memories
│   ├── persona-001/
│   │   ├── interactions.json
│   │   └── insights.json
└── reports/            # Generated research reports
```

## Quality Assurance Mechanisms

### 1. Persona Consistency Validation
- Cross-reference responses against defined traits
- Flag responses that deviate from persona profile
- Track consistency scores over time

### 2. Anti-Sycophancy Measures
- Explicit instructions to express criticism
- Include "devil's advocate" personas in panels
- Monitor positive/negative response ratios

### 3. Variance Monitoring
- Compare response distribution to expected human variance
- Alert when responses cluster too tightly
- Inject diversity-promoting prompts when needed

### 4. Calibration Pipeline
```
Real User Data ─┬─▶ Calibration ─┬─▶ Synthetic Personas
                │   Benchmark    │
                │                ▼
                │         Accuracy Metrics
                │                │
                └────────────────┘
                   Feedback Loop
```

## Integration Points

### Input Sources
- Survey definitions (JSON/YAML)
- Interview scripts
- Focus group discussion guides
- Product prototypes/descriptions

### Output Formats
- Research reports (Markdown, PDF)
- Quantitative summaries (JSON, CSV)
- Verbatim transcripts
- Theme analysis visualizations

### External Integrations
- Version control (Git) for persona versioning
- CI/CD for automated research pipelines
- Dashboard for research management

## Security and Ethics

### Data Handling
- No real user PII in persona definitions
- Clear labeling of synthetic vs. real data
- Audit trails for all research sessions

### Ethical Guidelines
- Never present synthetic data as real user research
- Always disclose AI-generated nature of insights
- Use hybrid validation for high-stakes decisions
- Maintain clear documentation of limitations

## Performance Considerations

### Scalability
- Parallel subagent execution for panel research
- Batch processing for large-scale surveys
- Caching of common persona configurations

### Cost Optimization
- Model selection based on task complexity
- Prompt caching for repeated research patterns
- Background execution for non-urgent research

---

**Version**: 1.0.0 | **Created**: 2026-01-24
