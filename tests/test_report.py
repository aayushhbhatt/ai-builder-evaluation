import unittest

from report import build_markdown_report


RUBRIC = {
    "dimensions": {
        "problem_framing": {
            "id": "problem_framing",
            "name": "Problem Framing",
            "description": "Evaluates concrete problem framing.",
            "weak_anchor": "Vague.",
            "solid_anchor": "Mostly clear.",
            "strong_anchor": "Tightly scoped.",
        }
    }
}

EXTRACTION = {
    "candidate_summary": "AI-assisted summary for human checking.",
    "dimensions": [
        {
            "dimension_id": "problem_framing",
            "dimension_name": "Problem Framing",
            "evidence": [
                {
                    "claim": "The submission names a workflow.",
                    "quote": "support operations team",
                    "relevance": "Shows a target workflow.",
                    "verification": {
                        "verified": True,
                        "message": "Verified: quote found in source submission.",
                    },
                }
            ],
            "missing_or_weak_evidence": [],
            "follow_up_questions": ["What is the success metric?"],
        }
    ],
    "overall_follow_up_questions": ["What should reviewers inspect manually?"],
}

ASSESSMENT = {
    "problem_framing": {
        "manual_signal": "Solid",
        "reviewer_notes": "Human-entered note.",
    }
}


class ReportTests(unittest.TestCase):
    def test_metadata_appears_when_supplied(self):
        report = build_markdown_report(
            {"title": "Scenario"},
            "Submission",
            EXTRACTION,
            ASSESSMENT,
            RUBRIC,
            {
                "app_version": "0.1.0",
                "model": "gpt-test",
                "prompt_version": "evidence-extraction-v2",
                "rubric_sha256": "a" * 64,
                "OPENAI_API_KEY": "sk-secret",
                "api_key": "secret",
            },
        )

        self.assertIn("- **Application version:** 0.1.0", report)
        self.assertIn("- **Model:** gpt-test", report)
        self.assertIn("- **Prompt version:** evidence-extraction-v2", report)
        self.assertIn("- **Rubric SHA-256:** " + "a" * 64, report)
        self.assertNotIn("sk-secret", report)
        self.assertNotIn("api_key", report.lower())
        self.assertNotIn("OPENAI_API_KEY", report)

    def test_report_still_works_without_metadata(self):
        report = build_markdown_report(
            {"title": "Scenario"},
            "Submission",
            EXTRACTION,
            ASSESSMENT,
            RUBRIC,
        )

        self.assertIn("## Review Context", report)
        self.assertIn("- **Scenario:** Scenario", report)
        self.assertIn("- **Submission:** Submission", report)
        self.assertIn("- **Generated:**", report)
        self.assertNotIn("Application version", report)
        self.assertNotIn("Prompt version", report)
        self.assertIn("## Decision Boundary", report)
        self.assertIn("## AI-Assisted Candidate Summary", report)
        self.assertIn("## Evidence and Human Assessment", report)
        self.assertIn("## Overall Suggested Follow-Up Questions", report)
        self.assertIn("## AI-Use Disclosure", report)

    def test_report_does_not_add_consequential_decision_outputs(self):
        report = build_markdown_report(
            {"title": "Scenario"},
            "Submission",
            EXTRACTION,
            ASSESSMENT,
            RUBRIC,
            {"app_version": "0.1.0"},
        ).lower()

        forbidden_phrases = [
            "automatic score:",
            "candidate score:",
            "ranking:",
            "ranked candidate",
            "recommendation:",
            "hire decision:",
            "no-hire decision:",
            "pass/fail:",
            "protected characteristic",
        ]
        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
