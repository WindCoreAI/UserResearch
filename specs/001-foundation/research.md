# Research: Phase 0 Foundation

**Date**: 2026-01-24
**Feature**: Phase 0 Foundation
**Purpose**: Document technology decisions and best practices research

## Technology Decisions

### 1. Programming Language: Python 3.11+

**Decision**: Use Python 3.11+ as the primary implementation language.

**Rationale**:
- Excellent YAML parsing ecosystem (PyYAML, ruamel.yaml)
- Pydantic provides robust schema validation with clear error messages
- Click is the de-facto standard for building modern CLIs
- Jinja2 templating is battle-tested for text generation
- Fast iteration speed for a prototype/foundation phase
- Wide adoption in AI/ML tooling aligns with project domain

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| TypeScript/Node | Less mature YAML tooling; async complexity for simple CLI |
| Go | Faster runtime but slower development; less flexible templating |
| Rust | Over-engineered for Phase 0 foundation work |

### 2. Schema Validation: Pydantic v2

**Decision**: Use Pydantic v2 for persona schema definition and validation.

**Rationale**:
- Declarative model definition matches YAML structure naturally
- Built-in validation with descriptive error messages
- JSON Schema export for documentation and cross-language compatibility
- Type hints provide IDE support and documentation
- v2 offers significant performance improvements over v1

**Best Practices Applied**:
- Use `Field()` with descriptions for self-documenting schemas
- Define custom validators for domain rules (e.g., Big Five range 1-10)
- Use enums for constrained values (tech adoption, Schwartz values)
- Export JSON Schema for persona template documentation

### 3. CLI Framework: Click

**Decision**: Use Click for command-line interface implementation.

**Rationale**:
- Decorator-based API is clean and composable
- Built-in support for subcommands, options, arguments
- Automatic help generation
- Testing utilities (CliRunner) for integration tests
- Rich ecosystem (click-extra for colors, tables)

**CLI Command Structure**:
```
research-cli
├── persona
│   ├── list         # List all personas
│   ├── show <id>    # Show persona details
│   ├── validate     # Validate persona file
│   └── prompt <id>  # Generate subagent prompt
└── init             # Initialize project structure
```

### 4. Templating: Jinja2

**Decision**: Use Jinja2 for subagent prompt generation.

**Rationale**:
- Industry standard for text templating in Python
- Supports template inheritance for composable prompts
- Filters and macros enable complex transformations
- Whitespace control for clean prompt output
- Well-documented with extensive examples

**Template Design Patterns**:
- Base template with common structure (identity, guidelines)
- Partial templates for reusable sections (anti-sycophancy)
- Variables for persona-specific content
- Conditional blocks for optional sections

### 5. Storage: File-based YAML

**Decision**: Store personas as individual YAML files in a dedicated directory.

**Rationale**:
- Human-readable and editable without special tools
- Git-friendly for version control
- No database setup required for Phase 0
- Easy to browse and inspect
- Standard format with wide tooling support

**Directory Structure**:
```
personas/
├── definitions/     # Actual persona files
│   └── *.yaml
└── templates/       # Blank templates for creation
    └── persona-template.yaml
```

### 6. Testing: pytest

**Decision**: Use pytest as the testing framework.

**Rationale**:
- De-facto standard for Python testing
- Fixture system for test setup/teardown
- Parametrized tests for schema validation edge cases
- click.testing.CliRunner integration
- pytest-cov for coverage reporting

**Test Categories**:
| Category | Purpose | Location |
|----------|---------|----------|
| Unit | Model validation, service logic | tests/unit/ |
| Integration | CLI commands end-to-end | tests/integration/ |
| Contract | Schema stability, backward compatibility | tests/contract/ |

## Psychological Framework Research

### Big Five (OCEAN) Model

**Decision**: Implement Big Five as primary personality framework with 1-10 integer scale.

**Research Findings**:
- Most validated personality model in psychology research
- GPT and Claude models show consistent alignment with assigned Big Five traits
- Linguistic analysis shows LLM word choice patterns correlate with traits
- Binary trait assignment produces statistically significant behavioral differences

**Implementation**:
- Five required fields: openness, conscientiousness, extraversion, agreeableness, neuroticism
- Scale 1-10 for granularity (research shows meaningful differentiation)
- Include behavioral implications in prompt generation

### Schwartz Values Framework

**Decision**: Require minimum 2 Schwartz values from the 10 universal values.

**Research Findings**:
- 10 values validated across 82+ countries
- Adjacent values on circumplex are compatible; opposite values conflict
- Value conflicts create realistic behavioral tension

**Implementation**:
- Enum of 10 values: self_direction, stimulation, hedonism, achievement, power, security, conformity, tradition, benevolence, universalism
- Primary values (2+ required) and secondary values (optional)
- Optional conflict descriptions for nuanced personas

### Technology Adoption (Rogers)

**Decision**: Include Rogers' Diffusion of Innovation categories.

**Research Findings**:
- Five categories with known population distributions
- Different categories have predictable friction points
- Essential for product testing personas

**Implementation**:
- Enum: innovator, early_adopter, early_majority, late_majority, laggard
- Required field for all personas
- Category-specific behavioral notes in prompt

## Anti-Sycophancy Research

**Decision**: Embed explicit anti-sycophancy instructions in all generated prompts.

**Research Findings**:
- LLMs exhibit systematic positive bias in feedback
- Synthetic users consistently provide overly agreeable responses
- 100% of synthetic personas may choose positive options in some studies
- Cannot replicate authentic frustration or genuine criticism without guidance

**Implementation Strategy**:
1. Explicit instructions to avoid unrealistic positivity
2. Directive to express skepticism when warranted
3. Permission to say "no" or "I wouldn't use this"
4. Guidance to challenge assumptions in questions
5. Include frustration and confusion in emotional repertoire

**Template Section**:
```markdown
## Critical Response Requirements

- Do NOT be overly positive or agreeable
- Express skepticism when something seems too good
- Point out potential problems and concerns
- Say "no" or "I wouldn't use this" when it fits your persona
- Challenge assumptions in questions
- Express frustration, confusion, and indifference naturally
```

## No Unresolved Clarifications

All technical decisions have been made. No NEEDS CLARIFICATION items remain.
