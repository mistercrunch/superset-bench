# Context for Claude Code

This document helps Claude understand the Apache Superset Knowledge Benchmark project when returning to it.

## Project Overview

We're building a benchmark to measure how much various LLMs know about Apache Superset across different training eras. Created for an OSACON talk.

## Key Files

### Configuration (YAML)
- **`models.yaml`** - List of models to test with OpenRouter IDs, training cutoffs, and unique PKs for sandboxing
- **`questions.yaml`** - Benchmark questions organized by category with detailed grading rubrics

### CLI Tool
- **`bench.py`** - Main CLI using `typer` and `rich` for pretty output
  - Commands: `models`, `generate`, `run`, `results`
  - Uses OpenRouter API (OpenAI-compatible) to test models
  - API key: `OPEN_ROUTER_API_KEY` (with underscore) in `~/.zshrc`

### Supporting Files
- **`requirements.txt`** - Python deps: openai, pyyaml, rich, typer
- **`setup.sh`** - Setup script using `uv` for venv
- **`README.md`** - Full documentation with design decisions
- **`PROMPT.md`** - Original project notes/brainstorming

## Core Design Decisions

### 1. Time-Contextualized Grading
**Problem:** Can't write questions fair to models trained years apart (Sept 2021 vs Jan 2025)

**Solution:** Grade each model against the Superset repo state at their training cutoff:
```bash
git checkout $(git rev-list -1 --before="2021-09-01" main)  # For GPT-3.5
git checkout $(git rev-list -1 --before="2023-04-01" main)  # For GPT-4
```

This lets us ask specific codebase questions without worrying about code churn.

### 2. Single-Pass Exam
- All 13 questions in one API call per model (not 13 separate calls)
- 11 models × 1 call = 11 API calls total (not 143)
- Cost-effective, faster, more realistic

### 3. Freeform Responses
- No required output format (JSON, etc.)
- Older models struggle with structured output
- Evaluator (Claude Code) parses any format
- Output saved as `raw_response` in `results/{model_id}/answers.json`

### 4. Hallucination Detection
Mix in plausible-but-false questions:
- "Describe Superset's notebook integration" (doesn't exist)
- "How does ML model deployment work?" (not a feature)
- "What's in the mobile app?" (no official app)

Tests epistemic awareness - can models say "I don't know"?

## Question Categories

1. **Historical** (h1, h2) - Timeless facts: origins, creator
2. **Codebase** (c1, c2, c3) - Specific implementation details
3. **Architecture** (a1, a2) - High-level design
4. **Hallucination traps** (trap1, trap2, trap3) - Non-existent features
5. **Practices** (p1) - Community standards, testing

## Workflow

1. Edit `models.yaml` and `questions.yaml`
2. `python bench.py generate` → creates `generated/questionnaire.txt` and `generated/grading_rubric.txt`
3. `python bench.py run` → tests all models via OpenRouter
4. Results saved to `results/{model_id}/answers.json` with `raw_response` field
5. Graders (Claude Code/Codex) evaluate using rubric
6. Graders save scores to `results/{model_id}/grades.json`

## Current Status / Open Issues

### Model IDs Need Verification
The `openrouter_id` fields in `models.yaml` may not be accurate. OpenRouter might not have older models (GPT-3.5, Claude 3 Opus, etc.) available anymore.

**Need to:**
1. Check which models are actually available on OpenRouter
2. Update `models.yaml` with correct IDs
3. May need to focus on more recent models only

### Sandboxes Not Yet Implemented
Each model has a `pk` for isolated sandbox directories (`sandboxes/{pk}/`) but this isn't wired up yet.

### Grading Automation Not Yet Built
Manual process: evaluators read rubric and grade answers. Could automate with:
- Script that feeds rubric + answer to Claude Code
- Structured output for scores
- Aggregation into reports

## Common Commands

```bash
# Setup
./setup.sh
source .venv/bin/activate

# Check API key is loaded
echo $OPEN_ROUTER_API_KEY

# View models
python bench.py models

# Test the prompt
python bench.py run --dry-run

# Run on one model
python bench.py run --models gpt-4

# Run all models
python bench.py run

# View results
python bench.py results
```

## Next Steps

1. **Verify OpenRouter model IDs** - Check what's actually available
2. **Test with one model** - Run `--models` with a single known-good model
3. **Build grading automation** - Script to use Claude Code for evaluation
4. **Add more questions** - Expand beyond the 13 samples
5. **Generate reports** - Analyze scores by category, model, era

## Repository Structure

```
superset-bench/
├── models.yaml          # Model configs with OpenRouter IDs
├── questions.yaml       # Questions with rubrics
├── bench.py            # Main CLI tool
├── requirements.txt    # Python dependencies
├── setup.sh            # Setup script (uses uv)
├── generated/          # Generated questionnaires
├── results/            # Model answers (raw_response in JSON)
└── reports/            # Analysis (not yet implemented)
```
