"""
Health check resource for monitoring server status.
"""

import json
import logging
from datetime import datetime
from typing import Any

from ..auth import test_graph_connection
from ..config import get_settings

logger = logging.getLogger(__name__)


class HealthResource:
    """Health check resource for MCP server monitoring."""

    @staticmethod
    async def get_health_status() -> dict[str, Any]:
        """
        Get comprehensive health status of the MCP server.

        Returns:
            Dictionary with health status information

        Example response:
            {
                "status": "healthy",
                "timestamp": "2025-10-26T10:30:00Z",
                "authenticated": true,
                "graphApiConnected": true,
                "configuration": {
                    "authMethod": "certificate",
                    "serverName": "m365-admin",
                    "serverVersion": "1.0.0"
                }
            }
        """
        settings = get_settings()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Test Graph API connection
        try:
            graph_connected = await test_graph_connection()
            authenticated = graph_connected
        except Exception as e:
            logger.error(f"Graph API connection test failed: {e}")
            graph_connected = False
            authenticated = False

        # Determine overall status
        if authenticated and graph_connected:
            status = "healthy"
        elif authenticated:
            status = "degraded"
        else:
            status = "unhealthy"

        # Get auth method from settings
        auth_method = settings.auth_method

        health_data = {
            "status": status,
            "timestamp": timestamp,
            "authenticated": authenticated,
            "graphApiConnected": graph_connected,
            "configuration": {
                "authMethod": auth_method,
                "serverName": settings.mcp_server_name,
                "serverVersion": settings.mcp_server_version,
                "auditLoggingEnabled": settings.enable_audit_logging,
                "rateLimitEnabled": settings.rate_limit_enabled,
            },
        }

        return health_data

    @staticmethod
    def format_as_resource_content(health_data: dict[str, Any]) -> str:
        """
        Format health data as MCP resource content.

        Args:
            health_data: Health status dictionary

        Returns:
            JSON string for MCP resource content
        """
        return json.dumps(health_data, indent=2)
