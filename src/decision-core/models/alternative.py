from dataclasses import dataclass


@dataclass(frozen=True)
class Alternative:
    id: str
    name: str
    measurements: dict[str, object]

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Alternative id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("Alternative name must be a non-empty string.")
        if not isinstance(self.measurements, dict):
            raise ValueError("Alternative measurements must be a dictionary.")
        for criterion_id, value in self.measurements.items():
            if not isinstance(criterion_id, str) or not criterion_id.strip():
                raise ValueError("Measurement criterion id must be a non-empty string.")
            if value is None:
                raise ValueError(
                    f"Measurement for criterion '{criterion_id}' must not be None."
                )