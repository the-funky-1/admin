# Browser-Based Authentication Setup

**Date**: 2025-10-26
**Status**: ✅ Implemented - Device Code & Interactive Browser Authentication

---

## 🎯 Overview

The M365 Admin MCP Server now supports **browser-based OAuth authentication**, making it much easier to get started without creating client secrets. Users can authenticate interactively through their web browser with their Microsoft 365 credentials.

## 🔐 Authentication Methods

The server supports four authentication methods:

| Method | User Experience | Requirements | Use Case |
|--------|----------------|--------------|----------|
| **device_code** ⭐ | Shows code in terminal → Enter at microsoft.com/devicelogin | Tenant ID + Client ID | **RECOMMENDED** - Easiest for users |
| **interactive** | Automatically opens browser | Tenant ID + Client ID | Good for desktop environments |
| **client_secret** | No user interaction | Tenant ID + Client ID + Secret | Automation scenarios |
| **certificate** | No user interaction | Tenant ID + Client ID + Certificate | Production deployments |

---

## 🚀 Quick Start (Device Code - Recommended)

### Step 1: Get Your Azure AD Application IDs

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App Registrations**
3. Create a new app registration or use existing one:
   - **Name**: "M365 Admin MCP Server"
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Not needed for device code flow
4. Copy these values:
   - **Application (client) ID** - This is your `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** - This is your `AZURE_TENANT_ID`

### Step 2: Configure API Permissions

In your app registration, add these **Delegated permissions** (not application permissions):

**Microsoft Graph API**:
- `User.Read.All` - Read all users
- `User.ReadWrite.All` - Create and manage users
- `Mail.Send` - Send mail as any user
- `Group.ReadWrite.All` - Read and write all groups (for Teams)
- `Team.Create` - Create teams
- `TeamSettings.ReadWrite.All` - Read and write team settings
- `Channel.Create` - Create channels
- `ChannelSettings.ReadWrite.All` - Read and write channel settings
- `TeamMember.ReadWrite.All` - Add and remove team members

**Important**: Click **"Grant admin consent"** for these permissions.

### Step 3: Configure .env File

Edit your `.env` file (or create from `.env.example`):

```bash
# Required - Get from Azure Portal
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here

# Set authentication method to device_code
AUTH_METHOD=device_code

# No client secret needed!
```

### Step 4: Start the Server

```bash
python -m m365_admin_mcp.server
```

### Step 5: Authenticate When Prompted

When the server first connects to Microsoft Graph API, you'll see output like:

```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code ABCD1234 to authenticate.
```

1. Open your browser to https://microsoft.com/devicelogin
2. Enter the code shown in terminal
3. Sign in with your Microsoft 365 admin account
4. Grant consent to the requested permissions
5. Return to terminal - authentication complete!

The server will then be fully authenticated and ready to use.

---

## 🌐 Alternative: Interactive Browser Authentication

If you prefer automatic browser opening (works on desktop environments):

### Configuration

Update `.env`:
```bash
AUTH_METHOD=interactive
```

### Behavior

When the server starts:
1. Browser automatically opens to Microsoft sign-in page
2. Sign in with your Microsoft 365 admin account
3. Grant consent to requested permissions
4. Browser shows success message
5. Server is authenticated and ready

**Note**: This method may not work in:
- SSH sessions without display forwarding
- Headless servers
- Docker containers without display access

---

## 🔧 Advanced Configuration

### Client Secret Authentication (For Automation)

If you need **application permissions** (server runs without user interaction):

```bash
AUTH_METHOD=client_secret
AZURE_CLIENT_SECRET=your-secret-value
```

**Setup**:
1. In Azure Portal → App Registration → Certificates & secrets
2. Create new client secret
3. Copy secret value immediately (won't be shown again)
4. Add **Application permissions** (not delegated) in API permissions
5. Grant admin consent

### Certificate Authentication (For Production)

Most secure method for production:

```bash
AUTH_METHOD=certificate
AZURE_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CERTIFICATE_PASSWORD=optional-password
```

**Setup**:
1. Generate certificate: `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.pem -out cert.pem`
2. Upload certificate to Azure Portal → App Registration → Certificates & secrets
3. Add **Application permissions** (not delegated) in API permissions
4. Grant admin consent

---

## 📋 Comparison: Delegated vs Application Permissions

### Device Code / Interactive Browser (Delegated)

**Permissions**: Acts on behalf of signed-in user
**Benefits**:
- ✅ No client secrets to manage
- ✅ User consent controls access
- ✅ Easier to set up
- ✅ Better audit trail (actions attributed to specific user)

**Limitations**:
- ⚠️ Requires user to sign in
- ⚠️ Access limited to what user can do

### Client Secret / Certificate (Application)

**Permissions**: Acts as application identity
**Benefits**:
- ✅ No user interaction required
- ✅ Good for automation and scheduled tasks
- ✅ Consistent permissions

**Limitations**:
- ⚠️ Must secure client secret/certificate
- ⚠️ Higher security risk if compromised
- ⚠️ Actions not attributed to specific user

---

## 🔍 Troubleshooting

### "Invalid tenant identifier" Error

**Problem**: Using placeholder GUID from .env.example
**Solution**: Replace `00000000-0000-0000-0000-000000000000` with your actual tenant ID

### "Insufficient privileges" Error

**Problem**: Missing API permissions or admin consent not granted
**Solution**:
1. Check API permissions in Azure Portal
2. Ensure using **delegated** permissions for device_code/interactive
3. Ensure using **application** permissions for client_secret/certificate
4. Click "Grant admin consent" button

### Device Code Not Working

**Problem**: Code expired or already used
**Solution**: Restart server to get new code (codes expire after 15 minutes)

### Interactive Browser Doesn't Open

**Problem**: Running in SSH session or headless environment
**Solution**: Use `device_code` method instead

### "AADSTS50011: Redirect URI mismatch"

**Problem**: Interactive mode needs redirect URI
**Solution**:
1. In Azure Portal → App Registration → Authentication
2. Add redirect URI: `http://localhost:8400`
3. Platform: Web application
4. Or switch to `device_code` method (no redirect URI needed)

---

## 🔐 Security Best Practices

### For Device Code / Interactive Authentication

1. **Protect Credentials**: Don't commit `.env` file to version control
2. **Regular Re-authentication**: Tokens expire, plan for re-auth flow
3. **Least Privilege**: Only request permissions you actually need
4. **Audit Logging**: Enable audit logging to track actions

### For Client Secret / Certificate

1. **Rotate Secrets**: Regularly rotate client secrets (every 90 days)
2. **Secure Storage**: Use Azure Key Vault or encrypted storage
3. **Certificate Protection**: Protect certificate files with proper permissions
4. **Monitor Usage**: Watch for unusual authentication patterns

---

## 📊 Implementation Details

### Changes Made

**Files Modified**:
- `src/m365_admin_mcp/config.py` - Added `auth_method` field and validation
- `src/m365_admin_mcp/auth/graph_auth.py` - Added device code and interactive browser credential support
- `.env.example` - Updated with comprehensive authentication documentation
- `.env` - Updated to use device_code by default

**New Imports**:
```python
from azure.identity import DeviceCodeCredential, InteractiveBrowserCredential
from azure.identity.aio import (
    DeviceCodeCredential as AsyncDeviceCodeCredential,
    InteractiveBrowserCredential as AsyncInteractiveBrowserCredential,
)
```

**New Methods**:
- `GraphAuthenticator._create_device_code_credential()`
- `GraphAuthenticator._create_interactive_browser_credential()`

### Configuration Flow

```
User sets AUTH_METHOD in .env
         ↓
Settings.auth_method validated (device_code|interactive|client_secret|certificate)
         ↓
GraphAuthenticator.get_credential() routes to appropriate method
         ↓
Credential created based on auth_method
         ↓
GraphServiceClient initialized with credential
         ↓
On first API call, authentication flow triggered
         ↓
User authenticates in browser (if device_code/interactive)
         ↓
Token cached for subsequent requests
```

---

## 🎓 Next Steps

1. **Test Authentication**: Start server and complete browser authentication flow
2. **Test MCP Tools**: Use Claude Code to test MCP tool operations
3. **Review Permissions**: Ensure you have all needed permissions for your use case
4. **Set Up Logging**: Monitor authentication and API operations
5. **Production Planning**: Consider certificate authentication for production deployments

---

## 📚 Additional Resources

- [Azure AD Authentication Flows](https://docs.microsoft.com/en-us/azure/active-directory/develop/authentication-flows-app-scenarios)
- [Microsoft Graph API Permissions](https://docs.microsoft.com/en-us/graph/permissions-reference)
- [Device Code Flow Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code)
- [Azure Identity Python SDK](https://docs.microsoft.com/en-us/python/api/azure-identity)

---

**Recommendation**: Use **device_code** authentication for initial setup and testing. It's the easiest method requiring only tenant ID and client ID, with no client secrets to manage. Once comfortable, evaluate if client_secret or certificate authentication is needed for your production scenarios.
