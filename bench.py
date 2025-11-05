#!/usr/bin/env python3
"""
🚀 Apache Superset Knowledge Benchmark CLI

A cute CLI tool for running the Superset knowledge benchmark.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from openai import OpenAI

app = typer.Typer(help="🚀 Apache Superset Knowledge Benchmark")
console = Console()


def load_yaml(file_path: Path) -> dict:
    """Load YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


@app.command()
def generate(
    output_dir: Path = typer.Option(Path("generated"), help="Output directory"),
):
    """
    📝 Generate questionnaire and grading rubric from questions.yaml
    """
    console.print(Panel.fit(
        "📝 Generating Questionnaire",
        border_style="cyan"
    ))

    # Load questions
    questions_data = load_yaml(Path('questions.yaml'))

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Generate questionnaire
    questions = questions_data['questions']

    content = []
    content.append("# Apache Superset Knowledge Assessment\n")
    content.append("Please answer the following questions about Apache Superset based on your knowledge.")
    content.append("Provide detailed, accurate answers. If you're unsure, please indicate that.\n")
    content.append("=" * 80 + "\n")

    for i, q in enumerate(questions, 1):
        category_display = 'features' if q['category'] == 'hallucination' else q['category']
        content.append(f"Question {i} [{category_display}]")
        content.append("-" * 80)
        content.append(q['text'].strip())
        content.append("\nYour answer:\n\n")
        content.append("=" * 80 + "\n")

    questionnaire_path = output_dir / 'questionnaire.txt'
    with open(questionnaire_path, 'w') as f:
        f.write("\n".join(content))

    console.print(f"✓ Generated questionnaire: [cyan]{questionnaire_path}[/cyan]")

    # Generate rubric
    rubric_content = ["# Apache Superset Knowledge Assessment - Grading Rubric\n"]

    for i, q in enumerate(questions, 1):
        rubric_content.append(f"## Question {i}: {q['id']} [{q['category']}/{q['subcategory']}]\n")
        rubric_content.append(f"**Question:**\n{q['text'].strip()}\n")

        if 'expected_answer' in q:
            rubric_content.append(f"**Expected Answer:**\n{q['expected_answer'].strip()}\n")

        rubric_content.append(f"**Rubric:**\n{q['rubric']['scoring'].strip()}\n")

        if 'examples' in q['rubric']:
            rubric_content.append("**Examples:**")
            for key, value in q['rubric']['examples'].items():
                score = key.replace('score_', '')
                rubric_content.append(f"- {score}: {value.strip()}")
            rubric_content.append("")

        rubric_content.append("=" * 80 + "\n")

    rubric_path = output_dir / 'grading_rubric.txt'
    with open(rubric_path, 'w') as f:
        f.write("\n".join(rubric_content))

    console.print(f"✓ Generated grading rubric: [cyan]{rubric_path}[/cyan]")

    console.print("\n[green]✨ Generation complete![/green]")


@app.command()
def models():
    """
    📋 List all available models
    """
    console.print(Panel.fit(
        "📋 Available Models",
        border_style="cyan"
    ))

    models_data = load_yaml(Path('models.yaml'))

    table = Table(box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Provider", style="yellow")
    table.add_column("Training Cutoff", style="green")
    table.add_column("PK", style="dim")

    for model in models_data['models']:
        table.add_row(
            model['id'],
            model['name'],
            model['provider'],
            str(model['training_cutoff']),
            model['pk']
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(models_data['models'])} models[/dim]")


@app.command()
def run(
    model_ids: Optional[str] = typer.Option(None, "--models", "-m", help="Comma-separated model IDs (default: all)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show prompt without API calls"),
):
    """
    🚀 Run the benchmark on selected models
    """
    console.print(Panel.fit(
        "🚀 Running Apache Superset Benchmark",
        border_style="green"
    ))

    # Check for API key (support both variants)
    api_key = os.environ.get('OPEN_ROUTER_API_KEY') or os.environ.get('OPENROUTER_API_KEY')
    if not api_key and not dry_run:
        console.print("[red]✗ Error: OPEN_ROUTER_API_KEY not set[/red]")
        console.print("[yellow]Set it with: export OPEN_ROUTER_API_KEY='your-key'[/yellow]")
        raise typer.Exit(1)

    # Load data
    questions_data = load_yaml(Path('questions.yaml'))
    models_data = load_yaml(Path('models.yaml'))

    # Create prompt
    questions = questions_data['questions']
    prompt_parts = [
        "# Apache Superset Knowledge Assessment\n",
        "Please answer the following questions about Apache Superset based solely on your training data.",
        "Do not use any external tools, web search, or code execution.",
        "Provide detailed, accurate answers. If you're unsure, please indicate that explicitly.\n",
        "Answer each question clearly, starting with the question ID (e.g., 'h1:', 'c2:', etc.).",
        "You can use whatever format is most natural for you.\n",
        "Questions:\n"
    ]

    for q in questions:
        category = 'features' if q['category'] == 'hallucination' else q['category']
        prompt_parts.append(f"[{q['id']}] ({category})")
        prompt_parts.append(q['text'].strip())
        prompt_parts.append("")

    prompt = "\n".join(prompt_parts)

    if dry_run:
        console.print(Panel(prompt, title="Questionnaire Prompt", border_style="cyan"))
        return

    # Filter models
    models_to_test = models_data['models']
    if model_ids:
        selected = set(model_ids.split(','))
        models_to_test = [m for m in models_to_test if m['id'] in selected]
        console.print(f"[cyan]Testing {len(models_to_test)} models: {', '.join(m['id'] for m in models_to_test)}[/cyan]\n")
    else:
        console.print(f"[cyan]Testing all {len(models_to_test)} models[/cyan]\n")

    # Initialize client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Run tests
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        for model_config in models_to_test:
            task = progress.add_task(
                f"Testing {model_config['name']}...",
                total=None
            )

            try:
                response = client.chat.completions.create(
                    model=model_config['openrouter_id'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=12000,  # Increased for 20-question benchmark
                )

                answer_text = response.choices[0].message.content

                results = {
                    "model_id": model_config['id'],
                    "model_name": model_config['name'],
                    "openrouter_id": model_config['openrouter_id'],
                    "training_cutoff": str(model_config['training_cutoff']),
                    "timestamp": datetime.utcnow().isoformat(),
                    "raw_response": answer_text,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                }

                # Save results
                results_dir = Path('results') / model_config['id']
                results_dir.mkdir(parents=True, exist_ok=True)

                output_file = results_dir / 'answers.json'
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)

                progress.update(task, completed=True)
                console.print(f"  ✓ [green]{model_config['name']}[/green] → {output_file}")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"  ✗ [red]{model_config['name']}: {e}[/red]")

    console.print("\n[green]✨ Benchmark complete![/green]")


@app.command()
def results():
    """
    📊 Show summary of test results
    """
    console.print(Panel.fit(
        "📊 Test Results Summary",
        border_style="cyan"
    ))

    results_dir = Path('results')
    if not results_dir.exists():
        console.print("[yellow]No results found. Run 'bench run' first.[/yellow]")
        return

    table = Table(box=box.ROUNDED)
    table.add_column("Model", style="cyan")
    table.add_column("Timestamp", style="dim")
    table.add_column("Response", style="green")
    table.add_column("Tokens", style="yellow")
    table.add_column("Status", style="white")

    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue

        answers_file = model_dir / 'answers.json'
        if not answers_file.exists():
            continue

        with open(answers_file, 'r') as f:
            data = json.load(f)

        timestamp = datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M')

        if 'error' in data:
            table.add_row(
                data['model_name'],
                timestamp,
                "—",
                "—",
                f"[red]Error: {data['error']}[/red]"
            )
        else:
            response_length = len(data.get('raw_response', ''))
            tokens = data.get('usage', {}).get('total_tokens', '—')

            status = "[green]✓ Complete[/green]"
            length_display = f"{response_length} chars"

            table.add_row(
                data['model_name'],
                timestamp,
                length_display,
                str(tokens),
                status
            )

    console.print(table)


if __name__ == '__main__':
    app()
