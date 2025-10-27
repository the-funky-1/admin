"""
Main MCP Server for Microsoft 365 Administration.

This module implements the Model Context Protocol server that provides
M365 administration capabilities to Claude Code.
"""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

from .auth import test_graph_connection
from .config import get_settings
from .resources.health_resource import HealthResource
from .tools.email_templates import EmailTemplateTools
from .tools.teams_provisioning import TeamsProvisioningTools
from .tools.user_management import UserManagementTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


class M365AdminServer:
    """
    MCP Server for Microsoft 365 administration and provisioning.

    Provides tools and resources for:
    - User management
    - Email templates
    - Teams provisioning
    - Service configuration
    - Monitoring and health checks
    """

    def __init__(self):
        """Initialize the MCP server."""
        self.settings = get_settings()
        self.server = Server(self.settings.mcp_server_name)
        self.health_resource = HealthResource()

        # Register handlers
        self._register_resources()
        self._register_tools()

        logger.info(
            f"Initialized {self.settings.mcp_server_name} "
            f"v{self.settings.mcp_server_version}"
        )

    def _register_resources(self) -> None:
        """Register MCP resources."""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="m365://health",
                    name="Server Health Status",
                    mimeType="application/json",
                    description="Health and authentication status of the MCP server",
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            if uri == "m365://health":
                health_data = await self.health_resource.get_health_status()
                return self.health_resource.format_as_resource_content(health_data)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="test_connection",
                    description="Test Microsoft Graph API connection",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="get_health",
                    description="Get server health status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="create_user",
                    description="Create a new Microsoft 365 user account with mailbox",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User principal name (email address)",
                            },
                            "displayName": {
                                "type": "string",
                                "description": "Display name for the user",
                            },
                            "password": {
                                "type": "string",
                                "description": "Initial password for the user",
                            },
                            "firstName": {
                                "type": "string",
                                "description": "First name (optional)",
                            },
                            "lastName": {
                                "type": "string",
                                "description": "Last name (optional)",
                            },
                            "forcePasswordChange": {
                                "type": "boolean",
                                "description": "Require password change on first login (default: true)",
                            },
                        },
                        "required": ["email", "displayName", "password"],
                    },
                ),
                Tool(
                    name="get_user",
                    description="Get information about a Microsoft 365 user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User principal name (email address)",
                            },
                        },
                        "required": ["email"],
                    },
                ),
                Tool(
                    name="list_users",
                    description="List all users in the Microsoft 365 tenant",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "maxResults": {
                                "type": "integer",
                                "description": "Maximum number of users to return (default: 100)",
                                "minimum": 1,
                                "maximum": 999,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="create_template",
                    description="Create a new email template with Jinja2 variable support",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "templateName": {
                                "type": "string",
                                "description": "Unique name for the template",
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line (supports Jinja2 variables)",
                            },
                            "bodyHtml": {
                                "type": "string",
                                "description": "HTML email body (supports Jinja2 variables)",
                            },
                            "category": {
                                "type": "string",
                                "description": "Template category (e.g., wiring, customer_service, internal)",
                            },
                            "bodyText": {
                                "type": "string",
                                "description": "Plain text email body (optional)",
                            },
                            "variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of variable names used in template",
                            },
                            "description": {
                                "type": "string",
                                "description": "Template description and usage notes",
                            },
                        },
                        "required": ["templateName", "subject", "bodyHtml", "category"],
                    },
                ),
                Tool(
                    name="get_template",
                    description="Get an email template by ID or name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "templateIdentifier": {
                                "type": "string",
                                "description": "Template ID (UUID) or template name",
                            },
                        },
                        "required": ["templateIdentifier"],
                    },
                ),
                Tool(
                    name="list_templates",
                    description="List all email templates, optionally filtered by category",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category (optional)",
                            },
                            "maxResults": {
                                "type": "integer",
                                "description": "Maximum number of templates to return (default: 100)",
                                "minimum": 1,
                                "maximum": 999,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="update_template",
                    description="Update an existing email template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "templateIdentifier": {
                                "type": "string",
                                "description": "Template ID (UUID) or template name",
                            },
                            "subject": {
                                "type": "string",
                                "description": "New email subject line",
                            },
                            "bodyHtml": {
                                "type": "string",
                                "description": "New HTML email body",
                            },
                            "bodyText": {
                                "type": "string",
                                "description": "New plain text email body",
                            },
                            "category": {
                                "type": "string",
                                "description": "New template category",
                            },
                            "variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Updated list of variable names",
                            },
                            "description": {
                                "type": "string",
                                "description": "Updated template description",
                            },
                        },
                        "required": ["templateIdentifier"],
                    },
                ),
                Tool(
                    name="delete_template",
                    description="Delete an email template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "templateIdentifier": {
                                "type": "string",
                                "description": "Template ID (UUID) or template name",
                            },
                        },
                        "required": ["templateIdentifier"],
                    },
                ),
                Tool(
                    name="send_from_template",
                    description="Send an email using a template with variable substitution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "templateIdentifier": {
                                "type": "string",
                                "description": "Template ID (UUID) or template name",
                            },
                            "fromEmail": {
                                "type": "string",
                                "description": "Sender email address",
                            },
                            "toEmails": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Recipient email addresses",
                            },
                            "variables": {
                                "type": "object",
                                "description": "Key-value pairs for template variable substitution",
                            },
                            "ccEmails": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "CC recipient email addresses (optional)",
                            },
                            "bccEmails": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "BCC recipient email addresses (optional)",
                            },
                        },
                        "required": ["templateIdentifier", "fromEmail", "toEmails"],
                    },
                ),
                Tool(
                    name="create_team",
                    description="Create a new Microsoft Team with configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "displayName": {
                                "type": "string",
                                "description": "Team display name",
                            },
                            "description": {
                                "type": "string",
                                "description": "Team description",
                            },
                            "visibility": {
                                "type": "string",
                                "description": "Team visibility: 'public' or 'private' (default: private)",
                                "enum": ["public", "private"],
                            },
                            "ownerEmail": {
                                "type": "string",
                                "description": "Email of team owner (optional)",
                            },
                        },
                        "required": ["displayName", "description"],
                    },
                ),
                Tool(
                    name="list_teams",
                    description="List all Microsoft Teams in the organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "maxResults": {
                                "type": "integer",
                                "description": "Maximum number of teams to return (default: 100)",
                                "minimum": 1,
                                "maximum": 999,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="create_channel",
                    description="Create a channel in a Microsoft Team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "teamId": {
                                "type": "string",
                                "description": "Team ID",
                            },
                            "displayName": {
                                "type": "string",
                                "description": "Channel display name",
                            },
                            "description": {
                                "type": "string",
                                "description": "Channel description (optional)",
                            },
                            "channelType": {
                                "type": "string",
                                "description": "Channel type: 'standard' or 'private' (default: standard)",
                                "enum": ["standard", "private"],
                            },
                        },
                        "required": ["teamId", "displayName"],
                    },
                ),
                Tool(
                    name="list_channels",
                    description="List all channels in a Microsoft Team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "teamId": {
                                "type": "string",
                                "description": "Team ID",
                            },
                        },
                        "required": ["teamId"],
                    },
                ),
                Tool(
                    name="add_team_member",
                    description="Add a member or owner to a Microsoft Team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "teamId": {
                                "type": "string",
                                "description": "Team ID",
                            },
                            "userEmail": {
                                "type": "string",
                                "description": "User email address",
                            },
                            "role": {
                                "type": "string",
                                "description": "Member role: 'owner' or 'member' (default: member)",
                                "enum": ["owner", "member"],
                            },
                        },
                        "required": ["teamId", "userEmail"],
                    },
                ),
                Tool(
                    name="list_team_members",
                    description="List all members of a Microsoft Team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "teamId": {
                                "type": "string",
                                "description": "Team ID",
                            },
                        },
                        "required": ["teamId"],
                    },
                ),
                Tool(
                    name="provision_team",
                    description="Provision a complete team with channels and members (orchestrated with rollback)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "teamName": {
                                "type": "string",
                                "description": "Team name",
                            },
                            "teamDescription": {
                                "type": "string",
                                "description": "Team description",
                            },
                            "ownerEmail": {
                                "type": "string",
                                "description": "Email of team owner",
                            },
                            "channels": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "type": {"type": "string", "enum": ["standard", "private"]},
                                    },
                                    "required": ["name"],
                                },
                                "description": "List of channels to create",
                            },
                            "members": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "role": {"type": "string", "enum": ["owner", "member"]},
                                    },
                                    "required": ["email"],
                                },
                                "description": "List of members to add (optional)",
                            },
                            "visibility": {
                                "type": "string",
                                "description": "Team visibility: 'public' or 'private' (default: private)",
                                "enum": ["public", "private"],
                            },
                        },
                        "required": ["teamName", "teamDescription", "ownerEmail", "channels"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
            """Execute a tool."""
            try:
                if name == "test_connection":
                    return await self._tool_test_connection()
                elif name == "get_health":
                    return await self._tool_get_health()
                elif name == "create_user":
                    return await self._tool_create_user(arguments)
                elif name == "get_user":
                    return await self._tool_get_user(arguments)
                elif name == "list_users":
                    return await self._tool_list_users(arguments)
                elif name == "create_template":
                    return await self._tool_create_template(arguments)
                elif name == "get_template":
                    return await self._tool_get_template(arguments)
                elif name == "list_templates":
                    return await self._tool_list_templates(arguments)
                elif name == "update_template":
                    return await self._tool_update_template(arguments)
                elif name == "delete_template":
                    return await self._tool_delete_template(arguments)
                elif name == "send_from_template":
                    return await self._tool_send_from_template(arguments)
                elif name == "create_team":
                    return await self._tool_create_team(arguments)
                elif name == "list_teams":
                    return await self._tool_list_teams(arguments)
                elif name == "create_channel":
                    return await self._tool_create_channel(arguments)
                elif name == "list_channels":
                    return await self._tool_list_channels(arguments)
                elif name == "add_team_member":
                    return await self._tool_add_team_member(arguments)
                elif name == "list_team_members":
                    return await self._tool_list_team_members(arguments)
                elif name == "provision_team":
                    return await self._tool_provision_team(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {name}", exc_info=True)
                return [
                    {
                        "type": "text",
                        "text": f"❌ Error executing {name}: {str(e)}",
                    }
                ]

    async def _tool_test_connection(self) -> list[dict[str, Any]]:
        """Test Microsoft Graph API connection."""
        try:
            is_connected = await test_graph_connection()

            if is_connected:
                message = "✅ Successfully connected to Microsoft Graph API"
                logger.info("Graph API connection test successful")
            else:
                message = "❌ Failed to connect to Microsoft Graph API"
                logger.warning("Graph API connection test failed")

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Connection test error: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Connection test failed: {str(e)}",
                }
            ]

    async def _tool_get_health(self) -> list[dict[str, Any]]:
        """Get server health status."""
        try:
            health_data = await self.health_resource.get_health_status()

            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
            }.get(health_data["status"], "❓")

            message = f"{status_emoji} Server Status: {health_data['status']}\n"
            message += f"Authenticated: {health_data['authenticated']}\n"
            message += f"Graph API: {health_data['graphApiConnected']}\n"
            message += f"Auth Method: {health_data['configuration']['authMethod']}\n"
            message += f"Server: {health_data['configuration']['serverName']} "
            message += f"v{health_data['configuration']['serverVersion']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Health check failed: {str(e)}",
                }
            ]

    async def _tool_create_user(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a new M365 user."""
        try:
            email = arguments.get("email")
            display_name = arguments.get("displayName")
            password = arguments.get("password")
            first_name = arguments.get("firstName")
            last_name = arguments.get("lastName")
            force_password_change = arguments.get("forcePasswordChange", True)

            logger.info(f"Creating user: {email}")

            result = await UserManagementTools.create_user(
                email=email,
                display_name=display_name,
                password=password,
                first_name=first_name,
                last_name=last_name,
                force_password_change=force_password_change,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"User ID: {result['userId']}\n"
            message += f"Email: {result['userPrincipalName']}\n"
            message += f"Display Name: {result['displayName']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"User creation failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to create user: {str(e)}",
                }
            ]

    async def _tool_get_user(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Get user information."""
        try:
            email = arguments.get("email")

            logger.info(f"Fetching user: {email}")

            result = await UserManagementTools.get_user(email)

            message = f"✅ User Information\n\n"
            message += f"Email: {result['userPrincipalName']}\n"
            message += f"Display Name: {result['displayName']}\n"
            message += f"First Name: {result.get('givenName', 'N/A')}\n"
            message += f"Last Name: {result.get('surname', 'N/A')}\n"
            message += f"Account Enabled: {result['accountEnabled']}\n"
            message += f"User ID: {result['userId']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"User fetch failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to get user: {str(e)}",
                }
            ]

    async def _tool_list_users(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """List all users in the tenant."""
        try:
            max_results = arguments.get("maxResults", 100)

            logger.info(f"Listing users (max: {max_results})")

            result = await UserManagementTools.list_users(max_results)

            if result["count"] == 0:
                return [{"type": "text", "text": "No users found in the tenant."}]

            message = f"✅ Found {result['count']} users:\n\n"
            for user in result["users"]:
                enabled = "✅" if user["accountEnabled"] else "❌"
                message += f"{enabled} {user['displayName']} ({user['userPrincipalName']})\n"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"User list failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to list users: {str(e)}",
                }
            ]

    async def _tool_create_template(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a new email template."""
        try:
            template_name = arguments.get("templateName")
            subject = arguments.get("subject")
            body_html = arguments.get("bodyHtml")
            category = arguments.get("category")
            body_text = arguments.get("bodyText")
            variables = arguments.get("variables")
            description = arguments.get("description")

            logger.info(f"Creating template: {template_name}")

            result = await EmailTemplateTools.create_template(
                template_name=template_name,
                subject=subject,
                body_html=body_html,
                category=category,
                body_text=body_text,
                variables=variables,
                description=description,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Template ID: {result['template_id']}\n"
            message += f"Template Name: {result['template_name']}\n"
            message += f"Category: {category}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Template creation failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to create template: {str(e)}",
                }
            ]

    async def _tool_get_template(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Get a template by ID or name."""
        try:
            template_identifier = arguments.get("templateIdentifier")

            logger.info(f"Retrieving template: {template_identifier}")

            result = await EmailTemplateTools.get_template(template_identifier)

            message = f"✅ Template Information\n\n"
            message += f"Template ID: {result['template_id']}\n"
            message += f"Name: {result['template_name']}\n"
            message += f"Subject: {result['subject']}\n"
            message += f"Category: {result['category']}\n"
            if result.get("variables"):
                message += f"Variables: {', '.join(result['variables'])}\n"
            if result.get("description"):
                message += f"Description: {result['description']}\n"
            message += f"Version: {result['version']}\n"
            message += f"Created: {result['created_at']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Template retrieval failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to get template: {str(e)}",
                }
            ]

    async def _tool_list_templates(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """List all templates."""
        try:
            category = arguments.get("category")
            max_results = arguments.get("maxResults", 100)

            logger.info(f"Listing templates (category: {category}, max: {max_results})")

            result = await EmailTemplateTools.list_templates(
                category=category, max_results=max_results
            )

            if result["count"] == 0:
                return [{"type": "text", "text": "No templates found."}]

            message = f"✅ Found {result['count']} template(s):\n\n"
            for template in result["templates"]:
                message += f"📧 {template['template_name']}\n"
                message += f"   Category: {template['category']}\n"
                message += f"   Subject: {template['subject']}\n"
                message += f"   ID: {template['template_id']}\n\n"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Template list failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to list templates: {str(e)}",
                }
            ]

    async def _tool_update_template(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Update an existing template."""
        try:
            template_identifier = arguments.get("templateIdentifier")
            subject = arguments.get("subject")
            body_html = arguments.get("bodyHtml")
            body_text = arguments.get("bodyText")
            category = arguments.get("category")
            variables = arguments.get("variables")
            description = arguments.get("description")

            logger.info(f"Updating template: {template_identifier}")

            result = await EmailTemplateTools.update_template(
                template_identifier=template_identifier,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                category=category,
                variables=variables,
                description=description,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Template ID: {result['template_id']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Template update failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to update template: {str(e)}",
                }
            ]

    async def _tool_delete_template(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Delete a template."""
        try:
            template_identifier = arguments.get("templateIdentifier")

            logger.info(f"Deleting template: {template_identifier}")

            result = await EmailTemplateTools.delete_template(template_identifier)

            message = f"✅ {result['message']}\n\n"
            message += f"Template ID: {result['template_id']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Template deletion failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to delete template: {str(e)}",
                }
            ]

    async def _tool_send_from_template(
        self, arguments: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Send an email from a template."""
        try:
            template_identifier = arguments.get("templateIdentifier")
            from_email = arguments.get("fromEmail")
            to_emails = arguments.get("toEmails")
            variables = arguments.get("variables")
            cc_emails = arguments.get("ccEmails")
            bcc_emails = arguments.get("bccEmails")

            logger.info(f"Sending email from template: {template_identifier}")

            result = await EmailTemplateTools.send_from_template(
                template_identifier=template_identifier,
                from_email=from_email,
                to_emails=to_emails,
                variables=variables,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Template: {result['template_name']}\n"
            message += f"From: {from_email}\n"
            message += f"To: {', '.join(to_emails)}"
            if cc_emails:
                message += f"\nCC: {', '.join(cc_emails)}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Send from template failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to send email: {str(e)}",
                }
            ]

    async def _tool_create_team(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a new Microsoft Team."""
        try:
            display_name = arguments.get("displayName")
            description = arguments.get("description")
            visibility = arguments.get("visibility", "private")
            owner_email = arguments.get("ownerEmail")

            logger.info(f"Creating team: {display_name}")

            result = await TeamsProvisioningTools.create_team(
                display_name=display_name,
                description=description,
                visibility=visibility,
                owner_email=owner_email,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Team ID: {result['team_id']}\n"
            message += f"Team Name: {result['display_name']}\n"
            message += f"Web URL: {result['web_url']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Team creation failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to create team: {str(e)}",
                }
            ]

    async def _tool_list_teams(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """List all teams."""
        try:
            max_results = arguments.get("maxResults", 100)

            logger.info(f"Listing teams (max: {max_results})")

            result = await TeamsProvisioningTools.list_teams(max_results)

            if result["count"] == 0:
                return [{"type": "text", "text": "No teams found."}]

            message = f"✅ Found {result['count']} team(s):\n\n"
            for team in result["teams"]:
                message += f"🏢 {team['display_name']}\n"
                message += f"   Visibility: {team['visibility']}\n"
                message += f"   ID: {team['team_id']}\n"
                if team.get("description"):
                    message += f"   Description: {team['description']}\n"
                message += "\n"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Team list failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to list teams: {str(e)}",
                }
            ]

    async def _tool_create_channel(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a channel in a team."""
        try:
            team_id = arguments.get("teamId")
            display_name = arguments.get("displayName")
            description = arguments.get("description")
            channel_type = arguments.get("channelType", "standard")

            logger.info(f"Creating channel: {display_name} in team {team_id}")

            result = await TeamsProvisioningTools.create_channel(
                team_id=team_id,
                display_name=display_name,
                description=description,
                channel_type=channel_type,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Channel ID: {result['channel_id']}\n"
            message += f"Channel Name: {result['display_name']}\n"
            message += f"Web URL: {result['web_url']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Channel creation failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to create channel: {str(e)}",
                }
            ]

    async def _tool_list_channels(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """List all channels in a team."""
        try:
            team_id = arguments.get("teamId")

            logger.info(f"Listing channels for team: {team_id}")

            result = await TeamsProvisioningTools.list_channels(team_id)

            if result["count"] == 0:
                return [{"type": "text", "text": "No channels found."}]

            message = f"✅ Found {result['count']} channel(s):\n\n"
            for channel in result["channels"]:
                message += f"💬 {channel['display_name']}\n"
                message += f"   Type: {channel['membership_type']}\n"
                message += f"   ID: {channel['channel_id']}\n"
                if channel.get("description"):
                    message += f"   Description: {channel['description']}\n"
                message += "\n"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Channel list failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to list channels: {str(e)}",
                }
            ]

    async def _tool_add_team_member(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Add a member to a team."""
        try:
            team_id = arguments.get("teamId")
            user_email = arguments.get("userEmail")
            role = arguments.get("role", "member")

            logger.info(f"Adding {role} {user_email} to team {team_id}")

            result = await TeamsProvisioningTools.add_team_member(
                team_id=team_id,
                user_email=user_email,
                role=role,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"User: {result['user_email']}\n"
            message += f"Role: {result['role']}\n"
            message += f"Member ID: {result['member_id']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Add member failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to add member: {str(e)}",
                }
            ]

    async def _tool_list_team_members(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """List all members of a team."""
        try:
            team_id = arguments.get("teamId")

            logger.info(f"Listing members for team: {team_id}")

            result = await TeamsProvisioningTools.list_team_members(team_id)

            if result["count"] == 0:
                return [{"type": "text", "text": "No members found."}]

            message = f"✅ Found {result['count']} member(s):\n\n"
            for member in result["members"]:
                role_emoji = "👑" if member["role"] == "owner" else "👤"
                message += f"{role_emoji} {member['display_name']}\n"
                message += f"   Email: {member.get('email', 'N/A')}\n"
                message += f"   Role: {member['role']}\n"
                message += f"   ID: {member['member_id']}\n\n"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"List members failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to list members: {str(e)}",
                }
            ]

    async def _tool_provision_team(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Provision a complete team with channels and members."""
        try:
            team_name = arguments.get("teamName")
            team_description = arguments.get("teamDescription")
            owner_email = arguments.get("ownerEmail")
            channels = arguments.get("channels", [])
            members = arguments.get("members")
            visibility = arguments.get("visibility", "private")

            logger.info(f"Provisioning team: {team_name}")

            result = await TeamsProvisioningTools.provision_team_with_structure(
                team_name=team_name,
                team_description=team_description,
                owner_email=owner_email,
                channels=channels,
                members=members,
                visibility=visibility,
            )

            message = f"✅ {result['message']}\n\n"
            message += f"Team ID: {result['team_id']}\n"
            message += f"Team Name: {result['team_name']}\n"
            message += f"Team URL: {result['team_url']}\n"
            message += f"Channels Created: {result['channels_created']}\n"
            message += f"Members Added: {result['members_added']}"

            return [{"type": "text", "text": message}]

        except Exception as e:
            logger.error(f"Team provisioning failed: {e}", exc_info=True)
            return [
                {
                    "type": "text",
                    "text": f"❌ Failed to provision team: {str(e)}",
                }
            ]

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        logger.info("Starting M365 Admin MCP Server")

        # Log configuration
        logger.info(f"Tenant ID: {self.settings.azure_tenant_id}")
        logger.info(f"Client ID: {self.settings.azure_client_id}")
        logger.info(f"Auth Method: {self.settings.auth_method}")

        # Test connection on startup
        try:
            is_connected = await test_graph_connection()
            if is_connected:
                logger.info("✅ Graph API connection validated")
            else:
                logger.warning("⚠️ Graph API connection test failed")
        except Exception as e:
            logger.error(f"Startup connection test failed: {e}")

        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server ready - listening on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        server = M365AdminServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
