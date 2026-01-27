# Quickstart Guide: Research Methods

**Feature**: 004-research-methods
**Date**: 2026-01-26

## Overview

This guide helps developers quickly get started implementing Survey, Interview, and Focus Group research methods for the Synthetic User Research Platform.

---

## Prerequisites

Before implementing this feature, ensure you understand:

1. **Existing Infrastructure** (from Phase 0/1/2):
   - `src/models/persona.py` - Persona schema with Big Five and Schwartz values
   - `src/models/session.py` - Session models and status enums
   - `src/services/session_runner.py` - Single persona execution
   - `src/services/panel_executor.py` - Parallel panel execution with asyncio
   - `src/services/response_parser.py` - Response parsing patterns
   - `src/cli/panel_commands.py` - CLI command patterns with Rich output

2. **Key Dependencies**:
   ```bash
   pip install pyyaml pydantic click jinja2 rich pytest pytest-asyncio
   ```

3. **Test Coverage Requirements**:
   - Run existing tests: `pytest tests/`
   - Current coverage: 239 tests passing

---

## Implementation Order

Follow this order to minimize dependencies between components:

### Phase 1: Survey Engine (P1 Priority)

```
1. src/models/enums.py          # Add ResearchMethodType, SurveyQuestionType
2. src/models/survey.py         # Survey, SurveyQuestion, SurveyResponse models
3. tests/unit/test_survey_model.py

4. src/services/survey_engine.py      # SurveyEngine class
5. src/services/survey_aggregator.py  # Statistical aggregation
6. tests/unit/test_survey_engine.py
7. tests/unit/test_survey_aggregator.py

8. src/templates/survey_prompt.j2     # Survey question prompt
9. src/templates/survey_report.j2     # Survey results report

10. src/cli/survey_commands.py        # survey run/create commands
11. tests/integration/test_survey_cli.py
```

### Phase 2: Protocol Management (P2 Priority)

```
1. src/models/protocol.py              # ResearchProtocol base and variants
2. tests/unit/test_protocol_model.py

3. src/services/protocol_loader.py     # Load/save/validate protocols
4. tests/unit/test_protocol_loader.py

5. protocols/                          # Directory structure
   ├── surveys/sample-survey.yaml
   ├── interviews/sample-interview.yaml
   └── focus-groups/sample-focus-group.yaml

6. src/cli/protocol_commands.py        # protocol list/show/delete
7. tests/contract/test_protocol_schema.py
```

### Phase 3: Interview Engine (P2 Priority)

```
1. src/models/interview.py             # InterviewGuide, Section, Transcript
2. tests/unit/test_interview_model.py

3. src/services/interview_engine.py    # InterviewEngine with follow-ups
4. tests/unit/test_interview_engine.py

5. src/templates/interview_prompt.j2   # Interview section prompt
6. src/templates/interview_report.j2   # Transcript report

7. src/cli/interview_commands.py       # interview run/create
8. tests/integration/test_interview_cli.py
```

### Phase 4: Focus Group Engine (P3 Priority)

```
1. src/models/focus_group.py           # FocusGroup, Turn, DiscussionLog
2. tests/unit/test_focus_group_model.py

3. src/services/focus_group_engine.py  # FocusGroupEngine turn-taking
4. tests/unit/test_focus_group_engine.py

5. src/templates/focus_group_prompt.j2 # Turn execution prompt
6. src/templates/focus_group_report.j2 # Discussion report

7. src/cli/focus_group_commands.py     # focus-group run/create
8. tests/integration/test_focus_group_cli.py
```

---

## Quick Reference: Key Patterns

### Pattern 1: Pydantic Model with Validators

```python
# src/models/survey.py
from pydantic import BaseModel, Field, field_validator, model_validator

class SurveyQuestion(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    text: str = Field(..., min_length=1, max_length=500)
    type: SurveyQuestionType
    scale_min: int | None = Field(default=None, ge=1, le=10)
    scale_max: int | None = Field(default=None, ge=1, le=10)

    @model_validator(mode='after')
    def validate_rating_fields(self) -> 'SurveyQuestion':
        if self.type == SurveyQuestionType.RATING:
            if self.scale_min is None or self.scale_max is None:
                raise ValueError("Rating questions require scale bounds")
        return self
```

### Pattern 2: Engine with Dependency Injection

```python
# src/services/survey_engine.py
from src.services.session_runner import SessionRunner
from src.services.prompt_builder import PromptBuilder

class SurveyEngine:
    def __init__(
        self,
        session_runner: SessionRunner | None = None,
        prompt_builder: PromptBuilder | None = None
    ):
        self.session_runner = session_runner or SessionRunner()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def execute_survey(self, survey: Survey, persona_id: str) -> SurveyResult:
        # Build persona prompt
        persona = self.session_runner.persona_loader.load(persona_id)
        persona_prompt = self.prompt_builder.build_prompt(persona)

        responses = []
        for question in survey.questions:
            prompt = self._build_question_prompt(persona_prompt, question)
            response = self._execute_question(prompt)
            parsed = self._parse_response(question, response)
            responses.append(parsed)

        return SurveyResult(
            survey_id=survey.id,
            persona_id=persona_id,
            responses=responses
        )
```

### Pattern 3: CLI Command with Rich Output

```python
# src/cli/survey_commands.py
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.group(name="survey")
def survey_group():
    """Survey research commands."""
    pass

@survey_group.command(name="run")
@click.option("--protocol", "-p", required=True, help="Survey protocol ID")
@click.option("--persona", help="Single persona ID")
@click.option("--panel", help="Panel ID for multi-persona survey")
@click.option("--output", "-o", type=click.Path(), help="Export JSON path")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def run_survey(protocol, persona, panel, output, format):
    """Execute a survey protocol."""
    from src.services.survey_engine import SurveyEngine
    from src.services.protocol_loader import ProtocolLoader

    # Load protocol
    loader = ProtocolLoader()
    survey = loader.load_survey(protocol)

    # Execute
    engine = SurveyEngine()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Running survey...", total=len(survey.questions))
        # ... execution logic
```

### Pattern 4: Jinja2 Template for Prompts

```jinja2
{# src/templates/survey_prompt.j2 #}
{{ persona_prompt }}

---

## Survey Question {{ question_number }} of {{ total_questions }}

{{ question.text }}

{% if question.type == "rating" %}
Please provide a rating from {{ question.scale_min }} to {{ question.scale_max }}.
{% if question.scale_labels %}
Scale:
{% for value, label in question.scale_labels.items() %}
- {{ value }}: {{ label }}
{% endfor %}
{% endif %}

Respond with your rating number followed by a brief explanation.
{% elif question.type == "multiple_choice" %}
Choose one of the following options:
{% for option in question.options %}
- {{ option }}
{% endfor %}

Respond with your chosen option followed by your reasoning.
{% else %}
Please provide your detailed thoughts.
{% endif %}

---

Remember to respond authentically as {{ persona_name }}, considering your personality traits, values, and experiences.
```

### Pattern 5: Async Panel Execution (for surveys)

```python
# Reuse existing PanelExecutor pattern
async def execute_panel_survey(
    self,
    survey: Survey,
    panel_id: str,
    progress_callback: Callable | None = None
) -> list[SurveyResult]:
    panel = self.panel_loader.load_by_id(panel_id)

    async def execute_one(persona_id: str) -> SurveyResult:
        return self.execute_survey(survey, persona_id)

    semaphore = asyncio.Semaphore(self.max_concurrent)

    async def bounded_execute(persona_id: str) -> SurveyResult:
        async with semaphore:
            result = await asyncio.to_thread(execute_one, persona_id)
            if progress_callback:
                progress_callback(persona_id)
            return result

    tasks = [bounded_execute(pid) for pid in panel.persona_ids]
    return await asyncio.gather(*tasks)
```

---

## Directory Setup

Create these directories before starting implementation:

```bash
# Protocol storage
mkdir -p protocols/surveys
mkdir -p protocols/interviews
mkdir -p protocols/focus-groups

# New test directories (if not existing)
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/contract
```

---

## Sample Protocol Files

### `protocols/surveys/sample-survey.yaml`

```yaml
protocol:
  id: sample-survey
  version: "1.0.0"
  type: survey
  name: "Sample Feature Survey"
  description: "A sample survey for testing"

survey:
  id: sample-survey
  version: "1.0.0"
  name: "Sample Feature Survey"
  questions:
    - id: q1-rating
      text: "How likely are you to recommend this feature?"
      type: rating
      scale_min: 1
      scale_max: 10

    - id: q2-choice
      text: "What best describes your reaction?"
      type: multiple_choice
      options:
        - "Excited"
        - "Interested"
        - "Neutral"
        - "Skeptical"

    - id: q3-open
      text: "What improvements would you suggest?"
      type: open_ended
```

---

## Testing Commands

```bash
# Run all tests
pytest tests/

# Run only new feature tests
pytest tests/unit/test_survey_model.py tests/unit/test_survey_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test
pytest tests/unit/test_survey_engine.py::test_execute_survey_with_rating -v
```

---

## Common Gotchas

1. **Persona ID validation**: All persona IDs must be kebab-case and exist in `personas/definitions/`

2. **YAML parsing**: Use `yaml.safe_load()` for security; wrap in try/except for user-friendly errors

3. **Async context**: When using PanelExecutor for surveys, ensure you're in async context or use `asyncio.run()`

4. **Template loading**: Jinja2 templates should be loaded via `importlib.resources` or absolute paths

5. **Quality metrics reuse**: Always call existing `QualityMetricsCalculator` for consistency scores

---

## Next Steps After Implementation

1. Run full test suite: `pytest tests/`
2. Verify CLI help: `research-cli research survey --help`
3. Test with sample protocol: `research-cli research survey run -p sample-survey --persona tech-early-adopter`
4. Generate coverage report: `pytest --cov=src --cov-report=html`
5. Update CLAUDE.md with new technologies if any
