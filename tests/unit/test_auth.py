"""
Unit tests for authentication module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from m365_admin_mcp.auth.graph_auth import GraphAuthenticator
from m365_admin_mcp.config import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.azure_tenant_id = "00000000-0000-0000-0000-000000000000"
    settings.azure_client_id = "11111111-1111-1111-1111-111111111111"
    settings.azure_client_secret = "test-secret"
    settings.azure_certificate_path = None
    settings.azure_certificate_password = None
    settings.use_certificate_auth = False
    settings.use_client_secret_auth = True
    return settings


def test_authenticator_initialization(mock_settings):
    """Test GraphAuthenticator initialization."""
    authenticator = GraphAuthenticator(mock_settings)
    assert authenticator.settings == mock_settings
    assert authenticator._graph_client is None


@patch("m365_admin_mcp.auth.graph_auth.AsyncClientSecretCredential")
def test_create_client_secret_credential(mock_credential_class, mock_settings):
    """Test client secret credential creation."""
    authenticator = GraphAuthenticator(mock_settings)

    credential = authenticator._create_client_secret_credential(async_mode=True)

    mock_credential_class.assert_called_once_with(
        tenant_id=mock_settings.azure_tenant_id,
        client_id=mock_settings.azure_client_id,
        client_secret=mock_settings.azure_client_secret,
    )


def test_get_credential_no_auth_configured():
    """Test error when no authentication method configured."""
    settings = Mock(spec=Settings)
    settings.use_certificate_auth = False
    settings.use_client_secret_auth = False

    authenticator = GraphAuthenticator(settings)

    with pytest.raises(ValueError, match="No authentication method configured"):
        authenticator.get_credential()


@patch("m365_admin_mcp.auth.graph_auth.GraphServiceClient")
@patch("m365_admin_mcp.auth.graph_auth.AsyncClientSecretCredential")
def test_get_graph_client(mock_credential, mock_client, mock_settings):
    """Test Graph client creation."""
    authenticator = GraphAuthenticator(mock_settings)

    client = authenticator.get_graph_client()

    assert client is not None
    mock_client.assert_called_once()


@pytest.mark.asyncio
@patch("m365_admin_mcp.auth.graph_auth.GraphServiceClient")
async def test_connection_test_success(mock_client_class, mock_settings):
    """Test successful connection test."""
    # Mock Graph client and organization response
    mock_org = Mock()
    mock_org.display_name = "Test Organization"

    mock_org_response = Mock()
    mock_org_response.value = [mock_org]

    mock_client = AsyncMock()
    mock_client.organization.get = AsyncMock(return_value=mock_org_response)
    mock_client_class.return_value = mock_client

    authenticator = GraphAuthenticator(mock_settings)
    authenticator._graph_client = mock_client

    result = await authenticator.test_connection()

    assert result is True


@pytest.mark.asyncio
@patch("m365_admin_mcp.auth.graph_auth.GraphServiceClient")
async def test_connection_test_failure(mock_client_class, mock_settings):
    """Test failed connection test."""
    mock_client = AsyncMock()
    mock_client.organization.get = AsyncMock(side_effect=Exception("Connection failed"))
    mock_client_class.return_value = mock_client

    authenticator = GraphAuthenticator(mock_settings)
    authenticator._graph_client = mock_client

    result = await authenticator.test_connection()

    assert result is False
