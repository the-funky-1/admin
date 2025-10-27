"""
Azure AD authentication and Microsoft Graph client initialization.

Supports multiple authentication methods:
- Device Code Flow (browser-based, shows code)
- Interactive Browser Flow (browser-based, automatic)
- Client Secret (app-only, requires secret)
- Certificate (app-only, requires certificate)
"""

import logging
from pathlib import Path
from typing import Optional

from azure.identity import (
    CertificateCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    InteractiveBrowserCredential,
)
from azure.identity.aio import (
    CertificateCredential as AsyncCertificateCredential,
    ClientSecretCredential as AsyncClientSecretCredential,
)
from msgraph import GraphServiceClient

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


class GraphAuthenticator:
    """
    Handles Azure AD authentication and Graph client creation.

    Supports both synchronous and asynchronous credentials.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize authenticator with settings.

        Args:
            settings: Application settings (uses global settings if not provided)
        """
        self.settings = settings or get_settings()
        self._sync_credential: Optional[
            CertificateCredential | ClientSecretCredential | DeviceCodeCredential | InteractiveBrowserCredential
        ] = None
        self._async_credential: Optional[
            AsyncCertificateCredential | AsyncClientSecretCredential
        ] = None
        self._graph_client: Optional[GraphServiceClient] = None

    def _create_certificate_credential(self, async_mode: bool = False) -> CertificateCredential | AsyncCertificateCredential:
        """Create certificate-based credential."""
        cert_path = self.settings.azure_certificate_path
        if not cert_path or not cert_path.exists():
            raise FileNotFoundError(f"Certificate file not found: {cert_path}")

        logger.info(f"Creating certificate credential from {cert_path}")

        credential_class = AsyncCertificateCredential if async_mode else CertificateCredential

        # Read certificate file
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()

        return credential_class(
            tenant_id=self.settings.azure_tenant_id,
            client_id=self.settings.azure_client_id,
            certificate_data=cert_data,
            password=self.settings.azure_certificate_password,
        )

    def _create_client_secret_credential(self, async_mode: bool = False) -> ClientSecretCredential | AsyncClientSecretCredential:
        """Create client secret credential."""
        if not self.settings.azure_client_secret:
            raise ValueError("AZURE_CLIENT_SECRET not configured")

        logger.info("Creating client secret credential")

        credential_class = AsyncClientSecretCredential if async_mode else ClientSecretCredential

        return credential_class(
            tenant_id=self.settings.azure_tenant_id,
            client_id=self.settings.azure_client_id,
            client_secret=self.settings.azure_client_secret,
        )

    def _create_device_code_credential(self, async_mode: bool = False) -> DeviceCodeCredential:
        """Create device code credential (browser-based with code display).

        Note: DeviceCodeCredential doesn't have async version - uses sync only.
        Interactive authentication flows are inherently synchronous.
        """
        logger.info("Creating device code credential - user will authenticate in browser")

        def prompt_callback(verification_uri, user_code, expires_in):
            """Custom callback to display device code prompt."""
            import sys
            message = f"\n{'='*70}\n"
            message += "🔐 DEVICE CODE AUTHENTICATION\n"
            message += f"{'='*70}\n"
            message += "\nTo sign in, use a web browser to open:\n"
            message += f"    {verification_uri}\n"
            message += "\nAnd enter the code:\n"
            message += f"    {user_code}\n"
            message += f"\nThis code expires in {expires_in} seconds.\n"
            message += f"{'='*70}\n"

            # Print to both stdout and logger
            print(message)
            sys.stdout.flush()
            logger.warning(message)

        return DeviceCodeCredential(
            tenant_id=self.settings.azure_tenant_id,
            client_id=self.settings.azure_client_id,
            prompt_callback=prompt_callback,
        )

    def _create_interactive_browser_credential(self, async_mode: bool = False) -> InteractiveBrowserCredential:
        """Create interactive browser credential (automatically opens browser).

        Note: InteractiveBrowserCredential doesn't have async version - uses sync only.
        Interactive authentication flows are inherently synchronous.
        """
        logger.info("Creating interactive browser credential - browser will open automatically")

        return InteractiveBrowserCredential(
            tenant_id=self.settings.azure_tenant_id,
            client_id=self.settings.azure_client_id,
        )

    def get_credential(self, async_mode: bool = True):
        """
        Get appropriate credential based on configuration.

        Args:
            async_mode: Whether to create async credential (default: True)
                       Note: device_code and interactive methods always use sync credentials

        Returns:
            Azure AD credential instance

        Raises:
            ValueError: If authentication method is invalid
        """
        # Route to appropriate credential based on auth_method setting
        auth_method = self.settings.auth_method

        if auth_method == "device_code":
            # DeviceCodeCredential only has sync version - cache in sync credential
            if self._sync_credential is None:
                self._sync_credential = self._create_device_code_credential()
            return self._sync_credential

        elif auth_method == "interactive":
            # InteractiveBrowserCredential only has sync version - cache in sync credential
            if self._sync_credential is None:
                self._sync_credential = self._create_interactive_browser_credential()
            return self._sync_credential

        elif auth_method == "certificate":
            if async_mode:
                if self._async_credential is None:
                    self._async_credential = self._create_certificate_credential(async_mode=True)
                return self._async_credential
            else:
                if self._sync_credential is None:
                    self._sync_credential = self._create_certificate_credential(async_mode=False)
                return self._sync_credential

        elif auth_method == "client_secret":
            if async_mode:
                if self._async_credential is None:
                    self._async_credential = self._create_client_secret_credential(async_mode=True)
                return self._async_credential
            else:
                if self._sync_credential is None:
                    self._sync_credential = self._create_client_secret_credential(async_mode=False)
                return self._sync_credential

        else:
            raise ValueError(f"Invalid authentication method: {auth_method}")

    def get_graph_client(self) -> GraphServiceClient:
        """
        Get or create Microsoft Graph client with async credentials.

        Returns:
            Configured GraphServiceClient instance

        Example:
            ```python
            authenticator = GraphAuthenticator()
            client = authenticator.get_graph_client()
            users = await client.users.get()
            ```
        """
        if self._graph_client is None:
            credential = self.get_credential(async_mode=True)
            scopes = ["https://graph.microsoft.com/.default"]

            logger.info("Creating Microsoft Graph client")
            self._graph_client = GraphServiceClient(
                credentials=credential,
                scopes=scopes
            )

        return self._graph_client

    async def test_connection(self) -> bool:
        """
        Test Graph API connection by fetching organization info.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = self.get_graph_client()
            org = await client.organization.get()

            if org and org.value:
                org_info = org.value[0]
                logger.info(f"Successfully connected to tenant: {org_info.display_name}")
                return True
            else:
                logger.error("No organization information returned")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}", exc_info=True)
            return False


# Global authenticator instance
_authenticator: Optional[GraphAuthenticator] = None


def get_graph_client() -> GraphServiceClient:
    """
    Get global Microsoft Graph client instance.

    Returns:
        Configured GraphServiceClient

    Example:
        ```python
        from m365_admin_mcp.auth import get_graph_client

        client = get_graph_client()
        users = await client.users.get()
        ```
    """
    global _authenticator
    if _authenticator is None:
        _authenticator = GraphAuthenticator()
    return _authenticator.get_graph_client()


async def test_graph_connection() -> bool:
    """
    Test Graph API connection using global authenticator.

    Returns:
        True if connection successful, False otherwise
    """
    global _authenticator
    if _authenticator is None:
        _authenticator = GraphAuthenticator()
    return await _authenticator.test_connection()
