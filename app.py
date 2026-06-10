from pathlib import Path

import streamlit as st

from criteria import load_rubric
from extractor import extract_evidence
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
    st.caption("Manual signals are reviewer-entered notes, not automated scores.")

    reviewer_inputs = st.session_state.setdefault("reviewer_inputs", {})

    for dimension in rubric["dimensions"].values():
        dimension_id = dimension["id"]
        with st.container(border=True):
            st.subheader(dimension["name"])
            st.write(dimension["description"])

            with st.expander("Rubric anchors"):
                st.markdown(f"**Weak:** {dimension['weak_anchor']}")
                st.markdown(f"**Solid:** {dimension['solid_anchor']}")
                st.markdown(f"**Strong:** {dimension['strong_anchor']}")

            signal = st.selectbox(
                "Manual signal",
                MANUAL_SIGNAL_OPTIONS,
                key=f"signal_{dimension_id}",
            )
            notes = st.text_area(
                "Reviewer notes",
                key=f"notes_{dimension_id}",
                placeholder="Add human reviewer observations, evidence references, and open questions.",
            )
            reviewer_inputs[dimension_id] = {"signal": signal, "notes": notes}


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")
    st.title(APP_TITLE)

    st.warning(DECISION_BOUNDARY, icon="⚠️")
    st.info(DESIGN_PRINCIPLE, icon="🖍️")

    st.header("Enterprise AI Builder Scenario")
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

    if st.button("Extract Evidence"):
        st.session_state.pop("extraction", None)
        st.session_state.pop("verified_extraction", None)
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

    st.divider()
    st.caption(
        "No automated score, ranking, recommendation, hire/no-hire decision, or pass/fail output is produced."
    )


if __name__ == "__main__":
    main()
