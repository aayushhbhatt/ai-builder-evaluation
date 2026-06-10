import hashlib
from pathlib import Path

import streamlit as st

from criteria import load_rubric
from extractor import extract_evidence
from report import build_markdown_report
from verifier import verify_extraction

APP_TITLE = "AI Builder Reviewer Workbench"
DECISION_BOUNDARY = (
    "This tool does not rank, reject, recommend, or select candidates. "
    "Human reviewers remain responsible for all evaluation judgments."
)
DESIGN_PRINCIPLE = "AI replaces the reviewer’s highlighter, not the reviewer."
RUBRIC_PATH = "criteria/ai_builder_rubric.yaml"
SAMPLE_PATHS = {
    "Strong synthetic submission": "sample_submissions/strong_submission.txt",
    "Shallow synthetic submission": "sample_submissions/shallow_submission.txt",
}
MANUAL_SIGNAL_OPTIONS = ["Not assessed", "Weak", "Solid", "Strong"]

SCENARIO_TITLE = "Enterprise AI Builder Scenario"
SCENARIO = """
An enterprise operations team is reviewing short AI Builder work samples. Reviewers
need a consistent way to inspect evidence about problem framing, execution,
workflow fit, responsible AI boundaries, and communication of tradeoffs. The
workbench helps reviewers organize evidence and notes without making candidate
selection decisions.
"""


def load_text_file(path: str) -> str:
    """Load a UTF-8 text file for display in the app."""
    return Path(path).read_text(encoding="utf-8")


def render_extraction_section(extraction: dict) -> None:
    """Render verified AI-assisted evidence separately from reviewer inputs."""
    st.header("AI-Assisted Evidence Extraction with Quote Verification")
    st.warning(
        "AI-extracted quotes are checked using deterministic substring verification. "
        "Reviewers should still inspect evidence before relying on it.",
        icon="⚠️",
    )

    candidate_summary = extraction.get("candidate_summary")
    if candidate_summary:
        st.subheader("Candidate Summary")
        st.write(candidate_summary)

    for dimension in extraction.get("dimensions", []):
        dimension_name = dimension.get(
            "dimension_name", dimension.get("dimension_id", "Rubric dimension")
        )
        with st.container(border=True):
            st.subheader(dimension_name)

            evidence_items = dimension.get("evidence", [])
            if evidence_items:
                st.markdown("**Extracted evidence**")
                for index, evidence in enumerate(evidence_items, start=1):
                    st.markdown(f"**Claim {index}:** {evidence.get('claim', '')}")
                    quote = evidence.get("quote", "")
                    if quote:
                        st.markdown(f"> {quote}")
                    st.markdown(f"**Relevance:** {evidence.get('relevance', '')}")
                    verification = evidence.get("verification", {})
                    verification_message = verification.get(
                        "message",
                        (
                            "Unverified: quote verification status is unavailable. "
                            "Reviewer should inspect before relying on it."
                        ),
                    )
                    if verification.get("verified"):
                        st.success(verification_message, icon="✅")
                    else:
                        st.warning(verification_message, icon="⚠️")
            else:
                st.caption("No evidence extracted for this dimension.")

            missing_or_weak = dimension.get("missing_or_weak_evidence", [])
            if missing_or_weak:
                st.markdown("**Missing or weak evidence**")
                for item in missing_or_weak:
                    st.markdown(f"- {item}")

            follow_up_questions = dimension.get("follow_up_questions", [])
            if follow_up_questions:
                st.markdown("**Follow-up questions**")
                for question in follow_up_questions:
                    st.markdown(f"- {question}")

    overall_questions = extraction.get("overall_follow_up_questions", [])
    if overall_questions:
        st.subheader("Overall Follow-Up Questions")
        for question in overall_questions:
            st.markdown(f"- {question}")

    boundary_notice = extraction.get("ai_boundary_notice")
    if boundary_notice:
        st.info(boundary_notice, icon="🧑‍⚖️")


def render_reviewer_section(rubric: dict) -> None:
    """Render manual reviewer controls for each rubric dimension."""
    st.header("Reviewer Section")
    st.caption(
        "Manual signals and notes are human-entered. The LLM does not assign "
        "reviewer signals or write reviewer notes."
    )

    reviewer_assessment = st.session_state.setdefault("reviewer_assessment", {})

    for dimension in rubric["dimensions"].values():
        dimension_id = dimension["id"]
        with st.container(border=True):
            st.subheader(dimension["name"])
            st.write(dimension["description"])

            with st.expander("Rubric anchors"):
                st.markdown(f"**Weak:** {dimension['weak_anchor']}")
                st.markdown(f"**Solid:** {dimension['solid_anchor']}")
                st.markdown(f"**Strong:** {dimension['strong_anchor']}")

            existing = reviewer_assessment.get(dimension_id, {})
            existing_signal = existing.get("manual_signal", "Not assessed")
            if existing_signal not in MANUAL_SIGNAL_OPTIONS:
                existing_signal = "Not assessed"

            signal_key = f"signal_{dimension_id}"
            notes_key = f"notes_{dimension_id}"
            st.session_state.setdefault(signal_key, existing_signal)
            st.session_state.setdefault(notes_key, existing.get("reviewer_notes", ""))

            signal = st.selectbox(
                "Human-entered manual reviewer signal",
                MANUAL_SIGNAL_OPTIONS,
                key=signal_key,
            )
            notes = st.text_area(
                "Human-entered reviewer notes",
                key=notes_key,
                placeholder="Add human reviewer observations, evidence references, and open questions.",
            )
            reviewer_assessment[dimension_id] = {
                "manual_signal": signal,
                "reviewer_notes": notes,
            }


def submission_fingerprint(selection: str, submission_text: str) -> str:
    """Return a deterministic fingerprint for the active submission."""
    digest = hashlib.sha256()
    digest.update(selection.encode("utf-8"))
    digest.update(b"\0")
    digest.update(submission_text.encode("utf-8"))
    return digest.hexdigest()


def reset_submission_state_if_changed(
    selection: str, submission_text: str, rubric: dict
) -> None:
    """Clear stale extraction, report, and reviewer state when submission changes."""
    fingerprint = submission_fingerprint(selection, submission_text)
    if st.session_state.get("active_submission_fingerprint") == fingerprint:
        return

    st.session_state["active_submission_fingerprint"] = fingerprint
    st.session_state.pop("extraction", None)
    st.session_state.pop("verified_extraction", None)
    st.session_state.pop("markdown_report", None)
    st.session_state["reviewer_assessment"] = {}

    for dimension in rubric["dimensions"].values():
        dimension_id = dimension["id"]
        st.session_state.pop(f"signal_{dimension_id}", None)
        st.session_state.pop(f"notes_{dimension_id}", None)


def render_report_export_section(rubric: dict, selection: str) -> None:
    """Render Markdown report generation, preview, and download controls."""
    st.header("Review Summary Export")
    st.caption(
        "The export summarizes AI-assisted evidence, deterministic quote verification, "
        "and human-entered reviewer assessment. It does not add an automated decision."
    )

    verified_extraction = st.session_state.get("verified_extraction")
    if not verified_extraction:
        st.info("Generate verified evidence before creating a Markdown review summary.")
        return

    if st.button("Generate Review Summary"):
        st.session_state["markdown_report"] = build_markdown_report(
            scenario={"title": SCENARIO_TITLE, "description": SCENARIO.strip()},
            submission_name=selection,
            verified_extraction=verified_extraction,
            reviewer_assessment=st.session_state.get("reviewer_assessment", {}),
            rubric=rubric,
        )

    markdown_report = st.session_state.get("markdown_report")
    if markdown_report:
        with st.expander("Markdown preview", expanded=True):
            st.text_area(
                "Generated Markdown review summary",
                value=markdown_report,
                height=420,
                disabled=True,
            )
        st.download_button(
            "Download Markdown Summary",
            data=markdown_report,
            file_name="ai_builder_review_summary.md",
            mime="text/markdown",
        )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")
    st.title(APP_TITLE)

    st.warning(DECISION_BOUNDARY, icon="⚠️")
    st.info(DESIGN_PRINCIPLE, icon="🖍️")

    st.header(SCENARIO_TITLE)
    st.write(SCENARIO)

    try:
        rubric = load_rubric(RUBRIC_PATH)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    selection = st.sidebar.radio(
        "Submission source",
        [
            "Strong synthetic submission",
            "Shallow synthetic submission",
            "Paste custom submission",
        ],
    )

    if selection in SAMPLE_PATHS:
        submission_text = load_text_file(SAMPLE_PATHS[selection])
    else:
        submission_text = ""

    st.header("Submission")
    submission_text = st.text_area(
        "Work sample text",
        value=submission_text,
        height=360,
        key=f"submission_text_{selection}",
        placeholder="Paste a synthetic or anonymized AI Builder work sample here.",
    )

    reset_submission_state_if_changed(selection, submission_text, rubric)

    if st.button("Extract Evidence"):
        st.session_state.pop("extraction", None)
        st.session_state.pop("verified_extraction", None)
        st.session_state.pop("markdown_report", None)
        with st.spinner("Extracting and verifying evidence for human review..."):
            try:
                extraction = extract_evidence(submission_text, rubric)
                st.session_state["extraction"] = extraction
                st.session_state["verified_extraction"] = verify_extraction(
                    extraction, submission_text
                )
            except RuntimeError as error:
                st.error(str(error))

    if st.session_state.get("verified_extraction"):
        render_extraction_section(st.session_state["verified_extraction"])
    elif st.session_state.get("extraction"):
        render_extraction_section(st.session_state["extraction"])

    render_reviewer_section(rubric)

    render_report_export_section(rubric, selection)

    st.divider()
    st.caption(
        "No automated score, ranking, recommendation, hire/no-hire decision, or pass/fail output is produced."
    )


if __name__ == "__main__":
    main()
