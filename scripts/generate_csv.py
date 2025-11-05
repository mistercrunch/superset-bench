#!/usr/bin/env python3
"""Generate CSV export of all benchmark scores for Superset dashboard."""

import json
import csv
import yaml
from pathlib import Path

# Load questions metadata
with open('metadata/questions.yaml', 'r') as f:
    questions_data = yaml.safe_load(f)

questions_lookup = {q['id']: q for q in questions_data['questions']}

# Load models metadata
with open('metadata/models.yaml', 'r') as f:
    models_data = yaml.safe_load(f)

models_lookup = {m['id']: m for m in models_data['models']}

# Collect all scores
rows = []

results_dir = Path('results')
for model_dir in results_dir.iterdir():
    if not model_dir.is_dir():
        continue

    grades_file = model_dir / 'grades.json'
    if not grades_file.exists():
        continue

    with open(grades_file, 'r') as f:
        grades = json.load(f)

    model_id = grades['model_id']
    model_info = models_lookup.get(model_id, {})

    # Handle both 'scores' and 'question_grades' formats
    question_scores = grades.get('scores', grades.get('question_grades', {}))

    for question_id, score_data in question_scores.items():
        question_info = questions_lookup.get(question_id, {})

        row = {
            'question_id': question_id,
            'question_text': question_info.get('text', '').strip().replace('\n', ' ')[:200],
            'category': question_info.get('category', ''),
            'subcategory': question_info.get('subcategory', ''),
            'difficulty': question_info.get('difficulty', ''),
            'model_id': model_id,
            'model_name': grades['model_name'],
            'model_provider': model_info.get('provider', ''),
            'training_cutoff': str(model_info.get('training_cutoff', '')),
            'score': score_data['score'],
            'max_score': score_data['max'],
            'percentage': round(score_data['score'] / score_data['max'] * 100, 1) if score_data['max'] > 0 else 0,
            'reasoning': score_data.get('reasoning', score_data.get('rationale', '')).replace('\n', ' ')[:500],
            'graded_at': grades.get('graded_at', grades.get('grading_date', '')),
            'grader': grades.get('grader', '')
        }
        rows.append(row)

# Write CSV
output_file = 'benchmark_scores.csv'
fieldnames = [
    'question_id', 'question_text', 'category', 'subcategory', 'difficulty',
    'model_id', 'model_name', 'model_provider', 'training_cutoff',
    'score', 'max_score', 'percentage', 'reasoning', 'graded_at', 'grader'
]

with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Generated {output_file} with {len(rows)} rows")
print(f"  Models: {len(set(r['model_id'] for r in rows))}")
print(f"  Questions: {len(set(r['question_id'] for r in rows))}")
