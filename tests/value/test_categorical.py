import pytest

from decision_core import MappingCategoricalValueFunction


def test_mapping_model_evaluates_boolean_inputs() -> None:
    value_fn = MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0})

    assert value_fn.evaluate(False) == 0.0
    assert value_fn.evaluate(True) == 100.0


def test_mapping_model_evaluates_ordinal_integer_inputs() -> None:
    value_fn = MappingCategoricalValueFunction(value_mapping={1: 0.0, 2: 0.0, 3: 10.0, 4: 50.0, 5: 100.0})

    assert value_fn.evaluate(1) == 0.0
    assert value_fn.evaluate(3) == 10.0
    assert value_fn.evaluate(5) == 100.0


def test_mapping_model_evaluates_string_category_inputs() -> None:
    value_fn = MappingCategoricalValueFunction(
        value_mapping={
            "None": 0.0,
            "Subscription": 30.0,
            "Wired Car Play": 60.0,
            "Wireless Car Play": 100.0,
        }
    )

    assert value_fn.evaluate("None") == 0.0
    assert value_fn.evaluate("Subscription") == 30.0
    assert value_fn.evaluate("Wireless Car Play") == 100.0


def test_mapping_model_rejects_unknown_category_input() -> None:
    value_fn = MappingCategoricalValueFunction(value_mapping={"A": 10.0})

    with pytest.raises(ValueError, match="Unknown categorical value"):
        value_fn.evaluate("B")


def test_mapping_model_rejects_empty_mapping() -> None:
    with pytest.raises(ValueError, match="at least one mapping entry"):
        MappingCategoricalValueFunction(value_mapping={})


def test_mapping_model_rejects_none_category_key() -> None:
    with pytest.raises(ValueError, match="does not allow None"):
        MappingCategoricalValueFunction(value_mapping={None: 10.0})


def test_mapping_model_rejects_non_numeric_score() -> None:
    with pytest.raises(ValueError, match="require numeric scores"):
        MappingCategoricalValueFunction(value_mapping={"A": "high"})


def test_mapping_model_rejects_out_of_range_score() -> None:
    with pytest.raises(ValueError, match=r"range \[0.0, 100.0\]"):
        MappingCategoricalValueFunction(value_mapping={"A": 101.0})
