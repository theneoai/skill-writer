"""CLI entry point for skill."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

app = typer.Typer(
    name="skill",
    help="Skill evaluation and management framework",
    add_completion=False,
)


@app.callback()
def version_callback(
    version: bool = typer.Option(False, "--version", help="Show version information"),
) -> None:
    """Show version information."""
    if version:
        from skill import __version__

        typer.echo(f"skill version {__version__}")
        raise typer.Exit(0)


@app.command()
def evaluate(
    target: str = typer.Argument(..., help="Target skill or prompt to evaluate"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Evaluate a skill or prompt using multi-dimensional assessment."""
    from skill.agents.evaluator import evaluate_skill

    path = Path(target)
    if not path.exists():
        typer.secho(f"Error: File not found: {target}", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo(f"Evaluating: {target}")
    result = evaluate_skill(str(path))

    if "error" in result:
        typer.secho(f"Error: {result['error']}", fg=typer.colors.RED)
        raise typer.Exit(1)

    score = result.get("total_score", 0)
    tier = result.get("tier", "UNKNOWN")
    typer.secho(f"Score: {score}", fg=typer.colors.GREEN)
    typer.echo(f"Tier:  {tier}")

    if verbose and "suggestions" in result:
        typer.echo("\nSuggestions:")
        for s in result["suggestions"]:
            typer.echo(f"  - {s}")

    if output:
        import json

        Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        typer.echo(f"Results saved to: {output}")


@app.command()
def create(
    prompt: str = typer.Argument(..., help="Skill description or prompt"),
    target_tier: str = typer.Option(
        "BRONZE", "--target", "-t", help="Target tier: GOLD, SILVER, BRONZE"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output SKILL.md path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without execution"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
) -> None:
    """Create a new skill from a prompt."""
    from skill.agents.creator import init_skill_file

    typer.echo(f"Creating skill: {prompt}")
    typer.echo(f"Target tier: {target_tier}")

    if dry_run:
        typer.echo("Dry run mode — no files will be written.")
        return

    output_path = Path(output) if output else Path.cwd() / "SKILL.md"

    if output_path.exists() and not force:
        typer.secho(
            f"Error: File exists: {output_path}. Use --force to overwrite.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    init_skill_file(str(output_path), prompt)
    typer.secho(f"Skill created: {output_path}", fg=typer.colors.GREEN)


@app.command()
def evolve(
    skill_file: str = typer.Argument(..., help="Skill file to evolve"),
    iterations: int = typer.Option(1, "--iterations", "-n", help="Number of evolution iterations"),
) -> None:
    """Evolve an existing skill."""
    from skill.engine.decider import EvolutionDecider
    from skill.engine.storage import storage_get_last_score, storage_get_eval_count

    path = Path(skill_file)
    if not path.exists():
        typer.secho(f"Error: File not found: {skill_file}", fg=typer.colors.RED)
        raise typer.Exit(1)

    skill_name = path.stem
    typer.echo(f"Evolving skill: {skill_file} ({iterations} iteration(s))")

    decider = EvolutionDecider()
    for i in range(iterations):
        score = storage_get_last_score(skill_name)
        eval_count = storage_get_eval_count(skill_name)
        decision = decider.should_evolve(skill_name, score, eval_count)
        typer.echo(f"  Iteration {i + 1}: decision={decision.decision}, reason={decision.reason}")
        if decision.decision == "no_action":
            typer.echo("  No evolution needed.")
            break


@app.command()
def version() -> None:
    """Show version information."""
    from skill import __version__

    typer.echo(f"skill version {__version__}")


@app.command()
def parse(
    skill_file: str = typer.Argument(..., help="Path to SKILL.md file to parse"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full metadata"),
) -> None:
    """Parse a SKILL.md file and show its metadata."""
    try:
        from skill.yaml_parser import extract_frontmatter, parse_skill_file

        path = Path(skill_file)
        if not path.exists():
            typer.secho(f"Error: File not found: {skill_file}", fg=typer.colors.RED)
            raise typer.Exit(1)

        metadata = parse_skill_file(path)
        typer.echo(f"Parsed: {skill_file}")
        typer.echo(f"Name: {metadata.name}")
        typer.echo(f"Description: {metadata.description}")

        if verbose:
            typer.echo("\nFull metadata:")
            typer.echo(f"  name: {metadata.name}")
            typer.echo(f"  description: {metadata.description}")
            if metadata.license:
                typer.echo(f"  license: {metadata.license}")
            if metadata.author:
                typer.echo(f"  author: {metadata.author}")
            if metadata.version:
                typer.echo(f"  version: {metadata.version}")
            if metadata.tags:
                typer.echo(f"  tags: {', '.join(metadata.tags)}")
            if metadata.type:
                typer.echo(f"  type: {metadata.type}")
    except ImportError:
        typer.secho("Error: yaml_parser module not found", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error parsing file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def validate(
    skill_file: str = typer.Argument(..., help="Path to SKILL.md file to validate"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict validation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show warnings"),
) -> None:
    """Validate a SKILL.md file."""
    try:
        from skill.yaml_parser import extract_frontmatter, validate_metadata

        path = Path(skill_file)
        if not path.exists():
            typer.secho(f"Error: File not found: {skill_file}", fg=typer.colors.RED)
            raise typer.Exit(1)

        content = path.read_text(encoding="utf-8")
        frontmatter, _ = extract_frontmatter(content)
        result = validate_metadata(frontmatter)

        if result.is_valid:
            typer.secho(f"✓ {skill_file} is valid", fg=typer.colors.GREEN)
            if result.warnings and verbose:
                typer.echo("Warnings:")
                for warning in result.warnings:
                    typer.echo(f"  - {warning}")
        else:
            typer.secho(f"✗ {skill_file} has errors:", fg=typer.colors.RED)
            for error in result.errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)
    except ImportError:
        typer.secho("Error: yaml_parser module not found", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error validating file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def generate(
    metadata_file: str = typer.Argument(..., help="Path to YAML metadata file"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output path for SKILL.md"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
) -> None:
    """Generate SKILL.md from YAML metadata."""
    try:
        from skill.md_generator import generate_frontmatter

        metadata_path = Path(metadata_file)
        if not metadata_path.exists():
            typer.secho(f"Error: File not found: {metadata_file}", fg=typer.colors.RED)
            raise typer.Exit(1)

        output_path = Path(output) if output else metadata_path.with_name("SKILL.md")

        if output_path.exists() and not force:
            typer.secho(
                f"Error: Output file exists: {output_path}. Use --force to overwrite.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(1)

        import yaml

        with open(metadata_path) as f:
            data = yaml.safe_load(f)

        from skill.md_generator import SkillMetadata

        metadata = SkillMetadata(
            name=data.get("name", ""),
            description=data.get("description", ""),
            license=data.get("license", "MIT"),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            tags=data.get("tags", []),
            type=data.get("type", "skill"),
        )

        frontmatter = generate_frontmatter(metadata)
        output_path.write_text(frontmatter, encoding="utf-8")
        typer.secho(f"Generated: {output_path}", fg=typer.colors.GREEN)
    except ImportError:
        typer.secho("Error: md_generator module not found", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error generating file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def init(
    skill_name: str = typer.Argument(..., help="Name of the skill to initialize"),
    template: str = typer.Option(
        "default", "--template", "-t", help="Template to use (default, minimal, advanced)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing skill"),
) -> None:
    """Initialize a new skill scaffold."""
    output_dir = Path(output) if output else Path.cwd() / skill_name

    if output_dir.exists() and not force:
        typer.secho(
            f"Error: Directory exists: {output_dir}. Use --force to overwrite.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    from skill.md_generator import generate_frontmatter, SkillMetadata

    metadata = SkillMetadata(
        name=skill_name,
        description=f"Skill: {skill_name}",
        license="MIT",
        author="",
        version="0.1.0",
        tags=[],
        type="skill",
    )

    skill_md_path = output_dir / "SKILL.md"
    skill_md_path.write_text(generate_frontmatter(metadata), encoding="utf-8")

    typer.secho(f"Initialized skill '{skill_name}' at {output_dir}", fg=typer.colors.GREEN)
    typer.echo(f"Template: {template}")
    typer.echo(f"Created: {skill_md_path}")


if __name__ == "__main__":
    app()
