# Synthetic User Research Platform

A platform that uses Claude Code subagents to simulate diverse user personas for rapid, scalable user research. Run surveys, interviews, and focus groups with AI-powered synthetic users that embody realistic psychological profiles.

## Overview

This platform enables product teams to:
- **Validate concepts quickly** - Get feedback from 10+ synthetic users in minutes
- **Test edge cases safely** - Simulate vulnerable users and crisis scenarios
- **Generate hypotheses** - Explore user needs before investing in real research

## Key Features

- **Subagent-based simulation**: Each persona runs as an independent Claude Code subagent
- **Psychological frameworks**: Big Five personality traits, Schwartz values, tech adoption profiles
- **Multiple research methods**: Surveys, interviews, and focus groups
- **Quality calibration**: Anti-sycophancy measures and variance monitoring

## Documentation

### Design Documents
- [Architecture](docs/design/architecture.md) - System components and data flow
- [Persona System](docs/design/persona-system.md) - Psychological frameworks and persona schema
- [User Experience](docs/design/user-experience.md) - CLI interaction patterns and output formats

### Planning
- [Development Roadmap](docs/roadmap/development-roadmap.md) - Phased implementation plan
- [Research Report](docs/research/user_research_status.md) - Background research on synthetic user methodologies

### Project Governance
- [Constitution](.specify/memory/constitution.md) - Core principles and standards

## Quick Start

```bash
# Quick concept validation
> research "daily reflection feature for productivity app"

# Run a survey panel
> survey --panel="tech-early-adopters" --questions="survey.yaml"

# Conduct deep interviews
> interview --persona="skeptical-user" --topic="onboarding"

# Simulate focus group
> focus-group --size=6 --topic="new pricing model"
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Research Orchestrator                   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│               Persona Manager                        │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│   │Persona A│  │Persona B│  │Persona C│  ...       │
│   │(Subagent│  │(Subagent│  │(Subagent│            │
│   └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│           Response Aggregation & Reporting          │
└─────────────────────────────────────────────────────┘
```

## Limitations

Synthetic user research has known constraints:
- **Sycophancy bias**: Tends toward overly positive feedback
- **Variance reduction**: Narrower opinion range than real users
- **No authentic experience**: Cannot access real behavioral history

**Always validate critical findings with real users.**

## License

[License information]
