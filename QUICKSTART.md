# Quick Start Guide - M365 Admin MCP Server

Get your M365 Admin MCP Server up and running in 15 minutes.

## Prerequisites

- **Python 3.11+** installed
- **Azure AD tenant** with Global Admin access
- **Microsoft 365 subscription** (any plan)
- **Git** (optional, for version control)

## Step 1: Install Dependencies (2 minutes)

```bash
# Clone or navigate to the project directory
cd m365-admin-mcp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Step 2: Azure AD Setup (5 minutes)

### Choose Your Authentication Method

**🌟 Recommended: Browser-Based Authentication (Device Code)**
- ✅ No client secrets to manage
- ✅ Easiest to set up
- ✅ Just need Tenant ID and Client ID
- ✅ Authenticates as signed-in user

**Alternative: Client Secret Authentication**
- Good for automation scenarios
- Requires managing secrets securely
- Authenticates as application

### Setup Instructions

1. **Go to Azure Portal**:
   - Navigate to Azure Active Directory → App registrations
   - Click "New registration"

2. **Configure App**:
   - Name: `M365-Admin-MCP-Server`
   - Supported account types: `Single tenant`
   - Register

3. **Copy Your IDs** (Required for all methods):
   - Copy **Application (client) ID** → This is your `AZURE_CLIENT_ID`
   - Copy **Directory (tenant) ID** → This is your `AZURE_TENANT_ID`

4. **Add Permissions** (Choose based on auth method):

   **For Browser-Based (Device Code/Interactive) - Add DELEGATED permissions:**
   - Go to "API permissions" → Add permission → Microsoft Graph
   - Select "Delegated permissions":
     - User.Read.All
     - User.ReadWrite.All
     - Mail.Send
     - Group.ReadWrite.All
     - Team.Create
     - TeamSettings.ReadWrite.All
     - Channel.Create
     - ChannelSettings.ReadWrite.All
     - TeamMember.ReadWrite.All
   - Click "Grant admin consent"

   **For Client Secret - Add APPLICATION permissions:**
   - User.ReadWrite.All
   - Mail.ReadWrite
   - Mail.Send
   - MailboxSettings.ReadWrite
   - Organization.ReadWrite.All
   - Group.ReadWrite.All
   - Directory.ReadWrite.All
   - Application.ReadWrite.All
   - AuditLog.Read.All
   - Click "Grant admin consent"

5. **Create Secret** (Only if using client secret method):
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the secret value immediately

## Step 3: Configure Environment (2 minutes)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Azure AD credentials
nano .env  # or use your preferred editor
```

**For Browser-Based Authentication (Recommended):**
```bash
# Required
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here

# Set authentication method to device_code
AUTH_METHOD=device_code

# No client secret needed!
```

**For Client Secret Authentication:**
```bash
# Required
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here

# Set authentication method
AUTH_METHOD=client_secret
```

**Optional configuration:**
```bash
# Database
DATABASE_PATH=./data/m365_admin.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/m365_admin.log

# Security
ENABLE_AUDIT_LOGGING=true
RATE_LIMIT_ENABLED=true
```

## Step 4: Initialize Database (1 minute)

```bash
python scripts/init_database.py
```

This creates the SQLite database with required tables.

## Step 5: Test Connection (2 minutes)

```bash
# Test the server
python -m m365_admin_mcp.server
```

**For Browser-Based Authentication:**
When the server first connects to Microsoft Graph, you'll see:
```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code ABCD1234 to authenticate.
```

1. Open https://microsoft.com/devicelogin in your browser
2. Enter the code shown in terminal
3. Sign in with your M365 admin account
4. Grant consent to the requested permissions

After successful authentication:
```
✅ Graph API connection validated
Server ready - listening on stdio
```

**For Client Secret Authentication:**
The server will authenticate automatically and show:
```
✅ Graph API connection validated
Server ready - listening on stdio
```

Press `Ctrl+C` to stop.

## Step 6: Integrate with Claude Code (3 minutes)

Add to your Claude Code MCP settings (`~/.config/claude-code/config.json` or similar):

```json
{
  "mcpServers": {
    "m365-admin": {
      "command": "python",
      "args": [
        "-m",
        "m365_admin_mcp.server"
      ],
      "cwd": "/path/to/m365-admin-mcp",
      "env": {
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

**Or use environment variables from .env:**
```json
{
  "mcpServers": {
    "m365-admin": {
      "command": "/path/to/m365-admin-mcp/venv/bin/python",
      "args": [
        "-m",
        "m365_admin_mcp.server"
      ],
      "cwd": "/path/to/m365-admin-mcp"
    }
  }
}
```

Restart Claude Code.

## Step 7: Test in Claude Code

Try these commands in Claude Code:

```
Test the M365 connection

Get server health status

List all users in the tenant
```

## Next Steps

### Production Setup

For production, use **certificate authentication** instead of client secret:

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout cert.key -out cert.pem

# Upload cert.pem to Azure Portal:
# Azure AD → App registrations → Your app → Certificates & secrets

# Update .env:
AZURE_CERTIFICATE_PATH=./cert.pem
# Remove or comment out AZURE_CLIENT_SECRET
```

### Security Hardening

1. **Enable database encryption** (optional):
   ```bash
   pip install pysqlcipher3
   # Set DB_ENCRYPTION_KEY in .env
   ```

2. **Configure audit logging**:
   ```bash
   ENABLE_AUDIT_LOGGING=true
   ```

3. **Set up log rotation** (for production):
   ```bash
   # Configure logrotate or similar
   ```

### Explore Features

- **User Management**: Create and configure M365 users
- **Email Templates**: Build reusable email templates
- **Teams Provisioning**: Create Teams with channels
- **Service Configuration**: Configure tracking, add-ins, features

See [README.md](README.md) for detailed usage examples.

## Troubleshooting

### "Authorization_RequestDenied" Error

**Problem**: Permission denied when calling Graph API

**Solution**:
1. Verify all permissions are added in Azure AD
2. Ensure admin consent is granted
3. Wait 5-10 minutes for permissions to propagate

### "No authentication method configured" Error

**Problem**: Missing Azure AD credentials

**Solution**:
1. Check `.env` file exists
2. Verify `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and either `AZURE_CLIENT_SECRET` or `AZURE_CERTIFICATE_PATH` are set

### "Unable to open database" Error

**Problem**: Database file not found or permission denied

**Solution**:
1. Run `python scripts/init_database.py`
2. Check `DATABASE_PATH` in `.env`
3. Ensure directory has write permissions

### Server Not Responding in Claude Code

**Problem**: Claude Code can't communicate with MCP server

**Solution**:
1. Test server manually first: `python -m m365_admin_mcp.server`
2. Check paths in Claude Code config are absolute
3. Verify Python virtual environment path is correct
4. Check Claude Code logs for error messages

## Support

- **Issues**: [GitHub Issues](https://github.com/libertygoldsilver/m365-admin-mcp/issues)
- **Documentation**: See [docs/](docs/) directory
- **Email**: admin@libertygoldsilver.com

## What's Next?

- ✅ **Phase 1 Complete**: Authentication, health check, basic user management
- 📋 **Phase 2**: Email template system
- 📋 **Phase 3**: Teams provisioning
- 📋 **Phase 4**: Advanced configuration (tracking, add-ins)
- 📋 **Phase 5**: Polish and production hardening

See [claudedocs/M365-Admin-MCP-Specification.md](claudedocs/M365-Admin-MCP-Specification.md) for the complete roadmap.
