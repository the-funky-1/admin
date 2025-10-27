"""
Configuration management for M365 Admin MCP Server.

Loads configuration from environment variables with validation.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Azure AD Configuration
    azure_tenant_id: str = Field(..., description="Azure AD tenant ID")
    azure_client_id: str = Field(..., description="Azure AD client ID")

    # Authentication method selection
    auth_method: str = Field(
        default="device_code",
        description="Authentication method: 'device_code', 'interactive', 'client_secret', or 'certificate'"
    )

    azure_client_secret: Optional[str] = Field(
        default=None, description="Azure AD client secret (for client_secret auth)"
    )
    azure_certificate_path: Optional[Path] = Field(
        default=None, description="Path to certificate file (for certificate auth)"
    )
    azure_certificate_password: Optional[str] = Field(
        default=None, description="Certificate password if encrypted"
    )

    # Database Configuration
    database_path: Path = Field(
        default=Path("./data/m365_admin.db"), description="Path to SQLite database"
    )
    db_encryption_key: Optional[str] = Field(
        default=None, description="Database encryption key (256-bit)"
    )

    # MCP Server Configuration
    mcp_server_name: str = Field(default="m365-admin", description="MCP server name")
    mcp_server_version: str = Field(default="1.0.0", description="MCP server version")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(
        default=Path("./logs/m365_admin.log"), description="Log file path"
    )

    # Security Settings
    enable_operation_confirmation: bool = Field(
        default=False, description="Require confirmation for destructive operations"
    )
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    max_requests_per_minute: int = Field(
        default=60, description="Maximum requests per minute"
    )

    # Feature Flags
    enable_template_encryption: bool = Field(
        default=True, description="Encrypt email templates in database"
    )
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    enable_exchange_powershell: bool = Field(
        default=False, description="Enable Exchange Online PowerShell integration"
    )

    @field_validator("azure_tenant_id", "azure_client_id")
    @classmethod
    def validate_guid(cls, v: str) -> str:
        """Validate GUID format for Azure IDs."""
        if len(v) != 36 or v.count("-") != 4:
            raise ValueError(f"Invalid GUID format: {v}")
        return v

    @field_validator("auth_method")
    @classmethod
    def validate_auth_method(cls, v: str) -> str:
        """Validate authentication method."""
        valid_methods = ["device_code", "interactive", "client_secret", "certificate"]
        v_lower = v.lower()
        if v_lower not in valid_methods:
            raise ValueError(f"Invalid auth method. Must be one of: {valid_methods}")
        return v_lower

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v_upper

    @field_validator("database_path", "log_file", "azure_certificate_path")
    @classmethod
    def ensure_parent_directory(cls, v: Optional[Path]) -> Optional[Path]:
        """Ensure parent directory exists for file paths."""
        if v is not None:
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def use_certificate_auth(self) -> bool:
        """Check if certificate authentication is configured."""
        return self.azure_certificate_path is not None and self.azure_certificate_path.exists()

    @property
    def use_client_secret_auth(self) -> bool:
        """Check if client secret authentication is configured."""
        return self.azure_client_secret is not None

    def validate_auth_config(self) -> None:
        """Validate that authentication is properly configured for the selected method."""
        if self.auth_method == "certificate":
            if not self.use_certificate_auth:
                raise ValueError(
                    "Certificate authentication selected but AZURE_CERTIFICATE_PATH not configured or file not found"
                )
        elif self.auth_method == "client_secret":
            if not self.use_client_secret_auth:
                raise ValueError(
                    "Client secret authentication selected but AZURE_CLIENT_SECRET not configured"
                )
        # device_code and interactive methods only require tenant_id and client_id (already validated as required fields)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_auth_config()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = None
    return get_settings()
