"""
Unit tests for validation utilities.
"""

import pytest

from m365_admin_mcp.utils.validation import (
    validate_email,
    validate_guid,
    validate_url,
    validate_input_schema,
)


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "john.doe@company.org",
            "test+tag@domain.co.uk",
            "admin@libertygoldsilver.com",
        ]
        for email in valid_emails:
            assert validate_email(email), f"Should accept valid email: {email}"

    def test_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Should reject invalid email: {email}"


class TestGuidValidation:
    """Tests for GUID validation."""

    def test_valid_guids(self):
        """Test valid GUID formats."""
        valid_guids = [
            "00000000-0000-0000-0000-000000000000",
            "11111111-2222-3333-4444-555555555555",
            "a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d",
        ]
        for guid in valid_guids:
            assert validate_guid(guid), f"Should accept valid GUID: {guid}"

    def test_invalid_guids(self):
        """Test invalid GUID formats."""
        invalid_guids = [
            "not-a-guid",
            "00000000000000000000000000000000",
            "00000000-0000-0000-000000000000",
            "0000-0000-0000-0000-000000000000",
        ]
        for guid in invalid_guids:
            assert not validate_guid(guid), f"Should reject invalid GUID: {guid}"


class TestUrlValidation:
    """Tests for URL validation."""

    def test_valid_urls(self):
        """Test valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.org/path",
            "https://example.com:8080/api",
        ]
        for url in valid_urls:
            assert validate_url(url), f"Should accept valid URL: {url}"

    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Not in default allowed schemes
            "javascript:alert('xss')",
            "//example.com",
        ]
        for url in invalid_urls:
            assert not validate_url(url), f"Should reject invalid URL: {url}"

    def test_custom_schemes(self):
        """Test URL validation with custom allowed schemes."""
        assert validate_url("ftp://example.com", ["ftp"])
        assert not validate_url("https://example.com", ["ftp"])


class TestSchemaValidation:
    """Tests for input schema validation."""

    def test_valid_input(self):
        """Test validation with valid input."""
        schema = {
            "required": ["name", "email"],
            "optional": ["age"],
        }
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
        }
        is_valid, errors = validate_input_schema(data, schema)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_field(self):
        """Test validation with missing required field."""
        schema = {
            "required": ["name", "email"],
        }
        data = {
            "name": "John Doe",
        }
        is_valid, errors = validate_input_schema(data, schema)
        assert not is_valid
        assert "email" in str(errors)

    def test_strict_mode_unknown_field(self):
        """Test strict mode rejects unknown fields."""
        schema = {
            "required": ["name"],
            "optional": ["email"],
            "strict": True,
        }
        data = {
            "name": "John Doe",
            "age": 30,  # Unknown field
        }
        is_valid, errors = validate_input_schema(data, schema)
        assert not is_valid
        assert "age" in str(errors)

    def test_non_strict_mode_allows_extra_fields(self):
        """Test non-strict mode allows extra fields."""
        schema = {
            "required": ["name"],
            "optional": ["email"],
        }
        data = {
            "name": "John Doe",
            "age": 30,  # Extra field
        }
        is_valid, errors = validate_input_schema(data, schema)
        assert is_valid
        assert len(errors) == 0
