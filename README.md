# Apache Superset Knowledge Benchmark

A benchmark designed to measure how much various language models know about Apache Superset across different training eras.

## Results Summary

**20-Question Benchmark** - Testing models from September 2021 to March 2025

| Model | Provider | Training Cutoff | Score | Percentage | Status |
|-------|----------|----------------|-------|------------|--------|
| Claude Sonnet 4 | Anthropic | 2025-03-01 | 17.3/19 | 91.3% | 🥉 Strong |
| Claude Opus 4.1 | Anthropic | 2025-02-01 | 18.3/19 | 96.3% | 🥈 Excellent |
| Claude Sonnet 4.5 | Anthropic | 2025-01-01 | 18.0/19 | 95.0% | 🥉 Strong |
| Gemini 2.5 Pro | Google | 2025-01-01 | 18.7/19 | 98.7% | 🥈 Excellent |
| Gemini 2.5 Flash | Google | 2025-01-01 | 19.0/19 | 100.0% | 🥇 Perfect |
| Gemini 2.0 Flash | Google | 2024-11-01 | 19.0/19 | 100.0% | 🥇 Perfect |
| GPT-5 Mini | OpenAI | 2024-08-01 | 17.0/19 | 89.5% | ✓ Good |
| GPT-5 | OpenAI | 2024-08-01 | 19.0/19 | 100.0% | 🥇 Perfect |
| Claude 3.5 Sonnet | Anthropic | 2024-04-01 | 15.2/19 | 80.0% | ✓ Good |
| GPT-4o | OpenAI | 2023-10-01 | 18.3/19 | 96.3% | 🥈 Excellent |
| Claude 3 Opus | Anthropic | 2023-08-01 | 17.4/19 | 91.6% | 🥉 Strong |
| GPT-4 | OpenAI | 2023-04-01 | 17.2/19 | 90.3% | 🥉 Strong |
| GPT-3.5 Turbo | OpenAI | 2021-09-01 | 15.0/19 | 78.9% | ✓ Good |

**Key Insights:**
- **3 Perfect Scores**: GPT-5, Gemini 2.5 Flash, and Gemini 2.0 Flash all achieved 100%
- **Zero Hallucinations**: All models from 2023+ correctly identified non-existent features
- **Clear Evolution**: Knowledge improved dramatically from GPT-3.5 (78.9%) to latest models (100%)
- **Google Gemini Dominance**: All 3 Gemini models scored 98.7%+, with 2 perfect scores

## Overview

This benchmark was created for OSACON to assess the evolution of model knowledge about Apache Superset. By testing models from different time periods, we can observe how their understanding of the project has developed over time.

## Objective

Evaluate language models' knowledge of Apache Superset across multiple dimensions:
- Codebase-specific knowledge
- Architectural understanding
- Community practices and standards
- Historical context and key events

## Design Decisions

This benchmark addresses several key challenges in evaluating model knowledge evolution:

### The Timelessness Problem
**Challenge:** How do you write questions that are fair to test models trained years apart?

**Solution:** Time-contextualized grading. Instead of trying to write "timeless" questions, we grade each model's answers against the repository state at their training cutoff date. A question like "What are the key methods in SupersetSecurityManager?" is fair because GPT-3.5 is graded against the 2021 codebase, while GPT-4 is graded against the 2023 codebase.

**Impact:** Opens up the entire question space. We can ask specific codebase questions without worrying about code churn, refactoring, or renamed classes.

### Single-Pass Exam Format
**Why:** One API call with all questions, rather than 13 separate calls per model.

**Benefits:**
- Cost-effective (11 API calls total vs 143)
- Faster execution (minutes vs hours)
- Mirrors realistic usage with long context
- Allows observation of cross-question behavior patterns

### Freeform Responses
**Why:** No required output format (JSON, XML, etc.)

**Reasoning:** Older models like GPT-3.5 struggle with structured output. By accepting freeform responses, we ensure fair comparison across model generations. The evaluator (Claude Code/Codex) can parse any format.

### Hallucination Detection
**Why:** Include plausible-but-false questions mixed with real ones.

**Examples:**
- "Describe Superset's notebook integration features" (doesn't exist)
- "How does the built-in ML model deployment work?" (not a feature)
- "What are the features of the mobile app?" (no official app)

**Purpose:** Test epistemic awareness—can models recognize when they don't know something, or will they confidently fabricate details?

**Scoring:** Higher scores for saying "I don't know" or "this doesn't exist" than for fabricating features.

## Methodology

### Test Creation
The benchmark questions are developed with full access to:
- The Apache Superset repository
- GitHub project history
- Community documentation

Questions include:
- **Historical questions**: Timeless facts about Superset's origins and evolution
- **Codebase questions**: Specific implementation details (classes, methods, architecture)
- **Hallucination traps**: Plausible-sounding but non-existent features to test epistemic awareness

### Test Administration
Models being evaluated will:
- Receive only the questions (no external resources)
- Rely solely on pre-existing knowledge from training
- Not have access to the internet, documentation, or repository

### Time-Contextualized Grading
A key innovation: **answers are graded against the codebase state at each model's training cutoff**.

**How it works:**
1. Same questions given to all models
2. Evaluators check out the Superset repository at each model's cutoff date
3. Answers are judged against what existed at that point in time
4. Example: `git checkout $(git rev-list -1 --before="2023-04-01" main)` for GPT-4

**Benefits:**
- No need for "timeless" questions
- Fair comparison (models judged on what they should know)
- Reveals how knowledge depth increases across model generations
- Can ask specific codebase questions without anachronism concerns

### Evaluation Process
- Multiple models will serve as evaluators
- Evaluators grade answers blindly (without knowing which model produced which answer)
- Rating sheets define scoring criteria for each question
- Each question is graded on a scale of 0 to 1

### Hallucination Detection
Some questions test whether models can recognize non-existent features:

**Scoring for hallucination questions:**
- 1.0: Correctly identifies feature doesn't exist
- 0.5: Expresses uncertainty or hedges appropriately
- 0.0: Confidently describes fabricated features

## Question Categories

### 1. Codebase-Specific Knowledge
Questions about the internal structure and implementation details of Apache Superset.

**Focus areas:**
- Key classes and their purposes
- Important methods and their functionality
- General codebase structure and organization
- Testing standards and practices

**Example question:**
> What are some of the standards used around unit tests in the Superset project?

### 2. Architectural Knowledge
Questions about the high-level design and architecture of Apache Superset.

**Focus areas:**
- System components and their interactions
- Design patterns employed
- Technology stack
- Data flow and processing

### 3. Cultural and Community Practices
Questions about the development practices, standards, and community norms.

**Focus areas:**
- Code review processes
- Contribution guidelines
- Coding standards and conventions
- Release processes
- Community governance

### 4. Historical Knowledge
Questions about the evolution of Apache Superset and key historical events.

**Focus areas:**
- Project origins and founding
- Superset Improvement Proposals (SIPs)
- Major milestones and releases
- Significant architectural changes

**Example question:**
> How did Superset come to be?

## Models Under Evaluation

The following models will be tested, representing multiple generations and providers:

| Model ID | Model Name | Training Cutoff | Provider |
|----------|------------|-----------------|----------|
| `gpt-3.5` | GPT-3.5 | September 2021 | OpenAI |
| `gpt-4` | GPT-4 | April 2023 | OpenAI |
| `gpt-4o` | GPT-4o | October 2023 | OpenAI |
| `claude-3-opus` | Claude 3 Opus | August 2023 | Anthropic |
| `claude-3.5-sonnet` | Claude 3.5 Sonnet | April 2024 | Anthropic |
| `claude-3.5-sonnet-v2` | Claude 3.5 Sonnet v2 | July 2024 | Anthropic |
| `claude-sonnet-4` | Claude Sonnet 4 | March 2025 | Anthropic |
| `claude-sonnet-4.5` | Claude Sonnet 4.5 | January 2025 | Anthropic |
| `gemini-2.0-flash` | Gemini 2.0 Flash | November 2024 | Google |
| `gemini-2.5-flash` | Gemini 2.5 Flash | January 2025 | Google |
| `gemini-2.5-pro` | Gemini 2.5 Pro | January 2025 | Google |

**Model identification:**
- Each model has a unique `pk` (primary key) - an 8-character hex identifier
- The `pk` is used for sandbox folder names to isolate model operations
- Model `id` is human-readable and used in reporting
- Sandbox folders: `sandboxes/{pk}/` for student models during testing
- Answer files: `results/{model_id}/answers.json`
- Grading sheets: `results/{model_id}/grades.json`

## Scoring

- Each question is scored from 0 to 1
- Scoring rubrics are defined per question to ensure consistency
- Partial credit is awarded for partially correct answers
- Evaluators use standardized rating sheets

## Reporting

Results are analyzed and reported with breakdowns by:
- Question category (codebase, architecture, cultural, historical)
- Model and training era
- Individual question performance
- Comparative analysis across models

## Results

### Overall Model Performance

Tested on 20-question benchmark (expanded from initial 13 questions):

| Model | Score | Percentage | Questions Tested | Notable Performance |
|-------|-------|------------|------------------|---------------------|
| **GPT-5** | 20.0/20.0 | **100%** | 20 | Perfect score on expanded test |
| **GPT-4** | 11.0/11.0 | **100%** | 13 | Perfect on original test |
| **Claude Sonnet 4.5** | 10.9/11.0 | 99.1% | 13 | Near-perfect |
| **GPT-4o** | 10.8/11.0 | 98.2% | 13 | Strong performance |
| **Gemini 2.5 Flash** | 10.8/11.0 | 98.2% | 13 | Strong performance |
| **Claude Sonnet 4** | 10.6/11.0 | 96.4% | 13 | Very good |
| **Gemini 2.0 Flash** | 10.6/11.0 | 96.4% | 13 | Very good |
| **Gemini 2.5 Pro** | 10.3/11.0 | 93.6% | 13 | Good |
| **Claude 3 Opus** | 10.0/11.0 | 90.9% | 13 | Good |
| **Claude 3.5 Sonnet** | 10.0/11.0 | 90.9% | 13 | Good |
| **GPT-5 Mini** | 17.0/19.0 | 89.5% | 20 | Good on expanded test |
| **GPT-3.5 Turbo** | 8.9/11.0 | 80.9% | 13 | Lowest score |

### Key Findings

**Evolution of Knowledge (2021-2025):**
- **GPT-3.5** (Sept 2021): 80.9% - First generation, hallucinated on notebook integration question
- **GPT-4** (Apr 2023): 100% - Perfect score showing major knowledge improvement
- **GPT-5** (Aug 2024): 100% - Perfect even on harder expanded test

**Hallucination Detection:**
- **GPT-3.5**: Only model that hallucinated, confidently describing non-existent notebook integration features
- **All 2023+ models**: 0% hallucination rate - correctly identified all fake features
- Evolution shows dramatic improvement in epistemic awareness ("I don't know" capability)

**Performance by Category:**
- **Historical Questions**: All models scored 90%+ (timeless facts easier to learn)
- **Codebase Details**: Significant variance - newer models showed deeper implementation knowledge
- **Hallucination Traps**: Clear generational divide - pre-2023 vs post-2023 models
- **Advanced Questions**: Added in expanded test to challenge top performers

**Provider Comparison:**
- **OpenAI**: GPT-4 and GPT-5 achieved perfect scores
- **Anthropic**: Claude Sonnet 4.5 came closest at 99.1%
- **Google**: Gemini 2.5 Flash performed best at 98.2%

**Epistemic Humility:**
The most striking evolution is in models' ability to recognize what they don't know. While GPT-3.5 confidently fabricated features, all 2023+ models correctly identified non-existent features with clear statements like "Superset does not have built-in notebook integration features."

### Data Export

Full results are available in `benchmark_scores.csv` with 148 rows of detailed scores across all models and questions, ready for analysis in Apache Superset or other BI tools.

## Getting Started

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <this-repo>
cd superset-bench
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source .venv/bin/activate

# Set your API key
export OPEN_ROUTER_API_KEY='your-key-here'
```

### Usage

The `bench.py` CLI provides all the tools you need:

```bash
# View available models
python bench.py models

# Generate questionnaires and rubrics
python bench.py generate

# Run benchmark on all models
python bench.py run

# Run on specific models
python bench.py run --models gpt-4,claude-3.5-sonnet

# View results summary
python bench.py results

# Dry run (see the prompt without API calls)
python bench.py run --dry-run
```

## Workflow

1. **Define models** - Edit `models.yaml` to add/remove models
2. **Create questions** - Edit `questions.yaml` to add questions and rubrics
3. **Generate materials** - Run `bench.py generate` to create questionnaires
4. **Run tests** - Run `bench.py run` to test all models via OpenRouter
5. **Grade answers** - Use Claude Code/Codex with grading rubric to evaluate raw responses
6. **Analyze results** - Generate reports from graded answers

## Repository Structure

```
superset-bench/
├── README.md                    # This file
├── CLAUDE.md                    # Context for Claude Code
├── PROMPT.md                    # Initial project notes
├── bench.py                     # Main CLI tool
├── requirements.txt             # Python dependencies
├── setup.sh                     # Setup script
├── benchmark_scores.csv         # Exported results for dashboards
├── metadata/                    # Configuration files
│   ├── models.yaml             # Model definitions with PKs and cutoff dates
│   └── questions.yaml          # Benchmark questions with rubrics
├── scripts/                     # Utility scripts
│   └── generate_csv.py         # Export results to CSV
├── generated/                   # Generated questionnaires and rubrics
│   ├── questionnaire.txt       # Questions for models
│   └── grading_rubric.txt      # Rubric for evaluators
├── results/                     # Model answers and evaluations
│   ├── gpt-3.5/
│   │   ├── answers.json        # Raw text response from model (freeform)
│   │   └── grades.json         # Evaluated scores (added by graders)
│   ├── gpt-4/
│   │   ├── answers.json
│   │   └── grades.json
│   └── ...                     # Other models
└── reports/                     # Analysis and visualizations
    └── benchmark_summary.md    # Overall findings
```

## Contributing

This benchmark is created as part of research for OSACON. Questions and improvements are welcome through pull requests.

## License

TBD
