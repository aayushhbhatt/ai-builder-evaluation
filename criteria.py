from pathlib import Path
from typing import Any

import yaml

REQUIRED_DIMENSIONS = {
    "problem_framing",
    "builder_execution",
    "workflow_systems_thinking",
    "responsible_ai",
    "tradeoffs_communication",
}

REQUIRED_FIELDS = {
    "name",
    "description",
    "weak_anchor",
    "solid_anchor",
    "strong_anchor",
}


def load_rubric(path: str) -> dict[str, Any]:
    """Load and validate the AI Builder reviewer rubric from YAML."""
    rubric_path = Path(path)
    if not rubric_path.exists():
        raise ValueError(f"Rubric file not found: {path}")

    with rubric_path.open("r", encoding="utf-8") as file:
        rubric = yaml.safe_load(file)

    if not isinstance(rubric, dict):
        raise ValueError("Rubric is malformed: top-level YAML must be a mapping.")

    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, dict):
        raise ValueError("Rubric is malformed: missing 'dimensions' mapping.")

    dimension_keys = set(dimensions.keys())
    if dimension_keys != REQUIRED_DIMENSIONS:
        missing = sorted(REQUIRED_DIMENSIONS - dimension_keys)
        extra = sorted(dimension_keys - REQUIRED_DIMENSIONS)
        details = []
        if missing:
            details.append(f"missing dimensions: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected dimensions: {', '.join(extra)}")
        raise ValueError("Rubric is malformed: " + "; ".join(details))

    for key, dimension in dimensions.items():
        if not isinstance(dimension, dict):
            raise ValueError(f"Rubric is malformed: dimension '{key}' must be a mapping.")
        missing_fields = REQUIRED_FIELDS - set(dimension.keys())
        if missing_fields:
            raise ValueError(
                f"Rubric is malformed: dimension '{key}' is missing fields: "
                + ", ".join(sorted(missing_fields))
            )
        empty_fields = [field for field in REQUIRED_FIELDS if not dimension.get(field)]
        if empty_fields:
            raise ValueError(
                f"Rubric is malformed: dimension '{key}' has empty fields: "
                + ", ".join(sorted(empty_fields))
            )

    return rubric
