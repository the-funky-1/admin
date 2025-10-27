#!/bin/bash
#
# Azure AD Application Setup Script
#
# This script provides guidance for setting up the Azure AD application
# for the M365 Admin MCP Server.
#

set -e

echo "========================================="
echo "M365 Admin MCP Server - Azure AD Setup"
echo "========================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"
echo ""

# Login check
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please log in to Azure..."
    az login
fi

TENANT_ID=$(az account show --query tenantId -o tsv)
echo "✅ Logged in to tenant: $TENANT_ID"
echo ""

# Get app registration name
read -p "Enter application name [M365-Admin-MCP-Server]: " APP_NAME
APP_NAME=${APP_NAME:-M365-Admin-MCP-Server}

echo ""
echo "Creating app registration: $APP_NAME"

# Create app registration
APP_ID=$(az ad app create \
    --display-name "$APP_NAME" \
    --sign-in-audience AzureSingleTenant \
    --query appId -o tsv)

echo "✅ Created app: $APP_ID"

# Create service principal
az ad sp create --id "$APP_ID" > /dev/null
echo "✅ Created service principal"

# Assign Microsoft Graph API permissions
echo ""
echo "Assigning Microsoft Graph API permissions..."

# Microsoft Graph API ID
MS_GRAPH_ID="00000003-0000-0000-c000-000000000000"

# Required permissions (Application permissions)
PERMISSIONS=(
    "User.ReadWrite.All=df021288-bdef-4463-88db-98f22de89214"
    "Mail.ReadWrite=e2a3a72e-5f79-4c64-b1b1-878b674786c9"
    "Mail.Send=b633e1c5-b582-4048-a93e-9f11b44c7e96"
    "MailboxSettings.ReadWrite=6931bccd-447a-43d1-b442-00a195474933"
    "Organization.ReadWrite.All=292d869f-3427-49a8-9dab-8c70152b74e9"
    "Group.ReadWrite.All=62a82d76-70ea-41e2-9197-370581804d09"
    "Directory.ReadWrite.All=19dbc75e-c2e2-444c-a770-ec69d8559fc7"
    "Application.ReadWrite.All=1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9"
    "AuditLog.Read.All=b0afded3-3588-46d8-8b3d-9842eff778da"
)

for PERM in "${PERMISSIONS[@]}"; do
    NAME="${PERM%%=*}"
    ID="${PERM##*=}"
    echo "  - Adding $NAME"
    az ad app permission add \
        --id "$APP_ID" \
        --api "$MS_GRAPH_ID" \
        --api-permissions "$ID=Role" > /dev/null
done

echo "✅ Permissions added"

# Grant admin consent
echo ""
read -p "Grant admin consent now? (requires Global Admin) [y/N]: " CONSENT
if [[ "$CONSENT" =~ ^[Yy]$ ]]; then
    echo "Granting admin consent..."
    az ad app permission admin-consent --id "$APP_ID"
    echo "✅ Admin consent granted"
else
    echo "⚠️  Admin consent required. Grant it manually in Azure Portal:"
    echo "   https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/$APP_ID"
fi

# Create client secret
echo ""
read -p "Create client secret (for development)? [Y/n]: " CREATE_SECRET
if [[ ! "$CREATE_SECRET" =~ ^[Nn]$ ]]; then
    SECRET=$(az ad app credential reset --id "$APP_ID" --query password -o tsv)
    echo "✅ Client secret created"
    echo ""
    echo "⚠️  SAVE THIS SECRET NOW - IT WON'T BE SHOWN AGAIN:"
    echo "   $SECRET"
fi

# Certificate instructions
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Configuration for .env file:"
echo ""
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_CLIENT_ID=$APP_ID"
if [[ ! "$CREATE_SECRET" =~ ^[Nn]$ ]]; then
    echo "AZURE_CLIENT_SECRET=$SECRET"
fi
echo ""
echo "For production, use certificate authentication:"
echo "1. Generate certificate:"
echo "   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\"
echo "     -keyout cert.key -out cert.pem"
echo ""
echo "2. Upload cert.pem to Azure Portal:"
echo "   https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Credentials/appId/$APP_ID"
echo ""
echo "3. Update .env:"
echo "   AZURE_CERTIFICATE_PATH=/path/to/cert.pem"
echo ""
echo "Next steps:"
echo "1. Copy the configuration above to your .env file"
echo "2. Install Python dependencies: pip install -e .[dev]"
echo "3. Test connection: python -m m365_admin_mcp.server"
echo ""
