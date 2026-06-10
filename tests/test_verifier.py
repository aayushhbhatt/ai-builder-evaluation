import unittest

from verifier import normalize_text, verify_extraction, verify_quote


class VerifierTests(unittest.TestCase):
    def test_verify_quote_found_after_whitespace_and_case_normalization(self):
        result = verify_quote("HUMAN   reviewer", "A human reviewer remains in control.")

        self.assertTrue(result["verified"])

    def test_verify_quote_found_after_unicode_punctuation_normalization(self):
        source = "The reviewer’s tool uses quote verification — not scoring."
        quote = "reviewer's tool uses quote verification - not scoring"

        result = verify_quote(quote, source)

        self.assertTrue(result["verified"])

    def test_empty_quote_is_unverified(self):
        result = verify_quote("", "source")

        self.assertFalse(result["verified"])

    def test_verify_extraction_does_not_mutate_input(self):
        extraction = {
            "dimensions": [
                {
                    "evidence": [
                        {"quote": "human reviewer", "claim": "", "relevance": ""}
                    ]
                }
            ]
        }

        verified = verify_extraction(extraction, "A human reviewer remains responsible.")

        self.assertNotIn("verification", extraction["dimensions"][0]["evidence"][0])
        self.assertTrue(verified["dimensions"][0]["evidence"][0]["verification"]["verified"])

    def test_normalize_text_handles_none(self):
        self.assertEqual(normalize_text(None), "")


if __name__ == "__main__":
    unittest.main()
