from __future__ import annotations

import ast
from numbers import Real
from typing import Mapping

from models import Alternative, Criterion, DecisionProblem, FeasibilityRule
from value import (
    LinearDecreasingValueFunction,
    LinearIncreasingValueFunction,
    MappingCategoricalValueFunction,
    PiecewiseLinearValueFunction,
)


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return value != value
    return False


def _normalize_allowed_values(raw_value: object) -> list[object] | None:
    if _is_missing(raw_value):
        return None
    if isinstance(raw_value, (list, tuple)):
        return list(raw_value)
    if isinstance(raw_value, str):
        text = raw_value.strip()
        if not text:
            return None
        if text.startswith("[") or text.startswith("("):
            try:
                parsed = ast.literal_eval(text)
            except Exception:
                return [text]
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        return [text]
    return None


def _normalize_numeric_bound_for_kind(raw_value: object, kind: str) -> object:
    if _is_missing(raw_value):
        return None
    if kind != "integer":
        return raw_value
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, float) and raw_value.is_integer():
        return int(raw_value)
    return raw_value


def _normalize_predicate_parameter(raw_value: object) -> object:
    if _is_missing(raw_value):
        return None
    if isinstance(raw_value, str):
        text = raw_value.strip()
        if not text:
            return None
        if text == "None":
            return "None"
        try:
            return ast.literal_eval(text)
        except Exception:
            return text
    return raw_value


def _error(stage: str, row_or_key: object, field: str, message: str) -> dict[str, object]:
    return {
        "stage": stage,
        "row_or_key": row_or_key,
        "field": field,
        "message": message,
    }


def _missing_columns(table: object, required_columns: list[str]) -> list[str]:
    columns = set(getattr(table, "columns", []))
    return [column for column in required_columns if column not in columns]


def validate_input_shapes(
    criteria_df: object,
    raw_df: object,
    weights_df: object,
    value_function_specs: Mapping[str, Mapping[str, object]],
    feasibility_df: object | None = None,
    predicate_registry: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []

    criteria_required = ["id", "name", "kind", "min_value", "max_value", "allowed_values"]
    raw_required_base = ["id", "name"]
    weights_required = ["criterion_id", "weight"]
    feasibility_required = ["id", "name", "criterion_id", "predicate_kind", "predicate_param"]

    for column in _missing_columns(criteria_df, criteria_required):
        errors.append(_error("criteria", "table", column, "Missing required column."))
    for column in _missing_columns(raw_df, raw_required_base):
        errors.append(_error("raw", "table", column, "Missing required column."))
    for column in _missing_columns(weights_df, weights_required):
        errors.append(_error("weights", "table", column, "Missing required column."))
    if feasibility_df is not None:
        for column in _missing_columns(feasibility_df, feasibility_required):
            errors.append(_error("feasibility", "table", column, "Missing required column."))

    if errors:
        return errors

    criterion_ids = [str(criterion_id) for criterion_id in criteria_df["id"].tolist()]
    criterion_id_set = set(criterion_ids)

    missing_criteria_columns = [criterion_id for criterion_id in criterion_ids if criterion_id not in raw_df.columns]
    if missing_criteria_columns:
        errors.append(
            _error(
                "raw",
                "table",
                "criteria columns",
                f"Missing measurement columns: {', '.join(missing_criteria_columns)}",
            )
        )

    raw_allowed_columns = set(raw_required_base) | criterion_id_set
    raw_unknown_columns = sorted(column for column in raw_df.columns if column not in raw_allowed_columns)
    if raw_unknown_columns:
        errors.append(_error("raw", "table", "columns", f"Unknown columns: {', '.join(raw_unknown_columns)}"))

    weights_ids = [str(criterion_id) for criterion_id in weights_df["criterion_id"].tolist()]
    weight_id_set = set(weights_ids)
    missing_weight_ids = sorted(criterion_id for criterion_id in criterion_id_set if criterion_id not in weight_id_set)
    unknown_weight_ids = sorted(criterion_id for criterion_id in weight_id_set if criterion_id not in criterion_id_set)
    if missing_weight_ids:
        errors.append(
            _error(
                "weights",
                "table",
                "criterion_id",
                f"Missing weights for: {', '.join(missing_weight_ids)}",
            )
        )
    if unknown_weight_ids:
        errors.append(
            _error(
                "weights",
                "table",
                "criterion_id",
                f"Unknown criterion ids in weights: {', '.join(unknown_weight_ids)}",
            )
        )

    for row in criteria_df.to_dict("records"):
        criterion_id = str(row["id"])
        kind = str(row["kind"])

        allowed_values = _normalize_allowed_values(row.get("allowed_values"))
        if kind in {"ordinal", "categorical"} and not allowed_values:
            errors.append(
                _error(
                    "criteria",
                    criterion_id,
                    "allowed_values",
                    "Required for ordinal and categorical criteria.",
                )
            )

        min_value = _normalize_numeric_bound_for_kind(row.get("min_value"), kind)
        max_value = _normalize_numeric_bound_for_kind(row.get("max_value"), kind)
        if kind in {"continuous", "integer"}:
            if min_value is not None and not isinstance(min_value, Real):
                errors.append(_error("criteria", criterion_id, "min_value", "Must be numeric when provided."))
            if max_value is not None and not isinstance(max_value, Real):
                errors.append(_error("criteria", criterion_id, "max_value", "Must be numeric when provided."))

    for criterion_id, spec in value_function_specs.items():
        if criterion_id not in criterion_id_set:
            errors.append(_error("value_functions", criterion_id, "criterion_id", "Unknown criterion id in spec."))
        if "type" not in spec:
            errors.append(_error("value_functions", criterion_id, "type", "Missing type."))

    if feasibility_df is not None:
        for row in feasibility_df.to_dict("records"):
            rule_id = str(row.get("id"))
            criterion_id = str(row.get("criterion_id"))
            predicate_kind = str(row.get("predicate_kind"))
            predicate_param = _normalize_predicate_parameter(row.get("predicate_param"))

            if criterion_id not in criterion_id_set:
                errors.append(
                    _error("feasibility", rule_id, "criterion_id", f"Unknown criterion id: {criterion_id}")
                )

            if predicate_registry is not None:
                if predicate_kind not in predicate_registry:
                    errors.append(
                        _error(
                            "feasibility",
                            rule_id,
                            "predicate_kind",
                            f"Unsupported predicate kind: {predicate_kind}",
                        )
                    )
                else:
                    predicate_factory = predicate_registry[predicate_kind]
                    try:
                        if predicate_param is None:
                            predicate_factory()
                        else:
                            predicate_factory(predicate_param)
                    except Exception as error:
                        errors.append(
                            _error(
                                "feasibility",
                                rule_id,
                                "predicate_param",
                                f"Invalid predicate parameter for kind '{predicate_kind}': {error}",
                            )
                        )

    return errors


def build_criteria_from_data_frame(criteria_df: object) -> list[Criterion]:
    criteria: list[Criterion] = []
    for row in criteria_df.to_dict("records"):
        kind = str(row["kind"])
        criteria.append(
            Criterion(
                id=str(row["id"]),
                name=str(row["name"]),
                kind=kind,
                min_value=_normalize_numeric_bound_for_kind(row.get("min_value"), kind),
                max_value=_normalize_numeric_bound_for_kind(row.get("max_value"), kind),
                allowed_values=_normalize_allowed_values(row.get("allowed_values")),
            )
        )
    return criteria


def build_alternatives_from_data_frame(criteria: list[Criterion], raw_df: object) -> list[Alternative]:
    alternatives: list[Alternative] = []
    for row in raw_df.to_dict("records"):
        measurements = {
            criterion.id: row[criterion.id]
            for criterion in criteria
        }
        alternatives.append(
            Alternative(
                id=str(row["id"]),
                name=str(row["name"]),
                measurements=measurements,
            )
        )
    return alternatives


def build_decision_problem(
    criteria: list[Criterion],
    alternatives: list[Alternative],
    *,
    problem_id: str = "data-frame-decision-problem",
    problem_name: str = "Data Frame Decision Problem",
) -> DecisionProblem:
    return DecisionProblem(
        id=problem_id,
        name=problem_name,
        criteria=criteria,
        alternatives=alternatives,
    )


def build_value_functions_from_specs(
    value_function_specs: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    value_functions: dict[str, object] = {}
    for criterion_id, spec in value_function_specs.items():
        vf_type = spec["type"]
        if vf_type == "linear_increasing":
            value_functions[criterion_id] = LinearIncreasingValueFunction(
                float(spec["min_raw_value"]),
                float(spec["max_raw_value"]),
            )
        elif vf_type == "linear_decreasing":
            value_functions[criterion_id] = LinearDecreasingValueFunction(
                float(spec["min_raw_value"]),
                float(spec["max_raw_value"]),
            )
        elif vf_type == "piecewise_linear":
            value_functions[criterion_id] = PiecewiseLinearValueFunction(list(spec["points"]))
        elif vf_type == "mapping":
            value_functions[criterion_id] = MappingCategoricalValueFunction(dict(spec["value_mapping"]))
        else:
            raise ValueError(f"Unsupported value-function type for criterion '{criterion_id}': {vf_type}")
    return value_functions


def build_criterion_weights_from_data_frame(weights_df: object) -> dict[str, float]:
    weights: dict[str, float] = {}
    for row in weights_df.to_dict("records"):
        weight = row["weight"]
        if not isinstance(weight, Real):
            raise ValueError(f"weight must be numeric for criterion '{row['criterion_id']}'. Got {weight!r}.")
        weights[str(row["criterion_id"])] = float(weight)
    return weights


def build_default_feasibility_predicate_registry() -> dict[str, object]:
    def requires_true_factory() -> object:
        def predicate(raw_value: object) -> bool:
            return raw_value is True

        return predicate

    def not_equal_factory(expected_value: object) -> object:
        def predicate(raw_value: object) -> bool:
            return raw_value != expected_value

        return predicate

    def gte_factory(minimum_value: object) -> object:
        threshold = float(minimum_value)

        def predicate(raw_value: object) -> bool:
            return float(raw_value) >= threshold

        return predicate

    return {
        "requires_true": requires_true_factory,
        "not_equal": not_equal_factory,
        "gte": gte_factory,
    }


def build_feasibility_rules_from_data_frame(
    feasibility_df: object,
    predicate_registry: Mapping[str, object],
) -> list[FeasibilityRule]:
    feasibility_rules: list[FeasibilityRule] = []
    for row in feasibility_df.to_dict("records"):
        rule_id = str(row["id"])
        predicate_kind = str(row["predicate_kind"])

        if predicate_kind not in predicate_registry:
            raise ValueError(f"Unsupported predicate kind for feasibility rule '{rule_id}': {predicate_kind}")

        predicate_factory = predicate_registry[predicate_kind]
        predicate_param = _normalize_predicate_parameter(row.get("predicate_param"))
        if predicate_param is None:
            predicate = predicate_factory()
        else:
            predicate = predicate_factory(predicate_param)

        feasibility_rules.append(
            FeasibilityRule(
                id=rule_id,
                name=str(row["name"]),
                criterion_id=str(row["criterion_id"]),
                predicate=predicate,
            )
        )

    return feasibility_rules
