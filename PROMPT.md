Hey! I'd like to create a new simple, yet informative benchmark as part of my talk at OSACON.

The idea is to create a benchmark that measures how much various models know about Apache Superset.

Models from different eras will be assessed for their ability to answer questions related to Apache Superset.

Ou first goal is to create the test ouselves, while we have access to the Superset repository and GitHub.

While taking the test, the models will not have access to any external resources, including the internet. They will rely solely on their pre-existing knowledge, aquired from training.

Each model will produce answers to our set of questions.

For evaluation we will use multiple models, and they will be grading blindly, without knowing which model produced which answer.

Rating sheets will be produced for the evaluators to use, what elements of the answer provide what score.

Each question will be graded on a scale of 0 to 1

Reports will be produced breaking down score:
- by question category

## Mesaurements


### Measuring Knowledge of specific to the codebase
- questions about specific key classes, key methods
- general knowledge about the structure of the codebase. Human hypervisors will validate questions are timeless and valid regardless of the timing of the training run. Older models can't

example question: what are some of the standards used around unit tests

### knowledge about the architecture of Superset


### Cultural knowledge about the practices and standards used in the Superset community
- 

### Historical questions about Superset Improvement proposals and key events (prior)

**example questions for inspiration **
- how did Superset came to be
