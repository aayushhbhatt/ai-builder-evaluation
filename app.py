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


def apply_dark_theme() -> None:
    """Apply a simple high-contrast dark presentation without external assets."""
    st.markdown(
        """
        <style>
        .stApp {
            background: #0f172a;
            color: #e5e7eb;
        }
        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #334155;
        }
        [data-testid="stHeader"] {
            background: rgba(15, 23, 42, 0.95);
        }
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: #e5e7eb;
        }
        h1, h2, h3, h4, h5, h6, label, .stCaptionContainer {
            color: #f8fafc !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #f8fafc !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"],
        details[data-testid="stExpander"] {
            background: #111827;
            border-color: #334155 !important;
        }
        details[data-testid="stExpander"] summary p {
            color: #f8fafc !important;
        }
        textarea, input, [data-baseweb="select"] > div {
            background: #020617 !important;
            color: #f8fafc !important;
            border-color: #475569 !important;
        }
        textarea::placeholder, input::placeholder {
            color: #94a3b8 !important;
        }
        div.stButton > button,
        div.stDownloadButton > button {
            background: #f8fafc !important;
            color: #111827 !important;
            border: 1px solid #cbd5e1 !important;
            font-weight: 700 !important;
        }
        div.stButton > button:hover,
        div.stDownloadButton > button:hover {
            background: #e2e8f0 !important;
            color: #020617 !important;
            border-color: #f8fafc !important;
        }
        div.stButton > button *,
        div.stDownloadButton > button * {
            color: #111827 !important;
        }
        div[role="button"][aria-haspopup="listbox"],
        div[role="button"][aria-haspopup="listbox"] * {
            color: #f8fafc !important;
        }
        .compact-boundary {
            border-left: 4px solid #f59e0b;
            padding: 0.55rem 0.75rem;
            background: #1f2937;
            border-radius: 0.35rem;
            color: #f8fafc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render compact sidebar context without hiding the scenario in an expander."""
    with st.sidebar:
        st.divider()
        st.subheader(SCENARIO_TITLE)
        st.write(SCENARIO)


def render_page_header() -> None:
    """Render compact first-load context and the required decision boundary."""
    st.title(APP_TITLE)
    st.caption("Human-led review supported by AI-assisted evidence extraction")
    st.markdown(
        f'<div class="compact-boundary">{DECISION_BOUNDARY}</div>',
        unsafe_allow_html=True,
    )
    st.divider()


def render_extraction_section(extraction: dict) -> None:
    """Render verified AI-assisted evidence separately from reviewer inputs."""
    st.header("2. AI Evidence")
    st.caption(
        "AI-assisted evidence is organized by rubric dimension. Quote checks are "
        "deterministic substring checks against the source submission."
    )

    candidate_summary = extraction.get("candidate_summary")
    if candidate_summary:
        with st.container(border=True):
            st.subheader("AI-Assisted Candidate Summary")
            st.write(candidate_summary)

    st.subheader("Evidence by Rubric Dimension")
    for dimension_index, dimension in enumerate(extraction.get("dimensions", [])):
        dimension_name = dimension.get(
            "dimension_name", dimension.get("dimension_id", "Rubric dimension")
        )
        with st.expander(dimension_name, expanded=dimension_index == 0):
            evidence_items = dimension.get("evidence", [])
            if evidence_items:
                st.markdown("**Evidence items**")
                for index, evidence in enumerate(evidence_items, start=1):
                    st.markdown(f"**Claim {index}:** {evidence.get('claim', '')}")
                    quote = evidence.get("quote", "")
                    if quote:
                        st.markdown("**Quote:**")
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
                        st.success(
                            "✅ Verified — quote found in source submission",
                            icon="✅",
                        )
                    else:
                        st.warning(
                            "⚠️ Unverified — reviewer inspection required",
                            icon="⚠️",
                        )
                    st.caption(verification_message)
                    if index < len(evidence_items):
                        st.divider()
            else:
                st.info("No evidence extracted for this dimension.")

            missing_or_weak = dimension.get("missing_or_weak_evidence", [])
            if missing_or_weak:
                st.markdown("**Missing or weak evidence**")
                for item in missing_or_weak:
                    st.markdown(f"- {item}")

            follow_up_questions = dimension.get("follow_up_questions", [])
            if follow_up_questions:
                st.markdown("**Suggested follow-up questions**")
                for question in follow_up_questions:
                    st.markdown(f"- {question}")

    overall_questions = extraction.get("overall_follow_up_questions", [])
    if overall_questions:
        with st.container(border=True):
            st.subheader("Overall Follow-Up Questions")
            for question in overall_questions:
                st.markdown(f"- {question}")

    boundary_notice = extraction.get("ai_boundary_notice")
    if boundary_notice:
        st.info(boundary_notice, icon="🧑‍⚖️")


def render_reviewer_section(rubric: dict) -> None:
    """Render manual reviewer controls for each rubric dimension."""
    st.header("3. Human Review")
    st.caption("Signals and notes in this section are entered by the human reviewer.")

    reviewer_assessment = st.session_state.setdefault("reviewer_assessment", {})

    for dimension_index, dimension in enumerate(rubric["dimensions"].values()):
        dimension_id = dimension["id"]
        with st.expander(dimension["name"], expanded=dimension_index == 0):
            st.write(dimension["description"])

            with st.expander("Behavioral anchors"):
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


def render_submission_section(selection: str, rubric: dict) -> str:
    """Render submission input and extraction action while preserving widget behavior."""
    st.header("1. Submission")
    st.caption(
        "Select or paste a candidate submission to begin, then extract evidence for human review."
    )

    if selection in SAMPLE_PATHS:
        submission_text = load_text_file(SAMPLE_PATHS[selection])
    else:
        submission_text = ""

    submission_text = st.text_area(
        "Work sample text",
        value=submission_text,
        height=360,
        key=f"submission_text_{selection}",
        placeholder="Paste a synthetic or anonymized AI Builder work sample here.",
    )

    st.caption(f"Submission characters: {len(submission_text)}")
    if not submission_text.strip():
        st.info("Select or paste a candidate submission to begin.")

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

    return submission_text


def render_report_export_section(rubric: dict, selection: str) -> None:
    """Render Markdown report generation, preview, and download controls."""
    st.header("4. Export")
    st.caption(
        "The review summary combines AI-assisted evidence, deterministic quote "
        "verification, and human-entered reviewer assessment."
    )

    verified_extraction = st.session_state.get("verified_extraction")
    if not verified_extraction:
        st.info("Complete evidence extraction and generate a review summary.")
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
    else:
        st.info(
            "No report yet. Generate a review summary when the human review notes are ready."
        )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")
    apply_dark_theme()

    try:
        rubric = load_rubric(RUBRIC_PATH)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    st.sidebar.subheader("Submission Source")
    selection = st.sidebar.radio(
        "Submission source",
        [
            "Strong synthetic submission",
            "Shallow synthetic submission",
            "Paste custom submission",
        ],
    )

    render_page_header()
    render_sidebar()

    render_submission_section(selection, rubric)

    st.divider()
    verified_extraction = st.session_state.get("verified_extraction")
    if verified_extraction:
        render_extraction_section(verified_extraction)
    elif st.session_state.get("extraction"):
        render_extraction_section(st.session_state["extraction"])
    else:
        st.header("2. AI Evidence")
        st.info("Run evidence extraction after reviewing the submission.")

    st.divider()
    render_reviewer_section(rubric)

    st.divider()
    render_report_export_section(rubric, selection)


if __name__ == "__main__":
    main()
