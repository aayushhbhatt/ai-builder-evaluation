from typing import Any


DECISION_BOUNDARY = (
    "This tool does not rank, reject, recommend, or select candidates. "
    "Human reviewers remain responsible for all evaluation judgments."
)


def build_markdown_report(
    submission_label: str,
    extraction: dict[str, Any] | None = None,
    reviewer_notes: dict[str, Any] | None = None,
) -> str:
    """Build a simple placeholder Markdown report for milestone 1."""
    _ = extraction
    _ = reviewer_notes
    return f"""# AI Builder Reviewer Workbench Report

## Decision Boundary
{DECISION_BOUNDARY}

## AI-Use Disclosure
Placeholder: automated evidence extraction is not implemented in milestone 1.

## Submission
{submission_label}

## Reviewer Notes
Placeholder: full report export will be implemented in a later milestone.
"""
