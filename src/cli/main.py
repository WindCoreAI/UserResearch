"""CLI entry point for research-cli.

Provides commands for persona management, validation, and prompt generation.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from services.persona_loader import PersonaLoader

# Default paths
DEFAULT_PERSONAS_DIR = Path("personas/definitions")
DEFAULT_TEMPLATES_DIR = Path("personas/templates")


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.version_option(version="0.1.0", prog_name="research-cli")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Synthetic User Research Platform - Persona Management CLI."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@cli.group()
def persona() -> None:
    """Manage personas - validate, list, show, and generate prompts."""
    pass


@persona.command("validate")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def persona_validate(
    ctx: click.Context, file_path: str, strict: bool, output_json: bool
) -> None:
    """Validate a persona YAML file against the schema."""
    loader = PersonaLoader()
    result = loader.validate(file_path)

    if output_json:
        output = {
            "file": file_path,
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        if result.is_valid:
            if not ctx.obj.get("quiet"):
                click.echo(click.style(f"✓ {file_path} is valid", fg="green"))
        else:
            click.echo(click.style(f"✗ {file_path} validation failed:", fg="red"))
            for error in result.errors:
                click.echo(f"  - {error}")

    if not result.is_valid:
        sys.exit(1)


@persona.command("list")
@click.option(
    "--dir",
    "personas_dir",
    type=click.Path(exists=True),
    default=None,
    help="Directory containing persona files",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.pass_context
def persona_list(
    ctx: click.Context, personas_dir: Optional[str], output_format: str
) -> None:
    """List all available personas."""
    from services.persona_library import PersonaLibrary

    library = PersonaLibrary(
        personas_dir=Path(personas_dir) if personas_dir else DEFAULT_PERSONAS_DIR
    )
    personas = library.list_all()

    if not personas:
        if output_format == "json":
            click.echo(json.dumps({"personas": [], "count": 0}))
        else:
            click.echo("No personas found. Run 'research-cli init' to create base personas.")
        return

    if output_format == "json":
        output = {
            "personas": [
                {
                    "id": p.id,
                    "name": p.name,
                    "tech_adoption": p.psychological_profile.tech_adoption.value,
                    "age": p.demographics.age,
                }
                for p in personas
            ],
            "count": len(personas),
        }
        click.echo(json.dumps(output, indent=2))
    elif output_format == "yaml":
        output = [
            {
                "id": p.id,
                "name": p.name,
                "tech_adoption": p.psychological_profile.tech_adoption.value,
                "age": p.demographics.age,
            }
            for p in personas
        ]
        click.echo(yaml.dump(output, default_flow_style=False))
    else:
        # Table format
        click.echo(f"{'ID':<25} {'NAME':<20} {'ADOPTION':<15} {'AGE':>4}")
        click.echo("-" * 68)
        for p in personas:
            click.echo(
                f"{p.id:<25} {p.name:<20} "
                f"{p.psychological_profile.tech_adoption.value:<15} {p.demographics.age:>4}"
            )
        click.echo(f"\n{len(personas)} personas found")


@persona.command("show")
@click.argument("persona_id")
@click.option(
    "--dir",
    "personas_dir",
    type=click.Path(exists=True),
    default=None,
    help="Directory containing persona files",
)
@click.option(
    "--section",
    type=click.Choice(["demographics", "psychological", "background", "calibration", "all"]),
    default="all",
    help="Show specific section only",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def persona_show(
    ctx: click.Context,
    persona_id: str,
    personas_dir: Optional[str],
    section: str,
    output_json: bool,
) -> None:
    """Show details of a specific persona."""
    from services.persona_library import PersonaLibrary

    library = PersonaLibrary(
        personas_dir=Path(personas_dir) if personas_dir else DEFAULT_PERSONAS_DIR
    )

    try:
        persona = library.get_by_id(persona_id)
    except FileNotFoundError:
        click.echo(click.style(f"Persona not found: {persona_id}", fg="red"), err=True)
        sys.exit(1)

    if output_json:
        data = persona.model_dump()
        if section != "all":
            section_map = {
                "demographics": "demographics",
                "psychological": "psychological_profile",
                "background": "background",
                "calibration": "response_calibration",
            }
            data = {section: data.get(section_map.get(section, section))}
        click.echo(json.dumps(data, indent=2, default=str))
        return

    # Human-readable output
    click.echo(f"\n{click.style(persona.name, bold=True)} ({persona.id})")
    click.echo(f"Version: {persona.version}\n")

    if section in ("all", "demographics"):
        d = persona.demographics
        click.echo(click.style("Demographics:", bold=True))
        click.echo(f"  Age: {d.age}")
        click.echo(f"  Gender: {d.gender}")
        click.echo(f"  Location: {d.location}")
        click.echo(f"  Occupation: {d.occupation.title}")
        if d.occupation.industry:
            click.echo(f"  Industry: {d.occupation.industry}")
        click.echo()

    if section in ("all", "psychological"):
        p = persona.psychological_profile
        click.echo(click.style("Psychological Profile:", bold=True))
        click.echo("  Big Five:")
        click.echo(f"    Openness: {p.big_five.openness}/10")
        click.echo(f"    Conscientiousness: {p.big_five.conscientiousness}/10")
        click.echo(f"    Extraversion: {p.big_five.extraversion}/10")
        click.echo(f"    Agreeableness: {p.big_five.agreeableness}/10")
        click.echo(f"    Neuroticism: {p.big_five.neuroticism}/10")
        click.echo(f"  Values: {', '.join(v.value for v in p.schwartz_values.primary)}")
        click.echo(f"  Tech Adoption: {p.tech_adoption.value}")
        click.echo()

    if section in ("all", "background"):
        b = persona.background
        click.echo(click.style("Background:", bold=True))
        click.echo(f"  Life Stage: {b.life_stage}")
        if b.pain_points:
            click.echo("  Pain Points:")
            for pp in b.pain_points:
                click.echo(f"    - {pp}")
        if b.goals:
            click.echo("  Goals:")
            for g in b.goals:
                click.echo(f"    - {g}")
        click.echo()

    if section in ("all", "calibration"):
        r = persona.response_calibration
        click.echo(click.style("Response Calibration:", bold=True))
        click.echo(f"  Verbosity: {r.verbosity.value}")
        click.echo(f"  Expressiveness: {r.emotional_expressiveness.value}")
        click.echo(f"  Criticism: {r.criticism_tendency.value}")
        if r.certainty_level:
            click.echo(f"  Certainty: {r.certainty_level.value}")


@persona.command("prompt")
@click.argument("persona_id")
@click.option(
    "--dir",
    "personas_dir",
    type=click.Path(exists=True),
    default=None,
    help="Directory containing persona files",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(),
    default=None,
    help="Save prompt to file",
)
@click.option(
    "--template",
    "template_path",
    type=click.Path(exists=True),
    default=None,
    help="Custom Jinja2 template for prompt generation",
)
@click.pass_context
def persona_prompt(
    ctx: click.Context,
    persona_id: str,
    personas_dir: Optional[str],
    output_file: Optional[str],
    template_path: Optional[str],
) -> None:
    """Generate a subagent prompt for a persona."""
    from services.persona_library import PersonaLibrary
    from services.prompt_builder import PromptBuilder

    library = PersonaLibrary(
        personas_dir=Path(personas_dir) if personas_dir else DEFAULT_PERSONAS_DIR
    )

    try:
        persona = library.get_by_id(persona_id)
    except FileNotFoundError:
        click.echo(click.style(f"Persona not found: {persona_id}", fg="red"), err=True)
        sys.exit(1)

    builder = PromptBuilder(
        template_path=Path(template_path) if template_path else None
    )
    prompt = builder.build(persona)

    if output_file:
        Path(output_file).write_text(prompt)
        if not ctx.obj.get("quiet"):
            click.echo(f"Prompt saved to: {output_file}")
    else:
        click.echo(prompt)


@cli.command("init")
@click.option(
    "--force", is_flag=True, help="Overwrite existing files"
)
@click.pass_context
def init(ctx: click.Context, force: bool) -> None:
    """Initialize project structure with base personas."""
    import shutil

    # Create directories
    dirs_to_create = [
        DEFAULT_PERSONAS_DIR,
        DEFAULT_TEMPLATES_DIR,
        Path("templates/prompts"),
    ]

    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        if ctx.obj.get("verbose"):
            click.echo(f"Created directory: {dir_path}")

    # Copy base personas from package
    package_dir = Path(__file__).parent.parent.parent
    base_personas_src = package_dir / "personas" / "definitions"
    template_src = package_dir / "personas" / "templates" / "persona-template.yaml"
    anti_syc_src = package_dir / "templates" / "prompts" / "anti-sycophancy.md"

    # Copy persona template
    if template_src.exists():
        dest = DEFAULT_TEMPLATES_DIR / "persona-template.yaml"
        if force or not dest.exists():
            shutil.copy2(template_src, dest)
            if not ctx.obj.get("quiet"):
                click.echo(f"Created: {dest}")

    # Copy anti-sycophancy template
    if anti_syc_src.exists():
        dest = Path("templates/prompts/anti-sycophancy.md")
        if force or not dest.exists():
            shutil.copy2(anti_syc_src, dest)
            if not ctx.obj.get("quiet"):
                click.echo(f"Created: {dest}")

    # Copy base personas if they exist
    if base_personas_src.exists():
        for persona_file in base_personas_src.glob("*.yaml"):
            dest = DEFAULT_PERSONAS_DIR / persona_file.name
            if force or not dest.exists():
                shutil.copy2(persona_file, dest)
                if not ctx.obj.get("quiet"):
                    click.echo(f"Created: {dest}")

    if not ctx.obj.get("quiet"):
        click.echo(click.style("\n✓ Project initialized successfully!", fg="green"))
        click.echo("\nNext steps:")
        click.echo("  1. View available personas: research-cli persona list")
        click.echo("  2. Show persona details: research-cli persona show <id>")
        click.echo("  3. Generate a prompt: research-cli persona prompt <id>")


if __name__ == "__main__":
    cli()
