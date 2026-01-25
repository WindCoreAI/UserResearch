# Quickstart: Phase 0 Foundation

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

## Installation

### 1. Clone and Setup

```bash
# Navigate to the project
cd UserResearch

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Initialize Project Structure

```bash
# Initialize the directory structure and base personas
research-cli init

# Verify initialization
research-cli persona list
```

Expected output:
```
ID                        NAME              ADOPTION        AGE
------------------------  ----------------  --------------  ----
tech-early-adopter        Alex Chen         early_adopter   32
skeptical-late-adopter    Margaret Wilson   late_majority   58
busy-professional         David Park        early_majority  42
privacy-conscious-user    Sarah Martinez    late_majority   35
power-user                Jamie Thompson    innovator       27

5 personas found
```

## Basic Usage

### View a Persona

```bash
# Show full persona details
research-cli persona show tech-early-adopter

# Show specific section
research-cli persona show tech-early-adopter --section psychological
```

### Validate a Persona

```bash
# Validate an existing persona
research-cli persona validate personas/definitions/tech-early-adopter.yaml

# Validate with strict mode (warnings become errors)
research-cli persona validate --strict personas/definitions/my-persona.yaml
```

### Generate Subagent Prompt

```bash
# Generate prompt to stdout
research-cli persona prompt tech-early-adopter

# Save prompt to file
research-cli persona prompt tech-early-adopter -o prompts/alex-chen.md
```

### Create New Persona

```bash
# Create from template
research-cli persona create my-new-persona

# Interactive mode
research-cli persona create my-new-persona --interactive
```

## Creating a Custom Persona

### 1. Copy the Template

```bash
cp personas/templates/persona-template.yaml personas/definitions/my-researcher.yaml
```

### 2. Edit the Persona

Open `personas/definitions/my-researcher.yaml` and fill in:

```yaml
persona:
  id: my-researcher
  version: "1.0.0"
  name: "Dr. Emily Watson"

  demographics:
    age: 45
    gender: "female"
    location: "Boston, MA"
    occupation:
      title: "Research Scientist"
      industry: "Biotech"
      years_experience: 20

  psychological_profile:
    big_five:
      openness: 9        # Very curious and creative
      conscientiousness: 8  # Highly organized
      extraversion: 4    # More introverted
      agreeableness: 6   # Moderately cooperative
      neuroticism: 5     # Balanced emotional stability

    schwartz_values:
      primary:
        - self_direction  # Values independence
        - universalism    # Cares about broader impact
      secondary:
        - achievement

    tech_adoption: early_majority  # Waits for proof

  background:
    life_stage: "Senior researcher considering industry move"
    pain_points:
      - "Academic bureaucracy slows research"
      - "Difficulty translating research to practice"
    goals:
      - "Make research more accessible"
      - "Find tools that don't require IT support"

  response_calibration:
    verbosity: detailed
    emotional_expressiveness: reserved
    criticism_tendency: critical
```

### 3. Validate and Generate

```bash
# Validate the new persona
research-cli persona validate personas/definitions/my-researcher.yaml

# Generate the subagent prompt
research-cli persona prompt my-researcher
```

## Project Structure Reference

After initialization:

```
UserResearch/
├── src/                          # Source code
│   ├── models/                   # Pydantic data models
│   ├── services/                 # Business logic
│   ├── cli/                      # CLI commands
│   └── templates/                # Jinja2 templates
├── personas/
│   ├── definitions/              # Persona YAML files
│   │   ├── tech-early-adopter.yaml
│   │   ├── skeptical-late-adopter.yaml
│   │   ├── busy-professional.yaml
│   │   ├── privacy-conscious-user.yaml
│   │   └── power-user.yaml
│   └── templates/
│       └── persona-template.yaml # Blank template
├── templates/
│   └── prompts/
│       └── anti-sycophancy.md    # Anti-sycophancy instructions
└── tests/                        # Test suite
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_persona_model.py

# Run tests matching a pattern
pytest -k "validation"
```

## Common Issues

### "Persona not found"

Check that:
1. The persona ID matches the file name (without `.yaml`)
2. The file is in `personas/definitions/`
3. The `id` field in the YAML matches the filename

### "Validation failed: big_five.X must be between 1 and 10"

All Big Five traits must be integers from 1 to 10:
- 1-3: Low
- 4-6: Medium
- 7-10: High

### "Validation failed: schwartz_values.primary must have at least 2 items"

The `primary` list under `schwartz_values` must contain at least 2 values from:
- self_direction, stimulation, hedonism, achievement, power
- security, conformity, tradition, benevolence, universalism

## Next Steps

After Phase 0 foundation is complete:

1. **Phase 1**: Use personas for single-session research with `research-cli research`
2. **Phase 2**: Create panels for multi-persona research
3. **Phase 3**: Run surveys, interviews, and focus groups

See [Development Roadmap](../../docs/roadmap/development-roadmap.md) for the full plan.
