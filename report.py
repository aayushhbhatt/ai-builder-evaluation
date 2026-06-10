from datetime import datetime, timezone
from typing import Any


DECISION_BOUNDARY = (
    "This workbench does not rank, reject, recommend, or select candidates. "
    "Human reviewers remain responsible for all evaluation judgments."
)
AI_USE_DISCLOSURE = (
    "AI extracted evidence and suggested questions from the submitted work sample. "
    "Deterministic code checked whether extracted quotes were present in the source text. "
    "Humans manually applied the rubric, entered assessment signals and notes, and remain "
    "responsible for all consequential decisions."
)


def _safe_text(value: Any, default: str = "") -> str:
    """Return plain text suitable for normal Markdown display."""
    if value is None:
        return default
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
    return text if text else default


def _bullet_list(items: Any, empty_message: str) -> list[str]:
    """Format an optional list as Markdown bullets without inventing content."""
    if not isinstance(items, list) or not items:
        return [empty_message]

    lines = []
    for item in items:
        text = _safe_text(item)
        if text:
            lines.append(f"- {text}")
    return lines or [empty_message]


def _blockquote(text: Any, empty_message: str = "No quote provided.") -> list[str]:
    """Format text as a Markdown blockquote, including multiline normal text."""
    safe = _safe_text(text, empty_message)
    return [f"> {line}" if line else ">" for line in safe.split("\n")]


def _dimensions_by_id(verified_extraction: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dimensions = verified_extraction.get("dimensions", [])
    if not isinstance(dimensions, list):
        return {}

    by_id: dict[str, dict[str, Any]] = {}
    for dimension in dimensions:
        if not isinstance(dimension, dict):
            continue
        dimension_id = dimension.get("dimension_id")
        if isinstance(dimension_id, str) and dimension_id:
            by_id[dimension_id] = dimension
    return by_id


def build_markdown_report(
    scenario: dict,
    submission_name: str,
    verified_extraction: dict,
    reviewer_assessment: dict,
    rubric: dict,
    review_metadata: dict | None = None,
) -> str:
    """Build a deterministic Markdown review summary for human reviewers.

    This function only formats already-available AI-assisted evidence,
    deterministic verification results, and human-entered reviewer assessments.
    It does not call an LLM, score, rank, or infer reviewer judgment.
    """
    scenario = scenario if isinstance(scenario, dict) else {}
    verified_extraction = (
        verified_extraction if isinstance(verified_extraction, dict) else {}
    )
    reviewer_assessment = (
        reviewer_assessment if isinstance(reviewer_assessment, dict) else {}
    )
    rubric = rubric if isinstance(rubric, dict) else {}
    review_metadata = review_metadata if isinstance(review_metadata, dict) else None

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    scenario_title = _safe_text(scenario.get("title"), "Untitled scenario")
    dimensions_by_id = _dimensions_by_id(verified_extraction)
    rubric_dimensions = rubric.get("dimensions", {})
    if not isinstance(rubric_dimensions, dict):
        rubric_dimensions = {}

    lines = [
        "# AI Builder Work Sample Review Summary",
        "",
        "## Review Context",
        f"- **Scenario:** {scenario_title}",
        f"- **Submission:** {_safe_text(submission_name, 'Unnamed submission')}",
        f"- **Generated:** {generated_at}",
    ]

    if review_metadata:
        metadata_fields = [
            ("Application version", review_metadata.get("app_version")),
            ("Model", review_metadata.get("model")),
            ("Prompt version", review_metadata.get("prompt_version")),
            ("Rubric SHA-256", review_metadata.get("rubric_sha256")),
        ]
        for label, value in metadata_fields:
            if value:
                lines.append(f"- **{label}:** {_safe_text(value)}")

    lines.extend([
        "",
        "## Decision Boundary",
        DECISION_BOUNDARY,
        "",
        "## AI-Assisted Candidate Summary",
        "This summary is AI-assisted and should be checked by a human reviewer.",
        "",
        _safe_text(
            verified_extraction.get("candidate_summary"),
            "No candidate summary was generated.",
        ),
        "",
        "## Evidence and Human Assessment",
    ])

    for dimension in rubric_dimensions.values():
        if not isinstance(dimension, dict):
            continue

        dimension_id = _safe_text(dimension.get("id"))
        dimension_name = _safe_text(dimension.get("name"), dimension_id)
        extracted_dimension = dimensions_by_id.get(dimension_id, {})
        assessment = reviewer_assessment.get(dimension_id, {})
        if not isinstance(assessment, dict):
            assessment = {}

        manual_signal = _safe_text(assessment.get("manual_signal"), "Not assessed")
        reviewer_notes = _safe_text(assessment.get("reviewer_notes"), "")

        lines.extend(
            [
                "",
                f"### {dimension_name}",
                "",
                f"**Dimension ID:** `{dimension_id}`",
                "",
                f"**Description:** {_safe_text(dimension.get('description'), 'No description provided.')}",
                "",
                "#### AI-Extracted Evidence",
            ]
        )

        evidence_items = extracted_dimension.get("evidence", [])
        if not isinstance(evidence_items, list) or not evidence_items:
            lines.extend(["", "No evidence was extracted."])
        else:
            for index, evidence in enumerate(evidence_items, start=1):
                if not isinstance(evidence, dict):
                    continue
                verification = evidence.get("verification", {})
                if not isinstance(verification, dict):
                    verification = {}
                verification_status = (
                    "Verified" if verification.get("verified") else "Unverified"
                )
                verification_message = _safe_text(
                    verification.get("message"),
                    "Unverified: quote verification status is unavailable. Reviewer should inspect before relying on it.",
                )

                lines.extend(
                    [
                        "",
                        f"**Evidence item {index}**",
                        "",
                        f"- **Claim:** {_safe_text(evidence.get('claim'), 'No claim provided.')}",
                        "- **Quote:**",
                        *_blockquote(evidence.get("quote")),
                        f"- **Relevance:** {_safe_text(evidence.get('relevance'), 'No relevance provided.')}",
                        f"- **Verification status:** {verification_status}",
                        f"- **Verification message:** {verification_message}",
                    ]
                )

        lines.extend(
            [
                "",
                "#### Missing or Weak Evidence",
                *_bullet_list(
                    extracted_dimension.get("missing_or_weak_evidence", []),
                    "No missing or weak evidence was identified by the extraction.",
                ),
                "",
                "#### Human-Entered Reviewer Assessment",
                f"- **Manual reviewer signal:** {manual_signal}",
                f"- **Reviewer notes:** {reviewer_notes if reviewer_notes else 'No reviewer notes entered.'}",
                "",
                "#### Suggested Follow-Up Questions",
                *_bullet_list(
                    extracted_dimension.get("follow_up_questions", []),
                    "No dimension-specific follow-up questions were suggested.",
                ),
            ]
        )

    lines.extend(
        [
            "",
            "## Overall Suggested Follow-Up Questions",
            *_bullet_list(
                verified_extraction.get("overall_follow_up_questions", []),
                "No overall follow-up questions were suggested.",
            ),
            "",
            "## AI-Use Disclosure",
            AI_USE_DISCLOSURE,
            "",
        ]
    )

    return "\n".join(lines)
