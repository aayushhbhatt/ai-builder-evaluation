from typing import Any


def verify_extraction(extraction: dict[str, Any], source_text: str) -> dict[str, Any]:
    """Return extraction unchanged until deterministic quote verification exists.

    Deterministic quote verification will be implemented next. It will check
    that extracted quotes are present in the source text and clearly mark each
    evidence item as verified or unverified.
    """
    _ = source_text
    return extraction
