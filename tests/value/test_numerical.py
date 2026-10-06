import pytest

from decision_core import (
    LinearDecreasingValueFunction,
    LinearIncreasingValueFunction,
    PiecewiseLinearValueFunction,
)


def test_linear_increasing_interpolates_and_clamps() -> None:
    value_fn = LinearIncreasingValueFunction(min_raw_value=10.0, max_raw_value=20.0)

    assert value_fn.evaluate(10.0) == 0.0
    assert value_fn.evaluate(20.0) == 100.0
    assert value_fn.evaluate(15.0) == pytest.approx(50.0)
    assert value_fn.evaluate(5.0) == 0.0
    assert value_fn.evaluate(25.0) == 100.0


def test_linear_decreasing_interpolates_and_clamps() -> None:
    value_fn = LinearDecreasingValueFunction(min_raw_value=10.0, max_raw_value=20.0)

    assert value_fn.evaluate(10.0) == 100.0
    assert value_fn.evaluate(20.0) == 0.0
    assert value_fn.evaluate(15.0) == pytest.approx(50.0)
    assert value_fn.evaluate(5.0) == 100.0
    assert value_fn.evaluate(25.0) == 0.0


@pytest.mark.parametrize(
    "model_type",
    [LinearIncreasingValueFunction, LinearDecreasingValueFunction],
)
def test_linear_models_reject_invalid_range(model_type: type) -> None:
    with pytest.raises(ValueError, match="requires max_raw_value > min_raw_value"):
        model_type(min_raw_value=5.0, max_raw_value=5.0)


@pytest.mark.parametrize(
    ("model_type", "bound_name", "kwargs"),
    [
        (LinearIncreasingValueFunction, "min_raw_value", {"min_raw_value": "0", "max_raw_value": 1.0}),
        (LinearIncreasingValueFunction, "max_raw_value", {"min_raw_value": 0.0, "max_raw_value": "1"}),
        (LinearDecreasingValueFunction, "min_raw_value", {"min_raw_value": None, "max_raw_value": 1.0}),
        (LinearDecreasingValueFunction, "max_raw_value", {"min_raw_value": 0.0, "max_raw_value": False}),
    ],
)
def test_linear_models_reject_non_numeric_bounds(
    model_type: type,
    bound_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match=rf"requires {bound_name} to be numeric"):
        model_type(**kwargs)


def test_linear_models_reject_boolean_input() -> None:
    value_fn = LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=1.0)

    with pytest.raises(ValueError, match="require numeric input"):
        value_fn.evaluate(True)


def test_piecewise_linear_interpolates_between_points_and_clamps() -> None:
    value_fn = PiecewiseLinearValueFunction(points=((0.0, 0.0), (10.0, 20.0), (20.0, 100.0)))

    assert value_fn.evaluate(-5.0) == 0.0
    assert value_fn.evaluate(0.0) == 0.0
    assert value_fn.evaluate(5.0) == pytest.approx(10.0)
    assert value_fn.evaluate(15.0) == pytest.approx(60.0)
    assert value_fn.evaluate(20.0) == 100.0
    assert value_fn.evaluate(25.0) == 100.0


def test_piecewise_linear_supports_integer_and_ordinal_like_numeric_inputs() -> None:
    value_fn = PiecewiseLinearValueFunction(points=((1, 0.0), (5, 100.0)))

    assert value_fn.evaluate(3) == pytest.approx(50.0)
    assert value_fn.evaluate(4.0) == pytest.approx(75.0)


def test_piecewise_linear_rejects_unsorted_points() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        PiecewiseLinearValueFunction(points=((0.0, 0.0), (0.0, 0.5), (2.0, 1.0)))


def test_piecewise_linear_rejects_out_of_range_values() -> None:
    with pytest.raises(ValueError, match=r"range \[0.0, 100.0\]"):
        PiecewiseLinearValueFunction(points=((0.0, -0.1), (1.0, 1.0)))


def test_piecewise_linear_requires_at_least_two_points() -> None:
    with pytest.raises(ValueError, match="at least two points"):
        PiecewiseLinearValueFunction(points=((0.0, 0.0),))
