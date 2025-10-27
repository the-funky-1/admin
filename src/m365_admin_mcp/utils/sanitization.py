"""
HTML sanitization utilities for email template security.

Uses bleach library to prevent XSS and injection attacks.
"""

import bleach

# Allowed HTML tags for email templates (safe subset)
ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "br", "code",
    "div", "em", "h1", "h2", "h3", "h4", "h5", "h6",
    "i", "li", "ol", "p", "pre", "span", "strong",
    "table", "tbody", "td", "th", "thead", "tr", "ul",
    "img", "hr",
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "abbr": ["title"],
    "acronym": ["title"],
    "img": ["src", "alt", "title", "width", "height"],
    "div": ["class", "style"],
    "span": ["class", "style"],
    "p": ["class", "style"],
    "table": ["class", "style", "border", "cellpadding", "cellspacing"],
    "td": ["class", "style", "colspan", "rowspan"],
    "th": ["class", "style", "colspan", "rowspan"],
}

# Allowed CSS properties (for inline styles)
ALLOWED_STYLES = [
    "color", "background-color", "font-size", "font-weight",
    "font-family", "text-align", "padding", "margin",
    "border", "width", "height",
]

# Allowed URL protocols
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(html: str, strict: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS and injection attacks.

    Args:
        html: HTML content to sanitize
        strict: If True, use stricter sanitization (fewer allowed tags)

    Returns:
        Sanitized HTML string

    Example:
        >>> sanitize_html('<script>alert("xss")</script><p>Safe content</p>')
        '<p>Safe content</p>'
        >>> sanitize_html('<p style="color:red">Text</p>')
        '<p style="color: red;">Text</p>'
    """
    if strict:
        # Stricter mode: only basic formatting tags
        allowed_tags = ["p", "br", "b", "i", "strong", "em"]
        allowed_attrs = {}
        allowed_styles = []
    else:
        allowed_tags = ALLOWED_TAGS
        allowed_attrs = ALLOWED_ATTRIBUTES
        allowed_styles = ALLOWED_STYLES

    # Clean HTML with bleach
    clean_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        styles=allowed_styles,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,  # Strip disallowed tags completely
    )

    return clean_html


def sanitize_text(text: str) -> str:
    """
    Sanitize plain text by removing HTML entirely.

    Args:
        text: Text to sanitize

    Returns:
        Text with all HTML removed

    Example:
        >>> sanitize_text('<script>alert("xss")</script>Plain text')
        'Plain text'
    """
    return bleach.clean(text, tags=[], strip=True)
