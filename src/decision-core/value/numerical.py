from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from numbers import Number
from typing import Protocol, Union, runtime_checkable


NumericInput = Union[float, int]


def coerce_numeric_input(raw_value: object) -> float:
    if not isinstance(raw_value, Number) or isinstance(raw_value, bool):
        raise ValueError("Numerical value models require numeric input (int/float, excluding bool).")
    return float(raw_value)


def coerce_numeric_bound(raw_value: object, bound_name: str, model_name: str) -> float:
    if not isinstance(raw_value, Number) or isinstance(raw_value, bool):
        raise ValueError(
            f"{model_name} requires {bound_name} to be numeric (int/float, excluding bool)."
        )
    return float(raw_value)


@runtime_checkable
class NumericalValueFunction(Protocol):
    def evaluate(self, raw_value: NumericInput) -> float:
        ...

    def __call__(self, raw_value: NumericInput) -> float:
        ...


class BaseNumericalValueFunction(ABC):
    def __call__(self, raw_value: NumericInput) -> float:
        return self.evaluate(raw_value)

    @abstractmethod
    def evaluate(self, raw_value: NumericInput) -> float:
        raise NotImplementedError


@dataclass(frozen=True)
class LinearIncreasingValueFunction(BaseNumericalValueFunction):
    min_raw_value: float
    max_raw_value: float

    def __post_init__(self) -> None:
        min_raw_value = coerce_numeric_bound(
            self.min_raw_value,
            bound_name="min_raw_value",
            model_name="Linear increasing value model",
        )
        max_raw_value = coerce_numeric_bound(
            self.max_raw_value,
            bound_name="max_raw_value",
            model_name="Linear increasing value model",
        )
        object.__setattr__(self, "min_raw_value", min_raw_value)
        object.__setattr__(self, "max_raw_value", max_raw_value)
        if self.max_raw_value <= self.min_raw_value:
            raise ValueError("Linear increasing value model requires max_raw_value > min_raw_value.")

    def evaluate(self, raw_value: NumericInput) -> float:
        x = coerce_numeric_input(raw_value)
        if x <= self.min_raw_value:
            return 0.0
        if x >= self.max_raw_value:
            return 100.0
        return 100.0 * (x - self.min_raw_value) / (self.max_raw_value - self.min_raw_value)


@dataclass(frozen=True)
class LinearDecreasingValueFunction(BaseNumericalValueFunction):
    min_raw_value: float
    max_raw_value: float

    def __post_init__(self) -> None:
        min_raw_value = coerce_numeric_bound(
            self.min_raw_value,
            bound_name="min_raw_value",
            model_name="Linear decreasing value model",
        )
        max_raw_value = coerce_numeric_bound(
            self.max_raw_value,
            bound_name="max_raw_value",
            model_name="Linear decreasing value model",
        )
        object.__setattr__(self, "min_raw_value", min_raw_value)
        object.__setattr__(self, "max_raw_value", max_raw_value)
        if self.max_raw_value <= self.min_raw_value:
            raise ValueError("Linear decreasing value model requires max_raw_value > min_raw_value.")

    def evaluate(self, raw_value: NumericInput) -> float:
        x = coerce_numeric_input(raw_value)
        if x <= self.min_raw_value:
            return 100.0
        if x >= self.max_raw_value:
            return 0.0
        return 100.0 * (self.max_raw_value - x) / (self.max_raw_value - self.min_raw_value)


@dataclass(frozen=True)
class PiecewiseLinearValueFunction(BaseNumericalValueFunction):
    points: tuple[tuple[NumericInput, float], ...]

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("Piecewise linear value model requires at least two points.")

        normalized_points: list[tuple[float, float]] = []
        for raw_x, raw_y in self.points:
            x = coerce_numeric_input(raw_x)
            y = coerce_numeric_input(raw_y)
            if y < 0.0 or y > 100.0:
                raise ValueError("Piecewise linear point values must be in the range [0.0, 100.0].")
            normalized_points.append((x, y))

        for index in range(1, len(normalized_points)):
            previous_x = normalized_points[index - 1][0]
            current_x = normalized_points[index][0]
            if current_x <= previous_x:
                raise ValueError("Piecewise linear points must have strictly increasing x values.")

        object.__setattr__(self, "points", tuple(normalized_points))

    def evaluate(self, raw_value: NumericInput) -> float:
        x = coerce_numeric_input(raw_value)
        first_x, first_y = self.points[0]
        last_x, last_y = self.points[-1]

        if x <= first_x:
            return first_y
        if x >= last_x:
            return last_y

        for index in range(1, len(self.points)):
            right_x, right_y = self.points[index]
            left_x, left_y = self.points[index - 1]
            if x <= right_x:
                span = right_x - left_x
                ratio = (x - left_x) / span
                return left_y + ratio * (right_y - left_y)

        return last_y
