import pytest

from decision_core import Criterion


def test_criterion_allows_valid_values() -> None:
    criterion = Criterion(id="cost", name="Cost", kind="continuous", min_value=0.0)

    assert criterion.id == "cost"
    assert criterion.name == "Cost"
    assert criterion.kind == "continuous"


@pytest.mark.parametrize("criterion_id", ["", "   "])
def test_criterion_rejects_blank_id(criterion_id: str) -> None:
    with pytest.raises(ValueError, match="Criterion id"):
        Criterion(id=criterion_id, name="Cost", kind="continuous")


@pytest.mark.parametrize("name", ["", "   "])
def test_criterion_rejects_blank_name(name: str) -> None:
    with pytest.raises(ValueError, match="Criterion name"):
        Criterion(id="cost", name=name, kind="continuous")


def test_criterion_rejects_invalid_kind() -> None:
    with pytest.raises(ValueError, match="not supported"):
        Criterion(id="cost", name="Cost", kind="ratio")  # type: ignore[arg-type]


def test_categorical_criterion_requires_allowed_values() -> None:
    with pytest.raises(ValueError, match="allowed_values"):
        Criterion(id="stereo", name="Stereo", kind="categorical")


def test_integer_criterion_rejects_non_integer_bounds() -> None:
    with pytest.raises(ValueError, match="must be an integer"):
        Criterion(id="airbags", name="Airbags", kind="integer", min_value=1.5)


def test_criterion_rejects_min_greater_than_max() -> None:
    with pytest.raises(ValueError, match="less than or equal"):
        Criterion(id="cost", name="Cost", kind="continuous", min_value=10.0, max_value=1.0)