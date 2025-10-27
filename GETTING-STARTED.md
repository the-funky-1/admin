# Getting Started Checklist

Complete these steps to get your M365 Admin MCP Server operational.

## ✅ Phase 1: Prerequisites (5 minutes)

- [ ] **Python 3.11+ installed**
  ```bash
  python3.11 --version
  ```

- [ ] **Access to Azure AD with Global Admin role**
  - Log into [Azure Portal](https://portal.azure.com)
  - Verify you can see Azure Active Directory

- [ ] **Microsoft 365 subscription active**
  - Any plan (Business Basic, Standard, or Premium)
  - At least one user license available

- [ ] **Azure CLI installed** (optional, for automated setup)
  ```bash
  az --version
  ```

## ✅ Phase 2: Installation (5 minutes)

- [ ] **Create virtual environment**
  ```bash
  cd /path/to/m365-admin-mcp
  python3.11 -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -e ".[dev]"
  ```

- [ ] **Verify installation**
  ```bash
  python -c "import m365_admin_mcp; print(m365_admin_mcp.__version__)"
  # Should print: 1.0.0
  ```

## ✅ Phase 3: Azure AD Setup (10 minutes)

### Option A: Automated (Recommended)

- [ ] **Run setup script**
  ```bash
  ./scripts/setup_azure_ad.sh
  ```

- [ ] **Save the output**
  - Copy TENANT_ID, CLIENT_ID, CLIENT_SECRET

- [ ] **Grant admin consent** (if prompted)

### Option B: Manual

- [ ] **Create app registration in Azure Portal**
  - Name: `M365-Admin-MCP-Server`
  - Single tenant
  - Record Application (client) ID
  - Record Directory (tenant) ID

- [ ] **Add API permissions**
  - Microsoft Graph (Application permissions):
    - User.ReadWrite.All
    - Mail.ReadWrite
    - Mail.Send
    - MailboxSettings.ReadWrite
    - Organization.ReadWrite.All
    - Group.ReadWrite.All
    - Directory.ReadWrite.All
    - Application.ReadWrite.All
    - AuditLog.Read.All

- [ ] **Grant admin consent**
  - Click "Grant admin consent for [Your Org]"
  - Confirm

- [ ] **Create client secret**
  - Certificates & secrets → New client secret
  - Copy the secret value immediately

## ✅ Phase 4: Configuration (3 minutes)

- [ ] **Create .env file**
  ```bash
  cp .env.example .env
  ```

- [ ] **Edit .env with your credentials**
  ```bash
  nano .env  # or your preferred editor
  ```

- [ ] **Verify required settings**
  ```bash
  AZURE_TENANT_ID=your-tenant-id-here
  AZURE_CLIENT_ID=your-client-id-here
  AZURE_CLIENT_SECRET=your-client-secret-here
  ```

- [ ] **Set database path** (optional)
  ```bash
  DATABASE_PATH=./data/m365_admin.db
  ```

## ✅ Phase 5: Database Setup (2 minutes)

- [ ] **Initialize database**
  ```bash
  python scripts/init_database.py
  ```

- [ ] **Verify database created**
  ```bash
  ls -lh data/m365_admin.db
  ```

## ✅ Phase 6: Test Connection (5 minutes)

- [ ] **Test authentication**
  ```bash
  python -c "
  import asyncio
  from m365_admin_mcp.auth import test_graph_connection
  result = asyncio.run(test_graph_connection())
  print(f'Connection: {'✅ Success' if result else '❌ Failed'}')
  "
  ```

- [ ] **Start the server**
  ```bash
  python -m m365_admin_mcp.server
  ```

- [ ] **Verify server output**
  - Should see: `✅ Graph API connection validated`
  - Should see: `Server ready - listening on stdio`

- [ ] **Stop server** (Ctrl+C)

## ✅ Phase 7: Claude Code Integration (5 minutes)

- [ ] **Locate Claude Code config**
  - Mac/Linux: `~/.config/claude-code/config.json`
  - Windows: `%APPDATA%\claude-code\config.json`

- [ ] **Add MCP server configuration**
  ```json
  {
    "mcpServers": {
      "m365-admin": {
        "command": "/absolute/path/to/venv/bin/python",
        "args": ["-m", "m365_admin_mcp.server"],
        "cwd": "/absolute/path/to/m365-admin-mcp"
      }
    }
  }
  ```

- [ ] **Restart Claude Code**

- [ ] **Test in Claude Code**
  - Type: `Test the M365 connection`
  - Should get: `✅ Successfully connected to Microsoft Graph API`

## ✅ Phase 8: First Operations (10 minutes)

- [ ] **Check server health**
  ```
  Get the M365 server health status
  ```

- [ ] **List users** (manual test)
  ```bash
  python -c "
  import asyncio
  from m365_admin_mcp.tools.user_management import UserManagementTools
  result = asyncio.run(UserManagementTools.list_users())
  print(result)
  "
  ```

- [ ] **Verify your tenant users listed**

## ✅ Phase 9: Run Tests (5 minutes)

- [ ] **Run unit tests**
  ```bash
  pytest tests/unit/
  ```

- [ ] **Verify all tests pass**
  - Should see: `X passed` with no failures

- [ ] **Check coverage** (optional)
  ```bash
  pytest --cov=src --cov-report=html
  open htmlcov/index.html  # View coverage report
  ```

## ✅ Phase 10: Security Review (5 minutes)

- [ ] **Verify .env not in git**
  ```bash
  git status  # .env should not appear
  ```

- [ ] **Check certificate files excluded** (if using cert auth)
  ```bash
  git status  # *.pem, *.key should not appear
  ```

- [ ] **Review permissions granted**
  - Azure Portal → App registrations → Your app → API permissions
  - Verify all permissions have green checkmarks

- [ ] **Enable audit logging** (optional)
  ```bash
  # In .env:
  ENABLE_AUDIT_LOGGING=true
  ```

## 🎉 Completion Checklist

### Minimum Viable Setup ✅
- [ ] Server starts successfully
- [ ] Graph API connection validated
- [ ] Claude Code can communicate with server
- [ ] Health check returns "healthy"

### Production Ready 🚀
- [ ] Certificate authentication configured (not client secret)
- [ ] Database encryption enabled
- [ ] Audit logging enabled
- [ ] Log rotation configured
- [ ] All tests passing
- [ ] Documentation reviewed

### Security Hardened 🔐
- [ ] Client secret removed (using certificate only)
- [ ] Database encrypted with strong key
- [ ] .env file permissions set (chmod 600)
- [ ] No credentials in logs
- [ ] Rate limiting enabled

## 📊 Verification Commands

Run these to verify everything is working:

```bash
# 1. Test imports
python -c "from m365_admin_mcp import __version__; print(f'Version: {__version__}')"

# 2. Test configuration
python -c "from m365_admin_mcp.config import get_settings; s = get_settings(); print(f'Tenant: {s.azure_tenant_id[:8]}...')"

# 3. Test auth connection (async)
python -c "import asyncio; from m365_admin_mcp.auth import test_graph_connection; print(asyncio.run(test_graph_connection()))"

# 4. Run tests
pytest tests/unit/ -v

# 5. Start server (manual test)
python -m m365_admin_mcp.server
# Press Ctrl+C after seeing "Server ready"
```

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'm365_admin_mcp'"

**Solution**:
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
# Reinstall in editable mode
pip install -e .
```

### Issue: "ValueError: No authentication method configured"

**Solution**:
```bash
# Check .env file exists
ls -la .env
# Verify it contains credentials
cat .env | grep AZURE_
```

### Issue: "Authorization_RequestDenied"

**Solution**:
1. Go to Azure Portal → App registrations → Your app
2. Click "API permissions"
3. Click "Grant admin consent"
4. Wait 5-10 minutes for propagation

### Issue: Server starts but Claude Code can't connect

**Solution**:
1. Verify absolute paths in Claude Code config
2. Test server manually first
3. Check Claude Code logs for errors
4. Restart Claude Code after config changes

## 📚 Next Steps

After completing this checklist:

1. **Review documentation**:
   - [README.md](README.md) - Comprehensive overview
   - [QUICKSTART.md](QUICKSTART.md) - Quick reference
   - [claudedocs/M365-Admin-MCP-Specification.md](claudedocs/M365-Admin-MCP-Specification.md) - Technical spec

2. **Explore capabilities**:
   - Try user management commands
   - Review health check output
   - Test different operations

3. **Plan Phase 2**:
   - Review email template requirements
   - Prepare sample templates
   - Plan integration approach

## 🎓 Training Resources

- **Microsoft Graph API**: https://learn.microsoft.com/en-us/graph/
- **Azure AD Authentication**: https://learn.microsoft.com/en-us/azure/active-directory/develop/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Pydantic Settings**: https://docs.pydantic.dev/latest/

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/libertygoldsilver/m365-admin-mcp/issues)
- **Documentation**: See [docs/](docs/) directory
- **Email**: admin@libertygoldsilver.com

---

**Estimated Total Time**: ~55 minutes for complete setup

**Status Check**: If you can run `python -m m365_admin_mcp.server` and see "Server ready", you're done! ✅
