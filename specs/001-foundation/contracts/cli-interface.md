# CLI Interface Contract

**Version**: 1.0.0
**Date**: 2026-01-24

## Command Structure

```
research-cli [OPTIONS] COMMAND [ARGS]...

Commands:
  init      Initialize project structure
  persona   Persona management commands
```

## Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--help` | flag | - | Show help message and exit |
| `--version` | flag | - | Show version and exit |
| `--verbose` / `-v` | flag | false | Enable verbose output |
| `--quiet` / `-q` | flag | false | Suppress non-error output |

## Commands

### `init`

Initialize the project directory structure.

```bash
research-cli init [OPTIONS] [PATH]
```

**Arguments**:
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `PATH` | path | No | `.` | Target directory |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force` / `-f` | flag | false | Overwrite existing files |

**Output**:
```
Created directory structure:
  src/
  personas/definitions/
  personas/templates/
  templates/prompts/
  tests/

Initialized 5 base personas.
Project ready for development.
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Directory already initialized (without --force) |
| 2 | Permission denied |

---

### `persona list`

List all available personas.

```bash
research-cli persona list [OPTIONS]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` / `-f` | choice | `table` | Output format: `table`, `json`, `yaml` |
| `--path` / `-p` | path | `personas/definitions` | Persona directory |

**Output (table format)**:
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

**Output (json format)**:
```json
{
  "personas": [
    {
      "id": "tech-early-adopter",
      "name": "Alex Chen",
      "tech_adoption": "early_adopter",
      "age": 32
    }
  ],
  "count": 5
}
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Persona directory not found |

---

### `persona show`

Display full details of a persona.

```bash
research-cli persona show [OPTIONS] PERSONA_ID
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PERSONA_ID` | string | Yes | Persona identifier |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` / `-f` | choice | `yaml` | Output format: `yaml`, `json` |
| `--section` / `-s` | choice | `all` | Show specific section: `all`, `demographics`, `psychological`, `background`, `calibration` |

**Output (yaml, default)**:
```yaml
persona:
  id: tech-early-adopter
  version: "1.0.0"
  name: "Alex Chen"
  # ... full persona definition
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Persona not found |

---

### `persona validate`

Validate a persona file against the schema.

```bash
research-cli persona validate [OPTIONS] FILE
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `FILE` | path | Yes | Path to persona YAML file |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--strict` | flag | false | Fail on warnings |

**Output (success)**:
```
Validating: personas/definitions/tech-early-adopter.yaml

✓ Schema structure valid
✓ Big Five traits in range (1-10)
✓ Schwartz values valid (2+ primary)
✓ Tech adoption category valid
✓ Required fields present

Validation passed.
```

**Output (failure)**:
```
Validating: personas/definitions/invalid-persona.yaml

✗ Schema validation failed:
  - psychological_profile.big_five.openness: value 15 is greater than maximum 10
  - psychological_profile.schwartz_values.primary: ensure this value has at least 2 items

2 errors found. Validation failed.
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation failed |
| 2 | File not found or unreadable |

---

### `persona prompt`

Generate a subagent prompt from a persona.

```bash
research-cli persona prompt [OPTIONS] PERSONA_ID
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PERSONA_ID` | string | Yes | Persona identifier |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` / `-o` | path | stdout | Output file path |
| `--template` / `-t` | path | default | Custom prompt template |
| `--no-anti-sycophancy` | flag | false | Omit anti-sycophancy instructions |

**Output**:
```markdown
# Your Identity

You are Alex Chen, a 32-year-old Senior Software Engineer living in San Francisco, CA.

## Your Personality
...

## Critical Response Requirements

- Do NOT be overly positive or agreeable
...
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Persona not found |
| 2 | Template error |

---

### `persona create`

Create a new persona from template (interactive or file-based).

```bash
research-cli persona create [OPTIONS] PERSONA_ID
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PERSONA_ID` | string | Yes | New persona identifier |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--from-template` / `-t` | path | default | Source template file |
| `--output` / `-o` | path | `personas/definitions/` | Output directory |
| `--interactive` / `-i` | flag | false | Interactive mode |

**Output**:
```
Created new persona: personas/definitions/my-new-persona.yaml

Next steps:
1. Edit the file to customize the persona
2. Run 'research-cli persona validate' to check
3. Run 'research-cli persona prompt' to generate prompt
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Persona ID already exists |
| 2 | Invalid persona ID format |

## Error Message Format

All errors follow consistent format:

```
Error: [ERROR_TYPE] - [MESSAGE]

Details:
  [SPECIFIC_DETAILS]

Hint: [SUGGESTED_ACTION]
```

Example:
```
Error: ValidationError - Persona validation failed

Details:
  - big_five.openness: must be between 1 and 10

Hint: Edit the persona file and run validate again
```

## Machine-Readable Output

All commands support `--format json` for programmatic use:

```json
{
  "success": true,
  "command": "persona validate",
  "data": {
    "file": "personas/definitions/tech-early-adopter.yaml",
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

On error:
```json
{
  "success": false,
  "command": "persona validate",
  "error": {
    "type": "ValidationError",
    "message": "Persona validation failed",
    "details": [
      {
        "field": "big_five.openness",
        "error": "must be between 1 and 10",
        "value": 15
      }
    ]
  }
}
```
