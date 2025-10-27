"""
Email template management tools for Microsoft 365.

Provides functionality for:
- Template CRUD operations (create, read, update, delete, list)
- Jinja2 template rendering with variable substitution
- Email sending from templates via Graph API
- Template usage tracking and analytics
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, Template, TemplateSyntaxError
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)

from ..auth import get_graph_client
from ..config import get_settings
from ..utils.sanitization import sanitize_html
from ..utils.validation import validate_email

logger = logging.getLogger(__name__)


class TemplateDatabase:
    """Database operations for email templates."""

    def __init__(self):
        """Initialize database connection."""
        self.settings = get_settings()
        self.db_path = self.settings.database_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_template(
        self,
        template_name: str,
        subject: str,
        body_html: str,
        category: str,
        body_text: str | None = None,
        variables: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new email template."""
        template_id = str(uuid.uuid4())
        variables_json = json.dumps(variables) if variables else None

        # Sanitize HTML content
        body_html = sanitize_html(body_html)

        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO email_templates
                (template_id, template_name, subject, body_html, body_text,
                 category, variables, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    template_id,
                    template_name,
                    subject,
                    body_html,
                    body_text,
                    category,
                    variables_json,
                    description,
                ),
            )
            conn.commit()

            return {
                "success": True,
                "template_id": template_id,
                "template_name": template_name,
                "message": f"Template '{template_name}' created successfully",
            }
        finally:
            conn.close()

    def get_template(self, template_id: str) -> dict[str, Any]:
        """Retrieve a template by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM email_templates WHERE template_id = ?",
                (template_id,),
            )
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Template not found: {template_id}")

            template = dict(row)
            # Parse variables JSON
            if template.get("variables"):
                template["variables"] = json.loads(template["variables"])

            return template
        finally:
            conn.close()

    def get_template_by_name(self, template_name: str) -> dict[str, Any]:
        """Retrieve a template by name."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM email_templates WHERE template_name = ?",
                (template_name,),
            )
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Template not found: {template_name}")

            template = dict(row)
            # Parse variables JSON
            if template.get("variables"):
                template["variables"] = json.loads(template["variables"])

            return template
        finally:
            conn.close()

    def list_templates(
        self, category: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List all templates, optionally filtered by category."""
        conn = self._get_connection()
        try:
            if category:
                cursor = conn.execute(
                    """
                    SELECT template_id, template_name, subject, category,
                           description, created_at, version
                    FROM email_templates
                    WHERE category = ?
                    ORDER BY template_name
                    LIMIT ?
                    """,
                    (category, limit),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT template_id, template_name, subject, category,
                           description, created_at, version
                    FROM email_templates
                    ORDER BY template_name
                    LIMIT ?
                    """,
                    (limit,),
                )

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_template(
        self,
        template_id: str,
        subject: str | None = None,
        body_html: str | None = None,
        body_text: str | None = None,
        category: str | None = None,
        variables: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing template."""
        # Get existing template
        template = self.get_template(template_id)

        # Prepare update values
        update_fields = []
        update_values = []

        if subject is not None:
            update_fields.append("subject = ?")
            update_values.append(subject)

        if body_html is not None:
            update_fields.append("body_html = ?")
            update_values.append(sanitize_html(body_html))

        if body_text is not None:
            update_fields.append("body_text = ?")
            update_values.append(body_text)

        if category is not None:
            update_fields.append("category = ?")
            update_values.append(category)

        if variables is not None:
            update_fields.append("variables = ?")
            update_values.append(json.dumps(variables))

        if description is not None:
            update_fields.append("description = ?")
            update_values.append(description)

        # Always update version and timestamp
        update_fields.append("version = version + 1")
        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        if not update_fields:
            return {
                "success": True,
                "message": "No changes to update",
                "template_id": template_id,
            }

        # Execute update
        conn = self._get_connection()
        try:
            update_values.append(template_id)
            conn.execute(
                f"UPDATE email_templates SET {', '.join(update_fields)} WHERE template_id = ?",
                update_values,
            )
            conn.commit()

            return {
                "success": True,
                "template_id": template_id,
                "message": "Template updated successfully",
            }
        finally:
            conn.close()

    def delete_template(self, template_id: str) -> dict[str, Any]:
        """Delete a template."""
        # Verify template exists
        self.get_template(template_id)

        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM email_templates WHERE template_id = ?", (template_id,))
            conn.commit()

            return {
                "success": True,
                "template_id": template_id,
                "message": "Template deleted successfully",
            }
        finally:
            conn.close()

    def log_usage(
        self,
        template_id: str,
        sent_by: str,
        sent_to: str,
        variables_used: dict[str, Any] | None = None,
        message_id: str | None = None,
    ) -> None:
        """Log template usage."""
        variables_json = json.dumps(variables_used) if variables_used else None

        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO template_usage
                (template_id, sent_by, sent_to, variables_used, message_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (template_id, sent_by, sent_to, variables_json, message_id),
            )
            conn.commit()
        finally:
            conn.close()

    def get_usage_stats(self, template_id: str) -> dict[str, Any]:
        """Get usage statistics for a template."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT COUNT(*) as usage_count,
                       MIN(sent_at) as first_used,
                       MAX(sent_at) as last_used
                FROM template_usage
                WHERE template_id = ?
                """,
                (template_id,),
            )
            row = cursor.fetchone()

            return dict(row) if row else {}
        finally:
            conn.close()


class EmailTemplateTools:
    """Email template management and sending tools."""

    db = TemplateDatabase()
    jinja_env = Environment(autoescape=True)

    @staticmethod
    def render_template(template_body: str, variables: dict[str, Any]) -> str:
        """Render a Jinja2 template with variables."""
        try:
            template = EmailTemplateTools.jinja_env.from_string(template_body)
            return template.render(**variables)
        except TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error: {e}")
        except Exception as e:
            raise ValueError(f"Template rendering error: {e}")

    @classmethod
    async def create_template(
        cls,
        template_name: str,
        subject: str,
        body_html: str,
        category: str,
        body_text: str | None = None,
        variables: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new email template."""
        logger.info(f"Creating email template: {template_name}")

        # Validate template syntax
        try:
            cls.jinja_env.from_string(subject)
            cls.jinja_env.from_string(body_html)
            if body_text:
                cls.jinja_env.from_string(body_text)
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax: {e}")

        result = cls.db.create_template(
            template_name=template_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            category=category,
            variables=variables,
            description=description,
        )

        logger.info(f"Template created: {result['template_id']}")
        return result

    @classmethod
    async def get_template(cls, template_identifier: str) -> dict[str, Any]:
        """Get a template by ID or name."""
        logger.info(f"Retrieving template: {template_identifier}")

        # Try by ID first (UUID format)
        try:
            if len(template_identifier) == 36 and template_identifier.count("-") == 4:
                return cls.db.get_template(template_identifier)
        except ValueError:
            pass

        # Try by name
        return cls.db.get_template_by_name(template_identifier)

    @classmethod
    async def list_templates(
        cls, category: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        """List all templates."""
        logger.info(f"Listing templates (category: {category}, max: {max_results})")

        templates = cls.db.list_templates(category=category, limit=max_results)

        return {"count": len(templates), "templates": templates}

    @classmethod
    async def update_template(
        cls,
        template_identifier: str,
        subject: str | None = None,
        body_html: str | None = None,
        body_text: str | None = None,
        category: str | None = None,
        variables: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing template."""
        logger.info(f"Updating template: {template_identifier}")

        # Get template to get ID
        template = await cls.get_template(template_identifier)
        template_id = template["template_id"]

        # Validate new template syntax if provided
        try:
            if subject:
                cls.jinja_env.from_string(subject)
            if body_html:
                cls.jinja_env.from_string(body_html)
            if body_text:
                cls.jinja_env.from_string(body_text)
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax: {e}")

        result = cls.db.update_template(
            template_id=template_id,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            category=category,
            variables=variables,
            description=description,
        )

        logger.info(f"Template updated: {template_id}")
        return result

    @classmethod
    async def delete_template(cls, template_identifier: str) -> dict[str, Any]:
        """Delete a template."""
        logger.info(f"Deleting template: {template_identifier}")

        # Get template to get ID
        template = await cls.get_template(template_identifier)
        template_id = template["template_id"]

        result = cls.db.delete_template(template_id)

        logger.info(f"Template deleted: {template_id}")
        return result

    @classmethod
    async def send_from_template(
        cls,
        template_identifier: str,
        from_email: str,
        to_emails: list[str],
        variables: dict[str, Any] | None = None,
        cc_emails: list[str] | None = None,
        bcc_emails: list[str] | None = None,
    ) -> dict[str, Any]:
        """Send an email from a template."""
        logger.info(f"Sending email from template: {template_identifier}")

        # Validate email addresses
        for email in to_emails:
            if not validate_email(email):
                raise ValueError(f"Invalid recipient email: {email}")

        if cc_emails:
            for email in cc_emails:
                if not validate_email(email):
                    raise ValueError(f"Invalid CC email: {email}")

        if bcc_emails:
            for email in bcc_emails:
                if not validate_email(email):
                    raise ValueError(f"Invalid BCC email: {email}")

        # Get template
        template = await cls.get_template(template_identifier)

        # Render template with variables
        variables = variables or {}
        rendered_subject = cls.render_template(template["subject"], variables)
        rendered_body_html = cls.render_template(template["body_html"], variables)

        # Create message
        message = Message()
        message.subject = rendered_subject

        # Set HTML body
        body = ItemBody()
        body.content_type = BodyType.Html
        body.content = rendered_body_html
        message.body = body

        # Set recipients
        message.to_recipients = []
        for email in to_emails:
            recipient = Recipient()
            email_address = EmailAddress()
            email_address.address = email
            recipient.email_address = email_address
            message.to_recipients.append(recipient)

        # Set CC recipients
        if cc_emails:
            message.cc_recipients = []
            for email in cc_emails:
                recipient = Recipient()
                email_address = EmailAddress()
                email_address.address = email
                recipient.email_address = email_address
                message.cc_recipients.append(recipient)

        # Set BCC recipients
        if bcc_emails:
            message.bcc_recipients = []
            for email in bcc_emails:
                recipient = Recipient()
                email_address = EmailAddress()
                email_address.address = email
                recipient.email_address = email_address
                message.bcc_recipients.append(recipient)

        # Send email via Graph API
        client = get_graph_client()

        request_body = SendMailPostRequestBody()
        request_body.message = message
        request_body.save_to_sent_items = True

        await client.users.by_user_id(from_email).send_mail.post(request_body)

        # Log usage for all recipients
        for email in to_emails:
            cls.db.log_usage(
                template_id=template["template_id"],
                sent_by=from_email,
                sent_to=email,
                variables_used=variables,
            )

        logger.info(
            f"Email sent from template {template['template_id']} to {len(to_emails)} recipients"
        )

        return {
            "success": True,
            "template_id": template["template_id"],
            "template_name": template["template_name"],
            "recipients": len(to_emails),
            "message": f"Email sent successfully to {len(to_emails)} recipient(s)",
        }

    @classmethod
    async def get_template_stats(cls, template_identifier: str) -> dict[str, Any]:
        """Get usage statistics for a template."""
        logger.info(f"Getting stats for template: {template_identifier}")

        # Get template
        template = await cls.get_template(template_identifier)

        # Get usage stats
        stats = cls.db.get_usage_stats(template["template_id"])

        return {
            "template_id": template["template_id"],
            "template_name": template["template_name"],
            "usage_count": stats.get("usage_count", 0),
            "first_used": stats.get("first_used"),
            "last_used": stats.get("last_used"),
        }
