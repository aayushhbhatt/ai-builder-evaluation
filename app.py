from pathlib import Path

import streamlit as st

from criteria import load_rubric

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


def render_reviewer_section(rubric: dict) -> None:
    """Render manual reviewer controls for each rubric dimension."""
    st.header("Reviewer Section")
    st.caption("Manual signals are reviewer-entered notes, not automated scores.")

    for key, dimension in rubric["dimensions"].items():
        with st.container(border=True):
            st.subheader(dimension["name"])
            st.write(dimension["description"])

            with st.expander("Rubric anchors"):
                st.markdown(f"**Weak:** {dimension['weak_anchor']}")
                st.markdown(f"**Solid:** {dimension['solid_anchor']}")
                st.markdown(f"**Strong:** {dimension['strong_anchor']}")

            st.selectbox(
                "Manual signal",
                MANUAL_SIGNAL_OPTIONS,
                key=f"signal_{key}",
            )
            st.text_area(
                "Reviewer notes",
                key=f"notes_{key}",
                placeholder="Add human reviewer observations, evidence references, and open questions.",
            )


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

    st.button(
        "Extract Evidence",
        disabled=True,
        help="Placeholder for a later milestone. No automated extraction runs in this skeleton.",
    )
    st.caption(
        "Evidence extraction is not implemented yet. This app currently supports manual review only."
    )

    render_reviewer_section(rubric)

    st.divider()
    st.caption(
        "No automated score, ranking, recommendation, hire/no-hire decision, or pass/fail output is produced."
    )


if __name__ == "__main__":
    main()
