from typing import Any


def extract_evidence(submission_text: str, rubric: dict[str, Any]) -> dict[str, Any]:
    """Return placeholder evidence extraction for a submission and rubric.

    This file will later call the OpenAI API to extract cited evidence from the
    submission text. The extraction should support human review only and must not
    generate scores, rankings, recommendations, or hire/no-hire outputs.
    """
    dimensions = rubric.get("dimensions", {})
    return {
        "status": "placeholder",
        "ai_use_disclosure": "OpenAI extraction is not implemented in milestone 1.",
        "submission_character_count": len(submission_text),
        "dimensions": {
            key: {
                "dimension_name": value.get("name", key),
                "evidence": [],
                "notes": "Evidence extraction placeholder; reviewer should inspect the submission manually.",
            }
            for key, value in dimensions.items()
        },
    }
