# AI Builder Reviewer Workbench

AI Builder Reviewer Workbench is a local Streamlit MVP for helping human reviewers evaluate AI Builder work samples consistently. The app is designed to extract and organize evidence for manual review in later milestones; it is not designed to make candidate decisions.

> Design principle: AI replaces the reviewer’s highlighter, not the reviewer.

## Project Purpose

The workbench supports reviewers who need a consistent way to inspect AI Builder submissions against a shared rubric. The intended workflow is:

1. Load or paste a synthetic work sample.
2. Review the submission against five rubric dimensions.
3. Record manual signals and reviewer notes.
4. In future milestones, use AI-generated evidence extraction only as a reviewer aid.

## MVP Scope

Milestone 2 includes the repo skeleton, Streamlit shell, and rubric-driven reviewer UI:

- Streamlit app with a clear responsible AI decision boundary.
- Two synthetic sample submissions.
- YAML rubric with exactly five dimensions.
- Reviewer UI driven by `criteria/ai_builder_rubric.yaml`.
- Manual reviewer controls for each rubric dimension.
- Placeholder modules for extraction, verification, and report generation.

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

Optionally copy the environment template for future OpenAI integration:

```bash
cp .env.example .env
```

Milestone 2 does not call the OpenAI API yet.

## Run Command

```bash
streamlit run app.py
```

## Current Status

Milestone 2. Rubric registry and reviewer UI are now driven by `criteria/ai_builder_rubric.yaml`. The app runs locally, loads synthetic submissions, validates the YAML rubric through `criteria.py`, and provides manual reviewer controls. Evidence extraction, deterministic quote verification, and full report export are placeholders for future milestones.
