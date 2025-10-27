"""
Input validation utilities for security and data integrity.
"""

import re
from typing import Any
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format (RFC 5322 simplified).

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    # Simplified RFC 5322 email regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_guid(guid: str) -> bool:
    """
    Validate GUID/UUID format.

    Args:
        guid: GUID string to validate

    Returns:
        True if valid GUID format, False otherwise

    Example:
        >>> validate_guid("00000000-0000-0000-0000-000000000000")
        True
        >>> validate_guid("invalid-guid")
        False
    """
    pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    return bool(re.match(pattern, guid))


def validate_url(url: str, allowed_schemes: list[str] | None = None) -> bool:
    """
    Validate URL format and scheme.

    Args:
        url: URL string to validate
        allowed_schemes: List of allowed URL schemes (default: ["http", "https"])

    Returns:
        True if valid URL with allowed scheme, False otherwise

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("ftp://example.com", ["ftp"])
        True
        >>> validate_url("javascript:alert('xss')")
        False
    """
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in allowed_schemes
    except Exception:
        return False


def validate_input_schema(data: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate input data against a simple schema.

    Args:
        data: Input data dictionary
        schema: Schema dictionary with required/optional fields

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> schema = {"required": ["email"], "optional": ["name"]}
        >>> validate_input_schema({"email": "test@example.com"}, schema)
        (True, [])
    """
    errors = []

    # Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Required field missing: {field}")

    # Check for unknown fields if strict mode
    if schema.get("strict", False):
        allowed_fields = set(required_fields + schema.get("optional", []))
        for field in data.keys():
            if field not in allowed_fields:
                errors.append(f"Unknown field: {field}")

    return (len(errors) == 0, errors)
