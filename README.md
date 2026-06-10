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

Milestone 4 includes the repo skeleton, Streamlit shell, rubric-driven reviewer UI, LLM evidence extraction, and deterministic quote verification:

- Streamlit app with a clear responsible AI decision boundary.
- Two synthetic sample submissions.
- YAML rubric with exactly five dimensions.
- Reviewer UI driven by `criteria/ai_builder_rubric.yaml`.
- Manual reviewer controls for each rubric dimension.
- LLM-based evidence extraction that returns candidate summary, evidence by rubric dimension, missing or weak evidence, and follow-up questions.
- Deterministic substring verification that checks whether each extracted quote appears in the original submission.
- Clear verification status for each extracted evidence item so reviewers can inspect verified and unverified quotes.
- Placeholder module for report generation.

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

Milestone 4 complete: deterministic quote verification is implemented. The app runs locally, loads synthetic submissions, validates the YAML rubric through `criteria.py`, provides manual reviewer controls, and can call the OpenAI API to extract structured evidence for human reviewers.

AI extracts evidence from the submission. Code then verifies whether each extracted quote appears in the original submission using deterministic normalized substring matching. Verified quotes are marked as found, and unverified quotes are flagged for reviewer inspection before use.

Reviewers still make all evaluation judgments. The app does not make candidate decisions and produces no automated score, ranking, recommendation, hire/no-hire decision, rejection, selection, or pass/fail output.

Report export is the next milestone.
