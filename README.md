# AI Builder Reviewer Workbench

AI Builder Reviewer Workbench is a local Streamlit MVP for helping human reviewers evaluate AI Builder work samples consistently. The app extracts and organizes evidence for manual review; it is not designed to make candidate decisions.

> Design principle: AI replaces the reviewer’s highlighter, not the reviewer.

## Project Purpose

The workbench supports reviewers who need a consistent way to inspect AI Builder submissions against a shared rubric. The intended workflow is:

1. Load or paste a synthetic work sample.
2. Use AI-assisted extraction to organize candidate-provided evidence by rubric dimension.
3. Review the submission against five rubric dimensions.
4. Record manual signals and reviewer notes separately from AI extraction.

The AI extraction is only a reviewer aid. Human reviewers remain responsible for all consequential judgments.

## MVP Scope

Milestone 3 includes the repo skeleton, Streamlit shell, rubric-driven reviewer UI, and LLM evidence extraction:

- Streamlit app with a clear responsible AI decision boundary.
- Two synthetic sample submissions.
- YAML rubric with exactly five dimensions.
- Reviewer UI driven by `criteria/ai_builder_rubric.yaml`.
- Manual reviewer controls for each rubric dimension.
- LLM-based evidence extraction that returns candidate summary, evidence by rubric dimension, missing or weak evidence, and follow-up questions.
- Clear warning that extracted quotes are not yet deterministically verified.
- Placeholder modules for deterministic verification and report generation.

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

## Current Status

Milestone 3 complete: LLM evidence extraction is implemented. The app runs locally, loads synthetic submissions, validates the YAML rubric through `criteria.py`, provides manual reviewer controls, and can call the OpenAI API to extract structured evidence for human reviewers.

Quote verification is the next milestone. Extracted quotes are currently AI-extracted and have not yet been deterministically verified, so reviewers must inspect them before relying on them.

The app still does not make candidate decisions. It produces no automated score, ranking, recommendation, hire/no-hire decision, rejection, selection, or pass/fail output.
