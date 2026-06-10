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
    "id",
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
    if not rubric_path.is_file():
        raise ValueError(f"Rubric path is not a file: {path}")

    try:
        with rubric_path.open("r", encoding="utf-8") as file:
            rubric = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Rubric YAML could not be parsed: {error}") from error

    if not isinstance(rubric, dict):
        raise ValueError("Rubric is malformed: top-level YAML must be a mapping.")

    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, dict):
        raise ValueError("Rubric is malformed: missing 'dimensions' mapping.")

    if len(dimensions) != 5:
        raise ValueError(
            f"Rubric is malformed: expected exactly five dimensions, found {len(dimensions)}."
        )

    dimension_ids = []
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

        dimension_id = dimension["id"]
        if not isinstance(dimension_id, str):
            raise ValueError(f"Rubric is malformed: dimension '{key}' id must be a string.")
        if dimension_id != key:
            raise ValueError(
                f"Rubric is malformed: dimension key '{key}' must match id '{dimension_id}'."
            )
        dimension_ids.append(dimension_id)

    if len(dimension_ids) != len(set(dimension_ids)):
        raise ValueError("Rubric is malformed: dimension IDs must be unique.")

    dimension_id_set = set(dimension_ids)
    if dimension_id_set != REQUIRED_DIMENSIONS:
        missing = sorted(REQUIRED_DIMENSIONS - dimension_id_set)
        extra = sorted(dimension_id_set - REQUIRED_DIMENSIONS)
        details = []
        if missing:
            details.append(f"missing required dimension IDs: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected dimension IDs: {', '.join(extra)}")
        raise ValueError("Rubric is malformed: " + "; ".join(details))

    return rubric
