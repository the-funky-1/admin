# Claude Desktop MCP Integration - Quick Setup

**5-Minute Setup Guide** for M365 Admin MCP Server

---

## 🚀 Quick Start (3 Steps)

### Step 1: Locate Your Claude Desktop Config File

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add M365 Admin Server

Open the config file and add this configuration:

```json
{
  "mcpServers": {
    "m365-admin": {
      "command": "python",
      "args": [
        "-m",
        "m365_admin_mcp.server"
      ],
      "cwd": "/home/funky_one/Music/MCPs/admin",
      "env": {
        "PYTHONPATH": "/home/funky_one/Music/MCPs/admin/src"
      }
    }
  }
}
```

**⚠️ Important**: If you have other MCP servers, add the "m365-admin" entry inside the existing `mcpServers` object.

**Example with existing servers**:
```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "m365-admin": {
      "command": "python",
      "args": ["-m", "m365_admin_mcp.server"],
      "cwd": "/home/funky_one/Music/MCPs/admin",
      "env": {
        "PYTHONPATH": "/home/funky_one/Music/MCPs/admin/src"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

1. **Quit** Claude Desktop completely (don't just close the window)
2. **Reopen** Claude Desktop
3. Look for the **🔌 MCP icon** in the interface
4. Verify **"m365-admin"** appears in the server list

---

## ✅ Verify It's Working

### Test 1: Check Server Health

In Claude Desktop, ask:
```
Can you check the M365 server health?
```

**Expected Response**: Claude will use the `check_server_health` tool and show:
- Server status: healthy/degraded/unhealthy
- Authentication: true/false
- Graph API connected: true/false
- Configuration details

### Test 2: List Available Tools

In Claude Desktop, ask:
```
What M365 admin tools do you have available?
```

**Expected Response**: Claude will list 18 tools including:
- Health & testing (2 tools)
- User management (3 tools)
- Email templates (6 tools)
- Teams provisioning (7 tools)

### Test 3: Run a Simple Operation

In Claude Desktop, ask:
```
Can you list the email templates in my M365 account?
```

**Expected Response**:
- Browser may open for authentication (first time only)
- Claude will use the `list_email_templates` tool
- You'll see a list of saved email templates (or empty if none exist)

---

## 🔍 Troubleshooting

### Issue: Server Not Listed in Claude Desktop

**Solutions**:
1. Check file path is correct: `/home/funky_one/Music/MCPs/admin`
2. Verify JSON syntax is valid (use [jsonlint.com](https://jsonlint.com))
3. Make sure you **quit** Claude Desktop (not just close window)
4. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`
   - Linux: `~/.config/Claude/logs/mcp*.log`

### Issue: Server Shows as "Disconnected"

**Solutions**:
1. Verify Python is accessible: `which python` or `where python`
2. Test server manually: `cd /home/funky_one/Music/MCPs/admin && python -m m365_admin_mcp.server`
3. Check `.env` file exists and has correct credentials
4. Review server logs: `tail -f logs/m365_admin.log`

### Issue: Authentication Fails

**Solutions**:
1. Verify Azure AD app redirect URIs are configured:
   - `http://localhost`
   - `https://login.microsoftonline.com/common/oauth2/nativeclient`
2. Check "Allow public client flows" is enabled in Azure Portal
3. Verify delegated permissions are granted with admin consent
4. Try clearing browser cookies/cache

---

## 📱 Using the M365 Admin Server

### Common Commands

**Health & Status**:
```
Check the M365 server health
Test my Graph API connection
```

**User Management**:
```
List all users in my organization
Get details for user john@example.com
Create a new user with email jane@example.com
```

**Email Templates**:
```
List my email templates
Create a welcome email template
Send a welcome email to new-user@example.com
```

**Teams Provisioning**:
```
Create a new team called "Marketing Department"
Add channels to the Sales team
Provision a complete department with standard setup
```

### Advanced Usage

**Bulk Operations**:
```
Create 10 new users from this CSV file
Provision teams for all departments
Send welcome emails to all new hires
```

**Template Management**:
```
Show me the onboarding email template
Update the welcome template with new content
Delete old unused templates
```

**Teams Administration**:
```
List all teams in the organization
Add members to the Engineering team
Configure standard channels for Project Alpha
```

---

## 🎯 Best Practices

### Security

1. **Never share .env file** - Contains sensitive credentials
2. **Use interactive auth in production** - More secure than client secrets
3. **Enable operation confirmation** - Already enabled in your config
4. **Review audit logs regularly** - Check `logs/m365_admin.log`

### Performance

1. **Rate limiting is active** - 30 requests/minute (adjustable in `.env`)
2. **Database is encrypted** - All sensitive data protected
3. **Logs rotate automatically** - Prevents disk space issues

### Maintenance

1. **Backup database weekly** - `cp data/m365_admin.db backups/`
2. **Review permissions monthly** - Check Azure AD app permissions
3. **Update regularly** - Check for MCP server updates

---

## 📚 Additional Documentation

- **Full Setup Guide**: `claudedocs/Production-Deployment-Guide.md`
- **Quick Start**: `QUICKSTART.md`
- **Browser Auth Guide**: `claudedocs/Browser-Authentication-Setup.md`
- **Phase 3 Details**: `claudedocs/Phase-3-Teams-Provisioning.md`

---

## ✨ What's Next?

Now that your M365 Admin MCP Server is integrated with Claude Desktop, you can:

1. **Automate user onboarding** - Create users and send welcome emails
2. **Manage Teams workspaces** - Provision departments with standard structure
3. **Handle email operations** - Create and use reusable email templates
4. **Monitor M365 health** - Check server status and connection

**Enjoy your automated M365 administration! 🚀**

---

**Last Updated**: 2025-10-26
**Version**: 1.0.0
**Status**: Production Ready ✅
