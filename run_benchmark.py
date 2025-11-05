#!/usr/bin/env python3
"""
Run the Apache Superset knowledge benchmark using OpenRouter API.

This script:
1. Loads questions and model configs
2. For each model, sends the questionnaire via OpenRouter API
3. Saves responses in results/{model_id}/answers.json

Usage:
    export OPEN_ROUTER_API_KEY="your-key-here"
    python run_benchmark.py [--models gpt-4,claude-3.5-sonnet] [--dry-run]
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI


def load_yaml(file_path):
    """Load YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def create_questionnaire_prompt(questions_data):
    """Create the prompt with all questions."""

    questions = questions_data['questions']

    prompt_parts = [
        "# Apache Superset Knowledge Assessment",
        "",
        "Please answer the following questions about Apache Superset based solely on your training data.",
        "Do not use any external tools, web search, or code execution.",
        "Provide detailed, accurate answers. If you're unsure about something, please indicate that explicitly.",
        "",
        "Format your response as a JSON object with question IDs as keys:",
        '{"q1": "your answer...", "q2": "your answer...", ...}',
        "",
        "Questions:",
        ""
    ]

    for q in questions:
        # Don't reveal hallucination traps
        category = 'features' if q['category'] == 'hallucination' else q['category']

        prompt_parts.append(f"[{q['id']}] ({category})")
        prompt_parts.append(q['text'].strip())
        prompt_parts.append("")

    return "\n".join(prompt_parts)


def run_model_test(client, model_config, prompt):
    """Run test for a single model via OpenRouter."""

    print(f"\nTesting {model_config['name']} ({model_config['id']})...")
    print(f"  OpenRouter ID: {model_config['openrouter_id']}")
    print(f"  Training cutoff: {model_config['training_cutoff']}")

    try:
        response = client.chat.completions.create(
            model=model_config['openrouter_id'],
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent answers
            max_tokens=4000,
        )

        answer_text = response.choices[0].message.content

        # Try to extract JSON from response
        # Models might wrap it in markdown code blocks
        if "```json" in answer_text:
            answer_text = answer_text.split("```json")[1].split("```")[0].strip()
        elif "```" in answer_text:
            answer_text = answer_text.split("```")[1].split("```")[0].strip()

        try:
            answers = json.loads(answer_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, save raw text
            print(f"  ⚠ Warning: Could not parse JSON response, saving raw text")
            answers = {"raw_response": answer_text, "parse_error": True}

        return {
            "model_id": model_config['id'],
            "model_name": model_config['name'],
            "openrouter_id": model_config['openrouter_id'],
            "training_cutoff": model_config['training_cutoff'],
            "timestamp": datetime.utcnow().isoformat(),
            "answers": answers,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }

    except Exception as e:
        print(f"  ✗ Error testing model: {e}")
        return {
            "model_id": model_config['id'],
            "model_name": model_config['name'],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def save_results(model_config, results):
    """Save results to results/{model_id}/answers.json"""

    results_dir = Path('results') / model_config['id']
    results_dir.mkdir(parents=True, exist_ok=True)

    output_file = results_dir / 'answers.json'

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  ✓ Saved results to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Run Apache Superset knowledge benchmark')
    parser.add_argument('--models', help='Comma-separated list of model IDs to test (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Print prompt without making API calls')
    args = parser.parse_args()

    # Check for API key (support both variants)
    api_key = os.environ.get('OPEN_ROUTER_API_KEY') or os.environ.get('OPENROUTER_API_KEY')
    if not api_key and not args.dry_run:
        print("Error: OPEN_ROUTER_API_KEY environment variable not set")
        print("Export it with: export OPEN_ROUTER_API_KEY='your-key-here'")
        sys.exit(1)

    # Load data
    print("Loading questions and models...")
    questions_data = load_yaml('questions.yaml')
    models_data = load_yaml('models.yaml')

    # Create questionnaire prompt
    prompt = create_questionnaire_prompt(questions_data)

    if args.dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN - Questionnaire prompt:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        return

    # Filter models if specified
    models_to_test = models_data['models']
    if args.models:
        selected_ids = set(args.models.split(','))
        models_to_test = [m for m in models_to_test if m['id'] in selected_ids]
        print(f"Testing {len(models_to_test)} selected models: {', '.join(m['id'] for m in models_to_test)}")
    else:
        print(f"Testing all {len(models_to_test)} models")

    # Initialize OpenRouter client (OpenAI-compatible)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Run tests
    print("\n" + "=" * 80)
    print("Running benchmark...")
    print("=" * 80)

    for model_config in models_to_test:
        results = run_model_test(client, model_config, prompt)
        save_results(model_config, results)

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print(f"Results saved in results/ directory")
    print("=" * 80)


if __name__ == '__main__':
    main()
