# AI Builder Reviewer Workbench

AI Builder Reviewer Workbench is a local Streamlit MVP for helping human reviewers evaluate AI Builder work samples consistently. The app extracts and organizes evidence for manual review; it is not designed to make candidate decisions.

> Design principle: AI replaces the reviewer’s highlighter, not the reviewer.

## Project Purpose

The workbench supports reviewers who need a consistent way to inspect AI Builder submissions against a shared rubric. The intended UI flow is:

1. **Submission:** Load or paste a synthetic work sample and run evidence extraction in the left pane.
2. **AI Evidence:** Inspect AI-assisted evidence and deterministic quote verification in the adjacent evidence pane.
3. **Human Review:** Record manual signals and reviewer notes in the human review section below.
4. **Export:** Generate, preview, and download a Markdown audit summary from the export section.

The AI extraction is only a reviewer aid. Human reviewers remain responsible for all consequential judgments.

## MVP Scope

Milestone 5 completes the local MVP workflow: repository skeleton, Streamlit shell, rubric-driven reviewer UI, LLM evidence extraction, deterministic quote verification, session-state reviewer assessment, and Markdown review export:

- Streamlit app with a clear responsible AI decision boundary.
- Two synthetic sample submissions.
- YAML rubric with exactly five dimensions.
- Reviewer UI driven by `criteria/ai_builder_rubric.yaml`.
- Manual reviewer controls for each rubric dimension, preserved in Streamlit session state by rubric dimension ID.
- LLM-based evidence extraction that returns candidate summary, evidence by rubric dimension, missing or weak evidence, and follow-up questions.
- Deterministic substring verification that checks whether each extracted quote appears in the original submission.
- Clear verification status for each extracted evidence item so reviewers can inspect verified and unverified quotes.
- Exportable Markdown review summary that includes AI-assisted evidence, quote verification, human-entered signals and notes, and follow-up questions.

## Explicit Non-Goals

This project is not any of the following:

- Automated hiring scorer.
- Resume screener.
- Applicant tracking system (ATS).
- AI interviewer.
- Candidate ranking system.
- Hire/no-hire recommender.
- Authentication or user management system.
- Database-backed review platform.
- Vector search, LangGraph, multi-agent, or complex orchestration project.

## Responsible AI Boundary

This tool does not rank, reject, recommend, or select candidates. Human reviewers remain responsible for all evaluation judgments.

The app should support evidence-based human review. It must not produce automated scores, rankings, recommendations, hire/no-hire decisions, or pass/fail outputs.

## Setup Instructions

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template and add your OpenAI API key before using evidence extraction:

```bash
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. `OPENAI_MODEL` defaults to `gpt-4.1-mini` if it is not set.

## Run Command

```bash
streamlit run app.py
```

## Demo Flow

1. Run the Streamlit app and note the dark, single-screen layout with the decision boundary visible in the header.
2. In the sidebar, select a synthetic submission or choose the custom submission option.
3. In **1. Submission**, review or paste the work sample and select **Extract Evidence**.
4. In **2. AI Evidence**, inspect the AI-assisted summary, rubric-dimension evidence, and verified/unverified quote labels.
5. In **3. Human Review**, enter human reviewer signals and notes.
6. In **4. Export**, generate, preview, and download the Markdown summary.

## Current Status

Milestone 5 complete: the complete MVP workflow is operational. The app runs locally, loads synthetic submissions or custom text, validates the YAML rubric through `criteria.py`, provides manual reviewer controls, calls the OpenAI API to extract structured evidence, verifies extracted quotes deterministically, preserves reviewer assessment in Streamlit session state, and generates an exportable Markdown review summary.

AI extracts evidence from the submission. Code then verifies whether each extracted quote appears in the original submission using deterministic normalized substring matching. Verified quotes are marked as found, and unverified quotes are flagged for reviewer inspection before use. Manual reviewer signals and notes are stored by rubric dimension ID in `st.session_state["reviewer_assessment"]`, and the Markdown export includes those human-entered assessments without converting them to scores.

Reviewers still make all evaluation judgments. The app does not make candidate decisions and produces no automated score, ranking, recommendation, hire/no-hire decision, rejection, selection, or pass/fail output.
