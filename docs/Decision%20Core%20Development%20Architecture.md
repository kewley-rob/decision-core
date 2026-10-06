# Decision Core Development Architecture

## Purpose

Build a small, testable Python decision-analysis core incrementally using AI coding agents. The architecture should remain easy to change as the domain model and production approach evolve.

The core should initially be usable directly from Python and Jupyter, without requiring an API, database, or UI. Those concerns can be added later as adapters around the core.

## Guiding Principles

- Keep the analytical core independent of FastAPI, databases, notebooks, and visualization frameworks.
- Prefer explicit, typed Python models over loosely structured dictionaries.
- Keep domain concepts separate from algorithm implementations where practical.
- Add capabilities in small increments with tests at every step.
- Preserve simple public APIs even if internal implementations change.
- Avoid premature abstraction. Refactor only when the next capability creates a clear need.
- Favor deterministic, inspectable calculations suitable for teaching and consulting.
- Use established Python libraries where they add clear value, but do not make them part of the domain model.

## Initial Package Shape

Start simple. A likely package structure is:

```text
decision_core/
    models/
    value/
    weighting/
    scoring/
    sensitivity/
    pareto/

tests/
examples/
```

This is a starting point, not a constraint. Allow the structure to evolve as the domain becomes clearer.

---

# Incremental Development Path

## Step 1 — Core Data Structures

Create the smallest useful domain model for representing a decision problem.

Implemented concepts:

- `DecisionProblem`
- `Alternative`
- `Criterion`
- criterion measurements / raw values
- identifiers and names

Implemented requirements:

- typed Python dataclass models in `decision_core.models`
- basic validation:
  - non-empty IDs and names
  - unique criterion IDs and alternative IDs in `DecisionProblem`
  - each alternative must provide measurements for all declared criteria
  - alternatives cannot include unknown criterion IDs
- creation and inspection from normal Python code
- unit tests for valid and invalid construction paths

Do not add persistence, APIs, or optimization yet.

**Agent goal:** Establish a clean domain model that later analytical capabilities can operate on without depending on external infrastructure.

---

## Step 2 — Criteria

Expand the criterion model to capture the semantics needed for decision analysis.

Implemented capabilities:

- typed criterion domains with kind-specific validation
- validation of missing or invalid alternative measurements through `DecisionProblem`
- criterion definitions remain independent from weighting and scoring

Supported criterion kinds:

- `continuous`: numeric raw values (`int`/`float`, excluding `bool`) with optional `min_value` / `max_value`
- `integer`: integer raw values (`int`, excluding `bool`) with optional integer `min_value` / `max_value`
- `boolean`: raw values must be `True`/`False`
- `ordinal`: raw values must be in an explicit `allowed_values` sequence (ordered rank labels)
- `categorical`: raw values must be in an explicit set of string `allowed_values`

Planned next criteria semantics (not yet implemented):

- units and descriptions
- richer acceptable value constraints beyond current type/domain checks

Keep criterion definitions independent from weighting and scoring.

**Agent goal:** Make criteria expressive enough to support value models without prematurely encoding a specific decision method.

---

## Step 3 — Value Models

Add transformation of raw criterion measurements into decision value.

### Part A - Numerical Value Models

Implemented capabilities:

- `decision_core.value` package with a common numerical value-function abstraction
- linear increasing value function
- linear decreasing value function
- piecewise linear interpolation value function with boundary clamping
- numerical value scores defined directly on a `0..100` scale

Supported usage:

- applies to continuous and integer criteria
- supports ordinal-as-numeric usage when ordinal levels are modeled numerically

Implemented validation and behavior:

- non-numeric inputs are rejected
- invalid model definitions are rejected (e.g., invalid linear ranges, unsorted or malformed piecewise points)
- piecewise point `y` values must be in `[0.0, 100.0]`

Implemented tests:

- boundary clamping behavior
- interpolation behavior
- invalid model-definition and input scenarios

### Part B - Categorical Value Models

Implemented capabilities:

- categorical value-model abstractions in `decision_core.value`
- explicit raw-category/label -> value-score mappings for boolean, ordinal, and categorical raw values
- strict evaluation behavior for unknown raw categories

Implemented validation and behavior:

- mapping must be non-empty
- mapping keys cannot be `None`
- mapped scores must be numeric (excluding `bool`) and in `0..100`

Implemented tests:

- valid boolean, integer-ordinal, and string-categorical mappings
- invalid mapping definitions and unknown category evaluation paths

### Part C - Total Value Model and Raw Feasibility Screening

Implemented capabilities:

- `TotalValueModel` in `decision_core.models` to bind a value-function set to a specific `DecisionProblem`
- explicit `criterion_id -> value_function` pairing with full-coverage validation
- `FeasibilityRule` in `decision_core.models` for typed raw-data pass/fail predicates
- model-owned raw feasibility screening via `TotalValueModel.feasibility_rules`

Implemented validation and behavior:

- `TotalValueModel` requires non-empty `id`/`name` and non-empty value-function mapping
- mapped criterion IDs must exist in the paired `DecisionProblem`
- all decision criteria must be covered by value functions
- feasibility rules must be valid `FeasibilityRule` instances with unique IDs
- feasibility predicates must return `bool`

Current evaluation flow in the car example:

```text
raw alternative measurements
    -> raw feasibility screening (all rules must pass)
    -> criterion value-function evaluation via TotalValueModel
    -> value-score matrix (0..100 per alternative/criterion cell)
```

```text
raw measurement -> value function -> value score (0..100)
```

**Agent goal:** Create an extensible but simple mechanism for converting heterogeneous measures into comparable value scores.

---

## Step 4 — Swing Weights

Add criterion weighting based on swing-weight concepts.

Initial capabilities should include:

- storing criterion weights
- validating weights
- normalization of weights
- construction of a weight set for a decision problem

Do not over-model elicitation workflows initially. The first implementation only needs to represent and apply the resulting weights.

**Agent goal:** Provide a clear representation of preference importance that can later support richer elicitation techniques.

---

## Step 5 — Solution Scoring

Implement the first complete decision evaluation workflow.

For each alternative:

1. obtain criterion measurements
2. convert measurements to criterion values
3. apply weights
4. aggregate into an overall score
5. produce a ranked result

Return a structured result containing both the overall score and criterion-level contributions so the result remains explainable.

**Agent goal:** Produce an end-to-end weighted additive value model suitable for use from Python and Jupyter.

---

## Step 6 — Sensitivity Analysis

Add analysis of how decision results change when assumptions change.

Start with weight sensitivity rather than trying to build a general uncertainty framework immediately.

Useful initial outputs:

- changed rankings
- score ranges
- break-even / crossover behavior where practical
- structured sensitivity results suitable for later visualization

Keep visualization outside the analytical implementation.

**Agent goal:** Make the decision recommendation inspectable rather than treating the calculated ranking as absolute.

---

## Step 7 — Pareto Analysis

Add objective-space comparison independent of preference weights.

Initial capabilities:

- dominance testing
- identification of non-dominated alternatives
- Pareto-front extraction
- support for mixed maximize/minimize criteria

Return structured data rather than plots. Visualization can consume the Pareto results later.

**Agent goal:** Separate preference-based ranking from objective trade-space analysis.

---

# Likely Next Capabilities

Do not implement these until the initial core is stable, but keep the architecture capable of accommodating them:

- uncertainty and Monte Carlo analysis
- SMART / SMARTER extensions
- richer weighting and elicitation methods
- alternative ranking methods
- visualization adapters using Plotly
- pandas import/export
- JSON/Pydantic serialization
- PostgreSQL persistence
- FastAPI service wrapper
- experiment and simulation-result integration
- multi-objective optimization using libraries such as pymoo

---

# AI-Agent Working Pattern

For each step, give the coding agent only the current capability plus the existing repository context.

A useful instruction pattern is:

> Implement the next capability in `Decision Core Development Architecture.md`. Preserve the existing public behavior unless there is a clear architectural reason to change it. Keep the implementation small, typed, independently testable, and free of API/database/UI dependencies. Add or update tests and briefly identify any architectural decisions that should be revisited before the next step.

Before moving to the next step:

1. run the complete test suite
2. review the public model/API
3. remove unnecessary abstractions
4. update this document if the architecture has materially changed
5. commit the working increment

The development sequence is intentionally negotiable. Change later steps when experience with earlier steps reveals a better domain model or architecture.

---

# Initial Definition of Done

The first Decision Core milestone is complete when Python code can:

```text
define a decision problem
        -> define criteria
        -> define alternatives and measurements
        -> apply value functions
        -> apply swing weights
        -> score and rank alternatives
        -> test ranking sensitivity
        -> identify Pareto-efficient alternatives
```

All of this should work as a standalone Python library with automated tests and no required external services.
