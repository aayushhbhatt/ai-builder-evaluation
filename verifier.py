from copy import deepcopy
import unicodedata
from typing import Any


VERIFICATION_METHOD = "normalized_substring_match"


UNICODE_PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "―": "-",
        "…": "...",
        " ": " ",
    }
)


def normalize_text(text: str) -> str:
    """Return text normalized for deterministic quote comparison."""
    if text is None:
        text = ""
    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = normalized.translate(UNICODE_PUNCTUATION_TRANSLATION)
    return " ".join(normalized.split()).strip().casefold()


def verify_quote(quote: str, source_text: str) -> dict[str, Any]:
    """Verify whether a quote appears in source text after simple normalization."""
    normalized_quote = normalize_text(quote)
    normalized_source = normalize_text(source_text)

    if not normalized_quote:
        return {
            "verified": False,
            "method": VERIFICATION_METHOD,
            "message": (
                "Unverified: quote is empty or missing. "
                "Reviewer should inspect before relying on it."
            ),
        }

    if normalized_quote in normalized_source:
        return {
            "verified": True,
            "method": VERIFICATION_METHOD,
            "message": "Verified: quote found in source submission.",
        }

    return {
        "verified": False,
        "method": VERIFICATION_METHOD,
        "message": (
            "Unverified: quote not found in source submission. "
            "Reviewer should inspect before relying on it."
        ),
    }


def verify_extraction(extraction: dict[str, Any], source_text: str) -> dict[str, Any]:
    """Add deterministic quote verification results to each evidence item.

    The original extraction shape is preserved and the input object is not mutated.
    Missing or malformed dimensions/evidence collections are left in place without
    crashing so the reviewer can still inspect the extractor output.
    """
    if not isinstance(extraction, dict):
        return {}

    verified_extraction = deepcopy(extraction)
    dimensions = verified_extraction.get("dimensions", [])
    if not isinstance(dimensions, list):
        return verified_extraction

    for dimension in dimensions:
        if not isinstance(dimension, dict):
            continue

        evidence_items = dimension.get("evidence", [])
        if not isinstance(evidence_items, list):
            continue

        for evidence in evidence_items:
            if not isinstance(evidence, dict):
                continue
            evidence["verification"] = verify_quote(
                evidence.get("quote", ""), source_text
            )

    return verified_extraction
