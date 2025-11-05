#!/usr/bin/env python3
"""
Generate questionnaire text files from questions.yaml.

This creates clean, formatted questionnaires that can be copy-pasted into
OpenRouter.ai or any LLM interface.
"""

import yaml
from pathlib import Path


def load_yaml(file_path):
    """Load YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def generate_questionnaire(questions_data, output_path):
    """Generate a formatted questionnaire for students (models being tested)."""

    questions = questions_data['questions']

    # Filter out hallucination traps from the visible category
    # (we still ask them, but don't label them as traps)

    content = []
    content.append("# Apache Superset Knowledge Assessment")
    content.append("")
    content.append("Please answer the following questions about Apache Superset based on your knowledge.")
    content.append("Provide detailed, accurate answers. If you're unsure about something, please indicate that.")
    content.append("")
    content.append("=" * 80)
    content.append("")

    for i, q in enumerate(questions, 1):
        # Don't reveal which questions are hallucination traps
        category_display = q['category']
        if category_display == 'hallucination':
            # Disguise as architecture or features question
            category_display = 'features'

        content.append(f"Question {i} [{category_display}]")
        content.append("-" * 80)
        content.append(q['text'].strip())
        content.append("")
        content.append("Your answer:")
        content.append("")
        content.append("")
        content.append("=" * 80)
        content.append("")

    questionnaire_text = "\n".join(content)

    with open(output_path, 'w') as f:
        f.write(questionnaire_text)

    print(f"✓ Generated questionnaire: {output_path}")
    return questionnaire_text


def generate_grading_rubric(questions_data, output_path):
    """Generate a detailed grading rubric for evaluators."""

    questions = questions_data['questions']

    content = []
    content.append("# Apache Superset Knowledge Assessment - Grading Rubric")
    content.append("")
    content.append("## Instructions for Evaluators")
    content.append("")
    content.append(questions_data['metadata']['instructions'].strip())
    content.append("")
    content.append("=" * 80)
    content.append("")

    for i, q in enumerate(questions, 1):
        content.append(f"## Question {i}: {q['id']} [{q['category']}/{q['subcategory']}]")
        content.append("")
        content.append("**Question:**")
        content.append(q['text'].strip())
        content.append("")

        if 'expected_answer' in q:
            content.append("**Expected Answer:**")
            content.append(q['expected_answer'].strip())
            content.append("")

        content.append("**Rubric:**")
        content.append(q['rubric']['scoring'].strip())
        content.append("")

        if 'examples' in q['rubric']:
            content.append("**Examples:**")
            for key, value in q['rubric']['examples'].items():
                score = key.replace('score_', '')
                content.append(f"- {score}: {value.strip()}")
            content.append("")

        if 'grading_notes' in q['rubric']:
            content.append("**Grading Notes:**")
            content.append(q['rubric']['grading_notes'].strip())
            content.append("")

        if 'notes' in q['rubric']:
            content.append("**Notes:**")
            content.append(q['rubric']['notes'].strip())
            content.append("")

        content.append("=" * 80)
        content.append("")

    rubric_text = "\n".join(content)

    with open(output_path, 'w') as f:
        f.write(rubric_text)

    print(f"✓ Generated grading rubric: {output_path}")
    return rubric_text


def main():
    """Main entry point."""

    # Load questions
    questions_data = load_yaml('questions.yaml')

    # Create output directory
    output_dir = Path('generated')
    output_dir.mkdir(exist_ok=True)

    # Generate questionnaire (for students/models)
    generate_questionnaire(
        questions_data,
        output_dir / 'questionnaire.txt'
    )

    # Generate grading rubric (for evaluators)
    generate_grading_rubric(
        questions_data,
        output_dir / 'grading_rubric.txt'
    )

    print("")
    print("=" * 80)
    print("Next steps:")
    print("1. Copy generated/questionnaire.txt and paste into OpenRouter.ai")
    print("2. Test each model and save their responses")
    print("3. Use generated/grading_rubric.txt to evaluate answers")
    print("=" * 80)


if __name__ == '__main__':
    main()
