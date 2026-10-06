import pytest

from decision_core import Alternative


def test_alternative_allows_valid_values() -> None:
    alternative = Alternative(
        id="alt-a",
        name="Alternative A",
        measurements={"cost": 1000.0, "airbags": 6, "traction": True, "stereo": "Premium"},
    )

    assert alternative.id == "alt-a"
    assert alternative.name == "Alternative A"
    assert alternative.measurements == {
        "cost": 1000.0,
        "airbags": 6,
        "traction": True,
        "stereo": "Premium",
    }


@pytest.mark.parametrize("alternative_id", ["", "   "])
def test_alternative_rejects_blank_id(alternative_id: str) -> None:
    with pytest.raises(ValueError, match="Alternative id"):
        Alternative(id=alternative_id, name="Alternative A", measurements={"cost": 1.0})


@pytest.mark.parametrize("name", ["", "   "])
def test_alternative_rejects_blank_name(name: str) -> None:
    with pytest.raises(ValueError, match="Alternative name"):
        Alternative(id="alt-a", name=name, measurements={"cost": 1.0})


def test_alternative_rejects_non_mapping_measurements() -> None:
    with pytest.raises(ValueError, match="measurements"):
        Alternative(id="alt-a", name="Alternative A", measurements=None)  # type: ignore[arg-type]


def test_alternative_rejects_none_measurement_value() -> None:
    with pytest.raises(ValueError, match="must not be None"):
        Alternative(
            id="alt-a",
            name="Alternative A",
            measurements={"cost": None},
        )


def test_alternative_rejects_blank_measurement_criterion_id() -> None:
    with pytest.raises(ValueError, match="criterion id"):
        Alternative(id="alt-a", name="Alternative A", measurements={"   ": 1.0})